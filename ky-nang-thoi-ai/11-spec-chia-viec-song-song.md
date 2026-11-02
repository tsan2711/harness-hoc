# Bài 11 — Viết spec và chia việc cho nhiều agent chạy song song

> Trục A+B · Sản phẩm: một plan lớn chia 3 phiên song song, đo thời gian so với làm tuần tự.

## 1. Câu chuyện
Bạn có plan 3 mảng. Mở 3 phiên agent cùng lúc để nhanh gấp ba. Kết quả: hai phiên sửa cùng một file, một phiên dựa vào API phiên khác chưa viết xong, bạn mất một giờ gỡ xung đột. Tổng thời gian *lâu hơn* làm tuần tự. Song song không tự động nhanh hơn — nó chỉ nhanh khi **việc thật sự độc lập và spec đủ rõ**.

## 2. Dừng 30 giây
Nhìn plan của bạn. Với mỗi cặp mảng, hỏi: mảng B có cần *kết quả* của mảng A không? Hai mảng có cùng đụng một file/ một asset không? Nếu câu trả lời là "có" ở đâu đó, chỗ đó là điểm nghẽn hoặc xung đột đang chờ.

## 3. Khái niệm lõi
- **Định luật Amdahl**: phần tuần tự không giảm; tăng tốc tối đa = 1 / (phần tuần tự + phần song song / số worker). Nếu 40% việc là nối ghép tuần tự, ba worker cũng không vượt ~1/(0.4+0.6/3) ≈ 1,67 lần.
- **Phân rã theo quyền sở hữu**: mỗi phiên sở hữu một tập file/thư mục riêng (đúng cơ chế bảng WORKBOARD của repo). Xung đột giảm khi ranh giới module rõ (bài 7).
- **Hợp đồng giao diện trước**: chốt chữ ký hàm/dữ liệu ở file chung *trước*, rồi hai phiên mới làm hai phía.
- **Spec đủ tốt cho agent**: mục tiêu, tiêu chí xong **máy kiểm được**, phạm vi (được/không được chạm), ví dụ vào/ra, ràng buộc (hiệu năng, luật repo). Spec quá dài làm loãng; quá ngắn làm đoán.
- **Cách ly bằng worktree/nhánh**: mỗi phiên có cây làm việc riêng, tích hợp qua merge nhỏ, thường xuyên. (Repo của bạn: không `git stash` cây dùng chung.)
- **Chi phí phối hợp**: mỗi phiên thêm = thêm review, thêm nguy cơ lệch. Con người (bạn) là nút cổ chai chấp nhận kết quả.
- **Kiểm tích hợp**: sau khi gộp, chạy một lượt test chung (luật repo: test một lượt ở cuối, gom job Unity).
- **Việc liên phòng**: giao qua `kit company send` kèm `--check` để bên nhận tự kiểm.

## 4. Các cấu trúc và đánh đổi
| Chiến lược | Ưu | Nhược |
|---|---|---|
| Tuần tự một phiên | Không xung đột | Chậm; ngữ cảnh dài làm giảm chất lượng |
| Song song theo mảng độc lập | Nhanh khi tách tốt | Cần hợp đồng giao diện + ranh giới file |
| Pipeline (A xong → B) | Rõ phụ thuộc | Không song song thật |
| Orchestrator + subagent ngắn | Ngữ cảnh sạch cho từng việc | Cần spec rất rõ; tốn token tổng |

## 5. Scale
- 2–3 phiên: tay bạn quản được bằng bảng claim.
- Chục phiên: cần lịch, ràng buộc tự động, phân xử xung đột (công ty agent).
- Tăng số phiên chỉ có lợi khi thời gian phối hợp < thời gian tiết kiệm; đo, đừng đoán.

## 6. Sản phẩm
1. Chọn một plan thật (ví dụ một hệ của Thousandfold gồm 3 mảng).
2. Vẽ đồ thị phụ thuộc, đánh dấu phần tuần tự bắt buộc, ước tính tăng tốc theo Amdahl.
3. Viết hợp đồng giao diện (file chung) + 3 spec theo mẫu: mục tiêu / tiêu chí xong máy kiểm / được-không được chạm / ví dụ.
4. Chạy 3 phiên song song (nhận file trong WORKBOARD); chạy tích hợp một lượt cuối.
5. Đo: tổng thời gian đồng hồ, số xung đột merge, số lần phải sửa spec, so với ước tính tuần tự (từ những lần làm trước). Ghi 3 bài học vào `log.md`.
- Nhắc subagent luật gom job Unity trong prompt.

## 7. Tự kiểm
- Phần tuần tự lớn nhất trong plan của bạn là gì và có thu nhỏ được không?
- Spec của bạn có "xong" nào mà máy không kiểm được không?
- Điểm nào bạn đã không đo được hiệu quả thật của song song?

## 8. Đọc thêm
Bài viết kỹ thuật về hệ nhiều agent (Anthropic: "How we built our multi-agent research system"); Amdahl's law; tài liệu git worktree.
