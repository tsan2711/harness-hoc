# 04 — Trộn nhiều kho: RRF, hằng k, trọng số và hạn ngạch

> Bài 4 của chuỗi "migrate thực chiến" (mổ **bước 4** ở [bài 00](00-tong-quan.md): nhiều nguồn cùng tranh 3 chỗ trong L1; đo bằng thước của [bài 01](01-do-dung-thu-agent-thay.md)).
> Đọc ~14 phút + lab 5 phút. Mang vào: BM25 (bài 00), hit@3 + McNemar (bài 01), cặp âm tiết (bài 02), doc2query (bài 03), Unity Profiler.

## Chuyện mở đầu

Tối 29/10, bật câu hỏi sinh sẵn (doc2query, bài 03) cho sổ tay. Ca bẫy `trap-tunable` (câu *"generator [Tunable] com.sanne.core partial"*)
lập tức hỏng: tài liệu cũ `kit-candidates-2026-10-04.md` lên hạng 3, commit đáp án tụt xuống hạng 4. Bỏ câu hỏi của chính tài liệu cũ đó:
vẫn hỏng. Chỉ tắt toàn bộ câu hỏi của sổ tay mới hết. Trong lúc đó cổng pre-push đỏ và chặn push của mọi phiên.

## Dừng 30 giây

Bạn có hai bản Profiler capture của cùng một cảnh, một từ máy dev, một từ điện thoại. Cột ms của hai bản không cùng thang. Sếp muốn một
danh sách "3 chỗ nóng nhất" duy nhất. Hình dung cách ghép hai danh sách mà không cộng ms của hai máy. Rồi hình dung danh sách 3 chỗ đó là
một pool có đúng 3 slot, và một nguồn có 200 mục, nguồn kia có 5.

---

## Mạch của bài

```
1. Hai lượt tìm cho hai thang điểm khác nhau   → không cộng điểm được → trộn theo HẠNG (RRF)
2. RRF có hai núm: k và trọng số W              → núm vặn được thì phải quét lưới → lưới lộ cái giá
3. Thắng para, hỏng bẫy                         → chọn cấu hình giữ "cũ↑ 0"; danh sách phụ trùng danh sách chính thì trộn vô ích
4. Nhiều kho tranh 3 chỗ L1                     → hạn ngạch (trần cho kho to) + sàn (kho do luật chọn không bị bỏ)
5. Trộn làm các kho dính nhau                   → đổi một kho xáo top của kho khác (29/10) → cổng phải chạy mỗi lần push
```

## 1. Vì sao trộn theo hạng, không theo điểm

Bài 02 thêm một **lượt tìm** (*pass*: một câu truy vấn chạy riêng trên chỉ mục) khớp cặp âm tiết liền kề, chạy song song với lượt thường
khớp từ đơn. Giờ có hai danh sách xếp hạng. Phải ghép thành một.

Ý đầu tiên: cộng điểm BM25. Không được. Điểm BM25 phụ thuộc vào số từ khớp, độ hiếm của từ (IDF) và độ dài tài liệu. Lượt thường khớp
nhiều từ đơn nên điểm to. Lượt cặp khớp cụm hiếm, ít tài liệu khớp, điểm nhỏ và phân bố khác. Cộng hai thứ đó giống cộng ms của
Profiler trên Mac M2 với ms trên một máy Android tầm trung: số to hơn thắng, không phải chỗ nóng hơn. Lab mục 1 cho thấy: cộng thô thì
đáp án nằm hạng 5, lượt cặp gần như vô hình.

Ý thứ hai: chuẩn hoá mỗi lượt về 0..1 (*min-max*) rồi cộng. Chạy được, nhưng hạng 1 của lượt nào cũng thành 1,0, kể cả khi lượt đó chỉ
khớp một tài liệu rác. Thang đã chuẩn hoá vẫn phụ thuộc vào giá trị ngoại lai.

**RRF** (*Reciprocal Rank Fusion*, Cormack, Clarke & Büttcher, SIGIR 2009) bỏ hẳn điểm, chỉ dùng thứ tự:

```
điểm_trộn(d) = Σ_qua_các_lượt  w / (k + hạng_của_d_trong_lượt_đó)
```

Tài liệu không có mặt trong một lượt thì lượt đó góp 0. Bài báo gốc thử trên các bộ TREC và thấy công thức đơn giản này thắng các cách
trộn theo điểm phổ biến lúc đó. Nó dùng `k = 60`, `w = 1`.

Code thật (`tools/claude/recall.py`):

```python
BIGRAM_W = float(os.environ.get('RECALL_BIGRAM_W', '1.0'))
BIGRAM_K = 3
BASE_K = 1      # RRF constant of the usual pass (small = its top ranks are hard to displace: keeps the trap/stale ordering)

def search(c, q, ...):
    base = _search(c, q, ...)                    # lượt thường
    if BIGRAM_W <= 0:
        return base
    bi = _search(c, q, ..., bigram=True)         # lượt cặp âm tiết: bigram_query(q) = "a b" OR "b c" ...
    if not bi:
        return base
    sc, keep = {}, {}
    for w, k, rows in ((1.0, BASE_K, base), (BIGRAM_W, BIGRAM_K, bi)):
        for rank, r in enumerate(rows):
            key = (r[4] or r[3], r[3])           # khoá tài liệu, để một tài liệu có mặt ở hai lượt được cộng dồn
            sc[key] = sc.get(key, 0.0) + w / (k + rank)
            if key not in keep:
                keep[key] = r ...                 # giữ hàng của lượt thường nếu có
    return [keep[k] for k in sorted(sc, key=lambda k: -sc[k])[:limit]]
```

Ba chi tiết đáng đọc kỹ:

- `enumerate` đếm hạng **từ 0**, bài báo đếm từ 1. Nên `BASE_K = 1` ở đây tương đương `k = 0` trong bài báo: hạng 1 được 1/1 = 1,0.
  Khi so số k giữa hai hệ, kiểm hạng bắt đầu từ đâu.
- Lượt thường chạy trước nên chèn khoá trước. `sorted` trong Python ổn định, nên khi hoà điểm thì tài liệu của lượt thường đứng trước.
  Docstring ghi "the usual pass wins ties". Đây là luật hoà được viết bằng thứ tự vòng lặp, không bằng một dòng `if`.
- Hai lượt là hai câu FTS chạy tuần tự. Thời gian tìm tăng từ ~12 ms lên 23–28 ms (trung bình trên bộ eval).

## 2. Hai núm: k và W

**k làm phẳng đầu bảng.** Với `w = 1`, điểm theo hạng 1..5 (lab mục 2):

| k (hạng từ 0) | hạng 1 | hạng 2 | hạng 3 | hạng 1 ÷ hạng 2 |
|---|---|---|---|---|
| 1 | 1,000 | 0,500 | 0,333 | ×2,00 |
| 3 | 0,333 | 0,250 | 0,200 | ×1,33 |
| 5 | 0,200 | 0,167 | 0,143 | ×1,20 |
| 60 | 0,017 | 0,016 | 0,016 | ×1,02 |

k nhỏ: đầu bảng dốc, hạng 1 của một lượt rất khó bị chiếm. k lớn: gần như phẳng, tài liệu có mặt ở *nhiều* lượt thắng tài liệu đứng
đầu *một* lượt. Đây là kiểu "bỏ phiếu": k = 60 hợp khi trộn nhiều lượt ngang hàng mà không biết lượt nào đáng tin hơn.

Seriously đặt hai k khác nhau có chủ đích: `BASE_K = 1` (lượt thường giữ đầu bảng, vì đầu bảng của nó đã đúng với câu từ khoá và giữ
thứ tự bản mới trên bản cũ), `BIGRAM_K = 3` (lượt cặp được chen vào nhưng không chiếm). Giống phân ưu tiên luồng: luồng chính không bị
chặn, luồng phụ chỉ lấp chỗ trống.

**W là tiếng nói của một lượt.** W = 0 tắt lượt đó. W càng lớn, lượt đó càng kéo được tài liệu của nó lên. Cái giá: lượt cặp kéo lên
*mọi* tài liệu chứa cụm từ của câu hỏi, kể cả bản cũ của cùng một quyết định.

**k lớn có thể làm hỏng câu đang đúng.** Lab mục 2 dựng lại một ca từ khoá: lượt gốc đúng hạng 1, một truy vấn viết lại (w = 0,3) không
chứa đáp án. Với k = 1, đáp án giữ hạng 1. Với k = 5, đáp án tụt hạng 3 vì hai tài liệu khác có mặt ở cả hai lượt. MRR của ca đó từ
1,00 xuống 0,33. Đây đúng là chuyện thật ở mục 3.

## 3. Thắng một chỉ số, hỏng chỉ số khác

**Lần 1: viết lại truy vấn rồi trộn (27/10), không có lợi.** `recall.search_fused` lấy 3 từ hiếm nhất của câu hỏi (IDF cao) làm một
truy vấn phụ, rồi RRF với `FUSE_K = 5`, trọng số 1,0 / 0,3. Lần đo đầu: para@3 (33 câu diễn đạt lại, đáp án có trong 3 kết quả đầu không)
4 → 6/33, thời gian ×3. Đo lại trên bộ 33 ca đã sửa: **fuse 6/33 = không fuse 6/33**, còn MRR của nhóm câu từ khoá **0,83 → 0,73**.
Kết luận: tắt. Hàm vẫn còn trong code nhưng chỉ bật trong eval bằng `RECALL_FUSE=1`.

Vì sao vô ích: truy vấn phụ dựng từ chính các từ của câu gốc. Nó trả về gần như cùng các tài liệu, chỉ xáo thứ tự. RRF chỉ thêm được
giá trị khi các lượt **sai ở những chỗ khác nhau**. Hai danh sách tương quan cao thì trộn chỉ cộng nhiễu, và k = 5 phẳng đủ để nhiễu đó
đẩy đáp án đúng xuống (đúng hình dạng lab mục 2). Giống lấy hai capture Profiler trên cùng một máy, cùng một frame: thêm capture không
thêm thông tin.

**Lần 2: cặp âm tiết + RRF (29/10), có lợi.** Lượt cặp khớp thứ lượt thường không khớp được (cụm "giao diện", "biểu tượng" thay vì
"giao", "diện" lẻ chìm trong âm tiết thường). Hai lượt sai ở chỗ khác nhau. Với `BASE_K = 1, BIGRAM_K = 3, W = 1`:

| | para@3 | so nền 6/33 | câu từ khoá @3 | bẫy @12 | cũ↑ | ms |
|---|---|---|---|---|---|---|
| Trước (có doc2query v1) | 9/33 | | 32/33 | 3/5 | 0 | ~12 |
| **Cặp âm tiết + RRF** | **12/33** | được 7, mất 0, McNemar p = 0,016 | 32/33 | 3/5 | 0 | 23–28 |

*Cũ↑* = số ca bẫy mà bản quyết định cũ xếp **trên** bản mới. Đây là lỗi nặng nhất của trí nhớ agent: agent đọc quyết định đã bị thay và
làm theo nó. Cổng pre-push đỏ khi cũ↑ > 0.

**Quét lưới W/K.** Trên bộ 33 ca, W lớn hơn cho para@3 **13–14/33**, nhưng cũ↑ = 1. Cấu hình được chọn là cấu hình tốt nhất trong số
giữ cũ↑ = 0, không phải cấu hình para cao nhất. Lab mục 3 dựng lại đúng hình dạng này với 5 ca:

```
   W    K | para@3 | kw@3 | cũ↑
  0.0    3 |  1/3   | 1/1  |  0     tắt lượt cặp
  1.0    3 |  2/3   | 1/1  |  0     ← cấu hình chọn
  2.0    1 |  3/3   | 1/1  |  1
  3.0    3 |  3/3   | 1/1  |  1
```

Luật chung: **chỉ số phụ là ràng buộc, không phải thứ đánh đổi**. Một cấu hình para +2 mà cũ↑ +1 là cấu hình hỏng. Với GPU cũng vậy: bỏ
một pass để được 2 ms mà hỏng ảnh là bug, không phải tối ưu. Lưu ý thêm: lưới quét trên chính bộ đề nên số tốt nhất trên lưới hơi lạc
quan (*overfit* vào đề). Chọn cấu hình đơn giản, giải thích được, không chọn đỉnh nhọn nhất.

## 4. Hạn ngạch và sàn: 3 chỗ trong L1

Bài 00: ngữ cảnh agent chỉ nhét được khoảng 3 đoạn mỗi lần hỏi, như L1. Khi `memhub.ask` hỏi nhiều *kho* (commit, sổ tay phòng mình,
sổ tay phòng khác, claim…), các kho tranh nhau đúng 3 chỗ đó. Giống một object pool có số slot cố định: nếu một nguồn spawn nhanh hơn,
nó chiếm hết pool.

Code thật (`tools/claude/memhub.py`):

```python
RRF_K = 1          # nhỏ: hạng 1 của kho đứng sau vẫn thắng hạng 3 của kho đứng trước
RRF_POS = 0.12     # trọng số kho theo thứ tự trong phiếu: 1/(1+POS*vị_trí)
XDEPT_QUOTA = {'M2': 2}   # câu liên phòng: kho phụ (M2) tối đa 2 chỗ trong top

def rrf_merge(stores, per, limit, quota=None):
    ...
    for pos, s in enumerate(stores):
        w = 1 / (1 + RRF_POS * pos)
        for r, h in enumerate(per[s]):
            sc[(s, r)] = (w / (RRF_K + r), pos, r, h)
    ranked = [v[3] for v in sorted(sc.values(), key=lambda v: (-v[0], v[1], v[2]))]
    if quota:                                   # bỏ hàng của kho đã dùng hết chỗ
        ...
    return ranked[:limit]
```

Ba cơ chế, mỗi cái giải một chuyện:

1. **RRF giữa các kho, k = 1.** Điểm BM25 của kho commit và kho sổ tay không cùng thang (kho khác nhau, độ dài khác nhau), nên lại trộn
   theo hạng. Với k = 1 và trọng số kho gần nhau, hạng 1 của mỗi kho thắng hạng 2 của bất kỳ kho nào. Kết quả tự **xen kẽ**: top 3
   thường có mỗi kho một mục (lab mục 4).
2. **Hạn ngạch = trần cho kho to.** `XDEPT_QUOTA = {'M2': 2}`: với câu liên phòng, kho commit (M2) giữ tối đa 2 chỗ trong danh sách
   trả về, phần còn lại để cho sổ tay hai phòng. Trong code đây là **trần** cho một kho, không phải mức tối thiểu cho kho khác. Tác dụng
   gần như nhau khi kho kia có hàng, khác nhau khi kho kia rỗng (chỗ thừa bị bỏ trống thay vì nhường lại). Kèm hạn ngạch, câu liên phòng
   trúng 33 → 47 % (bài 00).
3. **Sàn ở bước chọn kho.** Trước khi tìm, một bộ luật tất định (bậc 1) chọn danh sách kho; một model (bậc 2) có thể gợi ý thêm.

   ```python
   def merge_tiers(tier1, tier2, extra_cap=2):
       """B5: tủ do bậc 1 chọn là SÀN. Bậc 2 (model) chỉ được thêm tủ (tối đa extra_cap), không bỏ tủ nào của bậc 1, không đổi thứ tự bậc 1."""
       return list(tier1) + [s for s in dict.fromkeys(tier2 or []) if s not in tier1][:extra_cap]
   ```

   `dict.fromkeys` khử trùng mà giữ thứ tự. Model chỉ **thêm** được tối đa 2 kho, xếp sau. Nó không bỏ được kho nào luật đã chọn và không
   đổi thứ tự (thứ tự kho quyết định trọng số `1/(1+0,12×vị_trí)` ở trên). Phần tất định là sàn; phần không tất định chỉ được cộng thêm.

## 5. Trộn làm các kho dính nhau

Quay lại chuyện mở đầu. Bật câu hỏi sinh sẵn cho sổ tay thì một tài liệu cũ vượt commit đáp án. Bỏ câu hỏi của chính tài liệu cũ: vẫn
vượt. Lý do: BM25 dùng **thống kê toàn kho**: IDF (từ hiếm cỡ nào trong cả kho) và độ dài tài liệu trung bình. Thêm hàng nghìn câu hỏi
vào sổ tay làm đổi IDF của "generator", "partial", "tunable"… cho **mọi** tài liệu, kể cả tài liệu không được thêm chữ nào. Top 5 của cả
hai lượt bị xáo, rồi RRF với k nhỏ khuếch đại một lần đổi hạng nhỏ ở đầu bảng.

Đây là *false sharing* của tìm kiếm: bạn ghi vào biến của mình, nhưng biến đó nằm chung cache line với biến của luồng khác, nên luồng kia
bị invalidate dù không ai đụng vào dữ liệu của nó. Bài 05 nói tiếp chuyện này.

Hệ quả vận hành:

- Cổng không thể chỉ chạy khi "sửa code tìm kiếm". Đổi **dữ liệu** của một kho cũng đổi xếp hạng của kho khác. Cổng recall chạy ở
  pre-push, và nó đỏ đúng lúc.
- Sửa nhanh là tắt (`RECALL_D2Q_NOTES=1` để bật lại khi A/B) và đặt lại nền đo. Sửa thật (đang mở): không bake câu hỏi cho bản đã bị
  thay thế, hoặc trừ điểm bản cũ.

## So sánh các cách trộn

| Cách | Ưu | Gãy ở đâu | Ở Seriously |
|---|---|---|---|
| Cộng điểm thô | đơn giản | thang to nuốt thang nhỏ | không dùng |
| Chuẩn hoá điểm (min-max, L2) rồi cộng | giữ được khoảng cách điểm | ngoại lai làm lệch thang; hạng 1 lượt nào cũng = 1,0 | không dùng |
| **RRF** (w = 1, k = 60) | không cần biết thang; bền | phẳng: câu đã đúng có thể bị kéo xuống | không dùng k lớn |
| **RRF có trọng số, k riêng mỗi lượt** | ưu tiên lượt đáng tin, lượt phụ chỉ lấp chỗ | thêm núm → phải quét lưới, dễ khớp đề | `recall.search` (1/1 + 1/3), `memhub.rrf_merge` |
| Viết lại truy vấn + RRF | 0 token | vô ích khi lượt phụ tương quan với lượt chính | `search_fused`, tắt (`RECALL_FUSE=1`) |
| Hạn ngạch / xen kẽ theo kho | không kho nào chiếm hết L1 | kho kia rỗng thì chỗ bỏ trống | `XDEPT_QUOTA` |
| Sàn khi chọn kho | phần tất định không bị model gỡ | model không sửa được luật sai | `merge_tiers` |
| Model xếp hạng lại (*reranker*) | xếp lại chuẩn nhất | tốn token mỗi lần hỏi; chỉ xếp lại thứ đã lọt top N | chưa (luật 0 token mỗi prompt) |

Hệ ngoài: Elasticsearch và OpenSearch đều có *hybrid search*: chạy một lượt BM25 và một lượt vector (*embedding*), rồi trộn. Cả hai
cung cấp RRF; OpenSearch còn có đường chuẩn hoá điểm (min-max, L2) rồi cộng có trọng số. Elasticsearch đặt hằng RRF mặc định là 60 như
bài báo, và chỉ trộn trong một *cửa sổ* N kết quả đầu mỗi lượt. Lý do họ mặc định k lớn: họ không biết dữ liệu của bạn, nên chọn cách
bền nhất. Seriously có bộ đề riêng nên dám đặt k nhỏ và đo.

## Scale

- **Nhỏ (một kho, vài trăm tài liệu)**: một lượt là đủ. Trộn chỉ thêm ms và núm.
- **Vừa (Seriously: ~1.900 commit + vài nghìn đoạn sổ tay, ~10 kho)**: hai lượt trong một kho + RRF giữa kho, k nhỏ, trọng số theo thứ tự
  kho, hạn ngạch cho kho to. Mọi núm đều quét trên bộ đề, với cổng cũ↑ = 0. Hai lượt tuần tự 23–28 ms, vẫn xa ngân sách hook 300 ms.
- **Lớn (hàng triệu, nhiều shard)**: BM25 + vector + có khi tìm theo người dùng, trộn bằng RRF k lớn trong cửa sổ top N mỗi lượt (không
  trộn cả danh sách). Khi có log nhấp chuột thì học trọng số trộn từ log (*learning to rank*), hoặc thêm model xếp hạng lại cho top 50.

## Bốn nền tảng

RRF là ~15 dòng, không cấp phát gì lớn, tất định. Phần đắt là chạy *hai* lượt tìm.
- **Mac**: như trong repo. Hai lượt là hai câu SQLite FTS5 tuần tự trên một kết nối; muốn song song thì mỗi luồng một kết nối riêng
  (một kết nối SQLite không nên dùng chung giữa hai luồng chạy đồng thời).
- **Windows**: Python tải từ python.org kèm SQLite riêng; chạy `pragma compile_options` và tìm `ENABLE_FTS5` trước khi tin. Khởi động
  `python` trên Windows thường chậm hơn Mac (antivirus quét file), nên đo ngân sách hook từ lúc gọi tiến trình, không chỉ thời gian
  tìm. Đặt `PYTHONUTF8=1` để chuỗi tiếng Việt trong khoá trộn không vỡ.
- **iOS** (ô tìm kiếm trong game): SQLite hệ thống có FTS5. Viết RRF bằng C# trong Unity, chạy hai lượt trên luồng nền: 23–28 ms là hơn
  một frame 16,7 ms. Dùng `Dictionary` cấp sẵn dung lượng và tái dùng giữa các lần gõ để không sinh rác cho GC mỗi phím.
- **Android**: như iOS, nhưng SQLite có sẵn không chắc bật FTS5, nên đóng gói SQLite riêng hoặc tự viết BM25. Với máy yếu, cân nhắc chỉ
  chạy lượt thứ hai khi lượt đầu trả kết quả yếu, thay vì luôn chạy cả hai.

## Lab

1. `python3 lab/04_rrf.py`: bốn phần.
   - **Thang điểm**: cộng điểm thô đẩy đáp án xuống hạng 5; RRF đưa lên hạng 2 mà không cần biết điểm.
   - **Hằng k**: bảng điểm theo hạng với k = 1, 3, 5, 60; một ca từ khoá tụt từ hạng 1 xuống hạng 3 khi k = 5.
   - **Lưới W × K**: para@3 tăng theo W, cũ↑ bật lên 1; chỉ một ô vừa có para tốt vừa giữ cũ↑ = 0.
   - **Hạn ngạch + sàn**: xen kẽ tự nhiên khi k = 1, trần 2 chỗ cho kho commit, `merge_tiers` chép nguyên từ repo.
2. Trong Seriously: `RECALL_BIGRAM_W=0 python3 tools/claude/recall_eval.py` rồi chạy lại với `RECALL_BIGRAM_W=2`. So dòng `para @3` và
   dòng `trap` / cũ↑, rồi tự giải thích vì sao cấu hình mặc định là 1.

## Tóm một dòng

Điểm của hai lượt tìm không cùng thang, nên **trộn theo hạng** (RRF): k quyết định đầu bảng dốc hay phẳng, W quyết định tiếng nói mỗi
lượt, hạn ngạch giữ 3 chỗ L1 không bị một kho chiếm; và cấu hình thắng para mà làm bản cũ vượt bản mới là cấu hình hỏng.

**Bài sau:** 05 — Invalidation: nghi cũ, false sharing, ID ổn định.
