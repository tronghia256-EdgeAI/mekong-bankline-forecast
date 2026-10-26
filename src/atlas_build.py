"""P3 R5: build the data files of the static web atlas (docs/atlas/data/) from the release and the 2027 forecast.

Usage: python src/atlas_build.py   (needs release/data/* from src/release.py and data/processed/forecast_2027.csv from
       src/forecast_2027.py; runs src/release.py first if release/ is missing)
Writes docs/atlas/data/:
  banks_<year>.json   annual banklines of one year (GeoJSON, lon/lat 5 decimals)
  units.json          2 km units as lines (median bank position 2022-24 per transect-side) with satellite window retreat,
                      label, communes, reported inventory rows, unreported-reach visual check
  forecast.json       per unit: 2024 bank (3-yr mean) and its landward 90% bound for 2027 (GBT, Mondrian), with numbers
  trends.json         Theil-Sen rate per transect-side at its median bank point: [lat, lon, rate, kind]
  meta.json           years, accuracy (RMSE per click group), forecast half-widths, build date
"""
import datetime
import json
import pathlib
import subprocess
import sys

import numpy as np
import pandas as pd
from rasterio.warp import transform

REL, OUT = pathlib.Path('release/data'), pathlib.Path('docs/atlas/data')
GAP_M = 300.0
KEY = ['channel', 'transect', 'side']
GROUP_ORDER = ['Tien main', 'Hau wide', 'Hau narrow', 'Island']


def dump(name, obj):
    (OUT / name).write_text(json.dumps(obj, separators=(',', ':'), ensure_ascii=False), encoding='utf-8')


def r5(a):
    return np.round(np.asarray(a, float), 5)


def segments(g, x='x', y='y'):
    """Split points ordered by transect (columns lon, lat and x, y in m) where consecutive points are > GAP_M apart;
    returns lists of [lon, lat]. A lone point becomes a zero-length segment (drawn as a dot with round caps)."""
    xy = g[[x, y]].to_numpy()
    brk = np.hypot(*np.diff(xy, axis=0).T) > GAP_M
    segs = np.split(np.c_[r5(g.lon), r5(g.lat)], np.flatnonzero(brk) + 1)
    return [(s if len(s) >= 2 else np.r_[s, s]).tolist() for s in segs]


def utm(lon, lat):
    x, y = transform('EPSG:4326', 'EPSG:32648', list(lon), list(lat))
    return np.array(x), np.array(y)


def wgs(x, y):
    lon, lat = transform('EPSG:32648', 'EPSG:4326', list(x), list(y))
    return np.array(lon), np.array(lat)


def nz(v, d=1):
    return None if pd.isna(v) else round(float(v), d)


def banks_by_year():
    gj = json.loads((REL / 'banklines.geojson').read_text(encoding='utf-8'))
    years = sorted({f['properties']['year'] for f in gj['features']})
    for yr in years:
        feats = [{'type': 'Feature', 'properties': {'c': f['properties']['channel'], 's': f['properties']['side']},
                  'geometry': {'type': 'MultiLineString',
                               'coordinates': [r5(s).tolist() for s in f['geometry']['coordinates']]}}
                 for f in gj['features'] if f['properties']['year'] == yr]
        dump(f'banks_{yr}.json', {'type': 'FeatureCollection', 'features': feats})
    return years


def inventory():
    inv = pd.read_csv(REL / 'inventory.csv')
    inv = inv[inv.use_in_analysis.astype(bool) & inv.units_2km.notna()]
    rows = {}
    for r in inv.itertuples():
        quote = r.quote if isinstance(r.quote, str) else (r.hamlet_or_landmark if isinstance(r.hamlet_or_landmark, str)
                                                           else '')
        item = {'id': r.site_id, 'type': r.source_type, 'year': None if pd.isna(r.event_year) else int(r.event_year),
                'date': r.source_date if isinstance(r.source_date, str) else '',
                'url': r.source_url if isinstance(r.source_url, str) and r.source_url.startswith('http') else '',
                'q': quote[:220]}
        for un in r.units_2km.split(';'):
            rows.setdefault(un.strip(), []).append(item)
    return rows


def main():
    if not (REL / 'banks_annual.csv').exists():
        subprocess.run([sys.executable, 'src/release.py'], check=True)
    OUT.mkdir(parents=True, exist_ok=True)
    years = banks_by_year()

    b = pd.read_csv(REL / 'banks_annual.csv', low_memory=False)
    b['in_scope'] = b.in_scope.astype(str) == 'True'      # NaN where the point has no unit
    b['spike'] = b.spike.astype(str) == 'True'
    t = pd.read_csv(REL / 'trends.csv')
    t['ox'], t['oy'] = utm(t.lon0, t.lat0)

    # self-check: transect origin + normal x distance reproduces the released bank point (< 1 m)
    chk = b[b.year == 2024].sample(500, random_state=0).merge(t[KEY + ['ox', 'oy', 'nx', 'ny']], on=KEY)
    bx, by = utm(chk.lon, chk.lat)
    err = np.hypot(chk.ox + chk.nx * chk.dist_m - bx, chk.oy + chk.ny * chk.dist_m - by)
    assert err.max() < 1.0, f'transect geometry does not reproduce bank points (max {err.max():.2f} m)'

    # representative bank point per transect-side for units and trend points: median distance over 2022-2024 (the
    # current bank; all years if none), placed on the transect (median lon/lat where the side has no trends row)
    agg = dict(dist=('dist_m', 'median'), unit=('unit_2km', 'first'), lon=('lon', 'median'), lat=('lat', 'median'))
    ok = b[~b.spike]
    med = pd.concat([ok[ok.year >= 2022].groupby(KEY).agg(**agg), ok.groupby(KEY).agg(**agg)])
    med = med[~med.index.duplicated()].reset_index()
    med = med.merge(t[KEY + ['ox', 'oy', 'nx', 'ny', 'rate_m_per_yr', 'kind']], on=KEY, how='left')
    med['x'], med['y'] = utm(med.lon, med.lat)
    geo = med.ox.notna()
    med.loc[geo, 'x'], med.loc[geo, 'y'] = med.ox + med.nx * med.dist, med.oy + med.ny * med.dist
    med['lon'], med['lat'] = wgs(med.x, med.y)

    # units
    units = pd.read_csv(REL / 'units_2km.csv').set_index('unit')
    unrep = pd.read_csv(REL / 'unreported_reaches.csv').set_index('unit')
    inv = inventory()
    sc = b[b.in_scope & b.commune.notna()].drop_duplicates(['unit_2km', 'commune', 'district'])
    communes = sc.groupby('unit_2km')[['commune', 'district', 'province']].apply(lambda g: [f'{c} ({d}, {p})' for c, d, p in
                                                       zip(g.commune, g.district, g.province)]).to_dict()
    feats = []
    for un, g in med[med.unit.isin(units.index)].sort_values(KEY).groupby('unit'):
        segs = segments(g)
        if not segs:
            continue
        u = units.loc[un]
        p = {'u': un, 'ch': u.channel, 'side': u.side, 'km': [nz(u.km_from), nz(u.km_to)], 'r': nz(u.win_p75),
             'n': int(u.n_win), 'lab': None if pd.isna(u.lab_p75_20) else int(u.lab_p75_20),
             'com': communes.get(un, []), 'inv': inv.get(un, [])}
        if un in unrep.index:
            v = unrep.loc[un]
            p['unrep'] = {'loss': v.visual_loss, 'prot': v.visual_protection,
                          'note': v.visual_note if isinstance(v.visual_note, str) else '',
                          'old': v.old_capture, 'new': v.new_capture}
        feats.append({'type': 'Feature', 'properties': p, 'geometry': {'type': 'MultiLineString', 'coordinates': segs}})
    dump('units.json', {'type': 'FeatureCollection', 'features': feats})
    n_units, n_unrep = len(feats), sum('unrep' in f['properties'] for f in feats)
    missing = sorted(set(units.index) - {f['properties']['u'] for f in feats})

    # forecast 2027
    fc = pd.read_csv('data/processed/forecast_2027.csv').merge(t[KEY + ['ox', 'oy', 'nx', 'ny']], on=KEY, how='left')
    fc = fc[fc.d_2024.notna() & fc.ox.notna()].sort_values(KEY)
    fc['dist_b'] = fc.d_2024 + fc.hi_gbt_mondrian
    for col, d in (('', 'd_2024'), ('b', 'dist_b')):
        fc[f'x{col}'], fc[f'y{col}'] = fc.ox + fc.nx * fc[d], fc.oy + fc.ny * fc[d]
        fc[f'lon{col}'], fc[f'lat{col}'] = wgs(fc[f'x{col}'], fc[f'y{col}'])
    half = {(m, g): float((d[f'hi_{m}'] - d[f'lo_{m}']).iloc[0] / 2) for g, d in fc.groupby('group')
            for m in ('gbt_mondrian', 'pers_mondrian')}
    half_split = {m: float((fc[f'hi_{m}'] - fc[f'lo_{m}']).iloc[0] / 2) for m in ('gbt_split', 'pers_split')}
    ff = []
    for un, g in fc.groupby('unit_2km'):
        bank = segments(g)
        bound = segments(g.assign(lon=g.lonb, lat=g.latb), 'xb', 'yb')
        if not bank:
            continue
        p = {'u': un, 'g': g.group.iloc[0], 'n': len(g), 'pmed': nz(g.pred_gbt.median()),
             'pmin': nz(g.pred_gbt.min()), 'pmax': nz(g.pred_gbt.max()), 'hmax': nz(g.hi_gbt_mondrian.max()),
             'lmin': nz(g.lo_gbt_mondrian.min()), 'half': nz(half[('gbt_mondrian', g.group.iloc[0])]),
             'phalf': nz(half[('pers_mondrian', g.group.iloc[0])])}
        ff.append({'type': 'Feature', 'properties': dict(p, k='bank'),
                   'geometry': {'type': 'MultiLineString', 'coordinates': bank}})
        if bound:
            ff.append({'type': 'Feature', 'properties': dict(p, k='bound'),
                       'geometry': {'type': 'MultiLineString', 'coordinates': bound}})
    dump('forecast.json', {'type': 'FeatureCollection', 'features': ff})

    # trends
    tr = med[med.rate_m_per_yr.notna()]
    kinds = {'linear': 0, 'step': 1, 'nonlinear': 2}
    dump('trends.json', [[float(a), float(o), round(float(r), 1), kinds.get(k, 0)] for a, o, r, k in
                         zip(r5(tr.lat), r5(tr.lon), tr.rate_m_per_yr, tr.kind)])

    # meta
    cl = pd.read_csv(REL / 'accuracy_clicks.csv')
    acc = cl.groupby('group').landsat_minus_click_m.agg(rmse=lambda s: float(np.sqrt(np.nanmean(s ** 2))),
                                                         n='count').round(0)
    dump('meta.json', {'years': years, 'built': datetime.date.today().isoformat(),
                       'accuracy': {g: {'rmse': int(r.rmse), 'n': int(r.n)} for g, r in acc.iterrows()},
                       'half_mondrian': {g: round(half[('gbt_mondrian', g)], 1) for g in GROUP_ORDER},
                       'half_split': round(half_split['gbt_split'], 1), 'n_units': n_units, 'n_unreported': n_unrep,
                       'n_forecast': int(len(fc))})

    size = sum(f.stat().st_size for f in OUT.iterdir())
    print(f'years {years[0]}-{years[-1]} ({len(years)}); units {n_units} (no bank points: {missing}); unreported '
          f'{n_unrep}; forecast transect-sides {len(fc)}; trend points {len(tr)}; total {size / 1e6:.1f} MB')


if __name__ == '__main__':
    main()
