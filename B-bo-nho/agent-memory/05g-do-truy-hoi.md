# 05g — Đo truy hồi: con số nói gì, không nói gì, và thí nghiệm công bằng

> Đi kèm [05](05-tranh-luan-kg-vs-recall.md) vòng 5–7, mục 9. Đây là "trọng tài" của cuộc tranh luận.

## 1. Câu chuyện

Commit `9290232`: *"recall_para 45→50 % (hết đỏ)"*. Dashboard xanh. Hôm sau Bi hỏi một câu diễn đạt lại mới, không có trong bộ đo — trượt.
Con số tăng có thật không? Nó đo cái gì?

## 2. Dừng 30 giây
- 45 → 50 % trên 20 câu là bao nhiêu câu?
- Nếu người chỉnh đồng nghĩa *nhìn* vào 20 câu đó để chỉnh, con số 50 % còn nói về câu mới được không?
- Một bộ đo toàn câu một bước có thể bao giờ cho thấy graph thắng không?

## 3. Các chỉ số

Cho mỗi câu hỏi có danh sách đáp án đúng (**gold**). Hệ thống trả danh sách xếp hạng.
| Chỉ số | Định nghĩa | Hỏi gì |
|---|---|---|
| **recall@k** | tỉ lệ câu có ≥ 1 gold trong top k (biến thể: tỉ lệ gold tìm được) | "có lọt top không?" — Seriously dùng recall@12 |
| precision@k | phần top k là gold | "top có sạch không?" |
| **MRR** | trung bình 1/hạng của gold đầu tiên | "đúng có đứng *đầu* không?" — quan trọng khi `hint()` chỉ đưa 3 đoạn |
| nDCG | như MRR nhưng tính nhiều gold, giảm dần theo hạng | |
| **cũ@k** (Seriously) | số đoạn đã bị thay lọt top k | chính bài toán 05f |
| ms/truy vấn | | hook phải < 300 ms |

recall@12 tốt mà MRR kém → gold có mặt nhưng ở hạng 10; `hint()` (3 đoạn) **không thấy**. Ta nên đo cả recall@3.

## 4. Ba cái bẫy của bộ đo nhỏ

### 4.1 Cỡ mẫu
20 câu → mỗi câu = **5 điểm %**. Khoảng tin cậy 95 % (Wilson) của 10/20 ≈ **30 %–70 %**. 45 → 50 % = **một câu** = không phân biệt được với may rủi.
Muốn thấy chênh 10 điểm % một cách tin được cần cỡ trăm câu; với bộ nhỏ, so **từng câu** (câu nào chuyển trượt→trúng, trúng→trượt) có ích hơn so tỉ lệ.
*Đáp câu 1 mục 2.*

### 4.2 Rò rỉ / quá khớp (leakage, overfitting)
Đồng nghĩa trong `synonyms.toml` được viết *để vá đúng câu trượt* → con số đo **khả năng thuộc đề**, không phải khả năng tìm câu mới. *Câu 2.*
Chữa: tách **bộ phát triển** (được nhìn, được chỉnh) và **bộ giữ riêng** (held-out — không ai nhìn khi chỉnh, chỉ chạy để báo). Bộ giữ riêng tụt
trong khi bộ phát triển tăng = đang thuộc đề.

### 4.3 Thước đo chỉ thấy cái nó hỏi (coverage bias)
45 câu, 43 câu đúng 1 gold, mọi câu diễn đạt lại một bước → bộ đo **không có câu nhiều bước, không có câu toàn cục**. Một cấu hình giỏi multi-hop sẽ
không được ghi điểm. *Câu 3: không bao giờ.* Đây là điểm cho Bi ở vòng 7: kết luận "graph không cần" từ bộ này là méo.
Chữa: bộ câu phải **lấy mẫu từ câu thật** (transcript: Bi và agent đã hỏi gì) theo tỉ lệ thật, không chỉ câu người làm harness nghĩ ra.

## 5. Bộ vàng tốt trông thế nào

| Nhóm | Bao nhiêu | Nguồn | Đo |
|---|---|---|---|
| kw — từ khoá | 20 (có) | đã có | BM25 không lùi |
| para — diễn đạt lại, phát triển | 20 (có) | đã có | |
| para — **giữ riêng** | 15–20 (mới) | rút từ câu thật trong transcript, người khác viết | lỗ từ vựng thật |
| multi — **nhiều bước** | 10+ (mới) | câu quan hệ thật ("ADR nào chi phối…") | graph có đất không |
| stale — **thay thế** | 10–15 cặp (mới, mở rộng 5 câu `trap`) | quyết định đổi có thật trong git | cũ@k, nhãn có hiện không |
| tỉ lệ thật | — | đếm loại câu trong 2 tuần transcript | nhóm nào đáng tối ưu |

## 6. Thí nghiệm công bằng (khung cho mục 9 bài 05)

1. **Đặt luật thắng trước khi chạy** (pre-registration): "graph đáng dựng nếu hơn hybrid ≥ 2 câu ở nhóm multi và không tụt nhóm nào ≥ 1 câu". Đặt sau khi thấy
   số = tự lừa.
2. **Cùng bộ câu, cùng chunk, cùng k** cho mọi cấu hình. Chỉ đổi *một* thứ mỗi lần (ablation): BM25 → +vector → +RRF → +reranker → +graph.
3. **So với đối thủ mạnh:** graph so với **hybrid**, không so BM25 trơn ([05c](05c-hybrid-rrf-reranker.md) §7).
4. **So từng câu**, in bảng chuyển trạng thái; đọc tay các câu đổi.
5. **Báo chi phí cạnh chất lượng:** ms/truy vấn, thời gian dựng, token, MB.
6. **Đo lại sau 14 ngày dùng thật:** `inject_rate`, số lần agent phải mở transcript thô — chất lượng *trên việc thật*, không chỉ trên đề.

## 7. Bảng các cách đo

| Cách | Ưu | Nhược |
|---|---|---|
| Bộ vàng tay (hiện tại) | rẻ, nhanh, chạy mỗi commit | nhỏ, lệch người viết, rò rỉ |
| Câu thật từ transcript + gán gold tay | đúng phân phối | tốn công gán |
| LLM làm giám khảo (đánh giá đoạn có liên quan) | phủ rộng | tốn token, giám khảo cũng sai; phải kiểm mẫu |
| Đo trên việc (A/B: bật/tắt tính năng, đo token tới `check:` xanh) | đo đúng thứ cần | chậm, nhiễu, cần nhiều việc |
`layers.toml` của Seriously có `remove_test` cho `recall-inject` — đó là cách thứ tư.

## 8. Scale
- Nhỏ: 40 câu tay là ổn để **bắt lùi** (regression gate), không đủ để **chọn kiến trúc**.
- Vừa: chọn kiến trúc cần ≥ 100 câu phân nhóm + giữ riêng.
- Lớn: bộ đo phải tự lấy mẫu liên tục từ câu thật; con người chỉ kiểm mẫu.

## 9. Dừng lần hai — Seriously
- `company/eval/recall/cases.toml`: đếm nhóm (kw 20 · para 20 · trap 5). Không có nhóm multi.
- `tools/claude/recall_eval.py`: chạy `sh tools/claude/kit.sh recall-eval` — dòng "×5 nhiễu cố định (cổng)" là cách giả kho lớn hơn để thử độ bền; dòng
  "trượt:" liệt kê câu trượt — mở từng câu đối chiếu gold.
- `company/eval/recall/baseline.json`: cổng lùi trong `kit selftest` — đúng vai "bắt lùi", không phải "chọn kiến trúc".

## 10. Bốn nền tảng
Đo là việc chạy trên máy dev (Mac). Liên hệ game: cùng bẫy với đo hiệu năng — một lần đo trên một máy là một mẫu; memory `feedback_measure_render_windowed`
(phải đo cửa sổ thật, không batchmode) là ví dụ "thước đo chỉ thấy cái nó đo".

## 11. Tóm tắt
Bộ đo nhỏ để bắt lùi, không để chọn kiến trúc; cảnh giác cỡ mẫu (1 câu = 5 %), rò rỉ (chỉnh theo đề), và thiên lệch phủ (không hỏi multi-hop thì không
thấy graph). Đặt luật thắng trước, so với đối thủ mạnh, đổi một thứ mỗi lần.

**Thuật ngữ:** gold · recall@k · precision@k · MRR · nDCG · confidence interval · held-out · leakage · coverage bias · ablation · pre-registration · regression gate.
