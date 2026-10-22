# Bank position accuracy vs high-resolution imagery: mythuan

Source: `data/processed/mythuan/accuracy_review.csv` (Esri World Imagery Wayback, clicks by hand on the transect line; last answer per item, explore items excluded).
Answered: 8 (clicked 8, cannot see 0, skipped 0). error = ours - clicked, positive = our bank too far landward.

| Group | n | Mean bias (m) | Median abs error (m) | RMSE (m) | P90 abs error (m) |
|---|---|---|---|---|---|
| all | 6 | -4.7 | 5.2 | 12.1 | 20.0 |
| hotspot (abs lrr > 5 m/yr) | 2 | -10.0 | 10.2 | 14.2 | 18.2 |
| other stable banks | 4 | -2.0 | 5.2 | 10.8 | 16.3 |
| imagery Jan-Apr (dry) | 6 | -4.7 | 5.2 | 12.1 | 20.0 |
| imagery May-Dec (wet/transition) | 0 | - | - | - | - |
| imagery date unknown | 0 | - | - | - | - |
| flagged unstable (not in rows above) | 2 | -69.9 | 69.9 | 81.4 | 103.3 |

Verdict: median abs error 5.2 m = 3.4 x the median annual change of stable transect-sides (1.5 m/yr), so a single year of change is below the measurement error on a typical bank.
