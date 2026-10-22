"""Sample of transect-sides for the high-resolution accuracy check (served by review_server.py).

Usage: python src/review_sample.py sadec_caolanh
Reads data/processed/<reach>/bank_positions.csv and trends.csv; writes review_points.json.

Stratified random sample (fixed seed) of stable transect-sides: N_HOT hotspots (|lrr| > HOT) and
N_REST others, each stratum cut into equal-count chunks along the reach (both sides together) with
one pick per chunk, no two picks on the same side closer than GAP. Plus EXPLORE items from the Phu
Huu cluster (right bank), flagged explore=true and kept out of the accuracy statistics.
"""
import json
import pathlib
import sys

import numpy as np
import pandas as pd
from rasterio.warp import transform

SEED, N_HOT, N_REST, HOT = 20261022, 15, 30, 5.0
SPACING, GAP = 100.0, 500.0             # transect spacing, min distance between picks on one side (m)
SEG_FACTOR = 1.5                        # transect segment drawn out to this x max detected distance
EXPLORE_SIDE, EXPLORE_T, EXPLORE_N, EXPLORE_MIN = 'R', (373, 410), 4, 12.0


def pick(cand, n, taken, rng):
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
    reach = sys.argv[1]
    out = pathlib.Path('data/processed', reach)
    pos = pd.read_csv(out / 'bank_positions.csv')
    tr = pd.read_csv(out / 'trends.csv')
    ok = tr[tr.stable]
    rng = np.random.default_rng(SEED)

    ph = ok[(ok.side == EXPLORE_SIDE) & ok.transect.between(*EXPLORE_T) & (ok.lrr > EXPLORE_MIN)]
    ph = ph.sort_values('transect').reset_index(drop=True)
    explore = [ph.loc[j] for j in np.linspace(0, len(ph) - 1, EXPLORE_N).round().astype(int)]
    taken = [(r.transect, r.side) for r in explore]
    hot = pick(ok[ok.lrr.abs() > HOT], N_HOT, taken, rng)
    rest = pick(ok[ok.lrr.abs() <= HOT], N_REST, taken, rng)
    main_items = sorted(hot + rest, key=lambda r: (r.transect, r.side))

    items = []
    for r, is_explore in [(r, False) for r in main_items] + [(r, True) for r in explore]:
        g = pos[(pos.transect == r.transect) & (pos.side == r.side)].dropna(subset=['dist_m'])
        seg = SEG_FACTOR * g.dist_m.max()
        ends = latlon([r.cx, r.cx + r.nx * seg], [r.cy, r.cy + r.ny * seg])
        banks = latlon(r.cx + r.nx * g.dist_m, r.cy + r.ny * g.dist_m)
        items.append({
            'id': f'T{r.transect}{r.side}', 'transect': int(r.transect), 'side': r.side,
            'explore': is_explore, 'hotspot': bool(abs(r.lrr) > HOT),
            'lrr': round(float(r.lrr), 2), 'sd_res': round(float(r.sd_res), 2),
            'seg_len_m': round(float(seg), 1), 'segment': ends,
            'banks': [{'year': int(y), 'dist_m': round(float(d), 1), 'latlon': ll}
                      for y, d, ll in zip(g.year, g.dist_m, banks)],
        })
    (out / 'review_points.json').write_text(json.dumps({'reach': reach, 'items': items}, indent=1))

    m = [i for i in items if not i['explore']]
    print(f'{len(m)} items ({sum(i["hotspot"] for i in m)} hotspot, '
          f'L {sum(i["side"] == "L" for i in m)} / R {sum(i["side"] == "R" for i in m)}, '
          f'T{m[0]["transect"]}-T{m[-1]["transect"]}) + {len(items) - len(m)} explore '
          f'({", ".join(i["id"] for i in items if i["explore"])}) -> {out / "review_points.json"}')


if __name__ == '__main__':
    main()
