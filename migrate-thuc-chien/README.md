# migrate-thuc-chien/ — chuyện thật khi đưa thiết kế trí nhớ + tách repo vào chạy

Chuỗi [memory-theo-muc-dich](../memory-theo-muc-dich/README.md) là *thiết kế* (viết trước khi đo). Chuỗi này là *chuyện sau đó*:
26–28/10/2026, ~140 commit, R1–R11 — cái gì thắng, cái gì bị số đo bác, lỗi thật lúc chuyển nhà, và mỗi kỹ thuật nhỏ đổi được bao nhiêu.

Khác các chặng khác: đây là **nghiên cứu một ca thật**, nên ví dụ Seriously nằm ngay trong thân bài (mỗi thuật ngữ vẫn giải nghĩa lần đầu).
Mỗi bài: chuyện ngắn → dừng 30 giây → các cách làm + ưu/nhược → số thật → 4 nền tảng → thuật ngữ.

| # | Bài | Trạng thái |
|---|---|---|
| 00 | [Tổng quan: harness sau migrate + 10 bài học](00-tong-quan.md) | xong |
| 01 | Đo đúng thứ agent thấy: @3, MRR, so cặp, bộ đề ≥ 30 câu | chưa |
| 02 | Tên riêng & bí danh: "nhận ra" chưa chắc "tìm ra" | chưa |
| 03 | Báo động giả: lan "nghi cũ" 82 → 2 và ID ổn định | chưa |
| 04 | Trộn nhiều tủ: RRF, hạn ngạch, khi nào trộn làm hỏng | chưa |
| 05 | Model ở phía ghi: doc2query, claim, ước token trước | chưa |
| 06 | Chuyển nhà: lớp phủ symlink vs submodule / sparse / giữ monorepo | chưa |
| 07 | Lỗi chuyển nhà: đường dẫn 2 mặt, biến môi trường rò, lỗi cũ lộ ra | chưa |
| 08 | Cổng định kỳ & lệnh kiểm phải biết trả sai | chưa |

Nguồn (repo riêng, không công khai): `docs/shared/knowledge-graph-design.md` §10, `tools/harness/r11-cutover.md`,
`tools/harness/d7-2026-10-28.md`, `company/state/evals/memory-gates/latest.md`.
