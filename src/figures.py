"""Manuscript figures (static, print): PNG 300 dpi + SVG (text kept as text) in figures/.

Usage: python src/figures.py [study_area method validation change ...]   (default: all that have their inputs)
Sizes are journal column widths (Copernicus: ~8.3 cm one column, ~17 cm two columns); text >= 7 pt at that size.
Colours: categorical slots 1-3 of the validated dataviz palette (CVD-safe all-pairs); diverging blue (accretion) <->
red (erosion) through a neutral grey; water as one blue ramp. Light background only (print).
Cached inputs (re-creatable, gitignored): data/raw/fig_jrc_4326.tif, data/raw/fig_boundaries.json.
"""
import json
import pathlib
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
import requests
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Polygon, Rectangle
from rasterio.warp import transform
from scipy.stats import theilslopes

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from banklines import read  # noqa: E402
from tile_check import P0, match, project  # noqa: E402

OUT = pathlib.Path('figures')
COL1, COL2 = 8.3 / 2.54, 17.0 / 2.54
BLUE, ORANGE, AQUA, YELLOW = '#2a78d6', '#eb6834', '#1baf7a', '#eda100'   # categorical slots 1-4
INK, INK2, GRID = '#0b0b0b', '#52514e', '#d9d8d4'
WATER = LinearSegmentedColormap.from_list('water', ['#ffffff', '#d3d2cd', '#8f8e89'])   # grey, so river lines carry colour
RATE = LinearSegmentedColormap.from_list('rate', ['#184f95', '#6da7ec', '#c8c7c2', '#ec8a89', '#b52f2e'])
REGION = [104.95, 9.95, 106.0, 11.0]
LAT0 = 10.5
P0_REACHES = {'sadec_caolanh': 'Sa Đéc–Cao Lãnh', 'longxuyen': 'Long Xuyên', 'mythuan': 'Mỹ Thuận'}
TOWNS = {  # lon, lat, label offset (points)
    'Tân Châu': (105.24, 10.80, (-40, 5)), 'Châu Đốc': (105.117, 10.705, (-44, -4)),
    'Long Xuyên': (105.435, 10.386, (-52, -6)), 'Cao Lãnh': (105.632, 10.459, (5, 3)),
    'Sa Đéc': (105.757, 10.296, (-34, -9)), 'Cần Thơ': (105.78, 10.035, (-38, -4)),
    'Hồng Ngự': (105.343, 10.808, (5, 3)), 'Mỹ Thuận': (105.915, 10.275, (-12, 8)),
}
SIWRR = {'2003-2006': -30.0, '2006-2014': -41.5, '2014-2017': -11.5, '2017-2021': -23.0}   # ha, left bank (Dinh et al. 2022)

plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 8, 'axes.labelsize': 8, 'axes.titlesize': 8,
    'xtick.labelsize': 7, 'ytick.labelsize': 7, 'legend.fontsize': 7, 'axes.edgecolor': INK2,
    'axes.labelcolor': INK, 'xtick.color': INK2, 'ytick.color': INK2, 'axes.linewidth': .6,
    'xtick.major.width': .6, 'ytick.major.width': .6, 'lines.linewidth': 1.2, 'svg.fonttype': 'none',
    'pdf.fonttype': 42, 'savefig.dpi': 300, 'legend.frameon': False,
})


def save(fig, name):
    OUT.mkdir(exist_ok=True)
    for ext in ('png', 'svg'):
        fig.savefig(OUT / f'{name}.{ext}', bbox_inches='tight', pad_inches=.02)
    plt.close(fig)
    print('wrote', OUT / f'{name}.png')


def panel(ax, letter):
    ax.text(0, 1.01, f'({letter})', transform=ax.transAxes, fontweight='bold', va='bottom')


def chart_axes(ax):
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(color=GRID, lw=.5)
    ax.set_axisbelow(True)


def ee_init():
    import ee
    ee.Initialize(project='mekong-bankline')
    return ee


def jrc_4326():
    f = pathlib.Path('data/raw/fig_jrc_4326.tif')
    if not f.exists():
        ee = ee_init()
        img = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('occurrence').unmask(0)
        url = img.getDownloadURL({'region': ee.Geometry.Rectangle(REGION), 'scale': 90, 'crs': 'EPSG:4326',
                                  'format': 'GEO_TIFF'})
        r = requests.get(url, timeout=600)
        r.raise_for_status()
        f.write_bytes(r.content)
    with rasterio.open(f) as src:
        b = src.bounds
        return src.read(1), (b.left, b.right, b.bottom, b.top)


def boundaries():
    """Countries (LSIB 2017, simplified) around the delta and pre-2025 provinces (FAO GAUL 2015) over REGION."""
    f = pathlib.Path('data/raw/fig_boundaries.json')
    if not f.exists():
        ee = ee_init()
        box = ee.Geometry.Rectangle([101, 8, 110, 16])
        countries = (ee.FeatureCollection('USDOS/LSIB_SIMPLE/2017')
                     .filter(ee.Filter.inList('country_na', ['Vietnam', 'Cambodia', 'Laos', 'Thailand']))
                     .map(lambda x: x.setGeometry(x.geometry().intersection(box, 1000).simplify(1000))))
        prov = (ee.FeatureCollection('FAO/GAUL/2015/level1').filter(ee.Filter.eq('ADM0_NAME', 'Viet Nam'))
                .filterBounds(ee.Geometry.Rectangle(REGION))
                .map(lambda x: x.setGeometry(x.geometry().simplify(100))))
        f.write_text(json.dumps({'countries': countries.getInfo(), 'provinces': prov.getInfo()}))
    return json.loads(f.read_text())


def rings(geom):
    polys = geom['coordinates'] if geom['type'] == 'MultiPolygon' else [geom['coordinates']] \
        if geom['type'] == 'Polygon' else []
    if geom['type'] == 'GeometryCollection':
        return [r for g in geom['geometries'] for r in rings(g)]
    return [np.array(p[0]) for p in polys]


def scalebar(ax, lon, lat, km):
    dlon = km / (111.32 * np.cos(np.radians(lat)))
    ax.plot([lon, lon + dlon], [lat, lat], color=INK, lw=2, solid_capstyle='butt')
    ax.text(lon + dlon / 2, lat + .012, f'{km} km', ha='center', va='bottom', fontsize=7)


def north(ax, lon, lat):
    ax.annotate('N', xy=(lon, lat), xytext=(lon, lat - .07), ha='center', va='center', fontsize=8, fontweight='bold',
                arrowprops=dict(arrowstyle='-|>', color=INK, lw=1))


def study_area():
    occ, ext = jrc_4326()
    bd = boundaries()
    tiles = json.loads(pathlib.Path('data/tiles.json').read_text())
    fig, ax = plt.subplots(figsize=(COL2, COL2 * .86))
    ax.imshow(np.clip(occ, 40, 100), cmap=WATER, vmin=40, vmax=100, extent=ext, interpolation='bilinear')  # fade flooded fields
    for p in bd['provinces']['features']:
        for r in rings(p['geometry']):
            ax.plot(r[:, 0], r[:, 1], color='#9a9994', lw=.4)
    for c in bd['countries']['features']:
        if c['properties']['country_na'] == 'Cambodia':
            for r in rings(c['geometry']):
                ax.plot(r[:, 0], r[:, 1], color=INK2, lw=.9, ls=(0, (5, 2, 1, 2)))
    for p in bd['provinces']['features']:
        name = p['properties']['ADM1_NAME']
        lab = {'An Giang': (105.13, 10.48, 'An Giang'), 'Dong Thap': (105.62, 10.72, 'Đồng Tháp'),
               'Can Tho City': (105.55, 10.08, 'Cần Thơ'), 'Vinh Long': (105.96, 10.12, 'Vĩnh Long'),
               'Tien Giang': (105.96, 10.42, 'Tiền Giang')}.get(name)
        if lab:
            ax.text(*lab, fontsize=7, color=INK2, style='italic', ha='center')
    for river, col in (('tien', ORANGE), ('hau', BLUE)):
        units = pd.read_csv('data/processed/units.csv')
        first = units[(units.channel == river) & units.province.notna()].chainage_m.min() + tiles['border_m'][river]
        xy = np.array(tiles['centerlines'][river])[max(int(first / 100), 0):]   # 100 m vertices, from the first VN bank
        lon, lat = transform('EPSG:32648', 'EPSG:4326', xy[:, 0], xy[:, 1])
        ax.plot(lon, lat, color=col, lw=1.6, solid_capstyle='round',
                label=f'{"Tien" if river == "tien" else "Hau"} River, analysed reach ({xy.shape[0] * .1:.0f} km)')
    from gee_water import REACHES
    for n, (k, name) in enumerate(P0_REACHES.items(), 1):
        x0, y0, x1, y1 = REACHES[k]
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec=INK, lw=.8))
        ax.text(x0 + .008, y1 - .008, str(n), fontsize=7, fontweight='bold', va='top')
    ax.plot([], [], color=INK, lw=.8, label='Test reaches: 1 ' + ', 2 '.join(['Sa Đéc–Cao Lãnh', 'Long Xuyên'])
            + ', 3 Mỹ Thuận')
    for name, (lon, lat, off) in TOWNS.items():
        ax.plot(lon, lat, 'o', ms=3, mfc=INK, mec='white', mew=.5)
        ax.annotate(name, (lon, lat), xytext=off, textcoords='offset points', fontsize=7)
    ax.text(105.30, 10.955, 'Cambodia', fontsize=7, color=INK2, style='italic', ha='center')
    ax.set_xlim(104.98, 106.0)
    ax.set_ylim(9.97, 10.98)
    ax.set_aspect(1 / np.cos(np.radians(LAT0)))
    ax.xaxis.set_major_formatter(lambda v, _: f'{v:.1f}°E')
    ax.yaxis.set_major_formatter(lambda v, _: f'{v:.1f}°N')
    scalebar(ax, 105.02, 10.0, 20)
    north(ax, 105.03, 10.63)
    ax.plot([], [], color=INK2, lw=.9, ls=(0, (5, 2, 1, 2)), label='International border')
    ax.plot([], [], color='#9a9994', lw=.4, label='Province boundary (before 2025)')
    ax.legend(loc='upper center', bbox_to_anchor=(.5, -.06), ncol=2, handlelength=1.6, columnspacing=1.5)
    ins = ax.inset_axes([.72, .66, .26, .32])
    for c in bd['countries']['features']:
        for r in rings(c['geometry']):
            ins.add_patch(Polygon(r, fc='#e8e7e3' if c['properties']['country_na'] != 'Vietnam' else '#c8c7c2',
                                  ec='white', lw=.4))
    ins.add_patch(Rectangle((REGION[0], REGION[1]), 1.05, 1.05, fill=False, ec='#b52f2e', lw=1))
    ins.text(106.3, 13.3, 'Vietnam', fontsize=6, color=INK2)
    ins.text(104.2, 12.6, 'Cambodia', fontsize=6, color=INK2, ha='center')
    ins.set_xlim(102, 109.6)
    ins.set_ylim(8.3, 15.2)
    ins.set_aspect(1 / np.cos(np.radians(12)))
    ins.set_xticks([])
    ins.set_yticks([])
    ins.set_facecolor('#f7f9fc')
    save(fig, 'fig01_study_area')


def siwrr_areas():
    """Left-bank eroded area per SIWRR period, T255-315 of sadec_caolanh (as in results/p0/sadec_caolanh_siwrr_check.md)."""
    bp = pd.read_csv('data/processed/sadec_caolanh/bank_positions.csv')
    bp = bp[(bp.side == 'L') & bp.transect.between(255, 315) & ~bp.spike]
    at = {y: bp[bp.year.between(y - 1, y + 1)].groupby('transect').dist_m.mean() for y in (2003, 2006, 2014, 2017, 2021)}
    return {p: -(at[int(p[5:])] - at[int(p[:4])]).sum() * 100 / 1e4 for p in SIWRR}


def method():
    reach, tr_id = 'sadec_caolanh', None
    tr = pd.read_csv(f'data/processed/{reach}/trends.csv')
    hot = tr[tr.stable & (tr.side == 'L') & tr.transect.between(270, 300)]
    tr_id = int(hot.loc[hot.lrr.idxmax(), 'transect'])
    bp = pd.read_csv(f'data/processed/{reach}/bank_positions.csv')
    m24, tf = read(sorted(pathlib.Path('data/raw', reach).glob('mndwi_2024.tif'))[0])
    fig, (a, b) = plt.subplots(1, 2, figsize=(COL2, COL2 * .42), gridspec_kw={'width_ratios': [1, 1.25], 'wspace': .25})
    left = bp[(bp.side == 'L') & bp.transect.between(tr_id - 30, tr_id + 30)]
    c = left.drop_duplicates('transect')
    x0, y0 = c.cx.mean(), c.cy.mean()
    H, W = m24.shape
    ext = ((tf.c - x0) / 1e3, (tf.c + W * tf.a - x0) / 1e3, (tf.f + H * tf.e - y0) / 1e3, (tf.f - y0) / 1e3)
    a.imshow(m24, cmap='Greys', vmin=-.6, vmax=.6, extent=ext, interpolation='nearest')   # MNDWI 2024, water dark
    allc = bp.drop_duplicates(['transect'])
    a.plot((allc.cx - x0) / 1e3, (allc.cy - y0) / 1e3, color='white', lw=.8, ls=(0, (3, 2)))
    for _, r in c[c.transect % 5 == 0].iterrows():
        a.plot([(r.cx - x0) / 1e3, (r.cx + r.nx * 3000 - x0) / 1e3], [(r.cy - y0) / 1e3, (r.cy + r.ny * 3000 - y0) / 1e3],
               color='#9a9994', lw=.4)
    for yr, col in ((2000, BLUE), (2024, ORANGE)):
        g = left[(left.year == yr) & ~left.spike].dropna(subset=['dist_m'])
        a.plot((g.cx + g.nx * g.dist_m - x0) / 1e3, (g.cy + g.ny * g.dist_m - y0) / 1e3, color=col, lw=1.4,
               label=f'Bank {yr}')
    r = c[c.transect == tr_id].iloc[0]
    a.plot([(r.cx - x0) / 1e3, (r.cx + r.nx * 3000 - x0) / 1e3], [(r.cy - y0) / 1e3, (r.cy + r.ny * 3000 - y0) / 1e3],
           color=INK, lw=1)
    a.plot([], [], color=INK, lw=1, label=f'Transect T{tr_id} (panel b)')
    a.set_xlim(-3.2, 3.2)
    a.set_ylim(-3.2, 3.2)
    a.set_aspect('equal')
    a.set_xticks([])
    a.set_yticks([])
    a.plot([1.9, 2.9], [-2.9, -2.9], color=INK, lw=2, solid_capstyle='butt')
    a.text(2.4, -2.8, '1 km', ha='center', va='bottom', fontsize=7)
    a.legend(loc='upper center', bbox_to_anchor=(.5, -.01), ncol=2, handlelength=1.4, columnspacing=1)
    panel(a, 'a')

    s = bp[(bp.transect == tr_id) & (bp.side == 'L')].dropna(subset=['dist_m'])
    ok, sp = s[~s.spike], s[s.spike]
    slope, icpt, lo, hi = theilslopes(ok.dist_m, ok.year)
    d0 = ok.dist_m.iloc[0]                      # first observed bank (2000)
    b.plot(ok.year, ok.dist_m - d0, 'o', ms=4, mfc=BLUE, mec='white', mew=.5, label='Annual dry-season bank')
    if len(sp):
        b.plot(sp.year, sp.dist_m - d0, 'o', ms=4, mfc='white', mec=BLUE, mew=.8,
               label='Reverting jump (excluded)')
    yy = np.array([2000, 2024])
    b.plot(yy, icpt + slope * yy - d0, color=INK, lw=1, label=f'Theil–Sen {slope:.1f} m/yr (95% CI {lo:.1f}–{hi:.1f})')
    b.set_xlabel('Year')
    b.set_ylabel('Bank retreat since 2000 (m)')
    chart_axes(b)
    b.legend(loc='upper left')
    panel(b, 'b')
    save(fig, 'fig02_method_example')


def clicks(reach, narrow=None):
    """Hand-clicked banks joined to the final (stitched) Landsat positions; flagged-unstable and explore items left out.
    For a stitched river, narrow=True/False keeps only clicks up-/downstream of its narrow_until_m."""
    src = pathlib.Path('data/processed', reach)
    cl = pd.read_csv(src / 'accuracy_review.csv', encoding='utf-8-sig').drop_duplicates('id', keep='last')
    flagged = {i['id'] for i in json.loads((src / 'review_points.json').read_text())['items'] if i.get('unstable')}
    cl = cl[cl.verdict.eq('clicked') & ~cl.explore.astype(str).eq('True') & ~cl.id.isin(flagged)]
    if reach in P0:   # P0 reach: evaluate the stitched full-river banks along the P0 transects (tile_check.py)
        p0, st = pd.read_csv(src / 'bank_positions.csv'), pd.read_csv(f'data/processed/{P0[reach]}/bank_positions.csv')
        bp = project(p0, st, match(p0, st)).drop(columns='dist_m').rename(columns={'s_on_p0': 'dist_m'})
    else:
        bp = pd.read_csv(src / 'bank_positions.csv')
    if narrow is not None:
        to = json.loads(pathlib.Path('data/tiles.json').read_text())['narrow_until_m'].get(reach, 0)
        bp = bp[(bp.chainage_m < to) == narrow]
    bp = bp[['transect', 'side', 'year', 'dist_m']]
    return cl.merge(bp.rename(columns={'year': 'compared_year'}), on=['transect', 'side', 'compared_year']).dropna(
        subset=['dist_m', 'user_dist_m'])


def validation():
    fig, (a, b) = plt.subplots(1, 2, figsize=(COL2, COL2 * .4), gridspec_kw={'wspace': .3, 'width_ratios': [1.35, 1]})
    groups = [('Tien\nmain', [('sadec_caolanh', None), ('mythuan', None), ('tien', None)], BLUE),
              ('Hau\nwide', [('longxuyen', None), ('hau', False)], ORANGE),
              ('Hau\nnarrow', [('hau', True)], AQUA),
              ('Island\nchannels', [('islands', None)], YELLOW)]   # groups apart on x and labelled
    labels = []
    rng = np.random.default_rng(0)
    for i, (name, reaches, col) in enumerate(groups):
        e = pd.concat([clicks(*r) for r in reaches]).pipe(lambda d: d.dist_m - d.user_dist_m)
        a.plot(i + rng.uniform(-.18, .18, len(e)), e, 'o', ms=4, mfc=col, mec='white', mew=.5)
        a.plot([i - .28, i + .28], [e.median()] * 2, color=INK, lw=1.2)
        labels.append(f'{name}\nn = {len(e)}\nRMSE {np.sqrt((e ** 2).mean()):.0f} m')
    a.axhline(0, color=INK2, lw=.6)
    a.set_xticks(range(len(groups)), labels, fontsize=7)
    a.set_xlim(-.6, len(groups) - .4)
    a.set_ylabel('Landsat bank − hand-clicked bank (m)\n(negative = Landsat bank riverward)')
    chart_axes(a)
    a.grid(axis='x', visible=False)
    panel(a, 'a')

    ours = siwrr_areas()
    x = np.arange(len(SIWRR))
    b.bar(x - .2, -np.array(list(SIWRR.values())), .38, color=INK2, label=f'SIWRR (Dinh et al., 2022): {-sum(SIWRR.values()):.0f} ha')
    b.bar(x + .2, -np.array(list(ours.values())), .38, color=BLUE, label=f'This study: {-sum(ours.values()):.0f} ha')
    b.set_xticks(x, [k.replace('-', '–\n') for k in SIWRR])
    b.set_ylabel('Eroded area, left bank (ha)')
    chart_axes(b)
    b.grid(axis='x', visible=False)
    b.set_ylim(0, 62)
    b.legend(loc='upper left')
    panel(b, 'b')
    save(fig, 'fig04_validation')
    return ours


def change():
    """Linear bank-change rates along both rivers: map + along-river profiles (stitched P1 output)."""
    occ, ext = jrc_4326()
    fig = plt.figure(figsize=(COL2, COL2 * .66))
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 1], wspace=.3, hspace=.5)
    ax = fig.add_subplot(gs[:, 0])
    ax.imshow(np.clip(occ, 40, 100), cmap=WATER, vmin=40, vmax=100, extent=ext, interpolation='bilinear')
    lim = 10
    border = json.loads(pathlib.Path('data/tiles.json').read_text())['border_m']
    for k, river in enumerate(('tien', 'hau')):
        # Branches reuse transect ids; these panels show only the main channel.
        vn = pd.read_csv('data/processed/units.csv').query('channel == @river and province.notna()')[['transect', 'side']]
        tr = pd.read_csv(f'data/processed/{river}/trends.csv').merge(
            vn, on=['transect', 'side'], validate='one_to_one')   # banks in Vietnam
        bp = pd.read_csv(f'data/processed/{river}/bank_positions.csv')
        d = bp[bp.dist_m.notna() & ~bp.spike].groupby(['transect', 'side']).dist_m.median().rename('d')
        tr = tr.join(d, on=['transect', 'side'])
        lon, lat = transform('EPSG:32648', 'EPSG:4326', (tr.cx + tr.nx * tr.d).tolist(), (tr.cy + tr.ny * tr.d).tolist())
        tr['lon'], tr['lat'] = lon, lat
        ok, bad = tr[tr.stable], tr[~tr.stable]
        ax.scatter(bad.lon, bad.lat, s=1.5, c='#9a9994', lw=0, zorder=2)
        sc = ax.scatter(ok.lon, ok.lat, s=2.5, c=ok.lrr.clip(-lim, lim), cmap=RATE, vmin=-lim, vmax=lim, lw=0, zorder=3)
        pa = fig.add_subplot(gs[k, 1])
        for side, col, name in (('L', BLUE, 'left bank'), ('R', ORANGE, 'right bank')):
            g = ok[ok.side == side]
            pa.plot((g.chainage_m - border[river]) / 1e3, g.lrr, 'o', ms=1.6, mfc=col, mec='none', label=name)
        pa.axhline(0, color=INK2, lw=.6)
        pa.set_xlim(-10, 150)
        pa.set_ylim(-15, 22)
        pa.set_ylabel('Rate (m/yr)')
        chart_axes(pa)
        pa.set_title(f'({"bc"[k]}) {"Tien" if river == "tien" else "Hau"} River', loc='left', pad=3, fontweight='bold')
        pa.text(1, 1.01, '+ erosion, − accretion', transform=pa.transAxes, ha='right', va='bottom', fontsize=7,
                color=INK2)
        if k == 0:
            pa.legend(loc='upper right', markerscale=3, handletextpad=.1, ncol=2)
        else:
            pa.set_xlabel('Distance downstream of the border (km)')
    ax.set_xlim(104.98, 106.0)
    ax.set_ylim(9.97, 10.98)
    ax.set_aspect(1 / np.cos(np.radians(LAT0)))
    ax.xaxis.set_major_formatter(lambda v, _: f'{v:.1f}°E')
    ax.yaxis.set_major_formatter(lambda v, _: f'{v:.1f}°N')
    ax.tick_params(axis='x', labelrotation=0)
    ax.set_xticks([105.2, 105.6, 106.0])
    scalebar(ax, 105.02, 10.0, 20)
    ax.set_title('(a)', loc='left', pad=3, fontweight='bold')
    cb = fig.colorbar(sc, ax=ax, orientation='horizontal', fraction=.04, pad=.07, extend='both')
    cb.set_label('Bank change 2000–2024 (m/yr, + erosion)')
    cb.outline.set_linewidth(.4)
    ax.scatter([], [], s=6, c='#9a9994', label='Step or non-linear change')
    ax.legend(loc='upper right', markerscale=1.5, handletextpad=.1)
    save(fig, 'fig03_bank_change')


FIGS = {'study_area': study_area, 'method': method, 'change': change, 'validation': validation}

if __name__ == '__main__':
    for n in sys.argv[1:] or FIGS:
        FIGS[n]()
