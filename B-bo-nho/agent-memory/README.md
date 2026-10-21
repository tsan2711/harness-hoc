# agent-memory/ — agent nhớ bằng cách nào

| # | Bài | Từ đâu |
|---|---|---|
| 01 | [Agent "nhớ" bằng cách nào](01-agent-nho-the-nao.md) — ngữ cảnh, file, từ khoá, vector, đồ thị, LLM tóm tắt; Zero-Mem (đọc bài gốc); mem0, Graphiti, Letta, claude-mem, qmd, sqlite-vec; Claude Code / Cursor / Devin; số đo recall của Seriously; 4 nền tảng | arXiv 2607.29377 + web + đo repo 2026-10-15 |
| 04 | [Tìm kiếm: BM25, vector, hybrid, đồ thị tri thức, graph-RAG](04-do-thi-tri-thuc-va-tim-kiem-lai.md) — RRF, single vs multi-hop, entity resolution, STALE (ký ức cũ ngầm) | arXiv 2501.13956, 2605.06527, 2602.23372 + tranh luận 2026-10-20 |
| 05 | [Tranh luận: KG vs recall hiện tại](05-tranh-luan-kg-vs-recall.md) — biên bản 7 vòng: câu hỏi, lập luận, chỗ bị khoét, nhận sai, research, kiểm bằng dữ liệu repo, kết quả | phiên HQ 2026-10-20 |
| 05a | [BM25 và FTS5](05a-bm25-va-fts5.md) — chỉ mục ngược, IDF, bão hoà, bỏ dấu, AND/OR, cái `recall` dùng | bài khái niệm của 05 |
| 05b | [Embedding và vector](05b-embedding-va-vector.md) — cosine, chunk, model đa ngữ, giỏi/dở | bài khái niệm của 05 |
| 05c | [Hybrid, RRF, reranker](05c-hybrid-rrf-reranker.md) — "BM25 cộng vector" là gì | bài khái niệm của 05 |
| 05d | [Knowledge graph](05d-knowledge-graph.md) — nút/cạnh, gộp thực thể, PPR | bài khái niệm của 05 |
| 05e | [Graph-RAG](05e-graph-rag.md) — GraphRAG, HippoRAG, SPRIG; một bước vs nhiều bước | bài khái niệm của 05 |
| 05f | [Kiến thức cũ và thay thế](05f-ky-uc-cu-va-thay-the.md) — bitemporal, STALE, lan truyền | bài khái niệm của 05 |
| 05g | [Đo truy hồi](05g-do-truy-hoi.md) — recall@k, cỡ mẫu, rò rỉ, thí nghiệm công bằng | bài khái niệm của 05 |
| 06 | [Kiến trúc memory đề xuất](06-kien-truc-de-xuat.md) — nguyên tắc, sơ đồ đọc/ghi, bảng edges, pha P0–P4 + cổng đo, việc chờ chốt | kết quả của 05 |

Phương án áp cho công ty: `~/Documents/GitHub/Unity/Seriously/docs/shared/memory-options.md`.

## ĐANG LÀM — viết lại chuỗi 07 thành bài tổng quát, từ gạch đầu tiên (Bi, 2026-10-21)

Bi chê bản 07a–07i (bảng dưới) "chưa rõ": viết như người trong nhà, giả định đã biết Seriously. Viết lại thành chuỗi **ai ở đâu cũng
đọc được**, đi từ khái niệm gốc lên kiến trúc, **ghi đè** file 07 cũ (đổi tên theo dàn bài mới, sửa link; số liệu thật trong bản cũ dùng lại được).

Luật viết (thêm vào khuôn `CACH-HOC.md`):
1. **Không giả định gì.** Mỗi thuật ngữ được giải thích ở lần đầu bằng lời thường + ví dụ đời thường; không dùng tên nội bộ
   (`kit`, phòng, inbox, claim, chốt/chuyện, PA2, H-10, P0…) trong phần chính.
2. **Phần chính là tổng quát:** ví dụ trung tính (một nhóm 3 người + trợ lý AI viết code, một wiki công ty…).
3. **Seriously chỉ ở cuối bài**, khung "Ví dụ thật: Seriously làm thế này" — kể lại như kể cho người ngoài (repo có gì, file nào,
   số đo), đọc bỏ qua vẫn hiểu bài.
4. **Mỗi bài chỉ dùng khái niệm của bài trước nó.** Bài sau xây trên bài trước; đầu bài ghi "bạn đã biết: …", cuối bài "giờ bạn biết thêm: …".
5. Giữ: chuyện mở đầu → dừng 30 giây → các cách + chỗ gãy → bảng → scale → 4 nền tảng → tóm tắt + thuật ngữ; ≤ 10 phút/bài.

Dàn bài mới (bậc thang):
| Bài | Viên gạch | Ý chính |
|---|---|---|
| 07-01 | Model không nhớ | LLM là hàm không trạng thái; ngữ cảnh = trí nhớ ngắn hạn; token = tiền + chỗ; vì sao cần trí nhớ ngoài |
| 07-02 | Ghi ra ngoài | file text, nguồn sự thật vs bản sao (cache), git = lịch sử; tất định; vì sao không để LLM tóm lúc ghi |
| 07-03 | Tìm lại | đọc hết → grep → chỉ mục ngược → chấm điểm (ý BM25 bằng lời, link 05a để sâu) → chỉ mục dựng lại được |
| 07-04 | Ai bấm nút tìm | kéo vs đẩy; hook là gì (sự kiện → chạy lệnh → in ra thì vào ngữ cảnh); ngân sách thời gian/token; ngưỡng im |
| 07-05 | Nhãn trên tài liệu | metadata, frontmatter, schema; "chưa trả lời" ≠ "trả lời là không" |
| 07-06 | Quan hệ giữa tài liệu | đồ thị: nút, cạnh, nhãn; lưu bằng một bảng; đi 1 bước / nhiều bước; hub; cạnh có sẵn (git, link) vs cạnh phải đoán |
| 07-07 | Kiến thức cũ | thay thế / sửa sai / cùng tồn tại; vì sao "mới nhất thắng" sai; xếp hạng = tìm + luật; nhãn đặt đầu dòng |
| 07-08 | Lúc ghi | khi nào người viết biết nhiều nhất; nhắc vs chặn; đóng cứng; báo tài liệu phụ thuộc; kiểm định kỳ (lint) |
| 07-09 | Đo | bộ câu hỏi + đáp án; recall@k; bộ luyện vs bộ thi (held-out); rò rỉ; so từng câu; đo hành vi thật |
| 07-10 | Đổi hệ thống an toàn | từng bước một; luật thắng viết trước; ablation; công tắc tắt (feature flag); rollback |
| 07-11 | Nhận diện thực thể | regex / từ điển / model nhỏ / LLM; NER ≠ gộp thực thể ≠ trích quan hệ |
| 07-12 | Ghép lại | kiến trúc đầy đủ bằng lời tổng quát (bài 06 viết lại cho người ngoài) + Seriously đang ở đâu trên đó |

Số liệu thật đã đo (2026-10-21, dùng cho khung Seriously): dựng lại chỉ mục 28,6 s / 20 706 đoạn / 77 MB; tìm ấm 33–70 ms, ngay sau
commit 1,1 s (cache git lệch); đưa sẵn khi nhận việc 679/867 = 78 %; 95/1 516 commit (6 %) có trailer `Task:`; WORKBOARD.md 102 commit
(hub); bộ đo kw 20/20 · para 9/20 · bẫy 4/5; regex thực thể bắt đường dẫn/mã lỗi/tên test, sót "VFX Graph", "June", "Bi".

## Bản cũ (sẽ bị thay) — chuỗi 07 viết cho người trong nhà

Mỗi mảnh của bài 06 thành một bài, viết theo `CACH-HOC.md`, số đo lấy từ repo Seriously ngày 2026-10-21. Đọc theo thứ tự:

| Bài | Mảnh kiến trúc | Khái niệm |
|---|---|---|
| [07a](07a-nguyen-tac-git-nguon-su-that.md) | Nguyên tắc: 0 token, git là nguồn sự thật, chỉ mục dựng lại được | nguồn sự thật vs cache, tất định, H-10; dựng lại 28,6 s / 20k đoạn |
| [07b](07b-duong-doc-day.md) | Đường đọc **đẩy**: hook `UserPromptSubmit`, claim, mở phiên | push vs pull, ngân sách ms/token, ngưỡng im lặng; search ấm 33–70 ms, nguội 1,1 s |
| [07c](07c-frontmatter.md) | Frontmatter `status/supersedes/scope/keywords` | metadata, schema, `none` ≠ thiếu, suy ngược cạnh; ca `trap-art` |
| [07d](07d-bang-edges.md) | Bảng `edges` = knowledge graph tất định | cạnh từ git/link/trailer, hub (WORKBOARD 102 commit), CTE đệ quy, cạnh thưa (6 % có `Task:`) |
| [07e](07e-luat-xep-hang.md) | Luật xếp hạng sau khi tìm | xô điểm, chuỗi luật có thứ tự, nhãn đầu dòng, không hạ hạng theo ngày |
| [07f](07f-duong-ghi.md) | Đường ghi: hook nhắc, lan truyền, lint | PostToolUse, nhắc ≠ chặn, cascade 1 bước, ossification |
| [07g](07g-thuoc-do.md) | Thước đo mới: held-out, multi, stale; chỉ số dùng thật | rò rỉ, recall@3 vs @12, so từng câu, bộ đo như hợp đồng |
| [07h](07h-lo-trinh-pha-va-cong.md) | Lộ trình pha + cổng | P0 trước, luật thắng đặt trước, ablation, `crutch-test` + `layers.toml` |
| [07i](07i-ner.md) | NER (Bi hỏi 2026-10-20) | regex / gazetteer / model nhỏ / LLM; NER ≠ gộp thực thể ≠ trích quan hệ |

Sửa so với bài 06 (phát hiện khi viết 07): đường **mở phiên có việc dở** đã có từ 2026-10-16 (`leftover.recall_line()`, `78bb4ec05`);
trailer `Task:` đã tự gắn khi claim (`safe_commit.py`).
