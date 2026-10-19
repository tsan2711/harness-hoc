# Bài A01d — Cổng và hook: harness chen vào vòng lặp ở đâu, để làm gì

> Đọc sau A01c. Nguồn thật: `.claude/settings.json` của Seriously + `tools/claude/stuck_guard.py`, `ctxguard.py`, `tools/company/company_hook.py`.

## 1. Câu chuyện: agent chạy `rm` sai thư mục
Ngọc dặn trong prompt: "đừng xoá dữ liệu". Hôm sau agent, trong lúc "dọn", vẫn chạy lệnh xoá một thư mục. Lời dặn không sai — nó chỉ **không phải là cơ chế**. Chữ trong prompt là *xin*; hook là *buộc*.

## 2. Dừng 30 giây
- Có 5 mức kiểm soát một hành động nguy hiểm: (1) dặn trong prompt, (2) danh sách cho phép/cấm, (3) hỏi người, (4) hook tự động chặn, (5) sandbox. Xếp theo **độ chắc chắn** và đoán nhược điểm của mỗi mức.
- Vòng lặp A01 có các điểm: bắt đầu phiên · người gõ · trước công cụ · sau công cụ · công cụ lỗi · model dừng · trước nén · hết phiên. Với mỗi điểm đoán *loại việc* hợp để chen vào.
- Hook bị lỗi/treo — phiên nên sập hay chạy tiếp? Chọn rồi đọc mục 4.

## 3. Bản đồ hook thật của Seriously (rút từ settings.json)
| Điểm chen | Hook | Việc |
|---|---|---|
| **SessionStart** | session-start.sh · company_hook start · leftover start | in trạng thái repo, WORKBOARD, việc dở của phiên trước |
| **UserPromptSubmit** | presence prompt · **ctxguard** | ghi ai đang làm gì; nhắc khi ngữ cảnh > 120k |
| **PreToolUse** (Bash) | **company_hook guard** | chính sách tiền/xoá: hỏi người hoặc từ chối |
| **PreToolUse** (mọi) | ctxguard tool · presence pre | trần ngữ cảnh (tắt chặn mặc định); báo giẫm chân file |
| **PreToolUse** (Edit/Write) | company_hook edit | kiểm sửa file theo bộ phận |
| **PostToolUse** | meta (tạo `.meta` Unity) · harness-hook (ghi vấp) · presence post · **stuck_guard ok** | tự động hoá việc hậu kỳ; ghi nhận |
| **PostToolUseFailure** | **stuck_guard fail** | cùng lệnh lỗi lặp lại → nhắc "đổi cách" |
| **PreCompact** | leftover compact | lưu tờ bàn giao trước khi nén |
| **Stop / SessionEnd** | company_hook log · presence stop/end · leftover end | ghi nhật ký, trả claim |

## 4. Ba kiểu hook — chọn đúng kiểu cho đúng việc
| Kiểu | Cách | Ví dụ thật | Ưu | Nhược / điểm gãy |
|---|---|---|---|---|
| **Nhắc** | in `additionalContext` vào tờ giấy | stuck_guard (≥3 lỗi: "đổi cách", ≥5: ghi friction log); ctxguard (>120k) | không bao giờ làm kẹt việc; sửa hành vi bằng thông tin | model có thể lờ; mỗi lời nhắc tốn token |
| **Hỏi/chặn** | `permissionDecision: ask/deny` | company_hook guard: "tiền/xoá cần Bi duyệt" — `deny` nếu chạy nền (không có người), `ask` nếu có người | **chắc chắn** với việc không đảo ngược | chặn nhầm = agent kẹt; phải có lối thoát (người duyệt) |
| **Ghi nhận** | chỉ log, không đổi hành vi | presence, harness-hook, company log | rẻ, an toàn, nuôi đo lường (chặng G) | không bảo vệ gì; chỉ có ích nếu có người/việc đọc log |

Và một **quy ước sống còn** — *hook thất bại thì mở (fail-open)*: stuck_guard, ctxguard đều "never fails the session (always exit 0)". Hook là phụ; hook sập mà sập cả phiên thì tệ hơn việc nó cố bảo vệ. Ngoại lệ chủ động: cổng cho việc **không đảo ngược** (tiền, xoá) mới đáng fail-closed.

Hai chi tiết thiết kế đáng học:
- **`deny` trong nền, `ask` khi có người**: cùng một chính sách, hành vi khác theo ngữ cảnh — không người thì không ai trả lời "ask" nên phải từ chối.
- **ctxguard mặc định chỉ nhắc, không chặn** (`[context].deny = false`): chặn công cụ lúc ngữ cảnh đầy từng khiến phiên kẹt; thay bằng để hệ thống tự nén. Bài học: cổng chặn là dao hai lưỡi, đo trước khi bật.

## 5. So sánh với các cách khác
| | Chắc chắn | Phiền người | Linh hoạt | Điểm gãy |
|---|---|---|---|---|
| Dặn trong prompt | thấp | không | cao | model quên/bị injection |
| Allow/deny list | cao với lệnh khớp | thấp | thấp (khớp chuỗi) | lệnh biến thể lách được |
| Hỏi người mỗi lần | cao | **rất cao** | cao | người bấm "yes" theo quán tính; không chạy nền |
| **Hook tự động** | cao với việc kiểm tra được bằng mã | không | cao | hook viết sai/chậm; cần fail-open hay fail-closed rõ |
| Sandbox | rất cao | thấp | thấp | tốn công dựng; che mất việc cần thật |

Chú ý: cài đặt toàn cục của tác giả ở chế độ `bypassPermissions` với 138 mục cho phép — tức hệ thống **không dựa vào hỏi từng lệnh**, mà dựa vào hook chính sách. Đây là lựa chọn: nhanh, và đặt toàn bộ độ an toàn vào chất lượng hook. Hook đúng → an toàn mà không phiền; hook thiếu → không còn lưới.

## 6. Scale
| Cỡ | Hiện tượng |
|---|---|
| 1 người, vài hook | tuỳ ý |
| ~20 hook (như Seriously) | độ trễ cộng dồn mỗi công cụ (mỗi hook ~75ms trong dữ liệu stop_hook_summary → vài chục ms–trăm ms mỗi lượt), thứ tự và xung đột; cần đo thời gian hook (`hooklog`) |
| nhiều đội / nhiều game | hook phải đọc cấu hình theo game (manifest), không hard-code; có cờ bật/tắt (layers.toml) để gỡ "nạng" khi không cần |

## 7. Dừng lần hai
- Mở `tools/claude/stuck_guard.py` (108 dòng): tìm hằng `WARN, HARD, TTL`. Vì sao TTL 900 giây? Điều gì xảy ra nếu bạn thử cùng lệnh lỗi mỗi 20 phút?
- Mở `tools/company/company_hook.py` hàm `cmd_guard` (~dòng 201): tìm chỗ quyết định `deny` hay `ask`. Còn trường hợp nào bạn muốn thêm vào chính sách?
- Thử viết (không cần chạy) một hook PreToolUse chặn `git push --force`. Nó trả JSON gì? Nên fail-open hay fail-closed?

## 8. Bốn nền tảng
Hook là tính năng của harness (Claude Code CLI) nên giống nhau trên Mac/Windows; khác ở lệnh hook: Mac `sh`/`python3`, Windows cần `python`/PowerShell và dấu `\`. Trên iOS/Android không có hook của CLI — "cổng" nằm trong mã app/server của bạn: kiểm quyền (permission OS), xác nhận người dùng, rate limit; nguyên lý (nhắc/chặn/ghi) giữ nguyên.

## 9. Tóm tắt
Prompt là xin, hook là buộc. Ba kiểu: nhắc (an toàn), chặn (chắc, nhưng có thể kẹt), ghi (nuôi đo lường). Hook phụ thì fail-open; cổng cho tiền/xoá thì chắc tay. Khi tắt hỏi-từng-lệnh, chất lượng hook là toàn bộ lưới an toàn.
