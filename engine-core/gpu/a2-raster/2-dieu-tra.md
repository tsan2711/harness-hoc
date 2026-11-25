# 4. Điều tra

Cách đo: build macOS, chạy có cửa sổ, tắt vsync, `FrameTimingManager`, các cấu hình xen kẽ 3 vòng. Số ghi `run4 / run5` là trung vị GPU ms trong [`../../stress/results/`](../../stress/results). Máy **không rảnh** (load 12–66, xem `load.txt`), run5 có nhiều cấu hình chỉ đủ 1/3 số mẫu. Chênh dưới ~15% ở đây coi là nhiễu.

## Trước hết: kiểm xem phép đo có sống không
- Cảnh rỗng: 0,048 / 0,043 ms.
- Một đợt đo sau đó, `grid-64px-iter64` (vốn ~15 ms) ra 1 ms đồng hồ tường và 0 mẫu GPU. Player không render thật (nhiều khả năng cửa sổ bị che `[?]`). Cả đợt bị bỏ.
- Bài học: benchmark phải tự kiểm số mẫu và một cấu hình đã biết giá trị. Không kiểm thì "nhanh gấp 15 lần" trông như một tối ưu thành công.

## I1. "Sort gần→xa là cứu được cutout" — đúng một phần

**Giả thuyết:** URP bỏ sort (mục 3.1), bật lại `camera.opaqueSortMode = FrontToBack` thì cutout 16 lớp về gần giá 1 lớp.

**Bước 1: kiểm xem thứ tự có đổi thật không**, không cần công cụ ngoài. Tắt depth test (`ZTest Always`), tô mỗi lớp một màu, đọc pixel giữa màn: đó là lớp vẽ **sau cùng**. 8 lớp, 0 gần nhất, 7 xa nhất, khoảng cách giữa hai lớp là `dz` ([`probe.csv`](../../stress/results/run4/probe.csv)):

| chế độ | dz 0,1 | dz 2 | dz 20 | dz 100 |
|---|---|---|---|---|
| mặc định | 2 | 2 | 2 | 2 |
| ép xa→gần bằng `renderQueue` | 0 | 0 | 0 | 0 |
| `opaqueSortMode = FrontToBack` | 2 | 2 | **7** | **7** |

Đặt FrontToBack mà **không có gì đổi** khi các lớp cách nhau 2 đơn vị. Sort này lượng tử hoá khoảng cách (`QuantizedFrontToBack`) và bước lượng tử thô hơn nhiều so với trực giác: lớp cách 0,1 hay 2 đơn vị vẫn chung một nhóm. Kích thước bước nằm trong code native, mình không đọc được; chỉ quan sát được ngưỡng nằm đâu đó giữa hai cảnh thử.

Suýt sai ở đây: lần đo đầu dùng `dz = 0,1`, ra "sort không giúp gì". Kết luận đó vô giá trị vì sort chưa từng xảy ra.

**Bước 2: đo với sort đã kiểm là có tác dụng** (16 lớp cutout):

| | run4 | run5 |
|---|---|---|
| mặc định, dz 20 | 39,6 | 48,5 |
| FrontToBack, dz 20 | 33,9 | 37,5 |
| ép xa→gần (tệ nhất) | 60,5 | 63,4 |
| 1 lớp | 16,6 | 16,2 |

**Bác bỏ:** sort đúng chỉ bớt ~15–25%, vẫn hơn 2 lần giá 1 lớp. Giải thích khả dĩ `[?]`: lớp cutout chỉ ghi depth sau khi shade xong, nên các fragment chồng nhau trong cùng tile vẫn lọt qua test sớm. Số đo không phân biệt được cơ chế này với cơ chế khác.

Đối chứng: opaque 16 lớp ở mọi kiểu sort đều 15–18 ms. HSR làm đúng phần của nó.
Kiểm chéo: cutout xa→gần (60–63) ≈ additive 16 lớp (62–69), tức cả 16 lớp đều bị shade.

## I2. Depth priming

| 16 lớp | không priming | priming `Forced` |
|---|---|---|
| cutout, thứ tự xấu nhất | 60,5 / 63,4 | 20,9 / 19,9 |
| cutout, mặc định | 39,8 / 45,2 | 19,4 / 18,9 |
| cutout 1 lớp | 16,6 / 16,2 | 16,9 / 19,1 |
| opaque, xa→gần | 16,4 / 16,1 | 15,9 / 15,7 |

16 lớp cutout về gần giá 1 lớp và gần như không còn phụ thuộc thứ tự. Opaque không được lợi gì. Giá phải trả không lộ ra ở đây vì chỉ có 16 object: prepass là thêm một lượt vertex và draw call.

## I3. Đừng đọc một điểm, đọc độ dốc

Additive toàn màn hình, tăng số lớp:

| lớp | 1 | 2 | 4 | 8 | 16 | 32 |
|---|---|---|---|---|---|---|
| run4 | 16,1 | 21,0 | 30,8 | 36,6 | 55,9 | 100,4 |
| run5 | 19,4 | 23,6 | 31,2 | 42,3 | 61,8 | 100,7 |

Từ 8 đến 32 lớp: ~2,4–2,7 ms mỗi lớp. Ngoại suy về 0 lớp ra ~15 ms, trong khi cảnh rỗng đo được 0,05 ms. Vậy "1 lớp = 16 ms" **không** phải giá của một lớp. Phần chặn này chưa giải thích được; ứng viên là xung GPU thấp khi tải nhẹ `[?]`, chưa kiểm. Ngay cả độ dốc cũng chậm hơn nhiều so với ước lượng theo FLOPS lý thuyết, nên đừng mang số ms này sang máy khác.

**Áp vào glow.** Mô phỏng: 100–400 quad glow tròn. Thay quad bằng bát giác ngoại tiếp bớt được diện tích `1 − 8·tan(22,5°)/4 ≈ 17%`.

| | quad | bát giác | tiết kiệm |
|---|---|---|---|
| 100 glow, 128 vòng | 31,4 / 32,5 | 29,0 / 28,2 | 8% / 13% |
| 400 glow, 16 vòng | 26,7 / 26,8 | 25,3 / 24,2 | 5% / 10% |
| 400 glow, 16 vòng, render scale 0,5 | 10,9 / 10,5 | 10,0 / 10,6 | trong nhiễu |

**Dự đoán "nhanh hơn 17%" bị bác bỏ** nếu tính trên cả frame. 17% chỉ áp lên phần tỷ lệ với số fragment; trừ phần chặn ~15 ms thì mức tiết kiệm quan sát được khớp về cỡ độ lớn, nhưng nhiễu quá lớn để khẳng định hơn. Đòn mạnh hơn hẳn là giảm render scale (26,7 → 10,9), đồng thời đó là phép thử "có đang nghẽn fill không": giảm pixel mà frame time giảm mạnh thì đúng.

## I4. Tam giác 2 px và quad overshading — dự đoán sai, chưa rõ vì sao

Lưới phủ kín màn hình, đổi cỡ ô. Ô 2 px: 640×360×2 = 460.800 tam giác.

**Dự đoán:** mỗi ô 2×2 bị đường chéo cắt đôi, hai tam giác cùng chạm một quad ⇒ 8 lượt shade cho 4 pixel ⇒ phần fragment gấp đôi.

| GPU ms | 64 px | 8 px | 4 px | 2 px |
|---|---|---|---|---|
| 0 vòng (gần như chỉ hình học) | 5,7 / 3,7 | 6,2 / 4,5 | 6,4 / 5,0 | 13,2 / 12,6 |
| 256 vòng | 28,4 / 26,1 | 28,1 / 27,6 | 27,8 / 28,2 | 36,6 / 38,9 |
| 256 vòng + đạo hàm | 26,9 / 25,3 | 28,5 / 29,0 | 30,1 / 30,9 | 36,6 / 40,7 |

Từ 64 px xuống 2 px, bản 256 vòng tăng 8–13 ms, cỡ bằng phần tăng của bản 0 vòng (7–9 ms). Phần fragment không hề gấp đôi (nếu gấp đôi phải thêm khoảng hai chục ms).

**Giả thuyết cứu:** "shader không dùng đạo hàm nên GPU không chạy helper lane". Thêm `fwidth` lên **kết quả** của vòng lặp để ép chạy: vẫn không gấp đôi. **Cũng bị bác bỏ.**

Những gì chưa loại được: (a) GPU này xử lý quad không như mô hình sách vở; (b) vertex và fragment chồng thời gian trên GPU tile-based nên phép trừ hai hàng ở trên không hợp lệ; (c) variant đạo hàm không chạy trong run4/run5. Ảnh ở một đợt đo sau cho thấy variant có chạy (tô thêm xanh), nhưng đợt đó có số đo hỏng.

Kết luận được phép: **trong cấu hình này không đo được hình phạt 2×**. Không được phép: "quad overshading không tồn tại".
