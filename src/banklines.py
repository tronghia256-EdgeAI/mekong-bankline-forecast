"""P0: bank positions on transects from annual MNDWI composites, plus quick-look figures.

Usage: python src/banklines.py sadec_caolanh
Reads data/raw/<reach>/mndwi_*.tif; writes data/processed/<reach>/bank_positions.csv,
results/p0/<reach>_*.png and prints a detectability summary.

Method: per year, Otsu threshold on MNDWI -> largest connected water body (main channel).
Centerline = skeleton of the >=50%-of-years channel belt (islands filled, canals opened away).
Transects every 100 m, perpendicular to the smoothed centerline. On each side the bank is the
mainland's edge facing the river ("walking from the mainland, the first water"): walking out from
the open river (water >= ~330 m wide in >= half the years; river water on narrow branches), islands,
bars and spurs narrower than 30 m are passed over and the first mainland run is the bank. Mainland =
land joined to the raster border, with canals < ~90 m not cutting it and enclosed ponds filled.
Refined to sub-pixel by linear interpolation of bilinear MNDWI across the threshold. Distance is
measured from the centerline, so erosion = distance increases.
"""
import json
import pathlib
import sys
from collections import deque

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
from scipy import ndimage
from scipy.spatial import cKDTree
from scipy.stats import theilslopes
from skimage.filters import threshold_otsu
from skimage.morphology import binary_closing, binary_opening, disk, skeletonize

SPACING, HALF, STEP = 100.0, 3000.0, 5.0   # transect spacing, half-length, sample step (m)
SMOOTH_PX = 51                              # centerline moving-average window (skeleton pixels)
BELT_MARGIN = 500.0                         # reject banks this far beyond the belt edge (canal mouths)
REFINE = 6                                  # samples either side of the mask edge searched for the MNDWI crossing
JUMP = 150.0                                # year-to-year change (m): a spike if it reverts, a step if it persists
NONLIN = 30.0                               # robust residual scale (m) above which a trend is called non-linear
NOISE_M = 3.6                               # measured per-composite noise (repeat + window), sensor_check.md
CORE_PX = 5                                 # open river = water >= ~330 m wide in >= half the years
MIN_LAND = 6                                # samples (30 m): narrower mainland spurs (jetties, moored boats) are skipped
ISLAND_PX = 1111                            # 1 km2 of 30 m pixels: larger islands (cù lao) count as mainland
MAX_NODATA = 0.02                           # drop composites with more missing pixels than this
MIN_YEARS = 15
EIGHT = np.ones((3, 3), bool)
TILES = pathlib.Path('data/tiles.json')        # P1 tiles of the full rivers (river_tiles.py)
NARROW_CORRIDOR = 1000.0                    # narrow tiles: only water this near the coarse centerline (no long canals)


def largest(mask):
    lab, n = ndimage.label(mask, structure=EIGHT)
    if n == 0:
        return mask
    sizes = np.bincount(lab.ravel())
    sizes[0] = 0
    return lab == sizes.argmax()


def longest_path(skel):
    pix = set(zip(*np.nonzero(skel)))
    nbrs = [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if dr or dc]

    def bfs(start):
        par, q, last = {start: None}, deque([start]), start
        while q:
            last = q.popleft()
            for dr, dc in nbrs:
                p = (last[0] + dr, last[1] + dc)
                if p in pix and p not in par:
                    par[p] = last
                    q.append(p)
        return last, par

    a, _ = bfs(next(iter(pix)))
    b, par = bfs(a)
    path = [b]
    while par[path[-1]] is not None:
        path.append(par[path[-1]])
    return np.array(path, float)


def mainland_mask(water):
    """Land joined to the raster border or larger than ISLAND_PX (inhabited cù lao), with the ponds it encloses
    filled in; bars, small islets and boats are not. Canals narrower than ~90 m are opened away first so they
    do not cut the mainland into 'islands'."""
    lab, _ = ndimage.label(~binary_opening(water, disk(1)), structure=EIGHT)
    keep = np.bincount(lab.ravel()) >= ISLAND_PX
    keep[np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])] = True
    keep[0] = False                        # label 0 is water
    return ndimage.binary_fill_holes(keep[lab])


def mainland_edge(water, mainland, k0):
    """Last sample before the mainland's river-facing edge: walking out from the open river (k0),
    islands, bars and short spurs are passed over; the first mainland run of MIN_LAND samples is the bank."""
    j, n = k0, len(water)
    if mainland[j]:                        # bank built out past the open-river edge: step back to water
        while j > 0 and mainland[j] and water[j]:   # a ditch folded into the mainland is not the river
            j -= 1
        while j > 0 and not water[j]:
            j -= 1
        return j if water[j] else None
    while j + MIN_LAND < n:
        if not mainland[j + 1]:
            j += 1
            continue
        run = mainland[j + 1:j + 1 + MIN_LAND]
        if run.all():
            return j
        j += 1 + np.nonzero(~run)[0][0]
    return None


def to_xy(rc, tf):
    return np.column_stack([tf.c + (rc[:, 1] + 0.5) * tf.a, tf.f + (rc[:, 0] + 0.5) * tf.e])


def to_rc(xy, tf):
    return (xy[:, 1] - tf.f) / tf.e - 0.5, (xy[:, 0] - tf.c) / tf.a - 0.5


def read(f):
    """MNDWI composite as float with NaN for nodata, clipped to [-1, 1]: pixels seen in 1-2 scenes with
    green + SWIR ~ 0 reach |MNDWI| >> 1 and stretch Otsu's histogram until the threshold collapses."""
    with rasterio.open(f) as src:
        a = src.read(1).astype(float)
        tf = src.transform
    a[a == -9999] = np.nan
    return np.clip(a, -1, 1), tf


def tile(reach):
    """(tiles.json, this reach's tile entry or None)."""
    cfg = json.loads(TILES.read_text()) if TILES.exists() else {'tiles': {}}
    return cfg, cfg['tiles'].get(reach)


def own_river(reach, shape, tf):
    """For a P1 tile, pixels nearer its own river's coarse centerline than the other river's (and, in a narrow
    tile, within NARROW_CORRIDOR of it); else all pixels."""
    cfg, t = tile(reach)
    if t is None:
        return np.ones(shape, bool)
    xy = to_xy(np.argwhere(np.ones(shape, bool)).astype(float), tf)
    d = {r: cKDTree(line).query(xy)[0].reshape(shape) for r, line in cfg['centerlines'].items()}
    own = t['river']
    inside = np.all([d[own] < v for r, v in d.items() if r != own], axis=0)
    return inside & (d[own] <= NARROW_CORRIDOR) if t.get('narrow') else inside


def load(reach):
    """Yearly composites of a reach, dropping years with too much nodata (e.g. Landsat 7 SLC-off only).
    In a P1 tile the other river's side is set to nodata so it never enters Otsu or the main-channel pick."""
    files = sorted(pathlib.Path('data/raw', reach).glob('mndwi_*.tif'))
    years = np.array([int(f.stem.split('_')[1]) for f in files])
    pairs = [read(f) for f in files]
    stack, tf = np.array([p[0] for p in pairs]), pairs[0][1]
    inside = own_river(reach, stack.shape[1:], tf)
    keep = np.isnan(stack[:, inside]).mean(axis=1) <= MAX_NODATA
    stack[:, ~inside] = np.nan
    if (~keep).any():
        print('dropped years (nodata share > %.0f%%): %s' % (100 * MAX_NODATA, years[~keep].tolist()))
    return years[keep], stack[keep], tf


def geometry(stack, tf, narrow=False):
    """Smoothed centerline and transect-sides (with the fixed open-river and belt masks sampled on them).
    Each side: (transect, side, cx, cy, nx, ny, r, c, ri, ci, k0, belt_d).
    narrow: a ~200 m wide channel (Hau above Chau Doc) - canal filter ~90 m instead of ~150 m, no open-river core,
    belt opened by 1 px instead of 4, centerline smoothed over 15 px instead of SMOOTH_PX (tight bends)."""
    open_px, belt_px, smooth = (1, 1, 15) if narrow else (2, 4, SMOOTH_PX)
    thr = [threshold_otsu(m[np.isfinite(m)]) for m in stack]
    # close 1-2 px gaps (bridges), then drop water narrower than ~150 m (canals) before picking the main body
    main_ch = np.array([largest(binary_opening(binary_closing(np.nan_to_num(m, nan=-1) > t, disk(1)), disk(open_px)))
                        for m, t in zip(stack, thr)])
    river = largest(main_ch.mean(0) >= 0.5)                                  # river water in >= half the years
    core = river if narrow else largest(binary_opening(river, disk(CORE_PX)))   # open river, fixed for all years
    belt = largest(binary_opening(ndimage.binary_fill_holes(river), disk(belt_px)))
    xy = to_xy(longest_path(skeletonize(belt)), tf)
    k = np.ones(smooth) / smooth
    xy = np.column_stack([np.convolve(np.pad(xy[:, i], smooth // 2, mode='edge'), k, 'valid') for i in (0, 1)])
    seg = np.r_[0, np.cumsum(np.hypot(*np.diff(xy, axis=0).T))]
    st = np.arange(SPACING, seg[-1] - SPACING, SPACING)
    cx, cy = np.interp(st, seg, xy[:, 0]), np.interp(st, seg, xy[:, 1])
    tx = np.interp(st + 50, seg, xy[:, 0]) - np.interp(st - 50, seg, xy[:, 0])
    ty = np.interp(st + 50, seg, xy[:, 1]) - np.interp(st - 50, seg, xy[:, 1])
    nrm = np.column_stack([-ty, tx]) / np.hypot(tx, ty)[:, None]   # left-hand normal (looking downstream-ish)
    d = np.arange(0, HALF + STEP, STEP)
    H, W = belt.shape
    sides = []
    for i in range(len(st)):
        for side, sgn in (('L', 1), ('R', -1)):
            pts = np.column_stack([cx[i], cy[i]]) + sgn * d[:, None] * nrm[i]
            r, c = to_rc(pts, tf)
            ri, ci = np.round(r).astype(int), np.round(c).astype(int)
            if not ((ri >= 0) & (ri < H) & (ci >= 0) & (ci < W)).all():
                continue
            in_belt = np.nonzero(belt[ri, ci])[0]
            in_core = np.nonzero(core[ri, ci])[0]
            if not len(in_core):                          # narrow branch: no open river, start from the river water
                in_core = np.nonzero(river[ri, ci])[0]
            sides.append((i, side, cx[i], cy[i], nrm[i, 0] * sgn, nrm[i, 1] * sgn, r, c, ri, ci,
                          in_core[-1] if len(in_core) else None,       # outer edge of the open river on this side
                          d[in_belt[-1]] if len(in_belt) else np.nan))
    return xy, sides


def positions(m, sides):
    """Bank distance from the centerline (m) per transect-side for one composite (own Otsu threshold)."""
    t = threshold_otsu(m[np.isfinite(m)])
    wat = np.nan_to_num(m, nan=-1) > t
    ml = mainland_mask(wat)
    d = np.arange(0, HALF + STEP, STEP)
    out = {}
    for i, side, _, _, _, _, r, c, ri, ci, k0, belt_d in sides:
        dist = np.nan
        mv = m[ri, ci]
        j = None if k0 is None else mainland_edge(wat[ri, ci], ml[ri, ci], k0)
        if j is not None and np.isfinite(mv[min(k0, j):j + MIN_LAND + 1]).all():
            lo, hi = max(j - REFINE, 0), min(j + REFINE, len(d) - 1)
            v = ndimage.map_coordinates(m, [r[lo:hi + 1], c[lo:hi + 1]], order=1, cval=np.nan)
            cross = np.nonzero((v[:-1] > t) & (v[1:] <= t))[0]   # water -> land
            dist = d[j] + STEP / 2
            if np.isfinite(v).all() and len(cross):
                k = cross[np.argmin(np.abs(lo + cross - j))]    # the crossing nearest the mainland edge
                dist = d[lo + k] + STEP * (v[k] - t) / (v[k] - v[k + 1])
            if not dist <= belt_d + BELT_MARGIN:
                dist = np.nan
        out[(i, side)] = dist
    return pd.Series(out, name='dist_m').rename_axis(['transect', 'side'])


def main():
    reach = sys.argv[1]
    years, stack, tf = load(reach)
    thr = np.array([threshold_otsu(m[np.isfinite(m)]) for m in stack])
    xy, sides = geometry(stack, tf, narrow=bool((tile(reach)[1] or {}).get('narrow')))
    pos = pd.concat({y: positions(m, sides) for y, m in zip(years, stack)}, names=['year']).reset_index()
    meta = pd.DataFrame([s[:6] for s in sides], columns=['transect', 'side', 'cx', 'cy', 'nx', 'ny'])
    df = meta.merge(pos, on=['transect', 'side']).sort_values(['transect', 'side', 'year'])

    # spikes: a jump > JUMP that reverts the next year is a detection error; a jump that persists is real change
    valid = df.dropna(subset=['dist_m'])
    g = valid.groupby(['transect', 'side']).dist_m
    prev, nxt = valid.dist_m - g.shift(1), g.shift(-1) - valid.dist_m
    df['spike'] = ((prev.abs() > JUMP) & (nxt.abs() > JUMP) & (np.sign(prev) != np.sign(nxt))).reindex(df.index,
                                                                                                       fill_value=False)
    out = pathlib.Path('data/processed', reach)
    out.mkdir(parents=True, exist_ok=True)
    df[['transect', 'side', 'cx', 'cy', 'nx', 'ny', 'year', 'dist_m', 'spike']].to_csv(out / 'bank_positions.csv',
                                                                                        index=False)

    # per transect-side robust trend (Theil-Sen) and robust residual scale, spikes left out
    fits = []
    for (i, side), g in df[df.dist_m.notna() & ~df.spike].groupby(['transect', 'side']):
        if len(g) < MIN_YEARS:
            continue
        slope, icpt, _, _ = theilslopes(g.dist_m, g.year)
        res = g.dist_m - (icpt + slope * g.year)
        fits.append((i, side, g.cx.iloc[0], g.cy.iloc[0], g.nx.iloc[0], g.ny.iloc[0], slope,
                     1.4826 * np.median(np.abs(res - np.median(res))), len(g), g.dist_m.diff().abs().max(),
                     int(df.spike[(df.transect == i) & (df.side == side)].sum())))
    fit = pd.DataFrame(fits, columns=['transect', 'side', 'cx', 'cy', 'nx', 'ny', 'lrr', 'sd_res', 'n', 'max_jump',
                                      'n_spikes'])
    fit['kind'] = np.where(fit.max_jump > JUMP, 'step', np.where(fit.sd_res > NONLIN, 'nonlinear', 'linear'))
    fit['stable'] = fit.kind == 'linear'
    fit.to_csv(out / 'trends.csv', index=False)

    n_all = df.groupby(['transect', 'side']).ngroups
    ok = fit[fit.stable]
    print(f'years {years.min()}-{years.max()} ({len(years)}), Otsu thr {thr.min():.2f}..{thr.max():.2f}')
    print(f'transect-sides: {n_all}, >= {MIN_YEARS} valid years: {len(fit)}; kinds: '
          + ', '.join(f'{k} {v} ({v / len(fit):.0%})' for k, v in fit.kind.value_counts().items())
          + f'; spikes removed: {int(df.spike.sum())}')
    print(f'linear, Theil-Sen m/yr: median |rate| {ok.lrr.abs().median():.1f}, p90 {ok.lrr.abs().quantile(.9):.1f}, '
          f'max erosion {ok.lrr.max():.1f}, max accretion {ok.lrr.min():.1f}')
    print(f'linear, robust residual scale (m): median {ok.sd_res.median():.1f}, '
          f'p25 {ok.sd_res.quantile(.25):.1f}, p75 {ok.sd_res.quantile(.75):.1f}')
    print(f'linear, share with |rate| > 5 m/yr: {(ok.lrr.abs() > 5).mean():.0%}')
    for h in (1, 3, 5):
        print(f'horizon {h} yr: share of linear with |rate|*h > 2*scale = {(ok.lrr.abs() * h > 2 * ok.sd_res).mean():.0%}'
              f', > 2*{NOISE_M} m measured noise = {(ok.lrr.abs() * h > 2 * NOISE_M).mean():.0%}')

    figs = pathlib.Path('results/p1/tiles' if reach.split('_')[0] in ('tien', 'hau') else 'results/p0')   # P1 tile quick-looks
    figs.mkdir(parents=True, exist_ok=True)
    H, W = stack.shape[1:]
    ext = (tf.c, tf.c + W * tf.a, tf.f + H * tf.e, tf.f)

    def bank_xy(g):
        return g.cx + g.nx * g.dist_m, g.cy + g.ny * g.dist_m

    fig, ax = plt.subplots(figsize=(9, 8.5))
    ax.imshow(stack[-1], cmap='gray', vmin=-0.6, vmax=0.6, extent=ext)
    ax.plot(xy[:, 0], xy[:, 1], color='white', lw=1, alpha=.7, label='centerline')
    for y, col in ((years.min(), '#0072B2'), (years.max(), '#E69F00')):
        bx, by = bank_xy(df[df.year == y])
        ax.scatter(bx, by, s=4, color=col, label=f'bank {y}')
    ax.set_title(f'{reach}: banks {years.min()} vs {years.max()} on MNDWI {years.max()}')
    ax.legend(loc='lower left', markerscale=4)
    ax.set_axis_off()
    fig.savefig(figs / f'{reach}_banks.png', dpi=110, bbox_inches='tight')

    fig, ax = plt.subplots(figsize=(9, 8.5))
    ax.imshow(stack[-1], cmap='gray', vmin=-0.6, vmax=0.6, extent=ext, alpha=.6)
    lim = np.nanpercentile(fit.lrr.abs(), 98)
    bx = fit.cx + fit.nx * df.groupby(['transect', 'side']).dist_m.median().loc[list(zip(fit.transect, fit.side))].values
    by = fit.cy + fit.ny * df.groupby(['transect', 'side']).dist_m.median().loc[list(zip(fit.transect, fit.side))].values
    sc = ax.scatter(bx, by, c=fit.lrr, cmap='coolwarm', vmin=-lim, vmax=lim, s=10)
    fig.colorbar(sc, ax=ax, shrink=.6, label='LRR 2000-2024 (m/yr), + = erosion')
    ax.set_title(f'{reach}: bank retreat rate per transect')
    ax.set_axis_off()
    fig.savefig(figs / f'{reach}_lrr.png', dpi=110, bbox_inches='tight')

    pick = pd.concat([ok.nlargest(4, 'lrr'), ok.nsmallest(2, 'lrr'), ok.iloc[(ok.lrr.abs()).argsort()[:2]]])
    fig, axes = plt.subplots(2, 4, figsize=(14, 6), sharex=True)
    for ax, (_, f) in zip(axes.ravel(), pick.iterrows()):
        g = df[(df.transect == f.transect) & (df.side == f.side)].dropna()
        ax.plot(g.year, g.dist_m, 'o', ms=4, color='#0072B2')
        s, b, _, _ = theilslopes(g.dist_m, g.year)
        ax.plot(g.year, b + s * g.year, color='#555555', lw=2)
        ax.set_title(f'T{f.transect}{f.side}: {f.lrr:+.1f} m/yr, sd {f.sd_res:.0f} m', fontsize=9)
        ax.grid(alpha=.3)
    for ax in axes[:, 0]:
        ax.set_ylabel('bank distance from centerline (m)')
    fig.tight_layout()
    fig.savefig(figs / f'{reach}_timeseries.png', dpi=110)


if __name__ == '__main__':
    main()
