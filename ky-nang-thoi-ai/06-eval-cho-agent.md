# Bài 6 — Eval cho agent làm việc dài

> Trục B · Sản phẩm: bảng so sánh 2 cấu hình harness trên cùng 10 task.

## 1. Câu chuyện
Eval bài 3 đo một câu trả lời. Agent thật làm việc 30 bước: đọc file, sửa, chạy test, sửa lại. Một "lần chạy" tốn tiền, dài, và kết quả phụ thuộc cả đường đi. Bạn thêm hook mới vào harness; agent "có vẻ" gọn hơn, nhưng token tăng 40%. Tốt hơn hay chỉ đắt hơn?

## 2. Dừng 30 giây
Hai cấu hình đều làm xong task. Một cái dùng 80k token và sửa 3 lần, cái kia 200k token và sửa 9 lần. Điểm "xong/không xong" bằng nhau. Nghĩ xem còn những chiều nào bạn phải đo thì mới nói được cấu hình nào tốt.

## 3. Khái niệm lõi
- **Nhiều chiều kết quả**: tỉ lệ hoàn thành (theo tiêu chí máy kiểm), chất lượng đầu ra, **chi phí** (token/tiền), **thời gian**, số vòng sửa lại, số lần chạm vùng cấm (vi phạm luật).
- **Outcome vs process**: chấm kết quả cuối bằng test; thêm chỉ số quy trình (có chạy compile? có đọc lại file thừa?) để chẩn đoán *vì sao*.
- **pass@k vs pass^k**: pass@k = ít nhất 1 trong k lần đạt (đo tiềm năng); pass^k = cả k lần đều đạt (đo độ tin cậy). Agent dùng thật cần cái sau.
- **Môi trường lặp lại**: mỗi lần chạy bắt đầu từ cùng trạng thái repo (git worktree/commit cố định), cùng seed nếu được; dọn trạng thái giữa các lần.
- **Phương sai**: chạy mỗi task nhiều lần; so sánh trên cùng task (paired). Báo trung vị và khoảng thay vì trung bình.
- **Regression suite**: một bộ task nhỏ cố định, chạy khi đổi model/luật/hook, theo dõi theo thời gian.
- **Cái bẫy**: chỉnh harness theo đúng 10 task rồi đo trên 10 task đó — rò rỉ. Giữ vài task "giấu".
- **Chi phí eval**: 10 task × 2 cấu hình × 3 lần = 60 lần chạy dài. Ước lượng token và thời gian trước; chạy ngoài giờ.

## 4. Các cấu trúc và đánh đổi
| Thiết kế | Ưu | Nhược |
|---|---|---|
| Task tổng hợp nhỏ, có test | Rẻ, chạy lặp được | Xa thực tế |
| Task lấy từ lịch sử repo thật (commit cũ + test) | Sát thực | Cần dựng lại trạng thái, tốn công |
| Chấm bằng người | Bắt lỗi tinh tế | Chậm |
| Log phiên thật, đo chỉ số quy trình | Không tốn thêm chạy | Không có đối chứng |

## 5. Scale
- 10 task × 3 lần: phát hiện chênh lệch lớn (đủ cho quyết định kiểu "bỏ/giữ" một hook tốn kém).
- 50+ task: so sánh tinh; bắt đầu cần thống kê cặp có ý nghĩa.
- Liên tục: chạy hằng tuần theo lịch (cadence sẵn có của repo) và vẽ biểu đồ xu hướng.

## 6. Sản phẩm
1. Chọn 10 task từ lịch sử commit repo (mỗi task có kiểm tra máy kiểm được: test/`kit compile`/diff khớp tiêu chí). Chọn task nhỏ và độc lập.
2. Hai cấu hình harness: hiện tại vs một biến đổi (ví dụ thêm/bớt một hook hoặc rút gọn CLAUDE.md).
3. Mỗi task × cấu hình × 3 lần; ghi: đạt/không, token, thời gian, số vòng sửa, vi phạm luật.
4. Bảng tổng hợp: tỉ lệ đạt, pass^3, trung vị token. Một câu: cấu hình nào đáng giữ và vì sao; nếu chưa đủ bằng chứng, nói thẳng.
5. Ghi vào `log.md`; cân nhắc tự động hoá chạy bằng `kit` nếu bạn muốn lặp.

## 7. Tự kiểm
- Vì sao pass^k quan trọng hơn pass@k với agent chạy không giám sát?
- Chỉ số quy trình nào bạn thêm để *giải thích* một kết quả xấu?
- Nếu hai cấu hình hoà về tỉ lệ đạt, bạn dùng chiều nào để chọn?

## 8. Đọc thêm
Bài viết kỹ thuật của Anthropic/OpenAI về đánh giá agent và coding benchmark (SWE-bench và các biến thể); các bài về độ tin cậy `pass^k`.
