# 05 — File ghi chú

> Chuỗi "Triển khai trí nhớ", bài 5/21. Đọc ~9 phút.
> **Bạn đã biết** ([02](02-ban-do-lua-chon.md)–[04](04-tom-tat-va-nen.md)): bốn loại nội dung; ba trục; nhét hết đúng khi nhỏ; tóm là mất có
> chủ ý, an toàn khi bản gốc còn và điều quan trọng được ghi ra ngoài.

## 1. Chuyện mở đầu

Nhóm code tạo một file `HUONG-DAN.md` ở gốc dự án; công cụ agent tự đọc file này lúc mở phiên. Lan viết vào: "Không dùng ChartLite (giật
trên Android cũ)." Từ hôm đó agent không đề xuất ChartLite nữa. Ba tháng sau file dài 900 dòng: quy ước đặt tên, lệnh chạy test, ghi chú
của từng người, vài dòng đã sai từ lâu. Agent bắt đầu làm theo một quy ước mà cả nhóm đã bỏ.

## 2. Dừng 30 giây

- Vì sao một file chữ thường lại là "trí nhớ" tốt đến thế cho nhóm này?
- Ai nên được sửa file: người, agent, hay cả hai?
- File 900 dòng — giờ nó giống bài toán của bài nào trước đây?

## 3. Khái niệm

**File ghi chú** là file chữ thường (thường là Markdown — chữ có vài ký hiệu như `#` cho tiêu đề) nằm trên đĩa. Hai kiểu dùng:
- **Luôn đọc** (bài 03, cách C): công cụ tự đặt file lên bàn đầu mỗi phiên. Ví dụ: file hướng dẫn dự án của các agent viết code (nhiều
  công cụ có quy ước tên riêng cho file này), "custom instructions" của app chat.
- **Đọc khi cần**: một **thư mục** nhiều file; agent liệt kê, mở file liên quan. Anthropic có "memory tool" (2025): agent được các lệnh xem
  / tạo / sửa / xoá file trong một thư mục trí nhớ, thư mục nằm ở hạ tầng của bạn.

Câu hỏi 1, vì sao tốt: **người đọc được, người sửa được**, theo dõi thay đổi được (đặt trong git — hệ thống lưu lịch sử mọi lần sửa file),
không cần công cụ đặc biệt, không phụ thuộc nhà cung cấp, chuyển sang công cụ khác vẫn dùng được.

Câu hỏi 3: file 900 dòng luôn-đọc chính là "nhét hết" (bài 03) — và gãy y như vậy.

## 4. Các cách tổ chức

**A. Một file luôn đọc.** *Hợp khi:* vài chục quy tắc ổn định. *Gãy khi:* phình; dòng sai không ai xoá; mọi phiên trả token cho cả file.

**B. Một file ngắn luôn đọc + nhiều file đọc khi cần.** File ngắn là *mục lục*: "quyết định kỹ thuật ở `quyet-dinh.md`, quy ước test ở
`test.md`". *Hợp khi:* nhiều chủ đề. *Gãy khi:* agent không mở đúng file (mục lục mơ hồ), hoặc mục lục lỗi thời.

**C. File theo phạm vi.** File chung cho cả dự án + file riêng cho từng thư mục con, chỉ đọc khi làm trong thư mục đó; file của người dùng
(sở thích cá nhân) tách khỏi file của dự án. *Hợp khi:* dự án lớn, nhiều người. *Gãy khi:* quy tắc mâu thuẫn giữa các tầng — tầng nào thắng?

**D. Agent tự ghi** (câu hỏi 2). Agent có quyền ghi vào thư mục trí nhớ khi học được điều gì ("lệnh test đúng là X"). *Hợp khi:* agent làm
việc dài, một mình. *Gãy khi:* agent ghi rác, ghi điều sai một cách tự tin, ghi trùng — không ai duyệt. Hay dùng kèm: người duyệt định kỳ,
hoặc agent chỉ được ghi vào thư mục riêng, file chính do người giữ.

**E. Một file một sự thật ("ghi chú nguyên tử").** Mỗi điều một file ngắn, có tiêu đề rõ; một file mục lục liệt kê một dòng mỗi file. Gần với
phương pháp ghi chú Zettelkasten (một ý một thẻ, các thẻ trỏ nhau); hệ A-Mem (NeurIPS 2025) làm bản tự động của ý này. *Hợp khi:* sự thật
cần sửa/xoá riêng lẻ. *Gãy khi:* hàng nghìn file → cần tìm kiếm thay vì mục lục (phần 4).

## 5. Bảng một lần nhìn

| Cách | Token mỗi phiên | Dễ sửa | Ai ghi | Gãy khi |
|---|---|---|---|---|
| A. Một file luôn đọc | tăng theo file | ✓ | người | phình, dòng sai |
| B. Mục lục + file khi cần | thấp | ✓ | người | mục lục mơ hồ |
| C. Theo phạm vi | thấp | ✓ | người | mâu thuẫn tầng |
| D. Agent tự ghi | tuỳ | ✓ | agent | rác, sai tự tin |
| E. Một file một sự thật | thấp | ✓✓ | người/agent | quá nhiều file |

**Quy luật:** file ghi chú là kho **minh bạch nhất** — mạnh nhờ người đọc/sửa được; gãy khi không ai dọn. Mọi cách tổ chức là cách đẩy
lùi lúc phải cần tìm kiếm.

## 6. Ba kịch bản

- **Nhóm code:** B + C là điểm xuất phát rất hợp; git cho lịch sử "ai sửa gì, khi nào".
- **Mai:** một file hồ sơ (E nhỏ) — Mai có thể mở ra xem "trợ lý biết gì về mình" và sửa. Minh bạch này là một **tính năng** với người dùng.
- **Cửa hàng Lá:** một file mỗi khách cho hàng nghìn khách thì vụng — cần tìm theo khách, theo đơn, nhanh → bảng có cấu trúc (bài 06).

## 7. Scale

- **Nhỏ:** A.
- **Vừa:** B/C, có lịch dọn (ví dụ mỗi tháng xoá dòng đã sai).
- **Lớn** (nghìn file, nhiều người ghi): mục lục không đủ → thêm tìm kiếm trên các file (phần 4); file vẫn là **nguồn**, chỉ mục chỉ là
  bản sao để tìm nhanh. Cái vỡ là **độ đúng** — dòng sai sống lâu vì không ai biết nó sai.

## 8. Bốn nền tảng

- **Windows / Mac:** file nằm thẳng trên ổ đĩa; chú ý xuống dòng khác nhau (Windows `\r\n`, Mac `\n`) và đường dẫn (`\` vs `/`) khi
  script đọc file; mã hoá chữ nên là UTF-8 cho tiếng Việt.
- **iOS / Android:** app không có "thư mục dự án" người dùng mở được; file nằm trong vùng riêng của app (sandbox). Cùng ý vẫn dùng được:
  lưu ghi chú dạng chữ trong app, có màn hình "trợ lý nhớ gì về bạn" cho người dùng xem/sửa/xoá. Đồng bộ giữa máy qua iCloud / Google Drive
  hoặc máy chủ của app.

## 9. Tóm tắt

File ghi chú — luôn đọc hoặc đọc khi cần — là kho đơn giản, minh bạch, sửa được, đi cùng git. Tổ chức bằng mục lục, phạm vi, hoặc một
file một sự thật; quyết định lớn là **ai được ghi** và **ai dọn**.

**Thuật ngữ:** Markdown · instruction file (file hướng dẫn) · memory directory (thư mục trí nhớ) · memory tool · atomic note (ghi chú nguyên tử) · Zettelkasten · scope (phạm vi).

**Giờ bạn biết thêm:** kho trí nhớ ngoài đầu tiên và minh bạch nhất — và dấu hiệu khi nó cần thêm cấu trúc hoặc tìm kiếm.

**Bài sau:** [06 — Bảng có cấu trúc](06-bang-co-cau-truc.md).
