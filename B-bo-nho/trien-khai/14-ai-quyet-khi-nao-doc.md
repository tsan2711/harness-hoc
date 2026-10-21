# 14 — Ai quyết khi nào đọc

> Chuỗi "Triển khai trí nhớ", bài 14/21. Đọc ~9 phút.
> **Bạn đã biết** ([03](03-nhet-het-vao-ngu-canh.md), [13](13-ai-quyet-ghi-gi.md)): bàn làm việc có hạn, đặt quá nhiều thì model đọc kém (lost
> in the middle, context rot); bốn người ghi; các cách tìm (09–12).

## 1. Chuyện mở đầu

Trợ lý của Mai có 600 sự thật. Ba đội thử ba kiểu đọc:
- Đội 1 đặt **cả 600** lên bàn mỗi lượt. Tốn token, và khi Mai hỏi "tối nay nấu gì", trợ lý nhắc cả chuyện Mai từng ghét một bộ phim.
- Đội 2 **tự tìm** top 5 theo câu Mai vừa gõ. Mai gõ "ok làm đi" → top 5 toàn rác, vì câu này không có nội dung gì để tìm.
- Đội 3 cho trợ lý **công cụ** `tìm_nhớ`. Mai hỏi "món gì cho bé?" — trợ lý tự tin gợi ý tôm, không hề gọi `tìm_nhớ`. Bé dị ứng tôm.

## 2. Dừng 30 giây

- Có thông tin nào *luôn luôn* phải nằm trên bàn, bất kể câu hỏi là gì?
- Tìm theo câu vừa gõ hỏng khi câu đó ngắn. Nên tìm theo cái gì thay vào?
- Agent không biết là mình không biết. Làm sao để nó vẫn đọc đúng lúc?

## 3. Năm kiểu đọc

**A. Luôn trên bàn (ghim).** Một khối nhỏ được đặt vào mọi lượt: hồ sơ ngắn, luật quan trọng, dị ứng (câu hỏi 1). Letta gọi là *core memory*;
ChatGPT đặt "saved memories" vào ngữ cảnh; các file hướng dẫn của agent viết code (CLAUDE.md, AGENTS.md, rules của Cursor) được nạp đầu phiên.
*Hợp khi:* ít, quan trọng, áp dụng rộng. *Gãy khi:* khối phình dần (ai cũng muốn ghim thêm) → quay lại vấn đề của đội 1. Dùng chung với prompt
caching thì rẻ hơn, vì khối này ít đổi.

**B. Tìm tự động mỗi lượt.** Code chạy tìm trước khi gọi model, đặt top k lên bàn. Không phụ thuộc agent nhớ gọi. *Hợp khi:* câu hỏi có nội dung.
*Gãy khi:* câu ngắn/mơ hồ (đội 2); đặt rác lên bàn khi không có gì hợp → cần ngưỡng im lặng (bài 10). Sửa câu hỏi 2: tìm theo **vài lượt gần
nhất** hoặc **chủ đề đang làm**, không chỉ câu cuối.

**C. Agent gọi công cụ khi cần.** Bàn sạch, chỉ đọc khi agent thấy cần. Claude (app) có công cụ tìm chat cũ; memory tool của Anthropic để agent tự
`view` thư mục `/memories`. *Hợp khi:* agent mạnh, việc dài. *Gãy khi:* agent không biết mình thiếu (đội 3, câu hỏi 3); gọi quá nhiều tốn vòng.

**D. Theo sự kiện (hook / luật).** Code đọc khi **điều kiện** xảy ra, không theo câu hỏi: mở file `payment.ts` → đặt ghi chú về `payment.ts` lên
bàn; nhắc tới món ăn → đặt "dị ứng" lên bàn; đầu phiên → đặt "việc đang dở". *Hợp khi:* biết trước điều kiện quan trọng. Tất định. *Gãy khi:*
điều kiện không lường trước; luật nhiều lên khó quản.

**E. Lộ dần (progressive disclosure).** Bàn chỉ có **mục lục** (tên + một dòng mô tả mỗi mục); agent thấy mục hợp thì mở. Agent Skills dùng đúng cách
này: chỉ tên và mô tả của mỗi skill nằm trên bàn, nội dung đầy đủ được nạp khi cần. *Hợp khi:* nhiều mục, mỗi mục dài. *Gãy khi:* mô tả một dòng
viết mơ hồ → agent không mở đúng mục.

## 4. Bảng một lần nhìn

| Kiểu | Ai quyết | Token mỗi lượt | Bỏ sót khi | Thừa khi |
|---|---|---|---|---|
| A. Ghim | người thiết kế | cố định | điều không ghim | khối phình |
| B. Tìm tự động | code | k đoạn | câu ngắn, tìm kém | không ngưỡng |
| C. Agent gọi | agent | 0 đến nhiều | agent không biết mình thiếu | gọi thừa |
| D. Theo sự kiện | luật | theo luật | điều kiện lạ | luật chồng chéo |
| E. Lộ dần | agent, qua mục lục | mục lục + mục mở | mô tả mơ hồ | mục lục quá dài |

**Quy luật:** điều **sai thì nguy hiểm** không được phụ thuộc agent nhớ gọi — ghim (A) hoặc theo sự kiện (D). Điều **nhiều mà ít khi cần** để
cho tìm (B) hoặc lộ dần (E). Phần lớn hệ thống thật trộn A + một trong B/C/E.

## 5. Ba kịch bản

- **Mai:** A cho dị ứng + hồ sơ ngắn; D cho "nhắc món ăn → dị ứng"; B/C cho phần còn lại.
- **Cửa hàng Lá:** A = chính sách cửa hàng ngắn; D = "khách nêu mã đơn → tra đơn đó" (bài 06); B cho câu hỏi chính sách dài; C ít dùng vì cần
  nhanh và đoán trước được.
- **Nhóm code:** A = file hướng dẫn dự án ngắn; D = "mở/sửa file X → ghi chú của X"; E cho tài liệu dài và skill; C cho "lỗi này gặp chưa?".

## 6. Scale

- **Nhỏ:** A là đủ (bài 03).
- **Vừa:** A + B hoặc A + C.
- **Lớn:** khối ghim phình là vấn đề số một — cần ngân sách (ví dụ "tối đa N dòng") và người/agent dọn định kỳ; mục lục ở E cũng cần ngân sách.
  Cái vỡ là **độ chật của bàn**, không phải chỗ chứa.

## 7. Bốn nền tảng

- **Windows / Mac:** như nhau; hook theo sự kiện gắn vào công cụ đang dùng (trình soạn code, CLI của agent).
- **iOS / Android:** model trên máy có cửa sổ ngữ cảnh nhỏ (vài nghìn token) → A phải rất ngắn, B với k nhỏ; sự kiện của hệ điều hành (vị trí,
  giờ, app đang mở) là nguồn điều kiện cho D — nhưng phải xin quyền và nói rõ với người dùng.

## 8. Tóm tắt

Năm kiểu đọc: ghim, tìm tự động, agent tự gọi, theo sự kiện, lộ dần. Thứ nguy hiểm khi thiếu thì ghim hoặc gắn sự kiện; thứ nhiều thì tìm hoặc
lộ dần; và luôn giữ ngân sách cho bàn làm việc.

**Thuật ngữ:** read policy (chính sách đọc) · pinned / core memory · auto-retrieval · tool-based retrieval · hook / trigger · progressive disclosure · context budget.

**Giờ bạn biết thêm:** bên đọc của vòng trí nhớ — trí nhớ có cũng vô ích nếu không lên bàn đúng lúc.

**Bài sau:** [15 — Cập nhật, mâu thuẫn, quên](15-cap-nhat-mau-thuan-quen.md).
