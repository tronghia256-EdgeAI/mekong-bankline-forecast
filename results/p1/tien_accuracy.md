# Bank position accuracy vs high-resolution imagery: tien

Source: `data/processed/tien/accuracy_review.csv` (Esri World Imagery Wayback, clicks by hand on the transect line; last answer per item, explore items excluded).
Answered: 8 (clicked 8, cannot see 0, skipped 0). error = ours - clicked, positive = our bank too far landward.

| Group | n | Mean bias (m) | Median abs error (m) | RMSE (m) | P90 abs error (m) |
|---|---|---|---|---|---|
| all | 8 | -12.3 | 7.2 | 37.4 | 51.6 |
| hotspot (abs lrr > 5 m/yr) | 2 | -9.1 | 9.1 | 10.0 | 12.4 |
| other stable banks | 6 | -13.4 | 6.9 | 42.8 | 65.3 |
| imagery Jan-Apr (dry) | 2 | -3.0 | 3.0 | 3.6 | 4.5 |
| imagery May-Dec (wet/transition) | 6 | -15.4 | 11.3 | 43.1 | 65.3 |
| imagery date unknown | 0 | - | - | - | - |
| flagged unstable (not in rows above) | 0 | - | - | - | - |

Verdict: median abs error 7.2 m = 8.3 x the median annual change of stable transect-sides (0.9 m/yr), so a single year of change is below the measurement error on a typical bank.
