# P4 post hoc analyses after internal review round 1 (plan, written before running)

Owner approved 26/10 (after `paper/review_round1.md`, M1, M6, M7, M9). These analyses come after the confirmatory results
and after the conditional under-coverage was seen (`results/p4/review_checks.md`), so they are **post hoc**: they are
reported as such, they change no protocol verdict, and their design and criteria below are fixed before any of them is
run. Script: `src/p4_posthoc.py`; report: `results/p4/posthoc.md`.

## PH1. Locally adaptive conformal intervals (M1)

Same rows, GBT point forecasts and calibration/test split as H2 (`data/processed/forecast_h{3,5}_mean.csv`; calibration
targets 2016-2018, test targets 2019-2024, at both horizons), alpha = 0.1.
- **(a) Mondrian by past rate.** Classes of |Theil-Sen rate over the 10 years before the origin| (`rate10`): < 2, 2-5,
  5-10, >= 10 m/yr (rows without rate10 go to < 2). q-hat per class from the calibration rows of that class.
- **(b) Normalised scores** (locally weighted conformal, Lei et al. 2018). A difficulty model sigma(x) = gradient boosting
  (absolute-error loss, the GBT point hyperparameters of the same horizon from `results/p2/forecast.md`) regressing the
  absolute out-of-fold training residual of the GBT on the GBT features, fitted on training rows only; sigma floored at
  1 m. Score |y - yhat| / sigma; interval yhat +- q-hat sigma.
- Out-of-fold training residuals: the GBT refitted with the stored hyperparameters in 5-fold cross-validation grouped by
  10 km block on the training rows (as `forecast.tune_gbt`). Reproducibility check: the GBT refitted on all training rows
  must reproduce the stored test forecasts (max |difference| < 0.01 m); otherwise stop and report.
- Reported for split (reference), PH1a and PH1b: pooled coverage, mean width, Winkler score, and coverage by the five rate
  classes of `review_checks.md` (< 1, 1-2, 2-5, 5-10, > 10) and by channel group, with block-bootstrap CIs (10 km blocks,
  1000 resamples, seed 0).
- **Criterion (fixed now):** a variant "achieves rate-conditional coverage" if its pooled coverage lies in 90 +- 3 % and
  coverage in every one of the five rate classes lies in 90 +- 5 % (85-95 %). Reported whether or not it is met.

## PH2. Non-conformal comparators (M9)

Around the same GBT forecasts, without a calibration set: (a) Gaussian with a robust scale, yhat +- 1.645 x 1.4826 x MAD
of the out-of-fold training residuals; (b) empirical interval [yhat + q05, yhat + q95] of the out-of-fold training
residuals. Same metrics as PH1. No pass/fail rule; compared with split conformal against the H2 tolerance 90 +- 3 %.

## PH3. Independence null for omission and commission (M6)

Units and labels of analysis B (`data/processed/explore_reporting_units.csv`; 343 units, reported = any usable row,
satellite-eroding = `lab_p75_20`, below floor = `win_p75` < 9.3 m). Reported labels permuted among units within channel
group (Tien main, Hau main, island channels), 10 000 permutations, seed 0. Statistics: omission (share of satellite-eroding
units unreported), commission (share of reported units below the floor) and the commission gap (below-floor share of
reported minus unreported units). Reported: observed value, null median and 95 % range, two-sided permutation p.
**Criterion (fixed now):** "consistent with independence" if the observed value lies inside the null 95 % range.

## PH4. Second rater (M7)

A co-author who did not take part in the earlier reviews repeats, blind and without seeing the first answers:
- the visual check of all 60 units (`python -B src/visual_check.py serve 8781 rater2`; answers in
  `data/processed/visual_check/answers_rater2.csv`; same page, items and instructions as the first rater);
- 20 accuracy clicks: a seeded sample (seed 0) of transect sides the first rater clicked, 8 Tien, 4 wide Hau, 4 narrow Hau,
  4 island channels (`python src/p4_posthoc.py rater2-sample`, then `python -I src/review_server.py rater2_clicks 8766`).
Reported (`python src/p4_posthoc.py agree`): visual check, Cohen's kappa and raw agreement for Q1 "clear loss" vs not and
Q2 "protection yes/partly" vs not, on units both raters could judge; clicks, the RMSE and median absolute difference
between raters on pairs judged on the same imagery capture date, and each rater's RMSE against the Landsat bank. The first
rater's numbers in the paper stay as they are; the second rater's answers are reported next to them, not merged.
No pass/fail rule.
