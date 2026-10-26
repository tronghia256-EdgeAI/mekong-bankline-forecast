"""P1: satellite erosion labels per reach unit (H3, label source (b): retreat measured from Landsat).

Usage: python src/sat_labels.py
Reads data/processed/units.csv (in-scope bank points, 2 km / 5 km units), annual banks
data/processed/{tien,hau,islands}/bank_positions.csv and trends data/processed/{tien,hau,islands}/trends.csv.
Island rows are joined on (channel, ring_transect) = units.csv (channel isl_*, transect). dist_m is measured outward
from the centerline / island ring, so a larger dist_m is a bank further landward: retreat = + (checked: Binh Hang
Trung, Tien left bank, lrr +18.6 m/yr). Spikes and non-detections are left out.
Writes:
  data/processed/sat_labels_2km.csv, sat_labels_5km.csv  one row per unit: long-term lrr summaries, window retreat
      2014->2023 (mean 2022-24 minus mean 2013-15), pre-window retreat 2001->2013 (mean 2012-14 minus mean 2000-02),
      candidate binary labels (empty when the unit has < MIN_PTS points with a window retreat)
  data/processed/sat_events_2km.csv  one row per unit and year: p90 over points of the annual retreat on a 3-yr
      centred rolling mean, event flags at EVENT_M
  results/p1/sat_labels.md, figures/fig05_sat_labels.png + .svg
Does not read the reported inventory (data/hotspots): labels are defined before the H3 comparison.
"""
import pathlib
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from figures import AQUA, BLUE, COL2, INK, INK2, ORANGE, chart_axes, plt, save  # noqa: E402  (house style)

YEARS = range(2000, 2025)
WIN = ((2013, 2015), (2022, 2024))       # inventory window 2015-2024: 3-yr means centred on 2014 and 2023
PRE = ((2000, 2002), (2012, 2014))       # pre-window, centred on 2001 and 2013
MIN_YRS = 2                              # valid years needed in each 3-yr mean
MIN_PTS = 5                              # points with a window retreat needed for a unit label (500 m of bank)
EVENT_M = (10, 15, 20)                   # unit-year event thresholds, p90 annual retreat (m/yr)
MAX_RATE = 30.0                          # m/yr; a faster window/pre-window change is an edge switch (bar attached or
                                         # detached, island ring jump), not retreat: point left out (hotspot max ~22)
WIN_JUMP = 60.0                          # m; a year-to-year change this large inside 2013-2024 (~3x the fastest
                                         # hotspot rate) marks an edge switch or flip-flop (diagnostic label _clean)
MAX_ANNUAL = 100.0                       # m/yr on the rolling mean (a >= 300 m jump); left out likewise
SIGMA = 3.6                              # measured noise per composite (m, results/p0/sadec_caolanh_sensor_check.md)
LABELS = {   # candidate window labels on 2 km units; name -> (description, rule)
    'p75_20': ('p75 of window retreat >= 20 m', lambda u: u.win_p75 >= 20),
    'p75_30': ('p75 of window retreat >= 30 m', lambda u: u.win_p75 >= 30),
    'sh20_25': ('share of points > 20 m >= 25%', lambda u: u.win_sh20 >= .25),
    'p90_30': ('p90 of window retreat >= 30 m', lambda u: u.win_p90 >= 30),
    'med_20': ('median of window retreat >= 20 m', lambda u: u.win_med >= 20),
}
PRIMARY, VARIANTS = 'p75_20', ('p75_30', 'p90_30')
KEY = ['channel', 'transect', 'side']


def points():
    """In-scope bank points (units.csv) with their trend (lrr, kind)."""
    u = pd.read_csv('data/processed/units.csv').query('in_scope').reset_index(drop=True)
    u['type'] = np.where(u.channel.str.startswith('isl_'), 'island', 'main')
    tr = pd.concat([pd.read_csv(f'data/processed/{r}/trends.csv').assign(channel=r) for r in ('tien', 'hau')]
                   + [pd.read_csv('data/processed/islands/trends.csv').drop(columns='transect')
                      .rename(columns={'ring_transect': 'transect'})])
    return u.merge(tr[KEY + ['lrr', 'kind']], on=KEY, how='left', validate='one_to_one')


def positions(u):
    """Wide table of annual bank distances (rows = in-scope points, columns = 2000-2024; NaN = no valid bank)."""
    bp = pd.concat([pd.read_csv(f'data/processed/{r}/bank_positions.csv').assign(channel=r) for r in ('tien', 'hau')]
                   + [pd.read_csv('data/processed/islands/bank_positions.csv').drop(columns='transect')
                      .rename(columns={'ring_transect': 'transect'})])
    bp = bp[bp.dist_m.notna() & ~bp.spike.astype(bool)]
    w = bp.pivot_table(index=KEY, columns='year', values='dist_m').reindex(columns=YEARS)
    return w.reindex(pd.MultiIndex.from_frame(u[KEY]))


def change(w, period):
    """Retreat between two 3-yr means (m, + = landward) and the edge-switch flag (|rate| > MAX_RATE, set to NaN);
    NaN unless each mean has >= MIN_YRS valid years."""
    (a0, a1), (b0, b1) = period
    a, b = w.loc[:, a0:a1], w.loc[:, b0:b1]
    ok = (a.notna().sum(1) >= MIN_YRS) & (b.notna().sum(1) >= MIN_YRS)
    d = (b.mean(1) - a.mean(1)).where(ok).to_numpy()
    jump = np.abs(d) > MAX_RATE * ((b0 + b1) - (a0 + a1)) / 2
    return np.where(jump, np.nan, d), jump


def annual(w):
    """Year-to-year retreat (m/yr) on a 3-yr centred rolling mean, labelled by the later year. Where a year is missing
    (2012, the 2024 edge) the mean covers 2 years; dividing by the shift of its mean year keeps a trend unbiased."""
    yr = w.notna() * np.array(YEARS, float)
    roll = w.T.rolling(3, center=True, min_periods=2).mean().T
    cy = (yr.T.rolling(3, center=True, min_periods=2).sum() / w.notna().T.rolling(3, center=True, min_periods=2).sum()).T
    cy = cy.where(roll.notna())
    r = roll.diff(axis=1) / cy.diff(axis=1)
    return r.where(r.abs() <= MAX_ANNUAL)


def summarise(u, unit):
    """Per-unit summaries of the point metrics."""
    g = u.groupby(unit)
    q = lambda c, p: g[c].quantile(p)
    s = pd.DataFrame({
        'river': g.river.first(), 'channel': g.channel.first(), 'side': g.side.first(), 'type': g.type.first(),
        'km_from': g.chainage_m.min() / 1e3, 'km_to': g.chainage_m.max() / 1e3,
        'lon': g.lon.median(), 'lat': g.lat.median(), 'n_points': g.size(),
        'n_lrr': g.lrr.count(), 'lrr_med': g.lrr.median(), 'lrr_p90': q('lrr', .9),
        'lrr_sh1': g.lrr.apply(lambda x: (x.dropna() > 1).mean()),
        'sh_step': g.kind.apply(lambda x: x.dropna().eq('step').mean()),
        'sh_nonlinear': g.kind.apply(lambda x: x.dropna().eq('nonlinear').mean()),
        'n_win': g.win.count(), 'win_med': g.win.median(), 'win_p75': q('win', .75), 'win_p90': q('win', .9),
        'win_max': g.win.max(), 'n_win_jump': g.win_jump.sum(),
        'n_pre': g.pre.count(), 'pre_med': g.pre.median(), 'pre_p75': q('pre', .75), 'pre_p90': q('pre', .9),
        'pre_max': g.pre.max(), 'n_pre_jump': g.pre_jump.sum()})
    for m in (10, 20, 30):
        s[f'win_sh{m}'] = g.win.apply(lambda x: (x.dropna() > m).mean())
        s[f'pre_sh{m}'] = g.pre.apply(lambda x: (x.dropna() > m).mean())
    s['few_points'] = s.n_win < MIN_PTS
    for name, (_, rule) in LABELS.items():
        s[f'lab_{name}'] = rule(s).astype('Int64').mask(s.few_points)
    for v in ('lin', 'clean'):   # lin: linear + step series only; clean: no within-window jump > WIN_JUMP
        s[f'n_win_{v}'], s[f'win_p75_{v}'] = g[f'win_{v}'].count(), q(f'win_{v}', .75)
        s[f'lab_{PRIMARY}_{v}'] = (s[f'win_p75_{v}'] >= 20).astype('Int64').mask(s[f'n_win_{v}'] < MIN_PTS)
    return s.round(3).rename_axis('unit').reset_index()


def events(u, a, unit):
    """Unit-year p90 of the annual retreat and event flags."""
    long = a.set_axis(u[unit].to_numpy()).rename_axis('unit').stack().rename('r').reset_index()
    long = long.rename(columns={'level_1': 'year'})
    g = long.groupby(['unit', 'year']).r
    e = pd.DataFrame({'n': g.count(), 'p90': g.quantile(.9).round(2)}).reset_index()
    e = e[e.n >= MIN_PTS].copy()
    for m in EVENT_M:
        e[f'ev{m}'] = (e.p90 >= m).astype(int)
    e['in_window'] = e.year.between(2015, 2024)
    return e


def prevalence(s):
    """Number and share of labelled units per candidate, overall and by river / channel type."""
    rows = []
    groups = [('all', s), *[(f'{r} {t}', g) for (r, t), g in s.groupby(['river', 'type'])]]
    for name, (desc, _) in LABELS.items():
        row = {'label': name, 'definition': desc}
        for gname, g in groups:
            lab = g[f'lab_{name}'].dropna()
            row[gname] = f'{int(lab.sum())}/{len(lab)} ({lab.mean():.0%})'
        rows.append(row)
    return pd.DataFrame(rows)


def noise_floor():
    """1.96 x SD of a 3-yr-mean difference, for the measured noise and for the median robust residual scale."""
    sd_res = pd.concat([pd.read_csv(f'data/processed/{r}/trends.csv') for r in ('tien', 'hau', 'islands')])
    sig2 = float(sd_res.loc[sd_res.kind == 'linear', 'sd_res'].median())
    out = {}
    for name, s in (('measured', SIGMA), ('residual', sig2)):
        out[name] = dict(sigma=s, win3=1.96 * s * np.sqrt(2 / 3), win2=1.96 * s, annual=1.96 * s * np.sqrt(2) / 3)
    return out


def figure(s, prim_m=20):
    """(a, b) along-river p75 window retreat of 2 km units, Tien / Hau main channels; (c) ECDF by channel type."""
    fig = plt.figure(figsize=(COL2, COL2 * .5))
    gs = fig.add_gridspec(2, 2, width_ratios=[2.2, 1], wspace=.32, hspace=.55)
    ok = s[~s.few_points]
    for k, river in enumerate(('tien', 'hau')):
        ax = fig.add_subplot(gs[k, 0])
        for side, col, name, mk in (('L', BLUE, 'left bank', 'o'), ('R', ORANGE, 'right bank', 's')):
            g = ok[(ok.channel == river) & (ok.side == side)].sort_values('km_from')
            x, y = g.km_from.to_numpy() + 1, g.win_p75.clip(-30, 170).to_numpy()   # unit centre
            gap = np.r_[False, np.diff(x) > 3]                                     # no line across missing units
            ax.plot(np.insert(x, np.nonzero(gap)[0], np.nan), np.insert(y, np.nonzero(gap)[0], np.nan), color=col,
                    lw=.7, alpha=.6)
            ax.plot(x, y, mk, ms=3, mfc=col, mec='white', mew=.4, label=name)
        ax.axhline(0, color=INK2, lw=.6)
        ax.axhline(prim_m, color=INK, lw=.8, ls=(0, (4, 2)))
        ax.text(.995, prim_m + 4, f'primary threshold {prim_m} m', transform=ax.get_yaxis_transform(), ha='right',
                va='bottom', fontsize=7, color=INK)
        ax.set_xlim(-10, 150)
        ax.set_ylim(-30, 170)
        ax.set_ylabel('Retreat 2014→2023,\nunit p75 (m)')
        chart_axes(ax)
        ax.set_title(f'({"ab"[k]}) {"Tien" if river == "tien" else "Hau"} River, 2 km units', loc='left', pad=3,
                     fontweight='bold')
        if k == 0:
            ax.legend(loc='upper left', ncol=2, handletextpad=.2)
        else:
            ax.set_xlabel('Distance downstream of the border (km)')
    ax = fig.add_subplot(gs[:, 1])
    for t, col, name in (('main', BLUE, 'Main'), ('island', AQUA, 'Island')):
        v = np.sort(ok.loc[ok.type == t, 'win_p75'].clip(-20, 100).to_numpy())
        ax.step(v, 1 - np.arange(len(v)) / len(v), where='post', color=col, lw=1.4,
                label=f'{name} (n = {len(v)})')
    ax.axvline(prim_m, color=INK, lw=.8, ls=(0, (4, 2)))
    ax.set_xlim(-20, 100)
    ax.set_xticks([-20, 0, 20, 50, 100], ['≤ −20', '0', '20', '50', '≥ 100'])
    ax.set_xlabel('Unit p75 retreat (m)')
    ax.set_ylabel('Share of units ≥ value')
    chart_axes(ax)
    ax.legend(loc='upper right', title='Channels', alignment='left', bbox_to_anchor=(1, .85))
    ax.set_title('(c) All in-scope units', loc='left', pad=3, fontweight='bold')
    save(fig, 'fig05_sat_labels')


DIAG = [('tien', 199, 'L', 'tien_L_+008'), ('isl_tien_01', 66, 'O', 'isl_tien_01_O_+003'),
        ('isl_tien_02', 127, 'I', 'isl_tien_02_I_+006'), ('tien', 315, 'L', 'tien_L_+015'),
        ('tien', 321, 'L', 'tien_L_+015'), ('hau', 814, 'L', 'hau_L_+040')]


def diagnostic(w):
    """Annual series of points in primary positives that rest on step / non-linear series (QA, not for the paper)."""
    fig, axs = plt.subplots(2, 3, figsize=(COL2, COL2 * .5), sharex=True)
    for ax, (ch, tr, side, unit) in zip(axs.flat, DIAG):
        s = w.loc[(ch, tr, side)].dropna()
        ax.plot(s.index, s.values, 'o-', ms=2.5, lw=.7, color=BLUE)
        for a, b in WIN:
            ax.axvspan(a - .5, b + .5, color=INK2, alpha=.12, lw=0)
        ax.set_title(f'{unit}  T{tr}{side}', fontsize=7, loc='left')
        chart_axes(ax)
    for ax in axs[:, 0]:
        ax.set_ylabel('dist_m (m, + landward)')
    fig.tight_layout()
    fig.savefig('results/p1/sat_labels_series_check.png', dpi=150)
    plt.close(fig)


def report(s2, s5, ev, nf, u):
    pv2, pv5 = prevalence(s2), prevalence(s5)
    ew = ev[ev.in_window]
    unit_ev = ew.groupby('unit')[[f'ev{m}' for m in EVENT_M]].max()
    m, r = nf['measured'], nf['residual']
    few = s2[s2.few_points]
    pos = s2[f'lab_{PRIMARY}'] == 1
    dep = s2[pos & ((s2[f'lab_{PRIMARY}_lin'] != 1) | (s2[f'lab_{PRIMARY}_clean'] != 1))]
    lines = [
        '# Satellite erosion labels per reach unit (H3 label source b)', '',
        'Generated by `python src/sat_labels.py` (no reported-inventory data read). Retreat = + (bank moved landward).',
        f'In scope: {len(u)} bank points, {s2.shape[0]} units of 2 km, {s5.shape[0]} of 5 km; '
        f'{int((~s2.few_points).sum())} 2 km units and {int((~s5.few_points).sum())} 5 km units have >= {MIN_PTS} '
        'points with a window retreat.', '',
        '## Definitions', '',
        '- Point window retreat = mean(dist 2022-2024) - mean(dist 2013-2015), i.e. 2014 -> 2023 (9 yr), each mean '
        f'needing >= {MIN_YRS} valid years. Pre-window = mean(2012-2014) - mean(2000-2002) (2001 -> 2013, 12 yr).',
        '- Long-term: Theil-Sen lrr 2000-2024 per point (all kinds); sh_nonlinear = share of step or non-linear series.',
        '- Annual: year-to-year change of a 3-yr centred rolling mean (2-yr where 2012 is missing and at 2024, '
        'divided by the shift of the mean year); unit-year p90 over points; events p90 >= '
        + ', '.join(f'{x}' for x in EVENT_M) + ' m/yr.',
        f'- Points whose window or pre-window change exceeds {MAX_RATE:.0f} m/yr (edge switches: bar attached or '
        'detached, island-ring jumps; the fastest validated hotspot is ~22 m/yr) are left out and counted in '
        f'n_win_jump / n_pre_jump ({int(s2.n_win_jump.sum())} / {int(s2.n_pre_jump.sum())} points); annual changes '
        f'> {MAX_ANNUAL:.0f} m/yr likewise.',
        f'- A unit label is left empty when fewer than {MIN_PTS} points have a window retreat ({len(few)} 2 km units).',
        '', '## Prevalence of candidate window labels (2 km units; labelled / units with a label)', '',
        pv2.to_markdown(index=False), '', '5 km units (sensitivity):', '', pv5.to_markdown(index=False), '',
        'Unit-year events in 2015-2024 (2 km): '
        + '; '.join(f'p90 >= {x} m/yr: {int(ew[f"ev{x}"].sum())} unit-years in {int(unit_ev[f"ev{x}"].sum())} units'
                    for x in EVENT_M) + f' (of {ew.unit.nunique()} units with annual data). Per year (p90 >= 15): '
        + ', '.join(f'{y} {n}' for y, n in ew.groupby('year').ev15.sum().items()) + '. The 2024 change uses a '
        'one-sided 2-yr mean (noise ~1.7x an interior year) and has about twice the events of other years; '
        'treat 2024 events as uncertain (likewise 2012, next to the missing composite).', '',
        '## Robustness to series kind and edge switches (2 km, primary rule)', '',
        f'Of the {int(pos.sum())} primary positives, {int((s2.loc[pos, f"lab_{PRIMARY}_lin"] == 1).sum())} stay '
        f'positive when non-linear series are dropped (lab_{PRIMARY}_lin, linear + step only; '
        f'{int(s2[f"lab_{PRIMARY}_lin"].sum())}/{s2[f"lab_{PRIMARY}_lin"].count()} units positive) and '
        f'{int((s2.loc[pos, f"lab_{PRIMARY}_clean"] == 1).sum())} when points with a year-to-year jump > '
        f'{WIN_JUMP:.0f} m inside 2013-2024 are dropped (lab_{PRIMARY}_clean; '
        f'{int(s2[f"lab_{PRIMARY}_clean"].sum())}/{s2[f"lab_{PRIMARY}_clean"].count()}). Positives that change '
        'under either variant:', '',
        dep[['unit', 'km_from', 'n_win', 'sh_step', 'sh_nonlinear', 'win_p75', 'n_win_lin', 'win_p75_lin',
             'n_win_clean', 'win_p75_clean']].round(2).to_markdown(index=False), '',
        'Many large positives are step series, not non-linear ones: a riverward jump of 0.5-1.1 km in 2002-2006 (an '
        'island or bar joined the mainland, so the measured bank moved to its outer edge), then steady retreat of '
        'that new bank through the window (e.g. tien_L_+008 T199L, isl_tien_01_O_+003 T66O, isl_tien_02_I_+006 '
        'T127I; `results/p1/sat_labels_series_check.png`). Their long-term lrr is negative because of the old step, '
        'but the window retreat is real retreat of the present bank. Non-linear positives (tien_L_+015) are '
        'accelerating-then-slowing retreat, with one landward step 2011->2013 at T321L just before the window. A '
        'true artefact is flip-flopping between two edges (hau_L_+040 T814L, ~70 m alternations; _lin drops the unit, '
        '_clean keeps it at the threshold) and a bar that sits in front of the bank and then goes (isl_hau_02_O_+003: '
        'bank ~130 m riverward 2015-2021, back in 2022; _clean drops it). tien_R_+059 has a 60-130 m landward jump in '
        '2023 that persists in 2024 (a collapse or a detached bar; check imagery). Primary label therefore uses all '
        'points; the _clean variant is the robustness check.', '',
        '## Noise floor', '',
        f'Per-composite noise sigma = {m["sigma"]:.1f} m (measured repeatability) or {r["sigma"]:.1f} m (median robust '
        'residual scale of linear series, includes real year-to-year bank wobble). Difference of two 3-yr means: SD = '
        'sigma x sqrt(2/3); 95% (1.96 SD) floor '
        f'{m["win3"]:.1f} / {r["win3"]:.1f} m with 3 valid years in each mean, {m["win2"]:.1f} / {r["win2"]:.1f} m with '
        f'2. Annual rolling-mean change: {m["annual"]:.1f} / {r["annual"]:.1f} m/yr. Bank-position bias vs hand clicks '
        '(-10 to -20 m) is systematic and largely cancels in a difference. A 20 m point threshold is >= 2x the larger '
        'floor; a unit p75 over ~20 points is less noisy still, so the labels are limited by real change, not noise.', '',
        '## Recommendation', '',
        f'- Primary: **{PRIMARY}** ({LABELS[PRIMARY][0]}): a quarter of the unit (~500 m of a 2 km bank) retreated '
        'about 2 m/yr or more over the window, well above the noise floor; robust to a few bad points (multi-edge '
        'banks, transient objects) unlike max or p90; sh20_25 is nearly the same rule (p75 >= 20 m <=> at least a '
        'quarter of points >= 20 m, up to quantile interpolation), so it is not a separate variant.',
        f'- Sensitivity: **{VARIANTS[0]}** (stricter, ~3x the larger 95% floor, fewer and more certain positives) and '
        f'**{VARIANTS[1]}** (localised hotspots: ~200 m of bank retreating >= 30 m), plus the 5 km units and '
        f'{PRIMARY}_clean (edge switches inside the window removed).',
        f'- All points, not linear + step only: dropping non-linear series changes 3 positives, and dropping by kind '
        'is the wrong filter anyway (step and non-linear kinds describe 2000-2024, mostly before the window); the '
        f'within-window jump filter targets the actual failure. Fixed parameters: MAX_RATE {MAX_RATE:.0f} m/yr, '
        f'WIN_JUMP {WIN_JUMP:.0f} m, MIN_PTS {MIN_PTS}.',
        '- Event table (p90 >= 15 m/yr) for year-matched comparisons; long-term lrr and pre-window retreat as '
        'predictors, not labels.', '',
        '## Caveats', '',
        f'- Units with few points ({len(few)} of {len(s2)} 2 km units have < {MIN_PTS}): unit ends cut by the scope or '
        'border, island rings with patchy detection; their label is empty, not 0.',
        '- Island rings: side I is the island bank, O the opposite bank of the side channel; channels narrower than '
        'the canal filter give non-detections; ring banks within 150 m of a main bank were dropped (no double count).',
        '- Embanked reaches: a bank that retreated before an embankment and then stopped scores low in the window; '
        'Landsat sees retreat, not damage or risk. Accretion (negative retreat) is kept as measured.',
        '- 30 m pixels: collapses smaller than ~1 pixel and short-lived scars repaired within a year are missed.',
        '- Positives are concentrated: on the Hau main channel the primary label is almost never 1 (window retreat is '
        'small there), so H3 rests mainly on the Tien and the island channels; report H3 by river / channel type.',
        f'- Edge switches below {MAX_RATE:.0f} m/yr (multi-edge banks, ~100 m) are not caught by the cap; unit p75 limits '
        'their effect but a unit made mostly of such points can be mislabelled (check positives on imagery).',
        '- Thresholds chosen from noise and prevalence only, before any comparison with reported sites.',
    ]
    pathlib.Path('results/p1/sat_labels.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(pv2.to_string(index=False))


def main():
    u = points()
    w = positions(u)
    (u['win'], u['win_jump']), (u['pre'], u['pre_jump']) = change(w, WIN), change(w, PRE)
    u['win_lin'] = u.win.where(u.kind.isin(['linear', 'step']))
    u['win_clean'] = u.win.where(w.loc[:, WIN[0][0]:].ffill(axis=1).diff(axis=1).abs().max(axis=1).to_numpy()
                                 <= WIN_JUMP)
    a = annual(w)
    s2, s5 = summarise(u, 'unit_2km'), summarise(u, 'unit_5km')
    assert s2.n_points.sum() == len(u) and s2.shape[0] == u.unit_2km.nunique()
    s2.to_csv('data/processed/sat_labels_2km.csv', index=False)
    s5.to_csv('data/processed/sat_labels_5km.csv', index=False)
    ev = events(u, a, 'unit_2km')
    ev.to_csv('data/processed/sat_events_2km.csv', index=False)
    nf = noise_floor()
    report(s2, s5, ev, nf, u)
    figure(s2)
    diagnostic(w)


if __name__ == '__main__':
    main()
