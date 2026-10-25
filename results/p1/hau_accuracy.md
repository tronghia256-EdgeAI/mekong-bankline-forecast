# Bank position accuracy vs high-resolution imagery: hau

Source: `data/processed/hau/accuracy_review.csv` (Esri World Imagery Wayback, clicks by hand on the transect line; last answer per item, explore items excluded).
Answered: 23 (clicked 23, cannot see 0, skipped 0). error = ours - clicked, positive = our bank too far landward.

| Group | n | Mean bias (m) | Median abs error (m) | RMSE (m) | P90 abs error (m) |
|---|---|---|---|---|---|
| all | 21 | -14.2 | 13.1 | 25.7 | 37.6 |
| hotspot (abs lrr > 5 m/yr) | 6 | -28.6 | 24.8 | 41.6 | 65.8 |
| other stable banks | 15 | -8.4 | 13.1 | 15.1 | 22.0 |
| imagery Jan-Apr (dry) | 10 | -22.2 | 21.4 | 35.2 | 59.2 |
| imagery May-Dec (wet/transition) | 11 | -6.9 | 5.5 | 11.4 | 18.1 |
| imagery date unknown | 0 | - | - | - | - |
| flagged unstable (not in rows above) | 2 | +33.2 | 53.7 | 63.1 | 80.2 |

Verdict: median abs error 13.1 m = 21.4 x the median annual change of stable transect-sides (0.6 m/yr), so a single year of change is below the measurement error on a typical bank.
