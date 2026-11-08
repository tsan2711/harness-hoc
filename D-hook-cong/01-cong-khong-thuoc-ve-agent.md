# Bài D01 — Cổng không thuộc về agent: ba mối nối và một lớp phiên dịch

> **Bạn đã biết** (A01d): hook là đoạn mã tự chạy ở một điểm của vòng lặp agent; có kiểu *nhắc*, *chặn*, *ghi*; hook hỏng thì thường *mở* (fail-open).
> Nguồn thật: `tools/claude/ctxguard.py`, `tools/claude/transcript.py`, `tools/company/settings.py` của Seriously.

## 1. Câu chuyện
Hoa dựng một bộ "cổng" cho trợ lý AI: chặn lệnh xoá, nhắc khi cuộc trò chuyện quá dài, cảnh báo khi hai trợ lý sửa cùng file. Ba tháng sau công ty đổi sang một trợ lý khác rẻ hơn. Hoa chạy thử: **không báo lỗi gì, nhưng cổng nào cũng im lặng.** Mã chặn xoá vẫn đúng từng dòng; chỉ là không còn ai gọi nó.

## 2. Dừng 30 giây
- Một cổng gồm hai phần: *chuyện cần kiểm* (logic) và *chuyện được gọi thế nào* (nối dây). Đoán trong cổng "nhắc khi cuộc trò chuyện quá dài", phần nào là logic, phần nào là nối dây.
- Nghĩ ra ba thứ mà trợ lý A và trợ lý B gần như chắc chắn **làm khác nhau** dù cùng chạy một việc.
- Cổng im lặng khác cổng hỏng ở chỗ nào? Làm sao biết một cổng *đang sống*?

## 3. Cổng gồm hai nửa
Cách nghĩ chuẩn trong kỹ thuật phần mềm gọi là **ports & adapters** (kiến trúc lục giác): lõi nghiệp vụ không biết bên ngoài là ai; mỗi bên ngoài có một **adapter** (bộ phiên dịch) mỏng nằm giữa. Đổi bên ngoài = đổi adapter, lõi giữ nguyên.

Áp vào cổng của agent:

```
 agent (Claude / Codex / ...)
   │  ① sự kiện được gọi?          ← trigger
   │  ② JSON gửi vào có dạng gì?   ← wire format (stdin)
   │  ③ nhật ký phiên lưu ra sao?  ← transcript
   │  ④ tên công cụ là gì?         ← "Edit" hay "apply_patch"
   ▼
 adapter mỏng  ────────────►  lõi: "ngữ cảnh > 150k thì chặn"  (không biết agent nào)
```

Lõi (phép so sánh 150k, quy tắc chặn lệnh xoá) là mã thuần: nhận số, trả quyết định. Thứ dính vào agent là bốn mối nối ①–④.

## 4. Bốn mối nối, đo bằng mã thật
**① Kích hoạt.** Agent đọc một file cấu hình (`.claude/settings.json`) và gọi script ở đúng sự kiện. Agent khác có file cấu hình khác, danh sách sự kiện khác. Nếu agent không có sự kiện đó thì cổng không bao giờ chạy.

**② Hình dạng dữ liệu vào.** Hook nhận một khối JSON qua stdin. Ở Claude Code và Codex phần lớn trùng nhau: `session_id`, `transcript_path`, `cwd`, `tool_name`, `tool_input`; trả lời bằng `hookSpecificOutput.permissionDecision` hoặc thoát mã 2. Đây là mối nối **dễ** nhất vì hai bên cùng theo một khuôn.

**③ Nhật ký phiên (transcript).** Muốn biết "cuộc trò chuyện đã dài bao nhiêu", cổng phải đọc nhật ký. Trích `transcript.py`:

```python
def context_tokens(u):
    return sum(int(u.get(k) or 0) for k in CACHE_KEYS)   # input + cache đọc + cache ghi
```
Nó lấy `message.usage` của lần gọi model cuối trong file JSONL của Claude. Mỗi agent lưu nhật ký **tên trường khác, cấu trúc khác**. Đây là mối nối **khó** nhất, vì sai âm thầm: parser không tìm thấy trường → trả `None` → cổng hiểu là "chưa dài" → không chặn.

**④ Tên công cụ.** `presence.py` khớp `Edit|Write|MultiEdit|NotebookEdit` để biết "agent đang sửa file". Agent khác sửa file bằng công cụ tên khác thì bộ khớp bỏ sót, cảnh báo giẫm chân biến mất.

Chú ý ba cách hỏng khác nhau về **độ nguy hiểm**:
| Hỏng ở | Triệu chứng | Phát hiện |
|---|---|---|
| ① không gọi | không có dòng log nào | dễ: đếm số lần cổng chạy |
| ②/④ sai tên trường | cổng chạy, quyết định luôn "cho qua" | trung bình: cần ca thử biết trước đáp án |
| ③ parser trả rỗng | cổng chạy, số đo = rỗng, "cho qua" | **khó**: nhìn bề ngoài đang khoẻ |

## 5. Ba cách tổ chức khi muốn dùng nhiều agent
| Cách | Mô tả | Ưu | Nhược / điểm gãy |
|---|---|---|---|
| **A. Viết lại cổng cho mỗi agent** | mỗi agent một bộ script | đơn giản từng bộ | logic nhân đôi, hai bộ lệch nhau sau vài tuần |
| **B. Một lõi + adapter mỏng** | script đọc JSON chuẩn; mỗi agent có file cấu hình *sinh ra* từ cùng một bảng | sửa luật một chỗ; thêm agent = thêm một bộ sinh | phải giữ adapter đúng khi agent đổi phiên bản |
| **C. Đẩy cổng ra ngoài agent** | kiểm ở `git commit`, ở lệnh `kit` | chạy với **mọi** agent, kể cả agent không có hook | chỉ bắt được lúc commit, không chặn kịp một lệnh đang chạy |

Quy luật: *cổng nào cần chặn tức thì thì ở hook (B); cổng nào chỉ cần chặn kết quả cuối thì ở git (C).* Cách A hầu như luôn tệ nhất ở thang tháng.

## 6. Cổng "sống" phải chứng minh được
Cách chống im lặng giả: **ca thử vàng** (canary). Với mỗi cổng giữ một đầu vào đã biết đáp án và bắt buộc đúng:
- cho `ctxguard` một nhật ký giả với 200k token → *phải* ra "chặn";
- cho cổng xoá một lệnh `rm -rf` → *phải* ra "hỏi/từ chối".

Test chạy với **từng agent**, không chỉ "chạy không lỗi". Đây là cùng ý với A01d (hook hỏng thì mở), nhưng ngược chiều: vì mặc định mở, nên phải có một chỗ *chủ động* chứng minh cổng còn đóng được khi cần.

## 7. Scale
| Cỡ | Cái gì vỡ |
|---|---|
| 1 agent, vài hook | không gì; cứ viết thẳng |
| 2 agent | mối nối ③ (nhật ký) và ④ (tên công cụ) lộ ra; cần adapter + ca thử |
| nhiều agent / nhiều nhà cung cấp | giao thức hook đổi theo phiên bản; cần một file adapter duy nhất + fixture nhật ký thật của mỗi agent |

## 8. Ví dụ thật: Seriously làm thế này
- **Một nguồn sinh nhiều đích:** `tools/company/settings.py` có hàm `standard_hooks()`: MỘT bảng hook, sinh `settings.json` cho mọi đơn vị. Muốn thêm Codex: thêm một hàm sinh `.codex/hooks.json` từ cùng bảng — cách B, không viết lại script.
- **Adapter transcript đã tách riêng:** `tools/claude/transcript.py` ghi rõ "the ONE adapter over Claude Code session JSONL"; test ở `tools/harness/tests/test_transcript.py` dùng một file mẫu thật. Muốn Codex: thêm parser thứ hai + một file mẫu của Codex.
- **Cổng ngoài agent đã có:** `tools/claude/pre-commit`, `pre-push`, `kit compile` — cách C, chạy với mọi agent.
- **Dispatch đã có đường Codex:** `tools/company/dispatch.py` có `runner = claude|codex` và rơi về Claude khi lỗi — nhưng đường đó chưa từng chạy (máy chưa có `codex`), nên chưa có ca thử nào chứng minh nó sống.
- Tự kiểm: mở `ctxguard.py`, tìm chỗ nó gọi `transcript.last_context(path)`; nếu hàm trả `None` thì cổng làm gì? (Gợi ý: đọc hàm `tool` và tìm nhánh `None`.)

## 9. Bốn nền tảng
- **Mac / Linux:** hook là `sh`/`python3` chạy bình thường; đường dẫn dùng `/`.
- **Windows:** `sh` và `$VAR` không có sẵn; hook cần chạy qua `python` thuần hoặc PowerShell, và đường dẫn có `\`. Một lý do nữa để giữ lõi bằng Python thay vì shell.
- **iOS / Android:** agent coding **không chạy trên điện thoại**; phần liên quan là *cổng build* của game (`kit unity`, `kit compile`, kiểm gói Android/iOS) — thuộc loại C (ngoài agent), nên agent nào gọi cũng được.

## Tóm tắt
Cổng = lõi logic + adapter. Lõi không biết agent nào; bốn mối nối (kích hoạt · JSON vào · nhật ký · tên công cụ) mới dính. Nhật ký là mối nối nguy hiểm nhất vì hỏng mà không kêu. Chống bằng *một nguồn sinh cấu hình* và *ca thử vàng chạy trên từng agent*.

**Giờ bạn biết thêm:** ports & adapters, wire format, fail-open im lặng, canary test, cổng trong agent so với cổng ngoài agent.

**Bài sau (D02):** "xong giả" — cổng kiểm chứng kết quả, không chỉ kiểm hành động.

### Thuật ngữ
- **Adapter**: lớp phiên dịch mỏng giữa lõi và bên ngoài.
- **Wire format**: hình dạng dữ liệu trao đổi (ở đây là JSON qua stdin).
- **Transcript**: nhật ký đầy đủ của một phiên, mỗi dòng một sự kiện.
- **Canary / ca thử vàng**: đầu vào biết trước đáp án, dùng để chứng minh cơ chế còn sống.
- **Fail-open / fail-closed**: lỗi thì cho qua / lỗi thì chặn.
