# P2: transect forecasts with 90% intervals (H1, H2)

`python src/forecast.py` (1884 s). Protocol: docs/protocol.md section 2 + deviation 1 (tag protocol-v1). Test = targets 2019-2024, scored once; every choice below was made on training rows only (CV) or fixed a priori. CIs: 95% block bootstrap over 10 km blocks (1,000 resamples, seed 0). Retreat + = landward (m).

## Setup

- Inputs: lagged positions x(t-k) minus the trailing 3-yr mean (k = 0..5), Theil-Sen rates over 3/5/10 yr (>= 2/3/5 valid years), physical covariates ['curv_bank', 'width_00', 'is_island', 'river_km', 'node_km'] of the 2 km unit (width_00 = median 2000-02 channel width; width_m and dwidth_00_14 use 2000-2014 and are not used, see notes). No exposure variables.
- Groups (Mondrian): Tiền main; Hậu wide; Hậu narrow (channel hau, chainage < 30300 m = tiles.json narrow_until_m 38800 - border 8500; stitch.py uses raw chainage < narrow_until_m); island channels.
- Blocks: 28 blocks of 10 km (main: chainage; islands: island chainage in tiles.json).
- Change zones: Vàm Nao = 2 km units with |vamnao_km| <= 10 (covariates_2km, both rivers and island channels); Mỹ Thuận = Tiền bank points (incl. island channels) within 10 km of the downstream end of the reach at the Mỹ Thuận bridge.
- ACI: one alpha per forecast origin, pooled over transects, alpha_0 = 0.1, step γ = 0.005 (fixed a priori, Gibbs & Candès 2021 default), γ = 0.05 as a sensitivity; feedback from origin s is used from origin s + h on.
- Gaussian interval: ±1.645 SD of the out-of-fold training residuals (learned) or of the training residuals (baselines).

- h = 3, target mean: 6342 transect-sides; rows train 23727, calibration 16540, test 37269; origins {'cal': (2013, 2015), 'test': (2016, 2021), 'train': (2007, 2012)}
- GBT params (CV MAE / pinball): point {'learning_rate': 0.05, 'max_leaf_nodes': 15, 'min_samples_leaf': 100}, q05 {'learning_rate': 0.05, 'max_leaf_nodes': 31, 'min_samples_leaf': 20}, q95 {'learning_rate': 0.05, 'max_leaf_nodes': 15, 'min_samples_leaf': 100}
- GP: kernel matern15 (CV MAE rbf 25.96, matern15 24.43), n = 1000 random training rows (seed 0); fitted 3.55**2 * Matern(length_scale=[2.48e+04, 11.4, 6.34e+04, 1.62e+04, 7.18e+03, 49.9, 8.26e+04, 0.208, 9.69, 4.48, 15.7, 1.12, 1e+05, 1e+05], nu=1.5) + WhiteKernel(noise_level=0.0232)
- Baseline fallback to persistence (rows): {'persistence': 0, 'epr_all': 0, 'epr_10': 0, 'lrr_all': 0, 'lrr_10': 0}
- Gaussian SD (m): persistence 78.2, epr_all 94.4, epr_10 96.4, lrr_all 92.3, lrr_10 92.1, gbt 76.3, gp 94.3
- ACI alpha per test origin (GBT, γ = 0.005): 2016: 0.1000, 2017: 0.1000, 2018: 0.1000, 2019: 0.1001, 2020: 0.1002, 2021: 0.1003
- h = 5, target mean: 6341 transect-sides; rows train 19775, calibration 11205, test 37236; origins {'cal': (2011, 2013), 'test': (2014, 2019), 'train': (2007, 2010)}
- GBT params (CV MAE / pinball): point {'learning_rate': 0.05, 'max_leaf_nodes': 15, 'min_samples_leaf': 100}, q05 {'learning_rate': 0.05, 'max_leaf_nodes': 15, 'min_samples_leaf': 20}, q95 {'learning_rate': 0.05, 'max_leaf_nodes': 15, 'min_samples_leaf': 100}
- GP: kernel matern15 (CV MAE rbf 41.34, matern15 37.10), n = 1000 random training rows (seed 0); fitted 2.68**2 * Matern(length_scale=[0.668, 1e+05, 1e+05, 43.7, 3.67, 5.39, 2.62, 1e+05, 7.6, 0.931, 2.92, 5.19, 10.5, 7.59e+04], nu=1.5) + WhiteKernel(noise_level=0.00241)
- Baseline fallback to persistence (rows): {'persistence': 0, 'epr_all': 0, 'epr_10': 0, 'lrr_all': 0, 'lrr_10': 0}
- Gaussian SD (m): persistence 100.6, epr_all 132.7, epr_10 134.3, lrr_all 128.2, lrr_10 129.4, gbt 98.1, gp 109.1
- ACI alpha per test origin (GBT, γ = 0.005): 2014: 0.1000, 2015: 0.1000, 2016: 0.1000, 2017: 0.1000, 2018: 0.1000, 2019: 0.0996
- h = 3, target raw: 6342 transect-sides; rows train 16735, calibration 16513, test 37110; origins {'cal': (2013, 2015), 'test': (2016, 2021), 'train': (2007, 2011)}
- GBT params (CV MAE / pinball): point {'learning_rate': 0.05, 'max_leaf_nodes': 15, 'min_samples_leaf': 100}, q05 {'learning_rate': 0.05, 'max_leaf_nodes': 15, 'min_samples_leaf': 20}, q95 {'learning_rate': 0.05, 'max_leaf_nodes': 31, 'min_samples_leaf': 20}
- GP: kernel rbf (CV MAE rbf 25.35, matern15 26.75), n = 1000 random training rows (seed 0); fitted 3.28**2 * RBF(length_scale=[783, 3.95, 7.04, 1e+05, 3.27e+04, 0.349, 199, 1.36, 0.574, 2.5, 2.42, 15.6, 0.898, 15.1]) + WhiteKernel(noise_level=0.0351)
- Baseline fallback to persistence (rows): {'persistence': 0, 'epr_all': 0, 'epr_10': 0, 'lrr_all': 0, 'lrr_10': 0}
- Gaussian SD (m): persistence 84.4, epr_all 103.6, epr_10 105.4, lrr_all 100.4, lrr_10 99.7, gbt 83.8, gp 96.1
- ACI alpha per test origin (GBT, γ = 0.005): 2016: 0.1000, 2017: 0.1000, 2018: 0.1000, 2019: 0.1002, 2020: 0.1003, 2021: 0.1005
- h = 5, target raw: 6342 transect-sides; rows train 13508, calibration 9934, test 37298; origins {'cal': (2011, 2013), 'test': (2014, 2019), 'train': (2008, 2010)}
- GBT params (CV MAE / pinball): point {'learning_rate': 0.05, 'max_leaf_nodes': 15, 'min_samples_leaf': 100}, q05 {'learning_rate': 0.05, 'max_leaf_nodes': 15, 'min_samples_leaf': 20}, q95 {'learning_rate': 0.05, 'max_leaf_nodes': 15, 'min_samples_leaf': 20}
- GP: kernel matern15 (CV MAE rbf 40.28, matern15 38.33), n = 1000 random training rows (seed 0); fitted 3.49**2 * Matern(length_scale=[5.91, 67.9, 2.42e+03, 1e+05, 2.21, 2.52, 7.38e+03, 0.394, 6.52, 5.83, 3.48, 14.3, 10.4, 1e+05], nu=1.5) + WhiteKernel(noise_level=0.00764)
- Baseline fallback to persistence (rows): {'persistence': 0, 'epr_all': 0, 'epr_10': 0, 'lrr_all': 0, 'lrr_10': 0}
- Gaussian SD (m): persistence 117.1, epr_all 152.4, epr_10 154.9, lrr_all 150.3, lrr_10 151.9, gbt 115.8, gp 123.0
- ACI alpha per test origin (GBT, γ = 0.005): 2014: 0.1000, 2015: 0.1000, 2016: 0.1000, 2017: 0.1000, 2018: 0.1000, 2019: 0.0996

## h = 3 yr, 3-yr mean target (primary)

### H1: point accuracy (test)

| model       | MAE (m)           | RMSE (m)           |
|:------------|:------------------|:-------------------|
| persistence | 9.9 [7.7, 12.3]   | 37.5 [22.2, 49.0]  |
| epr_all     | 18.4 [12.2, 27.0] | 53.9 [31.4, 73.3]  |
| epr_10      | 14.6 [10.6, 19.1] | 52.1 [29.9, 68.8]  |
| lrr_all     | 15.0 [10.9, 19.8] | 44.3 [27.8, 57.3]  |
| lrr_10      | 12.8 [9.6, 16.2]  | 45.9 [27.4, 59.8]  |
| gbt         | 10.0 [8.1, 12.2]  | 36.3 [22.6, 46.7]  |
| gp          | 20.3 [14.4, 25.9] | 77.4 [44.8, 100.7] |

| learned   | best baseline (test MAE)   | MAE difference (m)   | H1 verdict   |
|:----------|:---------------------------|:---------------------|:-------------|
| gbt       | persistence                | 0.10 [-0.32, 0.62]   | not better   |
| gp        | persistence                | 10.37 [5.84, 15.25]  | not better   |

### H2: intervals (test, pooled)

| point model   | method          | coverage (%)      | mean width (m)       | Winkler (m)          | H2 (90 ± 3 pp)   |
|:--------------|:----------------|:------------------|:---------------------|:---------------------|:-----------------|
| gbt           | Gaussian        | 99.5 [99.3, 99.7] | 251.1 [251.1, 251.1] | 269.4 [257.8, 281.9] | fails            |
| gbt           | Split conformal | 92.4 [89.7, 94.7] | 50.0 [50.0, 50.0]    | 109.6 [86.8, 134.6]  | holds            |
| gbt           | Mondrian        | 92.7 [90.2, 94.8] | 50.7 [46.8, 53.6]    | 108.0 [85.2, 132.6]  | holds            |
| gbt           | ACI             | 92.4 [89.7, 94.7] | 50.0 [50.0, 50.0]    | 109.6 [86.8, 134.6]  | holds            |
| gbt           | ACI (γ = 0.05)  | 92.3 [89.6, 94.7] | 49.7 [49.7, 49.7]    | 109.5 [86.7, 134.7]  | holds            |
| gbt           | CQR             | 70.8 [68.3, 73.8] | 50.8 [38.9, 64.5]    | 104.6 [81.1, 130.6]  | fails            |
| gp            | Gaussian        | 98.6 [97.8, 99.4] | 310.1 [310.1, 310.1] | 403.3 [337.9, 473.1] | fails            |
| gp            | Split conformal | 90.7 [87.6, 93.6] | 81.7 [81.7, 81.7]    | 256.1 [160.8, 348.1] | holds            |
| gp            | Mondrian        | 90.2 [87.7, 92.5] | 83.2 [67.9, 95.7]    | 244.8 [153.7, 331.6] | holds            |
| gp            | ACI             | 90.7 [87.6, 93.6] | 81.7 [81.7, 81.7]    | 256.1 [160.8, 348.1] | holds            |
| gp            | ACI (γ = 0.05)  | 90.7 [87.6, 93.6] | 81.7 [81.7, 81.7]    | 256.1 [160.8, 348.1] | holds            |
| persistence   | Gaussian        | 99.5 [99.3, 99.7] | 257.4 [257.4, 257.4] | 276.2 [263.4, 290.3] | fails            |
| persistence   | Split conformal | 90.1 [86.5, 93.3] | 42.7 [42.7, 42.7]    | 113.6 [83.8, 145.8]  | holds            |
| persistence   | Mondrian        | 89.8 [86.9, 92.4] | 43.3 [36.2, 48.8]    | 109.7 [80.9, 139.1]  | holds            |
| persistence   | ACI             | 90.1 [86.5, 93.3] | 42.7 [42.7, 42.7]    | 113.6 [83.8, 145.8]  | holds            |
| persistence   | ACI (γ = 0.05)  | 90.1 [86.6, 93.3] | 42.9 [42.9, 42.9]    | 113.6 [83.9, 145.7]  | holds            |

### Coverage by group (test, GBT point model; CQR on GBT quantiles)

| group      |     n |   blocks | Gaussian           | Split conformal   | Mondrian          | ACI               | ACI (γ = 0.05)    | CQR               |
|:-----------|------:|---------:|:-------------------|:------------------|:------------------|:------------------|:------------------|:------------------|
| Hau narrow |  8892 |       10 | 99.9 [99.7, 100.0] | 96.3 [93.7, 98.3] | 95.4 [92.5, 97.7] | 96.3 [93.7, 98.3] | 96.3 [93.7, 98.3] | 73.6 [69.0, 79.5] |
| Hau wide   |  3279 |        5 | 99.6 [97.7, 100.0] | 97.9 [93.7, 99.2] | 95.7 [91.2, 97.3] | 97.9 [93.7, 99.2] | 97.9 [93.7, 99.2] | 69.7 [63.6, 76.9] |
| Island     | 11980 |        7 | 99.1 [98.5, 99.5]  | 89.7 [84.1, 94.1] | 92.1 [87.4, 95.8] | 89.7 [84.1, 94.1] | 89.6 [84.0, 94.1] | 68.1 [61.8, 74.6] |
| Tien main  | 13118 |       14 | 99.6 [99.3, 99.9]  | 90.8 [86.5, 94.7] | 90.6 [86.2, 94.6] | 90.8 [86.5, 94.7] | 90.7 [86.4, 94.7] | 71.7 [68.0, 75.4] |

### Coverage by target year (test, GBT)

|   target_year |    n |   blocks | Gaussian          | Split conformal   | Mondrian          | ACI               | ACI (γ = 0.05)    | CQR               |
|--------------:|-----:|---------:|:------------------|:------------------|:------------------|:------------------|:------------------|:------------------|
|          2019 | 6261 |       28 | 99.6 [99.4, 99.9] | 92.3 [89.8, 94.5] | 92.5 [89.9, 94.6] | 92.3 [89.8, 94.5] | 92.3 [89.8, 94.5] | 79.4 [74.0, 85.4] |
|          2020 | 6255 |       28 | 99.5 [99.2, 99.7] | 92.4 [89.7, 94.6] | 92.9 [90.2, 94.9] | 92.4 [89.7, 94.6] | 92.4 [89.7, 94.6] | 73.1 [68.9, 77.5] |
|          2021 | 6178 |       28 | 99.4 [99.0, 99.7] | 91.9 [88.7, 94.8] | 92.2 [89.5, 94.8] | 91.9 [88.7, 94.8] | 91.9 [88.7, 94.8] | 74.6 [71.0, 78.7] |
|          2022 | 6273 |       28 | 99.5 [99.1, 99.7] | 91.8 [88.6, 94.6] | 91.9 [89.0, 94.5] | 91.8 [88.6, 94.6] | 91.7 [88.5, 94.5] | 67.3 [64.8, 70.4] |
|          2023 | 6174 |       28 | 99.4 [99.1, 99.7] | 92.5 [89.6, 95.0] | 92.9 [90.2, 95.2] | 92.5 [89.6, 95.0] | 92.4 [89.5, 94.9] | 68.4 [65.1, 72.0] |
|          2024 | 6128 |       28 | 99.6 [99.2, 99.8] | 93.5 [91.1, 95.6] | 93.8 [91.5, 95.7] | 93.5 [91.1, 95.6] | 93.4 [91.0, 95.6] | 62.0 [57.8, 66.4] |

### Change periods (test, GBT)

| subset                                                           |     n |   blocks | GBT MAE (m)      | Gaussian             | Split conformal   | Mondrian          | ACI               | ACI (γ = 0.05)    | CQR               |
|:-----------------------------------------------------------------|------:|---------:|:-----------------|:---------------------|:------------------|:------------------|:------------------|:------------------|:------------------|
| Vàm Nao ±10 km, all test rows (targets 2019-2024 all after 2012) |  6999 |        5 | 4.6 [4.5, 4.7]   | 100.0 [100.0, 100.0] | 98.4 [98.1, 99.0] | 98.5 [98.0, 98.8] | 98.4 [98.1, 99.0] | 98.4 [98.1, 99.0] | 65.0 [62.3, 67.6] |
| Mỹ Thuận: last 10 km of the Tiền reach, all test rows            |  1024 |        2 | 10.0 [8.7, 11.8] | 99.9 [99.8, 100.0]   | 91.8 [90.5, 92.7] | 91.8 [90.5, 92.7] | 91.8 [90.5, 92.7] | 91.8 [90.5, 92.7] | 72.9 [71.7, 74.5] |
| Mỹ Thuận, forecast window overlapping 2014-2017 (origin <= 2017) |   342 |        2 | 9.4 [8.0, 11.4]  | 100.0 [100.0, 100.0] | 93.9 [93.6, 94.1] | 93.9 [93.6, 94.1] | 93.9 [93.6, 94.1] | 93.9 [93.6, 94.1] | 74.6 [72.1, 76.2] |
| outside both zones                                               | 29246 |       25 | 11.3 [8.9, 13.5] | 99.4 [99.1, 99.6]    | 91.0 [88.2, 93.9] | 91.3 [88.7, 94.0] | 91.0 [88.2, 93.9] | 90.9 [88.1, 93.9] | 72.2 [69.0, 75.6] |

### Calibration rows (in-sample check: split and Mondrian ~90% by construction)

| point model   | method          | coverage (%)      |
|:--------------|:----------------|:------------------|
| gbt           | Gaussian        | 99.5 [99.3, 99.7] |
| gbt           | Split conformal | 90.0 [87.1, 92.9] |
| gbt           | Mondrian        | 90.1 [87.2, 92.7] |
| gbt           | ACI             | 90.0 [87.1, 92.9] |
| gbt           | ACI (γ = 0.05)  | 90.0 [87.1, 92.9] |
| gbt           | CQR             | 90.0 [88.9, 91.2] |

### Spatial leave-one-block-out (fit on training rows of the other blocks, calibrate on their calibration rows, score the held-out block's test rows)

| model       | MAE (m)           |
|:------------|:------------------|
| persistence | 9.9 [7.6, 12.2]   |
| epr_all     | 18.4 [11.9, 26.2] |
| epr_10      | 14.6 [10.5, 18.9] |
| lrr_all     | 15.0 [10.8, 19.7] |
| lrr_10      | 12.8 [9.5, 16.2]  |
| gbt         | 10.0 [8.0, 11.9]  |
| gp          | 17.7 [13.2, 21.5] |

| point model   | method          | coverage (%)      | mean width (m)       | Winkler (m)          | H2 (90 ± 3 pp)   |
|:--------------|:----------------|:------------------|:---------------------|:---------------------|:-----------------|
| gbt           | Gaussian        | 99.4 [99.2, 99.7] | 246.1 [230.6, 256.2] | 265.5 [257.6, 274.4] | fails            |
| gbt           | Split conformal | 91.7 [88.9, 94.6] | 47.0 [45.3, 48.8]    | 109.4 [85.6, 132.5]  | holds            |
| gbt           | Mondrian        | 91.8 [88.9, 94.5] | 47.5 [43.4, 51.1]    | 109.1 [85.3, 131.7]  | holds            |
| gbt           | ACI             | 91.7 [88.9, 94.6] | 47.0 [45.3, 48.8]    | 109.3 [85.5, 132.4]  | holds            |
| gbt           | ACI (γ = 0.05)  | 91.8 [89.1, 94.5] | 46.9 [45.5, 48.5]    | 108.7 [84.8, 131.6]  | holds            |
| gbt           | CQR             | 79.2 [75.9, 81.7] | 53.4 [43.8, 63.4]    | 106.0 [83.4, 128.1]  | fails            |

| group      |     n |   blocks | Gaussian           | Split conformal   | Mondrian          | ACI               | ACI (γ = 0.05)    | CQR               |
|:-----------|------:|---------:|:-------------------|:------------------|:------------------|:------------------|:------------------|:------------------|
| Hau narrow |  8892 |       10 | 99.9 [99.7, 100.0] | 96.0 [93.2, 98.1] | 94.7 [91.5, 97.5] | 95.9 [93.2, 98.1] | 95.8 [93.2, 98.0] | 80.7 [75.0, 86.3] |
| Hau wide   |  3279 |        5 | 99.6 [97.7, 100.0] | 97.7 [93.6, 99.1] | 96.4 [93.0, 98.0] | 97.7 [93.6, 99.1] | 97.7 [93.6, 98.9] | 70.6 [66.2, 77.7] |
| Island     | 11980 |        7 | 98.9 [98.2, 99.5]  | 88.9 [82.1, 94.6] | 90.7 [84.5, 96.0] | 89.0 [82.2, 94.6] | 89.1 [82.5, 94.5] | 76.2 [68.0, 81.5] |
| Tien main  | 13118 |       14 | 99.6 [99.3, 99.8]  | 89.8 [85.4, 93.9] | 89.6 [84.6, 93.9] | 89.9 [85.4, 93.9] | 90.0 [85.8, 93.9] | 82.9 [80.5, 85.6] |

### Secondary: linear-only series (test, models fitted on all series)

| model       | MAE (m)           | RMSE (m)          |
|:------------|:------------------|:------------------|
| persistence | 6.4 [5.5, 7.5]    | 11.8 [9.8, 13.8]  |
| epr_all     | 8.1 [7.1, 9.3]    | 13.3 [11.5, 15.0] |
| epr_10      | 7.6 [6.7, 8.7]    | 13.0 [11.5, 14.7] |
| lrr_all     | 7.7 [6.7, 8.7]    | 12.6 [11.0, 14.1] |
| lrr_10      | 7.2 [6.4, 8.3]    | 12.4 [10.9, 13.9] |
| gbt         | 6.6 [5.9, 7.5]    | 11.5 [10.0, 13.0] |
| gp          | 14.5 [10.1, 19.4] | 58.6 [27.9, 82.0] |

| learned   | best baseline (test MAE)   | MAE difference (m)   | H1 verdict   |
|:----------|:---------------------------|:---------------------|:-------------|
| gbt       | persistence                | 0.21 [-0.15, 0.61]   | not better   |
| gp        | persistence                | 8.05 [4.36, 12.66]   | not better   |

| point model   | method          | coverage (%)         | mean width (m)       | Winkler (m)          | H2 (90 ± 3 pp)   |
|:--------------|:----------------|:---------------------|:---------------------|:---------------------|:-----------------|
| gbt           | Gaussian        | 100.0 [100.0, 100.0] | 251.1 [251.1, 251.1] | 251.2 [251.2, 251.3] | fails            |
| gbt           | Split conformal | 96.1 [94.7, 97.2]    | 50.0 [50.0, 50.0]    | 63.4 [58.7, 68.7]    | fails            |
| gbt           | Mondrian        | 96.1 [94.8, 97.1]    | 50.1 [46.1, 53.2]    | 62.9 [57.2, 68.9]    | fails            |
| gbt           | ACI             | 96.1 [94.7, 97.2]    | 50.0 [50.0, 50.0]    | 63.3 [58.7, 68.7]    | fails            |
| gbt           | ACI (γ = 0.05)  | 96.0 [94.7, 97.1]    | 49.7 [49.7, 49.7]    | 63.2 [58.5, 68.5]    | fails            |
| gbt           | CQR             | 70.3 [67.8, 73.4]    | 36.8 [30.4, 44.0]    | 65.2 [56.7, 73.5]    | fails            |

## h = 5 yr, 3-yr mean target (secondary horizon)

### H1: point accuracy (test)

| model       | MAE (m)           | RMSE (m)           |
|:------------|:------------------|:-------------------|
| persistence | 14.6 [10.9, 18.8] | 52.3 [30.1, 69.0]  |
| epr_all     | 30.3 [19.1, 45.8] | 87.7 [49.5, 121.3] |
| epr_10      | 24.5 [16.8, 33.2] | 84.4 [47.9, 112.2] |
| lrr_all     | 25.2 [17.4, 35.3] | 71.3 [43.9, 94.0]  |
| lrr_10      | 21.4 [15.2, 28.5] | 72.3 [41.6, 95.4]  |
| gbt         | 16.1 [13.0, 19.7] | 50.9 [31.4, 66.2]  |
| gp          | 24.8 [18.5, 30.8] | 74.2 [46.6, 92.9]  |

| learned   | best baseline (test MAE)   | MAE difference (m)   | H1 verdict   |
|:----------|:---------------------------|:---------------------|:-------------|
| gbt       | persistence                | 1.42 [0.19, 3.09]    | not better   |
| gp        | persistence                | 10.21 [7.09, 13.15]  | not better   |

### H2: intervals (test, pooled)

| point model   | method          | coverage (%)      | mean width (m)       | Winkler (m)          | H2 (90 ± 3 pp)   |
|:--------------|:----------------|:------------------|:---------------------|:---------------------|:-----------------|
| gbt           | Gaussian        | 99.5 [99.3, 99.7] | 322.7 [322.7, 322.7] | 351.0 [331.2, 371.6] | fails            |
| gbt           | Split conformal | 91.9 [89.1, 94.2] | 92.6 [92.6, 92.6]    | 170.3 [137.1, 207.7] | holds            |
| gbt           | Mondrian        | 91.8 [89.0, 94.2] | 92.8 [85.4, 99.3]    | 174.0 [143.3, 208.8] | holds            |
| gbt           | ACI             | 91.9 [89.1, 94.2] | 92.7 [92.7, 92.7]    | 170.4 [137.2, 207.7] | holds            |
| gbt           | ACI (γ = 0.05)  | 91.9 [89.2, 94.3] | 93.4 [93.3, 93.4]    | 170.6 [137.5, 207.7] | holds            |
| gbt           | CQR             | 92.8 [91.1, 94.4] | 104.8 [86.3, 125.1]  | 151.3 [117.4, 188.4] | holds            |
| gp            | Gaussian        | 98.6 [97.9, 99.4] | 358.8 [358.8, 358.8] | 437.4 [384.8, 486.4] | fails            |
| gp            | Split conformal | 92.9 [90.0, 95.6] | 129.2 [129.2, 129.2] | 276.6 [195.1, 350.5] | holds            |
| gp            | Mondrian        | 92.0 [89.7, 94.1] | 121.6 [101.5, 137.9] | 260.8 [176.4, 334.7] | holds            |
| gp            | ACI             | 92.9 [90.0, 95.6] | 129.2 [129.2, 129.2] | 276.6 [195.1, 350.5] | holds            |
| gp            | ACI (γ = 0.05)  | 92.9 [90.0, 95.6] | 129.0 [129.0, 129.0] | 276.5 [195.0, 350.5] | holds            |
| persistence   | Gaussian        | 99.5 [99.2, 99.7] | 331.1 [331.1, 331.1] | 360.7 [338.9, 383.5] | fails            |
| persistence   | Split conformal | 93.3 [90.1, 96.1] | 91.4 [91.4, 91.4]    | 173.5 [132.1, 219.9] | fails            |
| persistence   | Mondrian        | 93.2 [90.4, 95.5] | 90.4 [75.1, 102.7]   | 164.7 [122.8, 206.3] | fails            |
| persistence   | ACI             | 93.3 [90.1, 96.0] | 91.4 [91.4, 91.4]    | 173.5 [132.0, 219.9] | fails            |
| persistence   | ACI (γ = 0.05)  | 93.2 [90.1, 96.0] | 91.1 [91.1, 91.1]    | 173.4 [131.9, 219.9] | fails            |

### Coverage by group (test, GBT point model; CQR on GBT quantiles)

| group      |     n |   blocks | Gaussian            | Split conformal   | Mondrian          | ACI               | ACI (γ = 0.05)    | CQR               |
|:-----------|------:|---------:|:--------------------|:------------------|:------------------|:------------------|:------------------|:------------------|
| Hau narrow |  8894 |       10 | 100.0 [99.9, 100.0] | 94.5 [89.6, 97.7] | 96.3 [92.5, 98.6] | 94.5 [89.6, 97.7] | 94.5 [89.6, 97.7] | 95.3 [93.7, 96.9] |
| Hau wide   |  3332 |        5 | 99.8 [99.1, 100.0]  | 85.8 [83.1, 87.1] | 83.8 [79.5, 85.2] | 85.8 [83.1, 87.1] | 85.8 [83.1, 87.1] | 97.8 [96.8, 98.2] |
| Island     | 11894 |        7 | 98.9 [98.2, 99.4]   | 89.8 [83.2, 95.3] | 92.3 [87.1, 96.6] | 89.8 [83.3, 95.3] | 89.9 [83.4, 95.3] | 91.8 [89.6, 93.7] |
| Tien main  | 13116 |       14 | 99.6 [99.3, 99.9]   | 93.4 [89.9, 96.6] | 90.2 [85.7, 94.5] | 93.4 [89.9, 96.6] | 93.5 [90.0, 96.7] | 90.7 [87.2, 93.6] |

### Coverage by target year (test, GBT)

|   target_year |    n |   blocks | Gaussian          | Split conformal   | Mondrian          | ACI               | ACI (γ = 0.05)    | CQR               |
|--------------:|-----:|---------:|:------------------|:------------------|:------------------|:------------------|:------------------|:------------------|
|          2019 | 6229 |       28 | 99.5 [99.2, 99.7] | 82.3 [73.0, 89.1] | 83.1 [74.1, 90.0] | 82.3 [73.0, 89.1] | 82.3 [73.0, 89.1] | 93.2 [91.0, 95.4] |
|          2020 | 6260 |       28 | 99.6 [99.4, 99.7] | 92.6 [88.5, 95.9] | 92.6 [89.3, 95.6] | 92.6 [88.5, 95.9] | 92.6 [88.5, 95.9] | 96.0 [94.2, 97.6] |
|          2021 | 6165 |       28 | 99.6 [99.3, 99.8] | 94.4 [92.3, 96.3] | 94.0 [91.5, 96.2] | 94.4 [92.3, 96.3] | 94.4 [92.3, 96.3] | 94.6 [92.9, 96.4] |
|          2022 | 6260 |       28 | 99.5 [99.2, 99.8] | 94.2 [91.8, 96.4] | 93.9 [91.5, 96.0] | 94.2 [91.8, 96.4] | 94.2 [91.8, 96.4] | 92.3 [90.6, 93.9] |
|          2023 | 6187 |       28 | 99.3 [98.9, 99.6] | 94.0 [91.1, 96.5] | 93.7 [90.9, 96.3] | 94.0 [91.1, 96.5] | 94.0 [91.1, 96.5] | 90.6 [88.6, 92.5] |
|          2024 | 6135 |       28 | 99.5 [99.2, 99.8] | 93.7 [90.8, 96.3] | 93.2 [90.0, 95.9] | 93.8 [90.8, 96.3] | 94.1 [91.3, 96.5] | 89.8 [87.9, 91.5] |

### Change periods (test, GBT)

| subset                                                           |     n |   blocks | GBT MAE (m)       | Gaussian             | Split conformal   | Mondrian          | ACI               | ACI (γ = 0.05)    | CQR               |
|:-----------------------------------------------------------------|------:|---------:|:------------------|:---------------------|:------------------|:------------------|:------------------|:------------------|:------------------|
| Vàm Nao ±10 km, all test rows (targets 2019-2024 all after 2012) |  6999 |        5 | 6.7 [6.0, 7.1]    | 100.0 [100.0, 100.0] | 98.9 [98.6, 99.5] | 98.9 [98.4, 99.8] | 98.9 [98.6, 99.5] | 98.9 [98.6, 99.5] | 95.3 [93.7, 97.3] |
| Mỹ Thuận: last 10 km of the Tiền reach, all test rows            |  1023 |        2 | 12.6 [10.6, 15.4] | 100.0 [100.0, 100.0] | 95.3 [93.8, 96.4] | 93.0 [91.7, 93.9] | 95.3 [93.8, 96.4] | 95.3 [93.8, 96.4] | 86.1 [78.1, 91.7] |
| Mỹ Thuận, forecast window overlapping 2014-2017 (origin <= 2017) |   683 |        2 | 12.5 [10.8, 14.9] | 100.0 [100.0, 100.0] | 95.5 [94.6, 96.0] | 93.1 [92.5, 93.5] | 95.5 [94.6, 96.0] | 95.5 [94.6, 96.0] | 85.8 [75.7, 92.8] |
| outside both zones                                               | 29214 |       25 | 18.4 [14.6, 22.2] | 99.4 [99.1, 99.6]    | 90.1 [87.2, 92.8] | 90.0 [86.9, 92.9] | 90.1 [87.2, 92.8] | 90.1 [87.3, 92.8] | 92.4 [90.8, 94.2] |

### Calibration rows (in-sample check: split and Mondrian ~90% by construction)

| point model   | method          | coverage (%)      |
|:--------------|:----------------|:------------------|
| gbt           | Gaussian        | 98.7 [97.9, 99.5] |
| gbt           | Split conformal | 90.0 [85.8, 93.6] |
| gbt           | Mondrian        | 90.1 [85.8, 93.4] |
| gbt           | ACI             | 90.0 [85.8, 93.6] |
| gbt           | ACI (γ = 0.05)  | 90.0 [85.8, 93.6] |
| gbt           | CQR             | 90.0 [88.0, 92.0] |

### Spatial leave-one-block-out (fit on training rows of the other blocks, calibrate on their calibration rows, score the held-out block's test rows)

| model       | MAE (m)           |
|:------------|:------------------|
| persistence | 14.6 [10.8, 18.4] |
| epr_all     | 30.3 [18.6, 44.4] |
| epr_10      | 24.5 [16.5, 32.7] |
| lrr_all     | 25.2 [17.1, 34.6] |
| lrr_10      | 21.4 [14.9, 28.1] |
| gbt         | 16.4 [13.4, 19.5] |
| gp          | 28.2 [21.2, 34.4] |

| point model   | method          | coverage (%)      | mean width (m)       | Winkler (m)          | H2 (90 ± 3 pp)   |
|:--------------|:----------------|:------------------|:---------------------|:---------------------|:-----------------|
| gbt           | Gaussian        | 99.4 [99.0, 99.7] | 316.5 [298.0, 328.9] | 346.4 [334.6, 357.1] | fails            |
| gbt           | Split conformal | 92.1 [89.4, 94.5] | 94.1 [91.5, 96.4]    | 174.1 [143.0, 205.4] | holds            |
| gbt           | Mondrian        | 91.2 [87.9, 94.1] | 93.7 [83.8, 102.7]   | 181.6 [151.3, 212.0] | holds            |
| gbt           | ACI             | 92.1 [89.4, 94.5] | 94.2 [91.6, 96.5]    | 174.1 [143.1, 205.5] | holds            |
| gbt           | ACI (γ = 0.05)  | 92.1 [89.5, 94.5] | 94.8 [92.1, 97.1]    | 174.6 [143.3, 205.8] | holds            |
| gbt           | CQR             | 91.1 [89.7, 92.7] | 103.7 [86.3, 120.6]  | 156.8 [120.3, 191.4] | holds            |

| group      |     n |   blocks | Gaussian            | Split conformal   | Mondrian          | ACI               | ACI (γ = 0.05)    | CQR               |
|:-----------|------:|---------:|:--------------------|:------------------|:------------------|:------------------|:------------------|:------------------|
| Hau narrow |  8894 |       10 | 100.0 [99.9, 100.0] | 94.4 [89.4, 97.5] | 95.6 [91.1, 98.3] | 94.4 [89.4, 97.5] | 94.4 [89.5, 97.6] | 93.3 [91.1, 95.3] |
| Hau wide   |  3332 |        5 | 99.8 [98.9, 100.0]  | 84.9 [81.0, 86.7] | 83.8 [78.7, 85.2] | 84.9 [81.0, 86.7] | 85.0 [81.0, 86.7] | 94.2 [91.7, 97.4] |
| Island     | 11894 |        7 | 98.6 [97.5, 99.4]   | 91.1 [85.4, 96.1] | 91.9 [85.8, 97.2] | 91.1 [85.4, 96.1] | 91.2 [85.5, 96.1] | 87.6 [86.0, 88.8] |
| Tien main  | 13116 |       14 | 99.6 [99.3, 99.9]   | 93.3 [89.8, 96.5] | 89.4 [84.3, 94.0] | 93.3 [89.8, 96.5] | 93.3 [89.8, 96.4] | 92.0 [89.7, 94.2] |

### Secondary: linear-only series (test, models fitted on all series)

| model       | MAE (m)           | RMSE (m)          |
|:------------|:------------------|:------------------|
| persistence | 9.2 [7.6, 11.1]   | 16.9 [13.5, 20.2] |
| epr_all     | 12.3 [10.6, 14.3] | 19.9 [17.1, 22.6] |
| epr_10      | 11.2 [9.9, 12.8]  | 18.8 [16.6, 21.0] |
| lrr_all     | 11.5 [10.0, 13.2] | 18.6 [16.3, 20.9] |
| lrr_10      | 10.9 [9.6, 12.4]  | 18.2 [16.1, 20.4] |
| gbt         | 11.0 [9.6, 12.8]  | 18.7 [16.4, 21.4] |
| gp          | 17.5 [13.7, 21.0] | 47.9 [26.7, 61.9] |

| learned   | best baseline (test MAE)   | MAE difference (m)   | H1 verdict   |
|:----------|:---------------------------|:---------------------|:-------------|
| gbt       | persistence                | 1.79 [0.55, 3.42]    | not better   |
| gp        | persistence                | 8.28 [5.62, 10.89]   | not better   |

| point model   | method          | coverage (%)         | mean width (m)       | Winkler (m)          | H2 (90 ± 3 pp)   |
|:--------------|:----------------|:---------------------|:---------------------|:---------------------|:-----------------|
| gbt           | Gaussian        | 100.0 [100.0, 100.0] | 322.7 [322.7, 322.7] | 322.7 [322.7, 322.7] | fails            |
| gbt           | Split conformal | 95.0 [93.0, 96.6]    | 92.6 [92.6, 92.6]    | 109.8 [104.1, 117.5] | fails            |
| gbt           | Mondrian        | 95.0 [93.0, 96.7]    | 92.8 [85.4, 99.7]    | 113.5 [107.2, 120.5] | fails            |
| gbt           | ACI             | 95.0 [93.0, 96.6]    | 92.7 [92.7, 92.7]    | 109.9 [104.2, 117.6] | fails            |
| gbt           | ACI (γ = 0.05)  | 95.1 [93.1, 96.7]    | 93.4 [93.3, 93.4]    | 110.4 [104.7, 118.0] | fails            |
| gbt           | CQR             | 94.5 [93.5, 95.5]    | 86.0 [73.3, 98.6]    | 98.1 [84.2, 112.0]   | fails            |

## Sensitivity: raw annual target x(t+h) - x(t)

### h = 3

| model       | MAE (m)           | RMSE (m)          |
|:------------|:------------------|:------------------|
| persistence | 12.1 [9.7, 14.7]  | 46.3 [29.2, 59.4] |
| epr_all     | 20.6 [14.2, 29.4] | 60.8 [37.1, 80.6] |
| epr_10      | 17.3 [12.9, 22.0] | 59.8 [36.5, 78.2] |
| lrr_all     | 17.0 [12.8, 21.9] | 51.8 [33.7, 65.9] |
| lrr_10      | 15.0 [11.6, 18.7] | 53.4 [33.2, 68.9] |
| gbt         | 12.0 [9.7, 14.5]  | 45.3 [28.7, 57.8] |
| gp          | 22.3 [15.7, 30.5] | 65.5 [36.4, 90.9] |

| learned   | best baseline (test MAE)   | MAE difference (m)   | H1 verdict   |
|:----------|:---------------------------|:---------------------|:-------------|
| gbt       | persistence                | -0.13 [-0.38, 0.09]  | not better   |
| gp        | persistence                | 10.21 [5.81, 16.00]  | not better   |

| point model   | method          | coverage (%)      | mean width (m)       | Winkler (m)          | H2 (90 ± 3 pp)   |
|:--------------|:----------------|:------------------|:---------------------|:---------------------|:-----------------|
| gbt           | Gaussian        | 99.3 [99.0, 99.6] | 275.5 [275.5, 275.5] | 299.5 [286.3, 313.9] | fails            |
| gbt           | Split conformal | 93.6 [91.2, 95.6] | 65.7 [65.7, 65.7]    | 135.8 [109.8, 165.0] | fails            |
| gbt           | Mondrian        | 93.5 [91.2, 95.5] | 65.4 [62.9, 67.2]    | 135.0 [109.0, 163.2] | fails            |
| gbt           | ACI             | 93.6 [91.2, 95.6] | 65.6 [65.6, 65.6]    | 135.7 [109.8, 165.0] | fails            |
| gbt           | ACI (γ = 0.05)  | 93.5 [91.1, 95.5] | 65.0 [65.0, 65.1]    | 135.5 [109.5, 164.9] | fails            |
| gbt           | CQR             | 80.4 [78.7, 82.3] | 67.9 [55.9, 82.3]    | 131.7 [105.2, 161.8] | fails            |

| group      |     n |   blocks | Gaussian           | Split conformal   | Mondrian          | ACI               | ACI (γ = 0.05)    | CQR               |
|:-----------|------:|---------:|:-------------------|:------------------|:------------------|:------------------|:------------------|:------------------|
| Hau narrow |  8882 |       10 | 99.8 [99.6, 100.0] | 96.9 [94.9, 98.6] | 96.0 [93.7, 98.0] | 96.9 [94.9, 98.6] | 96.9 [94.9, 98.5] | 83.1 [81.0, 86.0] |
| Hau wide   |  3258 |        5 | 99.6 [97.3, 100.0] | 98.5 [95.7, 99.4] | 98.6 [96.0, 99.5] | 98.5 [95.7, 99.4] | 98.4 [95.7, 99.3] | 81.4 [76.7, 85.9] |
| Island     | 11874 |        7 | 99.0 [98.4, 99.5]  | 91.1 [86.0, 95.2] | 92.0 [87.4, 95.7] | 91.1 [86.0, 95.2] | 90.9 [85.8, 95.0] | 80.2 [75.7, 84.4] |
| Tien main  | 13096 |       14 | 99.2 [98.7, 99.7]  | 92.3 [88.4, 95.8] | 91.9 [87.9, 95.4] | 92.3 [88.4, 95.8] | 92.2 [88.3, 95.6] | 78.6 [76.7, 80.4] |

### h = 5

| model       | MAE (m)           | RMSE (m)           |
|:------------|:------------------|:-------------------|
| persistence | 16.1 [12.3, 20.4] | 59.4 [34.9, 77.9]  |
| epr_all     | 31.9 [20.6, 47.4] | 93.1 [53.7, 126.8] |
| epr_10      | 26.4 [18.4, 35.4] | 90.6 [52.4, 119.2] |
| lrr_all     | 26.5 [18.7, 36.6] | 76.6 [47.9, 99.9]  |
| lrr_10      | 22.9 [16.6, 30.2] | 77.6 [45.8, 101.8] |
| gbt         | 18.7 [15.4, 22.6] | 58.9 [37.0, 75.8]  |
| gp          | 25.9 [20.3, 31.6] | 75.0 [48.5, 92.9]  |

| learned   | best baseline (test MAE)   | MAE difference (m)   | H1 verdict   |
|:----------|:---------------------------|:---------------------|:-------------|
| gbt       | persistence                | 2.53 [1.31, 4.14]    | not better   |
| gp        | persistence                | 9.78 [7.06, 12.46]   | not better   |

| point model   | method          | coverage (%)      | mean width (m)       | Winkler (m)          | H2 (90 ± 3 pp)   |
|:--------------|:----------------|:------------------|:---------------------|:---------------------|:-----------------|
| gbt           | Gaussian        | 99.5 [99.3, 99.7] | 380.9 [380.9, 380.9] | 411.5 [390.1, 434.0] | fails            |
| gbt           | Split conformal | 91.2 [88.3, 93.8] | 94.5 [94.5, 94.5]    | 191.2 [153.6, 233.7] | holds            |
| gbt           | Mondrian        | 91.2 [88.4, 93.8] | 95.1 [87.9, 101.8]   | 196.3 [160.7, 235.5] | holds            |
| gbt           | ACI             | 91.2 [88.3, 93.8] | 94.5 [94.5, 94.5]    | 191.2 [153.6, 233.7] | holds            |
| gbt           | ACI (γ = 0.05)  | 91.2 [88.4, 93.8] | 95.0 [95.0, 95.0]    | 191.3 [153.8, 233.7] | holds            |
| gbt           | CQR             | 89.8 [88.5, 91.0] | 109.9 [94.1, 127.1]  | 175.1 [139.2, 213.5] | holds            |

| group      |     n |   blocks | Gaussian           | Split conformal   | Mondrian          | ACI               | ACI (γ = 0.05)    | CQR               |
|:-----------|------:|---------:|:-------------------|:------------------|:------------------|:------------------|:------------------|:------------------|
| Hau narrow |  8885 |       10 | 99.9 [99.9, 100.0] | 94.3 [89.0, 97.5] | 97.0 [94.3, 98.7] | 94.3 [89.0, 97.5] | 94.4 [89.1, 97.5] | 90.0 [88.8, 91.0] |
| Hau wide   |  3365 |        5 | 99.6 [98.4, 100.0] | 85.3 [83.2, 86.5] | 80.4 [77.5, 82.4] | 85.3 [83.2, 86.5] | 85.3 [83.2, 86.5] | 94.9 [93.7, 95.5] |
| Island     | 11955 |        7 | 99.0 [98.3, 99.6]  | 88.7 [81.8, 94.6] | 90.7 [84.9, 95.7] | 88.7 [81.9, 94.6] | 88.8 [82.0, 94.7] | 90.1 [88.6, 91.5] |
| Tien main  | 13093 |       14 | 99.6 [99.3, 99.9]  | 92.8 [89.1, 96.1] | 90.6 [86.3, 94.4] | 92.8 [89.1, 96.1] | 92.8 [89.1, 96.1] | 88.2 [85.5, 90.7] |

## Notes: readings of the protocol (proposed deviations / clarifications for the owner)

1. Covariates: width_m (median 2000-2014) and dwidth_00_14 (2000-02 -> 2012-14) contain bank positions after the training origins (2007-2012), against "inputs use only years <= t" (deviation 1); replaced by width_00 (median 2000-02 width). curv_bank, node_km, is_island come from the static JRC-derived planform and are treated as static.
2. Two learned models: H1 is judged for each separately. "Best baseline" = the baseline with the lowest test MAE (the hardest comparator; it chooses nothing that is then tuned).
3. Gaussian SD = SD of out-of-fold training residuals (in-sample GBT residuals would be overfit). Targets are heavy-tailed (edge switches up to ~2 km are not removed: the spike filter only catches reverting jumps), so the SD is 76-120 m and Gaussian intervals over-cover (~99%), not under-cover as the protocol expected.
4. ACI: 6 test origins and delayed feedback leave 3 (h = 3) or 1 (h = 5) updates; with a pooled per-origin miscoverage and γ = 0.005 alpha moves by < 0.001, so ACI equals split conformal by construction (γ = 0.05 too). With this design the protocol's ACI comparison is not informative.
5. The centred target uses year t + 1 at the origin and year 2019 in the last calibration target (d(2018)); this is the protocol's definition (target only), noted for transparency.
6. Change zones are not defined in the protocol: here ±10 km of the Vàm Nao junction (vamnao_km) and the last 10 km of the Tiền reach (Mỹ Thuận bridge); both have only 2-5 blocks, so their CIs are not reliable.
7. Spatial leave-one-block-out is combined with the temporal split (train/calibration rows of the other blocks, test rows of the held-out block); hyperparameters fixed from the temporal CV, GP kernel fixed and refitted.
8. GP on n = 1000 rows (n = 2000 took > 20 min per CV fit). With a Gaussian likelihood it interpolates the heavy-tailed target (fitted white noise ~1-3% of the normalised variance): poor MAE.
9. CQR at h = 3 under-covers on test (71%) although it is 90% on calibration: the raw GBT quantile width depends on the origin (calibration origins 2013-2015 sit next to the 2010 / 2012 / 2013 composite gaps: median raw width 60 m; test origins 2018-2021: 23 m) while the |retreat| distribution is the same (p90 21 m). A feature shift from composite completeness, not a code bug.
