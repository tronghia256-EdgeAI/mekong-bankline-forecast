"""P1: coarse centerlines of the Tien and Hau and the overlapping tiles the full rivers are processed in.

Usage: python src/river_tiles.py
Downloads JRC GSW v1.4 water occurrence (90 m) once to data/raw/jrc_occurrence_90m.tif, traces each river as
the cheapest path between its two end points through water seen in >= 50% of observations, with a step cost of
1 / (distance to land)^2 (land 1000, to bridge 1-2 px breaks) so the route keeps to the widest channel and never
short-cuts through canals, and places 30 km square tiles every 20 km of chainage. Writes data/tiles.json
(centerlines in UTM 48N m, tile bboxes in lon/lat for gee_water.py, the chainage up to which a river is narrow;
tiles centred there run banklines' narrow mode; the chainage where each river enters Vietnam, from LSIB 2017)
and results/p1/tiles.png; plus every river island of 1-150 km2 (a hole in the connected river system),
each its own tile measured all round by banklines' island mode (no hand-picked channels).
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
from skimage.measure import find_contours

REGION = [104.95, 9.95, 106.0, 11.0]
RIVERS = {  # (upstream end at the Cambodian border, downstream end), lon/lat
    'tien': [(105.19, 10.95), (105.915, 10.275)],   # to My Thuan bridge
    'hau': [(105.085, 10.955), (105.82, 10.03)],      # to Can Tho bridge
}
CRS, SCALE = 'EPSG:32648', 90
TILE, STRIDE = 30e3, 20e3          # tile side and spacing along the river (m)
MAX_SNAP = 5e3
NARROW_TO = {'hau': (105.117, 10.705)}   # narrow channel (~200 m vs ~420 m below) upstream of Chau Doc, lon/lat
ISLAND_KM2 = (1.0, 150.0)   # river islands (cù lao) measured all round: area of the hole in the JRC >= 50% river system
ISL_MARGIN = 3000.0          # island tile = island bounding box + this margin (m)


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
    # river islands: holes of the connected river system (both rivers join at Vam Nao), found by rule, not by hand
    lab, _ = ndimage.label(water, structure=np.ones((3, 3), bool))
    sizes = np.bincount(lab.ravel())
    sizes[0] = 0
    system = lab == sizes.argmax()
    hl, hn = ndimage.label(ndimage.binary_fill_holes(system) & ~system)
    lines = {r: np.array(v) for r, v in out['centerlines'].items()}
    found = []
    for k in range(1, hn + 1):
        m = hl == k
        area = m.sum() * SCALE ** 2 / 1e6
        if not ISLAND_KM2[0] <= area <= ISLAND_KM2[1]:
            continue
        rc = max(find_contours(np.pad(m, 1).astype(float), .5), key=len) - 1
        xy = np.column_stack([tf.c + (rc[:, 1] + 0.5) * tf.a, tf.f + (rc[:, 0] + 0.5) * tf.e])
        cen = xy.mean(0)
        river = min(lines, key=lambda r: np.hypot(*(lines[r] - cen).T).min())
        found.append((river, float(np.hypot(*(lines[river] - cen).T).argmin() * 100.0), area, xy))
    out['islands'] = {}
    for river, ch, area, xy in sorted(found, key=lambda f: (f[0], f[1])):
        name = f'isl_{river}_{sum(k.startswith(f"isl_{river}_") for k in out["islands"]) + 1:02d}'
        (x0, y0), (x1, y1) = xy.min(0) - ISL_MARGIN, xy.max(0) + ISL_MARGIN
        lon, lat = transform(CRS, 'EPSG:4326', [x0, x1, x0, x1], [y0, y0, y1, y1])
        out['islands'][name] = {'parent': river, 'area_km2': round(area, 1), 'chainage_m': round(ch),
                                'polygon': xy.round(0).tolist()}
        out['tiles'][name] = {'river': name, 'parent': river, 'island': True, 'chainage_m': round(ch),
                              'bbox': [round(min(lon), 4), round(min(lat), 4), round(max(lon), 4), round(max(lat), 4)]}
        ax.plot(xy[:, 0], xy[:, 1], 'm-', lw=1)
        ax.text(*xy.mean(0), name[4:], fontsize=6, color='m')
        print(f'{name}: {area:.1f} km2 at {ch / 1e3:.1f} km')
    ax.set_title('Coarse centerlines (JRC occurrence >= 50%) and P1 tiles')
    pathlib.Path('data/tiles.json').write_text(json.dumps(out, indent=1))
    figs = pathlib.Path('results/p1')
    figs.mkdir(parents=True, exist_ok=True)
    fig.savefig(figs / 'tiles.png', dpi=120, bbox_inches='tight')


if __name__ == '__main__':
    main()
