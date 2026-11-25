# Plan lại engine-core (2026-11-25) — đã duyệt

## Vì sao bản hiện tại nông
- 10 bài mà thư mục chỉ ~470 dòng: mỗi bài là một thẻ tóm tắt, không phải bài giảng.
- Ôm rộng quá, nên không chủ đề nào đi tới đáy.
- Số đo từ microbenchmark ngoài engine (Metal thuần, .NET CoreCLR), không phải trong Unity.
- "Use case" là tình huống một đoạn, không có đường điều tra, không có chỗ đoán sai.
- Hầu như không đọc source (URP, asm, shader đã biên dịch).

## Đổi cách làm
**1. Một project mẫu cho mọi chương** (`stress/`). Dựng hoàn toàn bằng code, build ra macOS, tự chạy các cấu hình và ghi CSV. Use case là tình huống mô phỏng trên project này: chạy lại được, không lộ code game riêng.

**2. Ít chương, mỗi chương nhiều phần.** Một chương là một thư mục:

| Phần | Nội dung |
|---|---|
| Vụ án | triệu chứng trên project mẫu, số đo ban đầu, bạn tự đặt giả thuyết |
| Nền | cơ chế từ gốc, có sơ đồ và phép tính tay |
| Mổ xẻ | source URP/engine, shader biên dịch, asm, kèm đường dẫn và phiên bản |
| Điều tra | từng bước đo, **kể cả giả thuyết sai**, tới khi sửa xong |
| Quyết định | các phương án, giá phải trả, ngưỡng vỡ, khác nhau giữa các kiến trúc GPU (theo tài liệu, ghi rõ là chưa đo) |
| Thực hành | bài tập sửa code, tiêu chí bác bỏ, đáp án ở file riêng |

**3. Điều kiện một chương được coi là xong**
- ≥ 2 cuộc điều tra trọn vẹn trên project mẫu, có artifact commit trong repo.
- ≥ 3 đoạn source hoặc output biên dịch được giải thích từng dòng.
- ≥ 1 giả thuyết bị số đo bác bỏ.
- Mọi con số trỏ về file kết quả thô; ghi load máy lúc đo.
- Reviewer (Opus, một agent) chấm ≥ 8/10 ở trình principal và không còn lỗi S1.
- Dài bao nhiêu tuỳ nội dung. Số dòng không phải tiêu chí.

## Nội dung

### Tập A — GPU & rendering (làm trước)
| # | Chương | Câu hỏi trung tâm |
|---|---|---|
| A1 | Đời của một frame: C# → render thread → driver → GPU → màn hình | Nghẽn ở đâu? frame pacing, latency |
| A2 | Hình học và raster: binning, quad overshading, early-Z / LRZ / FPK / HSR, overdraw | Vì sao hiệu ứng nhỏ làm sập fps? |
| A3 | Tile memory và render pass: load/store, MSAA, subpass, **đọc RenderGraph của URP** | Vì sao một pass thêm tốn vài ms? |
| A4 | Shader chạy thế nào: wave, register, occupancy, precision, đọc kết quả compiler | Shader "ngắn" sao lại chậm? |
| A5 | Texture, cache, bandwidth, nén, nhiệt | Vì sao đổi định dạng texture lại đổi frame time? |
| A6 | Variant, PSO, shader stutter | Khựng lần đầu thấy hiệu ứng |
| A7 | SRP Batcher, instancing, BRG, GPU Resident Drawer (đọc source) | 5.000 vật thể nên đi đường nào? |
| A8 | Ánh sáng và bóng: forward+, deferred, shadow | Bao nhiêu đèn thì vỡ? |
| A9 | Compute và GPU-driven: barrier, prefix sum, indirect, culling Hi-Z | Đẩy việc sang GPU khi nào lỗ? |
| A10 | Nâng cao: temporal/upscaling, meshlet, visibility buffer, GI, ray tracing | Cái nào đáng giá trong ngân sách hẹp? |

### Tập B — CPU và engine core (sau tập A)
B1 IL → IL2CPP → ARM64, đọc C++ sinh ra và asm · B2 bộ nhớ và GC · B3 Burst và vectorization trong Inspector · B4 job system, memory model ARM64 · B5 ECS: chunk, structural change, scheduling (đọc source) · B6 CoreCLR và Unity 7.

10 bài hiện tại thành nguyên liệu. Bài nào đã có chương thay thế thì xoá khỏi mục lục.

## Thứ tự
1. Bước 0: project mẫu và script build/đo.
2. Bước 1: chương mẫu A2. Chưa được duyệt thì không viết chương thứ hai.
3. Bước 2: A1, A3 → A10, review xong từng chương.
4. Bước 3: tập B.

## Phạm vi
Không làm phần thiết bị Android và công cụ profiler. Chỉ use case và ví dụ mô phỏng chạy trên máy phát triển (Apple Silicon, Unity 6000.5.1f1); số đo được ghi đúng là của máy đó.
