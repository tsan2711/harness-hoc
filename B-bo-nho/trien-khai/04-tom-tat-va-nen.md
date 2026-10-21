# 04 — Tóm tắt và nén

> Chuỗi "Triển khai trí nhớ", bài 4/21. Đọc ~9 phút.
> **Bạn đã biết** ([03](03-nhet-het-vao-ngu-canh.md)): nhét hết đúng khi nội dung nhỏ; ngoài đó gãy vì giá, độ trễ, "lạc ở giữa"; cache
> prompt chỉ trúng khi phần đầu không đổi.

## 1. Chuyện mở đầu

Mai chat với trợ lý suốt một năm. Ứng dụng dùng cách: khi lịch sử dài, nhờ model **tóm** phần cũ thành một đoạn ngắn, rồi tiếp tục. Sau
nhiều lần tóm chồng lên nhau, bản tóm còn: "Mai là nhân viên văn phòng, thích nấu ăn, hay hỏi công thức." Dòng "dị ứng tôm" đã biến mất
ở lần tóm thứ tư — model lúc đó thấy nó "không liên quan tới cuộc chat hiện tại".

## 2. Dừng 30 giây

- Tóm tắt luôn bỏ bớt. Ai quyết bỏ cái gì — và người đó có biết tương lai sẽ cần gì không?
- Tóm một bản tóm, rồi tóm tiếp bản đó… sai sót cộng dồn thế nào?
- Trong một phiên agent viết code, phần nào của ngữ cảnh *an toàn để vứt* mà không cần tóm?

## 3. Khái niệm

**Tóm tắt (summarization)** dùng chính LLM viết lại một đoạn dài thành đoạn ngắn. Nó giữ *ý chính theo đánh giá của model lúc đó* —
không giữ chi tiết mà model đánh giá là phụ (câu hỏi 1).

**Nén khi đầy (compaction).** Khi ngữ cảnh gần đầy, hệ thống tóm toàn bộ phiên thành một bản ngắn, xoá phần cũ, làm tiếp trên bản tóm.
Nhiều agent viết code làm vậy (có lệnh nén tay, và tự nén khi đầy).

**Xoá kết quả công cụ cũ (context editing).** Trong phiên agent, phần lớn ngữ cảnh là *kết quả công cụ*: nội dung file đã đọc, log đã
chạy. Sau khi dùng xong, chúng có thể bị xoá khỏi bàn (agent đọc lại được nếu cần) — không phải tóm gì cả (câu hỏi 3). Anthropic công bố
tính năng này năm 2025, ghép cùng một thư mục trí nhớ để agent ghi lại điều cần giữ trước khi bị xoá.

**Sai số cộng dồn.** Mỗi lần tóm mất một ít và có thể sai một ít. Tóm của tóm làm hai thứ đó chồng lên (câu hỏi 2) — giống chơi "tam sao
thất bản".

## 4. Các cách

**A. Tóm cuốn chiếu (rolling summary).** Giữ N lượt gần nhất nguyên văn + một bản tóm của mọi thứ trước đó; mỗi khi quá N, gộp lượt cũ
nhất vào bản tóm. *Hợp khi:* cuộc chat dài một chủ đề. *Gãy khi:* nhiều tháng — chi tiết hiếm nhưng quan trọng (dị ứng) bị tóm mất.

**B. Tóm phân tầng.** Tóm theo ngày → tóm các ngày thành tuần → tuần thành tháng; giữ cả các tầng. Cần chi tiết thì đi xuống tầng dưới.
*Hợp khi:* sự kiện có thời gian (nhật ký, lịch sử dự án). *Gãy khi:* không biết đi xuống tầng nào → cần tìm kiếm (phần 4).

**C. Nén khi đầy, một lần.** Không tóm gì cho tới khi gần đầy bàn; lúc đó tóm cả phiên. *Hợp khi:* một phiên làm việc dài (agent code).
*Gãy khi:* bản tóm bỏ mất quyết định nhỏ giữa phiên; sau nén, agent "quên" vì sao đã chọn hướng hiện tại.

**D. Xoá kết quả công cụ, giữ lập luận.** Vứt nội dung file/log cũ, giữ câu hỏi, quyết định, câu trả lời. *Hợp khi:* agent dùng nhiều công
cụ. *Gãy khi:* agent cần lại đúng chi tiết đã xoá mà không biết đọc lại ở đâu.

**E. Tóm có khuôn.** Thay "tóm cho ngắn", yêu cầu điền khuôn cố định: *sự thật về người dùng · quyết định · việc đang dở · điều cấm quên*.
Mục "điều cấm quên" được chép nguyên qua mọi lần tóm. *Hợp khi:* biết trước loại nội dung quan trọng. *Gãy khi:* khuôn phình; điều quan
trọng không thuộc mục nào.

## 5. Bảng một lần nhìn

| Cách | Tốn token lúc tóm | Mất chi tiết hiếm | Hợp với | Gãy khi |
|---|---|---|---|---|
| A. Cuốn chiếu | đều đặn | cao (lâu dài) | chat dài một chủ đề | nhiều tháng |
| B. Phân tầng | vừa | thấp (còn tầng dưới) | sự kiện theo thời gian | không biết xuống tầng nào |
| C. Nén khi đầy | một lần, lớn | vừa | phiên agent dài | quyết định giữa phiên |
| D. Xoá kết quả công cụ | 0 | thấp (đọc lại được) | agent nhiều công cụ | không biết đọc lại đâu |
| E. Khuôn | như A | thấp với mục có khuôn | biết trước loại quan trọng | khuôn phình |

**Quy luật:** tóm tắt là **mất có chủ ý** — nó an toàn khi bản gốc vẫn còn ở đâu đó để quay lại, và nguy hiểm khi bản tóm là bản duy nhất.

## 6. Ba kịch bản

- **Mai:** A một mình là nguy hiểm (dị ứng). E + giữ bản gốc trong kho.
- **Cửa hàng Lá:** cuộc chat với khách ngắn; tóm cuối mỗi cuộc ("khách khiếu nại giao trễ đơn #123, đã hứa hoàn tiền") lưu vào hồ sơ khách
  — đây là tóm làm **cầu nối** sang kho (bài 06).
- **Nhóm code:** C + D trong phiên; quyết định lớn phải được ghi ra ngoài *trước* khi nén (bài 05, 13).

## 7. Scale

- **Nhỏ:** không cần tóm (bài 03).
- **Vừa:** tóm trong phiên (C, D) là đủ; bản gốc vẫn còn.
- **Lớn** (nhiều tháng, nhiều người): tóm là bước *ghi* (biến cuộc chat thành ghi chú); câu hỏi chuyển sang "tóm thành gì và lưu ở đâu"
  — phần 3. Cái vỡ là **sai số cộng dồn** không ai thấy, vì không ai đọc lại bản tóm.

## 8. Bốn nền tảng

Tóm tốn một lần gọi model. **Windows / Mac:** có thể tóm bằng model nhỏ chạy trên máy (rẻ, riêng tư), chấp nhận chất lượng thấp hơn.
**iOS / Android:** model trên máy (Foundation Models, Gemini Nano) giỏi đúng loại việc này — tóm ngắn; nhưng ngữ cảnh vào nhỏ nên phải
tóm từng mẩu (rất hợp kiểu B). Chạy lúc máy rảnh/đang sạc để không tốn pin khi người dùng đang dùng.

## 9. Tóm tắt

Tóm và nén giúp một phiên dài vừa mặt bàn; xoá kết quả công cụ cũ là cách nén rẻ nhất. Nhưng tóm là mất có chủ ý và sai cộng dồn — chỉ
an toàn khi bản gốc còn lại và điều quan trọng được ghi ra ngoài trước khi bị tóm.

**Thuật ngữ:** summarization · rolling summary · hierarchical summary · compaction · context editing · error accumulation (sai số cộng dồn).

**Giờ bạn biết thêm:** cách kéo dài một phiên vượt mặt bàn, và vì sao gần như mọi hệ thống lâu dài cuối cùng cần một **kho ngoài** — phần tiếp theo.

**Bài sau:** [05 — File ghi chú](05-file-ghi-chu.md).
