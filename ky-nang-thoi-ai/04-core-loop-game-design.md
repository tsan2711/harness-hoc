# Bài 4 — Game design: vòng lặp cốt lõi của một game thư giãn

> Trục C · Sản phẩm: 1 trang mô tả vòng lặp 30 giây của Thousandfold.

## 1. Câu chuyện
Nhiều dev làm xong hệ thống đẹp rồi mới hỏi "chơi gì trong đó?". Game thư giãn nhìn có vẻ dễ vì không có độ khó, nhưng khó ở chỗ khác: **không có áp lực thì cái gì giữ người chơi ở lại?** Câu trả lời nằm ở vòng lặp nhỏ nhất bạn lặp đi lặp lại và thấy dễ chịu.

## 2. Dừng 30 giây
Nhớ một game bạn từng mở "thêm 5 phút nữa" mà ngồi hai tiếng. Đừng nghĩ tới tính năng — nghĩ tới **một hành động cụ thể ngay lúc đó**: bạn bấm gì, thấy gì, nghe gì, rồi muốn làm lại? Viết nó thành 3 động từ.

## 3. Khái niệm lõi
- **Core loop**: Hành động → Phản hồi → Thưởng/Tiến triển → (hành động tiếp). Phải thoả mãn *ngay cả khi tắt hết tiến trình dài hạn*.
- **Ba tầng vòng lặp**: giây (chạm, thấy, nghe) → phút (hoàn thành một mục nhỏ) → giờ/ngày (tiến triển dài hạn, meta). Làm tầng giây đúng trước.
- **Phản hồi ("juice")**: âm thanh, chuyển động, hạt, rung — biến hành động trung tính thành thoả mãn. Với game của bạn: cảnh cánh hoa tô màu thế giới *chính là* phản hồi.
- **Trạng thái flow** (Csikszentmihalyi): thử thách vừa kỹ năng. Game thư giãn hạ thử thách nhưng giữ **tự chủ và tiến bộ nhìn thấy được**.
- **Self-Determination Theory**: tự chủ, năng lực, kết nối — ba nhu cầu thường dùng để giải thích vì sao người ta thích game.
- **Cảm giác hoàn tất**: người chơi cần điểm dừng tự nhiên (hoàn thành vùng, đủ màu) và lý do quay lại (thế giới thay đổi).
- **Tránh bẫy**: thêm tính năng để che một vòng lặp chán. Nếu 30 giây đầu chưa vui thì thêm hệ thống không cứu được.

## 4. Các cấu trúc và đánh đổi
| Kiểu vòng lặp | Ví dụ thể loại | Ưu | Nhược |
|---|---|---|---|
| Thu thập → nâng cấp | Idle, incremental | Tiến triển rõ | Dễ thành bảng số, ít cảm giác |
| Sáng tạo / sắp đặt | City/garden builder, sandbox | Gắn kết, tự chủ | Cần công cụ tốt, dễ "trống" |
| Khám phá → hé lộ | Cozy exploration | Tò mò dẫn dắt | Nội dung đắt |
| Tô/biến đổi thế giới (hướng của bạn) | — | Phản hồi thị giác trực tiếp, hợp trailer | Cần quy tắc để có quyết định, không chỉ xem |

## 5. Scale
- 30 giây: một hành động + phản hồi hay.
- 5–15 phút: một mục tiêu nhỏ hoàn thành được trong một lần mở game.
- Nhiều giờ: mở rộng vùng, tính năng mới, thay đổi thế giới có thể nhìn.
- Mỗi tầng trên cần tầng dưới đã vững; test tầng dưới trước.

## 6. Sản phẩm
Viết **một trang** (`thousandfold-core-loop.md`, để cạnh GDD của game, không để trong thư mục học):
1. Ba động từ của vòng 30 giây.
2. Người chơi thấy/nghe gì sau mỗi động từ (phản hồi).
3. "Hoàn thành" của vòng 5 phút là gì.
4. Lý do mở lại ngày mai.
5. Một thứ bạn **không** làm (để giữ phạm vi).
- Lưu ý ghi nhớ của tác giả: giai đoạn này GDD trước, đồ hoạ chỉ prototype cơ bản.

## 7. Tự kiểm
- Bỏ hết tiến trình dài hạn, vòng 30 giây có còn dễ chịu không?
- Người xem trailer 15 giây có hiểu game làm gì không?
- Quyết định thú vị nhất người chơi đưa ra trong 5 phút là gì?

## 8. Đọc thêm
"A Theory of Fun" (Koster); "The Art of Game Design: A Book of Lenses" (Schell); bài nói GDC về core loop và juice ("Juice it or lose it").
