"""Download annual dry-season (Jan-Apr) median MNDWI composites from Landsat C2 L2 for one reach.

Usage: python src/gee_water.py sadec_caolanh [first_year last_year]
Writes data/raw/<reach>/mndwi_<year>.tif (bands: mndwi, n_obs) and scenes.csv.
"""
import csv
import pathlib
import sys

import ee
import requests

PROJECT = 'mekong-bankline'
REACHES = {'sadec_caolanh': [105.55, 10.22, 105.85, 10.50]}  # lon/lat bbox on the Tien River
CRS, SCALE, NODATA = 'EPSG:32648', 30, -9999
SENSORS = [  # collection, green, swir1
    ('LANDSAT/LT05/C02/T1_L2', 'SR_B2', 'SR_B5'),
    ('LANDSAT/LE07/C02/T1_L2', 'SR_B2', 'SR_B5'),
    ('LANDSAT/LC08/C02/T1_L2', 'SR_B3', 'SR_B6'),
    ('LANDSAT/LC09/C02/T1_L2', 'SR_B3', 'SR_B6'),
]


def scene_mndwi(green, swir):
    def f(img):
        clear = img.select('QA_PIXEL').bitwiseAnd(0b11010).eq(0)  # dilated cloud, cloud, shadow
        g = img.select(green).multiply(2.75e-05).add(-0.2)
        s = img.select(swir).multiply(2.75e-05).add(-0.2)
        return g.subtract(s).divide(g.add(s)).rename('mndwi').updateMask(clear)
    return f


def composite(region, year):
    start, end = f'{year}-01-01', f'{year}-05-01'
    parts, counts = [], {}
    for coll, green, swir in SENSORS:
        c = ee.ImageCollection(coll).filterBounds(region).filterDate(start, end)
        counts[coll.split('/')[1]] = c.size()
        parts.append(c.map(scene_mndwi(green, swir)))
    merged = parts[0].merge(parts[1]).merge(parts[2]).merge(parts[3])
    img = ee.Image.cat([
        merged.median().unmask(NODATA).rename('mndwi'),
        merged.count().unmask(0).toFloat().rename('n_obs'),
    ])
    return img, ee.Dictionary(counts).getInfo()


def main():
    reach = sys.argv[1]
    y0, y1 = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (2000, 2024)
    ee.Initialize(project=PROJECT)
    region = ee.Geometry.Rectangle(REACHES[reach])
    out = pathlib.Path('data/raw') / reach
    out.mkdir(parents=True, exist_ok=True)
    log = out / 'scenes.csv'
    rows = list(csv.DictReader(log.open())) if log.exists() else []
    done = {r['year'] for r in rows}
    for year in range(y0, y1 + 1):
        tif = out / f'mndwi_{year}.tif'
        if tif.exists() and str(year) in done:
            continue
        img, counts = composite(region, year)
        url = img.getDownloadURL({'region': region, 'scale': SCALE, 'crs': CRS,
                                  'format': 'GEO_TIFF', 'filePerBand': False})
        r = requests.get(url, timeout=600)
        r.raise_for_status()
        tif.write_bytes(r.content)
        rows = [x for x in rows if x['year'] != str(year)] + [{'year': str(year), **{k: str(v) for k, v in counts.items()}}]
        with log.open('w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=['year'] + [s[0].split('/')[1] for s in SENSORS])
            w.writeheader()
            w.writerows(sorted(rows, key=lambda x: x['year']))
        print(year, counts, f'{len(r.content) / 1e6:.1f} MB', flush=True)


if __name__ == '__main__':
    main()
