# 05 — Đồ thị có model: claim có thời gian, PPR, GraphRAG, LightRAG, và cổng quote

> Bài 5/6. Đọc ~12 phút. **Đã biết:** đồ thị tất định L0/L1, BFS ngược ([04](04-ban-do-quan-he.md)).
> Code thật: `tools/claude/distill.py` (P2, đã có). **Mọi thứ khác trong bài là thiết kế (K3 claim, K5 tóm tắt cụm L4, PPR ở đường đọc §5.2), chưa có code.** Thiết kế: §2, §4, §5.2.

## Chuyện mở đầu

Pilot P2 cho Haiku đọc 14 ngày hội thoại Thousandfold. Ước tính tốn 0,9M token. Đo lúc đầu đã là 4,4M. Lần chạy nền chạy hết 194 cửa sổ
thì ledger lên 6,98M trên trần 8M. Thu được 865 thẻ, 0 thẻ bịa trích dẫn. Nhưng cổng tìm lại ở ×10 không đạt (kw 15/20).
Model làm *đúng* việc, nhưng sai chỗ và quá đắt.

## Dừng 30 giây

Model đọc hội thoại thì nên sinh ra gì: một đoạn tóm tắt, một thẻ, hay một *cạnh* nối hai thực thể đã có? Khi hai thẻ mâu thuẫn ("dùng
cel-shade" ở 10-03, "bỏ cel-shade" ở 10-15), hệ cần biết thêm thông tin gì để trả lời đúng "hiện tại là gì"?

---

## 1. Cổng quote: model đề xuất, luật quyết (đã có — `distill.check`, dòng 105–120)

```python
t, text, quote = card.get('type'), (card.get('text') or '').strip(), (card.get('quote') or '').strip()
if t not in TYPES:                                    # TYPES = decision|fact|gotcha|open|rejected
    return None, 'bad-type'
if not text or len(text) > 280:
    return None, 'text-len'
if not quote or len(quote) > 200 or norm(quote) not in window_text:
    return None, 'quote-not-in-source'               # trích dẫn phải có NGUYÊN VĂN trong cửa sổ đã gửi
ents = [e for e in (card.get('entities') or []) if isinstance(e, str)]
if any(e not in window_text for e in ents):
    return None, 'entity-not-in-source'
```

- **Grounding bằng so khớp chuỗi.** Model phải trả về một trích dẫn, và trích dẫn đó phải là *chuỗi con* (sau `norm`) của văn bản đã gửi.
  Đây là kiểm tra tất định nằm ngoài model, nên tỉ lệ bịa trích dẫn bằng 0 *theo cấu tạo*. Nó không chứng minh *diễn giải* trong `text`
  là đúng. Nó chỉ chứng minh rằng có bằng chứng.
- ID = `sha1(unit + quote)[:10]` (dòng 179). Cùng một trích dẫn thì ra cùng một ID, nên chạy lại là **idempotent** (lặp lại vô hại),
  không sinh thẻ trùng.

**Chi phí: vì sao lệch ×5–×8.** Comment ở dòng 95: `claude -p` mặc định mang **~26k token** gồm danh sách tool và system prompt cho *mỗi
lần gọi*. Phần nội dung chỉ chiếm khoảng 30k/lần (`WINDOW_CHARS = 90 000`). Bản ước tính chỉ đếm phần nội dung. Có hai cách sửa, cả hai
đã vào code:

```python
['claude', '-p', '--model', 'haiku', '--output-format', 'json', '--max-turns', '1', '--tools', '', '--strict-mcp-config',
 '--disable-slash-commands', '--no-session-persistence', '--system-prompt', 'Bạn chỉ trả về các dòng JSON được yêu cầu.']
```

Phần vỏ giảm từ ~26k xuống ~2,6k. Gói nhiều phiên vào một cửa sổ thì số lần gọi giảm từ 194 xuống 29. Bài học tổng quát: **chi phí của
một lệnh gọi LLM = phần cố định × số lần gọi + phần nội dung**. Phải đo phần cố định trước khi ước tính (`--dry-run` cho 0 token).

## 2. Từ thẻ trôi nổi sang claim gắn vào đồ thị (thiết kế K3)

Thẻ P2 là văn bản rời, không có cạnh, và chỉ có một dấu thời gian. Thiết kế đổi đầu ra thành **claim** (mệnh đề):

```toml
[[claim]]
id = "c_8f2a…"                       # sha1(subject ‖ predicate ‖ quote)
subject = "entity:cel_shade"          # BẮT BUỘC là ID đã có trong bảng bí danh (entity linking ở bài 04)
predicate = "rejected"                # enum đóng
object = "doc:Thousandfold/design/gdd/art-bible.md"
quote = "bỏ cel-shade, nhìn như game mobile"
source = "talk:<sid>:<loc>"
valid_from = "2026-10-15"
invalid_at = ""                       # điền khi một claim mới thay thế
supersedes = ["c_31bc…"]
```

**Temporal KG / bi-temporal** (Zep/Graphiti, arXiv 2501.13956): mỗi cạnh mang *thời gian hiệu lực* (`valid_at`/`invalid_at`: sự thật
đúng trong khoảng nào ngoài đời), tách khỏi *thời gian giao dịch* (lúc hệ thống ghi nhận nó). Nhờ vậy, cạnh cũ không bị xoá mà được
**vô hiệu hoá**. Câu "trước đây chọn gì, vì sao đổi" vẫn trả lời được. Thiết kế lấy ý này nhưng làm *trong file git*. Thời gian giao dịch
chính là thời điểm commit, nên git đã cho sẵn.

**Hoà giải** (reconciliation): claim mới có cùng `(subject, predicate-nhóm)` với một claim còn hiệu lực sẽ được đẩy cho model phán đúng
một trong ba: `supersede` (điền `invalid_at` cho claim cũ) / `coexist` / `duplicate` (bỏ). Đầu ra là enum trong schema, có validate.
So với **mem0** (ADD/UPDATE/DELETE/NOOP, arXiv 2504.19413): ở đây không có DELETE, vì mất lịch sử là mất câu trả lời cho "vì sao".

Có ba ràng buộc giúp model không phá được đồ thị:
1. `subject` phải là ID đã có. Model **không tạo thực thể mới**, chỉ được đề xuất bí danh vào một hàng chờ để người duyệt.
2. Cổng quote giữ nguyên như §1.
3. Predicate thuộc enum đóng. Predicate lạ thì loại.

## 3. Personalized PageRank cho câu nhiều bước (thiết kế §5.2, chưa gán pha)

BFS ở bài 04 trả lời "ai *phụ thuộc* X" theo các cạnh có hướng, với số bước cố định. Câu "vì sao vùng 2 tụt perf sau khi đổi grass" cần
*các nút liên quan tới cả hai hạt giống* {vùng 2, grass}, xếp theo mức độ gần.

**Personalized PageRank (PPR)**: một bước đi ngẫu nhiên trên đồ thị. Tại mỗi bước, với xác suất α thì nhảy về một nút hạt giống, còn lại
thì đi theo một cạnh ngẫu nhiên:

```
π = α · s + (1 − α) · Mᵀ π          s = vector hạt giống (chuẩn hoá tổng = 1), M = ma trận chuyển (chuẩn hoá theo hàng)
```

Giải bằng lặp luỹ thừa (power iteration), khoảng 20–50 vòng, mỗi vòng O(E). Nút được nhiều đường ngắn từ *nhiều* hạt giống đi tới sẽ có
π cao. Đó chính là "giao" mềm của các hạt giống.

**HippoRAG** (Gutiérrez et al., arXiv 2405.14831) dùng đúng công thức này: LLM trích bộ ba (triple) để dựng KG khi đánh chỉ mục; lúc
truy vấn, thực thể trong câu hỏi làm hạt giống; PPR xếp hạng các đoạn văn. Bài báo báo cáo cải thiện ở QA nhiều bước (multi-hop) so với
retrieval một bước. *Số cụ thể chưa kiểm lại, không trích.* Thiết kế lấy PPR nhưng dựng KG chủ yếu từ L0/L1 (0 token), với α khoảng 0,15–0,5
và hạt giống là thực thể đã link. Điểm PPR là xác suất, khác thang với BM25, nên gộp bằng RRF (bài 03).

## 4. GraphRAG: tóm tắt cộng đồng cho câu tổng quan (L4, pha K5)

**MS GraphRAG** (Edge et al., arXiv 2404.16130): LLM trích thực thể và quan hệ → **phát hiện cộng đồng** bằng thuật toán Leiden (phân cụm
tối ưu modularity, có phân tầng) → LLM viết một **bản tóm tắt cho từng cộng đồng** → câu hỏi toàn cục được trả lời theo kiểu
*map-reduce*: mỗi tóm tắt sinh một câu trả lời cục bộ, rồi gộp lại. Nó giải quyết lớp câu "chủ đề chính của cả kho là gì", vốn là lớp mà
top-k retrieval không trả lời được vì đáp án nằm rải trên mọi đoạn.

Cái giá là chi phí đánh chỉ mục: LLM phải đọc toàn bộ kho, và mỗi lần kho đổi thì phải tóm tắt lại các cộng đồng bị ảnh hưởng. Ở Seriously,
câu tổng quan ("NanoSwarm đang ở đâu") đã có **bản tóm tắt viết tay**: INDEX, ORG.md. Bộ vàng nhóm `overview` đạt 10/10 bằng M5 + M3 mà
không cần GraphRAG. Vì vậy L4 trong thiết kế bị bó: chỉ tóm tắt cụm (unit × chủ đề) khi ≥ N nút trong cụm đổi, trần ≤ 0,5M tok/tuần, cổng K5 là overview ≥ 70 %
chấm bằng rubric. Phần gom cụm có thể làm bằng Leiden *không cần LLM*.

## 5. LightRAG: cập nhật tăng dần

**LightRAG** (Guo et al., arXiv 2410.05779): đồ thị có hai mức khoá (low-level = thực thể cụ thể, high-level = chủ đề). Điểm chính là
**incremental update**: tài liệu mới chỉ được trích rồi *hợp* (union) nút và cạnh vào đồ thị, không phải dựng lại cộng đồng như GraphRAG.
Thiết kế lấy nguyên tắc này: claim được thêm theo từng phiên (hook Stop), có ledger và ID theo hash nên chạy lại không sinh trùng.
Đồ thị L0/L1 dựng lại tăng dần theo hash của file.

## 6. So sánh và chọn

| Hệ | Dựng đồ thị bằng | Thời gian | Truy vấn | Lấy | Bỏ (lý do H-10) |
|---|---|---|---|---|---|
| Zep/Graphiti | LLM mỗi episode | bi-temporal | hybrid + đồ thị | `valid_from/invalid_at`, không xoá | dịch vụ nền ngoài git; LLM ở đường ghi nóng |
| HippoRAG | LLM trích triple (OpenIE) | không | PPR | PPR với hạt giống là thực thể | trích triple cho mọi đoạn: tốn token, cạnh nhiễu |
| MS GraphRAG | LLM trích + Leiden + tóm tắt | không | local / global map-reduce | tóm tắt theo cụm, có trần (L4) | tóm tắt toàn kho mỗi lần đổi: chi phí đánh chỉ mục |
| LightRAG | LLM trích | không | khoá hai mức | cập nhật tăng dần | — |
| mem0 | LLM rút fact | cập nhật đè | vector (+ graph) | hợp nhất lúc ghi | DELETE làm mất lịch sử |
| **Seriously (thiết kế)** | **L0/L1 luật** + L2 claim có cổng quote | `valid_from/invalid_at` trong git | BFS / PPR + RRF | — | — |

(Mức xác minh: Zep đã đọc abstract ngày 10-20; các hệ còn lại là kiến thức sẵn có về phương pháp, **không trích số benchmark**.)

## Các cách làm và ưu/nhược

| Cách dùng model trong đồ thị | Token | Rủi ro | Khi nào đáng |
|---|---|---|---|
| Không dùng (K1) | 0 | thiếu cạnh ngữ nghĩa ("A mâu thuẫn B") | mặc định |
| Model trích cạnh tự do | cao | bịa, nút trùng, ontology trôi | không bao giờ nếu không có cổng |
| **Model đề xuất claim, luật kiểm** (K3) | trung bình, có trần | diễn giải sai dù quote đúng | khi M4 là kho bị hỏi nhiều mà trả sai |
| Model tóm tắt cộng đồng | rất cao | lỗi thời ngay khi kho đổi | câu toàn cục mà không có tóm tắt viết tay |

## Khi lớn lên

Chi phí model tăng theo *số phiên hội thoại*, không theo cỡ repo. Trần theo ngày (`DAY_CAP_TOK = 400 000`) và trần tổng
(`TOTAL_CAP_TOK = 8 000 000`) được kiểm *trước* mỗi lần gọi. Khi vượt trần thì dừng và ghi log, không âm thầm chạy tiếp (tiêu tiền là việc Bi duyệt).
Số claim tăng thì chuỗi `supersedes` dài ra, và câu "hiện tại là gì" chỉ cần lấy claim có `invalid_at` rỗng. Đây là một lần lọc O(n) theo
subject, và có thể đánh chỉ mục theo subject. PPR trên khoảng 10⁴ nút với scipy sparse vẫn dưới 100 ms (ước tính, chưa đo).

## Tự làm

1. `python3 tools/claude/distill.py --unit Thousandfold --days 3 --dry-run` (0 token): đọc dòng `… cửa sổ, ~N tok vào`. Nhân số cửa sổ với 26k,
   rồi với 2,6k, để thấy phần vỏ chiếm bao nhiêu phần trăm. `distill.py --stats` cho tổng ledger thật.
2. Viết 30 dòng Python tính PPR bằng power iteration trên `company/state/kg/graph.json` (đọc `nodes`, `edges`), với hạt giống là
   `resolve("colour-territory.md")`. So top 10 của PPR với top 10 của `kg impact`. Kết quả nào ít `refs` rác hơn?
3. Lấy 2 thẻ mâu thuẫn trong `company/memory/cards/Thousandfold/*.jsonl` (grep "cel"), viết tay hai claim theo schema ở §2 với `supersedes`.
   Trường nào bạn không điền được từ thẻ? Đó chính là thông tin thẻ P2 đang thiếu.

## Đọc thêm

- Rasmussen et al., *Zep: A Temporal Knowledge Graph Architecture for Agent Memory*, arXiv 2501.13956.
- Gutiérrez et al., *HippoRAG*, arXiv 2405.14831 · Edge et al., *From Local to Global: A Graph RAG Approach*, arXiv 2404.16130.
- Guo et al., *LightRAG*, arXiv 2410.05779 · Traag et al., *From Louvain to Leiden*, Sci. Rep. 2019.
- Haveliwala, *Topic-Sensitive PageRank* (WWW 2002): nguồn gốc của PPR.

> **Một dòng:** model chỉ *đề xuất* claim gắn vào thực thể đã có, có quote kiểm bằng so khớp chuỗi và có thời gian hiệu lực. PPR dùng cho câu nhiều hạt giống. GraphRAG/LightRAG chỉ lấy phần không tốn token. Luôn đo phần chi phí cố định của mỗi lệnh gọi.
> **Bài sau:** [06 — Đo, lộ trình K0–K6, tách repo](06-do-lo-trinh-tach-repo.md)
