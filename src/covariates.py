"""P1: covariates per reach unit (2 km and 5 km) for H3: physical susceptibility and exposure / reporting-bias proxies.

Usage: python src/covariates.py [fig]      (fig: only redraw figures/fig06_covariates from the written CSV)
Reads data/processed/units.csv (in_scope bank points), data/processed/{tien,hau,isl_*}/bank_positions.csv and
data/tiles.json. Downloads once and caches under data/raw/covariates/ (gitignored): GHSL built-up, WorldPop and VIIRS
rasters for REF_YEAR from Earth Engine (UTM 48N, 100 m, BBOX) and OSM roads and towns as of OSM_DATE from Overpass.
Writes data/processed/covariates_{2km,5km}.csv, results/p1/covariates.md and figures/fig06_covariates.{png,svg}.
Never reads the reported inventory and relates nothing to erosion or labels (protocol: covariates are described only).

A unit = all in-scope bank points with the same unit_2km (unit_5km). A bank point = the median bank position over the
years of one transect-side (as in reach_units.py); n = its normal from the centerline (or island ring) to the bank, so
+n points landward. Columns (unit value = mean over its bank points unless stated):
  unit, river (tien/hau), channel (river or isl_*), side (L/R downstream; I island bank, O opposite bank of an island
  channel, as labelled in units.csv - see the check in results/p1/covariates.md), is_island (0/1: bank on an island
  channel ring), on_island_share (share of bank points lying on a tiles.json island, +100 m: geometric, independent
  of the I/O label), n_points (bank points, 100 m apart), province (most common)
  river_km      km downstream of where the river enters Vietnam, on the river's coarse centerline (island banks are
                projected onto their parent river's centerline)
  curv_bank     channel curvature at the bank (1/km), + = outer (concave) bank, - = inner bank. Curvature of the
                centerline after Gaussian smoothing (sigma CURV_SIGMA_M) times the side sign. Main channel: the river's
                coarse JRC centerline (tiles.json; the stitched fine centres jump between channels at tile seams).
                Island: the channel ring, so the bank facing the island is mostly the inner bank by construction and the ring
                turns sharply round island heads/tails, which are flow splits, not bends
  curv_abs      |curvature| (1/km)
  outer_share   share of the unit's bank points with curv_bank > OUTER_MIN (0-1)
  width_m       channel width (m; unit value = median over its transects, robust to a few failed detections):
                per transect the median over 2000-2014 of the yearly bank-to-bank distance (L + R, both from the
                same centre and opposite normals) minus the length of the transect inside river islands of tiles.json
                (main banks are the mainland edges; islands > 1 km2 between them are not water). Island channels:
                I + O of the ring transect = width of the channel between the island and the next land
  dwidth_00_14  width change 2000 -> 2014 (m; 3-yr medians 2000-02 and 2012-14; unit median), + = widening
  dwidth_00_24  width change 2000 -> 2024 (m; 2000-02 vs 2022-24). Overlaps the label window 2015-2024: descriptive
                only, not a model input (it contains the retreat that the satellite labels measure)
  vamnao_km     along-river km from the Vam Nao junction on the same river (+ downstream); the junction is the closest
                approach of the two coarse centerlines more than 20 km below the border (rule; Tien km 50.5, Hau km 63.7)
  node_km       along-river km to the nearest bifurcation/confluence: Vam Nao junction or the head/tail of a river
                island (tiles.json, 1-150 km2)
  built_500m, built_1km  built-up surface share (%) of the landward strip 0-500 m / 0-1000 m behind the bank
                (GHSL GHS-BUILT-S R2023A, epoch REF_YEAR, sampled every 100 m along the normal)
  pop_500m, pop_1km      population density (persons/km2) in the same strips (WorldPop Global 100 m,
                unconstrained, REF_YEAR)
  viirs_1km     night lights (nW/cm2/sr) in the 0-1000 m strip (VIIRS VNL V2.1 annual REF_YEAR, average_masked)
  road_km       median distance (km) to the nearest OSM trunk/primary/secondary road (national + provincial) on the
                landward side of the bank (road vertices with (p - bank) . n > 0; roads across the channel ignored)
  town_km       median straight-line distance (km) to the nearest OSM place=city|town node (district seats and cities)
"""
import json
import pathlib
import sys
import time

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
import requests
from rasterio.warp import transform
from scipy.ndimage import gaussian_filter1d
from scipy.spatial import cKDTree
from shapely.geometry import LineString, Point, Polygon

sys.path.insert(0, str(pathlib.Path(__file__).parent))

CACHE = pathlib.Path('data/raw/covariates')
REF_YEAR = 2020                          # exposure reference year (inventory window 2015-2024; GHSL epoch, WorldPop last)
OSM_DATE = '2020-01-01T00:00:00Z'        # OSM state used (Overpass attic query)
BBOX = [104.97, 10.03, 106.03, 11.06]    # lon/lat, in-scope bank points + ~0.1 deg
CRS, SCALE = 'EPSG:32648', 100
VAMNAO_SKIP_M = 20000.0                  # search the closest approach of the rivers only this far below the border
                                         # (at the border they are ~8 km apart too)
CURV_SIGMA_M = 1000.0                    # centerline smoothing before curvature (channel widths 0.2-2 km)
OUTER_MIN = 0.02                         # 1/km (radius 50 km): weaker curvature counts as straight, not outer
STRIP = np.arange(50, 1000, 100.0)       # landward sample distances (m)
WIN = {'w00': (2000, 2002), 'w14': (2012, 2014), 'w24': (2022, 2024), 'ref': (2000, 2014)}
UA = {'User-Agent': 'mekong-bankline-research/0.1'}
OVERPASS = ['https://overpass.private.coffee/api/interpreter', 'https://overpass-api.de/api/interpreter']
NUM = ['river_km', 'curv_bank', 'curv_abs', 'outer_share', 'width_m', 'dwidth_00_14', 'dwidth_00_24', 'vamnao_km',
       'node_km', 'built_500m', 'built_1km', 'pop_500m', 'pop_1km', 'viirs_1km', 'road_km', 'town_km']


# ---------- geometry from the bank tables ----------

def bank_table(channel):
    bp = pd.read_csv(f'data/processed/{channel}/bank_positions.csv')
    return bp[bp.dist_m.notna() & ~bp.spike]


def points():
    """In-scope bank points with UTM bank position (bx, by) and landward normal (nx, ny)."""
    u = pd.read_csv('data/processed/units.csv')
    u = u[u.in_scope].copy()
    geo = []
    for ch in u.channel.unique():
        g = bank_table(ch).groupby(['transect', 'side']).agg(cx=('cx', 'first'), cy=('cy', 'first'), nx=('nx', 'first'),
                                                             ny=('ny', 'first'), d=('dist_m', 'median')).reset_index()
        geo.append(g.assign(channel=ch))
    u = u.merge(pd.concat(geo), on=['channel', 'transect', 'side'], how='left', validate='one_to_one')
    u['bx'], u['by'] = u.cx + u.nx * u.d, u.cy + u.ny * u.d
    return u


def curvature(xy, ring):
    """Signed curvature (1/km, + = turning left looking along the line) and left normal of a polyline, on a grid every
    50 m of arc length (after Gaussian smoothing, sigma CURV_SIGMA_M). Returns grid arc length, kappa, lx, ly and the
    arc length of each input vertex."""
    if ring:
        xy = np.vstack([xy, xy[:1]])
    s = np.r_[0, np.cumsum(np.hypot(*np.diff(xy, axis=0).T))]
    keep = np.r_[True, np.diff(s) > 1]
    g = np.arange(0, s[-1], 50.0)
    x, y = (gaussian_filter1d(np.interp(g, s[keep], xy[keep, i]), CURV_SIGMA_M / 50, mode='wrap' if ring else 'nearest')
            for i in (0, 1))
    dx, dy = np.gradient(x, 50.0), np.gradient(y, 50.0)
    ddx, ddy = np.gradient(dx, 50.0), np.gradient(dy, 50.0)
    nrm = np.hypot(dx, dy)
    return g, (dx * ddy - dy * ddx) / nrm ** 3 * 1000.0, -dy / nrm, dx / nrm, s


def curv_at(g, k, s):
    return k[np.clip(np.round(np.asarray(s) / 50).astype(int), 0, len(g) - 1)]


def widths(channel, islands):
    """Per transect: width_m (2000-2014 median), w00, w14, w24 (3-yr medians), from yearly bank-to-bank distance."""
    bp = bank_table(channel)
    ring = channel.startswith('isl_')
    a, b = ('I', 'O') if ring else ('L', 'R')
    w = bp.pivot_table(index=['transect', 'year'], columns='side', values='dist_m')
    w = (w[a] + w[b]).dropna().rename('w').reset_index()
    if not ring:   # subtract the island chord between the two median banks
        g = bp.groupby(['transect', 'side']).agg(cx=('cx', 'first'), cy=('cy', 'first'), nx=('nx', 'first'),
                                                 ny=('ny', 'first'), d=('dist_m', 'median'))
        g = g.assign(bx=g.cx + g.nx * g.d, by=g.cy + g.ny * g.d)[['bx', 'by']].unstack('side').dropna()
        chord = pd.Series([sum(LineString([(x0, y0), (x1, y1)]).intersection(p).length for p in islands)
                           for x0, y0, x1, y1 in zip(g.bx[a], g.by[a], g.bx[b], g.by[b])], index=g.index)
        w['w'] -= w.transect.map(chord).fillna(0)
    out = {k: w[w.year.between(*yr)].groupby('transect').w.median() for k, yr in WIN.items()}
    return pd.DataFrame(out).reset_index().rename(columns={'index': 'transect'})


def chainage(line, s_line, pts):
    """Arc length (m) of the nearest vertex of a 100 m-spaced polyline, and the distance to it."""
    d, i = cKDTree(line).query(pts)
    return s_line[i], d


def along(cfg):
    """Coarse centerlines with their arc length, and the along-river position (m, from the line start) of the nodes:
    Vam Nao junction per river and island heads/tails."""
    lines = {r: np.array(v) for r, v in cfg['centerlines'].items()}
    s = {r: np.r_[0, np.cumsum(np.hypot(*np.diff(l, axis=0).T))] for r, l in lines.items()}
    d, j = cKDTree(lines['hau']).query(lines['tien'])
    skip = (s['tien'] < cfg['border_m']['tien'] + VAMNAO_SKIP_M) | (s['hau'][j] < cfg['border_m']['hau'] + VAMNAO_SKIP_M)
    i = int(np.where(skip, np.inf, d).argmin())
    vam = {'tien': s['tien'][i], 'hau': s['hau'][j[i]]}
    print(f'Vam Nao junction (closest approach of the centerlines, {d[i] / 1e3:.1f} km): tien km '
          f'{(vam["tien"] - cfg["border_m"]["tien"]) / 1e3:.1f}, hau km {(vam["hau"] - cfg["border_m"]["hau"]) / 1e3:.1f}')
    nodes = {r: [vam[r]] for r in lines}
    for isl in cfg['islands'].values():
        p, _ = chainage(lines[isl['parent']], s[isl['parent']], np.array(isl['polygon'], float))
        nodes[isl['parent']] += [p.min(), p.max()]
    return lines, s, vam, nodes


# ---------- downloads (cached) ----------

def ee_raster(name, make):
    f = CACHE / f'{name}_{REF_YEAR}.tif'
    if not f.exists():
        import ee
        ee.Initialize(project='mekong-bankline')
        url = make(ee).getDownloadURL({'region': ee.Geometry.Rectangle(BBOX), 'scale': SCALE, 'crs': CRS,
                                       'format': 'GEO_TIFF'})
        r = requests.get(url, timeout=600)
        r.raise_for_status()
        CACHE.mkdir(parents=True, exist_ok=True)
        f.write_bytes(r.content)
        print('downloaded', f)
    return f


def rasters():
    def ghsl(ee):   # built-up surface m2 per 100 m Mollweide cell (equal area, 1e4 m2) -> share 0-1
        return ee.Image(f'JRC/GHSL/P2023A/GHS_BUILT_S/{REF_YEAR}').select('built_surface').divide(1e4)

    def worldpop(ee):   # people per ~3 arcsec cell -> persons/km2 (area of the native cell)
        img = (ee.ImageCollection('WorldPop/GP/100m/pop').filter(ee.Filter.eq('country', 'VNM'))
               .filter(ee.Filter.eq('year', REF_YEAR)).first())
        return img.divide(ee.Image.pixelArea().reproject(img.projection())).multiply(1e6)

    def viirs(ee):
        return ee.Image(f'NOAA/VIIRS/DNB/ANNUAL_V21/{REF_YEAR}0101').select('average_masked').unmask(0)

    return {'built': ee_raster('ghsl_built', ghsl), 'pop': ee_raster('worldpop', worldpop),
            'viirs': ee_raster('viirs', viirs)}


def overpass(name, query):
    f = CACHE / f'osm_{name}.json'
    if not f.exists():
        q = f'[out:json][timeout:600][date:"{OSM_DATE}"][bbox:{BBOX[1]},{BBOX[0]},{BBOX[3]},{BBOX[2]}];{query}'
        for attempt in range(8):   # public servers answer 429/502/504 when busy: back off and alternate
            try:
                r = requests.post(OVERPASS[attempt % 2], data={'data': q}, headers=UA, timeout=900)
                if r.ok and r.text.lstrip().startswith('{'):
                    break
                print(f'overpass {name}: HTTP {r.status_code}, retry', flush=True)
            except requests.RequestException as e:
                print(f'overpass {name}: {e.__class__.__name__}, retry', flush=True)
            time.sleep(30 * 2 ** min(attempt, 4))
        else:
            raise RuntimeError(f'Overpass failed for {name}')
        CACHE.mkdir(parents=True, exist_ok=True)
        f.write_text(r.text, encoding='utf-8')
        print('downloaded', f)
    return json.loads(f.read_text(encoding='utf-8'))['elements']


def road_vertices():
    ways = overpass('roads', 'way["highway"~"^(trunk|primary|secondary)(_link)?$"];out geom;')
    xy = []
    for w in ways:
        lon, lat = zip(*[(p['lon'], p['lat']) for p in w['geometry']])
        x, y = transform('EPSG:4326', CRS, list(lon), list(lat))
        line = LineString(zip(x, y))
        xy += [line.interpolate(d).coords[0] for d in np.arange(0, line.length + 50, 50)]   # vertices <= 50 m apart
    print(f'OSM roads: {len(ways)} ways, {len(xy)} vertices')
    return np.array(xy)


def towns():
    nodes = overpass('places', 'node["place"~"^(city|town)$"];out;')
    x, y = transform('EPSG:4326', CRS, [n['lon'] for n in nodes], [n['lat'] for n in nodes])
    print(f'OSM places city/town: {len(nodes)}')
    return np.c_[x, y], [n['tags'].get('name', '') for n in nodes]


# ---------- per-point covariates ----------

def sample(f, x, y):
    with rasterio.open(f) as src:
        return np.array([v[0] for v in src.sample(zip(x, y))], float)


def landward_road(p, n, roads):
    """Distance to the nearest road vertex on the landward side of each bank point (NaN if none among the k nearest)."""
    out = np.full(len(p), np.nan)
    tree = cKDTree(roads)
    for k in (500, 5000, 20000):
        todo = np.nonzero(np.isnan(out))[0]
        if not len(todo):
            break
        d, i = tree.query(p[todo], k=min(k, len(roads)))
        ahead = np.einsum('pkj,pj->pk', roads[i] - p[todo, None], n[todo]) > 0
        out[todo] = np.where(ahead.any(1), d[np.arange(len(todo)), ahead.argmax(1)], np.nan)
    return out


def point_covariates(u, cfg):
    islands = [Polygon(v['polygon']) for v in cfg['islands'].values()]
    lines, s, vam, nodes = along(cfg)
    parts = []
    for ch, g in u.groupby('channel'):
        ring = ch.startswith('isl_')
        g = g.merge(widths(ch, islands), on='transect', how='left')
        river = g.river.iloc[0]
        if ring:   # curvature of the channel ring (transect centres in order); side from the bank normal
            pos, _ = chainage(lines[river], s[river], g[['bx', 'by']].to_numpy())
            t = pd.read_csv(f'data/processed/{ch}/bank_positions.csv').drop_duplicates('transect').sort_values('transect')
            gr, k, lx, ly, sv = curvature(t[['cx', 'cy']].to_numpy(), ring=True)
            at = g.transect.map(dict(zip(t.transect, sv[:len(t)])))
            left = np.sign(g.nx * curv_at(gr, lx, at) + g.ny * curv_at(gr, ly, at))
            g['curv_bank'] = -curv_at(gr, k, at) * left
        else:      # curvature of the river's coarse centerline (continuous; stitched fine centres jump at tile seams)
            pos = g.chainage_m.to_numpy() + cfg['border_m'][river]
            gr, k, _, _, _ = curvature(lines[river], ring=False)
            g['curv_bank'] = -curv_at(gr, k, pos) * np.where(g.side == 'L', 1, -1)
        g['river_km'] = (pos - cfg['border_m'][river]) / 1e3
        g['vamnao_km'] = (pos - vam[river]) / 1e3
        g['node_km'] = np.abs(pos[:, None] - np.array(nodes[river])[None]).min(1) / 1e3
        parts.append(g)
    u = pd.concat(parts, ignore_index=True)
    isl = [p.buffer(100) for p in islands]   # JRC outline (90 m) vs Landsat bank: 100 m tolerance
    u['on_island'] = [any(p.contains(Point(x, y)) for p in isl) for x, y in zip(u.bx, u.by)]

    p, n = u[['bx', 'by']].to_numpy(), u[['nx', 'ny']].to_numpy()
    for key, f in rasters().items():
        v = np.column_stack([sample(f, p[:, 0] + n[:, 0] * d, p[:, 1] + n[:, 1] * d) for d in STRIP])
        v[v < 0] = np.nan   # nodata
        if key == 'built':
            u['built_500m'], u['built_1km'] = 100 * v[:, STRIP < 500].mean(1), 100 * v.mean(1)
        elif key == 'pop':
            u['pop_500m'], u['pop_1km'] = v[:, STRIP < 500].mean(1), v.mean(1)
        else:
            u['viirs_1km'] = v.mean(1)
    u['road_km'] = landward_road(p, n, road_vertices()) / 1e3
    t, _ = towns()
    u['town_km'] = cKDTree(t).query(p)[0] / 1e3
    return u


def per_unit(u, col):
    g = u.groupby(col)
    out = g.agg(river=('river', 'first'), channel=('channel', 'first'), side=('side', 'first'),
                n_points=('transect', 'size'), province=('province', lambda x: x.mode().iat[0]),
                river_km=('river_km', 'mean'), curv_bank=('curv_bank', 'mean'), width_m=('ref', 'median'),
                vamnao_km=('vamnao_km', 'mean'), node_km=('node_km', 'mean'), built_500m=('built_500m', 'mean'),
                built_1km=('built_1km', 'mean'), pop_500m=('pop_500m', 'mean'), pop_1km=('pop_1km', 'mean'),
                viirs_1km=('viirs_1km', 'mean'), road_km=('road_km', 'median'), town_km=('town_km', 'median'))
    out['is_island'] = (out.channel != out.river).astype(int)
    out['on_island_share'] = g.on_island.mean()
    out['curv_abs'] = g.curv_bank.apply(lambda x: x.abs().mean())
    out['outer_share'] = g.curv_bank.apply(lambda x: (x > OUTER_MIN).mean())
    out['dwidth_00_14'] = (u.w14 - u.w00).groupby(u[col]).median()
    out['dwidth_00_24'] = (u.w24 - u.w00).groupby(u[col]).median()
    out = out.reset_index().rename(columns={col: 'unit'})
    return out[['unit', 'river', 'channel', 'side', 'is_island', 'on_island_share', 'n_points', 'province'] + NUM].round(4)


# ---------- report and figure ----------

SOURCES = {   # covariate: (definition short, source, licence, year)
    'river_km': ('distance downstream of the border (km)', 'this study, coarse JRC centerline', '-', '-'),
    'curv_bank': ('curvature at the bank, + outer (1/km)', 'this study, Landsat banks (centerline)', '-', '2000-2024 centre'),
    'curv_abs': ('|curvature| (1/km)', 'same', '-', 'same'),
    'outer_share': (f'share of points with curv_bank > {OUTER_MIN}/km', 'same', '-', 'same'),
    'width_m': ('channel width, median 2000-2014 (m)', 'this study, Landsat banks', '-', '2000-2014'),
    'dwidth_00_14': ('width change 2000-02 -> 2012-14 (m)', 'same', '-', '2000-2014'),
    'dwidth_00_24': ('width change 2000-02 -> 2022-24 (m); NOT a model input', 'same', '-', '2000-2024'),
    'vamnao_km': ('along-river km from Vam Nao junction (+ downstream)', 'this study, coarse centerlines', '-', '-'),
    'node_km': ('along-river km to Vam Nao or an island head/tail', 'this study, tiles.json islands', '-', '-'),
    'built_500m': ('built-up share, landward 0-500 m (%)', 'GHSL GHS-BUILT-S R2023A (JRC)',
                   'EC reuse notice (CC BY 4.0), acknowledge source', str(REF_YEAR)),
    'built_1km': ('built-up share, landward 0-1000 m (%)', 'same', 'same', str(REF_YEAR)),
    'pop_500m': ('population density, landward 0-500 m (/km2)', 'WorldPop Global 100 m (unconstrained)', 'CC BY 4.0',
                 str(REF_YEAR)),
    'pop_1km': ('population density, landward 0-1000 m (/km2)', 'same', 'CC BY 4.0', str(REF_YEAR)),
    'viirs_1km': ('night lights, landward 0-1000 m (nW/cm2/sr)', 'VIIRS VNL V2.1 annual (EOG, Colorado School of Mines)',
                  'public domain (GEE catalog terms)', str(REF_YEAR)),
    'road_km': ('distance to OSM trunk/primary/secondary road, landward side (km)', 'OpenStreetMap (Overpass)',
                'ODbL, (c) OpenStreetMap contributors', OSM_DATE[:10]),
    'town_km': ('distance to OSM place=city|town (km)', 'OpenStreetMap (Overpass)', 'ODbL', OSM_DATE[:10]),
}


def report(c2, c5, u):
    lines = ['# Covariates per reach unit (H3)', '',
             f'`python src/covariates.py` -> `data/processed/covariates_2km.csv` ({len(c2)} units), '
             f'`covariates_5km.csv` ({len(c5)} units); definitions in the module docstring. Built from '
             f'{len(u)} in-scope bank points. Exposure reference year {REF_YEAR} (middle of the inventory window '
             f'2015-2024; GHSL epoch, last WorldPop year); OSM state {OSM_DATE[:10]}. The reported inventory was not '
             'read; no relation to erosion or labels is computed here.', '',
             '## Definitions, sources, licences', '', '| Covariate | Definition | Source | Licence | Year |',
             '|---|---|---|---|---|']
    lines += [f'| {k} | {a} | {b} | {c} | {d} |' for k, (a, b, c, d) in SOURCES.items()]
    lines += ['', 'Categorical: river (tien/hau), channel, side (L/R/I/O), is_island (bank on an island channel ring).',
              '']
    for name, c in (('2 km', c2), ('5 km', c5)):
        st = c[NUM].describe(percentiles=[.1, .5, .9]).T
        st['NaN'] = c[NUM].isna().sum()
        lines += [f'## Summary, {name} units (n = {len(c)})', '', '| Covariate | n | NaN | mean | p10 | median | p90 | min | max |',
                  '|---|---|---|---|---|---|---|---|---|']
        lines += [f'| {k} | {r["count"]:.0f} | {r.NaN:.0f} | {r["mean"]:.3g} | {r["10%"]:.3g} | {r["50%"]:.3g} | '
                  f'{r["90%"]:.3g} | {r["min"]:.3g} | {r["max"]:.3g} |' for k, r in st.iterrows()]
        lines += ['']
    lines += ['Units by channel type (2 km): ' + ', '.join(f'{k} {v}' for k, v in
                                                          c2.groupby(['river', 'is_island']).size().items()), '']
    sp, pe = c2[NUM].corr('spearman'), c2[NUM].corr('pearson')
    flags = [(a, b, sp.loc[a, b], pe.loc[a, b]) for i, a in enumerate(NUM) for b in NUM[i + 1:]
             if abs(sp.loc[a, b]) > .7 or abs(pe.loc[a, b]) > .7]
    lines += ['## Correlation among covariates (2 km units)', '',
              'Pairs with |r| > 0.7 (Spearman rho or Pearson r):', '']
    lines += [f'- {a} ~ {b}: rho = {s:+.2f}, r = {p:+.2f}' for a, b, s, p in flags] or ['- none']
    phys, expo = NUM[:9], NUM[9:]
    cross = [(a, b, sp.loc[a, b]) for a in phys for b in expo if abs(sp.loc[a, b]) > .3]
    lines += ['', 'Physical x exposure pairs with |rho| > 0.3 (confounding to watch in H3):', '']
    lines += [f'- {a} ~ {b}: rho = {s:+.2f}' for a, b, s in sorted(cross, key=lambda t: -abs(t[2]))] or ['- none']
    io = u[u.side.isin(['I', 'O'])].groupby('side').on_island.mean()
    wide = []
    for r in ('tien', 'hau'):
        w = u[u.channel == r].drop_duplicates('transect').set_index('chainage_m').sort_index().ref
        wide += list(u[u.channel == r].drop_duplicates('transect').sort_values('chainage_m').transect[
            (w > 2.5 * w.rolling(41, center=True, min_periods=10).median()).to_numpy()].map(f'{r} T{{}}'.format))
    lines += ['', '## Notes and checks', '',
              f'- Island bank labels: share of bank points lying on the island (tiles.json outline + 100 m): side I '
              f'{io.get("I", np.nan):.0%}, side O {io.get("O", np.nan):.0%}. If I is low and O high, the I/O labels in '
              'units.csv are the reverse of the documented convention (I = island bank). curv_bank uses the bank '
              'normals, not the labels, so it is unaffected; on_island_share gives the side geometrically.',
              f'- Transects whose 2000-2014 width exceeds 2.5x the 4 km running median (likely failed detections, '
              f'bank picked km away): {len(wide)}: ' + ', '.join(wide) + '. Unit widths are medians, so a minority '
              'of such transects does not move them; their bank points also shift the landward exposure samples.',
              '- Curvature of main channels is from the coarse JRC centerline (the stitched fine centres jump '
              'between channels at tile seams). On island rings it is the ring curvature: the bank facing the island '
              'is mostly inner by construction, and island heads/tails (flow splits) show as sharp bends.',
              '- Vam Nao junction = closest approach of the two coarse centerlines more than 20 km below the border '
              '(Tien km 50.5, Hau km 63.7); vamnao_km is river_km shifted per river, hence rho ~ 0.98 with river_km '
              '(use one of them).',
              '- Exposure strips follow the bank normal landward; on islands they run into the island and may cross '
              'it. road_km ignores roads across the channel (half-plane test), town_km does not (ferries and bridges).',
              f'- OSM queried as of {OSM_DATE[:10]} (Overpass attic); places are OSM place=city|town nodes (cities, '
              'district seats and some townships), 53 in the box incl. Cambodian ones near the border.',
              '- dwidth_00_24 overlaps the 2015-2024 label window and must not be a model input; dwidth_00_14 and '
              'width_m use 2000-2014 only.']
    lines += ['', 'Spearman rho matrix:', '', '| | ' + ' | '.join(NUM) + ' |', '|---' * (len(NUM) + 1) + '|']
    lines += [f'| {a} | ' + ' | '.join(f'{sp.loc[a, b]:+.2f}' for b in NUM) + ' |' for a in NUM]
    return lines


def figure(c2):
    from figures import BLUE, COL2, INK2, ORANGE, TOWNS, chart_axes, save
    cfg = json.loads(pathlib.Path('data/tiles.json').read_text())
    fig, axes = plt.subplots(3, 2, figsize=(COL2, COL2 * .62), sharex=True, gridspec_kw={'hspace': .25, 'wspace': .22})
    rows = [('curv_bank', 'Curvature at bank\n(1/km, + outer)'), ('width_m', 'Width 2000–2014\n(km)'),
            ('built_1km', 'Built-up 0–1 km\nlandward (%)')]
    for j, river in enumerate(('tien', 'hau')):
        m = c2[(c2.river == river) & (c2.is_island == 0)].sort_values('river_km')
        line = np.array(cfg['centerlines'][river])
        sl = np.r_[0, np.cumsum(np.hypot(*np.diff(line, axis=0).T))]
        for i, (col, lab) in enumerate(rows):
            ax = axes[i, j]
            if col == 'width_m':   # one value per cross-section: both banks' units carry it
                g = m.dropna(subset=[col]).groupby((m.river_km // 2).rename('k')).agg(x=('river_km', 'mean'), y=(col, 'median'))
                ax.step(g.x, g.y / 1e3, where='mid', color=INK2, lw=.9)
            else:
                for side, cc, name in (('L', BLUE, 'left bank'), ('R', ORANGE, 'right bank')):
                    g = m[m.side == side]
                    ax.step(g.river_km, g[col], where='mid', color=cc, lw=.9, label=name)
            if col == 'curv_bank':
                ax.axhline(0, color=INK2, lw=.6)
            chart_axes(ax)
            if j == 0:
                ax.set_ylabel(lab)
        for name, (lon, lat, _) in TOWNS.items():   # town ticks on the built-up row (sanity check)
            x, y = transform('EPSG:4326', CRS, [lon], [lat])
            p, off = chainage(line, sl, np.array([[x[0], y[0]]]))
            km = (p[0] - cfg['border_m'][river]) / 1e3
            if off[0] < 6000 and km <= m.river_km.max() + 2:
                axes[2, j].axvline(km, color=INK2, lw=.5, ls=':')
                axes[2, j].text(km, .98, name, transform=axes[2, j].get_xaxis_transform(), rotation=90, fontsize=7,
                                ha='right', va='top', color=INK2)
        axes[2, j].set_ylim(0, m.built_1km.max() * 3.6)   # headroom: town names sit above the data, not on it
        axes[0, j].set_title(f'({"ab"[j]}) {"Tien" if river == "tien" else "Hau"} River, main channel', loc='left',
                             pad=3, fontweight='bold')
        axes[2, j].set_xlabel('Distance downstream of the border (km)')
    axes[0, 0].legend(loc='lower left', ncol=2, handlelength=1.2)
    save(fig, 'fig06_covariates')


def main():
    out = pathlib.Path('data/processed')
    if sys.argv[1:] == ['fig']:
        figure(pd.read_csv(out / 'covariates_2km.csv'))
        return
    cfg = json.loads(pathlib.Path('data/tiles.json').read_text())
    u = point_covariates(points(), cfg)
    c2, c5 = per_unit(u, 'unit_2km'), per_unit(u, 'unit_5km')
    c2.to_csv(out / 'covariates_2km.csv', index=False, encoding='utf-8')
    c5.to_csv(out / 'covariates_5km.csv', index=False, encoding='utf-8')
    pathlib.Path('results/p1/covariates.md').write_text('\n'.join(report(c2, c5, u)) + '\n', encoding='utf-8')
    print(f'{len(c2)} units of 2 km, {len(c5)} of 5 km; NaN per covariate (2 km):',
          c2[NUM].isna().sum()[lambda x: x > 0].to_dict())
    figure(c2)


if __name__ == '__main__':
    main()
