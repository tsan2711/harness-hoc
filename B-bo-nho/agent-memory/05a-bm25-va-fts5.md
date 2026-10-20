# 05a — BM25 và FTS5: tìm theo từ khoá, cái `recall` đang dùng

> Đi kèm [05 — tranh luận](05-tranh-luan-kg-vs-recall.md). Đọc ~10 phút.

## 1. Câu chuyện

Agent hỏi `kit recall "vì sao bỏ RenderMeshInstanced"`. Kho có 40.000 đoạn. Trong 4 ms, nó trả 12 đoạn, đoạn đầu là đúng ghi chú
"Bi rejected the CPU matrix bake + 1023-batch RenderMeshInstanced…". Hôm sau agent hỏi `kit recall "vì sao không vẽ hàng loạt bằng CPU"` —
0 đoạn đúng. Cùng một kiến thức, hai cách hỏi, hai kết quả.

## 2. Dừng 30 giây

Tự đoán trong đầu, không cần trả lời:
- Vì sao "RenderMeshInstanced" làm kết quả *rất* chính xác, còn "vẽ" thì gần như vô dụng?
- Nếu một đoạn nhắc "RenderMeshInstanced" 30 lần, nó có nên đứng trên đoạn nhắc 1 lần không? Gấp 30 lần?
- Đoạn dài 3.000 chữ nhắc một lần và đoạn 30 chữ nhắc một lần — cái nào "về" chủ đề đó hơn?

Ba câu này chính là ba phần của BM25.

## 3. Từ chỉ mục ngược tới BM25

### 3.1 Chỉ mục ngược (inverted index)
Thay vì đọc từng đoạn để tìm chữ, máy lập sẵn bảng: *từ → danh sách đoạn chứa nó*. Như mục lục cuối sách giáo khoa.
`rendermeshinstanced → [đoạn 812, 9033]`. Tra một từ = tra một dòng, nhanh bất kể kho to.

### 3.2 Chấm điểm: BM25
Tìm được đoạn rồi, phải *xếp* đoạn nào lên trước. BM25 ("Best Matching 25", từ những năm 1990) cộng điểm cho từng từ của câu hỏi:

```
điểm(đoạn, câu hỏi) = Σ_mỗi từ q   IDF(q) × f·(k1+1) / ( f + k1·(1 − b + b·|đoạn|/độ_dài_TB) )
```
- `f` = số lần từ q xuất hiện trong đoạn.
- **IDF** (độ hiếm) = log((N − n + 0,5)/(n + 0,5) + 1), N = tổng số đoạn, n = số đoạn chứa q. Từ có ở mọi đoạn ("là", "của") → IDF ≈ 0.
  "RenderMeshInstanced" có ở 2/40.000 đoạn → IDF rất lớn. *Trả lời câu 1 của mục 2.*
- **k1 ≈ 1,2: bão hoà.** f tăng thì điểm tăng nhưng chậm dần, chạm trần (k1+1). Nhắc 30 lần không gấp 30 lần nhắc 1 lần — chỉ hơn khoảng 2 lần. *Câu 2.*
- **b ≈ 0,75: phạt độ dài.** Đoạn dài hơn trung bình bị trừ: nhắc một lần trong 3.000 chữ yếu hơn nhắc một lần trong 30 chữ. *Câu 3.*

Ví dụ số (N = 40.000, k1 = 1,2, b = 0,75, đoạn dài bằng trung bình):
| Từ | n | IDF | f = 1 → phần TF | Đóng góp |
|---|---|---|---|---|
| rendermeshinstanced | 2 | ≈ 9,8 | 1·2,2/(1+1,2) = 1,0 | **9,8** |
| vẽ | 3.000 | ≈ 2,6 | 1,0 | 2,6 |
| là | 38.000 | ≈ 0,05 | 1,0 | 0,05 |

Một từ hiếm áp đảo cả câu. Đó là lý do hỏi bằng mã/tên riêng thì trúng 20/20.

## 4. Vì sao hỏi khác chữ thì trượt

BM25 chỉ thấy **chữ trùng**. "vẽ hàng loạt bằng CPU" không có chữ nào trong ghi chú "CPU matrix bake + RenderMeshInstanced"
ngoài "CPU". Nghĩa giống — điểm gần 0. Gọi là **lỗ từ vựng** (vocabulary mismatch). Cách vá trong họ từ khoá:
- **Đồng nghĩa (query expansion):** khi hỏi "biểu tượng", tìm luôn "icon", "ký hiệu". Seriously có `company/eval/recall/synonyms.toml` (29 nhóm, viết tay).
  Nhược: chỉ vá được cặp đã nghĩ ra; viết theo bộ đề → rò rỉ ([05g](05g-do-truy-hoi.md)).
- **Stemming / lemmatization:** gom "running/ran/run". Tiếng Việt ít biến hình nên ít tác dụng; vấn đề tiếng Việt là **dấu** và **từ ghép**.
- Vá tận gốc phải hiểu nghĩa → vector ([05b](05b-embedding-va-vector.md)).

## 5. Riêng tiếng Việt: bỏ dấu và "nhớ" ≠ "nhỏ"

Người gõ hay thiếu dấu ("nho"), nên chỉ mục thường **bỏ dấu** (fold): "nhớ" → "nho", "nhỏ" → "nho". Hai từ khác nghĩa thành một.
Seriously giải bằng **hai cột**: `text` bỏ dấu (bắt cả người gõ thiếu dấu) và `acc` giữ dấu (ưu tiên đoạn trùng dấu đúng);
truy vấn mỗi từ thành `("nho" OR acc:"nhớ")`, cột `acc` có trọng số 1,5 → đoạn đúng dấu đứng trên.

Từ ghép: tách theo khoảng trắng nên "giao diện" thành "giao" + "diện"; câu hỏi "giao diện" mặc định thành AND hai từ → vẫn ổn;
nhưng "diện" lẻ khớp lung tung. Có thể dùng cụm trong ngoặc kép (`"giao diện"`).

## 6. AND rồi OR

- **AND:** đoạn phải chứa *mọi* từ. Chính xác, nhưng câu hỏi 8 từ thì gần như không đoạn nào có đủ → 0 kết quả.
- **OR:** đoạn chứa *bất kỳ* từ. Luôn có kết quả, xếp bằng BM25 (nhiều từ hiếm trùng → cao).
- `recall.py` làm **AND trước, thiếu thì bù bằng OR** (`search()`): giữ chính xác khi có, không trả rỗng khi không.

## 7. FTS5 — BM25 có sẵn trong SQLite

SQLite có module **FTS5**: bảng ảo `CREATE VIRTUAL TABLE chunks USING fts5(text, acc, ent, …)`, truy vấn `WHERE chunks MATCH '…'`,
xếp `ORDER BY bm25(chunks, 1.0, 1.5, 3.0)` — ba số là **trọng số từng cột** (`text` 1, `acc` 1,5, `ent` 3). Lưu ý: hàm `bm25()` của FTS5
trả số **âm**, càng nhỏ càng tốt — nên `order by` tăng dần.

Cột `ent` (thực thể) chứa đường dẫn, mã lỗi `CS0103`, mã chẩn đoán `SEB001`, tên test, id việc, tiêu đề mục — nhân 3 vì một mã trùng
gần như chắc chắn đúng đoạn.

## 8. Các phương án và chỗ gãy

| Cách | Ưu | Nhược | Gãy khi |
|---|---|---|---|
| `grep` thô | 0 cài đặt | Không xếp hạng, đọc lại cả kho mỗi lần | kho > vài nghìn file; câu nhiều từ |
| BM25 (FTS5) | ms, 0 token, giải thích được, mã/tên riêng tuyệt đối | Lỗ từ vựng | hỏi khác chữ |
| BM25 + đồng nghĩa tay | Vá cặp hay gặp | Chỉ cặp đã nghĩ ra; rò rỉ theo bộ đề | câu mới, chủ đề mới |
| BM25 + vector | Vá lỗ từ vựng | Thêm model, mất tính giải thích | xem 05b |

**Quy luật:** BM25 là "người tra mục lục giỏi nhưng không hiểu nghĩa". Mạnh ở *cái tên*, yếu ở *cách nói*.

## 9. Scale

- Nhỏ (vài nghìn đoạn): BM25 gần như hoàn hảo cho từ khoá.
- Vừa (~50k đoạn, cỡ Seriously): vẫn ms; nhưng **nhiều đoạn trùng chữ mà khác ý** (transcript lặp) → nhiễu tăng; cần lọc theo bộ phận (`--unit`, `prefer`), khử trùng lặp.
- Lớn (hàng triệu): vẫn chạy (Elasticsearch/Lucene dùng BM25), nhưng câu diễn đạt lại thành đa số → gần như bắt buộc thêm vector.
  Cái vỡ là **chất lượng xếp hạng**, không phải tốc độ.

## 10. Dừng lần hai — mở Seriously kiểm chứng

- `tools/claude/recall.py`: `fold()` (bỏ dấu), `fts_query()` (mỗi từ → folded OR acc + đồng nghĩa), `search()` (AND rồi OR, `bm25(chunks, 1.0, W_ACC, W_ENT)`), dòng `W_ACC, W_ENT, BUCKET = 1.5, 3.0, 0.5`.
- `company/eval/recall/synonyms.toml`: đọc vài nhóm — bạn sẽ thấy chúng được viết để vá đúng câu trong `cases.toml`.
- Thử: `sh tools/claude/kit.sh recall "RenderMeshInstanced"` rồi `… recall "vẽ hàng loạt bằng CPU"`.

## 11. Bốn nền tảng

SQLite + FTS5 chạy y hệt trên **Windows, Mac, iOS, Android** (SQLite có sẵn trên iOS/Android; FTS5 cần bản build bật module — iOS
hệ thống có, Android tuỳ phiên bản, an toàn nhất là kèm SQLite riêng). BM25 là toán thuần CPU, không cần GPU/NPU, nên đây là cách tìm
duy nhất chạy giống hệt nhau và rẻ trên cả bốn. Khác biệt chỉ ở tokenizer (tách từ) mặc định.

## 12. Tóm tắt một dòng
BM25 = đếm chữ trùng, thưởng chữ hiếm, bão hoà tần suất, phạt đoạn dài; nhanh và đúng với tên riêng, mù với cách nói khác.

**Thuật ngữ:** inverted index (chỉ mục ngược) · TF (tần suất) · IDF (độ hiếm) · saturation (bão hoà) · length normalization (chuẩn hoá độ dài)
· vocabulary mismatch (lỗ từ vựng) · query expansion (mở rộng truy vấn) · fold (bỏ dấu). **Bài sau:** [05b — vector](05b-embedding-va-vector.md).
