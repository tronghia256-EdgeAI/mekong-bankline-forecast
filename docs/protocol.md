# Analysis protocol (draft, not frozen)

Paper 3: coverage-verified forecasts of riverbank retreat (H1, H2) and label-source sensitivity of
erosion-susceptibility evaluation (H3), Tiền and Hậu rivers, Vietnamese Mekong Delta.

Status: DRAFT 2026-10-26. Frozen = committed and tagged `protocol-v1` after the owner's approval. Everything
below is decided before any forecast is scored on the test period and before reported and satellite labels are
compared. Changes after the freeze go to a dated "Deviations" section at the end, with reasons; the frozen
version stays in git.

> **Tóm tắt cho chủ đề tài.** Văn bản này chốt trước mọi lựa chọn phân tích (tầm dự báo, cách chia dữ liệu, mô
> hình, ngưỡng, phép kiểm) để không ai chọn lại sau khi đã thấy kết quả. Sau khi bạn duyệt, tôi gắn tag git và
> từ đó chỉ được sửa bằng mục "Deviations" có ghi ngày và lý do. Các mục **[QUYẾT]** cần bạn chọn; các mục
> **[TBD]** đã được điền ngày 26/10 từ kết quả nhãn vệ tinh và biến phụ trợ (chưa so với bộ kiểm kê).

## 0. Decisions for the owner

| # | Question | Proposal |
|---|---|---|
| D1 | Forecast horizons | 3 yr primary, 5 yr secondary (detectability at sadec: 25% / 40% of transect-sides change > 2x noise; 1 yr ~8% is mostly noise) |
| D2 | Test period | targets 2019-2024 (never used for any choice) |
| D3 | Coverage target and tolerance | 90%, pass if pooled coverage within ±3 percentage points |
| D4 | H3 unit | 2 km units primary (owner decision 22/10), commune-bank units as sensitivity, 5 km as sensitivity. Note: 80 of 124 reported rows are commune-level, so one row labels a median of 5 units of 2 km |
| D5 | Satellite label (H3) | Primary: 75th percentile of the unit's bank-point window retreat >= 20 m (47 of 352 units, 13%). Variants: >= 30 m; p90 >= 30 m; 'clean' (points with a > 60 m year-to-year jump in 2013-2024 dropped); 5 km units. Chosen on noise floor and prevalence only |
| D7 | Fixed label parameters | point change faster than 30 m/yr dropped (MAX_RATE); in-window jump > 60 m dropped for the 'clean' variant (WIN_JUMP); >= 5 points per unit (MIN_PTS) |
| D8 | Primary exposure proxy (H3 strata) | built-up share 0-1 km landward, GHSL 2020 (`built_1km`); population, night lights, road and town distance as alternatives |
| D6 | Which rows count as "reported" | `use_in_analysis == True` in data/hotspots/inventory.csv (owner-kept, measured bank, event year 2015-2024); warned-reach lists count as reported |

## 1. Data (fixed)

- Banks: annual dry-season (Jan-Apr median) Landsat 5/7/8/9 C2 L2 MNDWI banks 2000-2024, 100 m transects, Tiền
  border to Mỹ Thuận bridge, Hậu border to Cần Thơ bridge, 11 river islands of 1-150 km² measured all round
  (`src/banklines.py`, `src/stitch.py`, `src/islands_merge.py`). Spikes removed; series kinds linear / step /
  non-linear as in trends.csv. Scope: bank points inside pre-2025 communes of new An Giang and Đồng Tháp
  (`data/processed/units.csv`, `in_scope`).
- Measurement error: 3.1 m per composite (repeatability), no sensor bias; accuracy vs hand clicks RMSE 14-33 m by
  channel type (`docs/paper_notes.md`).
- Reported inventory: `data/hotspots/inventory.csv` (owner review 26/10, 124 rows usable).
- Covariates: `data/processed/covariates_2km.csv`, `covariates_5km.csv` (`src/covariates.py`, `results/p1/covariates.md`).
- Satellite labels: `data/processed/sat_labels_2km.csv`, `sat_labels_5km.csv`, `sat_events_2km.csv` (`src/sat_labels.py`,
  `results/p1/sat_labels.md`). Window retreat per bank point = mean position 2022-2024 minus mean 2013-2015 (>= 2 valid
  years in each). Noise floor of such a difference 5.8-9.3 m (95%).

## 2. H1 and H2: transect forecasts with conformal intervals

Unit of prediction: a transect-side (bank point). Target: bank retreat between the forecast origin t and t + h,
d(t+h) - d(t), in m (positive = retreat), where d(t) is the 3-yr centred mean position at t when available
(reduces composite noise; the raw annual value is a sensitivity).

Inclusion: in-scope transect-sides with >= 15 valid years before the origin. Primary evaluation on all included
series (linear, step and non-linear); linear-only is secondary. Excluding hard series would flatter coverage.

Temporal split (h = 3; h = 5 analogous):
- training: targets <= 2015;
- calibration (conformal): targets 2016-2018;
- test: targets 2019-2024. Inputs may use any year <= origin.

Spatial generalisation: leave-block-out over contiguous 10 km river blocks (blocks never split between training
and test within a fold); reported alongside the temporal split.

Models:
- Baselines: persistence (no change); end-point rate (EPR) and Theil-Sen linear extrapolation (LRR) over all years
  <= t and over the last 10 years.
- Learned: gradient-boosted trees (quantile loss for CQR) and a Gaussian process on lagged positions, rates over
  3/5/10-yr windows and covariates; hyperparameters chosen by CV inside the training period only.

Intervals (nominal 90%): Gaussian (model residual SD, the comparison that is expected to under-cover), split
conformal, CQR, Mondrian conformal by group (river x channel type: Tiền main, Hậu wide, Hậu narrow, island
channels), and adaptive conformal inference (ACI) over forecast origins.

Metrics: MAE and RMSE of retreat; empirical coverage, mean interval width and interval (Winkler) score; all with
95% CIs from a block bootstrap over 10 km blocks (1,000 resamples).

H1 decision: the learned model beats the best baseline if its test MAE is lower and the block-bootstrap 95% CI of
the MAE difference excludes 0; otherwise "not better" (reported either way).
H2 decision: a method holds coverage if pooled test coverage is within 90 ± 3 pp; coverage is also reported by
group and for the documented change periods (Vàm Nao after 2012; bed incision near Mỹ Thuận 2014-2017). Expected:
split conformal may under-cover in some groups, Mondrian and ACI hold, Gaussian under-covers.

## 3. H3: label-source sensitivity of susceptibility evaluation

Units: in-scope 2 km units with satellite data (D4; sensitivities: commune-bank units, 5 km units).

Labels (2015-2024):
- Reported: unit intersects >= 1 inventory row with `use_in_analysis` (D6). Sensitivity: event rows only
  (hamlet/landmark or emergency decision; warned-reach lists excluded).
- Satellite: D5 (primary p75 >= 20 m; variants as listed), chosen on noise floor and prevalence only (the
  satellite-reported comparison was not run when choosing). Units with < 5 points have no label and are excluded.
  Positives are concentrated (Tiền main 15%, Hậu main 2%, island channels about 24%), so results are also reported by
  river and channel type.

Susceptibility model: logistic regression with physical covariates only (`curv_bank`, `width_m`, `dwidth_00_14`,
`is_island`, `river_km`, `node_km`, pre-window retreat `pre_p75` 2001-2013; `dwidth_00_24` and `vamnao_km` are NOT inputs:
the first overlaps the label window, the second duplicates `river_km`, r = 0.98) and gradient boosting as a check. Exposure covariates
(built-up, population, road and town distance) are NOT model inputs; they define the strata in which the AUC gap
is examined.

Evaluation:
- Train on each label source, score against both: a 2x2 matrix of AUC (and PR-AUC), with spatial block CV over
  10 km blocks and cAUC to account for spatial clustering.
- The gap: ΔAUC = AUC(reported) - AUC(satellite) for the same scores, with block-bootstrap 95% CI.
- Gradient: ΔAUC within terciles of each exposure proxy (primary D8: `built_1km`); test of trend across terciles by
  block bootstrap. Curvature and built-up correlate (+0.33: outer banks are more built-up), which is why the physical
  check below is required.
- Physical check (risk 3 in the roadmap): relation of satellite-measured retreat to the same exposure proxies;
  if retreat itself rises with exposure, the gap gradient is interpreted only beyond that relation.

H3 decision: supported if ΔAUC differs from 0 (CI excludes 0) beyond the cAUC / block-CV uncertainty and the
gradient across exposure terciles is monotone with CI of the top-minus-bottom difference excluding 0.

## 4. Robustness (planned, P3)

Sentinel-2 10 m banks 2017-2024 for the test period; reported-site coordinate error 100-500 m (Steger 2016 style
displacement); 5 km and commune-bank units; raw annual instead of 3-yr mean positions; linear-only series.

Known data limits (stated in the paper): no embankment inventory (embanked reaches score low on satellite retreat);
2024 annual changes are one-sided and noisier, and 2012 has no composite, so annual events of those years are not
used; the Hậu above Châu Đốc is a narrow-mode reach (RMSE 30 m).

## 5. What is not done

No causal claims (only associated factors). No tuning on the test period. No change to label definitions,
thresholds or units after seeing the H3 comparison.

## Deviations

(none yet)
