# Bài A03 — Từ "gõ từng câu" sang "vòng lặp tự chạy": mục tiêu, người kiểm, và cái phanh

> **Bạn đã biết:** agent là một vòng lặp (model xin việc → chương trình bao quanh làm → kết quả quay lại model), model không nhớ gì
> giữa các phiên, và mỗi vòng dài thêm thì tốn tiền hơn (bài A01–A02).
> Bài này kể **vòng lặp thứ hai nằm bên ngoài** vòng lặp đó. Nguồn ý tưởng: bài 13 của khóa *learn-harness-engineering*
> (walkinglabs, MIT) và bài viết "Loop Engineering" của Addy Osmani; phần so sánh và ví dụ thật là của mình.

## 1. Câu chuyện: Minh và 40 lỗi đỏ

Minh có một dự án với 40 test đang đỏ. Cô giao cho trợ lý AI: "Sửa test A." Trợ lý sửa xong. Minh đọc, gõ: "Giờ test B." Rồi C.
Đến test thứ 9 là 11 giờ đêm. Minh nhận ra: trợ lý chạy rất nhanh, nhưng **Minh mới là cái đồng hồ** — không có Minh gõ "tiếp", không có gì chạy.

Hôm sau cô thử cách khác: "Cứ sửa cho đến khi cả 40 test xanh, rồi dừng." Cô đi ngủ. Sáng ra: 38 test xanh,
2 test còn đỏ — và **trợ lý báo "xong hết"**, vì nó tự đọc lại và thấy mình làm tốt.

Hai chuyện, hai bài học: (1) có thể giao *đích* thay vì giao *từng bước*; (2) nhưng ai là người nói "đã tới đích"?

## 2. Dừng 30 giây — tự nghĩ, không cần trả lời ai

- Giao "sửa đến khi xanh" thì thiếu những mảnh nào để việc đó **không** chạy mãi, không đốt hết tiền, và không nói dối "xong"?
- Trợ lý vừa viết code vừa chấm code của chính nó. Bạn nghĩ nó chấm mình **khắt khe hay dễ dãi**? Vì sao?
- Nếu vòng lặp tự chạy lúc bạn ngủ và làm hỏng giữa chừng, sáng ra bạn cần thấy **gì** trên đĩa để biết nó đang dở ở đâu?

(Đáp án ở các mục sau.)

## 3. Ba mảnh tối thiểu của một vòng tự chạy

Khóa học gọi đó là `/goal`, nhưng ý tưởng độc lập với lệnh nào:

| | Gõ từng câu | Vòng tự chạy |
|---|---|---|
| Bạn đưa | việc kế tiếp | **trạng thái cuối mong muốn** |
| Agent làm | một lượt | lặp đến khi đạt |
| Ai phán "xong" | bạn | **một điều kiện kiểm được bằng máy** |
| Bạn đi được lúc nào | không | ngay sau khi giao |

Ba mảnh: **(1) đích**, **(2) cách kiểm**, **(3) điều kiện dừng** (đạt đích *hoặc* chạm trần). Thiếu mảnh nào cũng hỏng:
thiếu (2) → "tự thấy xong"; thiếu (3) → chạy vô hạn; thiếu (1) → chạy mà không biết đang đi đâu.

Phân biệt hai loại hay bị nhầm: **việc có đích** (làm hệ thống thanh toán — mỗi vòng tiến gần đích hơn) khác **việc canh gác**
("cứ 15 phút xem CI có đỏ không" — mỗi lần độc lập, không tích lũy). Mẹo một câu: *việc này có kết thúc không?* Có → vòng theo đích.
Không → vòng theo giờ. Nhét việc có đích vào vòng theo giờ là lỗi kinh điển: mỗi lần chạy lại bắt đầu từ vạch xuất phát, không nhớ lần trước.

## 4. Năm cách để cùng giải "40 test đỏ"

**Cách 1 — Người gõ từng câu (không vòng ngoài).** Chính là Minh đêm đầu.
Ưu: kiểm soát tuyệt đối, rẻ. Nhược: người là nút cổ chai. **Gãy ở:** việc dài hơn một buổi.

**Cách 2 — Hẹn giờ, lặp cùng một câu lệnh.** "Mỗi 30 phút: chạy test, sửa cái đỏ."
Ưu: đơn giản, hợp việc canh gác. Nhược: mỗi lần là một đầu óc mới, không nhớ lần trước đã thử gì. **Gãy ở:** lỗi khó — nó thử lại đúng cách đã thất bại, mãi.

**Cách 3 — Đích + tự chấm.** Giao đích, chính phiên làm việc tự phán xong chưa.
Ưu: chạy được cả đêm. Nhược: **người làm là luật sư biện hộ giỏi nhất cho sản phẩm của mình** — nó đã tự thuyết phục mình trong lúc viết,
nên đọc lại chỉ thấy lý lẽ của chính nó. Đây là chuyện của 2 test đỏ bị báo "xong". **Gãy ở:** mọi lúc bạn không có mặt để bắt.

**Cách 4 — Đích + người kiểm độc lập.** Một phiên khác (lời nhắc khác, đôi khi model khác) chỉ có việc kiểm; trượt thì trả về làm lại.
Ưu: đây là mảnh bảo đảm độ tin cậy lớn nhất. Nhược: tốn thêm một phiên mỗi vòng; nếu người kiểm chỉ "đọc và gật" thì vẫn vô dụng — nó phải **chạy** thứ kiểm được.
**Gãy ở:** kiểm kiểu "trông ổn" thay vì kiểm bằng lệnh có kết quả đỏ/xanh.

**Cách 5 — Nhiều vòng song song, chung bộ nhớ ngoài.** Mỗi nhánh làm trong thư mục riêng để không giẫm file nhau, ghi tiến độ vào một file chung.
Ưu: nhanh. Nhược: phải thiết kế va chạm, trần chi phí nhân lên. **Gãy ở:** khi không có cái phanh tổng — 5 vòng cùng đốt tiền.

| Cách | Ai phán xong | Chạy khi bạn ngủ | Rủi ro chính |
|---|---|---|---|
| 1 người gõ | bạn | không | nút cổ chai là bạn |
| 2 hẹn giờ | bạn | có | lặp lại cách đã thất bại |
| 3 tự chấm | chính người làm | có | **báo "xong" sai** |
| 4 người kiểm riêng | phiên độc lập | có | tốn thêm; kiểm hời hợt |
| 5 song song | phiên độc lập | có | va chạm + chi phí nhân lên |

**Quy luật:** *Càng ít người trông, càng cần (a) điều kiện dừng kiểm bằng máy và (b) một thành viên "không tin" người làm.*

## 5. Sáu mảnh ghép của một vòng (để biết khi nào chạm vào mảnh nào)

1. **Hẹn giờ / sự kiện** — ai bấm nút bắt đầu. 2. **Thư mục làm việc riêng** — để vòng song song không ghi đè nhau.
3. **Kỹ năng đóng gói** — đừng giải thích lại dự án mỗi lần. 4. **Cầu nối ra công cụ thật** — mở PR, đọc ticket.
5. **Người làm tách người kiểm.** 6. **Bộ nhớ ngoài** — một file trên đĩa ghi "xong gì, dở gì, kẹt gì". Model quên, repo thì không.
Mảnh 6 là xương sống: không có nó thì sáng ra bạn không biết đêm qua đã làm gì (đó là đáp án câu thứ ba ở mục 2).

## 6. Scale: vòng nhỏ / vừa / lớn thì cái gì vỡ?

- **Nhỏ (một việc, vài vòng):** hầu như không vỡ. Rủi ro duy nhất là cách 3 — tự chấm.
- **Vừa (hàng chục vòng, nhiều giờ):** vỡ ở **chi phí ngữ cảnh** (mỗi vòng đọc lại lịch sử, tổng tăng gần bình phương — bài A02) và ở **bộ nhớ**: không ghi ra file thì hết phiên là mất.
- **Lớn (nhiều vòng song song, chạy nhiều ngày):** vỡ ở **bốn chi phí ngầm**, không hiện ngay mà tích lũy:
  1. *Nợ kiểm chứng* — "trông ổn" chồng chất; điều kiện dừng phải là lệnh đỏ/xanh.
  2. *Mục nát hiểu biết* — vòng đẩy code nhanh hơn bạn đọc kịp; bạn dần không còn hiểu dự án của mình.
  3. *Đầu hàng nhận thức* — vòng chạy trơn tru thì dễ thôi có ý kiến. Osmani: hai người dựng cùng một vòng, một người dùng nó để đi nhanh
     hơn trong việc mình hiểu, người kia dùng để khỏi phải hiểu — vòng không phân biệt được, bạn phải tự biết.
  4. *Nổ token.*
  Điểm chung: lỗi lớn nhất ở quy mô lớn là **chất lượng và sự hiểu biết**, không phải dung lượng.

Thang trưởng thành (khóa học): 1 giao đích có điều kiện dừng → 2 một việc hẹn giờ → 3 tách làm/kiểm + thư mục riêng → 4 vòng tự tìm việc kế
từ bộ nhớ ngoài → 5 nhiều vòng chạy song song chung bộ nhớ. Đa số nhóm đang ở 2–3; đừng nhảy tới 5 khi chưa kiểm được bằng máy.

## 7. Ví dụ thật: Seriously làm thế này (bỏ qua vẫn hiểu bài)

Mở `tools/company/dispatch.py` (đoạn docstring đầu file) và `company/policy.toml`. Đối chiếu từng mảnh:

| Khái niệm | Trong Seriously |
|---|---|
| Đích + cách kiểm | `kit company send … --check <lệnh\|review>` — việc có kèm cách nghiệm thu |
| Người làm ≠ người kiểm | `check: review` → phiên của **bộ phận gửi** (không phải bộ phận làm) chạy `accept` hoặc `reject` |
| Bộ nhớ ngoài | file việc trong hộp thư (`status`, `result:`, `retried`, `reopened`) + `events.jsonl` |
| Chuỗi phụ thuộc | `--after <việc>`: việc sau chỉ mở khi việc trước xong |
| Cái phanh | song song 3 · độ sâu 3 · 30 phiên/ngày · 45 phút/phiên · bị trả quá 2 lần thì dừng chờ người |
| Phiên chết | không `done` thì mở lại **một lần** kèm lý do; lần hai vẫn không xong → `blocked`, không treo |
| Việc cần người | tiền, xóa dữ liệu → `done --blocked`, không tự quyết |

Hai chỗ để bạn tự mở file kiểm chứng và **tự hỏi** (mình chưa kết luận là lỗ hổng):
- Điều kiện dừng đa số là `review` — người kiểm là một phiên model. Khi việc không có lệnh đỏ/xanh (ví dụ "ảnh đẹp chưa"), "nợ kiểm chứng" nằm ở đâu?
  (Bộ nhớ của bạn nói bạn không còn tự chơi thử — vậy ai là thành viên "không tin" cuối cùng?)
- Bốn chi phí ngầm: cái nào đã có số đo (token: có `dispatch report`), cái nào chưa (mục nát hiểu biết)?

## 8. Bốn nền tảng

Phần "đích + kiểm + dừng" là logic, **chạy giống nhau** mọi nơi. Khác ở chỗ *ai bấm giờ*:

- **Mac:** `launchd`/`cron`, hoặc chạy nền như Seriously. Máy ngủ thì vòng ngủ theo.
- **Windows:** Task Scheduler; chú ý đường dẫn và quyền chạy nền.
- **iOS:** gần như không có tiến trình nền tự do — vòng thật sự chạy ở máy khác/đám mây; điện thoại chỉ để xem kết quả và duyệt.
- **Android:** chạy thật được trong terminal kiểu Termux nhưng hệ điều hành hay giết tiến trình nền; thực tế cũng thường để vòng chạy ở nơi khác.

Quy tắc chung: vòng tự chạy nên ở **máy bật 24/24 hoặc đám mây**; điện thoại là chỗ *duyệt*, không phải chỗ *chạy*.

## Tóm tắt một dòng

Vòng tự chạy = **đích + cách kiểm bằng máy + điều kiện dừng**, người làm tách khỏi người kiểm, bộ nhớ ghi ra đĩa, và có phanh tổng.

**Giờ bạn biết thêm:** 3 mảnh tối thiểu; vì sao tự chấm là cái bẫy; 6 mảnh ghép; 4 chi phí ngầm; thang trưởng thành 1–5.

**Bài sau (A04):** vòng không còn là một đường thẳng — khi việc rẽ nhánh, hợp lại, phải chọn đường: **đồ thị công việc** (nút, cạnh, trạng thái chung, định tuyến).

**Thuật ngữ:** vòng ngoài (outer loop) · điều kiện dừng (stopping condition) · tách làm/kiểm (generator–evaluator separation) · bộ nhớ ngoài (external state) · nợ kiểm chứng (verification debt).
