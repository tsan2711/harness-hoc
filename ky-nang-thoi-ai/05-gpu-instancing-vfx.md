# Bài 5 — GPU: draw call, instancing, VFX Graph và compute

> Trục A · Sản phẩm: bầy 100k cánh hoa bằng VFX Graph hoặc compute + indirect, đo windowed.

## 1. Câu chuyện
Bạn vẽ 100k cánh hoa bằng 100k GameObject: CPU kiệt vì mỗi object tốn việc gửi lệnh. Bạn thử bake ma trận trên CPU rồi `RenderMeshInstanced` theo lô 1023 — vẫn tốn vì CPU tính và đẩy dữ liệu mỗi frame (tác giả đã loại hướng này). Cách khác: **để dữ liệu sống trên GPU**, CPU chỉ ra lệnh "vẽ N cái".

## 2. Dừng 30 giây
Mỗi frame CPU phải nói với GPU "vẽ cái này, ở đây". Nếu 100k cánh hoa đều di chuyển, ai tính vị trí mới — CPU rồi gửi 100k ma trận lên (băng thông + thời gian), hay GPU tự tính từ trạng thái của chính nó? Nghĩ về hướng dữ liệu chảy.

## 3. Khái niệm lõi
- **Draw call & batching**: chi phí chính là CPU chuẩn bị/gửi lệnh và đổi trạng thái. SRP Batcher giảm đổi trạng thái cho nhiều vật liệu cùng shader.
- **GPU instancing**: một lệnh, nhiều bản sao cùng mesh/material. `Graphics.RenderMeshIndirect` (và họ `DrawMeshInstancedIndirect` cũ) cho số lượng nằm trên GPU (buffer args).
- **Compute shader + GraphicsBuffer**: GPU mô phỏng chuyển động; shader vẽ đọc thẳng buffer. CPU không biết vị trí từng cánh hoa.
- **VFX Graph**: hệ hạt chạy hoàn toàn GPU, hàng triệu hạt, nút kéo thả; bù lại khó đọc kết quả ngược về logic game, ít kiểm soát tương tác từng hạt.
- **Overdraw & băng thông**: nhiều cánh hoa trong suốt chồng nhau = fill-rate. Mobile dùng kiến trúc tile-based (Apple GPU, Mali, Adreno), rất nhạy với overdraw và blending.
- **Đọc GPU về CPU** (readback) đắt và trễ vài frame; tránh nếu có thể.
- **Nền tảng**: Windows (D3D11/12, Vulkan), macOS/iOS (Metal), Android (Vulkan/GLES). Compute cần hỗ trợ; kiểm danh sách thiết bị mục tiêu.
- **Công cụ đo**: Unity Profiler + Frame Debugger; RenderDoc (Windows/Linux), Xcode GPU Capture (Metal). **Phải đo windowed**, không batchmode.

## 4. Các cấu trúc và đánh đổi
| Cách | Ưu | Nhược |
|---|---|---|
| GameObject + MeshRenderer | Dễ | CPU quá tải ở số lượng lớn |
| CPU bake ma trận + instancing theo lô | Dễ hiểu | CPU tính + đẩy mỗi frame (đã loại) |
| Compute + Indirect | Linh hoạt, tuỳ biến logic | Viết shader, khó debug |
| VFX Graph | Nhanh làm, hàng triệu hạt | Logic game khó móc vào; ít điều khiển từng phần tử |
| Entities Graphics (ECS) | Gắn dữ liệu ECS | Phụ thuộc DOTS stack |

## 5. Scale
- 1k–10k: gần như cách nào cũng được.
- 100k: GPU-driven bắt đầu cần thiết.
- 1M: tối ưu fill-rate, LOD (đổi cánh hoa xa thành điểm), culling trên GPU.
- Mobile: giảm một bậc số lượng, giảm overdraw trước.

## 6. Sản phẩm
1. Chọn **một** hướng (khuyến nghị VFX Graph nếu muốn nhanh; compute + indirect nếu cần logic riêng/tương tác).
2. Dựng bầy 100k cánh hoa chuyển động đơn giản (gió/xoáy).
3. Đo windowed (`kit unity test --windowed`): ms CPU, ms GPU, draw call, SetPass. Ghi bảng cho 10k / 100k / 500k.
4. Mở Frame Debugger xác nhận số draw call như dự đoán. Nếu có Mac: chụp Xcode GPU Capture.
5. Ghi vào `log.md`: nút cổ chai là CPU, GPU hay fill-rate? bằng chứng nào?
- Theo luật repo: chỉ chạy lượt đo ở cuối mảng; giữa chừng `kit compile`.

## 7. Tự kiểm
- Vì sao Indirect nhanh hơn bake ma trận CPU dù cùng "instancing"?
- Khi nào VFX Graph không đủ?
- Fill-rate là gì và vì sao mobile nhạy hơn?

## 8. Đọc thêm
Tài liệu Unity: VFX Graph, GraphicsBuffer, RenderMeshIndirect; "GPU-driven rendering" (các bài GDC của Ubisoft/Frostbite); Apple "Metal Best Practices".
