# Covariates per reach unit (H3)

`python src/covariates.py` -> `data/processed/covariates_2km.csv` (390 units), `covariates_5km.csv` (172 units); definitions in the module docstring. Built from 6465 in-scope bank points. Exposure reference year 2020 (middle of the inventory window 2015-2024; GHSL epoch, last WorldPop year); OSM state 2020-01-01. The reported inventory was not read; no relation to erosion or labels is computed here.

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

## Summary, 2 km units (n = 390)

| Covariate | n | NaN | mean | p10 | median | p90 | min | max |
|---|---|---|---|---|---|---|---|---|
| river_km | 390 | 0 | 55.7 | 13 | 54.8 | 101 | -6.7 | 126 |
| curv_bank | 390 | 0 | -0.0596 | -0.454 | -0.0202 | 0.268 | -1.79 | 2.2 |
| curv_abs | 390 | 0 | 0.243 | 0.0356 | 0.134 | 0.608 | 0.0033 | 2.2 |
| outer_share | 390 | 0 | 0.411 | 0 | 0.23 | 1 | 0 | 1 |
| width_m | 382 | 8 | 794 | 191 | 755 | 1.43e+03 | 87.2 | 3.85e+03 |
| dwidth_00_14 | 373 | 17 | -41.1 | -122 | -8.81 | 51.3 | -1.3e+03 | 1.73e+03 |
| dwidth_00_24 | 369 | 21 | -40.7 | -171 | -20.5 | 74.3 | -982 | 2.26e+03 |
| vamnao_km | 390 | 0 | 0.601 | -42.7 | 1.01 | 45.4 | -70.4 | 75.8 |
| node_km | 390 | 0 | 9.69 | 0.462 | 2.69 | 34.6 | 0 | 70.4 |
| built_500m | 390 | 0 | 10.5 | 1.67 | 9.44 | 19.3 | 0 | 36.6 |
| built_1km | 390 | 0 | 8.27 | 2.54 | 6.8 | 15.2 | 0 | 38.4 |
| pop_500m | 390 | 0 | 1.67e+03 | 644 | 1.3e+03 | 2.9e+03 | 240 | 9.53e+03 |
| pop_1km | 390 | 0 | 1.54e+03 | 658 | 1.16e+03 | 2.58e+03 | 238 | 1.6e+04 |
| viirs_1km | 390 | 0 | 1.9 | 0.402 | 1.36 | 3.66 | 0 | 19.7 |
| road_km | 390 | 0 | 1.72 | 0.11 | 1.22 | 3.88 | 0.0274 | 9.63 |
| town_km | 390 | 0 | 4.54 | 1.7 | 4.53 | 7.5 | 0.305 | 11.3 |

## Summary, 5 km units (n = 172)

| Covariate | n | NaN | mean | p10 | median | p90 | min | max |
|---|---|---|---|---|---|---|---|---|
| river_km | 172 | 0 | 55.9 | 12.5 | 56 | 97.5 | -6.7 | 126 |
| curv_bank | 172 | 0 | -0.0298 | -0.425 | -0.0244 | 0.311 | -1.57 | 1.62 |
| curv_abs | 172 | 0 | 0.247 | 0.0503 | 0.168 | 0.577 | 0.0078 | 1.62 |
| outer_share | 172 | 0 | 0.438 | 0 | 0.372 | 1 | 0 | 1 |
| width_m | 171 | 1 | 751 | 182 | 739 | 1.34e+03 | 97.3 | 2.71e+03 |
| dwidth_00_14 | 171 | 1 | -40.1 | -90.1 | -12.3 | 34.4 | -966 | 985 |
| dwidth_00_24 | 169 | 3 | -32.5 | -131 | -22.6 | 54.6 | -916 | 2.26e+03 |
| vamnao_km | 172 | 0 | 0.886 | -42.8 | 2.55 | 43.7 | -70.4 | 75.5 |
| node_km | 172 | 0 | 9.25 | 0.628 | 2.07 | 32.1 | 0 | 70.4 |
| built_500m | 172 | 0 | 10.6 | 2.83 | 9.67 | 18.7 | 0 | 34 |
| built_1km | 172 | 0 | 8.33 | 3.51 | 7.33 | 14.3 | 0.16 | 35.8 |
| pop_500m | 172 | 0 | 1.7e+03 | 666 | 1.39e+03 | 2.79e+03 | 285 | 8.85e+03 |
| pop_1km | 172 | 0 | 1.57e+03 | 674 | 1.24e+03 | 2.45e+03 | 238 | 1.26e+04 |
| viirs_1km | 172 | 0 | 1.91 | 0.431 | 1.4 | 3.67 | 0 | 14.4 |
| road_km | 172 | 0 | 1.68 | 0.109 | 1.23 | 3.68 | 0.0321 | 8.79 |
| town_km | 172 | 0 | 4.49 | 1.71 | 4.41 | 7.32 | 0.305 | 10.3 |

Units by channel type (2 km): ('hau', 0) 116, ('hau', 1) 21, ('tien', 0) 127, ('tien', 1) 126

## Correlation among covariates (2 km units)

Pairs with |r| > 0.7 (Spearman rho or Pearson r):

- river_km ~ vamnao_km: rho = +0.98, r = +0.98
- curv_bank ~ outer_share: rho = +0.89, r = +0.65
- dwidth_00_14 ~ dwidth_00_24: rho = +0.92, r = +0.86
- built_500m ~ built_1km: rho = +0.82, r = +0.86
- built_500m ~ pop_500m: rho = +0.84, r = +0.84
- built_500m ~ pop_1km: rho = +0.78, r = +0.74
- built_1km ~ pop_500m: rho = +0.73, r = +0.84
- built_1km ~ pop_1km: rho = +0.80, r = +0.86
- built_1km ~ viirs_1km: rho = +0.65, r = +0.80
- pop_500m ~ pop_1km: rho = +0.96, r = +0.93
- pop_500m ~ viirs_1km: rho = +0.50, r = +0.71
- pop_1km ~ viirs_1km: rho = +0.57, r = +0.82

Physical x exposure pairs with |rho| > 0.3 (confounding to watch in H3):

- river_km ~ viirs_1km: rho = +0.46
- vamnao_km ~ viirs_1km: rho = +0.41
- curv_bank ~ built_500m: rho = +0.35
- curv_bank ~ built_1km: rho = +0.33
- outer_share ~ road_km: rho = -0.32
- outer_share ~ built_500m: rho = +0.31

## Notes and checks

- Island bank labels: share of bank points lying on the island (tiles.json outline + 100 m): side I 94%, side O 12%. If I is low and O high, the I/O labels in units.csv are the reverse of the documented convention (I = island bank). curv_bank uses the bank normals, not the labels, so it is unaffected; on_island_share gives the side geometrically.
- Transects whose 2000-2014 width exceeds 2.5x the 4 km running median (likely failed detections, bank picked km away): 9: hau T37, hau T200, hau T281, hau T282, hau T283, hau T284, hau T285, hau T320, hau T321. Unit widths are medians, so a minority of such transects does not move them; their bank points also shift the landward exposure samples.
- Curvature of main channels is from the coarse JRC centerline (the stitched fine centres jump between channels at tile seams). On island rings it is the ring curvature: the bank facing the island is mostly inner by construction, and island heads/tails (flow splits) show as sharp bends.
- Vam Nao junction = closest approach of the two coarse centerlines more than 20 km below the border (Tien km 50.5, Hau km 63.7); vamnao_km is river_km shifted per river, hence rho ~ 0.98 with river_km (use one of them).
- Exposure strips follow the bank normal landward; on islands they run into the island and may cross it. road_km ignores roads across the channel (half-plane test), town_km does not (ferries and bridges).
- OSM queried as of 2020-01-01 (Overpass attic); places are OSM place=city|town nodes (cities, district seats and some townships), 53 in the box incl. Cambodian ones near the border.
- dwidth_00_24 overlaps the 2015-2024 label window and must not be a model input; dwidth_00_14 and width_m use 2000-2014 only.

Spearman rho matrix:

| | river_km | curv_bank | curv_abs | outer_share | width_m | dwidth_00_14 | dwidth_00_24 | vamnao_km | node_km | built_500m | built_1km | pop_500m | pop_1km | viirs_1km | road_km | town_km |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| river_km | +1.00 | +0.01 | -0.11 | -0.01 | +0.28 | +0.03 | +0.06 | +0.98 | -0.02 | +0.01 | +0.20 | -0.07 | -0.00 | +0.46 | +0.08 | +0.21 |
| curv_bank | +0.01 | +1.00 | -0.20 | +0.89 | +0.06 | +0.05 | +0.05 | +0.00 | +0.13 | +0.35 | +0.33 | +0.29 | +0.29 | +0.20 | -0.30 | +0.02 |
| curv_abs | -0.11 | -0.20 | +1.00 | -0.04 | -0.37 | -0.09 | -0.09 | -0.10 | -0.29 | -0.18 | -0.21 | -0.10 | -0.12 | -0.12 | +0.05 | +0.02 |
| outer_share | -0.01 | +0.89 | -0.04 | +1.00 | +0.01 | +0.02 | +0.02 | -0.01 | +0.08 | +0.31 | +0.29 | +0.28 | +0.29 | +0.21 | -0.32 | +0.02 |
| width_m | +0.28 | +0.06 | -0.37 | +0.01 | +1.00 | +0.20 | +0.12 | +0.31 | -0.15 | -0.03 | +0.13 | -0.14 | -0.06 | +0.14 | -0.00 | +0.05 |
| dwidth_00_14 | +0.03 | +0.05 | -0.09 | +0.02 | +0.20 | +1.00 | +0.92 | +0.07 | -0.10 | -0.07 | -0.08 | -0.14 | -0.14 | -0.13 | +0.07 | +0.04 |
| dwidth_00_24 | +0.06 | +0.05 | -0.09 | +0.02 | +0.12 | +0.92 | +1.00 | +0.10 | -0.06 | -0.13 | -0.14 | -0.20 | -0.20 | -0.17 | +0.08 | +0.07 |
| vamnao_km | +0.98 | +0.00 | -0.10 | -0.01 | +0.31 | +0.07 | +0.10 | +1.00 | -0.08 | -0.03 | +0.16 | -0.11 | -0.05 | +0.41 | +0.06 | +0.23 |
| node_km | -0.02 | +0.13 | -0.29 | +0.08 | -0.15 | -0.10 | -0.06 | -0.08 | +1.00 | +0.12 | +0.08 | +0.09 | +0.08 | +0.10 | -0.02 | +0.14 |
| built_500m | +0.01 | +0.35 | -0.18 | +0.31 | -0.03 | -0.07 | -0.13 | -0.03 | +0.12 | +1.00 | +0.82 | +0.84 | +0.78 | +0.46 | -0.43 | -0.12 |
| built_1km | +0.20 | +0.33 | -0.21 | +0.29 | +0.13 | -0.08 | -0.14 | +0.16 | +0.08 | +0.82 | +1.00 | +0.73 | +0.80 | +0.65 | -0.38 | -0.13 |
| pop_500m | -0.07 | +0.29 | -0.10 | +0.28 | -0.14 | -0.14 | -0.20 | -0.11 | +0.09 | +0.84 | +0.73 | +1.00 | +0.96 | +0.50 | -0.54 | -0.24 |
| pop_1km | -0.00 | +0.29 | -0.12 | +0.29 | -0.06 | -0.14 | -0.20 | -0.05 | +0.08 | +0.78 | +0.80 | +0.96 | +1.00 | +0.57 | -0.53 | -0.24 |
| viirs_1km | +0.46 | +0.20 | -0.12 | +0.21 | +0.14 | -0.13 | -0.17 | +0.41 | +0.10 | +0.46 | +0.65 | +0.50 | +0.57 | +1.00 | -0.28 | -0.25 |
| road_km | +0.08 | -0.30 | +0.05 | -0.32 | -0.00 | +0.07 | +0.08 | +0.06 | -0.02 | -0.43 | -0.38 | -0.54 | -0.53 | -0.28 | +1.00 | +0.07 |
| town_km | +0.21 | +0.02 | +0.02 | +0.02 | +0.05 | +0.04 | +0.07 | +0.23 | +0.14 | -0.12 | -0.13 | -0.24 | -0.24 | -0.25 | +0.07 | +1.00 |
