# G1 — Frame, bound và giá của một draw call

## Đố trước (ghi đáp án ra giấy)
1. 10.000 draw giống hệt vs 1 draw instanced 10.000: CPU **encode** chênh bao nhiêu lần?
2. Frame 22 ms, CPU main 8 ms, render thread 6 ms, GPU 21 ms. Giảm draw call có giúp không?
3. Hạ độ phân giải còn một nửa mà fps không đổi. Bạn loại được những nguyên nhân nào?

## Số đo (Metal thuần, M2, CPU encode, tốt nhất trong 10 lần)
| N | N draw (`setVertexBytes` + `draw`) | 1 draw instanced |
|---|---|---|
| 1.000 | 0,05–0,12 ms | ~0,002–0,007 ms |
| 10.000 | 0,5–1,2 ms (dao động theo tải máy) | ~0,003 ms |
Tức ~0,05–0,12 µs mỗi draw **khi không đổi state nào**. Đây chỉ là phần **record** trên Metal/M2 (không tính `endEncoding`/`commit`). **Không** phải sàn cho Android: GLES/Vulkan trên Mali/Adreno phải đo bằng marker render thread trong player. Trong engine, một "draw call" còn gồm culling, sort, bind material/buffer, kiểm state, đổi pipeline: đắt hơn nhiều lần và **phụ thuộc cái gì đổi giữa hai draw**, không phụ thuộc số draw đơn thuần.

## Cơ chế: một frame là pipeline nhiều tầng chạy lệch pha
`Main thread (game + cull) → Render thread (encode command) → GPU (thực thi) → Display (vsync)`
- GPU chạy **sau** CPU 1–3 frame (frames in flight). Thời gian frame ≈ **tầng chậm nhất**, không phải tổng. Latency input thì **là** tổng.
- Hai tầng chờ nhau qua fence/semaphore: thời gian "chờ" trong Profiler là triệu chứng, không phải nguyên nhân. Marker chờ present/GPU lớn ⇒ CPU rảnh, đang đợi GPU hoặc vsync.
- Đọc ngược từ GPU về CPU (`GetData` đồng bộ, đọc timestamp ngay) ⇒ xả pipeline, mất tính lệch pha. Dùng `AsyncGPUReadback`.

Đáp án 2: không. GPU 21 ms là tầng quyết định; draw call chủ yếu là chi phí CPU. (Ngoại lệ: draw đổi state làm vỡ khả năng gộp trên GPU.)

## Chẩn đoán trong game (tình huống dựng)
**Triệu chứng:** màn đông quái, 38 fps trên Android tầm trung; team đề nghị "giảm draw call".
1. Đo CPU main / render thread / GPU time trên **máy thật** (FrameTimingManager, hoặc AGI/Snapdragon Profiler/Xcode). Editor không đại diện.
2. Thí nghiệm bác bỏ, mỗi lần đổi **một** thứ:

| Đổi | fps tăng ⇒ nghẽn ở |
|---|---|
| render scale 0,5 | fragment/bandwidth (G2, G3) |
| mọi material → unlit 1 màu, giữ số draw | shading/texture |
| tắt nửa số renderer, giữ coverage | CPU submit hoặc vertex |
| mesh LOD thấp, giữ số draw | vertex/primitive |
| timeScale = 0 (giữ hình) | phần gameplay CPU, không phải render |
3. Đáp án 3: nửa độ phân giải không đổi fps ⇒ loại fragment ALU, fill, phần lớn bandwidth render target. **Không** loại vertex/binning, CPU, vsync cap (kiểm trước tiên), và các target **không scale theo render scale** (shadow map, UI, một số post-process).

## Quy tắc quyết định
- Tính ngân sách trước: 60 fps = 16,7 ms **cho tầng chậm nhất**; mobile chừa ≥ 20–30 % cho nhiệt (đo sau 10 phút chơi, không phải 30 giây đầu).
- Chỉ tối ưu draw call khi render thread là tầng chậm nhất. Thứ tự: bỏ vẽ (culling) → giảm đổi state (ít shader/variant) → gộp (instancing/SRP Batcher/BRG, G8).

## Bài tập (30 phút)
Sửa lab: thêm biến thể "đổi pipeline state mỗi draw" (2 PSO luân phiên). **Giả thuyết trước:** chậm hơn ≥ 2×. Bác bỏ nếu < 1,3×. Ghi kết quả vào `../log.md`.
