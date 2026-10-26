# EXPLORATORY: forecast horizon and sampling interval (plan A)

**Exploratory** (docs/exploratory_plan.md section A, written before running). Nothing here changes a confirmatory verdict in results/p2/forecast.md, and no pass/fail verdict is given. `python src/explore_horizon.py` (129 s). Rows, inclusion and the 3-yr centred target are those of src/forecast.py (functions imported). CIs: 95% block bootstrap over 10 km blocks (1,000 resamples, seed 0); retreat + = landward.

## Summary (exploratory, plain language)

- Real bank change is above the composite noise for 27% of bank-point-years at 1 yr, 38% at 3 yr, 49% at 5 yr and 63% at 10 yr (sigma 3.6 m); the Hậu wide channel is the slowest up to 6 yr (Hậu narrow beyond), island channels the fastest at every horizon. Even at 10 yr a third of the banks do not move measurably.
- Rate extrapolation (Theil-Sen) is worse than "no change" at every horizon tested (it beats persistence at: none), and its excess error grows with the horizon. GBT is better than persistence (CI of the MAE difference below 0) at h = [1, 2] only, i.e. at horizons where most change is below the noise (see caveats on the centred target); from about 3 yr on it is indistinguishable from persistence or worse.
- Forecast errors are 3-8x the noise-only MAE and grow with h because a minority of banks (edge switches, fast erosion sites) move a lot; split-conformal 90% intervals stay at about 91-95% coverage at every horizon, with widths growing from ~17 m (1 yr) to ~140 m (7 yr, persistence).
- Sparse sampling costs little in the median rate (median |error| 0.10 m/yr every 2nd year, 0.25 every 5th, 0.35 with 4 dates) but changes the sign of 4-12% and the 'significant' status of 7-17% of transect-sides, and inflates extrapolation errors; with 4-6 random dates the result depends strongly on which dates were drawn.

## Caveats

- The centred target d(t+h) - d(t) contains x(t-1) and x(t) (known at the origin) and x(t+1) (not known). At every h part of the target is the reversal of known origin noise; at h = 1, 2 (overlapping windows, small real change) that part is large, which GBT can learn from the lag features and persistence cannot; the GBT gain at h = 1, 2 is therefore not evidence of forecasting real bank movement.
- Detectability above 5% at h = 1 (the share expected from noise alone) includes edge switches and real year-to-year wobble that the white-noise model does not capture; with sigma 4.7 m it is lower but similar.
- GBT conformal scores are spatial out-of-fold residuals of years the model was also fitted on (other blocks); baseline scores are true residuals. Interval width CIs are near-degenerate because the half-width is one number per target year.
- h = 7: GBT only for targets 2022-2024 (5,936-18,325 training rows); h = 10: no GBT (no training targets before the origins). The sampling analysis keeps the annual spike removal and 2012 has no composite.

## Noise floor

d(t) = mean of the valid annual positions in t-1..t+1 (weights w = 1/n). With white composite noise sigma, SD[d(t+h) - d(t)] = sigma sqrt(sum_y (w_{t+h,y} - w_{t,y})^2), computed per row (exact for the overlapping windows at h = 1, 2 and for missing years). 95% floor = 1.96 SD. Full windows: h >= 3: 1.96 sigma sqrt(2/3) = 5.8 m (sigma 3.6) / 7.5 m (sigma 4.7); h = 2: 1.96 sigma 2/3 = 4.7 / 6.1 m; h = 1: 1.96 sigma sqrt(2)/3 = 3.3 / 4.3 m. sigma = 3.6 m is the measured noise used throughout; 4.7 m is the median robust residual scale of linear series (includes real wobble).

## 1. Detectability by horizon

Share (%) of rows (included transect-side x usable origin, all origins 2007..2024-h pooled) whose true change |d(t+h) - d(t)| exceeds the 95% noise floor of that row.

### sigma = 3.6 m

|   h (yr) |   median floor (m) |   rows | All               | Tiền main         | Hậu wide          | Hậu narrow        | Island channels   |
|---------:|-------------------:|-------:|:------------------|:------------------|:------------------|:------------------|:------------------|
|        1 |                3.3 |  93279 | 27.3 [22.9, 31.9] | 29.1 [22.7, 36.1] | 15.4 [12.3, 20.2] | 21.2 [15.8, 26.3] | 32.3 [23.8, 41.2] |
|        2 |                4.7 |  84544 | 33.8 [28.6, 38.9] | 35.9 [28.4, 43.7] | 19.3 [16.1, 24.5] | 26.5 [20.5, 32.4] | 39.5 [31.2, 48.6] |
|        3 |                5.8 |  77536 | 37.9 [32.7, 43.2] | 40.0 [32.4, 48.0] | 20.9 [16.7, 28.5] | 29.7 [23.3, 35.8] | 44.1 [35.3, 53.8] |
|        4 |                5.8 |  71653 | 43.5 [38.3, 49.4] | 45.6 [37.8, 53.7] | 26.0 [19.9, 35.0] | 34.5 [27.3, 41.0] | 50.3 [42.0, 59.4] |
|        5 |                6.4 |  68216 | 48.7 [43.0, 54.0] | 50.5 [43.4, 58.0] | 33.5 [26.9, 45.0] | 39.5 [31.7, 46.2] | 55.4 [47.3, 64.6] |
|        6 |                5.8 |  64273 | 52.6 [47.3, 57.9] | 54.5 [47.3, 62.1] | 41.5 [34.2, 54.3] | 43.3 [35.9, 50.0] | 59.0 [50.8, 67.9] |
|        7 |                5.8 |  60123 | 55.7 [50.8, 60.8] | 57.3 [49.9, 65.0] | 48.8 [41.9, 61.0] | 46.3 [38.9, 52.4] | 61.8 [52.2, 71.8] |
|        8 |                5.8 |  53955 | 58.1 [53.3, 63.3] | 59.4 [52.1, 66.9] | 53.4 [46.4, 65.8] | 48.5 [41.3, 54.2] | 64.0 [54.8, 74.2] |
|        9 |                6.4 |  47744 | 60.5 [55.5, 65.6] | 61.6 [54.5, 68.9] | 56.5 [49.2, 69.7] | 51.3 [43.8, 57.1] | 65.9 [57.0, 76.0] |
|       10 |                6.4 |  41471 | 63.1 [58.0, 68.1] | 64.2 [57.4, 71.3] | 60.5 [52.8, 74.7] | 54.1 [46.6, 59.8] | 67.8 [59.1, 78.2] |

### sigma = 4.7 m

|   h (yr) |   median floor (m) |   rows | All               | Tiền main         | Hậu wide          | Hậu narrow        | Island channels   |
|---------:|-------------------:|-------:|:------------------|:------------------|:------------------|:------------------|:------------------|
|        1 |                4.3 |  93279 | 20.9 [16.9, 25.3] | 22.4 [16.7, 28.7] | 10.0 [7.5, 13.9]  | 14.8 [10.4, 19.3] | 25.9 [17.7, 34.6] |
|        2 |                6.1 |  84544 | 26.9 [21.9, 31.8] | 28.9 [22.0, 36.2] | 12.7 [9.9, 17.5]  | 19.4 [14.1, 25.0] | 32.6 [23.8, 42.1] |
|        3 |                7.5 |  77536 | 30.7 [25.6, 36.1] | 32.9 [25.5, 40.6] | 14.5 [11.1, 21.5] | 21.9 [15.9, 27.9] | 37.0 [27.9, 47.0] |
|        4 |                7.5 |  71653 | 36.2 [30.8, 42.3] | 38.5 [30.8, 46.6] | 18.5 [13.6, 26.4] | 26.4 [19.6, 32.9] | 43.2 [33.7, 52.7] |
|        5 |                8.4 |  68216 | 41.4 [35.4, 46.9] | 43.7 [36.2, 51.5] | 25.1 [18.7, 35.8] | 31.0 [23.7, 37.6] | 48.5 [39.5, 58.0] |
|        6 |                7.5 |  64273 | 45.3 [39.5, 50.8] | 47.3 [39.6, 55.4] | 32.6 [25.0, 45.1] | 34.9 [27.5, 41.8] | 52.5 [44.0, 61.9] |
|        7 |                7.5 |  60123 | 48.6 [43.4, 54.2] | 50.4 [42.6, 58.6] | 40.3 [32.3, 54.0] | 38.1 [30.5, 44.1] | 55.5 [45.7, 66.0] |
|        8 |                7.5 |  53955 | 51.2 [46.0, 56.7] | 52.9 [45.1, 60.9] | 44.8 [37.0, 58.5] | 40.3 [32.7, 46.2] | 57.8 [48.4, 68.1] |
|        9 |                8.4 |  47744 | 53.7 [48.3, 59.3] | 55.3 [47.5, 63.3] | 48.7 [40.5, 62.5] | 42.9 [35.2, 48.8] | 59.9 [50.2, 70.7] |
|       10 |                8.4 |  41471 | 56.2 [50.6, 61.9] | 57.2 [49.4, 65.3] | 53.2 [45.1, 67.3] | 45.8 [37.8, 51.6] | 62.1 [52.0, 73.4] |

## 2. Forecast skill by horizon (rolling origins)

Design: for each target year Y in 2019-2024, origin t = Y - h. GBT (features of forecast.py, confirmatory point hyperparameters {'learning_rate': 0.05, 'max_leaf_nodes': 15, 'min_samples_leaf': 100}, absolute error, 300 iterations; not re-tuned) is fitted on all rows whose target year <= t - 1, so every position it sees (including year target + 1 inside the centred mean) is <= t. Split conformal (90%): scores on the 3 most recent target years <= t - 1; baselines: plain residuals; GBT: 5-fold spatial-block (GroupKFold over 10 km blocks) out-of-fold residuals of the same training fit. A (h, Y) with < 1000 training rows gets no GBT. Noise-only MAE = mean of sigma f sqrt(2/pi) over the rows (the MAE a perfect forecast would score against the noisy 3-yr-mean positions).

Training rows per (h, target year):

|   h | 2019       | 2020       | 2021       | 2022       | 2023       | 2024       |
|----:|:-----------|:-----------|:-----------|:-----------|:-----------|:-----------|
|   1 | 49733      | 56007      | 62328      | 68593      | 74773      | 80952      |
|   2 | 34722      | 40988      | 47260      | 53522      | 59790      | 65969      |
|   3 | 23727      | 27770      | 33946      | 40267      | 46528      | 52783      |
|   4 | 16886      | 20228      | 24047      | 28089      | 34320      | 40637      |
|   5 | 7765       | 13851      | 19775      | 23116      | 26934      | 30980      |
|   7 | 0 (no GBT) | 0 (no GBT) | 0 (no GBT) | 5936       | 12186      | 18325      |
|  10 | 0 (no GBT) | 0 (no GBT) | 0 (no GBT) | 0 (no GBT) | 0 (no GBT) | 0 (no GBT) |

### Rows with a GBT forecast (all models on the same rows; split-conformal coverage and width)

|   h (yr) | model                     | MAE (m)           | MAE - persistence (m)   |   MAE / noise-only MAE | coverage (%)      | mean width (m)       |
|---------:|:--------------------------|:------------------|:------------------------|-----------------------:|:------------------|:---------------------|
|        1 | Persistence               | 3.9 [3.1, 4.7]    | -                       |                    2.9 | 90.9 [87.8, 93.6] | 16.5 [16.5, 16.5]    |
|        1 | Theil-Sen, last 10 yr     | 4.4 [3.5, 5.4]    | +0.54 [+0.38, +0.70]    |                    3.3 | 91.4 [88.5, 94.1] | 19.2 [19.2, 19.2]    |
|        1 | Theil-Sen, all years <= t | 5.3 [4.0, 6.8]    | +1.46 [+0.85, +2.24]    |                    4   | 91.0 [87.5, 94.2] | 25.1 [25.1, 25.1]    |
|        1 | GBT                       | 3.0 [2.4, 3.6]    | -0.90 [-1.14, -0.69]    |                    2.2 | 90.9 [88.1, 93.4] | 11.8 [11.8, 11.8]    |
|        2 | Persistence               | 7.0 [5.5, 8.7]    | -                       |                    3.6 | 91.0 [87.7, 93.8] | 32.4 [32.4, 32.4]    |
|        2 | Theil-Sen, last 10 yr     | 8.6 [6.6, 10.7]   | +1.54 [+1.04, +2.07]    |                    4.4 | 92.3 [89.4, 94.9] | 42.1 [42.0, 42.1]    |
|        2 | Theil-Sen, all years <= t | 10.2 [7.6, 13.2]  | +3.15 [+1.81, +4.96]    |                    5.3 | 91.6 [88.1, 94.7] | 52.3 [52.2, 52.3]    |
|        2 | GBT                       | 6.7 [5.4, 8.1]    | -0.37 [-0.72, -0.05]    |                    3.4 | 90.3 [87.3, 93.0] | 26.7 [26.7, 26.7]    |
|        3 | Persistence               | 9.9 [7.7, 12.3]   | -                       |                    4.1 | 92.5 [89.4, 95.1] | 56.0 [55.9, 56.1]    |
|        3 | Theil-Sen, last 10 yr     | 12.8 [9.6, 16.2]  | +2.92 [+1.82, +4.22]    |                    5.3 | 93.6 [91.0, 95.9] | 76.4 [76.3, 76.5]    |
|        3 | Theil-Sen, all years <= t | 15.0 [10.9, 19.8] | +5.13 [+2.88, +8.18]    |                    6.3 | 92.4 [89.2, 95.4] | 87.3 [87.3, 87.5]    |
|        3 | GBT                       | 9.7 [7.8, 11.7]   | -0.23 [-0.70, +0.30]    |                    4   | 91.8 [89.0, 94.2] | 47.0 [46.9, 47.1]    |
|        4 | Persistence               | 12.2 [9.3, 15.5]  | -                       |                    5.1 | 93.8 [90.8, 96.3] | 81.7 [81.6, 81.9]    |
|        4 | Theil-Sen, last 10 yr     | 16.8 [12.2, 21.9] | +4.62 [+2.76, +6.93]    |                    7   | 94.8 [92.5, 96.8] | 115.3 [115.1, 115.4] |
|        4 | Theil-Sen, all years <= t | 19.8 [14.1, 26.6] | +7.58 [+4.16, +12.31]   |                    8.3 | 93.1 [89.8, 95.9] | 123.8 [123.7, 123.9] |
|        4 | GBT                       | 12.3 [9.6, 15.5]  | +0.11 [-0.37, +0.59]    |                    5.1 | 92.8 [90.0, 95.4] | 69.4 [69.3, 69.5]    |
|        5 | Persistence               | 14.6 [10.9, 18.8] | -                       |                    6.1 | 94.6 [91.9, 97.1] | 110.6 [110.6, 110.7] |
|        5 | Theil-Sen, last 10 yr     | 21.4 [15.2, 28.5] | +6.79 [+3.89, +10.68]   |                    8.9 | 94.7 [92.4, 96.9] | 150.6 [150.5, 150.6] |
|        5 | Theil-Sen, all years <= t | 25.2 [17.4, 35.3] | +10.61 [+5.48, +18.02]  |                   10.5 | 92.9 [89.1, 96.0] | 154.5 [154.5, 154.5] |
|        5 | GBT                       | 15.6 [12.5, 19.2] | +0.97 [+0.10, +1.85]    |                    6.5 | 94.1 [91.5, 96.4] | 92.6 [92.6, 92.7]    |
|        7 | Persistence               | 18.0 [13.4, 23.3] | -                       |                    7.4 | 94.8 [92.1, 97.1] | 139.9 [139.9, 140.0] |
|        7 | Theil-Sen, last 10 yr     | 30.1 [20.5, 41.1] | +12.13 [+6.80, +18.82]  |                   12.3 | 93.8 [91.0, 96.4] | 188.2 [188.2, 188.2] |
|        7 | Theil-Sen, all years <= t | 34.7 [23.6, 48.4] | +16.65 [+9.05, +27.13]  |                   14.2 | 91.7 [87.5, 95.1] | 188.2 [188.2, 188.2] |
|        7 | GBT                       | 18.7 [14.3, 23.6] | +0.70 [-0.91, +2.46]    |                    7.7 | 94.1 [91.6, 96.5] | 114.5 [114.5, 114.6] |

### Every 2019-2024 target row (h = 7, 10: baselines only where GBT could not be fitted; h <= 5 identical to the table above)

|   h (yr) | model                     | MAE (m)            | MAE - persistence (m)   |   MAE / noise-only MAE |
|---------:|:--------------------------|:-------------------|:------------------------|-----------------------:|
|        1 | Persistence               | 3.9 [3.1, 4.7]     | -                       |                    2.9 |
|        1 | Theil-Sen, last 10 yr     | 4.4 [3.5, 5.4]     | +0.54 [+0.38, +0.70]    |                    3.3 |
|        1 | Theil-Sen, all years <= t | 5.3 [4.0, 6.8]     | +1.46 [+0.85, +2.24]    |                    4   |
|        1 | GBT                       | 3.0 [2.4, 3.6]     | -0.90 [-1.14, -0.69]    |                    2.2 |
|        2 | Persistence               | 7.0 [5.5, 8.7]     | -                       |                    3.6 |
|        2 | Theil-Sen, last 10 yr     | 8.6 [6.6, 10.7]    | +1.54 [+1.04, +2.07]    |                    4.4 |
|        2 | Theil-Sen, all years <= t | 10.2 [7.6, 13.2]   | +3.15 [+1.81, +4.96]    |                    5.3 |
|        2 | GBT                       | 6.7 [5.4, 8.1]     | -0.37 [-0.72, -0.05]    |                    3.4 |
|        3 | Persistence               | 9.9 [7.7, 12.3]    | -                       |                    4.1 |
|        3 | Theil-Sen, last 10 yr     | 12.8 [9.6, 16.2]   | +2.92 [+1.82, +4.22]    |                    5.3 |
|        3 | Theil-Sen, all years <= t | 15.0 [10.9, 19.8]  | +5.13 [+2.88, +8.18]    |                    6.3 |
|        3 | GBT                       | 9.7 [7.8, 11.7]    | -0.23 [-0.70, +0.30]    |                    4   |
|        4 | Persistence               | 12.2 [9.3, 15.5]   | -                       |                    5.1 |
|        4 | Theil-Sen, last 10 yr     | 16.8 [12.2, 21.9]  | +4.62 [+2.76, +6.93]    |                    7   |
|        4 | Theil-Sen, all years <= t | 19.8 [14.1, 26.6]  | +7.58 [+4.16, +12.31]   |                    8.3 |
|        4 | GBT                       | 12.3 [9.6, 15.5]   | +0.11 [-0.37, +0.59]    |                    5.1 |
|        5 | Persistence               | 14.6 [10.9, 18.8]  | -                       |                    6.1 |
|        5 | Theil-Sen, last 10 yr     | 21.4 [15.2, 28.5]  | +6.79 [+3.89, +10.68]   |                    8.9 |
|        5 | Theil-Sen, all years <= t | 25.2 [17.4, 35.3]  | +10.61 [+5.48, +18.02]  |                   10.5 |
|        5 | GBT                       | 15.6 [12.5, 19.2]  | +0.97 [+0.10, +1.85]    |                    6.5 |
|        7 | Persistence               | 20.4 [14.7, 26.5]  | -                       |                    8.2 |
|        7 | Theil-Sen, last 10 yr     | 32.8 [22.7, 43.2]  | +12.41 [+7.26, +17.93]  |                   13.2 |
|        7 | Theil-Sen, all years <= t | 37.3 [25.9, 50.5]  | +16.95 [+9.51, +27.09]  |                   15   |
|       10 | Persistence               | 33.1 [21.5, 46.4]  | -                       |                   12.8 |
|       10 | Theil-Sen, last 10 yr     | 62.5 [38.7, 92.5]  | +29.39 [+13.65, +52.76] |                   24.2 |
|       10 | Theil-Sen, all years <= t | 66.4 [39.7, 102.3] | +33.37 [+14.06, +63.13] |                   25.8 |

### Row sets

|   h | set     |     n |   blocks | years     | n_train     |   floor |   noise_mae |   med_abs_change |
|----:|:--------|------:|---------:|:----------|:------------|--------:|------------:|-----------------:|
|   1 | matched | 37272 |       28 | 2019-2024 | 49733-80952 |    3.33 |        1.32 |             1.53 |
|   1 | all     | 37272 |       28 | 2019-2024 | 49733-80952 |    3.33 |        1.32 |             1.53 |
|   2 | matched | 37284 |       28 | 2019-2024 | 34722-65969 |    4.7  |        1.94 |             2.6  |
|   2 | all     | 37284 |       28 | 2019-2024 | 34722-65969 |    4.7  |        1.94 |             2.6  |
|   3 | matched | 37269 |       28 | 2019-2024 | 23727-52783 |    5.76 |        2.4  |             3.67 |
|   3 | all     | 37269 |       28 | 2019-2024 | 23727-52783 |    5.76 |        2.4  |             3.67 |
|   4 | matched | 37333 |       28 | 2019-2024 | 16886-40637 |    5.76 |        2.4  |             4.34 |
|   4 | all     | 37333 |       28 | 2019-2024 | 16886-40637 |    5.76 |        2.4  |             4.34 |
|   5 | matched | 37236 |       28 | 2019-2024 | 7765-30980  |    5.76 |        2.41 |             5.07 |
|   5 | all     | 37236 |       28 | 2019-2024 | 7765-30980  |    5.76 |        2.41 |             5.07 |
|   7 | matched | 18566 |       28 | 2022-2024 | 5936-18325  |    5.76 |        2.44 |             6.21 |
|   7 | all     | 32587 |       28 | 2019-2024 | 0-18325     |    6.44 |        2.49 |             6.67 |
|  10 | all     | 29252 |       28 | 2019-2024 | 0-0         |    6.44 |        2.58 |             9.86 |

## 3. Sampling interval

Included transect-sides (>= 15 valid years). Every k-th year: all k phases; m dates: 2000 and 2024 kept, m - 2 interior years drawn without replacement from years with a composite (20 draws, seed 0); 2012 has no composite and is dropped where it falls in a set. Theil-Sen needs >= 2 valid dates. 'Significant' = |rate| > 1.96 x 3.6 / sqrt(sum (t - mean t)^2) over the transect-side's valid dates. Spike removal of the annual series is kept (a sparse study could not detect reverting jumps).

### (a) Theil-Sen rate 2000-2024 vs the full annual series

| date set   |   configs | dates (valid)   |   computable (%) | median |rate error| (m/yr) [range over configs]   | median bias (m/yr) [range]   | sign changed (%)   | 'significant' status changed (%)   | significant, full -> thinned (%)   |
|:-----------|----------:|:----------------|-----------------:|:--------------------------------------------------|:-----------------------------|:-------------------|:-----------------------------------|:-----------------------------------|
| annual     |         1 | 24-24           |            100   | 0.00 [0.00, 0.00]                                 | +0.00 [+0.00, +0.00]         | 0.0 [0.0, 0.0]     | 0.0 [0.0, 0.0]                     | 84 -> 84                           |
| every 2 yr |         2 | 12-12           |            100   | 0.10 [0.09, 0.10]                                 | -0.00 [-0.00, +0.00]         | 3.5 [2.8, 4.2]     | 6.7 [6.1, 7.3]                     | 84 -> 79                           |
| every 3 yr |         3 | 8-8             |            100   | 0.15 [0.13, 0.17]                                 | -0.00 [-0.03, +0.02]         | 5.4 [4.3, 6.4]     | 10.4 [9.4, 11.6]                   | 84 -> 76                           |
| every 5 yr |         5 | 4-5             |            100   | 0.25 [0.22, 0.29]                                 | -0.03 [-0.12, +0.02]         | 8.3 [6.9, 9.6]     | 15.3 [14.0, 16.7]                  | 84 -> 72                           |
| 4 dates    |        20 | 4-4             |             99.8 | 0.35 [0.26, 0.66]                                 | +0.10 [+0.06, +0.20]         | 11.7 [10.0, 13.9]  | 16.7 [15.1, 18.6]                  | 84 -> 74                           |
| 6 dates    |        20 | 6-6             |            100   | 0.25 [0.16, 0.44]                                 | +0.05 [-0.01, +0.13]         | 9.0 [7.7, 10.5]    | 14.2 [12.9, 15.6]                  | 84 -> 75                           |
| 9 dates    |        20 | 9-9             |            100   | 0.19 [0.13, 0.43]                                 | +0.03 [-0.03, +0.08]         | 6.5 [5.4, 7.7]     | 10.5 [9.6, 11.7]                   | 84 -> 78                           |

### (b) Forecast error of Theil-Sen extrapolation fitted on the thinned dates <= t (targets 2019-2024)

|   h (yr) | date set   | MAE (m) pooled [95% CI]   | MAE range over configs   |   fallback to persistence (%) |
|---------:|:-----------|:--------------------------|:-------------------------|------------------------------:|
|        3 | annual     | 15.0 [10.9, 19.8]         | 15.0-15.0                |                           0   |
|        3 | every 2 yr | 16.0 [11.4, 21.5]         | 15.4-16.5                |                           0   |
|        3 | every 3 yr | 17.0 [11.7, 23.6]         | 15.8-17.7                |                           0   |
|        3 | every 5 yr | 18.9 [12.5, 27.6]         | 16.7-20.8                |                           0.2 |
|        3 | 4 dates    | 23.2 [15.2, 34.2]         | 15.7-37.6                |                           4.1 |
|        3 | 6 dates    | 19.6 [13.0, 28.8]         | 14.0-26.1                |                           0.1 |
|        3 | 9 dates    | 17.9 [12.2, 25.8]         | 13.0-21.4                |                           0   |
|        5 | annual     | 25.2 [17.4, 35.3]         | 25.2-25.2                |                           0   |
|        5 | every 2 yr | 27.1 [18.3, 38.9]         | 26.0-28.3                |                           0   |
|        5 | every 3 yr | 29.2 [19.1, 42.5]         | 26.1-30.8                |                           0   |
|        5 | every 5 yr | 33.6 [20.9, 51.7]         | 29.7-38.5                |                           0.5 |
|        5 | 4 dates    | 37.3 [24.3, 55.4]         | 19.5-68.3                |                          14   |
|        5 | 6 dates    | 33.9 [21.4, 51.7]         | 25.2-50.7                |                           2.7 |
|        5 | 9 dates    | 30.3 [19.4, 45.5]         | 23.9-36.9                |                           0.1 |
