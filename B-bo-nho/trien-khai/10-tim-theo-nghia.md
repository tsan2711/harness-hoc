# 10 — Tìm theo nghĩa

> Chuỗi "Triển khai trí nhớ", bài 10/21. Đọc ~9 phút.
> **Bạn đã biết** ([07](07-kho-vector.md), [09](09-tim-theo-chu.md)): embedding, chia đoạn, kho vector, HNSW; tìm theo chữ giỏi mã/tên, mù
> diễn đạt lại; vector ngược lại.

## 1. Chuyện mở đầu

Cửa hàng Lá bật tìm theo nghĩa cho lịch sử chat với khách. Khách hỏi "shop có đổi size không?". Kết quả đầu: một đoạn chat về "đổi màu áo"
(gần nghĩa: "đổi"). Kết quả thứ hai đúng: chính sách đổi trả. Một khách khác viết "sz M có ko", hệ thống không tìm ra gì hợp — model
embedding không hiểu "sz" và tiếng Việt không dấu viết tắt.

## 2. Dừng 30 giây

- Câu hỏi ngắn, tài liệu dài — hai thứ "trông" khác hẳn nhau. Có cách nào làm câu hỏi giống tài liệu hơn trước khi tìm?
- Kho vector *luôn* trả về k kết quả gần nhất — kể cả khi không có cái nào đúng. Hậu quả gì khi đặt chúng lên bàn?
- Chọn model embedding bằng bảng xếp hạng công khai, hay bằng gì?

## 3. Bốn chỗ quyết định chất lượng

**1. Model embedding.** Có model chỉ giỏi tiếng Anh; có model **đa ngữ**. Bảng xếp hạng công khai (MTEB) đo trên dữ liệu chung — dữ liệu
của bạn (tiếng Việt chat, viết tắt, mã sản phẩm) có thể cho thứ hạng khác hẳn (câu hỏi 3: thử trên 30–50 câu thật của bạn, bài 19). Một số
model được huấn luyện riêng cho cặp *câu hỏi ↔ tài liệu* (cần thêm tiền tố như "query:" / "passage:" — đọc tài liệu của model).

**2. Chia đoạn** (bài 07): theo tiêu đề/đoạn văn tốt hơn cắt đều theo số ký tự; thêm tiêu đề tài liệu vào đầu mỗi mẩu giúp mẩu "biết mình
thuộc về đâu" (cách *contextual chunk*: chèn một câu mô tả mẩu nằm trong tài liệu nào, ý gì).

**3. Viết lại câu hỏi** (câu hỏi 1).
- **Mở rộng**: thêm từ đồng nghĩa, sửa viết tắt ("sz" → "size").
- **HyDE**: nhờ LLM viết một *câu trả lời giả định*, rồi nhúng câu đó để tìm — câu trả lời giả "trông giống" tài liệu hơn câu hỏi.
- **Tách câu hỏi**: câu hỏi kép thành hai câu đơn, tìm riêng.
Tất cả tốn thêm một lần gọi LLM (tiền + độ trễ).

**4. Ngưỡng và số lượng** (câu hỏi 2). Không đặt ngưỡng → luôn có k kết quả, kể cả rác; model đọc rác và có thể trả lời sai một cách tự tin.
Ngưỡng điểm (ví dụ chỉ lấy cosine > một mức) giúp **im lặng khi không chắc** — nhưng mức ngưỡng khác nhau theo từng model, phải chỉnh trên dữ
liệu thật.

## 4. Các cách

**A. Vector thuần, model mặc định.** *Hợp khi:* thử nhanh, nội dung tiếng Anh đời thường. *Gãy khi:* tiếng Việt, viết tắt, mã.

**B. Model đa ngữ chọn theo dữ liệu mình.** *Hợp khi:* nội dung không phải tiếng Anh. *Gãy khi:* đổi model sau này → nhúng lại toàn bộ.

**C. + viết lại câu hỏi.** *Hợp khi:* câu hỏi ngắn, mơ hồ. *Gãy khi:* cần nhanh (thêm một lần gọi LLM); LLM viết lại sai hướng.

**D. + ngưỡng im lặng.** *Hợp khi:* đẩy kết quả tự động lên bàn (bài 14). *Gãy khi:* ngưỡng chỉnh sai → im quá nhiều hoặc rác quá nhiều.

**E. Huấn luyện lại model embedding trên dữ liệu mình.** Cặp câu hỏi–tài liệu đúng của bạn. *Hợp khi:* nhiều dữ liệu cặp, lĩnh vực rất riêng.
*Gãy khi:* ít dữ liệu; mỗi lần huấn luyện là nhúng lại.

## 5. Bảng một lần nhìn

| Cách | Thêm tiền mỗi câu | Thêm độ trễ | Cải thiện | Gãy khi |
|---|---|---|---|---|
| A. Mặc định | 0 | 0 | — | tiếng Việt, mã |
| B. Đa ngữ đúng dữ liệu | 0 | 0 | lớn nếu không phải tiếng Anh | đổi model |
| C. Viết lại câu hỏi | 1 lần LLM | +0,3–2 s | câu ngắn/mơ hồ | cần nhanh |
| D. Ngưỡng | 0 | 0 | ít rác | chỉnh ngưỡng |
| E. Huấn luyện lại | huấn luyện | 0 | lĩnh vực riêng | ít dữ liệu |

**Quy luật:** chất lượng tìm theo nghĩa nằm ở **model hợp dữ liệu** và **đoạn chia hợp lý** nhiều hơn ở cơ sở dữ liệu vector; và luôn cần cách
nói "không có gì phù hợp".

## 6. Ba kịch bản

- **Mai:** chat đời thường tiếng Việt, nhiều diễn đạt lại → tìm theo nghĩa là lớp chính; B + D.
- **Cửa hàng Lá:** câu hỏi khách ngắn, viết tắt → B + mở rộng câu hỏi bằng bảng viết tắt (rẻ hơn HyDE); mã đơn vẫn đi đường tra bảng.
- **Nhóm code:** mã và tên chiếm nhiều → tìm theo nghĩa là lớp *bổ sung* cho câu diễn đạt lại.

## 7. Scale

- **Nhỏ:** A/B, so từng điểm.
- **Vừa:** B + D; bắt đầu đo trên câu thật.
- **Lớn:** đoạn gần nhau rất nhiều → kết quả đầu đầy "hàng xóm gần nhưng sai"; cần xếp lại (bài 11). Cái vỡ là **độ phân biệt** giữa các
  đoạn gần như trùng (bản cũ vs bản mới).

## 8. Bốn nền tảng

- **Windows / Mac:** model embedding đa ngữ cỡ vừa chạy CPU được; HyDE cần LLM — trên máy hoặc gọi dịch vụ.
- **iOS / Android:** embedding trên máy thường nhỏ, ít ngôn ngữ hơn → kiểm kỹ tiếng Việt; gọi dịch vụ embedding thì thêm độ trễ mạng mỗi câu
  hỏi. Viết lại câu hỏi bằng LLM trên máy được, nhưng cộng thêm thời gian chờ người dùng thấy.

## 9. Tóm tắt

Tìm theo nghĩa tốt hay dở chủ yếu do model embedding có hợp dữ liệu không, đoạn chia có hợp không, câu hỏi có cần viết lại không, và có
ngưỡng để im khi không chắc không.

**Thuật ngữ:** multilingual embedding · MTEB · query/passage prefix · contextual chunk · query expansion · HyDE · similarity threshold · fine-tuned embedding.

**Giờ bạn biết thêm:** những núm chỉnh thật sự quyết định tìm theo nghĩa, và cách chọn chúng theo dữ liệu của mình.

**Bài sau:** [11 — Lai và xếp lại](11-lai-va-xep-lai.md).
