# 05 — Tranh luận: có nên dựng knowledge graph cho bộ nhớ harness? (biên bản đủ vòng đời)

> **Đọc thế nào:** bài này kể lại *toàn bộ* cuộc tranh luận ngày 2026-10-20 giữa Bi và Claude — từng vòng: câu hỏi, lập trường,
> lập luận, chỗ bị khoét, ai nhận sai, kết quả, và **khái niệm phải hiểu để theo được vòng đó** (link sang bài 05a–05g).
> Nếu gặp từ lạ, mở bài khái niệm trước rồi quay lại.
>
> Bản quyết định (agent dùng khi refactor): `Seriously/docs/shared/memory-debate-2026-10-20.md`. Bài này là bản *học*.

**Các bài khái niệm đi kèm**

| Bài | Khái niệm | Cần cho vòng |
|---|---|---|
| [05a](05a-bm25-va-fts5.md) | BM25, FTS5, bỏ dấu, AND/OR, đồng nghĩa — cái `recall` đang dùng | 1, 2, 5, 6 |
| [05b](05b-embedding-va-vector.md) | Embedding, cosine, vector search, chunking, model cục bộ | 4, 5 |
| [05c](05c-hybrid-rrf-reranker.md) | Hybrid, RRF, reranker | 4, 5 |
| [05d](05d-knowledge-graph.md) | Knowledge graph, nút/cạnh, entity resolution, Personalized PageRank | 2, 5 |
| [05e](05e-graph-rag.md) | Graph-RAG (Microsoft GraphRAG, HippoRAG, SPRIG), một bước vs nhiều bước vs toàn cục | 5, 6 |
| [05f](05f-ky-uc-cu-va-thay-the.md) | Kiến thức cũ, thay thế, trục thời gian (bitemporal), STALE, lan truyền | 3, 4, 6 |
| [05g](05g-do-truy-hoi.md) | Đo truy hồi: recall@k, bộ vàng, khoảng tin cậy, rò rỉ, thí nghiệm công bằng | 5, 6, 7 |

---

## 0. Bối cảnh: hệ thống trước khi tranh luận

Model không có trí nhớ giữa các phiên (xem bài 01). Harness Seriously "nhớ" bằng 4 tầng:

| Tầng | Là gì | Ai đưa vào ngữ cảnh |
|---|---|---|
| 1. Memory Claude Code | `~/.claude-zzd/.../memory/*.md` + `MEMORY.md` (~1k token). Chỉ thứ về **Bi** và **cách làm việc** | tự động mỗi phiên |
| 2. Sổ tay trong git | `CLAUDE.md` → `docs/ai/INDEX.md` → `.claude/rules/` → `depts/*/knowledge/` | agent đi theo mục lục |
| 3. `kit recall` | `tools/claude/recall.py`: chỉ mục SQLite FTS5 trên transcript + sổ tay + git log + biên bản việc. Xếp hạng BM25 ([05a](05a-bm25-va-fts5.md)) | agent phải **tự gọi** |
| 4. Bàn giao | `leftover.py` (hook), `recall.hint()` khi nhận việc inbox (≤ 3 đoạn) | hook |

Số đo hôm đó (`recall_eval`, [05g](05g-do-truy-hoi.md)): hỏi đúng từ khoá **20/20**; hỏi bằng cách nói khác (*diễn đạt lại*) **10/20**;
`cũ@12 = 2` (2 đoạn cũ lọt top 12).

---

## Vòng 1 — "Hỏi kiến thức thì agent có phải tự tìm không?"

**Bi hỏi:** khi tôi hỏi kiến thức, hoặc agent cần đọc cái đã có, thì sao — nó phải tìm à?

**Claude trả lời:** đúng, phải tự tìm, qua 3 đường:
1. **Mục lục (INDEX)** — chắc nhất, nhưng chỉ khi kiến thức được ghi đúng chỗ *và* agent chịu đọc INDEX trước khi trả lời.
2. **Grep / subagent Explore** — tốn token, hên xui (phải đoán đúng từ).
3. **`kit recall`** — cho "chuyện cũ" (đã bàn/quyết gì), agent phải tự gọi; đo 15/10: phiên thường gần như không gọi.

**Phát hiện:** hỏi kiến thức *giữa phiên* (không qua inbox) thì **không có gì tự đưa kiến thức tới agent**. Agent trả lời đúng hay
không phụ thuộc may mắn.

**Đề xuất sinh ra:** hook `UserPromptSubmit` — mỗi khi Bi gửi câu hỏi, script chạy `recall.hint()` trên câu đó (~24 ms, 0 token model)
và in ≤ 3 đoạn liên quan trước khi agent nghĩ. (Đây là ý *đẩy* thay vì *chờ kéo*: xem bài 01 mục "lấy lại thế nào".)

**Kiến thức rút ra:** một kho nhớ tốt mà không ai gọi = không có kho. Câu hỏi "lưu thế nào" luôn đi kèm "ai, lúc nào đưa nó ra".

---

## Vòng 2 — "Dựng knowledge graph có hợp harness không?"

**Bi hỏi:** xây một biến thể knowledge graph (KG) phù hợp harness thì thế nào?

**Khái niệm cần:** KG = nút (file, ADR, việc, khái niệm) + cạnh có nhãn (`ADR-12 —chi phối→ kit.sh`). [05d](05d-knowledge-graph.md).

**Claude trả lời — chia hai loại:**

| Loại | Cách dựng cạnh | Hợp harness? | Vì sao |
|---|---|---|---|
| KG kiểu Graphiti / mem0 | LLM đọc văn bản, tự trích thực thể + quan hệ **lúc ghi** | Không | Tốn token mỗi lần ghi; kết quả không tất định (chạy lại ra khác); dữ liệu ngoài git → không review, nhiều phiên song song khó (luật H-10) |
| *Link graph* tất định | Script lấy cạnh từ thứ **đã có cấu trúc**: link markdown, trailer `Task:` ↔ commit ↔ file, `git log --name-only`, `unit.toml` | Có | 0 token, chạy lại ra y hệt, nằm cùng `recall.sqlite` |

Link graph hữu ích cho: (1) nhãn "có thể cũ" (cạnh commit→file); (2) mở rộng kết quả theo hàng xóm; (3) lint doc mồ côi;
(4) câu hỏi quan hệ ("việc nào đã đụng file này").

**Chỗ yếu (sẽ bị khoét ở vòng 5):** Claude loại KG-LLM bằng lý do *vận hành* (H-10), chưa nói gì về *chất lượng tìm*.

---

## Vòng 3 — "KG có giải quyết được kiến thức cũ khi có kiến thức mới chưa?"

**Bi hỏi:** kiến thức mới liên quan tới memory cũ và cần thay thế, để thuật toán không đẩy thông tin cũ lên. Graph giải quyết chưa?

**Khái niệm cần:** [05f](05f-ky-uc-cu-va-thay-the.md) — hai kiểu "cũ".

**Claude trả lời — chỉ một nửa:**

| Kiểu cũ | Ví dụ | Máy tự biết? |
|---|---|---|
| **Cũ vì file đổi** | Ghi chú tả `kit.sh` có 3 lệnh; hôm sau `kit.sh` có 5 | Có — git biết file đổi sau ngày ghi chú |
| **Cũ vì quyết định đổi** | Ghi chú cũ "dùng RenderMeshInstanced"; Bi chốt "bỏ, dùng VFX Graph". Không file nào bị sửa | Không — cần *hiểu nghĩa* mới biết hai câu mâu thuẫn |

Graph chỉ *lưu* cạnh "thay thế"; nó không tự *sinh* ra cạnh đó. Cần một **hành động tường minh lúc ghi**:
1. Trường `supersedes: [file cũ]` trong frontmatter.
2. Hook nhắc lúc ghi: recall in 3 đoạn gần nhất với nội dung mới → agent điền `supersedes` hoặc ghi `supersedes: none` (đã xét).
3. Xếp hạng/lint theo cạnh: đoạn bị thay → hạ đáy hoặc nhãn "đã thay bởi X".

**Kiến thức rút ra:** *phát hiện* mâu thuẫn và *lưu* mâu thuẫn là hai việc khác nhau. Cấu trúc dữ liệu (graph hay bảng) chỉ làm việc thứ hai.

---

## Vòng 4 — "Không dùng KG thì có giải được không? Hay KG là hiệu quả nhất?"

**Claude trả lời:** giải được; lời giải vòng 3 không cần graph — một dòng frontmatter hay một bảng SQLite cũng lưu được cạnh.
Mọi cách đều phải qua hai bước: **phát hiện** (máy làm được, bằng recall) → **phán quyết** (cần hiểu nghĩa: agent hoặc người).

Thang 6 cách, rẻ → đắt:

| | Cách | Bản chất | Mạnh | Yếu |
|---|---|---|---|---|
| A | **Sửa tại chỗ**, một chủ đề một file sống | Không giữ bản cũ (git giữ lịch sử) | Triệt để: không còn bản cũ để lọt | Mất "vì sao trước kia khác" nếu không ghi |
| B | Frontmatter `status` / `supersedes` | Giữ bản cũ, đánh dấu | Giữ lý do lịch sử (ADR) | Phải nhớ đánh dấu |
| C | Hook nhắc lúc ghi | Ép agent xét 3 đoạn gần nhất | Bắt đúng lúc ngữ cảnh còn nóng | Agent vẫn có thể xét sai |
| D | Xếp theo ngày | Mới hơn đứng trên | Gần như miễn phí | Thô: đoạn mới chưa chắc liên quan |
| E | Lint cặp gần nhau | Hai doc rất giống mà không có cạnh → cảnh báo | Bắt trùng ngầm | Báo nhầm |
| F | KG + LLM tự phát hiện | Máy tự đóng cạnh cũ | Tự động nhất | Đắt; sai không đoán được; ngoài git |

Đề xuất: A+B+C+E, D làm lưới; F chỉ khi có bằng chứng các cách kia để lọt nhiều.

---

## Vòng 5 — Bi phản biện: "KG đẩy ra kiến thức liên quan **chất lượng tốt hơn rất nhiều**"

Bi yêu cầu Claude đóng vai đối thủ, khoét chỗ yếu, nhưng hợp lý; thấy Bi đúng thì thống nhất.

### 5.1 Claude nhận sai trước (2 điểm)
1. **Lẫn hai loại lý lẽ.** Loại KG bằng H-10 (chi phí, git) là lý lẽ *ràng buộc*. Bi đang nói *chất lượng*. Ràng buộc không chứng minh chất lượng kém.
   → *Bài học tranh luận:* tách "nó tốt không?" khỏi "ta có kham nổi không?". Gộp hai câu là cách thắng tranh luận mà không đúng.
2. **Nói quá "graph không sửa được lỗ diễn đạt lại".** Nếu nhiều cách nói ("cuốn nhầm thay đổi phiên khác", "stash mất file")
   cùng trỏ về một nút, truy vấn diễn đạt lại sẽ trúng. Graph *có thể* sửa — với điều kiện gộp thực thể tốt.

### 5.2 Claude phản biện (3 luận điểm)
1. **Chất lượng KG nằm hết ở entity resolution (gộp thực thể).** Muốn "cuốn nhầm" và "stash" về một nút, phải có thứ *hiểu nghĩa*:
   LLM, từ điển tay, hoặc embedding. Dùng embedding → ta đã quay về vector ([05b](05b-embedding-va-vector.md)). Dùng LLM → độ đúng của
   graph = độ đúng của LLM lúc trích, và **gộp nhầm thì im lặng** kéo kiến thức lạc đề vào kết quả. ([05d](05d-knowledge-graph.md) §4)
2. **10 câu trượt là loại câu nào?** Graph mạnh ở câu **nhiều bước** (multi-hop: phải nối 2–3 đoạn) và câu **toàn cục**. Ở câu **một bước**
   (đáp án nằm trong một đoạn), hybrid BM25 + vector thường ngang. Nếu câu trượt của ta là một bước, graph là thuốc sai bệnh. ([05e](05e-graph-rag.md))
3. **"Tốt hơn rất nhiều" là giả định chưa đo.** Kho nhỏ, có cấu trúc; cạnh quan trọng đã nằm trong link/đường dẫn. Phần phi cấu trúc
   (transcript) nhiễu nhất — graph dựng từ đó nhiễu theo.

### 5.3 Claude tự soi
Chưa đo mật độ link; chưa chạy vector hay graph để so với 50 %; nếu Bi đúng thì cản = mất cơ hội thật.

### 5.4 Bi đáp
- Luận điểm **1: đồng ý** (gộp thực thể là cốt lõi và khó nhất).
- Luận điểm **3: đồng ý**.
- Luận điểm **2: chưa hiểu** (graph-RAG là gì, BM25 + vector là gì) → yêu cầu bài giảng → [05a](05a-bm25-va-fts5.md)–[05e](05e-graph-rag.md).
- Đề xuất cách hay hơn đoán: **tra nghiên cứu đã có** về đúng vấn đề này → vòng 6.

---

## Vòng 6 — Tra nghiên cứu: người khác đã gặp gì?

Tra 2026-10-20. Mức tin ghi rõ; "abstract" = mới đọc tóm tắt, chưa đọc cả bài.

| Nguồn | Kết luận chính | Liên quan vòng | Mức tin |
|---|---|---|---|
| **STALE** (arXiv 2605.06527) | Đặt tên đúng bài toán vòng 3: **implicit conflict** — thông tin mới làm ký ức cũ sai *mà không ai nói "cái cũ sai rồi"*. 400 kịch bản, 1.200 câu, 3 trục. **Model tốt nhất 55,2 %.** Lỗi: tin tiền đề cũ, không lan cập nhật sang ký ức liên quan, lấy được tin mới mà hành vi không đổi. Đề xuất CUPMem: sửa lúc ghi + tìm có lan truyền | 3, 4 | abstract |
| **Zep / Graphiti** (2501.13956) | KG có trục thời gian cho memory agent. DMR 94,8 % vs MemGPT 93,4 %; LongMemEval +tới 18,5 %, độ trễ −90 % | 2, 3 | số: abstract. Cơ chế đóng cạnh cũ: **chỉ nguồn thứ cấp** |
| **SPRIG** (2602.23372) | Graph-RAG **không token, chạy CPU**: đồ thị đồng xuất hiện từ nhận diện thực thể (NER) + Personalized PageRank; so với RRF hybrid; xác định khi nào graph giúp multi-hop, khi nào hybrid đủ | 2, 5 | abstract (số bị cắt) |
| Survey graph memory (2609.08599) | Phân loại xung đột: *thay theo thời gian / người dùng sửa / cùng tồn tại* — đừng gộp thành "mới nhất thắng" | 3, 4 | **snippet, chưa xác minh** |
| SSGM (2603.11768) | Lọc nhất quán quá chặt → kiến thức **đóng cứng** (ossification); phân biệt "trôi" với "cập nhật hợp lệ" còn mở | 4 | snippet |
| So sánh BM25 / hybrid / GraphRAG (2602.23372, 2604.01733, blog) | BM25 và hybrid RRF là baseline mạnh; GraphRAG thắng multi-hop + toàn cục, thường thua tra chi tiết; **chưa có benchmark so cả ba dưới cùng thiết lập** | 5 | thứ cấp |

**Rút ra:**
1. Bài toán vòng 3 có tên, có benchmark, và **khó**: 55 % → không thể giao cho agent tự phán quyết mà không có cơ chế ép; cũng không có
   bằng chứng KG tự phát hiện là xong. Hướng CUPMem (sửa lúc ghi) trùng hướng `supersedes` + nhắc lúc ghi.
2. Bằng chứng "KG hơn hybrid" **mạnh ở multi-hop, yếu ở một bước** → phân xử phải nhìn câu của ta.
3. Có graph không token (SPRIG) — hợp H-10 hơn Graphiti. Lý lẽ "KG = phải tốn LLM" của Claude ở vòng 2 **không còn đúng hoàn toàn**.

---

## Vòng 7 — Kiểm lại bằng dữ liệu thật của repo (viết bài này, 2026-10-20)

Khi viết bài này, mở `company/eval/recall/cases.toml` và `recall.py`. Ba phát hiện — hai cái **sửa lời Claude đã nói**:

**7.1 Claude đã nói sai về hiện trạng.**
- Nói "PA2.3 nhãn *có thể cũ* chưa xong" → **sai một phần**: `recall.py` đã có `is_stale()` (đoạn `chuyện` nhắc file đổi sau ngày đoạn → nhãn `cu`)
  và `doc_outdated()` (tiêu đề ghi "đã thay bởi / (cũ) / superseded" → nhãn `cu`). Nhưng chỉ **gắn nhãn, không hạ hạng** — vì hạ hạng làm mất
  3 câu diễn đạt lại (ghi chú trong code). Nên `cũ@12 = 2` là có thật, nhưng agent thấy nhãn.
- Nói "recall chỉ BM25, không biết đồng nghĩa" → **sai một phần**: có `synonyms.toml` 29 nhóm viết tay (vd `icon / biểu tượng / ký hiệu`);
  commit `9290232` nâng diễn đạt lại 45 → 50 % nhờ sửa nhóm.
- *Bài học:* đúng memory `feedback_verify_severity_against_code` — **đọc code trước khi nói về hệ thống**.

**7.2 Luận điểm 2 của Claude: dữ liệu ủng hộ — nhưng vì lý do đáng lo hơn.**
- 45 câu vàng: 43 câu có **đúng 1 tài liệu đáp án**, 2 câu có 2. Mọi câu diễn đạt lại đều **một bước**.
- 10 câu trượt nhìn vào đều là **lỗ từ vựng**: "đóng gói cho điện thoại" ↔ ghi chú viết "Android build"; "chống người chơi sửa dữ liệu lưu" ↔
  "anti-cheat save"; "mô hình nhúng" ↔ "embedding/vector". Không câu nào cần nối nhiều đoạn.
- → Với bộ câu hiện tại, thuốc đúng là đồng nghĩa / vector, **không phải graph**.
- **Nhưng:** bộ vàng **không có một câu nhiều bước nào**. Nó *không thể* cho thấy graph thắng ở đâu — vì không hỏi loại câu graph giỏi.
  Kết luận "graph không cần" từ bộ này là **kết luận méo do thước đo** ([05g](05g-do-truy-hoi.md) §5). Đây là điểm cho Bi.

**7.3 Con số 50 % rung hơn mình tưởng.**
- 20 câu, mỗi câu = 5 điểm %. Khoảng tin cậy 95 % của 10/20 ≈ **30–70 %**. "45 → 50 %" là **1 câu**, không phân biệt được với may rủi.
- Nhóm đồng nghĩa được chỉnh *nhìn vào chính bộ câu này* → **rò rỉ** (tối ưu theo đề thi). Câu mới ngoài bộ có thể tụt.
- → Cần **bộ câu giữ riêng** (held-out) không ai dùng để chỉnh. ([05g](05g-do-truy-hoi.md) §4)

---

## 8. Kết quả: đã thống nhất / còn mở

**Đã thống nhất**
1. Gộp thực thể là chỗ quyết định chất lượng KG, và là phần khó nhất.
2. Phần transcript phi cấu trúc là nguồn nhiễu nhất.
3. "Kiến thức cũ vì quyết định đổi" cần hành động tường minh lúc ghi; máy hay agent tự phát hiện đều kém (STALE 55 %).
4. Phân xử bằng thí nghiệm, không bằng đoán.

**Thay đổi lập trường sau vòng 6–7**
- Claude: lý lẽ "KG = tốn LLM" yếu đi (có SPRIG); lý lẽ "câu trượt là một bước" mạnh lên (dữ liệu) nhưng bộ đo thiếu câu nhiều bước.
- Còn chờ Bi: có giữ "tốt hơn rất nhiều" cho câu *một bước* không, hay thu lại về "tốt hơn ở câu *nhiều bước*"?

**Còn mở**
1. Harness thật sự có bao nhiêu nhu cầu câu nhiều bước? (vd "ADR nào chi phối file này", "việc nào đã sửa module ADR-12 chi phối",
   "quyết định X thay quyết định nào"). Nếu Bi/agent hay hỏi loại này → graph có đất.
2. Có ép agent khai báo `supersedes` lúc ghi không? Memory tầng 1 có dùng chung cơ chế không?
3. Cổng "vector chỉ mở sau 14 ngày đưa-sẵn" (PA2.4) chặn thí nghiệm vector mà không có lý do chất lượng — giữ hay mở?
4. Có chi tiền cho graph-LLM trong thí nghiệm không (cần Bi duyệt)?

## 9. Thí nghiệm phân xử (đề xuất, chưa chạy)

1. **Sửa thước đo trước:** thêm ~10 câu nhiều bước thật + ~15 câu diễn đạt lại *held-out* + 10–15 cặp "quyết định mới thay cũ" có thật
   trong lịch sử repo (bộ "STALE nhỏ").
2. **Cùng bộ câu, 5 cấu hình:** BM25 hiện tại · BM25 + mở rộng link/git · BM25 + vector (RRF) · SPRIG-like (NER + PPR, 0 token) ·
   graph-LLM trên một phần kho (chạy theo lô, kết quả commit vào git).
3. **Chỉ số:** recall@12 theo nhóm (kw / para / multi-hop / stale), `cũ@12`, ms/truy vấn, chi phí dựng.
4. **Luật thắng đặt trước:** cấu hình hơn hybrid ≥ 2 câu ở nhóm multi-hop *và* không tụt nhóm khác → đáng dựng. Ít hơn → không.

## 10. Kiến thức mang đi (dùng được ngoài vụ này)

1. **Tách "tốt không" khỏi "kham nổi không"** khi đánh giá một kỹ thuật.
2. **Hỏi loại câu trước khi chọn công cụ:** một bước → từ vựng (BM25 + đồng nghĩa/vector); nhiều bước → quan hệ (graph); toàn cục → tóm tắt cụm.
3. **Thước đo chỉ thấy cái nó hỏi.** Bộ câu toàn một bước sẽ luôn nói "graph vô dụng".
4. **20 câu là ít:** một câu = 5 %; chênh 1–2 câu là nhiễu.
5. **Phát hiện ≠ lưu:** cấu trúc dữ liệu lưu quan hệ; phát hiện mâu thuẫn cần hiểu nghĩa — đặt nó ở lúc ghi.
6. **Đọc code trước khi phán hệ thống** — Claude nói sai 2 chỗ về hiện trạng trong chính cuộc này.
