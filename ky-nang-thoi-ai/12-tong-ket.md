# Bài 12 — Ôn tập, tổng kết, quyết định bước tiếp

> Trục tổng · Sản phẩm: 1 trang tổng kết + quyết định đi sâu trục nào.

## 1. Câu chuyện
Mười một bài trôi qua, nhật ký có hàng chục dòng số. Nếu không gom lại, nó thành đống ghi chép. Bài cuối là lúc đổi **chi tiết** thành **quyết định**: bạn đã đổi được gì trong cách làm, con số nào chứng minh, và nên đầu tư thời gian tiếp theo vào đâu.

## 2. Dừng 30 giây
Nhớ lại bài mà bạn bất ngờ nhất vì kết quả đo khác với trực giác. Đó là chỗ bạn đã *thật sự* học, vì mô hình trong đầu bạn bị sửa. Ghi nó lên đầu trang tổng kết.

## 3. Khung tổng kết (mỗi trục)
Với từng trục A/B/C, trả lời bằng số hoặc bằng chứng cụ thể:
1. **Đã đo được gì?** (bảng ms, tỉ lệ đạt, khoảng tin cậy, ...)
2. **Khác trực giác ở đâu?**
3. **Đã đổi gì trong repo/quy trình?** (luật, hook, eval cố định, module sửa)
4. **Còn chưa biết gì?**
5. **Bằng chứng nào còn yếu?** (cỡ mẫu nhỏ, đo một lần, chưa windowed)

## 4. Các cấu trúc ra quyết định
| Kiểu quyết định | Khi dùng | Rủi ro |
|---|---|---|
| Đi sâu 1 trục (T-shape) | Có 1 trục rõ ràng mang lại lợi thế | Bỏ lỡ nền các trục khác |
| Giữ cân bằng 3 trục | Còn chưa rõ lợi thế | Loãng, ít nổi bật |
| Chuyển sang ship | Trục C cho thấy có thị trường | Nợ kỹ thuật chưa trả |

Gợi ý khung chọn: trục nào khiến bạn **tạo ra giá trị mà agent không tự làm được** và phù hợp mục tiêu "ship game riêng + đi sâu kỹ thuật" (đã chọn 2026-09-30)?

## 5. Scale — vòng lặp học tiếp
- Hàng tuần: 3 dòng log; kiểm chứng ít nhất một giả định bằng số.
- Hàng tháng: chạy lại eval cố định (bài 3, 6) để phát hiện hồi quy khi đổi model/luật.
- Hàng quý: đọc lại báo cáo nguồn (Anthropic Economic Index, các bản mới) và điều chỉnh kế hoạch. Nguồn nên kiểm từ bản gốc, không từ bài tổng hợp.
- Học từ nguồn ngoài, không chỉ từ dự án của mình (tránh "ếch ngồi đáy giếng").

## 6. Sản phẩm
1. Viết `tong-ket.md` (1 trang) theo khung mục 3 cho ba trục.
2. Một bảng "việc làm tiếp" 3 dòng: việc / vì sao / số đo thành công / hạn.
3. Một quyết định rõ ràng: đi sâu trục nào trong 3 tháng tới, kèm điều kiện đổi ý.
4. Cập nhật lại README (kế hoạch) cho chu kỳ kế tiếp; bổ sung bài mới nếu cần.
5. Nếu kết quả đáng chia sẻ (eval, benchmark), đẩy bài vào repo bài giảng công khai (`harness-hoc`) sau khi xoá thông tin nhạy cảm.

## 7. Tự kiểm
- Bạn có số đo cho ít nhất một cải thiện thật không, hay chỉ cảm giác?
- Điều gì sẽ khiến bạn đổi quyết định?
- Bạn đã học thêm gì từ nguồn ngoài, không phải từ chính dự án của mình?

## 8. Đọc thêm
Quay lại báo cáo gốc của Anthropic ("Labor market impacts of AI") và các bản cập nhật của Economic Index; đọc kèm phê bình về phương pháp đo "exposure" (độ phủ lý thuyết khác tác động thực tế).
