# Bank position accuracy vs high-resolution imagery: sadec_caolanh

Source: `data/processed/sadec_caolanh/accuracy_review.csv` (Esri World Imagery Wayback, clicks by hand on the transect line; last answer per item, explore items excluded).
Answered: 50 (clicked 50, cannot see 0, skipped 0). error = ours - clicked, positive = our bank too far landward.

| Group | n | Mean bias (m) | Median abs error (m) | RMSE (m) | P90 abs error (m) |
|---|---|---|---|---|---|
| all | 45 | -24.8 | 20.3 | 36.9 | 50.2 |
| hotspot (abs lrr > 5 m/yr) | 15 | -33.2 | 13.6 | 51.8 | 102.8 |
| other stable banks | 30 | -20.6 | 20.4 | 26.5 | 44.4 |
| imagery Jan-Apr (dry) | 11 | -25.9 | 13.6 | 37.9 | 47.7 |
| imagery May-Dec (wet/transition) | 33 | -24.6 | 20.3 | 37.0 | 50.4 |
| imagery date unknown | 1 | -20.5 | 20.5 | 20.5 | 20.5 |
| flagged unstable (not in rows above) | 5 | -5.0 | 15.3 | 19.7 | 28.5 |

Verdict: median abs error 20.3 m = 21.0 x the median annual change of stable transect-sides (1.0 m/yr), so a single year of change is below the measurement error on a typical bank.
