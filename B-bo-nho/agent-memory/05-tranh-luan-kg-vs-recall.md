> **Bản chụp 2026-10-20.** Bản sống (agent cập nhật khi refactor): `Seriously/docs/shared/memory-debate-2026-10-20.md`.

# Memory harness — tranh luận KG vs recall hiện tại (2026-10-20)

> **Mục đích:** ghi lại toàn bộ lập luận của phiên HQ 2026-10-20 để phiên sau cùng Bi review rồi refactor kiến trúc memory.
> Nối tiếp `memory-options.md` (PA2, 2026-10-15). Chưa có quyết định nào ở đây được áp vào code; mọi thứ dưới "Đề xuất" là để duyệt.
> Bài giảng nền (Bi đang học): `~/Documents/Learning/harness-hoc/B-bo-nho/agent-memory/04-do-thi-tri-thuc-va-tim-kiem-lai.md`.

## 1. Hiện trạng (đã đọc code, 2026-10-20)

| Tầng | Cơ chế | Nạp |
|---|---|---|
| 1 | Memory Claude Code: `~/.claude-zzd/projects/…/memory/*.md` + `MEMORY.md` (~1k token), chỉ giữ thứ về Bi + cách làm việc | tự động mỗi phiên |
| 2 | Sổ tay trong git: `CLAUDE.md` → `docs/ai/INDEX.md` → `.claude/rules/` → `depts/*/knowledge/` | agent đi theo chuỗi INDEX |
| 3 | `kit recall` (`tools/claude/recall.py`): FTS5 cục bộ trên transcript + notebook + git log + biên bản việc (`kind=task`) | agent phải tự gọi |
| 4 | `leftover.py` (SessionEnd / SessionStart / PreCompact), `Task:` trailer trong `kit commit`, `recall.hint()` trong `inbox.cmd_claim` (≤ 3 đoạn, ~600 token) | hook |

**Số đo `recall_eval` (2026-10-20):** từ khoá 20/20 · diễn đạt lại **10/20 (50 %)** · bẫy cũ 3/5 · `cũ@12` = 2 (mục tiêu 0) · ~24 ms/truy vấn.
Câu diễn đạt lại trượt: para-gd, icons, scale, guard, ccgs, kit, perf, why-index, android, anticheat.

## 2. Lỗ hổng đã nêu

1. Agent phải tự gọi recall; phiên thường gần như không gọi (đo 2026-10-15: 0).
2. Inject chỉ chạy khi `claim` việc inbox; hỏi kiến thức giữa phiên thì không có gì tự đưa tới. Đường "mở phiên với việc dở" chưa có.
3. PA2.3 (nhãn `có thể cũ`) chưa xong.
4. `inject_rate` và "lần mở transcript thô" chưa vào `kit weekly` → `remove_test` của `recall-inject` chưa có dữ liệu.
5. Chưa có vòng học từ nguồn ngoài (memory `feedback_learn_outside_not_echo`).
6. Ranh giới tầng 1 / tầng 2 chỉ dựa kỷ luật, không có lint.

## 3. Cuộc tranh luận (theo thứ tự)

**Q1 — Hỏi kiến thức, agent có phải tự tìm?** Có. Chắc chắn chỉ có đường INDEX (agent phải chịu đọc). Grep/Explore tốn token và hên xui. `kit recall` cho "chuyện cũ", không cho tra cứu, và agent phải tự gọi. → Đề xuất hook `UserPromptSubmit` chạy `recall.hint()` trên câu hỏi.

**Q2 — Dựng knowledge graph (KG) có hợp harness?**
Claude: KG kiểu Graphiti/mem0 (LLM trích xuất lúc ghi) vi phạm H-10 (tốn token, không tất định, dữ liệu ngoài git). Biến thể hợp: *link graph* dựng bằng script 0 token từ dữ liệu sẵn có (link markdown, `Task:`↔commit↔file, cột `ent`, `unit.toml`). Hữu ích cho: nhãn `cũ` (cạnh commit→file), mở rộng hàng xóm cho `hint()`, lint doc mồ côi, truy vấn quan hệ.

**Q3 — KG có giải quyết "kiến thức mới thay kiến thức cũ" chưa?**
Claude: chỉ một nửa. *Cũ do file đổi* → git thấy. *Cũ do quyết định đổi* (không file nào bị sửa) → máy không biết mâu thuẫn, graph không tự sinh cạnh `supersedes`. Cần hành động tường minh lúc ghi: trường `supersedes` + hook nhắc (recall 3 đoạn gần nhất, agent xác nhận hoặc ghi `supersedes: none`) + xếp hạng/lint theo cạnh.

**Q4 — Không KG có giải quyết được không?**
Claude: được; phần cốt lõi (`supersedes` + hook) không cần graph. Thang cách: (A) sửa tại chỗ, một chủ đề một file sống · (B) frontmatter `status/supersedes` · (C) hook nhắc lúc ghi · (D) xếp hạng theo ngày · (E) lint cặp gần nhau · (F) KG + LLM tự phát hiện mâu thuẫn (đắt, vi phạm H-10). Đề xuất A+B+C+E, D làm lưới.

**Q5 — Bi phản biện: "KG đẩy ra kiến thức liên quan chất lượng tốt hơn rất nhiều".**
Claude (đối thủ) thừa nhận:
- Đã lẫn hai loại lý lẽ: loại KG bằng ràng buộc harness (H-10) ≠ bằng chất lượng truy xuất.
- Nói quá khi bảo graph không sửa được lỗ diễn đạt lại: nếu entity resolution tốt, nhiều cách nói cùng trỏ một node → trúng.
Claude phản biện:
1. Chất lượng KG nằm hết ở *entity resolution* (khó nhất). Cần LLM/từ điển tay/embedding — dùng embedding thì thành vector, không còn là KG; dùng LLM thì lỗi gộp nhầm âm thầm kéo kiến thức lạc đề.
2. Nghi ngờ 10 câu trượt là câu khái niệm *một bước* (lỗ từ vựng), chưa phải multi-hop → graph không đúng thuốc. **Chưa kiểm chứng** (chưa mở từng câu).
3. "Tốt hơn rất nhiều" là con số Bi giả định; kho nhỏ, cạnh quan trọng đã nằm trong link/đường dẫn; phần phi cấu trúc (transcript) nhiễu nhất.
Claude tự soi: chưa đo mật độ link sổ tay; chưa chạy thử vector/graph so với 50 %; nếu Bi đúng thì cản là mất cơ hội cải thiện.
Bi đáp: đồng ý luận điểm 1 và 3; chưa hiểu 2 (graph-RAG, BM25+vector là gì) → viết bài giảng 04; đề nghị *research tài liệu đã có* thay vì đoán → mục 4.

## 4. Research bên ngoài (đã tra 2026-10-20; ghi rõ mức xác minh)

| Nguồn | Nói gì | Mức tin |
|---|---|---|
| Zep/Graphiti, arXiv 2501.13956 (Rasmussen et al.) | KG nhận biết thời gian cho memory agent; DMR 94,8 % vs MemGPT 93,4 %; LongMemEval +tới 18,5 %, độ trễ −90 % so baseline | Số trích từ abstract arXiv (đã đọc). Cơ chế `invalid_at` đóng cạnh cũ: **chỉ từ trang thứ cấp**, chưa đọc bài |
| STALE, arXiv 2605.06527 | Benchmark "Implicit Conflict": quan sát mới làm vô hiệu ký ức cũ *không có phủ định tường minh*. 400 kịch bản, 1.200 truy vấn; 3 trục: State Resolution / Premise Resistance / Implicit Policy Adaptation. **Model tốt nhất chỉ 55,2 %.** Lỗi: nhận tiền đề cũ, không lan truyền cập nhật sang ký ức liên quan, lấy được thông tin mới mà hành vi không đổi. Đề xuất CUPMem: sửa lúc ghi + tìm có lan truyền | Abstract đã đọc |
| SPRIG, arXiv 2602.23372 (Qizhi Wang) | GraphRAG CPU-only, không token: đồ thị đồng xuất hiện từ NER (không LLM) + Personalized PageRank; so với RRF hybrid; xác định *khi nào* graph giúp multi-hop và khi RRF đủ | Abstract đã đọc; số liệu bị cắt, **chưa có số tin cậy** |
| Survey 2609.08599 (graph memory cá nhân) | Chia bốn giai đoạn: biểu diễn, tiến hoá, truy xuất, đánh giá. Snippet tìm kiếm nói có phân loại xung đột *temporal supersession / user correction / contextual coexistence* và cảnh báo đừng gộp thành "mới nhất thắng" | Phân loại: **chỉ từ snippet, chưa xác minh** (tải trang chỉ ra abstract) |
| Governing Evolving Memory (SSGM), arXiv 2603.11768 | Lọc nhất quán quá chặt gây "ossification" (kiến thức đóng cứng); phân biệt drift với cập nhật hợp lệ còn mở | Snippet |
| 2602.23372 / 2604.01733 / bài blog so sánh | BM25 và RRF hybrid là baseline mạnh; GraphRAG thắng ở multi-hop & tổng hợp toàn cục, thường thua ở tra cứu chi tiết; chưa có benchmark nào chạy GraphRAG, BM25+vector và multi-hop dưới *cùng một thiết lập* | Tổng hợp thứ cấp |

**Rút ra cho ta (đã lọc):**
- Vấn đề của ta (kiến thức mới thay cũ, ngầm) là một bài toán có tên, có benchmark: *implicit conflict*. Ngay cả model mạnh nhất cũng chỉ 55 % → **không thể giao phán quyết mâu thuẫn cho agent mà không có cơ chế ép**; lẫn "giao hết cho KG tự phát hiện" cũng không có bằng chứng là xong.
- Hướng "sửa lúc ghi + lan truyền" (CUPMem) khớp với đề xuất `supersedes` + hook nhắc lúc ghi của ta; khác ở chỗ họ làm bằng cấu trúc trạng thái, ta làm bằng frontmatter + lint.
- Bằng chứng KG hơn hẳn hybrid cho *tra cứu một bước* là **yếu**; cho multi-hop là **có**. Quyết định phải dựa phân loại câu trượt của ta.
- Có biến thể graph không token (đồng xuất hiện NER + PPR) — hợp H-10 hơn Graphiti; đáng đọc kỹ trước khi quyết.

## 5. Vị thế hai phía (để phiên sau duyệt)

| Điểm | Bi | Claude |
|---|---|---|
| Chất lượng truy xuất KG | Tốt hơn rất nhiều | Chưa chứng minh cho câu một bước; có cho multi-hop |
| Entity resolution | (đồng ý đó là khó nhất) | Là chỗ chất lượng thắng/thua |
| Kho phi cấu trúc | (đồng ý) | Nhiễu nhất, graph dựng từ đó nhiễu theo |
| Thay kiến thức cũ | Cần có cơ chế | `supersedes` tường minh + nhắc lúc ghi; STALE xác nhận máy/agent tự phát hiện còn kém |
| Cách phân xử | Đồng ý đo, muốn tham khảo research | Đo trên bộ câu thật, so 4 cấu hình |

## 6. Việc chưa biết (cần đo trước khi chọn)

1. 10 câu trượt thuộc loại nào: một bước / hai bước / nhiều bước? (mở `company/eval/recall/cases.toml`).
2. Mật độ link tường minh trong sổ tay; số doc mồ côi.
3. Phần nào của 10 câu trượt là lỗ *từ vựng* (cần đồng nghĩa/vector) và phần nào là lỗ *quan hệ* (cần graph).
4. Bao nhiêu `feedback_*`/doc hiện có cặp mâu thuẫn ngầm? (kiểm tay vài chục cặp để có tỉ lệ nền).

## 7. Đề xuất thí nghiệm (chưa chạy)

Bộ câu: 20 câu hiện có + ~10 câu multi-hop thật ("ADR nào chi phối file này", "việc nào đã đổi module này", "quyết định X thay quyết định nào").
Bốn cấu hình trên cùng bộ câu, đo recall@12 + `cũ@12`:
1. BM25 (hiện tại).
2. BM25 + mở rộng theo link/git (link graph rẻ).
3. BM25 + vector (RRF), sqlite-vec + model đa ngữ nhỏ cục bộ.
4. Graph có LLM trích xuất trên một phần kho (chạy theo lô lúc build, kết quả commit vào git để duyệt; tốn tiền → Bi duyệt theo `policy.toml`).
Mở rộng: thêm biến thể 5 = SPRIG-like (NER đồng xuất hiện + PPR, 0 token). Thêm bộ **STALE-nhỏ nội bộ**: 10–15 cặp "quyết định mới thay cũ" có thật trong lịch sử repo để đo `cũ@12` và tỉ lệ agent bắt được khi ghi.

Tiêu chí: nếu graph có LLM thắng rõ → dùng (LLM theo lô, không lúc ghi); nếu câu trượt chủ yếu một bước và graph không hơn vector → hướng vector. Cổng vector "14 ngày đưa-sẵn" trong `memory-options.md` PA2.4 cần xem lại: nó chặn thí nghiệm 3 mà không có lý do chất lượng.

## 8. Đề xuất kiến trúc cho phiên refactor (chờ duyệt)

Ưu tiên theo giá trị / chi phí:
1. **Hook `UserPromptSubmit`** chạy `recall.hint()` trên câu hỏi (≈ 24 ms, 0 token model, ≤ 600 token in). Đóng lỗ #1–2.
2. **Vòng thay thế lúc ghi:** (A) sửa tại chỗ, một chủ đề một file sống; (B) frontmatter `status` + `supersedes` cho ADR/memory cần giữ lý do; (C) hook nhắc lúc ghi (3 đoạn gần nhất, agent điền `supersedes` hoặc `none`); (E) lint cặp gần nhau không có quan hệ; (D) xếp hạng theo ngày làm lưới. Áp cho cả memory tầng 1.
3. **PA2.3 nhãn `có thể cũ`** bằng cạnh commit→file (phần "cũ do file đổi").
4. **Đo:** `inject_rate`, lần mở transcript thô, `cũ@12` → `kit weekly`; thêm bộ STALE-nhỏ.
5. **Lint ranh giới tầng 1 / tầng 2** (memory chứa trạng thái dự án → báo).
6. Quyết graph / vector **sau** thí nghiệm mục 7, không trước.

## 9. Câu hỏi mở cho Bi

- Chấp nhận ép agent khai báo `supersedes` lúc ghi (thêm một bước, đổi lại bớt cũ)?
- Sẵn sàng chi tiền cho bước LLM-theo-lô trong thí nghiệm 4?
- Đưa memory tầng 1 vào cùng cơ chế `supersedes`, hay giữ tách?
- Có muốn cổng PA2.4 (14 ngày) giữ nguyên hay mở sớm để chạy thí nghiệm vector?

## Nguồn
- Zep: A Temporal Knowledge Graph Architecture for Agent Memory — https://arxiv.org/abs/2501.13956
- STALE: Can LLM Agents Know When Their Memories Are No Longer Valid? — https://arxiv.org/abs/2605.06527
- Democratizing GraphRAG (SPRIG) — https://arxiv.org/abs/2602.23372
- Graph-Based Personalized Memory for LLM Agents (survey) — https://arxiv.org/abs/2609.08599
- Governing Evolving Memory in LLM Agents (SSGM) — https://arxiv.org/abs/2603.11768
- From BM25 to Corrective RAG — https://arxiv.org/pdf/2604.01733
- MemGPT (chỉ có mục tham chiếu, chưa đọc nội dung) — arXiv 2310.08560
