# 01 — Model không nhớ

> Chuỗi "Triển khai trí nhớ", bài 1/21. Đọc ~9 phút.
> **Bạn đã biết:** dùng một chatbot AI bất kỳ (ChatGPT, Claude, Gemini…). Không cần biết gì thêm.

## 1. Chuyện mở đầu — ba lần quên trong một ngày

- **Mai** hôm qua kể với trợ lý AI: "mình dị ứng tôm". Sáng nay mở cuộc chat mới, hỏi "tối nay nấu gì?". Trợ lý gợi ý… tôm rang me.
- **Cửa hàng Lá** có chatbot trả lời khách. Một khách nhắn lần thứ ba về đơn hàng giao trễ; chatbot lại hỏi "anh/chị cho em xin mã đơn".
  Khách bỏ đi.
- **Nhóm 3 người** dùng agent viết code. Tuần trước cả nhóm đã bỏ thư viện vẽ biểu đồ ChartLite vì chạy giật trên điện thoại cũ. Hôm
  nay agent mở phiên mới và đề xuất… cài ChartLite.

Ba chuyện, cùng một nguyên nhân.

## 2. Dừng 30 giây

- Đoán xem: sau cuộc chat hôm qua, bên trong model có gì thay đổi không?
- Vậy vì sao vài app chat *có vẻ* nhớ bạn qua nhiều tuần?
- Cách "dễ" nhất là mỗi lần dán lại toàn bộ lịch sử chat. Thử hình dung nó gãy ở đâu sau một năm.

## 3. Model là một hàm, không phải một người

Một model ngôn ngữ lớn (LLM) làm đúng một việc: **nhận một đoạn chữ, trả ra một đoạn chữ tiếp theo**. Những gì nó "biết" nằm trong
**trọng số** (weights) — hàng tỉ con số được chỉnh *một lần* lúc huấn luyện, rồi **đóng băng**. Lúc bạn chat, không con số nào thay đổi.

Vì thế model là **không trạng thái** (stateless): như một máy tính bỏ túi — bấm `2 + 3` ra `5`, tắt đi bật lại không nhớ phép tính cũ.
Câu hỏi 1: sau cuộc chat hôm qua, model **không đổi gì cả**.

**Ngữ cảnh (context window)** là toàn bộ đoạn chữ model được đọc trong *một* lần trả lời — như mặt bàn làm việc: cái gì nằm trên bàn
thì dùng được, cái gì không thì coi như không tồn tại. Mặt bàn có giới hạn: từ vài nghìn **token** (model nhỏ chạy trên điện thoại) tới
khoảng một triệu token (model lớn trên máy chủ, 2026).

**Token** là mẩu chữ model đọc — khoảng ¾ từ tiếng Anh, tiếng Việt thường tốn hơn. Token là **tiền** (trả theo số token đọc + viết) và là
**chỗ** (mặt bàn chỉ chứa từng ấy). Đọc nhiều hơn cũng **chậm** hơn.

Câu hỏi 2: app "có vẻ nhớ" là vì **một chương trình bên ngoài model** đã lặng lẽ đặt lên bàn vài dòng chữ trước khi model đọc — ví dụ
"Người dùng tên Mai, dị ứng tôm". Model không nhớ; **chương trình bao quanh** nhớ hộ.

## 4. Trí nhớ = một vòng ba bước

Mọi hệ thống trí nhớ cho agent, dù đơn giản hay phức tạp, đều là một vòng ([arXiv 2603.07670](https://arxiv.org/abs/2603.07670)):

```
  cuộc trò chuyện / việc đang làm
        │
        ▼ GHI      chọn cái gì đáng giữ, lưu ở đâu
   [ kho trí nhớ ]
        │ QUẢN LÝ  gộp, sửa, đánh dấu cũ, quên
        ▼ ĐỌC      lúc nào lấy, lấy gì, đặt bao nhiêu lên bàn
  ngữ cảnh lần sau ──▶ model
```

Cả chuỗi bài này chỉ là trả lời ba câu: **ghi gì · quản lý thế nào · đọc lúc nào**, cho từng loại bài toán.

## 5. Ba chỗ có thể chứa trí nhớ

| Chỗ | Ví dụ | Đổi nhanh? | Đọc được bằng mắt? | Giá |
|---|---|---|---|---|
| **Trong ngữ cảnh** | dán lại lịch sử, dán "hồ sơ" đầu cuộc chat | tức thì | ✓ | token mỗi lần |
| **Kho bên ngoài** | file ghi chú, bảng dữ liệu, kho tìm kiếm | tức thì | tuỳ kho | lưu trữ + công tìm |
| **Trong trọng số** | huấn luyện thêm (fine-tune) trên dữ liệu của bạn | chậm (giờ–ngày) | ✗ | huấn luyện, khó sửa/xoá |

Hai chỗ đầu cuối cùng đều phải **đi qua ngữ cảnh** — kho ngoài chỉ có ích khi một phần của nó được lấy ra và đặt lên bàn.

## 6. Năm cách tối thiểu, thử trên chuyện của Mai

**A. Không làm gì.** Mỗi cuộc chat bắt đầu trắng. *Hợp khi:* câu hỏi một lần, hoặc riêng tư là trên hết (không lưu gì = không lộ gì).
*Gãy khi:* người dùng phải kể lại từ đầu mỗi lần.

**B. Dán lại toàn bộ lịch sử.** *Hợp khi:* lịch sử ngắn (vài chục lượt). *Gãy khi* (câu hỏi 3): sau một năm, lịch sử dài hơn mặt bàn →
không vừa; trước cả lúc đó, mỗi câu hỏi phải trả tiền đọc lại cả năm, chậm dần; và model có xu hướng bỏ sót chi tiết nằm giữa đoạn rất dài
(bài 03).

**C. Người dùng tự viết một "hồ sơ" luôn được dán đầu chat** (nhiều app gọi là *custom instructions*). Mai viết: "dị ứng tôm, ăn chay
thứ Hai". *Hợp khi:* vài sự thật ổn định, người dùng chịu viết. *Gãy khi:* người dùng quên cập nhật; hồ sơ dài dần; không chứa được
"chuyện đã xảy ra" (hôm qua kể gì).

**D. Chương trình tự ghi lại và tự đặt lại lên bàn.** Sau mỗi cuộc chat, chương trình giữ lại vài thứ (bằng luật, bằng LLM, hoặc để agent
tự quyết — bài 13); lần sau lấy ra cái liên quan (bài 09–14). *Hợp khi:* nhiều cuộc chat, dữ liệu lớn dần. *Gãy khi:* ghi sai, lấy sai,
hoặc lấy ra cái đã cũ (bài 15) — và giờ bạn có một hệ thống phải bảo trì.

**E. Dạy lại model.** Huấn luyện thêm trên lịch sử của Mai. *Hợp khi:* cần đổi *cách* model cư xử (giọng văn, thói quen) chứ không phải
nhớ *sự thật* cụ thể (bài 17). *Gãy khi:* Mai đổi ý — "giờ mình hết dị ứng rồi" — sửa một sự thật trong hàng tỉ con số rất khó; và
không ai đọc được model đang "nhớ" gì.

## 7. Bảng một lần nhìn

| Cách | Công làm | Giá mỗi câu | Sửa/xoá một điều | Đọc kiểm được | Chỗ gãy chính |
|---|---|---|---|---|---|
| A. Không gì | 0 | thấp | — | — | quên hết |
| B. Dán cả lịch sử | 0 | tăng theo thời gian | sửa lịch sử | ✓ | mặt bàn đầy, chậm, đắt |
| C. Hồ sơ tay | người dùng | thấp | ✓ dễ | ✓ | không ai cập nhật |
| D. Tự ghi + tự lấy | xây hệ thống | thấp–vừa | tuỳ thiết kế | tuỳ thiết kế | ghi sai, lấy sai, lấy cái cũ |
| E. Dạy lại model | huấn luyện | thấp | ✗ khó | ✗ | không sửa, không kiểm được |

**Quy luật:** không có cách tốt nhất — chỉ có cách hợp với **nhớ gì, bao lâu, cho ai, sai thì hậu quả gì**.

## 8. Ba kịch bản cần khác nhau

| | A. Mai | B. Cửa hàng Lá | C. Nhóm code |
|---|---|---|---|
| Nhớ cho ai | 1 người | hàng nghìn khách, mỗi người riêng | 3 người + agent, dùng chung |
| Nhớ gì chủ yếu | sở thích, chuyện đã kể | đơn hàng, khiếu nại, thông tin cá nhân | quyết định, tài liệu, cái gì đã bị thay |
| Sai thì sao | khó chịu (hoặc nguy hiểm: dị ứng) | mất khách, lộ dữ liệu | sửa lại code, mất ngày công |
| Cần nhanh cỡ nào | vài giây ổn | rất nhanh | vài giây ổn |
| Có sẵn dữ liệu có cấu trúc? | ít | có (hệ thống đơn hàng) | có (git, file tài liệu) |

Bạn sẽ thấy ở các bài sau: cùng một câu hỏi "lưu ở đâu?", ba kịch bản này thường chọn ba đáp án khác nhau.

## 9. Scale

- **Nhỏ** (một người, vài tuần): B hoặc C là đủ; xây D là thừa.
- **Vừa** (một người nhiều năm, hoặc một nhóm): B vỡ vì mặt bàn; C vỡ vì không ai cập nhật → bắt đầu cần D.
- **Lớn** (hàng nghìn người dùng): D bắt buộc, và câu hỏi chuyển từ "nhớ thế nào" sang "nhớ **của ai**, ai được xem, xoá thế nào" (bài 18).

## 10. Bốn nền tảng

- **Windows / Mac:** app chat trên máy tính và agent viết code thường lưu trí nhớ dạng file trên ổ đĩa của bạn; cũng chạy được model
  trên máy (Ollama, LM Studio) — khi đó dữ liệu không rời máy, nhưng model nhỏ hơn và mặt bàn hẹp hơn.
- **iOS:** có model chạy ngay trên máy (framework Foundation Models của Apple), mặt bàn chỉ vài nghìn token — nên cách B gãy rất sớm,
  phải chọn lọc kỹ cái đặt lên bàn. Dữ liệu app nằm trong vùng riêng (sandbox) của app.
- **Android:** tương tự với Gemini Nano chạy trên máy (qua AICore / ML Kit), và cùng giới hạn mặt bàn nhỏ.
- **Chung:** trí nhớ là **dữ liệu cá nhân**. Trên điện thoại, giữ trên máy vs gửi lên máy chủ là quyết định riêng tư đầu tiên phải chốt.

## 11. Tóm tắt

Model là hàm không trạng thái; "trí nhớ" là việc của chương trình bao quanh, đi qua vòng **ghi → quản lý → đọc**, và cuối cùng mọi thứ
phải được đặt lên mặt bàn ngữ cảnh có giới hạn. Có ba chỗ chứa (ngữ cảnh, kho ngoài, trọng số) và không chỗ nào thắng mọi bài toán.

**Thuật ngữ:** LLM · weights (trọng số) · stateless (không trạng thái) · context window (ngữ cảnh / mặt bàn) · token · custom instructions (hồ sơ dán đầu chat) · fine-tune (huấn luyện thêm) · write–manage–read (ghi–quản lý–đọc).

**Giờ bạn biết thêm:** "trí nhớ" của agent thật ra là bài toán gì, ba chỗ nó có thể nằm, và vì sao ba kịch bản Mai / cửa hàng Lá / nhóm
code sẽ cần ba lời giải khác nhau.

**Bài sau:** 02 — Bản đồ lựa chọn (chưa viết).
