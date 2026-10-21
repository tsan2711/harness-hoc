# 17 — Trí nhớ trong trọng số

> Chuỗi "Triển khai trí nhớ", bài 17/21. Đọc ~9 phút.
> **Bạn đã biết** ([01](01-model-khong-nho.md), [15](15-cap-nhat-mau-thuan-quen.md)–[16](16-tri-nho-cach-lam.md)): model không nhớ giữa các lần
> gọi; mọi trí nhớ tới giờ đều nằm **ngoài** model; cập nhật, xoá lan; trí nhớ cách làm.

## 1. Chuyện mở đầu

Cửa hàng Lá có 2 năm chat với khách. Một người đề xuất: "đừng tìm kiếm gì cả, **huấn luyện** model trên toàn bộ 2 năm chat, cho nó *biết* luôn".
Ba tháng sau: model trả lời đúng giọng cửa hàng, thuộc chính sách đổi trả. Nhưng nó cũng nói nhầm giá cũ (giá đã đổi), và một hôm trả lời khách
A bằng một chi tiết trong đơn của khách B.

## 2. Dừng 30 giây

- Huấn luyện giỏi dạy model **cái gì**: giọng, cách làm, hay sự thật cụ thể?
- Giá đổi — sửa trong file mất một phút. Sửa trong trọng số mất gì?
- Khách B yêu cầu xoá dữ liệu. Xoá khỏi trọng số bằng cách nào?

## 3. Khái niệm

**Trọng số (weights)**: hàng tỉ con số bên trong model, sinh ra từ huấn luyện. Mọi thứ model "biết sẵn" nằm ở đây. Thêm trí nhớ vào trọng số =
**huấn luyện tiếp**.

- **Fine-tuning**: huấn luyện tiếp trên dữ liệu của bạn.
- **LoRA** (và các cách "tiết kiệm tham số" khác): chỉ học thêm một lớp nhỏ bên cạnh, rẻ hơn nhiều, có thể bật/tắt theo người dùng hoặc theo việc.
- **Sửa tri thức trực tiếp** (knowledge editing — ROME, MEMIT): sửa vài trọng số để đổi một sự thật cụ thể. Còn là nghiên cứu; sửa một điều có thể
  làm lệch điều lân cận.
- **Học liên tục** (continual learning): huấn luyện nhiều lần nối tiếp; vấn đề kinh điển là **quên thảm hoạ** (catastrophic forgetting) — học cái
  mới làm hỏng cái cũ.

Câu hỏi 1: huấn luyện dạy tốt **giọng, định dạng, cách làm, kiến thức lĩnh vực chung**; dạy **sự thật cụ thể, hay đổi** thì kém — model có thể
học sai, trộn lẫn, hoặc "nhớ" mà vẫn bịa. Nhiều so sánh thực nghiệm cho thấy với sự thật mới, tìm kiếm + đặt lên bàn thường đáng tin hơn
fine-tuning; hai cách cũng có thể dùng chung.

## 4. Các cách

**A. Không đụng trọng số** (mọi bài trước). *Hợp khi:* hầu hết trường hợp. *Gãy khi:* cần giọng/cách làm mà lời dặn không đủ; bàn chật vì lời dặn quá dài.

**B. Fine-tune / LoRA cho giọng và cách làm.** *Hợp khi:* nhiều ví dụ mẫu tốt; muốn bớt lời dặn dài (rẻ hơn mỗi lượt). *Gãy khi:* cách làm đổi
thường xuyên.

**C. Fine-tune cho sự thật.** *Hợp khi:* kiến thức lĩnh vực ổn định, ít đổi (thuật ngữ y khoa, luật cũ). *Gãy khi:* sự thật đổi (câu hỏi 2: mỗi
lần đổi là một lần huấn luyện + kiểm lại); dữ liệu nhiều người trộn vào một model → lộ chéo (khách A thấy dữ liệu khách B).

**D. LoRA riêng cho từng người/nhóm.** *Hợp khi:* cần cá nhân hoá sâu, ít người. *Gãy khi:* hàng nghìn người → hàng nghìn lớp phải quản; vẫn khó xoá
từng điều trong một lớp.

**E. Chưng cất (distillation) trí nhớ ngoài vào model nhỏ.** Dùng hệ thống trí nhớ ngoài sinh ví dụ, dạy một model nhỏ chạy trên máy. *Hợp khi:*
cần chạy offline/rẻ. *Gãy khi:* như C.

Câu hỏi 3: **"quên" trong trọng số** (machine unlearning) còn là nghiên cứu, chưa có cách đảm bảo. Cách chắc chắn duy nhất hiện nay: huấn luyện lại
từ đầu không có dữ liệu đó — hoặc **không bao giờ đưa dữ liệu cá nhân vào trọng số chung**.

## 5. Bảng một lần nhìn

| | Trí nhớ ngoài (bài 03–16) | Trong trọng số |
|---|---|---|
| Sửa một sự thật | phút | huấn luyện lại + kiểm |
| Xoá theo yêu cầu | xoá + lan (bài 15) | chưa có cách đảm bảo |
| Biết nguồn ("vì sao nói vậy") | ✓ (trỏ về đoạn) | ✗ |
| Tách người dùng | lọc theo id | khó (trừ D) |
| Giá mỗi lượt | token cho phần đặt lên bàn | 0 thêm |
| Giọng, cách làm | lời dặn dài | **tốt** |

**Quy luật:** **trọng số cho cái ổn định và chung** (giọng, kỹ năng, lĩnh vực); **ngoài model cho cái hay đổi, riêng tư, cần nguồn**. Đừng đưa dữ
liệu cá nhân vào trọng số dùng chung.

## 6. Ba kịch bản

- **Cửa hàng Lá:** B cho giọng cửa hàng (từ chat mẫu đã lọc bỏ dữ liệu cá nhân); giá, chính sách, đơn → ngoài model.
- **Nhóm code:** A gần như luôn đủ; code đổi mỗi ngày.
- **Mai:** A; D chỉ khi chạy model trên máy của riêng Mai (dữ liệu không rời máy).

## 7. Scale

- **Nhỏ:** A.
- **Vừa:** B nếu lời dặn quá dài và có ví dụ tốt.
- **Lớn:** B giúp giảm token mỗi lượt cho hàng triệu lượt; C/D thành bài toán vận hành (phiên bản model, kiểm lại sau mỗi lần huấn luyện). Cái vỡ là
  **chu kỳ cập nhật** — thế giới đổi nhanh hơn bạn huấn luyện.

## 8. Bốn nền tảng

- **Windows / Mac:** fine-tune LoRA model nhỏ chạy được trên máy có GPU (Windows/Linux với GPU NVIDIA phổ biến nhất; Mac chip Apple dùng MLX).
- **iOS / Android:** huấn luyện trên điện thoại hạn chế; Apple cho phép gắn *adapter* tuỳ chỉnh vào model trên máy (Foundation Models, huấn luyện
  ở máy tính rồi đóng gói vào app); Android chạy model nhỏ qua AICore/MediaPipe, adapter cũng huấn luyện ngoài máy. Học trên dữ liệu nhiều máy mà
  dữ liệu không rời máy: *federated learning* (Google dùng cho bàn phím Gboard).

## 9. Tóm tắt

Có thể đưa trí nhớ vào trọng số bằng fine-tune, LoRA, sửa tri thức. Nó tốt cho giọng, cách làm, lĩnh vực ổn định; kém cho sự thật hay đổi; gần như
không xoá được; không chỉ ra được nguồn. Hầu hết hệ thống giữ trí nhớ ngoài model, chỉ dùng trọng số cho phần ổn định.

**Thuật ngữ:** weights · fine-tuning · LoRA / adapter · knowledge editing (ROME, MEMIT) · continual learning · catastrophic forgetting · machine unlearning · distillation · federated learning.

**Giờ bạn biết thêm:** đầu kia của trục "chất liệu" — và vì sao nó hiếm khi là lựa chọn đầu tiên.

**Bài sau:** [18 — Nhiều người, nhiều agent](18-nhieu-nguoi-nhieu-agent.md).
