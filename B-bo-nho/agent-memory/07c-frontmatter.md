# 07c — Frontmatter `status / supersedes / scope / keywords`

> Chuỗi 07, bài 3/9. Đọc ~10 phút. Cần trước: [05f kiến thức cũ](05f-ky-uc-cu-va-thay-the.md), [07a](07a-nguyen-tac-git-nguon-su-that.md).

## 1. Câu chuyện

Ngày 2026-10-11 có `docs/shared/thousandfold-art-directions.md` — "chọn hướng art". Vài ngày sau commit `d9e331fe` đổi hướng sang
Sky (grade ấm/lạnh, tàn tích đá). File cũ **không hề biết** mình đã cũ: không tiêu đề "(cũ)", không dòng nào trỏ sang cái mới.
Agent hỏi "hướng art Thousandfold hiện tại" → file cũ có đủ chữ "hướng art Thousandfold", điểm BM25 cao, lên top. Đây chính là câu
`trap-art` trong bộ đo `company/eval/recall/cases.toml`.

Máy không thể biết "cũ" bằng cách đọc chữ. Ai đó phải **nói** cho nó — và cách nói phải đọc được bằng máy.

## 2. Dừng 30 giây

- Khi có bản mới, nên ghi "đã bị thay" vào **file cũ** hay "tôi thay X" vào **file mới**? Cái nào ít quên hơn?
- `supersedes: none` và *không có dòng `supersedes`* — có giống nhau không?
- Hai game có hai luật khác nhau về cùng một chuyện (June dùng ECS, NanoSwarm dùng OOP) — đó có phải "cái mới thay cái cũ"?

## 3. Metadata và schema

**Frontmatter** là khối đầu file markdown, giữa hai dòng `---`, viết YAML: dữ liệu *về* tài liệu (metadata), không phải nội dung.
Người đọc lướt qua; máy đọc chắc chắn, không phải đoán.

**Schema** là bản hợp đồng: trường nào, kiểu gì, giá trị nào hợp lệ. Bài 06 đề xuất:

```yaml
---
status: active            # active | superseded | wrong
supersedes: [docs/shared/thousandfold-art-directions.md]   # hoặc: none
scope: [thousandfold]     # hoặc [all]; game hoặc bộ phận
keywords: [art, Sky, grade, hướng art]
---
```

| Trường | Trả lời câu | Vì sao cần |
|---|---|---|
| `status` | Còn dùng không? | `wrong` khác `superseded`: sửa sai thì **bỏ hẳn**, còn bị thay thì vẫn là lịch sử đúng *tại thời điểm đó* |
| `supersedes` | Tôi thay cái nào? | Câu hỏi 1 — xem §4 |
| `scope` | Đúng ở đâu? | Câu hỏi 3: hai luật khác game **cùng tồn tại**, không phải thay thế. Không có `scope` thì "mới nhất thắng" sẽ đè luật June bằng luật NanoSwarm |
| `keywords` | Tôi *về* cái gì? | Vào cột `ent` ×3 của FTS5 (đã có từ `cc86face`, 2026-10-18) — đoạn *về* chủ đề thắng đoạn chỉ *nhắc* chủ đề |

## 4. Ghi ở đâu: suy ngược cạnh

Ba chỗ có thể ghi quan hệ "Y thay X":

**(a) Trên file cũ:** `superseded_by: Y`. Phải mở và sửa file X — người viết Y thường không nhớ X, và có khi X thuộc phòng khác
(không được sửa file mảng người khác đang nhận). Hai file cùng phải đúng → dễ lệch.

**(b) Trên file mới:** `supersedes: [X]`. Người viết Y đang nghĩ đúng về chủ đề đó, đang ở trong file đó. **Một chỗ ghi.**

**(c) Một file sổ riêng** (`supersedes.toml`). Tách khỏi tài liệu → ai cũng quên cập nhật.

Đề xuất chọn (b), và chỉ mục **suy ngược**: đọc `Y.supersedes = [X]` → tạo cạnh `Y → X` → khi X lên kết quả, máy tra ngược
"ai thay X?" và gắn nhãn "ĐÃ THAY BỞI Y". File cũ **không cần sửa** — đúng với 07a (git là nguồn, chỉ mục tính phần còn lại).

## 5. `none` ≠ thiếu — câu hỏi 2

- **Không có dòng:** chưa ai xét. Có thể có bản cũ, có thể không.
- **`supersedes: none`:** người viết *đã xét* và khẳng định không thay gì.

Khác biệt này cho phép hook ở bài [07f](07f-duong-ghi.md) nhắc đúng lúc: thiếu dòng → nhắc "xét: X, Y"; có `none` → im. Không có
giá trị `none` thì hoặc hook nhắc mãi (ồn), hoặc phải ép điền một file giả. Đây là mẹo chung của schema: **phân biệt "chưa trả lời"
với "trả lời là không"** (giống `null` vs `[]` trong JSON).

## 6. Các cách, thử trên ca `trap-art`

| Cách | `trap-art` | Ưu | Gãy khi |
|---|---|---|---|
| 1. Không gì cả | file cũ lên top, không nhãn | 0 công | luôn |
| 2. Tiêu đề "(cũ) / đã thay bởi" (hiện có: regex `SUPERSEDED` trong `recall.py`) | có nhãn *nếu* ai sửa tiêu đề | không cần schema | phải sửa file cũ; regex bắt chữ, viết khác là trượt |
| 3. Frontmatter `supersedes` trên file mới | nhãn + đẩy bản mới | một chỗ ghi, máy đọc chắc | bản mới là **commit**, không phải doc (đúng ca này!) |
| 4. LLM đọc hai file, phán "cái nào mới" | thường đúng | không cần ai ghi | STALE: phán lúc đọc đúng ~55 %; tốn token (07a) |

Ca `trap-art` lộ một lỗ: quyết định mới nằm trong commit `d9e331fe`, không có doc mới để gắn frontmatter. Hai cách vá: luật "đổi
hướng = sửa/viết doc sống" (luật A của bài 06: một chủ đề một file sống, sửa tại chỗ) hoặc trailer commit `Supersedes: <path>`
(cùng kiểu trailer `Task:` đang có). Luật A rẻ hơn và tránh phải dựng thêm nguồn cạnh.

**Quy luật:** cái máy không suy ra được (ý định, phạm vi) thì người viết khai **một lần, ở chỗ đang viết**; cái suy ra được
(chiều ngược, ngày, ai sửa) thì để chỉ mục tính.

## 7. Scale

- **Nhỏ** (vài chục doc): đọc tay là thấy cũ/mới; frontmatter là thừa.
- **Vừa** (Seriously: hiện chỉ **1** file có `keywords:`, **2** file có `status/scope`): lợi ích đến từ việc *áp dần* — mỗi doc mới
  có frontmatter, `_template/` có sẵn khối. Không cần điền ngược cho doc cũ (suy ngược lo phần đó).
- **Lớn** (nhiều nghìn doc, nhiều người viết): schema trôi — người viết `superseeds`, `scope: [Thousandfold]` hoa/thường. Cần lint
  kiểm tên trường, giá trị hợp lệ, đường dẫn trong `supersedes` có tồn tại (bài 07f). Cái vỡ là **tính nhất quán của khai báo**.

## 8. Dừng lần hai — mở Seriously kiểm chứng

- `tools/claude/recall.py`: `KEYWORDS = re.compile(r'^keywords:…')` và `title_terms()` — `keywords:` + tiêu đề mục vào cột `ent`.
- Cùng file: `SUPERSEDED = re.compile(…đã thay bởi|superseded|\(cũ\)…)` và `doc_outdated()` — cách 2 trong bảng.
- `company/eval/recall/cases.toml` dòng ~249: nhóm `trap` (5 câu), trường `stale` = đường dẫn không được lên như bản mới.
- `head docs/shared/thousandfold-art-directions.md` rồi `git show --stat d9e331fe` — tự thấy ca bài này.
- `grep -rlE '^keywords:' docs depts/*/knowledge` — đếm số file đã dùng.

## 9. Bốn nền tảng

Frontmatter là text thuần, giống hệt trên **Windows / Mac**; lưu ý duy nhất là xuống dòng `\r\n` trên Windows — regex `^keywords:`
với cờ `re.M` vẫn khớp, nhưng giá trị có thể dính `\r` nếu không `strip()`. Trên **iOS / Android** cùng ý tưởng xuất hiện ở
**metadata của asset/bundle**: Addressables, AssetBundle manifest, Play Asset Delivery đều giữ "phiên bản nào thay phiên bản nào"
trong manifest của bản mới, chứ không sửa bundle cũ đã phát hành — đúng mô hình (b) "khai ở cái mới, suy ngược cái cũ".

## 10. Tóm tắt một dòng

Người viết khai một lần trên file mới (`status/supersedes/scope/keywords`, `none` = đã xét); chỉ mục suy ngược để file cũ tự mang nhãn.

**Thuật ngữ:** frontmatter · metadata · schema · supersede (thay thế) · scope (phạm vi) · coexistence (cùng tồn tại) · reverse edge
(cạnh suy ngược) · null vs empty. **Bài sau:** [07d — bảng edges](07d-bang-edges.md).
