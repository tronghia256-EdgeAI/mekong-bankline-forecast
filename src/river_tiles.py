"""P1: coarse centerlines of the Tien and Hau and the overlapping tiles the full rivers are processed in.

Usage: python src/river_tiles.py
Downloads JRC GSW v1.4 water occurrence (90 m) once to data/raw/jrc_occurrence_90m.tif, traces each river as
the cheapest path between its two end points through water seen in >= 50% of observations, with a step cost of
1 / (distance to land)^2 (land 1000, to bridge 1-2 px breaks) so the route keeps to the widest channel and never short-cuts through canals, and places 30 km square tiles every 20 km of chainage. Writes data/tiles.json
(centerlines in UTM 48N m, tile bboxes in lon/lat for gee_water.py) and results/p1/tiles.png.
Each tile owns the transects nearest its centre in chainage (stitch.py); banklines.load masks out the pixels of a
tile nearer the other river's centerline, so the other river (6.5 km away at Vam Nao) is never the main channel.
"""
import json
import pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
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



def main():
    occ, tf = occurrence()
    water = occ >= 50
    # land is passable at a high cost so 1-2 px breaks in narrow reaches (bridges, the Hau near the border) are bridged
    cost = np.where(water, 1 / np.maximum(ndimage.distance_transform_edt(water), 1) ** 2, 1e3)
    wet = np.argwhere(water)
    out = {'centerlines': {}, 'tiles': {}}
    fig, ax = plt.subplots(figsize=(9, 9))
    H, W = occ.shape
    ax.imshow(occ, cmap='Blues', extent=(tf.c, tf.c + W * tf.a, tf.f + H * tf.e, tf.f))
    for river, ends in RIVERS.items():
        ex, ey = transform('EPSG:4326', CRS, [e[0] for e in ends], [e[1] for e in ends])
        snap = []
        for x, y in zip(ex, ey):
            r, c = (y - tf.f) / tf.e, (x - tf.c) / tf.a
            d = np.hypot(wet[:, 0] - r, wet[:, 1] - c) * SCALE
            if d.min() > MAX_SNAP:
                raise RuntimeError(f'{river}: end point {d.min():.0f} m from water')
            snap.append(tuple(wet[d.argmin()]))
        rc = np.array(route_through_array(cost, *snap, fully_connected=True, geometric=True)[0])
        xy = np.column_stack([tf.c + (rc[:, 1] + 0.5) * tf.a, tf.f + (rc[:, 0] + 0.5) * tf.e])
        seg = np.r_[0, np.cumsum(np.hypot(*np.diff(xy, axis=0).T))]
        s = np.arange(0, seg[-1], 100.0)
        line = np.column_stack([np.interp(s, seg, xy[:, 0]), np.interp(s, seg, xy[:, 1])])
        out['centerlines'][river] = line.round(1).tolist()
        centres = np.arange(STRIDE / 2, seg[-1], STRIDE)
        if seg[-1] - centres[-1] > STRIDE / 2:
            centres = np.r_[centres, seg[-1] - STRIDE / 2]
        for k, sc in enumerate(centres, 1):
            x, y = np.interp(sc, s, line[:, 0]), np.interp(sc, s, line[:, 1])
            h = TILE / 2
            lon, lat = transform(CRS, 'EPSG:4326', [x - h, x + h, x - h, x + h], [y - h, y - h, y + h, y + h])
            name = f'{river}_{k:02d}'
            out['tiles'][name] = {'river': river, 'chainage_m': round(float(sc)),
                                  'bbox': [round(min(lon), 4), round(min(lat), 4), round(max(lon), 4), round(max(lat), 4)]}
            ax.add_patch(plt.Rectangle((x - h, y - h), TILE, TILE, fill=False, ec='C1' if river == 'tien' else 'C3', lw=.8))
            ax.text(x, y, name, fontsize=6, ha='center')
        ax.plot(line[:, 0], line[:, 1], 'k-', lw=1)
        ax.plot(ex, ey, 'r^')
        print(f'{river}: {seg[-1] / 1e3:.1f} km, {len(centres)} tiles')
    ax.set_title('Coarse centerlines (JRC occurrence >= 50%) and P1 tiles')
    pathlib.Path('data/tiles.json').write_text(json.dumps(out, indent=1))
    figs = pathlib.Path('results/p1')
    figs.mkdir(parents=True, exist_ok=True)
    fig.savefig(figs / 'tiles.png', dpi=120, bbox_inches='tight')


if __name__ == '__main__':
    main()
