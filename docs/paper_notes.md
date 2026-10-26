# Paper notes: figures, key numbers and decisions for the manuscript

Working notes for drafting (NHESS). Updated as results come in; every number here has a file behind it.
Status date: 2026-10-25. Main-channel figures and accuracy numbers are from 22/10; river islands (cù lao) are
measured all round by rule since 25/10 (the hand-picked branches of 22-24/10 were replaced).

## Figures (manuscript set, `python src/figures.py`)

All in `figures/` as PNG 300 dpi + SVG (text as text), sized to Copernicus columns (~8.3 / ~17 cm), text >= 7 pt,
CVD-safe categorical slots (blue, orange, aqua), diverging blue (accretion) - grey - red (erosion).

| File | Content | Draft caption | Inputs |
|---|---|---|---|
| fig01_study_area | Map of the analysed Tiền (127 km) and Hậu (146 km) reaches, three P0 test reaches, towns, pre-2025 provinces, inset | Study area: the Tiền and Hậu rivers from the Cambodian border to the Mỹ Thuận and Cần Thơ bridges. Boxes: test reaches used for accuracy checks (1 Sa Đéc–Cao Lãnh, 2 Long Xuyên, 3 Mỹ Thuận). Background: JRC Global Surface Water occurrence (Pekel et al., 2016). Province boundaries before the 2025 merger (FAO GAUL 2015). | JRC GSW v1.4, LSIB 2017, GAUL 2015, data/tiles.json |
| fig02_method_example | (a) Banks 2000 vs 2024 on the 2024 MNDWI composite at Bình Hàng Trung with transects; (b) annual bank series at T280L with Theil–Sen fit | Method illustration at Bình Hàng Trung (left bank of the Tiền, Cao Lãnh). (a) Dry-season banks of 2000 and 2024 on the 2024 MNDWI composite; transects every 100 m (every fifth drawn). (b) Bank retreat on transect T280 since 2000 with the Theil–Sen trend (18.5 m/yr, 95% CI 16.6–19.6); retreat slows after 2019. | data/processed/sadec_caolanh |
| fig03_bank_change | (a) Map of linear bank-change rates on both rivers; (b, c) along-river profiles, left/right banks | Bank change 2000–2024 from annual Landsat dry-season banks. (a) Theil–Sen rate per bank point (+ erosion); grey: step or non-linear series. (b, c) Rates along the Tiền and Hậu by distance from the border. | data/processed/{tien,hau}, units.csv |
| fig05_sat_labels | (a, b) Unit (2 km) window retreat 2014→2023 (75th percentile of bank points) along the Tiền and Hậu, L/R banks, with the 20 m label threshold; (c) distribution for main vs island channels | Satellite erosion labels. Retreat of 2 km bank units between the 3-yr mean positions around 2014 and 2023 (75th percentile of the unit's bank points). Dashed: label threshold (20 m, ≥ 2× the noise floor). | data/processed/sat_labels_2km.csv (`src/sat_labels.py`) |
| fig06_covariates | Along-river profiles of bank curvature, channel width (2000–2014) and built-up share 0–1 km landward (2020), Tiền and Hậu, with towns | Physical and exposure covariates of the 2 km units. | data/processed/covariates_2km.csv (`src/covariates.py`) |
| fig07_coverage | (a) Test coverage (90% intervals) by method and channel group, h = 3 yr, with the 90 ± 3 pp band; (b) pooled coverage vs mean interval width, h = 3 and 5; (c) coverage by test target year | Coverage of 90% prediction intervals for bank retreat on the 2019–2024 test period. Split, Mondrian and adaptive conformal intervals hold the nominal level (92%); Gaussian intervals over-cover with intervals 5× wider; CQR under-covers at h = 3. Bars: 95% block-bootstrap CI (10 km blocks). | data/processed/forecast_*.csv (`src/forecast.py`) |
| fig08_label_source | (a) AUC of a physical susceptibility model trained on each label source and scored against both (leave-one-block-out); (b) AUC gap by built-up tercile; (c) satellite window retreat vs built-up share | Label-source sensitivity at 2 km reach units. (a) AUC with block-bootstrap CI; (b) ΔAUC = AUC(reported) − AUC(satellite) by built-up tercile; (c) retreat 2014→2023 vs built-up share 0–1 km (dashed: 20 m label threshold). | data/processed/h3_*.csv (`src/h3.py`) |
| fig09_horizon (EXPLORATORY) | (a) Share of bank points whose change exceeds the 95% noise floor, h = 1–10 yr, by channel group; (b) rolling-origin test MAE of persistence, Theil–Sen (10 yr, all years), GBT and noise only, by horizon; (c) median rate error of thinned series vs annual rates by number of dates | Exploratory: forecast horizon and sampling interval. (a) Detectability with block-bootstrap bands (dashed: σ = 4.7 m); (b) targets 2019–2024, origins t = target − h, bars 95% block-bootstrap CI; (c) small markers: random date draws. GBT gain at h = 1–2 reflects known origin noise in the centred target, not bank movement. | data/processed/explore_horizon_*.csv (`src/explore_horizon.py`) |
| fig10_reporting (EXPLORATORY) | (a) Measured change class of reported units by source type and of never-reported units; (b) measured event rate from Y−3 to Y+3 around the reported year, reported vs never-reported units; (c, d) along-river strips: any report, event rows, satellite-eroding units (reported / never reported) | Exploratory: what the public reports capture. (a) Retreat 2014→2023 of 2 km units (no measurable change = within ±9.3 m); (b) unit-year events (p90 ≥ 15 m/yr; 2012, 2024 excluded) with block-bootstrap CI, controls matched on calendar year and channel group. | data/processed/explore_reporting_*.csv (`src/explore_reporting.py`) |
| fig11_sentinel2 | (a) Sentinel-2 minus Landsat bank position on the same transect-side and year (2018–2024) by channel group, share within ±30 m; (b) coverage of the frozen GBT split / Mondrian 90% intervals (h = 3) against Sentinel-2 and Landsat truth, with the 87–93% band; (c) unit p75 retreat 2018→2023, Sentinel-2 vs Landsat | Robustness to sensor resolution. Sentinel-2 SR (B3/B11 MNDWI, effective ~20 m) banks on the same transects as Landsat. | `src/gee_s2.py`, `src/s2_banks.py`, `src/p3_sentinel2.py`, results/p3/sentinel2.md |
| fig12_isprs2010 | Dumbbell chart: predicted (Lam Dao Nguyen et al., 2010) vs measured median bank retreat since 2009 at seven site-sides, 2015 and 2020, with the site-matching range | Verification of the 2010 deterministic forecast. Predicted change from the paper's appendices (weighted linear DSAS extrapolation, base 2009); measured from annual Landsat banks (3-yr means). Grey: range from two ways of matching the paper's sites to our transects. | `src/p3_isprs2010.py`, results/p3/isprs2010.md |
| figS1_placement (supplement) | (a) ΔAUC per training source for the original placement and 200 draws with reported rows shifted 2 km and 4 km along the bank; (b) omission and commission shares per draw with the original 95% CI | Placement sensitivity of the reported labels (protocol deviation 6). | `src/p3_placement.py`, results/p3/placement.md |
| fig04_validation | (a) Landsat minus hand-clicked bank by river / channel type; (b) eroded area vs SIWRR (Dinh et al., 2022) | Accuracy. (a) Difference between the Landsat bank and the bank clicked on Esri World Imagery Wayback (negative = Landsat bank riverward); bars = median. (b) Left-bank eroded area at Bình Hàng Trung per period, this study vs Dinh et al. (2022). | accuracy_review.csv per reach, tile_check.project |

Supplement candidates: `results/p0/sadec_caolanh_sensor_check.png` (sensor pairs, repeatability, window),
`results/p1/tiles.png` (tiles and coarse centerlines), per-tile quick-looks in `results/p1/tiles/` (not committed).
Planned: inventory map (P3); interactive web atlas (P3, owner's request 26/10): annual banks with a year slider, retreat
rates, satellite labels, inventory points with sources, forecasts with intervals; static site linked from Data availability.

## Key numbers

Measurement (P0, `results/p0/sadec_caolanh_sensor_check.md`):
- Sensor bias (pooled, block-bootstrap 95% CI): L7–L8 −0.2 m [−0.6, 0.2]; L8–L9 −0.2 m [−1.7, 1.5]; L5–L7 −1.0 m [−1.8, −0.3] → no harmonisation needed.
- Repeatability (two independent same-year composites): robust SD 4.3 m for the difference → 3.1 m per composite. Window Jan–Mar vs Feb–Apr: +1.0 m. Measured noise used: 3.6 m.
- SIWRR check (Bình Hàng Trung left bank, T255–315): −15.4, −45.7, −14.6, −30.6 ha vs −30.0, −41.5, −11.5, −23.0; total −106.3 vs −106.0 ha (`results/p0/sadec_caolanh_siwrr_check.md`).
- Detectability (sadec, linear transects, change > 2 × 3.6 m): ~8–9% at 1 yr, 25% at 3 yr, 40% at 5 yr → forecast horizon 3–5 yr.

Coverage (P1, main-channel checks of 22/10; `src/stitch.py`, `results/p1/tile_check.md`):
- Tiền 1,141 transects (in Vietnam) over ~127 km, 85% linear; Hậu 1,360 over ~146 km, 95% linear (incl. narrow reach above Châu Đốc).
- Stitched vs P0 reaches: median |diff| 0.9–5.7 m, |rate diff| 0.05–0.23 m/yr. Narrow vs normal mode on overlap: median diff 0.0 m, |diff| 3.7 m, 90% ≤ 15 m.
- River islands (25/10): 11 islands of 1–150 km² found by rule (holes of the connected river system in JRC ≥ 50%),
  each measured all round from a medial channel ring (island bank I, opposite bank O); ring banks within 150 m of a
  main-channel bank dropped, and (26/10, deviation 5) ring banks within 60 m of a lower-numbered island's ring bank
  dropped (adjacent islands measured the bank between them twice; 167 points). In scope (new An Giang + Đồng
  Tháp): 6,465 bank points, 390 units of 2 km, 172 of 5 km, 125 communes (`data/processed/units.csv`).

Accuracy vs hand clicks (Esri Wayback, final stitched product; `figures/fig04_validation`):
- Tiền n = 55, RMSE 33 m; Hậu wide n = 12, RMSE 19 m; Hậu narrow n = 13, RMSE 30 m; river-island channels n = 9, RMSE 15 m, median |err| 12 m after deviation 5 (before: n = 11, RMSE 14 m, median 9 m, `results/p1/islands_accuracy.md`; one of 12 clicks fell on a channel narrower than the canal filter and is a non-detection; two more, T7112O and T11092O, lie on ring banks dropped as duplicates of a neighbouring island's ring). Typical bias −10 to −20 m (Landsat bank riverward; wet-season imagery). Stable single-edge banks ~10–15 m.
- Known outlier types: multi-edge banks (vegetated strip/bar in front of ponds, ~100 m), transient riverward objects (T417L 2021–22), sharp bends and canal mouths (narrow reach).

P2 results (26/10, protocol-v1 + deviations 1-5; numbers AFTER the island-duplicate correction, deviation 5; `results/p2/forecast.md`, `results/p2/h3.md`):
- Sample: 6,177 transect-sides in 28 blocks of 10 km; h = 3 rows train 22,903 / calibration 16,049 / test 36,288 (h = 5: 19,127 / 10,792 / 36,255).
- H1 NOT supported: test MAE persistence 9.3 m [7.4, 11.4] vs GBT 9.9 [8.2, 11.9] (GBT worse, +0.59 [0.23, 0.98]) at h = 3; at h = 5 persistence 13.6 [10.5, 17.0] vs GBT 15.2 (+1.62 [0.31, 3.24]); GP 15.5 / 23.0 (GP fit on a 1,000-row subsample is unstable: 20.3 before the correction); rate extrapolation (LRR 10 yr) 12.3 / 20.4 — worse than persistence. Most banks move less than the noise over 3 yr.
- H2 SUPPORTED for split / Mondrian / ACI conformal: pooled test coverage 92.4 / 92.7 / 92.4% at h = 3 (width ~49 m), 91.5 / 91.5 / 91.5% at h = 5 (~85 m); Gaussian 99.5% with widths 246 / 314 m (fails, over-covers: heavy-tailed targets); CQR 79.5% at h = 3 (fails; feature shift from incomplete 2010-2013 composites), 93.0% at h = 5. By group h = 3 split: Tiền 90.5, Hậu wide 97.9, Hậu narrow 96.2, islands 90.1%. At h = 5 Hậu wide under-covers (84.7 split, 83.7 Mondrian). Spatial leave-block-out h = 3: split 92.3%. ACI identical to split by construction (deviation 4a).
- H3 NOT supported (logistic, 2 km): AUC trained on reported 0.50 (reported) / 0.57 (satellite); trained on satellite 0.52 / 0.72; ΔAUC −0.08 [−0.29, 0.25] and −0.20 [−0.40, 0.05]; tercile trend CIs include 0; all sensitivities fail. Exploratory: reported labels cover 76% of units (260/343) vs satellite 13% (43), agreement kappa −0.01 [−0.05, 0.02]; satellite retreat falls with built-up (Spearman −0.20 [−0.32, −0.07]; prevalence 22 / 12 / 3% by tercile).
- Before the correction (commit acaf6be): 6,342 transect-sides; H1 9.9 vs 10.0 m; H2 92.4 / 92.7% (h = 3), 91.9 / 91.8% (h = 5); CQR h = 3 70.8%; H3 ΔAUC −0.09 / −0.22; 47/352 satellite positives. No verdict changed (protocol deviation 5).

EXPLORATORY after P2 (26/10, planned in `docs/exploratory_plan.md` before running; no verdicts; CIs 10 km block bootstrap;
numbers after the island-duplicate correction, deviation 5):
- A, horizon (`results/p2/explore_horizon.md`): change above the noise floor (σ 3.6 m) for 27% [23, 31] of bank points at 1 yr,
  37% [32, 42] at 3 yr, 48% [43, 53] at 5 yr, 62% [58, 67] at 10 yr (h3: Tiền 40, Hậu wide 21, Hậu narrow 30, islands 42%;
  σ 4.7 m about 7 points lower). Rolling-origin MAE persistence / Theil–Sen 10 yr / Theil–Sen all / GBT: h1 3.7 / 4.2 / 5.2 / 2.8;
  h3 9.3 / 12.3 / 14.6 / 9.1; h5 13.6 / 20.4 / 24.6 / 13.9; h7 16.7 / 28.9 / 34.0 / 17.6 m. GBT − persistence: h1 −0.85 [−1.05,
  −0.68] (artefact: the centred target contains known origin noise), h2 −0.23 [−0.51, 0.03], h3 −0.23 [−0.57, 0.15], h5 +0.38
  [−0.47, 1.14]. Theil–Sen never beats persistence (excess +0.6 m at h1 to +12 m at h7). Split conformal 90–95% coverage at
  every horizon; persistence widths 16 / 51 / 103 / 132 m at h1 / 3 / 5 / 7. Thinned series vs annual: median |rate error| 0.09
  (every 2nd yr) to 0.25 (5th) and 0.35 m/yr (4 dates); sign changes 4–12%, 'significant' status changes 7–17% of
  transect-sides. The fixed confirmatory split's training/calibration targets overlap the earliest test origins; the strict
  rolling design gives the same H1 picture (state in the paper).
- B, reporting (`results/p2/explore_reporting.md`): omission 12 of 43 satellite-eroding units never reported, 28% [13, 44]
  (6 Tiền main, 6 islands; Hậu has 2 eroding units, both reported); 25/43 never as a dated event, 58% [47, 72]. Commission:
  201/260 reported units (77% [71, 84]) below the 9.3 m floor (warned lists 80%, news 70%, emergency decisions 88%, ODM 2018
  81%; Hậu main 89, Tiền main 74, islands 67%; built-up terciles 70 / 79 / 83%); never-reported units 81%. Timing (events
  ≥ 15 m/yr): reported units had fewer events than never-reported units in the 3 yr after the report, ratio 0.37 [0.09, 1.05]
  (0.48 [0.14, 1.48] matched on channel group), and before 0.35 [0.14, 0.89]; warned-list units vs not warned, next 1–3 yr
  0.49 [0.05, 0.96] (0.58 [0.08, 1.09] group-matched) → no sign that reports or warnings precede measured retreat. Largest
  unreported eroding units: Bình Hàng Tây / Bình Thạnh (Tiền L km 101–103, 156 / 137 m), Long Khánh A islands (134–148 m),
  Phú Thuận B (137 m, 6 points), An Hòa / An Bình A (111 m).
- Found by B (26/10, verified): ring banks of adjacent islands were measured twice (253 in-scope points within 30 m of another
  island channel) -> fixed by rule, protocol deviation 5; all analyses rerun.
- C, visual check (plan C, committed before sampling, dbbe527): 60 units (12 E_om, 12 E_rep, 24 N_rep, 12 N_non), blind owner
  review on Wayback old vs new imagery (`src/visual_check.py`, `results/p2/visual_check.md`; 60/60 answered 26/10; imagery
  median 2010-05 vs 2025-09, i.e. a longer span than the 2014→2023 label window). Exact 95% CIs.
  - Omission confirmed: 9/11 never-reported eroding units show clear land loss (82% [48, 98]; 1 cannot tell); of the 6
    omitted units with 110–156 m retreat, all 5 assessable clear (Long Khánh A, Bình Hàng Tây / Bình Thạnh, An Hòa / An
    Bình A); the sixth (V60, isl_tien_03_O_+000, 137 m) cannot tell (corrected 26/10 after internal review; was "all 6"). Owner notes: at
    Thường Phước 2 (tien_L_+004/+005) the loss is of a narrow strip in front of the mainland, not the mainland bank -> mainland
    bank loss 7/11 (64% [31, 89]).
  - Satellite label precision: 19/22 eroding-labelled units (reported or not) clear loss (86% [65, 97]); never-reported units
    below the floor 1/12 clear (8% [0, 38]).
  - Commission: reported units below the floor 6/23 clear loss (26% [10, 48]; owner notes: loss on part of the 2 km unit,
    e.g. Hòa Lạc, Bình Thạnh Đông, Vĩnh Lộc, An Hiệp) vs 8% in never-reported below-floor units -> reports partly capture
    short failures that the unit p75 label misses; 14/23 (61% [39, 80]) show neither loss nor protection.
  - Bank protection: none seen in any of the 60 units (0/60, [0, 6]), so visible embankments do not explain commission in
    this sample; the sample drew no town-centre reach with a known revetment (Tân Châu, Long Xuyên centre, Hồng Ngự town),
    and piles under vegetation are not visible from above.

P3 R1 (26/10, `results/p3/sentinel2.md`; criterion fixed in docs/p3_plan.md): Sentinel-2 SR 2018-2024 (no usable 2017
composite; 2018 thin, dropped by the > 2% nodata rule on hau_03-05), same transects as Landsat, Landsat outputs verified
byte-identical after adding the pixel-size argument. (a) S2 - Landsat on 41,196 transect-side-years: median +1.9 m [0.8, 2.8],
robust SD 13.1 m, 95% within 30 m (Tiền 94, Hậu wide 98, Hậu narrow 96, islands 96%); vs the same 89 hand clicks RMSE S2 30.3 m
vs Landsat 29.5 m (difference +0.8 [−8.6, 10.5]); S2 bias −11.3 vs −16.4 m, median |err| 9.7 vs 12.7 m. (b) UNCHANGED: frozen
GBT intervals (h = 3, origins 2018-2021, 22,691 test rows) cover 92.3% [89.7, 94.7] (split) and 92.6% [90.0, 94.9] (Mondrian)
of Sentinel-2-measured retreat (Landsat truth on the same rows 92.5 / 92.8%); by group split / Mondrian Tiền 90.6 / 90.7, Hậu
wide 98.9 / 98.3, Hậu narrow 96.1 / 96.1, islands 89.8 / 90.8. (c) unit retreat 2018→2023 (282 units): Spearman 0.82 [0.74,
0.88]; ≥ 20 m label 23 vs 24 positives, 22 shared, kappa 0.93 [0.84, 1.00]; omission 30% (Landsat) vs 38% (S2), wide CIs
(5-yr window). Shared rule-level errors (multi-edge banks, e.g. tien_R_+050) affect both sensors.

P3 R3 (26/10, `results/p3/isprs2010.md`; illustration): the 2010 forecast (Lam Dao Nguyen et al., ISPRS Archives XXXVIII-8,
appendices 1-7, every transect, base 2009) missed in both directions. Median retreat by 2020, measured vs predicted: Sa Đéc
(An Hiệp, Tiền R) 100 vs 252 m (retreat stopped after ~2015; 2001-09 rate 20 m/yr matched the paper); Thường Phước upstream
-1 vs 118; Thường Phước downstream 11 m vs 103 m of predicted accretion (the strong 2001-09 accretion did not continue);
Long Khánh A 198 vs 118 and 178 vs 71; "Châu Ma" east (isl_tien_04, matched by map grid only) 171 vs 142; west undecided (59 or
130 vs 123). Three headline numbers in the paper's text contradict its own appendices (appendix values used). Matches are
candidate stretches (paper maps 70-460 m off our composites); descriptive, seven site-sides.

P3 R2 (26/10, `results/p3/placement.md`, deviation 6; criterion fixed in docs/p3_plan.md): reported rows shifted along the
bank by 2 km (k = 1) and 4 km (k = 2), 200 draws each. UNCHANGED: H3 not supported in 40/40 full-decision draws (any-row and
event-only labels; fails on the tercile condition every time); median omission 26% [19, 35] (k = 1) and 28% [21, 40] (k = 2),
no event row 53% / 60%, commission 77% [75, 79] at both, all inside the original CIs. Note: the reported-trained values move
with placement (AUC against satellite 0.57 -> ~0.50; ΔAUC -0.08 -> +0.01 / +0.08), i.e. the original placement carries a weak
real erosion signal that a 2-4 km shift removes (consistent with plan C: reports catch short failures); trained on
satellite, the ΔAUC CI excludes 0 in 20 of 40 draws (did not originally). 58 of 124 rows list units on more than one
channel-side; island rings treated as open lines.

P3 R5 (26/10): forward forecast 2024 -> 2027 (`src/forecast_2027.py`, results/p3/forecast_2027.md; rolling design of A, GBT
fixed hyperparameters, no tuning; trained on targets <= 2023, calibrated on targets 2021-23): 90% half-widths GBT / persistence
split ±16.6 / ±19.6 m; Mondrian Tiền main 20.4 / 23.1, Hậu wide 9.0 / 9.3, Hậu narrow 12.7 / 13.0, islands 18.9 / 25.2 m;
median GBT forecast -1.8 m. The recent calibration years are the quietest (half-width 31 m for 2019 -> ~17 m for 2022-24, coverage
88.7-94.6% each year), so the 2027 bands assume 2024-27 as calm as 2021-23; width is constant per group (not a site risk score).
Interactive atlas `docs/atlas/` (Leaflet 1.9.4, static, 5.4 MB, EN/VI; `python src/release.py && python src/forecast_2027.py
&& python src/atlas_build.py`): annual banklines with year slider and reference year, 2 km retreat units with reported rows and
sources, unreported eroding reaches with the visual check, 2027 forecast band, Theil–Sen rates. Hosted with GitHub Pages from
/docs when the repository is made public (owner, 26/10).

P4 internal review round 1 (26/10, `paper/review_round1.md`; post hoc, descriptive, no refit; `src/p4_review_checks.py` ->
`results/p4/review_checks.md`): H2 coverage is marginal. Split GBT h = 3 by |Theil–Sen rate over the 10 yr before the origin|:
< 1 m/yr 97.4% [96.4, 98.2], 1–2 95.1, 2–5 91.3, 5–10 81.1, > 10 m/yr 60.2% [57.3, 63.8] (Mondrian 62.3; h = 5 68.0); rows
≥ 5 m/yr 71.9%; by kind linear 96.0, non-linear 72.0, step 65.8%. Zero-centred interval ±24.7 m covers 92.3% (h = 5 ±42.4 m:
93.3%). By origin h = 3 91.8–93.4% (calibration overlap does not inflate coverage); h = 5 target 2019 81.5% [71.6, 88.5].
Linear series among forecast transect sides 87% (Tiền 85, Hậu wide 97, Hậu narrow 95, islands 82%). Tiền clicks: 41 development
(Sa Đéc–Cao Lãnh, used to choose the bank rule) RMSE 34 m; 14 independent (Mỹ Thuận + new Tiền) RMSE 29 m. Corrected in the
manuscript: linear-only split h = 3 is 96.0% [94.6, 97.1] and raw-target split 93.4% [91.1, 95.3] (both fail; the draft had them
swapped as 90.0 / 96.0). H3 2×2: P(sat+ | rep+) 31/260 = 11.9%, P(sat+ | rep−) 12/83 = 14.5%, odds ratio 0.80. Under independence
omission would be 24% (observed 28%) and the below-floor share 78% (observed 77% reported, 81% unreported).

P4 post hoc analyses (26/10, owner approved; plan `docs/p4_posthoc_plan.md` committed before running, af64f18;
`python src/p4_posthoc.py run` -> `results/p4/posthoc.md`; GBT refit reproduces stored forecasts to 0.0005 m):
- PH1a Mondrian by past rate (classes < 2, 2–5, 5–10, ≥ 10 m/yr): h = 3 pooled 92.8% [90.7, 94.6], width 44.1 m (split 49.4),
  Winkler 91.9 (103.5); rate > 10 m/yr 86.1% [83.2, 88.7] (split 60.2); criterion missed only because < 1 m/yr is 95.2%.
  h = 5: pooled 90.5%, width 66.3 m (84.8), rate classes 86.7–92.5% -> criterion MET; > 10 m/yr 90.0%.
- PH1b normalised scores under-cover (76.5% h = 3, 83.7% h = 5): difficulty shifts between calibration and test (like CQR).
- PH2a robust-scale Gaussian 80.3% (both h); PH2b empirical OOF 5–95% 93.7% / 92.2% (close to split conformal; widths 56.7 /
  87.3 m). So conformal adds the guarantee, not better intervals; conditioning on past rate adds more.
- PH3 permutation within channel group (10 000): omission obs 27.9% vs null median 25.6% [14.0, 39.5]; commission 77.3% vs
  78.5% [76.2, 81.2]; gap −3.4 vs 1.4 [−8.2, 12.5] -> all consistent with independence.
- PH4 second rater (Nguyễn Việt Nam, 26/10 17:47-18:02; `results/p4/rater2.md`): visual check Q1 clear vs not agreement 50/57
  (88%), kappa 0.75; Q2 protection: no one saw any (100%, kappa undefined). Rater 2 clear loss: E_om 8/11 (r1 9/11), E_rep 10/11
  (10/11), N_rep 3/23 (6/23), N_non 0/12 (1/12) -> more conservative; the 'reports catch short failures' hint rests mainly on
  rater 1. Clicks: 20/20, 15 pairs on the same capture date, between raters RMSE 3 m, median 1 m; Landsat vs r1 20 m, vs r2 21 m.
  Rater 2 took 8 min for 60 units (median 7 s per answer) vs rater 1 39 min (15 s). Owner confirmed 26/10: Nam worked entirely on his own,
  blind to groups and to rater 1's answers; the owner only explained how to use the tool (rater 1 had to learn the task first).
- Review group B done 26/10: 7 references added after Crossref verification (freihardt2023, shampa2025, constantine2014,
  schwenk2017, brunier2014, jordan2019, vasilopoulos2021; no peer-reviewed CEGIS verification paper exists, CEGIS left out);
  fig07 shows h = 3 and h = 5 (ACI dropped, = split); figure units m yr^-1; label window '2013–15 to 2022–24' in figs 5, 8, 10;
  fig06 town labels clear of the curve; 30 m/yr rule removed 27 of 6033 window changes (0.4%) in 14 units, 7 labelled anyway
  (results/p4/review_checks.md); search paragraph corrected: the 104 queries are OpenAlex (84) + arXiv (20), not Crossref,
  plus Google Scholar (results/p0/g1_scholar_check.md).
- Title changed 26/10 (owner): "Coverage-verified forecasts of riverbank retreat and the limits of public erosion reports as
  hazard labels: Tien and Hau rivers, Vietnamese Mekong Delta".

Reported inventory (P1 draft, 25/10, `data/hotspots/inventory_draft.csv`): 187 rows = 158 G3 + 23 new
(quote-verified 23/23) + 6 ODV rows; 144 on measured banks, 4 on unmeasured banks, 3 unmatched, 36 out of scope.
Owner review done 26/10 (`src/inventory_server.py`, 151 rows -> `data/hotspots/inventory_review.csv`; final table
`data/hotspots/inventory.csv` by `src/inventory_final.py`): 141 kept, 8 duplicates (same commune, year and place as another
row; the commune-level warning merged into the specific event), 1 rejected (DT105: commune does not touch the Tien, site on
a canal), 1 unsure (DT118: source says Xa Phuoc Thuan, Hong Ngu; no such commune in the admin data, unresolved).
124 rows usable for labels (kept, on a measured bank, event year 2015-2024): 69 warned-reach lists, 41 news, 9 emergency
decisions, 5 ODM 2018. Kept rows outside the window: RC116, DT101, DT112-117 (before 2015) and 4 ODV points (no year; static
label only). Unmatched rows left unassigned on 26/10 rather than guessed: RC004 (Long Xuyen, 2012, outside the window anyway),
RC123 (city-level 'TP Cao Lanh', 3 km reach, ODM 2018), DT118 (Phuoc Thuan: no such commune; web searches for the commune
chairman named in the article found nothing). Check for the Methods: the machine's "confidence" is source specificity, not truth; the owner rejected 1 of 151.

## Method decisions (with dates)

- Water index: MNDWI, Landsat 5/7/8/9 C2 L2, dry season Jan 1–May 1 median, QA bits 1,3,4, 30 m UTM 48N; MNDWI clipped to [−1, 1]; Otsu per composite; composites with > 2% nodata dropped.
- Bank = "from the mainland, the first water" (owner's definition, 22/10): walking out from the open river; islands > 1 km² count as mainland; canals < ~90 m do not cut the mainland; ponds filled; sub-pixel MNDWI crossing.
- A bank found at the transect origin (centerline or island ring lying on the bank; channel narrower than the canal filter) is a non-detection (25/10; removed 1,448 sporadic rows in the narrow Hậu and 5% of island rows; P0 and Tiền outputs unchanged, Hậu 96% linear).
- Trends: Theil–Sen per transect-side; reverting jumps > 150 m removed as spikes; kinds linear / step / non-linear (robust residual scale > 30 m).
- Full rivers (P1): coarse JRC least-cost centerlines, 15 overlapping 30 km tiles, other river masked per tile (Vàm Nao), stitched by chainage; L/R looking downstream.
- Narrow mode (Hậu above Châu Đốc, width ~200 m; owner chose 22/10): canal filter ~90 m, no open-river core, smoothing 15 px, 1 km corridor.
- Island ring sides fixed 26/10: the I/O orientation test (island pixels 150 m out) failed on channels wider than 300 m and swapped I and O on all 11 islands; now decided by distance to the island on both sides. Positions identical, labels swapped (94% of I points now lie on the island outline); island clicks and review samples relabelled, accuracy unchanged (median |err| 9 m).
- Narrow mode: a bank farther than the 1 km corridor from the centerline is a non-detection (26/10; transects running along sharp bends in An Phú, 464 transect-years > 1.7 km removed, nothing else changed).
- Satellite labels (26/10, `results/p1/sat_labels.md`): unit window retreat = mean position 2022–24 minus 2013–15 per bank point (≥ 2 valid years each), point changes faster than 30 m/yr dropped; primary label p75 ≥ 20 m (43 of 343 units with ≥ 5 points after deviation 5, 13%; Tiền main 15%, Hậu main 2%, island channels 23%; before: 47 of 352); variants p75 ≥ 30 m, p90 ≥ 30 m, 'clean' (points with a > 60 m year-to-year jump in 2013–2024 dropped), 5 km units. Noise floor of a 3-yr mean difference 5.8–9.3 m.
- Covariates (26/10, `results/p1/covariates.md`): curvature (outer bank +), width 2000–2014, width change 2000–2014, distance from border / Vàm Nao / island nodes; exposure 2020: GHSL built-up and WorldPop 0–500 m and 0–1 km landward, VIIRS, OSM road and town distance. Physical–exposure correlations all |r| < 0.7 (largest curvature ~ built-up +0.33).
- Border: bank points outside Vietnamese communes dropped (Hậu is a border river at An Phú).
- Cù lao convention (owner chose B, 22/10; implemented by rule 25/10): every river island of 1–150 km² is measured all round (island bank and the opposite bank of each channel around it), so the unit set does not depend on where reports exist; duplicates within 150 m of main-channel banks dropped.
- H3 at reach level, 2 km units (5 km sensitivity); inventory scope = new An Giang + Đồng Tháp (old AG, DT, Tiền Giang).

## Data sources and licences (for Data availability)

Landsat C2 L2 (USGS, via Google Earth Engine); JRC Global Surface Water v1.4 (Pekel et al., 2016); LSIB 2017 (US DoS);
FAO GAUL 2015 (figure only); Kontur Boundaries Vietnam 2023-06-28 from OpenStreetMap (ODbL – credit "© OpenStreetMap
contributors"; share-alike if commune assignments are redistributed); Open Development Vietnam "Landslide points over
whole country in Vietnam" (CC-BY-SA); GHSL GHS-BUILT-S R2023A (JRC, CC BY 4.0); WorldPop 100 m 2020 (CC BY 4.0);
VIIRS VNL V2.1 (EOG, public domain per GEE catalogue); OSM roads and places 2020-01-01 (ODbL); Esri World Imagery Wayback (visual checks only); news and provincial sources
listed per row in the inventory.

## Limitations to state

30 m pixels vs sub-pixel collapses; multi-edge banks; transient objects; narrow reach accuracy (RMSE 30 m vs width
~200 m); wet-season reference imagery; reported labels mostly 2018–2024 and commune-level (reach-level H3).

## Literature anchors

Nguyen T.G. et al. 2025 (Physical Geography): pooled 95 reported/field + 272 Landsat points without comparing sources,
no spatial/temporal validation, no intervals. Steger et al. 2017, 2021 (inventory bias in landslide susceptibility);
Rüther et al. 2026 (NHESS, biased inventories inflate metrics); Villaça et al. 2024/2025 (newspaper inventories);
Langhorst & Pavelsky 2023 (global bank migration). Contribution 3 (owner, 26/10) = open annual bankline series 2000–2024
(with per-channel accuracy) + public inventory + blind-verified list of unreported eroding reaches; no "first" claim (Binh
et al. 2020, Remote Sens. 12:3298, Landsat bank detection in the VMD; Dente et al. 2026, EGU26-16468, global yearly river
positions). Citation names checked on Crossref 26/10: 10.1088/2515-7620/ae8ab8 = "Acceleration and spatial reorganization
of bank erosion under prolonged sediment starvation: multi-decadal evidence from the Vam Nao channel", Environ. Res.
Commun. 8(8), 085011 (2026); metadata lists the authors as Huy, Nguyen Dam Quoc; Van, Le Thi Thuy; Kim, Tran Thi
(Vietnamese order inverted; the first author is Nguyễn Đàm Quốc Huy). Cite as the DOI metadata gives it ("Huy et al., 2026"),
because reference checks match Crossref; the companion paper 10.1016/j.hydrch.2026.100046 (Hydrology Research) uses the same
"Huy, Nguyen Dam Quoc" form. Novelty statements are search-scope statements
(`results/p0/g1_scholar_check.md`).
