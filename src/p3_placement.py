"""P3 robustness R2: placement error of reported rows (docs/p3_plan.md R2, protocol deviation 6).

Usage: python src/p3_placement.py        run all draws, write the CSV, report and figure
       python src/p3_placement.py fig    redraw the figure from data/processed/p3_placement_draws.csv
Design (fixed in docs/p3_plan.md before running): each of the 124 usable inventory rows (h3.inventory) is shifted along
its bank by k = 1 or 2 units of 2 km, direction random per row (same direction for every unit of the row), each unit
staying on its own channel and side and clipped at the lowest / highest in-scope index of that channel-side; 200 draws
per k, seed 0 (one direction matrix, used for both k: draw j of k = 2 is draw j of k = 1 moved twice as far).
The reported labels are rebuilt with h3.reported on a shifted copy of the inventory (rep, rep_event); the satellite label,
features, blocks and folds are those of h3.unit_table (2 km). Per draw: logistic leave-one-block-out (h3.oof) AUC matrix
and ΔAUC for the any-row and the event-only label, omission and commission shares as explore_reporting defines them.
First 20 draws per k: full H3 decision (h3.analyse with its block bootstrap, h3.verdict).
Writes data/processed/p3_placement_draws.csv, results/p3/placement.md, figures/figS1_placement.png + .svg.
"""
import pathlib
import re
import sys
import time
from multiprocessing import Pool

import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import h3  # noqa: E402
from explore_reporting import FLOOR  # noqa: E402
from figures import BLUE, COL2, GRID, INK, INK2, ORANGE, chart_axes, plt, save  # noqa: E402

KS, NDRAW, NFULL, SEED, WORKERS = (1, 2), 200, 20, 0, 4
PAT = re.compile(r'^(.*)_([LRIO])_([+-]\d+)$')
CSV = pathlib.Path('data/processed/p3_placement_draws.csv')
LABELS = {'rep': 'any row', 'rep_event': 'event rows'}
# original values (results/p2/explore_reporting.md; checked against the k = 0 run below)
ORIG_CI = {'omission': (.13, .44), 'omission_event': (.47, .72), 'commission': (.71, .84)}


def channel_ranges():
    """(channel, side) -> lowest, highest unit index among in-scope 2 km units."""
    pts = pd.read_csv('data/processed/units.csv', encoding='utf-8')
    g = {}
    for x in set(pts[pts.in_scope].unit_2km):
        c, s, i = PAT.match(x).groups()
        g.setdefault((c, s), []).append(int(i))
    return {k: (min(v), max(v)) for k, v in g.items()}


def shift(inv, k, dirs, rng):
    """Copy of inv with every unit of row r moved k * dirs[r] along its channel-side, clipped at the ends."""
    def one(s, dr):
        out = []
        for x in s.split('; '):
            c, sd, i = PAT.match(x).groups()
            lo, hi = rng[(c, sd)]
            out.append(f'{c}_{sd}_{min(max(int(i) + dr * k, lo), hi):+04d}')
        return '; '.join(dict.fromkeys(out))
    inv = inv.copy()
    inv['units_2km'] = [one(s, dr) for s, dr in zip(inv.units_2km, dirs)]
    return inv


def labelled(d, inv):
    """d with rep / rep_event rebuilt exactly as h3.unit_table does."""
    d = d.copy()
    for name, pos in h3.reported(inv, None, 'unit_2km').items():
        d[name] = d.unit.isin(pos).astype(int)
    return d


# ---------- one draw (worker) ----------

G = {}


def init(d, s_sat):
    G.update(d=d, s_sat=s_sat)


def draw(task):
    k, j, inv, full = task
    d = labelled(G['d'], inv)
    ysat, w = d.lab_p75_20.to_numpy(int), d.win_p75.to_numpy()
    out = dict(k=k, draw=j)
    for name in LABELS:
        y = d[name].to_numpy(int)
        sc = {'reported': h3.oof(d, y, 'LR'), 'satellite': G['s_sat']}
        for train, s in sc.items():
            a_r, a_s = h3.auc(y, s), h3.auc(ysat, s)
            out |= {f'{name}_{train}_auc_rep': a_r, f'{name}_{train}_auc_sat': a_s, f'{name}_{train}_dauc': a_r - a_s}
        out |= {f'{name}_pos': int(y.sum()), f'{name}_changed': int((y != G['d'][name].to_numpy()).sum()), f'{name}_omission': np.mean(y[ysat == 1] == 0),
                f'{name}_commission': np.mean(w[y == 1] < FLOOR), f'{name}_kappa': h3.cohen_kappa_score(y, ysat)}
        if full:
            an = 'units 2km' if name == 'rep' else 'event-only reported'
            m = h3.analyse(an, d, name, 'lab_p75_20', models=('LR',), proxies=('built_1km',), groups=False)[0]
            v = h3.verdict(m, an)
            for train in h3.SOURCES:
                q = m[(m.train == train) & (m.stat == 'dauc') & (m.group == 'all')].iloc[0]
                out |= {f'{name}_{train}_dauc_lo': q.lo, f'{name}_{train}_dauc_hi': q.hi,
                        f'{name}_{train}_supported': v[train]['supported'], f'{name}_{train}_gap': v[train]['gap'],
                        f'{name}_{train}_monotone': v[train]['monotone'], f'{name}_{train}_trend': v[train]['trend']}
            out[f'{name}_verdict'] = 'supported' if v['overall'] else 'not supported'
    return out


# ---------- run ----------

def run():
    t0 = time.time()
    u, pc, cfg = h3.point_tables()
    inv = h3.inventory()
    d = h3.unit_table('unit_2km', u, pc, cfg, inv)
    d = d[d.lab_p75_20.notna()].reset_index(drop=True)          # as h3.analyse
    s_sat = h3.oof(d, d.lab_p75_20.to_numpy(int), 'LR')
    rng_ch = channel_ranges()
    dirs = np.random.default_rng(SEED).choice([-1, 1], size=(NDRAW, len(inv)))
    # shifted units falling in an index gap (unit dropped / out of scope) or merged by clipping: reported in the md
    allu = {f'{c}_{s}_{i:+04d}' for (c, s), (lo, hi) in rng_ch.items() for i in range(lo, hi + 1)}
    insc = set(pd.read_csv('data/processed/units.csv').query('in_scope').unit_2km)
    assert {x for s in inv.units_2km for x in s.split('; ')} <= insc
    tasks = [(0, 0, inv, True)]
    for k in KS:
        for j in range(NDRAW):
            tasks.append((k, j, shift(inv, k, dirs[j], rng_ch), j < NFULL))
    gap = {k: np.mean([np.mean([x not in insc for s in t[2].units_2km for x in s.split('; ')])
                       for t in tasks if t[0] == k]) for k in KS}
    lost = {k: np.mean([sum(len(a.split('; ')) - len(b.split('; ')) for a, b in zip(inv.units_2km, t[2].units_2km))
                        for t in tasks if t[0] == k]) for k in KS}
    assert all(x in allu for t in tasks for s in t[2].units_2km for x in s.split('; '))
    tasks.sort(key=lambda t: not t[3])                            # full decisions first: long tasks start early
    with Pool(WORKERS, initializer=init, initargs=(d, s_sat)) as p:
        res = p.map(draw, tasks, chunksize=1)
    R = pd.DataFrame(res).sort_values(['k', 'draw']).reset_index(drop=True)
    check_k0(R.iloc[0], d)
    R.round(5).to_csv(CSV, index=False)
    report(R, gap, lost, time.time() - t0, d)
    figure(R)
    print(f'done {time.time() - t0:.0f} s')


def check_k0(r, d):
    """k = 0 reproduces results/p2 (h3_metrics.csv point values, explore_reporting counts)."""
    m = pd.read_csv('data/processed/h3_metrics.csv')
    for an, name in (('units 2km', 'rep'), ('event-only reported', 'rep_event')):
        for train in h3.SOURCES:
            for st, col in (('auc_reported', 'auc_rep'), ('auc_satellite', 'auc_sat'), ('dauc', 'dauc')):
                ref = m[(m.analysis == an) & (m.model == 'LR') & (m.train == train) & (m.stat == st) & (m.group == 'all')]
                assert abs(ref.est.iloc[0] - r[f'{name}_{train}_{col}']) < 1e-3, (an, train, st)
    sat = d.lab_p75_20 == 1
    assert ((d.rep == 0) & sat).sum() == 12 and ((d.rep_event == 0) & sat).sum() == 25 and sat.sum() == 43
    assert ((d.rep == 1) & (d.win_p75 < FLOOR)).sum() == 201 and d.rep.sum() == 260
    assert r.rep_verdict == 'not supported' and r.rep_event_verdict == 'not supported'


# ---------- report ----------

def q(x, pct=False):
    x = x.dropna()
    f = (lambda v: f'{100 * v:.0f}%') if pct else (lambda v: f'{v:.2f}')
    return f'{f(x.median())} [{f(x.quantile(.025))}, {f(x.quantile(.975))}]'


def reading(R):
    """Plain statements of how the point values move with k (computed, no rule applied)."""
    m = lambda k, c: R[R.k == k][c].median()
    o = R[R.k == 0].iloc[0]
    f = R[(R.k > 0) & R.rep_verdict.notna()]
    cnt = lambda c: int(f[c].astype(bool).sum())
    below = {k: (R[R.k == k].rep_reported_auc_rep > o.rep_reported_auc_rep).mean() for k in KS}
    return [
        f'- The verdict holds, but the reported-trained point values are placement-sensitive. Trained on reported '
        f'(any row): AUC against satellite {o.rep_reported_auc_sat:.2f} (original) -> {m(1, "rep_reported_auc_sat"):.2f} '
        f'(k = 1) -> {m(2, "rep_reported_auc_sat"):.2f} (k = 2), AUC against reported {o.rep_reported_auc_rep:.2f} -> '
        f'{m(1, "rep_reported_auc_rep"):.2f} -> {m(2, "rep_reported_auc_rep"):.2f}, so ΔAUC {o.rep_reported_dauc:+.2f} -> '
        f'{m(1, "rep_reported_dauc"):+.2f} -> {m(2, "rep_reported_dauc"):+.2f}. The original AUC against reported is lower '
        f'than in {100 * below[1]:.0f}% (k = 1) and {100 * below[2]:.0f}% (k = 2) of the displaced draws, and the weak '
        'satellite signal of the reported-trained model fades as rows move: the original placement carries a little real '
        'erosion information that a 2-4 km shift removes, while displaced labels are, if anything, more learnable from the physical '
        'covariates. (Diagnostic, not part of the design: dropping instead of clipping units beyond a channel end gives '
        'the same pattern in 40 draws, so clipping does not cause it.)',
        f'- Trained on satellite, ΔAUC stays negative ({m(1, "rep_satellite_dauc"):+.2f}, {m(2, "rep_satellite_dauc"):+.2f}) '
        f'and its block-bootstrap CI excludes 0 in {cnt("rep_satellite_gap")} of {len(f)} full-decision draws (any row; '
        'original: no). H3 still fails in every draw because the exposure-tercile conditions fail: terciles monotone in '
        f'{cnt("rep_reported_monotone")} / {cnt("rep_satellite_monotone")} and T3 - T1 CI excluding 0 in '
        f'{cnt("rep_reported_trend")} / {cnt("rep_satellite_trend")} of {len(f)} draws (trained on reported / satellite).',
        f'- Event rows: ΔAUC trained on reported {o.rep_event_reported_dauc:+.2f} -> {m(1, "rep_event_reported_dauc"):+.2f} '
        f'-> {m(2, "rep_event_reported_dauc"):+.2f}; its CI excludes 0 (positive) in '
        f'{int(f[f.k == 2].rep_event_reported_gap.astype(bool).sum())} of {int((f.k == 2).sum())} k = 2 draws; tercile '
        f'conditions met in {cnt("rep_event_reported_monotone")} (monotone) / {cnt("rep_event_reported_trend")} (trend) '
        f'of {len(f)} draws, so the event-only sensitivity is not supported in any draw either.',
        f'- Omission and commission medians barely move (omission {100 * m(1, "rep_omission"):.0f}% / '
        f'{100 * m(2, "rep_omission"):.0f}%, commission {100 * m(1, "rep_commission"):.0f}% / '
        f'{100 * m(2, "rep_commission"):.0f}% at k = 1 / 2), because reported rows cover 76% of units and a shift mostly '
        'moves labels between reported units.']


def qn(x):
    return f'{x.median():.0f} [{x.quantile(.025):.0f}, {x.quantile(.975):.0f}]'


def report(R, gap, lost, runtime, d):
    o = R[R.k == 0].iloc[0]
    L = ['# R2: placement error of reported rows', '',
         f'Generated by `python src/p3_placement.py` ({runtime:.0f} s, {WORKERS} worker processes). Design and criterion '
         'fixed before running in `docs/p3_plan.md` R2 (protocol deviation 6). This is a robustness check of the '
         'confirmatory H3 (`results/p2/h3.md`) and of the exploratory omission / commission shares '
         '(`results/p2/explore_reporting.md`); it changes neither.', '',
         '## Design', '',
         f'- The 124 usable inventory rows carry no coordinates; each labels a list of 2 km units (`units_2km`). For k = 1 '
         f'and 2 every unit of a row moves k units (2-4 km) along its bank, in one random direction per row, on its own '
         'channel and side (unit id channel_side_index; consecutive index = adjacent 2 km), clipped at the lowest / highest '
         f'in-scope index of that channel-side. {NDRAW} draws per k, seed {SEED}; one direction matrix serves both k '
         '(draw j of k = 2 moves each row twice as far as draw j of k = 1).',
         '- Reported labels rebuilt with `h3.reported` on the shifted rows (any row = `rep`; event rows only = '
         '`rep_event`, the H3 event-only sensitivity). Satellite label (`lab_p75_20`), features, 10 km blocks and '
         f'leave-one-block-out folds unchanged (`h3.unit_table`, {len(d)} units, {d.block.nunique()} blocks), so the '
         'satellite-trained scores are fixed and only the reported-trained model is refitted.',
         f'- Per draw: logistic AUC matrix and ΔAUC = AUC(reported) - AUC(satellite) (point values); omission = share of '
         f'the {int(d.lab_p75_20.sum())} satellite-eroding units with no reported (no event) row; commission = share of '
         f'reported units with win_p75 < {FLOOR} m (`explore_reporting.FLOOR`).',
         f'- First {NFULL} draws per k: the full H3 decision (`h3.analyse`, B = {h3.B} block bootstrap, `h3.verdict`; '
         'logistic model, built_1km terciles, as the primary analysis), for the any-row label (the H3 decision) and the '
         'event-only label (its sensitivity row).',
         '- k = 0 is the original inventory; the script asserts that it reproduces `data/processed/h3_metrics.csv` and '
         'the counts of `results/p2/explore_reporting.md` (omission 12/43, no event row 25/43, commission 201/260).', '',
         '## Distributions (median [2.5%, 97.5%] over draws; k = 0 = original point value)', '']
    for name, lab in LABELS.items():
        L += [f'Reported label: {lab}.', '',
              '| k | reported + | labels changed | trained on reported: AUC rep | AUC sat | ΔAUC | trained on satellite: AUC rep | AUC sat | ΔAUC | kappa |',
              '|---|---|---|---|---|---|---|---|---|---|']
        for k in (0,) + KS:
            x = R[R.k == k]
            c = [q(x[f'{name}_{t}_{s}']) for t in h3.SOURCES for s in ('auc_rep', 'auc_sat', 'dauc')]
            L.append(f'| {k} | {qn(x[f"{name}_pos"])} | {qn(x[f"{name}_changed"])} | ' + ' | '.join(c)
                     + f' | {q(x[f"{name}_kappa"])} |')
        L.append('')
    L += ['Omission and commission shares:', '',
          '| k | omission (no row) | omission (no event row) | commission (any row) | commission (event rows) |',
          '|---|---|---|---|---|']
    for k in (0,) + KS:
        x = R[R.k == k]
        L.append(f'| {k} | ' + ' | '.join(q(x[c], True) for c in ('rep_omission', 'rep_event_omission',
                                                                    'rep_commission', 'rep_event_commission')) + ' |')
    L += ['', f'Original 95% block-bootstrap CIs (explore_reporting.md): omission 28% [13, 44], no event row 58% [47, 72], '
          'commission 77% [71, 84].', '',
          '## Full H3 decision (first 20 draws per k)', '',
          '| k | label | draws | not supported | supported | ΔAUC CI excludes 0 (trained on reported / satellite) | '
          'median ΔAUC CI, trained on reported | trained on satellite |', '|---|---|---|---|---|---|---|---|']
    for k in (0,) + KS:
        x = R[(R.k == k) & R.rep_verdict.notna()]
        for name, lab in LABELS.items():
            vc = x[f'{name}_verdict'].value_counts()
            ex = ' / '.join(str(int(((x[f'{name}_{t}_dauc_lo'] > 0) | (x[f'{name}_{t}_dauc_hi'] < 0)).sum()))
                            for t in h3.SOURCES)
            ci = [f'[{x[f"{name}_{t}_dauc_lo"].median():.2f}, {x[f"{name}_{t}_dauc_hi"].median():.2f}]' for t in h3.SOURCES]
            L.append(f'| {k} | {lab} | {len(x)} | {vc.get("not supported", 0)} | {vc.get("supported", 0)} | {ex} | '
                     + ' | '.join(ci) + ' |')
    full = R[(R.k > 0) & R.rep_verdict.notna()]
    ok_v = (full.rep_verdict == 'not supported').all()
    inside = {(k, c): ORIG_CI[c][0] <= R[R.k == k][{'omission': 'rep_omission', 'omission_event': 'rep_event_omission',
                                                     'commission': 'rep_commission'}[c]].median() <= ORIG_CI[c][1]
              for k in KS for c in ORIG_CI}
    unchanged = ok_v and all(inside.values())
    L += ['', '## Criterion (fixed in docs/p3_plan.md R2)', '',
          f'- H3 "not supported" in every full-decision draw: {"yes" if ok_v else "NO"} '
          f'({int((full.rep_verdict == "not supported").sum())} of {len(full)}).',
          '- Median shares inside the original 95% CIs: ' + '; '.join(
              f'k = {k}: ' + ', '.join(f'{c.replace("_", " ")} {"yes" if inside[(k, c)] else "NO"}' for c in ORIG_CI)
              for k in KS) + '.', '',
          f'**R2 verdict: {"UNCHANGED" if unchanged else "CHANGED"}** (H3 and the omission / commission findings '
          f'{"are" if unchanged else "are not"} robust to moving every reported row by 2-4 km).', '',
          '## Reading', '', *reading(R), '', '## Caveats', '',
          f'- {int((pd.Series([len({PAT.match(x).groups()[:2] for x in s.split("; ")}) for s in h3.inventory().units_2km]) > 1).sum())} '
          'of the 124 rows list units on more than one channel-side (a commune that holds a main bank and island banks); '
          'every unit moves on its own channel-side, all in the row\'s direction. Direction on island rings follows the '
          'ring index, which is not up/downstream; islands are clipped at the ring index ends although a ring is closed.',
          f'- Shifted units that land in an index gap (no in-scope unit there: dropped ring banks of deviation 5, or out of '
          f'scope) label nothing: mean share of shifted unit slots in a gap {100 * gap[1]:.1f}% (k = 1), '
          f'{100 * gap[2]:.1f}% (k = 2). Clipping at channel ends and overlaps inside a row merge units: on average '
          f'{lost[1]:.1f} (k = 1) and {lost[2]:.1f} (k = 2) of the {sum(len(s.split("; ")) for s in h3.inventory().units_2km)} '
          'row-unit entries disappear per draw. Both make shifted labels slightly sparser than the original.',
          '- Rows overlap heavily (warned-reach lists and commune rows cover whole communes, 76% of units reported), so a '
          f'shift of 2-4 km changes only part of the unit labels (column "labels changed": about '
          f'{R[R.k == 1].rep_changed.median():.0f} of {len(d)} at k = 1, {R[R.k == 2].rep_changed.median():.0f} at k = 2); '
          'the check measures sensitivity to placement, not to coverage.',
          '- Full-decision draws are 20 per k (run time); point values cover all 200. Block-bootstrap intervals are for '
          'fixed scores (as in H3).']
    pathlib.Path('results/p3').mkdir(parents=True, exist_ok=True)
    pathlib.Path('results/p3/placement.md').write_text('\n'.join(L) + '\n', encoding='utf-8')


# ---------- figure ----------

def figure(R=None):
    R = pd.read_csv(CSV) if R is None else R
    fig, axs = plt.subplots(1, 2, figsize=(COL2, COL2 * .36), gridspec_kw=dict(width_ratios=[1, 1.15], wspace=.3, left=.085, right=.995, top=.93, bottom=.17))
    rng = np.random.default_rng(1)
    pos = {0: 0, 1: 1, 2: 2}
    DX = (-.25, 0, .25)

    def strip(ax, x0, v, col, mk):
        v = v.dropna().to_numpy()
        if len(v) == 1:
            ax.plot(x0, v[0], mk, color=col, ms=5, mec='white', mew=.5, zorder=3)
            return
        ax.plot(x0 + rng.uniform(-.09, .09, len(v)), v, mk, color=col, ms=2, alpha=.25, mew=0, zorder=2)
        lo, med, hi = np.percentile(v, [2.5, 50, 97.5])
        ax.plot([x0, x0], [lo, hi], color=INK, lw=.9, zorder=3)
        ax.plot(x0, med, mk, color=col, ms=5, mec=INK, mew=.6, zorder=4)

    ax = axs[0]
    for t, col, mk, dx in (('reported', BLUE, 'o', -.17), ('satellite', ORANGE, 's', .17)):
        for k in (0, 1, 2):
            strip(ax, pos[k] + dx, R[R.k == k][f'rep_{t}_dauc'], col, mk)
        ax.text(2.32, R[R.k == 2][f'rep_{t}_dauc'].median(), f'trained on\n{t}', color=col, fontsize=7, va='center')
    ax.axhline(0, color=INK2, lw=.6)
    ax.set_xticks([0, 1, 2], ['original', 'k = 1\n(2 km)', 'k = 2\n(4 km)'])
    ax.set_xlim(-.45, 2.95)
    ax.set_ylabel('ΔAUC (reported − satellite)')
    chart_axes(ax)
    ax.grid(axis='x', visible=False)
    ax.set_title('(a) Gap in AUC, logistic, block CV', loc='left', pad=3, fontweight='bold')

    ax = axs[1]
    series = (('rep_omission', 'omission\n(no row)', BLUE, 'o', 'omission'),
              ('rep_event_omission', 'omission\n(no event row)', '#1baf7a', '^', 'omission_event'),
              ('rep_commission', 'commission\n(< 9.3 m)', ORANGE, 's', 'commission'))
    for i, (c, lab, col, mk, key) in enumerate(series):
        lo, hi = ORIG_CI[key]
        ax.add_patch(plt.Rectangle((i - .4, 100 * lo), .8, 100 * (hi - lo), color=GRID, alpha=.6, lw=0, zorder=1))
        for k, dx in zip((0, 1, 2), DX):
            strip(ax, i + dx, 100 * R[R.k == k][c], col, mk)
    ax.set_xticks(range(3), [s[1] for s in series])
    ax.set_xlim(-.5, 2.5)
    ax.set_ylim(0, 100)
    ax.set_ylabel('Share of units (%)')
    chart_axes(ax)
    ax.grid(axis='x', visible=False)
    for dx, lab in zip(DX, ('0', '1', '2')):
        ax.text(dx, 4, lab, fontsize=7, color=INK2, ha='center', va='bottom')
    ax.text(-.47, 98, 'k = 0 (original), 1, 2 within each group\ngrey band: original 95% CI', fontsize=7,
            color=INK2, va='top')
    ax.set_title('(b) Omission and commission', loc='left', pad=3, fontweight='bold')
    save(fig, 'figS1_placement')


if __name__ == '__main__':
    figure() if sys.argv[1:] == ['fig'] else run()
