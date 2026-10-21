# 07h — Lộ trình pha + cổng: vì sao P0 trước, luật thắng đặt trước

> Chuỗi 07, bài 8/9. Đọc ~10 phút. Cần trước: [07g](07g-thuoc-do.md).

## 1. Câu chuyện

Một phiên refactor hứng khởi: "làm luôn vector + graph-RAG + hook mới trong một lần". Ba ngày sau: recall chậm 300 ms, para lên
2 câu, kw **mất** 1 câu, `cũ↑` từ 0 lên 1. Câu hỏi không ai trả lời được: *cái nào* gây ra cái nào? Vector giúp para hay hook mới
giúp? Kw mất vì RRF hay vì luật xếp mới? Gỡ ra thì gỡ cái gì? Cuối cùng revert cả ba — ba ngày thành 0.

## 2. Dừng 30 giây

- Vì sao phải làm **thước đo** (P0) trước khi làm bất kỳ tính năng nào?
- "Vector tốt hơn" — tốt hơn bao nhiêu thì đáng thêm một model + một phụ thuộc? Ai quyết, và *khi nào* quyết?
- Một lớp đã lên production (đưa-sẵn khi claim) — làm sao biết nó còn cần, sau khi model mạnh hơn?

## 3. Năm pha (bài 06 §3)

| Pha | Làm | Cổng qua pha | Loại |
|---|---|---|---|
| **P0 Thước đo** | `para-heldout`, `multi`, `stale`; recall@3; so từng câu; chỉ số dùng thật vào `kit weekly` | bộ đo chạy trong selftest, có số nền mọi nhóm | nền |
| **P1 Đẩy** | `prompt-hint` + hook `UserPromptSubmit` (07b); lớp `recall-prompt` trong `layers.toml` | < 150 ms p95; 14 ngày: đoạn được dùng > 0, token phiên không tăng rõ | chắc chắn làm |
| **P2 Thay thế lúc ghi** | frontmatter (07c), `edges` (07d), luật xếp (07e), hook C + G, lint E (07f) | `cũ@3` nhóm stale = 0; kw/para không lùi | chắc chắn làm |
| **P3 Vector** | sqlite-vec + model đa ngữ nhỏ cục bộ, RRF ([05c](05c-hybrid-rrf-reranker.md)) | `para-heldout` +≥ 3 câu, kw không lùi, < 300 ms | **thí nghiệm** |
| **P4 Graph-RAG** | (a) mở rộng theo `edges`; (b) SPRIG-like NER + PPR; (c) LLM trích theo lô nếu Bi duyệt tiền | so với **hybrid P3**: `multi` +≥ 2 câu, nhóm khác không lùi ≥ 1 | **thí nghiệm** |

Ghi chú hiện trạng (2026-10-21): một phần P1 đã có — đường **mở phiên có việc dở** (`leftover.recall_line()`, commit `78bb4ec05`,
2026-10-16). Chưa có: đường câu hỏi giữa phiên.

## 4. Vì sao P0 trước — câu hỏi 1

Không có `multi` thì P4 không có gì để thắng — graph-RAG hứa giúp câu nhiều bước, và bộ đo hiện tại có **0** câu nhiều bước. Không có
`para-heldout` thì P3 "thắng" bằng cách nào cũng được (rò rỉ, 07g). Không có recall@3 thì P1 không biết đoạn đẩy có đúng đoạn không.
Làm tính năng trước thước đo = tự chấm bài mình bằng đề mình ra *sau khi* làm bài.

P1 và P2 không phụ thuộc kết quả tranh luận KG ([05](05-tranh-luan-kg-vs-recall.md)) — cả hai phía đều cần đẩy và cần cạnh thay thế. Nên
làm được ngay sau P0, không phải chờ.

## 5. Luật thắng đặt trước — câu hỏi 2

Cổng P3 viết **trước** khi chạy thí nghiệm: "+≥ 3 câu para-heldout, kw không lùi, < 300 ms". Vì sao phải viết trước:
- **Chống dời cột gôn.** Chạy xong thấy +2 câu, rất dễ tự nhủ "2 cũng tốt". Có luật trước thì +2 = không qua, hết bàn.
- **Gắn với chi phí.** +3 câu trên ~20 câu held-out ≈ +15 % — đủ lớn để vượt nhiễu (07g §4) và đáng một model + một phụ thuộc
  + 300 ms. Ngưỡng thấp hơn thì chưa chắc là thật.
- **So đúng đối thủ.** P4 so với *hybrid P3*, không với BM25 trần — nếu không, graph-RAG được "ăn" công của vector.

Bài 06 cũng **thay** cổng cũ PA2.4 ("vector chỉ sau 14 ngày đưa-sẵn") bằng cổng P3: cổng cũ đo *thời gian trôi*, không đo *chất lượng
tìm*. Một cổng tốt hỏi "nó có làm tốt hơn không", không hỏi "đã chờ đủ chưa".

## 6. Ablation và rollback qua `layers.toml` — câu hỏi 3

**Ablation (cắt bỏ để đo):** tắt *một* thành phần, giữ nguyên mọi thứ khác, xem số đổi. Chính là thứ phiên trong câu chuyện thiếu —
làm ba thứ cùng lúc thì không cắt riêng được. Một pha = một thay đổi đo được.

Seriously có cơ chế ablation cho lớp đã lên production:
- `company/layers.toml`: mỗi lớp có `metric`, `review_by`, và nếu là **nạng** (`crutch = true`) thì có `remove_test`. Lớp `recall-inject`:
  *"tắt đưa-sẵn 14 ngày: so token tới `check:` xanh + số lần mở transcript thô; không tệ đi → bỏ"*.
- `kit company crutch-test recall-inject --days 14` ghi `off_until` vào khối đó; `layerflag.off('recall-inject')` ở đầu `hint()` trả
  `''` → lớp tắt mà **không sửa code**. `--report` so số vấp (`friction.jsonl`) trong cửa sổ tắt với cửa sổ trước, cho phán quyết.
- `crutch-test list` nhắc "cần thử tháo" khi `company/models.toml` đổi sau lần thử cuối — model mới có thể không cần nạng nữa.

Mỗi pha mới phải vào `layers.toml` cùng lúc với code (đầu file: "Không có số đo → không thêm"). P1 thêm lớp `recall-prompt` có
`remove_test` — để mai này gỡ được bằng một lệnh.

## 7. Các cách triển khai, trên câu chuyện

| Cách | Biết cái gì gây ra gì? | Gỡ được từng phần? | Gãy khi |
|---|---|---|---|
| A. Làm hết một lần | ✗ | ✗ (revert cả) | luôn, khi có một chỉ số lùi |
| B. Từng pha, không cổng | một phần | ✓ | "thấy ổn" thay cho số; dời cột gôn |
| C. Từng pha + cổng viết trước | ✓ | ✓ | thước đo yếu (→ nên P0 trước) |
| D. C + lớp trong `layers.toml` + remove_test | ✓ | ✓ bằng 1 lệnh, cả sau khi ship | quên đăng ký lớp |

**Quy luật:** đo trước, đổi một thứ một lần, đặt luật thắng trước khi biết kết quả, và để mọi lớp có công tắc tắt + ngày xét lại.

## 8. Scale

- **Nhỏ** (một người, vài tính năng): pha + cổng có thể chỉ là một dòng ghi chú.
- **Vừa** (Seriously: nhiều phiên agent song song đụng `recall.py`): pha + cổng là cách duy nhất để hai phiên không phá số của nhau; cổng
  lùi trong `kit selftest` bắt ngay lúc commit.
- **Lớn** (nhiều đội, nhiều thí nghiệm cùng lúc): thí nghiệm chồng nhau làm ablation nhiễu; cần cờ tính năng theo nhóm và lịch thí
  nghiệm. Cái vỡ là **khả năng quy nguyên nhân**.

## 9. Dừng lần hai — mở Seriously kiểm chứng

- `company/layers.toml` đầu file (luật "không có số đo → không thêm") và khối `recall` / `recall-inject`.
- `tools/company/crutch.py` docstring: `list`, `<id> --days`, `--report`, `--end`, `GRACE = 1.25`.
- `tools/claude/layerflag.py` `off()`: đọc `off_until`, lỗi file = "bật".
- `tools/claude/recall_eval.py` `gate()`: cổng lùi so với `baseline.json` — chỗ cổng P2 ("kw/para không lùi") sẽ sống.
- `docs/shared/memory-architecture-proposal.md` §3 — bản sống của bảng pha.

## 10. Bốn nền tảng

Pha + cổng là quy trình, không phụ thuộc nền tảng — nhưng **số** của cổng thì có: cổng "< 150 ms" / "< 300 ms" phải ghi đo trên máy
nào (Windows thường chậm hơn Mac ở khởi động tiến trình, 07b). Trên **iOS / Android** đây chính là **staged rollout + feature flag**:
Google Play cho phát hành theo %, App Store có phased release 7 ngày; remote config (Firebase) là `layers.toml` của game — tắt tính năng
không cần bản build mới, và luật "giữ / gỡ" đặt trước khi mở cho 100 %.

## 11. Tóm tắt một dòng

P0 đo trước; P1–P2 làm chắc; P3–P4 là thí nghiệm có luật thắng viết trước, so với đối thủ mạnh nhất; mỗi lớp có công tắc trong
`layers.toml` để tắt thử và gỡ.

**Thuật ngữ:** gate (cổng) · pre-registered criterion (luật thắng đặt trước) · moving the goalposts (dời cột gôn) · ablation ·
rollback · feature flag · crutch (nạng) · remove test. **Bài sau:** [07i — NER](07i-ner.md).
