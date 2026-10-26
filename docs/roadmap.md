# Lộ trình bài 3: Dự báo lùi bờ sông có độ bất định đã kiểm chứng, và độ nhạy theo nguồn nhãn sạt lở, ĐBSCL

Lập ngày 21/10/2026, sửa cùng ngày theo báo cáo tính mới ([reports/Tính mới đề tài sạt lở.md](../reports/Tính%20mới%20đề%20tài%20sạt%20lở.md)). Máy: chỉ có CPU i5-12500H, không có GPU rời. Tính toán trên Google Earth Engine (project `mekong-bankline`, gói Community, đã đăng ký và kết nối Python).

> Lưu ý trung thực: hướng này liên quan thấp tới PhD cognitive robotics (1/5). Phần chuyển giao được là dự báo không gian–thời gian, độ bất định đã hiệu chỉnh (conformal) và tư duy kiểm định nhãn. Mục 6 có một nhánh mở rộng sang robotics.

## 1. Câu hỏi và ba đóng góp (đã thu hẹp sau kiểm tra tính mới)

**Tên tạm:** *Distribution-free, coverage-verified forecasts of riverbank retreat in the Vietnamese Mekong Delta, and the sensitivity of erosion-susceptibility evaluation to label source*

1. **Dự báo lùi bờ 1–3 năm theo transect, có khoảng tin cậy conformal được kiểm chứng độ phủ** theo từng đoạn sông và khi điều kiện thay đổi. Đây là đóng góp chính.
   - Còn trống trong phạm vi đã tìm: chưa thấy conformal cho bờ sông, bờ biển hay dịch chuyển lòng sông; chưa thấy ai đo độ phủ thực tế của các sản phẩm xác suất hiện có.
   - Chỉ được nhận "đầu tiên" về miền ứng dụng. Phải định vị so với Auer et al. 2024 (HESS, conformal cho lưu lượng, độ phủ theo lưu vực và khi phân phối thay đổi), GeoConformal (Lou et al. 2025), Singh et al. 2024 và CPTC 2025.
   - Không được viết "chưa có dự báo xác suất": CEGIS Bangladesh dự báo theo xác suất 30/50/70% từ 2004; Noh et al. 2024 (ESurf) có bản đồ rủi ro Bayesian; CoSMoS-COAST có dải dự báo. Điểm khác của bài: các sản phẩm đó chưa ai kiểm tra độ phủ.
   - Ở ĐBSCL, các dự báo trước đều tất định: ISPRS 2010 và bản journal 2011 (hồi quy tuyến tính trên transect DSAS), và mô phỏng TELEMAC của SIWRR 2024.
2. **Độ nhạy của việc đánh giá bản đồ nguy cơ theo nguồn nhãn:** cùng một mô hình, chấm bằng danh sách điểm báo cáo chính thức và bằng nhãn lùi bờ đo từ vệ tinh, rồi biểu diễn mức chênh AUC theo khoảng cách tới khu dân cư và đường sá.
   - Khái niệm đã có ở trượt lở và mô hình phân bố loài (Steger et al. 2017, 2021; Stanley & Kirschbaum 2017; Bornaetxea et al. 2023; Phillips et al. 2009; Hijmans 2012). Phần mới là phép so sánh cặp đầu tiên cho bờ sông.
   - Viết là "label-source sensitivity", không viết "nhãn báo cáo sai". Nhãn vệ tinh cũng có thiên lệch riêng.
   - Đối thủ cùng vùng: Nguyen et al. 2025 (*Physical Geography*, gộp 95 điểm khảo sát/báo cáo với 272 điểm Landsat mà không so sánh hai nguồn, GB AUC 0,85); Bui et al. 2026 (255 điểm đã ghi nhận); Binh et al. 2024 (sông Hàm Luông).
3. **Bộ kiểm kê điểm sạt lở cấp điểm, công khai, tải được** cho sông Tiền và sông Hậu ở An Giang và Đồng Tháp (theo địa giới trước 2025), có định nghĩa đơn vị nhất quán, ngày theo năm, nguồn gốc và sai số vị trí cho từng điểm.
   - Đã có các tập không công khai: WebGIS của Tổng cục PCTT ra mắt 6/2018 (562 điểm, máy chủ không phản hồi ngày 21/10/2026), 255 điểm của Bui et al. 2026, 248 vị trí của Bui & Tran 2023.
   - Số liệu chính thức trộn "điểm", "đoạn" và "vụ", trộn sông chính với kênh rạch. Ví dụ 585 điểm, 741 km "tính đến 2022", trong đó 87 điểm "đặc biệt nguy hiểm" ([VnExpress 15/8/2023](https://vnexpress.net/dong-mekong-gian-du-4634044.html)).

**Giả thuyết:**
- **H1:** Mô hình có biến phụ trợ cho sai số thấp hơn ngoại suy tuyến tính (EPR/LRR) ở tầm dự báo đã chọn, *hoặc* không thấp hơn. Kết quả nào cũng báo cáo.
- **H2:** Conformal giữ độ phủ 90% ± 3 điểm phần trăm khi gộp; khi tách theo đoạn sông và qua các giai đoạn thay đổi đã ghi nhận (Vàm Nao sau 2012, đào sâu đáy gần Mỹ Thuận 2014–2017), độ phủ của split conformal có thể hụt, còn bản Mondrian hoặc ACI thì giữ được. Khoảng Gauss phủ thiếu.
- **H3:** Mức chênh AUC giữa hai nguồn nhãn lớn hơn mức do gom cụm không gian gây ra (kiểm bằng cAUC và CV theo khối), và tăng theo độ gần khu dân cư và đường sá, sau khi đã kiểm tra hiệu ứng vật lý thật. **Làm ở cấp đoạn sông** (đơn vị 2–5 km): đoạn được tỉnh báo cáo hoặc cảnh báo so với đoạn lùi bờ đo từ vệ tinh, vì nguồn công khai chỉ đủ chi tiết tới cấp xã/đoạn (cổng G3).

**Không nằm trong phạm vi:** xác định nguyên nhân sạt lở. Bài chỉ phân tích các yếu tố liên quan trong phần thảo luận. Tác động của kè để cho bài sau.

## 2. Dữ liệu (tất cả miễn phí)

| Thành phần | Nguồn | Ghi chú |
|---|---|---|
| Mặt nạ nước, đường bờ | Landsat 5/7/8/9 C2 L2 (2000–2024), Sentinel-2 SR (2017–2024), ghép mùa khô tháng 1–4 trên GEE | JRC GSW v1.4 chỉ tới 2021, chỉ dùng để đối chiếu |
| Ảnh nét để kiểm sai số | Esri World Imagery Wayback, Google Earth Pro | NICFI đã kết thúc 23/1/2025 |
| Nhãn báo cáo | Quyết định công bố tình huống khẩn cấp (cổng tỉnh, thuvienphapluat), báo chí, CSV 55 vị trí trên ODM (địa chỉ dạng văn bản) | Bộ ODM Đồng Tháp 2016–2019 chỉ có số tổng theo xã |
| Mực nước | MRC, trạm Tân Châu 019803: đo thủ công 1979 tới nay, telemetry 15 phút từ 2010 | MRC không có lưu lượng của Tân Châu. Chưa gửi yêu cầu; chỉ cần ở bước kiểm tra mùa khô |
| Lưu lượng (tùy chọn) | Tân Châu theo giờ 2005–2015 (data.gov.uk), theo tháng 1995–2016 (GFZ) | Không phủ tới 2024 |
| Dân cư, đường sá | OSM, WorldPop, GHSL | |
| Lùi bờ toàn cầu để đối chiếu | Langhorst & Pavelsky 2023, JGR Earth Surface, doi:10.1029/2022JF006774 (Zenodo 10.5281/zenodo.7045021) | Một tốc độ trung bình 2001→2019 cho mỗi đoạn sông, không có chuỗi theo năm |
| Mô hình | EPR/LRR, Gradient Boosting, Gaussian Process; conformal bằng MAPIE | Không cần GPU |

## 3. Lộ trình (bắt đầu thứ Hai 26/10/2026)

Cột "Giờ của bạn" là ước lượng thô sau khi đã tự động hóa phần lặp lại. Máy chạy các bước xử lý ảnh, mô hình, hình và bảng.

| Giai đoạn | Thời gian | Giờ của bạn | Việc | Cổng kiểm tra |
|---|---|---|---|---|
| **P0 Thử nghiệm** | 26/10–8/11 | ~10 | Lấy toàn văn Nguyen et al. 2025 qua thư viện UEH; chạy các truy vấn Google Scholar và quét danh sách cited-by của Steger 2017/2021 và Phillips 2009. Chạy thử đoạn Sa Đéc–Cao Lãnh: mặt nạ nước, đường bờ, transect 100 m. Đo sai số đường bờ bằng ảnh nét và các đoạn có kè. So dự báo 2020 của ISPRS 2010 với thực tế (hình mở đầu). Đếm điểm báo cáo trên sông chính ở An Giang và Đồng Tháp. | **G1:** Nguyen 2025 chưa so sánh hai nguồn nhãn (nếu đã có, bỏ H3, bài còn H1+H2). **G2:** chọn tầm dự báo theo sai số đo (1 năm nếu sai số nhỏ hơn mức lùi ở phần lớn transect, nếu không thì 3–5 năm; nếu cả 3–5 năm cũng không thấy tín hiệu thì dừng). **G3:** có ít nhất 50 điểm báo cáo. **Kết quả (22/10):** G1 qua theo abstract; G2 qua (sai số 12–20 m so với ảnh nét, khớp diện tích sạt lở của SIWRR 2022, chọn tầm 3–5 năm); G3 chỉ 32 điểm cấp ấp nhưng 78 điểm/đoạn cấp xã → H3 làm ở cấp đoạn sông, không xin danh sách chính thức. |
| **P1 Dữ liệu** | 9/11–6/12 | ~15 | Đường bờ toàn tuyến sông Tiền và sông Hậu; nhãn vệ tinh; bộ kiểm kê bán tự động (máy tìm, đọc và định vị; bạn duyệt từng điểm); biến phụ trợ. **Đóng băng protocol** (git tag) trước khi chạy dự báo: tầm dự báo, cách chia, các phép kiểm, ngưỡng. | Protocol đã commit và tag |
| **P2 Mô hình** | 7/12–3/1 | ~5 | Huấn luyện tới 2018, dự báo 2019–2024; CV theo khối không gian; conformal (split, CQR, Mondrian theo đoạn, ACI); H3 với cAUC, chia theo khoảng cách, kiểm tra hiệu ứng vật lý. | Kết quả H1–H3 có khoảng tin cậy bootstrap theo khối |
| **P3 Độ bền** | 4/1–17/1 | ~3 | Kiểm lại bằng Sentinel-2 10 m; độ nhạy theo sai số tọa độ (100–500 m, theo Steger 2016); công bố bộ kiểm kê và code lên Zenodo; **bản đồ web tương tác** (chủ đề tài đề nghị 26/10): đường bờ từng năm, tốc độ lùi, nhãn vệ tinh, điểm kiểm kê kèm nguồn, dự báo kèm khoảng tin cậy; trang tĩnh, link đặt trong Data availability. | Kết luận không đổi |
| **P4 Viết bài** | 18/1–21/2 | ~30 | Tôi viết bản nháp, bạn sửa, kiểm từng con số và quyết định cách khai báo dùng AI. Gửi giảng viên. Đăng EarthArXiv khi nộp. Nộp khoảng cuối tháng 2/2027 (trừ hao Tết). | Giảng viên đã duyệt |

**Tiêu chí đóng P0** (chỉ sang P1 khi mọi mục có kết quả và không mục nào đỏ):
1. G1: đọc toàn văn Nguyen et al. 2025; tìm Google Scholar và quét danh sách cited-by của Steger 2017/2021, Phillips 2009 (chủ đề tài: khoảng 1 giờ).
2. Thuật toán chạy ổn trên ít nhất 3 đoạn: Sa Đéc–Cao Lãnh (xong), một đoạn sông Hậu (Long Xuyên), một đoạn hạ lưu sông Tiền (Mỹ Thuận); tỷ lệ transect ổn định và sai số so với điểm bấm tay không kém đoạn đầu.
3. Không có lệch hệ thống giữa các thế hệ vệ tinh (Landsat 5/7 so với 8/9; 8 so với 9) đủ lớn để tạo xu hướng giả, hoặc có hiệu chỉnh.
4. Độ lặp lại đo trực tiếp bằng hai ảnh ghép độc lập trong cùng năm; độ nhạy theo khung thời gian ghép ảnh (tháng 1–3 so với 2–4) đã biết.
5. Sai số kiểm cả ở transect bị đánh dấu không ổn định và ở sông Hậu (khoảng 15 điểm bấm thêm).
Dời có chủ đích: so dự báo ISPRS 2010 với thực tế chuyển sang P3 (hình minh họa, không phải cổng).

**Trạng thái (22/10, thuật toán cuối của P0):**
1. ✅ Scholar + quét cited-by xong (`results/p0/g1_scholar_check.md`): không thấy conformal cho bờ sông/bờ biển, không thấy so sánh nhãn báo cáo–vệ tinh cho bờ sông. ✅ Toàn văn Nguyen 2025 đã đọc (22/10), xem dưới.
2. ✅ Ba đoạn: transect tuyến tính 80% / 89% / 78%; sai số so với điểm bấm (transect ổn định) RMSE 37 m (Sa Đéc, 3 điểm nhiều mép kéo lên) / 23 m (Long Xuyên) / 12 m (Mỹ Thuận). Sửa trong P0: kẹp MNDWI về [-1, 1] (Otsu hỏng; Long Xuyên 2008 được cứu), lùi qua mương bị gộp vào đất liền (hết transect bị kẹt), cù lao > 1 km² tính là đất liền, nhảy-trở-lại (spike) bị loại còn đổi bậc (step) được giữ và đánh dấu.
3. ✅ Không lệch hệ thống giữa vệ tinh (L7–L8 −0,2 m; L8–L9 −0,2 m; L5–L7 −1,0 m), không cần hiệu chỉnh (`results/p0/sadec_caolanh_sensor_check.md`).
4. ✅ Độ lặp lại 3,1 m mỗi ảnh ghép; khung tháng 1–3 so với 2–4 lệch khoảng 1 m.
5. ✅ Transect từng bị đánh dấu: RMSE 20 m (5 điểm); sông Hậu: 23 m (6 điểm).
Còn ghi nhận: 3 điểm nhiều mép ở Sa Đéc (T303R, T326L, T410R) lệch khoảng 100 m; quy ước cù lao (bờ cù lao đối mặt sông chính được đo, bờ đất liền dọc lạch phụ sau cù lao thì không) - quyết ở P1. SIWRR: −106,3 so với −106 ha.
**P0 đóng ngày 22/10** (chủ đề tài đồng ý). Toàn văn Nguyen 2025 đã đọc 22/10: nhãn gộp hai nguồn (95 khảo sát/báo cáo + 272 Landsat), không so sánh, không chia khối không gian, không dự báo theo thời gian → G1 qua; H3 trích bài này như ví dụ gộp nhãn chưa kiểm tra (`results/p0/g1_scholar_check.md`). Nguồn mới cho bộ kiểm kê: bản đồ sạt lở của Bộ NN&PTNT (satlov2.vndss.com).

**Trạng thái P1 (22/10):**
- Phạm vi (chủ đề tài chọn): sông Tiền từ biên giới tới cầu Mỹ Thuận, sông Hậu từ biên giới tới cầu Cần Thơ. Đường tâm thô từ JRC (đường đi rẻ nhất qua lòng sông rộng), 15 ô 30 km chồng nhau (`src/river_tiles.py`, `data/tiles.json`); trong mỗi ô, phần gần sông kia hơn bị bỏ (tách hai sông ở Vàm Nao). Thuật toán P0 giữ nguyên (đầu ra Mỹ Thuận trùng từng byte).
- Ghép (`src/stitch.py`), chỉ phần thuộc Việt Nam (ranh giới LSIB 2017: sông Tiền vào Việt Nam ở km 4,6, sông Hậu ở km 8,5): sông Tiền 1.141 transect trên 127 km (85% tuyến tính), sông Hậu 1.360 transect trên 146 km (95% tuyến tính). Bờ trái/phải theo hướng xuôi dòng.
- Kiểm chéo với P0 (`results/p1/tile_check.md`): lệch vị trí trung vị 0,9–5,7 m, lệch tốc độ 0,05–0,23 m/năm; RMSE so với điểm bấm 34 / 22 / 12 m (P0: 37 / 25 / 12 m).
- Sông Hậu biên giới → Châu Đốc (rộng trung vị 180–210 m, ~20 điểm báo cáo ở An Phú): chủ đề tài chọn **chế độ sông hẹp** (22/10) cho các ô thượng nguồn Châu Đốc (`narrow_until_m`): lọc kênh ~90 m thay vì ~150 m, không dùng lõi sông mở, làm trơn đường tâm 15 px, chỉ xét nước trong 1 km quanh đường tâm thô. Trên đoạn chồng dưới Châu Đốc, chế độ hẹp so với chế độ thường: lệch trung vị 0,0 m, |lệch| trung vị 3,7 m, 90% ≤ 15 m. 15 điểm bấm tay (`results/p1/hau_accuracy.md`): 13 điểm ổn định RMSE 30 m, trung vị |sai số| 13 m (bờ ổn định 13 m; điểm nóng 51 m, n = 4); lệch lớn ở khúc cua gắt, cửa kênh và cồn sát Châu Đốc (T90L, T245R, T267R) → đạt theo chuẩn P0 (không kém Sa Đéc 37 m), giữ đoạn hẹp.
- Đoạn rộng mới (ngoài ba đoạn P0), 16 điểm bấm (`results/p1/{tien,hau}_accuracy.md`): sông Tiền 8 điểm, trung vị |sai số| 7 m, RMSE 37 m do một điểm (T417L, −100 m: vật thể/đất tạm sát bờ chỉ có năm 2021–2022, chuỗi các năm khác ổn định; Theil–Sen không bị ảnh hưởng); sông Hậu 8 điểm, RMSE 16 m. Toàn bộ điểm bấm so với sản phẩm cuối (đã ghép): Tiền RMSE 33 m (n = 55), Hậu rộng 19 m (n = 12), Hậu hẹp 30 m (n = 13) → đạt chuẩn P0. Phần đường bờ của P1 xong.
- Bộ kiểm kê (bước 4, phạm vi An Giang + Đồng Tháp mới, chủ đề tài chọn 22/10): G3 158 dòng + 23 dòng mới (Tiền Giang cũ 4, Đồng Tháp 19; 23/23 câu trích kiểm lại bằng `src/inventory_verify.py`) + 9 điểm ODV/Bộ NN&PTNT có tọa độ (CC-BY-SA). Ranh giới xã trước 2025: Kontur/OSM (ODbL, ghi công khi công bố). `src/reach_units.py` gán xã cho 5.132 điểm bờ (trong phạm vi: 4.322 điểm, 244 đơn vị 2 km, 109 xã); `src/inventory_build.py` → `data/hotspots/inventory_draft.csv`: 133 dòng nằm trên bờ đã đo, 15 dòng ở xã có bờ chưa đo (12 sau cù lao trên sông Tiền), 3 chưa khớp tên xã, 36 ngoài phạm vi (kênh, Vàm Nao, ngoài 2000–2024). Bản đồ sạt lở Bộ NN&PTNT đã ngừng; VNDMS cần tài khoản.
- Sửa: cắt biên giới theo từng điểm bờ (điểm bờ không thuộc xã Việt Nam thì loại), không theo đường tâm, vì sông Hậu ở An Phú là sông biên giới.
- Trước khi đóng băng protocol: quyết quy ước cù lao (12 dòng báo cáo nằm trên bờ đất liền sau cù lao, chủ yếu nhánh tây sông Tiền Phú Tân–Chợ Mới).
- Hình bài báo (`src/figures.py` → `figures/`, PNG 300 dpi + SVG): vùng nghiên cứu, ví dụ phương pháp, tốc độ thay đổi bờ toàn tuyến, kiểm định.

**Cập nhật P1 (25/10): quy ước cù lao (B) làm theo quy tắc, không chọn tay.**
- Bốn nhánh chọn tay (24/10) bị thay: chúng được chọn theo chỗ có điểm báo cáo (làm lệch tập đơn vị của H3), bỏ sót cù lao Ông Hổ, và b1/b3b có 53%/71% chuỗi "đổi bậc" (chế độ sông hẹp không hợp nhánh rộng 400–600 m).
- Quy tắc mới (`src/river_tiles.py`): mọi cù lao 1–150 km² là lỗ trong hệ thống sông nối liền (JRC ≥ 50%) → 11 cù lao (Tiền 7, Hậu 4), mỗi cù lao một ô ảnh. `banklines.island_geometry`: đường giữa các lạch quanh đảo (đường trung tuyến giữa đảo và mọi vùng đất khác), đo hai phía: I = bờ cù lao, O = bờ bên kia của lạch. Cù lao dính đất liền qua lạch < ~90 m thì cắt theo đường viền JRC. Bờ trùng bờ dòng chính (< 150 m) bị loại trong `reach_units.py`. Đầu ra P0 trùng từng byte.
- 11 cù lao: 2.663 bờ-transect có xu hướng (82% tuyến tính); "đổi bậc" nhiều ở cù lao gần biên giới (bồi lớn) và Long Khánh (lạch nhỏ bị bồi lấp) là thay đổi thật.
- units.csv: trong phạm vi 6.641 điểm bờ, 400 đơn vị 2 km, 179 đơn vị 5 km, 125 xã. Inventory: 144 dòng trên bờ đã đo, 4 chưa có bờ (Long Bình trên sông Bình Di; 2 điểm ODV xa bờ; Bình Thạnh không rõ sông), 3 chưa khớp xã, 36 ngoài phạm vi.
- Sai số bờ cù lao (12 điểm bấm, `results/p1/islands_accuracy.md`): RMSE 14 m, trung vị |sai số| 9 m (n = 11; 1 điểm rơi vào lạch hẹp hơn bộ lọc kênh, nay là "không đo được"). Sửa chung: bờ nằm ngay tại điểm đầu transect = đo hỏng (bỏ 1.448 dòng rải rác ở sông Hậu hẹp, 5% dòng cù lao; P0 và sông Tiền không đổi).
- Chủ đề tài duyệt xong inventory 26/10 (151 dòng): giữ 141, trùng 8, loại 1, chưa chắc 1; 124 dòng dùng được cho nhãn (`data/hotspots/inventory.csv`, `src/inventory_final.py`).
- 26/10: nhãn vệ tinh (`src/sat_labels.py`; nhãn chính: 75% điểm bờ của đơn vị lùi ≥ 20 m 2014→2023, 47/352 đơn vị) và biến phụ trợ (`src/covariates.py`) xong. Sửa hai lỗi: nhãn I/O của bờ cù lao bị đảo ở cả 11 cù lao (số đo không đổi); chế độ sông hẹp loại bờ xa hơn 1 km. Bản nháp protocol: `docs/protocol.md`.
- 26/10: chủ đề tài duyệt toàn bộ đề xuất D1–D8; protocol khóa (tag `protocol-v1`). **P1 xong.** Tiếp: P2.

**Tạp chí** (SJR 2025, đều Q1; giá lấy từ danh sách APC của Elsevier ngày 5/10/2026):
- **Chính: NHESS** (SJR 1,418). Hợp nhất với câu chuyện độ phủ và nguồn nhãn của bản đồ nguy cơ. Phí 1.800 €, được miễn nếu Việt Nam thuộc Research4Life; phải xác nhận trên research4life.org trước khi nộp.
- **Dự phòng 1: Geomorphology** (SJR 1,003). Đăng miễn phí theo đường subscription.
- **Dự phòng 2: IJAEOG** (SJR 2,177). Chỉ có open access, 3.670 USD.
- **Tránh:** Environmental Modelling & Software (dễ bị từ chối ngay nếu là bài ứng dụng không có đóng góp phần mềm), Remote Sensing of Environment (cần tiến bộ về phương pháp viễn thám).

## 4. Rủi ro và phương án

1. **Nhiều vụ sạt nhỏ hơn một pixel 30 m.** Cổng G2 quyết định tầm dự báo; dùng Sentinel-2 10 m cho 2017–2024; nói rõ giới hạn.
2. **H3 bị xem là đánh vào hình nộm** (đối thủ cùng vùng đã dùng nhãn vệ tinh). Ghi lại sản phẩm nào của Bộ, Tổng cục PCTT, SIWRR hay tỉnh thực sự dùng danh sách báo cáo; trình bày là độ nhạy theo nguồn nhãn.
3. **Gần khu dân cư thật sự lở nhiều hơn** (tải trọng nhà, sóng tàu). Kiểm tra lùi bờ đo từ vệ tinh theo khoảng cách tới khu dân cư trước khi diễn giải mức chênh AUC.
4. **Gắn tọa độ khó, địa giới đổi do sáp nhập 2025.** Dựng bảng đối chiếu xã cũ và xã mới; ghi sai số cho từng điểm và dùng trong phân tích độ nhạy.
5. **Mô hình có biến phụ trợ không thắng ngoại suy tuyến tính.** Báo cáo thẳng, vì đóng góp chính là độ phủ đã kiểm chứng.
6. **Bờ nhiều mép** (dải đất có ao hoặc đầm phía sau, cồn sát bờ, nhà sàn): khoảng 9% điểm kiểm (4/45). Đã chuyển sang quy tắc "mép đất liền" (đi từ đất liền ra, gặp nước đầu tiên; bỏ qua cồn, kênh dưới ~90 m không cắt đất liền): RMSE so với điểm bấm tay giảm từ 45 xuống 36 m, đo đủ 810/810 transect, vẫn khớp SIWRR (tổng −105 so với −106 ha). Còn lệch ở chỗ cồn dính bờ qua bãi bùn và transect xiên ở ngã ba kênh; transect nhảy chế độ vẫn được đánh dấu và loại.
7. **Có người công bố trước.** Cổng G1 ở P0; đăng EarthArXiv khi nộp. Theo dõi nhóm Bui/Tran (ĐH Mỏ–Địa chất) và nhóm Nguyen (ĐH KHTN Hà Nội, có đồng tác giả ở Đài KTTV An Giang).

## 5. Phân công

- **Bạn:** quyết định ở các cổng G1–G3 và khi đóng băng protocol; duyệt từng điểm của bộ kiểm kê; kiểm sai số đường bờ bằng mắt trên trang so sánh; sửa và chịu trách nhiệm bản thảo; liên lạc giảng viên.
- **Tự động (Claude và script):** xử lý ảnh trên GEE, transect, nhãn vệ tinh, tìm và trích văn bản cho bộ kiểm kê, mô hình, conformal, H3, bootstrap, hình, bảng, bản nháp.

## 6. Nhánh mở rộng sang robotics (để kể cho hồ sơ PhD)
Dùng độ bất định của dự báo để quyết định nên cho UAV hoặc USV khảo sát ở đâu với ngân sách có hạn (active sensing). Mô phỏng trên chính dữ liệu vệ tinh của bài. Để cho bài sau.

## 7. Gửi giảng viên
Chỉ gửi kết quả cuối (bản thảo), không gửi báo cáo giữa chừng.

## Liên quan tới các bài khác
- **Bài seed bias (PRL):** gói nộp gần xong. Còn sửa số trong abstract (0,040 so với 0,041), quyết định khai báo dùng AI theo chính sách Elsevier, và thầy ký form. Làm trong phiên CAAP.
- **Bài MAPPO (C&EE):** đang chờ phản biện.
- **Hướng UAV đo vết nứt:** gác lại, vì cần GPU và thiết bị.
