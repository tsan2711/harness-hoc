# 07e — Luật xếp hạng sau khi tìm

> Chuỗi 07, bài 5/9. Đọc ~10 phút. Cần trước: [05a](05a-bm25-va-fts5.md), [07c](07c-frontmatter.md), [07d](07d-bang-edges.md).

## 1. Câu chuyện

Agent hỏi "hướng art Thousandfold hiện tại". BM25 trả (điểm FTS5 âm, càng nhỏ càng tốt):

| # | Đoạn | BM25 | Loại |
|---|---|---|---|
| 1 | `docs/shared/thousandfold-art-directions.md` — "chọn hướng art (2026-10-11)" | −14,2 | chốt (doc) |
| 2 | phiên 2026-10-14: "Bi bảo đổi sang Sky…" | −13,9 | chuyện |
| 3 | commit `d9e331fe` "đổi hướng art sang Sky…" | −11,0 | chuyện |

*(số minh hoạ)* Nếu chỉ xếp theo BM25, agent đọc dòng 1 — bản cũ, gắn chữ "chốt" uy tín — và tin nó. Kiến thức đúng có trong top 3
nhưng đứng dưới, không có gì báo dòng 1 đã hết hạn. **Tìm thấy chưa đủ; thứ tự và nhãn quyết định agent tin cái gì.**

## 2. Dừng 30 giây

- Sao không đơn giản "cái mới nhất lên đầu"?
- Nhãn "ĐÃ THAY BỞI X" đặt ở **đầu** dòng hay **cuối** dòng — khác gì nhau với một LLM đọc lướt?
- Thứ tự các luật có quan trọng không, nếu luật nào cũng "đúng"?

## 3. Hiện trạng: một khoá sắp xếp

`search()` trong `recall.py` sắp theo bộ khoá:
```python
rows.sort(key=lambda r: (round(r[7] / BUCKET), r[6] == 'cu', r[6] != 'chot', r[7]))   # BUCKET = 0.5
```
Đọc từ trái sang:
1. **Xô điểm** (`BUCKET = 0,5` điểm BM25): hai đoạn chênh < 0,5 coi như *ngang nhau*. Không có xô thì luật phụ không bao giờ có tác
   dụng, vì BM25 hiếm khi bằng nhau tuyệt đối.
2. Trong cùng xô: đoạn **không** mang nhãn "có thể cũ" lên trước.
3. Trong cùng xô: **chốt** (sổ tay, docs, ADR) trước **chuyện** (transcript, commit, inbox).
4. Cuối cùng: BM25 thô.

Lưu ý tinh: nhãn `cu` *có* hạ nhẹ — nhưng chỉ trong cùng xô (chênh < 0,5 điểm). Không bao giờ đẩy một đoạn khớp mạnh xuống dưới một
đoạn khớp yếu. Comment trong code nói rõ lý do: hạ hạng thật sự đã đo **mất 3 câu para**.

## 4. Chuỗi luật đề xuất (bài 06 §2.2.3)

Theo thứ tự — luật trên thắng luật dưới:

| # | Luật | Làm gì | Vì sao ở vị trí này |
|---|---|---|---|
| 1 | Khớp `scope` | đoạn cùng game/phòng với người hỏi được ưu tiên (như `W_UNIT = 8.0` hiện nay, mềm) | luật June không được đè câu hỏi NanoSwarm — trước mọi so sánh cũ/mới |
| 2 | `status: wrong` | **loại** khỏi top | sửa sai = không dùng cả làm lịch sử; giữ lại chỉ tốn chỗ trong 3 dòng |
| 3 | Bị `supersedes` | nhãn **`ĐÃ THAY BỞI <path>`** ở đầu dòng **và** kéo bản thay vào top nếu chưa có | không xoá bản cũ (có thể chính câu hỏi là "trước đây làm sao") — nhưng không để nó đứng một mình |
| 4 | Chốt trên chuyện cùng xô | như hiện nay | doc đã được viết cẩn thận > câu nói trong phiên |
| 5 | `có thể cũ` | giữ nhãn như hiện nay | tín hiệu yếu (file đổi sau ngày đoạn ≠ đoạn sai) — chỉ báo |
| — | Ngày | chỉ là tie-break cuối | xem §5 |

Áp vào câu chuyện: dòng 1 bị `supersedes` (nếu doc Sky có frontmatter) → `ĐÃ THAY BỞI docs/…/art-sky.md`, doc Sky được kéo vào top.
Agent thấy cả hai, và thấy quan hệ.

Câu hỏi 3: thứ tự **có** quan trọng. Đảo luật 1 và 3: câu hỏi về June gặp "ĐÃ THAY BỞI" một doc NanoSwarm — nhãn đúng về mặt quan
hệ nhưng sai phạm vi, agent bỏ luật June đang còn hiệu lực. Luật lọc *phạm vi* phải chạy trước luật *thời gian*.

## 5. Vì sao không hạ hạng theo ngày — câu hỏi 1

"Mới nhất lên đầu" nghe hợp lý, nhưng:
- **Câu diễn đạt lại thường trúng đoạn cũ.** Ghi chú gốc lúc quyết định thường giải thích *vì sao* đầy đủ nhất; nhắc lại về sau ngắn và
  thiếu ngữ cảnh. Đã đo trên bộ 45 câu: phạt theo tuổi làm **mất 3 câu para**.
- **Cùng tồn tại ≠ thay thế** ([05f](05f-ky-uc-cu-va-thay-the.md)). Luật GCLess trong `docs/shared/` viết từ lâu vẫn đúng; một câu trong
  phiên hôm qua nhắc "GC" không thay được nó.
- **Mới ≠ đúng.** Bản mới có thể là một câu hỏi, một ý thử, một lần sửa sai *sai*.

Ngày chỉ dùng khi mọi thứ khác ngang nhau. Cái thay thế được ngày là **khai báo** (`supersedes`), vì nó mang *ý định* của người viết.

## 6. Nhãn ở đầu dòng — câu hỏi 2

`fmt()` hiện in:
```
2026-10-11 hq           chốt docs/shared/thousandfold-art-directions.md#…
    …đoạn trích…
```
Đề xuất thêm nhãn mạnh **ngay sau ngày**: `2026-10-11 hq ĐÃ THAY BỞI docs/…/art-sky.md · chốt …`. Lý do:
- LLM (và người) đọc lướt phần đầu; nhãn cuối dòng dễ bị đọc *sau* khi đã tin nội dung.
- Ngân sách 1 800 ký tự cắt từ cuối: nhãn đặt cuối có thể bị cắt mất.
- Nhãn đầu dòng nằm *trước* nội dung → định khung cho cách đọc nội dung ("đây là lịch sử").

## 7. Các cách, trên ca `trap-art`

| Cách | Agent tin | Gãy khi |
|---|---|---|
| A. BM25 thuần | bản cũ | luôn với ca thay thế |
| B. Mới nhất lên đầu | bản mới (ca này) | câu para (−3), cùng tồn tại, bản mới sai |
| C. Hiện nay (xô + chốt + nhãn `có thể cũ`) | bản cũ, có thể mang nhãn yếu | doc cũ không có tiêu đề "(cũ)" và không trích file đổi |
| D. Chuỗi luật 1–5 | thấy cả hai, bản cũ mang nhãn đầu dòng | không ai khai `supersedes` (→ bài 07f) |
| E. LLM xếp lại (reranker) | thường đúng | tốn token mỗi câu; STALE ~55 % khi phán cũ/mới |

**Quy luật:** BM25 trả lời "đoạn nào *nói về* câu hỏi"; luật xếp trả lời "đoạn nào *nên tin*". Luật thứ hai phải dựa vào thứ được
**khai** (phạm vi, thay thế, sửa sai), không dựa vào thứ được **đoán** (ngày, giọng văn).

## 8. Scale

- **Nhỏ**: BM25 thuần ổn — ít bản trùng chủ đề.
- **Vừa** (Seriously): nhiều phiên nói về cùng chuyện → chuỗi luật cần thiết; xô 0,5 đủ khi ngân sách chỉ 3 dòng.
- **Lớn**: 3 dòng không chứa nổi "bản cũ + bản mới + hàng xóm"; phải gộp (một dòng "X — ĐÃ THAY BỞI Y" thay vì hai dòng), và xô theo
  điểm RRF khi có vector (P3 phải viết lại luật xô — bài 06 ghi rõ).

## 9. Dừng lần hai — mở Seriously kiểm chứng

- `tools/claude/recall.py` dòng `W_ACC, W_ENT, BUCKET = 1.5, 3.0, 0.5` và `W_UNIT = 8.0`.
- Cuối `search()`: dòng `rows.sort(key=…)` + comment "only LABELLED … demoting cost 3 paraphrase hits".
- `fmt()`: thứ tự trường in ra; `hint()`: `budget=1800` cắt theo dòng.
- `tools/claude/recall_eval.py` `score()`: `cũ↑` = bản cũ xếp **trên** bản mới — chỉ số đo đúng điều bài này nói.

## 10. Bốn nền tảng

Toán sắp xếp không khác gì trên **Windows / Mac / iOS / Android**. Khác duy nhất: sắp chuỗi tiếng Việt có dấu theo locale — đừng
dùng tên/nhãn làm khoá sắp, dùng số và bool như `recall.py` làm. Trong game, cùng bài học xuất hiện ở **xếp nhiệm vụ/thông báo**: lọc
phạm vi (khu vực người chơi đang ở) trước, ưu tiên khai báo của designer ("nhiệm vụ chính") sau, ngày nhận chỉ là tie-break — xếp
theo "mới nhất" là cách nhanh nhất làm người chơi lạc nhiệm vụ chính.

## 11. Tóm tắt một dòng

Sau BM25, một chuỗi luật có thứ tự (phạm vi → loại sai → nhãn + kéo bản thay → chốt > chuyện → nhãn cũ → ngày) quyết định agent tin
gì; nhãn đặt đầu dòng; không phạt theo tuổi.

**Thuật ngữ:** rerank (xếp lại) · tie-break · bucket (xô điểm) · rule cascade (chuỗi luật) · demotion (hạ hạng) · label (nhãn) ·
framing (định khung). **Bài sau:** [07f — đường ghi](07f-duong-ghi.md).
