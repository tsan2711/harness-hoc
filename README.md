# harness-hoc/ — chỗ học harness, từng bài một

Một chỗ duy nhất để học **harness** (mọi thứ bao quanh model để nó làm việc thật): nhớ, công cụ, hook, nhiều phiên, giao việc,
đo, scale. Học theo thứ tự các **chặng**; mỗi chặng là một thư mục, mỗi bài một file.

**Cách mỗi bài viết** (xem [CACH-HOC.md](CACH-HOC.md)): câu chuyện → "dừng 30 giây" tự nghĩ (không có câu hỏi bắt trả lời) →
nhiều cách làm + ưu/nhược/điểm gãy → bảng so sánh → scale → liên hệ Seriously → 4 nền tảng. **Mỗi lần một bài**, ngủ rồi bài sau.

## Lộ trình

| Chặng | Chủ đề | Bài dự kiến | Trạng thái |
|---|---|---|---|
| **A** | Nền: [A01](A-nen/01-vong-lap-agent.md) · [b vòng lặp](A-nen/01b-sau-vong-lap.md) · [c công cụ](A-nen/01c-sau-cong-cu.md) · [d hook](A-nen/01d-sau-cong-hook.md) · [A02](A-nen/02-ngu-canh-va-tien.md) · [b cache](A-nen/02b-sau-ngu-canh.md) · [c nền+token](A-nen/02c-sau-nen-va-token.md) · [d nén](A-nen/02d-sau-nen-ngu-canh.md) · [A03 vòng tự chạy](A-nen/03-vong-lap-tu-chay.md) · [A04 đồ thị](A-nen/04-do-thi-cong-viec.md) · [lab/](A-nen/lab/) | vòng lặp · ngữ cảnh · tiền · vòng tự chạy · đồ thị | **xong 10 bài** |
| **B** | [Bộ nhớ](B-bo-nho/README.md) | tổ chức · tool call cho bộ nhớ · truy hồi · ghi/quên · scale · đo | **triển khai: 21 bài xong** |
| **B+** | [Memory theo mục đích](memory-theo-muc-dich/README.md) | 11 loại trí nhớ · bộ chọn kho · bản đồ quan hệ chống hao hụt · tách repo · lộ trình đo trước | **6 bài xong** (chờ duyệt) |
| **B++** | [Migrate thực chiến](migrate-thuc-chien/README.md) | tổng quan sau migrate · đo @3 · bí danh · nghi cũ · RRF · doc2query/claim · tách repo · lỗi chuyển nhà · cổng | **3 bài xong** (00–02) |
| **C** | Công cụ: tool call, MCP, mô tả công cụ | tool call từ gốc · viết mô tả để model chọn đúng · MCP · quyền | chưa |
| **D** | Hook & cổng kiểm chứng | nhắc vs chặn · pre-commit · "xong giả" · kiểm Unity không mở Editor | chưa |
| **E** | Nhiều phiên song song | vì sao giẫm chân · worktree · claim/WORKBOARD · gom-tất-cả | chưa |
| **F** | Tổ chức & giao việc | công ty agent · hộp thư · dispatch tự chạy · nghiệm thu | chưa |
| **G** | Đo & tự nâng cấp | eval · cadence · friction log · nạng vs bền | chưa |
| **H** | Scale & tách khỏi game | 9 chiều scale · manifest game/variant/target · rủi ro | chưa |

## Ghi chú

- Các bài đào sâu dùng số đo thật từ transcript Claude Code của tác giả (xấp xỉ; chạy `A-nen/lab/*.py` trên transcript của bạn để có số của bạn).
- Ví dụ lấy từ một monorepo game Unity có harness riêng ("Seriously"); đường dẫn trong bài chỉ để minh hoạ, repo đó không công khai.
- Khi một chặng mới có bài, cập nhật bảng lộ trình ở trên.
