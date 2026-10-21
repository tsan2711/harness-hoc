# 07-01 — Model không nhớ

> Chuỗi 07 "Trí nhớ cho agent, từ viên gạch đầu tiên", bài 1/12. Đọc ~8 phút.
> **Bạn đã biết:** chưa cần biết gì. Chỉ cần từng dùng một chatbot AI (ChatGPT, Claude…).

Cả chuỗi dùng chung một ví dụ: **nhóm Quán Nhỏ** — ba người (Lan trưởng nhóm, Minh, Huy) làm một app đặt món trên điện thoại, có
một **trợ lý AI viết code** (gọi tắt là "agent": AI không chỉ trả lời mà còn tự đọc file, chạy lệnh, sửa code).

## 1. Chuyện mở đầu

Thứ Hai, Lan ngồi với agent cả buổi chiều: thư viện vẽ biểu đồ *ChartLite* làm app giật trên điện thoại Android đời cũ, cả hai thống
nhất bỏ ChartLite, tự vẽ bằng Canvas. Thứ Ba, Lan mở một cửa sổ chat mới: "vẽ biểu đồ doanh thu theo tuần". Agent hăng hái đề xuất…
ChartLite.

Lan nghĩ agent "quên". Thật ra nó **chưa bao giờ nhớ**.

## 2. Dừng 30 giây

Tự nghĩ, không cần trả lời:
- Trong cùng một cuộc chat, vì sao agent vẫn "nhớ" câu bạn nói 20 tin nhắn trước?
- Nếu cứ giữ một cuộc chat dài mãi mãi, chuyện gì xảy ra sau một tháng?
- Ai, hoặc cái gì, nên chịu trách nhiệm nhắc agent rằng "đã bỏ ChartLite"?

## 3. Khái niệm

**Model là một hàm không trạng thái.** Mô hình ngôn ngữ (LLM) giống một chiếc máy tính bỏ túi *không có phím nhớ M+*: đưa vào một
đoạn chữ, nó trả ra đoạn chữ tiếp theo. Xong lần gọi, nó không giữ lại gì. Lần gọi sau bắt đầu từ trắng.

**Vậy sao trong một cuộc chat nó vẫn nhớ?** Vì *ứng dụng chat* gửi lại **toàn bộ** lịch sử mỗi lượt. Tin nhắn thứ 21 của bạn thực ra
được gửi kèm 20 tin trước. Câu hỏi 1: "nhớ" là do app chép lại, không phải do model.

**Ngữ cảnh (context window)** là tờ giấy model nhìn được trong *một* lần gọi: lời dặn hệ thống + lịch sử chat + file agent đã đọc +
câu hỏi mới. Đây là **trí nhớ ngắn hạn**. Mở cửa sổ chat mới = tờ giấy mới.

**Token** là mẩu chữ model đếm (khoảng ¾ từ tiếng Anh; tiếng Việt có dấu thường tốn hơn). Token là hai thứ cùng lúc:
- **Tiền:** nhà cung cấp tính theo token *mỗi lần gọi*. Vì lịch sử bị gửi lại mỗi lượt, lượt thứ 40 trả tiền cho cả 39 lượt trước.
- **Chỗ:** tờ giấy có giới hạn (vài trăm nghìn token). Đầy thì phải cắt hoặc tóm. Và kể cả chưa đầy, tờ giấy càng dày thì model càng
  dễ bỏ sót chi tiết nằm ở giữa — chất lượng giảm trước khi chạm trần.

Câu hỏi 2: chat dài mãi thì đắt dần, chậm dần, rồi bị cắt — và phần bị cắt thường là phần cũ, đúng chỗ có quyết định "bỏ ChartLite".

**Trí nhớ ngoài** là mọi thứ nằm *ngoài* tờ giấy và được đưa vào tờ giấy khi cần. Toàn bộ chuỗi bài này là về nó: ghi ở đâu, tìm lại
thế nào, ai đưa vào, làm sao biết cái nào đã cũ, và đo xem nó có giúp thật không.

## 4. Bốn cách giữ kiến thức qua ngày, thử trên "đã bỏ ChartLite"

**Cách 1 — Một cuộc chat dài mãi.** Không bao giờ mở chat mới.
Ưu: không phải làm gì. Nhược: tiền và độ chậm tăng theo độ dài. Gãy: khi đầy, phần cũ bị cắt; Minh và Huy có cuộc chat riêng, không
thấy gì của Lan.

**Cách 2 — Dán tay một ghi chú đầu mỗi chat.** Lan giữ file "những điều agent cần biết", mỗi sáng dán vào.
Ưu: đơn giản, rõ. Nhược: ghi chú phình dần — 5 dòng thành 500 dòng, mà mỗi chat chỉ cần vài dòng trong đó. Gãy: khi ghi chú to
hơn phần việc thật; khi Lan quên dán.

**Cách 3 — Để model tự tóm cuộc chat cũ** (nhiều app gọi là "nén" hay "compact").
Ưu: tự động, giữ được ý chính. Nhược: tóm là chọn bỏ — chi tiết "vì máy Android đời cũ" có thể rơi mất. Gãy: tóm nhiều lần thì sai
số cộng dồn, như photocopy bản photocopy.

**Cách 4 — Trí nhớ ngoài + lấy lại phần cần.** Kiến thức nằm ngoài (file, cơ sở dữ liệu); mỗi lần chỉ đưa vào tờ giấy vài đoạn liên
quan tới việc đang làm.
Ưu: tờ giấy gọn, ba người dùng chung một kho. Nhược: phải giải được ba bài khó — *ghi gì*, *tìm thế nào*, *ai đưa vào*. Gãy: khi
tìm sai đoạn, hoặc không ai bấm tìm.

## 5. Bảng một lần nhìn

| | Qua ngày | Chia cho cả nhóm | Chi phí mỗi lượt | Gãy khi |
|---|---|---|---|---|
| 1. Chat dài mãi | ✓ tới khi đầy | ✗ | tăng dần | đầy → mất phần cũ |
| 2. Dán ghi chú tay | ✓ | ~ (chép cho nhau) | tăng theo ghi chú | ghi chú phình, quên dán |
| 3. Tự tóm | ✓ | ✗ | vừa | tóm sai, mất "vì sao" |
| 4. Trí nhớ ngoài | ✓ | ✓ | thấp, ổn định | tìm sai / không ai tìm |

**Quy luật:** ngữ cảnh là **mặt bàn làm việc**, không phải **tủ hồ sơ**. Bàn nhỏ và đắt; tủ to và rẻ; việc khó là lấy đúng tờ từ tủ
đặt lên bàn đúng lúc.

## 6. Scale — to lên thì cái gì vỡ

- **Nhỏ** (một người, vài ngày): cách 2 là đủ.
- **Vừa** (nhóm 3 người, vài tháng): ghi chú tay phình tới mức không ai đọc hết; mỗi người một agent, kiến thức không chảy qua nhau.
- **Lớn** (nhiều agent chạy song song cả ngày): mỗi agent một tờ giấy riêng, không cái nào thấy của cái nào. Không có trí nhớ ngoài
  chung thì cùng một sai lầm được lặp lại ở mọi phiên. Cái vỡ trước không phải dung lượng mà là **kiến thức không tới được đúng chỗ**.

## 7. Bốn nền tảng

Model chạy trên máy chủ nên **giống hệt** dù bạn gọi từ Windows, Mac, iOS hay Android — nó không nhớ ở đâu cả. Khác nhau là *app*:
app chat trên điện thoại và máy tính lưu lịch sử trên cloud hoặc trên máy, và tính năng "Memory" của các app chat chính là một dạng
trí nhớ ngoài (cách 4, thường kèm cách 3). Model chạy *ngay trên máy* (loại nhỏ trên iPhone, điện thoại Android đời mới, hay Mac/PC
có GPU) có tờ giấy nhỏ hơn nhiều — nên trí nhớ ngoài càng quan trọng.

## 8. Tóm tắt

Model không nhớ gì giữa các lần gọi; "nhớ trong cuộc chat" là app gửi lại lịch sử; muốn nhớ qua ngày và chia cho cả nhóm thì phải có
trí nhớ ngoài và cách đưa đúng phần vào ngữ cảnh.

**Thuật ngữ:** LLM · stateless (không trạng thái) · context window (ngữ cảnh) · token · compaction (nén/tóm) · external memory (trí nhớ ngoài).

**Giờ bạn biết thêm:** vì sao agent "quên", token là tiền và chỗ, và bốn cách giữ kiến thức — cách 4 là đường cả chuỗi sẽ đi.

---

> **Ví dụ thật: Seriously làm thế này** *(đọc bỏ qua vẫn hiểu bài)*
>
> Seriously là một kho code (monorepo) chứa ba game Unity, do một người (Bi) điều hành và **hàng chục phiên agent mỗi ngày** làm
> việc — mỗi "phòng" (art, QA, từng game…) một phiên riêng. Mỗi phiên bắt đầu từ tờ giấy trắng, đúng như bài này.
> - Cách 2 có thật: mỗi thư mục có file `CLAUDE.md` mà công cụ tự đọc đầu phiên. Nó từng phình to, nên giờ có luật giữ ngắn và trỏ
>   sang file chi tiết.
> - Cách 3 có thật: khi ngữ cảnh vượt ~120k token, phiên phải ghi bàn giao rồi xoá ngữ cảnh làm lại — vì phiên dài vừa đắt vừa kém.
> - Chuyện kiểu "ChartLite" có thật: Bi đã bỏ một cách vẽ (CPU tính ma trận + `RenderMeshInstanced`) vì chậm, chuyển sang VFX Graph.
>   Phiên sau không biết thì sẽ đề xuất lại đúng cách đã bỏ. Phần còn lại của chuỗi là cách Seriously chống chuyện đó.

**Bài sau:** [07-02 — Ghi ra ngoài](07-02-ghi-ra-ngoai.md).
