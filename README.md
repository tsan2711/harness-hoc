# harness-hoc/ — chỗ học harness, từng bài một

Một chỗ duy nhất để học **harness** (mọi thứ bao quanh model để nó làm việc thật): nhớ, công cụ, hook, nhiều phiên, giao việc,
đo, scale. Học theo thứ tự các **chặng**; mỗi chặng là một thư mục, mỗi bài một file.

**Cách mỗi bài viết** (xem [CACH-HOC.md](CACH-HOC.md)): câu chuyện → "dừng 30 giây" tự nghĩ (không có câu hỏi bắt trả lời) →
nhiều cách làm + ưu/nhược/điểm gãy → bảng so sánh → scale → liên hệ Seriously → 4 nền tảng. **Mỗi lần một bài**, ngủ rồi bài sau.

## Lộ trình

| Chặng | Chủ đề | Bài dự kiến | Trạng thái |
|---|---|---|---|
| **A** | Nền ([A01](A-nen/01-vong-lap-agent.md) + [sâu](A-nen/01b-sau-vong-lap.md), [A02](A-nen/02-ngu-canh-va-tien.md) + [sâu](A-nen/02b-sau-ngu-canh.md); [lab/](A-nen/lab/)): model, vòng lặp agent, ngữ cảnh, tiền | vòng lặp agent (xong) · ngữ cảnh = tờ giấy + tiền (xong) | **A01, A02 xong** |
| **B** | [Bộ nhớ](B-bo-nho/README.md) | tổ chức · tool call cho bộ nhớ · truy hồi · ghi/quên · scale · đo | **bài 01 xong** |
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
