# mekong-bankline-forecast

Calibrated forecasting of riverbank retreat on the Tien and Hau rivers (Vietnamese Mekong Delta) from 2000–2024 satellite water masks, with an audit of how report-based erosion-hotspot labels bias susceptibility maps.

Plan and timeline: [docs/roadmap.md](docs/roadmap.md)

## Layout

| Path | Contents | In git? |
|---|---|---|
| `docs/` | roadmap, protocol (frozen before forecasting), notes | yes |
| `data/raw/` | Google Earth Engine exports (water masks, composites) | no |
| `data/processed/` | banklines, transects, features | no |
| `data/hotspots/hotspots.csv` | geocoded erosion-hotspot inventory (a contribution of the paper) | yes |
| `src/` | GEE export scripts, bankline extraction, models, conformal | yes |
| `notebooks/` | exploration only; anything reused moves to `src/` | yes |
| `results/` | figures and tables cited by the paper | yes |
| `paper/` | manuscript | yes |

## Setup

```bash
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
earthengine authenticate   # noncommercial Cloud project, Community tier
```

Runs on CPU; heavy raster work happens server-side in Earth Engine.
