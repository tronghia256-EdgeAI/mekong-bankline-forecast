"""P3 R4: build the data release (Zenodo) in release/ (gitignored).

Usage: python src/release.py
Writes release/data/: banks_annual.csv, banklines.geojson, trends.csv, units_2km.csv, inventory.csv,
unreported_reaches.csv, accuracy_clicks.csv; release/README.md and release/LICENSE-data.txt are copied from
docs/release_README.md. Coordinates WGS84 (EPSG:4326); distances in m along each transect from its origin.
"""
import json
import pathlib
import shutil

import numpy as np
import pandas as pd
from rasterio.warp import transform

OUT = pathlib.Path('release')
GAP_M = 300.0   # bankline polyline broken where consecutive bank points are farther apart


def channels():
    cfg = json.loads(pathlib.Path('data/tiles.json').read_text())
    isl = sorted(k for k, v in cfg['islands'].items() if pathlib.Path('data/processed', k, 'bank_positions.csv').exists())
    return [('tien', 'tien'), ('hau', 'hau')] + [(k, cfg['islands'][k]['parent']) for k in isl]


def lonlat(x, y):
    lon, lat = transform('EPSG:32648', 'EPSG:4326', list(x), list(y))
    return np.round(lon, 6), np.round(lat, 6)


def banks():
    u = pd.read_csv('data/processed/units.csv')
    parts, trends = [], []
    for ch, river in channels():
        b = pd.read_csv(f'data/processed/{ch}/bank_positions.csv')
        t = pd.read_csv(f'data/processed/{ch}/trends.csv')
        b = b[b.dist_m.notna()].copy()
        b['bank_x'], b['bank_y'] = b.cx + b.nx * b.dist_m, b.cy + b.ny * b.dist_m
        b['lon'], b['lat'] = lonlat(b.bank_x, b.bank_y)
        b['river'], b['channel'] = river, ch
        parts.append(b[['river', 'channel', 'transect', 'side', 'year', 'dist_m', 'spike', 'lon', 'lat', 'bank_x', 'bank_y']])
        t['lon0'], t['lat0'] = lonlat(t.cx, t.cy)   # transect origin
        t['river'], t['channel'] = river, ch
        trends.append(t[['river', 'channel', 'transect', 'side', 'lon0', 'lat0', 'nx', 'ny', 'lrr', 'sd_res', 'n',
                         'max_jump', 'n_spikes', 'kind', 'stable']])
    b = pd.concat(parts, ignore_index=True)
    t = pd.concat(trends, ignore_index=True).rename(columns={'lrr': 'rate_m_per_yr', 'sd_res': 'robust_resid_m'})
    key = ['channel', 'transect', 'side']
    meta = u[key + ['commune', 'district', 'province', 'in_scope', 'unit_2km']]
    b = b.merge(meta, on=key, how='left')
    t = t.merge(meta, on=key, how='left')
    for d in (b, t):   # False: ring bank dropped as a duplicate of a main-channel or other island bank (reach_units.py)
        d['in_units'] = d.unit_2km.notna()
    b['dist_m'], b['lon'] = b.dist_m.round(1), b.lon
    for c in ('rate_m_per_yr', 'robust_resid_m', 'max_jump'):
        t[c] = t[c].round(2)
    return b, t


def lines(b):
    """One feature per (channel, side, year): MultiLineString of consecutive non-spike bank points."""
    feats = []
    b = b[~b.spike].sort_values(['channel', 'side', 'year', 'transect'])
    for (ch, side, yr), g in b.groupby(['channel', 'side', 'year']):
        xy = g[['bank_x', 'bank_y']].to_numpy()
        tr = g.transect.to_numpy()
        brk = (np.hypot(*np.diff(xy, axis=0).T) > GAP_M) | (np.diff(tr) != 1)
        segs = np.split(g[['lon', 'lat']].to_numpy(), np.flatnonzero(brk) + 1)
        segs = [s.tolist() for s in segs if len(s) >= 2]
        if segs:
            feats.append({'type': 'Feature', 'properties': {'channel': ch, 'side': side, 'year': int(yr)},
                          'geometry': {'type': 'MultiLineString', 'coordinates': segs}})
    return {'type': 'FeatureCollection', 'features': feats}


def clicks():
    """The clicks of fig04 (figures.clicks: final stitched banks; P0-reach clicks measured along the P0 transect)."""
    import figures
    groups = [('Tien main', 'sadec_caolanh', None), ('Tien main', 'mythuan', None), ('Tien main', 'tien', None),
              ('Hau wide', 'longxuyen', None), ('Hau wide', 'hau', False), ('Hau narrow', 'hau', True),
              ('Island channels', 'islands', None)]
    rows = []
    for g, reach, narrow in groups:
        a = figures.clicks(reach, narrow).assign(group=g, review_reach=reach)
        rows.append(a.rename(columns={'dist_m': 'landsat_dist_m', 'user_dist_m': 'click_dist_m'}))
    c = pd.concat(rows, ignore_index=True)[['id', 'group', 'review_reach', 'transect', 'side', 'compared_year',
                                            'imagery_release', 'imagery_capture_date', 'imagery_source',
                                            'click_dist_m', 'landsat_dist_m']]
    c['landsat_minus_click_m'] = (c.landsat_dist_m - c.click_dist_m).round(1)
    c[['click_dist_m', 'landsat_dist_m']] = c[['click_dist_m', 'landsat_dist_m']].round(1)
    return c


def main():
    (OUT / 'data').mkdir(parents=True, exist_ok=True)
    b, t = banks()
    b.drop(columns=['bank_x', 'bank_y']).to_csv(OUT / 'data/banks_annual.csv', index=False, encoding='utf-8')
    (OUT / 'data/banklines.geojson').write_text(json.dumps(lines(b), separators=(',', ':')), encoding='utf-8')
    t.to_csv(OUT / 'data/trends.csv', index=False, encoding='utf-8')
    s = pd.read_csv('data/processed/sat_labels_2km.csv')
    c = pd.read_csv('data/processed/covariates_2km.csv').drop(columns=['river', 'channel', 'side', 'n_points'])
    s.merge(c, on='unit', how='left').to_csv(OUT / 'data/units_2km.csv', index=False, encoding='utf-8')
    inv = pd.read_csv('data/hotspots/inventory.csv')
    inv.drop(columns=['source_file', 'dedup_key', 'lat', 'lon']).to_csv(OUT / 'data/inventory.csv', index=False,
                                                                       encoding='utf-8')
    om = pd.read_csv('data/processed/explore_reporting_omitted.csv').drop(columns=['shared_with'])
    key = pd.read_csv('data/processed/visual_check/key.csv')
    va = pd.read_csv('data/processed/visual_check/answers.csv', encoding='utf-8-sig').drop_duplicates('id', keep='last')
    v = key.merge(va, on='id')[['unit', 'q1_loss', 'q2_protection', 'note', 'old_capture', 'new_capture']]
    om.merge(v, on='unit', how='left').rename(columns={'q1_loss': 'visual_loss', 'q2_protection': 'visual_protection',
                                                        'note': 'visual_note'}) \
        .to_csv(OUT / 'data/unreported_reaches.csv', index=False, encoding='utf-8')
    cl = clicks()
    cl.to_csv(OUT / 'data/accuracy_clicks.csv', index=False, encoding='utf-8')
    shutil.copy('docs/release_README.md', OUT / 'README.md')
    print(f'banks_annual {len(b)} rows, {b.groupby(["channel", "transect", "side"]).ngroups} transect-sides, '
          f'years {b.year.min()}-{b.year.max()}; trends {len(t)}; clicks {len(cl)} '
          f'(RMSE {np.sqrt(np.nanmean(cl.landsat_minus_click_m ** 2)):.1f} m); unreported {len(om)}')
    for f in sorted((OUT / 'data').iterdir()):
        print(f'{f.name:28s} {f.stat().st_size / 1e6:6.1f} MB')


if __name__ == '__main__':
    main()
