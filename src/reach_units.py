"""P1: commune of every bank point and the 2 km / 5 km reach units used for labels (H3).

Usage: python src/reach_units.py
Reads data/processed/{tien,hau}/{bank_positions,trends}.csv, data/tiles.json and the pre-2025 commune polygons
data/raw/admin/communes_mekong.geojson (Kontur Boundaries VN 2023-06-28 from OpenStreetMap, ODbL). The bank point
of a transect-side is its median position over the years (spikes left out). Branch bank points within DUP_M of
a main-channel bank point (the outer banks both measure) are dropped. Writes data/processed/units.csv:
river (tien/hau), channel (river or its branch behind a cù lao, data/processed/<branch>/), transect, side,
chainage_m (from where the centerline enters Vietnam, negative along a border river; along a branch, from its start),
lon, lat, province, district, commune (empty = bank in Cambodia), in_scope (old An Giang, Dong Thap, Tien Giang =
new An Giang and Dong Thap), unit_2km, unit_5km.
"""
import json
import pathlib

import numpy as np
import pandas as pd
from rasterio.warp import transform
from shapely.geometry import Point, shape
from scipy.spatial import cKDTree
from shapely.strtree import STRtree

SCOPE = {'An Giang', 'Đồng Tháp', 'Tiền Giang'}
DUP_M = 150.0   # a branch bank point this close to a main-channel bank point is the same bank (already measured)


def main():
    gj = json.loads(pathlib.Path('data/raw/admin/communes_mekong.geojson').read_text(encoding='utf-8'))
    polys = [shape(f['geometry']) for f in gj['features']]
    props = [f['properties'] for f in gj['features']]
    tree = STRtree(polys)
    cfg = json.loads(pathlib.Path('data/tiles.json').read_text())
    channels = [('tien', 'tien'), ('hau', 'hau')] + [(b, v['parent']) for b, v in cfg.get('branches', {}).items()
                                                      if pathlib.Path('data/processed', b, 'bank_positions.csv').exists()]
    rows = []
    for channel, river in channels:
        bp = pd.read_csv(f'data/processed/{channel}/bank_positions.csv')
        bp = bp[bp.dist_m.notna() & ~bp.spike]
        g = bp.groupby(['transect', 'side']).agg(chainage_m=('chainage_m', 'first'), cx=('cx', 'first'),
                                                 cy=('cy', 'first'), nx=('nx', 'first'), ny=('ny', 'first'),
                                                 d=('dist_m', 'median')).reset_index()
        g['bx'], g['by'] = g.cx + g.nx * g.d, g.cy + g.ny * g.d
        lon, lat = transform('EPSG:32648', 'EPSG:4326', g.bx.tolist(), g.by.tolist())
        g['lon'], g['lat'] = np.round(lon, 6), np.round(lat, 6)
        g['chainage_m'] = (g.chainage_m - cfg['border_m'].get(channel, 0)).round(1)
        for _, r in g.iterrows():
            p = Point(r.lon, r.lat)
            hit = [i for i in tree.query(p) if polys[i].contains(p)]
            a = props[hit[0]] if hit else {}
            rows.append((river, channel, r.transect, r.side, r.chainage_m, r.lon, r.lat, r.bx, r.by, a.get('province'),
                         a.get('district'), a.get('commune')))
    u = pd.DataFrame(rows, columns=['river', 'channel', 'transect', 'side', 'chainage_m', 'lon', 'lat', 'bx', 'by',
                                    'province', 'district', 'commune'])
    dup = np.zeros(len(u), bool)
    for river in ('tien', 'hau'):
        main, br = u.channel == river, (u.river == river) & (u.channel != river)
        if br.any():
            dup[br.to_numpy()] = cKDTree(u.loc[main, ['bx', 'by']]).query(u.loc[br, ['bx', 'by']])[0] < DUP_M
    print(f'branch bank points dropped as already measured on the main channel: {dup.sum()} of '
          f'{(u.river != u.channel).sum()}')
    u = u[~dup].drop(columns=['bx', 'by'])
    u['in_scope'] = u.province.isin(SCOPE)
    for km in (2, 5):
        u[f'unit_{km}km'] = (u.channel + '_' + u.side + '_'
                             + (u.chainage_m // (km * 1000)).astype(int).map('{:+04d}'.format))
    u.to_csv('data/processed/units.csv', index=False, encoding='utf-8')
    print(f'{len(u)} bank points, no commune: {u.commune.isna().sum()}')
    print(u.groupby(['channel', 'province']).size().to_string())
    s = u[u.in_scope]
    print(f'in scope: {len(s)} bank points, {s.unit_2km.nunique()} units of 2 km, {s.unit_5km.nunique()} of 5 km, '
          f'{s.groupby(["province", "district", "commune"]).ngroups} communes')


if __name__ == '__main__':
    main()
