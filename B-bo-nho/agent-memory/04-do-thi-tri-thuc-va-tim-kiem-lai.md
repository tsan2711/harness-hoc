# 04 — Tìm kiếm: BM25, vector, hybrid, đồ thị tri thức, graph-RAG

> Mục tiêu: đủ kiến thức để tranh luận "KG có tốt hơn recall hiện tại không". Bài này chỉ nói *tìm ra đoạn liên quan*.
> Phần "kiến thức mới thay kiến thức cũ" nằm ở mục 7. Bối cảnh tranh luận: `Seriously/docs/shared/memory-debate-2026-10-20.md`.

## 1. Câu chuyện

Thư viện có 10.000 cuốn. Bạn hỏi thủ thư: "sách nào nói về **cuốn nhầm thay đổi của người khác khi commit**?"

- Thủ thư A tra **mục lục từ khoá**: tìm chữ "commit", "cuốn", "nhầm". Cuốn viết "stash làm mất file phiên khác" không có chữ nào trùng → không ra.
- Thủ thư B đã đọc hết sách, **hiểu nghĩa**: biết "cuốn nhầm" ≈ "mất file phiên khác" ≈ "git stash". Ra đúng. Nhưng bạn không thể kiểm tra ông ấy nghĩ gì, và đôi khi ông ấy nhớ lẫn hai cuốn.
- Thủ thư C vẽ một **bản đồ quan hệ**: cuốn A nói về `git stash`, `git stash` thuộc chủ đề "nhiều phiên cùng lúc", chủ đề đó được quy định bởi ADR-0012, ADR-0012 sửa file `kit.sh`. Hỏi "cái gì chi phối kit.sh" thì đi theo bản đồ.

Ba thủ thư = ba họ phương pháp. Hệ của ta hiện là thủ thư A.

**Dừng 30 giây.** Không cần trả lời: trong 10 câu mà `recall` đang trượt (para-gd, para-icons, para-scale…), bạn nghĩ câu nào cần "hiểu nghĩa" (B), câu nào cần "đi theo quan hệ" (C)? Chưa có đáp án đúng — đây chính là điều ta chưa đo.

## 2. Thủ thư A: BM25 (đã có trong `recall.py`)

- **Ý tưởng:** chấm điểm đoạn văn theo các từ trùng với câu hỏi.
- **Ba yếu tố:** (1) từ xuất hiện nhiều trong đoạn → điểm cao (tần suất, nhưng bão hoà dần); (2) từ hiếm toàn kho quan trọng hơn từ phổ biến ("RenderMeshInstanced" nặng hơn "là"); (3) đoạn dài bị trừ nhẹ.
- **Ưu:** nhanh (ms), 0 token, giải thích được, tên riêng/mã (`CS0103`, đường dẫn) trúng tuyệt đối. Ta đo: từ khoá 20/20.
- **Nhược:** không biết đồng nghĩa; khác từ là trượt (ta đo: diễn đạt lại 10/20). Bỏ dấu tiếng Việt làm "nhớ" khớp "nhỏ" (đã vá bằng cột giữ dấu).
- SQLite FTS5 có sẵn hàm `bm25()`.

## 3. Thủ thư B: vector (embedding)

- **Ý tưởng:** một model nhỏ biến mỗi đoạn văn thành một dãy số (vector, vài trăm chiều) sao cho đoạn *cùng nghĩa* nằm gần nhau. Câu hỏi cũng thành vector; tìm vector gần nhất (cosine).
- **Chạy cục bộ được:** model embedding đa ngữ cỡ vài trăm MB + `sqlite-vec` trong cùng file SQLite. Ghi chỉ mục tốn CPU, **không tốn token LLM**.
- **Ưu:** "cuốn nhầm" ≈ "mất file phiên khác" trúng được. Đây là thuốc cho lỗ diễn đạt lại.
- **Nhược:** hay trượt mã/tên riêng (`CS0103` gần "CS0104" hay gần "lỗi compile"? mơ hồ); không giải thích được vì sao gần; có thể trúng đoạn "cùng chủ đề nhưng khác ý" (ví dụ cùng nói về stash nhưng một đoạn khuyên dùng, một đoạn cấm).

## 4. BM25 + vector = hybrid (trả lời câu "triển khai gì?")

Chạy cả hai, ra hai danh sách xếp hạng, rồi **trộn bằng RRF (Reciprocal Rank Fusion)**:

```
điểm(đoạn) = Σ_trên_mỗi_danh_sách  1 / (k + hạng_trong_danh_sách)     k ≈ 60
```

Đoạn nào đứng cao ở *cả hai* thì tổng lớn. Không cần chuẩn hoá điểm hai hệ (điểm BM25 và cosine khác thang), chỉ dùng *thứ hạng*. Rất đơn giản, ~10 dòng code.

Ví dụ nhỏ: đoạn X hạng 1 ở BM25, hạng 5 ở vector → 1/61 + 1/65 ≈ 0,0318. Đoạn Y hạng 30 ở BM25, hạng 1 ở vector → 1/90 + 1/61 ≈ 0,0275. X thắng, nhưng Y vẫn lọt top nhờ vector.

Trong repo: `recall.py` đã có BM25 (FTS5). Thêm vector = thêm `sqlite-vec` + bước embedding khi index + hàm trộn RRF. `memory-options.md` PA2.4 mô tả đúng hướng này nhưng đang bị khoá bởi cổng 14 ngày.

Tài liệu nghiên cứu cho thấy hybrid RRF là **baseline mạnh** — nhiều khi ngang hoặc hơn phương pháp phức tạp hơn ở tra cứu một bước.

## 5. Thủ thư C: đồ thị tri thức (KG)

- **Nút (node):** thực thể — file, ADR, bộ phận, khái niệm, việc, commit.
- **Cạnh (edge):** quan hệ có nhãn — `ADR-12 --chi phối--> kit.sh`, `task-45 --đã sửa--> kit.sh`, `ADR-20 --thay thế--> ADR-12`.
- **Truy vấn quan hệ:** "cái gì chi phối kit.sh" = đi một bước; "việc nào đã sửa thứ mà ADR-12 chi phối" = đi hai bước (**multi-hop**).
- **Hai cách dựng cạnh:**
  - *Tất định:* lấy từ dữ liệu đã có cấu trúc (link markdown, trailer `Task:`, `git log --name-only`, `unit.toml`). Rẻ, đáng tin, nhưng chỉ có những quan hệ đã được ghi.
  - *Bằng LLM trích xuất:* cho LLM đọc văn bản và rút "thực thể + quan hệ". Phủ rộng, nhưng tốn token, không tất định, và có thể bịa/gộp nhầm.
- **Entity resolution (gộp thực thể):** "stash", "git stash", "cất tạm thay đổi" có phải một node không? Đây là chỗ quyết định chất lượng KG, và là phần khó nhất — cần hiểu nghĩa (LLM, từ điển tay, hoặc embedding).

## 6. Graph-RAG là gì

RAG = tìm đoạn liên quan rồi đưa cho LLM trả lời. **Graph-RAG** = dùng đồ thị trong bước tìm.

Có nhiều biến thể; hai ý chính:

1. **Kiểu Microsoft GraphRAG (đầy đủ):** LLM đọc từng chunk, rút thực thể + quan hệ → dựng đồ thị → chia đồ thị thành các cụm (community detection) → LLM viết bản tóm tắt cho từng cụm. Lúc hỏi: *local search* (đi quanh thực thể trong câu hỏi) hoặc *global search* (gom các tóm tắt cụm để trả lời câu toàn cục kiểu "các chủ đề chính của kho là gì?"). Đắt (nhiều lần gọi LLM lúc dựng), mạnh ở câu tổng hợp.
2. **Kiểu nhẹ (PageRank trên đồ thị):** bắt đầu từ vài đoạn trúng (hạt giống, "seed") do BM25/vector tìm, rồi *lan truyền* qua cạnh để kéo thêm đoạn hàng xóm (Personalized PageRank: người đi bộ ngẫu nhiên xuất phát từ seed; nơi nào hay ghé thì quan trọng). Biến thể SPRIG (arXiv 2602.23372) dựng đồ thị bằng NER đồng xuất hiện, **không LLM**, chạy CPU. Ý tưởng tương tự cũng có ở HippoRAG (theo trí nhớ của người viết, chưa xác minh lại trong phiên này).

Zep/Graphiti (arXiv 2501.13956) là KG **có trục thời gian**: mỗi cạnh có thời điểm hiệu lực; khi thông tin mới mâu thuẫn, cạnh cũ bị đóng (không xoá) — theo mô tả thứ cấp, cơ chế này chưa đọc trong bài gốc.

## 7. Hai bài toán khác nhau: tìm ra vs thay thế

| Bài toán | Ví dụ | Công cụ |
|---|---|---|
| **Tìm đúng đoạn liên quan** | "ADR nào chi phối file này?" | BM25, vector, hybrid, graph |
| **Biết đoạn nào đã bị thay** | Quyết định mới đảo quyết định cũ | `supersedes`, sửa tại chỗ, nhắc lúc ghi |

Benchmark **STALE** (arXiv 2605.06527) chỉ ra bài toán thứ hai khó tới mức model mạnh nhất chỉ đạt 55,2 %: quan sát mới làm vô hiệu ký ức cũ mà không có phủ định tường minh ("Implicit Conflict"). Lỗi điển hình: nhận tiền đề đã cũ, không lan truyền cập nhật sang ký ức liên quan, lấy được thông tin mới nhưng hành vi không đổi. Bài học: *đừng giả định* agent hay đồ thị sẽ tự bắt được; phải có cơ chế ép lúc ghi.

## 8. Single-hop vs multi-hop (luận điểm 2 trong tranh luận)

- **Một bước:** câu trả lời nằm *trong một đoạn*. "Vì sao bỏ RenderMeshInstanced?" → một ghi chú. BM25/vector đủ; graph không hơn.
- **Nhiều bước:** câu trả lời cần *nối nhiều đoạn*. "Việc nào đã sửa module mà ADR-12 chi phối?" → đoạn ADR → đoạn module → đoạn việc. BM25/vector thường trượt vì không đoạn nào chứa đủ từ; graph đi theo cạnh nên trúng.
- **Toàn cục:** "các rủi ro chính của harness là gì?" → phải tổng hợp cả kho. GraphRAG đầy đủ (tóm tắt cụm) mạnh nhất.

Các tài liệu đã tra nhìn chung nói: graph thắng ở nhiều bước + toàn cục, hybrid thắng hoặc ngang ở một bước. Luận điểm của người tranh luận đối lập: nếu 10 câu trượt của ta chủ yếu là một bước (lỗ từ vựng), graph không phải thuốc đúng; **chưa kiểm chứng**.

## 9. Bảng so sánh

| | BM25 | Vector | Hybrid RRF | Link graph (tất định) | Graph-RAG LLM |
|---|---|---|---|---|---|
| Hiểu đồng nghĩa | không | có | có | không | có (nếu gộp thực thể tốt) |
| Mã / tên riêng | rất tốt | yếu | tốt | tốt | trung bình |
| Quan hệ nhiều bước | không | không | không | có (cạnh đã ghi) | có |
| Chi phí ghi chỉ mục | ~0 | CPU, 0 token | CPU, 0 token | ~0 | token LLM, cao |
| Giải thích được | có | không | một phần | có | một phần |
| Tất định / nằm trong git | có | gần như | gần như | có | không |
| Lỗi điển hình | trượt khác từ | trúng nhầm chủ đề gần | — | thiếu cạnh | gộp nhầm / bịa quan hệ |

## 10. Bản đồ lên harness của ta

- BM25 = `recall.py` hiện tại. Vector = PA2.4 (đang khoá bởi cổng 14 ngày). Link graph = cạnh `commit→file`, `task→commit`, link markdown. Graph-RAG LLM = Graphiti/mem0 (bị loại bởi H-10 — nhưng H-10 là ràng buộc vận hành, **không phải** bằng chứng chất lượng).
- Cách phân xử: đo bốn–năm cấu hình trên cùng bộ câu (kế hoạch ở mục 7 của file debate).

## 11. Tự kiểm tra (đáp án ở cuối)

1. Vì sao RRF dùng *thứ hạng* thay vì điểm?
2. Câu "ADR nào chi phối file này?" cần đi mấy bước? Thủ thư nào trả lời tốt nhất?
3. Một đồ thị dựng từ LLM gộp nhầm "git stash" và "git stash pop" thành một node. Hậu quả với kết quả tìm?
4. Vì sao graph thời gian (Graphiti) vẫn không loại bỏ được nhu cầu agent khai báo thay thế?

*Đáp án gợi ý:* (1) điểm BM25 và cosine khác thang, thứ hạng so sánh được mà không cần chuẩn hoá. (2) hai bước: câu hỏi→file→ADR; link graph hoặc graph-RAG. (3) kéo kiến thức về "pop" vào truy vấn "stash" — nhiễu im lặng. (4) graph chỉ đóng cạnh khi *biết* có mâu thuẫn; phát hiện mâu thuẫn ngầm vẫn cần hiểu nghĩa (STALE: 55 %).

## 12. Nguồn
- Zep — https://arxiv.org/abs/2501.13956
- STALE — https://arxiv.org/abs/2605.06527
- SPRIG (Democratizing GraphRAG) — https://arxiv.org/abs/2602.23372
- Survey graph memory — https://arxiv.org/abs/2609.08599
- Bài 01–03 cùng thư mục.
