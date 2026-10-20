# 03 — `leftover.py`: tờ bàn giao cuối ca (đọc code thật)

Nguồn: `Seriously/tools/claude/leftover.py` (416 dòng, đọc 2026-10-17). Không gọi AI, ~0 token.

## 1. Nó giải bài toán gì

Bạn `/clear` hoặc đóng phiên giữa chừng → phiên mới **quên sạch** việc dở. `leftover` là một script nhỏ:
- **Lúc phiên kết thúc:** đọc transcript, rút "việc còn dở", cất lại.
- **Lúc phiên mới mở:** in tối đa 2 dòng nhắc việc dở.

Ví dụ nhắc bạn sẽ thấy:
`Việc dở từ phiên trước ở thư mục này: 1 phiên — mới nhất: "Sửa KeyframeCapture" (3 file chưa commit, 2 todo). Chi tiết: company/state/leftovers/ab12cd34.md`

## 2. Ba cửa vào (hook)

| Lệnh | Hook | Việc |
|---|---|---|
| `end` | SessionEnd | `capture()` — ghi bản bàn giao |
| `compact` | PreCompact | như `end`, lý do = compact |
| `start` | SessionStart | `cmd_start()` — in nhắc việc dở |
| `backfill [ngày]` | chạy tay | bù cho các phiên chưa có bản ghi |

Mọi lỗi đều bị nuốt (`except Exception`): "hook không bao giờ được làm hỏng phiên". Thời gian chạy ghi vào `hook-timing.jsonl`.

## 3. Bước 1 — `extract()`: đọc transcript, rút sự kiện

Transcript là file JSONL, mỗi dòng một sự kiện. Script duyệt từ đầu đến cuối bằng **quy tắc cứng**, không hiểu nghĩa:

| Rút ra | Cách nhận biết |
|---|---|
| **Yêu cầu cuối của Bi** (`ask`) | tin nhắn user cuối cùng không phải tool_result, không phải nhiễu (`<command-…>`, `<system-reminder>`…), không phải lệnh `/xxx` đứng một mình. Cắt 600 ký tự |
| **Đã trả lời xong chưa** (`answered`) | sau `ask`, thấy một khối **text** của assistant → xong. Nhưng nếu sau đó lại có **tool_use** → đặt lại "chưa xong" (lượt vẫn đang chạy) |
| **Bị ngắt** (`interrupted`) | thấy chuỗi `[Request interrupted by user` |
| **File đã sửa** (`files`) | mọi tool_use `Write/Edit/MultiEdit/NotebookEdit`, lấy `file_path` (giữ 60 file cuối) |
| **Todo chưa xong** | lần `TodoWrite` cuối (lọc status ≠ completed) + `TaskCreate/TaskUpdate` chưa completed/deleted, tối đa 12 |
| **Dòng WORKBOARD đã nhận** (`claims`) | `Edit` vào `WORKBOARD.md`: dòng bảng mới thêm (so `new_string` với `old_string`) |
| Tiêu đề, tóm tắt | `custom-title` (ưu tiên) hoặc `ai-title`; sự kiện `away_summary` của Claude Code |
| Phiên kế nhiệm | sự kiện `continued-in` |

Điểm hay: "đã trả lời chưa" suy ra từ **hình dạng** hội thoại (có chữ trả lời cuối hay đang gọi tool), không cần AI đoán.

## 4. Bước 2 — kiểm tra thực tế bây giờ: còn mở không?

Rút từ transcript mới là "đã từng sửa file X". Việc dở thật phải hỏi **hiện trạng**:

- **`dirty(files)`**: chạy `git status --porcelain` (một lệnh mỗi repo) → file nào trong danh sách vẫn **chưa commit**. Loại file bị sửa **sau** lúc phiên im 120 giây (đó là việc của phiên khác, không phải của phiên này).
- **`open_claims()`**: dòng WORKBOARD phiên này nhận mà **vẫn còn** trong bảng (chưa xoá = chưa trả).

Quy tắc kết luận (`is_open`): mở nếu có **một trong**: file chưa commit · todo chưa xong · claim còn · yêu cầu cuối chưa trả lời. Và phiên phải có ít nhất 1 lượt (`turns > 0`) để khỏi nhắc phiên rỗng.

## 5. Bước 3 — cất

- Thêm một dòng JSON vào `company/state/leftovers.jsonl` (giữ tối đa ~4000 dòng, vượt thì cắt nửa đầu).
- Nếu `open` → viết thêm `company/state/leftovers/<sid>.md`: yêu cầu cuối (ghi rõ "CHƯA xong / bị ngắt"), tóm tắt, câu trả lời cuối, todo, file chưa commit, dòng WORKBOARD còn, và lệnh `claude --resume <sid>` (tốn token, chỉ dùng khi cần).
- Cả hai nằm trong `company/state/` → **riêng từng máy, không vào git**.

## 6. Lúc mở phiên mới — `cmd_start()`

Hai trường hợp:

**(a) Sau `/clear`.** Vấn đề: id phiên mới không biết id phiên cũ.
- Lúc `end` với reason `clear`, script ghi một "dấu kết thúc" vào `succession.jsonl` kèm **PID của tiến trình `claude`** (leo cây tiến trình bằng `ps`, `claude_pid()`).
- Lúc `start`, `pair_clear()` tìm dấu đó (cùng PID, hoặc cùng thư mục trong 20 giây), chờ tối đa 2 giây vì hai hook có thể chạy chéo nhau, rồi ghi cặp `cũ → mới`.
- Nếu phiên cũ còn dở → in: `↺ Phiên trước (vừa /clear) còn dở: … — 3 file chưa commit, 2 todo. Chi tiết: …`

**(b) Mở phiên bình thường.** Lấy các bản ghi `open` trong **cùng thư mục**, trong 14 ngày, rồi **kiểm lại lần nữa**: chỉ giữ những phiên mà file dở **vẫn còn dirty** hoặc claim **vẫn còn**. (Nếu bạn đã commit xong thì tự biến mất, không nhắc nữa.) In 1 dòng cho phiên mới nhất.

Nguồn `compact` thì **không in gì** (cùng phiên, ngữ cảnh được tóm lại rồi).

**Dòng thứ hai (tuỳ chọn):** `recall_line()` gọi `recall.hint()` với đường dẫn ghi chú → tối đa 3 trích đoạn trí nhớ liên quan đến các file phiên cũ đã chạm, nén thành 1 dòng `↳ Nhớ liên quan: …` (≤400 ký tự). Lỗi thì bỏ qua.

## 7. Nó KHÔNG làm gì (giới hạn thật)

- **Không hiểu nghĩa.** Phiên chỉ trả lời "đã ổn rồi nhé" mà bỏ dở lời hứa nửa chừng → không bắt được.
- Việc dở chỉ có thể nhận ra qua 4 dấu: file chưa commit, todo, claim, câu hỏi chưa trả lời. Việc dở "trong đầu" không có dấu thì mất.
- Todo phụ thuộc agent có dùng `TodoWrite/Task*` hay không.
- Chỉ cùng thư mục (`realpath(cwd)` khớp) và trong 14 ngày.
- Chỉ trên **một máy** (state không vào git).
- Với phiên chạy nhiều giờ, `extract` đọc cả file mỗi lần kết thúc (script nói ~0,2 s cho 15 MB).

## 8. Vì sao thiết kế thế này (bài học chung)

- Dùng **dấu hiệu cứng + trạng thái thật (git)** thay vì để AI "nhớ lại": rẻ, không bịa, tự dọn (commit xong là hết nhắc).
- So với **claude-mem**: claude-mem nén bằng AI nên nắm được ý, đổi lại tốn token và có thể sai. `leftover` đảo lại: chắc chắn nhưng nông.
- Hợp với lớp **bàn giao** trong bài 02. Ba lớp bổ sung nhau: `leftover` (việc dở, tự động) · INDEX "Đang làm gì" (việc đang theo đuổi, agent viết) · `recall` (tra chuyện cũ).

## 9. Ý tưởng cải tiến (chỉ ghi, chưa làm)

- Bắt thêm dấu "lời hứa chưa thực hiện" (ví dụ cụm "tôi sẽ…", "bước tiếp theo" ở câu trả lời cuối) — vẫn bằng regex, không cần AI.
- Đồng bộ giữa máy nếu Bi dùng nhiều máy.
- Đo: bao nhiêu lần nhắc leftover thực sự được agent dùng (hiện chỉ có `hook-timing.jsonl`).

## Tự kiểm tra

1. Vì sao `answered` bị đặt lại `False` khi thấy tool_use sau câu trả lời?
2. Vì sao cần PID để ghép phiên cũ ↔ mới khi `/clear`?
3. Bạn commit hết file xong rồi mở phiên mới: có còn nhắc không? Vì sao?

(Đáp: 1. Lượt vẫn đang chạy, chưa có câu chốt. 2. Id phiên mới do Claude cấp, hai hook chạy ở hai lúc; PID của tiến trình `claude` là thứ duy nhất chung. 3. Không — `cmd_start` kiểm lại `dirty` và claims, hết dirty là bỏ.)
