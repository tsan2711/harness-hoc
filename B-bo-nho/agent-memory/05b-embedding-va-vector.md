# 05b — Embedding và tìm bằng vector: tìm theo nghĩa

> Đi kèm [05](05-tranh-luan-kg-vs-recall.md). Trước đó: [05a BM25](05a-bm25-va-fts5.md).

## 1. Câu chuyện

Câu `para-android` trong bộ đo hỏi: *"lỗi hay gặp khi đóng gói cho điện thoại"*. Đáp án là `docs/shared/unity-gotchas.md`, nơi viết
"Android build fails…", "Gradle", "IL2CPP". Không chữ nào trùng. BM25 trượt. Một người đọc thì thấy ngay: "đóng gói cho điện thoại" = "build Android".
Làm sao cho máy "thấy ngay" như vậy?

## 2. Dừng 30 giây
- Nếu phải biểu diễn *nghĩa* của một câu bằng con số, bạn sẽ đo những gì?
- "Mèo đuổi chuột" và "chuột đuổi mèo" — cùng chữ, khác nghĩa. Cách biểu diễn của bạn có phân biệt được không?
- Hai đoạn cùng nói về `git stash`, một đoạn "nên dùng", một đoạn "cấm dùng". Chúng nên gần hay xa nhau?

## 3. Embedding là gì

Một **model embedding** (mạng nơ-ron, thường là encoder kiểu Transformer) đọc một đoạn văn và trả ra một dãy số cố định, ví dụ 384 hoặc 1024 số.
Dãy đó là một **điểm trong không gian nhiều chiều**. Model được huấn luyện (bằng hàng trăm triệu cặp câu "cùng nghĩa / khác nghĩa") để
**câu cùng nghĩa → điểm gần nhau**, khác nghĩa → xa nhau.

Không có chiều nào là "chiều Android" cụ thể; nghĩa nằm rải trên mọi chiều. Nhưng hiệu ứng là: "đóng gói cho điện thoại" và "Android build"
rơi vào cùng một vùng.

### Đo "gần": cosine
cos(a, b) = (a·b) / (|a|·|b|) — góc giữa hai mũi tên. 1 = cùng hướng (cùng nghĩa), 0 = không liên quan. Thường chuẩn hoá vector về độ dài 1
trước, khi đó cosine = tích vô hướng, tính rất nhanh.

### Tìm
1. Lúc **dựng chỉ mục**: cắt kho thành đoạn (chunk), chạy model trên từng đoạn, lưu vector.
2. Lúc **hỏi**: chạy model trên câu hỏi (vài ms–vài chục ms trên CPU), tìm k vector gần nhất (k-NN).

## 4. Các phần phải chọn

### 4.1 Model
Phải **đa ngữ** (kho trộn Việt–Anh). Ví dụ hay dùng (theo hiểu biết người viết; kiểm lại phiên bản trước khi chọn):
| Model | Cỡ (ước) | Ghi chú |
|---|---|---|
| `paraphrase-multilingual-MiniLM-L12-v2` | ~120M tham số, ~470 MB | nhẹ, cũ, đủ dùng |
| `multilingual-e5-small` / `-base` | ~120M / ~280M | cần tiền tố "query: " / "passage: " |
| `bge-m3` | ~570M, ~2 GB | mạnh, đa ngữ tốt, chậm hơn |
Chạy cục bộ: **0 token LLM**, chỉ tốn CPU khi dựng chỉ mục.

### 4.2 Chunking (cắt đoạn)
Vector biểu diễn *cả đoạn*. Đoạn quá dài → nghĩa bị pha loãng (một đoạn nói 5 chuyện thì vector nằm "giữa" 5 chuyện, không gần chuyện nào).
Đoạn quá ngắn → mất ngữ cảnh ("nó bị cấm" — cái gì?). Thường 200–500 từ, cắt theo tiêu đề markdown, gối nhau một ít.
`recall.py` đã cắt theo mục (`split()`), dùng lại được.

### 4.3 Tìm láng giềng: quét hết hay ANN
- **Quét hết (brute force):** so câu hỏi với mọi vector. 50.000 vector × 384 chiều ≈ 19 triệu phép nhân → vài ms. Đủ cho cỡ Seriously.
- **ANN** (gần đúng, vd HNSW — đồ thị nhiều tầng nhảy dần tới gần): cần khi hàng triệu vector; đổi lấy sai sót nhỏ.
- `sqlite-vec`: extension SQLite lưu vector cạnh FTS5 trong cùng file; chủ yếu quét hết — hợp cỡ ta.

## 5. Vector giỏi gì, dở gì (trả lời mục 2)

| | Giỏi | Dở |
|---|---|---|
| Đồng nghĩa, diễn đạt lại, khác ngôn ngữ | ✔ "đóng gói điện thoại" ≈ "Android build" | |
| Mã / tên riêng hiếm | | ✘ `CS0103` gần `CS0104` hay "lỗi compile"? Model chưa từng thấy mã đó, vector mơ hồ |
| Phủ định, lập trường | | ✘ "nên dùng stash" và "cấm dùng stash" **gần nhau** (cùng chủ đề) — câu 3 mục 2 |
| Thứ tự ("mèo đuổi chuột") | khá (model Transformer có để ý thứ tự) | không tuyệt đối |
| Giải thích vì sao | | ✘ không chỉ ra được chữ nào khớp |
| Cập nhật | | đổi model → phải tính lại toàn bộ vector |

Điểm "phủ định gần nhau" rất quan trọng với bài toán kiến thức cũ ([05f](05f-ky-uc-cu-va-thay-the.md)): vector sẽ *tìm ra* đoạn cũ mâu thuẫn rất giỏi
(vì cùng chủ đề) — tốt cho bước **phát hiện**, nhưng nó **không biết** đoạn nào thắng.

## 6. Nó có chữa đúng bệnh của ta không?

10 câu diễn đạt lại trượt đều là lỗ từ vựng, một bước ([05 vòng 7](05-tranh-luan-kg-vs-recall.md)). Đây chính xác là việc vector giỏi nhất.
Nhưng vector *thay* BM25 thì mất 20/20 câu từ khoá → nên **cộng** với BM25: hybrid ([05c](05c-hybrid-rrf-reranker.md)).

## 7. Scale
- Nhỏ: quét hết, một file SQLite, model nhỏ. Rủi ro chính: chọn chunk dở.
- Vừa (50k–500k đoạn): vẫn quét hết được; dựng lại chỉ mục mất vài phút–vài chục phút CPU → phải dựng **tăng dần** (chỉ đoạn mới/đổi).
- Lớn (triệu+): ANN, server vector riêng. Cái vỡ: **trúng nhầm chủ đề gần** tăng theo kho (nhiều đoạn "gần gần") → cần reranker.

## 8. Dừng lần hai — Seriously
- `docs/shared/memory-options.md` PA2.4: vector đã được thiết kế (sqlite-vec + model đa ngữ nhỏ, trộn RRF) nhưng bị khoá bởi cổng
  "diễn đạt lại < 70 % **và** đưa-sẵn chạy 14 ngày". Điều kiện thứ hai không liên quan chất lượng tìm — đáng xem lại.
- Câu `para-why-index` trong `cases.toml` hỏi đúng "vì sao chọn một kho tìm kiếm thay vì **mô hình nhúng**" — nó trượt vì ghi chú dùng chữ "vector/embedding".
  Mỉa mai: câu hỏi về việc không dùng vector chỉ vector mới tìm ra.

## 9. Bốn nền tảng
- **Mac (Apple Silicon):** model nhỏ chạy CPU nhanh; có thể dùng GPU (Metal) / Neural Engine qua Core ML.
- **Windows:** CPU (ONNX Runtime), GPU qua DirectML/CUDA.
- **iOS:** Core ML trên Neural Engine — model ~100M tham số chạy được trên máy, bộ nhớ là giới hạn (vài trăm MB).
- **Android:** TFLite/ONNX Runtime + NNAPI/GPU; chênh lệch máy rất lớn, máy yếu chậm hơn nhiều lần.
Với harness (chạy trên Mac của Bi) chỉ Mac quan trọng; với *game* muốn tìm kiếm theo nghĩa trên điện thoại thì cỡ model là ràng buộc chính.

## 10. Tóm tắt
Embedding biến nghĩa thành điểm trong không gian; tìm = lấy điểm gần nhất. Vá lỗ từ vựng, nhưng mù mã hiếm và không phân biệt "nên" với "cấm".

**Thuật ngữ:** embedding · vector · cosine · chunk · k-NN · ANN · HNSW · sqlite-vec · encoder. **Bài sau:** [05c — hybrid](05c-hybrid-rrf-reranker.md).
