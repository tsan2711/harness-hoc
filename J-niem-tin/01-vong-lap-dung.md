# Bài J01 — Vì sao vòng lặp quan trọng, và vòng nào mới là vòng đúng

> **Bạn đã biết** (J00): niềm tin = bằng chứng máy tạo ra. Ở đây: *vòng lặp* là chỗ bằng chứng đó được tạo ra lặp đi lặp lại.

## 1. Câu chuyện
Lan bảo trợ lý: "Làm 3 việc, đừng dừng." Trợ lý làm xong việc 1, 2, rồi viết "đã xong cả 3". Việc 3 thực ra test đỏ. Lan thêm vào lời dặn: "chỉ dừng khi test xanh". Hôm sau trợ lý dừng giữa chừng vì ngữ cảnh đầy — lời dặn biến mất cùng phiên.

## 2. Dừng 30 giây
- Câu "đừng dừng" nằm ở đâu: trong *model* hay trong *chương trình bao quanh model*? Cái nào sống sót khi phiên chết?
- Ai nên quyết định "việc này xong chưa": agent làm việc, hay một lệnh có exit code?
- Nếu thử-sửa-thử mãi mà không tiến, điều kiện thoát nên là "đủ N vòng" hay "điểm đạt / không tiến nữa"?

## 3. Cơ chế
**Vòng lặp agent** (bên trong một phiên): model → gọi công cụ → nhận kết quả → model. Nó quyết định *làm gì tiếp*, nhưng cũng tự quyết *khi nào dừng* — chính là điểm yếu: nó vừa làm bài vừa chấm bài.

**Vòng ngoài (outer loop)**: một chương trình thường (không phải model) đứng trên, làm: lấy việc từ hàng đợi → giao agent → chạy **lệnh kiểm** → chỉ đánh DONE nếu exit 0 → nếu không, thử lại / báo kẹt. Tốn 0 token khi chờ vì chỉ là script.

Vì sao quan trọng — ba lý do, mỗi cái ứng một lỗi thật:
1. **Tách người làm khỏi người chấm.** Agent tự khai "xong" là thiên kiến (ai cũng muốn xong). Lệnh kiểm không muốn gì cả.
2. **Trạng thái nằm ngoài ngữ cảnh.** Hàng đợi, sổ ghi (ledger), file bàn giao nằm trên đĩa → phiên chết, vòng ngoài dựng phiên mới đọc tiếp. Lời dặn trong prompt thì mất.
3. **Có điều kiện thoát khách quan.** Vòng không điều kiện thoát = đốt tiền; vòng chỉ giới hạn số lần = dừng sớm khi sắp đạt hoặc chạy hết số lần dù đã vô vọng.

### Hill-climb: vòng lặp để *cải thiện*, không chỉ để *hoàn thành*
Tên gọi từ tối ưu hoá (leo đồi): mỗi vòng **giả thuyết → đổi đúng 1 thứ → đo → giữ nếu tốt hơn, hoàn tác nếu tệ hơn → ghi 1 dòng sổ**. Đổi 1 thứ/vòng để biết thứ nào gây ra thay đổi (giống git bisect).
Điều kiện thoát: **điểm đạt ngưỡng** hoặc **stuck** (N vòng liền không tiến). Giới hạn số vòng chỉ là trần an toàn, không phải mục tiêu.

```python
# mini hill-climb: chạy được, ~15 dòng
import random
random.seed(1)
score = lambda x: -(x - 7) ** 2          # đo: càng gần 7 càng tốt
best, bad_streak, ledger = 0, 0, []
for step in range(50):                    # trần an toàn
    cand = best + random.choice([-1, 1])  # đổi 1 thứ
    if score(cand) > score(best):         # đo → giữ
        best, bad_streak = cand, 0; ledger.append(("keep", cand))
    else:                                 # hoàn tác
        bad_streak += 1; ledger.append(("revert", cand))
    if score(best) >= 0 or bad_streak >= 8: break   # đạt hoặc stuck
print(best, len(ledger))
```
Hãy sửa `bad_streak >= 8` thành `>= 2` rồi chạy lại: thoát sớm khi *chưa* đạt → đó là "stuck" bắt nhầm. Đây chính là chỗ cần chỉnh ngưỡng bằng dữ liệu.

## 4. Ba cách dựng "việc chạy nhiều giờ", so sánh
| Cách | Mô tả | Ưu | Điểm gãy |
|---|---|---|---|
| **A. Dặn trong prompt** "đừng dừng tới khi xong" | không xây gì | rẻ | model tự quyết dừng; phiên chết là mất |
| **B. Hook chặn dừng trong một phiên** | hook từ chối khi agent định dừng, bắt làm tiếp | chặn được dừng sớm | danh sách việc do agent tự chấm; ngữ cảnh vẫn đầy; một phiên = một điểm hỏng |
| **C. Vòng ngoài + lệnh kiểm + sổ ghi** | script điều phối nhiều phiên ngắn | DONE chỉ khi máy kiểm đạt; sống sót qua phiên chết; đo được | phải viết lệnh kiểm cho từng việc; việc "cảm tính" không vào được |

Quy luật: *B là miếng vá cho A; C mới là kiến trúc. Dùng B khi phải ngắn hạn, nhưng đừng mở rộng nó.*

## 5. Scale
- **Việc 20 phút:** A đủ.
- **Vài giờ, 1 phiên:** B giúp, nhưng danh sách việc do agent tự chấm → có "mảng xong giả".
- **Qua đêm / nhiều lane song song:** chỉ C. Thêm: mỗi lane một **worktree** (bản làm việc git riêng) để không giẫm chân; khoá tài nguyên đắt (như Unity Editor) để hai việc không giành nhau.

## 6. Ví dụ thật: Seriously làm thế này
Plan P3/P6: `kit marathon` (kiểu B: hook Stop chặn dừng trong một phiên) bị xác định là **vá tạm**; vòng đúng là `tools/night/conductor.py` (kiểu C: vòng ngoài 0 token, DONE chỉ khi check máy pass, nối HANDOFF, `stuck.py`, worktree, khoá Unity). chủ dự án chốt 2026-11-14: "chuyển việc dài sang conductor, dừng mở rộng marathon". `tools/night/hillclimb.py` là loại task hill-climb; kịch bản kiểm: `fake_claude` chạy 3 vòng (1 tốt, 1 xấu, 1 hoà) → sổ phải đúng 3 dòng, vòng xấu bị revert. Mở `conductor.py` tìm chỗ nó quyết định DONE: có phải nó đọc lời agent, hay chạy lệnh?

## 7. Bốn nền tảng
Vòng ngoài là script nên giống nhau trên cả bốn; khác ở *lịch chạy* (Mac: `launchd`; Windows: Task Scheduler; Linux CI: cron/systemd) và *thứ phải khoá* (Windows/Mac chia sẻ một Editor; Android/iOS cần thiết bị hoặc simulator — tài nguyên khan hiếm nhất, nên khoá).

**Giờ bạn biết thêm:** outer loop, DONE bằng lệnh kiểm, hill-climb, stuck, worktree.
**Bài sau:** J02 — đo trước khi sửa.
