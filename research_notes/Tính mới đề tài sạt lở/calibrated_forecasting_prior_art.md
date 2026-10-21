# Prior art: probabilistic / uncertainty-calibrated forecasting of riverbank retreat, channel migration and shoreline change, with a focus on conformal prediction (adversarial novelty check, as of 2026-10-21)

Claim under test: "first application of conformal prediction (split / CQR, Mondrian per river reach, possibly adaptive conformal under temporal shift) to riverbank-retreat forecasts 1–3 years ahead, with coverage evaluated per reach and under distribution shift (sand mining, dams), benchmarked against EPR/LRR; Tien and Hau rivers, Landsat 2000–2024, transects every 100 m."

Verification legend used below:
- [V-fetched] = page fetched in this session and title/authors confirmed from the page itself.
- [V-search] = title and URL/DOI matched in search-engine results, but the page was not fetched (paywall, 403 or redirect). Treat details as abstract-level.
- [UNVERIFIED] = could not confirm title against the URL. Do not cite without checking.

Search scope (applies to every "not found" statement below). Engine: WebSearch (general web plus scholarly indexes it surfaces: arXiv, Copernicus/ESurf/HESS/EGU, MDPI, ScienceDirect, Wiley/AGU, Nature, T&F, SSRN, ResearchGate, NSF-PAR, USGS pubs), run 2026-10-21. I had no direct Google Scholar, Scopus or Web of Science access. Exact queries:
1. `conformal prediction shoreline change forecasting`
2. `conformal prediction riverbank erosion channel migration uncertainty`
3. `"conformal" coastal erosion OR "shoreline" prediction intervals coverage machine learning 2025`
4. `"conformal prediction" river bank erosion forecasting` (phrased like a competitor title)
5. `calibrated uncertainty shoreline forecasts distribution-free prediction intervals coastline` (phrased like a competitor title)
6. `conformal prediction remote sensing geoscience uncertainty landslide OR erosion OR geomorphology 2025 2026`
7. `"conformal prediction" coastal OR "sea level" OR "wave" OR "beach" geophysical uncertainty arXiv`
8. `conformal prediction streamflow hydrology prediction intervals LSTM`
9. `conformalized quantile regression flood OR streamflow OR "water level" forecasting coverage hydrology 2024 2025`
10. `conformal prediction hydrology Water Resources Research OR HESS uncertainty quantification deep learning rainfall-runoff`
11. `conformal prediction hydrological predictions temporal spatial information uncertainty neuralhydrology paper`
12. `uncertainty quantification earth observation conformal prediction Singh Moncrieff Scientific Reports 2024`
13. `GeoConformal prediction Lou Luo Meng Annals of the American Association of Geographers`
14. `Geomorphic risk maps for river migration using probabilistic modeling Earth Surface Dynamics 2024`
15. `uncertainty-aware riverbank erosion prediction Bayesian OR "Gaussian process" OR "quantile regression" bankline migration forecast`
16. `Jamuna Brahmaputra bankline prediction machine learning uncertainty forecast`
17. `CEGIS Jamuna Ganges Padma erosion prediction annual probabilistic method validation`
18. `CEGIS bank erosion prediction Jamuna method "probability" empirical predicted bankline accuracy paper`
19. `Mekong riverbank erosion prediction machine learning Vietnam bankline forecast`
20. `Mekong Cambodia Vietnam riverbank erosion rate forecast Landsat transects future bankline 2030 prediction`
21. `riverbank erosion time series forecasting LSTM transect Tien Hau river Vietnam deep learning`
22. `deep learning forecast river planform change satellite images Jamuna ConvLSTM erosion prediction`
23. `"Deep learning for planform predictions of braided rivers" Magherini Jamuna uncertainty`
24. `Hybrid AI-Geo-informatics framework for river course change prediction and disaster risk mitigation Scientific Reports 2026`
25. `ShoreShop 2.0 blind shoreline model competition Mao 2025 uncertainty`
26. `Vitousek CoSMoS-COAST ensemble Kalman filter shoreline projections uncertainty 2023`
27. `Vitousek 2024 "Scalable, data-assimilated models predict large-scale shoreline response" uncertainty hindcast coverage`
28. `probabilistic shoreline forecast prediction interval coverage calibration evaluation CRPS`

Not searched (gaps): Chinese-language (CNKI) and Vietnamese-language journals (e.g., VN Journal of Science and Technology, Tạp chí Khoa học Thủy lợi), Scopus/WoS full-text, AGU Fall Meeting 2025 abstracts by keyword, the Yellow River and Indus literature beyond one Yellow River hit, and the Amazon beyond the Ucayali paper.

---

## Q1. Has conformal prediction (any variant) been applied to shoreline change, coastal erosion, riverbank erosion, channel migration or other geomorphic change forecasting? Are there hydrology or remote-sensing uses that could be read as the same contribution?

### Takeaway
None of the 28 queries above turned up a paper, preprint or abstract that applies conformal prediction (split, CQR, jackknife+, ACI, Mondrian, spatial/GeoConformal) to shoreline, coastal-erosion, riverbank-erosion or channel-migration forecasting. Conformal prediction is established in neighbouring areas, though. Streamflow work has evaluated coverage per basin and under temporal shift (Auer et al., HESS 2024). Earth observation has generic conformal tooling (Singh et al., Sci Rep 2024), and geography has spatially weighted conformal prediction (GeoCP, AAAG 2025). So "first conformal for bank retreat" is defensible only as an application-domain first. Calling the method new is not.

### Cited Findings
**Geomorphology and coastal: no conformal application found (scope as listed above).**
- No study combining conformal prediction with shoreline change came up. The closest results were general time-series conformal methods and a non-conformal probabilistic shoreline paper (queries 1, 3, 5, 7). The search engine's own summaries said so explicitly, e.g. "didn't turn up any study that applies conformal prediction to shoreline change" — [WebSearch results, query 1; see Adeli et al. below](https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2025.1562504/full)
- The closest geophysical conformal uses found were (a) block-based conformal prediction for bathymetry super-resolution, whose authors say conformal methods "have not been applied for super-resolution tasks, particularly on EO datasets" [V-search], and (b) conformal UQ in data assimilation on an idealised 1-D shallow-water model, submitted to QJRMS [V-search]. Neither is a morphological-change forecast — [arXiv 2504.14372](https://arxiv.org/html/2504.14372); [arXiv 2606.27001](https://arxiv.org/abs/2606.27001)

**Hydrology: the nearest methodological precedent for "coverage per unit and under shift".**
- Auer, Gauch, Kratzert, Nearing, Hochreiter, Klotz (2024), "A data-centric perspective on the information needed for hydrological uncertainty predictions", *HESS* 28, 4099–4126, DOI 10.5194/hess-28-4099-2024 [V-fetched]. Methods: HopCPT (Hopfield-network conformal for time series), a global variant HopCPT-G, and a conformalised Bluecat'. Data: CAMELS, 531 US basins, train/calibration/test split by time, test period about 9 years. Metrics: ΔCoverage (target minus empirical), PI width and Winkler score, with per-basin coverage shown as CDFs. They test **distribution shift** by comparing offline and online calibration memory with update intervals from one week to two years. Under-coverage concentrates in the 10–20 % of basins with the lowest coverage, which the authors attribute to runoff shifts not visible in the inputs. Peak flows and ungauged basins (11 folds) are also tested. This is structurally very close to "coverage per reach + under temporal shift", but for streamflow, not geomorphology — [HESS](https://hess.copernicus.org/articles/28/4099/2024/)
- HopCPT (Auer et al., NeurIPS 2023; arXiv 2303.12783) uses streamflow with an LSTM base model as a benchmark. The authors report approximately preserved coverage in non-exchangeable time series [V-search] — [arXiv 2303.12783](https://arxiv.org/pdf/2303.12783)
- An SSRN preprint (Zhang, Han, Zhai) on deep-learning streamflow finds that global CQR restores marginal coverage near 0.90, but 1-year high-flow coverage stays at 0.841, rising only to 0.867 with stratified (Mondrian-like) calibration. Its conclusion is to report conditional coverage, not pooled coverage. This is a preprint and peer review is unconfirmed [V-search] — [SSRN 7506823](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7506823)
- A physics-guided runoff paper combines Weighted Conformal Inference with a mixture density network to handle distribution shift in runoff (venue not confirmed from the snippet) [UNVERIFIED venue] — [ResearchGate](https://www.researchgate.net/publication/355295105_Physics-guided_deep_learning_for_rainfall-runoff_modeling_by_considering_extreme_events_and_monotonic_relationships)
- CPTC (NeurIPS 2025, arXiv 2509.02844): online conformal combined with a state-transition model for time series **with change points**. It claims asymptotic coverage and is directly relevant to the "sand mining / dam regime shift" angle. Generic method, not tested on geomorphic data [V-search] — [arXiv 2509.02844](https://arxiv.org/abs/2509.02844)

**Remote sensing and geography: generic conformal frameworks that a reviewer could cite against "methodological novelty".**
- Singh, Moncrieff, Venter, Cawse-Nicholson, Slingsby, Robinson (2024), "Uncertainty quantification for probabilistic machine learning in earth observation using conformal prediction", *Scientific Reports*, DOI 10.1038/s41598-024-65954-w. Conformal regression and classification modules native to Google Earth Engine. Their review found only 22.5 % of EO datasets carried any uncertainty information [V-search] — [PMC11246475](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11246475/); [arXiv 2401.06421](https://arxiv.org/abs/2401.06421)
- Lou, Luo, Meng (2025), "GeoConformal prediction: a model-agnostic framework of measuring the uncertainty of spatial prediction", *Annals of the AAG* 115(8), 1971–1998, DOI 10.1080/24694452.2025.2516091. Spatially weighted (geographically local) conformal prediction, released as the Python package `geoconformal`. The preprint reports about 93.67 % coverage on a housing-price XGBoost task versus at most 68.33 % for bootstrap. Its uncertainty tracks kriging variance in interpolation tests. The tasks are spatial **interpolation/regression**, not temporal forecasting of geomorphic change [V-search] — [MIT DSpace](https://dspace.mit.edu/handle/1721.1/163369); [arXiv 2412.08661](https://arxiv.org/abs/2412.08661v2); [RePEc](https://ideas.repec.org/a/taf/raagxx/v115y2025i8p1971-1998.html)

### Inferences
- The application gap (conformal → bankline/shoreline change) appears real within this search scope. A reviewer will still see split conformal, CQR, Mondrian and ACI as off-the-shelf. Novelty therefore has to rest on (i) the domain, (ii) the evaluation design (per-reach conditional coverage, coverage under documented anthropogenic shift), and (iii) what the coverage diagnostics reveal about the physics (e.g., which reaches lose coverage after sand-mining intensification).
- Auer et al. (2024) is the template a hydrology reviewer will compare against: per-unit coverage CDFs, plus online vs offline calibration under shift. Cite it and position against it.
- GeoCP (spatially weighted conformal) is an obvious baseline or alternative to Mondrian-per-reach, and reviewers may ask why it wasn't used. Comparing Mondrian-per-reach against GeoCP-style localisation would strengthen the paper.
- The SSRN result (pooled coverage hiding conditional under-coverage; stratification only partly fixing it) is a direct analogue of the expected finding "marginal coverage OK, but hotspot reaches under-covered".

### Gaps
- No access to Google Scholar, Scopus or WoS full-text search. A paper titled with neither "conformal" nor "shoreline" in indexed text (e.g., "distribution-free intervals for coastal retreat") could be missed. Recommend running Scholar queries: `"conformal" "shoreline"`, `"conformal" "bank erosion"`, `"conformal" "channel migration"`, `"jackknife+" shoreline`, `"adaptive conformal" erosion`.
- Chinese-language (CNKI) literature on Yellow River / Yangtze bank collapse was not searched. Conformal prediction is increasingly used in Chinese engineering journals.
- The WSU master's thesis "Uncertainty Quantification for Streamflow Forecasting via..." (2026) surfaced but was not inspected — [WSU](https://rex.libraries.wsu.edu/esploro/outputs/graduate/Uncertainty-Quantification-for-Streamflow-Forecasting-via/99901392006301842) [UNVERIFIED content]

---

## Q2. Which ML/statistical forecasts of riverbank/bankline position exist for large rivers, what UQ do they use, and does any report calibration/coverage?

### Takeaway
Bankline forecasting on large rivers is dominated by (a) DSAS EPR/LRR extrapolation and CA-Markov projections with no calibrated intervals, (b) susceptibility classification (AUC, not a position forecast), (c) the CEGIS empirical-probabilistic one-year-ahead forecast in Bangladesh (probability bands, validation reported only informally), and (d) one Bayesian migration framework (Noh et al. 2024, Ucayali). That last one gives pixel erosion probabilities scored by RMSD, with no interval-coverage or reliability analysis. None of the bankline works found report empirical coverage of prediction intervals. For the Vietnamese Mekong, everything found was susceptibility mapping or historical rates. No calibrated bankline forecast turned up.

### Cited Findings
**Known prior art: what exactly was done.**
- **Noh, Wani, Dunne, Lamb (2024)**, "Geomorphic risk maps for river migration using probabilistic modeling – a framework", *Earth Surface Dynamics* 12, 691–708, DOI 10.5194/esurf-12-691-2024 [V-fetched]:
  - River and data: Ucayali River, Peru (single-thread meandering, about 20 km reach). Centerlines are from Schwenk et al. (2017), Landsat 1985–2015, with 1985→1995 used for inference.
  - Model: Howard–Knutson curvature-based migration model, plus additive smooth random functions (truncated Fourier series) for structural error.
  - Inference: Bayesian with MCMC (emcee). Forward Monte Carlo produces pixel-level erosion-probability "risk maps" at horizons of **5–30 years**.
  - Validation: RMSD between assigned probability and observed 0/1 erosion, over all pixels and over eroded pixels only. The probabilistic forecast beats a deterministic run on both. Pixels at p ≥ 0.75 are classed "certain" and 0.25–0.75 "uncertain".
  - What it lacks: **no interval coverage, no reliability diagram, no Brier/ROC, no conformal**. It models centerlines only (no width/banks), and cutoffs are excluded.
  - Closeness to the claim: same goal (probabilistic erosion hazard), different paradigm (Bayesian physics-based, decadal horizon, single meandering reach, uncalibrated in the frequentist sense).
  — [ESurf](https://esurf.copernicus.org/articles/12/691/2024/)
- **CEGIS (Bangladesh) annual erosion prediction**:
  - Forecasts since 2004 for the Jamuna, Padma and Ganges, one year ahead, from dry-season satellite imagery — [Daily Star](https://campaign.thedailystar.net/river-erosion/)
  - Method: EGIS/CEGIS empirical relationships for channel-abandonment probability, bifurcation migration and annual outer-bank erosion rates, which depend on bar presence and bend radius. Primary source: EGIS (2002) Technical Note 29, "Developing and updating empirical methods for predicting morphological changes of the Jamuna River", not accessed — [Brahmaputra-Jamuna chapter, ResearchGate](https://www.researchgate.net/publication/279417946_The_Brahmaputra-Jamuna_River_Bangladesh) [V-search]
  - Output: probability-level vulnerability lines at 30 %, 50 % and 70 % (secondary source).
  - Accuracy: reported only by CEGIS staff in news media. Erosion-rate predictions match about 70 % and vulnerable locations about 80 %. The 2020 forecast was 2,800 ha against 1,965 ha observed.
  - A secondary review cites Nardi et al. (2013) on its "relative degree of inaccuracy".
  - No peer-reviewed coverage/calibration study of the CEGIS probability levels was found (queries 17–18).
  — [Academia.edu: Risk informed early warning system…](https://www.academia.edu/40346168/Risk_informed_early_warning_system_and_non_migration_pattern_riverbank_erosion_areas) [V-search, secondary]; [Prothom Alo](https://en.prothomalo.com/environment/climate-change/expert-study-predicts-river-erosion-in-northwest-seeks-precaution)

**Other big-river bankline forecasts (all without coverage evaluation, as far as abstracts show).**
- Brahmaputra (India): CA-Markov + DSAS projection of banklines, validated by counting transects within a 10 m uncertainty band. This is deterministic, though the band count is the nearest thing to a "coverage" check found [V-search] — [ScienceDirect S1674987123000245](https://www.sciencedirect.com/science/article/pii/S1674987123000245)
- Padma: DSAS-based bankline forecast plus LULC, "validated with a kappa accuracy of 85 %" (classification accuracy, not interval coverage) [V-search] — [Ecological Indicators, S1470160X23012463](https://www.sciencedirect.com/science/article/pii/S1470160X23012463)
- Jamuna: ANN forecasting of course decades ahead (Sarker et al., 2024), cited in arXiv 2510.17198 with no details. Primary source not located [UNVERIFIED] — [arXiv 2510.17198](https://arxiv.org/html/2510.17198v1)
- Jamuna: multivariate regression of bankline shifting [V-search, not inspected] — [JSoftCivil](https://www.jsoftcivil.com/article_147520.html)
- Brahmaputra stochastic bank-erosion modelling (uncertainty in stage hydrograph, erodibility, stratification; compared against observed distributions), and BSTEM with PDFs of bank properties (EGU 2020 abstract). These are physically based Monte Carlo, not statistical forecasts with calibrated intervals [V-search] — [ADS EGU2020-19427](https://ui.adsabs.harvard.edu/abs/2020EGUGA..2219427L/abstract)
- Yellow River tail channel: "Navigating uncertainty: Stochastic simulation prediction of the Yellow River tail channel (fluvial reach)…", *Geomorphology* 2024. Stochastic simulation; details not accessible (403) [V-search title only] — [ScienceDirect S0169555X24005361](https://www.sciencedirect.com/science/article/abs/pii/S0169555X24005361)
- Basin-scale channel migration by landscape-evolution simulation, using Bayesian treatment of parameter uncertainty, *HESS* 30, 1563, 2026 [V-search title only] — [HESS](https://hess.copernicus.org/articles/30/1563/2026/)

**Vietnamese / Cambodian Mekong.**
- "Prediction of riverbank erosion susceptibility areas of the Vietnam Mekong Delta using machine learning and remote sensing…", *Physical Geography* (2025, vol. 47 no. 2), DOI 10.1080/02723646.2025.2555849.
  - Method: GB/AdaBoost/RF/CatBoost on Landsat-detected erosion points with 16 factors; GB best at AUC 0.85.
  - Location: hotspots along the Tien and Hau main branches (An Giang, Dong Thap).
  - This is **susceptibility classification**, not a position/retreat forecast, and has no interval UQ [V-search].
  — [T&F](https://www.tandfonline.com/doi/full/10.1080/02723646.2025.2555849)
- "Assessing River Corridor Stability and Erosion Dynamics in the Mekong Delta: Implications for Sustainable Management", *Earth* (MDPI) 6(2):34, 2025, DOI 10.3390/earth6020034.
  - Data and methods: Landsat 2000–2023, field surveys and numerical simulation.
  - Results: hotspots up to about 40 m/yr.
  - Full text returned 403, so I could not confirm whether it contains a forward forecast or UQ. **Check this paper first: its study period and region overlap the planned paper's** [V-search].
  — [MDPI](https://doi.org/10.3390/earth6020034)
- Logistic-regression susceptibility for the Ham Luong River (100 locations) [V-search] — [VNU J. Earth & Env. Sci.](https://js.vnu.edu.vn/EES/article/view/5234)
- Cambodia: SEI / *Water* 2022 hotspot assessment (Landsat/Sentinel-2, historical rates up to tens of m/yr). Descriptive, no forecast [V-search] — [MDPI Water 14(13):1981](https://www.mdpi.com/2073-4441/14/13/1981)
- AGU FM 2020 abstract on erosion hotspots in Cambodia and the VMD via GEE (descriptive) [V-search] — [ADS](https://ui.adsabs.harvard.edu/abs/2020AGUFMEP0120017T/abstract)

### Inferences
- "Any calibrated forecast of bank position in the Vietnamese Mekong" appears unclaimed within the search scope. The Earth 2025 corridor paper must be checked to confirm it has no forward probabilistic forecast.
- The CEGIS 30/50/70 % probability bands are the most serious "operational prior art" for calibrated one-year-ahead bank-erosion forecasting. Their calibration has apparently never been reported as empirical coverage, so the planned paper can frame per-reach coverage evaluation as the missing piece.
- The Brahmaputra CA-Markov paper's "% of transects within ±10 m" is a crude coverage-like metric. Cite it and contrast it with nominal-level coverage.

### Gaps
- The CEGIS primary method documents (EGIS 2002 TN-29; CEGIS 2005 prediction report) and Nardi et al. (2013) were not accessed. The exact meaning of the "30/50/70 %" levels (probability of exceedance of erosion distance? of a location eroding?) is unconfirmed.
- I found no ML bankline forecast for the Indus, the Amazon main stem (beyond Ucayali), or the Yellow River with quantile/GP/ensemble UQ. This may reflect search limits rather than absence.

---

## Q3. Do recent shoreline-forecasting benchmarks (ShoreShop 1/2, CoastSat-based forecasting, CoSMoS-COAST 2023/2024) evaluate interval coverage?

### Takeaway
No. ShoreShop2.0 scored deterministic accuracy only. CoSMoS-COAST (Vitousek 2023 JGR-ES; 2024 Sci Rep) produces ensemble-Kalman parametric bands plus an RMSE-based structural band meant to contain about 95 %, but the 2024 paper does not report the empirical fraction of held-out observations inside the bands. The ML shoreline paper by Adeli et al. (2025) produces Monte Carlo occupancy probabilities without testing calibration. Coverage evaluation is a gap here too.

### Cited Findings
- **ShoreShop2.0** — Mao, Coco, Vitousek, … Splinter (2025), "Benchmarking shoreline prediction models over multi-decadal timescales", *Communications Earth & Environment* 6, 581, DOI 10.1038/s43247-025-02550-4 [V-fetched via USGS record]:
  - Design: 34 groups made blind predictions for an anonymised site ("BeachX", revealed as Curl Curl, NSW) at 5-year and 50-year horizons.
  - Result: the best models reached about 10 m, comparable to satellite shoreline error.
  - The abstract mentions no uncertainty bands, probabilistic forecasts or coverage.
  — [USGS pubs 70270366](https://pubs.usgs.gov/publication/70270366); [UNSW news](https://www.unsw.edu.au/newsroom/news/2025/08/Predicting-beach-changes-models-just-as-good-as-satellites)
- **CoSMoS-COAST 2024** — Vitousek et al. (2024), "Scalable, data-assimilated models predict large-scale shoreline response to waves and sea-level rise", *Scientific Reports*, DOI 10.1038/s41598-024-77030-4 [V-fetched via PMC]:
  - Ensemble: 200-member littoral-cell EnKF for parametric uncertainty.
  - Structural band: from validation RMSE, intended to contain "~95 %".
  - Periods: calibration 1990–2015, hindcast 2015–2020 with data assimilation off, projection to 2100.
  - Reported metrics: RMSE and index of agreement (0.44 South Atlantic vs 0.56 California).
  - **No empirical band coverage reported; no conformal.**
  — [PMC11564573](https://pmc.ncbi.nlm.nih.gov/articles/PMC11564573/)
- **CoSMoS-COAST 2023** — Vitousek et al. (2023), "A model integrating satellite-derived shoreline observations for predicting fine-scale shoreline response to waves and sea-level rise across large coastal regions", *JGR Earth Surface*, DOI 10.1029/2022JF006936. Ensemble Kalman filter with satellite shoreline assimilation; California projections data release 2023 [V-search] — [Wiley](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2022JF006936); [USGS data release](https://www.usgs.gov/data/projections-shoreline-change-california-due-21st-century-sea-level-rise)
- **ML probabilistic shoreline** — Adeli, Dastgheib, Roelvink (2025), "Shoreline dynamics prediction using machine learning models: from process learning to probabilistic forecasting", *Frontiers in Marine Science* 12, DOI 10.3389/fmars.2025.1562504 [V-fetched]:
  - Training data: DNN/CNN/LSTM/ConvLSTM on **synthetic** ShorelineS output.
  - Horizon: 1 year.
  - UQ: 1,000 Monte Carlo wave-direction runs → pixel shoreline-occupancy probability.
  - **No PICP/CRPS/reliability diagrams; no conformal.**
  — [Frontiers](https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2025.1562504/full)
- Hainan Island GPR shoreline-forecast preprint ("Shoreline Forecasting and Uncertainty", preprints.org).
  - Reported results: temporal-validation R² 0.781 and RMSE 11.81 m, with intervals about ±32–40 m by 2050 (from the search snippet).
  - Not fetched (403), so whether it checks coverage is unknown [UNVERIFIED].
  — [preprints.org](https://www.preprints.org/frontend/manuscript/7ac5e17ebf561eed1340b92bfeddfa69/download_pub)
- Classic statistical shoreline forecasting (EPR, LR, WLR, Kalman filter) on coastal Bangladesh reports RMSE that grows with horizon. No coverage is mentioned in the snippet [V-search] — [NSF-PAR 10391500](https://par.nsf.gov/servlets/purl/10391500)

### Inferences
- An empirical-coverage evaluation of shoreline/bankline forecast intervals would also be new relative to the main coastal benchmarks. Framing the paper's evaluation protocol (nominal vs empirical coverage, interval width, Winkler/interval score, per-reach) as something ShoreShop-type benchmarks lack is fair.
- CoSMoS-COAST's "±k·RMSE structural band" is conceptually a crude, unconditional split-conformal interval (residual quantile from a hindcast window) without the finite-sample guarantee or quantile choice. The planned paper should point this out explicitly, because a coastal reviewer may argue "CoSMoS already does residual-based bands".

### Gaps
- ShoreShop 1.0 (Montaño et al. 2020, *Sci Rep*) was not re-checked in this session. From memory it was deterministic, but this is unverified here.
- I could not access the ShoreShop2.0 full text to confirm whether any team submitted uncertainty bands voluntarily.

---

## Q4. Does a deep-learning bankline/planform forecaster with uncertainty exist for any big river (2023–2026)?

### Takeaway
Deep-learning planform forecasters exist (the U-Net on the Jamuna from TU Delft/Deltares; an undergraduate BiLSTM-GRU thesis on Bangladeshi rivers), but none found quantifies predictive uncertainty or reports coverage. A 2026 Scientific Reports "hybrid AI-geoinformatics river course change" paper could not be inspected.

### Cited Findings
- Magherini, Mosselman, Chavarrías, Taormina, "Deep learning for planform predictions of braided rivers", EGU25-650 (2025). U-Net CNN on JRC Global Surface Water for the Brahmaputra-Jamuna, binary water/non-water: 4 yearly images → year 5 (1-year-ahead). No UQ is described in the abstract. A full paper, "A deep-learning model for predicting the planform evolution of braided sand-bed rivers", is in the TU Delft repository (not inspected) [V-search] — [EGU25-650](https://meetingorganizer.copernicus.org/EGU25/EGU25-650.html); [EPFL STREEM project page](https://www.epfl.ch/labs/streem/wp-content/uploads/2025/11/STREEM_project_DLRiverMorphology.pdf)
- Rahman, Elma, Tashin, Afrin (2026), "Predicting Riverbank Erosion and Accretion Using Multi-level LSTM-Based Deep Models and Satellite-Derived Land Cover Indices", B.Sc. thesis, BRAC University [V-fetched]:
  - Data: seven rivers, mainly Bangladeshi (Jamuna and Padma are mentioned), Landsat/Sentinel-2 1988–2025.
  - Model: BiLSTM-GRU with attention.
  - Target: quantised into tertile classes and evaluated with confusion matrices.
  - Full text contains 0 occurrences of "conformal" or "quantile". "Uncertainty" appears 5 times, apparently not as predictive intervals.
  — [BRAC DSpace PDF](https://dspace.bracu.ac.bd/server/api/core/bitstreams/afc70315-1ebc-435b-91ab-25975e33802f/content)
- "Hybrid AI-Geo-informatics framework for river course change prediction and disaster risk mitigation", *Scientific Reports* 2026 (s41598-026-62726-6). The search snippet mentions CNN/U-Net/LSTM/ConvLSTM, but the page redirected to a login. Title, river and UQ are **unverified** [UNVERIFIED] — [Nature](https://www.nature.com/articles/s41598-026-62726-6)
- EGU26-22: Transformer U-Net segmentation of Brahmaputra morphology from Sentinel-1/2 (Dice 0.95–0.96). This is segmentation, not forecasting [V-search] — [EGU26-22](https://meetingorganizer.copernicus.org/EGU26/EGU26-22.html)
- A GitHub hobby project on Jamuna bankline prediction reports that a 37-year dataset "did not yield reliable erosion predictions" and that no surveyed ground truth exists (non-peer-reviewed) — [GitHub semisaad](https://github.com/semisaad/River-Bankline-Prediction-)
- A Mekong-Delta coastline RNN/LSTM/BiLSTM comparison exists for **coastal** erosion risk (Hybrid RNN_LSTM R² 0.77). It is not riverbank and has no UQ in the snippet [V-search] — [Geoplanning](https://ejournal.undip.ac.id/index.php/geoplanning/article/view/72246)

### Inferences
- An uncertainty-quantified DL bankline forecaster for a big river is still an open niche. If the planned paper wraps any ML/DL base model (not only EPR/LRR) in conformal intervals, it fills it. Even a modest ML base learner plus CQR would be "first with calibrated intervals" within this search scope.
- The Magherini U-Net is the obvious DL competitor for the Jamuna. If the TU Delft full paper added ensembles or MC dropout, that would narrow the "DL + UQ" gap (not checked).

### Gaps
- The TU Delft full paper and the Sci Rep 2026 hybrid paper were not inspected for UQ.

---

## Overall verdict: which parts of the claim survive

Ranked by robustness, within the stated search scope:

1. **"First conformal prediction for riverbank retreat / bankline forecasts"**: survives as an application-domain first. I found no conformal application to bank erosion, channel migration, shoreline or coastal-erosion forecasting. Wording should be "to our knowledge, the first application of conformal prediction to bankline/riverbank-retreat forecasting". Do not claim methodological novelty: split, CQR, Mondrian, ACI, HopCPT and GeoCP all pre-exist, and conformal is already standard in streamflow (Auer et al. 2024) and EO (Singh et al. 2024).
2. **"Coverage evaluated per reach"**: survives for geomorphology. No bankline/shoreline work found reports empirical interval coverage at all, per reach or otherwise. Noh et al. 2024 uses RMSD on pixel probabilities, CoSMoS-COAST gives no coverage numbers, ShoreShop2 is deterministic, and CEGIS reports only informal hit rates. Methodologically it mirrors Auer et al.'s per-basin coverage CDFs, which must be cited.
3. **"Coverage under distribution shift (sand mining, dams)"**: survives for geomorphology and is the strongest scientific hook. Online vs offline calibration under shift has been done for streamflow (Auer et al. 2024), and change-point conformal exists generically (CPTC, NeurIPS 2025). Linking coverage loss to *documented anthropogenic drivers* is new within scope.
4. **"Any calibrated probabilistic bank-position forecast in the (Vietnamese) Mekong"**: survives; none found. Mekong ML work is susceptibility classification (Physical Geography 2025, AUC 0.85) or descriptive rates. **Risk item:** confirm that the *Earth* 2025 Mekong corridor paper (Landsat 2000–2023, Tien/Hau region, numerical simulation) contains no forward probabilistic forecast.
5. **"Probabilistic/calibrated 1–3-year bank-erosion forecast in general"**: does **not** survive as a first. CEGIS has issued one-year-ahead probabilistic (30/50/70 %) bank-erosion forecasts for the Jamuna/Padma/Ganges since 2004. Noh et al. 2024 give Bayesian risk maps (5–30 yr) for the Ucayali, and CoSMoS-COAST gives ensemble bands for shorelines. Frame the contribution as distribution-free, finite-sample-valid intervals with verified coverage, contrasted with probability products whose calibration has not been reported.
6. **Benchmark vs EPR/LRR**: not novel by itself, since EPR/LRR/WLR/Kalman comparisons are standard (Bangladesh coast, Padma, Brahmaputra DSAS papers). Its value is as the base learner whose conformalised intervals are compared.

Citations to double-check before using (unverified or abstract-only): the Sci Rep 2026 hybrid river-course paper; the Hainan GPR preprint; Sarker et al. 2024 (Jamuna ANN); the WCI-MDN runoff paper's venue; the Yellow River Geomorphology 2024 paper; the *Earth* 2025 Mekong paper's contents; and the CEGIS 30/50/70 % method (secondary sources only).
