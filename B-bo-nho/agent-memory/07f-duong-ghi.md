# 07f — Đường ghi: hook nhắc, lan truyền, lint

> Chuỗi 07, bài 6/9. Đọc ~10 phút. Cần trước: [07c](07c-frontmatter.md), [07d](07d-bang-edges.md).

## 1. Câu chuyện

Phòng Art viết `depts/art/knowledge/gu-moi.md`: "từ nay nhà dùng mái dốc, màu ấm". Trong kho đã có `depts/art/knowledge/style-nha.md`
nói ngược lại, và ba doc khác (`previews/…/README.md`, một prompt sinh ảnh, một checklist QA) **link tới** `style-nha.md`. Agent
viết doc mới xong, commit, đi tiếp. Không ai khai `supersedes`. Tuần sau QA vẫn chấm theo checklist cũ, prompt sinh ảnh vẫn ra mái
bằng — ba doc kia "dựa trên cái cũ" mà không ai biết.

Bài [07c](07c-frontmatter.md) và [07e](07e-luat-xep-hang.md) chỉ chạy được nếu **có người khai**. Bài này là cơ chế làm cho việc khai
xảy ra — mà không biến thành giấy tờ.

## 2. Dừng 30 giây

- Lúc nào agent *biết rõ nhất* doc mới thay doc nào: lúc viết, lúc commit, hay lúc tuần sau có người hỏi?
- Nếu hook **chặn** lưu file cho tới khi điền `supersedes`, sau 2 tuần agent sẽ làm gì?
- Khi Y thay X, những ai cần được báo ngoài X?

## 3. Hook `PostToolUse` — câu hỏi 1

Lúc viết là lúc ngữ cảnh đầy nhất: agent vừa đọc chủ đề, vừa nghĩ về nó. Claude Code chạy hook `PostToolUse` **sau** mỗi lần dùng
công cụ, với `matcher` lọc tên công cụ (`Write|Edit|MultiEdit`). Hook nhận JSON có `tool_input.file_path`. Seriously đã dùng sự kiện
này cho `kit.sh meta --hook` (tạo `.meta`), `presence.py post`, `stuck_guard.py`.

Hook đề xuất (bước C, `tools/claude/supersede_hint.py`):
1. Lọc đường dẫn: chỉ `docs/**`, `depts/*/knowledge/**`, ADR, memory tầng 1. File khác → thoát ngay.
2. Đọc tiêu đề + `keywords:` của file vừa ghi → gọi `search()` (bài 07b: không `index()`, ms).
3. Có đoạn **cùng chủ đề, điểm cao, ở file khác** mà frontmatter chưa có `supersedes` → in **một dòng**:
   `xét: depts/art/knowledge/style-nha.md — điền supersedes: [...] hoặc supersedes: none`
4. Đã có `supersedes` (kể cả `none`) → im.

Một dòng đưa về agent ngay trong lượt đó (qua ngữ cảnh phụ của hook), agent sửa frontmatter trong vài giây.

## 4. Nhắc ≠ chặn — câu hỏi 2

Claude Code cho hook *chặn* (thoát mã 2 ở `PreToolUse` → không cho ghi). Vì sao không dùng?

- **Đóng cứng (ossification).** Bài SSGM (arXiv 2603.11768, trong [05](05-tranh-luan-kg-vs-recall.md)): lọc nhất quán quá chặt làm kiến
  thức không đổi được nữa — mọi cập nhật đều thành "mâu thuẫn cần xử lý".
- **Agent học lách.** Bị chặn mãi, agent điền `supersedes: none` cho xong — câu trả lời rác giống hệt câu trả lời đúng, và giờ còn
  *mất* tín hiệu "chưa xét". Cổng chặn biến khai báo thật thành khai báo cho có.
- **Gợi ý sai thường gặp.** BM25 trùng chữ ≠ cùng chủ đề. Nếu chặn, mọi gợi ý sai thành một lần kẹt.

Nên: hook nhắc, `none` là câu trả lời hợp lệ, không có gì bị chặn. Đo hiệu quả bằng **số `supersedes` mới / tuần** (bài [07g](07g-thuoc-do.md)),
không bằng tỉ lệ tuân thủ.

## 5. Lan truyền (bước G) — câu hỏi 3

Khi Y khai `supersedes: [X]`, ngoài X còn những doc **dựa vào** X. Bảng `edges` (bài 07d) trả lời ngay:
```sql
select src from edges where dst = 'depts/art/knowledge/style-nha.md' and type = 'links';
```
Hook C in thêm: `có thể dựa trên cái cũ: previews/…/README.md, prompts/nha.md, qa/checklist.md`. Agent quyết sửa, gửi việc cho
phòng chủ (`kit company send`), hay bỏ qua. Lan truyền chỉ **một bước** — đi tiếp thì danh sách nổ (hub, bài 07d §5).

Đây là cascade (lan truyền) theo kiểu "báo", không phải "tự sửa": tự sửa doc phòng khác vi phạm luật mảng (WORKBOARD) và có thể sai.

## 6. Lint tuần (bước E)

Hook chỉ thấy file *vừa ghi*. Có lỗi chỉ thấy khi nhìn cả kho:
| Kiểm | Bắt được |
|---|---|
| Cặp doc rất giống (BM25 chéo; sau P3 là cosine) mà không có cạnh `supersedes`/`links` | hai bản cùng chủ đề sống song song |
| Doc mồ côi (không ai link tới, không link ai) | kiến thức không ai tìm thấy bằng đường cạnh |
| `supersedes` trỏ file không tồn tại | đổi tên / xoá mà không sửa khai báo |
| Vòng `A supersedes B supersedes A` | khai sai |

Gắn vào `kit company lint` sẵn có: hiện in `WARN …`, không chặn trừ khi `--strict`. Đúng tinh thần: báo, chạy theo nhịp tuần.

## 7. Các cách, trên ca `gu-moi.md`

| Cách | Kết quả | Gãy khi |
|---|---|---|
| A. Luật trong `.claude/rules/`: "nhớ khai supersedes" | thường bị quên | agent bận |
| B. Cổng pre-commit chặn | khai `none` cho xong | sau 2 tuần — ossification + rác |
| C. Hook nhắc lúc ghi + `none` hợp lệ | khai đúng phần lớn ca | gợi ý BM25 sai → nhắc thừa (chấp nhận được, 1 dòng) |
| D. C + lan truyền G | thấy 3 doc phụ thuộc | hub làm danh sách dài → giới hạn ≤ 5, bỏ hub |
| E. LLM đọc doc mới, tự điền | ít công | token mỗi lần ghi (07a); tự tin sai |
| F. Chỉ lint tuần | bắt muộn 1 tuần | QA đã chấm sai cả tuần |

**Quy luật:** hỏi ở lúc ngữ cảnh đầy nhất (lúc ghi), hỏi một dòng, chấp nhận "không" làm câu trả lời; còn lại để lưới thưa hơn (lint
tuần) hứng.

## 8. Scale

- **Nhỏ**: luật A đủ, người viết nhớ hết.
- **Vừa** (Seriously: nhiều phòng, hàng chục phiên/ngày): C + G là chỗ có lời nhất — người viết Y không biết ai đang link X.
- **Lớn**: gợi ý của hook thành nhiễu nếu kho có nhiều doc trùng chữ; cần ngưỡng điểm cao hơn, lọc `scope`, và sau P3 dùng cosine thay
  BM25 cho câu "cùng chủ đề". Cái vỡ là **độ chính xác của gợi ý**, kéo theo agent nhờn.

## 9. Dừng lần hai — mở Seriously kiểm chứng

- `.claude/settings.json` → khối `PostToolUse` matcher `Write|Edit|MultiEdit` (`kit.sh meta --hook`, timeout 15 s): khuôn có sẵn cho
  hook mới.
- `tools/company/company.py` dòng ~727: `lint` = `scan()` + in `WARN`, `--strict` mới trả mã lỗi.
- `tools/claude/stuck_guard.py`, `tools/claude/harness-hook.py`: ví dụ hook "nhắc, không chặn" đang chạy.
- `docs/shared/memory-debate-2026-10-20.md` dòng ~60: trích SSGM.

## 10. Bốn nền tảng

Hook PostToolUse là tiến trình con, giống bài 07b: **Windows** khởi động chậm hơn **Mac**, nên lọc đường dẫn phải là việc *đầu tiên*
(thoát trước khi import nặng); đường dẫn trong `tool_input.file_path` trên Windows có `\` → chuẩn hoá trước khi so glob. **iOS /
Android** không có hook, nhưng cùng mẫu trong pipeline game: khi đổi một asset dùng chung (font, atlas), công cụ editor **liệt kê**
prefab/scene tham chiếu nó (Unity "Find References") thay vì chặn lưu — báo phụ thuộc, người quyết.

## 11. Tóm tắt một dòng

Đường ghi = hook nhắc một dòng lúc viết doc kiến thức ("xét X — supersedes hoặc none"), báo doc phụ thuộc một bước, lint tuần hứng
phần còn lại; không bao giờ chặn.

**Thuật ngữ:** PostToolUse · matcher · nudge vs gate (nhắc / chặn) · ossification (đóng cứng) · cascade (lan truyền) · orphan (mồ côi)
· lint. **Bài sau:** [07g — thước đo](07g-thuoc-do.md).
