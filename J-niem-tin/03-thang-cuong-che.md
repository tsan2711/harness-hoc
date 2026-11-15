# Bài J03 — Thang cưỡng chế: biến luật thành cổng, và đừng để cổng chặn nhầm

> **Bạn đã biết** (J02): đo hậu quả để biết hệ thống tốt lên chưa. Giờ: khi đo thấy *cùng một lỗi lặp lại*, sửa bằng cách nào bền nhất?

## 1. Câu chuyện
Quy ước của nhóm: "UI mới phải đặt cạnh ảnh mẫu đã duyệt trước khi báo xong." Ghi trong tài liệu. Agent vẫn quên 3 lần. Nhóm viết một cổng chặn commit nếu thiếu ảnh so sánh — sáng hôm sau cổng chặn nhầm gần hết commit vì chỉ kiểm tên file `compare.jpg`, trong khi nhiều việc dùng tên khác.

## 2. Dừng 30 giây
- Một luật có thể "sống" ở những tầng nào, từ yếu đến mạnh? (gợi ý: lời dặn → … → compiler)
- Cổng chặn nhầm 1 trong 30 và chặn nhầm 29 trong 30 khác nhau thế nào về hậu quả với niềm tin?
- Làm sao biết cổng mới có chặn nhầm *trước khi* cho nó chặn thật?

## 3. Thang cưỡng chế (mạnh → yếu)
1. **Cấu trúc**: sai là *không viết nổi* (ví dụ assembly definition cấm module này gọi module kia).
2. **Compiler / source generator**: sai là *không build được* (mã lỗi như `STU0xx`, `SSJ0xx`).
3. **Lint / pre-commit / guard**: sai là *không commit được*.
4. **Rule / skill** (chữ cho agent đọc): sai là *có thể quên*.
5. **Review người**: sai là *có thể lọt*.

Nguyên tắc: **một luật bị vi phạm ≥ 3 lần (có bằng chứng) thì đẩy lên tầng cao hơn**, và ghi lại *"vì sao không lên tầng cao hơn nữa"* (ví dụ: không đo được bằng máy). Chữ trong tài liệu còn tốn **context** mỗi phiên (always-on); chuyển luật chữ → code thì context *giảm*.

### Shadow → enforce
Cổng mới chạy chế độ **shadow** (ghi "sẽ chặn" nhưng cho qua) ≥ 2 ngày; xem log `would_block`; chỉ khi false-positive thấp mới bật chặn thật. Mỗi cổng có **cờ tắt 1 lệnh** (rollback).

### Đo false-positive bằng replay
Lấy 30 commit gần nhất (đã biết là hợp lệ), chạy cổng lên từng cái. Số cổng chặn = false-positive. Mục tiêu ≤ 1/30. Bài học thật từ red-team: bản cổng 1 dựa vào "claims" (khai báo ai sửa file nào) chặn nhầm **29/30** vì Bash ghi file 200+ lần/ngày mà không tạo claim; đổi sang "file sửa kể từ commit trước của chính nó" còn 1/30 và vẫn bắt được vi phạm thật.

### Test dương và âm cho mỗi cổng
- **Âm**: cố ý vi phạm → cổng phải chặn.
- **Dương**: làm đúng → cổng *không* được chặn.
Thiếu một nửa là cổng hoặc vô dụng (luôn cho qua) hoặc phiền (luôn chặn).

## 4. Ba cách xử lý luật bị lặp lỗi
| Cách | Ưu | Nhược / điểm gãy |
|---|---|---|
| **A. Viết rõ hơn trong tài liệu** | rẻ | tốn context; agent vẫn quên; không kiểm được |
| **B. Cổng cứng bật ngay** | hiệu quả tức thì | chặn nhầm khi hệ thống đang nhiễu (≈22 vấp/ngày) → người tắt cổng đi |
| **C. Cổng shadow → đo replay → enforce → có cờ tắt** | biết trước false-positive; rollback rẻ | chậm hơn vài ngày; cần viết lệnh replay |

Quy luật: *cổng chưa đo false-positive là một lỗi đang chờ xảy ra.*

## 5. Scale
- **Ít luật:** nhắc là đủ.
- **Chục luật, nhiều agent:** cần *kiểm kê* (luật → tầng hiện tại → tầng đích → bằng chứng vấp), xếp theo tần suất vấp thật (TOP5), không phải theo cảm giác.
- **Lớn:** cổng chồng cổng làm commit chậm và khó đoán nguyên nhân → mỗi cổng phải in 1 dòng lý do + cách xử lý.
- **Giới hạn thật:** guard bằng regex trên lệnh shell không phải hàng rào (đo: lọt 13/25 cách xoá/ghi đè). Hàng rào thật là cô lập (J06).

## 6. Ví dụ thật: Seriously làm thế này
`tools/harness/wip/rule-ladder.md`: 19 luật, TOP5 theo `friction.jsonl`. P1 cài 4 cổng, tất cả shadow trước; check: `kit selftest` PASS + `kit improve check` (always-on không tăng) + replay 30 commit ≤ 1 false-positive. Red-team: `review-B-redteam.md`. Mở file đó, xem cổng 2 đổi từ "chỉ tên `compare.jpg`" (chặn nhầm 11/30) sang "cả `review.md` có nhắc ref".

## 7. Bốn nền tảng
Cổng ở `git commit` chạy mọi OS như nhau (hook git). Khác biệt: Windows cần chú ý ký tự xuống dòng và đường dẫn `\`; trên Android/iOS cổng *build* (ký số, quyền, kích thước) là tầng 2–3 hữu ích nhất vì lỗi ở đó chỉ lộ khi lên store.

**Giờ bạn biết thêm:** thang cưỡng chế, shadow→enforce, replay, test dương/âm, ngưỡng "≥ 3 lần vấp thì lên tầng".
**Bài sau:** J04 — verification theo sản phẩm.
