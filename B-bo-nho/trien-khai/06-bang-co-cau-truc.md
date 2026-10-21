# 06 — Bảng có cấu trúc

> Chuỗi "Triển khai trí nhớ", bài 6/21. Đọc ~8 phút.
> **Bạn đã biết** ([05](05-file-ghi-chu.md)): file ghi chú minh bạch, sửa được; gãy khi hàng nghìn file hoặc không ai dọn; bốn loại nội dung (bài 02).

## 1. Chuyện mở đầu

Cửa hàng Lá thử cách "một file ghi chú mỗi khách". Một khách hỏi "đơn của em tới đâu rồi?". Chatbot mở file của khách, đọc 40 dòng chữ
tự do, thấy "đơn #123 đang giao" — dòng viết từ thứ Hai. Thật ra đơn đã giao xong hôm qua; hệ thống đơn hàng biết, file ghi chú thì không.

## 2. Dừng 30 giây

- Câu "đơn của em tới đâu rồi?" có cần *tìm* không, hay chỉ cần *tra*?
- Dữ liệu nào của cửa hàng đã có sẵn ở dạng bảng trước khi có chatbot?
- "Mai dị ứng tôm" có hợp để làm một cột trong bảng không? Còn "Mai kể chuyện đi Đà Lạt"?

## 3. Khái niệm

**Bảng có cấu trúc** là dữ liệu có **cột cố định**: mỗi dòng một bản ghi, mỗi cột một loại thông tin. Như bảng tính Excel, nhưng nằm
trong một **cơ sở dữ liệu** (như SQLite, PostgreSQL) có **khoá** (mã duy nhất mỗi dòng, ví dụ mã khách) và có thể **tra** bằng ngôn ngữ
truy vấn SQL: "lấy mọi đơn của khách K, mới nhất trước".

**Tra (lookup) ≠ tìm (search).** Tra là biết chính xác mình cần gì và hỏi bằng khoá — kết quả **đúng tuyệt đối**, nhanh tới mili giây.
Tìm là đoán cái nào *liên quan* (phần 4). Câu hỏi 1: tình trạng đơn là việc **tra**.

**Nguồn sự thật (source of truth).** Nơi được coi là đúng khi hai nơi lệch nhau. Đơn hàng có nguồn sự thật là hệ thống đơn hàng; mọi bản
chép khác (file ghi chú của chatbot) sẽ lệch. Câu hỏi 2: đơn, khách, sản phẩm, thanh toán — đã có bảng từ trước.

**Hồ sơ (profile).** Một dòng (hoặc vài dòng khoá–giá trị) cho mỗi người dùng: `tên`, `ngôn ngữ`, `dị_ứng`, `kênh_liên_lạc_ưa_thích`.

## 4. Các cách

**A. Đọc thẳng nguồn sự thật đã có.** Không lưu gì mới: khi khách hỏi, gọi công cụ `tra_đơn(mã_khách)` lấy từ hệ thống đơn hàng, đặt kết
quả lên bàn. *Hợp khi:* dữ liệu đã nằm ở một hệ thống khác. *Gãy khi:* hệ thống đó chậm hoặc không có cách tra (không có API).

**B. Hồ sơ cột cố định.** Thiết kế trước các cột cần nhớ. *Hợp khi:* biết trước loại sự thật (dị ứng, ngôn ngữ, kích cỡ áo…). *Gãy khi:*
gặp sự thật không có cột ("Mai sợ độ cao") → hoặc bỏ, hoặc phải thêm cột.

**C. Hồ sơ khoá–giá trị tự do.** Bảng ba cột `người_dùng · khoá · giá_trị` (+ `cập_nhật_lúc`, `nguồn`). Thêm loại sự thật mới không cần sửa
cấu trúc. *Hợp khi:* sự thật đa dạng. *Gãy khi:* cùng một ý mang nhiều khoá (`di_ung`, `dị ứng`, `allergy`) → cần danh sách khoá chuẩn.

**D. Bảng sự kiện (nhật ký).** Mỗi dòng một chuyện: `lúc · ai · loại · nội_dung` ("21/10 · khách K · khiếu nại · giao trễ"). Tra theo thời
gian, theo người, theo loại. *Hợp khi:* sự kiện nhiều, hỏi theo thời gian. *Gãy khi:* cần tìm theo *nội dung* tự do ("lần nào khách than
về bao bì?") → cần tìm kiếm (phần 4) trên cột `nội_dung`.

**E. Bảng + cột chữ tự do.** Kết hợp: cột cấu trúc để tra, một cột ghi chú tự do để model đọc. *Hợp khi:* hầu hết hệ thống thật. *Gãy khi:*
thông tin quan trọng trôi vào cột tự do và không còn tra được.

## 5. Bảng một lần nhìn

| Cách | Đúng tuyệt đối | Linh hoạt | Hợp với | Gãy khi |
|---|---|---|---|---|
| A. Đọc nguồn có sẵn | ✓ | — | dữ liệu đã có hệ thống | không có cách tra |
| B. Cột cố định | ✓ | ✗ | sự thật biết trước | sự thật mới |
| C. Khoá–giá trị | ✓ | ✓ | sự thật đa dạng | khoá trùng nghĩa |
| D. Nhật ký sự kiện | ✓ theo thời gian | vừa | sự kiện | tìm theo nội dung |
| E. Bảng + chữ tự do | phần cấu trúc | ✓ | đa số | thông tin trôi vào chữ tự do |

**Quy luật:** câu hỏi **biết trước dạng** → tra bảng, đúng và nhanh; câu hỏi **mở** → cần tìm kiếm. Và đừng chép dữ liệu đã có nguồn sự thật
ở chỗ khác — hãy đọc thẳng nó.

## 6. Ba kịch bản

- **Cửa hàng Lá:** A cho đơn/thanh toán (không bao giờ chép), C cho sở thích khách, D cho khiếu nại. Đây là lời giải chính của kịch bản B.
- **Mai:** C cho sự thật ổn định (câu hỏi 3: dị ứng → một dòng khoá–giá trị, rất hợp); chuyện Đà Lạt là **sự kiện** → D hoặc ghi chú.
- **Nhóm code:** ít dùng bảng cho kiến thức; nhưng có bảng sẵn: lịch sử git, hệ thống quản lý việc (ticket) → A: tra thẳng.

## 7. Scale

- **Nhỏ:** một file SQLite (cơ sở dữ liệu nằm gọn trong một file) là đủ.
- **Vừa** (hàng nghìn người dùng): SQLite vẫn chạy tốt cho một máy; nhiều máy chủ cùng ghi → PostgreSQL hoặc dịch vụ cơ sở dữ liệu.
- **Lớn** (hàng triệu): bảng vẫn chạy rất tốt — tra bằng khoá là thứ cơ sở dữ liệu giỏi nhất. Cái vỡ là **khoá trùng nghĩa** và **dữ liệu lệch
  nguồn** — giải bằng danh sách khoá chuẩn và không chép.

## 8. Bốn nền tảng

SQLite chạy y hệt trên **Windows, Mac, iOS, Android** (có sẵn trên cả hai hệ điều hành điện thoại). Trên **iOS** còn có Core Data / SwiftData
(lớp tiện lợi bên trên SQLite); trên **Android** có Room (cũng trên SQLite). Trên điện thoại, hồ sơ người dùng nằm trong máy → nhanh,
riêng tư, nhưng mất khi xoá app nếu không đồng bộ lên máy chủ.

## 9. Tóm tắt

Bảng có cấu trúc trả lời đúng tuyệt đối các câu hỏi biết trước dạng; đọc thẳng nguồn sự thật đã có thay vì chép; hồ sơ khoá–giá trị cho sự
thật đa dạng; nhật ký cho sự kiện theo thời gian.

**Thuật ngữ:** database (cơ sở dữ liệu) · table / row / column · key (khoá) · SQL · lookup vs search (tra vs tìm) · source of truth · profile · key–value · event log.

**Giờ bạn biết thêm:** kho thứ hai — nhanh và chính xác cho câu hỏi đã biết dạng — và nguyên tắc "đọc nguồn, đừng chép".

**Bài sau:** [07 — Kho vector](07-kho-vector.md).
