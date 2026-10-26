"""P2: H3, label-source sensitivity of susceptibility evaluation (docs/protocol.md section 3, protocol-v1).

Usage: python src/h3.py
Reads data/processed/units.csv, sat_labels_{2km,5km}.csv, covariates_{2km,5km}.csv, data/tiles.json and the reported
inventory data/hotspots/inventory.csv (rows with use_in_analysis == True, D6). Commune-bank units (channel, side,
province, district, commune) get their satellite labels from sat_labels.summarise and their covariates from
covariates.per_unit on the same point tables (both imported, not copied), so the rules are identical to the 2 km ones.
Writes:
  data/processed/h3_units.csv    one row per analysed unit (2km, 5km, commune-bank): block, group, exposure terciles,
                                 labels, out-of-fold scores of the primary models
  data/processed/h3_metrics.csv  long table of every statistic: analysis, model, train, stat, group, est, lo, hi, n
  results/p2/h3.md, figures/fig08_label_source.png + .svg
Fixed before any AUC was computed (a priori):
  logistic regression = median imputation (fitted on the training fold) + standardisation + L2, C = 1 (sklearn default,
      lbfgs); gradient boosting = HistGradientBoostingClassifier defaults (100 iterations, learning rate 0.1, 31 leaves,
      min 20 per leaf, no early stopping at this n), NaN handled natively, random_state 0.
  spatial CV = leave-one-block-out over 10 km blocks (every block is one fold; out-of-fold scores pooled).
  uncertainty = cluster (block) bootstrap: whole 10 km blocks resampled with replacement, B = 1000, seed SEED, the same
      draws for every statistic of one analysis (paired); 95% percentile intervals; resamples where a statistic is
      undefined (one class absent) are dropped and counted (n_boot).
  terciles = equal-count terciles of the exposure proxy over the analysed units, ordered least -> most exposed
      (road_km and town_km reversed: nearer = more exposed); cut points fixed, not re-drawn per resample.
  H3 verdict = protocol rule applied to the logistic model, per training source; overall "supported" only if both hold.
"""
import json
import pathlib
import sys
import time
import unicodedata

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr
from sklearn.base import clone
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, cohen_kappa_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import covariates as cv  # noqa: E402
import sat_labels as sl  # noqa: E402
from figures import AQUA, BLUE, COL2, GRID, INK, INK2, ORANGE, chart_axes, plt, save  # noqa: E402

FEATURES = ['curv_bank', 'width_m', 'dwidth_00_14', 'is_island', 'river_km', 'node_km', 'pre_p75']   # protocol s. 3
PROXIES = ['built_1km', 'pop_1km', 'viirs_1km', 'road_km', 'town_km']   # D8 primary first
REVERSED = {'road_km', 'town_km'}       # distance: smaller = more exposed
SAT_VARIANTS = ['lab_p75_30', 'lab_p90_30', 'lab_p75_20_clean']
B, SEED, BLOCK_KM = 1000, 20261026, 10
MODELS = {
    'LR': make_pipeline(SimpleImputer(strategy='median'), StandardScaler(), LogisticRegression(C=1.0, max_iter=1000)),
    'GB': HistGradientBoostingClassifier(random_state=0),
}
SOURCES = ('reported', 'satellite')
GROUPS = {'Tiền main': lambda d: d.channel == 'tien', 'Hậu main': lambda d: d.channel == 'hau',
          'island channels': lambda d: d.is_island == 1, 'Tiền (all)': lambda d: d.river == 'tien',
          'Hậu (all)': lambda d: d.river == 'hau'}


# ---------- inputs ----------

def point_tables():
    """In-scope points with window / pre-window retreat (as sat_labels.main) and point covariates (covariates.py)."""
    u = sl.points()
    w = sl.positions(u)
    (u['win'], u['win_jump']), (u['pre'], u['pre_jump']) = sl.change(w, sl.WIN), sl.change(w, sl.PRE)
    u['win_lin'] = u.win.where(u.kind.isin(['linear', 'step']))
    u['win_clean'] = u.win.where(w.loc[:, sl.WIN[0][0]:].ffill(axis=1).diff(axis=1).abs().max(axis=1).to_numpy()
                                 <= sl.WIN_JUMP)
    cfg = json.loads(pathlib.Path('data/tiles.json').read_text())
    pc = cv.point_covariates(cv.points(), cfg)
    for d in (u, pc):
        d['unit_cb'] = d.channel + '|' + d.side + '|' + d.province + '|' + d.district + '|' + d.commune
    return u, pc, cfg


def blocks(u, col, cfg):
    """10 km block per unit: main channels mean chainage of its points; islands the island's chainage on the parent."""
    isl = {k: (v['chainage_m'] - cfg['border_m'][v['parent']]) / 1e3 for k, v in cfg['islands'].items()}
    km = (u.chainage_m / 1e3).where(~u.channel.str.startswith('isl_'), u.channel.map(isl))
    g = pd.DataFrame({'river': u.river, 'km': km}).groupby(u[col]).agg(river=('river', 'first'), km=('km', 'mean'))
    return (g.river + '_' + (g.km // BLOCK_KM).astype(int).astype(str)).rename('block')


def inventory():
    inv = pd.read_csv('data/hotspots/inventory.csv', encoding='utf-8-sig')
    inv = inv[inv.use_in_analysis.astype(str) == 'True'].copy()
    nfc = lambda s: s.fillna('').map(lambda x: unicodedata.normalize('NFC', x))
    ut, st = nfc(inv.unit_type), inv.source_type
    # event rows: hamlet/landmark (unit_type vụ / điểm) or emergency decision; warned-reach lists never
    inv['event'] = (ut.isin(['vụ', 'điểm']) | (st == 'decision_via_news')) & (st != 'official_list_via_news')
    return inv


def row_points(u, r):
    """Bank points of one inventory row, as inventory_build matched them (its units and communes)."""
    pairs = [p.split(' / ') for p in r.communes_matched.split('; ')]
    return (u.unit_2km.isin(r.units_2km.split('; ')) & u.district.isin([p[0] for p in pairs])
            & u.commune.isin([p[1] for p in pairs]))


def reported(inv, u, col):
    """Units intersecting >= 1 row (all rows; event rows only)."""
    out = {}
    for name, rows in (('rep', inv), ('rep_event', inv[inv.event])):
        if col == 'unit_cb':
            m = np.zeros(len(u), bool)
            for _, r in rows.iterrows():
                m |= row_points(u, r).to_numpy()
            out[name] = set(u.loc[m, col])
        else:
            out[name] = {x for s in rows[f'units_{col[5:]}'] for x in s.split('; ')}
    return out


def unit_table(col, u, pc, cfg, inv):
    """Units with a satellite label (>= MIN_PTS points), covariates, labels, block and group."""
    if col == 'unit_cb':
        s = sl.summarise(u, col)
        c = cv.per_unit(pc, col)
    else:
        km = col[5:]
        s, c = pd.read_csv(f'data/processed/sat_labels_{km}.csv'), pd.read_csv(f'data/processed/covariates_{km}.csv')
    d = s[['unit', 'river', 'channel', 'side', 'n_win', 'win_p75', 'pre_p75', 'few_points', 'lab_p75_20']
          + SAT_VARIANTS].merge(c[['unit', 'is_island'] + [f for f in FEATURES if f not in ('pre_p75', 'is_island')]
                                  + PROXIES], on='unit', validate='one_to_one')
    d = d.merge(blocks(u, col, cfg), left_on='unit', right_index=True, how='left')
    for name, pos in reported(inv, u, col).items():
        d[name] = d.unit.isin(pos).astype(int)
    d = d[~d.few_points].reset_index(drop=True)
    d['group'] = np.where(d.is_island == 1, 'island channels', np.where(d.channel == 'tien', 'Tiền main', 'Hậu main'))
    for p in PROXIES:
        d[f't_{p}'] = pd.qcut(-d[p] if p in REVERSED else d[p], 3, labels=False)
    return d


# ---------- statistics ----------

def auc(y, s):
    """Mann-Whitney AUC (ties = 0.5); NaN if a class is absent."""
    n1 = y.sum()
    n0 = len(y) - n1
    if n1 == 0 or n0 == 0:
        return np.nan
    return (rankdata(s)[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def ap(y, s):
    return average_precision_score(y, s) if 0 < y.sum() < len(y) else np.nan


def boot_index(block):
    """B resamples of whole blocks (with replacement); each a row-index array."""
    rng = np.random.default_rng(SEED)
    members = [np.flatnonzero(block == b) for b in np.unique(block)]
    return [np.concatenate([members[i] for i in rng.integers(0, len(members), len(members))]) for _ in range(B)]


def boot(fn, n, idx):
    """Estimate on all rows, 95% percentile interval over the block resamples, number of defined resamples."""
    v = np.array([fn(i) for i in idx], float)
    ok = np.isfinite(v)
    lo, hi = np.percentile(v[ok], [2.5, 97.5]) if ok.sum() >= 2 else (np.nan, np.nan)
    return fn(np.arange(n)), lo, hi, int(ok.sum())


def oof(d, y, model):
    """Leave-one-block-out out-of-fold scores."""
    X, s = d[FEATURES].to_numpy(float), np.full(len(d), np.nan)
    for b in d.block.unique():
        te = (d.block == b).to_numpy()
        m = clone(MODELS[model]).fit(X[~te], y[~te])
        s[te] = m.predict_proba(X[te])[:, 1]
    return s


def analyse(name, d, rep, sat, models=('LR',), proxies=('built_1km',), groups=True):
    """2x2 AUC / PR-AUC, ΔAUC overall, by group and by exposure tercile, for every model and training source."""
    d = d[d[sat].notna()].reset_index(drop=True)
    y = {'reported': d[rep].to_numpy(int), 'satellite': d[sat].to_numpy(int)}
    idx, n, rows, scores = boot_index(d.block.to_numpy()), len(d), [], {}

    def add(model, train, stat, group, fn, mask=None):
        m = np.ones(n, bool) if mask is None else np.asarray(mask)
        est, lo, hi, nb = boot(lambda i: fn(i[m[i]]), n, idx)
        rows.append(dict(analysis=name, model=model, train=train, stat=stat, group=group, est=est, lo=lo, hi=hi,
                         n_boot=nb, n=int(m.sum()), pos_rep=int(y['reported'][m].sum()),
                         pos_sat=int(y['satellite'][m].sum())))

    for model in models:
        for train in SOURCES:
            s = scores[(model, train)] = oof(d, y[train], model)
            A = {lab: (lambda i, yy=y[lab]: auc(yy[i], s[i])) for lab in SOURCES}
            dA = lambda i: A['reported'](i) - A['satellite'](i)
            for lab in SOURCES:
                add(model, train, f'auc_{lab}', 'all', A[lab])
                add(model, train, f'ap_{lab}', 'all', lambda i, yy=y[lab]: ap(yy[i], s[i]))
            add(model, train, 'dauc', 'all', dA)
            if groups:
                for g, f in GROUPS.items():
                    for lab in SOURCES:
                        add(model, train, f'auc_{lab}', g, A[lab], f(d))
                    add(model, train, 'dauc', g, dA, f(d))
            for p in proxies:
                t = d[f't_{p}'].to_numpy()
                for k in range(3):
                    for lab in SOURCES:
                        add(model, train, f'auc_{lab}', f'{p} T{k + 1}', A[lab], t == k)
                    add(model, train, 'dauc', f'{p} T{k + 1}', dA, t == k)
                add(model, train, 'dauc_T3_T1', p, lambda i: dA(i[t[i] == 2]) - dA(i[t[i] == 0]))
    k_fn = lambda i: cohen_kappa_score(y['reported'][i], y['satellite'][i])
    add('-', '-', 'kappa', 'all', k_fn)
    return pd.DataFrame(rows), scores, d


def physical(d):
    """Satellite retreat and labels against each exposure proxy (block bootstrap), primary 2 km units."""
    idx, n, rows = boot_index(d.block.to_numpy()), len(d), []
    for p in PROXIES:
        x, t = d[p].to_numpy(), d[f't_{p}'].to_numpy()
        for stat, fn in (
                ('rho_win_p75', lambda i: spearmanr(x[i], d.win_p75.to_numpy()[i])[0]),
                ('rho_lab_sat', lambda i: spearmanr(x[i], d.lab_p75_20.to_numpy()[i])[0]),
                *[(f'prev_{lab}_T{k + 1}', lambda i, k=k, c=c: d[c].to_numpy()[i][t[i] == k].mean())
                  for lab, c in (('sat', 'lab_p75_20'), ('rep', 'rep')) for k in range(3)],
                *[(f'prev_{lab}_T3_T1', lambda i, c=c: d[c].to_numpy()[i][t[i] == 2].mean()
                   - d[c].to_numpy()[i][t[i] == 0].mean()) for lab, c in (('sat', 'lab_p75_20'), ('rep', 'rep'))],
                ('med_win_T3_T1', lambda i: np.median(d.win_p75.to_numpy()[i][t[i] == 2])
                 - np.median(d.win_p75.to_numpy()[i][t[i] == 0]))):
            est, lo, hi, nb = boot(fn, n, idx)
            rows.append(dict(analysis='physical 2km', model='-', train='-', stat=stat, group=p, est=est, lo=lo, hi=hi,
                             n_boot=nb, n=n))
    return pd.DataFrame(rows)


def verdict(m, analysis, model='LR', proxy='built_1km'):
    """Protocol rule: ΔAUC CI excludes 0, terciles monotone (point estimates) and T3 - T1 CI excludes 0."""
    out = {}
    for train in SOURCES:
        q = m[(m.analysis == analysis) & (m.model == model) & (m.train == train)].set_index(['stat', 'group'])
        da = q.loc[('dauc', 'all')]
        terc = np.array([q.loc[('dauc', f'{proxy} T{k}'), 'est'] for k in (1, 2, 3)])
        tt = q.loc[('dauc_T3_T1', proxy)]
        c1 = da.lo > 0 or da.hi < 0
        mono = bool(np.all(np.diff(terc) > 0) or np.all(np.diff(terc) < 0))
        c3 = tt.lo > 0 or tt.hi < 0
        out[train] = dict(gap=c1, monotone=mono, trend=c3, supported=c1 and mono and c3)
    out['overall'] = all(out[t]['supported'] for t in SOURCES)
    return out


# ---------- report ----------

def f3(r):
    return '-' if not np.isfinite(r.est) else f'{r.est:.2f} [{r.lo:.2f}, {r.hi:.2f}]'


def get(m, analysis, model, train, stat, group='all'):
    q = m[(m.analysis == analysis) & (m.model == model) & (m.train == train) & (m.stat == stat) & (m.group == group)]
    return q.iloc[0]


def matrix(m, analysis, model, stat='auc'):
    rows = [f'| trained on \\ scored against | reported | satellite | ΔAUC (rep - sat) |' if stat == 'auc' else
            '| trained on \\ scored against | reported | satellite |', '|---|---|---|---|' if stat == 'auc' else '|---|---|---|']
    for t in SOURCES:
        cells = [f3(get(m, analysis, model, t, f'{stat}_{lab}')) for lab in SOURCES]
        if stat == 'auc':
            cells.append(f3(get(m, analysis, model, t, 'dauc')))
        rows.append(f'| {t} | ' + ' | '.join(cells) + ' |')
    return rows


def report(m, phys, d2, ver, sens, agree, runtime):
    a, L = 'units 2km', []
    n, pr, ps = len(d2), d2.rep.mean(), d2.lab_p75_20.mean()
    L += ['# H3: label-source sensitivity of susceptibility evaluation', '',
          f'Generated by `python src/h3.py` ({runtime:.0f} s). Protocol: docs/protocol.md section 3 (protocol-v1, frozen '
          '26/10, deviation 1 concerns section 2 only). This is the first comparison of reported and satellite labels; '
          'no label definition, threshold, unit or variable was changed after it. Settings fixed a priori are listed in '
          'the module docstring of `src/h3.py`.', '',
          '## Units and labels', '',
          f'Primary: {n} in-scope 2 km units with a satellite label (>= {sl.MIN_PTS} points), {d2.block.nunique()} blocks '
          f'of {BLOCK_KM} km. Reported (D6, use_in_analysis, 124 rows): {int(d2.rep.sum())} positive ({pr:.0%}); event rows '
          f'only: {int(d2.rep_event.sum())} ({d2.rep_event.mean():.0%}). Satellite primary p75 >= 20 m: '
          f'{int(d2.lab_p75_20.sum())} ({ps:.0%}).', '',
          '| group | units | reported + | event-only + | satellite + |', '|---|---|---|---|---|']
    for g, f in [('all', lambda d: d.unit == d.unit)] + list(GROUPS.items()):
        x = d2[f(d2)]
        L.append(f'| {g} | {len(x)} | {int(x.rep.sum())} ({x.rep.mean():.0%}) | {int(x.rep_event.sum())} '
                 f'({x.rep_event.mean():.0%}) | {int(x.lab_p75_20.sum())} ({x.lab_p75_20.mean():.0%}) |')
    ct = pd.crosstab(d2.rep, d2.lab_p75_20)
    k = get(m, a, '-', '-', 'kappa')
    L += ['', '## Agreement of the two label sources (descriptive)', '',
          '| | satellite 0 | satellite 1 |', '|---|---|---|',
          f'| reported 0 | {ct.loc[0, 0]} | {ct.loc[0, 1]} |', f'| reported 1 | {ct.loc[1, 0]} | {ct.loc[1, 1]} |', '',
          f'Cohen kappa {f3(k)} (block bootstrap). Raw agreement {(d2.rep == d2.lab_p75_20).mean():.0%}. '
          'Agreement tables of the sensitivities: data/processed/h3_metrics.csv and the sensitivity table below.']
    L += ['', '## Evaluation matrix (2 km, spatial block CV, out-of-fold scores)', '',
          'cAUC = AUC of the pooled leave-one-block-out scores with a 95% interval from a cluster bootstrap that resamples '
          f'whole {BLOCK_KM} km blocks (B = {B}), so spatially clustered units are not treated as independent (clustered '
          'ROC data: Obuchowski, 1997, Biometrics 53; cluster bootstrap: Field and Welsh, 2007, JRSS B 69). The interval '
          'covers the sampling of blocks for fixed scores, not refitting. ΔAUC uses the same scores and the same '
          'resamples (paired).', '', 'Logistic regression (primary), AUC:', '']
    L += matrix(m, a, 'LR') + ['', 'PR-AUC (prevalence: reported '
                               f'{pr:.2f}, satellite {ps:.2f}):', ''] + matrix(m, a, 'LR', 'ap')
    L += ['', 'Gradient boosting (check), AUC:', ''] + matrix(m, a, 'GB') + ['', 'PR-AUC:', ''] + matrix(m, a, 'GB', 'ap')
    L += ['', '## By river and channel type (logistic regression, same out-of-fold scores)', '',
          '| group | trained on | n | rep + | sat + | AUC reported | AUC satellite | ΔAUC |', '|---|---|---|---|---|---|---|---|']
    for g in GROUPS:
        for t in SOURCES:
            r = get(m, a, 'LR', t, 'dauc', g)
            L.append(f'| {g} | {t} | {r.n} | {int(r.pos_rep)} | {int(r.pos_sat)} | {f3(get(m, a, "LR", t, "auc_reported", g))} | '
                     f'{f3(get(m, a, "LR", t, "auc_satellite", g))} | {f3(r)} |')
    L += ['', '## Gradient across exposure terciles (2 km)', '',
          'Terciles ordered least (T1) to most (T3) exposed. ΔAUC = AUC(reported) - AUC(satellite) within the tercile.', '',
          '| proxy | model | trained on | ΔAUC T1 | ΔAUC T2 | ΔAUC T3 | T3 - T1 |', '|---|---|---|---|---|---|---|']
    for p in PROXIES:
        for model in ('LR', 'GB'):
            if model == 'GB' and p != 'built_1km':
                continue
            for t in SOURCES:
                c = [f3(get(m, a, model, t, 'dauc', f'{p} T{k}')) for k in (1, 2, 3)]
                L.append(f'| {p} | {model} | {t} | ' + ' | '.join(c) + f' | {f3(get(m, a, model, t, "dauc_T3_T1", p))} |')
    L += ['', 'AUC within built_1km terciles (logistic regression):', '',
          '| trained on | tercile | n | rep + | sat + | AUC reported | AUC satellite |', '|---|---|---|---|---|---|---|']
    for t in SOURCES:
        for kk in (1, 2, 3):
            g = f'built_1km T{kk}'
            r = get(m, a, 'LR', t, 'auc_reported', g)
            L.append(f'| {t} | T{kk} | {r.n} | {int(r.pos_rep)} | {int(r.pos_sat)} | {f3(r)} | {f3(get(m, a, "LR", t, "auc_satellite", g))} |')
    L += ['', '## Physical check: satellite retreat vs exposure (2 km)', '',
          '| proxy | Spearman win_p75 | Spearman sat label | sat prevalence T1 / T2 / T3 | sat T3 - T1 | reported T1 / T2 / T3 | reported T3 - T1 | median win_p75 T3 - T1 (m) |',
          '|---|---|---|---|---|---|---|---|']
    P = phys.set_index(['stat', 'group'])
    for p in PROXIES:
        pv = lambda lab: ' / '.join(f'{P.loc[(f"prev_{lab}_T{k}", p), "est"]:.2f}' for k in (1, 2, 3))
        L.append(f'| {p} | {f3(P.loc[("rho_win_p75", p)])} | {f3(P.loc[("rho_lab_sat", p)])} | {pv("sat")} | '
                 f'{f3(P.loc[("prev_sat_T3_T1", p)])} | {pv("rep")} | {f3(P.loc[("prev_rep_T3_T1", p)])} | '
                 f'{f3(P.loc[("med_win_T3_T1", p)])} |')
    L += ['', 'Spearman of distance proxies: negative = retreat larger nearer roads / towns (more exposed).']
    L += ['', '## H3 decision (protocol rule, logistic regression, primary 2 km, built_1km)', '']
    for t in SOURCES:
        v = ver[t]
        L.append(f'- Trained on {t}: ΔAUC CI excludes 0: {"yes" if v["gap"] else "no"}; terciles monotone: '
                 f'{"yes" if v["monotone"] else "no"}; T3 - T1 CI excludes 0: {"yes" if v["trend"] else "no"} -> '
                 f'**{"supported" if v["supported"] else "not supported"}**.')
    rho = P.loc[('rho_win_p75', 'built_1km')]
    gbr = get(m, a, 'GB', 'reported', 'dauc')
    L += ['', f'**Verdict: H3 {"SUPPORTED" if ver["overall"] else "NOT SUPPORTED"}** under the protocol rule.', '',
          'Reading (descriptive, no definition changed): the reported label marks '
          f'{pr:.0%} of units, because warned-reach lists and commune-level rows label every bank of a commune (D4 note), '
          f'and it is unrelated to the satellite label (kappa {f3(k)}); no physical score can rank such a label, so '
          'AUC against reported labels sits near 0.5 whatever the model learns. Satellite retreat does not rise with '
          f'exposure: it falls (Spearman with built_1km {f3(rho)}; satellite prevalence by built_1km tercile '
          + ' / '.join(f'{P.loc[(f"prev_sat_T{q}", "built_1km"), "est"]:.2f}' for q in (1, 2, 3))
          + '), so the protocol\'s physical-check caveat (retreat rising with exposure) does not apply, but the top '
          f'tercile holds only {int(get(m, a, "LR", "reported", "auc_satellite", "built_1km T3").pos_sat)} satellite '
          'positives and its AUC(satellite) is very uncertain. Gradient boosting trained on reported labels gives '
          f'ΔAUC {f3(gbr)} (it can learn the commune pattern along river_km); its built_1km T3 - T1 is '
          f'{f3(get(m, a, "GB", "reported", "dauc_T3_T1", "built_1km"))}.',
          '',
          '## Sensitivities (logistic regression)', '', sens.to_markdown(index=False), '',
          'Columns: AUC(scores trained on source) against reported / satellite labels, ΔAUC, built_1km T3 - T1 of ΔAUC, '
          'monotone terciles, protocol verdict per training source (S = supported), kappa between the two label sources.', '',
          '## Choices and notes', '',
          '- Missing inputs: width_m, dwidth_00_14 and pre_p75 NaN are imputed by the training-fold median inside the '
          'logistic pipeline (gradient boosting uses NaN natively). Chosen before any AUC. pre_p75 is NaN for '
          f'{int(d2.pre_p75.isna().sum())} of {n} units ({int(d2[d2.channel == "hau"].pre_p75.isna().sum())} of '
          f'{int((d2.channel == "hau").sum())} Hậu main units: no 2012 composite and the 2013 Hậu composite covers ~26% of '
          'points, so the 2012-14 mean has < 2 valid years). This is a property of the frozen pre_p75 definition.',
          '- Event-only filter: (unit_type in {vụ, điểm} or source_type == decision_via_news) and source_type != '
          f'official_list_via_news: {agree["n_event"]} of 124 rows (drops the 69 warned-reach list rows incl. 5 hamlet-level '
          '"điểm" rows from those lists, 5 ODM 2018 reaches, 6 news "đoạn" rows and 1 "khu vực" row).',
          '- Commune-bank units = (channel, side, province, district, commune) (province only disambiguates; same 182 '
          'groups without it). A unit is reported-positive if it holds a bank point matched to a row by inventory_build '
          '(row units x row communes). Satellite labels and covariates by the same functions as the 2 km units.',
          '- Blocks: main channels mean chainage of the unit points / 1000, island channels (tiles.json chainage_m - '
          f'border_m[parent]) / 1000, block = river_int(km // {BLOCK_KM}) (same rule as H1/H2).',
          '- One training fold = all blocks but one; every block is tested once. Reported labels of commune-level rows '
          'cover whole communes (D4 note), so reported positives are spatially contiguous.']
    pathlib.Path('results/p2').mkdir(parents=True, exist_ok=True)
    pathlib.Path('results/p2/h3.md').write_text('\n'.join(L) + '\n', encoding='utf-8')


def sens_table(m, analyses):
    rows = []
    for name in analyses:
        v = verdict(m, name)
        for t in SOURCES:
            g = lambda s, grp='all': get(m, name, 'LR', t, s, grp)
            r = g('dauc')
            rows.append({'analysis': name, 'trained on': t, 'n': r.n, 'rep +': int(r.pos_rep), 'sat +': int(r.pos_sat),
                         'AUC rep': f3(g('auc_reported')), 'AUC sat': f3(g('auc_satellite')), 'ΔAUC': f3(r),
                         'T3-T1': f3(g('dauc_T3_T1', 'built_1km')), 'mono': 'y' if v[t]['monotone'] else 'n',
                         'verdict': 'S' if v[t]['supported'] else 'not S',
                         'kappa': f3(get(m, name, '-', '-', 'kappa'))})
    return pd.DataFrame(rows)


# ---------- figure ----------

def figure(m, d2):
    a = 'units 2km'
    fig = plt.figure(figsize=(COL2, COL2 * .4))
    gs = fig.add_gridspec(1, 3, width_ratios=[1, 1.1, 1.1], wspace=.6, left=.07, right=.985, bottom=.2)
    ax = fig.add_subplot(gs[0])
    cmap = plt.get_cmap('Blues')
    for i, t in enumerate(SOURCES):
        for j, lab in enumerate(SOURCES):
            r = get(m, a, 'LR', t, f'auc_{lab}')
            ax.add_patch(plt.Rectangle((j, 1 - i), 1, 1, color=cmap(.15 + .7 * (r.est - .5) / .5), ec='white', lw=1.5))
            col = 'white' if r.est > .75 else INK
            ax.text(j + .5, 1.58 - i, f'{r.est:.2f}', ha='center', va='center', fontsize=10, color=col, fontweight='bold')
            ax.text(j + .5, 1.3 - i, f'{r.lo:.2f}–{r.hi:.2f}', ha='center', va='center', fontsize=7, color=col)
    ax.set_xlim(0, 2)
    ax.set_ylim(0, 2)
    ax.set_xticks([.5, 1.5], ['Reported', 'Satellite'])
    ax.set_yticks([1.5, .5], ['Reported', 'Satellite'])
    ax.set_xlabel('Scored against')
    ax.set_ylabel('Trained on')
    ax.tick_params(length=0)
    ax.spines[:].set_visible(False)
    ax.set_aspect('equal')
    ax.set_title('(a) AUC, block CV', loc='left', pad=3, fontweight='bold')

    ax = fig.add_subplot(gs[1])
    for k, (t, col, mk) in enumerate((('reported', BLUE, 'o'), ('satellite', ORANGE, 's'))):
        rs = [get(m, a, 'LR', t, 'dauc', f'built_1km T{q}') for q in (1, 2, 3)]
        x = np.arange(3) + (k - .5) * .2
        ax.errorbar(x, [r.est for r in rs], yerr=[[r.est - r.lo for r in rs], [r.hi - r.est for r in rs]], fmt=mk,
                    color=col, ms=4, lw=1, capsize=2, label=f'trained on {t}')
    ax.axhline(0, color=INK2, lw=.6)
    ax.set_xticks(range(3), ['T1\nlow', 'T2', 'T3\nhigh'])
    ax.set_xlabel('Built-up 0–1 km tercile')
    ax.set_ylabel('ΔAUC (rep. − sat.)')
    ax.set_ylim(-.75, 1.0)
    chart_axes(ax)
    ax.legend(loc='upper left', handletextpad=.2, fontsize=7)
    ax.set_title('(b) Gap by exposure', loc='left', pad=3, fontweight='bold')

    ax = fig.add_subplot(gs[2])
    for g, col, mk in (('Tiền main', BLUE, 'o'), ('Hậu main', ORANGE, 's'), ('island channels', AQUA, '^')):
        x = d2[d2.group == g]
        ax.plot(x.built_1km, x.win_p75.clip(-40, 150), mk, ms=2.6, mfc=col, mec='white', mew=.3, alpha=.85,
                label={'Tiền main': 'Tien main', 'Hậu main': 'Hau main', 'island channels': 'islands'}[g])
    ax.axhline(20, color=INK, lw=.8, ls=(0, (4, 2)))
    rho = spearmanr(d2.built_1km, d2.win_p75)[0]
    ax.text(.98, .6, f'Spearman ρ = {rho:+.2f}', transform=ax.transAxes, ha='right', va='top', fontsize=7)
    ax.set_xlabel('Built-up share 0–1 km (%)')
    ax.set_ylabel('Retreat 2013–15 to 2022–24, unit p75 (m)')
    chart_axes(ax)
    ax.legend(loc='upper right', handletextpad=.1, fontsize=7, markerscale=1.6)   # empty corner: built-up banks barely move
    ax.set_title('(c) Physical check', loc='left', pad=3, fontweight='bold')
    save(fig, 'fig08_label_source')


# ---------- main ----------

def main():
    t0 = time.time()
    u, pc, cfg = point_tables()
    inv = inventory()
    d = {c: unit_table(c, u, pc, cfg, inv) for c in ('unit_2km', 'unit_5km', 'unit_cb')}
    # sanity: summarise / per_unit reproduce the written 2 km tables; inventory rows map to their recorded points
    s2 = sl.summarise(u, 'unit_2km').set_index('unit')
    ref = pd.read_csv('data/processed/sat_labels_2km.csv').set_index('unit')
    assert (s2.lab_p75_20.fillna(-1) == ref.loc[s2.index, 'lab_p75_20'].fillna(-1)).all()
    npts = [int(row_points(u, r).sum()) for _, r in inv.iterrows()]
    assert npts == inv.n_bank_points.astype(int).tolist(), 'inventory rows do not map to their bank points'

    runs = [('units 2km', d['unit_2km'], 'rep', 'lab_p75_20', dict(models=('LR', 'GB'), proxies=PROXIES)),
            ('units 5km', d['unit_5km'], 'rep', 'lab_p75_20', {}),
            ('commune-bank', d['unit_cb'], 'rep', 'lab_p75_20', {}),
            ('event-only reported', d['unit_2km'], 'rep_event', 'lab_p75_20', {})]
    runs += [(f'sat {v[4:]}', d['unit_2km'], 'rep', v, {}) for v in SAT_VARIANTS]
    ms, units = [], []
    for name, dd, rep, sat, kw in runs:
        m, scores, used = analyse(name, dd, rep, sat, **kw)
        ms.append(m)
        if rep == 'rep' and sat == 'lab_p75_20':
            for (model, train), s in scores.items():
                used[f'score_{model}_{train}'] = s
            units.append(used.assign(level=name))
        print(f'{name}: n {len(used)}, done {time.time() - t0:.0f} s', flush=True)
    phys = physical(d['unit_2km'])
    m = pd.concat(ms + [phys], ignore_index=True)
    m.round(4).to_csv('data/processed/h3_metrics.csv', index=False, encoding='utf-8')
    keep = ['level', 'unit', 'river', 'channel', 'side', 'group', 'block', 'n_win', 'win_p75', 'rep', 'rep_event',
            'lab_p75_20'] + SAT_VARIANTS + FEATURES + PROXIES + [f't_{p}' for p in PROXIES]
    out = pd.concat(units, ignore_index=True)
    out[keep + [c for c in out if c.startswith('score_')]].round(4).to_csv('data/processed/h3_units.csv', index=False,
                                                                           encoding='utf-8')
    ver = verdict(m, 'units 2km')
    sens = sens_table(m, [r[0] for r in runs])
    report(m, phys, d['unit_2km'], ver, sens, {'n_event': int(inv.event.sum())}, time.time() - t0)
    figure(m, d['unit_2km'])
    print(sens.to_string(index=False))
    print('verdict', ver)


if __name__ == '__main__':
    main()
