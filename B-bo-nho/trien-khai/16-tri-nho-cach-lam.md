# 16 — Trí nhớ cách làm

> Chuỗi "Triển khai trí nhớ", bài 16/21. Đọc ~10 phút.
> **Bạn đã biết** ([02](02-ban-do-lua-chon.md), [14](14-ai-quyet-khi-nao-doc.md)–[15](15-cap-nhat-mau-thuan-quen.md)): bốn loại nội dung (làm
> việc / sự kiện / sự thật / cách làm); năm kiểu đọc, có lộ dần; cập nhật và quên.

## 1. Chuyện mở đầu

Agent của nhóm code lần thứ ba quên chạy test trên Android cũ trước khi đổi thư viện — đúng lỗi khiến nhóm bỏ ChartLite. Nó *có* ghi chú "ChartLite
giật trên Android cũ" (một **sự thật**). Cái nó thiếu là **cách làm**: "trước khi thêm thư viện giao diện, chạy bài test hiệu năng trên máy ảo
Android 8".

## 2. Dừng 30 giây

- "ChartLite giật" và "trước khi thêm thư viện thì chạy test X" khác nhau ở đâu? Cái nào agent tự suy ra được từ cái kia?
- Nếu cách làm là một đoạn chữ trong file hướng dẫn, agent có thể bỏ qua. Có cách nào **buộc** nó làm?
- Agent tự viết bài học sau mỗi lần sai — hay hay nguy hiểm?

## 3. Khái niệm

**Trí nhớ cách làm (procedural memory)**: biết *làm thế nào*, không phải biết *cái gì*. Ở agent, nó có nhiều dạng, từ mềm tới cứng:

1. **Lời dặn trong ngữ cảnh**: file hướng dẫn, quy tắc ("luôn chạy test trước khi…"). Agent đọc, *có thể* làm theo.
2. **Quy trình / skill**: một tài liệu từng bước cho một loại việc, nạp khi cần (lộ dần — bài 14). Agent Skills là ví dụ.
3. **Code dùng lại**: hàm/script agent đã viết và chạy thành công, lưu thành thư viện. Voyager (2023, agent chơi Minecraft) lưu mỗi kỹ năng thành
   một đoạn code, tìm lại theo mô tả.
4. **Bài học rút từ thất bại**: Reflexion (2023) cho agent viết lời tự nhận xét sau lần thử hỏng, đọc lại ở lần thử sau. Agent Workflow Memory
   (2024) rút "quy trình" từ các lần làm thành công.
5. **Luật bị thi hành bởi máy**: test, hook, kiểm tra trước khi commit, linter. Agent không *nhớ* — hệ thống *chặn* (câu hỏi 2).

Câu hỏi 1: sự thật → cách làm cần một bước suy luận ("vì ChartLite giật, nên lần sau phải kiểm"). Agent làm được bước này *nếu* có sự thật trên bàn
đúng lúc và nghĩ tới — hai điều kiện hay hụt. Ghi thẳng cách làm bỏ được bước đó.

## 4. Các cách

**A. File hướng dẫn luôn trên bàn.** *Hợp khi:* vài chục quy tắc quan trọng. *Gãy khi:* phình dần; quy tắc mâu thuẫn; agent bỏ qua khi bận.

**B. Thư viện quy trình, nạp theo mô tả.** *Hợp khi:* nhiều loại việc, mỗi loại dài. *Gãy khi:* mô tả mơ hồ → không được nạp; quy trình cũ không ai
sửa (*skill rot*).

**C. Thư viện code dùng lại.** *Hợp khi:* việc lặp có dạng rõ, kiểm được bằng chạy. *Gãy khi:* môi trường đổi (API mới) → code cũ hỏng; trùng lặp
nhiều phiên bản gần giống nhau.

**D. Agent tự rút bài học.** *Hợp khi:* có tín hiệu thành công/thất bại rõ (test đỏ/xanh). *Gãy khi:* rút sai bài học từ một lần ("lần trước lỗi khi
dùng X → không bao giờ dùng X"); bài học tích tụ không ai duyệt (câu hỏi 3: hay *và* nguy hiểm — cần người duyệt hoặc cần đo trước khi giữ).

**E. Biến cách làm thành rào chắn.** Cách làm quan trọng → viết thành test/hook. *Hợp khi:* điều kiện kiểm được bằng máy. *Gãy khi:* điều kiện
không kiểm được (gu thẩm mỹ, "hỏi khách lịch sự"); rào chắn quá nhiều làm chậm mọi việc.

**F. Tối ưu lời nhắc tự động.** Chạy nhiều phiên bản lời dặn trên bộ câu thử, giữ bản điểm cao (ví dụ DSPy). *Hợp khi:* có bộ đo tốt (bài 19).
*Gãy khi:* bộ đo nhỏ → tối ưu theo đề.

## 5. Bảng một lần nhìn

| Cách | Độ chắc agent làm theo | Giá viết | Giá giữ | Gãy khi |
|---|---|---|---|---|
| A. File hướng dẫn | thấp–vừa | thấp | phình | bận thì bỏ qua |
| B. Thư viện quy trình | vừa | vừa | skill rot | mô tả mơ hồ |
| C. Code dùng lại | cao (chạy được) | vừa | môi trường đổi | trùng lặp |
| D. Tự rút bài học | thấp–vừa | 0 (tự động) | cần duyệt | bài học sai |
| E. Rào chắn máy | **cao nhất** | vừa–cao | thấp | không kiểm được |
| F. Tối ưu lời nhắc | vừa | cao (bộ đo) | chạy lại | tối ưu theo đề |

**Quy luật:** càng **quan trọng** và càng **kiểm được bằng máy**, càng nên chuyển từ "lời dặn" sang "rào chắn". Lời dặn hợp với thứ cần phán đoán.

## 6. Ba kịch bản

- **Nhóm code:** A ngắn + E cho điều quan trọng (test hiệu năng Android chạy tự động khi thêm thư viện) + D có người duyệt.
- **Cửa hàng Lá:** B (quy trình xử lý khiếu nại, đổi trả) — viết bởi người, đổi khi chính sách đổi; E cho "không bao giờ hứa hoàn tiền khi chưa
  kiểm đơn" (kiểm bằng code trước khi gửi tin).
- **Mai:** ít trí nhớ cách làm; vài thói quen ("nhắc uống nước lúc 3 giờ") là luật theo sự kiện (bài 14), không cần thư viện.

## 7. Scale

- **Nhỏ:** A.
- **Vừa:** A + B; bắt đầu E cho lỗi lặp lại.
- **Lớn:** B phình thành hàng trăm skill — chọn skill thành bài toán *tìm* (bài 09–11); skill mâu thuẫn nhau; cần chủ sở hữu từng skill. Cái vỡ
  là **ai giữ cho cách làm còn đúng**.

## 8. Bốn nền tảng

- **Windows / Mac:** script dùng lại phải viết được cho cả hai shell (PowerShell vs zsh) hoặc dùng ngôn ngữ chung (Python); đường dẫn `\` vs `/`.
- **iOS / Android:** app không cho agent chạy code tuỳ ý trên máy → C chỉ làm được ở phía máy chủ; trên máy, cách làm thường là luật có sẵn trong
  app (E) hoặc lời dặn ngắn (A).

## 9. Tóm tắt

Trí nhớ cách làm đi từ mềm (lời dặn) tới cứng (rào chắn máy): file hướng dẫn, thư viện quy trình, code dùng lại, bài học tự rút, rào chắn, tối ưu lời
nhắc. Điều quan trọng và kiểm được thì đưa về rào chắn; bài học tự rút cần duyệt hoặc cần đo.

**Thuật ngữ:** procedural memory · instruction file · skill library · Voyager · Reflexion · workflow memory · guardrail / hook · skill rot · prompt optimization / DSPy.

**Giờ bạn biết thêm:** loại trí nhớ thứ tư — và vì sao nó thường nên sống ở ngoài model, dưới dạng máy kiểm được.

**Bài sau:** [17 — Trí nhớ trong trọng số](17-tri-nho-trong-trong-so.md).
