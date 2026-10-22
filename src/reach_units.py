"""P1: commune of every bank point and the 2 km / 5 km reach units used for labels (H3).

Usage: python src/reach_units.py
Reads data/processed/{tien,hau}/{bank_positions,trends}.csv, data/tiles.json and the pre-2025 commune polygons
data/raw/admin/communes_mekong.geojson (Kontur Boundaries VN 2023-06-28 from OpenStreetMap, ODbL). The bank point
of a transect-side is its median position over the years (spikes left out). Writes data/processed/units.csv:
river, transect, side, chainage_m (from where the centerline enters Vietnam; negative along a border river),
lon, lat, province, district, commune (empty = bank in Cambodia), in_scope (old An Giang, Dong Thap, Tien Giang =
new An Giang and Dong Thap), unit_2km, unit_5km.
"""
import json
import pathlib

import numpy as np
import pandas as pd
from rasterio.warp import transform
from shapely.geometry import Point, shape
from shapely.strtree import STRtree

SCOPE = {'An Giang', 'Đồng Tháp', 'Tiền Giang'}


def main():
    gj = json.loads(pathlib.Path('data/raw/admin/communes_mekong.geojson').read_text(encoding='utf-8'))
    polys = [shape(f['geometry']) for f in gj['features']]
    props = [f['properties'] for f in gj['features']]
    tree = STRtree(polys)
    border = json.loads(pathlib.Path('data/tiles.json').read_text())['border_m']
    rows = []
    for river in ('tien', 'hau'):
        bp = pd.read_csv(f'data/processed/{river}/bank_positions.csv')
        bp = bp[bp.dist_m.notna() & ~bp.spike]
        g = bp.groupby(['transect', 'side']).agg(chainage_m=('chainage_m', 'first'), cx=('cx', 'first'),
                                                 cy=('cy', 'first'), nx=('nx', 'first'), ny=('ny', 'first'),
                                                 d=('dist_m', 'median')).reset_index()
        lon, lat = transform('EPSG:32648', 'EPSG:4326', (g.cx + g.nx * g.d).tolist(), (g.cy + g.ny * g.d).tolist())
        g['lon'], g['lat'] = np.round(lon, 6), np.round(lat, 6)
        g['chainage_m'] = (g.chainage_m - border[river]).round(1)
        for _, r in g.iterrows():
            p = Point(r.lon, r.lat)
            hit = [i for i in tree.query(p) if polys[i].contains(p)]
            a = props[hit[0]] if hit else {}
            rows.append((river, r.transect, r.side, r.chainage_m, r.lon, r.lat, a.get('province'), a.get('district'),
                         a.get('commune')))
    u = pd.DataFrame(rows, columns=['river', 'transect', 'side', 'chainage_m', 'lon', 'lat', 'province', 'district',
                                    'commune'])
    u['in_scope'] = u.province.isin(SCOPE)
    for km in (2, 5):
        u[f'unit_{km}km'] = (u.river + '_' + u.side + '_'
                             + (u.chainage_m // (km * 1000)).astype(int).map('{:+04d}'.format))
    u.to_csv('data/processed/units.csv', index=False, encoding='utf-8')
    print(f'{len(u)} bank points, no commune: {u.commune.isna().sum()}')
    print(u.groupby(['river', 'province']).size().to_string())
    s = u[u.in_scope]
    print(f'in scope: {len(s)} bank points, {s.unit_2km.nunique()} units of 2 km, {s.unit_5km.nunique()} of 5 km, '
          f'{s.groupby(["province", "district", "commune"]).ngroups} communes')


if __name__ == '__main__':
    main()
