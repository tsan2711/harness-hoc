# 06 — Đo: bộ vàng, recall@k / store@k / MRR, khoảng tin cậy; lộ trình K0–K6; tách repo

> Bài 6/6. Đọc ~12 phút. **Đã biết:** cả chuỗi 01–05.
> Code thật: `tools/claude/memory_eval.py`, `company/eval/memory/cases.toml`, `baseline.json` (**K0, commit `c74c5e340`**). Tách repo: thiết kế §6, chưa làm.

## Chuyện mở đầu

P2 đốt hàng triệu token để sinh 865 thẻ. Sau đó mới phát hiện bộ vàng *không có câu nào hỏi nội dung thẻ*, nên không có cách nào đo được
thẻ có giúp hay không. Ở K1, para nhảy 9 → 7 khi đổi `CARD_FACTOR`. Đó là tín hiệu thật hay nhiễu? Với n = 20 thì gần như không biết được.

## Dừng 30 giây

Một con số "66,7 %" trên 15 ca cho phép bạn kết luận điều gì, và *không* cho phép kết luận điều gì? Nếu bạn chỉnh router cho tới khi bộ
vàng đạt, thì bộ vàng còn đo được điều gì?

---

## 1. Bộ vàng (gold set)

**Định nghĩa.** Một tập câu hỏi cố định, mỗi câu có *đáp án đã biết*. Ở đây đáp án là chuỗi con phải xuất hiện trong nguồn trả về, kèm
**kho đúng**. Một ca trong `cases.toml`:

```toml
[[case]]
id = "impact-02"
group = "impact"
split = "test"
asker = "hq"
q = "colour-territory.md vừa đổi, cái gì phụ thuộc vào nó và có thể lệch?"
stores = ["M5"]
gold = ["residents.md", "run-loop", "sleeping-spots", "time-frozen-world"]
```

Cách dựng sao cho không tự lừa mình:
- **Đáp án lấy từ dữ kiện, không lấy từ hệ.** Đáp án impact = các file *thật sự đổi cùng commit* với file được hỏi (comment dòng 3).
  Nếu lấy đáp án từ output của `kg impact` thì bộ vàng chỉ đo xem hệ có giống chính nó không.
- **Phủ theo mục đích, có hạn ngạch**: 15 impact, 15 xdept, 10 overview, 10 decided có supersede, 10 metric, 10 howto, 10 taste/asset,
  10 nhiều kho, 10 không-có-đáp-án. Thiếu nhóm nào thì nhóm đó không đo được. Đúng bài học P2 thiếu nhóm `card`.
- **Ca không có đáp án** (`absent = true`) đo *precision* của việc trả lời: hệ phải nói "không có" thay vì trả mảnh gần giống (bài 03 §6).
- **Ảnh chụp đông kho** (`company/state/recall-real-snap.sqlite`): đo trên bản kho cố định, để kho tự phình không làm số trôi giữa hai lần đo.
- **dev/test split**: chỉ được nhìn ca `dev` khi chỉnh router. Ca `test` để đo. Đây là chống **overfitting vào bộ đánh giá**: router regex
  rất dễ được "chỉnh cho đúng từng ca". Khi đó điểm dev tăng nhưng không nói gì về câu thật.

## 2. Các chỉ số

| Chỉ số | Định nghĩa | Ở đâu |
|---|---|---|
| **store@1** | kho đầu của plan ∈ kho vàng | `row['s1']` |
| **store@k** | *mọi* kho vàng ∈ plan (k = độ dài plan, ≤ 4) | `row['sk']` |
| **mảnh** (≈ recall@k, k = 12) | có ít nhất một (hoặc tất cả, nếu `all`) chuỗi vàng nằm trong 12 kết quả | `piece_ok` |
| **MRR** | trung bình của 1/hạng của kết quả đúng đầu tiên | **chưa đo** |
| `planner_rate`, `planner_tok_pct` | tỉ lệ câu lên bậc model, phần trăm token tuần | thiết kế K2 |

`memory_eval.score` (dòng 53–77) tính cả **đường cũ** (`old_path` = `recall.search_routed`) trên cùng các ca, để so trước/sau trong cùng một lần chạy:

```python
res = memhub.ask(case['q'], case.get('asker'), c=c)
...
row['s1'] = int(res['plan']['stores'][0] in gold_st)
row['sk'] = int(all(s in res['plan']['stores'] for s in gold_st))
row['old_s1'] = int(old_stores[0] in gold_st)
row['p'] = int(piece_ok(case, res['hits'], res['absent']))
```

**Vì sao cần MRR.** "Mảnh" chỉ hỏi *có trong 12 hay không*. Nhưng `hint()` chỉ bơm ≤ 3 mảnh vào ngữ cảnh, nên đáp án ở hạng 11 thì
coi như mất. MRR (hoặc recall@3) đo đúng thứ mà agent nhìn thấy. Bài 01 đã chỉ ra: thứ hạng hỏng trước khả năng tìm thấy, nên recall@12
sẽ báo "ổn" lâu hơn thực tế.

## 3. Khoảng tin cậy khi n nhỏ

Mỗi ca là một phép thử Bernoulli. Với n = 15–20, sai số chuẩn `√(p(1−p)/n)` vào khoảng ±11 điểm phần trăm. Xấp xỉ Wald `p ± 1,96·SE`
hỏng khi p gần 0 hoặc 1 (cho ra khoảng vượt [0, 1]). Nên dùng **khoảng Wilson**:

```
         p̂ + z²/2n  ±  z·√( p̂(1−p̂)/n + z²/4n² )
CI  =  ─────────────────────────────────────────          z = 1,96 (95 %)
                     1 + z²/n
```

Tính cho số thật của dự án:

| Kết quả | p̂ | Wilson 95 % | Đọc ra |
|---|---|---|---|
| para 8/20 (baseline-real) | 40 % | [21,9 ; 61,3] | — |
| para 7/20 ↔ 9/20 (CARD_FACTOR 0,5 ↔ 1,0) | 35 / 45 % | [18,1 ; 56,7] / [25,8 ; 65,8] | **chồng nhau gần hết: chưa phân biệt được** |
| impact 10/15 (K1) | 66,7 % | [41,7 ; 84,8] | "đạt cổng ≥ 60 %" nhưng cận dưới chỉ 42 % |
| impact store@1 14/15 | 93,3 % | [70,2 ; 98,8] | — |
| store@1 88/90 (K0b) | 97,8 % | [92,3 ; 99,4] | cận dưới vẫn trên cổng 85 %: kết luận chắc chắn |

Hệ quả kỹ thuật:
- Cổng nên viết theo **cận dưới** (`wilson_lo ≥ ngưỡng`) hoặc theo **chênh lệch trên các ca giống nhau** (paired: đếm ca lật đúng → sai
  và sai → đúng, như kiểm định McNemar), thay vì so tỉ lệ thô.
- Luật hồi quy của `gate()` (dòng 106–117) là "lùi > 1 ca ở một nhóm". Ở nhóm n = 10, đó là 10 điểm %. Đây là chặn **thô có chủ đích**
  (chống nhiễu nhỏ), không phải kiểm định thống kê.
- `--twice` (chạy 2 lần, lệch ≤ 1 ca) đo **tính tất định** của chính phép đo, khác với độ chính xác.
- Muốn thu hẹp khoảng thì phải tăng n. Ở p ≈ 0,5, ±10 điểm cần n ≈ 96 ca; ±5 điểm cần khoảng 385 ca.

## 4. Lộ trình và cổng (thiết kế §7, trạng thái 2026-10-27)

| Pha | Làm | Cổng | Trạng thái |
|---|---|---|---|
| K0 | bộ vàng 100 ca, gắn kho đúng | ổn định (`--twice`), 0 token model | **XONG**: đường cũ store@1 56,7 %, mảnh 39 % |
| K0b | cửa chung `memhub`, adapter, router luật, lint ghi sai kho | store@1 ≥ 85 %; metric/howto/asset ≥ 80 % | **ĐẠT**: 97,8 %; 100/90/100 %. xdept mảnh 5/15, decided 5/10 vì `*/design/**` chưa vào chỉ mục |
| K1 | schema, entities, L0/L1, pre-commit, nghi cũ | impact ≥ 60 %; para +15 điểm | **MỘT PHẦN**: impact 66,7 %; para chưa lên vì entity link chưa nối vào recall; `refs` vẫn là đường dẫn |
| K2 | planner bậc model + rewrites | para ≥ 70 % hoặc +20; planner_rate < 20 %; tok ≤ 1 % | chưa |
| K3 | claim + hoà giải (Thousandfold 14 ngày) | decided-có-supersede ≥ 80 %; quote-fail 0; tok ≤ ước ×1,3 | chưa |
| K4 | tách repo | selftest xanh mọi repo; 0 `refs` gãy | chưa |
| K5 | L4 tóm tắt cụm + repo phòng ban | overview ≥ 70 % (rubric) | chưa |
| K6 | vector hẹp | chỉ khi para < 70 % sau K2 | chưa |

Luật thứ tự (plan → test → plan kế): không sang pha sau khi cổng pha trước chưa đạt. K1 *chưa đạt trọn*, nên K2 là phần còn thiếu của
K1 (entity link vào recall, `refs → kg://`) chứ không phải pha mới.

## 5. Pipeline ghi và pipeline đọc

```
GHI                                                         ĐỌC
───                                                         ───
sửa file / commit                                           câu hỏi (hook UserPromptSubmit)
   │                                                           │
   ├─ pre-commit: lint ghi sai kho (memhub --lint)             ├─ cache sha256(q‖schema_v‖router_v)      [K2]
   ├─ pre-commit: kg staged → cảnh báo nghi cũ  [K1 ✓]         ├─ plan(): regex gom tín hiệu → JSON     [K0b ✓]
   │                                                           │    └─ tự tin thấp → Haiku + schema     [K2]
kg build (8 s): L0 frontmatter · L1 đường dẫn/import           ├─ entity link (bảng bí danh)            [K1 một phần]
   · git co-change → graph.json                [K1 ✓]          ├─ adapter theo kho:
   │                                                           │    M8 số · M10 bảng · M6 lệnh          [✓]
recall.index: FTS5 tăng dần theo mtime:size     [✓]            │    M3/M2/M4/M11 → recall FTS5 BM25     [✓]
   │                                                           │    M5 → kg.impact BFS ngược            [✓ chỉ tên file]
Stop hook → distill (Haiku, cổng quote, trần)  [P2 ✓ tắt]      │    default → RRF(BM25, PPR, tươi)      [thiết kế]
   └─ claim + hoà giải supersede               [K3]            ├─ gộp: xen kẽ theo thứ tự kho          [✓]
                                                               ├─ absent nếu conf/coverage < ngưỡng    [✓]
                                                               └─ hint(): ≤ 3 mảnh, ≤ 1 800 ký tự → ngữ cảnh
```

## 6. Tách repo (thiết kế §6 — K4, chưa làm)

**Đích:** `seriously-hq` (tools, company, docs/shared, `kg/schema.toml`; repo duy nhất có chỉ mục gộp) + `seriously-<game>` ×3 +
`seriously-depts` (gom các phòng ban; phòng nào > 50 file sổ tay hoặc cần quyền riêng thì tách tiếp). `sanne-kit` đã là repo riêng, giữ nguyên.

**Thứ gãy và cơ chế thay thế**, theo nguyên tắc: *mọi thứ đang dựa vào "cùng một cây thư mục" phải đổi sang ID hoặc hàng đợi*.

| Đang dựa vào monorepo | Vì sao gãy | Thay bằng |
|---|---|---|
| `refs` = đường dẫn | repo khác không có đường dẫn đó | **ID ổn định** `kg://<id>` + bảng phân giải ở hub. Phải đổi *trước* khi tách (K1) |
| `company send` ghi vào `depts/x/inbox/` | ghi chéo repo = commit vào repo người khác | hàng đợi ở hub (`company/queue/`), phiên phòng đọc bằng `kit company list` |
| pre-commit `kg staged` | chỉ thấy diff của repo mình; nghi cũ *liên repo* bị mù | hub dựng đồ thị gộp từ mọi repo trong workspace, chạy `suspect` định kỳ (xem README: mơ hồ) |
| recall quét một cây | — | chỉ mục ở hub quét mọi repo theo manifest `company/workspace.toml` (repo, đường dẫn, tag) |
| hook / selftest | — | `hooks install` từ hub, mỗi repo chạy phần của mình |

**Giữ lịch sử khi tách:** `git filter-repo --subdirectory-filter <Game>/` viết lại lịch sử, chỉ giữ các commit chạm thư mục đó, và đưa
thư mục lên làm gốc. Hash commit **đổi**, nên mọi tham chiếu dạng `commit abc123` trong sổ tay sẽ trỏ sai. Vì vậy `refs` phải dùng ID, không
dùng hash. Chạy song song 2 tuần, monorepo cũ để chỉ đọc. Gỡ thư mục khỏi monorepo hay archive repo là *xoá dữ liệu*, nên Bi phải duyệt (`policy.toml`).

## Các cách làm và ưu/nhược (về đo)

| Cách | Ưu | Nhược |
|---|---|---|
| Đo bằng cảm giác / vài câu tay | nhanh | không lặp lại được; P2 là ví dụ đốt token mà không biết lợi |
| Bộ vàng chuỗi con + tỉ lệ (hiện tại) | 0 token, tất định, chạy trong pre-commit | n nhỏ nên khoảng tin cậy rộng; chuỗi con có thể trúng vì tình cờ |
| LLM-as-judge | chấm được câu mở (overview) | tốn token, không tất định, cần hiệu chỉnh với người chấm |
| Đo online (`recall-inject.jsonl`: mảnh bơm vào có được dùng không) | đo trên câu thật | cần nhãn ngầm; nhiễu |

## Khi lớn lên

Bộ vàng phải lớn cùng hệ: mỗi kho mới, mỗi loại câu mới thì thêm ca *trước* khi build (luật thêm kho, bài 02). Ca `test` không bao giờ
được dùng để chỉnh. Khi số ca dev đã bị "học thuộc" thì rút ca mới từ log câu thật. Với nhiều repo, `memory-eval` chạy ở hub trên ảnh
chụp chỉ mục gộp.

## Tự làm

1. `sh tools/claude/kit.sh memory-eval --no-old` rồi so với `company/eval/memory/baseline.json`. Tính Wilson 95 % cho nhóm `xdept`
   (p = 5/15) bằng `python3 -c` với công thức ở §3. Cận trên của khoảng có chạm 60 % không? Từ đó, có thể nói xdept "gần đạt" được không?
2. Sửa `memory_eval.piece_ok` *trên bản nháp ở scratchpad* để trả thêm hạng của kết quả đúng đầu tiên, rồi tính MRR và recall@3 cho
   nhóm impact. So với "mảnh" (recall@12).
3. Viết 3 ca mới cho nhóm `card` theo khuôn ở §1: đáp án lấy từ trích dẫn trong `company/memory/cards/Thousandfold/*.jsonl`. Gán `split`
   thế nào để vẫn đo công bằng được?

## Đọc thêm

- Wilson, *Probable Inference, the Law of Succession, and Statistical Inference* (JASA 1927) · Brown, Cai, DasGupta, *Interval Estimation
  for a Binomial Proportion* (Stat. Sci. 2001): vì sao không dùng Wald.
- Manning, Raghavan, Schütze, *Introduction to Information Retrieval*, ch. 8 (recall@k, MRR).
- `git filter-repo` docs: github.com/newren/git-filter-repo.
- Trong repo: `docs/shared/knowledge-graph-design.md` §6–§7; `company/eval/memory/`.

> **Một dòng:** bộ vàng có đáp án lấy từ dữ kiện, chia dev/test, đo store@1/store@k/mảnh (và nên thêm MRR). Đọc mọi tỉ lệ kèm khoảng Wilson. Tách repo chỉ an toàn khi mọi tham chiếu đã là ID ổn định và mọi giao tiếp đã đi qua hàng đợi ở hub.
> **Về mục lục:** [README](README.md)
