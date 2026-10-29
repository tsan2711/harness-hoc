# migrate-thuc-chien/ — chuyện thật khi đưa thiết kế trí nhớ + tách repo vào chạy

Chuỗi [memory-theo-muc-dich](../memory-theo-muc-dich/README.md) là *thiết kế* (viết trước khi đo). Chuỗi này là *chuyện sau đó*:
26–28/10/2026, ~140 commit, R1–R11 — cái gì thắng, cái gì bị số đo bác, lỗi thật lúc chuyển nhà, và mỗi kỹ thuật nhỏ đổi được bao nhiêu.

Khác các chặng khác: đây là **nghiên cứu một ca thật**, nên ví dụ Seriously nằm ngay trong thân bài (mỗi thuật ngữ vẫn giải nghĩa lần đầu).
Mỗi bài: chuyện ngắn → dừng 30 giây → một mạch nhân quả (bước này sinh vấn đề bước sau), gắn vào CPU cache / Unity → số thật → 4 nền tảng. Thuật ngữ giải ngay chỗ dùng lần đầu.

| # | Bài | Trạng thái |
|---|---|---|
| 00 | [Toàn cảnh: trí nhớ agent là một hệ cache, 5 bước nối nhau](00-tong-quan.md) | xong (viết lại 10-28) |
| 01 | [Đo đúng thứ agent thấy: hit@3, MRR, McNemar, Wilson, tất định](01-do-dung-thu-agent-thay.md) · [lab](lab/01_do_recall.py) | xong |
| 02 | [Tên riêng, bí danh và cặp âm tiết tiếng Việt](02-ten-rieng-va-am-tiet.md) · [lab](lab/02_am_tiet.py) | xong |
| 03 | [Bake sẵn: doc2query, khoá băm, ước token trước](03-bake-san-doc2query.md) · [lab](lab/03_bake_san.py) | xong |
| 04 | Trộn nhiều kho: RRF và hạn ngạch | chưa |
| 05 | Invalidation: nghi cũ, false sharing, ID ổn định | chưa |
| 06 | Chuyển nhà: lớp phủ symlink vs submodule vs monorepo | chưa |
| 07 | Lỗi chuyển nhà: đường dẫn 2 mặt, biến môi trường rò | chưa |
| 08 | Cổng định kỳ: lệnh kiểm phải biết trả sai | chưa |

Nguồn (repo riêng, không công khai): `docs/shared/knowledge-graph-design.md` §10, `tools/harness/r11-cutover.md`,
`tools/harness/d7-2026-10-28.md`, `company/state/evals/memory-gates/latest.md`.
