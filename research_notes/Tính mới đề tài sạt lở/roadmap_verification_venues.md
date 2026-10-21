# Roadmap claim verification and venue fit (docs/roadmap.md, checked 21 Oct 2026)

## Q1. Do the roadmap's URLs resolve to the named works, and do they support the sentences that cite them?

### Takeaway
Out of 12 sourced claims, 4 are wrong as written and need fixing before anything is shared:
- **SGGP 585/741/87:** the linked article has none of these numbers. They come from VnExpress (15/8/2023), describe the situation "as of 2022", and the 87 sites are "đặc biệt nguy hiểm" (especially dangerous), not "khẩn cấp" (emergency).
- **"REAL (ESSD 2025)" link:** it points to the NERM dataset (Northern Eurasia, no Mekong).
- **ODM Đồng Tháp:** the data are commune/district aggregates, not point sites.
- **JRC GSW:** it stops at 2021.

Several others are partly right and need rewording: the ISPRS 2010 description, the ShoreShop "simple beat ML" sentence, the MARD WebGIS (launched 2018, 564 includes coastal sites), and Binh et al. 2024 (label source not stated in the abstract).

### Cited Findings

**Verification table**

| # | Roadmap claim (line) | Cited source | Link resolves to named work? | Source supports claim? | Correction |
|---|---|---|---|---|---|
| 1 | Cục QLĐĐ&PCTT: 2023 có 585 điểm, 741 km, 87 điểm khẩn cấp (l.12) | [SGGP post684067](https://www.sggp.org.vn/dbscl-lai-nom-nop-lo-sat-lo-post684067.html) | Resolves to "ĐBSCL: Lại nơm nớp lo sạt lở", SGGP, 31/3/2023 | **No.** The article gives "gần 800 khu vực sạt lở", "tổng chiều dài gần 1.000km" (Tổng cục PCTT), plus local figures (Cái Bè 62 điểm; Hậu Giang 8 điểm). It does not contain 585, 741 or 87. | Cite [VnExpress, "Dòng Mekong 'giận dữ'", 15/8/2023](https://vnexpress.net/dong-mekong-gian-du-4634044.html): 585 điểm, >741 km, per Cục quản lý đê điều và PCTT, chart labelled "tính đến 2022". 87 điểm (135 km) are **đặc biệt nguy hiểm**, 155 nguy hiểm (306 km), 343 bình thường (300 km). Write "tính đến 2022", not "2023", and "đặc biệt nguy hiểm", not "khẩn cấp". |
| 2 | Cục chỉ công bố số tổng; chưa có danh sách chính thức gắn tọa độ (l.12) | none | n/a | Mostly true, but there **is** a public list of named sites without coordinates. The [ODM "Bản đồ quản lý lở đất WebGIS ĐBSCL" dataset](https://data.opendevelopmentmekong.net/vi/dataset/b-n-d-qu-n-ly-l-d-t-webgis-d-ng-b-ng-song-c-u-long-vi-t-nam) (source: Vietnam Disaster Management Authority; dated 2018, updated 2022) has a CSV `land_slide_locations.csv` with columns STT, Tỉnh, Địa điểm, Dài (m), Tổng (m). Addresses are text only, the description says 55 locations, and the 13 provinces are listed. | Rephrase: "Có danh sách địa điểm dạng văn bản (WebGIS 2018, 55 vị trí, tải được từ ODM) nhưng không có tọa độ." That list is itself a seed for geocoding. |
| 3 | Bộ dữ liệu sạt lở Đồng Tháp 2016–2019 trên ODM, tải được SHP/GeoJSON (l.15) | [ODM Đồng Tháp](https://data.opendevelopmentmekong.net/lo/dataset/impacts-of-mekong-river-erosion-in-dong-thap-province) | Yes. "Impacts of Mekong river erosion in Dong Thap province", 2016–2019, published by Open Development Vietnam. | Partly. SHP/KML/GeoJSON exist through GeoServer, plus CSV/WMS. But the attributes are **per administrative unit**: number of communes facing erosion, erosion length (km), area (ha), houses to relocate, collapsed houses, economic loss. Sources are Dong Thap DARD and the water-governance department. | Not a point inventory. Use it only as a commune/district-level count, or to sanity-check geocoded sites. Say so in the text. |
| 4 | WebGIS Bộ NN&PTNT năm 2020 với 564 điểm (l.16) | none (UNVERIFIED) | n/a | Partly. MARD launched the riverbank/coastal erosion WebGIS in **June 2018** ([SGGP 18/3/2020](https://www.sggp.org.vn/som-hoan-thien-ban-do-sat-lo-vung-dbscl-post550101.html)). SGGP (3/2020) reports "564 vị trí sạt lở bờ sông, xói lở bờ biển với chiều dài hơn 834km", i.e. it **includes coastal sites**. [ADB SEADS, 15/10/2020](https://seads.adb.org/articles/viet-nam-using-web-mapping-technology-monitor-mekong-deltas-riverbanks-and-coastline) gives 564 hotspots, 104 extremely dangerous, 121 dangerous. ODM lists the viewer URL as http://satlodbscl.phongchongthientai.vn, which did not respond from this machine on 21/10/2026. | "WebGIS ra mắt 6/2018; số liệu 564 vị trí sạt lở bờ sông **và bờ biển**, >834 km (báo chí dẫn, 3/2020)". The viewer is currently unreachable, so the bulk-download question is still open. |
| 5 | Dự báo gần nhất ở ĐBSCL là ngoại suy tuyến tính DSAS ở Sa Đéc/Hồng Ngự từ 2010, một con số cố định, không có độ bất định, không kiểm chứng (l.20) | [ISPRS 2010 PDF](https://www.isprs.org/proceedings/XXXVIII/part8/pdf/W01OH3_20100308201836.pdf) | Yes. Lam Dao Nguyen, Nguyen Thanh Minh, Pham Thi Mai Thy, Hoang Phi Phung, Hoang Van Huan, "Analysis of changes in the riverbanks of Mekong River – Vietnam by using multi-temporal remote sensing data", ISPRS Archives XXXVIII Part 8, Kyoto 2010, p. 287ff. | Mostly. Data are Landsat MSS/TM/ETM+, ASTER, ERS-2 (plus SPOT/Radarsat in §3.1), 1989–2009, and 1966–68 topographic maps. Transects come from DSAS; the regression is a **time-weighted linear regression the authors wrote in Matlab**, with weights favouring recent years. Forecasts are for 2015 and 2020; Sa Đéc/Hồng Ngự are "forecasted to erode from 100 to 520m in next 10 years". No prediction interval, no hindcast validation. "Most recent forecast in the VMD" was **not verified** and is risky. | Reword: "weighted linear regression on DSAS transects (Nguyen et al. 2010), point forecasts for 2015/2020 without intervals or validation". Drop "gần nhất" (most recent) unless a dedicated search confirms it. Bonus: the 2015/2020 forecasts can now be scored against Landsat, which makes a neat retrospective benchmark. |
| 6 | Bản đồ nguy cơ kiểm chứng bằng điểm sạt lở được báo cáo, ví dụ Binh et al. 2024, AUC 0,86 (l.23) | [VNU EES 5234](https://js.vnu.edu.vn/EES/article/view/5234) | Yes. Doan Van Binh, Le Van Quyet, Luc Anh Tuan, "Predict the Riverbank Erosion Susceptibility for the Ham Luong River Using the Logistic Regression Model", VNU J. Sci.: Earth & Env. Sci. 40(4), 25/12/2024 | AUC 0.86 is correct (accuracy 0.83; logistic regression, 12 factors, 15-fold CV). But the river is the **Hàm Luông**, not Tiền/Hậu, and the abstract says only "100 riverbank locations classified as eroded or stable". It does **not** say they were reported sites. The full-text PDF returned HTTP 500. | Check the full text before calling this "report-based". Also note a counter-example: [Nguyen et al. 2025, *Physical Geography*, doi:10.1080/02723646.2025.2555849](https://doi.org/10.1080/02723646.2025.2555849) maps VMD riverbank erosion susceptibility from **Landsat-derived erosion points** (2010/2015/2024) with AdaBoost/CatBoost/GB/RF, best AUC 0.85 (details from search snippet; DOI and title confirmed via Crossref, abstract not read). So not all existing VMD maps are report-labelled. H3 must define its contrast carefully. |
| 7 | Nền tảng: Steger et al. 2017 (l.25) | [Springer link](https://link.springer.com/article/10.1007/s10346-017-0820-0) | Yes; the DOI resolves (WebFetch was bounced to a login, so checked via Crossref): Steger, Brenning, Bell, Glade 2017, "The influence of systematically incomplete shallow landslide inventories on statistical susceptibility models and suggestions for improvements", *Landslides* 14:1767–1781 | Yes, systematic incompleteness of inventories biases models. | OK as is. |
| 8 | Nền tảng: Steger et al. 2016 (l.25) | [NHESS 16/2729](https://nhess.copernicus.org/articles/16/2729/2016/) | Yes. Steger, Brenning, Bell, Glade 2016, "The propagation of inventory-based positional errors into statistical landslide susceptibility models", NHESS 16:2729–2745 | Partly. It is about **positional error** (shifting points 5–120 m distorts model relationships and validation results), not reporting/proximity bias. | Cite it for the per-point location-error sensitivity analysis (P3). For the AUC-inflation argument, add [Steger et al. 2021, STOTEN 776:145935, "Correlation does not imply geomorphic causation… landslide data collection effects"](https://doi.org/10.1016/j.scitotenv.2021.145935) and [Steger et al. 2016, Geomorphology, doi:10.1016/j.geomorph.2016.03.015](https://doi.org/10.1016/j.geomorph.2016.03.015) ("discrepancies between quantitative validation results and geomorphic plausibility"). Both DOIs confirmed via Crossref. |
| 9 | Nền tảng: Stanley & Kirschbaum 2017 (l.25) | [NTRS PDF](https://ntrs.nasa.gov/api/citations/20170007214/downloads/20170007214.pdf) | Yes. [NTRS 20170007214](https://ntrs.nasa.gov/citations/20170007214): "Effects of Inventory Bias on Landslide Susceptibility Calculations", Proc. 3rd North American Symposium on Landslides (AEG), 2017 | Yes. They took a synthetic unbiased Oregon inventory, removed landslides to mimic population/infrastructure reporting bias, refit logistic regression, and repeated with the real SLIDO inventory. This is the closest analogue to H3. | Cite as a conference paper. |
| 10 | Có biến phụ trợ thấp hơn LR, hoặc không; ở bờ biển mô hình đơn giản từng thắng ML (ShoreShop, Mao et al. 2025) (l.30) | [USGS pubs 70270366](https://pubs.usgs.gov/publication/70270366) | Yes. Mao, Coco, Vitousek et al. (35 authors), "Benchmarking shoreline prediction models over multi-decadal timescales", *Commun. Earth Environ.* 6:581, 2025, doi:10.1038/s43247-025-02550-4 | Partly. The abstract says 34 groups made blind predictions and the best models reached ~10 m accuracy. Per the USGS summary (via search snippet; the USGS news page did not render), ML models were the most common entries but the top performer was CoSMoS-COAST, a simplified physics-based model. I could not read the full paper (nature.com login redirect). | Soften to: "in a blind benchmark of 34 shoreline models, a reduced-complexity physics-based model ranked first and data-driven models did not dominate (Mao et al. 2025)". Quote the exact ranking after reading the paper. Note that it is a coastal site (Curl Curl, NSW), not a river. |
| 11 | GEE Community: 150 EECU-giờ/tháng, phi thương mại, cả sinh viên, vượt quota bị chậm chứ không bị cắt (l.39) | [Google noncommercial tiers](https://developers.google.com/earth-engine/guides/noncommercial_tiers) | Yes | Yes. Community = 150 EECU-h/month, open to all verified noncommercial projects, "intended for undergraduate students and other users with typical computation needs". Limits are "**not** hard cut-off values"; above quota you get "restricted mode" with reduced concurrency and workers. Nuance: Contributor (1,000 EECU-h/month) targets graduate students and requires a billing account, though noncommercial use is not charged. Partner gives 100,000 EECU-h. | OK. Optionally note the Contributor tier as the upgrade path. |
| 12 | Dữ liệu lùi bờ toàn cầu: REAL (ESSD 2025), chỉ trung bình thập kỷ, sông >150 m (l.40) | [ESSD 17/5615](https://essd.copernicus.org/articles/17/5615/2025/) | **No.** It resolves to Chalov et al. 2025, "The Northern Eurasian Riverbank Migration multi-tool dataset (NERM)", ESSD 17:5615–5639 (12 Eurasian basins, no Mekong). | The phrase "decadal-scale averages, rivers >150 m" is NERM's **description of earlier global datasets**, not a description of NERM. | Cite Langhorst & Pavelsky 2023 (see Q2). Either keep NERM as a secondary citation for the limitation, or drop it. |
| 13 | Ảnh/mặt nước: Landsat 2000–2024 … JRC Global Surface Water (l.38) | none | n/a | JRC GSW v1.4 YearlyHistory covers 1984-03-16 to 2022-01-01, i.e. **through 2021 only** ([GEE catalog](https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_YearlyHistory)). | Use your own Landsat/S2 water classification for 2022–2024 (or the whole period). Use JRC only as a cross-check up to 2021. |
| 14 | Conformal bằng MAPIE (l.42) | none | n/a | MAPIE exists: [PyPI](https://pypi.org/project/MAPIE/) latest is 1.6.0 (checked 21/10/2026), scikit-learn-contrib, "estimating prediction intervals". | OK; pin the version in the frozen protocol. |
| 15 | Tạp chí: SJR 2025 EMS 1,344, Q1 4 ngành gồm Software; C&G 1,033 Q1 Computers in Earth Sciences; IJAEOG 2,177 (l.54–57) | "đoạn trích kết quả tìm kiếm" | n/a | **Confirmed** from the SCImago full ranking CSV (`journalrank.php?out=xls`, column header "Total Docs. (2025)", downloaded 21/10/2026). Details in Q3. IJAEOG "first decision ~3 days, ~130 days to acceptance, 14% acceptance" was **not verified** (ScienceDirect journal pages return 403). | Mark the IJAEOG speed/acceptance figures as unverified. |
| 16 | Lưu lượng Tân Châu từ cổng MRC (l.41) | none (UNVERIFIED) | n/a | Not checked in this pass. | Still open. |

**Other counts that conflict with the 585 figure (for a footnote on how unstable the official numbers are):**
- [Thông báo 349/TB-VPCP (2023)](https://static.luatvietnam.vn/tai-file-thong-bao-349-tb-vpcp-2023-ket-luan-ve-phong-chong-sut-lun-o-dong-bang-song-cuu-long-276246-d6/uploaded/VIETLAWFILE/2023/11/349_TB-VPCP_141123103214.pdf.aspx) cites MARD: since 2016, 779 sites, >1,130 km (from search snippet, PDF not opened).
- [Đại Đoàn Kết](https://daidoanket.vn/dong-bang-song-cuu-long-sat-lo-bua-vay-bai-1-bat-an-ben-mieng-ha-ba-10261609.html) gives 558 sites, >740 km, 81 especially dangerous (search snippet).
- [Saigon Times](https://thesaigontimes.vn/dong-bang-song-cuu-long-co-hon-740-diem-sat-lo/) cites the Southern Institute of Water Resources Research: 743 sites, 794 km, 168 especially dangerous (search snippet, undated).

### Inferences
- The official counts swing between 558 and 800 sites depending on date, agency and whether coastal sites are included. The paper should cite one dated source (VnExpress/Cục, as of 2022). This instability also supports the label-bias motivation: report-based inventories are moving targets.
- Point 6 matters for the reframed headline. A satellite-labelled VMD susceptibility study (Physical Geography 2025, AUC 0.85) already exists. The novelty claim therefore has to be the **paired comparison**: the same model and covariates, trained/evaluated with reported labels versus satellite labels, with the AUC gap explained by distance to settlements and roads. "Nobody uses satellite labels" is not available as a claim.
- Steger 2016 (NHESS) is the right citation for the 100–500 m geocoding error. Steger 2021 (STOTEN) and Stanley & Kirschbaum 2017 are the right ones for "reporting bias inflates validation".

### Gaps
- Binh et al. 2024 full text (label source) could not be retrieved (HTTP 500 on the PDF).
- ShoreShop full text not read; the model ranking comes from a USGS summary seen via search snippet.
- Whether the MARD WebGIS layer can be downloaded (or has coordinates) is unknown; the host did not respond.
- The claims "no probabilistic forecast / no conformal for banklines" and "2010 is the most recent VMD forecast" were not searched here.
- MRC Tân Châu discharge access conditions not checked.

## Q2. What is the correct citation for the global Landsat riverbank erosion dataset (>150 m), and does it have Mekong data?

### Takeaway
The correct citation is Langhorst, T. & Pavelsky, T. (2023), "Global Observations of Riverbank Erosion and Accretion From Landsat Imagery", *JGR: Earth Surface* 128(2), e2022JF006774, doi:10.1029/2022JF006774. The dataset ("REAL", Riverbank Erosion and Accretion from Landsat) is on Zenodo (doi:10.5281/zenodo.7045021, CC-BY-4.0). It gives one multi-year mean rate per SWORD reach/node (Landsat ~2001 vs ~2019), not annual series. Mekong delta coverage is likely but not confirmed.

### Cited Findings
- Crossref: doi 10.1029/2022JF006774, "Global Observations of Riverbank Erosion and Accretion From Landsat Imagery", JGR Earth Surface vol. 128, article e2022JF006774, issued Feb 2023. Preprint: ESSOAr doi 10.1002/essoar.10511473.1 (2022) — [Crossref API](https://api.crossref.org/works/10.1029/2022JF006774); [Semantic Scholar record](https://api.semanticscholar.org/graph/v1/paper/DOI:10.1029/2022JF006774)
- Abstract: "the first global data set of riverbank erosion for >370,000 km of large rivers using up to 20 years of water classifications from Landsat imagery". Uncertainty comes from propagating water-classification error. For rivers >150 m wide, the median erosion is 1.52 m/yr (approximately log-normal). Against 25 independent estimates: normalized MAE 42%, bias 5.8%. Width is the best first-order predictor — [Semantic Scholar abstract](https://api.semanticscholar.org/graph/v1/paper/DOI:10.1029/2022JF006774)
- Dataset: "Riverbank Erosion and Accretion from Landsat", Zenodo 10.5281/zenodo.7045021 (2022-09-02, CC-BY-4.0); code release "tedlanghorst/REAL: publication" 10.5281/zenodo.7045008 — [Zenodo API](https://zenodo.org/api/records/7045021)
- The code's settings show SWORD v09 reaches filtered `width > 150`, river-type reaches only (`reach_id % 10 == 1`), `YR1 = 2001`, `DT = 18`, 30 m scale. So a single ~2001→2019 change is converted to a mean annual rate, not a time series — [GitHub tedlanghorst/REAL, SCREAMinG_iterate.py](https://github.com/tedlanghorst/REAL/blob/HEAD/EarthEngine/SCREAMinG_iterate.py)
- NERM (ESSD 2025) describes the earlier global datasets as limited to decadal-scale averages and rivers >150 m, and NERM itself covers only 12 Northern Eurasian basins (no Mekong) — [ESSD 17:5615](https://essd.copernicus.org/articles/17/5615/2025/)
- Tiền River width is 0.33–2.1 km (Nguyen et al. 2010) — [ISPRS 2010](https://www.isprs.org/proceedings/XXXVIII/part8/pdf/W01OH3_20100308201836.pdf)

### Inferences
- Tiền/Hậu are well above 150 m, so they should be in REAL if SWORD v09 classifies the delta reaches as type 1 (river). Tidally influenced or multichannel delta reaches may be typed differently and dropped. The roadmap should say "REAL provides one ~2001–2019 mean rate per reach/node", which is useful as an external check of long-term rates but not of 1–3-year forecasts.
- Roadmap line 40 should read: "REAL (Langhorst & Pavelsky 2023, JGR Earth Surface; Zenodo 10.5281/zenodo.7045021) — one mean rate ~2001–2019, rivers >150 m (SWORD)".

### Gaps
- Mekong coverage not confirmed: the Wiley full text and the ESSOAr preprint returned 403. To confirm, download the Zenodo files and filter by Mekong delta SWORD reach IDs / bounding box (~9.5–11°N, 104.8–106.8°E).

## Q3. Venue fit: SJR/quartile, APC or free route, scope fit, example papers; does EMS desk-reject application papers?

### Takeaway
All eight journals are Q1 in SJR 2025. Ranked for a label-bias-led paper, the best fits are NHESS, IJAEOG and Geomorphology:
- **NHESS:** hazard-susceptibility and inventory-bias literature lives there. Full OA at €1,800, waived for Research4Life countries.
- **IJAEOG:** full OA, USD 3,670.
- **Geomorphology:** subscription route is free.

EMS and Computers & Geosciences publish mostly tool/framework papers in this space. No explicit EMS rule against application papers was found, but its guide asks for generalizable insights, so a pure Mekong application is at real desk-reject risk unless it is packaged as a reusable protocol or software. RSE is a stretch for an application paper.

### Cited Findings

**SJR 2025, from the SCImago full CSV (downloaded 21/10/2026, header "Total Docs. (2025)") — [SCImago Journal Rank](https://www.scimagojr.com/journalrank.php)**

| Journal | SJR 2025 | Best quartile; categories (all Q1) | SCImago OA flag |
|---|---|---|---|
| Remote Sensing of Environment | 4.266 | Computers in Earth Sciences; Geology; Soil Science | No (hybrid) |
| IJAEOG | 2.177 | Computers in Earth Sciences; Earth-Surface Processes; Global & Planetary Change; Management, Monitoring, Policy & Law | Yes |
| Catena | 1.759 | Earth-Surface Processes | No |
| NHESS | 1.418 | Earth & Planetary Sciences (misc.) | Yes |
| Environmental Modelling & Software | 1.344 | Ecological Modeling; Environmental Engineering; Modeling & Simulation; Software | No |
| Computers & Geosciences | 1.033 | Computers in Earth Sciences; Information Systems | No |
| Geomorphology | 1.003 | Earth-Surface Processes | No |
| Earth Surface Processes and Landforms | 0.843 | Earth & Planetary Sci. (misc.); Earth-Surface Processes; Geography, Planning & Development | No |
| (ref) JGR Earth Surface | 1.437 | Earth-Surface Processes; Geophysics | No |
| (ref) Ecological Informatics / EAAI | 1.770 / 1.782 | — | Yes / No |

**APC / free route**
- Elsevier APC list, "Prices as of date: 05-Oct-2026", excl. taxes (USD/EUR):
  - RSE hybrid: 4,310 / 3,930
  - Catena hybrid: 4,170 / 3,800
  - C&G hybrid: 3,870 / 3,530
  - EMS hybrid: 3,570 / 3,260
  - Geomorphology hybrid: 3,500 / 3,190
  - IJAEOG **Full Open Access**: 3,670 / 3,350

  Hybrid means publishing under subscription is free — [Elsevier APC price list (xlsx)](https://legacyfileshare.elsevier.com/els_com_pricing/article-publishing-charge.xlsx), linked from [Elsevier pricing page](https://www.elsevier.com/about/policies-and-standards/pricing/journals)
- Older IJAEOG APC figures (DOAJ USD 2,770; Editage USD 2,400; 2019 launch USD 2,250) are stale — [DOAJ](https://doaj.org/toc/1872-826X); [Editage](https://www.editage.com/research-solutions/journal/international-journal-of-applied-earth-observation-and-geoinformation/14695)
- NHESS (submissions from 1/1/2025): €1,800 net list price; EGU members / institutional agreement €1,620; EED countries 50% off; **Research4Life countries: waived** (only if all corresponding authors are R4L-affiliated). Brief communications cost €900 — [NHESS APC page](https://www.natural-hazards-and-earth-system-sciences.net/about/article_processing_charges.html)
- Viet Nam appears to be in Research4Life **Group B** (inferred from the WIPO ARDI eligibility listing; the R4L page itself returned 403) — [WIPO ARDI eligibility](https://www.wipo.int/ardi/en/eligibility.html); [Research4Life eligibility](https://research4life.org/access/eligibility/)
- ESPL is hybrid (Wiley). An aggregator lists the APC at USD 4,840 (not verified on Wiley, which returned 403) — [Journal Metrics](https://www.journalmetrics.org/journal/earth-surface-processes-and-landforms); [MPDL OA record](https://oapublishing.mpdl.mpg.de/journals/Record/Wiley-ESP)

**EMS scope and desk rejection**
- The EMS guide (seen via search snippet; ScienceDirect returned 403 to WebFetch, curl and the Chrome extension) wants generic frameworks/techniques, and model development or application work only if it yields "insights that are generalizable in some way and are likely to be of interest to those studying other systems". It also encourages comparison with alternative approaches — [EMS guide for authors](https://www.sciencedirect.com/journal/environmental-modelling-and-software/publish/guide-for-authors)
- SciRev: immediate rejection takes ~34 days on average; first review round 5.8 months; 7.0 months total for accepted papers. One author reported a desk rejection as "too narrowly focused/out of scope" (single anecdote) — [SciRev EMS](https://scirev.org/journal/environmental-modelling-and-software/); [SciRev reviews](https://scirev.org/reviews/environmental-modelling-and-software/)
- No explicit EMS rule that application papers without a software/modelling contribution are desk-rejected was found.

**Computers & Geosciences scope**
- A third-party copy of the guide lists a "code availability section (for code-related manuscripts)". A garbled Overleaf template line links missing checklist items to desk rejection — [eshukan mirror](https://eshukan.com/displayj.aspx?jid=45975); [Overleaf C&G template](https://www.overleaf.com/latex/templates/computers-and-geosciences/fxydfxgqwwtp). Not verified on the official page.

**Example similar papers (DOIs confirmed via Crossref unless noted)**

| Journal | Examples |
|---|---|
| EMS | Vos et al. 2019, CoastSat (GEE shoreline toolkit), [10.1016/j.envsoft.2019.104528](https://doi.org/10.1016/j.envsoft.2019.104528); Monegaglia et al. 2018, automated extraction of meandering-river morphodynamics from multitemporal RS (PyRIS), [10.1016/j.envsoft.2018.03.028](https://doi.org/10.1016/j.envsoft.2018.03.028); Simmons et al. 2022, multi-model ensemble for coastal storm erosion prediction, [10.1016/j.envsoft.2022.105356](https://doi.org/10.1016/j.envsoft.2022.105356); also QSCAT QGIS shoreline plugin (Facun 2025), [10.1016/j.envsoft.2024.106263](https://doi.org/10.1016/j.envsoft.2024.106263) |
| C&G | Lv et al. 2023, pyShore deep-learning shoreline toolkit, [10.1016/j.cageo.2022.105296](https://doi.org/10.1016/j.cageo.2022.105296); James et al. 2024, PyShoreVolume, [10.1016/j.cageo.2024.105591](https://doi.org/10.1016/j.cageo.2024.105591); Liu et al. 2026, CNN–transformer shoreline extraction, [10.1016/j.cageo.2026.106243](https://doi.org/10.1016/j.cageo.2026.106243) |
| IJAEOG | Valsangkar et al. 2024, EO + ground data for river topography and morphologic change, lower Jamuna, [10.1016/j.jag.2024.104146](https://doi.org/10.1016/j.jag.2024.104146); Yuan et al. 2025, large-scale detection of river cutoffs from multi-temporal water extent, [10.1016/j.jag.2025.104934](https://doi.org/10.1016/j.jag.2025.104934) |
| Geomorphology | Valentine et al. 2023, riverbank erosion along the fluvial-to-tidal transition, Lower Meghna, [10.1016/j.geomorph.2023.108692](https://doi.org/10.1016/j.geomorph.2023.108692); van Rooijen et al. 2024, spatiotemporal distribution of bank-erosion events and drivers, [10.1016/j.geomorph.2024.109140](https://doi.org/10.1016/j.geomorph.2024.109140); Steger et al. 2016, validation vs geomorphic plausibility, [10.1016/j.geomorph.2016.03.015](https://doi.org/10.1016/j.geomorph.2016.03.015) |
| NHESS | Freihardt & Frey 2023, riverbank erosion in Bangladesh from Sentinel-1 time series in GEE, [10.5194/nhess-23-751-2023](https://doi.org/10.5194/nhess-23-751-2023); Steger et al. 2016, inventory positional errors, [10.5194/nhess-16-2729-2016](https://doi.org/10.5194/nhess-16-2729-2016); Athanasiou et al. 2022, neural-network meta-model for dune erosion, [10.5194/nhess-22-3897-2022](https://doi.org/10.5194/nhess-22-3897-2022) |
| RSE | Isikdogan et al. 2017, RivaMap, [10.1016/j.rse.2017.03.044](https://doi.org/10.1016/j.rse.2017.03.044); Rowland et al. 2016, morphology-independent planview river change from RS, [10.1016/j.rse.2016.07.005](https://doi.org/10.1016/j.rse.2016.07.005). No 2023–2026 RSE riverbank-ML paper found. |
| Catena | Bhuyan et al. 2024, landscape ecological vulnerability to riverbank erosion with ML, Brahmaputra, [10.1016/j.catena.2023.107581](https://doi.org/10.1016/j.catena.2023.107581); Liu et al. 2024, gully erosion susceptibility with three ML models, [10.1016/j.catena.2024.108275](https://doi.org/10.1016/j.catena.2024.108275) |
| ESPL | "Utilizing geospatial tools for the assessment of river bank erosion and migration patterns in complex braided and meandering river…" 2024, [10.1002/esp.6043](https://doi.org/10.1002/esp.6043); "River ice controls permafrost bank erosion across an Arctic delta" 2025, [10.1002/esp.70189](https://doi.org/10.1002/esp.70189); "Riverbank Erosion Susceptibility Under Varying Sedimentological and Freeze–Thaw Conditions in Cold Climate Regions" 2026, [10.1002/esp.70418](https://doi.org/10.1002/esp.70418). Titles from the Crossref listing; authors not retrieved. |
| Off-list but relevant | Langhorst & Pavelsky 2023 (JGR-ES) REAL; Nguyen et al. 2025 *Physical Geography* VMD susceptibility ML, [10.1080/02723646.2025.2555849](https://doi.org/10.1080/02723646.2025.2555849); Battaglini-Fischer et al. 2026 *GeoHazards* Bassac/Cần Thơ bankline change 2001–2025 (LRR, 6 Landsat images, ADCP, AHP; no forecast intervals), [10.3390/geohazards7040111](https://doi.org/10.3390/geohazards7040111) |

### Inferences
- **EMS:** its riverbank and shoreline papers are almost all tools (CoastSat, PyRIS, QSCAT) or ensemble frameworks. A Mekong application with a web map is weak there. It would only be competitive if the core contribution were a reusable, open "label-bias audit + conformal transect forecasting" protocol/package, tested beyond one site. The roadmap's own note that the web map alone is not enough is consistent with this. Risk: desk rejection in ~1 month.
- **NHESS:** best scope match for the reframed headline (reported vs satellite labels inflating susceptibility AUC). The inventory-bias literature (Steger 2016) and riverbank remote sensing (Freihardt 2023) are already there. Open discussion adds visibility. The APC may be waived if Viet Nam qualifies as R4L and all corresponding authors are Viet Nam-based. This must be confirmed.
- **IJAEOG:** good scope fit for satellite-derived labels and banklines, but APC USD 3,670 with no free route.
- **Geomorphology:** fits if the paper explains *why* reported sites cluster (settlement/road proximity vs geomorphic drivers). Free via subscription.
- **Catena:** soil- and gully-oriented, with many ML susceptibility papers. Acceptable, but the label-bias angle gets less reach there.
- **ESPL:** lower SJR; process-oriented.
- **RSE:** needs an RS methodological advance or global scale; poor fit.
- **C&G:** needs a computational/code contribution.
- **Suggested order:** NHESS (if the APC waiver is confirmed) or Geomorphology first, IJAEOG as the OA option, and EMS only if the work is reframed as a software/protocol paper.

### Gaps
- Official guide-for-authors and aims & scope text for EMS, C&G, RSE, Geomorphology and Catena could not be read (ScienceDirect blocks automated fetch; Chrome extension permission denied for that domain). The EMS wording above comes from a search snippet.
- The IJAEOG speed/acceptance figures (3 days / 130 days / 14%) are unverified.
- The ESPL APC (USD 4,840) comes from an aggregator.
- Viet Nam's current Research4Life group was not confirmed on research4life.org.
- No recent (2023–2026) RSE example on riverbank/shoreline ML with uncertainty was found.
