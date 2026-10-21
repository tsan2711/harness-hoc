# 03 — Nhét hết vào ngữ cảnh

> Chuỗi "Triển khai trí nhớ", bài 3/21. Đọc ~8 phút.
> **Bạn đã biết** ([01](01-model-khong-nho.md)–[02](02-ban-do-lua-chon.md)): ngữ cảnh = mặt bàn có giới hạn; token = tiền + chỗ; bốn loại
> nội dung; ba trục bao lâu / chất liệu / ai điều khiển.

## 1. Chuyện mở đầu

Nhóm code nghe tin model mới có ngữ cảnh 1 triệu token. "Tuyệt — khỏi làm trí nhớ, cứ nhét cả kho tài liệu (600 nghìn token) vào mỗi lần."
Tuần đầu chạy tốt. Rồi hoá đơn tháng về: mỗi câu hỏi đọc lại 600 nghìn token. Và có một lần agent vẫn đề xuất ChartLite — dòng "bỏ
ChartLite" nằm đúng ở giữa đống tài liệu.

## 2. Dừng 30 giây

- Ngữ cảnh 1 triệu token thì model có "đọc kỹ" từng dòng trong đó như nhau không?
- Nếu 95 % nội dung giống hệt nhau giữa các câu hỏi, có cách nào khỏi trả tiền đọc lại phần đó?
- Kịch bản nào trong ba (Mai, cửa hàng Lá, nhóm code) mà "nhét hết" có thể là lời giải đúng luôn?

## 3. Khái niệm

**Ngữ cảnh dài (long context).** Các model lớn năm 2026 nhận từ hàng trăm nghìn tới khoảng một triệu token mỗi lần. Đủ chứa một cuốn
sách dày hoặc một kho code vừa.

**"Lạc ở giữa" (lost in the middle).** Nghiên cứu của Liu và cộng sự (2023) cho thấy model dùng thông tin ở **đầu** và **cuối** ngữ cảnh
tốt hơn thông tin nằm **giữa**. Các báo cáo sau (ví dụ "context rot" của Chroma, 2025) thấy chất lượng giảm dần khi ngữ cảnh dài ra, kể
cả với việc đơn giản. Model mới đỡ hơn, nhưng xu hướng vẫn còn: **vừa vặn trên bàn ≠ được dùng tốt** (câu hỏi 1).

**Cache prompt (prompt caching).** Nếu phần đầu của ngữ cảnh giống hệt lần trước, nhà cung cấp có thể giữ sẵn kết quả xử lý phần đó và
tính giá rẻ hơn nhiều cho lần đọc lại (thường còn khoảng một phần mười giá), trong một khoảng thời gian (vài phút đến khoảng một giờ,
tuỳ nhà cung cấp và tuỳ chọn). Điều kiện: phần giống nhau phải nằm **ở đầu** và **giống từng ký tự** (câu hỏi 2).

## 4. Các cách nhét

**A. Nhét nguyên văn mọi thứ.** *Hợp khi:* tổng nội dung nhỏ hơn nhiều so với mặt bàn, ít câu hỏi mỗi ngày. *Gãy khi:* nội dung lớn dần;
mỗi câu đắt và chậm; chi tiết ở giữa bị bỏ sót.

**B. Nhét nguyên văn + cache.** Đặt phần ổn định (tài liệu, hồ sơ) ở đầu, phần thay đổi (câu hỏi mới) ở cuối. *Hợp khi:* nhiều câu hỏi
liên tiếp trên cùng một khối nội dung (một phiên làm việc). *Gãy khi:* nội dung đổi thường xuyên (mỗi lần đổi là mất cache); câu hỏi thưa
(cache hết hạn giữa hai câu).

**C. Nhét có chọn lọc bằng tay.** Người dùng/nhà phát triển chọn sẵn vài file "luôn đưa vào" (một file hướng dẫn dự án, một hồ sơ). Đây là
cách C ở bài 01, ở dạng tổng quát. *Hợp khi:* vài thứ quan trọng, ổn định. *Gãy khi:* danh sách "luôn đưa" phình dần — ai cũng muốn thêm
điều của mình, không ai dám xoá.

**D. Nhét theo thứ tự ưu tiên.** Điều quan trọng nhất đặt ở **đầu hoặc cuối**; nhắc lại điều then chốt ngay trước câu hỏi. *Hợp khi:* phải
nhét dài. *Gãy khi:* ai quyết "điều quan trọng nhất"? — đó chính là bài toán chọn lọc, dẫn sang bài 04 và phần 4.

## 5. Bảng một lần nhìn

| Cách | Công | Giá mỗi câu | Chất lượng khi dài | Gãy khi |
|---|---|---|---|---|
| A. Nguyên văn | 0 | cao, tăng dần | giảm (lạc ở giữa) | nội dung lớn |
| B. + cache | thấp | thấp nếu trúng cache | như A | nội dung đổi / câu thưa |
| C. Chọn tay | vừa | thấp | tốt | danh sách phình |
| D. Sắp ưu tiên | vừa | như A | khá hơn A | ai chọn ưu tiên |

**Quy luật:** nhét hết là lời giải đúng khi **tổng nội dung nhỏ và ổn định**; ngoài vùng đó, giá và chất lượng đều kéo bạn sang chọn lọc.

Câu hỏi 3: **cửa hàng Lá** với một khách cụ thể — lịch sử đơn của *một* khách thường chỉ vài nghìn token → nhét hết lịch sử của khách đó
(lấy từ hệ thống đơn hàng) là lời giải hợp lý, không cần kho trí nhớ riêng. Mai sau vài năm và nhóm code thì không.

## 6. Scale

- **Nhỏ** (< ~10 % mặt bàn): A hoặc B. Đừng xây gì thêm.
- **Vừa** (gần đầy bàn): B + C; bắt đầu thấy "lạc ở giữa".
- **Lớn** (lớn hơn bàn): không nhét được nữa → bắt buộc tóm (bài 04) hoặc tìm (phần 4). Cái vỡ trước là **giá và độ trễ**, rồi mới tới chỗ.

## 7. Bốn nền tảng

- **Windows / Mac** dùng model trên máy chủ: ngữ cảnh dài + cache tuỳ nhà cung cấp. Model chạy trên máy (Ollama, LM Studio…) nhận ngữ
  cảnh dài thì **tốn RAM/VRAM tăng theo độ dài** — máy 16 GB sẽ chậm hẳn hoặc không chạy nổi ngữ cảnh rất dài.
- **iOS / Android** với model trên máy: mặt bàn chỉ vài nghìn token → "nhét hết" gần như không bao giờ là lời giải; mọi thứ phải chọn lọc.
  Gọi model trên máy chủ từ app thì gửi ngữ cảnh dài qua mạng di động cũng tốn thời gian và dữ liệu.

## 8. Tóm tắt

Nhét hết vào ngữ cảnh là cách không cần kho — đúng khi nội dung nhỏ và ổn định, rẻ hơn nhờ cache khi phần đầu không đổi; sai khi nội dung
lớn dần, vì giá, độ trễ và "lạc ở giữa".

**Thuật ngữ:** long context · lost in the middle · context rot · prompt caching · static prefix (phần đầu cố định).

**Giờ bạn biết thêm:** khi nào *không cần* hệ thống trí nhớ nào cả, và dấu hiệu nào cho thấy bạn đã ra khỏi vùng đó.

**Bài sau:** [04 — Tóm tắt và nén](04-tom-tat-va-nen.md).
