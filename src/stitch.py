"""P1: join the per-tile outputs of banklines.py into one table per river.

Usage: python src/stitch.py tien|hau
Reads data/tiles.json and data/processed/<tile>/{bank_positions,trends}.csv; writes
data/processed/<river>/{bank_positions,trends}.csv and results/p1/<river>_lrr.png, and prints coverage.
Each transect is placed on the river's coarse centerline (chainage_m from the upstream end at the border) and kept
only by the tile whose centre is nearest in chainage, so overlaps are not counted twice; upstream of the river's
narrow_until_m only narrow-mode tiles count, below it only normal tiles. Sides are relabelled so
that L/R are the left/right banks looking downstream. Transects beyond either end of the river are dropped; bank points outside Vietnam are left for reach_units.py.
"""
import json
import pathlib
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

MAX_OFF = 5000.0   # transect centre to coarse centerline (m): a fine centerline through a big island sits ~3 km off


def chainage(line, s_line, pts):
    """Distance along the polyline of each point's projection, and its offset from the line (m).
    Points projecting past either end get NaN."""
    a, b = line[:-1], line[1:]
    ab = b - a
    t = np.einsum('pij,ij->pi', pts[:, None] - a, ab) / (ab ** 2).sum(1)
    inside = (t >= 0) & (t <= 1)
    off = np.hypot(*(pts[:, None] - (a + np.clip(t, 0, 1)[..., None] * ab)).transpose(2, 0, 1))
    off[~inside] = np.inf
    k = off.argmin(1)
    i = np.arange(len(pts))
    s = s_line[k] + t[i, k] * np.hypot(*ab[k].T)
    return np.where(np.isfinite(off[i, k]), s, np.nan), off[i, k]


def main():
    river = sys.argv[1]
    cfg = json.loads(pathlib.Path('data/tiles.json').read_text())
    line = np.array(cfg['centerlines'][river])
    s_line = np.r_[0, np.cumsum(np.hypot(*np.diff(line, axis=0).T))]
    tiles = {k: v for k, v in cfg['tiles'].items() if v['river'] == river}
    names = list(tiles)
    centres = np.array([v['chainage_m'] for v in tiles.values()], float)
    narrow = np.array([v.get('narrow', False) for v in tiles.values()])
    narrow_to = cfg.get('narrow_until_m', {}).get(river, 0)
    pos, fit = [], []
    for name in names:
        src = pathlib.Path('data/processed', name)
        bp, tr = pd.read_csv(src / 'bank_positions.csv'), pd.read_csv(src / 'trends.csv')
        t = bp.drop_duplicates('transect')[['transect', 'cx', 'cy']]
        t['chainage_m'], off = chainage(line, s_line, t[['cx', 'cy']].to_numpy())
        t = t[off <= MAX_OFF]   # banks outside Vietnam get no commune in reach_units.py (border rivers keep their VN bank)
        flip = np.corrcoef(t.transect, t.chainage_m)[0, 1] < 0    # this tile's centerline runs upstream
        # nearest tile centre among tiles of the right mode (narrow tiles upstream of narrow_to, normal tiles below)
        s = t.chainage_m.to_numpy()[:, None]
        own = t[np.array([names[i] for i in np.where(narrow[None] == (s < narrow_to), np.abs(s - centres), np.inf)
                          .argmin(1)]) == name]
        for df, out in ((bp, pos), (tr, fit)):
            df = df.merge(own[['transect', 'chainage_m']], on='transect').rename(columns={'transect': 'tile_transect'})
            if flip:
                df['side'] = df.side.map({'L': 'R', 'R': 'L'})
            out.append(df.assign(tile=name))
        print(f'{name}: {len(own)} transects kept of {bp.transect.nunique()}{" (flipped)" if flip else ""}')
    pos, fit = pd.concat(pos), pd.concat(fit)
    key = pos.drop_duplicates(['tile', 'tile_transect']).sort_values('chainage_m')
    ids = {k: i for i, k in enumerate(zip(key.tile, key.tile_transect))}
    for df in (pos, fit):
        df.insert(0, 'transect', [ids[k] for k in zip(df.tile, df.tile_transect)])
    pos = pos.sort_values(['transect', 'side', 'year'])
    fit = fit.sort_values(['transect', 'side'])
    out = pathlib.Path('data/processed', river)
    out.mkdir(parents=True, exist_ok=True)
    first = ['transect', 'side', 'chainage_m', 'tile', 'tile_transect']
    pos[first + [c for c in pos.columns if c not in first]].to_csv(out / 'bank_positions.csv', index=False)
    fit[first + [c for c in fit.columns if c not in first]].to_csv(out / 'trends.csv', index=False)

    gaps = np.diff(key.chainage_m.to_numpy())
    n_sides = pos.groupby(['transect', 'side']).ngroups
    print(f'{river}: {len(ids)} transects over {s_line[-1] / 1e3:.1f} km, largest chainage gap {gaps.max():.0f} m '
          f'(gaps > 300 m: {(gaps > 300).sum()}); transect-sides {n_sides}, with a trend {len(fit)}; kinds: '
          + ', '.join(f'{k} {v} ({v / len(fit):.0%})' for k, v in fit.kind.value_counts().items()))

    fig, ax = plt.subplots(figsize=(9, 9))
    ax.plot(line[:, 0], line[:, 1], color='0.7', lw=.8)
    ok = fit[fit.stable]
    sc = ax.scatter(ok.cx + ok.nx * 1500, ok.cy + ok.ny * 1500, c=ok.lrr.clip(-15, 15), cmap='RdBu_r', s=4)
    bad = fit[~fit.stable]
    ax.scatter(bad.cx + bad.nx * 1500, bad.cy + bad.ny * 1500, c='k', s=1, label='step / non-linear')
    fig.colorbar(sc, ax=ax, shrink=.6, label='Theil-Sen rate (m/yr, + = erosion)')
    ax.set_aspect('equal')
    ax.legend(loc='upper right')
    ax.set_title(f'{river}: bank change 2000-2024 (points offset 1.5 km to each side)')
    figs = pathlib.Path('results/p1')
    figs.mkdir(parents=True, exist_ok=True)
    fig.savefig(figs / f'{river}_lrr.png', dpi=120, bbox_inches='tight')


if __name__ == '__main__':
    main()
