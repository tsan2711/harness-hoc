# 05e — Graph-RAG: dùng đồ thị trong bước tìm, và khi nào nó thắng

> Trả lời câu Bi hỏi ở vòng 5: "graph-RAG là gì" + luận điểm 2 (một bước vs nhiều bước). Trước đó: [05d](05d-knowledge-graph.md), [05c](05c-hybrid-rrf-reranker.md).

## 1. Câu chuyện

Ba câu hỏi gửi cho cùng một kho:
1. "Vì sao bỏ RenderMeshInstanced?" — đáp án nằm trong **một** ghi chú.
2. "Việc nào đã sửa file mà ADR-0028 chi phối?" — phải nối **ADR → file → việc**: ba đoạn khác nhau.
3. "Ba rủi ro lớn nhất của harness hiện nay là gì?" — không đoạn nào chứa; phải **tổng hợp cả kho**.

## 2. Dừng 30 giây
- Với câu 2, BM25 tìm "ADR-0028" ra đoạn ADR. Bước tiếp theo nó làm được không?
- Với câu 3, lấy 12 đoạn gần nhất rồi đưa LLM có đủ không?
- Bộ câu đo của Seriously (45 câu) có câu loại 2 hay 3 nào không? (Đáp án ở mục 7.)

## 3. RAG nhắc lại
**RAG** = Retrieval-Augmented Generation: *tìm* đoạn liên quan → *nhét* vào ngữ cảnh → LLM *trả lời*. Chất lượng trả lời bị chặn trên bởi chất lượng tìm.
"Graph-RAG" = RAG mà bước tìm dùng đồ thị. Không phải một thuật toán, mà là một họ.

## 4. Ba loại câu và ai thắng

| Loại | Đặc điểm | Ví dụ | Ai thường thắng |
|---|---|---|---|
| **Một bước** (single-hop) | đáp án trong 1 đoạn | câu 1 | BM25 (nếu trùng chữ), vector/hybrid (nếu khác chữ). Graph không hơn |
| **Nhiều bước** (multi-hop) | phải nối 2+ đoạn qua thực thể trung gian | câu 2 | Graph (đi cạnh), hoặc tìm lặp nhiều vòng |
| **Toàn cục** (global sensemaking) | tổng hợp cả kho | câu 3 | GraphRAG kiểu tóm tắt cụm |

Vì sao tìm thường trượt câu nhiều bước: đoạn "việc 45 sửa kit.sh" **không nhắc ADR-0028**, nên nó không gần câu hỏi theo chữ hay theo nghĩa.
Chỉ tới được bằng cách đi qua `kit.sh` — tức là theo cạnh.

Thay thế không cần graph cho câu nhiều bước: **tìm lặp** (agent tìm → đọc → tìm tiếp với thực thể vừa thấy). Agent Claude Code vốn làm vậy bằng grep.
Chậm hơn, tốn token hơn, nhưng không cần dựng gì.

## 5. Các biến thể graph-RAG

### 5.1 Microsoft GraphRAG (đầy đủ, đắt)
Dựng: cắt kho → LLM đọc từng đoạn, rút thực thể + quan hệ (+ "claim") → gộp thành đồ thị → **phát hiện cộng đồng** (thuật toán Leiden: chia đồ thị thành
cụm nút dính nhau, nhiều tầng) → LLM viết **tóm tắt cho từng cụm**.
Hỏi:
- *Local search:* tìm thực thể trong câu hỏi → lấy láng giềng, quan hệ, đoạn gốc → LLM trả lời.
- *Global search:* map-reduce qua các tóm tắt cụm → trả câu toàn cục (câu 3).
Mạnh nhất ở câu toàn cục. Chi phí: nhiều lần gọi LLM cho *mỗi* đoạn lúc dựng; kho đổi thì phải dựng lại phần đổi. Trái H-10 trực tiếp.

### 5.2 HippoRAG (PPR trên đồ thị trích bằng LLM)
(Theo hiểu biết người viết, chưa tra lại trong phiên này.) Lấy cảm hứng từ hồi hải mã: LLM rút bộ ba kiểu OpenIE từ mỗi đoạn → đồ thị; khi hỏi, thực thể
trong câu hỏi làm hạt giống → **Personalized PageRank** ([05d](05d-knowledge-graph.md) §6) → đoạn chứa các nút điểm cao. Mạnh ở multi-hop với một lần tìm.

### 5.3 SPRIG (không token, CPU) — arXiv 2602.23372
Thay LLM bằng **NER + đồng xuất hiện** (hai thực thể cùng đoạn → cạnh), hạt giống từ BM25, đi bằng PPR. Chạy CPU, thời gian tuyến tính, 0 token.
Abstract nói: xác định *khi nào* cách này giúp multi-hop và *khi nào* hybrid RRF đã đủ; một nguồn thứ cấp nói nó hơn BM25 trên 2WikiMultiHopQA nhưng
không hơn RRF trên HotpotQA. → Ngay cả graph tốt cũng **không thắng hybrid ở mọi nơi**.
Đây là biến thể hợp harness ta nhất (0 token, dựng lại tất định).

### 5.4 Graph-mở-rộng (cái "link graph" của vòng 2)
Không thay bước tìm: hybrid tìm như thường → lấy láng giềng 1 bước theo cạnh **tất định** (file, việc, ADR) → đưa thêm 1–2 đoạn. Rẻ nhất, cải câu nhiều bước loại
"cái gì chi phối / ai đã sửa".

## 6. Nghiên cứu nói gì (vòng 6)
- GraphRAG hơn RAG trơn ở multi-hop (một bài 2026 thấy khoảng cách lớn nhất ở MuSiQue 4 bước) — **nhưng so với vector trơn, không so với hybrid**.
- Tổng hợp thứ cấp: graph giúp multi-hop và tổng hợp, thường **thua** RAG thường ở tra chi tiết.
- Chưa có benchmark nào so GraphRAG / hybrid / multi-hop dưới **cùng một thiết lập** → phải đo trên kho của mình.

## 7. Áp vào tranh luận (luận điểm 2)

Đáp câu 3 mục 2: bộ đo `company/eval/recall/cases.toml` có 45 câu, 43 câu đúng 1 tài liệu đáp án; mọi câu diễn đạt lại là **một bước**. 10 câu trượt là lỗ từ vựng.
→ Trên bộ này graph không có đất. Nhưng bộ này **không có câu loại 2 và 3**, nên nó cũng không thể nói graph vô dụng. Câu hỏi thật: **Bi và agent có hay hỏi loại 2, 3 không?**
Ví dụ có thể có ích trong harness:
- "Sửa file này có phạm ADR nào không?" (pre-commit có thể tự hỏi)
- "Lần cuối ai/việc nào đụng module này, vì sao?"
- "Quyết định X đã thay quyết định nào, còn chỗ nào dựa vào cái cũ?" (lan truyền — [05f](05f-ky-uc-cu-va-thay-the.md))
- "Rủi ro lớn của harness tuần này?" (toàn cục — hiện do `kit weekly` + người đọc)

## 8. Bảng chọn

| Nếu câu của bạn chủ yếu là… | Dùng | Chi phí |
|---|---|---|
| một bước, trùng chữ | BM25 | ~0 |
| một bước, khác chữ | hybrid BM25 + vector (+ reranker) | CPU |
| nhiều bước qua quan hệ đã ghi | hybrid + mở rộng link graph tất định | ~0 |
| nhiều bước qua quan hệ ngầm | SPRIG-like (NER + PPR) → HippoRAG | CPU → token |
| toàn cục | GraphRAG tóm tắt cụm, hoặc báo cáo định kỳ viết sẵn | token cao |

## 9. Scale
- Nhỏ: tìm lặp bằng agent thay được graph.
- Vừa: câu nhiều bước bắt đầu đắt khi tìm lặp (nhiều vòng × token) → link graph đáng tiền.
- Lớn: câu toàn cục không thể trả bằng 12 đoạn → tóm tắt cụm hoặc báo cáo tổng hợp định kỳ.

## 10. Bốn nền tảng
Như 05d §10: SQLite + PPR (toán ma trận thưa, CPU) chạy được mọi nơi; GraphRAG đầy đủ cần LLM → cloud/desktop mạnh.

## 11. Tóm tắt
Graph-RAG = đồ thị trong bước tìm; thắng ở câu nhiều bước và toàn cục, không hơn hybrid ở câu một bước. Chọn theo **loại câu**, không theo độ "xịn".

**Thuật ngữ:** RAG · single/multi-hop · global sensemaking · community detection (Leiden) · local/global search · OpenIE · iterative retrieval.
**Bài sau:** [05f — kiến thức cũ](05f-ky-uc-cu-va-thay-the.md).
