# 05c — Hybrid: BM25 + vector, trộn bằng RRF, xếp lại bằng reranker

> Trả lời câu Bi hỏi ở vòng 5: "BM25 cộng vector là cách triển khai gì?". Trước đó: [05a](05a-bm25-va-fts5.md), [05b](05b-embedding-va-vector.md).

## 1. Câu chuyện

Hai thủ thư cùng tra một câu hỏi. Thủ thư Từ-khoá (BM25) đưa danh sách 12 cuốn; thủ thư Nghĩa (vector) đưa 12 cuốn khác. Có 3 cuốn trùng.
Bạn chỉ đọc được 3 cuốn. Chọn cuốn nào?

## 2. Dừng 30 giây
- Thủ thư Từ-khoá chấm điểm 0–25, thủ thư Nghĩa chấm 0–1. Cộng thẳng điểm có công bằng không?
- Cuốn đứng thứ 1 ở một bên và không có ở bên kia, so với cuốn đứng thứ 4 ở cả hai bên — cuốn nào đáng tin hơn?

## 3. Vấn đề: hai thang điểm không cộng được

BM25 không có trần (vài chục điểm, tuỳ câu hỏi); cosine nằm trong 0–1. Cộng thẳng → BM25 át hết. Chuẩn hoá (chia cho max) thì phụ thuộc
từng câu hỏi, dễ méo. Cách đơn giản và bền nhất: **bỏ điểm, chỉ dùng thứ hạng**.

## 4. RRF — Reciprocal Rank Fusion

```
RRF(đoạn) = Σ_trên mỗi danh sách   1 / (k + hạng của đoạn trong danh sách đó)        k thường = 60
```
Không có trong danh sách → đóng góp 0.

| Đoạn | Hạng BM25 | Hạng vector | RRF |
|---|---|---|---|
| X | 1 | 5 | 1/61 + 1/65 = 0,0318 |
| Y | 4 | 4 | 1/64 + 1/64 = 0,0313 |
| Z | 1 | — | 1/61 = 0,0164 |
| W | — | 1 | 0,0164 |

→ Đoạn **cả hai cùng đồng ý** (X, Y) thắng đoạn chỉ một bên thích (Z, W). *Trả lời câu 2 mục 2.*
`k = 60` làm cho chênh lệch giữa hạng 1 và hạng 5 nhỏ (không để một bên độc đoán); k nhỏ hơn → ưu tiên đỉnh mạnh hơn.

Cài đặt ~10 dòng:
```python
def rrf(*lists, k=60):
    s = {}
    for lst in lists:
        for rank, doc in enumerate(lst, 1):
            s[doc] = s.get(doc, 0) + 1 / (k + rank)
    return sorted(s, key=s.get, reverse=True)
```

Trong `recall.py`: lấy top-50 từ FTS5 (đã có) + top-50 từ sqlite-vec → `rrf()` → top-12. Các luật sau đó (chốt trên chuyện, nhãn `cu`, ưu tiên bộ phận) giữ nguyên.

## 5. Các cách trộn khác

| Cách | Làm gì | Ưu | Nhược |
|---|---|---|---|
| **RRF** | trộn theo hạng | không cần chỉnh, bền | bỏ thông tin "cách nhau bao xa" |
| Cộng có trọng số sau chuẩn hoá | α·BM25' + (1−α)·cos | tinh chỉnh được | phải chọn α, chuẩn hoá theo câu méo |
| Lọc nối tiếp | BM25 lấy 200 → vector xếp lại | rẻ | đoạn BM25 bỏ sót (lỗ từ vựng!) không bao giờ quay lại — mất đúng cái cần |
| Reranker (mục 6) | model đọc câu + đoạn cùng lúc | chính xác nhất | chậm, thêm model |

## 6. Reranker (cross-encoder)

Embedding mã hoá câu hỏi và đoạn **riêng rẽ** (bi-encoder) rồi so — nhanh vì vector đoạn tính sẵn. **Cross-encoder** đọc *cặp*
"câu hỏi + đoạn" **cùng lúc** rồi cho một điểm liên quan. Nó thấy được tương tác từng chữ ("cấm" trong đoạn vs "có nên" trong câu hỏi),
nên chính xác hơn, nhưng phải chạy một lần cho *mỗi* cặp → chỉ dùng cho top 30–50 sau RRF.
Ví dụ: họ `bge-reranker` (đa ngữ). Chạy cục bộ, 0 token LLM, ~vài chục–vài trăm ms cho 50 cặp trên CPU.

Thứ tự thường dùng: **BM25 ∥ vector → RRF → reranker → top k.**

## 7. Nghiên cứu nói gì (vòng 6 của 05)
- Hybrid RRF là **baseline mạnh**: trong một benchmark tài chính, RRF hơn BM25 hoặc vector riêng lẻ (Recall@5, MRR). Trong một bài GraphRAG
  CPU (SPRIG, 2602.23372), RRF hybrid là đối thủ khó vượt — graph có chỗ thắng chỗ không. (Nguồn thứ cấp/abstract, xem bảng vòng 6.)
- Ý nghĩa: trước khi nói "KG tốt hơn rất nhiều", phải so với **hybrid**, không phải với BM25 trơn. So với BM25 trơn là so với đối thủ yếu.

## 8. Scale
- Nhỏ/vừa (Seriously): hybrid + RRF đủ; reranker tuỳ chọn.
- Lớn: reranker gần như bắt buộc (nhiều đoạn "gần gần" do vector đưa lên).
- Cái vỡ: độ trễ khi thêm reranker; quản lý hai chỉ mục phải đồng bộ (một đoạn đã xoá ở FTS mà còn ở vector → "bóng ma").

## 9. Dừng lần hai — Seriously
- Đọc `search()` trong `tools/claude/recall.py`: chỗ chèn RRF là sau vòng AND/OR, trước dòng `rows.sort(...)`.
- Hỏi: luật "chốt trên chuyện cùng BUCKET" dựa trên *điểm* BM25 (`round(r[7]/BUCKET)`). Sau RRF không còn điểm BM25 → luật này phải viết lại theo
  điểm RRF. Đây là loại chi tiết nhỏ làm tụt chất lượng nếu không đo lại.

## 10. Bốn nền tảng
RRF là cộng trừ thuần — giống nhau mọi nơi. Phần nặng là vector (05b §9) và reranker (nặng hơn embedding, iOS/Android máy yếu khó chạy realtime).

## 11. Tóm tắt
Hybrid = chạy cả hai thủ thư, tin cuốn cả hai cùng đưa; RRF trộn theo hạng (10 dòng); reranker đọc kỹ top đầu.

**Thuật ngữ:** hybrid search · RRF · bi-encoder · cross-encoder · reranker. **Bài sau:** [05d — knowledge graph](05d-knowledge-graph.md).
