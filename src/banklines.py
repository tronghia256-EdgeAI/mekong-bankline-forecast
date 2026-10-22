"""P0: bank positions on transects from annual MNDWI composites, plus quick-look figures.

Usage: python src/banklines.py sadec_caolanh
Reads data/raw/<reach>/mndwi_*.tif; writes data/processed/<reach>/bank_positions.csv,
results/p0/<reach>_*.png and prints a detectability summary.

Method: per year, Otsu threshold on MNDWI -> largest connected water body (main channel).
Centerline = skeleton of the >=50%-of-years channel belt (islands filled, canals opened away).
Transects every 100 m, perpendicular to the smoothed centerline. On each side the bank is the
outermost main-channel sample seen from the land end, refined to sub-pixel by linear
interpolation of bilinear MNDWI across the threshold. Distance is measured from the
centerline, so erosion = distance increases.
"""
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
from scipy.stats import theilslopes
from skimage.filters import threshold_otsu
from skimage.morphology import binary_opening, disk, skeletonize

SPACING, HALF, STEP = 100.0, 3000.0, 5.0   # transect spacing, half-length, sample step (m)
SMOOTH_PX = 51                              # centerline moving-average window (skeleton pixels)
BELT_MARGIN = 500.0                         # reject banks this far beyond the belt edge (canal mouths)
REFINE = 6                                  # samples either side of the mask edge searched for the MNDWI crossing
JUMP = 150.0                                # year-to-year change (m) treated as a detection mode switch
MIN_YEARS = 15
EIGHT = np.ones((3, 3), bool)


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


def to_xy(rc, tf):
    return np.column_stack([tf.c + (rc[:, 1] + 0.5) * tf.a, tf.f + (rc[:, 0] + 0.5) * tf.e])


def to_rc(xy, tf):
    return (xy[:, 1] - tf.f) / tf.e - 0.5, (xy[:, 0] - tf.c) / tf.a - 0.5


def main():
    reach = sys.argv[1]
    files = sorted(pathlib.Path('data/raw', reach).glob('mndwi_*.tif'))
    years = np.array([int(f.stem.split('_')[1]) for f in files])
    stack = []
    for f in files:
        with rasterio.open(f) as src:
            a = src.read(1).astype(float)
            tf = src.transform
        a[a == -9999] = np.nan
        stack.append(a)
    stack = np.array(stack)
    thr = np.array([threshold_otsu(m[np.isfinite(m)]) for m in stack])
    main_ch = np.array([largest(np.nan_to_num(m, nan=-1) > t) for m, t in zip(stack, thr)])

    belt = largest(main_ch.mean(0) >= 0.5)
    belt = largest(binary_opening(ndimage.binary_fill_holes(belt), disk(4)))
    rc = longest_path(skeletonize(belt))
    xy = to_xy(rc, tf)
    k = np.ones(SMOOTH_PX) / SMOOTH_PX
    xy = np.column_stack([np.convolve(np.pad(xy[:, i], SMOOTH_PX // 2, mode='edge'), k, 'valid')
                          for i in (0, 1)])
    seg = np.r_[0, np.cumsum(np.hypot(*np.diff(xy, axis=0).T))]
    st = np.arange(SPACING, seg[-1] - SPACING, SPACING)
    cx, cy = np.interp(st, seg, xy[:, 0]), np.interp(st, seg, xy[:, 1])
    tx = np.interp(st + 50, seg, xy[:, 0]) - np.interp(st - 50, seg, xy[:, 0])
    ty = np.interp(st + 50, seg, xy[:, 1]) - np.interp(st - 50, seg, xy[:, 1])
    nrm = np.column_stack([-ty, tx]) / np.hypot(tx, ty)[:, None]   # left-hand normal (looking downstream-ish)

    d = np.arange(0, HALF + STEP, STEP)
    H, W = belt.shape
    rows = []
    for i in range(len(st)):
        for side, sgn in (('L', 1), ('R', -1)):
            pts = np.column_stack([cx[i], cy[i]]) + sgn * d[:, None] * nrm[i]
            r, c = to_rc(pts, tf)
            ri, ci = np.round(r).astype(int), np.round(c).astype(int)
            inside = (ri >= 0) & (ri < H) & (ci >= 0) & (ci < W)
            if not inside.all():
                continue
            in_belt = np.nonzero(belt[ri, ci])[0]
            belt_d = d[in_belt[-1]] if len(in_belt) else np.nan
            for y, m, mc, t in zip(years, stack, main_ch, thr):
                w = np.nonzero(mc[ri, ci])[0]
                dist = np.nan
                if len(w) and w[-1] < len(d) - 1:
                    j = w[-1]
                    lo, hi = max(j - REFINE, 0), min(j + REFINE, len(d) - 1)
                    v = ndimage.map_coordinates(m, [r[lo:hi + 1], c[lo:hi + 1]], order=1, cval=np.nan)
                    cross = np.nonzero((v[:-1] > t) & (v[1:] <= t))[0]   # water -> land, outermost
                    if np.isfinite(v).all() and len(cross):
                        k = cross[-1]
                        dist = d[lo + k] + STEP * (v[k] - t) / (v[k] - v[k + 1])
                    if not dist <= belt_d + BELT_MARGIN:
                        dist = np.nan
                rows.append((i, side, cx[i], cy[i], nrm[i, 0] * sgn, nrm[i, 1] * sgn, y, dist))

    df = pd.DataFrame(rows, columns=['transect', 'side', 'cx', 'cy', 'nx', 'ny', 'year', 'dist_m'])
    out = pathlib.Path('data/processed', reach)
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / 'bank_positions.csv', index=False)

    # per transect-side robust trend (Theil-Sen) and robust residual scale (upper bound on measurement noise)
    fits = []
    for (i, side), g in df.dropna().groupby(['transect', 'side']):
        if len(g) < MIN_YEARS:
            continue
        slope, icpt, _, _ = theilslopes(g.dist_m, g.year)
        res = g.dist_m - (icpt + slope * g.year)
        fits.append((i, side, g.cx.iloc[0], g.cy.iloc[0], g.nx.iloc[0], g.ny.iloc[0], slope,
                     1.4826 * np.median(np.abs(res - np.median(res))), len(g), g.dist_m.diff().abs().max()))
    fit = pd.DataFrame(fits, columns=['transect', 'side', 'cx', 'cy', 'nx', 'ny', 'lrr', 'sd_res', 'n', 'max_jump'])
    fit['stable'] = fit.max_jump <= JUMP
    fit.to_csv(out / 'trends.csv', index=False)

    n_all = df.groupby(['transect', 'side']).ngroups
    ok = fit[fit.stable]
    print(f'years {years.min()}-{years.max()} ({len(years)}), Otsu thr {thr.min():.2f}..{thr.max():.2f}')
    print(f'transect-sides: {n_all}, >= {MIN_YEARS} valid years: {len(fit)}, '
          f'no jump > {JUMP:.0f} m: {len(ok)} ({len(ok) / len(fit):.0%})')
    print(f'stable, Theil-Sen m/yr: median |rate| {ok.lrr.abs().median():.1f}, p90 {ok.lrr.abs().quantile(.9):.1f}, '
          f'max erosion {ok.lrr.max():.1f}, max accretion {ok.lrr.min():.1f}')
    print(f'stable, robust residual scale (m): median {ok.sd_res.median():.1f}, '
          f'p25 {ok.sd_res.quantile(.25):.1f}, p75 {ok.sd_res.quantile(.75):.1f}')
    print(f'stable, share with |rate| > 5 m/yr: {(ok.lrr.abs() > 5).mean():.0%}')
    for h in (1, 3, 5):
        print(f'horizon {h} yr: share of stable with |rate|*h > 2*scale = {(ok.lrr.abs() * h > 2 * ok.sd_res).mean():.0%}')

    figs = pathlib.Path('results/p0')
    figs.mkdir(parents=True, exist_ok=True)
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
