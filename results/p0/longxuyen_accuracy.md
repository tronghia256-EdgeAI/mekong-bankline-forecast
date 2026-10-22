# Bank position accuracy vs high-resolution imagery: longxuyen

Source: `data/processed/longxuyen/accuracy_review.csv` (Esri World Imagery Wayback, clicks by hand on the transect line; last answer per item, explore items excluded).
Answered: 8 (clicked 8, cannot see 0, skipped 0). error = ours - clicked, positive = our bank too far landward.

| Group | n | Mean bias (m) | Median abs error (m) | RMSE (m) | P90 abs error (m) |
|---|---|---|---|---|---|
| all | 6 | -11.4 | 24.7 | 23.3 | 30.9 |
| hotspot (abs lrr > 5 m/yr) | 3 | +0.2 | 21.1 | 20.9 | 27.1 |
| other stable banks | 3 | -23.1 | 28.3 | 25.6 | 32.2 |
| imagery Jan-Apr (dry) | 0 | - | - | - | - |
| imagery May-Dec (wet/transition) | 6 | -11.4 | 24.7 | 23.3 | 30.9 |
| imagery date unknown | 0 | - | - | - | - |
| flagged unstable (not in rows above) | 2 | -229.3 | 229.3 | 320.5 | 408.4 |

Verdict: median abs error 24.7 m = 34.5 x the median annual change of stable transect-sides (0.7 m/yr), so a single year of change is below the measurement error on a typical bank.
