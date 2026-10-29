# 03 — Bake sẵn: doc2query, khoá băm, và ước token trước khi bật

> Bài 3 của chuỗi "migrate thực chiến" (mổ **bước 3** ở [bài 00](00-tong-quan.md), đo bằng thước của [bài 01](01-do-dung-thu-agent-thay.md)).
> Đọc ~14 phút + lab 5 phút. Mang vào: BM25 (bài 00), hit@3 + McNemar (bài 01), cặp âm tiết (bài 02), Unity bake lightmap.

## Chuyện mở đầu

Bài 02 kết thúc ở chỗ: câu hỏi *"đổi biểu tượng trên giao diện web từ ký tự sang ảnh vẽ"* và commit *"web HQ: emoji → icon"* không
chung chữ nào. Cặp âm tiết chỉ giúp khi chữ **có mặt** ở cả hai bên. Ở đây chữ không có. Phía đọc không thể tự đẻ ra chữ còn thiếu
trong tài liệu, nên phải sửa ở phía ghi: nhờ model viết sẵn câu hỏi cho mỗi commit, *một lần*, rồi lưu lại.

## Dừng 30 giây

Bạn sắp bake lightmap cho 1.500 scene, mỗi lần bake tốn tiền thật. Tự liệt kê: phải biết gì *trước* khi bấm nút, scene nào cần bake
lại khi có thay đổi (và Unity dựa vào đâu để biết), và chuyện gì xảy ra nếu bạn chỉnh setting bake trong lúc nhìn đúng scene dùng để chấm điểm.
Giữ ba ý đó. Cả bài đi qua đúng ba ý này, theo thứ tự.

---

## Mạch của bài

```
1. Lỗ từ vựng không vá được ở phía đọc        → chuyển việc sang phía ghi (doc2query) → tốn token, phải ước trước
2. Ước token trước khi bật                     → ước 0,6M > trần 0,3M → cắt phạm vi → thật 0,40M (khớp ước ×1,3)
3. Chỉ sinh lại phần đổi: khoá băm nội dung     → nhưng khoá thiếu "phiên bản prompt" → đổi prompt mà không ai biết phải sinh lại
4. Prompt quyết định chất lượng                 → v1 chép chữ commit: 6→9/33; v2 hỏi theo mục đích: 7→19/33
5. Cái giá                                      → bản cũ cũng được bake → bẫy @3 3→1/5; và phải chứng minh không rò đề
```

## 1. Vì sao phải chuyển sang phía ghi

**doc2query** (Nogueira & Lin, 2019) = với mỗi tài liệu, nhờ model đoán *những câu người ta sẽ gõ để tìm nó*, rồi dán các câu đó vào
tài liệu trước khi đưa vào chỉ mục. Lúc tìm vẫn là BM25 thuần, 0 token, ~20–30 ms. Toàn bộ chi phí model dồn vào lúc ghi.

Đây đúng là **bake lightmap**: tính toán đắt (ánh sáng gián tiếp ↔ hiểu nghĩa câu) làm một lần lúc build, kết quả lưu thành dữ liệu
tĩnh (texture ↔ câu hỏi trong JSONL), lúc chạy chỉ việc đọc. Ngược lại là *realtime GI* ↔ gọi model mỗi lần hỏi (*query rewriting*
bằng LLM): linh hoạt hơn nhưng trả tiền và độ trễ mỗi lần, và kết quả không tất định (mỗi lần hỏi ra một kiểu).

Code thật nối câu hỏi vào mảnh commit (`tools/claude/recall.py`):

```python
def git_rows():
    qs = d2q()                                   # {mã commit: [câu hỏi]} đọc từ company/memory/d2q/commits.jsonl
    ...
    yield f'{s}\n' + ' '.join(fl[:30]) + ... + ('\n' + ' '.join(qs[h]) if h in qs else ''), d, unit, h
```

Mảnh commit giờ chứa: tiêu đề + danh sách file + **4 câu hỏi sinh sẵn**. BM25 không biết đâu là chữ thật, đâu là chữ sinh; nó chỉ
thấy tài liệu giờ có chữ "biểu tượng".

## 2. Ước token trước khi bật

Luật của Seriously (H-10 trong thiết kế): việc tốn token theo lô phải **ước trước, có trần, và chạy xong so thật với ước**. Lý do:
lần thử trước với thẻ chắt lọc (*distill*), số thật lệch ước ×5.

**Công thức** (đơn vị: token, *tok*):

```
tok_vào ≈ N × (ký tự mỗi mảnh ÷ ký tự mỗi token)  +  số_lượt_gọi × mào_đầu_mỗi_lượt
tok_ra  ≈ N × số_câu × token_mỗi_câu  (+ token suy nghĩ, nếu model bật thinking)
số_lượt_gọi = ⌈N ÷ cỡ_lô⌉
```

*Mào đầu* = phần token mỗi lần gọi `claude -p` phải trả dù gửi gì (system prompt, khung hội thoại). Tiếng Việt có dấu tốn token hơn
tiếng Anh (mỗi chữ có dấu hay bị tách nhỏ), nên dùng số đo thật thay vì quy tắc "4 ký tự = 1 token" của tiếng Anh.

**Lần ước thật (R6b, 28/10):**

| | Phạm vi | Ước | Trần | Quyết định |
|---|---|---|---|---|
| Lần 1 | 1.868 commit + 1.469 đoạn sổ tay | 289k vào + 150k ra + ~110 lượt × 1,5k mào đầu ≈ **0,6M** | 0,3M | **dừng, không chạy** |
| Lần 2 | chỉ commit 30 ngày = 1.478 | ≈ 0,32M → trần duyệt 0,42M | 0,42M | chạy |
| Thật | | **≈ 0,40M** | | ≤ ước × 1,3 → đạt |

Hai chi tiết đổi được nhiều tiền nhất, cả hai nằm trong code:

**(a) Tắt suy nghĩ.** Đo một lượt: 212 trong 341 token ra là *thinking* (62 %). Viết câu hỏi không cần suy luận, nên:

```python
r = subprocess.run(['claude', '-p', '--model', 'haiku', '--effort', 'low', '--output-format', 'json', '--max-turns', '1',
                    '--tools', '', '--strict-mcp-config', '--disable-slash-commands', '--no-session-persistence', ...])
```

Mỗi cờ cắt một khoản mào đầu: `--tools ''` (không gửi mô tả tool), `--strict-mcp-config` (không nạp MCP server),
`--disable-slash-commands`, `--no-session-persistence`. `--output-format json` trả về `usage` để **đếm token thật**, không đoán.

**(b) Gộp lô.** 80 commit một lượt gọi: mào đầu trả 19 lần thay vì 1.478 lần. Lô to quá thì model bỏ sót dòng; code đếm
`got/len(batch)` mỗi lô để thấy chuyện đó.

**Phanh** trong vòng lặp:

```python
for i in range(0, len(todo), BATCH):
    if spent >= budget:
        print(f'DỪNG: {spent} tok ≥ trần {budget}')
        return 2
```

Kiểm *trước* mỗi lô, nên có thể vượt trần tối đa **một lô** (~20k tok). Muốn chặn cứng thì kiểm `spent + ước_một_lô ≥ budget`.

## 3. Chỉ sinh lại phần đổi: khoá băm nội dung

Bake lại 1.478 commit mỗi đêm là đốt tiền. Unity giải bài này bằng thư mục `Library/`: mỗi asset có một **khoá băm** từ nội dung
file + setting import + **phiên bản importer**. Khoá không đổi → dùng lại kết quả cũ. Đây gọi là *content-addressed cache*.

doc2query làm y như vậy:

```python
def key_of(text):
    return hashlib.sha1(text[:CUT].encode()).hexdigest()[:10]

todo = [(h, t) for h, t in commits() if have.get(h, {}).get('k') != key_of(t)]
```

Mỗi dòng lưu `{"h": mã commit, "k": khoá, "q": [câu hỏi]}`. Lần chạy sau chỉ gửi commit mới hoặc commit có khoá đổi.

**Lỗ trong khoá (bài học thật).** Ngày 29/10 prompt đổi từ v1 sang v2. Khoá chỉ băm *chữ commit*, không băm *prompt*, nên với
`doc2query.py` thì 1.478 commit cũ "vẫn còn mới", không cần sinh lại. Phiên đó phải sinh lại bằng tay (kho tạm rồi thay file).
Unity không mắc lỗi này vì khoá có **phiên bản importer**: đổi code importer là reimport. Sửa đúng:

```python
PROMPT_VER = 'v2'
def key_of(text):
    return hashlib.sha1((PROMPT_VER + MODEL + text[:CUT]).encode()).hexdigest()[:10]
```

Quy tắc chung của cache: **khoá phải chứa mọi thứ làm đổi đầu ra**. Thiếu một thứ = dữ liệu cũ mà không ai biết là cũ (bài 05 nói
tiếp chuyện này). Lab mục 3 cho bạn thấy lỗ này chạy thật.

Tầng thứ hai cũng có khoá: chỉ mục recall tự dựng lại khi `HEAD + kích thước file commits.jsonl` đổi (`recall.d2q_key`). Kích thước
file là khoá yếu (sửa mà giữ nguyên số byte thì không dựng lại), nhưng đủ dùng vì file chỉ *nối thêm* dòng.

## 4. Prompt quyết định chất lượng: chép chữ vs hỏi theo mục đích

Cùng 1.478 commit, cùng model, hai prompt:

- **v1**: "viết 2 câu hỏi … KHÔNG chép nguyên tên file/hàm, dùng từ đồng nghĩa."
- **v2**: "viết 4 câu theo góc nhìn người **không biết kỹ thuật**, hỏi theo **mục đích** (việc này để làm gì) … TUYỆT ĐỐI không dùng
  tên riêng, tên file, mã, thuật ngữ trong dòng commit; thay bằng từ đời thường (icon → biểu tượng, cache → bộ nhớ đệm).
  Câu cuối là cụm 5–8 từ đồng nghĩa."

Ví dụ thật, commit `memory R7+R8: M4 đọc claim trong memhub.ask, Stop hook tóm phiên nối (cờ tắt), bảng ước token R7, +3 ca gu ảnh`:

```
v1: "Commit nào bật tóm tắt phiên lúc dừng và thêm ca kiểm tra gu ảnh?"
    "Bảng ước lượng token cho vòng R7 nằm ở commit nào nhỉ?"
v2: "Việc tóm tắt phiên làm việc được bật hoặc tắt bằng cách nào?"
    "Những ví dụ mới về gu hình ảnh được thêm để làm gì?"
    "Bổ sung khả năng đọc và tóm tắt phiên làm việc"
```

Đo trên toàn bộ kho (đo lại 29/10 cho bài này):

| | v1 | v2 |
|---|---|---|
| Câu mỗi commit | 2 | 4 |
| Từ trong câu hỏi mà commit đã có sẵn | **44 %** | **11 %** |

v1 dù được dặn vẫn chép gần nửa số chữ. Chép chữ commit vào commit thì BM25 không được thêm gì: chữ đó đã có. Giá trị của doc2query
nằm hết ở **chữ mới**. Đây là lý do số para nhảy mạnh khi đổi prompt, không phải khi đổi model.

**Kết quả** (`kit recall-eval`, bộ 33 câu diễn đạt lại; cặp âm tiết bài 02 bật ở cả hai dòng "29/10"):

| Cấu hình | para @3 | para @12 | Ghi chú |
|---|---|---|---|
| Nền (không doc2query) 28/10 | 6/33 | 10/33 | |
| v1, 2 câu (R6b) 28/10 | 9/33 | 14/33 | McNemar p = 0,125 → chưa chắc |
| Cặp âm tiết, không doc2query 29/10 | 7/33 | 13/33 | `RECALL_D2Q=0` |
| **Cặp âm tiết + v2, 4 câu** 29/10 | **19/33** | **21/33** | so nền: được 11, mất 0, **p = 0,001** |

Đọc cột @3 với @12 cùng lúc: v2 không chỉ kéo đáp án vào top 12 mà kéo lên **top 3**, tức là lên được ngữ cảnh của agent (bài 00:
L1 chỉ chứa 3).

## 5. Cái giá: bản cũ cũng được bake, và nghi ngờ rò đề

**(a) Bẫy bản cũ tụt.** Cùng lần đo, nhóm *bẫy* (5 câu có một bản quyết định cũ và một bản mới) cho:

| | không doc2query | có v2 |
|---|---|---|
| bẫy @3 | 3/5 | **1/5** |
| bẫy MRR | 0,37 | 0,19 |
| cũ↑ (bản cũ xếp *trên* bản mới) | 0 | 0 |

Nguyên nhân dễ thấy khi nghĩ theo prompt v2: hỏi theo **mục đích** thì commit cũ ("đổi icon thành chữ cái") và commit mới ("đổi chữ
cái thành icon") sinh ra *cùng* câu hỏi ("đổi biểu tượng các phòng để làm gì"). Bake xoá mất chính chi tiết phân biệt hai bản. Cả hai
cùng leo, nên đáp án bị đẩy khỏi top 3 dù bản cũ chưa vượt bản mới (cũ↑ vẫn 0, cổng vẫn xanh). Nhóm chỉ 5 câu nên là chỉ báo,
nhưng hướng sửa rõ: commit đã bị thay thế thì không bake câu hỏi, hoặc trừ điểm (bài 05).

**(b) Rò đề** (*leakage*). Câu hỏi sinh ra trông rất giống câu trong bộ đề, vì cả hai cùng là "người hỏi nói đời thường". Nếu máy sinh
từng *thấy* bộ đề thì 19/33 là số giả. Ba lớp chặn:

1. **Cấu trúc**: máy sinh chỉ nhận `mã | 200 ký tự commit`, không bao giờ nhận file `cases.toml`. Docstring ghi rõ, review kiểm.
2. **Đo**: đếm câu sinh có chung một chuỗi 5 chữ liên tiếp (*5-gram*) với câu đề. v1: **0**. v2: **2**, cả hai là cụm
   *"kiểm tra trước khi đẩy"*, đó là cách dịch tự nhiên của "pre-push", có trong commit. Hai bên dịch giống nhau, không phải chép.
3. **Không chỉnh theo ca**: prompt v2 được viết theo *loại lỗi* (chép chữ, dùng thuật ngữ), không theo từng câu trượt.

Còn một tín hiệu cần canh: chuỗi 3 chữ chung với đề tăng 44 → 179. Đó chính là mục đích (nói giọng người hỏi), nhưng cũng là lý do
**bộ đề phải có câu mới định kỳ**, viết bởi người không đọc câu sinh. Giống benchmark shader: cập nhật scene test, đừng tối ưu mãi trên một scene.

## So sánh: chi phí model đặt ở đâu

| Cách | Trả token lúc | Tất định | Ưu | Gãy ở đâu |
|---|---|---|---|---|
| Chỉ BM25 + cặp âm tiết | không bao giờ | có | 0 đồng, nhanh | lỗ từ vựng (chữ không có mặt) |
| **doc2query** | ghi (một lần / mảnh) | có, sau khi bake | đọc vẫn 0 token; câu sinh đọc được, sửa tay được | khoá cache thiếu thứ; bake mất chi tiết cũ/mới; ngốn token khi kho lớn |
| Viết lại truy vấn bằng LLM | mỗi lần hỏi | không | biết ngữ cảnh câu hỏi | trả tiền + ~1–2 s mỗi prompt; khó tái lập để đo |
| Vector (embedding) | ghi + đọc (rẻ, model nhỏ) | có | khớp theo nghĩa | khó giải thích vì sao trúng; bản cũ/mới gần nhau trong không gian vector y như bẫy ở mục 5 |
| Model xếp hạng lại (*reranker*) | mỗi lần hỏi, chỉ top K | gần | sửa thứ hạng rất tốt | chỉ sửa được đáp án *đã* lọt vào top K |

Seriously chọn doc2query vì hai luật nền: hook mỗi prompt phải nhanh và 0 token, và mọi kết quả phải đo lại được giống hệt.

## Scale

- **Nhỏ (vài trăm tài liệu)**: không cần bake, đọc hết hoặc BM25 là đủ.
- **Vừa (Seriously: ~1.900 commit + vài nghìn đoạn)**: bake theo lô, có trần, khoá băm. 1.478 commit ≈ 0,4M tok một lần, sau đó chỉ
  trả cho commit mới (~50/ngày ≈ vài nghìn tok). Mở rộng sang sổ tay/inbox đang chờ chạy `--dry` để có số thật trước.
- **Lớn (hàng triệu)**: model sinh câu hỏi nhỏ tự chạy (bản gốc dùng T5, không phải LLM lớn), bake trong pipeline dữ liệu; câu sinh
  được lọc bằng chính bộ tìm (chỉ giữ câu mà tìm lại ra đúng tài liệu, gọi là *round-trip filtering*).

## Bốn nền tảng

Bake chạy trên máy dev/CI; đọc chạy ở nơi agent hoặc game chạy. Tách hai việc này là điểm mấu chốt khi nhiều nền tảng.
- **Mac**: chạy như trong repo. `claude -p` dùng đăng nhập của máy; trần token là chặn tiền duy nhất, nên đừng bỏ `--budget`.
- **Windows**: `doc2query.py` gọi `subprocess.run(..., cwd='/tmp')`, đường dẫn này không có trên Windows (lỗi khi chuyển máy). Dùng
  `tempfile.gettempdir()`. Đặt `PYTHONUTF8=1` để đọc/ghi JSONL tiếng Việt không vỡ.
- **iOS / Android** (nếu game có ô tìm kiếm, ví dụ tra công thức trong game): không gọi được model lúc chơi, và không nên. Bake câu
  hỏi lúc build, đóng gói như dữ liệu tĩnh (giống `StreamingAssets`), lúc chơi chỉ BM25. iOS có SQLite hệ thống kèm FTS5. SQLite có
  sẵn của Android không chắc bật FTS5, nên đóng gói bản SQLite riêng (vd. `requery/sqlite-android`) hoặc tự viết BM25 trong C#.

## Lab

1. `python3 lab/03_bake_san.py`: ba phần.
   - **Bake**: thấy đáp án không lọt top khi chỉ có chữ commit, lên hạng 1 sau khi dán câu hỏi v2, và câu hỏi kiểu v1 thì không giúp.
   - **Ước token**: hàm ước với số R6b; đổi `n_q`, `batch`, bật thinking để thấy khoản nào to nhất.
   - **Khoá cache**: đổi prompt, khoá cũ báo "0 cần sinh lại"; khoá có phiên bản prompt báo đủ.
2. Trong Seriously: `RECALL_D2Q=0 python3 tools/claude/recall_eval.py` rồi chạy lại không có biến (mỗi lần ~2–3 phút). So dòng `para @3`
   và dòng `trap`, rồi tự giải thích vì sao một dòng lên còn dòng kia xuống.

## Tóm một dòng

Chữ không có trong tài liệu thì phía đọc không tìm ra. **Bake** chữ của người hỏi vào lúc ghi: ước token trước, khoá cache phải chứa cả
phiên bản prompt, và giá trị nằm ở **chữ mới**, không phải chữ chép lại.

**Bài sau:** 04 — Trộn nhiều kho: RRF và hạn ngạch.
