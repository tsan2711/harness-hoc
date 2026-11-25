# G2 — Raster, overdraw, early-Z và Hidden Surface Removal

## Đố trước
16 quad full-screen 2048², fragment ~64 phép lặp, bật depth test. So với 1 lớp, 16 lớp tốn mấy lần trong mỗi trường hợp: (a) opaque gần→xa, (b) opaque **xa→gần**, (c) có `discard` (không bao giờ discard thật) gần→xa, (d) alpha blend xa→gần?

## Số đo (M2, ms GPU mỗi frame, median [min..max] của 5 đợt × 40 frame; load máy ~60 — [thô](../lab/results/gpu.txt))
| Fragment | 1 lớp | 16 lớp gần→xa | 16 lớp xa→gần |
|---|---|---|---|
| opaque | 4,6 [3,2..6,2] | 7,4 [7,3..10] | 10 [9..12] |
| `discard` trong code | 11 [9..13] | **38 [26..40]** | **53 [51..57]** |
| `discard` + `[[early_fragment_tests]]` | 8 [6..9] | **10 [8..12]** | 60 [49..62] |
| alpha blend | 8,7 [7..10] | 11 [8..13] | **57 [53..59]** |

Điều đa số đoán sai: opaque xa→gần **không** tốn 16×; `discard` tốn nhiều lần dù **không bao giờ kích hoạt**.
Hàng 3 là thí nghiệm bác bỏ: ép depth test chạy trước shader thì gần→xa trở lại rẻ (38 → 10), tức chi phí đến từ việc mất early-Z. Nhưng xa→gần vẫn 60: có `discard` thì HSR không cứu được. `early_fragment_tests` đổi ngữ nghĩa với shader discard thật (depth được ghi cả cho pixel bị bỏ), nên đây là phép đo, không phải cách sửa.

## Cơ chế
- Rasterizer xử lý tam giác theo **quad 2×2 pixel** (để tính đạo hàm chọn mip). Tam giác nhỏ hơn vài pixel ⇒ helper lane vô ích ⇒ chi phí fragment tăng dù diện tích không đổi.
- **Early-Z** (GPU IMR, desktop): loại fragment trước shader nếu đã bị che — chỉ hiệu quả khi vẽ gần→xa.
- **HSR** (Apple/PowerVR; Mali có FPK, Adreno có LRZ — cơ chế khác nhau, `[?]` chi tiết): trong tile, GPU xác định fragment nào thắng **rồi mới** shade ⇒ thứ tự opaque gần như không quan trọng.
- `discard`/alpha test: GPU không biết pixel có được ghi depth hay không trước khi chạy shader ⇒ không hoãn được ⇒ HSR/early-Z mất tác dụng. Chỉ cần **lệnh có mặt trong shader** là đủ.
- Blend: kết quả phụ thuộc lớp dưới ⇒ mọi lớp nhìn thấy đều phải shade. Hàng gần→xa trong bảng rẻ vì depth test loại các lớp sau — nhưng blend trong suốt đúng thì phải xa→gần.

## Chẩn đoán trong game (tình huống dựng)
**Triệu chứng:** thêm cỏ + hiệu ứng nổ, frame GPU từ 9 → 24 ms chỉ khi camera nhìn sát đất.
**Điều tra:** render scale 0,5 → thời gian giảm mạnh ⇒ fill. Tắt particle → còn 15 ms; đổi shader cỏ alpha-test sang opaque (nhìn xấu, chỉ để đo) → 10 ms.
**Quyết định:**
- Cỏ/lá: mesh bám sát hình (nhiều vertex hơn, ít pixel rỗng hơn) thay vì quad to + alpha test.
- Tách material: chỉ vật **thật sự** cần cutout dùng shader có `discard`; đừng để uber-shader có `discard` sau một nhánh keyword runtime.
- Particle: trim sprite, giới hạn số lớp che nhau, particle lớn render ở độ phân giải nửa.
- Thứ tự vẽ: opaque → alpha-tested → skybox → transparent.
- Depth prepass: đáng trên IMR khi fragment đắt; trên tile GPU có HSR thường là **trả thêm vertex để mua thứ đã có sẵn** — đo trước.

## Quy tắc quyết định
Ngân sách overdraw cho mobile: đo bằng GPU capture; nếu lớp trong suốt trung bình > ~2–3 trên vùng lớn của màn hình, xử lý nội dung trước khi xử lý shader.

## Bài tập
Thêm vào lab quad lưới tam giác 4×4 px và 1×1 px phủ cùng diện tích. Giả thuyết: 1×1 px tốn ≥ 2× ở fragment. Bác bỏ nếu < 1,3×.
