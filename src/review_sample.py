"""Sample of transect-sides for the high-resolution accuracy check (served by review_server.py).

Usage: python src/review_sample.py sadec_caolanh
       python src/review_sample.py longxuyen --hot 3 --rest 3 --unstable 2 --no-explore
       python src/review_sample.py mythuan --transects 175 253 --hot 2 --rest 4 --unstable 2 --no-explore
       python src/review_sample.py sadec_caolanh --append --hot 0 --rest 0 --unstable 5 --no-explore
Reads data/processed/<reach>/bank_positions.csv and trends.csv; writes review_points.json.

Stratified random sample (fixed seed) of stable transect-sides: N_HOT hotspots (|lrr| > HOT) and
N_REST others, each stratum cut into equal-count chunks along the reach (both sides together) with
one pick per chunk, no two picks on the same side closer than GAP. Plus EXPLORE items from the Phu
Huu cluster (right bank), flagged explore=true and kept out of the accuracy statistics.
--unstable N adds N flagged-unstable transect-sides (max jump > 150 m), flagged unstable=true.
--transects A B samples only transects A..B (e.g. the part of a reach not covered by another one).
--append keeps the existing items unchanged (answers are keyed by id) and adds the new picks after them.
"""
import argparse
import json
import pathlib

import numpy as np
import pandas as pd
from rasterio.warp import transform

SEED, N_HOT, N_REST, HOT = 20261022, 15, 30, 5.0
SPACING, GAP = 100.0, 500.0             # transect spacing, min distance between picks on one side (m)
SEG_FACTOR = 1.5                        # transect segment drawn out to this x max detected distance
EXPLORE_SIDE, EXPLORE_T, EXPLORE_N, EXPLORE_MIN = 'R', (373, 410), 4, 12.0


def pick(cand, n, taken, rng):
    if n <= 0 or cand.empty:
        return []
    cand = cand.sort_values(['transect', 'side']).reset_index(drop=True)
    out = []
    # one pick per chunk; a chunk blocked by the spacing rule is made up from anywhere at the end
    for chunk in np.array_split(np.arange(len(cand)), n) + [np.arange(len(cand))] * n:
        if len(out) == n:
            break
        for j in rng.permutation(chunk):
            t, s = cand.transect[j], cand.side[j]
            if all(s != s2 or abs(t - t2) * SPACING >= GAP for t2, s2 in taken):
                taken.append((t, s))
                out.append(cand.loc[j])
                break
    return out


def latlon(x, y):
    lon, lat = transform('EPSG:32648', 'EPSG:4326', list(x), list(y))
    return [[round(a, 7), round(b, 7)] for a, b in zip(lat, lon)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('reach')
    ap.add_argument('--hot', type=int, default=N_HOT)
    ap.add_argument('--rest', type=int, default=N_REST)
    ap.add_argument('--unstable', type=int, default=0)
    ap.add_argument('--no-explore', action='store_true')
    ap.add_argument('--append', action='store_true')
    ap.add_argument('--transects', type=int, nargs=2, metavar=('A', 'B'))
    a = ap.parse_args()
    reach = a.reach
    out = pathlib.Path('data/processed', reach)
    pos = pd.read_csv(out / 'bank_positions.csv')
    tr = pd.read_csv(out / 'trends.csv')
    if a.transects:
        tr = tr[tr.transect.between(*a.transects)]
    ok = tr[tr.stable]
    rng = np.random.default_rng(SEED)
    old = json.loads((out / 'review_points.json').read_text())['items'] if a.append else []

    explore = []
    if not a.no_explore:
        ph = ok[(ok.side == EXPLORE_SIDE) & ok.transect.between(*EXPLORE_T) & (ok.lrr > EXPLORE_MIN)]
        ph = ph.sort_values('transect').reset_index(drop=True)
        explore = [ph.loc[j] for j in np.linspace(0, len(ph) - 1, EXPLORE_N).round().astype(int)]
    taken = [(i['transect'], i['side']) for i in old] + [(r.transect, r.side) for r in explore]
    hot = pick(ok[ok.lrr.abs() > HOT], a.hot, taken, rng)
    rest = pick(ok[ok.lrr.abs() <= HOT], a.rest, taken, rng)
    unstable = pick(tr[~tr.stable], a.unstable, taken, rng)
    main_items = sorted(hot + rest + unstable, key=lambda r: (r.transect, r.side))

    items = []
    for r, is_explore in [(r, False) for r in main_items] + [(r, True) for r in explore]:
        g = pos[(pos.transect == r.transect) & (pos.side == r.side)].dropna(subset=['dist_m'])
        seg = SEG_FACTOR * g.dist_m.max()
        ends = latlon([r.cx, r.cx + r.nx * seg], [r.cy, r.cy + r.ny * seg])
        banks = latlon(r.cx + r.nx * g.dist_m, r.cy + r.ny * g.dist_m)
        item = {
            'id': f'T{r.transect}{r.side}', 'transect': int(r.transect), 'side': r.side,
            'explore': is_explore, 'hotspot': bool(abs(r.lrr) > HOT),
            'lrr': round(float(r.lrr), 2), 'sd_res': round(float(r.sd_res), 2),
            'seg_len_m': round(float(seg), 1), 'segment': ends,
            'banks': [{'year': int(y), 'dist_m': round(float(d), 1), 'latlon': ll}
                      for y, d, ll in zip(g.year, g.dist_m, banks)],
        }
        if not r.stable:
            item.update(unstable=True, max_jump_m=round(float(r.max_jump), 1))
        items.append(item)
    ids = [i['id'] for i in old + items]
    assert len(ids) == len(set(ids)), 'duplicate item ids'
    (out / 'review_points.json').write_text(json.dumps({'reach': reach, 'items': old + items}, indent=1))

    m = [i for i in items if not i['explore']]
    print(f'{len(old)} kept + {len(m)} new items ({sum(i["hotspot"] for i in m)} hotspot, '
          f'{sum(i.get("unstable", False) for i in m)} unstable, '
          f'L {sum(i["side"] == "L" for i in m)} / R {sum(i["side"] == "R" for i in m)}: '
          f'{", ".join(i["id"] for i in m)}) + {len(items) - len(m)} explore '
          f'({", ".join(i["id"] for i in items if i["explore"])}) -> {out / "review_points.json"}')


if __name__ == '__main__':
    main()
