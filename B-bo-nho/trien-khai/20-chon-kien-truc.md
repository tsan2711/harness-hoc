# 20 — Chọn kiến trúc

> Chuỗi "Triển khai trí nhớ", bài 20/21. Đọc ~10 phút.
> **Bạn đã biết** (01–19): bản đồ ba trục (bài 02), mọi khối xây (03–17), an toàn (18), đo (19).

## 1. Chuyện mở đầu

Ba đội ngồi cùng bàn, mỗi đội mang một tờ giấy ghi "kiến trúc trí nhớ tốt nhất" đọc được trên mạng. Ba tờ khác hẳn nhau. Không tờ nào sai — mỗi
tờ đúng cho dữ liệu của người viết nó.

## 2. Dừng 30 giây

- Trước khi chọn kho hay cách tìm, bạn cần trả lời những câu hỏi nào về **chính bài toán** của mình?
- Bắt đầu đơn giản rồi nâng cấp — nâng cấp lúc nào? Dấu hiệu gì?
- Lựa chọn nào khó đổi về sau nhất?

## 3. Bảy câu hỏi trước khi chọn (câu hỏi 1)

1. **Ai nhớ cho ai?** Một người, một nhóm, hàng nghìn khách? → phạm vi, an toàn (bài 18).
2. **Nhớ loại gì?** Sự kiện, sự thật, cách làm? Tỉ lệ mỗi loại? (bài 02)
3. **Bao nhiêu, tăng nhanh không?** Vừa bàn làm việc không? (bài 03)
4. **Câu hỏi trông thế nào?** Mã/tên, diễn đạt lại, nhiều bước, thời gian, tổng hợp? Lấy 30 câu thật đếm thử. (bài 09–12, 19)
5. **Sai đắt hay quên đắt?** → ai ghi, đọc kiểu gì (bài 13–14).
6. **Đổi thường không? Có phải xoá theo yêu cầu không?** → cập nhật, dòng dõi dữ liệu (bài 15).
7. **Chạy ở đâu, ngân sách bao nhiêu?** Máy chủ, máy tính, điện thoại; tiền mỗi câu, độ trễ chấp nhận được.

## 4. Đi từ câu trả lời tới khối xây

| Nếu… | Thì cân nhắc | Bài |
|---|---|---|
| Ít, vừa bàn | nhét hết, ghim | 03, 14 |
| Lịch sử chat dài, cần ý chính | tóm tắt cuốn chiếu | 04 |
| Người cần đọc/sửa trí nhớ | file ghi chú | 05 |
| Có dữ liệu cấu trúc (đơn, giá, lịch) | bảng, tra thẳng | 06 |
| Câu có mã, tên, số | tìm theo chữ | 09 |
| Câu diễn đạt lại, đa ngữ | tìm theo nghĩa, model hợp dữ liệu | 07, 10 |
| Trộn cả hai | lai + RRF, có thể xếp lại | 11 |
| Nhiều câu nhiều bước / tổng hợp | đồ thị (cạnh có sẵn trước) | 08, 12 |
| Sai đắt | người ghi hoặc duyệt; ghim / theo sự kiện | 13, 14 |
| Sự thật đổi nhiều | thời điểm, hiệu lực, "thay bởi" | 15 |
| Lỗi lặp lại | cách làm → rào chắn máy | 16 |
| Giọng / cách làm ổn định, lời dặn quá dài | fine-tune / LoRA | 17 |
| Nhiều người | kho tách ở tầng CSDL | 18 |

## 5. Bắt đầu nhỏ, nâng khi có dấu hiệu (câu hỏi 2)

Một đường đi thường gặp — không phải con đường duy nhất:
1. **Nhét hết / file ghi chú + ghim.** Đo 30 câu.
2. Bàn chật hoặc bộ đo hụt → **thêm tìm** (chữ nếu nhiều mã, nghĩa nếu nhiều diễn đạt lại).
3. Bộ đo hụt cả hai loại → **lai**.
4. Top đầu hay sai, kết quả được đặt tự động → **xếp lại**.
5. Câu nhiều bước chiếm phần đáng kể và bộ đo cho thấy hụt ở đó → **đồ thị**.
6. Mỗi bước: chạy lại bộ đo; **không** nâng nếu số không đổi.

Dấu hiệu nâng = **số trên bộ đo của bạn**, không phải độ mới của công nghệ.

## 6. Khó đổi nhất (câu hỏi 3)

- **Định dạng nguồn gốc** — giữ bản gốc (chat, tài liệu, sự kiện) ở dạng thô, dễ đọc. Mọi chỉ mục, vector, đồ thị, bản tóm nên **dựng lại được**
  từ đó. Đổi model embedding hay đổi kho khi ấy chỉ là dựng lại.
- **Phạm vi và quyền** — thêm tách người sau khi đã trộn dữ liệu rất đắt.
- **Dòng dõi (nguồn → bản dẫn xuất)** — thêm sau thì không biết bản tóm cũ sinh từ đâu.
- **Mô hình thời gian** — thêm "ghi lúc" cho dữ liệu cũ thì không còn biết.

Ba thứ cuối rẻ khi làm từ đầu, đắt khi làm sau — kể cả khi hệ thống còn nhỏ.

## 7. Ba kịch bản — kiến trúc cuối

**Mai (trợ lý cá nhân, điện thoại):**
- Ghim: hồ sơ ngắn + dị ứng. Theo sự kiện: nhắc món ăn → dị ứng.
- Chat thô (SQLite trên máy) + sự thật rút nền lúc sạc (model trên máy), mỗi sự thật trỏ về đoạn chat, có thời điểm.
- Tìm theo nghĩa, model đa ngữ, ngưỡng im lặng. Màn hình cho Mai xem/sửa/xoá.
- Đo: 30 câu gồm cập nhật và im lặng.

**Cửa hàng Lá (chatbot khách, máy chủ):**
- Bảng: khách, đơn, sản phẩm, giá → tra thẳng, không chép vào trí nhớ.
- Ghim: chính sách ngắn. Tìm theo nghĩa + bảng viết tắt cho câu hỏi chính sách.
- Mỗi khách: tóm ngắn cuối mỗi cuộc chat (model nhỏ). Kho tách theo khách ở tầng CSDL; mã hoá; TTL cho chat thô; xoá lan qua dòng dõi.
- Fine-tune LoRA cho giọng cửa hàng nếu lời dặn quá dài. Đo: tìm + kiểm lộ chéo tự động + tỉ lệ khách hỏi lại.

**Nhóm code (3 người, repo):**
- File hướng dẫn ngắn luôn trên bàn; ghi chú quyết định dạng file trong repo (git giữ lịch sử và giải ghi cùng lúc).
- Tìm chữ (grep / FTS) là lớp đầu; tìm nghĩa thêm sau nếu bộ đo hụt câu diễn đạt lại; mở rộng một bước theo cạnh git/link cho "ảnh hưởng tới đâu".
- Theo sự kiện: mở file X → ghi chú của X. Lỗi lặp lại → test/hook.
- Đo: bộ câu chia loại mã / diễn đạt lại / nhiều bước.

Ba kiến trúc khác nhau, cùng làm từ một bộ khối xây.

## 8. Scale

- Kiến trúc tốt **thay được từng khối** mà không đổi khối khác — vì bản gốc dựng lại được, và đọc/ghi đi qua một lớp giao diện chung
  (`ghi()`, `tìm()`, `xoá()`), không gọi thẳng kho cụ thể.

## 9. Bốn nền tảng

- **Windows / Mac:** máy tính đủ chạy hầu hết khối cục bộ; chọn thư viện chạy được trên cả hai.
- **iOS / Android:** cửa sổ ngữ cảnh nhỏ, pin, dung lượng → ưu tiên ghim ngắn, SQLite (FTS5 + vector), việc nặng chạy nền lúc sạc hoặc trên máy
  chủ; khi gửi dữ liệu lên máy chủ, nói rõ với người dùng.

## 10. Tóm tắt

Trả lời bảy câu hỏi về bài toán trước; chọn khối xây theo câu trả lời; bắt đầu nhỏ và chỉ nâng khi bộ đo cho thấy hụt; làm đúng từ đầu bốn thứ khó
đổi — bản gốc dựng lại được, phạm vi, dòng dõi, thời gian.

**Thuật ngữ:** requirements (yêu cầu) · building block (khối xây) · rebuildable index · interface / abstraction · lineage · migration.

**Giờ bạn biết thêm:** cách tự ghép một kiến trúc trí nhớ cho bài toán của mình — không cần chép của ai.

**Bài sau:** [21 — Hệ thống thật trên bản đồ](21-he-thong-that.md).
