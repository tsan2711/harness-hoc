# Bài 3 — Eval 101: biến "có vẻ tốt" thành số

> Trục B · Sản phẩm: eval 20 mục cho 1 việc agent hay làm sai; chạy 2 cách prompt và so sánh.

## 1. Câu chuyện
Bạn đổi một dòng trong CLAUDE.md. Chạy thử 3 task, thấy "mượt hơn". Bạn giữ thay đổi. Hai tuần sau agent hay quên bước kiểm tra — có thể do dòng đó, có thể do may rủi ban đầu. Bạn **không có cách biết**. Eval là cái cân: cùng bộ đề, đo trước/sau, có thước đo độ nhiễu.

## 2. Dừng 30 giây
Bạn chạy cùng một prompt 5 lần trên cùng một task, được 3 lần đạt, 2 lần trượt. Cùng input, kết quả khác nhau. Nghĩ xem: nếu mỗi cấu hình chỉ chạy một lần, bạn đang so sánh hai cấu hình hay hai lần tung xúc xắc?

## 3. Khái niệm lõi
- **Bộ eval** = danh sách case (input + tiêu chí đạt), cố định và có phiên bản. Lấy case từ *thất bại thật* bạn đã gặp, không bịa.
- **Chấm điểm**: ưu tiên máy kiểm được (test chạy, regex, đối chiếu file) > con người > LLM-as-judge.
- **Baseline**: luôn đo cấu hình hiện tại trước; "tốt hơn" nghĩa là hơn baseline.
- **Nhiễu**: chạy mỗi case nhiều lần (k ≥ 3–5) nếu mô hình ngẫu nhiên; báo tỉ lệ, không báo một lần.
- **So sánh cặp (paired)**: cùng case, hai cấu hình. Với kết quả đạt/trượt dùng **McNemar** (chỉ nhìn các case hai bên *khác nhau*). Với số liên tục dùng **bootstrap** lấy khoảng tin cậy của hiệu.
- **Cỡ mẫu**: 20 case chỉ phát hiện chênh lệch lớn (vài chục điểm %). Khác biệt 3–5% cần hàng trăm case. Đừng tuyên bố thắng khi khoảng tin cậy chứa 0.
- **LLM-as-judge**: thiên vị vị trí (thích đáp án đứng trước), thiên vị độ dài, thiên vị chính nó. Giảm bằng: đổi thứ tự, rubric rõ, kiểm tra vài mẫu bằng tay.
- **Rò rỉ (leakage)**: nếu bạn tinh chỉnh prompt trên chính bộ eval rồi đo lại trên nó, điểm phồng lên. Giữ riêng một tập "giữ lại".

## 4. Các cấu trúc và đánh đổi
| Kiểu chấm | Ưu | Nhược |
|---|---|---|
| Test/lệnh chạy được | Khách quan, rẻ, lặp lại | Chỉ cho việc có đáp án máy kiểm được |
| Con người | Bắt được tinh tế | Chậm, mệt, không lặp lại |
| LLM judge | Rẻ, mở rộng | Thiên vị; cần hiệu chỉnh bằng mẫu người chấm |
| Sao chép số liệu sản phẩm thật | Sát thực tế | Chậm, nhiễu |

## 5. Scale
- 20 case: để phát hiện hồi quy lớn, chạy mỗi lần đổi prompt.
- 100–300 case: so sánh hai cấu hình có ý nghĩa thống kê vừa phải.
- Nhiều nghìn: eval tự động liên tục, theo dõi trôi (drift) khi đổi model.
- Chi phí = số case × k × token; ước lượng trước khi chạy.

## 6. Sản phẩm
1. Chọn **một** hành vi agent hay sai trong repo (ví dụ: quên `kit compile` trước khi báo xong, hay đọc lại file đã đọc).
2. Gom 20 case thật từ lịch sử (hoặc dựng tình huống). Mỗi case ghi tiêu chí máy kiểm được.
3. Hai cách prompt/luật (A = hiện tại, B = sửa). Chạy mỗi cái trên 20 case × 3 lần.
4. Tính tỉ lệ đạt từng bên, bảng 2×2 các case khác nhau (A đạt/B trượt, A trượt/B đạt), phép McNemar (hoặc nếu số cặp khác nhau < 10, ghi "chưa đủ bằng chứng").
5. Ghi kết luận một dòng vào `log.md`. Bạn đã làm recall eval ở harness — bài này là chuẩn hoá nó cho **mọi** thay đổi luật.

## 7. Tự kiểm
- Vì sao McNemar bỏ qua các case cả hai cùng đạt?
- 14/20 so với 12/20 có đáng tin không? Vì sao?
- Nêu 2 cách LLM judge có thể lừa bạn.

## 8. Đọc thêm
Hướng dẫn eval của Anthropic và OpenAI (phần "building evals"); bài giới thiệu paired test và bootstrap (bất kỳ giáo trình thống kê thực hành nào).
