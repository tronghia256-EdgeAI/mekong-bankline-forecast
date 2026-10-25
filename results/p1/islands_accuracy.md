# Bank position accuracy vs high-resolution imagery: islands

Source: `data/processed/islands/accuracy_review.csv` (Esri World Imagery Wayback, clicks by hand on the transect line; last answer per item, explore items excluded).
Answered: 12 (clicked 12, cannot see 0, skipped 0). error = ours - clicked, positive = our bank too far landward.

| Group | n | Mean bias (m) | Median abs error (m) | RMSE (m) | P90 abs error (m) |
|---|---|---|---|---|---|
| all | 11 | -8.2 | 9.1 | 13.9 | 23.2 |
| hotspot (abs lrr > 5 m/yr) | 2 | -8.5 | 8.5 | 9.2 | 11.3 |
| other stable banks | 9 | -8.1 | 9.1 | 14.7 | 24.7 |
| imagery Jan-Apr (dry) | 2 | -5.7 | 17.5 | 18.4 | 22.1 |
| imagery May-Dec (wet/transition) | 9 | -8.8 | 8.5 | 12.7 | 15.8 |
| imagery date unknown | 0 | - | - | - | - |
| flagged unstable (not in rows above) | 0 | - | - | - | - |

Verdict: median abs error 9.1 m = 8.2 x the median annual change of stable transect-sides (1.1 m/yr), so a single year of change is below the measurement error on a typical bank.
