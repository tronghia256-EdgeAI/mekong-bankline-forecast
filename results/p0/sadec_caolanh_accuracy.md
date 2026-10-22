# Bank position accuracy vs high-resolution imagery: sadec_caolanh

Source: `data/processed/sadec_caolanh/accuracy_review.csv` (Esri World Imagery Wayback, clicks by hand on the transect line; last answer per item, explore items excluded).
Answered: 45 (clicked 45, cannot see 0, skipped 0). error = ours - clicked, positive = our bank too far landward.

| Group | n | Mean bias (m) | Median abs error (m) | RMSE (m) | P90 abs error (m) |
|---|---|---|---|---|---|
| all | 45 | -26.6 | 19.3 | 44.6 | 52.8 |
| hotspot (abs lrr > 5 m/yr) | 15 | -26.9 | 12.2 | 44.4 | 72.0 |
| other stable banks | 30 | -26.4 | 19.8 | 44.8 | 52.1 |
| imagery Jan-Apr (dry) | 11 | -13.1 | 12.2 | 19.5 | 27.5 |
| imagery May-Dec (wet/transition) | 33 | -31.3 | 19.7 | 50.8 | 92.0 |
| imagery date unknown | 1 | -20.5 | 20.5 | 20.5 | 20.5 |

Verdict: median abs error 19.3 m = 19.1 x the median annual change of stable transect-sides (1.0 m/yr), so a single year of change is below the measurement error on a typical bank.
