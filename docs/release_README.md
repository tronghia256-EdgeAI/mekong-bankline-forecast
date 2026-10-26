# Annual dry-season banklines (2000–2024) and a public erosion inventory, Tiền and Hậu rivers, Vietnamese Mekong Delta

Data release for the paper "Coverage-verified forecasts of riverbank retreat and the limits of public erosion reports as
hazard labels: Tien and Hau rivers, Vietnamese Mekong Delta" (in preparation). Code: the companion repository (MIT licence),
archived at the tagged commit named in the Zenodo record.

## Coverage

- Tiền River from the Cambodian border to the Mỹ Thuận bridge (~127 km) and Hậu River from the border to the Cần Thơ bridge
  (~146 km), both banks, plus all 11 river islands of 1–150 km² measured all round (island bank I and opposite bank O of the
  channel around each island).
- Annual dry-season (1 January – 1 May median) composites of Landsat 5/7/8/9 Collection 2 Level 2, 2000–2024 (no composite
  in 2012; composites with > 2% nodata dropped). Transects every 100 m perpendicular to coarse centerlines.

## Files (`data/`)

| file | content |
|---|---|
| `banks_annual.csv` | one row per transect-side and year: `river`, `channel` (tien, hau, isl_*), `transect`, `side` (L/R looking downstream; I/O on island channels), `year`, `dist_m` (bank distance from the transect origin along the transect), `spike` (reverting jump > 150 m, excluded from trends), `lon`, `lat` (bank point, WGS84), `commune`/`district`/`province` (pre-2025 units, OpenStreetMap/Kontur), `in_scope` (new An Giang and Đồng Tháp), `unit_2km`, `in_units` (False = island-ring bank that duplicates a main-channel bank or a neighbouring island's ring bank, or has no median position; not used in the analyses) |
| `banklines.geojson` | the same banks as polylines, one MultiLineString per channel, side and year (broken where points are > 300 m apart) |
| `trends.csv` | per transect-side: Theil–Sen rate (`rate_m_per_yr`, positive = retreat away from the channel), robust residual scale, number of years, largest year-to-year jump, spikes, `kind` (linear / step / nonlinear), transect origin and direction |
| `units_2km.csv` | 2 km bank units: satellite window retreat (mean position 2022–24 minus 2013–15; p75 etc.), satellite erosion labels (primary `lab_p75_20`), physical and exposure covariates |
| `inventory.csv` | reported erosion rows 2015–2024 from public provincial and news sources and Open Development Vietnam points: commune, hamlet/landmark, event year, source type, URL and date, short quote, owner review verdict, matched 2 km units, `use_in_analysis` |
| `unreported_reaches.csv` | 2 km units with satellite-measured retreat >= 20 m and no reported row, with a blind visual check on Esri World Imagery Wayback (loss visible, bank protection visible, imagery dates) |
| `accuracy_clicks.csv` | hand-clicked banks on Esri World Imagery Wayback vs the Landsat bank of the same year |

## Accuracy

Against hand clicks: Tiền RMSE 33 m (n = 55), Hậu wide channel 19 m (12), Hậu narrow reach above Châu Đốc 30 m (13), island
channels 15 m (9); typical bias −10 to −20 m (Landsat bank riverward). Repeatability of two independent same-year composites
3.1 m per composite; no sensor bias between Landsat 5/7/8/9 (≤ 1 m). Eroded area at Bình Hàng Trung matches the SIWRR 2022
survey (106.3 vs 106.0 ha). Known error types: multi-edge banks (vegetated strip or bar in front of ponds), transient objects,
sharp bends and canal mouths in the narrow reach, and edge switches of several hundred metres that the spike filter does not
remove.

## Licences

- Bank positions, trends, unit labels and covariates derived from Landsat (USGS, public domain): **CC BY 4.0**.
  Covariates also use GHSL (CC BY 4.0), WorldPop (CC BY 4.0), VIIRS (public domain) and OpenStreetMap (ODbL).
- Commune names and assignments come from OpenStreetMap/Kontur Boundaries (**ODbL**, "© OpenStreetMap contributors");
  the inventory includes Open Development Vietnam points (**CC BY-SA 4.0**). The inventory and every column derived from
  communes are therefore distributed under share-alike terms (ODbL for the commune data, CC BY-SA 4.0 for the inventory).
- Esri World Imagery Wayback was used for visual checks only; no imagery is redistributed.

## Citation

Please cite the paper (reference added on publication) and this record.
