# P3 R5: forward forecast of bank retreat 2024 -> 2027 (h = 3) for the atlas

`python src/forecast_2027.py` (~30 s) -> `data/processed/forecast_2027.csv`. Exploratory product for the atlas; it does
not change any confirmatory result and nothing was tuned for it.

## Design

The rolling-origin design of `src/explore_horizon.py` (results/p2/explore_horizon.md section 2) at origin t = 2024:

- Rows, inclusion and features from `forecast.build` (in-scope transect-sides with >= 15 valid years 2000-2024, origin
  with >= 8 valid years; target = change of the 3-yr centred mean position, + = landward). The origin-2024 feature rows
  use positions <= 2024 only; a self-check asserts that they equal `build`'s features on a shared origin.
- GBT with the confirmatory point hyperparameters (learning rate 0.05, 15 leaves, min 100 per leaf, absolute error,
  300 iterations; `explore_horizon.GBT_P`), fitted on all 69 275 rows with target year <= 2023.
- 90% split-conformal half-width from 5-fold spatial-block (10 km) out-of-fold residuals of the training rows with
  target years 2021-2023 (18 133 rows); Mondrian = the same per group. Persistence (forecast 0): half-width from its
  plain residuals on the same rows.
- d_2024 = 3-yr centred mean at 2024 (mean of 2023 and 2024; needs both). 6177 transect-sides have a forecast; 201 of
  them have no d_2024 and are not drawn in the atlas.

## Half-widths (m) of the 90% interval

| group      | calibration rows | GBT | persistence | transect-sides |
|:-----------|-----------------:|----:|------------:|---------------:|
| all (split)|           18 133 | 16.6 |       19.6 |           6177 |
| Tiền main  |            6 564 | 20.4 |       23.1 |           2193 |
| Hậu wide   |            1 658 |  9.0 |        9.3 |            603 |
| Hậu narrow |            4 446 | 12.7 |       13.0 |           1484 |
| island channels |       5 465 | 18.9 |       25.2 |           1897 |

GBT predictions: median -1.8 m (slightly riverward), 5-95% range -9.4 to +4.6 m; largest predicted retreat +72 m
(isl_tien_01, side I). The atlas draws the landward 90% bound as d_2024 + upper limit of the GBT Mondrian interval
along the transect normal; where the upper limit is negative the bound lies riverward of the 2024 bank.

## Coverage these settings achieved in validation

- Rolling origins, h = 3, target years 2019-2024, split conformal with the 3 most recent target years: GBT 91.3%
  [88.5, 93.7], mean width 43.2 m; persistence 92.3% [89.4, 94.6], 51.2 m (results/p2/explore_horizon.md section 2).
- The half-width shrinks over the period because recent residuals are smaller; coverage held per target year
  (re-run of the same design, h = 3 only): GBT half-width 31.2 / 25.8 / 20.2 / 16.8 / 17.1 / 18.5 m for 2019-2024
  with coverage 94.6 / 92.8 / 90.7 / 88.7 / 90.0 / 91.1%; persistence 90.2-94.9%. The 2027 half-width (16.6 m)
  matches the narrowest recent calibrations, so it assumes 2024-2027 is about as quiet as 2021-2023.
- Per group (same re-run, split): Tiền main 89.0%, island channels 89.2%, Hậu narrow 95.1%, Hậu wide 97.3%; this
  over-coverage of the Hậu groups is what Mondrian removes. Confirmatory test (fixed calibration 2016-2018): GBT split
  92.4%, Mondrian 92.7% [90.3, 94.8], persistence split 89.9%, Mondrian 89.7% (results/p2/forecast.md, H2 at h = 3).

## Caveat

The interval half-width is constant within a group by construction (split / Mondrian conformal), and the GBT point
forecast is close to persistence (its MAE is not better than persistence, results/p2/forecast.md H1). The map
therefore shows where each bank may plausibly reach by 2027 at 90% marginal coverage, not a site-specific risk score:
coverage is an average over transect-sides, and individual eroding hotspots can exceed the bound.
