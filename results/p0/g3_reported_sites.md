# G3: reported erosion sites on the Tien/Hau main channels, An Giang + Dong Thap (pre-2025 boundaries)

Date of all searches and URL checks: 2026-10-22. Window 2015-2024; 2025-2026 items kept and flagged.
Candidate table: `data/hotspots/reported_candidates.csv` (158 rows, one row per site-event; all source URLs
of a merged site-event are in `source_ref`, separated by " | "). No coordinates were filled: none of the
sources gives coordinates or km markers.

## Verdict

**G3 is not met at the event-point level; it is met only at commune/reach level. Confidence: medium.**

| Definition of a "distinct site" (main channel incl. islet banks, 2015-2024) | An Giang | Dong Thap | Total | Excl. islet banks |
|---|---|---|---|---|
| A. Reported event or emergency decision, located to hamlet/khóm/landmark | 23 | 9 | **32** | 26 |
| A + commune-level events (no hamlet given) | 25 | 12 | 37 | 30 |
| A + all commune-level sites (events or official warned reaches) in communes with no hamlet-level site | 58 | 20 | **78** | 69 |

- Only definition A is something the later geocoding step can locate to ≤ 500 m. It falls short of 50.
- The ≥ 50 total depends on An Giang DONRE's warned-reach lists (2018, 2020). These name the commune only,
  are "đoạn" (reaches, often several km), and are warnings, not dated events.
- Dong Thap is badly under-represented. This is mostly an access problem (see Gaps), not evidence of few
  events. Official tallies show many more sites exist than the public record yields (table below).
- Suggested decision: do not expand provinces yet. First ask for the An Giang DONRE semi-annual monitoring
  reports (đợt quan trắc) and the Dong Thap Sở NN&MT erosion-point list. Alternatively, redefine the
  reported-label unit as "reach" with a 2-5 km position error for the H3 sensitivity analysis.

## Breakdown (main channel, 2015-2024)

Hamlet/landmark-level sites (definition A) by province × channel: An Giang: Hậu 16, Tiền 3, Vàm Nao 1, islet
(Mỹ Hòa Hưng) 3. Dong Thap: Tiền 6, islet bank 3 (Tân Quới ×2, An Hiệp).

Site-events (rows) that are events or emergency decisions, by province × channel × year:

| Province | Channel | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| An Giang | Hậu | | | | | 7 | 3 | | 5 | 3 | 4 |
| An Giang | Tiền | | | | 1 | 1 | 1 | | 1 | | |
| An Giang | Vàm Nao | | | 1 | | | | | | | |
| An Giang | islet bank | | | | 1 | 1 | | | | | 1 |
| Dong Thap | Tiền | | 1 | 1 | 1 | 2 | 1 | | 1 | | 3 |
| Dong Thap | islet bank | 1 | 1 | 1 | | | | | 2 | | 1 |

Warning rows (official warned reaches) add 79 site-event rows, mostly An Giang 2020 (49 communes named
along 12 Tiền + 27 Hậu warned reaches) and Dong Thap 2019 (11 communes named in the province's 2019 plan).

All main-channel rows in the window (125), by source type: official list quoted in news 75, news report 33,
emergency decision quoted in news 10, ODM/MARD WebGIS 2018 CSV 7. By confidence: high 20, medium 38, low 67.
By unit as the source states it: đoạn 86, vụ 26, điểm 12.

Hamlet-level or better: 51 main-channel rows (32 distinct sites). Two of the hamlet-level sites are reaches
longer than 1 km (Châu Phong 6.9 km; the Tân Quới ferry reach 1.5 km), so they are not ≤ 500 m points as stated.
Excluded or unresolved rows: canal/tributary 12 (rạch Ông Chưởng, rạch Cái Sắn, Kênh Xáng Tân An, sông Châu
Đốc, sông Bình Di, kênh Bảy Xã, sông Hồ Cứ), unresolved river 3. Outside the window: 16 rows from 2025-2026,
2 rows before 2015, 3 rows with no year (An Giang emergencies listed in QĐ 515/QĐ-UBND).

## Official counts mix units and channels

These are context only and are not added to the counts above:

| Source | Count | Unit and scope |
|---|---|---|
| An Giang 2017 | 54 | điểm, bank of sông/kênh/rạch, 4,171 m |
| An Giang 2019 (Jan-Sep) | 25 | vụ, of which 9 on the Hậu; 11 on large canals, 5 on small canals |
| An Giang 2021 (Jan-Sep) | 36 | điểm sạt lở/sụt lún/rạn nứt; 8 emergency decisions issued |
| An Giang 2023 (to 21 Jun) | 44 | điểm (53 vụ by early July) |
| An Giang QĐ 515/QĐ-UBND (17/4/2023) | 22 | đoạn, closing 26 emergency decisions (9 of the named reaches are on main channels) |
| An Giang warned reaches | 51 → 52 → 53 → 56 | đoạn, 2018 → 2019 → 2020 → 2021-2026. In 2018: 11 Tiền, 26 Hậu. In 2026: 12 Tiền, 29 Hậu, 4 Kênh Xáng |
| Dong Thap 2019 (Aug) | 85 | điểm "đang sạt lở và có nguy cơ", 21 communes (main channel and canals mixed) |
| Dong Thap 2024 (to Oct) | 27 | vụ "bờ sông, rạch / nội đồng", 818 m |
| Dong Thap 2025 | 113-155 | điểm, 2025 only (out of window) |

Sources: baoangiang a219464, a256270, a316046, a369909, a360497, a484805; SGGP post526860; nongnghiep d404325
(full URLs in the CSV).

## Search scope (all on 2026-10-22)

Web search (Vietnamese unless noted). Province, river and decision queries:
- "Quyết định công bố tình huống khẩn cấp sạt lở bờ sông Tiền Đồng Tháp"; "công bố tình huống khẩn cấp sạt lở bờ sông Hậu An Giang quyết định UBND tỉnh"
- the same two restricted to thuvienphapluat.vn; dongthap.gov.vn "công bố tình huống khẩn cấp sạt lở sông Tiền"
- "Đồng Tháp sạt lở bờ sông Tiền" + 2016 / 2017 / 2018 / 2019 2020 / 2021 / 2022 2023 / 2021-2024 (some restricted to vnexpress, tuoitre, thanhnien, sggp, plo, dantri, vietnamplus, nongnghiep, nongnghiepmoitruong, nld, vov, baotintuc)
- "An Giang sạt lở" + 2016 2017 / 2020 / 2021 / 2024 (baoangiang.com.vn)
- "từ đầu năm đến nay toàn tỉnh xảy ra vụ sạt lở … An Giang" (baoangiang, extended)
- "danh sách điểm sạt lở đặc biệt nguy hiểm ĐBSCL … Tổng cục PCTT" (extended)
- An Giang / Dong Thap "danh mục đoạn sông cảnh báo sạt lở / khoanh vùng"
- English: "Đồng Tháp / An Giang riverbank landslide …" on vietnamnews, tuoitrenews, e.vnexpress, en.vietnamplus, sggpnews

District and commune queries (baoangiang.com.vn, baodongthap.vn, or open web):
- Tân Châu
- Châu Phong
- Long Sơn / Vĩnh Hòa / Tân An / Vĩnh Xương / Long Hưng / Long Thạnh
- Phú Tân (Phú An, Phú Thạnh, Tân Hòa; Phú Hiệp, Hòa Lạc, Phú Bình, Chợ Vàm)
- Chợ Mới (Long Điền, Mỹ Hội Đông, Tấn Mỹ, Mỹ Hiệp, Bình Phước Xuân, Kiến An, Kiến Thành, Nhơn Mỹ, Long Kiến)
- Vàm Nao
- Long Xuyên (Mỹ Hòa Hưng, Bình Khánh, Mỹ Bình, Mỹ Thới, Bình Đức)
- Châu Thành AG (An Hòa, Bình Hòa)
- Châu Đốc / Vĩnh Mỹ / Châu Phú B
- Châu Phú (Mỹ Đức, Mỹ Phú, Bình Long, Cái Dầu)
- An Phú (Vĩnh Hội Đông, Phước Hưng, Vĩnh Lộc, Khánh An, Đa Phước)
- Hồng Ngự (An Lạc, An Thạnh, Tân Hội; Thường Phước, Long Khánh, Long Thuận, Phú Thuận; "thị xã Hồng Ngự"; "huyện Hồng Ngự" 2018-2021)
- Thanh Bình (Tân Quới, An Phong, Bình Thành, Tân Bình, Tân Huề, Tân Hòa)
- Cao Lãnh (Bình Hàng Trung, Mỹ Hiệp, Bình Thạnh, Mỹ Xương, Bình Hàng Tây; Tịnh Thới, Hòa An, Tân Thuận Đông/Tây, Phường 6, Phường 11)
- Sa Đéc (Tân Quy Đông, Phường 4)
- Châu Thành DT (An Hiệp, Phú Hựu, Tân Bình, An Nhơn, Tân Nhuận Đông, An Khánh)
- Lấp Vò / Lai Vung (Mỹ An Hưng, Vĩnh Thạnh, Bình Thạnh Trung, Phong Hòa, Tân Thành)
- "1207 quyết định … Tân Quới"

Direct access attempts:
- ODM CKAN API → `land_slide_locations.csv`: downloaded. 55 rows in total; 9 An Giang and 3 Dong Thap rows, all as text addresses.
- thuvienphapluat.vn search page: blocked by a Cloudflare challenge.
- baoangiang.com.vn search/tag pages: 404. Its articles load.
- baodongthap.vn: its search page needs JavaScript. Pre-2025 `.aspx` articles return HTTP 500; post-merger articles load.
- dongthap.gov.vn news articles 13174465, 20726068 and 314018: HTTP 404 to both fetchers, although the search engine indexes them. One portal PDF loaded (960/UBND-KT, 2026).
- MARD WebGIS (satlodbscl.phongchongthientai.vn, satlov2.vndss.com, satlo.vndss.com): no response, or 502.
- Bui & Tran 2023 (JMES 64(5)) full text: read. The 248 points come from satlov2.vndss.com plus field surveys. The paper has no point table.
- HCMUE papers by Trịnh Phi Hoành: cover 2009-2013 only.

"Not found" below means "not found in the searches above on 2026-10-22". Not found:
- the full text of any An Giang or Dong Thap emergency decision (only news quoting them);
- a public list of An Giang's 56 warned reaches with hamlet detail;
- any Dong Thap event list for 2015-2024 below commune level.

## URL check

Every URL in the CSV was fetched (`urllib`, cached) and checked for the commune or hamlet name.

All loaded with HTTP 200 except the following, which were confirmed with WebFetch:
- tuoitre 20241009191306685, whose body is rendered by script;
- four VietnamPlus pages that returned 502 to the script.

English-language pages (Viet Nam News, Tuổi Trẻ News) give names without diacritics; they were checked by eye.

The ODM dataset landing page carries no site text. The CSV it serves does.

One claim was dropped. A search summary cited "QĐ 1207, 4/11/2022" for Tân Quới, but no fetched page contains it.

## Gaps and caveats

- **Dong Thap 2015-2024.** The local paper's archive is dead, the provincial portal articles return 404, and the
  search engine heavily favours 2025-2026 items. Of 20 Dong Thap sites, 11 are commune-level or low confidence.
- **Islet banks.** Many Dong Thap "sông Tiền" sites are on cù lao communes (Tân Quới/Tân Long, Long Thuận,
  Phú Thuận A, An Hiệp, Tịnh Thới). Some, for example Tân Quới opposite An Long, may face a secondary channel.
  The main-channel definition needs a decision on imagery; counts are given with and without islet banks.
- **Overlap within definition A.** Sites in the same reach were counted once by hamlet. Still possibly
  overlapping: Tân Quới ấp Thượng vs the ferry reach; Bình Đức khóm 3 vs khóm 4; the two Vĩnh Thạnh Trung
  emergency segments; Mỹ Hòa Hưng ấp Mỹ Khánh vs Mỹ Khánh 2. Strict lower bound ≈ 28.
- **Conflicting sources.**
  - Bình Thành (April 2017): SGGP says "bờ sông Tiền", Viet Nam News says "Cả Lách canal".
  - Long Bình (2022): Báo An Giang says "sông Hậu", the ODM CSV says "sông Bình Di".
  - Vĩnh Thạnh Trung ấp Vĩnh Thuận: one article dates the event to 2020, another to 2021.
- **Unconfirmed.** An Giang sites with unknown or uncertain river: Khánh Hòa tổ 20, Kiến An ấp Phú Thượng 2,
  and Lai Vung Tân Hòa (Dong Thap). The commune_new values marked "?" are guesses or unknown. The
  Dong Thap 2025 rows assign commune_old = Tân Quới from the An Long-Tân Quới ferry landmark.

## Best sources for the geocoding step

1. **An Giang DONRE lists quoted in Báo An Giang** (a256270/a256873 for 2019; a284528 for 2020; a360715 and
   a394598 for 2023-2024). They give hamlet and tổ, and distinguish river from canal.
2. **Emergency decisions quoted in news.** They give landmark-bounded reaches: from Trường TH A Bình Mỹ điểm
   phụ to điểm chính; Trung tâm Y tế Châu Phú to BV Huỳnh Trung Dũng; bến đò Cần Xây; bến đò An Long;
   kè Trung đoàn 9. These geocode well on Esri/Google imagery.
3. **Báo An Giang event reports.** Ferry landings, đình, factories and distances to roads, typically ≤ 200 m.
4. **The ODM 2018 CSV.** Weakest: district/ward-level text only.

## Reproduce

Scratch tools (not committed) are in `C:/Users/ASUS/AppData/Local/Temp/claude/c--Users-ASUS-Desktop-mekong-bankline-forecast/c00b7ed3-11a3-4d97-bbe8-cce86a3fd54e/scratchpad/tools/`: `tools/fx.py` (fetch and cache),
`tools/verify.py` (URL and name check), `tools/build.py` (rows → CSV), `tools/stats.py` (these counts). Same-site, same-year separate events carry a `#2`/`#3` suffix on `dedup_key`.
