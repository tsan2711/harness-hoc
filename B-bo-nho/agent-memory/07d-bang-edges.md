# 07d — Bảng `edges` = knowledge graph tất định

> Chuỗi 07, bài 4/9. Đọc ~10 phút. Cần trước: [05d knowledge graph](05d-knowledge-graph.md), [07c](07c-frontmatter.md).

## 1. Câu chuyện

Agent sửa `tools/claude/recall.py` và hỏi: *"việc nào trước đây đã đổi module này, và vì sao?"*. BM25 tìm chữ "recall.py" — ra 12
đoạn chuyện nhắc tên file, phần lớn là "đã chạy recall.py". Câu trả lời thật nằm ở **hai bước**: file → các commit đã sửa nó → việc
inbox mà commit đó làm (trailer `Task:`). Không đoạn văn nào chứa cả ba. Thông tin có đủ trong git, chỉ là nó nằm ở **quan hệ**,
không nằm ở **chữ**.

## 2. Dừng 30 giây

- Muốn trả lời câu trên mà không gọi LLM — quan hệ "commit sửa file" lấy từ đâu? "commit làm việc nào" lấy từ đâu?
- `docs/ai/WORKBOARD.md` bị 102 commit sửa trong 180 ngày, `recall.py` bị 12. Đi qua hàng xóm của WORKBOARD có ích không?
- Cần graph database (Neo4j) không, hay một bảng là đủ?

## 3. Đồ thị không cần LLM

Knowledge graph = **nút** (thứ) + **cạnh có nhãn** (quan hệ). Ở bài [05d](05d-knowledge-graph.md), cách đắt là cho LLM đọc văn bản và
trích quan hệ. Nhưng Seriously có sẵn rất nhiều quan hệ **đã được viết ra theo dạng máy đọc**:

| type | Nút → nút | Lấy từ (0 token) | Câu hỏi 1 |
|---|---|---|---|
| `touches` | commit → file | `git log --name-only` (đã đọc sẵn trong `last_touch()`) | "commit nào sửa file" |
| `implements` | việc → commit | trailer `Task:` trong commit | "commit làm việc nào" |
| `links` | doc → doc/file | link markdown `[..](..)`, đường dẫn trong văn bản | "doc nào dựa vào doc nào" |
| `supersedes` | doc → doc | frontmatter (bài 07c) | "cái gì thay cái gì" |
| `scope` | doc → game/phòng | frontmatter; đường dẫn (`depts/x/`, `June/`) | "đúng ở đâu" |

Tất cả là **tất định**: cùng git → cùng bảng (07a). Đó là lý do bài 06 nói "bảng `edges` *chính là* knowledge graph" — một KG
nghèo nhãn hơn KG trích bằng LLM, nhưng **không bao giờ bịa cạnh**.

Mô hình dữ liệu, một bảng trong `recall.sqlite`:
```sql
create table edges(src text, dst text, type text, ts text, source text);
create index edges_dst on edges(dst, type);
create index edges_src on edges(src, type);
```
`source` ghi cạnh đến từ đâu (`git`, `frontmatter`, `markdown`) — để debug và để bỏ cả một loại nếu nó gây nhiễu.

## 4. Truy vấn: một bước và đệ quy

**Một bước** — "ai links tới X?":
```sql
select src from edges where dst = 'docs/a.md' and type = 'links';
```

**Đệ quy** — chuỗi thay thế A ← B ← C, tìm bản mới nhất. SQLite có `with recursive` (CTE đệ quy):
```sql
with recursive chain(doc, depth) as (
  select 'docs/a.md', 0
  union all
  select e.src, chain.depth + 1 from edges e join chain on e.dst = chain.doc
  where e.type = 'supersedes' and chain.depth < 5
)
select doc from chain order by depth desc limit 1;     -- → docs/c.md
```
(Đã chạy thử với 3 cạnh mẫu: ra `docs/c.md`, độ sâu 2.) `depth < 5` chặn vòng lặp nếu ai đó khai A thay B và B thay A.
Câu hỏi 3: với vài chục nghìn cạnh, SQLite + chỉ mục trả trong ms. Graph DB đáng tiền khi đi **nhiều** bước trên **hàng trăm
triệu** cạnh — không phải cỡ này.

## 5. Hub — câu hỏi 2

Trong 180 ngày có 1 516 commit. Số commit sửa từng file:
| File | Commit | "Độ hiếm" log(1516/n) |
|---|---|---|
| `docs/ai/WORKBOARD.md` | 102 | 2,7 |
| `CLAUDE.md` | 32 | 3,9 |
| `tools/claude/recall.py` | 12 | 4,8 |

WORKBOARD bị sửa ở gần mọi phiên (nhận mảng, xoá dòng) — nó nối với *mọi thứ*, nên đi qua nó là đi tới *bất kỳ đâu*. Cũng như chữ
"là" trong BM25 ([05a](05a-bm25-va-fts5.md) §3.2): xuất hiện khắp nơi → gần như không mang thông tin. Cách xử lý giống IDF: khi mở
rộng theo cạnh, **hạ trọng số nút có bậc cao** (vd. nhân log(N/bậc)), hoặc bỏ hẳn danh sách hub (`WORKBOARD.md`, `CLAUDE.md`, `kit.sh`,
`tasks.jsonl`).

## 6. Các cách, thử trên câu "việc nào đã đổi recall.py"

| Cách | Kết quả | Ưu | Gãy khi |
|---|---|---|---|
| 1. BM25 chữ "recall.py" | 12 đoạn nhắc tên, ít đoạn nói *vì sao* | có sẵn | câu nhiều bước |
| 2. `edges` 2 bước: file ←touches← commit ←implements← việc | đúng các việc, kèm commit | tất định, ms | commit thiếu trailer `Task:` |
| 3. LLM trích KG từ toàn kho | cạnh giàu nhãn ("vì", "gây ra") | hiểu ý | tốn token; bịa cạnh; trái 07a |
| 4. Graph DB riêng | như 2 | truy vấn nhiều bước đẹp | thêm server cho một bảng nhỏ |

Điểm gãy của cách 2 là có thật: trong 1 516 commit chỉ **95 (≈ 6 %)** có trailer `Task:`. Cạnh `implements` thưa → câu "việc nào"
trả được cho việc đi qua inbox, còn việc làm thẳng thì không. Vá ở nguồn **đã có**: `kit commit` tự thêm `Task: <id>` khi phiên đang
claim một việc (`tools/claude/safe_commit.py`, `taskrec.set_active`) — nên 6 % phản ánh việc phần lớn commit *không* đi qua inbox
(Bi gõ "làm tiếp", sửa harness, art). Đồ thị tất định chỉ dày bằng quy trình sinh ra nó.

**Quy luật:** quan hệ đã được viết theo dạng máy đọc (git, link, frontmatter, trailer) thì đọc thẳng thành cạnh — rẻ, đúng, không
bịa; chỉ đi tìm cách đắt cho phần quan hệ **chưa ai viết ra**.

## 7. Scale

- **Nhỏ**: đồ thị vài trăm cạnh, nhìn bằng mắt cũng được.
- **Vừa** (Seriously: ~1,5k commit × vài file + vài nghìn link): một bảng SQLite, dựng lại cùng `index()` vài giây. Cái vỡ trước là
  **hub** và **cạnh thưa** (trailer), không phải tốc độ.
- **Lớn** (hàng triệu cạnh, đi 3+ bước): CTE đệ quy bùng nổ số đường; cần giới hạn bậc, PPR (Personalized PageRank, [05d](05d-knowledge-graph.md))
  thay cho duyệt hết — lúc đó mới bàn graph DB.

## 8. Dừng lần hai — mở Seriously kiểm chứng

- `tools/claude/recall.py` `git_rows()`: đã đọc `git log --name-only` **và** `%(trailers:key=Task…)` — dữ liệu cho `touches` và
  `implements` có sẵn, chỉ chưa lưu thành bảng.
- `last_touch()`: cùng `git log`, cache theo HEAD vào `company/state/recall-touch.json`.
- Đếm hub: `git log --since='180 days ago' --format=%h -- docs/ai/WORKBOARD.md | wc -l`.
- Đếm trailer: `git log --since='180 days ago' --format='%(trailers:key=Task,valueonly)' | grep -c .`.
- `tools/company/taskrec.py` + `company/records/tasks.jsonl`: nguồn nút "việc"; `taskrec` dòng ~61 đã tra "commit nào mang
  `Task: <id>`" bằng `git log --grep` — một cạnh `implements` tính lúc hỏi, chưa lưu bảng.
- `tools/claude/safe_commit.py` dòng ~49: chỗ trailer `Task:` được gắn.

## 9. Bốn nền tảng

SQLite và `with recursive` giống nhau trên **Windows / Mac / iOS / Android** (CTE đệ quy có từ SQLite 3.8.3, mọi bản hệ thống đều
có). Trên **Windows** chú ý đường dẫn: git trả `/`, Python có thể tạo `\` — nút `src/dst` phải chuẩn hoá về `/` không thì một file
thành hai nút. Trong game mobile, cùng mô hình "bảng cạnh trong SQLite" hay dùng cho cây kỹ năng, quan hệ nhiệm vụ, đồ thị hội
thoại — nhỏ, đọc nhanh, không cần thư viện graph.

## 10. Tóm tắt một dòng

Knowledge graph của Seriously là một bảng `edges(src, dst, type, ts, source)` đọc thẳng từ git/link/frontmatter/trailer: 0 token,
không bịa cạnh, truy vấn bằng SQL đệ quy; nhớ hạ trọng số hub và vá cạnh thưa ở nguồn.

**Thuật ngữ:** node / edge (nút / cạnh) · edge label (nhãn cạnh) · degree (bậc) · hub · recursive CTE · trailer · sparse edges
(cạnh thưa) · PPR. **Bài sau:** [07e — luật xếp hạng](07e-luat-xep-hang.md).
