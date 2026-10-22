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
   - Đối thủ cùng vùng: Nguyen et al. 2025 (*Physical Geography*, nhãn từ Landsat, GB AUC 0,85); Bui et al. 2026 (255 điểm đã ghi nhận); Binh et al. 2024 (sông Hàm Luông).
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
| **P3 Độ bền** | 4/1–17/1 | ~3 | Kiểm lại bằng Sentinel-2 10 m; độ nhạy theo sai số tọa độ (100–500 m, theo Steger 2016); công bố bộ kiểm kê và code lên Zenodo. | Kết luận không đổi |
| **P4 Viết bài** | 18/1–21/2 | ~30 | Tôi viết bản nháp, bạn sửa, kiểm từng con số và quyết định cách khai báo dùng AI. Gửi giảng viên. Đăng EarthArXiv khi nộp. Nộp khoảng cuối tháng 2/2027 (trừ hao Tết). | Giảng viên đã duyệt |

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
6. **Bờ nhiều mép** (dải đất có ao hoặc đầm phía sau, cồn sát bờ): khoảng 9% điểm kiểm (4/45) lệch tới khoảng 110 m. Đã thử quy tắc "đất liền đầu tiên tính từ lòng sông" (P0, 22/10): sửa được 2/4 điểm nhưng làm hỏng điểm khác và lệch khỏi số liệu SIWRR (2006–2014: −24 so với −41,5 ha), nên giữ quy tắc cũ; các transect nhảy chế độ được đánh dấu và loại. Xử lý lại ở P1 khi có thêm mẫu.
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
