# Bài 10 — Marketing một người: trailer, capsule, devlog

> Trục C · Sản phẩm: trailer 30 giây + capsule nháp.

## 1. Câu chuyện
Người lướt Steam hoặc TikTok cho game của bạn **2–3 giây**. Trong thời gian đó họ chỉ thấy một khung hình và nghe một âm. Nếu khung hình ấy không nói "đây là game gì, vì sao dễ chịu", họ lướt đi. Marketing cho dev một mình không phải quảng cáo — là **làm cho 3 giây đầu rõ ràng**.

## 2. Dừng 30 giây
Mở game của bạn như một người lạ. Chọn đúng **một** khoảnh khắc 3 giây đẹp nhất, không cần giải thích. Nếu không chọn được, vấn đề không nằm ở marketing mà ở bài 4 (vòng lặp/phản hồi thị giác).

## 3. Khái niệm lõi
- **Capsule (ảnh nhỏ)**: hiển thị cực nhỏ trong danh sách; cần chủ thể rõ, tên dễ đọc, ít chữ, tương phản mạnh. Thử xem ở kích thước thật (khoảng vài trăm px).
- **Trailer**: vài giây đầu phải là gameplay/khoảnh khắc đẹp, không logo dài; thể hiện vòng lặp; 30–60 giây; có nhịp và âm thanh. Kết bằng lời kêu gọi (wishlist).
- **Ảnh chụp màn hình**: ảnh đầu quyết định; thể hiện game, không phải menu.
- **Devlog & cộng đồng**: đăng đều những khoảnh khắc ngắn (GIF/video) ở nơi người chơi mục tiêu có mặt (Reddit thể loại, Bluesky/X, TikTok/Shorts, Discord). Quy tắc nền tảng khác nhau — đọc luật subreddit trước khi đăng.
- **Phễu**: thấy → chú ý → vào trang → wishlist → mua. Đo từng bước để biết nghẽn ở đâu (impressions, visits, wishlist trên Steamworks).
- **Đo & thử**: thử hai bản capsule/ảnh đầu và so sánh tỉ lệ vào trang; một thay đổi một lần.
- **Đừng spam**: giá trị trước, link sau. Chia sẻ quá trình tạo ra thứ đẹp thường hiệu quả hơn quảng bá thô.
- **Công cụ AI**: có thể dựng nháp, phụ đề, biến thể; chỉnh bằng mắt người. Nhớ ghi nguồn asset (luật asset-backlog) và kiểm tra quy định công bố nội dung AI của Steam.

## 4. Các cấu trúc và đánh đổi
| Kênh | Ưu | Nhược |
|---|---|---|
| Steam (trang, Next Fest) | Người đã sẵn ý mua | Cần có trang & trailer tốt trước |
| Video ngắn (TikTok/Shorts/Reels) | Tiếp cận rộng, hợp game có hình ảnh đẹp | Biến động, cần đăng đều |
| Reddit/Discord | Cộng đồng đúng thể loại | Nhạy cảm với tự quảng bá |
| Báo chí/streamer | Khuếch đại | Khó, cần liên hệ cá nhân hoá |

## 5. Scale
- Giai đoạn prototype: chỉ cần clip 10–15 giây đẹp để thử phản ứng.
- Trước ra mắt: trang Steam đầy đủ + trailer + lịch devlog.
- Sau ra mắt: cập nhật + đánh giá để duy trì.

## 6. Sản phẩm
1. Chọn khoảnh khắc 3 giây (từ mục 2). Quay clip windowed bằng công cụ quay màn hình/`kit` nếu có (đồ hoạ prototype vẫn ổn để thử).
2. Dựng trailer 30 giây: 0–3s khoảnh khắc đẹp → 3–20s vòng lặp cốt lõi (bài 4) → 20–28s tiến triển/thế giới đổi màu → 28–30s tên + wishlist.
3. Làm capsule nháp (vài biến thể); xem ở kích thước nhỏ nhất.
4. Đưa cho 3 người ngoài (hoặc agent GD/Marketing theo quy trình công ty) xem 5 giây rồi hỏi "game này làm gì?" — ghi câu trả lời nguyên văn.
5. Lưu đường dẫn vào `log.md`; chuyển việc hoàn thiện cho bộ phận Marketing bằng `kit company send` nếu phù hợp.
- Giai đoạn này tác giả muốn GDD trước, đồ hoạ chỉ cơ bản: đây là bản thử phản ứng, không phải bản cuối.

## 7. Tự kiểm
- 3 giây đầu của trailer nói gì mà không cần chữ?
- Capsule của bạn đọc được ở kích thước thật không?
- Bạn đo được bước nào của phễu và bước nào còn mù?

## 8. Đọc thêm
Tài liệu Steamworks "Store page best practices"; bài phân tích trailer thành công của game indie (GDC, devlogs); HowToMarketAGame.
