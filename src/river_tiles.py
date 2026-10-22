"""P1: coarse centerlines of the Tien and Hau and the overlapping tiles the full rivers are processed in.

Usage: python src/river_tiles.py
Downloads JRC GSW v1.4 water occurrence (90 m) once to data/raw/jrc_occurrence_90m.tif, traces each river as
the cheapest path between its two end points through water seen in >= 50% of observations, with a step cost of
1 / (distance to land)^2 (land 1000, to bridge 1-2 px breaks) so the route keeps to the widest channel and never
short-cuts through canals, and places 30 km square tiles every 20 km of chainage. Writes data/tiles.json
(centerlines in UTM 48N m, tile bboxes in lon/lat for gee_water.py, the chainage up to which a river is narrow;
tiles centred there run banklines' narrow mode; the chainage where each river enters Vietnam, from LSIB 2017)
and results/p1/tiles.png; plus secondary channels behind large islands (BRANCHES), each one narrow-mode tile.
Each tile owns the transects nearest its centre in chainage (stitch.py); banklines.load masks out the pixels of a
tile nearer the other river's centerline, so the other river (6.5 km away at Vam Nao) is never the main channel.
"""
import json
import pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.path import Path
import rasterio
import requests
from rasterio.warp import transform
from scipy import ndimage
from skimage.graph import route_through_array

REGION = [104.95, 9.95, 106.0, 11.0]
RIVERS = {  # (upstream end at the Cambodian border, downstream end), lon/lat
    'tien': [(105.19, 10.95), (105.915, 10.275)],   # to My Thuan bridge
    'hau': [(105.085, 10.955), (105.82, 10.03)],      # to Can Tho bridge
}
CRS, SCALE = 'EPSG:32648', 90
TILE, STRIDE = 30e3, 20e3          # tile side and spacing along the river (m)
MAX_SNAP = 5e3
NARROW_TO = {'hau': (105.117, 10.705)}   # narrow channel (~200 m vs ~420 m below) upstream of Chau Doc, lon/lat
BRANCHES = {  # secondary channels behind large islands (cù lao), run in narrow mode; (parent, [start, end] downstream),
    # end points picked on the gridded JRC >= 50% mask, inside each branch and away from its junctions
    'tien_b1': ('tien', [(105.3411, 10.6925), (105.3592, 10.5794)]),   # west branch along Phu Tan (Phu Tho, Phu My, Kien An)
    'tien_b2': ('tien', [(105.268, 10.7694), (105.3292, 10.7224)]),    # loop around Long Hoa / Phu Thuan A
    'tien_b3a': ('tien', [(105.4899, 10.5159), (105.5619, 10.4317)]),  # west channel around cù lao Gieng (Cho Moi)
    'tien_b3b': ('tien', [(105.5027, 10.5313), (105.572, 10.4615)]),   # east channel around cù lao Gieng (main route)
}


def occurrence():
    f = pathlib.Path('data/raw/jrc_occurrence_90m.tif')
    if not f.exists():
        import ee
        ee.Initialize(project='mekong-bankline')
        img = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('occurrence').unmask(0)
        url = img.getDownloadURL({'region': ee.Geometry.Rectangle(REGION), 'scale': SCALE, 'crs': CRS,
                                  'format': 'GEO_TIFF'})
        r = requests.get(url, timeout=600)
        r.raise_for_status()
        f.write_bytes(r.content)
    with rasterio.open(f) as src:
        return src.read(1), src.transform


def cambodia():
    """Cambodia (LSIB 2017, not simplified) clipped to REGION, as matplotlib paths in lon/lat; cached."""
    f = pathlib.Path('data/raw/lsib_cambodia.json')
    if not f.exists():
        import ee
        ee.Initialize(project='mekong-bankline')
        kh = ee.FeatureCollection('USDOS/LSIB_SIMPLE/2017').filter(ee.Filter.eq('country_na', 'Cambodia'))
        f.write_text(json.dumps(kh.geometry().intersection(ee.Geometry.Rectangle(REGION), 1).getInfo()))

    def polys(g):
        if g['type'] == 'GeometryCollection':
            return [p for x in g['geometries'] for p in polys(x)]
        return {'Polygon': [g.get('coordinates')], 'MultiPolygon': g.get('coordinates')}.get(g['type'], [])
    return [Path(np.array(p[0])) for p in polys(json.loads(f.read_text()))]


def main():
    occ, tf = occurrence()
    water = occ >= 50
    # land is passable at a high cost so 1-2 px breaks in narrow reaches (bridges, the Hau near the border) are bridged
    cost = np.where(water, 1 / np.maximum(ndimage.distance_transform_edt(water), 1) ** 2, 1e3)
    wet = np.argwhere(water)
    out = {'centerlines': {}, 'tiles': {}, 'border_m': {}}
    kh = cambodia()
    fig, ax = plt.subplots(figsize=(9, 9))
    H, W = occ.shape
    ax.imshow(occ, cmap='Blues', extent=(tf.c, tf.c + W * tf.a, tf.f + H * tf.e, tf.f))
    def route(name, ends, cost=cost):
        ex, ey = transform('EPSG:4326', CRS, [e[0] for e in ends], [e[1] for e in ends])
        snap = []
        for x, y in zip(ex, ey):
            r, c = (y - tf.f) / tf.e, (x - tf.c) / tf.a
            d = np.hypot(wet[:, 0] - r, wet[:, 1] - c) * SCALE
            if d.min() > MAX_SNAP:
                raise RuntimeError(f'{name}: end point {d.min():.0f} m from water')
            snap.append(tuple(wet[d.argmin()]))
        rc = np.array(route_through_array(cost, *snap, fully_connected=True, geometric=True)[0])
        xy = np.column_stack([tf.c + (rc[:, 1] + 0.5) * tf.a, tf.f + (rc[:, 0] + 0.5) * tf.e])
        seg = np.r_[0, np.cumsum(np.hypot(*np.diff(xy, axis=0).T))]
        s = np.arange(0, seg[-1], 100.0)
        return np.column_stack([np.interp(s, seg, xy[:, 0]), np.interp(s, seg, xy[:, 1])]), s, seg, ex, ey

    def tile_box(x, y):
        h = TILE / 2
        lon, lat = transform(CRS, 'EPSG:4326', [x - h, x + h, x - h, x + h], [y - h, y - h, y + h, y + h])
        return [round(min(lon), 4), round(min(lat), 4), round(max(lon), 4), round(max(lat), 4)]

    for river, ends in RIVERS.items():
        line, s, seg, ex, ey = route(river, ends)
        out['centerlines'][river] = line.round(1).tolist()
        lon, lat = transform(CRS, 'EPSG:4326', line[:, 0], line[:, 1])
        in_kh = np.any([p.contains_points(np.c_[lon, lat]) for p in kh], axis=0)
        out['border_m'][river] = round(float(s[np.nonzero(in_kh)[0].max() + 1])) if in_kh.any() else 0   # entry into Vietnam
        centres = np.arange(STRIDE / 2, seg[-1], STRIDE)
        if seg[-1] - centres[-1] > STRIDE / 2:
            centres = np.r_[centres, seg[-1] - STRIDE / 2]
        narrow_to = 0.0
        if river in NARROW_TO:
            nx, ny = transform('EPSG:4326', CRS, [NARROW_TO[river][0]], [NARROW_TO[river][1]])
            narrow_to = float(s[np.hypot(line[:, 0] - nx[0], line[:, 1] - ny[0]).argmin()])
            out.setdefault('narrow_until_m', {})[river] = round(narrow_to)
        for k, sc in enumerate(centres, 1):
            x, y = np.interp(sc, s, line[:, 0]), np.interp(sc, s, line[:, 1])
            h = TILE / 2
            name = f'{river}_{k:02d}'
            out['tiles'][name] = {'river': river, 'chainage_m': round(float(sc)), 'bbox': tile_box(x, y),
                                  'narrow': bool(sc < narrow_to)}
            ax.add_patch(plt.Rectangle((x - h, y - h), TILE, TILE, fill=False, ec='C1' if river == 'tien' else 'C3', lw=.8))
            ax.text(x, y, name, fontsize=6, ha='center')
        ax.plot(line[:, 0], line[:, 1], 'k-', lw=1)
        ax.plot(ex, ey, 'r^')
        print(f'{river}: {seg[-1] / 1e3:.1f} km, {len(centres)} tiles, enters Vietnam at {out["border_m"][river] / 1e3:.1f} km')
    out['branches'] = {}
    for name, (parent, ends) in BRANCHES.items():   # one narrow-mode tile per branch, centred on it
        # shortest path through water: the width weighting would pull a branch route back into the main channel
        line, s, seg, ex, ey = route(name, ends, np.where(water, 1.0, 1e3))
        out['branches'][name] = {'parent': parent, 'line': line.round(1).tolist()}
        mid = len(line) // 2
        out['tiles'][name] = {'river': name, 'parent': parent, 'branch': True, 'narrow': True,
                              'chainage_m': round(float(s[mid])), 'bbox': tile_box(*line[mid])}
        ax.plot(line[:, 0], line[:, 1], 'm-', lw=1)
        print(f'{name}: {seg[-1] / 1e3:.1f} km')
    ax.set_title('Coarse centerlines (JRC occurrence >= 50%) and P1 tiles')
    pathlib.Path('data/tiles.json').write_text(json.dumps(out, indent=1))
    figs = pathlib.Path('results/p1')
    figs.mkdir(parents=True, exist_ok=True)
    fig.savefig(figs / 'tiles.png', dpi=120, bbox_inches='tight')


if __name__ == '__main__':
    main()
