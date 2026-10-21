# 07 — Kho vector

> Chuỗi "Triển khai trí nhớ", bài 7/21. Đọc ~10 phút.
> **Bạn đã biết** ([05](05-file-ghi-chu.md)–[06](06-bang-co-cau-truc.md)): file ghi chú gãy khi quá nhiều file; bảng giỏi *tra* câu biết trước
> dạng, nhưng câu hỏi mở cần *tìm*.

## 1. Chuyện mở đầu

Mai hỏi: "hồi trước mình có kể món gì ăn xong bị ngứa không?". Trong nhật ký có dòng: "ăn tôm rang me xong nổi mẩn đỏ". Không chữ nào trùng:
"ngứa" ≠ "nổi mẩn", "món" ≠ "tôm rang me". Tìm theo chữ không thấy gì. Nhưng với người đọc, hai câu rõ ràng nói cùng một chuyện.

## 2. Dừng 30 giây

- Làm sao để máy "thấy" hai câu không chung chữ nào là gần nghĩa nhau?
- Nhật ký một năm dài 2 triệu chữ. Lưu cả khối, hay cắt thành mẩu? Mẩu to cỡ nào?
- Tìm theo nghĩa giỏi diễn đạt lại. Thử nghĩ nó dở ở loại câu nào.

## 3. Khái niệm

**Embedding** (vector nhúng): một model nhỏ chuyên biệt đọc một đoạn chữ và trả về một **dãy số** cố định độ dài (vài trăm tới vài nghìn
số). Model được huấn luyện để **đoạn gần nghĩa → dãy số gần nhau**. Hình dung mỗi đoạn là một điểm trên một tấm bản đồ rất nhiều chiều;
"ngứa sau khi ăn" và "nổi mẩn đỏ sau món tôm" rơi vào cùng một khu (câu hỏi 1).

**Độ gần (cosine similarity)**: đo hai mũi tên chỉ cùng hướng cỡ nào; 1 = cùng hướng, 0 = không liên quan.

**Chia đoạn (chunking)**: cắt tài liệu dài thành mẩu trước khi nhúng — vì một dãy số cho cả cuốn sách thì "nghĩa trung bình" vô dụng.
Câu hỏi 2: mẩu quá nhỏ (một câu) mất ngữ cảnh ("nó" là gì?); quá to (cả chương) loãng nghĩa. Thường vài trăm token, cắt theo đoạn văn/tiêu
đề, có thể chồng nhau một ít.

**Kho vector**: nơi lưu dãy số + đoạn chữ gốc + vài cột phụ (nguồn, ngày, người dùng), và trả lời nhanh câu "k điểm nào gần điểm này nhất?".
Với hàng triệu điểm, so từng điểm quá chậm → dùng **chỉ mục gần đúng** (ANN, phổ biến nhất là HNSW — một dạng "mạng đường tắt" giữa các
điểm): nhanh hơn rất nhiều, đổi lại đôi khi bỏ sót điểm gần nhất thật.

## 4. Các cách lưu

**A. Thư viện trong chương trình** (FAISS, hoặc tự tính cosine trong bộ nhớ). *Hợp khi:* vài chục nghìn mẩu, một máy. *Gãy khi:* nhiều tiến
trình cùng ghi; phải tự lo lưu xuống đĩa.

**B. Phần mở rộng trong cơ sở dữ liệu đã có** (pgvector cho PostgreSQL, sqlite-vec cho SQLite). Vector nằm cạnh bảng hồ sơ (bài 06) → lọc
"chỉ mẩu của khách K" và tìm gần trong một câu truy vấn. *Hợp khi:* đã có cơ sở dữ liệu. *Gãy khi:* quy mô rất lớn, cần tốc độ cực cao.

**C. Cơ sở dữ liệu vector chuyên dụng** (Qdrant, Weaviate, Milvus, Chroma, LanceDB; hoặc dịch vụ đám mây như Pinecone). *Hợp khi:* hàng triệu–tỉ
mẩu, nhiều người dùng. *Gãy khi:* thêm một hệ thống phải vận hành, đồng bộ với nguồn sự thật.

**D. Dịch vụ "trí nhớ" có sẵn vector bên trong** (bài 13, 21). *Hợp khi:* không muốn tự vận hành. *Gãy khi:* dữ liệu nằm ở nhà cung cấp; khó
tự kiểm tra cái gì đã được lưu.

Quyết định đi kèm cho mọi cách:
- **Model embedding nào** — chạy trên máy (miễn phí, riêng tư) hay gọi dịch vụ (tốn tiền mỗi đoạn); có hiểu tiếng Việt không (bài 10).
- **Đổi model = nhúng lại toàn bộ**: dãy số của hai model khác nhau không so được với nhau. Nên giữ chữ gốc làm nguồn, vector chỉ là bản sao
  dựng lại được.

## 5. Giỏi và dở (câu hỏi 3)

| Loại câu | Kho vector |
|---|---|
| Diễn đạt lại, đồng nghĩa ("ngứa" ↔ "nổi mẩn") | **giỏi** |
| Khác ngôn ngữ (hỏi tiếng Việt, ghi chú tiếng Anh), nếu model đa ngữ | **giỏi** |
| Mã chính xác, số, tên riêng hiếm (`#123`, `TS2345`, "ChartLite") | **dở** — gần nghĩa ≠ đúng chữ |
| Phủ định ("món *không* dùng tôm") | dở — "có tôm" và "không tôm" rất gần nhau |
| "Cái nào mới nhất / đã bị thay" | **không biết** — vector không có khái niệm thời gian (bài 15) |
| Câu nhiều bước ("ai đã sửa file mà quyết định X ảnh hưởng?") | dở (bài 12) |

## 6. Bảng một lần nhìn — cách lưu

| Cách | Vận hành | Quy mô | Lọc theo cột | Gãy khi |
|---|---|---|---|---|
| A. Thư viện | thấp | nhỏ | tự làm | nhiều tiến trình |
| B. Mở rộng CSDL | thấp | vừa | ✓ cùng truy vấn | quy mô rất lớn |
| C. CSDL vector | cao | lớn | ✓ | đồng bộ nguồn |
| D. Dịch vụ trí nhớ | thấp | lớn | tuỳ | dữ liệu ở ngoài |

**Quy luật:** vector là cách rẻ nhất để có **tìm theo nghĩa**; nó không thay được tra chính xác (bài 06) hay tìm theo chữ (bài 09), và không
biết gì về thời gian.

## 7. Scale

- **Nhỏ** (< 10 nghìn mẩu): A hoặc B; so từng điểm cũng đủ nhanh.
- **Vừa** (trăm nghìn – vài triệu): B hoặc C với HNSW; chú ý RAM (chỉ mục thường nằm trong bộ nhớ).
- **Lớn** (trăm triệu+): C, nén vector (lượng tử hoá — lưu số ít chính xác hơn để tiết kiệm chỗ). Cái vỡ là **chất lượng**: càng nhiều mẩu
  càng nhiều "hàng xóm gần nhưng sai", đặc biệt bản cũ và bản mới của cùng một tài liệu gần như trùng nhau.

## 8. Bốn nền tảng

- **Windows / Mac:** model embedding nhỏ chạy CPU được (vài chục ms một đoạn); Mac chip Apple tăng tốc tốt; Windows có GPU NVIDIA thì nhanh hơn
  nữa. sqlite-vec, LanceDB, Chroma đều chạy trên cả hai.
- **iOS:** Apple có embedding câu sẵn trong framework NaturalLanguage, hoặc chạy model riêng qua Core ML; sqlite-vec nhúng được vào app.
- **Android:** MediaPipe có bộ nhúng chữ chạy trên máy; hoặc model qua TensorFlow Lite / ONNX Runtime. Trên điện thoại, nhúng hàng chục
  nghìn đoạn tốn pin → làm dần lúc sạc.

## 9. Tóm tắt

Embedding biến đoạn chữ thành điểm trên bản đồ nghĩa; kho vector tìm điểm gần nhất. Giỏi diễn đạt lại và đa ngữ; dở với mã, tên riêng,
phủ định; không biết thời gian. Chia đoạn và chọn model là hai quyết định quyết định chất lượng; đổi model là nhúng lại.

**Thuật ngữ:** embedding · vector · cosine similarity · chunking · vector store / vector database · ANN · HNSW · quantization (lượng tử hoá).

**Giờ bạn biết thêm:** kho thứ ba — tìm theo nghĩa — và đúng loại câu nó giỏi / dở.

**Bài sau:** [08 — Đồ thị tri thức](08-do-thi-tri-thuc.md).
