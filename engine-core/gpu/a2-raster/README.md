# A2 — Raster, early-Z, overdraw: vì sao "hiệu ứng nhỏ" làm sập fps

Chương mẫu. Mọi tình huống là **mô phỏng** trên project [`stress/`](../../stress), không phải sự cố của game nào.
Máy đo: Apple M2, Metal, 1280×720, Unity 6000.5.1f1, URP 17.5.0. Số đo chỉ đúng cho cấu hình này.

| Phần | File |
|---|---|
| 1. Vụ án + 2. Nền | file này |
| 3. Mổ source | [1-source.md](1-source.md) |
| 4. Điều tra (4 cuộc, có giả thuyết sai) | [2-dieu-tra.md](2-dieu-tra.md) |
| 5. Quyết định + 6. Thực hành | [3-quyet-dinh.md](3-quyet-dinh.md) |
| Đáp án (đọc sau) | [4-dap-an.md](4-dap-an.md) |

## 1. Vụ án (mô phỏng)

Màn boss phủ nhiều lớp lá dùng alpha cutout (`clip`) chồng lên nhau. Người làm art đổi lá từ opaque sang cutout, hình không đổi bao nhiêu, frame GPU tăng vọt. Mô phỏng tối giản: 16 quad phủ kín màn hình, fragment cố tình đắt (64 vòng lặp), cutout với ngưỡng âm nên **không pixel nào bị bỏ**: hình ra y hệt opaque.

| 16 lớp toàn màn hình (GPU ms, trung vị, run4 / run5) | |
|---|---|
| opaque | 16,9 / 14,8 |
| cutout, không bỏ pixel nào | 39,8 / 45,2 |
| 1 lớp cutout, để so | 16,6 / 16,2 |

**Dừng 30 giây**, viết ra trước khi đọc tiếp:
1. Cùng hình, cùng shader tô màu, vì sao chênh 2–3 lần?
2. Bạn sẽ thử sửa gì đầu tiên: sort gần→xa, depth priming, hay giảm shader?
3. Số nào sẽ khiến bạn bỏ giả thuyết của mình?

## 2. Nền: một fragment phải qua những gì

```
tam giác → raster (chia thành quad 2×2) → depth/stencil test sớm → fragment shader → depth test muộn → blend → ghi
```

- **Early-Z**: test depth trước khi chạy shader. Chỉ loại được fragment nằm sau thứ **đã ghi depth trước đó**, nên phụ thuộc thứ tự vẽ.
- **HSR** (hidden surface removal, có trên GPU tile-based như máy đo: `SystemInfo.hasHiddenSurfaceRemovalOnGPU == true`): gom hình trong tile, tìm fragment thắng rồi mới shade, nên opaque gần như không phụ thuộc thứ tự.
- **`clip`/`discard`** phá cả hai: chưa chạy shader thì chưa biết pixel có ghi depth không.
- **Blend** (trong suốt, additive): lớp nào cũng phải shade, không có gì để loại.
- **Quad**: GPU shade theo khối 2×2 để tính đạo hàm. Pixel trong khối nhưng ngoài tam giác vẫn chạy (helper lane).

Tính tay: một lớp toàn màn hình = 1280×720 = 921.600 fragment. 16 lớp không bị loại = 14,7 triệu fragment mỗi frame. Overdraw là **số lần shade trên mỗi pixel**, và chi phí fragment xấp xỉ `pixel × overdraw × giá một fragment`.
