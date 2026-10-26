# P2: transect forecasts with 90% intervals (H1, H2)

`python src/forecast.py` (2047 s). Protocol: docs/protocol.md section 2 + deviation 1 (tag protocol-v1). Test = targets 2019-2024, scored once; every choice below was made on training rows only (CV) or fixed a priori. CIs: 95% block bootstrap over 10 km blocks (1,000 resamples, seed 0). Retreat + = landward (m).

## Setup

- Inputs: lagged positions x(t-k) minus the trailing 3-yr mean (k = 0..5), Theil-Sen rates over 3/5/10 yr (>= 2/3/5 valid years), physical covariates ['curv_bank', 'width_00', 'is_island', 'river_km', 'node_km'] of the 2 km unit (width_00 = median 2000-02 channel width; width_m and dwidth_00_14 use 2000-2014 and are not used, see notes). No exposure variables.
- Groups (Mondrian): Tiền main; Hậu wide; Hậu narrow (channel hau, chainage < 30300 m = tiles.json narrow_until_m 38800 - border 8500; stitch.py uses raw chainage < narrow_until_m); island channels.
- Blocks: 28 blocks of 10 km (main: chainage; islands: island chainage in tiles.json).
- Change zones: Vàm Nao = 2 km units with |vamnao_km| <= 10 (covariates_2km, both rivers and island channels); Mỹ Thuận = Tiền bank points (incl. island channels) within 10 km of the downstream end of the reach at the Mỹ Thuận bridge.
- ACI: one alpha per forecast origin, pooled over transects, alpha_0 = 0.1, step γ = 0.005 (fixed a priori, Gibbs & Candès 2021 default), γ = 0.05 as a sensitivity; feedback from origin s is used from origin s + h on.
- Gaussian interval: ±1.645 SD of the out-of-fold training residuals (learned) or of the training residuals (baselines).

- h = 3, target mean: 6177 transect-sides; rows train 22903, calibration 16049, test 36288; origins {'cal': (2013, 2015), 'test': (2016, 2021), 'train': (2007, 2012)}
- GBT params (CV MAE / pinball): point {'learning_rate': 0.05, 'max_leaf_nodes': 31, 'min_samples_leaf': 100}, q05 {'learning_rate': 0.05, 'max_leaf_nodes': 15, 'min_samples_leaf': 20}, q95 {'learning_rate': 0.05, 'max_leaf_nodes': 31, 'min_samples_leaf': 20}
- GP: kernel matern15 (CV MAE rbf 26.27, matern15 24.75), n = 1000 random training rows (seed 0); fitted 4.03**2 * Matern(length_scale=[42.8, 702, 7.47, 10.6, 8.86, 1.59, 1.72e+03, 5.63, 5.97, 5.01, 3.15, 4.09, 3.31, 144], nu=1.5) + WhiteKernel(noise_level=0.0533)
- Baseline fallback to persistence (rows): {'persistence': 0, 'epr_all': 0, 'epr_10': 0, 'lrr_all': 0, 'lrr_10': 0}
- Gaussian SD (m): persistence 76.5, epr_all 93.6, epr_10 95.9, lrr_all 91.8, lrr_10 91.5, gbt 74.7, gp 92.9
- ACI alpha per test origin (GBT, γ = 0.005): 2016: 0.1000, 2017: 0.1000, 2018: 0.1000, 2019: 0.1001, 2020: 0.1002, 2021: 0.1003
- h = 5, target mean: 6176 transect-sides; rows train 19127, calibration 10792, test 36255; origins {'cal': (2011, 2013), 'test': (2014, 2019), 'train': (2007, 2010)}
- GBT params (CV MAE / pinball): point {'learning_rate': 0.05, 'max_leaf_nodes': 15, 'min_samples_leaf': 100}, q05 {'learning_rate': 0.05, 'max_leaf_nodes': 15, 'min_samples_leaf': 20}, q95 {'learning_rate': 0.05, 'max_leaf_nodes': 15, 'min_samples_leaf': 20}
- GP: kernel rbf (CV MAE rbf 33.76, matern15 35.04), n = 1000 random training rows (seed 0); fitted 2.26**2 * RBF(length_scale=[14.4, 19.9, 6.73, 7.48, 10.5, 2.63, 247, 10.5, 0.0476, 1.16, 558, 353, 32.8, 1e+05]) + WhiteKernel(noise_level=0.0221)
- Baseline fallback to persistence (rows): {'persistence': 0, 'epr_all': 0, 'epr_10': 0, 'lrr_all': 0, 'lrr_10': 0}
- Gaussian SD (m): persistence 97.7, epr_all 131.4, epr_10 133.4, lrr_all 127.5, lrr_10 128.8, gbt 95.4, gp 112.3
- ACI alpha per test origin (GBT, γ = 0.005): 2014: 0.1000, 2015: 0.1000, 2016: 0.1000, 2017: 0.1000, 2018: 0.1000, 2019: 0.0996
- h = 3, target raw: 6177 transect-sides; rows train 16235, calibration 16022, test 36131; origins {'cal': (2013, 2015), 'test': (2016, 2021), 'train': (2007, 2011)}
- GBT params (CV MAE / pinball): point {'learning_rate': 0.05, 'max_leaf_nodes': 15, 'min_samples_leaf': 100}, q05 {'learning_rate': 0.05, 'max_leaf_nodes': 15, 'min_samples_leaf': 20}, q95 {'learning_rate': 0.05, 'max_leaf_nodes': 31, 'min_samples_leaf': 20}
- GP: kernel matern15 (CV MAE rbf 34.87, matern15 29.85), n = 1000 random training rows (seed 0); fitted 2.17**2 * Matern(length_scale=[2.98e+03, 1e+05, 20.1, 5.98, 0.242, 5.12, 0.178, 351, 11.9, 1.16, 31, 0.0402, 3.56e+03, 1.56e+04], nu=1.5) + WhiteKernel(noise_level=0.00112)
- Baseline fallback to persistence (rows): {'persistence': 0, 'epr_all': 0, 'epr_10': 0, 'lrr_all': 0, 'lrr_10': 0}
- Gaussian SD (m): persistence 82.7, epr_all 103.0, epr_10 105.0, lrr_all 99.9, lrr_10 99.2, gbt 81.9, gp 93.7
- ACI alpha per test origin (GBT, γ = 0.005): 2016: 0.1000, 2017: 0.1000, 2018: 0.1000, 2019: 0.1002, 2020: 0.1003, 2021: 0.1004
- h = 5, target raw: 6177 transect-sides; rows train 13093, calibration 9608, test 36318; origins {'cal': (2011, 2013), 'test': (2014, 2019), 'train': (2008, 2010)}
- GBT params (CV MAE / pinball): point {'learning_rate': 0.05, 'max_leaf_nodes': 15, 'min_samples_leaf': 100}, q05 {'learning_rate': 0.05, 'max_leaf_nodes': 15, 'min_samples_leaf': 20}, q95 {'learning_rate': 0.05, 'max_leaf_nodes': 15, 'min_samples_leaf': 20}
- GP: kernel matern15 (CV MAE rbf 46.32, matern15 43.42), n = 1000 random training rows (seed 0); fitted 2.47**2 * Matern(length_scale=[1.07, 1.13e+04, 6.58e+03, 1.09, 5.71e+03, 28.6, 3.11e+03, 1e+05, 52, 1.37, 3.04, 7.05, 53.7, 1.31e+04], nu=1.5) + WhiteKernel(noise_level=0.00626)
- Baseline fallback to persistence (rows): {'persistence': 0, 'epr_all': 0, 'epr_10': 0, 'lrr_all': 0, 'lrr_10': 0}
- Gaussian SD (m): persistence 113.9, epr_all 151.1, epr_10 153.8, lrr_all 149.5, lrr_10 151.2, gbt 112.9, gp 161.7
- ACI alpha per test origin (GBT, γ = 0.005): 2014: 0.1000, 2015: 0.1000, 2016: 0.1000, 2017: 0.1000, 2018: 0.1000, 2019: 0.0996

## h = 3 yr, 3-yr mean target (primary)

### H1: point accuracy (test)

| model       | MAE (m)           | RMSE (m)          |
|:------------|:------------------|:------------------|
| persistence | 9.3 [7.4, 11.4]   | 32.8 [19.1, 42.8] |
| epr_all     | 18.0 [11.9, 26.6] | 51.2 [28.1, 71.8] |
| epr_10      | 14.1 [10.4, 18.4] | 48.6 [26.8, 64.7] |
| lrr_all     | 14.6 [10.7, 19.5] | 40.8 [25.1, 53.7] |
| lrr_10      | 12.3 [9.4, 15.5]  | 42.3 [24.4, 55.5] |
| gbt         | 9.9 [8.2, 11.9]   | 32.0 [19.3, 41.6] |
| gp          | 15.5 [11.3, 20.5] | 43.2 [24.5, 59.0] |

| learned   | best baseline (test MAE)   | MAE difference (m)   | H1 verdict   |
|:----------|:---------------------------|:---------------------|:-------------|
| gbt       | persistence                | 0.59 [0.23, 0.98]    | not better   |
| gp        | persistence                | 6.20 [3.50, 9.51]    | not better   |

### H2: intervals (test, pooled)

| point model   | method          | coverage (%)      | mean width (m)       | Winkler (m)          | H2 (90 ± 3 pp)   |
|:--------------|:----------------|:------------------|:---------------------|:---------------------|:-----------------|
| gbt           | Gaussian        | 99.5 [99.3, 99.7] | 245.7 [245.7, 245.7] | 260.4 [250.4, 272.7] | fails            |
| gbt           | Split conformal | 92.4 [89.9, 94.5] | 49.4 [49.4, 49.4]    | 103.5 [82.8, 125.8]  | holds            |
| gbt           | Mondrian        | 92.7 [90.3, 94.8] | 50.3 [48.5, 51.7]    | 102.9 [82.3, 124.9]  | holds            |
| gbt           | ACI             | 92.4 [89.9, 94.5] | 49.4 [49.4, 49.4]    | 103.5 [82.8, 125.8]  | holds            |
| gbt           | ACI (γ = 0.05)  | 92.4 [89.8, 94.5] | 49.1 [49.1, 49.1]    | 103.4 [82.6, 125.8]  | holds            |
| gbt           | CQR             | 79.5 [78.2, 81.0] | 49.6 [39.2, 61.9]    | 95.2 [74.6, 119.4]   | fails            |
| gp            | Gaussian        | 99.0 [98.1, 99.7] | 305.5 [305.5, 305.5] | 332.1 [309.4, 364.1] | fails            |
| gp            | Split conformal | 90.8 [87.0, 94.3] | 71.9 [71.9, 71.9]    | 171.0 [116.9, 240.5] | holds            |
| gp            | Mondrian        | 90.1 [87.2, 92.9] | 71.2 [58.9, 81.3]    | 160.7 [110.3, 221.9] | holds            |
| gp            | ACI             | 90.8 [87.0, 94.3] | 71.9 [71.9, 71.9]    | 171.0 [116.9, 240.5] | holds            |
| gp            | ACI (γ = 0.05)  | 90.8 [87.0, 94.3] | 71.9 [71.9, 71.9]    | 171.0 [116.9, 240.5] | holds            |
| persistence   | Gaussian        | 99.5 [99.3, 99.7] | 251.6 [251.6, 251.6] | 266.3 [255.4, 279.2] | fails            |
| persistence   | Split conformal | 89.9 [86.6, 92.7] | 39.3 [39.3, 39.3]    | 104.6 [79.1, 132.9]  | holds            |
| persistence   | Mondrian        | 89.7 [86.7, 92.1] | 39.5 [34.1, 43.8]    | 101.5 [76.1, 128.5]  | holds            |
| persistence   | ACI             | 89.9 [86.6, 92.7] | 39.3 [39.3, 39.3]    | 104.6 [79.2, 132.9]  | holds            |
| persistence   | ACI (γ = 0.05)  | 89.9 [86.6, 92.7] | 39.7 [39.7, 39.7]    | 104.7 [79.3, 132.9]  | holds            |

### Coverage by group (test, GBT point model; CQR on GBT quantiles)

| group      |     n |   blocks | Gaussian           | Split conformal   | Mondrian          | ACI               | ACI (γ = 0.05)    | CQR               |
|:-----------|------:|---------:|:-------------------|:------------------|:------------------|:------------------|:------------------|:------------------|
| Hau narrow |  8892 |       10 | 99.9 [99.6, 100.0] | 96.2 [93.5, 98.2] | 96.3 [93.8, 98.3] | 96.1 [93.5, 98.2] | 96.1 [93.5, 98.2] | 80.5 [78.5, 83.3] |
| Hau wide   |  3279 |        5 | 99.6 [97.7, 100.0] | 97.9 [93.9, 99.2] | 96.4 [91.6, 98.1] | 97.9 [93.9, 99.2] | 97.8 [93.8, 99.2] | 78.6 [72.9, 82.4] |
| Island     | 10999 |        7 | 99.1 [98.5, 99.5]  | 90.1 [84.4, 93.9] | 91.1 [85.8, 94.6] | 90.1 [84.4, 93.9] | 90.0 [84.2, 93.9] | 79.2 [75.9, 82.8] |
| Tien main  | 13118 |       14 | 99.5 [99.2, 99.8]  | 90.5 [86.0, 94.5] | 90.7 [86.3, 94.7] | 90.5 [86.0, 94.5] | 90.4 [86.0, 94.4] | 79.4 [77.5, 81.4] |

### Coverage by target year (test, GBT)

|   target_year |    n |   blocks | Gaussian          | Split conformal   | Mondrian          | ACI               | ACI (γ = 0.05)    | CQR               |
|--------------:|-----:|---------:|:------------------|:------------------|:------------------|:------------------|:------------------|:------------------|
|          2019 | 6098 |       28 | 99.7 [99.5, 99.8] | 91.8 [88.9, 94.2] | 91.9 [89.1, 94.1] | 91.8 [88.9, 94.2] | 91.8 [88.9, 94.2] | 65.1 [56.8, 73.7] |
|          2020 | 6092 |       28 | 99.5 [99.4, 99.7] | 92.5 [89.7, 94.7] | 92.8 [90.1, 94.9] | 92.5 [89.7, 94.7] | 92.5 [89.7, 94.7] | 69.3 [61.9, 76.0] |
|          2021 | 6014 |       28 | 99.4 [99.1, 99.7] | 92.3 [89.4, 94.6] | 92.7 [90.1, 94.9] | 92.3 [89.4, 94.6] | 92.3 [89.4, 94.6] | 87.0 [85.3, 88.5] |
|          2022 | 6109 |       28 | 99.4 [99.1, 99.7] | 91.8 [89.1, 94.3] | 92.1 [89.5, 94.4] | 91.8 [89.1, 94.3] | 91.8 [89.0, 94.3] | 86.2 [84.4, 87.8] |
|          2023 | 6010 |       28 | 99.5 [99.1, 99.7] | 92.7 [90.1, 95.0] | 92.9 [90.3, 95.1] | 92.7 [90.1, 95.0] | 92.6 [89.9, 94.8] | 86.7 [85.0, 88.2] |
|          2024 | 5965 |       28 | 99.5 [99.2, 99.8] | 93.4 [91.2, 95.5] | 93.8 [91.6, 95.8] | 93.4 [91.1, 95.5] | 93.2 [91.0, 95.3] | 83.0 [81.2, 84.7] |

### Change periods (test, GBT)

| subset                                                           |     n |   blocks | GBT MAE (m)      | Gaussian             | Split conformal   | Mondrian          | ACI               | ACI (γ = 0.05)    | CQR               |
|:-----------------------------------------------------------------|------:|---------:|:-----------------|:---------------------|:------------------|:------------------|:------------------|:------------------|:------------------|
| Vàm Nao ±10 km, all test rows (targets 2019-2024 all after 2012) |  6999 |        5 | 5.0 [4.9, 5.3]   | 100.0 [100.0, 100.0] | 98.3 [98.1, 98.9] | 98.4 [98.2, 99.0] | 98.3 [98.1, 98.9] | 98.3 [98.1, 98.9] | 77.8 [76.1, 78.9] |
| Mỹ Thuận: last 10 km of the Tiền reach, all test rows            |  1024 |        2 | 9.8 [8.7, 11.3]  | 99.9 [99.8, 100.0]   | 92.2 [91.2, 92.9] | 92.3 [91.2, 93.0] | 92.2 [91.2, 92.9] | 92.2 [91.2, 92.9] | 75.7 [73.3, 77.3] |
| Mỹ Thuận, forecast window overlapping 2014-2017 (origin <= 2017) |   342 |        2 | 9.6 [8.4, 11.4]  | 100.0 [100.0, 100.0] | 94.2 [93.6, 94.6] | 94.2 [93.6, 94.6] | 94.2 [93.6, 94.6] | 94.2 [93.6, 94.6] | 63.2 [55.7, 68.3] |
| outside both zones                                               | 28265 |       25 | 11.1 [8.9, 13.4] | 99.4 [99.1, 99.6]    | 91.0 [88.1, 93.9] | 91.3 [88.5, 94.1] | 91.0 [88.1, 93.9] | 90.9 [88.0, 93.9] | 80.1 [78.5, 81.8] |

### Calibration rows (in-sample check: split and Mondrian ~90% by construction)

| point model   | method          | coverage (%)      |
|:--------------|:----------------|:------------------|
| gbt           | Gaussian        | 99.5 [99.2, 99.7] |
| gbt           | Split conformal | 90.0 [86.9, 92.9] |
| gbt           | Mondrian        | 90.1 [87.0, 92.7] |
| gbt           | ACI             | 90.0 [86.9, 92.9] |
| gbt           | ACI (γ = 0.05)  | 90.0 [86.9, 92.9] |
| gbt           | CQR             | 90.0 [87.9, 92.2] |

### Spatial leave-one-block-out (fit on training rows of the other blocks, calibrate on their calibration rows, score the held-out block's test rows)

| model       | MAE (m)           |
|:------------|:------------------|
| persistence | 9.3 [7.3, 11.3]   |
| epr_all     | 18.0 [11.6, 25.8] |
| epr_10      | 14.1 [10.2, 18.2] |
| lrr_all     | 14.6 [10.5, 19.3] |
| lrr_10      | 12.3 [9.3, 15.5]  |
| gbt         | 9.8 [8.1, 11.5]   |
| gp          | 18.8 [13.4, 26.6] |

| point model   | method          | coverage (%)      | mean width (m)       | Winkler (m)          | H2 (90 ± 3 pp)   |
|:--------------|:----------------|:------------------|:---------------------|:---------------------|:-----------------|
| gbt           | Gaussian        | 99.5 [99.2, 99.7] | 241.2 [225.6, 250.9] | 256.5 [244.5, 268.2] | fails            |
| gbt           | Split conformal | 92.3 [89.4, 95.0] | 48.2 [46.1, 50.2]    | 103.1 [82.1, 124.9]  | holds            |
| gbt           | Mondrian        | 92.3 [89.6, 94.9] | 48.2 [45.1, 50.9]    | 102.5 [81.4, 124.1]  | holds            |
| gbt           | ACI             | 92.3 [89.4, 95.0] | 48.1 [46.1, 50.2]    | 103.0 [82.0, 124.8]  | holds            |
| gbt           | ACI (γ = 0.05)  | 92.3 [89.7, 94.9] | 48.0 [46.3, 49.7]    | 102.5 [81.5, 124.2]  | holds            |
| gbt           | CQR             | 78.6 [75.7, 81.5] | 47.3 [40.4, 54.7]    | 97.8 [78.4, 118.5]   | fails            |

| group      |     n |   blocks | Gaussian           | Split conformal   | Mondrian          | ACI               | ACI (γ = 0.05)    | CQR               |
|:-----------|------:|---------:|:-------------------|:------------------|:------------------|:------------------|:------------------|:------------------|
| Hau narrow |  8892 |       10 | 99.9 [99.6, 100.0] | 95.8 [92.8, 98.1] | 95.5 [92.1, 98.1] | 95.8 [92.8, 98.1] | 95.7 [92.8, 98.0] | 76.8 [72.6, 81.6] |
| Hau wide   |  3279 |        5 | 99.7 [97.9, 100.0] | 97.8 [93.3, 99.2] | 95.4 [89.8, 97.8] | 97.7 [93.3, 99.2] | 97.7 [93.3, 99.2] | 79.5 [67.4, 87.2] |
| Island     | 10999 |        7 | 99.0 [98.2, 99.6]  | 90.3 [83.2, 95.0] | 91.5 [85.7, 95.7] | 90.3 [83.3, 95.0] | 90.4 [83.8, 94.9] | 76.6 [69.2, 81.2] |
| Tien main  | 13118 |       14 | 99.5 [99.3, 99.8]  | 90.1 [85.6, 94.1] | 90.1 [85.1, 94.4] | 90.1 [85.6, 94.1] | 90.3 [86.1, 94.1] | 81.4 [79.0, 84.1] |

### Secondary: linear-only series (test, models fitted on all series)

| model       | MAE (m)         | RMSE (m)          |
|:------------|:----------------|:------------------|
| persistence | 6.2 [5.4, 7.3]  | 11.5 [9.7, 13.6]  |
| epr_all     | 8.0 [7.0, 9.3]  | 13.2 [11.6, 14.9] |
| epr_10      | 7.5 [6.7, 8.6]  | 12.9 [11.4, 14.6] |
| lrr_all     | 7.6 [6.7, 8.6]  | 12.5 [11.0, 14.0] |
| lrr_10      | 7.1 [6.3, 8.1]  | 12.3 [10.8, 13.9] |
| gbt         | 6.8 [6.2, 7.6]  | 11.6 [10.3, 13.0] |
| gp          | 9.8 [8.2, 11.6] | 17.8 [13.9, 21.1] |

| learned   | best baseline (test MAE)   | MAE difference (m)   | H1 verdict   |
|:----------|:---------------------------|:---------------------|:-------------|
| gbt       | persistence                | 0.58 [0.22, 0.97]    | not better   |
| gp        | persistence                | 3.55 [2.47, 4.64]    | not better   |

| point model   | method          | coverage (%)         | mean width (m)       | Winkler (m)          | H2 (90 ± 3 pp)   |
|:--------------|:----------------|:---------------------|:---------------------|:---------------------|:-----------------|
| gbt           | Gaussian        | 100.0 [100.0, 100.0] | 245.7 [245.7, 245.7] | 245.8 [245.7, 245.9] | fails            |
| gbt           | Split conformal | 96.0 [94.6, 97.1]    | 49.4 [49.4, 49.4]    | 62.7 [58.5, 67.9]    | fails            |
| gbt           | Mondrian        | 96.1 [94.8, 97.1]    | 50.1 [48.2, 51.6]    | 62.7 [58.0, 68.4]    | fails            |
| gbt           | ACI             | 96.0 [94.6, 97.1]    | 49.4 [49.4, 49.4]    | 62.7 [58.5, 67.9]    | fails            |
| gbt           | ACI (γ = 0.05)  | 95.9 [94.5, 97.0]    | 49.1 [49.1, 49.1]    | 62.5 [58.3, 67.8]    | fails            |
| gbt           | CQR             | 79.9 [78.7, 81.5]    | 37.2 [33.2, 42.1]    | 61.1 [55.4, 67.8]    | fails            |

## h = 5 yr, 3-yr mean target (secondary horizon)

### H1: point accuracy (test)

| model       | MAE (m)           | RMSE (m)           |
|:------------|:------------------|:-------------------|
| persistence | 13.6 [10.5, 17.0] | 45.5 [26.0, 59.1]  |
| epr_all     | 29.6 [18.6, 45.1] | 84.0 [45.1, 119.7] |
| epr_10      | 23.6 [16.4, 32.1] | 80.0 [42.8, 107.4] |
| lrr_all     | 24.6 [17.1, 34.4] | 67.2 [40.7, 90.8]  |
| lrr_10      | 20.4 [14.9, 27.2] | 67.4 [37.3, 89.5]  |
| gbt         | 15.2 [12.6, 18.3] | 44.9 [27.9, 57.6]  |
| gp          | 23.0 [19.1, 27.2] | 65.3 [45.5, 80.3]  |

| learned   | best baseline (test MAE)   | MAE difference (m)   | H1 verdict   |
|:----------|:---------------------------|:---------------------|:-------------|
| gbt       | persistence                | 1.62 [0.31, 3.24]    | not better   |
| gp        | persistence                | 9.50 [7.87, 11.03]   | not better   |

### H2: intervals (test, pooled)

| point model   | method          | coverage (%)      | mean width (m)       | Winkler (m)          | H2 (90 ± 3 pp)   |
|:--------------|:----------------|:------------------|:---------------------|:---------------------|:-----------------|
| gbt           | Gaussian        | 99.5 [99.3, 99.7] | 313.8 [313.8, 313.8] | 335.7 [319.1, 354.1] | fails            |
| gbt           | Split conformal | 91.5 [89.1, 93.7] | 84.8 [84.8, 84.8]    | 159.4 [131.5, 191.0] | holds            |
| gbt           | Mondrian        | 91.5 [88.8, 93.9] | 86.3 [79.7, 93.4]    | 164.4 [137.6, 193.2] | holds            |
| gbt           | ACI             | 91.5 [89.1, 93.7] | 84.9 [84.9, 84.9]    | 159.4 [131.5, 191.0] | holds            |
| gbt           | ACI (γ = 0.05)  | 91.6 [89.1, 93.7] | 85.5 [85.4, 85.5]    | 159.6 [131.8, 191.1] | holds            |
| gbt           | CQR             | 93.0 [91.6, 94.2] | 93.7 [78.2, 111.6]   | 133.2 [106.8, 164.5] | holds            |
| gp            | Gaussian        | 99.2 [98.9, 99.5] | 369.5 [369.5, 369.5] | 414.0 [385.3, 442.4] | fails            |
| gp            | Split conformal | 92.1 [89.8, 94.0] | 125.8 [125.8, 125.8] | 235.7 [192.8, 280.2] | holds            |
| gp            | Mondrian        | 91.5 [89.2, 93.4] | 121.1 [108.1, 131.6] | 229.6 [186.6, 273.0] | holds            |
| gp            | ACI             | 92.1 [89.8, 94.0] | 125.8 [125.8, 125.8] | 235.7 [192.8, 280.2] | holds            |
| gp            | ACI (γ = 0.05)  | 92.1 [89.8, 94.0] | 125.7 [125.7, 125.7] | 235.6 [192.8, 280.1] | holds            |
| persistence   | Gaussian        | 99.5 [99.3, 99.7] | 321.3 [321.3, 321.3] | 343.9 [325.9, 363.7] | fails            |
| persistence   | Split conformal | 93.1 [90.1, 95.5] | 82.6 [82.6, 82.6]    | 156.3 [121.5, 193.9] | fails            |
| persistence   | Mondrian        | 92.9 [90.0, 95.2] | 81.3 [70.2, 90.4]    | 149.7 [113.9, 185.5] | holds            |
| persistence   | ACI             | 93.1 [90.1, 95.5] | 82.6 [82.6, 82.6]    | 156.3 [121.5, 193.9] | fails            |
| persistence   | ACI (γ = 0.05)  | 93.1 [90.1, 95.5] | 82.3 [82.3, 82.3]    | 156.2 [121.4, 193.9] | fails            |

### Coverage by group (test, GBT point model; CQR on GBT quantiles)

| group      |     n |   blocks | Gaussian            | Split conformal   | Mondrian          | ACI               | ACI (γ = 0.05)    | CQR               |
|:-----------|------:|---------:|:--------------------|:------------------|:------------------|:------------------|:------------------|:------------------|
| Hau narrow |  8894 |       10 | 100.0 [99.9, 100.0] | 94.0 [88.8, 97.3] | 96.7 [93.1, 98.8] | 94.0 [88.8, 97.3] | 94.0 [88.9, 97.3] | 95.1 [93.7, 96.5] |
| Hau wide   |  3332 |        5 | 99.8 [98.9, 100.0]  | 84.7 [80.7, 86.4] | 83.7 [79.7, 85.0] | 84.7 [80.7, 86.4] | 84.8 [80.7, 86.4] | 97.0 [94.9, 97.8] |
| Island     | 10913 |        7 | 99.0 [98.2, 99.4]   | 90.2 [83.7, 94.5] | 91.5 [85.5, 95.4] | 90.2 [83.7, 94.5] | 90.2 [83.8, 94.5] | 91.9 [90.4, 93.0] |
| Tien main  | 13116 |       14 | 99.6 [99.3, 99.9]   | 92.7 [88.8, 96.2] | 90.0 [85.1, 94.4] | 92.7 [88.8, 96.2] | 92.8 [88.9, 96.2] | 91.5 [88.4, 93.9] |

### Coverage by target year (test, GBT)

|   target_year |    n |   blocks | Gaussian          | Split conformal   | Mondrian          | ACI               | ACI (γ = 0.05)    | CQR               |
|--------------:|-----:|---------:|:------------------|:------------------|:------------------|:------------------|:------------------|:------------------|
|          2019 | 6065 |       28 | 99.5 [99.2, 99.7] | 81.5 [71.6, 88.5] | 83.1 [73.9, 89.8] | 81.5 [71.6, 88.5] | 81.5 [71.6, 88.5] | 94.9 [93.3, 96.5] |
|          2020 | 6096 |       28 | 99.6 [99.4, 99.8] | 92.5 [89.1, 95.5] | 93.0 [90.1, 95.5] | 92.5 [89.1, 95.5] | 92.5 [89.1, 95.5] | 95.0 [93.7, 96.4] |
|          2021 | 6002 |       28 | 99.7 [99.5, 99.8] | 93.7 [91.5, 95.6] | 93.0 [90.4, 95.3] | 93.7 [91.5, 95.6] | 93.7 [91.5, 95.6] | 95.9 [94.4, 97.2] |
|          2022 | 6097 |       28 | 99.5 [99.3, 99.8] | 93.8 [91.3, 96.0] | 93.3 [90.6, 95.5] | 93.8 [91.3, 96.0] | 93.8 [91.3, 96.0] | 92.7 [90.9, 94.3] |
|          2023 | 6023 |       28 | 99.3 [99.0, 99.7] | 94.0 [91.5, 96.1] | 93.4 [90.5, 95.9] | 94.0 [91.5, 96.1] | 94.0 [91.5, 96.1] | 89.9 [87.9, 91.6] |
|          2024 | 5972 |       28 | 99.5 [99.2, 99.8] | 93.7 [91.2, 95.9] | 93.2 [90.3, 95.7] | 93.7 [91.3, 95.9] | 94.0 [91.6, 96.1] | 89.4 [87.5, 91.1] |

### Change periods (test, GBT)

| subset                                                           |     n |   blocks | GBT MAE (m)       | Gaussian             | Split conformal   | Mondrian          | ACI               | ACI (γ = 0.05)    | CQR               |
|:-----------------------------------------------------------------|------:|---------:|:------------------|:---------------------|:------------------|:------------------|:------------------|:------------------|:------------------|
| Vàm Nao ±10 km, all test rows (targets 2019-2024 all after 2012) |  6999 |        5 | 6.8 [6.1, 7.3]    | 100.0 [100.0, 100.0] | 98.7 [98.3, 99.3] | 98.7 [98.2, 99.8] | 98.7 [98.3, 99.3] | 98.7 [98.3, 99.3] | 95.3 [94.3, 97.0] |
| Mỹ Thuận: last 10 km of the Tiền reach, all test rows            |  1023 |        2 | 11.9 [10.4, 14.0] | 100.0 [100.0, 100.0] | 94.7 [93.3, 95.7] | 92.4 [91.0, 93.4] | 94.7 [93.3, 95.7] | 94.7 [93.3, 95.7] | 88.4 [83.8, 91.5] |
| Mỹ Thuận, forecast window overlapping 2014-2017 (origin <= 2017) |   683 |        2 | 11.5 [10.4, 13.2] | 100.0 [100.0, 100.0] | 94.7 [93.9, 95.3] | 92.8 [92.5, 93.1] | 94.7 [93.9, 95.3] | 94.7 [93.9, 95.3] | 89.3 [84.3, 92.8] |
| outside both zones                                               | 28233 |       25 | 17.4 [14.2, 20.8] | 99.4 [99.1, 99.7]    | 89.6 [86.9, 92.1] | 89.7 [86.5, 92.5] | 89.6 [86.9, 92.1] | 89.7 [87.0, 92.2] | 92.6 [91.2, 94.0] |

### Calibration rows (in-sample check: split and Mondrian ~90% by construction)

| point model   | method          | coverage (%)      |
|:--------------|:----------------|:------------------|
| gbt           | Gaussian        | 98.8 [98.1, 99.4] |
| gbt           | Split conformal | 90.0 [85.6, 93.3] |
| gbt           | Mondrian        | 90.1 [85.7, 93.2] |
| gbt           | ACI             | 90.0 [85.6, 93.3] |
| gbt           | ACI (γ = 0.05)  | 90.0 [85.6, 93.3] |
| gbt           | CQR             | 90.0 [88.6, 91.5] |

### Spatial leave-one-block-out (fit on training rows of the other blocks, calibrate on their calibration rows, score the held-out block's test rows)

| model       | MAE (m)           |
|:------------|:------------------|
| persistence | 13.6 [10.4, 16.6] |
| epr_all     | 29.6 [18.1, 43.8] |
| epr_10      | 23.6 [16.1, 31.8] |
| lrr_all     | 24.6 [16.5, 33.8] |
| lrr_10      | 20.4 [14.6, 26.9] |
| gbt         | 15.6 [13.0, 18.5] |
| gp          | 21.4 [17.4, 25.1] |

| point model   | method          | coverage (%)      | mean width (m)       | Winkler (m)          | H2 (90 ± 3 pp)   |
|:--------------|:----------------|:------------------|:---------------------|:---------------------|:-----------------|
| gbt           | Gaussian        | 99.4 [99.1, 99.7] | 308.5 [290.1, 320.6] | 331.5 [319.3, 345.6] | fails            |
| gbt           | Split conformal | 91.7 [89.1, 94.0] | 86.2 [84.3, 88.3]    | 161.5 [135.1, 188.4] | holds            |
| gbt           | Mondrian        | 91.1 [88.1, 93.8] | 87.7 [80.1, 95.1]    | 167.2 [142.7, 193.8] | holds            |
| gbt           | ACI             | 91.7 [89.1, 94.0] | 86.3 [84.4, 88.3]    | 161.5 [135.2, 188.5] | holds            |
| gbt           | ACI (γ = 0.05)  | 91.8 [89.2, 94.0] | 87.0 [85.2, 88.9]    | 162.0 [135.7, 189.0] | holds            |
| gbt           | CQR             | 91.4 [89.7, 93.2] | 95.3 [82.4, 107.7]   | 144.1 [117.6, 169.6] | holds            |

| group      |     n |   blocks | Gaussian            | Split conformal   | Mondrian          | ACI               | ACI (γ = 0.05)    | CQR               |
|:-----------|------:|---------:|:--------------------|:------------------|:------------------|:------------------|:------------------|:------------------|
| Hau narrow |  8894 |       10 | 100.0 [99.9, 100.0] | 93.5 [88.1, 97.1] | 95.4 [90.9, 98.2] | 93.5 [88.1, 97.1] | 93.6 [88.2, 97.1] | 94.4 [92.2, 96.4] |
| Hau wide   |  3332 |        5 | 99.7 [98.5, 100.0]  | 84.8 [80.7, 86.5] | 83.8 [78.6, 85.3] | 84.8 [80.7, 86.5] | 84.8 [80.8, 86.6] | 95.3 [92.1, 98.5] |
| Island     | 10913 |        7 | 98.6 [97.6, 99.4]   | 91.5 [85.9, 95.7] | 91.6 [85.4, 96.3] | 91.5 [85.9, 95.7] | 91.5 [85.9, 95.7] | 88.9 [86.0, 91.0] |
| Tien main  | 13116 |       14 | 99.6 [99.3, 99.9]   | 92.4 [88.6, 96.0] | 89.7 [84.6, 94.3] | 92.4 [88.6, 96.0] | 92.5 [88.6, 96.0] | 90.4 [87.5, 93.1] |

### Secondary: linear-only series (test, models fitted on all series)

| model       | MAE (m)           | RMSE (m)          |
|:------------|:------------------|:------------------|
| persistence | 8.9 [7.5, 10.6]   | 16.2 [13.3, 19.4] |
| epr_all     | 12.1 [10.6, 14.1] | 19.7 [17.1, 22.4] |
| epr_10      | 11.0 [9.8, 12.6]  | 18.6 [16.4, 20.8] |
| lrr_all     | 11.3 [9.9, 13.0]  | 18.4 [16.2, 20.6] |
| lrr_10      | 10.7 [9.5, 12.2]  | 18.0 [16.0, 20.1] |
| gbt         | 10.7 [9.5, 12.3]  | 18.4 [16.3, 20.8] |
| gp          | 17.1 [15.1, 19.3] | 39.9 [27.0, 50.4] |

| learned   | best baseline (test MAE)   | MAE difference (m)   | H1 verdict   |
|:----------|:---------------------------|:---------------------|:-------------|
| gbt       | persistence                | 1.82 [0.52, 3.49]    | not better   |
| gp        | persistence                | 8.21 [7.01, 9.36]    | not better   |

| point model   | method          | coverage (%)         | mean width (m)       | Winkler (m)          | H2 (90 ± 3 pp)   |
|:--------------|:----------------|:---------------------|:---------------------|:---------------------|:-----------------|
| gbt           | Gaussian        | 100.0 [100.0, 100.0] | 313.8 [313.8, 313.8] | 313.9 [313.8, 313.9] | fails            |
| gbt           | Split conformal | 94.7 [92.8, 96.3]    | 84.8 [84.8, 84.8]    | 106.2 [99.5, 114.5]  | fails            |
| gbt           | Mondrian        | 94.8 [92.9, 96.5]    | 86.6 [79.5, 94.3]    | 110.5 [102.3, 119.8] | fails            |
| gbt           | ACI             | 94.7 [92.8, 96.3]    | 84.9 [84.9, 84.9]    | 106.3 [99.6, 114.6]  | fails            |
| gbt           | ACI (γ = 0.05)  | 94.8 [92.8, 96.3]    | 85.5 [85.4, 85.5]    | 106.7 [100.1, 115.0] | fails            |
| gbt           | CQR             | 94.6 [93.7, 95.4]    | 78.1 [69.0, 88.5]    | 90.2 [79.8, 101.4]   | fails            |

## Sensitivity: raw annual target x(t+h) - x(t)

### h = 3

| model       | MAE (m)           | RMSE (m)          |
|:------------|:------------------|:------------------|
| persistence | 11.5 [9.4, 13.9]  | 40.1 [25.1, 51.8] |
| epr_all     | 20.1 [14.0, 28.9] | 56.6 [32.9, 77.7] |
| epr_10      | 16.7 [12.6, 21.3] | 54.9 [32.3, 72.1] |
| lrr_all     | 16.6 [12.6, 21.5] | 46.7 [30.0, 61.1] |
| lrr_10      | 14.5 [11.4, 17.9] | 48.3 [29.3, 62.8] |
| gbt         | 11.5 [9.4, 13.8]  | 39.2 [24.6, 50.5] |
| gp          | 20.6 [17.6, 23.5] | 56.8 [42.1, 66.5] |

| learned   | best baseline (test MAE)   | MAE difference (m)   | H1 verdict   |
|:----------|:---------------------------|:---------------------|:-------------|
| gbt       | persistence                | 0.00 [-0.23, 0.18]   | not better   |
| gp        | persistence                | 9.16 [6.76, 11.37]   | not better   |

| point model   | method          | coverage (%)      | mean width (m)       | Winkler (m)          | H2 (90 ± 3 pp)   |
|:--------------|:----------------|:------------------|:---------------------|:---------------------|:-----------------|
| gbt           | Gaussian        | 99.3 [99.0, 99.6] | 269.5 [269.5, 269.5] | 289.0 [277.9, 302.9] | fails            |
| gbt           | Split conformal | 93.4 [91.1, 95.3] | 62.2 [62.2, 62.2]    | 127.2 [102.9, 154.0] | fails            |
| gbt           | Mondrian        | 93.5 [91.3, 95.3] | 62.3 [61.5, 63.0]    | 126.8 [102.5, 153.2] | fails            |
| gbt           | ACI             | 93.4 [91.1, 95.3] | 62.1 [62.1, 62.1]    | 127.2 [102.8, 154.0] | fails            |
| gbt           | ACI (γ = 0.05)  | 93.3 [91.0, 95.2] | 61.7 [61.7, 61.7]    | 127.0 [102.6, 153.9] | fails            |
| gbt           | CQR             | 85.6 [84.0, 87.0] | 61.3 [50.7, 75.1]    | 111.7 [88.2, 138.1]  | fails            |

| group      |     n |   blocks | Gaussian           | Split conformal   | Mondrian          | ACI               | ACI (γ = 0.05)    | CQR               |
|:-----------|------:|---------:|:-------------------|:------------------|:------------------|:------------------|:------------------|:------------------|
| Hau narrow |  8882 |       10 | 99.8 [99.6, 100.0] | 96.6 [94.6, 98.4] | 96.4 [94.2, 98.2] | 96.6 [94.6, 98.4] | 96.6 [94.5, 98.4] | 88.2 [86.7, 90.3] |
| Hau wide   |  3258 |        5 | 99.6 [97.3, 100.0] | 98.3 [95.5, 99.3] | 98.2 [95.4, 99.2] | 98.3 [95.4, 99.3] | 98.2 [95.4, 99.3] | 88.5 [85.3, 90.5] |
| Island     | 10895 |        7 | 99.0 [98.4, 99.5]  | 91.4 [86.3, 94.9] | 91.7 [86.9, 95.1] | 91.4 [86.3, 94.9] | 91.2 [86.1, 94.7] | 85.2 [81.7, 88.1] |
| Tien main  | 13096 |       14 | 99.2 [98.6, 99.7]  | 91.6 [87.7, 95.2] | 91.8 [87.8, 95.3] | 91.6 [87.6, 95.2] | 91.5 [87.6, 95.2] | 83.6 [81.2, 85.7] |

### h = 5

| model       | MAE (m)           | RMSE (m)           |
|:------------|:------------------|:-------------------|
| persistence | 15.0 [11.9, 18.6] | 51.5 [29.7, 66.7]  |
| epr_all     | 31.2 [20.1, 46.6] | 88.2 [48.4, 124.3] |
| epr_10      | 25.4 [18.2, 34.3] | 84.9 [46.6, 113.1] |
| lrr_all     | 25.8 [18.3, 35.6] | 71.3 [43.2, 96.0]  |
| lrr_10      | 22.0 [16.2, 28.8] | 71.5 [40.5, 94.6]  |
| gbt         | 17.0 [14.3, 20.2] | 51.2 [31.5, 66.1]  |
| gp          | 25.8 [19.1, 33.8] | 81.8 [39.9, 112.8] |

| learned   | best baseline (test MAE)   | MAE difference (m)   | H1 verdict   |
|:----------|:---------------------------|:---------------------|:-------------|
| gbt       | persistence                | 2.00 [0.87, 3.44]    | not better   |
| gp        | persistence                | 10.80 [6.78, 15.27]  | not better   |

| point model   | method          | coverage (%)      | mean width (m)       | Winkler (m)          | H2 (90 ± 3 pp)   |
|:--------------|:----------------|:------------------|:---------------------|:---------------------|:-----------------|
| gbt           | Gaussian        | 99.5 [99.3, 99.7] | 371.4 [371.4, 371.4] | 395.2 [377.1, 415.1] | fails            |
| gbt           | Split conformal | 91.0 [88.6, 93.3] | 86.9 [86.9, 86.9]    | 174.6 [139.9, 212.0] | holds            |
| gbt           | Mondrian        | 90.9 [88.1, 93.3] | 86.8 [80.3, 93.6]    | 180.4 [148.4, 215.9] | holds            |
| gbt           | ACI             | 91.0 [88.6, 93.3] | 87.0 [87.0, 87.0]    | 174.6 [139.9, 212.0] | holds            |
| gbt           | ACI (γ = 0.05)  | 91.1 [88.7, 93.3] | 87.6 [87.6, 87.6]    | 174.8 [140.2, 212.0] | holds            |
| gbt           | CQR             | 90.0 [88.5, 91.2] | 105.6 [89.0, 125.1]  | 159.4 [128.1, 196.6] | holds            |

| group      |     n |   blocks | Gaussian           | Split conformal   | Mondrian          | ACI               | ACI (γ = 0.05)    | CQR               |
|:-----------|------:|---------:|:-------------------|:------------------|:------------------|:------------------|:------------------|:------------------|
| Hau narrow |  8885 |       10 | 99.9 [99.9, 100.0] | 93.6 [87.9, 97.1] | 96.6 [93.3, 98.6] | 93.6 [87.9, 97.1] | 93.6 [88.0, 97.1] | 88.1 [86.5, 89.9] |
| Hau wide   |  3365 |        5 | 99.7 [98.4, 100.0] | 85.3 [82.7, 86.4] | 80.1 [76.6, 82.0] | 85.3 [82.7, 86.4] | 85.3 [82.8, 86.4] | 96.8 [94.8, 97.4] |
| Island     | 10975 |        7 | 99.2 [98.5, 99.6]  | 89.6 [82.9, 94.0] | 90.1 [83.4, 94.5] | 89.6 [82.9, 94.0] | 89.8 [83.1, 94.1] | 90.7 [89.4, 91.9] |
| Tien main  | 13093 |       14 | 99.6 [99.3, 99.8]  | 91.9 [87.9, 95.5] | 90.4 [86.0, 94.3] | 91.9 [87.9, 95.5] | 92.0 [88.0, 95.6] | 88.8 [86.3, 91.2] |

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
