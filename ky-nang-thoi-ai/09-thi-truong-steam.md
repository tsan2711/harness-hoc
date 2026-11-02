# Bài 9 — Thị trường Steam: dữ liệu trước khi dựng thêm

> Trục C · Sản phẩm: bảng 10 game tương tự + ước lượng wishlist/review.

## 1. Câu chuyện
Hầu hết game indie không thất bại vì dở; chúng thất bại vì **không ai biết chúng tồn tại**, hoặc vì người đúng khách hàng không thấy "đây là thứ tôi muốn". Bạn có thể làm game đẹp trong 2 năm rồi ra mắt trong im lặng. Dữ liệu thị trường hỏi ngay từ sớm: ai chơi, so với cái gì, và họ đã trả bao nhiêu cho những game giống thế này.

## 2. Dừng 30 giây
Nghĩ về ba game thư giãn bạn biết trên Steam. Vì sao bạn nghe tới chúng — bạn thấy ở đâu? Giờ nghĩ: game của bạn xuất hiện trước người ấy bằng con đường nào?

## 3. Khái niệm lõi
- **Wishlist**: người chơi bấm theo dõi; là chỉ báo doanh số ra mắt được dùng rộng rãi. Quy tắc ngón tay cái trong cộng đồng (Chris Zukowski/HowToMarketAGame và các bài tương tự): tỉ lệ chuyển wishlist → mua trong tuần đầu thường vài phần trăm đến ~chục phần trăm, và mốc vài nghìn wishlist trước ra mắt được coi là tối thiểu để có đà. **Coi là kinh nghiệm cộng đồng, không phải luật; kiểm lại số liệu mới.**
- **Tag & thể loại**: thuật toán gợi ý của Steam dựa vào tag và hành vi; chọn tag thật sự mô tả người chơi mục tiêu.
- **Trang store**: capsule (ảnh nhỏ), 5 ảnh đầu, trailer, mô tả ngắn — người xem quyết định trong vài giây.
- **Đối thủ & "comp titles"**: tìm các game cùng ý tưởng/giá/đối tượng để ước lượng quy mô hợp lý, không dùng game hiện tượng làm mốc.
- **Nguồn dữ liệu**: SteamDB (lượng người chơi, giá, lịch sử), Steam trang store công khai (số review → ước lượng doanh số bằng nhân hệ số, thường 30–50 lần số review, rất thô), các dịch vụ phân tích (Gamalytic, VG Insights...), tin tức Next Fest.
- **Sự kiện**: Steam Next Fest, lễ giảm giá — cơ hội lên wishlist; có lịch đăng ký trước.
- **Thể loại cozy/relaxing**: cộng đồng rõ nhưng cạnh tranh cao; điểm khác biệt thị giác dễ thấy trong ảnh/trailer là lợi thế lớn.
- Chi phí cố định: phí đăng ký một app trên Steam (hiện khoảng 100 USD, hoàn lại khi đạt doanh thu ngưỡng — kiểm tra điều khoản hiện hành).

## 4. Các cấu trúc và đánh đổi
| Cách ước lượng | Ưu | Nhược |
|---|---|---|
| Số review × hệ số | Nhanh, công khai | Rất thô, hệ số thay đổi theo thể loại |
| Dịch vụ phân tích trả phí | Số liệu gọn | Là ước lượng, có lệch |
| Hỏi/đọc devlog của dev khác | Số thật | Thiên lệch người thành công đăng bài |
| Wishlist của chính bạn | Chính xác nhất cho bạn | Chỉ có sau khi có trang |

## 5. Scale
- Mục tiêu cá nhân thực tế (cần quy tắc): đặt 3 kịch bản — tệ (ít), vừa, tốt — và xem ngân sách thời gian/tiền ở kịch bản tệ có chấp nhận được không.
- Càng sớm có trang Steam (Coming Soon), wishlist càng có thời gian tích lũy.

## 6. Sản phẩm
1. Tìm 10 game gần với Thousandfold (thể loại, thị giác, giá). Dùng SteamDB và trang store.
2. Mỗi game ghi: giá, ngày ra mắt, số review + % tích cực, tag chính, điểm hấp dẫn thị giác trong 3 giây đầu, ước lượng doanh số thô (ghi công thức).
3. Tìm mẫu chung: tag nào xuất hiện nhiều, mức giá, lý do review tích cực/tiêu cực lặp lại.
4. Viết 5 dòng kết luận: người chơi mục tiêu, giá hợp lý, khoảng trống thị giác của bạn, rủi ro lớn nhất.
5. Nhớ: Tác giả giao các quyết định kiểu giá/quảng cáo cho Claude quyết theo dữ liệu — ghi lý do kèm số.
- Việc này nên chuyển thành một việc cho bộ phận Marketing/Phát hành qua `kit company send` thay vì giữ riêng ở đây (xem lại luật liên phòng).

## 7. Tự kiểm
- Vì sao dùng game hiện tượng làm mốc là nguy hiểm?
- Hệ số "review → doanh số" sai theo hướng nào ở thể loại giá thấp?
- Nếu kịch bản tệ xảy ra, bạn mất gì và có chịu được không?

## 8. Đọc thêm
Blog/newsletter HowToMarketAGame (Chris Zukowski); tài liệu Steamworks về trang store và Next Fest; GDC talks về indie launch postmortem. (Kiểm số liệu cũ trước khi dùng.)
