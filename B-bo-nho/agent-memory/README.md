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

## Chuỗi 07 — hiểu hết kiến trúc đề xuất (bài 06)

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
