# Bài 2 — Job System + Burst

> Trục A · Sản phẩm: chuyển 1 vòng lặp bầy cánh hoa sang Burst job, so trước/sau.

## 1. Câu chuyện
Bài 1 bạn sắp dữ liệu liên tục. Giờ CPU có 8–16 nhân mà `Update()` chỉ dùng 1. Bạn bọc vòng lặp vào `Parallel.For` — nhanh hơn một chút rồi... crash ngẫu nhiên, hoặc không nhanh hơn. Job System + Burst ra đời để giải đúng chuyện này: **chạy song song an toàn, và biên dịch C# thành mã native tốt**.

## 2. Dừng 30 giây
Hai luồng cùng ghi vào mảng `pos[]`. Luồng 1 ghi `pos[10]`, luồng 2 ghi `pos[11]` — hai ô khác nhau, đúng logic. Nhưng chúng nằm **chung một cache line**. Mỗi lần ghi, nhân kia phải bỏ bản copy của mình. Hãy nghĩ: chương trình đúng mà vẫn chậm vì sao?

## 3. Khái niệm lõi
- **Job**: struct (`IJob`, `IJobParallelFor`, `IJobEntity`...) chứa dữ liệu vào/ra, không chạm object managed. Scheduler của Unity phân việc cho worker thread.
- **NativeArray/NativeContainer**: bộ nhớ ngoài GC. Có **safety system** (editor) bắt race condition; attribute `[ReadOnly]` cho phép nhiều job cùng đọc.
- **Dependency (JobHandle)**: job B đợi job A. Dựng đồ thị phụ thuộc thay vì khoá (lock).
- **Burst**: compiler LLVM cho một tập con C# (HPC#) — không managed alloc, không class. Cho phép SIMD tự động, `[NoAlias]`, `math` của Unity.Mathematics. Cần IL2CPP trên iOS; chạy trên Windows, macOS, Android ARM64.
- **Batch size** của `IJobParallelFor`: quá nhỏ → overhead scheduling; quá lớn → mất cân bằng tải. Điểm bắt đầu 64–1024, đo rồi chỉnh.
- **False sharing**: hai nhân ghi vào cùng cache line (câu chuyện trên). Cách tránh: chia việc theo đoạn liên tục lớn, không xen kẽ.
- WebGL không chạy job đa luồng thật (một luồng) — lưu ý nếu có bản web.

## 4. Các cấu trúc và đánh đổi
| Cách | Ưu | Nhược |
|---|---|---|
| `Update()` đơn luồng | Đơn giản | Dùng 1 nhân |
| `Parallel.For` / `Task` | Quen thuộc | Không có safety system của Unity, GC, tranh scheduler với Unity |
| `IJobParallelFor` + Burst | An toàn, nhanh, SIMD | Chỉ dữ liệu blittable, phải nghĩ theo dữ liệu |
| Compute shader (GPU) | Hàng triệu phần tử | Đọc kết quả về CPU đắt; bài 5 |

## 5. Scale
- Việc nhỏ (< ~vài chục µs): overhead job còn lớn hơn lợi → giữ đơn luồng, nhưng vẫn Burst được (`[BurstCompile]` job chạy `.Run()`).
- Hàng chục nghìn phần tử, phép tính đồng đều: Burst + parallel cho tăng tốc lớn nhất.
- Quá nhiều job nhỏ nối tiếp: gộp lại; mỗi `Complete()` là một điểm đồng bộ.
- Mobile: ít nhân lớn, nhiệt hạn chế — đo thời gian *kéo dài*, không chỉ vài frame đầu.

## 6. Sản phẩm trong Thousandfold
1. Lấy vòng cập nhật vị trí/chuyển động cánh hoa (kết quả bài 1).
2. Viết thành `IJobParallelFor` + `[BurstCompile]`; dữ liệu trong `NativeArray`.
3. Đo 4 cấu hình: managed đơn luồng → Burst `.Run()` → Burst parallel (batch 64) → Burst parallel (batch 512). N = 100k.
4. Tắt thử Burst để thấy chênh lệch; bật Jobs Debugger / safety khi phát triển, tắt khi đo.
5. Đo windowed bằng Profiler (Timeline view để thấy worker thread bận/rảnh). Ghi bảng vào `log.md`.
- Nhớ luật gom job Unity của repo: `kit compile` giữa chừng, một lượt test/đo ở cuối.

## 7. Tự kiểm
- Vì sao job không được giữ tham chiếu tới `class` managed?
- Batch size 1 sai ở đâu? Batch size = N sai ở đâu?
- Đọc Timeline: nhân nào rảnh thì bạn kết luận gì?

## 8. Đọc thêm
Tài liệu Unity: C# Job System, Burst User Guide (phần "Burst-compatible C#"), Unity.Mathematics.
