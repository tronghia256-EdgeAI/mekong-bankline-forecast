"""P2: transect forecasts of bank retreat with 90% intervals (H1, H2), exactly per docs/protocol.md section 2 + deviation 1.

Usage: python src/forecast.py          (all: h = 3 and 5, 3-yr mean and raw annual target, spatial leave-block-out)
       python src/forecast.py fig      (only redraw figures/fig07_coverage from the written CSVs)
Reads data/processed/units.csv, {tien,hau,islands}/{bank_positions,trends}.csv (via sat_labels.points/positions),
covariates_2km.csv, data/tiles.json; channel width 2000-02 per transect via covariates.widths.
Writes:
  data/processed/forecast_h{3,5}_{mean,raw}.csv  calibration and test rows: key, origin, target year, split, group,
      block, y (retreat d(t+h) - d(t), m, + = landward), point forecasts p_<model>, intervals lo/hi_<model>_<method>
  data/processed/forecast_lbo_h{3,5}.csv          the same for the spatial leave-one-block-out test rows
  results/p2/forecast.md                           all tables (metrics with 95% block-bootstrap CIs, H1/H2 verdicts)
  figures/fig07_coverage.png + .svg
Design (protocol section 2):
  unit = in-scope transect-side with >= 15 valid years 2000-2024; origin t used if >= 8 valid years in 2000..t (dev. 1).
  d(t) = 3-yr centred mean (mean of the available years, >= 2); enters the target only. Inputs use years <= t only.
  Split by target year t + h: train <= 2015, calibration 2016-2018, test 2019-2024 (scored once, never used to choose).
  Baselines: persistence; EPR and Theil-Sen LRR over all years <= t and the last 10 years (rate x h; a baseline that
  cannot be computed falls back to persistence). Learned: HistGradientBoosting (absolute error; quantile 0.05 / 0.95
  for CQR) and a Gaussian process (ARD kernel on a random subsample of GP_N training rows) on lagged positions
  (x(t-k) minus the trailing 3-yr mean, k = 0..5), Theil-Sen rates over 3/5/10-yr windows and physical covariates
  COV. Hyperparameters by 5-fold spatial-block grouped CV inside the training rows.
  Intervals (90%): Gaussian (SD of the out-of-fold training residuals; baselines: training residuals), split
  conformal, Mondrian conformal by group, ACI over forecast origins (pooled miscoverage per origin, delayed feedback:
  the error of origin s is used from origin s + h on; step GAMMA fixed a priori, GAMMA_SENS as a sensitivity), CQR.
"""
import json
import pathlib
import sys
import time
import warnings

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, Matern, WhiteKernel
from sklearn.model_selection import GroupKFold

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from figures import AQUA, BLUE, COL2, GRID, INK, INK2, ORANGE, YELLOW, chart_axes, plt, save  # noqa: E402
from sat_labels import points, positions  # noqa: E402

YEARS = np.arange(2000, 2025)
MIN_SERIES, MIN_ORIGIN = 15, 8          # valid years: per series over 2000-2024; per origin in 2000..t (deviation 1)
TRAIN_END, CAL = 2015, (2016, 2018)     # target years; test = 2019-2024
ALPHA, Z = .1, 1.6449
GAMMA, GAMMA_SENS = .005, .05           # ACI step (Gibbs & Candes 2021 default), sensitivity; both fixed a priori
GP_N = 1000                             # GP training subsample (O(n^3); n = 2000 took > 20 min per CV fit on this CPU)
NB, SEED = 1000, 0
COV = ['curv_bank', 'width_00', 'is_island', 'river_km', 'node_km']
FEAT = [f'lag{k}' for k in range(6)] + ['rate3', 'rate5', 'rate10'] + COV
BASE = ['persistence', 'epr_all', 'epr_10', 'lrr_all', 'lrr_10']
LEARN = ['gbt', 'gp']
MODELS = BASE + LEARN
METHODS = ['gauss', 'split', 'mondrian', 'aci', 'aci_sens']
GROUPS = ['Tien main', 'Hau wide', 'Hau narrow', 'Island']
GRID_GBT = [dict(learning_rate=lr, max_leaf_nodes=ln, min_samples_leaf=ms)
            for lr in (.05, .1) for ln in (15, 31) for ms in (20, 100)]
ZONE_KM = 10.0                          # change-period zones: within 10 km of Vam Nao / of the Tien reach end (My Thuan)
OUT = pathlib.Path('results/p2')
LABEL = {'gauss': 'Gaussian', 'split': 'Split conformal', 'mondrian': 'Mondrian', 'aci': 'ACI',
         'aci_sens': f'ACI (γ = {GAMMA_SENS})', 'cqr': 'CQR'}


# ---------- data ----------

def load():
    """In-scope points with group, 10 km block, covariates, kind; wide annual positions W (n x 25)."""
    cfg = json.loads(pathlib.Path('data/tiles.json').read_text())
    u = points()
    W = positions(u).to_numpy()
    cov = pd.read_csv('data/processed/covariates_2km.csv').set_index('unit')
    for c in ['curv_bank', 'is_island', 'river_km', 'node_km', 'vamnao_km']:
        u[c] = u.unit_2km.map(cov[c]).to_numpy()
    u['width_00'] = width00(u, cfg)
    narrow = cfg['narrow_until_m']['hau'] - cfg['border_m']['hau']      # stitch.py: s < narrow_until_m (raw chainage)
    isl = u.channel.str.startswith('isl_')
    u['group'] = np.select([u.channel == 'tien', (u.channel == 'hau') & (u.chainage_m < narrow), u.channel == 'hau'],
                           GROUPS[:3], GROUPS[3])
    ikm = u.channel.map({k: (v['chainage_m'] - cfg['border_m'][v['parent']]) / 1e3 for k, v in cfg['islands'].items()})
    u['km'] = np.where(isl, ikm, u.chainage_m / 1e3)
    u['block'] = u.river + '_' + (u.km // 10).astype(int).astype(str)
    tien_end = u.loc[u.channel == 'tien', 'km'].max()
    u['zone_vamnao'] = u.vamnao_km.abs() <= ZONE_KM
    u['zone_mythuan'] = (u.river == 'tien') & (u.km >= tien_end - ZONE_KM)
    return u, W, narrow


def width00(u, cfg):
    """Unit median of the 2000-02 channel width (covariates.widths w00): a width covariate from years <= every origin
    (width_m and dwidth_00_14 use 2000-2014 and so contain years after the training origins)."""
    from covariates import widths
    from shapely.geometry import Polygon
    isl = [Polygon(v['polygon']) for v in cfg['islands'].values()]
    w = pd.concat([widths(ch, isl)[['transect', 'w00']].assign(channel=ch) for ch in u.channel.unique()])
    m = u[['channel', 'transect', 'unit_2km']].merge(w, on=['channel', 'transect'], how='left')
    return m.groupby('unit_2km').w00.transform('median').to_numpy()


def centred(W):
    """3-yr centred mean position; mean of the available years, NaN unless >= 2."""
    P = np.pad(W, ((0, 0), (1, 1)), constant_values=np.nan)
    S = np.stack([P[:, :-2], P[:, 1:-1], P[:, 2:]])
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return np.where(np.isfinite(S).sum(0) >= 2, np.nanmean(S, 0), np.nan)


def ts_slope(Y, yrs, min_n):
    """Theil-Sen slope per row over the valid values (NaN unless >= min_n valid)."""
    i, j = np.triu_indices(len(yrs), 1)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        s = np.nanmedian((Y[:, j] - Y[:, i]) / (yrs[j] - yrs[i]), 1)
    return np.where(np.isfinite(Y).sum(1) >= min_n, s, np.nan)


def epr(Y, yrs):
    """End-point rate between the first and last valid values per row (NaN unless >= 2 valid)."""
    v = np.isfinite(Y)
    f, l = v.argmax(1), Y.shape[1] - 1 - v[:, ::-1].argmax(1)
    r = np.arange(len(Y))
    with np.errstate(invalid='ignore', divide='ignore'):
        out = (Y[r, l] - Y[r, f]) / (yrs[l] - yrs[f])
    return np.where(v.sum(1) >= 2, out, np.nan)


def build(u, W, D, h, target):
    """One row per (included transect-side, usable origin) with target, features and baseline forecasts."""
    ok_series = np.isfinite(W).sum(1) >= MIN_SERIES
    cum = np.isfinite(W).cumsum(1)
    parts = []
    for k in range(len(YEARS) - h):
        t, y = YEARS[k], (D[:, k + h] - D[:, k]) if target == 'mean' else (W[:, k + h] - W[:, k])
        idx = np.where(ok_series & (cum[:, k] >= MIN_ORIGIN) & np.isfinite(y))[0]
        if not len(idx):
            continue
        Y, yr = W[idx, :k + 1], YEARS[:k + 1]
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            ref = np.nanmean(Y[:, -3:], 1)
        f = {'i': idx, 'origin': t, 'target_year': t + h, 'y': y[idx]}
        for L in range(6):
            f[f'lag{L}'] = Y[:, k - L] - ref
        for w, mn in ((3, 2), (5, 3), (10, 5)):
            f[f'rate{w}'] = ts_slope(Y[:, -w:], yr[-w:], mn)
        f['p_persistence'] = 0.0
        f['p_epr_all'], f['p_epr_10'] = h * epr(Y, yr), h * epr(Y[:, -10:], yr[-10:])
        f['p_lrr_all'], f['p_lrr_10'] = h * ts_slope(Y, yr, 2), h * ts_slope(Y[:, -10:], yr[-10:], 3)
        parts.append(pd.DataFrame(f))
    df = pd.concat(parts, ignore_index=True)
    keep = ['channel', 'transect', 'side', 'river', 'group', 'block', 'km', 'kind', 'zone_vamnao', 'zone_mythuan'] + COV
    df = pd.concat([u.iloc[df.i][keep].reset_index(drop=True), df], axis=1)
    df['split'] = np.select([df.target_year <= TRAIN_END, df.target_year <= CAL[1]], ['train', 'cal'], 'test')
    fb = {m: int(df[f'p_{m}'].isna().sum()) for m in BASE}
    for m in BASE:
        df[f'p_{m}'] = df[f'p_{m}'].fillna(0.0)
    return df, fb


# ---------- models ----------

def gbt(params, loss, q=None):
    kw = dict(quantile=q) if loss == 'quantile' else {}
    return HistGradientBoostingRegressor(loss=loss, max_iter=300, early_stopping=False, random_state=SEED,
                                         **params, **kw)


def pinball(y, p, q):
    d = y - p
    return np.mean(np.maximum(q * d, (q - 1) * d)) if q is not None else np.mean(np.abs(d))


def _gbt_fold(X, y, tr, te, p, loss, q):
    return gbt(p, loss, q).fit(X[tr], y[tr]).predict(X[te])


def tune_gbt(X, y, g, loss, q=None):
    """Grid over GRID_GBT by 5-fold spatial-block CV (training rows only); best params and their OOF predictions."""
    folds = list(GroupKFold(5).split(X, y, g))
    res = Parallel(n_jobs=-1)(delayed(_gbt_fold)(X, y, tr, te, p, loss, q) for p in GRID_GBT for tr, te in folds)
    oofs, scores = [], []
    for a in range(len(GRID_GBT)):
        oof = np.empty(len(y))
        for (tr, te), pr in zip(folds, res[a * 5:(a + 1) * 5]):
            oof[te] = pr
        oofs.append(oof)
        scores.append(pinball(y, oof, q))
    b = int(np.argmin(scores))
    return GRID_GBT[b], oofs[b], scores


def gp_scaler(X):
    med = np.nanmedian(X, 0)
    Xf = np.where(np.isnan(X), med, X)
    mu, sd = Xf.mean(0), Xf.std(0) + 1e-9
    return lambda A: (np.where(np.isnan(A), med, A) - mu) / sd


def gp_kernels(p):
    return {'rbf': ConstantKernel() * RBF(np.ones(p)) + WhiteKernel(),
            'matern15': ConstantKernel() * Matern(np.ones(p), nu=1.5) + WhiteKernel()}


def gp_fit(X, y, kernel, seed, optimize=True):
    sub = np.random.default_rng(seed).choice(len(y), min(GP_N, len(y)), replace=False)
    m = GaussianProcessRegressor(kernel, normalize_y=True, optimizer='fmin_l_bfgs_b' if optimize else None,
                                 random_state=SEED)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return m.fit(X[sub], y[sub])


def _gp_fold(X, y, tr, te, kernel, seed):
    return gp_fit(X[tr], y[tr], kernel, seed).predict(X[te])


def tune_gp(X, y, g):
    """Kernel choice (RBF vs Matern 1.5, both ARD + white noise) by 5-fold spatial-block CV MAE; kernel
    hyperparameters by marginal likelihood on the subsample."""
    folds = list(GroupKFold(5).split(X, y, g))
    ks = gp_kernels(X.shape[1])
    res = Parallel(n_jobs=-1)(delayed(_gp_fold)(X, y, tr, te, k, SEED + f)
                              for k in ks.values() for f, (tr, te) in enumerate(folds))
    oofs, scores = {}, {}
    for a, name in enumerate(ks):
        oof = np.empty(len(y))
        for (tr, te), pr in zip(folds, res[a * 5:(a + 1) * 5]):
            oof[te] = pr
        oofs[name], scores[name] = oof, float(np.mean(np.abs(y - oof)))
    best = min(scores, key=scores.get)
    return best, ks[best], oofs[best], scores


# ---------- intervals ----------

def cq(s, alpha):
    """Split-conformal quantile: the ceil((n+1)(1-alpha))-th smallest score (inf if beyond n)."""
    n = len(s)
    lev = np.ceil((n + 1) * (1 - alpha)) / n
    return np.inf if lev > 1 or n == 0 else float(np.quantile(s, max(lev, 0), method='higher'))


def aci_half(pred, y, origin, s, h, gamma):
    """ACI over origins with delayed feedback: the pooled miscoverage of origin o is known at o + h and moves alpha
    from then on: alpha <- alpha + gamma (ALPHA - err). Returns the half-width per row and the alpha path."""
    half, err, a, path = np.empty(len(y)), {}, ALPHA, {}
    for t in np.sort(np.unique(origin)):
        if t - h in err:
            a += gamma * (ALPHA - err[t - h])
        path[int(t)] = a
        m = origin == t
        half[m] = cq(s, a)
        err[t] = float(np.mean(np.abs(y[m] - pred[m]) > half[m]))
    return half, path


def intervals(cal, test, sd, h):
    """lo/hi columns for every point model x method on the test rows (+ CQR on the GBT quantiles)."""
    out, paths = {}, {}
    yt, ot = test.y.to_numpy(), test.origin.to_numpy()
    for m in MODELS:
        pt = test[f'p_{m}'].to_numpy()
        s = np.abs(cal.y.to_numpy() - cal[f'p_{m}'].to_numpy())
        half = {'gauss': np.full(len(test), Z * sd[m]), 'split': np.full(len(test), cq(s, ALPHA)),
                'mondrian': test.group.map({g: cq(s[(cal.group == g).to_numpy()], ALPHA) for g in GROUPS}).to_numpy()}
        half['aci'], paths[m] = aci_half(pt, yt, ot, s, h, GAMMA)
        half['aci_sens'], _ = aci_half(pt, yt, ot, s, h, GAMMA_SENS)
        for k in METHODS:
            out[f'lo_{m}_{k}'], out[f'hi_{m}_{k}'] = pt - half[k], pt + half[k]
    e = np.maximum(cal.q05 - cal.y, cal.y - cal.q95).to_numpy()
    Q = cq(e, ALPHA)
    out['lo_gbt_cqr'], out['hi_gbt_cqr'] = test.q05.to_numpy() - Q, test.q95.to_numpy() + Q
    return pd.DataFrame(out, index=test.index), paths


def resid_sd(df, mask):
    """Gaussian-interval SD per model: OOF residuals (learned) / residuals (baselines) on the given training rows."""
    t = df[mask]
    return {m: float(np.std(t.y - t[f'oof_{m}' if m in LEARN else f'p_{m}'], ddof=1)) for m in MODELS}


# ---------- one configuration ----------

def run(u, W, D, h, target):
    df, fb = build(u, W, D, h, target)
    tr = (df.split == 'train').to_numpy()
    X, y, g = df[FEAT].to_numpy(float), df.y.to_numpy(), df.block.to_numpy()
    info = {'h': h, 'target': target, 'fallback': fb, 'n': df.split.value_counts().to_dict(),
            'n_series': df.groupby(['channel', 'transect', 'side']).ngroups,
            'origins': {s: (int(d.origin.min()), int(d.origin.max())) for s, d in df.groupby('split')}}
    for name, loss, q in (('gbt', 'absolute_error', None), ('q05', 'quantile', .05), ('q95', 'quantile', .95)):
        p, oof, sc = tune_gbt(X[tr], y[tr], g[tr], loss, q)
        info[f'params_{name}'], info[f'cv_{name}'] = p, sc
        df[f'p_{name}' if name == 'gbt' else name] = gbt(p, loss, q).fit(X[tr], y[tr]).predict(X)
        if name == 'gbt':
            df.loc[tr, 'oof_gbt'] = oof
    lo, hi = np.minimum(df.q05, df.q95), np.maximum(df.q05, df.q95)
    df['q05'], df['q95'] = lo, hi
    scale = gp_scaler(X[tr])
    kname, kern, oof, sc = tune_gp(scale(X[tr]), y[tr], g[tr])
    gp = gp_fit(scale(X[tr]), y[tr], kern, SEED)
    df['p_gp'] = gp.predict(scale(X))
    df.loc[tr, 'oof_gp'] = oof
    info.update(gp_kernel=kname, gp_cv=sc, gp_fitted=str(gp.kernel_), gp_n=min(GP_N, int(tr.sum())))
    info['sd'] = resid_sd(df, tr)
    cal, test = df[df.split == 'cal'], df[df.split == 'test']
    iv, info['aci_path'] = intervals(cal, test, info['sd'], h)
    ivc, _ = intervals(cal, cal, info['sd'], h)           # calibration rows (in-sample check, split ~90% by design)
    out = pd.concat([pd.concat([test, iv], axis=1), pd.concat([cal, ivc], axis=1)])
    return df, out, info, (scale, gp.kernel_)


def _lbo_fold(df, b, info, gp_scale_kernel):
    """Leave block b out: fit on training rows of the other blocks, calibrate on their calibration rows, predict
    the test rows of b. Hyperparameters fixed from the temporal CV (GP kernel fixed, refitted on a subsample)."""
    other, inb = (df.block != b).to_numpy(), (df.block == b).to_numpy()
    tr = other & (df.split == 'train').to_numpy()
    use = (other & (df.split == 'cal').to_numpy()) | (inb & (df.split == 'test').to_numpy())
    X, y = df[FEAT].to_numpy(float), df.y.to_numpy()
    d = df[use].copy()
    for name, loss, q in (('gbt', 'absolute_error', None), ('q05', 'quantile', .05), ('q95', 'quantile', .95)):
        d[f'p_{name}' if name == 'gbt' else name] = gbt(info[f'params_{name}'], loss, q).fit(X[tr], y[tr]).predict(X[use])
    d['q05'], d['q95'] = np.minimum(d.q05, d.q95), np.maximum(d.q05, d.q95)
    scale = gp_scaler(X[tr])
    d['p_gp'] = gp_fit(scale(X[tr]), y[tr], gp_scale_kernel[1], SEED, optimize=False).predict(scale(X[use]))
    sd = resid_sd(df, tr)
    cal, test = d[d.split == 'cal'], d[d.split == 'test']
    if not len(test):
        return None
    iv, _ = intervals(cal, test, sd, info['h'])
    return pd.concat([test, iv], axis=1)


def lbo(df, info, gsk):
    blocks = sorted(df.loc[df.split == 'test', 'block'].unique())
    res = Parallel(n_jobs=8)(delayed(_lbo_fold)(df, b, info, gsk) for b in blocks)
    return pd.concat([r for r in res if r is not None]), len(blocks)


# ---------- metrics (block bootstrap over 10 km blocks) ----------

def boot(d, num, den=None):
    """Ratio-of-sums estimate and 95% CI from NB block-bootstrap resamples of the 10 km blocks (fixed seed, so every
    metric on the same rows uses the same resamples: paired differences)."""
    codes, uniq = pd.factorize(d.block)
    nb = len(uniq)
    w = np.random.default_rng(SEED).multinomial(nb, np.full(nb, 1 / nb), size=NB)
    s = np.bincount(codes, num, nb)
    c = np.bincount(codes, np.ones(len(d)) if den is None else den, nb)
    return s.sum() / c.sum(), np.percentile((w @ s) / (w @ c), [2.5, 97.5])


def point_metrics(d, m):
    e = d.y.to_numpy() - d[f'p_{m}'].to_numpy()
    mae, mci = boot(d, np.abs(e))
    mse, sci = boot(d, e ** 2)
    return {'MAE': (mae, mci), 'RMSE': (np.sqrt(mse), np.sqrt(sci))}


def interval_metrics(d, m, k):
    y, lo, hi = d.y.to_numpy(), d[f'lo_{m}_{k}'].to_numpy(), d[f'hi_{m}_{k}'].to_numpy()
    cov = ((y >= lo) & (y <= hi)).astype(float)
    wink = (hi - lo) + 2 / ALPHA * (np.maximum(lo - y, 0) + np.maximum(y - hi, 0))
    est, ci = boot(d, cov)
    return {'coverage': (100 * est, 100 * ci), 'width': boot(d, hi - lo),
            'winkler': boot(d, wink)}


def f(v, d=1):
    est, (lo, hi) = v
    return f'{est:.{d}f} [{lo:.{d}f}, {hi:.{d}f}]'


def mae_diff(d, m, base):
    a = np.abs(d.y - d[f'p_{m}']).to_numpy()
    b = np.abs(d.y - d[f'p_{base}']).to_numpy()
    return boot(d, a - b)


def pairs(m):
    return [(m, k) for k in METHODS] + ([('gbt', 'cqr')] if m == 'gbt' else [])


# ---------- report ----------

def md(df):
    return df.to_markdown(index=False)


def h1(test):
    """H1: each learned model vs the baseline with the lowest test MAE; CI of the MAE difference excludes 0."""
    pm = {m: point_metrics(test, m) for m in MODELS}
    best = min(BASE, key=lambda m: pm[m]['MAE'][0])
    rows = [{'model': m, 'MAE (m)': f(pm[m]['MAE']), 'RMSE (m)': f(pm[m]['RMSE'])} for m in MODELS]
    verdict = []
    for m in LEARN:
        dv = mae_diff(test, m, best)
        better = dv[0] < 0 and dv[1][1] < 0
        verdict.append({'learned': m, 'best baseline (test MAE)': best, 'MAE difference (m)': f(dv, 2),
                        'H1 verdict': 'better' if better else 'not better'})
    return pd.DataFrame(rows), pd.DataFrame(verdict), best


def h2(test, models):
    rows = []
    for m in models:
        for mm, k in pairs(m):
            im = interval_metrics(test, mm, k)
            c = im['coverage'][0]
            rows.append({'point model': mm, 'method': LABEL[k], 'coverage (%)': f(im['coverage']),
                         'mean width (m)': f(im['width']), 'Winkler (m)': f(im['winkler']),
                         'H2 (90 ± 3 pp)': 'holds' if abs(c - 90) <= 3 else 'fails'})
    return pd.DataFrame(rows)


def coverage_table(test, by, m='gbt', fmt=True):
    rows = []
    for key, d in test.groupby(by):
        row = {by: key, 'n': len(d), 'blocks': d.block.nunique()}
        for mm, k in pairs(m):
            v = interval_metrics(d, mm, k)['coverage']
            row[LABEL[k]] = f(v) if fmt else v[0]
        rows.append(row)
    return pd.DataFrame(rows)


def zone_table(test, h):
    rows = []
    sets = [('Vàm Nao ±10 km, all test rows (targets 2019-2024 all after 2012)', test[test.zone_vamnao]),
            ('Mỹ Thuận: last 10 km of the Tiền reach, all test rows', test[test.zone_mythuan]),
            ('Mỹ Thuận, forecast window overlapping 2014-2017 (origin <= 2017)',
             test[test.zone_mythuan & (test.origin <= 2017)]),
            ('outside both zones', test[~test.zone_vamnao & ~test.zone_mythuan])]
    for name, d in sets:
        if not len(d):
            rows.append({'subset': name, 'n': 0})
            continue
        row = {'subset': name, 'n': len(d), 'blocks': d.block.nunique(), 'GBT MAE (m)': f(point_metrics(d, 'gbt')['MAE'])}
        for mm, k in pairs('gbt'):
            row[LABEL[k]] = f(interval_metrics(d, mm, k)['coverage'])
        rows.append(row)
    return pd.DataFrame(rows)


def lbo_tables(lb):
    pm = pd.DataFrame([{'model': m, 'MAE (m)': f(point_metrics(lb, m)['MAE'])} for m in MODELS])
    return pm, h2(lb, ['gbt']), coverage_table(lb, 'group')


def info_lines(info):
    n = info['n']
    return [f"- h = {info['h']}, target {info['target']}: {info['n_series']} transect-sides; rows train {n.get('train', 0)}, "
            f"calibration {n.get('cal', 0)}, test {n.get('test', 0)}; origins {info['origins']}",
            f"- GBT params (CV MAE / pinball): point {info['params_gbt']}, q05 {info['params_q05']}, q95 {info['params_q95']}",
            f"- GP: kernel {info['gp_kernel']} (CV MAE {', '.join(f'{k} {v:.2f}' for k, v in info['gp_cv'].items())}), "
            f"n = {info['gp_n']} random training rows (seed {SEED}); fitted {info['gp_fitted']}",
            f"- Baseline fallback to persistence (rows): {info['fallback']}",
            f"- Gaussian SD (m): " + ', '.join(f'{k} {v:.1f}' for k, v in info['sd'].items()),
            f"- ACI alpha per test origin (GBT, γ = {GAMMA}): "
            + ', '.join(f'{k}: {v:.4f}' for k, v in info['aci_path']['gbt'].items())]


NOTES = [
    '## Notes: readings of the protocol (proposed deviations / clarifications for the owner)', '',
    '1. Covariates: width_m (median 2000-2014) and dwidth_00_14 (2000-02 -> 2012-14) contain bank positions after the '
    'training origins (2007-2012), against "inputs use only years <= t" (deviation 1); replaced by width_00 (median '
    '2000-02 width). curv_bank, node_km, is_island come from the static JRC-derived planform and are treated as static.',
    '2. Two learned models: H1 is judged for each separately. "Best baseline" = the baseline with the lowest test MAE '
    '(the hardest comparator; it chooses nothing that is then tuned).',
    '3. Gaussian SD = SD of out-of-fold training residuals (in-sample GBT residuals would be overfit). Targets are '
    'heavy-tailed (edge switches up to ~2 km are not removed: the spike filter only catches reverting jumps), so the SD '
    'is 76-120 m and Gaussian intervals over-cover (~99%), not under-cover as the protocol expected.',
    '4. ACI: 6 test origins and delayed feedback leave 3 (h = 3) or 1 (h = 5) updates; with a pooled per-origin '
    f'miscoverage and γ = {GAMMA} alpha moves by < 0.001, so ACI equals split conformal by construction (γ = {GAMMA_SENS} '
    'too). With this design the protocol\'s ACI comparison is not informative.',
    '5. The centred target uses year t + 1 at the origin and year 2019 in the last calibration target (d(2018)); '
    'this is the protocol\'s definition (target only), noted for transparency.',
    f'6. Change zones are not defined in the protocol: here ±{ZONE_KM:.0f} km of the Vàm Nao junction (vamnao_km) and the '
    f'last {ZONE_KM:.0f} km of the Tiền reach (Mỹ Thuận bridge); both have only 2-5 blocks, so their CIs are not reliable.',
    '7. Spatial leave-one-block-out is combined with the temporal split (train/calibration rows of the other blocks, '
    'test rows of the held-out block); hyperparameters fixed from the temporal CV, GP kernel fixed and refitted.',
    f'8. GP on n = {GP_N} rows (n = 2000 took > 20 min per CV fit). With a Gaussian likelihood it interpolates the '
    'heavy-tailed target (fitted white noise ~1-3% of the normalised variance): poor MAE.',
    '9. CQR at h = 3 under-covers on test (71%) although it is 90% on calibration: the raw GBT quantile width depends '
    'on the origin (calibration origins 2013-2015 sit next to the 2010 / 2012 / 2013 composite gaps: median raw width '
    '60 m; test origins 2018-2021: 23 m) while the |retreat| distribution is the same (p90 21 m). A feature shift from '
    'composite completeness, not a code bug.', '']


def report(res, runtime):
    L = ['# P2: transect forecasts with 90% intervals (H1, H2)', '',
         f'`python src/forecast.py` ({runtime:.0f} s). Protocol: docs/protocol.md section 2 + deviation 1 (tag protocol-v1). '
         'Test = targets 2019-2024, scored once; every choice below was made on training rows only (CV) or fixed a priori. '
         'CIs: 95% block bootstrap over 10 km blocks (1,000 resamples, seed 0). Retreat + = landward (m).', '',
         '## Setup', '',
         f'- Inputs: lagged positions x(t-k) minus the trailing 3-yr mean (k = 0..5), Theil-Sen rates over 3/5/10 yr '
         f'(>= 2/3/5 valid years), physical covariates {COV} of the 2 km unit (width_00 = median 2000-02 channel width; '
         'width_m and dwidth_00_14 use 2000-2014 and are not used, see notes). No exposure variables.',
         f'- Groups (Mondrian): Tiền main; Hậu wide; Hậu narrow (channel hau, chainage < {res["narrow"]:.0f} m = '
         'tiles.json narrow_until_m 38800 - border 8500; stitch.py uses raw chainage < narrow_until_m); island channels.',
         f'- Blocks: {res["n_blocks"]} blocks of 10 km (main: chainage; islands: island chainage in tiles.json).',
         f'- Change zones: Vàm Nao = 2 km units with |vamnao_km| <= {ZONE_KM:.0f} (covariates_2km, both rivers and island '
         f'channels); Mỹ Thuận = Tiền bank points (incl. island channels) within {ZONE_KM:.0f} km of the downstream end of the '
         'reach at the Mỹ Thuận bridge.',
         f'- ACI: one alpha per forecast origin, pooled over transects, alpha_0 = {ALPHA}, step γ = {GAMMA} (fixed a priori, '
         f'Gibbs & Candès 2021 default), γ = {GAMMA_SENS} as a sensitivity; feedback from origin s is used from origin s + h on.',
         '- Gaussian interval: ±1.645 SD of the out-of-fold training residuals (learned) or of the training residuals (baselines).', '']
    for key in ('h3_mean', 'h5_mean', 'h3_raw', 'h5_raw'):
        L += info_lines(res[key]['info'])
    L.append('')
    for h in (3, 5):
        r = res[f'h{h}_mean']
        test = r['out'][r['out'].split == 'test']
        pm, verdict, best = h1(test)
        r['best'] = best
        L += [f'## h = {h} yr, 3-yr mean target ({"primary" if h == 3 else "secondary horizon"})', '',
              '### H1: point accuracy (test)', '', md(pm), '', md(verdict), '',
              '### H2: intervals (test, pooled)', '', md(h2(test, ['gbt', 'gp', best])), '',
              '### Coverage by group (test, GBT point model; CQR on GBT quantiles)', '', md(coverage_table(test, 'group')), '',
              '### Coverage by target year (test, GBT)', '', md(coverage_table(test, 'target_year')), '',
              '### Change periods (test, GBT)', '', md(zone_table(test, h)), '',
              '### Calibration rows (in-sample check: split and Mondrian ~90% by construction)', '',
              md(h2(r['out'][r['out'].split == 'cal'], ['gbt'])[['point model', 'method', 'coverage (%)']]), '',
              '### Spatial leave-one-block-out (fit on training rows of the other blocks, calibrate on their '
              'calibration rows, score the held-out block\'s test rows)', '']
        pm2, cov2, grp2 = lbo_tables(r['lbo'])
        L += [md(pm2), '', md(cov2), '', md(grp2), '',
              '### Secondary: linear-only series (test, models fitted on all series)', '']
        lin = test[test.kind == 'linear']
        pm3, v3, _ = h1(lin)
        L += [md(pm3), '', md(v3), '', md(h2(lin, ['gbt'])), '']
    L += ['## Sensitivity: raw annual target x(t+h) - x(t)', '']
    for h in (3, 5):
        r = res[f'h{h}_raw']
        test = r['out'][r['out'].split == 'test']
        pm, verdict, _ = h1(test)
        L += [f'### h = {h}', '', md(pm), '', md(verdict), '', md(h2(test, ['gbt'])), '', md(coverage_table(test, 'group')), '']
    L += NOTES
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'forecast.md').write_text('\n'.join(L), encoding='utf-8')
    print('wrote', OUT / 'forecast.md')


# ---------- figure ----------

FIG_M = [('gauss', INK2, 'o'), ('split', BLUE, 's'), ('cqr', AQUA, 'D'), ('mondrian', ORANGE, '^'), ('aci', YELLOW, 'v')]


def figure():
    """(a) test coverage by method and group, h = 3; (b) mean width vs pooled coverage, h = 3 and 5; (c) coverage by
    target year, h = 3. GBT point model (CQR: GBT quantiles)."""
    d3 = pd.read_csv('data/processed/forecast_h3_mean.csv').query('split == "test"')
    d5 = pd.read_csv('data/processed/forecast_h5_mean.csv').query('split == "test"')
    fig, axs = plt.subplots(1, 3, figsize=(COL2, COL2 * .4), gridspec_kw=dict(width_ratios=[1.35, 1, 1], wspace=.42))
    cats = ['All'] + GROUPS
    for ax in axs[[0, 2]]:
        ax.axhspan(87, 93, color=GRID, alpha=.6, lw=0)
        ax.axhline(90, color=INK2, lw=.6)
    ax = axs[0]
    for j, (k, col, mk) in enumerate(FIG_M):
        m = 'gbt'
        for i, c in enumerate(cats):
            d = d3 if c == 'All' else d3[d3.group == c]
            est, (lo, hi) = interval_metrics(d, m, k)['coverage']
            x = i + (j - 2) * .14
            ax.errorbar(x, est, [[est - lo], [hi - est]], fmt=mk, ms=4, color=col, mec='white', mew=.4, lw=.8,
                        label=LABEL[k] if i == 0 else None)
    ax.set_xticks(range(len(cats)), ['All', 'Tiền\nmain', 'Hậu\nwide', 'Hậu\nnarrow', 'Islands'])
    ax.set_ylabel('Test coverage (%)')
    ax.set_title('(a) By group, h = 3 yr', loc='left', pad=3, fontweight='bold')
    chart_axes(ax)
    ax = axs[1]
    for k, col, mk in FIG_M:
        for d, fill in ((d3, col), (d5, 'white')):
            est = interval_metrics(d, 'gbt', k)
            ax.plot(est['width'][0], est['coverage'][0], mk, ms=5, mfc=fill, mec=col, mew=1)
    ax.axhspan(87, 93, color=GRID, alpha=.6, lw=0)
    ax.axhline(90, color=INK2, lw=.6)
    ax.plot([], [], 'o', mfc=INK2, mec=INK2, ms=4, label='h = 3 yr')
    ax.plot([], [], 'o', mfc='white', mec=INK2, ms=4, label='h = 5 yr')
    ax.legend(loc='lower right', handletextpad=.2)
    ax.set_xscale('log')
    ax.set_xticks([30, 100, 300], ['30', '100', '300'])
    ax.set_xlabel('Mean interval width (m)')
    ax.set_ylabel('Pooled test coverage (%)')
    ax.set_title('(b) Width vs coverage', loc='left', pad=3, fontweight='bold')
    chart_axes(ax)
    ax = axs[2]
    for k, col, mk in FIG_M:
        yrs = sorted(d3.target_year.unique())
        v = [interval_metrics(d3[d3.target_year == y], 'gbt', k)['coverage'][0] for y in yrs]
        ax.plot(yrs, v, '-', marker=mk, ms=4, color=col, mec='white', mew=.4, lw=1)
    ax.set_xlabel('Target year')
    ax.set_ylabel('Test coverage (%)')
    ax.set_title('(c) By target year, h = 3 yr', loc='left', pad=3, fontweight='bold')
    chart_axes(ax)
    lo = min(a.get_ylim()[0] for a in axs)
    for a in axs:
        a.set_ylim(lo, 100)
    hd, lb = axs[0].get_legend_handles_labels()
    fig.legend(hd, lb, loc='upper center', ncol=5, bbox_to_anchor=(.5, -.02), handletextpad=.2, columnspacing=1.2)
    save(fig, 'fig07_coverage')


# ---------- main ----------

def main():
    if sys.argv[1:] == ['fig']:
        return figure()
    t0 = time.time()
    u, W, narrow = load()
    D = centred(W)
    res = {'narrow': narrow, 'n_blocks': u[np.isfinite(W).sum(1) >= MIN_SERIES].block.nunique()}
    for target in ('mean', 'raw'):
        for h in (3, 5):
            df, out, info, gsk = run(u, W, D, h, target)
            r = {'out': out, 'info': info}
            cols = [c for c in out.columns if not c.startswith('oof_') and c != 'i']
            out[cols].round(3).to_csv(f'data/processed/forecast_h{h}_{target}.csv', index=False)
            if target == 'mean':
                r['lbo'], _ = lbo(df, info, gsk)
                r['lbo'][[c for c in cols if c in r['lbo']]].round(3).to_csv(f'data/processed/forecast_lbo_h{h}.csv',
                                                                            index=False)
            res[f'h{h}_{target}'] = r
            print(f'h={h} {target}: done {time.time() - t0:.0f} s', flush=True)
    report(res, time.time() - t0)
    figure()


if __name__ == '__main__':
    main()
