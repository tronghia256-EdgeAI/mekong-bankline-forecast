# Lộ trình bài 3: Dự báo lùi bờ sông có độ bất định và thiên lệch nhãn điểm sạt lở, ĐBSCL

Lập ngày 21/10/2026. Kết quả từ hội đồng nghiên cứu (6 nhóm độc lập). Máy: chỉ có CPU i5-12500H, không có GPU rời. Tính toán dùng Google Earth Engine, Colab và Kaggle miễn phí.

> Lưu ý trung thực: hướng này rất khả thi và có cơ hội Q1, nhưng **liên quan thấp tới PhD cognitive robotics** (1/5). Bạn đã chọn hướng này vì tác động cho ĐBSCL, và đó là một lựa chọn hợp lệ. Phần chuyển giao được sang robotics là: dự báo không gian–thời gian, độ bất định đã hiệu chỉnh (conformal), và tư duy kiểm định nhãn. Phần cuối có một nhánh mở rộng sang robotics.

## 1. Câu hỏi và ba đóng góp

**Tên tạm:** *Calibrated forecasting of riverbank retreat in the Vietnamese Mekong Delta, and how report-based hotspot labels bias erosion maps*

1. **Bộ kiểm kê điểm sạt lở có tọa độ cho sông Tiền và sông Hậu, công bố mở.**
   - Hiện chưa có danh sách chính thức nào gắn tọa độ. Cục Quản lý đê điều và PCTT chỉ công bố số tổng: 2023 có 585 điểm, dài 741 km, trong đó 87 điểm khẩn cấp ([SGGP](https://www.sggp.org.vn/dbscl-lai-nom-nop-lo-sat-lo-post684067.html)).
   - Nguồn để dựng bộ kiểm kê:
     - các quyết định công bố tình huống khẩn cấp của tỉnh, có địa chỉ cấp tổ/khóm/phường;
     - bộ dữ liệu sạt lở Đồng Tháp 2016–2019 trên Open Development Mekong, tải được dạng SHP/GeoJSON ([ODM](https://data.opendevelopmentmekong.net/lo/dataset/impacts-of-mekong-river-erosion-in-dong-thap-province));
     - WebGIS của Bộ NN&PTNT năm 2020 với 564 điểm, nếu tải được (UNVERIFIED).
   - Ghi kèm sai số vị trí cho từng điểm, ước khoảng 100–500 m.
   - Bạn đọc được văn bản tiếng Việt, đây là lợi thế mà nhóm nước ngoài không có.
2. **Dự báo lùi bờ 1–3 năm theo từng mặt cắt ngang (transect), có khoảng tin cậy đã hiệu chỉnh** bằng split conformal, đánh giá theo từng đoạn sông.
   - Bài dự báo gần nhất ở ĐBSCL là ngoại suy tuyến tính DSAS tại Sa Đéc/Hồng Ngự từ năm 2010, một con số cố định, không có độ bất định và không kiểm chứng ([ISPRS 2010](https://www.isprs.org/proceedings/XXXVIII/part8/pdf/W01OH3_20100308201836.pdf)).
   - Hội đồng không tìm thấy dự báo xác suất, cũng không thấy ai áp dụng conformal cho đường bờ hay bờ sông.
3. **Kiểm tra thiên lệch nhãn.**
   - Các bản đồ nguy cơ hiện nay kiểm chứng bằng điểm sạt lở được báo cáo (ví dụ [Binh et al. 2024](https://js.vnu.edu.vn/EES/article/view/5234), AUC 0,86).
   - Điểm được báo cáo thường nằm gần khu dân cư và đường sá. Bài sẽ đo xem điều đó thổi phồng AUC bao nhiêu so với nhãn lùi bờ đo từ vệ tinh.
   - Đây là chuyển phương pháp của văn liệu về thiên lệch kiểm kê trượt lở sang bờ sông, hội đồng chưa thấy ai làm. Nền tảng: [Steger et al. 2017](https://link.springer.com/article/10.1007/s10346-017-0820-0), [Steger et al. 2016](https://nhess.copernicus.org/articles/16/2729/2016/), [Stanley & Kirschbaum 2017](https://ntrs.nasa.gov/api/citations/20170007214/downloads/20170007214.pdf).

**Trực quan hóa:** một bản đồ web (GEE App, hoặc Leaflet đặt trên GitHub Pages) hiển thị dự báo kèm dải bất định cho từng transect và từng điểm sạt lở. Phần này chiếm khoảng 10% công sức. Nó tăng giá trị tái lập và phù hợp với tạp chí Environmental Modelling & Software, nhưng **một mình nó không đủ làm đóng góp Q1**.

**Giả thuyết:**
- **H1:** Mô hình có biến phụ trợ cho sai số lùi bờ thấp hơn ngoại suy tuyến tính (EPR/LR) ở tầm 1–3 năm, *hoặc* không thấp hơn. Kết quả nào cũng là một phát hiện, vì ở bài toán bờ biển, mô hình đơn giản từng thắng ML ([ShoreShop, Mao et al. 2025](https://pubs.usgs.gov/publication/70270366)).
- **H2:** Conformal giữ độ phủ 90% ± 3 điểm phần trăm khi tách theo đoạn sông, còn khoảng tin cậy Gauss thì phủ thiếu.
- **H3:** Nhãn dựa trên báo cáo làm AUC của mô hình nguy cơ cao hơn đáng kể so với nhãn đo từ vệ tinh, và mức chênh tăng theo độ gần khu dân cư và đường sá.

## 2. Dữ liệu và công cụ (tất cả miễn phí, chạy được trên CPU)

| Thành phần | Nguồn | Ghi chú |
|---|---|---|
| Ảnh vệ tinh và mặt nước | Landsat 5/7/8/9 (2000–2024) và Sentinel-2 (2016–2024), ghép ảnh mùa khô hằng năm trên GEE; JRC Global Surface Water | Dùng mùa khô để giảm ảnh hưởng của mực nước |
| Quota GEE | Gói Community: 150 EECU-giờ/tháng, cấp cho dự án phi thương mại, dành cả cho sinh viên. Vượt quota thì bị chạy chậm chứ không bị cắt. Phải xác minh lại hằng năm ([Google](https://developers.google.com/earth-engine/guides/noncommercial_tiers)) | Xuất dữ liệu sớm |
| Dữ liệu lùi bờ toàn cầu để đối chiếu | REAL ([ESSD 2025](https://essd.copernicus.org/articles/17/5615/2025/)) | Chỉ có trung bình theo thập kỷ, sông rộng trên 150 m |
| Biến phụ trợ | Lưu lượng Tân Châu (cổng dữ liệu MRC, điều kiện truy cập UNVERIFIED), độ cong lòng sông, bề rộng, tốc độ lùi bờ quá khứ, OSM roads, WorldPop | Dữ liệu khai thác cát không có công khai; ghi thành hạn chế của bài |
| Mô hình | EPR/LR theo transect, Gaussian Process, Gradient Boosting (CPU); ConvLSTM nhỏ (Colab, tùy chọn); conformal bằng MAPIE | Không cần GPU cho phần lõi |

## 3. Lộ trình (20 giờ/tuần, bắt đầu thứ Hai 26/10/2026)

| Giai đoạn | Thời gian | Giờ | Việc | Cổng kiểm tra |
|---|---|---|---|---|
| P0 Thử nghiệm | 26/10–8/11 | 40 | Đăng ký GEE phi thương mại. Tìm sâu tính mới trên Google Scholar và tạp chí Việt Nam (Khoa học Thủy lợi, ĐH Cần Thơ, vnjhm). Chạy thử đoạn Sa Đéc–Cao Lãnh: mặt nạ nước 2000–2024, trích đường bờ, transect cách nhau 100 m. Gắn tọa độ thử 20 điểm sạt lở. | Lùi bờ nhìn thấy rõ ở độ phân giải 30 m; 20 điểm có sai số ≤ 500 m; chưa có ai làm dự báo hiệu chỉnh |
| P1 Dữ liệu | 9/11–6/12 | 80 | Toàn tuyến sông Tiền và sông Hậu; bộ kiểm kê 100 điểm trở lên; biến phụ trợ. **Đóng băng protocol** (git tag) trước khi chạy dự báo | Protocol đã commit |
| P2 Mô hình | 7/12–3/1 | 80 | Huấn luyện tới 2018, dự báo 2019–2024; kiểm chứng chéo theo khối không gian; conformal; kiểm tra thiên lệch nhãn | Kết quả H1–H3 có khoảng tin cậy bootstrap |
| P3 Độ bền và bản đồ | 4/1–17/1 | 40 | Kiểm tra lại bằng Sentinel-2 10 m; độ nhạy theo sai số tọa độ; dựng bản đồ web | Kết luận không đổi |
| P4 Viết bài | 18/1–21/2 | 70 | Bản thảo (trừ hao Tết); nộp khoảng cuối tháng 2/2027 | Giảng viên đã duyệt |

**Tạp chí** (SJR 2025, lấy từ đoạn trích kết quả tìm kiếm; cần xác minh trên trình duyệt):
- **Chính:** Environmental Modelling & Software. SJR 1,344, Q1 ở 4 ngành, trong đó có **Computer Science: Software**. Có đường đăng miễn phí, hợp với phần bản đồ web.
- **Dự phòng 1:** Computers & Geosciences. SJR 1,033, Q1 Computers in Earth Sciences, đăng miễn phí.
- **Dự phòng 2:** IJAEOG, phù hợp nhất về chuyên môn. SJR 2,177, phản hồi đầu khoảng 3 ngày, khoảng 130 ngày tới chấp nhận, tỉ lệ nhận 14%. Nhưng là tạp chí open access, phải trả phí.
- **Tránh:** Ecological Informatics (thiên về sinh thái) và EAAI (chỉ nhận khi phương pháp thật sự mới).

## 4. Rủi ro và phương án

1. **Nhiều vụ sạt nhỏ hơn một pixel 30 m.** Dự báo nhắm vào lùi bờ dài hạn; dùng Sentinel-2 10 m cho giai đoạn 2016–2024; nói rõ giới hạn trong bài.
2. **Gắn tọa độ khó, địa giới bị đổi do sáp nhập 2025.** Ghi sai số cho từng điểm, và dùng chính sai số đó trong phân tích độ nhạy.
3. **Mô hình học sâu không thắng ngoại suy tuyến tính.** Báo cáo thẳng như một phát hiện, vì đóng góp chính là độ bất định đã hiệu chỉnh.
4. **Đường mép nước lệch theo mực nước.** Dùng ảnh ghép mùa khô và đối chiếu với lưu lượng.
5. **Có người công bố trước** (tính mới mới kiểm qua tìm kiếm sơ bộ). Cổng kiểm tra ở P0; đăng arXiv hoặc EarthArXiv khi nộp bài.

## 5. Nhánh mở rộng sang robotics (để kể cho hồ sơ PhD)
Có thể làm thêm một phần, hoặc thành bài sau: dùng độ bất định của dự báo để quyết định nên khảo sát UAV/USV ở đâu với ngân sách có hạn (active sensing / lấy mẫu theo thông tin). Phần này mô phỏng trên chính dữ liệu vệ tinh của bài, nối được câu chuyện "nhận thức có độ bất định dẫn tới hành động".

## 6. Lịch gửi giảng viên
- **~8/11:** kết quả cổng P0 và 1 trang mô tả hướng đi.
- **~3/1:** kết quả H1–H3.
- **~14/2:** bản thảo.

## Liên quan tới các bài khác
- **Bài seed bias (PRL):** gói nộp gần xong. Còn sửa số trong abstract (0,040 so với 0,041), quyết định khai báo dùng AI theo chính sách Elsevier, và thầy ký form. Làm trong phiên CAAP.
- **Bài MAPPO (C&EE):** đang chờ phản biện.
- **Hướng UAV đo vết nứt:** gác lại, vì cần GPU và thiết bị.
