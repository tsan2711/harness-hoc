# 03 — Query routing: luật → JSON schema → model, gộp kết quả bằng RRF, và biết nói "không có"

> Bài 3/6. Đọc ~10 phút. **Đã biết:** 11 kho, adapter cùng định dạng ([02](02-muoi-mot-loai-tri-nho.md)).
> Code thật: `recall.INTENTS/route()`, `memhub.plan()/ask()`, `recall.coverage()` (đã có). Thiết kế: V6, §5 (bậc model = K2, chưa làm).

## Chuyện mở đầu

Router cũ có 4 regex, cái nào khớp trước thì thắng. Câu "tại sao perf vùng 2 tụt sau khi đổi grass" khớp `tai sao`, nên bị xếp là
`decided`. Kết quả là tìm chữ trong sổ tay, trong khi một nửa câu trả lời nằm trong chuỗi số đo. Câu thật hay cần **nhiều kho cùng lúc**.

## Dừng 30 giây

Router chạy *trước mỗi câu* Bi gõ. Hãy tự tính ngân sách thời gian và token cho nó. Đầu ra của router phải có hình dạng gì để phần phía
sau không cần biết ai đã sinh ra nó: luật, model, hay cache?

---

## 1. Định nghĩa

- **Query routing**: ánh xạ một câu hỏi sang *chiến lược truy xuất* (kho nào, lọc gì, mấy bước).
- **Intent classification**: phân loại câu hỏi vào một tập nhãn đóng (`lookup|decided|episode|impact|overview|howto|metric|taste|asset|default`).
- **Query plan**: bản ghi có cấu trúc mô tả chiến lược. Ở đây là JSON theo schema cố định (§5.1).

## 2. Router v1: first-match-wins (`recall.py`, dòng 456–470)

```python
INTENTS = (          # first match wins; folded, lower-case
    ('lookup', re.compile(r'(?:[\w.-]+/[\w.-]+)|\bcs\d{4}\b|\btest_\w+|...')),
    ('impact', re.compile(r'\b(?:anh huong|phu thuoc|lech|doi .{1,40} thi|dung toi|keo theo)\b')),
    ('episode', re.compile(r'\b(?:lan truoc|hom qua|hom nay|tuan truoc|...)\b')),
    ('decided', re.compile(r'\b(?:da chot|chot|quyet dinh|tai sao|ly do|vi sao|...)\b')),
)
def route(q):
    f = fold(q).lower()
    for name, rx in INTENTS:
        if rx.search(f):
            return name
    return 'default'
```

Regex chạy trên chuỗi đã **bỏ dấu** (`fold`), nên "tại sao" và "tai sao" cùng khớp. Router ra **một** nhãn, và nhãn đó chỉ đổi *cách sắp*
(`search_routed`, dòng 483–487). Kho thì không đổi: mọi câu vẫn đi FTS chữ.

## 3. Router v2: gom tín hiệu → danh sách kho (`memhub.plan()`, dòng 88–132, K0b)

Thay đổi về cấu trúc: thu **mọi** tín hiệu theo thứ tự *độ đặc hiệu*, rồi lấy hợp các kho:

```python
if is_metric and not is_howto:
    sig.append('metric')
if is_asset:
    sig.append('asset')
...
intent = sig[0] if sig else 'default'
stores = list(DEFAULT_STORES[intent])
if len(sig) > 1:                              # nhiều mục đích → danh sách kho theo thứ tự tín hiệu
    stores = []
    for s in sig:
        stores += [x for x in DEFAULT_STORES[s] if x not in stores]
```

Chạy thật (`kit recall --plan`, 0,1 s, 0 token):

```json
{"intent": "metric", "stores": ["M8", "M2", "M4", "M3"], "entities": [], "units": [],
 "time": {"from": null, "to": null}, "hops": 1, "need_answer_absent_ok": true,
 "rewrites": ["perf vung grass", "perf vung", "grass perf vung"]}
```

`metric` đứng trước `decided` vì "perf … tụt" đặc hiệu hơn "tại sao". Hai luật phụ thêm M2 (chuyện) và M4 (lý do) khi câu hỏi về số đo
mà kèm "tại sao". `entities` rỗng, vì "grass" và "vùng 2" chưa được link sang thực thể nào. Đó là việc của K1/K2.

**Vì sao đầu ra phải là một schema cố định:** người gọi (`ask()`) không phân biệt luật với model. Có thể thay bậc sinh plan, cache nó,
hoặc chấm nó riêng (`store@1`) mà không đụng tới adapter.

## 4. Bậc model: cascade + structured output + fallback (thiết kế K2, **chưa có**)

```
câu hỏi ──► [cache: sha256(norm(q) ‖ schema_v ‖ router_v)] ──trúng──► plan
              │ trượt
              ▼
          Bậc 1: plan() luật + bảng bí danh       0 token, ~100 ms (đo ở trên)
              │ escalate nếu: entities rỗng  HOẶC  top-1 coverage < θ  HOẶC  dấu hiệu nhiều bước
              ▼
          Bậc 2: Haiku, structured output theo JSON schema
              │ validate(schema) ── sai ──► Bậc 3: dùng lại plan của bậc 1
              ▼
          plan  ──► ghi cache ──► ask(): adapter M2…M11
```

- **Cascade** (bậc thang): mô hình rẻ hoặc luật xử lý trước, chỉ chuyển lên bậc đắt khi có *tín hiệu tự tin thấp*. Tổng chi phí xấp xỉ
  `cost_rule + planner_rate × cost_model`. Mục tiêu thiết kế: `planner_rate < 20 %`, `planner_tok_pct ≤ 1 %`.
- **Structured output**: ép model trả JSON theo schema. Có thể dùng tool-use với `input_schema`, hoặc chế độ JSON schema của API.
  Dù dùng cách nào thì **vẫn phải validate phía mình** (kiểu enum của `intent`, `stores ⊆ {M1..M11}`, `hops ∈ {1,2}`). Model có thể
  trả JSON đúng cú pháp nhưng sai nghĩa.
- **Fallback**: schema sai, hết thời gian, hoặc lỗi mạng thì dùng plan của bậc 1. Hook không bao giờ được chặn câu của người dùng
  (cùng nguyên tắc với `hint()`: `except Exception: … never blocks`).
- **Cache theo hash**: khoá gồm câu đã chuẩn hoá (fold, gộp khoảng trắng), *phiên bản schema* và *phiên bản router*. Đổi schema thì
  khoá đổi, cache cũ tự mất hiệu lực, không cần một bước xoá riêng. Đây cũng là cách `last_touch()` cache theo `HEAD` (dòng 302–331).
- Ràng buộc "model được **thêm** kho, không được **bỏ** kho mặc định" là để giữ sàn chất lượng của bậc 1.

Cảnh báo chi phí, lấy từ dự án: gọi model qua `claude -p` mặc định mang theo ~26k token prompt hệ thống mỗi lần (bài 05). Nếu planner
cũng gọi theo cách đó thì 40 câu/ngày ≈ 1M token chỉ cho phần vỏ. Bậc 2 phải dùng cờ bare (như `distill.call_haiku`) hoặc gọi API trực tiếp.

## 5. Gộp nhiều kho

**Hiện tại** (`memhub.ask()`, dòng 403–408): **xen kẽ vòng tròn** (round-robin) theo thứ tự kho của plan. Phần tử thứ i của M8, rồi
thứ i của M2, rồi M4, và cứ thế. Không có điểm nào bị cộng giữa các kho.

```python
while len(hits) < limit and any(i < len(v) for v in per.values()):
    for s in pl['stores']:
        if i < len(per.get(s, [])) and len(hits) < limit:
            hits.append(per[s][i])
    i += 1
```

**Vì sao không cộng điểm:** mỗi kho dùng một thang đo khác.
- BM25 của FTS5 là số âm, không có cận, và độ lớn phụ thuộc vào câu hỏi. Comment ở dòng 42 ghi "BM25 magnitudes vary 10x between queries".
- `coverage` nằm trong 0..1. PPR là xác suất, tổng bằng 1 trên cả đồ thị. `conf` của M5 là `0.9 / d`.

Cộng các số này với nhau thì kho nào có thang lớn sẽ thắng. Chuẩn hoá min-max cũng rất dễ vỡ, vì chỉ một giá trị ngoại lai là kéo lệch cả dải.

**RRF trong cùng một kho** (thiết kế §5.1/§5.2: `default` = RRF(BM25, PPR, độ tươi)). *Reciprocal Rank Fusion* (Cormack, Clarke, Büttcher, SIGIR 2009):

```
RRF(d) = Σ_{r ∈ các danh sách}  1 / (k + rank_r(d))          k = 60 (giá trị của bài báo)
```

Công thức chỉ dùng **thứ hạng**, nên không cần thang đo chung. `k` làm phẳng đầu bảng: hạng 1 và hạng 2 chỉ chênh nhau rất ít.
Kết quả là một tài liệu đứng *khá cao ở nhiều danh sách* sẽ thắng tài liệu *đứng đầu chỉ một danh sách*.

Ví dụ tính tay. BM25 cho ra [d1, d2, d3], PPR cho ra [d3, d1, d4]:

| d | BM25 rank | PPR rank | RRF |
|---|---|---|---|
| d1 | 1 | 2 | 1/61 + 1/62 = 0,03252 |
| d3 | 3 | 1 | 1/63 + 1/61 = 0,03227 |
| d2 | 2 | — | 1/62 = 0,01613 |
| d4 | — | 3 | 1/63 = 0,01587 |

## 6. Biết nói "không có": ngưỡng coverage

BM25 không phân biệt được hai trường hợp: "diễn đạt lại một đáp án có thật" và "câu không có đáp án trong kho". Điểm của hai loại chồng
lên nhau (comment ở dòng 449–450). Vì vậy code dùng thêm một tín hiệu: **coverage có trọng số IDF** (dòng 438–453):

```python
df = c.execute('select doc from chunks_v where term = ?', (w,)).fetchone()
out.append((w, math.log(1 + n / (1 + (df[0] if df else 0)))))
...
return sum(max(x, 0.0) for w, x in weights if w in txt) / tot
```

`chunks_v` là bảng `fts5vocab` cho biết số tài liệu chứa từng từ, nên lấy được IDF mà không phải quét kho. Coverage là phần trăm *trọng
lượng IDF* của câu hỏi có mặt trong mảnh top-1. Thiếu một từ hiếm thì tụt nhiều. Thiếu một từ phổ biến thì gần như không tụt.

Ngưỡng `WEAK_COV = 0.5` (đây là θ của thiết kế). Phân bố đo được trong `baseline-real.json`:

| | p10 | p50 | p90 |
|---|---|---|---|
| top-1 coverage, câu **có** đáp án | 0,58 | 1,00 | — |
| top-1 coverage, câu **không có** đáp án | — | 0,36 | 0,76 |

Hai phân bố chồng nhau, nên ngưỡng nào cũng phải đánh đổi. Ở 0,5 thì 6/15 câu không-đáp-án vẫn bị trả kết quả (false positive). Thử 0,6
thì sửa được `noans-02` nhưng lại gắn "yếu" nhầm cho 15 đáp án thật, so với 9 ở mức 0,5 (backlog 10-24). Cuối cùng giữ 0,5. Đây là
đường cong precision/recall của một bộ phân loại nhị phân. Muốn tách tốt hơn thì phải có thêm tín hiệu, ví dụ "không link được thực thể nào"
(K1/K2), chứ không phải chỉnh ngưỡng.

## Các cách làm và ưu/nhược

| Cách | Độ trễ | Token | Chất lượng | Gãy khi |
|---|---|---|---|---|
| Regex first-match (v1) | ~0 | 0 | một nhãn, sai với câu nhiều ý | câu "tại sao + số đo" |
| Regex gom tín hiệu (v2, hiện tại) | ~100 ms | 0 | store@1 97,8 % trên bộ vàng | câu diễn đạt lại không có từ khoá nào |
| Model cho mọi câu | 1–2 s | cao | tốt với câu lạ | "ok", "làm tiếp" cũng tốn tiền; phụ thuộc mạng |
| **Cascade + cache** (K2) | ~100 ms phần lớn thời gian | ≤ 1 % | tốt nhất nếu ngưỡng escalate đúng | ngưỡng sai: gọi model quá nhiều hoặc quá ít |
| Embedding classifier | ~10 ms | dựng một lần | cần dữ liệu nhãn | ít ca, nhãn lệch |

## Khi lớn lên

Có thêm kho thì chỉ thêm một adapter và một dòng trong `DEFAULT_STORES`. Rủi ro là các regex chồng lấn nhau. Thứ tự ưu tiên trong `plan()`
đã dài 20 dòng, và mỗi luật mới có thể phá một ca cũ. Phải chặn bằng việc **chạy bộ vàng sau mỗi lần sửa router** (`kit memory-eval --check`,
lùi hơn 1 ca là đỏ) và chia **dev/test**: chỉ được nhìn ca dev khi chỉnh router (bài 06). Khi có nhiều câu được cache, bậc model sẽ bị gọi
ít dần theo thời gian.

## Tự làm

1. Chạy `kit recall --plan` cho 5 câu: "build iOS thế nào", "còn thiếu icon nào ở NanoSwarm", "tại sao bỏ cel-shade",
   "đổi colour-territory.md thì gì lệch", "bầy cánh chậm ở vùng nhiều cỏ". Câu nào ra `default` hoặc `entities` rỗng? Đó là những ca sẽ escalate lên Haiku ở K2.
2. Tính RRF với k = 60 cho hai danh sách [a, b, c, d] và [d, c, e]. Tính lại với k = 1 và giải thích vì sao thứ tự đổi.
3. Viết schema JSON (draft 2020-12) cho plan ở §3: `intent` là enum, `stores` là mảng enum M1–M11, `hops` có minimum 1, maximum 2.
   Rồi liệt kê 3 output "đúng cú pháp, sai nghĩa" mà schema vẫn cho qua.

## Đọc thêm

- Cormack, Clarke, Büttcher, *Reciprocal Rank Fusion outperforms Condorcet and individual rank learning methods*, SIGIR 2009.
- Tài liệu Anthropic về tool use / structured outputs (input_schema): docs.anthropic.com. *Chưa đọc lại để trích.*
- Chen, Zaharia, Zou, *FrugalGPT* (arXiv 2305.05176): cascade LLM theo độ tin cậy. *Kiến thức sẵn có.*

> **Một dòng:** router xuất một plan JSON theo schema cố định. Luật xử lý đa số câu, model chỉ chạy khi tín hiệu tự tin thấp. Gộp kết quả giữa các kho bằng xen kẽ, trong một kho bằng RRF trên thứ hạng. Nói "không có" dựa vào coverage có trọng số IDF.
> **Bài sau:** [04 — Đồ thị tất định: entity linking, BFS ngược, nghi cũ](04-ban-do-quan-he.md)
