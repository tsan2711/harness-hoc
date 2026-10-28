# 04 — Đồ thị tất định: entity linking, ontology, BFS ngược, và "nghi cũ"

> Bài 4/6. Đọc ~11 phút. **Đã biết:** router và adapter ([03](03-bo-chon-kho.md)).
> Code thật: `tools/harness/kg.py`, `kg/schema.toml`, `<Game>/kg/entities.toml` (**K1, commit `3d69a9662`, 2026-10-27**); `tools/harness/gdd_drift.py` (bản trước K1).
> Thiết kế: §2–§4, V1–V3.

## Chuyện mở đầu

`gdd_drift.py` quét lịch sử Thousandfold và thấy: trong 62 lần sửa GDD, có 15 lần không file phụ thuộc nào đổi theo, kể cả sau 2 ngày.
Hỏi "đổi colour-territory.md thì gì lệch?" bằng FTS thì 0/15 ca trúng mảnh đúng. Câu hỏi tác động là câu hỏi về **cạnh**, mà chỉ mục chữ
không có cạnh.

## Dừng 30 giây

Một cạnh "A phụ thuộc B" có thể đến từ đâu mà *không cần model đọc hiểu*? Mỗi nguồn đó sai theo kiểu gì: thiếu cạnh hay thừa cạnh?
Khi B đổi, đi theo hướng nào thì ra được danh sách "cần xem lại"?

---

## 1. Định nghĩa

- **Knowledge graph (KG)**: tập nút (thực thể, tài liệu, file) và cạnh có kiểu (`depends_on`, `implements`, …).
- **Ontology / schema**: danh sách *kiểu nút* và *kiểu cạnh* được phép, kèm thuộc tính của từng kiểu (có lan truyền không, lấy từ nguồn nào).
  Ở đây đó là `kg/schema.toml`.
- **Entity linking**: ánh xạ một chuỗi trong văn bản ("bầy cánh", "SwarmPrototype") sang **một ID thực thể chuẩn** (`entity:swarm`).
  Gồm hai bước: *phát hiện* chuỗi ứng viên (mention detection), rồi *phân giải* nó qua bảng bí danh (alias table) sang ID.
- **Lane** (làn nguồn): **L0** = cạnh khai báo tay (frontmatter, `[[link]]`, `unit.toml`); **L1** = cạnh suy ra bằng luật (đường dẫn
  được nhắc trong file, import trong code); **git** = cạnh đồng thay đổi (co-change). Model *không* tạo cạnh trong K1. Đó là bài 05.

## 2. Ontology của K1 (`kg/schema.toml`)

| Cạnh | Ý nghĩa | Nguồn | `propagate` |
|---|---|---|---|
| `depends_on` | A dùng luật/số của B | frontmatter L0 | có |
| `implements` | code A thực thi GDD B | L0/L1 | có |
| `derived_from` | A sinh ra từ B (ảnh từ prompt, bake từ glb) | L1 | có |
| `tests` | test A kiểm B | L1 (tên test) | có |
| `refs` | A *nhắc tới* B | L1 (đường dẫn trong chữ) | **có** ← xem §6 |
| `about` | A nói về thực thể E | L1 (bí danh khớp) | không (chỉ dùng khi hỏi tác động) |
| `co_change` | A, B cùng đổi ≥ 3 commit trong 120 ngày, commit ≤ 8 file | git | không |

Hai luật của co-change có lý do rõ ràng. Ngưỡng ≥ 3 lần lọc bỏ trùng hợp. Giới hạn ≤ 8 file/commit loại các commit "dọn cả cây": một
commit đổi 200 file sẽ sinh ra C(200,2) ≈ 20 000 cạnh rác.

## 3. Entity linking trong code (`kg.resolve`, dòng 353–364)

```python
def resolve(g, q):
    nodes = g['nodes']
    q = q.strip()
    if q in nodes:                                   # 1. đúng ID
        return [q]
    ql = q.lower()
    out = [i for i, n in nodes.items() if n['path'] == q or (n['path'] and os.path.basename(n['path']).lower()
           == os.path.basename(ql) and n['type'] in ('doc', 'artifact') and '.' in ql)]   # 2. đường dẫn / tên file
    if out:
        return out
    ents = {e['id']: e for e in load_entities()}
    return [i for i, e in ents.items() if i in nodes and any(a.lower() == ql for a in e.get('aliases', []) + [e['id']])]  # 3. bí danh
```

Ba bậc, khớp **chính xác**. Bậc 2 đòi có dấu `.` để "swarm" không vô tình khớp tên file `swarm`. Bậc 3 so *nguyên chuỗi* với bí danh,
không có fuzzy, không cắt câu.

Hệ quả, đã kiểm trong code `memhub.a_impact`: nó chỉ trích **tên file** từ câu bằng regex `IMPACT_FILE` rồi mới gọi `kg.impact`. Câu
"đổi palette thì gì lệch" không có tên file, nên M5 trả rỗng, dù `resolve` có hỗ trợ bí danh. Thiếu bước mention detection (cắt n-gram
của câu → tra bảng bí danh), và đó là việc của K2.

Bảng bí danh (`Thousandfold/kg/entities.toml`, 166 thực thể trên 3 game) được `kg seed` sinh tự động từ heading và tên class. Chất lượng
còn thô: có bí danh kiểu "BI DUYET", không phải khái niệm của game. Hợp đồng thiết kế: model chỉ được **đề xuất** bí danh, người duyệt,
file nằm trong git.

## 4. Câu hỏi tác động = BFS trên cạnh ngược (`reverse_walk`, dòng 367–386)

```python
inc = {}
for e in g['edges']:
    if e['type'] in types:
        inc.setdefault(e['b'], []).append((e['a'], e['type']))      # đảo chiều: ai trỏ VÀO b
seen = {s: (0, '') for s in start}
frontier = list(start)
for d in range(1, hops + 1):                                        # BFS theo tầng, dừng ở hops=2
    nxt = []
    for x in frontier:
        for a, t in inc.get(x, []):
            if a not in seen:
                seen[a] = (d, t); nxt.append(a)
    frontier = nxt
```

- Cạnh lưu theo chiều `A → B` ("A phụ thuộc B"). Khi B đổi, người bị ảnh hưởng là những A có cạnh *đi vào* B. Vì vậy phải dựng
  **danh sách kề ngược** `inc`.
- Đây là **BFS theo tầng**. `seen` giữ *khoảng cách ngắn nhất* và *loại cạnh cuối cùng*. `hops = 2` vì sang tầng 3 thì tập kết quả bùng
  lên gần cả repo (một GDD trung tâm có hàng chục cạnh `refs` đi vào).
- Độ phức tạp O(V + E) cho mỗi câu hỏi, cộng một lần dựng `inc` với chi phí O(E). Với 2 098 nút / 4 969 cạnh thì gần như tức thời.
  Phần đắt là dựng đồ thị (8 s, quét file + `git log`).
- `impact()` (dòng 389–398) sắp kết quả theo `(khoảng cách, doc trước artifact, hạng cạnh)` với `depends_on = 0 … co_change = 4`.
  Đây là xếp hạng *từ điển*, không có điểm số, nên không cần lo vấn đề thang đo như ở bài 03.

## 5. "Nghi cũ": staleness theo cạnh, thay cho cửa sổ thời gian

`gdd_drift.py` (bản cũ) hỏi: *GDD đổi thì trong 2 ngày phụ thuộc có đổi theo không?* Cửa sổ thời gian sai theo cả hai chiều. Phụ thuộc
đổi vì lý do khác vẫn được tính là "đã theo". Còn một tài liệu đúng mà không cần sửa lại bị tính là trượt (15/62 là ca `t == 0`).

`kg.suspects()` (dòng 414–431) đổi câu hỏi:

```python
for e in g['edges']:
    if e['type'] not in REV_TYPES:
        continue
    a, b = nodes.get(e['a']), nodes.get(e['b'])
    if not a or not b or a['type'] != 'doc':
        continue
    last_a = max(a.get('touched', 0), ver.get(a['id'], 0))
    if b.get('touched', 0) > last_a and b['type'] != 'entity' ...:
        out.append((a['id'], b['id'], round(age, 1)))
```

**A nghi cũ ⇔ tồn tại cạnh A → B sao cho `touched(B) > max(touched(A), verified(A))`.** Ở đây `touched` là thời điểm commit cuối, còn
`verified` là lần người chủ chạy `kg verify A` để xác nhận "đã xem, vẫn đúng" (lưu trong JSONL). Không còn cửa sổ thời gian nào. Một tài
liệu được *xác nhận* sẽ hết nghi mà không phải sửa chữ. Đây là cơ chế "kiểm tra phiên bản theo cạnh", giống cách build system so mtime của
target với dependency.

Pre-commit chạy `kg staged`, chỉ lấy file trong `git diff --cached` làm `changed`, mất khoảng 0,05 s (đọc đồ thị đã dựng, không dựng lại).
Nó chỉ cảnh báo, không chặn.

## 6. Số thật của K1 và lỗi thật

| Chỉ số | Trước K1 | Sau K1 | Cổng |
|---|---|---|---|
| impact: tìm đúng mảnh trong 12 (15 ca) | 0 / 15 | **10 / 15 = 66,7 %** | ≥ 60 % |
| impact: store@1 | — | 14 / 15 = 93,3 % | — |
| para (diễn đạt lại) toàn bộ | 7 – 9 | chưa lên | **chưa đạt** |
| `kg weekly` | — | `suspect_open: 82, orphan_entity: 2, nodes: 2098, edges: 4969, build_secs: 8.6` | — |

Có hai lỗi, phân tích nguyên nhân:

1. **82 nghi cũ là quá nhiều để có người xử lý.** Nguyên nhân: `refs` nằm trong `REV_TYPES` (propagate = true). Mọi tài liệu chỉ *nhắc*
   đường dẫn của một GDD đều thành "phụ thuộc". Chạy thật `kg impact colour-territory.md` ra toàn cạnh `refs` 1 bước: `audio-asmr.md`,
   `game-concept.md`, `residents.md`, `run-loop.md`, `swarm.md`… Nhắc tới không có nghĩa là dùng luật/số của nó. Đây là **precision thấp
   do kiểu cạnh quá rộng**. Hướng sửa: tách `refs` ra khỏi lan truyền nghi cũ, chỉ dùng nó cho câu hỏi tác động (giống `about`). Hoặc nâng
   `refs` thành `depends_on` khi chữ nhắc tới nằm trong mục "Phụ thuộc". *Thiết kế chưa chốt, xem README.*
2. **ID suy từ đường dẫn.** Đổi tên hoặc chuyển file thì nút cũ chết, cạnh đứt, `verified` mất. `refs` trong `unit.toml` vẫn là đường
   dẫn, chưa đổi sang `kg://<id>`. Đây cũng là điều kiện tiên quyết để tách repo (bài 06).

## Các cách làm và ưu/nhược

| Cách dựng cạnh | Ưu | Nhược | Gãy khi |
|---|---|---|---|
| Khai báo tay (L0) | đúng ý người viết | thiếu cạnh vì không ai ghi | tài liệu mới không có frontmatter |
| Luật suy (L1: đường dẫn, import) | 0 token, tất định, tự cập nhật | thừa cạnh (`refs`), không hiểu nghĩa | chữ nhắc tới mà không phụ thuộc |
| Co-change git | bắt được phụ thuộc ngầm mà không ai ghi | nhiễu do commit lớn, cần lịch sử | dự án mới, ít commit |
| Model trích xuất (bài 05) | hiểu nghĩa, bắt "A mâu thuẫn B" | tốn token, có thể bịa | không có cổng quote |
| Fuzzy entity linking | bắt được biến thể chính tả | link nhầm thực thể gần tên | hai thực thể trùng tên ngắn |

## Khi lớn lên

Đồ thị tăng tuyến tính theo số file. Dựng lại toàn bộ mất 8 s, và sẽ lâu hơn nhiều khi có ×10 file. Lối ra là **dựng tăng dần theo mtime
hoặc hash** (giống `recall.index`) và chỉ dựng lại cạnh của file đã đổi. Truy vấn BFS 2 bước không lo. Thứ thật sự phình là *nghi cũ*:
số cạnh lan truyền tăng thì số cảnh báo tăng theo. Vì vậy phải có trần `--send cap 3` (mỗi lần chỉ gửi tối đa 3 việc cho chủ tài liệu) và
chỉ số `suspect_open` theo dõi hằng tuần.

## Tự làm

1. `sh tools/claude/kit.sh kg impact colour-territory.md`: đếm có bao nhiêu kết quả là `refs`. Mở 2 file trong đó và tự quyết: chúng
   *dùng* luật của colour-territory, hay chỉ *nhắc* tới?
2. `sh tools/claude/kit.sh kg suspect | head -20`: chọn một cặp (A, B), xem `git log -1 --format=%ci -- B` và `-- A` để kiểm lại điều
   kiện `touched(B) > touched(A)`. Chạy `kg verify A` rồi chạy lại `suspect`.
3. Thêm một bí danh tay cho `entity:swarm` (vd "bầy cánh") vào `Thousandfold/kg/entities.toml` *trên nhánh nháp*, chạy `kg impact "bầy cánh"`,
   rồi chạy `kit recall --hub "đổi bầy cánh thì gì lệch"`. Vì sao lệnh thứ hai vẫn rỗng? (Gợi ý: `memhub.a_impact`.)

## Đọc thêm

- Hogan et al., *Knowledge Graphs* (ACM Computing Surveys 2021, arXiv 2003.02320): định nghĩa, ontology. *Kiến thức sẵn có.*
- Shen, Wang, Han, *Entity Linking with a Knowledge Base: Issues, Techniques, and Solutions* (TKDE 2015). *Kiến thức sẵn có.*
- Zimmermann et al., *Mining Version Histories to Guide Software Changes* (ICSE 2004): luật co-change. *Kiến thức sẵn có.*
- Trong repo: `kg/schema.toml`, `docs/shared/knowledge-graph-design.md` §2–§4.

> **Một dòng:** đồ thị tất định = ontology có kiểu cạnh + entity linking bằng bảng bí danh + BFS trên danh sách kề ngược. "Nghi cũ" so thời điểm theo cạnh thay cho cửa sổ thời gian. Kiểu cạnh quá rộng (`refs`) là nguồn báo động giả.
> **Bài sau:** [05 — Đồ thị có model: temporal KG, PPR, GraphRAG](05-do-thi-co-model.md)
