# G1: Google Scholar check (owner, 2026-10-22)

Run by the owner in a browser (Scholar blocks automated access). First two result pages per query.
Novelty statements below are search-scope statements for these queries on this date.

| Query | Relevant hits |
|---|---|
| "conformal" "shoreline change" uncertainty forecast | None: hits are the Lambert Conformal map projection |
| riverbank erosion susceptibility "inventory bias" OR "sampling bias" OR "reporting bias" | No reported-vs-satellite label comparison. Modhiya et al. 2026, *Hybrid AI-Geo-informatics framework for river course change prediction and disaster risk mitigation*, Sci. Rep. (mentions sampling bias generically; confirms a title earlier marked unverified) |
| flood susceptibility "inventory" bias "satellite" "reported" points AUC | Idowu et al. 2026, *National-Scale Flood Susceptibility Mapping of Nigeria ... Satellite-Driven Validation for Data-Sparse ...*, Remote Sens. (to read: does it compare with reported inventories?); Prasad et al. 2025, SAR threshold-based flood inventory (satellite inventory, no comparison) |
| Mekong riverbank erosion forecast uncertainty Landsat | Kumkong et al. 2025, ML estimation of riverbank erosion/deposition, Mekong in Loei (Thailand), GEE 1988-2025, IEEE conf. (no calibrated intervals in snippet) |
| "Tien River" OR "Hau River" bank erosion prediction | Deterministic only: Nga et al. 2025, *The Impact of Sediment Deficiency on Riverbed Evolution in Major Mekong Delta Rivers*, J. Water Manag. Model. (projection to 2030); Le Manh, Tanaka et al., *Prediction of river bank erosion in the Lower Mekong River Delta* (Thuong Phuoc, Sa Dec); Van et al. 2021, empirical formulas, Tien River |
| sạt lở bờ sông Tiền dự báo | Long et al. 2019, GEE bankline monitoring on the Tien/Hau (HCMUE journal; methodological precedent); Điệp et al. 2019, erosion progression Tien/Hau; Phan et al. 2026, sediment decline and channel morphology Tien/Hau (Geodesy journal, deterministic); a Chợ Mới (An Giang) empirical-formula study citing 129 erosion sites (river + canal) - possible extra reported-site source for P1 |
| Owner additions | *Depth-Conditional Uncertainty Calibration for Satellite-Derived Bathymetry via Conformal Prediction* (known); *Beyond isotropic uncertainty in tropical cyclone tracks with adaptive conformal prediction* (ACI in geophysical forecasting - cite for H2) |

Steger et al. 2017 (Landslides 14:1767) full text read: inventory bias is SIMULATED (landslides removed in
forests and selected municipalities), logistic regression with and without bias-describing predictors,
mixed-effects models as the correction. Our H3 differs by using two real, independent label sources
(provincial reports vs satellite retreat) on riverbanks; mixed-effects is a candidate correction.

## "Cited by" scans (owner, 2026-10-22; "search within citing articles" ticked)

| Cited work | riverbank | bank erosion | flood |
|---|---|---|---|
| Steger et al. 2017 (Landslides; 172 citing) | 2 hits, landslide LSM only | 20 hits; "bank erosion" only as a landslide predictor | ~77 hits; flash-flood / landslide susceptibility, no label-source comparison |
| Steger et al. 2021, *Correlation does not imply geomorphic causation ...* (Sci. Total Environ. 776:145935) | landslide / multi-hazard susceptibility | landslide | Villaça et al. 2024, 2025: flash-flood inventory compiled from newspapers (DISASTER database) - reported labels, no satellite comparison |
| Phillips et al. 2009 (Ecol. Appl.) | 15 hits, all ecology | ecology / freshwater biodiversity | - |

Result: within these scans no study compares reported vs satellite-derived labels for riverbank erosion.
To cite: Rüther et al. 2026 (NHESS, *Spatial machine learning modelling reveals that soil indicators and tree
type best explain shallow landslide release*) - biased inventories lead to over-optimistic performance
metrics (motivation for H3, landslide domain); Villaça et al. 2024/2025 - newspaper-based flood inventories.

## Nguyen et al. 2025, full text read 2026-10-22

Nguyen T.G. et al. (2025/2026) *Physical Geography* 47(2): 105-129, doi:10.1080/02723646.2025.2555849 (26 pp.).
- Labels are **pooled from two sources**, not Landsat only as the abstract suggests: 95 erosion points from
  field missions (April and November 2024, handheld GPS), the MARD inventory map of coastal and riverbank
  erosion (http://satlov2.vndss.com/) and provincial DONRE biannual erosion reports; plus 272 points from
  Landsat water-land change 2010/2015/2024 (September images, random-forest water classification). 367 erosion
  + 367 non-erosion points.
- The two sources are not compared, stratified or tested for agreement; no source-wise performance.
- Validation: AUC/RMSE/MAE/R2 on a "validation dataset" whose split is not described (no spatial or temporal
  blocking stated); no forecast in time, no prediction intervals or coverage.
- Delta-wide static susceptibility map (Tien, Hau, Ham Luong); highest in An Giang, Dong Thap, Vinh Long.

Consequence: G1 passes. H3 framing changes: the closest same-region study pools reported and satellite labels
without testing whether they agree, which is the question H3 asks; cite it as such (not as "satellite-only").
New lead for the inventory (P1): the MARD erosion inventory map (satlov2.vndss.com).
