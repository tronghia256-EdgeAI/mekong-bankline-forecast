# Sensor bias, repeatability and window sensitivity: sadec_caolanh

Script: `src/sensor_check.py`. Bank positions on the standard transects (fixed centerline, core and river masks from the standard composites) with the same mainland-edge rule and per-composite Otsu threshold as `src/banklines.py`. Difference = first - second (m); + = first composite puts the bank farther from the centerline (landward). Statistics on the 652 stable transect-sides of 810 (trends.csv); CI = 2000 bootstrap resamples of blocks of 10 consecutive transects. Composites in `data/raw/sadec_caolanh/checks/`. Figure: `sadec_caolanh_sensor_check.png`.

Sanity check: the position code applied to the standard composites reproduces `bank_positions.csv` (18630 rows): max abs difference 4.5e-13 m, NaN pattern mismatches 0.

All composites are clipped to MNDWI in [-1, 1] by `banklines.read`: a few pixels with green + SWIR near 0 reach |MNDWI| >> 1 and would stretch the 256-bin Otsu histogram until the threshold collapses.

Mean, SD and CI exclude differences > 150 m (detection mode switches, counted separately; the last column is the mean with them).

## Pooled

| check | n | bias = mean (m) | 95% CI (block bootstrap) | median | SD | robust SD | abs > 150 m | mean incl. > 150 m |
|---|---|---|---|---|---|---|---|---|
| L7-L8 | 4795 | -0.2 | [-0.6, +0.2] | -0.3 | 11.7 | 5.3 | 298 | +21.9 |
| L8-L9 | 1628 | -0.2 | [-1.7, +1.5] | +0.1 | 17.0 | 5.7 | 183 | +58.2 |
| L5-L7 | 2921 | -1.0 | [-1.8, -0.3] | -1.6 | 16.3 | 8.1 | 557 | -19.7 |
| repeat A-B | 6887 | +0.6 | [+0.2, +0.9] | +0.4 | 10.5 | 4.3 | 53 | +2.4 |
| window | 3900 | +1.0 | [+0.7, +1.4] | +0.4 | 8.0 | 2.4 | 2 | +1.0 |

Spread of the per-year bias (SD across years of the per-year mean): L7-L8 3.2 m (8 yr), L8-L9 2.6 m (3 yr), L5-L7 3.5 m (7 yr), A-B 2.2 m (11 yr), Jan-Mar minus Feb-Apr 1.5 m (6 yr).

## 1. Sensor pairs (same year, Jan 1 - May 1)

| pair, year | scenes | coverage (all sides) | n | bias = mean (m) | 95% CI (block bootstrap) | median | SD | robust SD | abs > 150 m | mean incl. > 150 m |
|---|---|---|---|---|---|---|---|---|---|---|
| L7-L8 2014 | 7/8 | 100% / 100% | 650 | -3.9 | [-5.0, -2.9] | -3.1 | 10.0 | 4.2 | 3 | -4.9 |
| L7-L8 2015 | 7/8 | 100% / 100% | 652 | -2.6 | [-3.4, -1.8] | -2.2 | 7.5 | 3.5 | 1 | -2.9 |
| L7-L8 2016 | 8/6 | 100% / 96% | 633 | -0.8 | [-1.8, +0.2] | -0.7 | 8.2 | 4.4 | 0 | -0.8 |
| L7-L8 2017 | 8/7 | 97% / 100% | 637 | -2.3 | [-3.2, -1.4] | -1.7 | 9.5 | 3.9 | 0 | -2.3 |
| L7-L8 2018 | 8/7 | 82% / 98% | 515 | +2.8 | [+1.4, +4.3] | +1.2 | 14.2 | 5.1 | 33 | -41.3 |
| L7-L8 2019 | 7/8 | 100% / 81% | 508 | +4.9 | [+3.1, +7.7] | +46.1 | 15.3 | 77.3 | 249 | +270.6 |
| L7-L8 2020 | 7/8 | 91% / 100% | 593 | +2.4 | [+1.0, +3.9] | +1.8 | 13.6 | 4.8 | 12 | -9.2 |
| L7-L8 2021 | 7/8 | 98% / 96% | 607 | +2.3 | [+0.7, +4.0] | +0.9 | 13.7 | 7.0 | 0 | +2.3 |
| L8-L9 2022 | 7/8 | 100% / 100% | 651 | +1.7 | [-0.1, +3.6] | +0.3 | 14.0 | 4.3 | 1 | +2.0 |
| L8-L9 2023 | 7/7 | 99% / 58% | 349 | +2.1 | [-3.1, +9.1] | +258.2 | 27.9 | 387.1 | 180 | +272.7 |
| L8-L9 2024 | 8/8 | 96% / 100% | 628 | -2.7 | [-4.6, -1.1] | -1.2 | 15.5 | 4.3 | 2 | -2.8 |
| L5-L7 2001 | 6/3 | 99% / 93% | 617 | -7.0 | [-8.7, -5.4] | -5.3 | 12.3 | 5.6 | 5 | -4.3 |
| L5-L7 2004 | 4/7 | 53% / 95% | 358 | -3.0 | [-7.8, +1.5] | -30.1 | 25.1 | 73.6 | 165 | -205.6 |
| L5-L7 2005 | 5/7 | 94% / 100% | 615 | +3.4 | [+1.8, +5.4] | +1.8 | 14.1 | 4.3 | 6 | +1.1 |
| L5-L7 2006 | 5/7 | 100% / 86% | 583 | +0.8 | [-0.6, +2.6] | -0.9 | 12.8 | 4.4 | 1 | +1.2 |
| L5-L7 2009 | 7/4 | 99% / 55% | 358 | +1.7 | [-3.4, +8.8] | +358.6 | 30.1 | 457.9 | 197 | +295.2 |
| L5-L7 2010 | 4/5 | 23% / 52% | 72 | -0.0 | [-2.3, +2.1] | +0.0 | 8.5 | 2.6 | 9 | +6.2 |
| L5-L7 2011 | 4/4 | 50% / 99% | 318 | -2.8 | [-5.3, -0.9] | -329.9 | 9.0 | 450.5 | 174 | -278.9 |

## 2. Repeatability (two disjoint scene sets, alternate acquisition dates)

| pair, year | scenes | coverage (all sides) | n | bias = mean (m) | 95% CI (block bootstrap) | median | SD | robust SD | abs > 150 m | mean incl. > 150 m |
|---|---|---|---|---|---|---|---|---|---|---|
| A-B 2014 | 8/7 (L8x4+L7x4 / L8x4+L7x3) | 99% / 100% | 647 | -2.7 | [-3.5, -1.9] | -2.0 | 7.4 | 3.9 | 0 | -2.7 |
| A-B 2015 | 8/7 (L8x4+L7x4 / L8x4+L7x3) | 100% / 100% | 652 | +1.5 | [+1.0, +2.1] | +1.0 | 6.0 | 3.0 | 0 | +1.5 |
| A-B 2016 | 7/7 (L8x3+L7x4 / L8x3+L7x4) | 95% / 100% | 615 | +1.2 | [+0.5, +1.9] | +1.0 | 6.0 | 4.1 | 0 | +1.2 |
| A-B 2017 | 8/7 (L8x4+L7x4 / L8x3+L7x4) | 91% / 100% | 592 | -2.8 | [-3.8, -1.8] | -2.1 | 9.3 | 4.5 | 4 | -4.8 |
| A-B 2018 | 8/7 (L8x4+L7x4 / L8x3+L7x4) | 98% / 94% | 612 | +0.8 | [+0.2, +1.4] | +0.7 | 8.9 | 3.9 | 35 | +28.5 |
| A-B 2019 | 8/7 (L8x4+L7x4 / L8x4+L7x3) | 97% / 100% | 631 | -0.7 | [-1.5, +0.1] | -0.6 | 9.7 | 3.6 | 0 | -0.7 |
| A-B 2020 | 8/7 (L8x4+L7x4 / L8x4+L7x3) | 100% / 100% | 652 | -1.5 | [-2.5, -0.5] | -1.0 | 11.6 | 3.3 | 0 | -1.5 |
| A-B 2021 | 8/7 (L8x4+L7x4 / L8x4+L7x3) | 91% / 97% | 561 | +3.4 | [+1.9, +5.0] | +2.7 | 14.6 | 4.9 | 5 | +0.3 |
| A-B 2022 | 11/10 (L8x4+L9x4+L7x3 / L8x3+L9x4+L7x3) | 99% / 100% | 643 | +2.1 | [+1.3, +3.0] | +1.0 | 8.9 | 3.7 | 0 | +2.1 |
| A-B 2023 | 12/11 (L8x4+L9x3+L7x5 / L8x3+L9x4+L7x4) | 99% / 99% | 641 | +3.1 | [+1.8, +4.4] | +2.1 | 12.2 | 5.3 | 1 | +3.4 |
| A-B 2024 | 9/8 (L8x4+L9x4+L7x1 / L8x4+L9x4) | 98% / 100% | 641 | +2.0 | [+0.2, +3.8] | +2.1 | 14.7 | 5.0 | 8 | -0.8 |

## 3. Window (Jan 1 - Apr 1 minus Feb 1 - May 1, all sensors)

| pair, year | scenes | coverage (all sides) | n | bias = mean (m) | 95% CI (block bootstrap) | median | SD | robust SD | abs > 150 m | mean incl. > 150 m |
|---|---|---|---|---|---|---|---|---|---|---|
| Jan-Mar minus Feb-Apr 2001 | 6/8 | 99% / 99% | 652 | -0.8 | [-1.8, +0.7] | -1.1 | 10.0 | 2.3 | 0 | -0.8 |
| Jan-Mar minus Feb-Apr 2005 | 9/9 | 100% / 100% | 652 | +0.9 | [-0.1, +2.2] | -0.3 | 11.3 | 1.9 | 0 | +0.9 |
| Jan-Mar minus Feb-Apr 2009 | 7/10 | 99% / 100% | 645 | -0.4 | [-1.0, +0.2] | -1.0 | 6.3 | 1.8 | 1 | -0.6 |
| Jan-Mar minus Feb-Apr 2015 | 11/12 | 100% / 100% | 652 | +1.1 | [+0.8, +1.5] | +0.6 | 3.3 | 1.3 | 0 | +1.1 |
| Jan-Mar minus Feb-Apr 2019 | 11/11 | 100% / 100% | 648 | +1.9 | [+1.5, +2.5] | +1.4 | 4.6 | 1.9 | 0 | +1.9 |
| Jan-Mar minus Feb-Apr 2023 | 18/17 | 100% / 100% | 651 | +3.3 | [+2.5, +4.0] | +1.9 | 8.4 | 3.0 | 1 | +3.5 |

## Detectability with measured noise

Share of the 652 stable transect-sides with |Theil-Sen rate| x horizon > 2 x noise (the criterion in `src/banklines.py`).

| noise | 1 yr | 3 yr | 5 yr |
|---|---|---|---|
| per-side residual scale (trends.csv sd_res) | 0.0% | 3.2% | 13.3% |
| repeatability, 1 composite (3.1 m) | 9.0% | 29.4% | 44.3% |
| window, 1 composite (1.7 m) | 18.7% | 46.5% | 59.2% |
| repeat + window (3.5 m) | 8.1% | 25.3% | 40.0% |
| repeat + window, difference of two dates (x sqrt 2 = 5.0 m) | 5.4% | 18.9% | 30.4% |

Median per-side residual scale (sd_res): 6.5 m.

## Verdict

**Criterion 3 (sensor bias): passed, no correction needed.** Pooled biases L7-L8 -0.2 m, L8-L9 -0.2 m, L5-L7 -1.0 m; the largest CI bound is 1.8 m. Single-year sensor differences reach 3-5 m, but two composites of disjoint scenes from the SAME sensors differ by as much (per-year bias spread: sensor pairs ~3-4 m, scene splits 2.2 m), so this is a per-composite common-mode offset (acquisition dates, water level), not a sensor effect. A step of 1.8 m at 2013 (L8) would tilt a 2000-2024 OLS trend by 0.11 m/yr (0.05 m/yr at 2022, L9), and the standard composites are medians over mixed sensors, which dilutes it further. This is small next to the median |rate| of stable banks and far below hotspot rates.

**Criterion 4a (repeatability): measured.** Two disjoint half-scene composites differ with robust SD 4.3 m, so one composite carries ~3.1 m of noise (a full composite has about twice the scenes, so this is an upper value). That is about half the 6.5 m robust residual around linear trends: most of the trend residual is real non-linear bank change and between-year water level, not measurement noise. Tails are heavy (SD 10.5 m without mode switches, 53 switches > 150 m in 6887 pairs), so use robust statistics.

**Criterion 4b (window): small, known.** Jan-Mar minus Feb-Apr: bias +1.0 m (Jan-Mar banks slightly landward, as expected from the falling dry-season stage), robust SD 2.4 m (~1.7 m per composite). The window choice changes positions by about 1 m; keep it fixed across years.

**Detectability.** With measurement noise alone (repeat + window) the 1/3/5-year shares rise from 0/4/13% to the values in the table above (the sqrt 2 row is the fair test for the difference of two dates). Use the measured noise to say which changes are real; for forecast intervals keep the per-side residual scale, because it contains the non-linear change the forecast must cover.
