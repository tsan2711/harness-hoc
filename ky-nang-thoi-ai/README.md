# Kế hoạch học 12 bài — theo kịp thời AI agent (ngoài harness)

Bắt đầu 2026-11-03. Căn cứ: Anthropic "Labor market impacts of AI" (3/2026) — mảng viết code theo spec là mảng bị phủ nhiều nhất; chỗ đứng = kiến trúc, kiểm chứng, sản phẩm.
Nguyên tắc: mỗi bài một chủ đề (story → "dừng 30 giây" → cấu trúc ưu/nhược → scale), ~5–6 giờ/bài, **mỗi bài kết bằng 1 sản phẩm nhỏ trong Thousandfold** (không học suông).

## Ba trục (tỉ lệ thời gian)
| Trục | % | Vì sao |
|---|---|---|
| A. Kiến trúc & hiệu năng engine | 45% | Agent viết nhanh nhưng không chịu hậu quả kiến trúc; đây là chỗ senior thắng |
| B. Eval / kiểm chứng | 30% | Kỹ năng được nhắc nhiều nhất; biến "có vẻ tốt" thành số |
| C. Sản phẩm indie (design, thị trường, phát hành) | 25% | AI = đòn bẩy cho một người làm ra cả game |

## Lịch

### Giai đoạn 1 — Nền (bài 1–4)
| Bài | Trục | Chủ đề | Sản phẩm cuối bài |
|---|---|---|---|
| 1 | A | Bộ nhớ & cache CPU: data-oriented design, layout dữ liệu, vì sao ECS nhanh | Đo 1 hệ trong Thousandfold: AoS vs SoA, ghi số |
| 2 | A | Job System + Burst: phụ thuộc job, false sharing, đo bằng Profiler (windowed) | Chuyển 1 vòng lặp bầy cánh hoa sang Burst job, so trước/sau |
| 3 | B | Eval 101: tập kiểm thử, baseline, nhiễu, kiểm định (McNemar/bootstrap), LLM-as-judge và bẫy của nó | Viết eval 20 mục cho 1 việc agent hay làm sai; chạy 2 cách prompt |
| 4 | C | Game design: vòng lặp cốt lõi, "vì sao người ta quay lại" (relaxing sim) | 1 trang GDD vòng lặp 30 giây của Thousandfold |

### Giai đoạn 2 — Sâu (bài 5–8)
| Bài | Trục | Chủ đề | Sản phẩm |
|---|---|---|---|
| 5 | A | GPU: draw call, instancing, VFX Graph/compute, bandwidth (nhớ: không RenderMeshInstanced bake CPU) | Bầy 100k cánh hoa bằng VFX Graph/compute, đo windowed |
| 6 | B | Eval cho agent: đo agent làm việc dài (tỉ lệ xong, chi phí/token, số lần sửa lại), regression | Bảng so sánh 2 cấu hình harness trên cùng 10 task |
| 7 | A | Kiến trúc: ranh giới module, dependency, khi nào ECS vs OOP, đọc code agent sinh ra để bắt nợ kiến trúc | Review 1 module agent viết, liệt kê 3 nợ, sửa |
| 8 | B | Bảo mật agent: quyền tối thiểu, sandbox, prompt injection, bí mật trong repo | Rà quyền hook/settings của repo, vá lỗ hổng tìm được |

### Giai đoạn 3 — Ra sản phẩm (bài 9–12)
| Bài | Trục | Chủ đề | Sản phẩm |
|---|---|---|---|
| 9 | C | Thị trường Steam: wishlist, tag, trang store, đối thủ cùng thể loại (dùng dữ liệu thật) | Bảng 10 game tương tự + số wishlist/review ước tính |
| 10 | C | Marketing một người: trailer, capsule, devlog, cộng đồng | Trailer 30s + capsule nháp |
| 11 | A+B | Spec & chia việc song song: viết spec đủ nhỏ cho agent, tránh dẫm file | 1 plan lớn chia 3 phiên, đo thời gian vs làm tuần tự |
| 12 | Tổng | Ôn: viết bài tổng kết "học được gì, số liệu nào" | 1 trang + quyết định tiếp (đi sâu trục nào) |

## Nguồn khởi đầu (kiểm lại trước khi tin)
- Anthropic: Labor market impacts of AI; Economic Index (theo dõi bản mới)
- arXiv 2606.21894 (kỹ năng nghề phần mềm thời agent)
- Unity docs: DOTS/Burst/Jobs, VFX Graph; Mike Acton "Data-Oriented Design" (CppCon 2014)
- Eval: tài liệu eval của Anthropic/OpenAI + bài về McNemar/bootstrap cho so sánh cặp

## Cách chạy
- Hết mỗi bài: ghi 3 dòng "học được / đo được / sai ở đâu" vào `log.md` cùng thư mục.
- Bài nào trượt thì bỏ sản phẩm phụ, không bỏ phép đo.
- Bài giảng (story → dừng 30 giây → khái niệm → cấu trúc ưu/nhược → scale → sản phẩm → tự kiểm), học theo thứ tự:
  1. [Bộ nhớ, cache CPU](01-bo-nho-cache-cpu.md)
  2. [Job System + Burst](02-job-system-burst.md)
  3. [Eval cơ bản](03-eval-co-ban.md)
  4. [Core loop & game design](04-core-loop-game-design.md)
  5. [GPU, instancing, VFX](05-gpu-instancing-vfx.md)
  6. [Eval cho agent](06-eval-cho-agent.md)
  7. [Kiến trúc & nợ code agent](07-kien-truc-no-code-agent.md)
  8. [Bảo mật agent](08-bao-mat-agent.md)
  9. [Thị trường Steam](09-thi-truong-steam.md)
  10. [Marketing một người](10-marketing-mot-nguoi.md)
  11. [Spec & chia việc song song](11-spec-chia-viec-song-song.md)
  12. [Tổng kết](12-tong-ket.md)
