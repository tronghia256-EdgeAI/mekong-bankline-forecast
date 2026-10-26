"""EXPLORATORY (docs/exploratory_plan.md section B): what public reporting captures, beside the confirmatory H3.

Usage: python src/explore_reporting.py
Reads data/processed/h3_units.csv (the analysed 2 km units of H3: block, group, built-up tercile, rep, rep_event,
win_p75, lab_p75_20), data/hotspots/inventory.csv (use_in_analysis rows, loaded with h3.inventory), sat_events_2km.csv,
sat_labels_2km.csv and units.csv. Nothing here changes the H3 verdict; no pass/fail rule is applied.
Writes:
  data/processed/explore_reporting_units.csv    per unit: river km, communes, reported-by-source flags, measured class
  data/processed/explore_reporting_shares.csv   omission / commission / capture shares by source and stratum, block CI
  data/processed/explore_reporting_timing.csv   measured unit-year event rates around reported / warned years
  data/processed/explore_reporting_omitted.csv  satellite-eroding units without any reported row (candidate sites)
  results/p2/explore_reporting.md, figures/fig10_reporting.png + .svg
Settings (fixed before running):
  noise floors of a 3-yr mean difference: 9.3 m (2 valid years, sigma 4.7) primary, 5.8 m (3 years, sigma 3.6);
  accretion = win_p75 < -9.3 m. Measured classes: accretion / no measurable change (|win_p75| < 9.3) / retreat below
  the label (9.3-20 m) / eroding (lab_p75_20).
  timing: events p90 >= 15 m/yr (10, 20 sensitivity), years 2012 and 2024 dropped; reported pairs = unique (unit,
  event_year); rate per unit-year in Y-3..Y-1, Y, Y+1..Y+3 against the calendar-year-matched rate of never-reported
  units (expected = mean over the pair-years of the control rate in the same calendar year).
  uncertainty: h3.boot_index (whole 10 km blocks, B = 1000, h3.SEED; same draws as the H3 2 km analysis).
"""
import pathlib
import sys
import time

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import h3  # noqa: E402
from figures import BLUE, COL2, GRID, INK, INK2, ORANGE, chart_axes, plt, save  # noqa: E402

FLOOR, FLOOR3 = 9.3, 5.8
THRESHOLDS = (15, 10, 20)               # primary first
DROP_YEARS = (2012, 2024)
YEARS = np.arange(2001, 2025)
YS = np.arange(2015, 2025)              # reported years
KS = np.arange(-3, 4)
WINDOWS = {'before (Y-3..Y-1)': [-3, -2, -1], 'year Y': [0], 'after (Y+1..Y+3)': [1, 2, 3]}
SOURCES = {'any report': None, 'event rows': 'event', 'warned-reach list': 'official_list_via_news',
           'news report': 'news', 'emergency decision': 'decision_via_news', 'ODM 2018': 'odm_webgis_2018'}
CLASSES = ['accretion', 'no measurable change', 'retreat below label', 'eroding (label)']
CLASS_COL = ['#184f95', '#c8c7c2', '#ec8a89', '#b52f2e']   # figures.RATE stops: blue accretion - grey - red erosion
GROUPS = ['Tiền main', 'Hậu main', 'island channels']


# ---------- inputs ----------

def units_table(inv):
    """H3 2 km units + river km (main: unit mid; island: chainage of nearest main point), communes, source flags."""
    d = pd.read_csv('data/processed/h3_units.csv')
    d = d[d.level == 'units 2km'].reset_index(drop=True)
    s = pd.read_csv('data/processed/sat_labels_2km.csv').set_index('unit')
    pts = pd.read_csv('data/processed/units.csv', encoding='utf-8')
    pts = pts[pts.in_scope]
    d['km'] = ((s.km_from + s.km_to) / 2).reindex(d.unit).to_numpy()
    for r in ('tien', 'hau'):
        m = pts[pts.channel == r]
        tree = cKDTree(np.c_[m.lon * np.cos(np.radians(10.5)), m.lat])
        isl = (d.river == r) & (d.is_island == 1)
        ll = s.loc[d.unit[isl], ['lon', 'lat']].to_numpy()
        d.loc[isl, 'km'] = m.chainage_m.to_numpy()[tree.query(np.c_[ll[:, 0] * np.cos(np.radians(10.5)), ll[:, 1]])[1]] / 1e3
    com = pts.assign(c=pts.district + ' / ' + pts.commune).groupby('unit_2km').c.agg(
        lambda x: '; '.join(x.value_counts().index))
    d['communes'] = d.unit.map(com)
    for name, st in SOURCES.items():
        rows = inv if st is None else inv[inv.event] if st == 'event' else inv[inv.source_type == st]
        d[f'r_{name}'] = d.unit.isin({x for v in rows.units_2km for x in v.split('; ')}).astype(int)
    assert (d['r_any report'] == d.rep).all() and (d['r_event rows'] == d.rep_event).all(), 'reported sets differ from H3'
    w = d.win_p75
    d['cls'] = np.select([d.lab_p75_20 == 1, w >= FLOOR, w < -FLOOR], [3, 2, 0], 1)
    d['class'] = [CLASSES[c] for c in d.cls]
    return d


def event_matrix(d, thr):
    """Unit x year event indicator (NaN = no data or dropped year)."""
    e = pd.read_csv('data/processed/sat_events_2km.csv')
    m = e.pivot(index='unit', columns='year', values=f'ev{thr}').reindex(index=d.unit, columns=YEARS).astype(float)
    m[list(DROP_YEARS)] = np.nan
    return m.to_numpy()


def pair_matrix(d, rows):
    """Unit x reported-year boolean: unit covered by a row dated Y (unique pairs)."""
    a = np.zeros((len(d), len(YS)), bool)
    pos = {u: i for i, u in enumerate(d.unit)}
    for _, r in rows[rows.event_year.between(YS[0], YS[-1])].iterrows():
        for x in r.units_2km.split('; '):
            if x in pos:
                a[pos[x], int(r.event_year) - YS[0]] = True
    return a


def stack(ev, a):
    """(events, valid) arrays unit x Y x k for the pair matrix a."""
    col = (YS[:, None] + KS[None, :]) - YEARS[0]
    ok = (col >= 0) & (col < len(YEARS))
    E = np.where(ok, ev[:, np.clip(col, 0, len(YEARS) - 1)], np.nan)
    V = np.isfinite(E) & a[:, :, None]
    return np.where(V, E, 0.), V.astype(float)


def shared_points(p, unit, tol=30.):
    """Units of other channels with bank points within tol m of this unit's points (ring banks of adjacent islands can
    be the same bank measured twice), as 'unit (k of n points)'."""
    xy = lambda q: np.c_[q.lon * 111320 * np.cos(np.radians(10.5)), q.lat * 110570]
    a = p[p.unit_2km == unit]
    o = p[p.channel != a.channel.iloc[0]]
    dist, j = cKDTree(xy(o)).query(xy(a))
    hit = o.unit_2km.to_numpy()[j[dist < tol]]
    return '; '.join(f'{k} ({v} of {len(a)} points)' for k, v in pd.Series(hit).value_counts().items())


# ---------- statistics ----------

def shares(d, idx):
    """Omission, commission and capture shares with block-bootstrap CIs, by source and stratum."""
    n, w, rows = len(d), d.win_p75.to_numpy(), []
    sat = d.lab_p75_20.to_numpy() == 1
    strata = {'all': np.ones(n, bool)} | {g: (d.group == g).to_numpy() for g in GROUPS} | {
        f'built T{k + 1}': (d.t_built_1km == k).to_numpy() for k in range(3)}

    def add(stat, source, stratum, den, num):
        f = lambda i: num[i][den[i]].mean() if den[i].any() else np.nan
        est, lo, hi, nb = h3.boot(f, n, idx)
        rows.append(dict(stat=stat, source=source, stratum=stratum, num=int((num & den).sum()), den=int(den.sum()),
                         est=est, lo=lo, hi=hi, n_boot=nb))

    for sname in SOURCES:
        r = d[f'r_{sname}'].to_numpy() == 1
        for g, m in strata.items():
            add('missed by source (share of satellite-eroding)', sname, g, sat & m, ~r)
            add('below 9.3 m (share of reported)', sname, g, r & m, w < FLOOR)
            add('below 5.8 m (share of reported)', sname, g, r & m, w < FLOOR3)
            add('accretion < -9.3 m (share of reported)', sname, g, r & m, w < -FLOOR)
            add('satellite-eroding (share of reported)', sname, g, r & m, sat)
    nr = d.rep.to_numpy() == 0
    for g, m in strata.items():
        add('satellite-eroding (share of never-reported)', 'never reported', g, nr & m, sat)
        add('below 9.3 m (share of never-reported)', 'never reported', g, nr & m, w < FLOOR)
    return pd.DataFrame(rows)


def rates(R, C, ks, wts, grp):
    """Observed rate in pair-years; control rate matched on calendar year, and on calendar year within channel group."""
    k = np.isin(KS, ks)
    rn_all = np.einsum('u,uyk->yk', wts, R[1])[:, k]
    obs = np.einsum('u,uyk->yk', wts, R[0])[:, k].sum() / rn_all.sum() if rn_all.sum() else np.nan
    out = [obs]
    for masks in ([np.ones_like(grp, bool)], [grp == g for g in range(len(GROUPS))]):
        num = den = 0.
        for m in masks:
            wm = wts * m
            rn = np.einsum('u,uyk->yk', wm, R[1])[:, k]
            with np.errstate(invalid='ignore', divide='ignore'):
                cr = (np.einsum('u,uyk->yk', wm, C[0]) / np.einsum('u,uyk->yk', wm, C[1]))[:, k]
            ok = np.isfinite(cr) & (rn > 0)
            num, den = num + (rn[ok] * cr[ok]).sum(), den + rn[ok].sum()
        out.append(num / den if den else np.nan)
    o, e, eg = out
    with np.errstate(invalid='ignore', divide='ignore'):
        return np.array([o, e, o - e, o / e, eg, o - eg, o / eg])


STATS = ['obs', 'exp', 'diff', 'ratio', 'exp_g', 'diff_g', 'ratio_g']


def boot_vec(fn, n, idx):
    """h3.boot for a vector-valued statistic (one evaluation per draw): estimate, 2.5 / 97.5 percentiles."""
    v = np.array([fn(i) for i in idx])
    return fn(np.arange(n)), *np.nanpercentile(np.where(np.isfinite(v), v, np.nan), [2.5, 97.5], axis=0)


def timing(d, inv, idx):
    """Event rates around reported years (vs never reported) and after warned-list years (vs not warned)."""
    n, rows, per_k = len(d), [], []
    never = np.repeat((d.rep.to_numpy() == 0)[:, None], len(YS), 1)
    sets = {'all dated rows': inv, 'event rows': inv[inv.event],
            'warned-reach lists': inv[inv.source_type == 'official_list_via_news']}
    grp = d.group.map({g: i for i, g in enumerate(GROUPS)}).to_numpy()
    for thr in THRESHOLDS:
        ev = event_matrix(d, thr)
        runs = [(f'reported: {k}', pair_matrix(d, v), never) for k, v in sets.items()]
        warned = pair_matrix(d, sets['warned-reach lists'])
        runs.append(('warned vs not warned in Y', warned, ~warned))
        for name, a, c in runs:
            R, C = stack(ev, a), stack(ev, c & a.any(0)[None, :])
            for wname, ks in WINDOWS.items():
                est, lo, hi = boot_vec(lambda i: rates(R, C, ks, np.bincount(i, minlength=n), grp), n, idx)
                rows.append(dict(analysis=name, threshold=thr, window=wname, pairs=int(a.sum()),
                                 unit_years=int(R[1][:, :, np.isin(KS, ks)].sum()),
                                 events=int(R[0][:, :, np.isin(KS, ks)].sum()),
                                 **{f'{s}_{q}': v[j] for j, s in enumerate(STATS)
                                    for q, v in zip(('est', 'lo', 'hi'), (est, lo, hi))}))
            if thr == THRESHOLDS[0] and name == 'reported: all dated rows':
                for k in KS:
                    est, lo, hi = boot_vec(lambda i: rates(R, C, [k], np.bincount(i, minlength=n), grp), n, idx)
                    per_k.append(dict(k=k, **{f'{s}_{q}': v[j] for j, s in enumerate(STATS)
                                              for q, v in zip(('est', 'lo', 'hi'), (est, lo, hi))}))
    return pd.DataFrame(rows), pd.DataFrame(per_k)


# ---------- report ----------

def ci(est, lo, hi, pct=True):
    f = (lambda x: f'{100 * x:.0f}%') if pct else (lambda x: f'{x:.2f}')
    return '-' if not np.isfinite(est) else f'{f(est)} [{f(lo)}, {f(hi)}]'


def sh(S, stat, source='any report', stratum='all'):
    r = S[(S.stat == stat) & (S.source == source) & (S.stratum == stratum)].iloc[0]
    return r, f'{r.num}/{r.den} = {ci(r.est, r.lo, r.hi)}'


def report(d, S, T, om, runtime):
    L = ['# What public reporting captures (EXPLORATORY)', '',
         f'Generated by `python src/explore_reporting.py` ({runtime:.0f} s). Exploratory analysis B of '
         '`docs/exploratory_plan.md` (planned 26/10 after the P2 results, written before running). It does not change '
         'the confirmatory H3 verdict (not supported, `results/p2/h3.md`); no pass/fail rule is applied. Units: the '
         f'{len(d)} analysed 2 km units of H3; reported = unit listed in `units_2km` of >= 1 use_in_analysis inventory row '
         '(same sets as H3). Intervals: 95% block bootstrap (whole 10 km blocks, B = 1000, same draws as H3). Shares of '
         'units equal shares of reach length (every unit is 2 km of bank).', '']
    r_om, t_om = sh(S, 'missed by source (share of satellite-eroding)')
    r_ome, t_ome = sh(S, 'missed by source (share of satellite-eroding)', 'event rows')
    r_c, t_c = sh(S, 'below 9.3 m (share of reported)')
    L += ['## 1. Omission: satellite-eroding units without a report', '',
          f'Satellite-eroding units (lab_p75_20, p75 retreat 2014→2023 >= 20 m): {r_om.den}. Without any reported row: '
          f'{t_om}. Without an event row (hamlet / landmark report or emergency decision): {t_ome}.', '',
          '| stratum | eroding units | no report (any) | no event row | no warned-list row |', '|---|---|---|---|---|']
    for g in ['all'] + GROUPS + [f'built T{k}' for k in (1, 2, 3)]:
        a = [sh(S, 'missed by source (share of satellite-eroding)', s, g) for s in
             ('any report', 'event rows', 'warned-reach list')]
        L.append(f'| {g} | {a[0][0].den} | ' + ' | '.join(x[1].split(' = ')[0] + ' = ' + ci(x[0].est, x[0].lo, x[0].hi)
                                                         for x in a) + ' |')
    L += ['', f'Candidate unreported erosion sites ({len(om)} units; `data/processed/explore_reporting_omitted.csv`, '
          'sorted by window retreat). km = distance from the border along the main channel (island units: km of the '
          'nearest main-channel bank point). Side I = island bank, O = opposite bank of the side channel.', '',
          '| unit | channel | km | commune(s) (district / commune) | p75 retreat (m) | points | clean variant | '
          'bank points within 30 m of another channel unit |', '|---|---|---|---|---|---|---|---|']
    for _, r in om.iterrows():
        L.append(f'| {r.unit} | {r.channel} | {r.km:.0f} | {r.communes} | {r.win_p75:.0f} | {r.n_win} | '
                 f'{"eroding" if r.lab_p75_20_clean == 1 else "not eroding" if r.lab_p75_20_clean == 0 else "-"} | '
                 f'{r.shared_with or "-"} |')
    L += ['', '## 2. Commission: reported units without measurable retreat', '',
          f'Reported units whose window retreat is below the noise floor of a 3-yr mean difference (win_p75 < '
          f'{FLOOR} m): {t_c}. Classes: accretion < -{FLOOR} m; no measurable change |win_p75| < {FLOOR} m; retreat '
          f'below the label {FLOOR}-20 m; eroding = label.', '',
          '| source | units | < 9.3 m | < 5.8 m | accretion < -9.3 m | eroding (label) |', '|---|---|---|---|---|---|']
    for s in list(SOURCES) + ['never reported']:
        st = ['below 9.3 m', 'below 5.8 m', 'accretion < -9.3 m', 'satellite-eroding'] if s != 'never reported' else \
            ['below 9.3 m', None, None, 'satellite-eroding']
        cells = []
        for x in st:
            if x is None:
                cells.append('-')
                continue
            stat = f'{x} (share of {"never-reported" if s == "never reported" else "reported"})'
            r, t = sh(S, stat, s)
            cells.append(t)
        L.append(f'| {s} | {r.den} | ' + ' | '.join(cells) + ' |')
    L += ['', 'Below the 9.3 m floor, by stratum (share of reported units):', '',
          '| source | ' + ' | '.join(GROUPS + [f'built T{k}' for k in (1, 2, 3)]) + ' |', '|---' * 7 + '|']
    for s in SOURCES:
        L.append(f'| {s} | ' + ' | '.join(sh(S, 'below 9.3 m (share of reported)', s, g)[1]
                                          for g in GROUPS + [f'built T{k}' for k in (1, 2, 3)]) + ' |')
    L += ['', '## 3. Captured and missed, by source and group (descriptive counts, not a classifier score)', '',
          'reported = units the source covers; of them eroding (label) and below the 9.3 m floor; captured / missed = '
          'satellite-eroding units of the group that the source covers / does not cover.', '',
          '| source | group | reported | of which eroding | of which < 9.3 m | eroding in group | captured | missed |',
          '|---|---|---|---|---|---|---|---|']
    for s in SOURCES:
        for g in ['all'] + GROUPS:
            m = d if g == 'all' else d[d.group == g]
            r = m[f'r_{s}'] == 1
            e = m.lab_p75_20 == 1
            L.append(f'| {s} | {g} | {r.sum()} | {(r & e).sum()} | {(r & (m.win_p75 < FLOOR)).sum()} | {e.sum()} | '
                     f'{(r & e).sum()} | {(~r & e).sum()} |')
    L += ['', '## 4. Timing of measured events around reported years', '',
          'Measured events: unit-year p90 of annual retreat on a 3-yr centred rolling mean >= 15 m/yr (10, 20 '
          'sensitivity; `sat_events_2km.csv`), years 2012 and 2024 dropped. Pairs = unique (unit, reported year Y), '
          'Y 2015-2024. Observed = events per unit-year in the pair-years; expected = rate of never-reported units in the '
          'same calendar years (warned analysis: units not on a warned list in Y); expected, group = the same, matched '
          'also on channel group (Tiền main / Hậu main / island channels), because reports concentrate on the Hậu main '
          'channel where retreat is small and never-reported units are mostly on the Tiền. Note the timing blur: a dry-season '
          'composite of year Y precedes the flood season of Y, and the rolling mean spreads a step over three labels, '
          'so a collapse in the flood season of Y shows up as events labelled Y to Y+2.', '',
          '| analysis | threshold | window | pairs | unit-years | events | observed rate | expected | ratio | '
          'expected, group | ratio, group |', '|---|---|---|---|---|---|---|---|---|---|---|']
    for _, r in T.iterrows():
        L.append(f'| {r.analysis} | {r.threshold} | {r.window} | {r.pairs} | {r.unit_years} | {r.events} | '
                 f'{ci(r.obs_est, r.obs_lo, r.obs_hi, False)} | {ci(r.exp_est, r.exp_lo, r.exp_hi, False)} | '
                 f'{ci(r.ratio_est, r.ratio_lo, r.ratio_hi, False)} | {ci(r.exp_g_est, r.exp_g_lo, r.exp_g_hi, False)} | '
                 f'{ci(r.ratio_g_est, r.ratio_g_lo, r.ratio_g_hi, False)} |')
    L += ['', 'Differences (observed - expected) are in `data/processed/explore_reporting_timing.csv`.']
    return L


def summary(d, S, T, om):
    r_om = sh(S, 'missed by source (share of satellite-eroding)')[0]
    r_ome = sh(S, 'missed by source (share of satellite-eroding)', 'event rows')[0]
    r_c = sh(S, 'below 9.3 m (share of reported)')[0]
    r_w = sh(S, 'below 9.3 m (share of reported)', 'warned-reach list')[0]
    r_n = sh(S, 'below 9.3 m (share of reported)', 'news report')[0]
    q = T[(T.threshold == 15) & (T.analysis == 'reported: all dated rows')].set_index('window')
    wv = T[(T.threshold == 15) & (T.analysis == 'warned vs not warned in Y')].set_index('window')
    a, b = q.loc['after (Y+1..Y+3)'], wv.loc['after (Y+1..Y+3)']
    pb = q.loc['before (Y-3..Y-1)']
    rr = lambda r, g='': f'{r[f"ratio{g}_est"]:.1f}x [{r[f"ratio{g}_lo"]:.1f}, {r[f"ratio{g}_hi"]:.1f}]'
    where = om.group.value_counts()
    return ['## 5. Plain-language summary (exploratory)', '',
            f'- {ci(r_om.est, r_om.lo, r_om.hi)} of the 2 km bank units that measurably eroded in 2014→2023 '
            f'({r_om.num} of {r_om.den}) never appear in the public reports collected here; '
            f'{ci(r_ome.est, r_ome.lo, r_ome.hi)} never appear as a dated event (hamlet-level report or emergency '
            + (f'decision). All {len(om)} unreported eroding units are on the Tiền ('
               + ', '.join(f'{v} {k}' for k, v in where.items()) + '; list in section 1).'
               if (om.river == 'tien').all() else 'decision) (list in section 1).'),
            f'- {ci(r_c.est, r_c.lo, r_c.hi)} of reported bank length ({r_c.num} of {r_c.den} units) shows no '
            f'retreat above the {FLOOR} m noise floor over 2014→2023 (warned-reach lists {ci(r_w.est, r_w.lo, r_w.hi)}, '
            f'news reports {ci(r_n.est, r_n.lo, r_n.hi)}).',
            f'- Reports do not mark where measured retreat events (p90 >= 15 m/yr) happen next: reported units had '
            f'{rr(a)} the calendar-matched event rate of never-reported units in the three years after the report '
            f'({rr(a, "_g")} when also matched on channel group) and {rr(pb)} ({rr(pb, "_g")}) in the three years before; '
            f'units on a warned list had {rr(b)} ({rr(b, "_g")}) the event rate of not-warned units in the following '
            '1-3 years.',
            '', 'Caveats: reports locate erosion at commune level (a warned list or a commune-level row labels every '
            'bank of the commune), so "no measurable retreat" over a whole reported unit can hide a short failure; '
            '30 m Landsat banks miss collapses smaller than a pixel and scars repaired within a year; embanked banks '
            'show no retreat because they were protected (a report followed by an embankment reads as commission); '
            'reports cover 2015-2024 only and the satellite window is 2014→2023; the inventory is a search of public '
            'news and lists, not a complete official register, so omission here is omission from the public record '
            'collected, not from government knowledge. Satellite labels themselves contain a few edge-switch '
            'artefacts (see the clean-variant column). Ring banks of adjacent islands are partly measured twice (last '
            'column of the list: isl_tien_02_I_+008/+009 and isl_tien_03_O_+006/+007 are largely the same bank at Long '
            'Khánh A), so the 13 omitted units are about 11 distinct 2 km banks; the same duplication affects other '
            'island units upstream of this analysis (reach_units.py drops ring banks near main banks, not near other '
            'rings).']


# ---------- figure ----------

def figure(d, S, K):
    fig = plt.figure(figsize=(COL2, COL2 * .78))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.05], width_ratios=[1.25, 1], hspace=.55, wspace=.5,
                          left=.17, right=.99, top=.95, bottom=.07)
    ax = fig.add_subplot(gs[0, 0])
    bars = [('Warned-reach lists', 'r_warned-reach list'), ('News reports', 'r_news report'),
            ('Emergency decisions', 'r_emergency decision'), ('ODM 2018', 'r_ODM 2018'), ('Any report', 'r_any report'),
            ('Never reported', None)]
    for y, (lab, c) in enumerate(bars):
        m = d[d.rep == 0] if c is None else d[d[c] == 1]
        f = np.bincount(m.cls, minlength=4) / len(m)
        left = 0
        for k in range(4):
            ax.barh(y, f[k], left=left, color=CLASS_COL[k], height=.7, ec='white', lw=.4,
                    label=CLASSES[k] if y == 0 else None)
            if f[k] >= .07:
                ax.text(left + f[k] / 2, y, f'{100 * f[k]:.0f}', ha='center', va='center', fontsize=7,
                        color='white' if k in (0, 3) else INK)
            left += f[k]
        ax.text(1.01, y, f'n={len(m)}', va='center', fontsize=7, color=INK2)
    ax.set_yticks(range(len(bars)), [b[0] for b in bars])
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.set_xticks([0, .25, .5, .75, 1], ['0', '25', '50', '75', '100%'])
    ax.set_xlabel('Share of units, retreat 2013–15 to 2022–24')
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(axis='y', length=0)
    ax.legend(['accretion', 'no measurable change', 'retreat < label', 'eroding (label)'], ncol=4, loc='lower left',
              bbox_to_anchor=(-.3, 1.0), handlelength=1, columnspacing=.8, handletextpad=.3, fontsize=7)
    ax.set_title('(a) Measured change in reported units', loc='left', pad=17, fontweight='bold', x=-.3)

    ax = fig.add_subplot(gs[0, 1])
    for dx, (s, col, mk, lab) in zip((-.18, 0, .18), (('obs', BLUE, 'o', 'reported units'),
                                                       ('exp', INK2, 's', 'never reported, same years'),
                                                       ('exp_g', ORANGE, '^', '... and same channel group'))):
        ax.errorbar(K.k + dx, K[f'{s}_est'], yerr=[K[f'{s}_est'] - K[f'{s}_lo'], K[f'{s}_hi'] - K[f'{s}_est']],
                    fmt=mk, color=col, ms=3, lw=.9, capsize=1.5, label=lab)
    ax.axvspan(-.5, .5, color=GRID, alpha=.5, lw=0)
    ax.set_xticks(KS, [f'{k:+d}' if k else 'Y' for k in KS])
    ax.set_xlabel('Year relative to reported year Y')
    ax.set_ylabel('Events per unit-year\n(p90 ≥ 15 m yr$^{-1}$)')
    ax.set_ylim(0, .33)
    chart_axes(ax)
    ax.legend(loc='upper left', fontsize=7, handletextpad=.2, borderaxespad=.1, labelspacing=.25)
    ax.set_title('(b) Events around reports', loc='left', pad=3, fontweight='bold')

    sub = gs[1, :].subgridspec(2, 1, hspace=.75)
    tracks = [('Any report', lambda m: m.rep == 1, '#9a9995'), ('Event row', lambda m: m.rep_event == 1, '#9a9995'),
              ('Satellite eroding', lambda m: m.lab_p75_20 == 1, None)]
    for j, (river, name) in enumerate((('tien', 'Tiền'), ('hau', 'Hậu'))):
        ax = fig.add_subplot(sub[j])
        m = d[d.river == river]
        for y, (lab, f, col) in enumerate(tracks):
            x = m[f(m)].sort_values('rep', ascending=False)   # unreported drawn last: never hidden
            cols = col if col else np.where(x.rep == 1, BLUE, ORANGE)
            ax.bar(x.km, .7, width=2, bottom=-y - .35, color=cols, ec=cols, lw=.4)
        ax.set_yticks([0, -1, -2], [t[0] for t in tracks])
        ax.tick_params(axis='y', length=0)
        ax.set_ylim(-2.6, .6)
        ax.set_xlim(-1, max(d.km.max(), 150) + 1)
        ax.spines[['top', 'right', 'left']].set_visible(False)
        ax.grid(axis='x', color=GRID, lw=.5)
        ax.set_axisbelow(True)
        ax.set_title(f'({"cd"[j]}) {name}: units along the river (L, R and island banks overlaid)', loc='left', pad=3,
                     fontweight='bold', x=-.17)
        if j == 1:
            ax.set_xlabel('Distance from the Cambodian border (km)')
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(color=BLUE, label='eroding, reported'), Patch(color=ORANGE, label='eroding, never reported'),
                        Patch(color='#9a9995', label='reported unit')], ncol=3, loc='lower right',
               bbox_to_anchor=(.99, .455), fontsize=7, handlelength=1)
    save(fig, 'fig10_reporting')


# ---------- main ----------

def main():
    t0 = time.time()
    inv = h3.inventory()
    d = units_table(inv)
    idx = h3.boot_index(d.block.to_numpy())
    S = shares(d, idx)
    T, K = timing(d, inv, idx)
    om = d[(d.lab_p75_20 == 1) & (d.rep == 0)].sort_values('win_p75', ascending=False)
    pts = pd.read_csv('data/processed/units.csv', encoding='utf-8')
    om['shared_with'] = om.unit.map(lambda x: shared_points(pts[pts.in_scope], x))
    keep = ['unit', 'river', 'channel', 'side', 'group', 'block', 'km', 'communes', 'n_win', 'win_p75', 'lab_p75_20',
            'lab_p75_20_clean', 'class', 't_built_1km'] + [f'r_{s}' for s in SOURCES]
    d[keep].round(3).to_csv('data/processed/explore_reporting_units.csv', index=False, encoding='utf-8')
    om[keep[:12] + ['shared_with']].round(2).to_csv('data/processed/explore_reporting_omitted.csv', index=False, encoding='utf-8')
    S.round(4).to_csv('data/processed/explore_reporting_shares.csv', index=False, encoding='utf-8')
    T.round(4).to_csv('data/processed/explore_reporting_timing.csv', index=False, encoding='utf-8')
    L = report(d, S, T, om, time.time() - t0) + [''] + summary(d, S, T, om)
    pathlib.Path('results/p2/explore_reporting.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    figure(d, S, K)
    print(f'done {time.time() - t0:.0f} s')


if __name__ == '__main__':
    main()
