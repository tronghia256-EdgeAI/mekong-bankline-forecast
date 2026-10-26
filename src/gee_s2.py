"""P3 R1: annual dry-season (Jan-Apr) median MNDWI composites from Sentinel-2 for one reach (mirrors gee_water.py).

Usage: python src/gee_s2.py <reach> [first_year last_year]
Writes data/raw/s2/<reach>/mndwi_<year>.tif (bands: mndwi, n_obs; float32, nodata -9999) and scenes.csv.
Design (docs/p3_plan.md R1): COPERNICUS/S2_SR_HARMONIZED, Jan 1 - May 1, Cloud Score+ cs_cdf >= 0.6, median composite,
MNDWI = (B3 - B11) / (B3 + B11) with B11 (20 m) resampled bilinearly to 10 m. Grid: UTM 48N, 10 m, same origin and
footprint as the reach's Landsat raster (data/raw/<reach>/, 30 m), so one Landsat pixel = 3 x 3 Sentinel-2 pixels.
Downloaded in chunks (getDownloadURL request limit) and mosaicked locally.
"""
import csv
import pathlib
import sys
import tempfile
import time

import ee
import numpy as np
import rasterio
import requests
from rasterio.transform import Affine

PROJECT = 'mekong-bankline'
CRS, PX, NODATA = 'EPSG:32648', 10, -9999
CS_MIN = 0.6
MAX_CHUNK = 1600                     # chunk side (px): 1600^2 x 2 bands x 4 B = 20 MB < the 48 MB request limit


def scene_mndwi(img):
    clear = img.select('cs_cdf').gte(CS_MIN)
    g = img.select('B3').toFloat()
    s = img.select('B11').toFloat().resample('bilinear')
    return g.subtract(s).divide(g.add(s)).rename('mndwi').updateMask(clear)


def composite(region, year, coll):
    c = (ee.ImageCollection(coll).filterBounds(region).filterDate(f'{year}-01-01', f'{year}-05-01')
         .linkCollection(ee.ImageCollection('GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED'), ['cs_cdf']))
    m = c.map(scene_mndwi)
    img = ee.Image.cat([m.median().unmask(NODATA).rename('mndwi'), m.count().unmask(0).rename('n_obs')]).toFloat()
    return img, c.size()


def fetch(img, x0, y0, w, h):
    region = ee.Geometry.Rectangle([x0, y0 - h * PX, x0 + w * PX, y0], CRS, False)
    url = img.getDownloadURL({'region': region, 'crs': CRS, 'crs_transform': [PX, 0, x0, 0, -PX, y0],
                              'format': 'GEO_TIFF', 'filePerBand': False})
    for attempt in range(6):   # EE answers 429/503 now and then under parallel downloads
        try:
            r = requests.get(url, timeout=900)
            if r.status_code < 429 or attempt == 5:
                break
        except requests.RequestException:
            if attempt == 5:
                raise
        time.sleep(30 * (attempt + 1))
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as fh:
        fh.write(r.content)
    with rasterio.open(fh.name) as src:
        a, tf = src.read(), src.transform
    pathlib.Path(fh.name).unlink()
    assert (tf.a, tf.e, tf.c, tf.f) == (PX, -PX, x0, y0) and a.shape[1:] == (h, w), (tf, a.shape, (h, w))
    return a


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    reach = args[0]
    y0, y1 = (int(args[1]), int(args[2])) if len(args) > 2 else (2017, 2024)
    coll = 'COPERNICUS/S2_SR_HARMONIZED'
    ee.Initialize(project=PROJECT)
    with rasterio.open(sorted(pathlib.Path('data/raw', reach).glob('mndwi_*.tif'))[0]) as ls:
        H, W, ltf = ls.height * 3, ls.width * 3, ls.transform
    X0, Y0 = ltf.c, ltf.f
    assert X0 % PX == 0 and Y0 % PX == 0      # Landsat origins are multiples of 30 m: the S2 10 m grid, no resampling of B3
    region = ee.Geometry.Rectangle([X0, Y0 - H * PX, X0 + W * PX, Y0], CRS, False)
    out = pathlib.Path('data/raw', 's2', reach)
    out.mkdir(parents=True, exist_ok=True)
    log = out / 'scenes.csv'
    rows = list(csv.DictReader(log.open())) if log.exists() else []
    done = {r['year'] for r in rows}
    nr, nc = -(-H // MAX_CHUNK), -(-W // MAX_CHUNK)
    rs, cs = np.linspace(0, H, nr + 1).astype(int), np.linspace(0, W, nc + 1).astype(int)
    for year in range(y0, y1 + 1):
        tif = out / f'mndwi_{year}.tif'
        if tif.exists() and str(year) in done:
            continue
        img, n = composite(region, year, coll)
        n = n.getInfo()
        a = np.full((2, H, W), NODATA, np.float32)
        a[1] = 0
        if n:
            for i in range(nr):
                for j in range(nc):
                    a[:, rs[i]:rs[i + 1], cs[j]:cs[j + 1]] = fetch(img, X0 + cs[j] * PX, Y0 - rs[i] * PX,
                                                                   cs[j + 1] - cs[j], rs[i + 1] - rs[i])
        prof = dict(driver='GTiff', height=H, width=W, count=2, dtype='float32', crs=CRS, nodata=NODATA,
                    transform=Affine(PX, 0, X0, 0, -PX, Y0), compress='deflate', predictor=3, tiled=True)
        with rasterio.open(tif, 'w', **prof) as dst:
            dst.write(a)
            dst.set_band_description(1, 'mndwi')
            dst.set_band_description(2, 'n_obs')
        rows = [x for x in rows if x['year'] != str(year)] + [{'year': str(year), 'S2': str(n)}]
        with log.open('w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=['year', 'S2'])
            w.writeheader()
            w.writerows(sorted(rows, key=lambda x: x['year']))
        print(reach, year, n, 'scenes, nodata share %.3f' % (a[0] == NODATA).mean(), flush=True)


if __name__ == '__main__':
    main()
