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

## Chuỗi 07 — trí nhớ cho agent, từ gạch đầu tiên (viết lại 2026-10-21)

Viết cho **ai ở đâu cũng đọc được**: phần chính tổng quát (ví dụ: nhóm "Quán Nhỏ" 3 người + agent làm app đặt món); Seriously chỉ ở khung
"Ví dụ thật" cuối bài, bỏ qua vẫn hiểu. Mỗi bài chỉ dùng khái niệm của bài trước. Đọc theo thứ tự:

| Bài | Viên gạch | Ý chính |
|---|---|---|
| [07-01](07-01-model-khong-nho.md) | Model không nhớ | LLM là hàm không trạng thái; ngữ cảnh = trí nhớ ngắn hạn; token = tiền + chỗ; vì sao cần trí nhớ ngoài |
| [07-02](07-02-ghi-ra-ngoai.md) | Ghi ra ngoài | file text, nguồn sự thật vs bản sao (cache), git = lịch sử; tất định; vì sao không để LLM tóm lúc ghi |
| [07-03](07-03-tim-lai.md) | Tìm lại | đọc hết → grep → chỉ mục ngược → chấm điểm (ý BM25) → chỉ mục dựng lại được |
| [07-04](07-04-ai-bam-nut-tim.md) | Ai bấm nút tìm | kéo vs đẩy; hook; ngân sách thời gian/token; ngưỡng im |
| [07-05](07-05-nhan-tren-tai-lieu.md) | Nhãn trên tài liệu | metadata, frontmatter, schema; "chưa trả lời" ≠ "trả lời là không" |
| [07-06](07-06-quan-he-giua-tai-lieu.md) | Quan hệ giữa tài liệu | đồ thị = một bảng cạnh; 1 bước / nhiều bước; hub; cạnh có sẵn vs cạnh phải đoán |
| [07-07](07-07-kien-thuc-cu.md) | Kiến thức cũ | thay thế / sửa sai / cùng tồn tại; "mới nhất thắng" sai; tìm + luật xếp; nhãn đầu dòng |
| [07-08](07-08-luc-ghi.md) | Lúc ghi | nhắc lúc ghi, không chặn; đóng cứng; báo tài liệu phụ thuộc; lint |
| [07-09](07-09-do.md) | Đo | bộ đo + đáp án; recall@k; bộ luyện vs bộ thi; rò rỉ; so từng câu; đo hành vi thật |
| [07-10](07-10-doi-he-thong-an-toan.md) | Đổi hệ thống an toàn | từng bước; luật thắng viết trước; ablation; công tắc tắt; quay lui; "nạng" |
| [07-11](07-11-nhan-dien-thuc-the.md) | Nhận diện thực thể | mẫu chữ / từ điển / model nhỏ / LLM; NER ≠ gộp thực thể ≠ trích quan hệ |
| [07-12](07-12-ghep-lai.md) | Ghép lại | kiến trúc đầy đủ bằng lời tổng quát, so với kiến trúc khác + Seriously đang ở đâu |

Bản 07a–07i cũ (viết cho người trong nhà) đã được thay bằng chuỗi trên; xem lịch sử git nếu cần.

Sửa so với bài 06 (phát hiện khi viết 07): đường **mở phiên có việc dở** đã có từ 2026-10-16 (`leftover.recall_line()`, `78bb4ec05`);
trailer `Task:` đã tự gắn khi claim (`safe_commit.py`).
