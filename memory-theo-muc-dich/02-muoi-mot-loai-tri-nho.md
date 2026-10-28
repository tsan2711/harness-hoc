# 02 — Phân loại trí nhớ: CoALA → 11 kho, và ghi đúng kho

> Bài 2/6. Đọc ~9 phút. **Đã biết:** BM25/FTS5, vì sao một pool bị loãng ([01](01-mot-kho-khong-du.md)).
> Code thật: `recall.tier_of`, `memhub.DEFAULT_STORES`, `memhub.lint_wrong_store` (đã có). Thiết kế: §1b.

## Chuyện mở đầu

Câu "perf tuần này tệ hơn không" từng đi qua FTS chữ. Nó trả về 12 đoạn hội thoại có chữ "perf". Câu trả lời đúng lại là một phép trừ
trên `company/state/harness-health.jsonl`. Trên bộ vàng K0, nhóm metric/howto/asset đi đường cũ có store@1 = 0 %.

## Dừng 30 giây

Hãy liệt kê *dạng* của câu trả lời cho những câu Bi hay hỏi: đoạn văn, con số, bảng lọc, tên lệnh, ảnh. Mỗi dạng cần phép toán đọc nào?
Có dạng nào mà "tìm theo độ giống chữ" cho kết quả sai về bản chất, chứ không chỉ kém chính xác?

---

## 1. CoALA — bộ phân loại chuẩn

**CoALA** (Cognitive Architectures for Language Agents, Sumers và cộng sự, arXiv 2309.02427) chia trí nhớ của agent thành:

| Loại | Định nghĩa | Ví dụ ở Seriously |
|---|---|---|
| **Working** | trạng thái của quyết định hiện tại, nằm trong ngữ cảnh | việc đang nhận, bàn giao, mục "Đang làm gì" của INDEX |
| **Episodic** | các sự kiện đã trải qua, có thời điểm | transcript, `company/records/tasks.jsonl`, git log |
| **Semantic** | sự thật và tri thức về thế giới, không gắn với một sự kiện | GDD, ADR, `depts/*/knowledge/` |
| **Procedural** | cách làm: code, prompt, kỹ năng | skill, `.claude/rules/`, lệnh kit, pre-commit |

CoALA còn tách hai chuyện: hành động *truy xuất* (đọc từ trí nhớ dài hạn vào working) và hành động *học* (ghi vào trí nhớ dài hạn).
Thiết kế Seriously dùng đúng cách tách này: mỗi kho có luật đọc riêng và luật ghi riêng.

## 2. Từ 4 loại thành 11 kho

Thiết kế tách mỏng hơn, vì nhiều loại trong cùng một nhóm CoALA vẫn cần **phép đọc khác nhau**:

| Kho | Nhóm CoALA | Hình dạng dữ liệu | Phép đọc | Trạng thái |
|---|---|---|---|---|
| M1 đang làm gì | working | JSON/INDEX | nạp sẵn, không tìm | có |
| M2 chuyện đã xảy ra | episodic | log chỉ thêm (append-only) + `ts` | lọc thời gian → BM25, sắp theo ngày | có |
| M3 luật đã chốt | semantic | một chủ đề một file | entity link → BM25 tầng ấm | có |
| M4 quyết định + lý do | semantic có thời gian | claim `valid_from/invalid_at` | lấy theo subject, đi chuỗi `supersedes` | một phần (thẻ chưa có thời gian) |
| M5 phụ thuộc | semantic quan hệ | đồ thị | duyệt đồ thị (BFS/PPR) | **K1 vừa vào code** |
| M6 cách làm | procedural | skill, rule, lệnh | **kích hoạt**, không tìm | có |
| M7 gu | preference (ngoài CoALA) | verdict + ảnh | nạp theo unit; sau này dùng embedding ảnh | một phần |
| M8 số đo | (ngoài CoALA) | chuỗi thời gian | **truy vấn tính toán** | có |
| M9 code | — | chính mã nguồn | grep/symbol/compile, không nhớ | có |
| M10 tài nguyên | semantic có cấu trúc | bảng | lọc theo cột trạng thái | có |
| M11 kiến thức ngoài | semantic | nguồn có tier + ngày tra | BM25, ưu tiên tier A | có |

Luật **5 thứ** (§1b): một kho phải có *chủ*, *luật ghi*, *phép đọc*, *luật quên/hợp nhất*, *chỉ số*. Thiếu một thì chưa được coi là kho.
Luật thêm kho: phải có ca trong bộ vàng mà các kho cũ trả sai. Luật này ngăn việc thêm kho theo cảm hứng, đúng bài học P2.

Có hai điểm kỹ thuật cần nhớ:
- **M9 không phải trí nhớ.** Code đổi từng commit. Một bản tóm tắt code đã lưu chính là cache *không có cơ chế làm mới*. Memory chỉ giữ
  *vì sao* code như vậy (M4). Bằng chứng trong code: `is_stale()` (recall.py dòng 334–339) gắn nhãn "có thể cũ" cho một đoạn hội thoại
  nhắc tới một file đã được commit đổi *sau* ngày của đoạn đó.
- **M6 không tìm kiếm.** Cách đọc là *kích hoạt*: skill bật khi mô tả của nó khớp với việc đang làm, rule nạp theo `paths:` khi agent mở
  file trong thư mục tương ứng. Một bài học lặp lại thì ưu tiên biến thành cổng (script chặn). Chữ có thể bị bỏ qua, cổng thì không.

## 3. Tầng tin cậy trong code hiện tại

Trước khi có 11 kho, `recall.py` đã có hai tầng (dòng 47 và 64–65):

```python
CHOT = ('knowledge/', '/docs/ai/', 'docs/shared/', 'tools/ccgs/lessons/')
def tier_of(kind, path):
    return 'chot' if kind in ('task', 'card') or kind == 'note' and any(m in '/' + path for m in CHOT) else 'chuyen'
```

`chot` ≈ semantic (tầng ấm), `chuyen` ≈ episodic (tầng lạnh). Ta thấy được giới hạn của cách làm này: nó chỉ có *hai nhãn trên cùng một pool*.
Nhãn chỉ giúp phá thế hoà điểm, không đổi được *phép đọc*.

## 4. Router chọn kho: `DEFAULT_STORES` (đã có — K0b, commit `c74c5e340`)

```python
DEFAULT_STORES = {'lookup': ['M3', 'M9'], 'decided': ['M4', 'M3'], 'episode': ['M2'], 'impact': ['M5'], 'overview': ['M5', 'M3'],
                  'howto': ['M6'], 'metric': ['M8'], 'taste': ['M7'], 'asset': ['M10'], 'xdept': ['M3', 'M2'], 'default': ['M3', 'M4', 'M11']}
```

Mỗi **intent** (ý định của câu hỏi) ánh xạ sang một danh sách kho có thứ tự. `memhub.ask()` gọi **adapter** của từng kho: `a_metric`
đọc JSONL số, `a_asset` lọc bảng, `a_howto` trả tên lệnh/skill, `a_fts` dùng lại `recall.search` rồi lọc theo loại. Mỗi adapter trả cùng
một kiểu bản ghi `{store, src, title, snip, conf}` (`hit()`, dòng 136–137). Đây chính là "nhiều kho, một cửa". Bài 03 đi vào cách chọn intent.

Kết quả đo trên bộ vàng 100 ca (`company/eval/memory/baseline.json`): store@1 tăng từ 56,7 % (đường cũ) lên **97,8 %**.
Metric/howto/asset tăng từ 0 lên 100 % về chọn kho, 100/90/100 % về tìm đúng mảnh.

## 5. Ghi đúng kho: lint tất định

Lỗi phổ biến nhất là *ghi* sai kho. `memhub.lint_wrong_store()` (dòng 424–461) bắt lỗi này bằng luật mẫu, không dùng model:

```python
UNIT_RX = re.compile(r'\b\d+(?:[.,]\d+)?\s?(?:ms|fps|drawcalls?|MB|GB)\b')
SRC_RX = re.compile(r'company/state|perf/|baseline|\.jsonl?|harness-health|nguồn đo|đo bằng|đo ở|kit perf', re.I)
STATUS_RX = re.compile(r'\b(?:đã xong|xong rồi|hoàn thành|✅|tiến độ)\b', re.I)
...
if UNIT_RX.search(para) and not SRC_RX.search(para) and not para.lstrip().startswith(('|', '```')):
    out.append(('M8', ...
```

- Một đoạn sổ tay có số kèm đơn vị (12 ms, 60 fps) mà không trỏ tới nguồn đo thì báo về M8. Số nằm trong chữ là số chết: không ai cập nhật nó.
- Memory của Claude có "đã xong / tiến độ" thì báo về M1 (INDEX).
- `asset-backlog.md` không có cột trạng thái chuẩn thì báo về M10.

Ưu: 0 token, chạy được trong pre-commit. Nhược: chỉ bắt được *mẫu*. "Bi thích ánh sáng ấm" ghi nhầm vào sổ tay gd thì regex không bắt được.

## 6. So với các hệ ngoài

| Hệ | Cách nhớ | Lấy gì | Bỏ gì, vì sao |
|---|---|---|---|
| **Claude Code** (CLAUDE.md + auto-memory) | file md nạp lúc mở phiên; auto-memory có `MEMORY.md` làm mục lục | đây là M1/M7 + tầng nóng | không có tìm kiếm, nên không dùng cho M2–M5 (quan sát trực tiếp trong repo này) |
| **Letta / MemGPT** (arXiv 2310.08560) | "hệ điều hành cho ngữ cảnh": core memory (khối agent tự sửa) + recall storage (lịch sử) + archival (vector); agent tự gọi hàm để phân trang | ý core memory ≈ tầng nóng | việc *agent tự quyết khi nào đọc* là pull. Model không biết mình không biết (chuỗi B, bài 07-04); bản sửa memory không qua git để duyệt. *Kiến thức sẵn có.* |
| **mem0** (arXiv 2504.19413) | LLM rút fact mỗi lượt hội thoại → so với memory tương tự → LLM chọn ADD/UPDATE/DELETE/NOOP; vector store, có bản graph | ý "hợp nhất lúc ghi" | gọi LLM mỗi lần ghi (tốn token, không tất định); DELETE làm mất lịch sử "vì sao đổi". *Kiến thức sẵn có, số liệu benchmark chưa kiểm.* |
| **Zep / Graphiti** (arXiv 2501.13956) | đồ thị thời gian; cạnh có thời điểm hiệu lực/hết hiệu lực | mô hình claim có thời gian (bài 05) | trích xuất bằng LLM lúc ghi, chạy dịch vụ nền ngoài git. *Abstract đã đọc 10-20.* |

Tiêu chí chọn là **H-10**: tất định trước, nguồn sự thật nằm trong git, model chỉ dùng ở chỗ luật bó tay và có trần token.

## Các cách làm và ưu/nhược

| Cách phân kho | Ưu | Nhược |
|---|---|---|
| 4 loại CoALA nguyên bản | chuẩn, ít kho | gộp số đo/gu/bảng vào "semantic" thì vẫn bị đọc bằng chữ |
| 11 kho theo *phép đọc* (thiết kế) | mỗi câu hỏi có phép đọc đúng | cần router; ranh giới M4/M5 mờ (README) |
| Kho theo phòng (art, gd…) | khớp với quyền sở hữu | cùng một câu hỏi phải tìm 7 nơi; đó là trục *phạm vi*, không phải trục *loại* (unit là bộ lọc, không phải kho) |

## Khi lớn lên

M2 phình nhanh nhất. Luật quên: sau 60 ngày, chắt lọc sang M4/M5 và chỉ giữ chỉ mục. M8 gộp số theo ngày/tuần. M3 không phình vì mỗi
chủ đề chỉ có một file. Thêm game thứ 4 không thêm kho mới: các adapter đọc danh sách game từ `game.toml` (commit `c0d288744` đã gỡ tên
game ra khỏi lõi). Thêm loại câu hỏi mới mà kho cũ trả sai thì mới thêm kho, và kho mới phải đủ 5 thứ.

## Tự làm

1. `sh tools/claude/kit.sh recall --plan "perf tuần này tệ hơn không"` rồi `sh tools/claude/kit.sh recall "perf tuần này tệ hơn không"`.
   So JSON plan với kết quả: câu này đi adapter M8 hay FTS? (Đọc `recall.main` dòng 582.)
2. `sh tools/claude/kit.sh recall --lint`: mở 2 dòng báo đầu tiên và tự quyết xem đó là lỗi thật hay báo nhầm. Nếu báo nhầm thì regex nào cần sửa?
3. Lấy 10 câu bạn đã hỏi agent tuần này, gán mỗi câu một kho M1–M11. Câu nào cần từ 2 kho trở lên?

## Đọc thêm

- Sumers et al., *Cognitive Architectures for Language Agents*, arXiv 2309.02427.
- Packer et al., *MemGPT*, arXiv 2310.08560 · Chhikara et al., *Mem0*, arXiv 2504.19413 · Rasmussen et al., *Zep*, arXiv 2501.13956.
- Trong repo: `docs/shared/knowledge-graph-design.md` §1b; `company/eval/memory/cases.toml`.

> **Một dòng:** phân kho theo *phép đọc* mà câu trả lời cần (CoALA + số/gu/bảng). Một cửa với các adapter cùng định dạng; ghi sai kho thì lint tất định bắt.
> **Bài sau:** [03 — Query routing, JSON schema, RRF](03-bo-chon-kho.md)
