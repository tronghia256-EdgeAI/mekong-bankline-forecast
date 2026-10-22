# Independent check: eroded area, left bank of the Tien River at Binh Hang Trung

Reference: Đinh Quốc Phong, Lê Quản Quân, Lê Mạnh Hùng (2022). Xử lý khẩn cấp hạn chế sạt lở bờ tả sông Tiền
thuộc xã Bình Hàng Trung, huyện Cao Lãnh, tỉnh Đồng Tháp. Tạp chí KH&CN Thủy lợi 72, Table 1 (areas from
overlaid remote-sensing banklines 2003, 2006, 2014, 2017, 2021; exact reach extent not stated).
https://vawr.org.vn/Upload/BaibaoKH/dinh-quoc-phong-72-2022.pdf

Ours: `src/banklines.py` positions (mean of available years within ±1 yr), summed over transects
T255-315 (6 km, 100 m spacing), area = Σ retreat × 100 m. Sensitivity to the reach window (T260-310,
T250-330) changes each value by ≤ 3 ha.

| Period | SIWRR left bank (ha) | Ours left bank, T255-315 (ha) |
|---|---|---|
| 2003-2006 | -30.0 | -18.8 |
| 2006-2014 | -41.5 | -46.9 |
| 2014-2017 | -11.5 | -14.3 |
| 2017-2021 | -23.0 | -28.8 |
| Total | -106.0 | -108.8 |

Same temporal pattern (slowdown 2014-2017, re-acceleration 2017-2021) and near-identical total.
Right bank does not match (SIWRR +73 ha accretion in total; ours mixed): the right side of this reach
is the mid-channel bar / side-channel zone where bank identity changes (flagged unstable transects).
