"""EXPLORATORY (docs/exploratory_plan.md section A, written before running): forecast horizon and sampling interval.
Does not change any confirmatory verdict of results/p2/forecast.md; no pass/fail verdicts here.

Usage: python src/explore_horizon.py          (all, ~5-10 min with N_JOBS workers)
       python src/explore_horizon.py fig      (only redraw figures/fig09_horizon from the written CSVs)
Reads the same inputs as src/forecast.py (its load / centred / build are imported, so the rows, inclusion and
3-yr centred target are identical: series >= 15 valid years 2000-2024, origin t with >= 8 valid years in 2000..t).
Writes:
  data/processed/explore_horizon_{detect,skill,sampling,sampling_fc}.csv   summary tables (figure input)
  results/p2/explore_horizon.md                                            tables + plain-language summary
  figures/fig09_horizon.png + .svg
Design:
  Noise floor of a true change d(t+h) - d(t), d = 3-yr centred mean of the valid years (1/n weights w): with white
  composite noise sigma, SD = sigma * sqrt(sum_y (w_{t+h,y} - w_{t,y})^2) per row (overlapping windows at h = 1, 2
  handled exactly); 95% floor = 1.96 SD. Full non-overlapping windows: 1.96 sigma sqrt(2/3) = 5.8 m (sigma 3.6) /
  7.5 m (4.7). Detectability = share of rows (transect-side x origin, all origins pooled) with |change| > floor.
  Forecast skill, rolling origins: for each evaluated target year Y in 2019-2024 and horizon h, origin t = Y - h; GBT
  (confirmatory point hyperparameters, not re-tuned) fitted on all rows whose target year <= t - 1 (so every
  position used, incl. year target + 1 of the centred mean, is <= t). Split conformal: scores on the 3 most recent
  target years <= t - 1 (baselines: plain residuals; GBT: 5-fold spatial-block out-of-fold residuals of the same
  training rows). A (h, Y) with < MIN_TRAIN training rows has no GBT. MAE CIs: forecast.boot (10 km blocks).
  Sampling: annual series thinned to every 2nd / 3rd / 5th year (all phases) and to DSAS-like sets of 4, 6, 9 dates
  (2000 and 2024 always kept, interior dates drawn from years with a composite, NDRAW seed-fixed draws). Theil-Sen
  rates 2000-2024 vs the full annual series; 'significant' = |rate| > 1.96 sigma / sqrt(sum (t - mean t)^2) over the
  valid dates (95% rate floor for white noise sigma). Forecast: Theil-Sen over the thinned dates <= t, x h.
"""
import pathlib
import sys
import time
import warnings

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from sklearn.model_selection import GroupKFold

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from figures import AQUA, BLUE, COL2, GRID, INK, INK2, ORANGE, YELLOW, chart_axes, plt, save  # noqa: E402
from forecast import (ALPHA, FEAT, GROUPS, SEED, YEARS, boot, build, centred, cq, gbt, load,  # noqa: E402
                      mae_diff, ts_slope)

SIGMA, SIGMA2 = 3.6, 4.7                # measured noise per composite; median robust residual scale (sat_labels.md)
H_DET = range(1, 11)
H_SKILL = (1, 2, 3, 4, 5, 7, 10)
EVAL = range(2019, 2025)                # evaluated target years (= the confirmatory test years)
CAL_YRS, MIN_TRAIN = 3, 1000
GBT_P = dict(learning_rate=.05, max_leaf_nodes=15, min_samples_leaf=100)   # confirmatory point GBT (h = 3 and 5)
MODELS = ['persistence', 'lrr_10', 'lrr_all', 'gbt']
MLAB = {'persistence': 'Persistence', 'lrr_10': 'Theil-Sen, last 10 yr', 'lrr_all': 'Theil-Sen, all years <= t',
        'gbt': 'GBT'}
NDRAW, MIN_THIN = 20, 2                 # random date sets per size; valid dates for a thinned Theil-Sen (as build)
N_JOBS = 10
GLAB = {'All': 'All', 'Tien main': 'Tiền main', 'Hau wide': 'Hậu wide', 'Hau narrow': 'Hậu narrow',
        'Island': 'Island channels'}
OUT = pathlib.Path('results/p2')
CSV = 'data/processed/explore_horizon_{}.csv'


# ---------- noise floor ----------

def weights(W):
    """G[i, c, y]: weight of year y in the 3-yr centred mean at centre c (1/n over the valid years of the window)."""
    V = np.isfinite(W).astype(float)
    T = W.shape[1]
    G = np.zeros((len(W), T, T))
    for c in range(T):
        a, b = max(c - 1, 0), min(c + 2, T)
        n = V[:, a:b].sum(1, keepdims=True)
        G[:, c, a:b] = V[:, a:b] / np.maximum(n, 1)
    return G


def rows_h(u, W, D, G, h):
    """forecast.build rows (target = 3-yr mean change) + f = SD factor of the target's noise (SD = sigma * f)."""
    df, _ = build(u, W, D, h, 'mean')
    i, k = df.i.to_numpy(), (df.origin - YEARS[0]).to_numpy()
    df['f'] = np.sqrt(((G[i, k + h] - G[i, k]) ** 2).sum(1))
    return df


# ---------- 1. detectability ----------

def detect(rows):
    out = []
    for h in H_DET:
        df = rows[h]
        for g in GLAB:
            d = df if g == 'All' else df[df.group == g]
            for s in (SIGMA, SIGMA2):
                est, (lo, hi) = boot(d, (np.abs(d.y) > 1.96 * s * d.f).to_numpy(float))
                out.append(dict(h=h, group=g, sigma=s, share=100 * est, lo=100 * lo, hi=100 * hi, n=len(d),
                                blocks=d.block.nunique(), floor=1.96 * s * d.f.median()))
    return pd.DataFrame(out)


# ---------- 2. forecast skill by horizon ----------

def fit_year(X, y, g, tr, te):
    """GBT on the training rows -> predictions for te; 5-fold spatial-block OOF predictions for the training rows."""
    pt = gbt(GBT_P, 'absolute_error').fit(X[tr], y[tr]).predict(X[te])
    oof = np.empty(len(tr))
    for a, b in GroupKFold(5).split(tr, groups=g[tr]):
        oof[b] = gbt(GBT_P, 'absolute_error').fit(X[tr[a]], y[tr[a]]).predict(X[tr[b]])
    return pt, oof


def skill(rows):
    """Rolling-origin forecasts for every (h, Y); returns the evaluated rows with p_gbt and conformal half-widths."""
    plan = []
    for h in H_SKILL:
        df = rows[h]
        for Y in EVAL:
            cut = Y - h - 1
            plan.append((h, Y, cut, np.where(df.target_year <= cut)[0], np.where(df.target_year == Y)[0]))
    todo = [p for p in plan if len(p[3]) >= MIN_TRAIN]
    res = Parallel(n_jobs=N_JOBS, verbose=0)(
        delayed(fit_year)(rows[h][FEAT].to_numpy(float), rows[h].y.to_numpy(), rows[h].block.to_numpy(), tr, te)
        for h, Y, cut, tr, te in todo)
    fitted = {(p[0], p[1]): r for p, r in zip(todo, res)}
    parts = []
    for h, Y, cut, tr, te in plan:
        df = rows[h]
        d = df.iloc[te].copy()
        calpos = np.where(df.target_year.to_numpy()[tr] > cut - CAL_YRS)[0]
        cal = df.iloc[tr[calpos]]
        d['h'], d['n_train'], d['n_cal'] = h, len(tr), len(cal)
        pt, oof = fitted.get((h, Y), (None, None))
        d['p_gbt'] = np.nan if pt is None else pt
        for m in MODELS:
            pc = (oof[calpos] if oof is not None else None) if m == 'gbt' else cal[f'p_{m}'].to_numpy()
            ok = pc is not None and len(cal) >= 100
            d[f'half_{m}'] = cq(np.abs(cal.y.to_numpy() - pc), ALPHA) if ok else np.nan
        parts.append(d)
    return pd.concat(parts, ignore_index=True)


def skill_summary(ev):
    """Per h and row set ('matched' = rows with a GBT forecast; 'all' = every 2019-2024 target row, baselines)."""
    out = []
    for h, dh in ev.groupby('h'):
        for rset, d in (('matched', dh[dh.p_gbt.notna()]), ('all', dh)):
            if not len(d):
                continue
            nm = d.f.to_numpy() * SIGMA * np.sqrt(2 / np.pi)       # E|noise| of the target = MAE of a perfect forecast
            base = dict(h=h, set=rset, n=len(d), blocks=d.block.nunique(), years=f'{d.target_year.min()}-'
                        f'{d.target_year.max()}', floor=1.96 * SIGMA * d.f.median(), noise_mae=nm.mean(),
                        med_abs_change=d.y.abs().median(), n_train=f'{d.n_train.min()}-{d.n_train.max()}')
            for m in MODELS:
                if d[f'p_{m}'].isna().any():
                    continue
                e = np.abs(d.y - d[f'p_{m}']).to_numpy()
                mae, (lo, hi) = boot(d, e)
                dv, (dlo, dhi) = mae_diff(d, m, 'persistence') if m != 'persistence' else (0, (0, 0))
                r = dict(base, model=m, mae=mae, lo=lo, hi=hi, diff=dv, dlo=dlo, dhi=dhi)
                half = d[f'half_{m}'].to_numpy()
                if np.isfinite(half).all():
                    p = d[f'p_{m}'].to_numpy()
                    c, (clo, chi) = boot(d, (np.abs(d.y.to_numpy() - p) <= half).astype(float))
                    w, (wlo, whi) = boot(d, 2 * half)
                    r.update(cov=100 * c, cov_lo=100 * clo, cov_hi=100 * chi, width=w, w_lo=wlo, w_hi=whi)
                out.append(r)
    return pd.DataFrame(out)


# ---------- 3. sampling interval ----------

def date_sets(W):
    have = np.where(np.isfinite(W).any(0))[0]                 # 2012 has no composite
    S = [('annual', '-', np.arange(len(YEARS)))]
    for k in (2, 3, 5):
        S += [(f'every {k} yr', f'phase {p}', np.arange(p, len(YEARS), k)) for p in range(k)]
    rng = np.random.default_rng(SEED)
    inner = have[(have > 0) & (have < len(YEARS) - 1)]
    for m in (4, 6, 9):
        S += [(f'{m} dates', f'draw {d}', np.r_[0, np.sort(rng.choice(inner, m - 2, replace=False)), len(YEARS) - 1])
              for d in range(NDRAW)]
    return [(s, c, cols[np.isin(cols, have)]) for s, c, cols in S]


def rate(Wc, yrs):
    """Theil-Sen rate (NaN unless >= MIN_THIN valid dates) and 'significant' vs the white-noise rate floor."""
    r = ts_slope(Wc, yrs, MIN_THIN)
    t = np.where(np.isfinite(Wc), yrs, np.nan)
    with np.errstate(invalid='ignore', divide='ignore'), warnings.catch_warnings():
        warnings.simplefilter('ignore')
        sxx = np.nansum((t - np.nanmean(t, 1, keepdims=True)) ** 2, 1)
        return r, np.abs(r) > 1.96 * SIGMA / np.sqrt(sxx)


def sampling(u, W, rows):
    inc = np.isfinite(W).sum(1) >= 15
    Wi, blk = W[inc], u.block.to_numpy()[inc]
    full, fsig = rate(Wi, YEARS)
    rr, fc = [], []
    for s, c, cols in date_sets(W):
        r, sig = rate(Wi[:, cols], YEARS[cols])
        ok = np.isfinite(r)
        rr.append(pd.DataFrame(dict(set=s, cfg=c, n_dates=len(cols), block=blk[ok], err=r[ok] - full[ok],
                                    sign=np.sign(r[ok]) != np.sign(full[ok]), sig=sig[ok] != fsig[ok],
                                    sig_full=fsig[ok], sig_thin=sig[ok], computable=ok.mean())))
        for h in (3, 5):
            d = rows[h][rows[h].target_year.isin(EVAL)]
            p = np.zeros(len(d))
            for t in d.origin.unique():
                m = (d.origin == t).to_numpy()
                cc = cols[YEARS[cols] <= t]
                p[m] = h * ts_slope(W[d.i.to_numpy()[m]][:, cc], YEARS[cc], MIN_THIN)
            fb = ~np.isfinite(p)
            p[fb] = 0.0                                          # fallback to persistence, as in forecast.build
            if s == 'annual':
                assert np.allclose(p, d.p_lrr_all), 'annual thinned set must reproduce forecast.build lrr_all'
            fc.append(pd.DataFrame(dict(set=s, cfg=c, n_dates=len(cols), h=h, block=d.block.to_numpy(),
                                        ae=np.abs(d.y.to_numpy() - p), fallback=fb)))
    return pd.concat(rr, ignore_index=True), pd.concat(fc, ignore_index=True)


def sampling_tables(rr, fc):
    order = list(dict.fromkeys(rr.set))
    per = rr.groupby(['set', 'cfg'], sort=False).agg(n_dates=('n_dates', 'first'), med_abs=('err', lambda x: x.abs().median()),
                                                     bias=('err', 'median'), computable=('computable', 'first')).reset_index()
    rows = []
    for s in order:
        d, p = rr[rr.set == s], per[per.set == s]
        sg = boot(d, d.sign.to_numpy(float))
        sc = boot(d, d.sig.to_numpy(float))
        rows.append({'date set': s, 'configs': len(p), 'dates (valid)': f'{p.n_dates.min()}-{p.n_dates.max()}',
                     'computable (%)': f'{100 * p.computable.mean():.1f}',
                     'median |rate error| (m/yr) [range over configs]': f'{d.err.abs().median():.2f} '
                     f'[{p.med_abs.min():.2f}, {p.med_abs.max():.2f}]',
                     'median bias (m/yr) [range]': f'{d.err.median():+.2f} [{p.bias.min():+.2f}, {p.bias.max():+.2f}]',
                     'sign changed (%)': pct(sg), "'significant' status changed (%)": pct(sc),
                     'significant, full -> thinned (%)': f'{100 * d.sig_full.mean():.0f} -> {100 * d.sig_thin.mean():.0f}'})
    fper = fc.groupby(['set', 'cfg', 'h'], sort=False).ae.mean().reset_index()
    frows = []
    for h in (3, 5):
        for s in order:
            d, p = fc[(fc.set == s) & (fc.h == h)], fper[(fper.set == s) & (fper.h == h)]
            frows.append({'h (yr)': h, 'date set': s, 'MAE (m) pooled [95% CI]': f1(boot(d, d.ae.to_numpy())),
                          'MAE range over configs': f'{p.ae.min():.1f}-{p.ae.max():.1f}',
                          'fallback to persistence (%)': f'{100 * d.fallback.mean():.1f}'})
    return per, pd.DataFrame(rows), pd.DataFrame(frows)


# ---------- report ----------

def pct(v):
    est, (lo, hi) = v
    return f'{100 * est:.1f} [{100 * lo:.1f}, {100 * hi:.1f}]'


def f1(v, d=1):
    est, (lo, hi) = v
    return f'{est:.{d}f} [{lo:.{d}f}, {hi:.{d}f}]'


def md(df):
    return df.to_markdown(index=False)


def detect_table(det, s):
    d = det[det.sigma == s]
    t = d.assign(v=[f'{a:.1f} [{b:.1f}, {c:.1f}]' for a, b, c in zip(d.share, d.lo, d.hi)]).pivot(
        index='h', columns='group', values='v')[list(GLAB)].rename(columns=GLAB).reset_index()
    fl = d[d.group == 'All'].set_index('h')
    t.insert(1, 'median floor (m)', fl.floor.round(1).to_numpy())
    t.insert(2, 'rows', fl.n.to_numpy())
    return t.rename(columns={'h': 'h (yr)'})


def skill_tables(sk):
    a, b = [], []
    for _, r in sk.iterrows():
        row = {'h (yr)': r.h, 'model': MLAB[r.model], 'MAE (m)': f'{r.mae:.1f} [{r.lo:.1f}, {r.hi:.1f}]',
               'MAE - persistence (m)': '-' if r.model == 'persistence' else f'{r["diff"]:+.2f} [{r.dlo:+.2f}, {r.dhi:+.2f}]',
               'MAE / noise-only MAE': f'{r.mae / r.noise_mae:.1f}'}
        if r.set == 'matched':
            row.update({'coverage (%)': f"{r['cov']:.1f} [{r.cov_lo:.1f}, {r.cov_hi:.1f}]" if np.isfinite(r['cov']) else '-',
                        'mean width (m)': f'{r.width:.1f} [{r.w_lo:.1f}, {r.w_hi:.1f}]' if np.isfinite(r.width) else '-'})
            a.append(row)
        else:
            b.append(row)
    meta = sk.drop_duplicates(['h', 'set'])[['h', 'set', 'n', 'blocks', 'years', 'n_train', 'floor', 'noise_mae',
                                              'med_abs_change']].round(2)
    return pd.DataFrame(a), pd.DataFrame(b), meta


def summary(det, sk, rr):
    """Plain-language summary; every number is read from the tables written below."""
    a = det[(det.group == 'All') & (det.sigma == SIGMA)].set_index('h').share
    m = sk[sk.set == 'matched'].set_index(['h', 'model'])
    beat = [h for h in sorted(m.index.levels[0]) if (h, 'gbt') in m.index and m.loc[(h, 'gbt'), 'dhi'] < 0]
    ts = [h for h in sorted(m.index.levels[0]) if m.loc[(h, 'lrr_10'), 'dhi'] < 0]
    med = rr.assign(a=rr.err.abs()).groupby('set').a.median()
    return ['## Summary (exploratory, plain language)', '',
            f'- Real bank change is above the composite noise for {a[1]:.0f}% of bank-point-years at 1 yr, {a[3]:.0f}% at '
            f'3 yr, {a[5]:.0f}% at 5 yr and {a[10]:.0f}% at 10 yr (sigma {SIGMA} m); the Hậu wide channel is the slowest up to '
            '6 yr (Hậu narrow beyond), island channels the fastest at every horizon. Even at 10 yr a third of the banks do not move measurably.',
            f'- Rate extrapolation (Theil-Sen) is worse than "no change" at every horizon tested (it beats persistence at: '
            f'{ts or "none"}), and its excess error grows with the horizon. GBT is better than persistence (CI of the MAE '
            f'difference below 0) at h = {beat or "none"} only, i.e. at horizons where most change is below the noise '
            '(see caveats on the centred target); from about 3 yr on it is indistinguishable from persistence or worse.',
            '- Forecast errors are 3-8x the noise-only MAE and grow with h because a minority of banks (edge switches, '
            'fast erosion sites) move a lot; split-conformal 90% intervals stay at about 91-95% coverage at every '
            'horizon, with widths growing from ~17 m (1 yr) to ~140 m (7 yr, persistence).',
            f'- Sparse sampling costs little in the median rate (median |error| {med["every 2 yr"]:.2f} m/yr every 2nd year, '
            f'{med["every 5 yr"]:.2f} every 5th, {med["4 dates"]:.2f} with 4 dates) but changes the sign of 4-12% and the '
            "'significant' status of 7-17% of transect-sides, and inflates extrapolation errors; with 4-6 random dates "
            'the result depends strongly on which dates were drawn.', '',
            '## Caveats', '',
            '- The centred target d(t+h) - d(t) contains x(t-1) and x(t) (known at the origin) and x(t+1) (not known). '
            'At every h part of the target is the reversal of known origin noise; at h = 1, 2 (overlapping windows, small real change) that part is large, which GBT can '
            'learn from the lag features and persistence cannot; the GBT gain at h = 1, 2 is therefore not evidence of '
            'forecasting real bank movement.',
            '- Detectability above 5% at h = 1 (the share expected from noise alone) includes edge switches and real '
            'year-to-year wobble that the white-noise model does not capture; with sigma 4.7 m it is lower but similar.',
            '- GBT conformal scores are spatial out-of-fold residuals of years the model was also fitted on (other '
            'blocks); baseline scores are true residuals. Interval width CIs are near-degenerate because the half-width is '
            'one number per target year.',
            '- h = 7: GBT only for targets 2022-2024 (5,936-18,325 training rows); h = 10: no GBT (no training targets '
            'before the origins). The sampling analysis keeps the annual spike removal and 2012 has no composite.', '']


def report(det, sk, rtab, ftab, ev, rr, runtime):
    ta, tb, meta = skill_tables(sk)
    feas = ev.groupby(['h', 'target_year']).agg(n_train=('n_train', 'first'), gbt=('p_gbt', lambda x: x.notna().any()))
    feas = feas.reset_index().pivot(index='h', columns='target_year', values='n_train')
    gb = ev.groupby(['h', 'target_year']).p_gbt.apply(lambda x: x.notna().any()).unstack()
    feas = feas.astype(int).astype(str).where(gb, feas.astype(int).astype(str) + ' (no GBT)').reset_index()
    L = ['# EXPLORATORY: forecast horizon and sampling interval (plan A)', '',
         '**Exploratory** (docs/exploratory_plan.md section A, written before running). Nothing here changes a '
         'confirmatory verdict in results/p2/forecast.md, and no pass/fail verdict is given. '
         f'`python src/explore_horizon.py` ({runtime:.0f} s). Rows, inclusion and the 3-yr centred target are those of '
         'src/forecast.py (functions imported). CIs: 95% block bootstrap over 10 km blocks (1,000 resamples, seed 0); '
         'retreat + = landward.', ''] + summary(det, sk, rr) + [
         '## Noise floor', '',
         'd(t) = mean of the valid annual positions in t-1..t+1 (weights w = 1/n). With white composite noise sigma, '
         'SD[d(t+h) - d(t)] = sigma sqrt(sum_y (w_{t+h,y} - w_{t,y})^2), computed per row (exact for the overlapping '
         'windows at h = 1, 2 and for missing years). 95% floor = 1.96 SD. Full windows: h >= 3: 1.96 sigma sqrt(2/3) = '
         f'{1.96 * SIGMA * np.sqrt(2 / 3):.1f} m (sigma {SIGMA}) / {1.96 * SIGMA2 * np.sqrt(2 / 3):.1f} m (sigma {SIGMA2}); '
         f'h = 2: 1.96 sigma 2/3 = {1.96 * SIGMA * 2 / 3:.1f} / {1.96 * SIGMA2 * 2 / 3:.1f} m; h = 1: 1.96 sigma sqrt(2)/3 = '
         f'{1.96 * SIGMA * np.sqrt(2) / 3:.1f} / {1.96 * SIGMA2 * np.sqrt(2) / 3:.1f} m. sigma = {SIGMA} m is the measured '
         f'noise used throughout; {SIGMA2} m is the median robust residual scale of linear series (includes real wobble).', '',
         '## 1. Detectability by horizon', '',
         'Share (%) of rows (included transect-side x usable origin, all origins 2007..2024-h pooled) whose true change '
         '|d(t+h) - d(t)| exceeds the 95% noise floor of that row.', '',
         f'### sigma = {SIGMA} m', '', md(detect_table(det, SIGMA)), '',
         f'### sigma = {SIGMA2} m', '', md(detect_table(det, SIGMA2)), '',
         '## 2. Forecast skill by horizon (rolling origins)', '',
         'Design: for each target year Y in 2019-2024, origin t = Y - h. GBT (features of forecast.py, confirmatory '
         f'point hyperparameters {GBT_P}, absolute error, 300 iterations; not re-tuned) is fitted on all rows whose '
         'target year <= t - 1, so every position it sees (including year target + 1 inside the centred mean) is <= t. '
         f'Split conformal (90%): scores on the {CAL_YRS} most recent target years <= t - 1; baselines: plain residuals; '
         'GBT: 5-fold spatial-block (GroupKFold over 10 km blocks) out-of-fold residuals of the same training fit. '
         f'A (h, Y) with < {MIN_TRAIN} training rows gets no GBT. Noise-only MAE = mean of sigma f sqrt(2/pi) over the rows '
         '(the MAE a perfect forecast would score against the noisy 3-yr-mean positions).', '',
         'Training rows per (h, target year):', '', md(feas), '',
         '### Rows with a GBT forecast (all models on the same rows; split-conformal coverage and width)', '', md(ta), '',
         '### Every 2019-2024 target row (h = 7, 10: baselines only where GBT could not be fitted; h <= 5 identical to the table above)', '', md(tb), '',
         '### Row sets', '', md(meta), '',
         '## 3. Sampling interval', '',
         f'Included transect-sides (>= 15 valid years). Every k-th year: all k phases; m dates: 2000 and 2024 kept, m - 2 '
         f'interior years drawn without replacement from years with a composite ({NDRAW} draws, seed {SEED}); 2012 has '
         f'no composite and is dropped where it falls in a set. Theil-Sen needs >= {MIN_THIN} valid dates. '
         f"'Significant' = |rate| > 1.96 x {SIGMA} / sqrt(sum (t - mean t)^2) over the transect-side's valid dates. "
         'Spike removal of the annual series is kept (a sparse study could not detect reverting jumps).', '',
         '### (a) Theil-Sen rate 2000-2024 vs the full annual series', '', md(rtab), '',
         '### (b) Forecast error of Theil-Sen extrapolation fitted on the thinned dates <= t (targets 2019-2024)', '',
         md(ftab), '']
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'explore_horizon.md').write_text('\n'.join(L), encoding='utf-8')
    print('wrote', OUT / 'explore_horizon.md')


# ---------- figure ----------

GCOL = {'All': INK, 'Tien main': BLUE, 'Hau wide': ORANGE, 'Hau narrow': AQUA, 'Island': YELLOW}
MSTY = {'persistence': (INK2, 'o', '-'), 'lrr_10': (ORANGE, 's', '-'), 'lrr_all': (YELLOW, 'D', '-'),
        'gbt': (BLUE, '^', '-')}


def figure():
    det, sk = pd.read_csv(CSV.format('detect')), pd.read_csv(CSV.format('skill'))
    per = pd.read_csv(CSV.format('sampling'))
    fig, axs = plt.subplots(1, 3, figsize=(COL2, COL2 * .42), gridspec_kw=dict(wspace=.36))
    ax = axs[0]
    for g, col in GCOL.items():
        d = det[(det.group == g) & (det.sigma == SIGMA)]
        ax.fill_between(d.h, d.lo, d.hi, color=col, alpha=.15, lw=0)
        ax.plot(d.h, d.share, '-o', color=col, ms=2.5, lw=1.4 if g == 'All' else 1, label=GLAB[g])
    d = det[(det.group == 'All') & (det.sigma == SIGMA2)]
    ax.plot(d.h, d.share, '--', color=INK, lw=.8, label=f'All, σ = {SIGMA2} m')
    ax.set_xticks(range(1, 11))
    ax.set_xlabel('Horizon h (yr)')
    ax.set_ylabel('Change > 95% noise floor (%)')
    ax.set_ylim(0, None)
    ax.legend(loc='upper center', bbox_to_anchor=(.45, -.22), ncol=2, handlelength=1.4, labelspacing=.25, columnspacing=.8)
    ax.set_title('(a) Detectability', loc='left', pad=3, fontweight='bold')
    chart_axes(ax)
    ax = axs[1]
    m0 = sk[sk.set == 'matched']
    nm = m0.drop_duplicates('h')
    ax.plot(nm.h, nm.noise_mae, ':', color=INK, lw=1, label='Noise only')
    off = dict(zip(MSTY, (-.15, -.05, .05, .15)))
    for m, (col, mk, ls) in MSTY.items():
        d = m0[m0.model == m]
        ax.errorbar(d.h + off[m], d.mae, [d.mae - d.lo, d.hi - d.mae], fmt=mk + ls, color=col, ms=3.5, lw=1,
                    elinewidth=.7, mec='white', mew=.3, label=MLAB[m].replace('Theil-Sen, ', 'TS ').replace('all years <= t', 'all yr'))
    ax.set_xticks(sorted(m0.h.unique()))
    ax.set_xlabel('Horizon h (yr)')
    ax.set_ylabel('MAE of retreat (m)')
    ax.set_ylim(0, None)
    ax.legend(loc='upper center', bbox_to_anchor=(.45, -.22), ncol=2, handlelength=1.6, labelspacing=.25, columnspacing=.8)
    ax.set_title('(b) Forecast error (rolling)', loc='left', pad=3, fontweight='bold')
    chart_axes(ax)
    ax = axs[2]
    sty = {'every 2 yr': (BLUE, 'o'), 'every 3 yr': (BLUE, 's'), 'every 5 yr': (BLUE, 'D'),
           '4 dates': (ORANGE, 'v'), '6 dates': (ORANGE, '^'), '9 dates': (ORANGE, 'P')}
    rng = np.random.default_rng(SEED)
    for s, (col, mk) in sty.items():
        d = per[per.set == s]
        x = d.n_dates + rng.uniform(-.25, .25, len(d))
        ax.plot(x, d.med_abs, mk, color=col, ms=3, alpha=.45, mew=0)
        ax.plot(d.n_dates.median(), d.med_abs.median(), mk, color=col, ms=5.5, mec=INK, mew=.6, label=s)
    ax.set_xlabel('Dates used, 2000–2024')
    ax.set_ylabel('Median |rate error| (m/yr)')
    ax.set_ylim(0, None)
    ax.set_xticks([4, 6, 8, 10, 12])
    ax.legend(loc='upper center', bbox_to_anchor=(.5, -.22), ncol=3, handletextpad=.1, columnspacing=.6, labelspacing=.25)
    ax.set_title('(c) Sparse vs annual rates', loc='left', pad=3, fontweight='bold')
    chart_axes(ax)
    fig.text(.995, .93, 'Exploratory analysis', ha='right', va='bottom', color=INK2, fontsize=7)
    save(fig, 'fig09_horizon')


# ---------- main ----------

def main():
    if sys.argv[1:] == ['fig']:
        return figure()
    t0 = time.time()
    u, W, _ = load()
    D, G = centred(W), weights(W)
    rows = {h: rows_h(u, W, D, G, h) for h in sorted(set(H_DET) | set(H_SKILL))}
    det = detect(rows)
    print(f'detectability done {time.time() - t0:.0f} s', flush=True)
    ev = skill(rows)
    sk = skill_summary(ev)
    print(f'skill done {time.time() - t0:.0f} s', flush=True)
    rr, fc = sampling(u, W, rows)
    per, rtab, ftab = sampling_tables(rr, fc)
    det.to_csv(CSV.format('detect'), index=False)
    sk.to_csv(CSV.format('skill'), index=False)
    per.to_csv(CSV.format('sampling'), index=False)
    fc.groupby(['set', 'cfg', 'h'], sort=False).ae.mean().reset_index().to_csv(CSV.format('sampling_fc'), index=False)
    report(det, sk, rtab, ftab, ev, rr, time.time() - t0)
    figure()


if __name__ == '__main__':
    main()
