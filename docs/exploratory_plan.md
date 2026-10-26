# Exploratory analyses after P2 (planned 2026-10-26)

Planned after the confirmatory P2 results (H1 not supported, H2 supported, H3 not supported; `docs/protocol.md`,
tag `protocol-v1`, deviations 1-4). These analyses are EXPLORATORY: they were chosen after seeing the P2 results and
the gap scan (`reports/gap_scan_2026-10-26.md`), they do not change any confirmatory verdict, and the paper labels them
as exploratory. Uncertainty is reported (10 km block bootstrap) but no p-value is used as a confirmatory test.

## A. Forecast horizon and sampling interval (beside H1)

Question: with 30 m Landsat banks, how far ahead must a forecast reach before bank change exceeds measurement noise,
and how many images per decade does a bank-retreat forecast need?
- Detectability by horizon h = 1-10 yr: share of transect-sides whose true change (3-yr centred means) exceeds the
  noise floor of a difference, by channel group.
- Forecast skill by horizon (persistence, Theil-Sen extrapolation, gradient boosting) with rolling forecast origins
  (training targets always before the evaluated target years), and split-conformal coverage and width by horizon.
- Sampling: thin the annual series to every 2nd, 3rd and 5th year and to 4-9 dates (typical DSAS studies); compare the
  estimated retreat rates and the forecast errors with the full annual series.

## B. What official reporting captures (beside H3)

Question: how much measured bank retreat is never reported, how much reported bank shows no measurable retreat, and
do warnings precede measured retreat?
- Omission: satellite-eroding 2 km units (primary label) without any reported row; commission: reported units whose
  window retreat is below the noise floor of a 3-yr mean difference. By channel group, source type (warned-reach list,
  news event, emergency decision) and exposure tercile.
- Timing: for dated reported rows, measured unit-year retreat events (`sat_events_2km.csv`, years 2012 and 2024
  excluded as noisier) before, in and after the reported year; relative frequency of events in units warned vs not
  warned in the following 1-3 years.
