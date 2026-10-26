# EXPLORATORY: forecast horizon and sampling interval (plan A)

**Exploratory** (docs/exploratory_plan.md section A, written before running). Nothing here changes a confirmatory verdict in results/p2/forecast.md, and no pass/fail verdict is given. `python src/explore_horizon.py` (164 s). Rows, inclusion and the 3-yr centred target are those of src/forecast.py (functions imported). CIs: 95% block bootstrap over 10 km blocks (1,000 resamples, seed 0); retreat + = landward.

## Summary (exploratory, plain language)

- Real bank change is above the composite noise for 27% of bank-point-years at 1 yr, 37% at 3 yr, 48% at 5 yr and 62% at 10 yr (sigma 3.6 m); the Hậu wide channel is the slowest up to 6 yr (Hậu narrow beyond), island channels the fastest at every horizon. Even at 10 yr a third of the banks do not move measurably.
- Rate extrapolation (Theil-Sen) is worse than "no change" at every horizon tested (it beats persistence at: none), and its excess error grows with the horizon. GBT is better than persistence (CI of the MAE difference below 0) at h = [1] only, i.e. at horizons where most change is below the noise (see caveats on the centred target); from about 3 yr on it is indistinguishable from persistence or worse.
- Forecast errors are 3-8x the noise-only MAE and grow with h because a minority of banks (edge switches, fast erosion sites) move a lot; split-conformal 90% intervals stay at about 91-95% coverage at every horizon, with widths growing from ~17 m (1 yr) to ~140 m (7 yr, persistence).
- Sparse sampling costs little in the median rate (median |error| 0.09 m/yr every 2nd year, 0.25 every 5th, 0.35 with 4 dates) but changes the sign of 4-12% and the 'significant' status of 7-17% of transect-sides, and inflates extrapolation errors; with 4-6 random dates the result depends strongly on which dates were drawn.

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
|        1 |                3.3 |  90652 | 26.6 [22.7, 31.1] | 29.1 [22.7, 36.1] | 15.4 [12.3, 20.2] | 21.2 [15.8, 26.3] | 30.6 [23.1, 39.7] |
|        2 |                4.7 |  82083 | 33.1 [28.4, 37.7] | 35.9 [28.4, 43.7] | 19.3 [16.1, 24.5] | 26.5 [20.5, 32.4] | 37.7 [30.4, 47.2] |
|        3 |                5.8 |  75240 | 37.0 [32.3, 42.2] | 40.0 [32.4, 48.0] | 20.9 [16.7, 28.5] | 29.7 [23.3, 35.8] | 42.1 [34.2, 51.6] |
|        4 |                5.8 |  69518 | 42.7 [37.8, 48.3] | 45.6 [37.8, 53.7] | 26.0 [19.9, 35.0] | 34.5 [27.3, 41.0] | 48.3 [41.0, 57.7] |
|        5 |                6.4 |  66174 | 47.9 [42.7, 53.0] | 50.5 [43.4, 58.0] | 33.5 [26.9, 45.0] | 39.5 [31.7, 46.2] | 53.6 [46.3, 62.9] |
|        6 |                5.8 |  62396 | 51.9 [46.9, 56.9] | 54.5 [47.3, 62.1] | 41.5 [34.2, 54.3] | 43.3 [35.9, 50.0] | 57.2 [49.7, 66.8] |
|        7 |                5.8 |  58409 | 55.0 [50.3, 60.1] | 57.3 [49.9, 65.0] | 48.8 [41.9, 61.0] | 46.3 [38.9, 52.4] | 60.0 [51.9, 70.7] |
|        8 |                5.8 |  52404 | 57.4 [52.8, 62.5] | 59.4 [52.1, 66.9] | 53.4 [46.4, 65.8] | 48.5 [41.3, 54.2] | 62.3 [54.4, 73.1] |
|        9 |                6.4 |  46357 | 59.8 [55.1, 64.8] | 61.6 [54.5, 68.9] | 56.5 [49.2, 69.7] | 51.3 [43.8, 57.1] | 64.3 [56.6, 75.2] |
|       10 |                6.4 |  40249 | 62.4 [57.6, 67.3] | 64.2 [57.4, 71.3] | 60.5 [52.8, 74.7] | 54.1 [46.6, 59.8] | 66.3 [58.5, 77.1] |

### sigma = 4.7 m

|   h (yr) |   median floor (m) |   rows | All               | Tiền main         | Hậu wide          | Hậu narrow        | Island channels   |
|---------:|-------------------:|-------:|:------------------|:------------------|:------------------|:------------------|:------------------|
|        1 |                4.3 |  90652 | 20.2 [16.5, 24.3] | 22.4 [16.7, 28.7] | 10.0 [7.5, 13.9]  | 14.8 [10.4, 19.3] | 24.2 [16.8, 33.1] |
|        2 |                6.1 |  82083 | 26.1 [21.6, 30.5] | 28.9 [22.0, 36.2] | 12.7 [9.9, 17.5]  | 19.4 [14.1, 25.0] | 30.7 [22.4, 39.7] |
|        3 |                7.5 |  75240 | 29.8 [25.2, 34.7] | 32.9 [25.5, 40.6] | 14.5 [11.1, 21.5] | 21.9 [15.9, 27.9] | 34.9 [26.6, 44.4] |
|        4 |                7.5 |  69518 | 35.3 [30.3, 40.9] | 38.5 [30.8, 46.6] | 18.5 [13.6, 26.4] | 26.4 [19.6, 32.9] | 41.0 [33.1, 50.9] |
|        5 |                8.4 |  66174 | 40.5 [35.2, 45.7] | 43.7 [36.2, 51.5] | 25.1 [18.7, 35.8] | 31.0 [23.7, 37.6] | 46.3 [38.3, 55.6] |
|        6 |                7.5 |  62396 | 44.4 [39.2, 49.7] | 47.3 [39.6, 55.4] | 32.6 [25.0, 45.1] | 34.9 [27.5, 41.8] | 50.5 [42.6, 60.1] |
|        7 |                7.5 |  58409 | 47.8 [42.7, 53.2] | 50.4 [42.6, 58.6] | 40.3 [32.3, 54.0] | 38.1 [30.5, 44.1] | 53.5 [45.1, 64.4] |
|        8 |                7.5 |  52404 | 50.4 [45.3, 55.8] | 52.9 [45.1, 60.9] | 44.8 [37.0, 58.5] | 40.3 [32.7, 46.2] | 55.9 [47.5, 67.1] |
|        9 |                8.4 |  46357 | 52.9 [47.7, 58.5] | 55.3 [47.5, 63.3] | 48.7 [40.5, 62.5] | 42.9 [35.2, 48.8] | 58.0 [49.4, 69.7] |
|       10 |                8.4 |  40249 | 55.4 [50.2, 60.9] | 57.2 [49.4, 65.3] | 53.2 [45.1, 67.3] | 45.8 [37.8, 51.6] | 60.2 [51.7, 72.2] |

## 2. Forecast skill by horizon (rolling origins)

Design: for each target year Y in 2019-2024, origin t = Y - h. GBT (features of forecast.py, confirmatory point hyperparameters {'learning_rate': 0.05, 'max_leaf_nodes': 15, 'min_samples_leaf': 100}, absolute error, 300 iterations; not re-tuned) is fitted on all rows whose target year <= t - 1, so every position it sees (including year target + 1 inside the centred mean) is <= t. Split conformal (90%): scores on the 3 most recent target years <= t - 1; baselines: plain residuals; GBT: 5-fold spatial-block (GroupKFold over 10 km blocks) out-of-fold residuals of the same training fit. A (h, Y) with < 1000 training rows gets no GBT. Noise-only MAE = mean of sigma f sqrt(2/pi) over the rows (the MAE a perfect forecast would score against the noisy 3-yr-mean positions).

Training rows per (h, target year):

|   h | 2019       | 2020       | 2021       | 2022       | 2023       | 2024       |
|----:|:-----------|:-----------|:-----------|:-----------|:-----------|:-----------|
|   1 | 48252      | 54363      | 60520      | 66621      | 72637      | 78652      |
|   2 | 33570      | 39672      | 45781      | 51880      | 57984      | 63999      |
|   3 | 22903      | 26783      | 32795      | 38952      | 45050      | 51142      |
|   4 | 16310      | 19564      | 23220      | 27099      | 33166      | 39319      |
|   5 | 7445       | 13367      | 19127      | 22381      | 26036      | 29919      |
|   7 | 0 (no GBT) | 0 (no GBT) | 0 (no GBT) | 5779       | 11866      | 17842      |
|  10 | 0 (no GBT) | 0 (no GBT) | 0 (no GBT) | 0 (no GBT) | 0 (no GBT) | 0 (no GBT) |

### Rows with a GBT forecast (all models on the same rows; split-conformal coverage and width)

|   h (yr) | model                     | MAE (m)           | MAE - persistence (m)   |   MAE / noise-only MAE | coverage (%)      | mean width (m)       |
|---------:|:--------------------------|:------------------|:------------------------|-----------------------:|:------------------|:---------------------|
|        1 | Persistence               | 3.7 [3.0, 4.4]    | -                       |                    2.8 | 90.8 [88.0, 93.2] | 15.7 [15.6, 15.7]    |
|        1 | Theil-Sen, last 10 yr     | 4.2 [3.4, 5.2]    | +0.55 [+0.40, +0.72]    |                    3.2 | 91.5 [88.6, 93.9] | 18.5 [18.5, 18.5]    |
|        1 | Theil-Sen, all years <= t | 5.2 [3.9, 6.6]    | +1.49 [+0.87, +2.30]    |                    3.9 | 91.1 [87.8, 94.1] | 24.7 [24.7, 24.7]    |
|        1 | GBT                       | 2.8 [2.3, 3.4]    | -0.85 [-1.05, -0.68]    |                    2.1 | 90.8 [88.2, 93.0] | 11.2 [11.2, 11.2]    |
|        2 | Persistence               | 6.6 [5.3, 8.1]    | -                       |                    3.4 | 90.9 [87.9, 93.4] | 30.2 [30.2, 30.2]    |
|        2 | Theil-Sen, last 10 yr     | 8.2 [6.5, 10.2]   | +1.59 [+1.06, +2.17]    |                    4.2 | 92.3 [89.6, 94.7] | 40.6 [40.5, 40.6]    |
|        2 | Theil-Sen, all years <= t | 9.9 [7.4, 12.9]   | +3.26 [+1.87, +5.11]    |                    5.1 | 91.6 [88.1, 94.6] | 51.2 [51.2, 51.2]    |
|        2 | GBT                       | 6.4 [5.3, 7.6]    | -0.23 [-0.51, +0.03]    |                    3.3 | 90.3 [87.5, 92.7] | 25.5 [25.5, 25.5]    |
|        3 | Persistence               | 9.3 [7.4, 11.4]   | -                       |                    3.9 | 92.3 [89.4, 94.6] | 51.2 [51.1, 51.3]    |
|        3 | Theil-Sen, last 10 yr     | 12.3 [9.4, 15.5]  | +2.99 [+1.84, +4.36]    |                    5.1 | 93.6 [91.1, 95.7] | 72.2 [72.2, 72.4]    |
|        3 | Theil-Sen, all years <= t | 14.6 [10.7, 19.5] | +5.33 [+3.01, +8.49]    |                    6.1 | 92.2 [88.8, 95.2] | 83.6 [83.6, 83.7]    |
|        3 | GBT                       | 9.1 [7.4, 10.9]   | -0.23 [-0.57, +0.15]    |                    3.8 | 91.3 [88.5, 93.7] | 43.2 [43.2, 43.3]    |
|        4 | Persistence               | 11.4 [8.9, 14.1]  | -                       |                    4.7 | 93.7 [91.0, 95.9] | 75.0 [74.9, 75.2]    |
|        4 | Theil-Sen, last 10 yr     | 16.1 [12.0, 20.8] | +4.70 [+2.77, +7.08]    |                    6.7 | 94.7 [92.5, 96.5] | 108.9 [108.8, 109.1] |
|        4 | Theil-Sen, all years <= t | 19.3 [13.8, 26.3] | +7.87 [+4.34, +12.72]   |                    8   | 92.7 [89.1, 95.6] | 116.8 [116.7, 116.9] |
|        4 | GBT                       | 11.6 [9.3, 14.1]  | +0.26 [-0.23, +0.71]    |                    4.9 | 92.5 [89.8, 94.9] | 62.7 [62.6, 62.8]    |
|        5 | Persistence               | 13.6 [10.5, 17.0] | -                       |                    5.6 | 94.8 [92.3, 96.9] | 103.1 [103.0, 103.2] |
|        5 | Theil-Sen, last 10 yr     | 20.4 [14.9, 27.2] | +6.89 [+3.90, +10.81]   |                    8.5 | 94.6 [92.2, 96.6] | 140.7 [140.7, 140.7] |
|        5 | Theil-Sen, all years <= t | 24.6 [17.1, 34.4] | +11.04 [+5.75, +18.41]  |                   10.2 | 92.3 [88.3, 95.5] | 143.8 [143.8, 143.8] |
|        5 | GBT                       | 13.9 [11.1, 17.0] | +0.38 [-0.47, +1.14]    |                    5.8 | 93.6 [91.1, 95.8] | 83.4 [83.3, 83.4]    |
|        7 | Persistence               | 16.7 [12.8, 21.0] | -                       |                    6.8 | 95.0 [92.7, 97.1] | 131.6 [131.5, 131.6] |
|        7 | Theil-Sen, last 10 yr     | 28.9 [20.1, 39.3] | +12.20 [+6.80, +19.06]  |                   11.8 | 93.7 [91.0, 96.0] | 176.1 [176.0, 176.1] |
|        7 | Theil-Sen, all years <= t | 34.0 [23.2, 47.7] | +17.30 [+9.52, +27.85]  |                   13.9 | 91.0 [86.6, 94.6] | 176.1 [176.0, 176.1] |
|        7 | GBT                       | 17.6 [13.7, 22.1] | +0.97 [-0.52, +2.38]    |                    7.2 | 94.1 [91.6, 96.4] | 110.5 [110.5, 110.6] |

### Every 2019-2024 target row (h = 7, 10: baselines only where GBT could not be fitted; h <= 5 identical to the table above)

|   h (yr) | model                     | MAE (m)            | MAE - persistence (m)   |   MAE / noise-only MAE |
|---------:|:--------------------------|:-------------------|:------------------------|-----------------------:|
|        1 | Persistence               | 3.7 [3.0, 4.4]     | -                       |                    2.8 |
|        1 | Theil-Sen, last 10 yr     | 4.2 [3.4, 5.2]     | +0.55 [+0.40, +0.72]    |                    3.2 |
|        1 | Theil-Sen, all years <= t | 5.2 [3.9, 6.6]     | +1.49 [+0.87, +2.30]    |                    3.9 |
|        1 | GBT                       | 2.8 [2.3, 3.4]     | -0.85 [-1.05, -0.68]    |                    2.1 |
|        2 | Persistence               | 6.6 [5.3, 8.1]     | -                       |                    3.4 |
|        2 | Theil-Sen, last 10 yr     | 8.2 [6.5, 10.2]    | +1.59 [+1.06, +2.17]    |                    4.2 |
|        2 | Theil-Sen, all years <= t | 9.9 [7.4, 12.9]    | +3.26 [+1.87, +5.11]    |                    5.1 |
|        2 | GBT                       | 6.4 [5.3, 7.6]     | -0.23 [-0.51, +0.03]    |                    3.3 |
|        3 | Persistence               | 9.3 [7.4, 11.4]    | -                       |                    3.9 |
|        3 | Theil-Sen, last 10 yr     | 12.3 [9.4, 15.5]   | +2.99 [+1.84, +4.36]    |                    5.1 |
|        3 | Theil-Sen, all years <= t | 14.6 [10.7, 19.5]  | +5.33 [+3.01, +8.49]    |                    6.1 |
|        3 | GBT                       | 9.1 [7.4, 10.9]    | -0.23 [-0.57, +0.15]    |                    3.8 |
|        4 | Persistence               | 11.4 [8.9, 14.1]   | -                       |                    4.7 |
|        4 | Theil-Sen, last 10 yr     | 16.1 [12.0, 20.8]  | +4.70 [+2.77, +7.08]    |                    6.7 |
|        4 | Theil-Sen, all years <= t | 19.3 [13.8, 26.3]  | +7.87 [+4.34, +12.72]   |                    8   |
|        4 | GBT                       | 11.6 [9.3, 14.1]   | +0.26 [-0.23, +0.71]    |                    4.9 |
|        5 | Persistence               | 13.6 [10.5, 17.0]  | -                       |                    5.6 |
|        5 | Theil-Sen, last 10 yr     | 20.4 [14.9, 27.2]  | +6.89 [+3.90, +10.81]   |                    8.5 |
|        5 | Theil-Sen, all years <= t | 24.6 [17.1, 34.4]  | +11.04 [+5.75, +18.41]  |                   10.2 |
|        5 | GBT                       | 13.9 [11.1, 17.0]  | +0.38 [-0.47, +1.14]    |                    5.8 |
|        7 | Persistence               | 18.7 [14.2, 23.3]  | -                       |                    7.5 |
|        7 | Theil-Sen, last 10 yr     | 31.4 [22.4, 41.1]  | +12.73 [+7.34, +18.71]  |                   12.6 |
|        7 | Theil-Sen, all years <= t | 36.4 [25.5, 49.7]  | +17.70 [+9.81, +27.90]  |                   14.6 |
|       10 | Persistence               | 30.7 [21.0, 41.4]  | -                       |                   11.9 |
|       10 | Theil-Sen, last 10 yr     | 61.4 [37.7, 92.0]  | +30.68 [+14.48, +53.99] |                   23.8 |
|       10 | Theil-Sen, all years <= t | 65.5 [38.6, 102.3] | +34.79 [+15.12, +64.59] |                   25.4 |

### Row sets

|   h | set     |     n |   blocks | years     | n_train     |   floor |   noise_mae |   med_abs_change |
|----:|:--------|------:|---------:|:----------|:------------|--------:|------------:|-----------------:|
|   1 | matched | 36289 |       28 | 2019-2024 | 48252-78652 |    3.33 |        1.32 |             1.51 |
|   1 | all     | 36289 |       28 | 2019-2024 | 48252-78652 |    3.33 |        1.32 |             1.51 |
|   2 | matched | 36302 |       28 | 2019-2024 | 33570-63999 |    4.7  |        1.94 |             2.55 |
|   2 | all     | 36302 |       28 | 2019-2024 | 33570-63999 |    4.7  |        1.94 |             2.55 |
|   3 | matched | 36288 |       28 | 2019-2024 | 22903-51142 |    5.76 |        2.4  |             3.59 |
|   3 | all     | 36288 |       28 | 2019-2024 | 22903-51142 |    5.76 |        2.4  |             3.59 |
|   4 | matched | 36352 |       28 | 2019-2024 | 16310-39319 |    5.76 |        2.4  |             4.25 |
|   4 | all     | 36352 |       28 | 2019-2024 | 16310-39319 |    5.76 |        2.4  |             4.25 |
|   5 | matched | 36255 |       28 | 2019-2024 | 7445-29919  |    5.76 |        2.41 |             4.96 |
|   5 | all     | 36255 |       28 | 2019-2024 | 7445-29919  |    5.76 |        2.41 |             4.96 |
|   7 | matched | 18076 |       28 | 2022-2024 | 5779-17842  |    5.76 |        2.44 |             6.07 |
|   7 | all     | 31607 |       28 | 2019-2024 | 0-17842     |    6.44 |        2.49 |             6.48 |
|  10 | all     | 28349 |       28 | 2019-2024 | 0-0         |    6.44 |        2.58 |             9.54 |

## 3. Sampling interval

Included transect-sides (>= 15 valid years). Every k-th year: all k phases; m dates: 2000 and 2024 kept, m - 2 interior years drawn without replacement from years with a composite (20 draws, seed 0); 2012 has no composite and is dropped where it falls in a set. Theil-Sen needs >= 2 valid dates. 'Significant' = |rate| > 1.96 x 3.6 / sqrt(sum (t - mean t)^2) over the transect-side's valid dates. Spike removal of the annual series is kept (a sparse study could not detect reverting jumps).

### (a) Theil-Sen rate 2000-2024 vs the full annual series

| date set   |   configs | dates (valid)   |   computable (%) | median |rate error| (m/yr) [range over configs]   | median bias (m/yr) [range]   | sign changed (%)   | 'significant' status changed (%)   | significant, full -> thinned (%)   |
|:-----------|----------:|:----------------|-----------------:|:--------------------------------------------------|:-----------------------------|:-------------------|:-----------------------------------|:-----------------------------------|
| annual     |         1 | 24-24           |            100   | 0.00 [0.00, 0.00]                                 | +0.00 [+0.00, +0.00]         | 0.0 [0.0, 0.0]     | 0.0 [0.0, 0.0]                     | 83 -> 83                           |
| every 2 yr |         2 | 12-12           |            100   | 0.09 [0.09, 0.10]                                 | -0.00 [-0.00, -0.00]         | 3.6 [2.9, 4.3]     | 6.8 [6.1, 7.4]                     | 83 -> 79                           |
| every 3 yr |         3 | 8-8             |            100   | 0.15 [0.13, 0.17]                                 | -0.00 [-0.03, +0.02]         | 5.5 [4.5, 6.4]     | 10.6 [9.6, 11.7]                   | 83 -> 75                           |
| every 5 yr |         5 | 4-5             |            100   | 0.25 [0.22, 0.28]                                 | -0.03 [-0.12, +0.02]         | 8.4 [7.0, 9.6]     | 15.5 [14.2, 16.9]                  | 83 -> 71                           |
| 4 dates    |        20 | 4-4             |             99.8 | 0.35 [0.25, 0.64]                                 | +0.10 [+0.06, +0.21]         | 11.8 [10.1, 14.0]  | 16.9 [15.3, 18.8]                  | 83 -> 74                           |
| 6 dates    |        20 | 6-6             |            100   | 0.25 [0.16, 0.43]                                 | +0.05 [-0.01, +0.13]         | 9.1 [7.8, 10.6]    | 14.4 [13.2, 15.8]                  | 83 -> 75                           |
| 9 dates    |        20 | 9-9             |            100   | 0.18 [0.13, 0.42]                                 | +0.03 [-0.03, +0.08]         | 6.6 [5.5, 7.8]     | 10.7 [9.7, 11.9]                   | 83 -> 77                           |

### (b) Forecast error of Theil-Sen extrapolation fitted on the thinned dates <= t (targets 2019-2024)

|   h (yr) | date set   | MAE (m) pooled [95% CI]   | MAE range over configs   |   fallback to persistence (%) |
|---------:|:-----------|:--------------------------|:-------------------------|------------------------------:|
|        3 | annual     | 14.6 [10.7, 19.5]         | 14.6-14.6                |                           0   |
|        3 | every 2 yr | 15.6 [11.2, 21.3]         | 15.0-16.1                |                           0   |
|        3 | every 3 yr | 16.6 [11.5, 23.3]         | 15.4-17.3                |                           0   |
|        3 | every 5 yr | 18.5 [12.3, 27.1]         | 16.3-20.5                |                           0.2 |
|        3 | 4 dates    | 22.7 [14.9, 33.8]         | 15.1-36.9                |                           4.2 |
|        3 | 6 dates    | 19.3 [12.7, 28.3]         | 13.5-25.6                |                           0.1 |
|        3 | 9 dates    | 17.5 [11.9, 25.2]         | 12.5-21.1                |                           0   |
|        5 | annual     | 24.6 [17.1, 34.4]         | 24.6-24.6                |                           0   |
|        5 | every 2 yr | 26.5 [17.9, 38.0]         | 25.4-27.6                |                           0   |
|        5 | every 3 yr | 28.6 [18.6, 41.8]         | 25.4-30.2                |                           0   |
|        5 | every 5 yr | 33.0 [20.4, 51.3]         | 29.1-38.1                |                           0.5 |
|        5 | 4 dates    | 36.3 [23.4, 54.5]         | 18.5-65.8                |                          14.1 |
|        5 | 6 dates    | 33.2 [20.8, 51.3]         | 24.3-49.7                |                           2.7 |
|        5 | 9 dates    | 29.7 [19.0, 44.9]         | 23.1-36.5                |                           0.1 |
