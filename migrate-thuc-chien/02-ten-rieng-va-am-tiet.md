# 02 — Tên riêng và bí danh: vì sao "nhận ra" chưa chắc "tìm ra", và đơn vị nghĩa của tiếng Việt

> Bài 2 của chuỗi "migrate thực chiến" (mổ **bước 2** ở [bài 00](00-tong-quan.md), dùng thước đo của [bài 01](01-do-dung-thu-agent-thay.md)).
> Đọc ~12 phút + lab 5 phút. Mang vào: hit@3, McNemar (bài 01); BM25 (bài 00: chữ hiếm khớp thì điểm cao).

## Chuyện mở đầu

Câu hỏi thật trong bộ đề: *"đổi biểu tượng trên giao diện web từ ký tự sang ảnh vẽ"*. Commit đáp án viết: *"web HQ: emoji → icon"*.
Hai câu cùng nói một việc nhưng gần như không chung chữ nào. BM25 trượt. Ý đầu tiên ai cũng nghĩ ra: dạy máy rằng "biểu tượng" = "icon".

## Dừng 30 giây

Hình dung bạn có một bảng "tên khác → một thứ" (giống GUID: nhiều đường dẫn, một asset). Thử tự liệt kê những cách bảng đó *làm hại*
việc tìm kiếm: một tên chung chung trỏ đi khắp nơi, hai từ khác nghĩa trông giống nhau khi bỏ dấu, và bảng được viết bởi chính người
ra đề. Sau đó nghĩ xem tiếng Việt khác tiếng Anh ở đâu khi máy tách câu thành "từ".

---

## Mạch của bài

```
1. Bảng bí danh: nhiều tên → một thực thể            → nhưng bảng tự sinh rất bẩn
2. Dọn bảng trước khi dùng                            → tiếng Việt bỏ dấu sinh thêm loại bẩn riêng (bầy/bay)
3. Nhận diện thực thể: 85 % câu nhận ra đúng          → nhưng nhét vào truy vấn: 10 → 11 câu, MRR còn giảm
4. Vì sao "nhận ra" không thành "tìm ra"              → câu diễn đạt lại không gọi tên, nó mô tả
5. Đòn bẩy thật: cặp âm tiết (từ ghép)                → para@3 9 → 12/33, McNemar 7–0
```

## 1. Bảng bí danh: nhiều tên, một thực thể

**Thực thể** (*entity*) = một "thứ" có danh tính: một khái niệm (routing), một file (`SwarmPrototype.cs`), một hệ thống game.
**Bí danh** (*alias*) = các cách gọi khác của nó. Seriously có hai bảng trong `kg/`:

- `entities.toml`: **108** thực thể tự sinh từ tiêu đề tài liệu (*seed-docs*).
- `entities-curated.toml`: **20** khái niệm viết tay, ví dụ thật:

```toml
[[entity]]
id = "harness:concept/routing"
aliases = ["định tuyến việc", "gửi việc cho phòng", "phòng đúng chuyên môn", "giao việc theo năng lực", "bảng giao việc"]
defined_in = "docs/shared/agent-company-design.md"
```

`id` là ID ổn định (kiểu GUID ở bài 00), không phải đường dẫn.

## 2. Dọn bảng trước khi dùng

Bảng tự sinh lấy mọi tiêu đề làm bí danh, nên dính các cụm xuất hiện ở *mọi nơi*. Ví dụ thật: "BI DUYET" (Bi duyệt) thành bí danh
của một thực thể, nên mọi câu có chữ "duyệt" đều bị nối sai. Ba luật dọn trong `tools/harness/kg.py`:

| Luật | Code | Chặn loại bẩn nào |
|---|---|---|
| Danh sách cụm chung chung bị cấm | `STOP_ALIAS = {'bi duyet', 'overview', 'index', 'readme', …}` | cụm nhắc ở khắp nơi |
| Bí danh trỏ ≥ 2 thực thể thì **trả cả hai**, không tự chọn | `detect` trả `(cụm, [id…])` | đoán bừa khi mơ hồ |
| Độ dài tối thiểu (≥ 4 ký tự; câu không dấu: ≥ 6) | điều kiện trong `detect` | từ ngắn trùng ngẫu nhiên |

Thứ tự này là bài học: **dọn rồi mới làm thông minh**. Thông minh trên dữ liệu bẩn chỉ sai nhanh hơn. Giống bake lightmap trên mesh
UV chồng nhau: thuật toán bake tốt mấy thì kết quả vẫn hỏng.

## 3. Tiếng Việt bỏ dấu: bầy ≠ bay

Thousandfold là game về **bầy** cánh hoa **bay**. Bỏ dấu thì hai chữ đều thành `bay`. Chỉ mục tìm kiếm bỏ dấu (để người gõ không dấu
vẫn tìm được), nhưng bước nhận diện thực thể thì **không được** bỏ dấu:

```python
def detect(text, maxn=4):
    """Có dấu: khớp theo chữ có dấu (bầy ≠ bay); câu không dấu nào: khớp theo ASCII nhưng chỉ bí danh ≥ 6 ký tự."""
    ...
    for n in range(min(maxn, len(w) - i), 0, -1):      # thử cụm dài nhất trước (4 chữ → 1 chữ)
        k = ' '.join(w[i:i + n])
        ids = acc.get(k) or (asc.get(...) if ascii_only and len(...) >= 6 else None)
```

Hai tầng, hai lựa chọn ngược nhau, và cả hai đều đúng:
- **Tìm kiếm**: bỏ dấu → tìm được nhiều hơn (*recall* cao), chấp nhận lẫn một ít.
- **Nối thực thể**: giữ dấu → nối sai một lần là kéo cả nhánh đồ thị sai theo, nên cần chắc (*precision* cao).

"Cụm dài nhất trước" (*longest match*) để "giao diện web" khớp cả cụm trước khi khớp "web" riêng lẻ.

## 4. Nhận ra 85 %, tìm ra +1 câu

Đo theo cách của bài 01 (ngày 27/10):

| | Kết quả |
|---|---|
| Câu para nhận ra ít nhất một thực thể | **28/33 = 85 %** |
| Nối thực thể vào truy vấn (`RECALL_ENT=1`): para trúng | 10 → **11**/33 |
| MRR | **giảm** |

Kết luận: tắt mặc định, giữ code sau cờ. Có hai lý do, cả hai đều đáng nhớ.

**Lý do 1: câu diễn đạt lại không gọi tên, nó mô tả.** Người hỏi "đổi biểu tượng … từ ký tự sang ảnh vẽ" không nói "icons-web".
Bảng bí danh chỉ giúp khi câu hỏi *chứa một tên khác* của thứ cần tìm. Para thì thường không chứa tên nào cả.

**Lý do 2: thêm chữ vào truy vấn làm loãng nó** (*query drift*). Nhét tên thực thể + tiêu đề tài liệu định nghĩa vào truy vấn tức là
thêm nhiều chữ phổ biến. BM25 cộng điểm cho mọi chữ khớp, nên tài liệu "nói nhiều chữ chung" leo lên trên đáp án. MRR giảm là dấu hiệu đó.

**Một cảnh báo về cách đo:** 20 bí danh tay được viết *trong lúc nhìn bộ đề*, nên con số 85 % là lạc quan. Giống tối ưu shader trên
đúng cái scene benchmark: số đẹp trên scene đó, scene khác thì không chắc. Luật của Seriously: **không chỉnh theo ca test**.

## 5. Đòn bẩy thật: đơn vị nghĩa của tiếng Việt là từ ghép

Ngày 29/10, harness phân loại 24 câu para còn trượt. 28 commit đáp án *đều đã có* câu hỏi đặt sẵn (doc2query, bài 00), nên chỉ mục
không thiếu. 12 câu có đáp án nằm trong top 40 nhưng **xếp hạng sai**. Nguyên nhân:

Chỉ mục tách câu theo **âm tiết** (khoảng trắng). Tiếng Anh tách theo khoảng trắng ra *từ*. Tiếng Việt tách theo khoảng trắng ra
*âm tiết*, mà nghĩa thường nằm ở *cặp*: "giao diện", "biểu tượng", "hiệu năng". Từng âm tiết "giao", "diện", "biểu", "tượng" thì phổ biến
và mang nghĩa khác ("giao việc", "diện mạo", "biểu quyết", "tượng đài"), nên một tài liệu nói chuyện khác hoàn toàn vẫn gom đủ điểm.

Lab của bài này dựng đúng tình huống đó:

```
từng âm tiết : C (mồi: "giao việc… tượng đài… biểu quyết… diện mạo") -3,31   >   A (đáp án) -1,21
cặp liền kề  : A -2,97   (C không khớp cặp nào)
```

**Sửa (0 token)** trong `tools/claude/recall.py`: thêm một lượt tìm theo **cặp âm tiết liền kề** dạng cụm FTS (`"giao dien" OR "bieu tuong"
OR …`, bỏ cặp toàn từ dừng), rồi trộn với lượt thường theo thứ hạng (RRF, bài 04):

```python
def bigram_query(q):
    ws = [fold(w) for w in re.findall(r'\w+', q)]
    return ' OR '.join(f'"{a} {b}"' for a, b in zip(ws, ws[1:]) if not (a in _STOP2 and b in _STOP2))
```

Kết quả đo hai lần, giống nhau:

| | Trước | Sau |
|---|---|---|
| para @3 | 9/33 | **12/33** |
| so với nền 6/33 | — | được 7, mất 0, **McNemar p = 0,016** (chắc, theo luật bài 01) |
| kw @3 | 32/33 | 32/33 (không lùi) |
| bẫy @3 | 3/5 | 2/5 (nhóm 5 câu, chỉ báo) |
| ms/truy vấn | ~12 | ~23–28 (hai lượt tìm) |

Có thể đẩy trọng số cặp cao hơn để được 13–14/33, nhưng khi đó một bản cũ xếp lên trên bản mới (cổng "cũ↑" đỏ). Vì vậy chọn cấu hình
giữ cổng xanh: thắng một chỉ số mà làm hỏng chỉ số khác thì không tính.

## So sánh các cách nối "chữ của người hỏi" với "chữ của tài liệu"

| Cách | Làm lúc | Ưu | Gãy ở đâu | Ở Seriously |
|---|---|---|---|---|
| Bảng bí danh / từ đồng nghĩa | đọc | rẻ, giải thích được | phải viết tay, bẩn, lạc quan | giữ cho đồ thị, tắt cho tìm kiếm |
| Nhận diện thực thể + nối truy vấn | đọc | đi được sang đồ thị | loãng truy vấn | tắt (`RECALL_ENT`) |
| **n-gram / cụm âm tiết** | chỉ mục + đọc | 0 token, hợp tiếng Việt | ms ×2; cặp chung chung vẫn nhiễu | **bật** (R6c) |
| Tách từ tiếng Việt chuẩn (VnCoreNLP, pyvi) | chỉ mục | đúng ranh giới từ | thêm phụ thuộc, sai với tên riêng/code | chưa thử |
| **doc2query** | ghi | thêm chữ của người hỏi vào tài liệu | tốn token một lần | **bật** (bài 03) |
| Vector (embedding) | ghi + đọc | khớp theo nghĩa | khó giải thích, tốn, lẫn bản cũ | để sau, chưa cần |

## Scale

- **Nhỏ (vài trăm tài liệu)**: bí danh tay là đủ, đọc được hết.
- **Vừa (Seriously: ~3.300 mảnh)**: bí danh chỉ cho đồ thị; tìm kiếm cần n-gram + doc2query; mọi thay đổi qua bộ đề.
- **Lớn (hàng triệu)**: tách từ chuẩn + vector + xếp hạng lại bằng model (*reranker*); bảng thực thể do một hệ riêng nuôi (như Wikidata).

## Bốn nền tảng

Điểm chung cần nhớ: **chuẩn hoá Unicode**. Chữ "ầ" có thể lưu thành 1 ký tự (NFC) hoặc "a + dấu mũ + dấu huyền" (NFD). Hai dạng nhìn y
hệt nhưng so chuỗi thì khác, nên `kg.py` gọi `_nfc(text)` trước khi khớp.
- **Mac**: tên file trên HFS+ cũ lưu dạng NFD; APFS giữ nguyên dạng được đưa vào. Git có `core.precomposeunicode=true` để đổi về NFC.
  Tên file tiếng Việt từ Mac lên git dễ thành hai file "giống nhau".
- **Windows**: NTFS lưu nguyên dạng, phần lớn công cụ gõ ra NFC. Nếu chạy harness ở đây: PowerShell cũ mặc định không phải UTF-8 (`chcp 65001`).
- **iOS**: giống Mac (cùng hệ file). Bàn phím Telex/VNI gửi NFC, nhưng chữ dán vào có thể là NFD. Game nhận text nhập tay nên chuẩn hoá trước khi so.
- **Android**: Java/Kotlin `Normalizer.normalize(s, NFC)`. Bàn phím Laban/Gboard gửi NFC.
- **SQLite FTS5** (dùng ở cả 4 nền tảng): tokenizer `unicode61 remove_diacritics 2` bỏ dấu tiếng Việt đúng, nên `bầy` và `bay` thành
  cùng một token. Vì vậy nhận diện thực thể phải làm ở tầng khác, trước khi vào FTS.

## Lab

1. `python3 lab/02_am_tiet.py`: thấy tài liệu mồi C thắng đáp án A khi tìm từng âm tiết, và thua khi tìm theo cặp.
   Làm theo dòng "Thử" cuối output để thấy cặp âm tiết cũng có giới hạn.
2. Trong Seriously: `RECALL_BIGRAM_W=0 python3 tools/claude/recall_eval.py` (tắt lượt cặp) rồi chạy lại không có biến đó. So hai dòng
   `para @3` và dòng "so cặp với nền".

## Tóm một dòng

Bảng bí danh giúp **nối đồ thị**, không giúp **tìm câu diễn đạt lại**. Với tiếng Việt, đòn bẩy rẻ nhất là tôn trọng đơn vị nghĩa:
**cặp âm tiết**, không phải âm tiết lẻ.

**Bài sau:** 03 — Bake sẵn: doc2query và ước token trước khi bật.
