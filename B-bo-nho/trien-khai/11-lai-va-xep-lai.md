# 11 — Lai và xếp lại

> Chuỗi "Triển khai trí nhớ", bài 11/21. Đọc ~9 phút.
> **Bạn đã biết** ([09](09-tim-theo-chu.md)–[10](10-tim-theo-nghia.md)): tìm theo chữ giỏi mã/tên, mù diễn đạt lại; tìm theo nghĩa ngược lại;
> ngưỡng im lặng; viết lại câu hỏi.

## 1. Chuyện mở đầu

Nhóm code có cả hai: tìm chữ và tìm nghĩa. Câu "TS2345 ở payment" — tìm chữ đúng, tìm nghĩa sai. Câu "hồi trước sao mình bỏ thư viện biểu đồ?"
— tìm nghĩa đúng, tìm chữ sai. Minh viết: "lấy 5 kết quả mỗi bên, cộng điểm lại". Kết quả tệ hơn cả hai: điểm BM25 là số 0–30, điểm cosine là
0–1 — cộng vào thì BM25 luôn thắng.

## 2. Dừng 30 giây

- Hai danh sách có thang điểm khác nhau. Có cách nào trộn mà không cần so điểm?
- Muốn xếp hạng thật kỹ, model phải đọc *câu hỏi và đoạn cùng lúc*. Vì sao không làm vậy cho cả triệu đoạn?
- Thay vì tìm một lần, nếu để agent tự tìm nhiều lần, tự đổi từ khoá — được gì, mất gì?

## 3. Khái niệm

**Tìm lai (hybrid search)**: chạy cả tìm chữ và tìm nghĩa, rồi trộn.

**Trộn theo thứ hạng (RRF — Reciprocal Rank Fusion, Cormack 2009)** (câu hỏi 1): bỏ điểm, chỉ dùng **thứ hạng**. Mỗi đoạn được
`1 / (60 + hạng)` từ mỗi danh sách, cộng lại. Đoạn đứng cao ở **cả hai** thắng; đoạn đứng đầu một bên vẫn có chỗ. Không cần chỉnh thang điểm.
Hằng số 60 là giá trị trong bài gốc, hầu hết công cụ dùng mặc định.

**Xếp lại (rerank)** (câu hỏi 2): tìm nhanh lấy 50–100 ứng viên, rồi một model **chậm mà kỹ** đọc *(câu hỏi, đoạn)* cùng lúc và chấm lại.
- **Cross-encoder reranker**: model nhỏ chuyên chấm cặp — chính xác hơn embedding nhiều, nhưng chỉ chạy nổi trên vài chục ứng viên.
- **LLM làm reranker**: đưa danh sách cho LLM chọn — tốt nhất, đắt nhất.
- Kiểu ở giữa: **late interaction** (ColBERT) — giữ vector cho từng từ, so khớp chi tiết hơn embedding một vector.

**Agent tự tìm (agentic search)** (câu hỏi 3): cho agent công cụ tìm; agent đọc kết quả, đổi từ khoá, tìm lại, mở file, đi theo link… nhiều
vòng. Nhiều agent viết code dùng chính cách này (grep + đọc file lặp lại) thay vì kho vector.

## 4. Các cách

**A. Một loại tìm.** *Hợp khi:* nội dung chủ yếu một dạng (toàn mã → chữ; toàn chat → nghĩa). *Gãy khi:* câu hỏi trộn.

**B. Lai + RRF.** *Hợp khi:* nội dung trộn. Rẻ (hai lần tìm nhanh). *Gãy khi:* một bên trả rác nhiều → rác vẫn chen vào top.

**C. Lai + reranker.** *Hợp khi:* cần top 3 thật đúng (đặt tự động lên bàn). *Gãy khi:* độ trễ thêm (vài chục–vài trăm ms trên CPU); reranker
không hiểu tiếng Việt/mã nếu chọn sai model.

**D. Agent tự tìm nhiều vòng.** *Hợp khi:* câu hỏi phức tạp, chấp nhận chờ; kho đọc được trực tiếp (file). *Gãy khi:* tốn token cho mỗi vòng;
agent dừng sớm khi tìm thấy "cái gì đó" (có thể là bản cũ); không chạy được khi cần trả lời trong 1 giây.

**E. Định tuyến theo loại câu.** Câu có mã/đường dẫn → tìm chữ; câu tự nhiên → tìm nghĩa; câu "đơn của tôi" → tra bảng. Luật đơn giản (có
khớp mẫu mã không?) hoặc một model nhỏ phân loại. *Hợp khi:* loại câu rõ. *Gãy khi:* phân loại sai thì mất hẳn.

## 5. Bảng một lần nhìn

| Cách | Độ trễ | Tiền | Chất lượng top 3 | Gãy khi |
|---|---|---|---|---|
| A. Một loại | thấp | 0 | tốt một loại câu | câu trộn |
| B. Lai + RRF | thấp | 0 | tốt hơn A trên câu trộn | một bên rác |
| C. + reranker | +vừa | thấp (model nhỏ) / cao (LLM) | tốt nhất một lần | độ trễ, ngôn ngữ |
| D. Agent nhiều vòng | cao | token mỗi vòng | tốt với câu khó | cần nhanh, dừng sớm |
| E. Định tuyến | thấp | 0 | tốt nếu phân loại đúng | phân loại sai |

**Quy luật:** trộn **theo thứ hạng**, không theo điểm; tìm rộng bằng cách rẻ rồi **xếp lại hẹp** bằng cách đắt; để agent tự tìm khi được
phép chậm.

## 6. Ba kịch bản

- **Nhóm code:** B (mã + diễn đạt lại) hoặc D (agent grep/đọc file nhiều vòng) — cả hai đều có hệ thống thật dùng thành công.
- **Cửa hàng Lá:** E (mã đơn → tra; câu hỏi chính sách → nghĩa) + C nếu cần chính xác; D quá chậm cho chat khách.
- **Mai:** A (nghĩa) có thể đủ; B khi Mai hay nhắc tên riêng (tên quán, tên người).

## 7. Scale

- **Nhỏ:** A; D nếu là agent viết code.
- **Vừa:** B; C khi kết quả được đẩy tự động.
- **Lớn:** C gần như bắt buộc — tìm nhanh càng nhiều ứng viên "gần mà sai". Cái vỡ là **chi phí xếp lại** × số câu hỏi; giải bằng reranker nhỏ
  hoặc cache.

## 8. Bốn nền tảng

- **Windows / Mac:** reranker nhỏ chạy CPU được (vài chục ms cho 50 ứng viên); Mac chip Apple nhanh hơn rõ. Elasticsearch/OpenSearch, Weaviate,
  Qdrant… đã có tìm lai dựng sẵn.
- **iOS / Android:** tìm lai trên máy = SQLite FTS5 + sqlite-vec (hoặc AppSearch/Core Spotlight + embedding trên máy), trộn RRF bằng vài dòng code;
  reranker trên điện thoại tốn pin → thường bỏ, hoặc chỉ chạy trên ít ứng viên.

## 9. Tóm tắt

Hai cách tìm dở ở chỗ ngược nhau nên trộn chúng — bằng thứ hạng (RRF). Muốn top đầu thật đúng thì xếp lại bằng model đọc cặp. Agent tự tìm
nhiều vòng là một lựa chọn khác hẳn: chậm và tốn token, nhưng linh hoạt nhất.

**Thuật ngữ:** hybrid search · RRF · rerank · cross-encoder · late interaction / ColBERT · agentic search · query routing (định tuyến).

**Giờ bạn biết thêm:** cách ghép các kiểu tìm thành một đường tìm, và khi nào giao việc tìm cho chính agent.

**Bài sau:** [12 — Đi theo đồ thị](12-di-theo-do-thi.md).
