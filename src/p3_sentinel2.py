"""P3 R1: Sentinel-2 banks 2017-2024 against Landsat (docs/p3_plan.md R1, criterion fixed before running).

Usage: python src/p3_sentinel2.py        checks (a), (b), (c) -> results/p3/sentinel2.md, data/processed/p3_s2_*.csv, figure
       python src/p3_sentinel2.py fig    only redraw figures/fig11_sentinel2 from the written CSVs
Reads Landsat banks data/processed/{tien,hau,islands}/bank_positions.csv and Sentinel-2 banks on the same transect ids
data/processed/s2/{tien,hau,islands}/bank_positions.csv (src/gee_s2.py, src/s2_banks.py), units.csv (in-scope points),
the hand clicks data/processed/<reach>/accuracy_review.csv, forecast_h3_mean.csv (frozen GBT h = 3 test intervals) and
h3_units.csv (2 km units: block, rep).
(a) S2 - Landsat per in-scope transect-side and year 2017-2024 (spikes left out in both), by channel group; clicks:
    each click against the bank of its compared_year from both sensors (figures.clicks rules: P0 reaches through the
    stitched product projected on the P0 transect; flagged-unstable and explore items left out).
(b) Frozen intervals (lo/hi_gbt_split, lo/hi_gbt_mondrian) scored against y_S2 = d_S2(t + 3) - d_S2(t), d = 3-yr centred
    mean (forecast.centred: >= 2 valid years), origins >= 2018; Landsat truth y on the same rows. 95% CIs: forecast.boot
    (10 km blocks, 1000 resamples, seed 0). Criterion: pooled split and Mondrian coverage vs S2 truth within 90 +- 3 pp.
(c) Unit window retreat 2017-19 -> 2022-24 (sat_labels.change: >= 2 valid years per mean, MAX_RATE; unit p75 over
    >= MIN_PTS points), S2 vs Landsat on the H3 2 km units; label >= 20 m; omission = share of label-positive units with
    rep == 0. CIs: h3.boot_index / h3.boot (10 km blocks, B = 1000). Descriptive.
"""
import json
import pathlib
import sys

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import cohen_kappa_score

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import forecast as fc  # noqa: E402
import h3  # noqa: E402
import sat_labels as sl  # noqa: E402
from figures import AQUA, BLUE, COL2, GRID, INK, INK2, ORANGE, YELLOW, chart_axes, plt, save  # noqa: E402
from tile_check import P0, match, project  # noqa: E402

S2 = pathlib.Path('data/processed/s2')
L8 = pathlib.Path('data/processed')
OUT = pathlib.Path('results/p3')
YRS = list(range(2017, 2025))
WIN = ((2017, 2019), (2022, 2024))
GROUPS = fc.GROUPS                       # Tien main, Hau wide, Hau narrow, Island
GCOL = dict(zip(GROUPS, (BLUE, ORANGE, AQUA, YELLOW)))
CLICK_GROUPS = [('Tien main', [('sadec_caolanh', None), ('mythuan', None), ('tien', None)]),
                ('Hau wide', [('longxuyen', None), ('hau', False)]), ('Hau narrow', [('hau', True)]),
                ('Island', [('islands', None)])]
METH = ['split', 'mondrian']
CSV = {k: L8 / f'p3_s2_{k}.csv' for k in ('diff', 'coverage', 'units')}


# ---------- inputs ----------

def wide(u, root):
    """sat_labels.positions for another product root: annual bank distance per in-scope point (NaN = none / spike)."""
    bp = pd.concat([pd.read_csv(root / r / 'bank_positions.csv').assign(channel=r) for r in ('tien', 'hau')]
                   + [pd.read_csv(root / 'islands' / 'bank_positions.csv').drop(columns='transect')
                      .rename(columns={'ring_transect': 'transect'})])
    bp = bp[bp.dist_m.notna() & ~bp.spike.astype(bool)]
    w = bp.pivot_table(index=sl.KEY, columns='year', values='dist_m').reindex(columns=sl.YEARS)
    return w.reindex(pd.MultiIndex.from_frame(u[sl.KEY]))


def points():
    """In-scope points with forecast group and 10 km block (forecast.load rules, without the covariates)."""
    cfg = json.loads(pathlib.Path('data/tiles.json').read_text())
    u = sl.points()
    narrow = cfg['narrow_until_m']['hau'] - cfg['border_m']['hau']
    isl = u.channel.str.startswith('isl_')
    u['group'] = np.select([u.channel == 'tien', (u.channel == 'hau') & (u.chainage_m < narrow), u.channel == 'hau'],
                           GROUPS[:3], GROUPS[3])
    ikm = u.channel.map({k: (v['chainage_m'] - cfg['border_m'][v['parent']]) / 1e3 for k, v in cfg['islands'].items()})
    u['block'] = u.river + '_' + (np.where(isl, ikm, u.chainage_m / 1e3) // 10).astype(int).astype(str)
    return u


def ci(est, lo, hi, d=1, pct=False):
    k = 100 if pct else 1
    return f'{k * est:.{d}f} [{k * lo:.{d}f}, {k * hi:.{d}f}]'


# ---------- (a) ----------

def check_a(u, WL, WS):
    rows = []
    for j, y in enumerate(YRS):
        a, b = WL[y].to_numpy(), WS[y].to_numpy()
        rows.append(pd.DataFrame({'channel': u.channel, 'transect': u.transect, 'side': u.side, 'group': u.group,
                                  'block': u.block, 'year': y, 'landsat': a, 's2': b}))
    long = pd.concat(rows, ignore_index=True)
    long['diff'] = long.s2 - long.landsat
    return long


def a_table(long, by):
    med = lambda x: np.median(x)
    rsd = lambda x: 1.4826 * np.median(np.abs(x - np.median(x)))
    w30 = lambda x: np.mean(np.abs(x) <= 30)
    out = []
    for key, d in [('all', long)] + list(long.groupby(by)):
        both = d.dropna(subset=['diff'])
        x, blk = both['diff'].to_numpy(), both.block.to_numpy()
        r = {by: key, 'Landsat banks': int(d.landsat.notna().sum()),
             'S2 bank also (%)': f'{100 * d.s2[d.landsat.notna()].notna().mean():.0f}',
             'pairs': len(x), 'blocks': len(np.unique(blk))}
        if not len(x):                     # 2017: no Sentinel-2 composite kept
            out.append(r)
            continue
        idx = h3.boot_index(blk)
        for name, fn, d_ in (('median S2 - Landsat (m)', med, 1), ('robust SD (m)', rsd, 1)):
            r[name] = ci(*h3.boot(lambda i: fn(x[i]), len(x), idx)[:3], d=d_)
        r['|diff| <= 30 m (%)'] = ci(*h3.boot(lambda i: w30(x[i]), len(x), idx)[:3], d=0, pct=True)
        out.append(r)
    return pd.DataFrame(out)


def clicks(reach, narrow, root):
    """figures.clicks with the bank product taken from root (Landsat L8 or Sentinel-2 S2)."""
    src = L8 / reach
    cl = pd.read_csv(src / 'accuracy_review.csv', encoding='utf-8-sig').drop_duplicates('id', keep='last')
    flagged = {i['id'] for i in json.loads((src / 'review_points.json').read_text())['items'] if i.get('unstable')}
    cl = cl[cl.verdict.eq('clicked') & ~cl.explore.astype(str).eq('True') & ~cl.id.isin(flagged)]
    if reach in P0:
        p0, st = pd.read_csv(src / 'bank_positions.csv'), pd.read_csv(root / P0[reach] / 'bank_positions.csv')
        bp = project(p0, st, match(p0, st)).drop(columns='dist_m').rename(columns={'s_on_p0': 'dist_m'})
    else:
        bp = pd.read_csv(root / reach / 'bank_positions.csv')
    if narrow is not None:
        to = json.loads(pathlib.Path('data/tiles.json').read_text())['narrow_until_m'].get(reach, 0)
        bp = bp[(bp.chainage_m < to) == narrow]
    bp = bp[['transect', 'side', 'year', 'dist_m']].rename(columns={'year': 'compared_year'})
    return cl.merge(bp, on=['transect', 'side', 'compared_year'], how='left')[['id', 'compared_year', 'user_dist_m',
                                                                              'dist_m']].assign(reach=reach)


def click_table():
    rows, allc = [], []
    rng = np.random.default_rng(0)
    for g, reaches in CLICK_GROUPS:
        a = pd.concat([clicks(r, n, L8) for r, n in reaches])
        b = pd.concat([clicks(r, n, S2) for r, n in reaches])
        c = a.merge(b[['reach', 'id', 'dist_m']], on=['reach', 'id'], suffixes=('_l', '_s')).assign(group=g)
        allc.append(c)
    allc = pd.concat(allc)
    for g, c in [('all', allc)] + list(allc.groupby('group', sort=False)):
        el, es = c.dist_m_l - c.user_dist_m, c.dist_m_s - c.user_dist_m
        both = el.notna() & es.notna()
        el, es = el[both].to_numpy(), es[both].to_numpy()
        rm = lambda e: np.sqrt(np.mean(e ** 2))
        bs = rng.integers(0, len(el), (1000, len(el)))
        dlt = np.array([rm(es[i]) - rm(el[i]) for i in bs])
        rows.append({'group': g, 'with Landsat bank': int(c.dist_m_l.notna().sum()),
                     'with S2 bank': int(c.dist_m_s.notna().sum()), 'both': int(both.sum()),
                     'Landsat RMSE (m)': f'{rm(el):.1f}', 'S2 RMSE (m)': f'{rm(es):.1f}',
                     'S2 - Landsat RMSE (m) [95% CI]': ci(rm(es) - rm(el), *np.percentile(dlt, [2.5, 97.5])),
                     'Landsat bias (m)': f'{el.mean():+.1f}', 'S2 bias (m)': f'{es.mean():+.1f}',
                     'Landsat median abs (m)': f'{np.median(np.abs(el)):.1f}',
                     'S2 median abs (m)': f'{np.median(np.abs(es)):.1f}'})
    return pd.DataFrame(rows), allc


# ---------- (b) ----------

def check_b(u, WS):
    t = pd.read_csv(L8 / 'forecast_h3_mean.csv').query('split == "test"').reset_index(drop=True)
    D = fc.centred(WS.to_numpy())
    pos = pd.Series(np.arange(len(u)), index=pd.MultiIndex.from_frame(u[sl.KEY]))
    i = pos.reindex(pd.MultiIndex.from_frame(t[sl.KEY])).to_numpy()
    assert not np.isnan(i).any()
    i = i.astype(int)
    t['y_s2'] = D[i, t.target_year - 2000] - D[i, t.origin - 2000]
    rows_all = len(t)
    t = t[(t.origin >= 2018) & t.y_s2.notna()].reset_index(drop=True)
    cov = []
    for g, d in [('All', t)] + [(g, t[t.group == g]) for g in GROUPS]:
        for truth, col in (('Sentinel-2', 'y_s2'), ('Landsat', 'y')):
            for k in METH:
                est, (lo, hi) = fc.interval_metrics(d.assign(y=d[col]), 'gbt', k)['coverage']
                cov.append({'group': g, 'truth': truth, 'method': k, 'n': len(d), 'blocks': d.block.nunique(),
                            'coverage': est, 'lo': lo, 'hi': hi})
    return pd.DataFrame(cov), t, rows_all


# ---------- (c) ----------

def check_c(u, WL, WS):
    for name, W in (('l', WL), ('s', WS)):
        u[f'win_{name}'], u[f'jump_{name}'] = sl.change(W, WIN)
    g = u.groupby('unit_2km')
    s = pd.DataFrame({f'n_{k}': g[f'win_{k}'].count() for k in 'ls'}
                     | {f'p75_{k}': g[f'win_{k}'].quantile(.75) for k in 'ls'}
                     | {f'jumps_{k}': g[f'jump_{k}'].sum() for k in 'ls'})
    for k in 'ls':
        s[f'lab_{k}'] = (s[f'p75_{k}'] >= 20).astype(float).where(s[f'n_{k}'] >= sl.MIN_PTS)
    d = pd.read_csv(L8 / 'h3_units.csv').query('level == "units 2km"').reset_index(drop=True)
    d = d.join(s, on='unit')
    return d


def c_stats(d):
    both = d.dropna(subset=['lab_l', 'lab_s']).reset_index(drop=True)
    idx = h3.boot_index(both.block.to_numpy())
    rho = lambda i: spearmanr(both.p75_l.iloc[i], both.p75_s.iloc[i])[0]
    agree = lambda i: np.mean(both.lab_l.iloc[i].to_numpy() == both.lab_s.iloc[i].to_numpy())
    kap = lambda i: cohen_kappa_score(both.lab_l.iloc[i], both.lab_s.iloc[i])
    res = {'n_units': len(both), 'blocks': both.block.nunique(),
           'spearman': h3.boot(rho, len(both), idx)[:3], 'agree': h3.boot(agree, len(both), idx)[:3],
           'kappa': h3.boot(kap, len(both), idx)[:3],
           'pos_l': int(both.lab_l.sum()), 'pos_s': int(both.lab_s.sum()),
           'pos_both': int(((both.lab_l == 1) & (both.lab_s == 1)).sum()),
           'n_l': int(d.lab_l.notna().sum()), 'n_s': int(d.lab_s.notna().sum()),
           'p75_diff_med': float(np.median(both.p75_s - both.p75_l))}
    om = []
    for name, col, dd in (('Landsat 2014->2023 (primary label, P2)', 'lab_p75_20', d),
                          ('Landsat 2018->2023, all labelled units', 'lab_l', d),
                          ('Sentinel-2 2018->2023, all labelled units', 'lab_s', d),
                          ('Landsat 2018->2023, units labelled by both', 'lab_l', both),
                          ('Sentinel-2 2018->2023, units labelled by both', 'lab_s', both)):
        x = dd.dropna(subset=[col]).reset_index(drop=True)
        sat, rep = (x[col] == 1).to_numpy(), (x.rep == 1).to_numpy()
        f = lambda i: np.mean(~rep[i][sat[i]]) if sat[i].any() else np.nan
        est, lo, hi, _ = h3.boot(f, len(x), h3.boot_index(x.block.to_numpy()))
        om.append({'label': name, 'units': len(x), 'satellite-eroding': int(sat.sum()),
                   'never reported': int((sat & ~rep).sum()), 'omission (%)': ci(est, lo, hi, d=0, pct=True)})
    return res, pd.DataFrame(om)


# ---------- figure ----------

def figure():
    long, cov, d = (pd.read_csv(CSV[k]) for k in ('diff', 'coverage', 'units'))
    fig, axs = plt.subplots(1, 3, figsize=(COL2, COL2 * .4), gridspec_kw=dict(width_ratios=[1.12, 1.22, 1], wspace=.42))
    ax = axs[0]
    labs = ['Tiền\nmain', 'Hậu\nwide', 'Hậu\nnarrow', 'Islands']
    for i, g in enumerate(GROUPS):
        x = long.loc[(long.group == g), 'diff'].dropna().to_numpy()
        q = np.percentile(x, [10, 25, 50, 75, 90])
        ax.plot([i, i], [q[0], q[4]], color=GCOL[g], lw=1)
        ax.add_patch(plt.Rectangle((i - .22, q[1]), .44, q[3] - q[1], fc=GCOL[g], ec='none', alpha=.85))
        ax.plot([i - .22, i + .22], [q[2]] * 2, color=INK, lw=1.2)
        ax.text(i, 33, f'{100 * np.mean(np.abs(x) <= 30):.0f}%', ha='center', va='center', fontsize=7, color=INK)
    ax.axhline(0, color=INK2, lw=.6)
    ax.set_xticks(range(4), labs)
    ax.set_xlim(-.6, 3.6)
    ax.set_ylabel('Sentinel-2 − Landsat bank (m)\n(+ = Sentinel-2 bank landward)')
    ax.set_title('(a) Same bank, same year', loc='left', pad=3, fontweight='bold')
    ax.text(-.5, 39, 'Share within ±30 m', fontsize=7, color=INK2, va='center')
    ax.set_ylim(-30, 43)
    ax.set_yticks([-30, -20, -10, 0, 10, 20, 30])
    chart_axes(ax)
    ax.grid(axis='x', visible=False)

    ax = axs[1]
    ax.axhspan(87, 93, color=GRID, alpha=.6, lw=0)
    ax.axhline(90, color=INK2, lw=.6)
    cats = ['All'] + GROUPS
    styles = {('Sentinel-2', 'split'): (BLUE, 's', 'white'), ('Landsat', 'split'): (INK2, 's', 'white'),
              ('Sentinel-2', 'mondrian'): (BLUE, '^', None), ('Landsat', 'mondrian'): (INK2, '^', None)}
    off = {('Landsat', 'split'): -.27, ('Sentinel-2', 'split'): -.09, ('Landsat', 'mondrian'): .09,
           ('Sentinel-2', 'mondrian'): .27}
    for (truth, k), (col, mk, mfc) in styles.items():
        for i, c in enumerate(cats):
            r = cov[(cov.group == c) & (cov.truth == truth) & (cov.method == k)].iloc[0]
            ax.errorbar(i + off[truth, k], r.coverage, [[r.coverage - r.lo], [r.hi - r.coverage]], fmt=mk, ms=3.5,
                        color=col, mfc=mfc or col, mec=col, mew=.8, lw=.8,
                        label=f'{"Split" if k == "split" else "Mondrian"}, {truth} truth' if i == 0 else None)
    ax.set_xticks(range(len(cats)), ['All', 'Tiền\nmain', 'Hậu\nwide', 'Hậu\nnarrow', 'Islands'])
    ax.set_ylabel('Coverage of 90% intervals (%)')
    ax.set_title('(b) GBT intervals, h = 3 yr', loc='left', pad=3, fontweight='bold')
    lo = min(80, np.floor(cov.lo.min() / 5) * 5)
    ax.set_ylim(lo, 100)
    ax.legend(loc='upper center', bbox_to_anchor=(.5, -.2), ncol=2, handletextpad=.2, columnspacing=.8,
              labelspacing=.3)
    chart_axes(ax)
    ax.grid(axis='x', visible=False)

    ax = axs[2]
    b = d.dropna(subset=['lab_l', 'lab_s'])
    lim = (-40, 160)
    xl, xs = b.p75_l.clip(*lim), b.p75_s.clip(*lim)
    for gname, col, mk in (('island channels', YELLOW, 'o'), ('Tiền main', BLUE, 'o'), ('Hậu main', ORANGE, 's')):
        m = b.group == gname
        ax.plot(xl[m], xs[m], mk, ms=3, mfc=col, mec='white', mew=.3, alpha=.9,
                label={'Tiền main': 'Tiền main', 'Hậu main': 'Hậu main', 'island channels': 'Islands'}[gname])
    ax.plot(lim, lim, color=INK2, lw=.6)
    ax.axvline(20, color=INK, lw=.6, ls=(0, (4, 2)))
    ax.axhline(20, color=INK, lw=.6, ls=(0, (4, 2)))
    ax.set_xlim(*lim)
    ax.set_ylim(*lim)
    ax.set_xlabel('Landsat unit p75 retreat (m)')
    ax.set_ylabel('Sentinel-2 unit p75 retreat (m)')
    ax.set_title('(c) 2 km units, 2018→2023', loc='left', pad=3, fontweight='bold')
    ax.legend(loc='upper left', handletextpad=.1, borderaxespad=.2, labelspacing=.25, frameon=True, facecolor='white',
              edgecolor='none', framealpha=1)
    chart_axes(ax)
    save(fig, 'fig11_sentinel2')


# ---------- report ----------

def years_table():
    rows = []
    for f in sorted(S2.glob('*/years.csv')):
        y = pd.read_csv(f)
        rows.append({'tile': f.parent.name, **{str(r.year): f'{100 * r.nodata_share:.1f}' + ('' if r.kept else ' x')
                                               for r in y.itertuples()}})
    sc = {f.parent.name: pd.read_csv(f).set_index('year').S2 for f in sorted(pathlib.Path('data/raw/s2').glob('*/scenes.csv'))}
    return pd.DataFrame(rows), pd.DataFrame(sc).T


def main():
    if sys.argv[1:] == ['fig']:
        return figure()
    u = points()
    WL, WS = wide(u, L8), wide(u, S2)
    long = check_a(u, WL, WS)
    long.round(2).to_csv(CSV['diff'], index=False)
    ta, ty = a_table(long, 'group'), a_table(long, 'year')
    tc, allc = click_table()
    cov, tb, nb_all = check_b(u, WS)
    cov.round(3).to_csv(CSV['coverage'], index=False)
    d = check_c(u, WL, WS)
    d[['unit', 'group', 'block', 'rep', 'lab_p75_20', 'win_p75', 'n_l', 'n_s', 'p75_l', 'p75_s', 'lab_l', 'lab_s',
       'jumps_l', 'jumps_s']].round(3).to_csv(CSV['units'], index=False)
    cs, om = c_stats(d)
    yt, sc = years_table()
    figure()

    pooled = cov[(cov.group == 'All') & (cov.truth == 'Sentinel-2')].set_index('method')
    ok = {k: abs(pooled.coverage[k] - 90) <= 3 for k in METH}
    fmt = lambda r: f'{r.coverage:.1f} [{r.lo:.1f}, {r.hi:.1f}]'
    cvt = cov.assign(c=cov.apply(fmt, axis=1)).pivot_table(index=['group', 'n', 'blocks'], columns=['truth', 'method'],
                                                           values='c', aggfunc='first').reindex(['All'] + GROUPS,
                                                                                                 level=0)
    cvt.columns = [f'{m} vs {t} truth' for t, m in cvt.columns]
    yd = tb.y_s2 - tb.y
    L = ['# P3 R1: Sentinel-2 banks 2017-2024', '',
         '`python src/gee_s2.py <tile>` (each tile and island), `python src/s2_banks.py <tile> ...`, '
         '`python src/s2_banks.py stitch`, `python src/p3_sentinel2.py`. Design and criterion: docs/p3_plan.md R1 '
         '(fixed before running).', '',
         '## Design', '',
         '- COPERNICUS/S2_SR_HARMONIZED, Jan 1 - May 1, Cloud Score+ cs_cdf >= 0.6, median; MNDWI = (B3 - B11)/(B3 + B11), '
         'B11 (20 m) bilinear to 10 m (effective resolution ~20 m across the water-land edge). 10 m grid in UTM 48N with '
         'the origin and footprint of each tile\'s Landsat raster.',
         '- Same tiles, islands, transects and bank rule: the geometry (centerline / island ring, transects, open-river '
         'edge, belt limit) is rebuilt from each tile\'s Landsat stack exactly as banklines.py does (checked against the '
         'Landsat output) and sampled on the 10 m grid; banklines.positions runs with px = 10, so the canal-filter disc '
         '(9 px = 90 m) and the island area (9999 px = 1 km2) keep their physical size. All other extraction constants are '
         'along-transect, in metres or 5 m samples, and unchanged; the geometry-only pixel constants (centerline smoothing, '
         'gap closing, core / belt openings) are not applied to Sentinel-2 at all because the Landsat geometry is reused '
         '(this is what keeps the transect ids). Other-river masking and the > 2% nodata rule as for Landsat; spikes as '
         'for Landsat. Stitching and island tables reuse the Landsat keys.',
         '- Landsat outputs unchanged: banklines.py only gained a pixel-size argument (default 30 m); reruns of '
         'sadec_caolanh, tien_03, hau_01 (narrow) and isl_tien_04 reproduce bank_positions.csv and trends.csv '
         'byte for byte (sha256).', '',
         '### Composites', '',
         'Scenes per dry season (S2 SR, tile footprint):', '', sc.to_markdown(), '',
         'Nodata share inside the own-river mask (%; x = dropped by the > 2% rule):', '', yt.to_markdown(index=False), '',
         '## (a) Agreement with Landsat (in-scope transect-sides, 2017-2024, spikes left out)', '',
         'diff = Sentinel-2 - Landsat distance from the same centerline (+ = Sentinel-2 bank further landward). '
         '95% CIs: block bootstrap over 10 km blocks (h3.boot_index, B = 1000).', '',
         ta.to_markdown(index=False), '', 'By year (pooled over groups):', '', ty.to_markdown(index=False), '',
         '### Accuracy against the hand clicks (same clicks, bank of the compared year from each sensor)', '',
         'error = satellite - clicked (negative = satellite bank riverward). CI of the RMSE difference: bootstrap over '
         'clicks (1000, seed 0).', '', tc.to_markdown(index=False), '',
         '## (b) H2 with Sentinel-2 truth (frozen GBT intervals, h = 3, test rows)', '',
         f'Test rows {nb_all}; with origin >= 2018 and a Sentinel-2 target: {len(tb)} '
         f'(origins {sorted(tb.origin.unique().tolist())}, targets {sorted(tb.target_year.unique().tolist())}). '
         f'Truths on these rows: median y_S2 - y_Landsat {yd.median():+.1f} m, median |diff| {yd.abs().median():.1f} m, '
         f'Spearman {spearmanr(tb.y_s2, tb.y)[0]:.2f}; |y| p90 Landsat {tb.y.abs().quantile(.9):.1f} m, '
         f'Sentinel-2 {tb.y_s2.abs().quantile(.9):.1f} m. 95% CIs: forecast.boot (10 km blocks, 1000, seed 0).', '',
         cvt.reset_index().to_markdown(index=False), '',
         f'**Verdict (criterion fixed in p3_plan R1: pooled coverage vs Sentinel-2 truth within 90 ± 3 pp):** split '
         f'{pooled.coverage["split"]:.1f}% ({"holds" if ok["split"] else "fails"}), Mondrian '
         f'{pooled.coverage["mondrian"]:.1f}% ({"holds" if ok["mondrian"] else "fails"}) -> H2 conclusion '
         f'{"unchanged" if all(ok.values()) else "CHANGED"}.', '',
         '## (c) Unit window retreat 2017-19 -> 2022-24 (2 km H3 units; descriptive)', '',
         f'sat_labels rules (>= {sl.MIN_YRS} valid years per 3-yr mean, |change| > {sl.MAX_RATE:.0f} m/yr x 5 yr left out, '
         f'unit p75 over >= {sl.MIN_PTS} points). Units labelled by Landsat {cs["n_l"]}, by Sentinel-2 {cs["n_s"]}, by both '
         f'{cs["n_units"]} ({cs["blocks"]} blocks). Median unit p75 difference S2 - Landsat {cs["p75_diff_med"]:+.1f} m.', '',
         f'- Spearman (unit p75): {ci(*cs["spearman"], d=2)}',
         f'- Label >= 20 m: Landsat {cs["pos_l"]} positive, Sentinel-2 {cs["pos_s"]}, both {cs["pos_both"]}; '
         f'agreement {ci(*cs["agree"], d=0, pct=True)}%; Cohen kappa {ci(*cs["kappa"], d=2)}', '',
         'Omission (share of satellite-eroding units never reported), 95% block-bootstrap CI:', '',
         om.to_markdown(index=False), '',
         '## Caveats', '',
         '- No usable Sentinel-2 SR composite for 2017 on any tile (0-2 SR scenes per dry season; the collection is '
         'sparse over the delta before late 2018), and 2018 composites come from 1-6 scenes; 2018 is dropped by the > 2% '
         'nodata rule on hau_03-hau_05 (the wide Hậu below Châu Đốc and Vàm Nao). Consequences: no 2017 pairs in (a); '
         'in (b) origin 2018 is missing where 2018 is dropped (centred mean needs 2 of 2017-2019); in (c) the 2017-19 '
         'mean rests on 2018-2019 only, and units on the three Hậu tiles get no Sentinel-2 label (343 -> 282 units).',
         '- Effective resolution across the edge is ~20 m (B11 bilinear), not 10 m.',
         '- Sentinel-2 reuses the Landsat geometry (centerline / ring, transects, open-river edge, belt limit) and the same '
         'bank rule, so it is an independent measurement of the bank position on each transect, not of the geometry or '
         'of rule-level errors (multi-edge banks, strips in front of the mainland). The hand clicks are the independent check.',
         '- (b): the intervals were calibrated on Landsat targets; Sentinel-2 truth has its own noise (truths agree to a '
         'median 2.7 m, Spearman 0.69, because most 3-yr changes are small). The subset (origins 2018-2021) is the later part '
         'of the test period.',
         '- (c): the 5-yr window has about half the positives of the primary 9-yr window (23 vs 43), so the omission '
         'shares have wide CIs; it is a sensor comparison, not a replacement label.',
         '- Largest unit disagreement: tien_R_+050 (Landsat p75 5 m, Sentinel-2 94 m). Its downstream transects '
         '(T942-T950) flip between two edges ~180 m apart in both sensors (a strip or pond row in front of the bank); the '
         'sensors flip in different years, so the unit p75 differs. A multi-edge bank, not a Sentinel-2 processing error.', '']
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'sentinel2.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
