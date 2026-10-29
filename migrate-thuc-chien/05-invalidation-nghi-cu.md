# 05 — Invalidation: nghi cũ, false sharing, ID ổn định

> Bài 5 của chuỗi "migrate thực chiến" (mổ **bước 3** và nửa đầu **bước 4** ở [bài 00](00-tong-quan.md); đo bằng thước của [bài 01](01-do-dung-thu-agent-thay.md)).
> Đọc ~15 phút + lab 5 phút. Mang vào: cache coherence (MESI, false sharing), Unity GUID/`.meta`, `Library/`, bẫy cũ/mới và cũ↑ (bài 03–04).

## Chuyện mở đầu

28/10, Bi hỏi: L1/L2/L3 có cache line, dữ liệu đổi thì đánh **dirty**. Trí nhớ agent có làm được vậy không? Và *"khi làm việc với bên
khác mà cần cập nhật kiến thức thì sao, phải mở phòng đó thì bất tiện"*. Một ngày sau, ca bẫy `trap-tunable` đỏ ở pre-push (bài 04). Soi
nhãn thì thấy chuyện tệ hơn: commit đáp án mang nhãn **"có thể cũ"**, còn tài liệu cũ `kit-candidates-2026-10-04.md` mang nhãn **"chốt"**.
Hệ có dirty bit, nhưng bit cắm ngược chiều.

## Dừng 30 giây

Bạn có 3 core cùng giữ một bản sao của biến `hp`. Core 0 ghi `hp`. Tự liệt kê: ai phải biết, báo bằng cách nào (gửi bản mới hay chỉ
báo "bản của mày hỏng"), và chuyện gì xảy ra nếu `hp` nằm chung 64 byte với `mana` mà core 1 đang đọc liên tục. Rồi đổi "core" thành
"phòng ban", "biến" thành "đoạn tài liệu", "64 byte" thành "một file .md". Giữ các ý đó. Cả bài đi qua chúng.

---

## Mạch của bài

```
1. Sửa A thì mọi B dựa vào A có thể sai   → dirty bit theo đồ thị, đẩy-khi-ghi   → 82 cảnh báo, gần hết sai
2. Loại mũi tên quá rộng + hạt cả file     → false sharing                       → bỏ `refs`: 82 → 2; hạt file vẫn còn
3. Đẩy cờ hay tính cờ lúc đọc?             → kiểm-khi-đọc, 0 token, không ghi    → nhưng cờ chỉ dựa trên NGÀY
4. Ngày ≠ phiên bản                         → 29/10: đáp án "cũ", bản cũ "chốt"   → cần khai báo `supersedes`
5. Mũi tên trỏ bằng đường dẫn               → tách repo là gãy                    → ID ổn định (GUID / kg://) → bài 06
```

## 1. Dirty bit theo đồ thị: đẩy-khi-ghi

Trong CPU, mỗi cache line có vài bit trạng thái. Giao thức **MESI** dùng 4 trạng thái: *Modified* (tôi sửa, chưa ghi về RAM: dirty),
*Exclusive* (chỉ tôi giữ, sạch), *Shared* (nhiều core giữ, sạch), *Invalid* (bản của tôi đã hỏng). Khi core 0 ghi vào một line đang
Shared, nó phát tín hiệu và mọi bản sao ở core khác chuyển sang Invalid. Đó là **write-invalidate**: báo "bản của mày hỏng", không gửi dữ
liệu mới. Cách ngược lại là **write-update** (giao thức Dragon, Firefly): gửi luôn giá trị mới cho mọi bản sao. MESI thắng trên phần cứng
phổ thông vì đa số lần ghi không ai đọc lại ngay, gửi dữ liệu là phí băng thông.

Harness Seriously có cùng hình dạng, chỉ khác đơn vị. `tools/harness/kg.py` dựng một **đồ thị phụ thuộc** tất định (0 token): nút là tài
liệu, file code, thực thể; cạnh là "B dựa vào A". Cạnh lấy từ frontmatter `depends_on`, code nhắc tên GDD (`implements`), tên test
(`tests`), link markdown (`refs`). Kho thật lúc dựng: 2.098 nút, 4.969 cạnh, 8 s (`knowledge-graph-design.md`, K1).

"Bị dirty" ở đây gọi là **nghi cũ** (*suspect*): A nghi cũ khi một nút B mà A dựa vào đã đổi *sau* lần cuối A được sửa hoặc xác nhận.

```python
# tools/harness/kg.py
REV_TYPES = ('depends_on', 'implements', 'derived_from', 'tests')   # (refs = "nhắc tới", không lan nghi cũ)

def suspects(g=None, min_age_days=0, changed=None):
    """nút A nghi cũ khi một nút B mà A phụ thuộc đổi SAU lần cuối A được đổi/xác nhận. -> [(A, B, tuổi ngày)]."""
    for e in g['edges']:
        if e['type'] not in REV_TYPES:
            continue
        a, b = nodes.get(e['a']), nodes.get(e['b'])
        ...
        last_a = max(a.get('touched', 0), ver.get(a['id'], 0))     # ver = kg/verified.jsonl: "vẫn đúng"
        if b.get('touched', 0) > last_a and ...:
            out.append((a['id'], b['id'], round(age, 1)))
```

Ba đường dùng kết quả này:

- `kg.py staged` (nối pre-commit): file đang staged đổi → in các nút sẽ nghi cũ. Cảnh báo, không chặn. ~0,05 s nhờ cache.
- `kg.py suspect --send`: nút nghi cũ quá 7 ngày → `kit company send <phòng chủ> "kiểm lệch: …" --check review`, trần 3 việc/lần.
- `kg.py verify <id>`: phòng chủ đọc lại, thấy vẫn đúng → ghi một dòng vào `verified.jsonl`, `last_a` nhảy lên, hết nghi.

Đây là câu trả lời cho câu hỏi "phải mở phòng đó thì bất tiện": bạn không mở phòng kia. Đồ thị biết **ai đang giữ bản sao** (phòng nào có
tài liệu dựa vào file bạn vừa sửa), và gửi tín hiệu invalidate đúng tới phòng đó, như **directory-based coherence** trên CPU nhiều socket:
một bảng thư mục ghi line nào đang nằm ở core nào, nên chỉ gửi invalidate tới đúng các core đó thay vì hét lên bus cho tất cả (*snooping*).
Phòng nhận tự mở phiên, tự sửa hoặc `verify`. Bên ghi không viết lại tài liệu của phòng khác: luật sở hữu cấm, và tốn token. Đó là lý do
Seriously chọn write-invalidate, không chọn write-update.

**Vấn đề.** Lần đầu bật, `suspect` báo **82** nút. Gần hết sai. Cảnh báo sai nhiều thì người ta thôi đọc, và tín hiệu đúng chìm theo.

## 2. False sharing: mũi tên quá rộng, hạt quá thô

**False sharing** trên CPU: hai biến độc lập nằm chung một cache line 64 byte. Core 0 ghi biến của nó, line bị invalidate ở core 1, core 1
phải nạp lại dù dữ liệu của nó không đổi. Gốc rễ: **đơn vị theo dõi to hơn đơn vị dữ liệu thật**. Harness gặp hai dạng.

**(a) Loại cạnh quá rộng.** Link markdown `](x.md)` chỉ nói "nhắc tới", không nói "đúng hay sai tuỳ vào". Một trang INDEX link 30 tài liệu
thì sửa tài liệu nào cũng làm INDEX nghi cũ. Sửa: bỏ `refs` khỏi `REV_TYPES` (vẫn giữ cạnh để tìm "cái gì liên quan").
Kết quả ghi ở `knowledge-graph-design.md`: **82 → 2**, cả 2 đúng (một GDD nhắc `SwarmPrototype.cs` vừa đổi). Mẫu 2 nút quá nhỏ để gọi
là precision cao, nhưng nhiễu đã hết.

Cạnh "hay được sửa cùng nhau" (`co_change`, đếm từ git log) chưa bao giờ được vào `REV_TYPES`, và còn bằng 0 từ ngày đầu vì một lệnh git
sai bị nuốt lỗi (lộ ra lúc tách repo, bài 07). Nếu cho nó lan nghi cũ thì đó là false sharing nặng nhất: hai file hay cùng sửa không có
nghĩa file này đúng nhờ file kia.

**(b) Hạt cả file.** Cạnh còn lại vẫn so **mốc sửa cả file B**. GDD 600 dòng, ADR chỉ trích mục "§3 Kinh tế". Sửa lỗi chính tả ở §9 thì
ADR vẫn nghi cũ. Đây chính xác là hai biến chung một line: §3 và §9 chung "line" là cả file. Dòng backlog mở 28/10:

> Nghi cũ hạt thô: `suspects()` so mốc sửa cả file B, sửa chỗ không liên quan cũng gây nghi cũ ("false sharing"). Đề xuất: so băm đoạn
> được trích/được tham chiếu thay mốc sửa cả file; chưa làm. (`tools/harness/backlog.md`)

Cách sửa trên CPU là **padding** (đẩy hai biến ra hai line, `alignas(64)`, hay `[StructLayout]` + đệm trong C#), tức là thu nhỏ đơn vị
chia sẻ. Bản tài liệu của padding là **băm đoạn**: lúc `verify` hoặc lúc trích, lưu `sha1(nội dung §3)`. Lần kiểm sau, băm lại §3. Băm
không đổi thì sửa ở §9 không liên quan. Đây cũng là cách Unity theo dõi phụ thuộc trong `Library/`: khoá là băm nội dung, không phải
mtime (bài 03). Lab mục 2 cho thấy số cảnh báo giảm khi đổi hạt.

## 3. Đẩy cờ hay tính cờ lúc đọc

Có hai chỗ để đặt việc kiểm "còn mới không":

- **Đẩy-khi-ghi** (*push*): lúc ghi B, tìm mọi A và **lưu** cờ dirty vào đâu đó. Rẻ lúc đọc. Nhưng ở Seriously, nhiều phiên và nhiều repo
  cùng ghi. Một file cờ chung = xung đột merge, và cờ lưu trong repo này không thấy được ở repo kia. Việc giao 28/10 ghi rõ phần "không làm":
  *"lưu cờ boolean vào file chung (xung đột đa phiên/đa repo)"*.
- **Kiểm-khi-đọc** (*lazy validation*): không lưu cờ. Lúc đọc A, **tính** lại `B.touched > max(A.touched, verified[A])`. Giống
  HTTP `If-Modified-Since` / `ETag`: client giữ bản cũ, hỏi lại "đã đổi chưa" đúng lúc cần dùng.

Seriously chọn cả hai cho hai việc khác nhau: `suspect --send` (đẩy, theo lô, cho chủ sửa) và nhãn lúc đọc (kéo, cho người đang hỏi).
Code nhãn lúc đọc, commit `c30436519` (28/10):

```python
# tools/claude/recall.py
def suspect_reason(kind, path):
    """Kiểm-khi-đọc: 'nghi cũ: <path B> đổi <ngày>' khi nút doc `path` đang nghi cũ theo kg.suspects(); '' nếu không.
    Chỉ cảnh báo, không xếp lại hạng. Thiếu graph / lỗi -> '' im lặng."""
    ...
        hit = kg.suspect_paths().get(rel)
        return f'nghi cũ: {hit[0]} đổi {hit[1]}' if hit else ''
    except Exception:  # a hint never blocks
        return ''
```

`kg.suspect_paths()` nạp đồ thị **một lần mỗi tiến trình**, cache theo mtime của `graph.json`. Ba chi tiết đáng chép:

1. **0 token, gần 0 ms.** Kết quả việc 28/10 ghi hint p95 "172 vs 177 ms": chênh vài ms, nằm trong nhiễu.
2. **Lỗi thì im lặng.** Thiếu đồ thị (máy khác, repo tách) thì không có nhãn, không chặn. Cờ là gợi ý, không phải cổng.
3. **Nhãn, không xếp lại hạng mạnh.** Thứ tự sắp: `(round(điểm/BUCKET), nhãn == 'cu', nhãn != 'chot', điểm)`. Nhãn `cu` chỉ đẩy xuống
   *trong cùng nấc điểm* (BUCKET = 0,5). Comment ghi lý do: hạ hạng mạnh từng làm mất 3 ca para.

Trước đó (commit `53b320508`, 18/10) recall đã có một tín hiệu cấp tài liệu khác, không cần đồ thị:

```python
SUPERSEDED = re.compile(r'^#{1,6} .*(?:đã thay bởi|bị thay bởi|thay thế bởi|superseded|\(cũ\)|— cũ\b)', re.I | re.M)

def doc_outdated(kind, path):
    # (a) tiêu đề trong file nói nó đã bị thay; (b) review có ngày (company/reviews/YYYY-MM-DD-*.md) trích file repo đổi SAU ngày đó
```

Commit đó đưa **cũ↑** (số lần bản cũ xếp *trên* đáp án trong 12 đầu, chỉ đếm bản cũ không mang nhãn `cu`) từ **3 → 0** trên bộ đề,
**1 → 0** trên nhiễu ×5; kw/para không đổi.

**Vấn đề.** Cả ba tín hiệu (`is_stale`, `doc_outdated`, `suspect_reason`) đều trả lời câu "*có cái gì đổi sau ngày X*". Không cái nào trả
lời "*cái này đã bị cái kia thay thế*". Đo thật: nhãn nghi cũ từ đồ thị gắn được **0 / 462** mảnh bơm vào trên 154 ca. Không sai, nhưng
cũng chưa giúp được ca nào.

## 4. Ngày không phải phiên bản: chuyện 29/10

Ca `trap-tunable` (`company/eval/recall/cases.toml`): hỏi *"generator [Tunable] com.sanne.core partial"*, đáp án commit `47c96f29`
(04/10, "[Tunable] generator (core 1.6.0)"), bản cũ phải tránh là `docs/shared/kit-candidates-2026-10-04.md` (danh sách ứng viên viết
*trước* khi làm). Chạy lại logic nhãn của `recall.py` trên đúng hai mảnh này cho bài viết:

```
commit 47c96f29   tier chuyen   is_stale → True      → nhãn 'cu'   ("có thể cũ")
kit-candidates    tier chot     doc_outdated → False, suspect_reason → ''   → nhãn 'chot'
```

Vì sao:

- `is_stale` gắn `cu` cho mảnh *chuyện* (commit, phiên chat) nếu nó **nhắc tên một file đã sửa sau ngày của mảnh**. Commit `47c96f29` sửa
  `June/docs/ai/tunable-wire.md`; file đó được sửa tiếp ngày 07/10. Vậy là commit "cũ". Nhưng file được sửa tiếp là chuyện bình thường của
  *mọi* commit có tuổi. Tín hiệu này đúng cho câu chat "hôm qua tôi thấy X.cs làm Y", sai cho commit: commit là sự kiện, không bao giờ "hết đúng".
- `is_stale` bỏ qua mọi mảnh `chot` (`if tier == 'chot' ...: return False`). `chot` được gán **theo thư mục** (`CHOT = ('knowledge/',
  '/docs/ai/', 'docs/shared/', ...)`), không theo nội dung. Tài liệu ở `docs/shared/` là "chốt" mãi, kể cả khi đã lỗi thời.
- Tiêu đề `kit-candidates` không có chữ "(cũ)" hay "đã thay bởi", và nó không có cạnh `depends_on` nào tới code `[Tunable]`, nên hai tín
  hiệu kia im.

Sắp xếp có `nhãn == 'cu'` và `nhãn != 'chot'` làm khoá phụ, nên khi điểm gần nhau, bản cũ **thắng** đáp án. Ngày 29/10, bật doc2query cho
sổ tay đẩy điểm hai bên sát nhau (bài 04), bản cũ lên hạng 3, đáp án hạng 4, cũ↑ = 1, pre-push đỏ. Sửa nhanh là tắt doc2query cho sổ tay
(`RECALL_D2Q_NOTES=1` để bật lại). Gốc rễ vẫn còn.

Trên CPU, chuyện này giống một giao thức coherence mà bit trạng thái suy ra từ **địa chỉ** (vùng nhớ này luôn coi là Shared sạch) và từ
**đồng hồ** thay vì từ sự kiện ghi thật. Coherence không đến từ thời gian. Nó đến từ việc *ai ghi gì, thay thế cái gì*.

Hướng sửa, cả hai đã có trong thiết kế nhưng chưa vào code (quét 29/10, mục 5: *"so ngày cả file → false sharing; lưu băm đoạn được trích
lúc ghi `verified`, thêm trường `supersedes:` thay regex tiêu đề. 0 token"*):

1. **`supersedes:` tường minh.** Tài liệu/thẻ mới khai trong frontmatter: `supersedes: [shared:doc/kit-candidates-2026-10-04]`. Lúc đọc,
   mảnh nào bị một nút live thay thì nhãn `cu`, bất kể thư mục. Thiết kế M4 đi xa hơn: claim có `valid_from` / `invalid_at` / `status:
   live|superseded`, khi thay thì đóng `invalid_at`, **không xoá** (dữ liệu *bitemporal*: biết cả "đúng từ khi nào" lẫn "ghi khi nào").
2. **Commit không dùng `is_stale`.** Commit là sự kiện bất biến. Thứ có thể cũ là *tài liệu tóm tắt* về nó.

Đây là ý chính của mục này: **dirty bit phải gắn với sự kiện ghi, không suy ra từ đồng hồ hay từ chỗ file nằm**.

## 5. ID ổn định: mũi tên không được trỏ bằng đường dẫn

Mọi thứ ở trên dựa vào mũi tên. Ban đầu `refs` trong `company/units/*.toml` là đường dẫn file. Tách repo (bài 06) chuyển `Thousandfold/`,
`depts/` sang repo khác: đường dẫn đổi, mũi tên gãy, và mũi tên gãy thì **im lặng**: không có cạnh thì không có nghi cũ.

Unity đã giải đúng bài này. Scene không trỏ `Assets/Art/hero.png`; nó trỏ `{guid: 3f2a…, fileID: 21300000}`. GUID nằm trong `hero.png.meta`,
đi theo file khi bạn kéo sang thư mục khác. Xoá `.meta` (hoặc chép file ra ngoài Editor mà quên `.meta`) thì GUID mới sinh ra và mọi tham
chiếu thành *Missing*. Còn `fileID` là ID của **đối tượng bên trong file** (sprite thứ mấy trong atlas): GUID là hạt file, fileID là hạt đoạn.
Đúng hai tầng mà mục 2 cần.

Harness làm tương tự:

```python
# tools/harness/kg.py
def doc_id(rel, fm_id=None):
    if fm_id:                      # frontmatter `id:` ghi đè: ID sống sót qua đổi tên
        return fm_id
    ...
    return f'{u}:doc/{os.path.splitext(sub)[0].lower()}'     # vd. shared:doc/kit-candidates-2026-10-04
```

- **Thực thể** có ID tay, không dính đường dẫn: `harness:concept/routing` (`kg/entities-curated.toml`), với `defined_in =
  "docs/shared/agent-company-design.md"`. Đổi chỗ file định nghĩa chỉ sửa một dòng `defined_in`.
- **Tham chiếu** viết `kg://<id>`: `refs = ["kg://shared:doc/sanne-kit", "kg://shared:doc/kit-candidates-2026-10-04", ...]`
  (`company/units/sanne-kit.toml`). Thư mục và file ngoài repo dùng `kg://ref/<slug>`, đường dẫn thật đặt **một chỗ**:
  `kg/ids.toml [ref]` (vd. `"ref/thousandfold-tools-audio" = "Thousandfold/tools/audio"`). Đổi tên tài liệu: thêm dòng `[alias]` cũ → mới.
- Kết quả (`knowledge-graph-design.md`, R4): 17 refs → `kg://id`, 19 refs → `kg://ref/<slug>`, **0 refs đường dẫn**.

Lưu ý thật thà: ID tài liệu mặc định vẫn **suy từ đường dẫn**; frontmatter `id:` chỉ ghi đè khi có và chưa gắn hàng loạt. Tức là đổi tên
tài liệu không có `id:` mà quên thêm `[alias]` thì vẫn gãy. Giống `.meta` tự sinh lần đầu: chỉ ổn định từ lúc nó tồn tại.

## So sánh các cách giữ "còn mới"

| Cách | Ưu | Gãy ở đâu | Ở Seriously |
|---|---|---|---|
| Không làm gì, tin ngày ghi trên tài liệu | 0 công | bản cũ đọc như bản mới | trước 18/10 (cũ↑ = 3) |
| Tiêu đề tự khai "(cũ)" / "đã thay bởi" (regex) | 0 token, tác giả quyết | quên ghi là mất; không có cạnh tới bản mới | `doc_outdated`, cũ↑ 3 → 0 |
| Đẩy-khi-ghi, lưu cờ (write-invalidate) | đọc rẻ | file cờ chung xung đột đa phiên/đa repo | **không** lưu cờ |
| Đẩy-khi-ghi, gửi việc cho chủ (directory) | đúng phòng, không phải mở phòng kia | trễ (≥ 7 ngày, trần 3/lần) | `kg.py suspect --send` |
| Write-update: tự viết lại tài liệu khi nguồn đổi | luôn khớp | tốn token, vi phạm sở hữu phòng, sai thì lan | cấm |
| Kiểm-khi-đọc theo ngày cả file | 0 token, không trạng thái | false sharing (hạt file); sai chiều nếu nhãn theo thư mục | `suspect_reason`, `is_stale` |
| Kiểm-khi-đọc theo băm đoạn | hết false sharing hạt file | phải lưu băm lúc `verify`; đoạn cần ID | đề xuất, chưa làm |
| `supersedes:` tường minh / claim có `invalid_at` | đúng chiều theo định nghĩa | phải có người/agent khai lúc ghi | thiết kế M4, chưa vào recall |
| TTL (hết hạn sau N ngày) | đơn giản | tài liệu đúng lâu cũng bị nghi | chỉ dùng cho "lạnh" (> 60 ngày, 0 lượt đọc → đề xuất archive) |

## Scale

- **Nhỏ (một người, vài chục tài liệu)**: không cần đồ thị. Quy ước tiêu đề "(cũ) → thay bởi X" và xoá/archive mạnh tay là đủ.
- **Vừa (Seriously: ~2.100 nút, ~5.000 cạnh, 7 phòng, 3 repo)**: đồ thị tất định dựng lại mỗi commit (8 s; `staged` 0,05 s), kiểm-khi-đọc
  cho người hỏi, gửi việc theo lô cho chủ. Phần còn thiếu đúng là hai mục 2b và 4: hạt đoạn và `supersedes`.
- **Lớn (công ty, hàng triệu tài liệu)**: không quét cả đồ thị mỗi lần. Luồng sự kiện thay đổi (*change data capture*) đẩy vào hàng
  đợi; mỗi tài liệu lưu phiên bản của từng nguồn nó trích (*vector version*), so lúc đọc. Dữ liệu dạng claim bitemporal, truy vấn "đúng tại
  ngày X". Giống CPU nhiều socket: thư mục coherence phân tán, không broadcast.

## Bốn nền tảng

- **Mac**: `recall.py` lấy ngày sửa từ `git log` (`last_touch`), không lấy mtime. Đúng: checkout/clone đặt mtime = lúc checkout, nên mtime
  không cho biết nội dung đổi khi nào. APFS mặc định **không phân biệt hoa thường**: ID suy từ đường dẫn phải `.lower()` (code đã làm) để
  `Docs/X.md` và `docs/x.md` không thành hai nút.
- **Windows**: thêm hai bẫy cho ID theo đường dẫn: dấu `\` (chuẩn hoá về `/` trước khi băm hay so), và `core.autocrlf` đổi CRLF/LF làm
  **băm cả file** đổi dù nội dung không đổi. Băm đoạn nên chuẩn hoá xuống dòng trước khi băm. Unity cũng thế: `.meta` nên để `eol=lf`.
- **iOS**: bản tài liệu/nội dung tải về nằm trong cache của app. Kiểm-khi-đọc là cách hợp lý: lúc mở app so băm catalog (Addressables:
  `CheckForCatalogUpdates`) thay vì chờ server đẩy. Push ngầm qua APNs bị hệ điều hành giới hạn và không đảm bảo tới, nên đừng dựa vào nó
  làm tín hiệu invalidate duy nhất.
- **Android**: cùng mẫu. `UnityWebRequestAssetBundle.GetAssetBundle(url, Hash128, crc)` dùng hash làm **phiên bản**: hash khác thì tải lại,
  hash giống thì dùng bản cache. Đó là ID nội dung, không phải ngày. FCM cũng không đảm bảo giao tin ngay khi máy ở chế độ Doze.

## Lab

1. `python3 lab/05_nghi_cu.py`: bốn phần.
   - **False sharing theo loại cạnh**: đồ thị nhỏ, sửa một file; lan qua cả `refs` thì nghi cũ cả loạt, chỉ cạnh cấu trúc thì còn đúng
     nút thật sự dựa vào.
   - **Hạt file vs băm đoạn**: sửa §9 của GDD; so mốc file thì ADR (trích §3) nghi cũ, so băm §3 thì không. Sửa §3 thì cả hai bắt được.
   - **Ngày vs `supersedes`**: dựng lại đúng ca `trap-tunable` với luật nhãn của `recall.py`; xem bản cũ thắng; thêm `supersedes` rồi chạy lại.
   - **ID ổn định**: chuyển thư mục; đếm tham chiếu gãy khi trỏ bằng đường dẫn và khi trỏ `kg://` qua bảng `ids`.
2. Trong Seriously: `python3 tools/harness/kg.py suspect` rồi `python3 tools/harness/kg.py impact docs/shared/sanne-kit.md` và
   `--structural`. So số nút hai lần chạy `impact`, rồi tự giải thích vì sao `suspect` chỉ đi theo cạnh cấu trúc.

## Tóm một dòng

Dirty bit chỉ có ích khi **đúng chiều và đúng hạt**: gắn với sự kiện ghi/thay thế (`supersedes`), không suy từ ngày hay thư mục; theo dõi
theo đoạn, không theo cả file; mũi tên trỏ bằng ID ổn định; và báo cho đúng phòng giữ bản sao thay vì bắt người hỏi tự mở phòng đó.

**Bài sau:** 06 — Chuyển nhà: lớp phủ symlink vs submodule vs monorepo.
