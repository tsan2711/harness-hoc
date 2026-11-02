# Bài 1 — Bộ nhớ, cache CPU và data-oriented design

> Trục A · Sản phẩm: đo AoS vs SoA trên 1 hệ của Thousandfold, ghi số.

## 1. Câu chuyện
Hai vòng lặp cùng làm một việc: cộng vận tốc vào vị trí cho 100.000 cánh hoa. Bản A dùng `class Petal` rải trong heap, bản B dùng mảng `float3` liên tục. Cùng thuật toán, cùng số phép tính — bản B thường nhanh gấp 5–20 lần. CPU không chậm vì tính toán; nó **chờ bộ nhớ**.

Con số cần nhớ (bậc độ lớn, không phải số chính xác): đọc từ L1 cache ~1 ns, từ RAM ~100 ns. Chênh ~100 lần. Một lần "cache miss" = CPU bỏ phí hàng trăm phép tính.

## 2. Dừng 30 giây
Nghĩ về vòng `foreach (var p in petals) p.pos += p.vel * dt`. Trong bộ nhớ, `petals` là mảng tham chiếu tới object nằm ở đâu đó. Mỗi `p` là một lần nhảy tới địa chỉ lạ. Mỗi object lại mang cả `color`, `age`, `id`... mà vòng lặp này không dùng. Hãy tự hỏi: **mỗi lần CPU kéo 1 cache line về, bao nhiêu byte trong đó thực sự có ích?**

## 3. Khái niệm lõi
- **Cache line**: đơn vị CPU kéo từ RAM, 64 byte trên x86 và đa số ARM; chip Apple Silicon dùng line 128 byte. Đọc 1 byte = kéo cả line.
- **Locality**: không gian (dữ liệu cạnh nhau) và thời gian (dùng lại sớm). Prefetcher của CPU đoán được truy cập tuần tự, không đoán được truy cập nhảy cóc.
- **AoS** (Array of Structs): `Petal[]` mỗi phần tử chứa mọi field. **SoA** (Struct of Arrays): `float3[] pos; float3[] vel; float[] age;`.
- **Data-oriented design** (Mike Acton, CppCon 2014 "Data-Oriented Design and C++"): thiết kế quanh *dữ liệu và phép biến đổi* trên nó, không quanh "đối tượng". Câu hỏi gốc: dữ liệu nào đi cùng nhau, được đọc bao nhiêu lần, bởi ai.
- **Unity ECS**: component cùng loại nằm liên tục trong *chunk* (16 KB) theo archetype — đó là SoA có tổ chức sẵn.

## 4. Các cấu trúc và đánh đổi
| Cách | Ưu | Nhược | Dùng khi |
|---|---|---|---|
| `class` trong `List<T>` | Dễ viết, đa hình | Nhảy con trỏ, GC, miss cache | Ít phần tử, logic phức tạp |
| `struct[]` (AoS) | Liên tục, không GC | Kéo cả field không dùng | Vòng lặp dùng hầu hết field |
| SoA (nhiều mảng) | Chỉ kéo field cần dùng, hợp SIMD | Thêm/xoá/đồng bộ nhiều mảng khó hơn | Hot loop trên số lượng lớn |
| ECS chunk | SoA + quản lý vòng đời sẵn | Đường cong học, ranh giới với OOP | Hàng chục nghìn+ thực thể |

Quy tắc kinh nghiệm: **tối ưu theo thứ tự đo → đổi layout → mới tới thuật toán vi mô**.

## 5. Scale
- 1k phần tử: layout gần như không quan trọng.
- 100k: layout quyết định có đạt 60 fps trên mobile hay không.
- 1M+: băng thông bộ nhớ thành giới hạn; cần chunk, streaming, LOD dữ liệu.
- Nền tảng: Windows/Mac desktop có cache lớn hơn; iOS (A-series) mạnh nhưng nóng nhanh; Android tầm thấp cache nhỏ, lệch nhiều nhất. Thousandfold nhắm PC (Steam) trước nên dư địa lớn, nhưng thói quen layout tốt đi theo bạn sang mọi nền tảng.

## 6. Sản phẩm trong Thousandfold
1. Chọn 1 hệ cập nhật hàng loạt (di chuyển bầy cánh hoa).
2. Viết 2 bản benchmark: AoS `struct[]` và SoA, cùng N = 10k / 100k / 1M.
3. Đo bằng Profiler, **chạy windowed** (không batchmode) khi có render; benchmark thuần CPU có thể headless. Lấy trung vị của ≥ 10 lần chạy bỏ lần đầu (JIT/warmup).
4. Ghi bảng ms/frame theo N vào `log.md`. Một câu kết luận: layout nào, vì sao.

## 7. Tự kiểm
- Giải thích bằng 3 câu vì sao SoA nhanh hơn dù số phép tính như nhau.
- Khi nào SoA **không** đáng (gợi ý: truy cập ngẫu nhiên nhiều field cùng lúc)?
- Agent viết cho bạn một `List<Petal>` class — bạn nhìn ra vấn đề gì trong 10 giây?

## 8. Đọc thêm
Mike Acton CppCon 2014 (video); tài liệu Unity Entities về chunk và archetype; "What every programmer should know about memory" (Drepper) nếu muốn sâu — nặng, đọc chọn lọc.
