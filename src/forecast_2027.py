"""P3 R5: forward forecast of bank retreat 2024 -> 2027 (h = 3) for the web atlas, with the validated method, no tuning.

Usage: python src/forecast_2027.py
Design = the rolling-origin design of src/explore_horizon.py (section 2) at origin t = 2024:
  rows and features from forecast.build (3-yr centred mean target, series >= 15 valid years, origin >= 8 valid years);
  GBT with the confirmatory point hyperparameters (explore_horizon.GBT_P, absolute error) fitted on all rows whose
  target year <= t - 1 = 2023 (every position used is <= 2024); split-conformal 90% half-width from the 5-fold
  spatial-block out-of-fold residuals of the training rows with target years 2021-2023 (explore_horizon.fit_year,
  CAL_YRS = 3), and a Mondrian version per group. Persistence (forecast 0): split / Mondrian half-width from its plain
  residuals on the same target years. The origin-2024 feature rows come from forecast.build itself (run with three
  dummy future years so it emits origin 2024; the dummy values enter neither the features nor the inclusion rule).
Writes data/processed/forecast_2027.csv (one row per in-scope transect-side with a forecast).
"""
import pathlib
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import forecast as F  # noqa: E402
from explore_horizon import CAL_YRS, fit_year  # noqa: E402

H, ORIGIN = 3, 2024
OUT = pathlib.Path('data/processed/forecast_2027.csv')


def origin_rows(u, W):
    """forecast.build rows at origin 2024 (features use W[:, :25] only)."""
    years = F.YEARS
    try:
        F.YEARS = np.arange(years[0], years[-1] + H + 1)
        Wx = np.hstack([W, np.zeros((len(W), H))])
        fx, _ = F.build(u, Wx, np.zeros_like(Wx), H, 'mean')
    finally:
        F.YEARS = years
    ok = np.isfinite(W).sum(1) >= F.MIN_SERIES          # inclusion on the real years only
    return fx, fx[(fx.origin == ORIGIN) & ok[fx.i]].reset_index(drop=True)


def main():
    u, W, _ = F.load()
    D = F.centred(W)
    df, _ = F.build(u, W, D, H, 'mean')
    fx, new = origin_rows(u, W)
    # self-check: the patched build reproduces build's features on a shared origin
    a = df[df.origin == 2015].set_index('i')[F.FEAT]
    b = fx[fx.origin == 2015].set_index('i').loc[a.index, F.FEAT]
    assert np.allclose(a.to_numpy(float), b.to_numpy(float), equal_nan=True), 'origin-2024 features differ from build'

    cut = ORIGIN - 1
    tr = np.where(df.target_year <= cut)[0]
    allx = pd.concat([df[F.FEAT], new[F.FEAT]], ignore_index=True).to_numpy(float)
    ally = np.r_[df.y.to_numpy(), np.zeros(len(new))]
    allg = np.r_[df.block.to_numpy(), new.block.to_numpy()]
    te = np.arange(len(df), len(df) + len(new))
    pt, oof = fit_year(allx, ally, allg, tr, te)

    calpos = np.where(df.target_year.to_numpy()[tr] > cut - CAL_YRS)[0]
    cal = df.iloc[tr[calpos]]
    s_gbt = np.abs(cal.y.to_numpy() - oof[calpos])
    s_per = np.abs(cal.y.to_numpy())
    grp = cal.group.to_numpy()
    half = {'gbt': (F.cq(s_gbt, F.ALPHA), {g: F.cq(s_gbt[grp == g], F.ALPHA) for g in F.GROUPS}),
            'pers': (F.cq(s_per, F.ALPHA), {g: F.cq(s_per[grp == g], F.ALPHA) for g in F.GROUPS})}

    o = new[['channel', 'transect', 'side', 'group']].copy()
    o['unit_2km'] = u.unit_2km.to_numpy()[new.i]
    o['d_2024'] = D[new.i, ORIGIN - F.YEARS[0]]
    o['pred_gbt'] = pt
    for m, p in (('gbt', pt), ('pers', np.zeros(len(new)))):
        hs, hm = half[m][0], o.group.map(half[m][1]).to_numpy()
        o[f'lo_{m}_split'], o[f'hi_{m}_split'] = p - hs, p + hs
        o[f'lo_{m}_mondrian'], o[f'hi_{m}_mondrian'] = p - hm, p + hm
    o.round(2).to_csv(OUT, index=False)

    print(f'training rows {len(tr)} (targets <= {cut}), calibration rows {len(cal)} '
          f'(targets {cut - CAL_YRS + 1}-{cut}), forecast rows {len(o)}, d_2024 missing {o.d_2024.isna().sum()}')
    print(f'GBT prediction: median {np.median(pt):.1f} m, p5 {np.percentile(pt, 5):.1f}, p95 {np.percentile(pt, 95):.1f}')
    rows = [('All', len(cal), half['gbt'][0], half['pers'][0], len(o))]
    rows += [(g, int((grp == g).sum()), half['gbt'][1][g], half['pers'][1][g], int((o.group == g).sum()))
             for g in F.GROUPS]
    print(pd.DataFrame(rows, columns=['group', 'n_cal', 'half_gbt', 'half_persistence', 'n_forecast'])
          .round(1).to_markdown(index=False))


if __name__ == '__main__':
    main()
