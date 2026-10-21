# 02 — Bản đồ lựa chọn

> Chuỗi "Triển khai trí nhớ", bài 2/21. Đọc ~9 phút.
> **Bạn đã biết** ([01](01-model-khong-nho.md)): model không trạng thái; ngữ cảnh = mặt bàn có giới hạn; token = tiền + chỗ; vòng ghi →
> quản lý → đọc; ba chỗ chứa trí nhớ (ngữ cảnh, kho ngoài, trọng số); ba kịch bản Mai / cửa hàng Lá / nhóm code.

## 1. Chuyện mở đầu

Ba người cùng tra "agent memory" trên mạng và đọc ba bài khác nhau. Người thứ nhất kết luận "phải dùng kho vector". Người thứ hai: "phải
có đồ thị tri thức". Người thứ ba: "chỉ cần một file ghi chú". Cả ba bài đều có số đo đẹp. Họ cãi nhau cả buổi mà không ai sai — vì ba
người đang nói về **ba chỗ khác nhau trên cùng một bản đồ**.

## 2. Dừng 30 giây

- "Hôm qua Mai kể chuyện đi Đà Lạt" và "Mai dị ứng tôm" — hai điều này khác nhau ở chỗ nào?
- Cái "agent đang sửa file nào trong 10 phút qua" có cần giữ đến năm sau không?
- Ai nên quyết "điều này đáng nhớ": người dùng, một luật cố định, hay chính model?

## 3. Bốn loại nội dung

Khoa học nhận thức chia trí nhớ người thành vài loại; các hệ thống agent mượn lại cách chia này (LangMem, Letta, Mem0 đều dùng gần như vậy):

| Loại | Là gì | Ví dụ Mai | Ví dụ nhóm code |
|---|---|---|---|
| **Đang làm** (working) | cái đang trên bàn, cho việc trước mắt | 5 câu chat vừa rồi | file đang mở, lỗi vừa chạy ra |
| **Sự kiện** (episodic) | *chuyện đã xảy ra*, có thời điểm | "21/10 kể chuyện đi Đà Lạt" | "phiên hôm thứ Ba thử ChartLite, giật" |
| **Sự thật** (semantic) | điều đúng, không gắn một lúc cụ thể | "dị ứng tôm" | "không dùng ChartLite" |
| **Cách làm** (procedural) | kỹ năng, quy trình, thói quen | "Mai thích câu trả lời ngắn" | "trước khi commit chạy test X" |

Câu hỏi 1: Đà Lạt là **sự kiện**, dị ứng tôm là **sự thật**. Hai loại cần lưu và tìm khác nhau: sự kiện hỏi theo thời gian ("tuần
trước nói gì?"), sự thật hỏi theo chủ đề ("Mai ăn được gì?") và phải *sửa* được khi đổi.

Một sự thật thường **rút ra từ** nhiều sự kiện. Rút lúc nào, ai rút — là một quyết định thiết kế lớn (bài 13, 15).

## 4. Ba trục của bản đồ

Một bài tổng quan năm 2026 ([arXiv 2603.07670](https://arxiv.org/abs/2603.07670)) đặt mọi hệ thống lên ba trục. Mỗi hệ thống là một
điểm trong không gian này — không điểm nào "đúng" cho mọi bài toán.

**Trục 1 — Nhớ bao lâu (phạm vi thời gian).**
- trong một lượt trả lời → trong một phiên → qua nhiều phiên → suốt đời người dùng / dự án.
- Câu hỏi 2: "agent đang sửa file nào" là trí nhớ *trong phiên*; giữ nó qua năm là rác.

**Trục 2 — Lưu bằng gì (chất liệu).**
- chữ thô (lịch sử nguyên văn) · chữ đã tóm · ghi chú có cấu trúc (file, bảng) · vector (bài 07) · đồ thị (bài 08) · trọng số model (bài 17).
- Càng sang phải càng "máy hiểu" hơn nhưng càng khó cho người đọc và sửa tay.

**Trục 3 — Ai điều khiển (chính sách).**
- **Người** khai (người dùng bấm "nhớ cái này", người viết tài liệu).
- **Luật cố định** (code: "mọi đơn hàng đều lưu", "mỗi commit là một sự kiện").
- **LLM tự động** (sau mỗi cuộc chat, một model đọc lại và trích "sự thật mới").
- **Agent tự quyết** (agent có công cụ `ghi_nhớ()` / `tìm_nhớ()` và tự gọi khi thấy cần).
- Câu hỏi 3: không có đáp án chung — bài 13 so bốn cách này.

## 5. Đặt vài cách tiếp cận lên bản đồ

| Cách tiếp cận | Bao lâu | Chất liệu | Ai điều khiển |
|---|---|---|---|
| Dán lại lịch sử (bài 03) | phiên | chữ thô | luật |
| Tóm cuốn chiếu (bài 04) | phiên → nhiều phiên | chữ đã tóm | LLM |
| File ghi chú (bài 05) | suốt dự án | ghi chú | người hoặc agent |
| Hồ sơ người dùng dạng bảng (bài 06) | suốt đời | bảng | luật hoặc LLM |
| Kho vector (bài 07) | nhiều phiên | vector | luật (cắt + lưu mọi thứ) |
| Đồ thị tri thức có thời gian (bài 08) | suốt đời | đồ thị | LLM trích |
| Thư viện kỹ năng (bài 16) | suốt đời | code/ghi chú | agent |
| Huấn luyện thêm (bài 17) | vĩnh viễn | trọng số | người (lúc huấn luyện) |

Đây là lý do ba người ở §1 cãi nhau: họ đọc về ba hàng khác nhau của bảng này.

## 6. Các cách *chọn* một điểm trên bản đồ

**A. Chọn theo công cụ đang hot.** *Hợp khi:* muốn thử nghiệm nhanh. *Gãy khi:* công cụ giỏi một loại nội dung mà bài toán cần loại khác
(ví dụ kho vector rất tốt cho "tìm theo nghĩa" nhưng không tự biết "sự thật này đã bị thay").

**B. Chọn theo loại nội dung chiếm đa số.** Mai: phần lớn là sự thật cá nhân + sự kiện → hồ sơ + nhật ký. Cửa hàng Lá: sự kiện (đơn,
khiếu nại) đã nằm trong hệ thống đơn hàng → chỉ cần đọc từ đó. Nhóm code: sự thật kỹ thuật hay bị thay → cần cách đánh dấu cũ.
*Hợp khi:* biết rõ người dùng hỏi gì. *Gãy khi:* đoán sai loại câu hỏi.

**C. Chọn theo câu hỏi thật + đo** (bài 19). Thu 30–50 câu hỏi thật, thử 2–3 điểm trên bản đồ, đo. *Hợp khi:* có dữ liệu thật. *Gãy khi:*
chưa có người dùng (chưa có câu hỏi thật) → bắt đầu bằng B, chuyển sang C khi có.

**D. Chọn nhiều điểm cùng lúc** — mỗi loại nội dung một chỗ (đang làm: ngữ cảnh; sự thật: hồ sơ; sự kiện: kho tìm kiếm). Đa số hệ thống
thật cuối cùng thành thế này. *Gãy khi:* làm nhiều chỗ ngay từ đầu, trước khi biết chỗ nào cần → nhiều thứ để bảo trì.

## 7. Bảng một lần nhìn

| Cách chọn | Nhanh | Đúng bài toán | Gãy khi |
|---|---|---|---|
| A. Theo công cụ | ✓ | may rủi | công cụ không hợp loại nội dung |
| B. Theo loại nội dung | ✓ | khá | đoán sai câu hỏi |
| C. Theo câu hỏi thật + đo | chậm | ✓ | chưa có câu hỏi thật |
| D. Nhiều chỗ | chậm | ✓ về lâu dài | làm quá sớm |

**Quy luật:** xác định **loại nội dung** và **câu hỏi** trước, rồi mới chọn **chất liệu** và **người điều khiển**.

## 8. Scale

- **Nhỏ:** một điểm trên bản đồ là đủ (thường là file ghi chú hoặc hồ sơ).
- **Vừa:** loại nội dung tách ra — sự kiện nhiều lên nhanh, sự thật thì ít nhưng cần sửa → hai chỗ khác nhau.
- **Lớn:** trục 3 thành vấn đề chính — "LLM tự động" với hàng nghìn người dùng là hàng nghìn lần gọi model mỗi ngày; "người khai" thì
  không ai khai. Thường trộn: luật cho cái chắc, LLM cho cái mờ.

## 9. Bốn nền tảng

Bản đồ giống nhau ở mọi nơi; khác là **điểm nào làm được**. Trên **Windows / Mac** làm được mọi điểm (đủ ổ đĩa, có thể chạy model trên
máy). Trên **iOS / Android**, "LLM tự động" chạy trên máy bị giới hạn bởi pin và model nhỏ → thường làm khi máy đang sạc/rảnh, hoặc gửi
lên máy chủ; "trọng số" gần như không làm trên điện thoại. Hệ điều hành điện thoại cũng có sẵn kho tìm kiếm trên máy (Core Spotlight
trên iOS, AppSearch trên Android) — một điểm "chất liệu" miễn phí.

## 10. Tóm tắt

Trí nhớ agent có bốn loại nội dung (đang làm, sự kiện, sự thật, cách làm) và ba trục thiết kế (bao lâu, lưu bằng gì, ai điều khiển).
Mọi hệ thống là một điểm — hoặc vài điểm — trên bản đồ đó; chọn từ câu hỏi thật, không từ công cụ.

**Thuật ngữ:** working / episodic / semantic / procedural memory · temporal scope (phạm vi thời gian) · substrate (chất liệu) · control policy (chính sách điều khiển).

**Giờ bạn biết thêm:** một bản đồ để đặt mọi hệ thống trí nhớ lên và so sánh chúng cho công bằng — các bài sau đi lần lượt qua từng vùng.

**Bài sau:** [03 — Nhét hết vào ngữ cảnh](03-nhet-het-vao-ngu-canh.md).
