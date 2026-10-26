# P3 plan: robustness, release, atlas (written 2026-10-26, before any P3 run)

Robustness checks named in `docs/protocol.md` section 4 that P2 already ran: 5 km and commune-bank units (H3), raw annual
target and linear-only series (H1/H2). The roadmap criterion for P3 is "conclusions unchanged"; for each check below the
criterion is fixed here, before running. Results are reported whatever they show.

## R1. Sentinel-2 banks 2017-2024

- Data: COPERNICUS/S2_SR_HARMONIZED, dry season Jan 1 - May 1 as for Landsat, clouds masked with Cloud Score+
  (cs_cdf >= 0.6), median composite; MNDWI = (B3 - B11)/(B3 + B11), B11 (20 m) resampled bilinearly to 10 m (effective
  resolution about 20 m, stated). Same tiles, islands, transects and bank rule as Landsat; every pixel-based constant of
  the extraction rescaled so its physical size is unchanged (Landsat outputs must stay byte-identical).
- Checks:
  (a) agreement with Landsat on the same transect-side and year (median difference, robust spread, share within 30 m) by
      channel group; and accuracy against the existing hand clicks (Landsat RMSE vs Sentinel-2 RMSE on the same clicks);
  (b) H2: the frozen Landsat-calibrated split / Mondrian intervals (GBT, h = 3) scored against retreat measured by
      Sentinel-2 (3-yr centred means, so origins >= 2018 and targets 2021-2024) on the test rows where both exist; the
      Landsat-truth coverage on the same rows is reported alongside. Unchanged if pooled coverage against Sentinel-2 truth
      is within 90 +- 3 pp for split and Mondrian;
  (c) labels: unit window retreat 2017-19 -> 2022-24 from Sentinel-2 vs Landsat over the same years (Spearman, agreement of
      the >= 20 m label, kappa) and the B omission share recomputed with each. Descriptive.

## R2. Placement error of reported rows (replaces the 100-500 m displacement; protocol deviation 6)

- Shift each reported row's set of 2 km units along its bank by k units (k = 1, 2, i.e. 2-4 km; direction random per row;
  same channel and side; clipped at the channel end); 200 draws per k (seed 0).
- Recompute per draw: H3 logistic leave-one-block-out AUC matrix and ΔAUC (point values), and B omission / commission
  shares. Full H3 decision (block bootstrap) on 20 draws per k.
- Unchanged if H3 is "not supported" in every full-decision draw and the median omission / commission shares lie inside the
  original 95% CIs.

## R3. Verification of the 2010 deterministic forecast (illustration, not a gate)

- Lam Dao Nguyen et al. 2010 (ISPRS Archives XXXVIII-8): weighted linear DSAS extrapolation, predicted bank retreat by 2015
  and 2020 at named sites (Sa Đéc, Hồng Ngự, Thường Phước, Long Khánh A, Châu Ma). Read the open-access PDF (kept local,
  not committed), take the predicted numbers as printed, locate the sites on our transects by name, and compare with our
  measured retreat 2009 -> 2015 and 2009 -> 2020 (3-yr means). Descriptive table and one figure panel; site matching
  uncertainty stated.

## R4. Release (Zenodo)

- Package: annual bank positions per transect-side (2000-2024, both rivers and islands; CSV + GeoPackage), trends, units,
  accuracy clicks, inventory (124 usable + reviewed rows, sources), unreported eroding reaches (plan C), code at a tagged
  commit, README with methods, accuracy and licences. Licences: bank data CC BY 4.0 (Landsat public domain); inventory and
  commune assignments carry share-alike terms (ODV CC-BY-SA, OSM/Kontur ODbL). Built locally; the owner uploads with their
  own Zenodo account (no token stored here).

## R5. Interactive web atlas

- Static page (Leaflet, no server): annual banks with a year slider, retreat rates, satellite labels, inventory points with
  sources, forecasts with intervals, unreported reaches. Built from the R4 files. Hosting needs a public URL (the code
  repository is private): owner chooses between a separate public repository (GitHub Pages) and another host.
