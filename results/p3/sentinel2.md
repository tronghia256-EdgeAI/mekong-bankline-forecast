# P3 R1: Sentinel-2 banks 2017-2024

`python src/gee_s2.py <tile>` (each tile and island), `python src/s2_banks.py <tile> ...`, `python src/s2_banks.py stitch`, `python src/p3_sentinel2.py`. Design and criterion: docs/p3_plan.md R1 (fixed before running).

## Design

- COPERNICUS/S2_SR_HARMONIZED, Jan 1 - May 1, Cloud Score+ cs_cdf >= 0.6, median; MNDWI = (B3 - B11)/(B3 + B11), B11 (20 m) bilinear to 10 m (effective resolution ~20 m across the water-land edge). 10 m grid in UTM 48N with the origin and footprint of each tile's Landsat raster.
- Same tiles, islands, transects and bank rule: the geometry (centerline / island ring, transects, open-river edge, belt limit) is rebuilt from each tile's Landsat stack exactly as banklines.py does (checked against the Landsat output) and sampled on the 10 m grid; banklines.positions runs with px = 10, so the canal-filter disc (9 px = 90 m) and the island area (9999 px = 1 km2) keep their physical size. All other extraction constants are along-transect, in metres or 5 m samples, and unchanged; the geometry-only pixel constants (centerline smoothing, gap closing, core / belt openings) are not applied to Sentinel-2 at all because the Landsat geometry is reused (this is what keeps the transect ids). Other-river masking and the > 2% nodata rule as for Landsat; spikes as for Landsat. Stitching and island tables reuse the Landsat keys.
- Landsat outputs unchanged: banklines.py only gained a pixel-size argument (default 30 m); reruns of sadec_caolanh, tien_03, hau_01 (narrow) and isl_tien_04 reproduce bank_positions.csv and trends.csv byte for byte (sha256).

### Composites

Scenes per dry season (S2 SR, tile footprint):

|             |   2017 |   2018 |   2019 |   2020 |   2021 |   2022 |   2023 |   2024 |
|:------------|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|
| hau_01      |      2 |      6 |     92 |    100 |     98 |     98 |     96 |     96 |
| hau_02      |      2 |      6 |     92 |    100 |     96 |     98 |     96 |     96 |
| hau_03      |      2 |      6 |     92 |    100 |     96 |     96 |     96 |     96 |
| hau_04      |      0 |      1 |     23 |     25 |     24 |     24 |     24 |     24 |
| hau_05      |      0 |      1 |     23 |     25 |     24 |     24 |     24 |     24 |
| hau_06      |      0 |      1 |     23 |     25 |     24 |     24 |     24 |     24 |
| hau_07      |      0 |      1 |     23 |     25 |     24 |     24 |     24 |     24 |
| hau_08      |      0 |      2 |     46 |     50 |     48 |     48 |     50 |     48 |
| isl_hau_01  |      0 |      1 |     23 |     25 |     24 |     24 |     24 |     24 |
| isl_hau_02  |      0 |      1 |     23 |     25 |     24 |     24 |     24 |     24 |
| isl_hau_03  |      0 |      1 |     23 |     25 |     24 |     24 |     24 |     24 |
| isl_hau_04  |      0 |      1 |     23 |     25 |     24 |     24 |     24 |     24 |
| isl_tien_01 |      0 |      4 |     46 |     50 |     48 |     49 |     48 |     48 |
| isl_tien_02 |      0 |      4 |     46 |     50 |     48 |     49 |     48 |     48 |
| isl_tien_03 |      0 |      4 |     46 |     50 |     48 |     48 |     48 |     48 |
| isl_tien_04 |      0 |      1 |     23 |     25 |     24 |     24 |     24 |     24 |
| isl_tien_05 |      0 |      1 |     23 |     25 |     24 |     24 |     24 |     24 |
| isl_tien_06 |      0 |      1 |     23 |     25 |     24 |     24 |     24 |     24 |
| isl_tien_07 |      0 |      1 |     23 |     25 |     24 |     24 |     24 |     24 |
| tien_01     |      2 |      6 |     92 |    100 |     98 |     98 |     96 |     96 |
| tien_02     |      0 |      4 |     46 |     50 |     49 |     50 |     48 |     48 |
| tien_03     |      0 |      4 |     46 |     50 |     48 |     48 |     48 |     48 |
| tien_04     |      0 |      1 |     23 |     25 |     24 |     24 |     24 |     24 |
| tien_05     |      0 |      1 |     23 |     25 |     24 |     24 |     24 |     24 |
| tien_06     |      0 |      1 |     23 |     25 |     24 |     24 |     24 |     24 |
| tien_07     |      1 |      2 |     46 |     50 |     48 |     48 |     48 |     48 |

Nodata share inside the own-river mask (%; x = dropped by the > 2% rule):

| tile        | 2017    | 2018   |   2019 |   2020 |   2021 |   2022 |   2023 |   2024 |
|:------------|:--------|:-------|-------:|-------:|-------:|-------:|-------:|-------:|
| hau_01      | 66.6 x  | 0.0    |      0 |      0 |      0 |      0 |      0 |      0 |
| hau_02      | 80.5 x  | 0.1    |      0 |      0 |      0 |      0 |      0 |      0 |
| hau_03      | 98.7 x  | 13.4 x |      0 |      0 |      0 |      0 |      0 |      0 |
| hau_04      | 100.0 x | 16.5 x |      0 |      0 |      0 |      0 |      0 |      0 |
| hau_05      | 100.0 x | 5.0 x  |      0 |      0 |      0 |      0 |      0 |      0 |
| hau_06      | 100.0 x | 0.9    |      0 |      0 |      0 |      0 |      0 |      0 |
| hau_07      | 100.0 x | 0.0    |      0 |      0 |      0 |      0 |      0 |      0 |
| hau_08      | 100.0 x | 0.0    |      0 |      0 |      0 |      0 |      0 |      0 |
| isl_hau_01  | 100.0 x | 0.0    |      0 |      0 |      0 |      0 |      0 |      0 |
| isl_hau_02  | 100.0 x | 0.0    |      0 |      0 |      0 |      0 |      0 |      0 |
| isl_hau_03  | 100.0 x | 0.0    |      0 |      0 |      0 |      0 |      0 |      0 |
| isl_hau_04  | 100.0 x | 0.0    |      0 |      0 |      0 |      0 |      0 |      0 |
| isl_tien_01 | 100.0 x | 0.0    |      0 |      0 |      0 |      0 |      0 |      0 |
| isl_tien_02 | 100.0 x | 0.0    |      0 |      0 |      0 |      0 |      0 |      0 |
| isl_tien_03 | 100.0 x | 0.0    |      0 |      0 |      0 |      0 |      0 |      0 |
| isl_tien_04 | 100.0 x | 0.0    |      0 |      0 |      0 |      0 |      0 |      0 |
| isl_tien_05 | 100.0 x | 0.0    |      0 |      0 |      0 |      0 |      0 |      0 |
| isl_tien_06 | 100.0 x | 0.0    |      0 |      0 |      0 |      0 |      0 |      0 |
| isl_tien_07 | 100.0 x | 0.0    |      0 |      0 |      0 |      0 |      0 |      0 |
| tien_01     | 100.0 x | 0.0    |      0 |      0 |      0 |      0 |      0 |      0 |
| tien_02     | 100.0 x | 0.0    |      0 |      0 |      0 |      0 |      0 |      0 |
| tien_03     | 100.0 x | 0.0    |      0 |      0 |      0 |      0 |      0 |      0 |
| tien_04     | 100.0 x | 0.0    |      0 |      0 |      0 |      0 |      0 |      0 |
| tien_05     | 100.0 x | 0.0    |      0 |      0 |      0 |      0 |      0 |      0 |
| tien_06     | 100.0 x | 0.0    |      0 |      0 |      0 |      0 |      0 |      0 |
| tien_07     | 60.3 x  | 0.0    |      0 |      0 |      0 |      0 |      0 |      0 |

## (a) Agreement with Landsat (in-scope transect-sides, 2017-2024, spikes left out)

diff = Sentinel-2 - Landsat distance from the same centerline (+ = Sentinel-2 bank further landward). 95% CIs: block bootstrap over 10 km blocks (h3.boot_index, B = 1000).

| group      |   Landsat banks |   S2 bank also (%) |   pairs |   blocks | median S2 - Landsat (m)   | robust SD (m)     | |diff| <= 30 m (%)   |
|:-----------|----------------:|-------------------:|--------:|---------:|:--------------------------|:------------------|:---------------------|
| all        |           48890 |                 84 |   41196 |       28 | 1.9 [0.8, 2.8]            | 13.1 [11.4, 14.8] | 95 [94, 97]          |
| Hau narrow |           11853 |                 78 |    9223 |       10 | 1.2 [0.0, 3.1]            | 10.3 [8.2, 13.0]  | 96 [94, 98]          |
| Hau wide   |            4547 |                 86 |    3892 |        5 | -1.9 [-7.0, -0.3]         | 13.9 [9.5, 19.7]  | 98 [94, 99]          |
| Island     |           14963 |                 86 |   12851 |        7 | 2.2 [-0.1, 3.9]           | 15.1 [11.6, 19.2] | 96 [93, 97]          |
| Tien main  |           17527 |                 87 |   15230 |       14 | 3.3 [2.0, 4.9]            | 13.0 [10.8, 15.5] | 94 [91, 97]          |

By year (pooled over groups):

| year   |   Landsat banks |   S2 bank also (%) |   pairs |   blocks | median S2 - Landsat (m)   | robust SD (m)     | |diff| <= 30 m (%)   |
|:-------|----------------:|-------------------:|--------:|---------:|:--------------------------|:------------------|:---------------------|
| all    |           48890 |                 84 |   41196 |       28 | 1.9 [0.8, 2.8]            | 13.1 [11.4, 14.8] | 95 [94, 97]          |
| 2017   |            6134 |                  0 |       0 |        0 | nan                       | nan               | nan                  |
| 2018   |            6171 |                 81 |    5028 |       25 | 2.4 [1.3, 3.3]            | 12.1 [10.6, 13.7] | 96 [95, 97]          |
| 2019   |            6189 |                 99 |    6098 |       28 | 2.0 [0.6, 3.1]            | 14.5 [12.2, 17.2] | 95 [93, 97]          |
| 2020   |            6039 |                 99 |    6003 |       28 | 1.5 [0.5, 2.5]            | 13.6 [11.7, 15.5] | 96 [94, 97]          |
| 2021   |            6130 |                 99 |    6076 |       28 | 2.3 [0.9, 3.2]            | 15.0 [12.8, 17.1] | 94 [92, 96]          |
| 2022   |            6034 |                 99 |    5996 |       28 | 2.2 [1.1, 3.1]            | 11.9 [10.4, 13.5] | 96 [95, 97]          |
| 2023   |            6172 |                 97 |    6002 |       28 | 1.0 [-0.3, 2.2]           | 12.4 [10.9, 14.1] | 96 [94, 97]          |
| 2024   |            6021 |                100 |    5993 |       28 | 2.0 [0.6, 3.1]            | 12.0 [10.4, 13.6] | 96 [94, 97]          |

### Accuracy against the hand clicks (same clicks, bank of the compared year from each sensor)

error = satellite - clicked (negative = satellite bank riverward). CI of the RMSE difference: bootstrap over clicks (1000, seed 0).

| group      |   with Landsat bank |   with S2 bank |   both |   Landsat RMSE (m) |   S2 RMSE (m) | S2 - Landsat RMSE (m) [95% CI]   |   Landsat bias (m) |   S2 bias (m) |   Landsat median abs (m) |   S2 median abs (m) |
|:-----------|--------------------:|---------------:|-------:|-------------------:|--------------:|:---------------------------------|-------------------:|--------------:|-------------------------:|--------------------:|
| all        |                  89 |             89 |     89 |               29.5 |          30.3 | 0.8 [-8.6, 10.5]                 |              -16.4 |         -11.3 |                     12.7 |                 9.7 |
| Tien main  |                  55 |             55 |     55 |               32.9 |          35.4 | 2.5 [-10.9, 15.7]                |              -18.2 |         -10.4 |                     13.9 |                 9.5 |
| Hau wide   |                  12 |             12 |     12 |               18.6 |          14.2 | -4.4 [-8.5, -1.0]                |              -10.1 |         -10   |                     15.6 |                10.3 |
| Hau narrow |                  13 |             13 |     13 |               30   |          27.1 | -2.9 [-14.4, 4.6]                |              -19.1 |         -18.5 |                     12.6 |                16.3 |
| Island     |                   9 |              9 |      9 |               15.3 |           9.6 | -5.7 [-11.6, 1.3]                |              -10.4 |          -7.5 |                     11.6 |                10.7 |

## (b) H2 with Sentinel-2 truth (frozen GBT intervals, h = 3, test rows)

Test rows 36288; with origin >= 2018 and a Sentinel-2 target: 22691 (origins [2018, 2019, 2020, 2021], targets [2021, 2022, 2023, 2024]). Truths on these rows: median y_S2 - y_Landsat -0.3 m, median |diff| 2.7 m, Spearman 0.69; |y| p90 Landsat 18.5 m, Sentinel-2 17.8 m. 95% CIs: forecast.boot (10 km blocks, 1000, seed 0).

| group      |     n |   blocks | mondrian vs Landsat truth   | split vs Landsat truth   | mondrian vs Sentinel-2 truth   | split vs Sentinel-2 truth   |
|:-----------|------:|---------:|:----------------------------|:-------------------------|:-------------------------------|:----------------------------|
| All        | 22691 |       28 | 92.8 [90.4, 95.0]           | 92.5 [90.0, 94.8]        | 92.6 [90.0, 94.9]              | 92.3 [89.7, 94.7]           |
| Tien main  |  8665 |       14 | 91.3 [87.3, 95.0]           | 91.1 [87.0, 94.8]        | 90.7 [86.8, 94.4]              | 90.6 [86.7, 94.3]           |
| Hau wide   |  2144 |        5 | 96.6 [91.1, 98.5]           | 97.7 [93.0, 99.2]        | 98.3 [95.6, 99.3]              | 98.9 [97.0, 99.6]           |
| Hau narrow |  4780 |       10 | 96.6 [94.3, 98.5]           | 96.5 [94.1, 98.5]        | 96.1 [93.8, 98.2]              | 96.1 [93.7, 98.1]           |
| Island     |  7102 |        7 | 91.0 [85.4, 94.8]           | 89.9 [83.9, 94.2]        | 90.8 [85.4, 94.9]              | 89.8 [84.0, 94.3]           |

**Verdict (criterion fixed in p3_plan R1: pooled coverage vs Sentinel-2 truth within 90 ± 3 pp):** split 92.3% (holds), Mondrian 92.6% (holds) -> H2 conclusion unchanged.

## (c) Unit window retreat 2017-19 -> 2022-24 (2 km H3 units; descriptive)

sat_labels rules (>= 2 valid years per 3-yr mean, |change| > 30 m/yr x 5 yr left out, unit p75 over >= 5 points). Units labelled by Landsat 343, by Sentinel-2 282, by both 282 (23 blocks). Median unit p75 difference S2 - Landsat -0.6 m.

- Spearman (unit p75): 0.82 [0.74, 0.88]
- Label >= 20 m: Landsat 23 positive, Sentinel-2 24, both 22; agreement 99 [98, 100]%; Cohen kappa 0.93 [0.84, 1.00]

Omission (share of satellite-eroding units never reported), 95% block-bootstrap CI:

| label                                         |   units |   satellite-eroding |   never reported | omission (%)   |
|:----------------------------------------------|--------:|--------------------:|-----------------:|:---------------|
| Landsat 2014->2023 (primary label, P2)        |     343 |                  43 |               12 | 28 [13, 44]    |
| Landsat 2018->2023, all labelled units        |     343 |                  23 |                7 | 30 [0, 64]     |
| Sentinel-2 2018->2023, all labelled units     |     282 |                  24 |                9 | 38 [8, 68]     |
| Landsat 2018->2023, units labelled by both    |     282 |                  23 |                7 | 30 [0, 64]     |
| Sentinel-2 2018->2023, units labelled by both |     282 |                  24 |                9 | 38 [8, 68]     |

## Caveats

- No usable Sentinel-2 SR composite for 2017 on any tile (0-2 SR scenes per dry season; the collection is sparse over the delta before late 2018), and 2018 composites come from 1-6 scenes; 2018 is dropped by the > 2% nodata rule on hau_03-hau_05 (the wide Hậu below Châu Đốc and Vàm Nao). Consequences: no 2017 pairs in (a); in (b) origin 2018 is missing where 2018 is dropped (centred mean needs 2 of 2017-2019); in (c) the 2017-19 mean rests on 2018-2019 only, and units on the three Hậu tiles get no Sentinel-2 label (343 -> 282 units).
- Effective resolution across the edge is ~20 m (B11 bilinear), not 10 m.
- Sentinel-2 reuses the Landsat geometry (centerline / ring, transects, open-river edge, belt limit) and the same bank rule, so it is an independent measurement of the bank position on each transect, not of the geometry or of rule-level errors (multi-edge banks, strips in front of the mainland). The hand clicks are the independent check.
- (b): the intervals were calibrated on Landsat targets; Sentinel-2 truth has its own noise (truths agree to a median 2.7 m, Spearman 0.69, because most 3-yr changes are small). The subset (origins 2018-2021) is the later part of the test period.
- (c): the 5-yr window has about half the positives of the primary 9-yr window (23 vs 43), so the omission shares have wide CIs; it is a sensor comparison, not a replacement label.
- Largest unit disagreement: tien_R_+050 (Landsat p75 5 m, Sentinel-2 94 m). Its downstream transects (T942-T950) flip between two edges ~180 m apart in both sensors (a strip or pond row in front of the bank); the sensors flip in different years, so the unit p75 differs. A multi-edge bank, not a Sentinel-2 processing error.

