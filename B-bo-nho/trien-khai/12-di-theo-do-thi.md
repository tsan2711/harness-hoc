# 12 — Đi theo đồ thị

> Chuỗi "Triển khai trí nhớ", bài 12/21. Đọc ~10 phút.
> **Bạn đã biết** ([08](08-do-thi-tri-thuc.md), [11](11-lai-va-xep-lai.md)): đồ thị = nút + cạnh + thời gian hiệu lực; dựng từ dữ liệu có cấu
> trúc / người khai / cùng xuất hiện / LLM trích; gộp thực thể; hub; tìm lai + xếp lại.

## 1. Chuyện mở đầu

Lan hỏi agent: "quyết định bỏ ChartLite ảnh hưởng tới những màn hình nào?". Không đoạn nào chứa câu trả lời. Câu trả lời nằm ở *chuỗi*: ghi
chú quyết định → việc "tự vẽ biểu đồ" → ba commit → ba file màn hình. Tìm lai trả về ghi chú quyết định (đúng nhưng chưa đủ) và một ghi chú
khác nhắc "biểu đồ" (sai).

## 2. Dừng 30 giây

- Câu nào cần *một* đoạn để trả lời, câu nào cần *nối nhiều* đoạn?
- Nếu đi từ "ChartLite" theo mọi cạnh, hai bước, có bao nhiêu nút? Điều gì xảy ra khi gặp một nút nối với hàng nghìn thứ?
- Để nối được đồ thị từ chữ tự do, máy phải nhận ra "ChartLite" là một *thứ có tên*. Nó làm bằng gì?

## 3. Câu một bước vs nhiều bước

- **Một bước (single-hop):** câu trả lời nằm trong một đoạn ("vì sao bỏ ChartLite?"). Tìm lai thường đủ.
- **Nhiều bước (multi-hop):** câu trả lời là *nối* của nhiều đoạn qua các thực thể chung ("màn hình nào bị ảnh hưởng?"). Tìm theo độ giống
  một lần thường hụt, vì đoạn cuối chuỗi (file màn hình) không giống câu hỏi chút nào (câu hỏi 1).
- **Tổng hợp toàn cục:** "các chủ đề chính khách hay than phiền là gì?" — không đoạn nào, chuỗi nào trả lời; cần nhìn cả kho.

## 4. Nhận diện thực thể — cửa vào của đồ thị (câu hỏi 3)

Muốn dựng đồ thị từ chữ (bài 08, cách C và D), máy phải nhặt "thứ có tên". Bốn cách, rẻ → đắt:
1. **Mẫu chữ (regex):** cái có *hình dạng* — đường dẫn, mã lỗi, mã đơn, email. Nhanh, tất định; mù với tên tự nhiên ("ChartLite").
2. **Từ điển (gazetteer):** danh sách tên đã khai ở đâu đó (tên thư viện trong file khai báo, danh mục sản phẩm, danh bạ). Biết đúng thuật ngữ
   riêng; mù với tên mới.
3. **Model nhỏ** (spaCy, GLiNER; tiếng Việt: underthesea, VnCoreNLP, model dựa PhoBERT): bắt tên tự nhiên; loại nhãn chung (người, nơi, tổ
   chức) không khớp thuật ngữ riêng; dở với câu trộn Việt–Anh–code.
4. **LLM:** tốt nhất, đắt nhất, có thể bịa.

Ba việc hay bị gọi chung: **nhận diện** (đoạn chữ nào là thực thể) ≠ **gộp** (nhiều cách viết → một nút) ≠ **trích quan hệ** (cạnh có tên gì).
Đồ thị "cùng xuất hiện" chỉ cần hai việc đầu.

## 5. Các cách đi theo đồ thị

**A. Tìm lai rồi mở rộng 1 bước theo cạnh.** Lấy top đoạn, thêm các nút kề (file được commit sửa, tài liệu được link). *Hợp khi:* cạnh có sẵn
(git, link). Rẻ. *Gãy khi:* cần 3+ bước; nút hub kéo vào hàng trăm thứ.

**B. Truy vấn đồ thị có cấu trúc.** "Từ nút `ChartLite`, đi `quyết_định → việc → commit → file`" bằng ngôn ngữ truy vấn đồ thị (Cypher) hoặc
SQL đệ quy. *Hợp khi:* biết trước dạng câu hỏi. Đúng tuyệt đối. *Gãy khi:* câu hỏi tự do — ai viết truy vấn? (có thể để LLM viết, thêm rủi ro).

**C. Lan truyền điểm (Personalized PageRank).** Đặt "điểm" ở các nút khớp câu hỏi, cho điểm chảy theo cạnh vài vòng, lấy các nút nhận nhiều điểm.
HippoRAG (2024) dùng cách này cho câu nhiều bước. *Hợp khi:* nhiều bước, câu tự do. *Gãy khi:* đồ thị nhiễu (cạnh sai) → điểm chảy sai; hub hút
điểm (thường phải giảm trọng số hub).

**D. Tóm theo cụm (GraphRAG, Microsoft 2024).** Chia đồ thị thành **cộng đồng** (cụm nút dày liên kết), LLM viết tóm tắt cho từng cụm; câu
tổng hợp toàn cục được trả lời từ các bản tóm cụm. *Hợp khi:* câu "chủ đề chính là gì?" trên kho lớn. *Gãy khi:* rất đắt để dựng (LLM trích +
tóm mọi cụm), phải dựng lại khi kho đổi nhiều; không giúp câu một bước.

**E. Agent tự đi** (bài 11, cách D) với công cụ "cho tôi nút kề của X". *Hợp khi:* chấp nhận chậm. *Gãy khi:* đi lạc, tốn token.

## 6. Bảng một lần nhìn

| Cách | Hợp loại câu | Giá dựng | Giá mỗi câu | Gãy khi |
|---|---|---|---|---|
| A. Lai + 1 bước | một bước + kề | thấp (cạnh có sẵn) | thấp | 3+ bước, hub |
| B. Truy vấn cấu trúc | nhiều bước, dạng biết trước | tuỳ | thấp | câu tự do |
| C. PPR | nhiều bước, tự do | vừa–cao | thấp | cạnh nhiễu, hub |
| D. Tóm theo cụm | tổng hợp toàn cục | rất cao | vừa | kho đổi nhiều |
| E. Agent tự đi | mọi loại | tuỳ | cao | đi lạc |

**Quy luật:** đồ thị chỉ thắng ở câu **nhiều bước** và **tổng hợp**; với câu một bước, tìm lai thường bằng hoặc hơn với giá thấp hơn nhiều. Biết
tỉ lệ câu nhiều bước trong câu hỏi thật của bạn **trước** khi dựng (bài 19).

## 7. Ba kịch bản

- **Nhóm code:** câu "ảnh hưởng tới đâu?" là nhiều bước thật; cạnh có sẵn từ git + link → A hoặc B rẻ.
- **Cửa hàng Lá:** "khách nào mua sản phẩm X và từng khiếu nại?" — B trên bảng có sẵn (thực ra là SQL thường). D cho "khách hay than gì nhất?".
- **Mai:** ít câu nhiều bước; C/D thường thừa.

## 8. Scale

- **Nhỏ:** không cần; đọc vài file theo link là đủ.
- **Vừa:** A/B trên bảng cạnh.
- **Lớn:** hub và cạnh nhiễu là vấn đề chính; D thành rất đắt. Cái vỡ là **chất lượng cạnh** — đồ thị sai thì đi càng xa càng sai.

## 9. Bốn nền tảng

- **Windows / Mac:** truy vấn đệ quy trên SQLite/PostgreSQL chạy giống nhau; Neo4j cả hai. NER bằng model nhỏ chạy CPU được; cài thư viện học
  máy trên Windows hay vướng bản build hơn Mac.
- **iOS / Android:** hệ điều hành có nhận diện thực thể sẵn trên máy — Apple `NaturalLanguage` (người, nơi, tổ chức), Google ML Kit Entity
  Extraction (địa chỉ, ngày, số điện thoại, URL…) — loại chung, không biết thuật ngữ của app; phần riêng dùng từ điển. GraphRAG trên điện thoại
  gần như không thực tế; A/B trên SQLite thì được.

## 10. Tóm tắt

Câu nhiều bước và câu tổng hợp là nơi đồ thị có lý do tồn tại: mở rộng một bước theo cạnh có sẵn, truy vấn cấu trúc, lan truyền điểm (PPR), hoặc
tóm theo cụm (GraphRAG) — giá tăng dần. Cửa vào là nhận diện thực thể, rẻ → đắt: mẫu chữ, từ điển, model nhỏ, LLM.

**Thuật ngữ:** single-hop / multi-hop · global query · NER · gazetteer · entity resolution · relation extraction · Cypher · recursive SQL · Personalized PageRank · HippoRAG · GraphRAG · community summary.

**Giờ bạn biết thêm:** đủ các kiểu tìm — chữ, nghĩa, lai, xếp lại, đồ thị. Phần sau hỏi: **ai** quyết ghi và đọc.

**Bài sau:** [13 — Ai quyết ghi gì](13-ai-quyet-ghi-gi.md).
