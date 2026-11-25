# G3 — Tile-based GPU: load/store, bandwidth, ranh giới render pass

## Đố trước
16 draw full-screen blend trong **1** render pass, so với **16 pass** mỗi pass 1 draw (load/store). Cùng số fragment. Chênh bao nhiêu?

## Số đo (M2, 2048², median 5 đợt; load ~60 — [thô](../lab/results/gpu.txt))
| Attachment | 16 draw, 1 pass | 16 pass × 1 draw |
|---|---|---|
| chỉ màu | 52 ms | 212 ms |
| màu + depth, store `dontCare` | 58 | 219 |
| màu + depth load/store | 58 | 214 |
Cùng công shading, ngắt pass đắt gấp ~4×. Lần đo trước (cách đo khác, máy rảnh hơn) chỉ ~1,7× (54 → 90 ms): **hướng chắc chắn, hệ số thì không** — đo lại trên máy đích.
Điều **không** thấy: load/store depth không tạo khác biệt vượt nhiễu. Depth ở đây gần như đồng nhất (một mặt phẳng), nhiều khả năng nén rất tốt `[?]`; đừng suy ra depth luôn miễn phí.

**Bài học đo lường:** thiết kế đầu tiên (scissor 64×64, opaque) cho chênh ~0,3 ms và dẫn tới kết luận ngược. Thiết kế thứ hai lấy `end−start` từng command buffer khi gửi liên tiếp, và các buffer chồng pha nhau nên số phồng hàng chục lần. Kiểm phép đo trước khi tin nó.

## Cơ chế
- GPU tile-based chia màn hình thành ô nhỏ: pha 1 xử lý hình học và xếp tam giác vào tile; pha 2 shade từng tile trong **bộ nhớ on-chip** (nhanh, rẻ điện), xong mới ghi ra DRAM.
- Mỗi render pass: `loadAction` quyết định có đọc DRAM vào tile không (`load` = đọc; `clear`/`dontCare` = không), `storeAction` quyết định có ghi ra không.
- Ngắt pass = store toàn bộ attachment rồi load lại. Trên mobile, bandwidth còn là **nhiệt và pin**.
- MSAA trên tile GPU resolve được ngay trong tile (store = resolve, attachment MSAA `memoryless`) ⇒ rẻ hơn nhiều so với trực giác desktop. Depth không ai đọc lại ⇒ `dontCare`/`memoryless`.

## Thứ làm vỡ pass trong engine
Đọc texture màu/depth của frame hiện tại (distortion, soft particle, decal), post-effect nối chuỗi, đổi render target giữa chừng rồi quay lại, copy màu để làm hiệu ứng kính. Unity 6 URP dùng **RenderGraph** để gộp pass tương thích và suy ra load/store; một pass "không tương thích" ở giữa sẽ cắt chuỗi. Xem Render Graph Viewer để biết pass nào được gộp và vì sao không `[kiểm trên bản Unity đang dùng]`.

## Chẩn đoán (tình huống dựng)
**Triệu chứng:** thêm hiệu ứng gợn nước, GPU +6 ms trên điện thoại dù mặt nước chiếm 5 % màn hình.
**Điều tra:** capture (Xcode / AGI) → thấy pass chính bị cắt làm đôi, có store + load toàn màn hình và một blit copy màu.
**Bằng chứng:** chi phí không tỉ lệ với diện tích nước ⇒ không phải shading.
**Quyết định (theo thứ tự rẻ):** lấy màu từ bản downsample đã có; hoặc framebuffer fetch (đọc pixel hiện tại ngay trong tile — chỉ đúng khi không cần pixel lân cận); hoặc dời hiệu ứng để dùng chung điểm ngắt pass đã tồn tại.

## Quy tắc quyết định
Ước tính trước khi thêm pass: `byte = rộng × cao × (bpp) × (số lần load + store)` mỗi frame, nhân fps. Ví dụ 2400×1080 RGBA8: một cặp store+load ≈ 20 MB/frame ≈ 1,2 GB/s ở 60 fps (trần trên, chưa trừ nén).

## Bài tập
Thay quad phẳng bằng nhiều tam giác nhỏ có z ngẫu nhiên (depth khó nén) rồi đo lại ba hàng. Dự đoán trước hàng "depth load/store" tăng bao nhiêu.
