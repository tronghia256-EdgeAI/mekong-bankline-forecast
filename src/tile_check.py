"""P1 check: do the stitched full-river banks reproduce the P0 reaches and the hand clicks?

Usage: python src/tile_check.py
For every P0 transect-side, the nearest stitched transect on the same physical side (centre <= 100 m away,
normals within ~25 deg) gives its bank point, projected on the P0 transect so both are distances from the P0
centerline. Compares positions (same year), linear trend rates and errors against the clicks in
data/processed/<reach>/accuracy_review.csv; also narrow vs normal mode where hau_02 and hau_03 overlap.
Writes results/p1/tile_check.md.
"""
import json
import pathlib

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

P0 = {'sadec_caolanh': 'tien', 'mythuan': 'tien', 'longxuyen': 'hau'}


def match(p0, st):
    """P0 transect-sides -> stitched (transect, side) on the same bank."""
    a = p0.drop_duplicates(['transect', 'side'])[['transect', 'side', 'cx', 'cy', 'nx', 'ny']]
    b = st.drop_duplicates(['transect', 'side'])[['transect', 'side', 'cx', 'cy', 'nx', 'ny']].reset_index(drop=True)
    d, k = cKDTree(b[['cx', 'cy']].to_numpy()).query(a[['cx', 'cy']].to_numpy(), k=4)
    rows = []
    for (_, r), dd, kk in zip(a.iterrows(), d, k):
        for di, ki in zip(dd, kk):
            if di <= 100 and r.nx * b.nx[ki] + r.ny * b.ny[ki] > 0.9:
                rows.append((r.transect, r.side, b.transect[ki], b.side[ki]))
                break
    return pd.DataFrame(rows, columns=['transect', 'side', 's_transect', 's_side'])


def project(p0, st, m):
    """Stitched bank distance measured along the P0 transect, per P0 transect-side and year."""
    s = st.rename(columns={'transect': 's_transect', 'side': 's_side', 'cx': 'scx', 'cy': 'scy', 'nx': 'snx',
                           'ny': 'sny', 'dist_m': 's_dist'})[['s_transect', 's_side', 'year', 'scx', 'scy', 'snx',
                                                              'sny', 's_dist']]
    df = p0.merge(m, on=['transect', 'side']).merge(s, on=['s_transect', 's_side', 'year'])
    bx, by = df.scx + df.snx * df.s_dist, df.scy + df.sny * df.s_dist
    df['s_on_p0'] = (bx - df.cx) * df.nx + (by - df.cy) * df.ny
    return df


def main():
    lines = ['# P1 tiles vs P0 reaches', '',
             'Stitched full-river output (`src/stitch.py`) matched to each P0 transect-side (nearest stitched transect on '
             'the same bank, centre <= 100 m). diff = stitched - P0, as distances along the P0 transect (m).', '',
             '| Reach | Matched sides | Position pairs | Median abs diff | Share abs diff <= 15 m | Linear sides both | '
             'Median abs rate diff (m/yr) | Clicks n | Click RMSE P0 | Click RMSE stitched |',
             '|---|---|---|---|---|---|---|---|---|---|']
    for reach, river in P0.items():
        src, dst = pathlib.Path('data/processed', reach), pathlib.Path('data/processed', river)
        p0, st = pd.read_csv(src / 'bank_positions.csv'), pd.read_csv(dst / 'bank_positions.csv')
        m = match(p0, st)
        df = project(p0, st, m).dropna(subset=['dist_m', 's_on_p0'])
        diff = (df.s_on_p0 - df.dist_m).abs()
        t0, ts = pd.read_csv(src / 'trends.csv'), pd.read_csv(dst / 'trends.csv')
        tr = (t0[t0.stable].merge(m, on=['transect', 'side'])
              .merge(ts[ts.stable][['transect', 'side', 'lrr']].rename(columns={'transect': 's_transect', 'side': 's_side',
                                                                                 'lrr': 's_lrr'}),
                     on=['s_transect', 's_side']))
        clicks = pd.read_csv(src / 'accuracy_review.csv', encoding='utf-8-sig').drop_duplicates('id', keep='last')
        flagged = {i['id'] for i in json.loads((src / 'review_points.json').read_text())['items'] if i.get('unstable')}
        clicks = clicks[clicks.verdict.eq('clicked') & ~clicks.explore.astype(str).eq('True') & ~clicks.id.isin(flagged)]
        c = clicks.rename(columns={'compared_year': 'year'})[['transect', 'side', 'year', 'user_dist_m']].merge(
            df[['transect', 'side', 'year', 'dist_m', 's_on_p0']], on=['transect', 'side', 'year']).dropna()
        rmse = lambda e: np.sqrt((e ** 2).mean())
        lines.append(f'| {reach} | {len(m)} of {p0.groupby(["transect", "side"]).ngroups} | {len(df)} | {diff.median():.1f} | '
                     f'{(diff <= 15).mean():.0%} | {len(tr)} | {(tr.lrr - tr.s_lrr).abs().median():.2f} | {len(c)} | '
                     f'{rmse(c.dist_m - c.user_dist_m):.1f} | {rmse(c.s_on_p0 - c.user_dist_m):.1f} |')
    # narrow mode (Hau above Chau Doc) vs normal mode where the tiles overlap below Chau Doc
    a, b = (pd.read_csv(f'data/processed/{t}/bank_positions.csv') for t in ('hau_02', 'hau_03'))
    m = match(a, b)
    df = project(a, b, m).dropna(subset=['dist_m', 's_on_p0'])
    diff = df.s_on_p0 - df.dist_m
    lines += ['', '## Narrow vs normal mode (Hau: hau_02 narrow vs hau_03 normal where they overlap below Chau Doc)', '',
              f'Matched sides {len(m)}, position pairs {len(df)}: median diff (normal - narrow) {diff.median():+.1f} m, '
              f'median abs {diff.abs().median():.1f} m, share abs <= 15 m {(diff.abs() <= 15).mean():.0%}.']
    text = '\n'.join(lines) + '\n'
    print(text)
    pathlib.Path('results/p1').mkdir(parents=True, exist_ok=True)
    pathlib.Path('results/p1/tile_check.md').write_text(text, encoding='utf-8')


if __name__ == '__main__':
    main()
