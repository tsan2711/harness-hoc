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

## Đang viết — chuỗi 07: hiểu hết kiến trúc đề xuất (bài 06)

Mỗi mảnh của bài 06 thành một bài, viết theo `CACH-HOC.md` (chuyện → dừng 30 giây → các cách + chỗ gãy → bảng → scale → Seriously → 4 nền tảng → tóm tắt). Đọc theo thứ tự:

| Bài | Mảnh kiến trúc | Khái niệm cần có |
|---|---|---|
| 07a | Nguyên tắc: 0 token, git là nguồn sự thật, chỉ mục dựng lại được | nguồn sự thật vs cache, tất định, H-10 |
| 07b | Đường đọc **đẩy**: hook `UserPromptSubmit`, claim, mở phiên | hook Claude Code, push vs pull, ngân sách ms/token, ngưỡng im lặng |
| 07c | Frontmatter `status/supersedes/scope/keywords` | metadata, schema, suy ngược cạnh |
| 07d | Bảng `edges` = knowledge graph tất định | dựng cạnh từ git/link/trailer, hub, truy vấn đệ quy SQLite |
| 07e | Luật xếp hạng sau khi tìm | chuỗi luật, nhãn đầu dòng, vì sao không hạ hạng theo ngày |
| 07f | Đường ghi: hook nhắc, lan truyền, lint | PostToolUse, nhắc ≠ chặn, cascade, ossification |
| 07g | Thước đo mới: held-out, multi, stale; chỉ số dùng thật | (dựa 05g) bộ đo như hợp đồng |
| 07h | Lộ trình pha + cổng: vì sao P0 trước, luật thắng đặt trước | gate, ablation, rollback qua `layers.toml` |
| 07i | NER (Bi hỏi 2026-10-20) | regex vs model nhỏ vs LLM; NER ≠ gộp thực thể ≠ quan hệ |
