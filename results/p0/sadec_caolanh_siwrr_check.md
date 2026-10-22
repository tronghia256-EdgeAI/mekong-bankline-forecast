# Independent check: eroded area, left bank of the Tien River at Binh Hang Trung

Reference: Đinh Quốc Phong, Lê Quản Quân, Lê Mạnh Hùng (2022). Xử lý khẩn cấp hạn chế sạt lở bờ tả sông Tiền
thuộc xã Bình Hàng Trung, huyện Cao Lãnh, tỉnh Đồng Tháp. Tạp chí KH&CN Thủy lợi 72, Table 1 (areas from
overlaid remote-sensing banklines 2003, 2006, 2014, 2017, 2021; exact reach extent not stated).
https://vawr.org.vn/Upload/BaibaoKH/dinh-quoc-phong-72-2022.pdf

Ours: `src/banklines.py` positions (mean of available years within ±1 yr), summed over transects
T255-315 (6 km, 100 m spacing), area = Σ retreat × 100 m. Sensitivity to the reach window (T260-310,
T250-330) changes each value by ≤ 3 ha.

| Period | SIWRR left bank (ha) | Ours, mainland-edge rule (adopted) | Ours, earlier outermost-water rule |
|---|---|---|---|
| 2003-2006 | -30.0 | -14.2 | -18.8 |
| 2006-2014 | -41.5 | -45.5 | -46.9 |
| 2014-2017 | -11.5 | -14.6 | -14.3 |
| 2017-2021 | -23.0 | -30.8 | -28.8 |
| Total | -106.0 | -105.1 | -108.8 |

Same temporal pattern (slowdown 2014-2017, re-acceleration 2017-2021) and near-identical total under
both bank rules. Right bank does not match (SIWRR +73 ha accretion in total; ours mixed): the right side
of this reach is the mid-channel bar / side-channel zone.

## Bank rule comparison against the owner's 45 hand-clicked sites (Esri Wayback, reviewed 2026-10-22)

The owner clicked "walking from the mainland, the first water". Error = ours - clicked (m).

| Rule | n | Bias | Median abs | RMSE | Multi-edge sites (n=4) RMSE |
|---|---|---|---|---|---|
| Outermost main-channel water seen from land (earlier) | 45 | -26.6 | 19.3 | 44.6 | 109.8 |
| Mainland edge: first mainland from the open river; islands skipped; canals < ~90 m do not cut the mainland; ponds filled (adopted) | 45 | -23.2 | 19.3 | 36.1 | 86.4 |

The adopted rule also measures all 810 transect-sides for >= 15 years (771 before) and leaves 88% free
of > 150 m jumps (83% before). It fixes T95L (-152 -> -28 m) and T352L (-140 -> -36 m) and worsens T410R
(-26 -> -101 m; an oblique transect at a canal junction).
