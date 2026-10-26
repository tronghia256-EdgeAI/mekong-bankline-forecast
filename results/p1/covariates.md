# Covariates per reach unit (H3)

`python src/covariates.py` -> `data/processed/covariates_2km.csv` (399 units), `covariates_5km.csv` (178 units); definitions in the module docstring. Built from 6632 in-scope bank points. Exposure reference year 2020 (middle of the inventory window 2015-2024; GHSL epoch, last WorldPop year); OSM state 2020-01-01. The reported inventory was not read; no relation to erosion or labels is computed here.

## Definitions, sources, licences

| Covariate | Definition | Source | Licence | Year |
|---|---|---|---|---|
| river_km | distance downstream of the border (km) | this study, coarse JRC centerline | - | - |
| curv_bank | curvature at the bank, + outer (1/km) | this study, Landsat banks (centerline) | - | 2000-2024 centre |
| curv_abs | |curvature| (1/km) | same | - | same |
| outer_share | share of points with curv_bank > 0.02/km | same | - | same |
| width_m | channel width, median 2000-2014 (m) | this study, Landsat banks | - | 2000-2014 |
| dwidth_00_14 | width change 2000-02 -> 2012-14 (m) | same | - | 2000-2014 |
| dwidth_00_24 | width change 2000-02 -> 2022-24 (m); NOT a model input | same | - | 2000-2024 |
| vamnao_km | along-river km from Vam Nao junction (+ downstream) | this study, coarse centerlines | - | - |
| node_km | along-river km to Vam Nao or an island head/tail | this study, tiles.json islands | - | - |
| built_500m | built-up share, landward 0-500 m (%) | GHSL GHS-BUILT-S R2023A (JRC) | EC reuse notice (CC BY 4.0), acknowledge source | 2020 |
| built_1km | built-up share, landward 0-1000 m (%) | same | same | 2020 |
| pop_500m | population density, landward 0-500 m (/km2) | WorldPop Global 100 m (unconstrained) | CC BY 4.0 | 2020 |
| pop_1km | population density, landward 0-1000 m (/km2) | same | CC BY 4.0 | 2020 |
| viirs_1km | night lights, landward 0-1000 m (nW/cm2/sr) | VIIRS VNL V2.1 annual (EOG, Colorado School of Mines) | public domain (GEE catalog terms) | 2020 |
| road_km | distance to OSM trunk/primary/secondary road, landward side (km) | OpenStreetMap (Overpass) | ODbL, (c) OpenStreetMap contributors | 2020-01-01 |
| town_km | distance to OSM place=city|town (km) | OpenStreetMap (Overpass) | ODbL | 2020-01-01 |

Categorical: river (tien/hau), channel, side (L/R/I/O), is_island (bank on an island channel ring).

## Summary, 2 km units (n = 399)

| Covariate | n | NaN | mean | p10 | median | p90 | min | max |
|---|---|---|---|---|---|---|---|---|
| river_km | 399 | 0 | 55.4 | 13 | 54.6 | 99.4 | -6.7 | 126 |
| curv_bank | 399 | 0 | -0.0515 | -0.452 | -0.0172 | 0.285 | -1.79 | 2.14 |
| curv_abs | 399 | 0 | 0.245 | 0.0356 | 0.134 | 0.608 | 0.0033 | 2.14 |
| outer_share | 399 | 0 | 0.414 | 0 | 0.25 | 1 | 0 | 1 |
| width_m | 390 | 9 | 810 | 191 | 753 | 1.44e+03 | 87.2 | 4.6e+03 |
| dwidth_00_14 | 381 | 18 | -41.4 | -122 | -8.12 | 55.1 | -1.3e+03 | 461 |
| dwidth_00_24 | 377 | 22 | -41.2 | -165 | -20.2 | 79.2 | -982 | 2.26e+03 |
| vamnao_km | 399 | 0 | 0.428 | -42.7 | 0.525 | 44.7 | -70.4 | 75.8 |
| node_km | 399 | 0 | 9.5 | 0.464 | 2.59 | 33.8 | 0 | 70.4 |
| built_500m | 399 | 0 | 10.5 | 1.66 | 9.38 | 19.3 | 0 | 36.6 |
| built_1km | 399 | 0 | 8.19 | 2.58 | 6.76 | 15 | 0 | 38.4 |
| pop_500m | 399 | 0 | 1.66e+03 | 644 | 1.29e+03 | 2.88e+03 | 240 | 9.53e+03 |
| pop_1km | 399 | 0 | 1.53e+03 | 651 | 1.15e+03 | 2.57e+03 | 238 | 1.6e+04 |
| viirs_1km | 399 | 0 | 1.87 | 0.356 | 1.33 | 3.58 | 0 | 19.7 |
| road_km | 399 | 0 | 1.73 | 0.113 | 1.25 | 3.88 | 0.0274 | 9.63 |
| town_km | 399 | 0 | 4.54 | 1.7 | 4.53 | 7.48 | 0.305 | 11.3 |

## Summary, 5 km units (n = 178)

| Covariate | n | NaN | mean | p10 | median | p90 | min | max |
|---|---|---|---|---|---|---|---|---|
| river_km | 178 | 0 | 55.5 | 12.6 | 54.5 | 97.5 | -6.7 | 126 |
| curv_bank | 178 | 0 | -0.0196 | -0.419 | -0.02 | 0.342 | -1.57 | 1.78 |
| curv_abs | 178 | 0 | 0.252 | 0.0534 | 0.173 | 0.58 | 0.0078 | 1.78 |
| outer_share | 178 | 0 | 0.443 | 0 | 0.377 | 1 | 0 | 1 |
| width_m | 176 | 2 | 783 | 182 | 741 | 1.35e+03 | 97.3 | 4.6e+03 |
| dwidth_00_14 | 176 | 2 | -39.3 | -76.8 | -11.8 | 37.8 | -966 | 324 |
| dwidth_00_24 | 174 | 4 | -33.2 | -130 | -21.9 | 58.7 | -916 | 2.26e+03 |
| vamnao_km | 178 | 0 | 0.648 | -42.2 | 2 | 42.6 | -70.4 | 75.5 |
| node_km | 178 | 0 | 8.97 | 0.579 | 1.98 | 32.1 | 0 | 70.4 |
| built_500m | 178 | 0 | 10.5 | 2.74 | 9.61 | 18.7 | 0 | 34 |
| built_1km | 178 | 0 | 8.21 | 3.25 | 7.12 | 14 | 0.16 | 35.8 |
| pop_500m | 178 | 0 | 1.68e+03 | 657 | 1.39e+03 | 2.76e+03 | 285 | 8.85e+03 |
| pop_1km | 178 | 0 | 1.55e+03 | 654 | 1.23e+03 | 2.4e+03 | 238 | 1.26e+04 |
| viirs_1km | 178 | 0 | 1.86 | 0.4 | 1.36 | 3.66 | 0 | 14.4 |
| road_km | 178 | 0 | 1.7 | 0.109 | 1.3 | 3.69 | 0.0321 | 8.79 |
| town_km | 178 | 0 | 4.47 | 1.7 | 4.43 | 7.25 | 0.305 | 10.3 |

Units by channel type (2 km): ('hau', 0) 116, ('hau', 1) 21, ('tien', 0) 127, ('tien', 1) 135

## Correlation among covariates (2 km units)

Pairs with |r| > 0.7 (Spearman rho or Pearson r):

- river_km ~ vamnao_km: rho = +0.98, r = +0.98
- curv_bank ~ outer_share: rho = +0.90, r = +0.65
- dwidth_00_14 ~ dwidth_00_24: rho = +0.92, r = +0.83
- built_500m ~ built_1km: rho = +0.82, r = +0.86
- built_500m ~ pop_500m: rho = +0.84, r = +0.84
- built_500m ~ pop_1km: rho = +0.78, r = +0.74
- built_1km ~ pop_500m: rho = +0.73, r = +0.84
- built_1km ~ pop_1km: rho = +0.80, r = +0.86
- built_1km ~ viirs_1km: rho = +0.66, r = +0.81
- pop_500m ~ pop_1km: rho = +0.96, r = +0.93
- pop_500m ~ viirs_1km: rho = +0.51, r = +0.72
- pop_1km ~ viirs_1km: rho = +0.58, r = +0.83

Physical x exposure pairs with |rho| > 0.3 (confounding to watch in H3):

- river_km ~ viirs_1km: rho = +0.45
- vamnao_km ~ viirs_1km: rho = +0.39
- curv_bank ~ built_500m: rho = +0.33
- curv_bank ~ built_1km: rho = +0.32
- outer_share ~ road_km: rho = -0.31
- outer_share ~ built_500m: rho = +0.30

## Notes and checks

- Island bank labels: share of bank points lying on the island (tiles.json outline + 100 m): side I 94%, side O 27%. If I is low and O high, the I/O labels in units.csv are the reverse of the documented convention (I = island bank). curv_bank uses the bank normals, not the labels, so it is unaffected; on_island_share gives the side geometrically.
- Transects whose 2000-2014 width exceeds 2.5x the 4 km running median (likely failed detections, bank picked km away): 9: hau T37, hau T200, hau T281, hau T282, hau T283, hau T284, hau T285, hau T320, hau T321. Unit widths are medians, so a minority of such transects does not move them; their bank points also shift the landward exposure samples.
- Curvature of main channels is from the coarse JRC centerline (the stitched fine centres jump between channels at tile seams). On island rings it is the ring curvature: the bank facing the island is mostly inner by construction, and island heads/tails (flow splits) show as sharp bends.
- Vam Nao junction = closest approach of the two coarse centerlines more than 20 km below the border (Tien km 50.5, Hau km 63.7); vamnao_km is river_km shifted per river, hence rho ~ 0.98 with river_km (use one of them).
- Exposure strips follow the bank normal landward; on islands they run into the island and may cross it. road_km ignores roads across the channel (half-plane test), town_km does not (ferries and bridges).
- OSM queried as of 2020-01-01 (Overpass attic); places are OSM place=city|town nodes (cities, district seats and some townships), 53 in the box incl. Cambodian ones near the border.
- dwidth_00_24 overlaps the 2015-2024 label window and must not be a model input; dwidth_00_14 and width_m use 2000-2014 only.

Spearman rho matrix:

| | river_km | curv_bank | curv_abs | outer_share | width_m | dwidth_00_14 | dwidth_00_24 | vamnao_km | node_km | built_500m | built_1km | pop_500m | pop_1km | viirs_1km | road_km | town_km |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| river_km | +1.00 | +0.02 | -0.10 | +0.01 | +0.27 | +0.01 | +0.06 | +0.98 | -0.02 | +0.00 | +0.19 | -0.08 | -0.01 | +0.45 | +0.07 | +0.22 |
| curv_bank | +0.02 | +1.00 | -0.18 | +0.90 | +0.06 | +0.06 | +0.06 | +0.02 | +0.11 | +0.33 | +0.32 | +0.27 | +0.27 | +0.17 | -0.28 | +0.03 |
| curv_abs | -0.10 | -0.18 | +1.00 | -0.02 | -0.36 | -0.08 | -0.08 | -0.09 | -0.30 | -0.18 | -0.21 | -0.10 | -0.13 | -0.12 | +0.05 | +0.03 |
| outer_share | +0.01 | +0.90 | -0.02 | +1.00 | +0.02 | +0.02 | +0.02 | +0.00 | +0.06 | +0.30 | +0.28 | +0.27 | +0.28 | +0.19 | -0.31 | +0.02 |
| width_m | +0.27 | +0.06 | -0.36 | +0.02 | +1.00 | +0.21 | +0.11 | +0.30 | -0.15 | -0.03 | +0.12 | -0.14 | -0.06 | +0.13 | +0.01 | +0.04 |
| dwidth_00_14 | +0.01 | +0.06 | -0.08 | +0.02 | +0.21 | +1.00 | +0.92 | +0.06 | -0.11 | -0.08 | -0.09 | -0.15 | -0.15 | -0.16 | +0.09 | +0.04 |
| dwidth_00_24 | +0.06 | +0.06 | -0.08 | +0.02 | +0.11 | +0.92 | +1.00 | +0.10 | -0.07 | -0.15 | -0.15 | -0.22 | -0.22 | -0.20 | +0.10 | +0.08 |
| vamnao_km | +0.98 | +0.02 | -0.09 | +0.00 | +0.30 | +0.06 | +0.10 | +1.00 | -0.08 | -0.04 | +0.15 | -0.12 | -0.05 | +0.39 | +0.05 | +0.24 |
| node_km | -0.02 | +0.11 | -0.30 | +0.06 | -0.15 | -0.11 | -0.07 | -0.08 | +1.00 | +0.12 | +0.08 | +0.09 | +0.08 | +0.11 | -0.02 | +0.14 |
| built_500m | +0.00 | +0.33 | -0.18 | +0.30 | -0.03 | -0.08 | -0.15 | -0.04 | +0.12 | +1.00 | +0.82 | +0.84 | +0.78 | +0.46 | -0.44 | -0.14 |
| built_1km | +0.19 | +0.32 | -0.21 | +0.28 | +0.12 | -0.09 | -0.15 | +0.15 | +0.08 | +0.82 | +1.00 | +0.73 | +0.80 | +0.66 | -0.39 | -0.14 |
| pop_500m | -0.08 | +0.27 | -0.10 | +0.27 | -0.14 | -0.15 | -0.22 | -0.12 | +0.09 | +0.84 | +0.73 | +1.00 | +0.96 | +0.51 | -0.54 | -0.25 |
| pop_1km | -0.01 | +0.27 | -0.13 | +0.28 | -0.06 | -0.15 | -0.22 | -0.05 | +0.08 | +0.78 | +0.80 | +0.96 | +1.00 | +0.58 | -0.53 | -0.26 |
| viirs_1km | +0.45 | +0.17 | -0.12 | +0.19 | +0.13 | -0.16 | -0.20 | +0.39 | +0.11 | +0.46 | +0.66 | +0.51 | +0.58 | +1.00 | -0.30 | -0.25 |
| road_km | +0.07 | -0.28 | +0.05 | -0.31 | +0.01 | +0.09 | +0.10 | +0.05 | -0.02 | -0.44 | -0.39 | -0.54 | -0.53 | -0.30 | +1.00 | +0.07 |
| town_km | +0.22 | +0.03 | +0.03 | +0.02 | +0.04 | +0.04 | +0.08 | +0.24 | +0.14 | -0.14 | -0.14 | -0.25 | -0.26 | -0.25 | +0.07 | +1.00 |
