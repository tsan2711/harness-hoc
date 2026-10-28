# 01 — Tìm theo chữ: inverted index, BM25, FTS5, và vì sao một kho chung bị loãng

> Chuỗi "Memory theo mục đích", bài 1/6. Đọc ~10 phút.
> Code thật: `tools/claude/recall.py` (đã có). Thiết kế: `docs/shared/knowledge-graph-design.md` §1, V0.

## Chuyện mở đầu

Ngày 10-24 Bi báo "nhớ kém, hay quên". Đo lại thì thấy kho tìm lại có 22 290 mảnh chữ, trong đó 83 % là bản ghi hội thoại (transcript).
Hỏi đúng từ khoá thì vẫn trượt 4/20 câu. Hỏi bằng cách nói khác thì chỉ trúng 8/20.
Tìm theo chữ không hỏng vì code chậm: kho còn chạy được ~0,6 ms cho mỗi 1 000 mảnh. Nó hỏng vì cách chấm điểm.

## Dừng 30 giây

Một hệ chấm điểm theo *tần suất từ* sẽ làm gì khi bạn đổ thêm 18 000 đoạn hội thoại có chứa đúng những từ đó, nhưng nói về chuyện khác?
Còn một câu hỏi không có chung từ nào với câu trả lời thì sao?

---

## 1. Inverted index — cấu trúc nằm dưới mọi máy tìm chữ

**Định nghĩa.** Inverted index (chỉ mục ngược) là một bảng *từ → danh sách tài liệu chứa từ đó* (posting list), có kèm số lần xuất hiện
và vị trí. Lúc tìm, máy không đọc từng tài liệu. Nó chỉ lấy posting list của từng từ trong câu hỏi rồi giao (AND) hoặc hợp (OR) các
danh sách đó lại.

```
"grass"  → [doc 17 (×3), doc 204 (×1), doc 9 801 (×1), …]
"vung"   → [doc 17 (×2), doc 88 (×5), …]
AND      → [doc 17]           OR → [17, 88, 204, 9 801, …]
```

Muốn tạo được các "từ" thì phải có **tokenizer** (bộ cắt từ): nó cắt chuỗi thành token và chuẩn hoá (chữ thường, có bỏ dấu hay không).
Với tiếng Việt, chọn bỏ dấu hay giữ dấu là chọn giữa hai lỗi. Bỏ dấu thì "nhớ" và "nhỏ" thành một từ. Giữ dấu thì người gõ không
dấu tìm không ra.

## 2. BM25 — công thức chấm điểm

**Định nghĩa.** BM25 (Robertson & Zaragoza) chấm điểm tài liệu D cho câu hỏi Q như sau:

```
score(D,Q) = Σ_{q∈Q} IDF(q) · f(q,D)·(k1+1) / ( f(q,D) + k1·(1 − b + b·|D|/avgdl) )

IDF(q) = ln( (N − n(q) + 0.5) / (n(q) + 0.5) )        (FTS5 kẹp IDF ≤ 0 thành 1e-6)
```

- `f(q,D)`: số lần từ q xuất hiện trong D. Hạng tử này **bão hoà**: lần xuất hiện thứ 10 cộng thêm rất ít. Độ bão hoà do `k1` quyết định.
  Trong SQLite FTS5, `k1 = 1.2` và không đổi được.
- `|D|/avgdl`: độ dài D so với độ dài trung bình. `b = 0.75` là mức phạt tài liệu dài, vì tài liệu dài thì dễ chứa từ một cách tình cờ.
- `N`: tổng số mảnh. `n(q)`: số mảnh chứa q. Từ càng hiếm thì IDF càng cao.

(Hằng số k1/b và cách kẹp IDF lấy theo mã nguồn `fts5_aux.c` / tài liệu sqlite.org/fts5.html. Đây là kiến thức sẵn có, chưa đọc lại hôm nay.)

## 3. SQLite FTS5 trong `recall.py`

Bảng chỉ mục được tạo trong `connect()` (dòng 76–77):

```python
c.execute("create virtual table if not exists chunks using fts5(text, acc, ent, path unindexed, kind unindexed,"
          " ts unindexed, unit unindexed, loc unindexed, tier unindexed, tokenize='unicode61 remove_diacritics 0')")
```

- Chỉ ba cột `text`, `acc`, `ent` được đưa vào chỉ mục. Các cột còn lại (`unindexed`) chỉ là nhãn để lọc theo đơn vị, ngày, tầng.
- `unicode61 remove_diacritics 0`: tokenizer **giữ dấu**. Việc bỏ dấu do `fold()` tự làm (dòng 51–54), vì `remove_diacritics` của
  unicode61 không tách được chữ "đ" (đ không có dạng phân rã NFD). Cột `text` chứa bản đã bỏ dấu. Cột `acc` giữ nguyên dấu, nên khi
  người gõ có dấu thì "nhớ" vẫn xếp trên "nhỏ".
- `ent` chứa đường dẫn, mã lỗi `CS0000`, tên test, tiêu đề mục (`title_terms`). Đây là cột "mảnh này *nói về* cái gì".

Câu truy vấn nằm trong `_pull()` (dòng 374–375):

```python
got = c.execute(f'select kind, ts, unit, loc, path, acc, tier, bm25(chunks, 1.0, {W_ACC}, {W_ENT}), rowid from chunks'
                f' where chunks match ?{extra} order by 8 limit ?', [fts_query(q, op)] + args + [n]).fetchall()
```

- `bm25(chunks, 1.0, 1.5, 3.0)` gán **trọng số cột**: số lần trúng trong cột `ent` được nhân 3, trong `acc` nhân 1,5, rồi cộng lại
  thành `f(q,D)`. Một mảnh có "Grass.shader" trong `ent` sẽ thắng một đoạn hội thoại chỉ nhắc chữ grass.
- `order by 8` sắp **tăng dần**, vì FTS5 trả BM25 dưới dạng **số âm** (càng âm càng khớp). Đây là chỗ hay gây nhầm. Trong `adj()`
  (dòng 420–428), nhân `sc *= 1 + WARM_BOOST` làm điểm âm hơn, tức là *tốt lên*. Còn `CARD_FACTOR = 0.5` làm điểm bớt âm, tức là
  *tụt hạng* thẻ chắt lọc.
- Câu được chạy hai lượt: `' AND '` trước (mảnh chứa mọi từ), rồi `' OR '` để lấp cho đủ 12. Lý do ghi ngay ở docstring: AND quá mỏng
  không được che mất đáp án (đo được kw 16 → 20).

## 4. Vì sao 83 % transcript làm loãng top-k

**Top-k** là k kết quả đầu, ở đây `LIMIT = 12`. Có ba cơ chế cộng lại:

1. **Cạnh tranh cho một số chỗ cố định.** k không đổi, nhưng số mảnh "cùng từ vựng, khác chuyện" tăng theo kho. Hội thoại về
   Thousandfold nhắc "vùng 2", "grass", "palette" hàng trăm lần. Mỗi lần nhắc là một ứng viên có điểm BM25 khác 0. Chỉ cần vài chục
   ứng viên điểm sát mảnh đúng là mảnh đúng bị đẩy khỏi 12.
2. **IDF bị bào mòn.** Một từ vốn hiếm trong sổ tay (n nhỏ, IDF cao) xuất hiện trong hàng nghìn đoạn hội thoại thì n tăng, IDF giảm.
   Từ đó mất khả năng phân biệt.
3. **Trùng lặp.** Phiên được resume sẽ phát lại lịch sử, nên cùng một câu xuất hiện nhiều lần. `_pull` có khử trùng bằng `hash(r[5])`,
   nhưng bản *gần* trùng thì vẫn lọt.

Số đo thật (`tools/harness/recall-scale.md`, bơm nhiễu nhân bản kho):

| Kho | ×1 | ×5 | ×10 | ×20 | ×40 |
|---|---|---|---|---|---|
| kw trúng trong 12 (eval, 20 ca) | 20 | ≤ 18 | ~17 | 15 | **5** (mix) |
| kw kho thật | 16 | — | 13–15 | — | — |

Có một chi tiết quan trọng: ở ×20, mảnh đúng vẫn nằm trong top 60 ở 19/20 ca. **Thứ hạng hỏng trước khả năng tìm thấy.** Vì vậy cách
chữa là *tách nhóm ứng viên* chứ không phải tìm rộng hơn. P1 đã làm việc này trong `search()` (dòng 415–416):

```python
if LAYERED and sum(r[6] == 'chot' for r in rows) < MIN_POOL:
    rows += _pull(c, q, extra + ' and tier = ?', args + ['chot'], limit, seen, texts)
```

Nếu trang chung có ít hơn 3 mảnh "chốt" (sổ tay, GDD, ADR — xem `tier_of`, dòng 64–65), hệ chạy thêm một lượt BM25 *chỉ trên tầng ấm*,
để hội thoại không thể chiếm hết danh sách ứng viên.

## 5. Vì sao diễn đạt lại (para) chỉ đạt 40 %

BM25 chỉ cộng điểm cho từ **có mặt**. Câu "bầy cánh hoa chậm" không có chung token nào với `SwarmPrototype.cs`, nên điểm bằng 0.
Đây là **lỗ hổng từ vựng** (vocabulary mismatch), và không xếp hạng lại kiểu gì cũng lấp được.

Thuốc hiện có là `synonyms.toml`, đọc trong `synonyms()` (dòng 262–275) và mở rộng trong `fts_query` (dòng 285–286):

```python
alts = [f'"{fold(t)}" OR acc:"{unicodedata.normalize("NFC", t)}"']
alts += [f'"{fold(x)}"' for x in dict.fromkeys(syn.get(fold(t), []))]
```

Nó nhóm theo **từ** ("hiệu năng" = "perf" = "fps"). Thêm 9 nhóm mà para không lên, vì lỗ hổng thật nằm ở **khái niệm của game**
("bầy cánh" = `SwarmPrototype`). Cách chữa đúng là entity linking (bài 04).

## 6. Bài học từ pilot thẻ: thêm tài liệu tốt vào cùng một pool không cứu được thứ hạng

P2 cho Haiku đọc hội thoại Thousandfold, rút ra 865 thẻ ngắn (`company/memory/cards/`). Thẻ được đưa vào **cùng bảng `chunks`**
(`card_rows`, dòng 184–194), chấm cùng BM25. Kết quả ở ×10: kw 15/20 (cổng 18), trap 2/5 (cổng 4). Không đạt.

Về kỹ thuật, có ba lý do:

- Thẻ ngắn và dày từ khoá, nên BM25 thưởng quá tay. Vì thế phải đặt `CARD_FACTOR = 0.5` (comment dòng 43 ghi gold para 9→7 ở 1.0).
  Nghĩa là phải *hãm* chính thứ vừa thêm vào.
- Thẻ không nối với thực thể hay tài liệu nào. Không có cạnh thì không có tín hiệu nào ngoài chữ.
- Bộ vàng không có câu nào hỏi nội dung thẻ, nên không thể đo được lợi ích (bài 06).

Còn chi phí thì vì sao ước 0,9M token mà đốt tới 4,4M? Xem bài 05.

## Các cách làm và ưu/nhược

| Cách | Ưu | Nhược | Gãy khi |
|---|---|---|---|
| Một kho FTS, chỉnh trọng số | 0 token, tất định, nhanh | thứ hạng loãng theo cỡ kho; không chữa lỗ từ vựng | kho ×10 |
| Một kho vector (embedding) | bắt được diễn đạt lại | nhiễu "cùng chuyện, bản cũ" làm embedding lẫn còn tệ hơn BM25 (`memory-architecture.md` §1); tốn token để dựng | bản cũ/bản mới gần nghĩa |
| Hybrid BM25 + vector + RRF | bù nhau | vẫn là *một* pool; số đo và gu vẫn không sống được dưới dạng chữ | câu hỏi về số, về ảnh |
| **Nhiều kho, một cửa** (thiết kế) | mỗi câu hỏi tìm trong kho đúng hình dạng | phải có router và phải đo router | router chọn sai kho |

## Khi lớn lên (scale)

Chi phí thời gian tăng tuyến tính và còn rẻ: ×80 mất khoảng 102 ms. Chất lượng mới là thứ hỏng: ×40 sập còn 25 %. Có ba hướng giữ được:
**lọc phạm vi trước khi xếp hạng** (unit, tầng, ngày — ×40 với lọc unit lên lại 16/20), **tách pool**, và **chắt lọc ở phía ghi** để kho
không phình bằng rác. Mảnh hội thoại cũ quá 60 ngày thì không giữ trong chỉ mục, nên kho lạnh tự có giới hạn.

## Tự làm

1. Chạy hai cách nói cho cùng một ý rồi so 3 dòng đầu:
   `sh tools/claude/kit.sh recall "SwarmPrototype"` và `sh tools/claude/kit.sh recall "bầy cánh hoa"`.
   Ghi lại mảnh nào là `chốt`, mảnh nào là `chuyện`.
2. Xem điểm BM25 thô:
   `sqlite3 company/state/recall.sqlite "select kind, tier, round(bm25(chunks,1.0,1.5,3.0),2) s, substr(acc,1,60) from chunks where chunks match 'grass' order by s limit 8"`.
   Đổi `3.0` thành `1.0` rồi xem thứ hạng của dòng `note` thay đổi thế nào.
3. Chạy `sh tools/claude/kit.sh recall-eval` và đọc dòng `recall@12 từ khoá … diễn đạt lại …`. Đối chiếu với `company/eval/recall/baseline-real.json`.

## Đọc thêm

- Robertson & Zaragoza, *The Probabilistic Relevance Framework: BM25 and Beyond* (2009).
- SQLite FTS5: https://sqlite.org/fts5.html (§4.3 tokenizer unicode61, §5.1.1 bm25).
- Trong repo: `tools/harness/recall-scale.md` (đo nhiễu), `docs/shared/memory-architecture.md` §1–§3.

> **Một dòng:** BM25 chấm tần suất từ có bão hoà và IDF. Kho chung đầy hội thoại cùng từ vựng làm *thứ hạng* hỏng trước, còn lỗ hổng từ vựng thì BM25 không bao giờ chữa được.
> **Bài sau:** [02 — Phân loại trí nhớ: CoALA → 11 kho](02-muoi-mot-loai-tri-nho.md)
