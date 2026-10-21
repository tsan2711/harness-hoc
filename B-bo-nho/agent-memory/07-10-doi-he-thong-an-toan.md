# 07-10 — Đổi hệ thống an toàn

> Chuỗi 07, bài 10/12. Đọc ~9 phút.
> **Bạn đã biết:** các mảnh của trí nhớ — ghi file, tìm, đẩy, nhãn, cạnh, luật xếp, nhắc lúc ghi ([07-02](07-02-ghi-ra-ngoai.md)…[07-08](07-08-luc-ghi.md));
> bộ đo có bộ luyện / bộ thi, recall@k, so từng câu, chỉ số dùng thật ([07-09](07-09-do.md)).

## 1. Chuyện mở đầu

Minh hứng khởi: "làm luôn ba thứ một lần — tìm theo nghĩa bằng vector, đẩy ở mỗi câu, và luật xếp mới". Ba ngày sau: công cụ tìm chậm
thêm 300 ms, câu diễn đạt lại +2, câu đúng chữ **−1**, và lần đầu tiên có bản cũ lên trên bản mới. Không ai trả lời được: *cái nào* gây
ra *cái nào*? Gỡ thì gỡ cái gì? Cuối cùng quay lại bản cũ cả ba — ba ngày thành con số không.

## 2. Dừng 30 giây

- Vì sao nên làm **bộ đo** trước khi làm bất kỳ tính năng nào?
- "Tìm theo nghĩa tốt hơn" — tốt hơn bao nhiêu thì đáng thêm một model và một thư viện? Ai quyết, và quyết *khi nào*?
- Một tính năng đã chạy thật nhiều tháng — làm sao biết nó còn cần, khi model mới đã giỏi hơn?

## 3. Năm thói quen

**1. Đo trước (câu hỏi 1).** Không có câu nhiều bước trong bộ đo thì đồ thị không có gì để "thắng". Không có bộ thi thì vector "thắng" bằng
cách nào cũng được (rò rỉ). Làm tính năng trước bộ đo = tự chấm bài mình bằng đề mình ra *sau khi* làm bài.

**2. Một lần một thay đổi.** Mỗi bước là *một* thay đổi đo được. Chính là thứ Minh thiếu: ba thay đổi cùng lúc thì không tách được tác dụng.

**3. Luật thắng viết trước (câu hỏi 2).** Trước khi chạy thí nghiệm, ghi ra: "vector được giữ nếu bộ thi diễn đạt lại +≥ 3 câu, câu đúng
chữ không lùi, chậm thêm < 300 ms". Vì sao *trước*:
- **Chống dời cột gôn.** Chạy xong thấy +2, rất dễ tự nhủ "2 cũng tốt". Có luật trước thì +2 = không qua, hết bàn.
- **Gắn với chi phí.** +3 trên ~20 câu ≈ +15 % — vượt nhiễu (bài 07-09) và đáng một model + một thư viện + 300 ms.
- **So đúng đối thủ mạnh nhất.** Thử đồ thị thì so với hệ thống *đã có* vector, không so với bản trần — nếu không, đồ thị được "ăn" công
  của vector.
- **Hỏi chất lượng, không hỏi thời gian.** Cổng kiểu "chờ đủ 14 ngày rồi làm tiếp" không nói gì về việc tìm có tốt hơn không.

**4. Ablation — tắt một phần xem số đổi.** Giữ nguyên mọi thứ, tắt đúng một thành phần, chạy bộ đo. Số tụt → thành phần đó đang gánh;
số giữ nguyên → nó có thể thừa.

**5. Công tắc tắt + quay lui.** Mỗi tính năng có một **công tắc** (feature flag) — một dòng cấu hình tắt nó mà **không sửa code**. Có
công tắc thì: thử tắt dễ (ablation ngoài đời thật), có sự cố thì tắt ngay, và **quay lui** (rollback) là gạt một dòng chứ không phải gỡ code.

## 4. "Nạng" — lớp chống đỡ có hạn dùng (câu hỏi 3)

Nhiều phần của hệ thống bao quanh agent tồn tại để bù chỗ yếu của model *hiện tại* — như cái nạng. Model mới giỏi hơn có thể không cần
nạng nữa, mà nạng vẫn tốn token, thời gian và sự chú ý. Nên mỗi lớp như vậy cần ghi sẵn:
- chỉ số nói nó có ích (ví dụ: tỉ lệ lần đẩy có đoạn đúng);
- **phép thử tháo**: tắt 14 ngày, so số vấp / số token / số lần agent phải tự đào; không tệ đi → bỏ;
- ngày xét lại, và xét lại ngay khi đổi model.

## 5. Thứ tự hợp lý cho trí nhớ agent

| Bước | Làm | Cổng qua bước | Loại |
|---|---|---|---|
| 1 | Bộ đo đủ nhóm (07-09) | chạy tự động, có số nền mọi nhóm | nền |
| 2 | Đẩy ở mọi điểm vào (07-04) | < 150 ms; 14 ngày: đoạn đẩy được dùng, token không tăng rõ | chắc chắn làm |
| 3 | Nhãn + cạnh + luật xếp + nhắc lúc ghi (07-05…07-08) | bản cũ không lên top 3 ở nhóm cũ/mới; nhóm khác không lùi | chắc chắn làm |
| 4 | Vector + trộn điểm ([05c](05c-hybrid-rrf-reranker.md)) | bộ thi +≥ 3 câu, đúng chữ không lùi, < 300 ms | **thí nghiệm** |
| 5 | Tìm dựa trên đồ thị ([05e](05e-graph-rag.md)) | so với bước 4: nhóm nhiều bước +≥ 2 câu, nhóm khác không lùi | **thí nghiệm** |

Bước 2 và 3 cần cho mọi kiến trúc nên làm ngay; bước 4 và 5 là cược, nên có luật thắng.

## 6. Các cách triển khai, trên chuyện của Minh

| Cách | Biết cái gì gây ra gì? | Gỡ từng phần được? | Gãy khi |
|---|---|---|---|
| A. Làm hết một lần | ✗ | ✗ (quay lui cả) | luôn, khi có một chỉ số lùi |
| B. Từng bước, không cổng | một phần | ✓ | "thấy ổn" thay cho số; dời cột gôn |
| C. Từng bước + luật thắng viết trước | ✓ | ✓ | bộ đo yếu (→ nên đo trước) |
| D. C + công tắc + phép thử tháo | ✓ | ✓ bằng một dòng, cả sau khi chạy thật | quên đăng ký công tắc |

**Quy luật:** đo trước, đổi một thứ một lần, đặt luật thắng trước khi biết kết quả, và để mọi lớp có công tắc tắt + ngày xét lại.

## 7. Scale

- **Nhỏ** (một người): bước + cổng có thể chỉ là một dòng ghi chú.
- **Vừa** (nhiều người/agent cùng đụng một hệ thống): bước + cổng là cách duy nhất để hai người không phá số của nhau; cổng chạy tự động
  lúc lưu vào git bắt ngay.
- **Lớn** (nhiều đội, nhiều thí nghiệm cùng lúc): thí nghiệm chồng nhau làm ablation nhiễu; cần công tắc theo nhóm người dùng và lịch thí
  nghiệm. Cái vỡ là **khả năng chỉ ra nguyên nhân**.

## 8. Bốn nền tảng

Đây là quy trình, không phụ thuộc nền tảng — nhưng **con số** trong cổng thì có: "< 150 ms" phải ghi đo trên máy nào (Windows thường
chậm hơn Mac ở bật chương trình con, bài 07-04). Trên **iOS / Android**, cùng ý là **phát hành theo từng phần + công tắc từ xa**: Google
Play cho phát hành cho X % người dùng, App Store có phát hành dần 7 ngày; cấu hình từ xa (như Firebase Remote Config) là công tắc tắt tính
năng không cần bản build mới — và luật "giữ / gỡ" đặt trước khi mở cho 100 %.

## 9. Tóm tắt

Đổi hệ thống an toàn = đo trước → một thay đổi một lần → luật thắng viết trước, so với đối thủ mạnh nhất → công tắc tắt + phép thử tháo
cho mọi lớp chống đỡ.

**Thuật ngữ:** gate (cổng) · pre-registered criterion (luật thắng đặt trước) · moving the goalposts (dời cột gôn) · ablation · feature flag (công tắc) · rollback (quay lui) · crutch (nạng) · staged rollout (phát hành dần).

**Giờ bạn biết thêm:** *thứ tự* và *cách* lắp các mảnh của bài 02–08 vào một hệ thống đang chạy mà không phá nó.

---

> **Ví dụ thật: Seriously làm thế này**
>
> - Kế hoạch của Seriously chính là bảng §5, đặt tên P0 (đo) → P1 (đẩy) → P2 (thay thế lúc ghi) → P3 (vector, thí nghiệm) → P4 (đồ thị,
>   thí nghiệm). Bản sống: `docs/shared/memory-architecture-proposal.md` §3. Một phần P1 đã có (đẩy lúc mở phiên có việc dở, 2026-10-16).
> - Công tắc + nạng có thật: file `company/layers.toml` liệt kê mọi "lớp" của hệ thống, mỗi lớp có chỉ số, ngày xét lại, và nếu là nạng thì
>   có phép thử tháo. Đầu file ghi luật: *không có số đo → không thêm lớp*.
> - Lớp "đẩy lúc nhận việc" có phép thử tháo: `kit company crutch-test recall-inject --days 14` ghi hạn tắt vào file; đầu hàm đẩy kiểm công
>   tắc và trả rỗng → tắt mà không sửa code; `--report` so số vấp trong 14 ngày tắt với 14 ngày trước. Khi đổi model, công cụ nhắc "cần
>   thử tháo lại".
> - Seriously từng có cổng kiểu "vector chỉ sau 14 ngày đẩy" — đã bị thay bằng cổng chất lượng (+≥ 3 câu bộ thi) vì đúng lý do ở §3.

**Bài sau:** [07-11 — Nhận diện thực thể](07-11-nhan-dien-thuc-the.md).
