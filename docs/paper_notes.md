# Paper notes: figures, key numbers and decisions for the manuscript

Working notes for drafting (NHESS). Updated as results come in; every number here has a file behind it.
Status date: 2026-10-25. Main-channel figures and accuracy numbers are from 22/10; river islands (cù lao) are
measured all round by rule since 25/10 (the hand-picked branches of 22-24/10 were replaced).

## Figures (manuscript set, `python src/figures.py`)

All in `figures/` as PNG 300 dpi + SVG (text as text), sized to Copernicus columns (~8.3 / ~17 cm), text >= 7 pt,
CVD-safe categorical slots (blue, orange, aqua), diverging blue (accretion) - grey - red (erosion).

| File | Content | Draft caption | Inputs |
|---|---|---|---|
| fig01_study_area | Map of the analysed Tiền (127 km) and Hậu (146 km) reaches, three P0 test reaches, towns, pre-2025 provinces, inset | Study area: the Tiền and Hậu rivers from the Cambodian border to the Mỹ Thuận and Cần Thơ bridges. Boxes: test reaches used for accuracy checks (1 Sa Đéc–Cao Lãnh, 2 Long Xuyên, 3 Mỹ Thuận). Background: JRC Global Surface Water occurrence (Pekel et al., 2016). Province boundaries before the 2025 merger (FAO GAUL 2015). | JRC GSW v1.4, LSIB 2017, GAUL 2015, data/tiles.json |
| fig02_method_example | (a) Banks 2000 vs 2024 on the 2024 MNDWI composite at Bình Hàng Trung with transects; (b) annual bank series at T280L with Theil–Sen fit | Method illustration at Bình Hàng Trung (left bank of the Tiền, Cao Lãnh). (a) Dry-season banks of 2000 and 2024 on the 2024 MNDWI composite; transects every 100 m (every fifth drawn). (b) Bank retreat on transect T280 since 2000 with the Theil–Sen trend (18.5 m/yr, 95% CI 16.6–19.6); retreat slows after 2019. | data/processed/sadec_caolanh |
| fig03_bank_change | (a) Map of linear bank-change rates on both rivers; (b, c) along-river profiles, left/right banks | Bank change 2000–2024 from annual Landsat dry-season banks. (a) Theil–Sen rate per bank point (+ erosion); grey: step or non-linear series. (b, c) Rates along the Tiền and Hậu by distance from the border. | data/processed/{tien,hau}, units.csv |
| fig04_validation | (a) Landsat minus hand-clicked bank by river / channel type; (b) eroded area vs SIWRR (Phong et al., 2022) | Accuracy. (a) Difference between the Landsat bank and the bank clicked on Esri World Imagery Wayback (negative = Landsat bank riverward); bars = median. (b) Left-bank eroded area at Bình Hàng Trung per period, this study vs Phong et al. (2022). | accuracy_review.csv per reach, tile_check.project |

Supplement candidates: `results/p0/sadec_caolanh_sensor_check.png` (sensor pairs, repeatability, window),
`results/p1/tiles.png` (tiles and coarse centerlines), per-tile quick-looks in `results/p1/tiles/` (not committed).
Planned: H1/H2 coverage figures (P2), H3 label-source figure (P2), inventory map (P1/P3).

## Key numbers

Measurement (P0, `results/p0/sadec_caolanh_sensor_check.md`):
- Sensor bias (pooled, block-bootstrap 95% CI): L7–L8 −0.2 m [−0.6, 0.2]; L8–L9 −0.2 m [−1.7, 1.5]; L5–L7 −1.0 m [−1.8, −0.3] → no harmonisation needed.
- Repeatability (two independent same-year composites): robust SD 4.3 m for the difference → 3.1 m per composite. Window Jan–Mar vs Feb–Apr: +1.0 m. Measured noise used: 3.6 m.
- SIWRR check (Bình Hàng Trung left bank, T255–315): −15.4, −45.7, −14.6, −30.6 ha vs −30.0, −41.5, −11.5, −23.0; total −106.3 vs −106.0 ha (`results/p0/sadec_caolanh_siwrr_check.md`).
- Detectability (sadec, linear transects, change > 2 × 3.6 m): ~8–9% at 1 yr, 25% at 3 yr, 40% at 5 yr → forecast horizon 3–5 yr.

Coverage (P1, main-channel checks of 22/10; `src/stitch.py`, `results/p1/tile_check.md`):
- Tiền 1,141 transects (in Vietnam) over ~127 km, 85% linear; Hậu 1,360 over ~146 km, 95% linear (incl. narrow reach above Châu Đốc).
- Stitched vs P0 reaches: median |diff| 0.9–5.7 m, |rate diff| 0.05–0.23 m/yr. Narrow vs normal mode on overlap: median diff 0.0 m, |diff| 3.7 m, 90% ≤ 15 m.
- River islands (25/10): 11 islands of 1–150 km² found by rule (holes of the connected river system in JRC ≥ 50%),
  each measured all round from a medial channel ring (island bank I, opposite bank O); ring banks within 150 m of a
  main-channel bank dropped. 2,472 ring transect-sides with a trend, 82% linear. In scope (new An Giang + Đồng
  Tháp): 6,635 bank points, 399 units of 2 km, 178 of 5 km, 125 communes (`data/processed/units.csv`).

Accuracy vs hand clicks (Esri Wayback, final stitched product; `figures/fig04_validation`):
- Tiền n = 55, RMSE 33 m; Hậu wide n = 12, RMSE 19 m; Hậu narrow n = 13, RMSE 30 m; river-island channels n = 11, RMSE 14 m, median |err| 9 m (`results/p1/islands_accuracy.md`; one of 12 clicks fell on a channel narrower than the canal filter and is now a non-detection). Typical bias −10 to −20 m (Landsat bank riverward; wet-season imagery). Stable single-edge banks ~10–15 m.
- Known outlier types: multi-edge banks (vegetated strip/bar in front of ponds, ~100 m), transient riverward objects (T417L 2021–22), sharp bends and canal mouths (narrow reach).

Reported inventory (P1 draft, 25/10, `data/hotspots/inventory_draft.csv`): 187 rows = 158 G3 + 23 new
(quote-verified 23/23) + 6 ODV rows; 144 on measured banks, 4 on unmeasured banks, 3 unmatched, 36 out of scope.
Owner review pending (`src/inventory_server.py`, 151 rows).

## Method decisions (with dates)

- Water index: MNDWI, Landsat 5/7/8/9 C2 L2, dry season Jan 1–May 1 median, QA bits 1,3,4, 30 m UTM 48N; MNDWI clipped to [−1, 1]; Otsu per composite; composites with > 2% nodata dropped.
- Bank = "from the mainland, the first water" (owner's definition, 22/10): walking out from the open river; islands > 1 km² count as mainland; canals < ~90 m do not cut the mainland; ponds filled; sub-pixel MNDWI crossing.
- A bank found at the transect origin (centerline or island ring lying on the bank; channel narrower than the canal filter) is a non-detection (25/10; removed 1,448 sporadic rows in the narrow Hậu and 5% of island rows; P0 and Tiền outputs unchanged, Hậu 96% linear).
- Trends: Theil–Sen per transect-side; reverting jumps > 150 m removed as spikes; kinds linear / step / non-linear (robust residual scale > 30 m).
- Full rivers (P1): coarse JRC least-cost centerlines, 15 overlapping 30 km tiles, other river masked per tile (Vàm Nao), stitched by chainage; L/R looking downstream.
- Narrow mode (Hậu above Châu Đốc, width ~200 m; owner chose 22/10): canal filter ~90 m, no open-river core, smoothing 15 px, 1 km corridor.
- Border: bank points outside Vietnamese communes dropped (Hậu is a border river at An Phú).
- Cù lao convention (owner chose B, 22/10; implemented by rule 25/10): every river island of 1–150 km² is measured all round (island bank and the opposite bank of each channel around it), so the unit set does not depend on where reports exist; duplicates within 150 m of main-channel banks dropped.
- H3 at reach level, 2 km units (5 km sensitivity); inventory scope = new An Giang + Đồng Tháp (old AG, DT, Tiền Giang).

## Data sources and licences (for Data availability)

Landsat C2 L2 (USGS, via Google Earth Engine); JRC Global Surface Water v1.4 (Pekel et al., 2016); LSIB 2017 (US DoS);
FAO GAUL 2015 (figure only); Kontur Boundaries Vietnam 2023-06-28 from OpenStreetMap (ODbL – credit "© OpenStreetMap
contributors"; share-alike if commune assignments are redistributed); Open Development Vietnam "Landslide points over
whole country in Vietnam" (CC-BY-SA); Esri World Imagery Wayback (visual checks only); news and provincial sources
listed per row in the inventory.

## Limitations to state

30 m pixels vs sub-pixel collapses; multi-edge banks; transient objects; narrow reach accuracy (RMSE 30 m vs width
~200 m); wet-season reference imagery; reported labels mostly 2018–2024 and commune-level (reach-level H3).

## Literature anchors

Nguyen T.G. et al. 2025 (Physical Geography): pooled 95 reported/field + 272 Landsat points without comparing sources,
no spatial/temporal validation, no intervals. Steger et al. 2017, 2021 (inventory bias in landslide susceptibility);
Rüther et al. 2026 (NHESS, biased inventories inflate metrics); Villaça et al. 2024/2025 (newspaper inventories);
Langhorst & Pavelsky 2023 (global bank migration). Novelty statements are search-scope statements
(`results/p0/g1_scholar_check.md`).
