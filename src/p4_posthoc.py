"""P4 post hoc analyses after internal review round 1 (plan: docs/p4_posthoc_plan.md, committed before running).

Usage:
  python src/p4_posthoc.py run             PH1-PH3 -> results/p4/posthoc.md (refits the GBT on training rows, ~2 min)
  python src/p4_posthoc.py rater2-sample   PH4: 20 click items -> data/processed/rater2_clicks/ (review_server.py)
  python src/p4_posthoc.py agree           PH4: agreement of the two raters -> results/p4/rater2.md
PH1 locally adaptive conformal (Mondrian by past rate; normalised scores), PH2 non-conformal comparators,
PH3 independence null for omission / commission, PH4 second rater. Post hoc: no protocol verdict depends on them.
"""
import csv
import json
import pathlib
import sys

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from sklearn.metrics import cohen_kappa_score
from sklearn.model_selection import GroupKFold

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import forecast as fc  # noqa: E402
from figures import clicks  # noqa: E402
from p4_review_checks import RATE_BINS, RATE_LABELS, boot  # noqa: E402

OUT = pathlib.Path('results/p4')
PARAMS = {3: dict(learning_rate=.05, max_leaf_nodes=31, min_samples_leaf=100),   # GBT point params, results/p2/forecast.md
          5: dict(learning_rate=.05, max_leaf_nodes=15, min_samples_leaf=100)}
PH1_BINS, PH1_LABELS = [0, 2, 5, 10, np.inf], ['< 2', '2-5', '5-10', '>= 10']
R2 = pathlib.Path('data/processed/rater2_clicks')
R2_N = {'Tien main': ([('sadec_caolanh', None), ('mythuan', None), ('tien', None)], 8),
        'Hau wide': ([('longxuyen', None), ('hau', False)], 4), 'Hau narrow': ([('hau', True)], 4),
        'Island': ([('islands', None)], 4)}


# ---------- PH1, PH2 ----------

def fit(df, h):
    """GBT refitted with the stored params: predictions for all rows and out-of-fold residuals of the training rows."""
    tr = (df.split == 'train').to_numpy()
    X, y, g = df[fc.FEAT].to_numpy(float), df.y.to_numpy(), df.block.to_numpy()
    Xt, yt = X[tr], y[tr]
    folds = list(GroupKFold(5).split(Xt, yt, g[tr]))
    res = Parallel(n_jobs=-1)(delayed(fc._gbt_fold)(Xt, yt, a, b, PARAMS[h], 'absolute_error', None) for a, b in folds)
    oof = np.empty(len(yt))
    for (_, b), p in zip(folds, res):
        oof[b] = p
    pred = fc.gbt(PARAMS[h], 'absolute_error').fit(Xt, yt).predict(X)
    r = np.abs(yt - oof)
    sigma = np.maximum(fc.gbt(PARAMS[h], 'absolute_error').fit(Xt, r).predict(X), 1.0)
    return pred, yt - oof, sigma


def metrics(d, lo, hi, name):
    d = d.assign(cov=d.y.between(lo, hi).astype(int), w=hi - lo,
                 wink=(hi - lo) + 20 * np.maximum(lo - d.y, 0) + 20 * np.maximum(d.y - hi, 0))
    rc = pd.cut(d.rate10.abs(), RATE_BINS, labels=RATE_LABELS, right=False)
    by_rate = {k: x for k, x in d.groupby(rc, observed=True)}
    rate_cov = {k: 100 * x['cov'].mean() for k, x in by_rate.items()}
    met = 87 <= 100 * d['cov'].mean() <= 93 and all(85 <= v <= 95 for v in rate_cov.values())
    row = (f'| {name} | {boot(d, "cov")} | {d.w.mean():.1f} | {d.wink.mean():.1f} | '
           + ' | '.join(boot(by_rate[k], 'cov') for k in RATE_LABELS) + f' | {"yes" if met else "no"} |')
    grp = f'| {name} | ' + ' | '.join(boot(x, 'cov') for _, x in d.groupby('group')) + ' |'
    return row, grp


def ph12(h, u, W, D):
    df, _ = fc.build(u, W, D, h, 'mean')
    pred, oofres, sigma = fit(df, h)
    df['p'], df['sigma'] = pred, sigma
    stored = pd.read_csv(f'data/processed/forecast_h{h}_mean.csv', usecols=['channel', 'transect', 'side', 'origin', 'split', 'p_gbt'])
    chk = df.merge(stored, on=['channel', 'transect', 'side', 'origin', 'split'])
    dmax = float(np.abs(chk.p - chk.p_gbt).max())
    if len(chk) != (df.split != 'train').sum() or dmax >= .01:
        sys.exit(f'h={h}: refit does not reproduce the stored GBT forecasts ({len(chk)} rows, max diff {dmax:.4f} m)')
    cal, test = df[df.split == 'cal'], df[df.split == 'test'].copy()
    s = np.abs(cal.y - cal.p).to_numpy()
    p = test.p.to_numpy()
    q = fc.cq(s, fc.ALPHA)
    cls = lambda d: pd.cut(d.rate10.abs().fillna(0), PH1_BINS, labels=PH1_LABELS, right=False)  # noqa: E731
    qc = {k: fc.cq(s[(cls(cal) == k).to_numpy()], fc.ALPHA) for k in PH1_LABELS}
    half_m = cls(test).map(qc).astype(float).to_numpy()
    qn = fc.cq(s / cal.sigma.to_numpy(), fc.ALPHA)
    half_n = qn * test.sigma.to_numpy()
    mad = 1.4826 * np.median(np.abs(oofres - np.median(oofres)))
    q05, q95 = np.quantile(oofres, [.05, .95])
    variants = [('Split conformal (H2)', p - q, p + q), ('PH1a Mondrian by past rate', p - half_m, p + half_m),
                ('PH1b normalised scores', p - half_n, p + half_n),
                ('PH2a Gaussian, robust scale', p - fc.Z * mad, p + fc.Z * mad),
                ('PH2b empirical OOF 5-95%', p + q05, p + q95)]
    rows = [metrics(test, lo, hi, n) for n, lo, hi in variants]
    groups = sorted(test.group.unique())
    L = [f'## h = {h} yr', '',
         f'Refit check: {len(chk)} calibration and test rows, max |refit - stored GBT forecast| {dmax:.4f} m. '
         f'Split q-hat {q:.1f} m; PH1a q-hat by class ' + ', '.join(f'{k} m/yr {v:.1f} m' for k, v in qc.items())
         + f' (calibration rows per class: ' + ', '.join(f'{k} {(cls(cal) == k).sum()}' for k in PH1_LABELS)
         + f'); PH1b q-hat {qn:.2f} x sigma (sigma median {np.median(test.sigma):.1f} m, 90th pct '
         f'{np.quantile(test.sigma, .9):.1f} m); PH2a half-width {fc.Z * mad:.1f} m; PH2b [{q05:.1f}, {q95:.1f}] m.', '',
         '| method | coverage (%) | mean width (m) | Winkler (m) | ' + ' | '.join(f'rate {k} m/yr' for k in RATE_LABELS)
         + ' | rate-conditional criterion |', '|' + '---|' * 10]
    L += [r for r, _ in rows] + ['', '| method | ' + ' | '.join(groups) + ' |', '|' + '---|' * (len(groups) + 1)]
    L += [g for _, g in rows] + ['']
    return L


# ---------- PH3 ----------

def ph3(n=10000, seed=0):
    d = pd.read_csv('data/processed/explore_reporting_units.csv')
    rep, sat, below = d['r_any report'].to_numpy(), d.lab_p75_20.to_numpy(), (d.win_p75 < 9.3).to_numpy()
    rng = np.random.default_rng(seed)
    perm = np.tile(rep, (n, 1))
    for g in d.group.unique():
        idx = np.where(d.group.to_numpy() == g)[0]
        perm[:, idx] = rng.permuted(perm[:, idx], axis=1)

    def stats(r):
        r = np.atleast_2d(r)
        om = (r[:, sat == 1] == 0).mean(1)
        com = (r * below).sum(1) / r.sum(1)
        gap = com - ((1 - r) * below).sum(1) / (1 - r).sum(1)
        return {'omission': om, 'commission': com, 'commission gap': gap}

    obs, null = stats(rep), stats(perm)
    L = ['## PH3: independence null for omission and commission', '',
         f'{len(d)} units; reported labels permuted within channel group ({n} permutations, seed 0).', '',
         '| statistic | observed (%) | null median (%) | null 95% range (%) | permutation p | consistent with independence |',
         '|---|---|---|---|---|---|']
    for k in obs:
        o, z = float(obs[k][0]), null[k]
        p = min(1.0, 2 * min((z <= o).mean(), (z >= o).mean()))
        lo, md, hi = np.percentile(z, [2.5, 50, 97.5])
        L.append(f'| {k} | {100 * o:.1f} | {100 * md:.1f} | [{100 * lo:.1f}, {100 * hi:.1f}] | {p:.2f} | '
                 f'{"yes" if lo <= o <= hi else "no"} |')
    return L + ['']


def run():
    u, W, _ = fc.load()
    D = fc.centred(W)
    L = ['# P4 post hoc analyses (internal review round 1)', '',
         'Generated by `python src/p4_posthoc.py run`. Plan and criteria: `docs/p4_posthoc_plan.md` (committed before running). '
         'Post hoc: no protocol verdict depends on these results. Test targets 2019-2024, calibration targets 2016-2018, '
         'GBT point forecasts refitted with the stored hyperparameters. CIs: 95% block bootstrap over 10 km blocks. '
         'Rate classes: |Theil-Sen rate over the 10 years before the origin|. Criterion (PH1): pooled coverage in 90 +- 3% and '
         'every rate class in 85-95%.', '']
    for h in (3, 5):
        L += ph12(h, u, W, D)
        print(f'h = {h} done', flush=True)
    L += ph3()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'posthoc.md').write_text('\n'.join(L), encoding='utf-8')
    print('\n'.join(L))


# ---------- PH4 ----------

def rater2_sample():
    rng = np.random.default_rng(0)
    items, key = [], []
    for grp, (reaches, n) in R2_N.items():
        c = pd.concat([clicks(*r).assign(reach=r[0], narrow=r[1]) for r in reaches], ignore_index=True)
        for r in c.iloc[np.sort(rng.choice(len(c), n, replace=False))].itertuples():
            src = json.loads(pathlib.Path('data/processed', r.reach, 'review_points.json').read_text())['items']
            it = dict(next(i for i in src if i['id'] == r.id))
            key.append({'id': f'R{len(key) + 1:02d}', 'group': grp, 'reach': r.reach, 'item': r.id})
            it.update(id=key[-1]['id'], explore=False)
            items.append(it)
    order = rng.permutation(len(items))
    R2.mkdir(parents=True, exist_ok=True)
    (R2 / 'review_points.json').write_text(json.dumps({'reach': 'rater2_clicks', 'items': [items[i] for i in order]}),
                                           encoding='utf-8')
    pd.DataFrame(key).to_csv(R2 / 'key.csv', index=False)
    print(pd.DataFrame(key).group.value_counts().to_string(), f'\n{len(items)} items -> {R2}')


def last(path):
    with open(path, newline='', encoding='utf-8-sig') as f:
        return pd.DataFrame({r['id']: r for r in csv.DictReader(f)}.values())


def agree():
    vc = pathlib.Path('data/processed/visual_check')
    L = ['# PH4: second rater (post hoc, docs/p4_posthoc_plan.md)', '',
         'Generated by `python src/p4_posthoc.py agree`. The second rater worked blind to the group and to the first '
         "rater's answers.", '']
    if (vc / 'answers_rater2.csv').exists():
        a = last(vc / 'answers.csv').merge(last(vc / 'answers_rater2.csv'), on='id', suffixes=('_1', '_2'))
        L += ['## Visual check', '', '| question | units judged by both | agreement | Cohen kappa |', '|---|---|---|---|']
        for q, pos in (('q1_loss', {'clear'}), ('q2_protection', {'yes', 'partly'})):
            b = a[(a[f'{q}_1'] != 'cannot_tell') & (a[f'{q}_2'] != 'cannot_tell')]
            x, y = b[f'{q}_1'].isin(pos), b[f'{q}_2'].isin(pos)
            k = cohen_kappa_score(x, y) if x.nunique() + y.nunique() > 2 else float('nan')
            L.append(f'| {q} ({"/".join(sorted(pos))} vs not) | {len(b)} | {100 * (x == y).mean():.0f}% | {k:.2f} |')
        key = pd.read_csv(vc / 'key.csv')[['id', 'group']]
        a = a.merge(key, on='id')
        L += ['', f'Rater 2 answered {len(a)} of 60 units.', '',
              '| group (plan C) | rater 1 clear loss | rater 2 clear loss |', '|---|---|---|']
        for g, x in a.groupby('group'):
            c = [f'{(x[q] == "clear").sum()}/{(x[q] != "cannot_tell").sum()}' for q in ('q1_loss_1', 'q1_loss_2')]
            L.append(f'| {g} | {c[0]} | {c[1]} |')
        for r, f in (('rater 1', 'answers.csv'), ('rater 2', 'answers_rater2.csv')):
            t = pd.to_datetime(last(vc / f).timestamp).sort_values()
            L.append(f'\n{r}: answers from {t.min():%H:%M} to {t.max():%H:%M} ({(t.max() - t.min()).total_seconds() / 60:.0f} '
                     f'min; median {t.diff().dt.total_seconds().median():.0f} s between answers).')
        L += ['']
    if (R2 / 'accuracy_review.csv').exists():
        key = pd.read_csv(R2 / 'key.csv')
        r2 = last(R2 / 'accuracy_review.csv').merge(key, on='id')
        r2 = r2[r2.verdict == 'clicked']
        r1 = pd.concat([clicks(*r).assign(reach=r[0]) for grp in R2_N.values() for r in grp[0]]).drop_duplicates(['reach', 'id'])
        p = r2.merge(r1, left_on=['reach', 'item'], right_on=['reach', 'id'], suffixes=('_2', '_1'))
        p = p[p.imagery_capture_date_2 == p.imagery_capture_date_1]
        d12 = p.user_dist_m_2.astype(float) - p.user_dist_m_1.astype(float)
        e1, e2 = p.dist_m - p.user_dist_m_1.astype(float), p.dist_m - p.user_dist_m_2.astype(float)
        rm = lambda e: np.sqrt((e ** 2).mean())  # noqa: E731
        L += ['## Accuracy clicks', '',
              f'{len(r2)} of 20 items clicked by rater 2; {len(p)} pairs on the same imagery capture date.', '',
              f'- Between raters: RMSE {rm(d12):.0f} m, median |difference| {d12.abs().median():.0f} m.',
              f'- Landsat bank vs rater 1: RMSE {rm(e1):.0f} m; vs rater 2: RMSE {rm(e2):.0f} m (same pairs).', '']
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'rater2.md').write_text('\n'.join(L), encoding='utf-8')
    print('\n'.join(L))


if __name__ == '__main__':
    {'run': run, 'rater2-sample': rater2_sample, 'agree': agree}[sys.argv[1]]()
