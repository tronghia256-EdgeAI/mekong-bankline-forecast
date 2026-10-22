# Bank position accuracy vs high-resolution imagery: hau

Source: `data/processed/hau/accuracy_review.csv` (Esri World Imagery Wayback, clicks by hand on the transect line; last answer per item, explore items excluded).
Answered: 15 (clicked 15, cannot see 0, skipped 0). error = ours - clicked, positive = our bank too far landward.

| Group | n | Mean bias (m) | Median abs error (m) | RMSE (m) | P90 abs error (m) |
|---|---|---|---|---|---|
| all | 13 | -19.1 | 12.6 | 30.0 | 53.6 |
| hotspot (abs lrr > 5 m/yr) | 4 | -41.3 | 47.6 | 50.5 | 69.1 |
| other stable banks | 9 | -9.2 | 9.0 | 12.7 | 21.8 |
| imagery Jan-Apr (dry) | 6 | -33.9 | 29.9 | 42.7 | 65.8 |
| imagery May-Dec (wet/transition) | 7 | -6.4 | 4.5 | 10.3 | 16.2 |
| imagery date unknown | 0 | - | - | - | - |
| flagged unstable (not in rows above) | 2 | +33.2 | 53.7 | 63.1 | 80.2 |

Verdict: median abs error 12.6 m = 20.5 x the median annual change of stable transect-sides (0.6 m/yr), so a single year of change is below the measurement error on a typical bank.
