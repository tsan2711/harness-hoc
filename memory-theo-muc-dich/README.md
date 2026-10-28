# memory-theo-muc-dich/ — hệ thống nhớ của công ty agent sẽ được triển khai ra sao, và vì sao

Bản dễ đọc của thiết kế `docs/shared/knowledge-graph-design.md` (Seriously, Bi duyệt 2026-10-26). Thiết kế gốc viết cho agent
(bảng dày, ký hiệu M1–M11, K0–K6, L0–L4); chuỗi này kể lại cùng nội dung bằng chuyện đời thường + ví dụ trong dự án.

Mỗi bài: chuyện mở đầu → **Dừng 30 giây** (tự nghĩ, không có câu hỏi bắt trả lời) → các cách làm + ưu/nhược → khi lớn lên thì sao.
Mỗi bài ≤ 7 phút. Đọc theo thứ tự.

| # | Bài | Ý chính | Phần thiết kế |
|---|---|---|---|
| 01 | [Tìm theo chữ & vì sao một kho chung bị loãng](01-mot-kho-khong-du.md) | inverted index, BM25, FTS5; hình dạng câu hỏi quyết định hình dạng kho | §1, §1b, V0 |
| 02 | [Phân loại trí nhớ: 11 kho](02-muoi-mot-loai-tri-nho.md) | CoALA → M1–M11; ghi đúng kho | §1b |
| 03 | [Query routing](03-bo-chon-kho.md) | luật → JSON schema → model, gộp bằng RRF, biết nói "không có" | V6, §5 |
| 04 | [Đồ thị tất định & "nghi cũ"](04-ban-do-quan-he.md) | entity linking, ontology, BFS ngược | V1–V5, §3, §4 |
| 05 | [Đồ thị có model](05-do-thi-co-model.md) | claim có thời gian, PPR, GraphRAG/LightRAG, cổng quote | §3, §4 |
| 06 | [Đo, lộ trình & tách repo](06-do-lo-trinh-tach-repo.md) | bộ vàng, recall@k/store@k/MRR; K0–K6; tách repo | V7–V8, §6–§9 |

## Trạng thái triển khai (2026-10-28)

Thiết kế đã chạy R1–R9 (`knowledge-graph-design.md` §10). Đọc bài nào cũng nhớ: bài viết trước khi đo, nên **số liệu và thứ tự là của lúc thiết kế**.
- Đã vào code: đo recall@3/MRR + McNemar (R1–R2), làm sạch bí danh, `refs` thành `kg://id` (R3–R4), RRF giữa tủ + tủ bậc 1 làm sàn (R5–R6),
  doc2query commit 30 ngày (R6b), claim + Stop hook (R7, cờ tắt), đo online (R8).
- Kết quả thật khác kỳ vọng: cổng "para +15 điểm" **không đạt** (6→9/33 sau doc2query); viết lại truy vấn bằng luật 0 token không hơn; RRF mạnh tay làm nhóm xdept lùi.
  Bài học: đo trước đúng chỗ — nhiều ý "nghe hợp lý" bị bộ vàng bác.
- Tách repo (bài 06), **R11 xong 2026-10-28**: Thousandfold → `seriously-thousandfold`, depts → `seriously-depts` đã chuyển hẳn (git ở repo tách,
  CI Thousandfold chạy ở repo tách). Cách làm "lớp phủ symlink": ở hub `Thousandfold/` là symlink sang repo tách; trong repo tách có symlink
  ngược về `tools/`, `docs/`, `company/`… nên mọi lệnh cũ vẫn chạy, chỉ git đổi chỗ. Công cụ đọc git gọi `tools/company/repos.py`
  (`repo_of`: path này thuộc repo nào). June + NanoSwarm đóng băng, ở lại monorepo. Thư mục cũ trong hub chỉ gỡ sau 2026-11-11 + Bi duyệt.
  Chỗ mơ hồ #1 dưới đây: lan "nghi cũ" chạy ở hub (đồ thị gộp mọi repo qua `repos.log`), không ở pre-commit từng repo.
- "Chỗ còn mơ hồ" #7 (trạng thái tài liệu lệch) đã được sửa ở R10.

## Bảng tra ký hiệu (khi đọc lại thiết kế gốc)

| Ký hiệu | Nghĩa thường |
|---|---|
| M1…M11 | 11 "tủ" trí nhớ (bài 02) |
| K0…K6 | 7 pha của lộ trình (bài 06) |
| L0…L4 | 5 lớp vẽ bản đồ, từ máy đọc miễn phí tới model tóm tắt (bài 04) |
| V0…V8 | 9 cuộc tự tranh luận trong thiết kế |
| intent | ý định của câu hỏi: tra, vì sao, chuyện, ảnh hưởng, tổng quan, cách làm, số, gu, asset (bài 03) |
| planner | lễ tân điền phiếu JSON chọn tủ (bài 03) |
| claim | mệnh đề có ngày hiệu lực, cái cũ đóng ngày chứ không xoá (bài 02, 04) |
| ontology | danh mục đóng các loại nút/cạnh của bản đồ (bài 04) |
| BFS | đi lần theo hàng xóm từng bước (bài 04) |
| PPR | lan điểm từ nút hạt giống sang hàng xóm (bài 04) |
| RRF | trộn bảng xếp hạng bằng thứ hạng, không bằng điểm (bài 03) |
| θ | điểm sàn: dưới sàn thì trả "không có trong kho" (bài 03) |
| store@1 | tỉ lệ lễ tân chọn đúng tủ ngay lần đầu (bài 06) |
| hub | repo trụ sở giữ công cụ + chỉ mục gộp (bài 05) |

## Chỗ thiết kế còn mơ hồ

Ghi lại những chỗ khó giải thích vì thiết kế chưa nói rõ — nên chốt trước khi tới pha liên quan.

1. **"Nghi cũ" chạy ở đâu sau khi tách repo (K1 ↔ K4).** §4 nói lan truyền chạy lúc commit (pre-commit), nhưng §3.4/§6.1 nói chỉ mục gộp
   mọi repo chỉ có ở hub và không commit. Sau K4, pre-commit của `seriously-thousandfold` không nhìn thấy sổ tay art trong
   `seriously-depts` → không thể đi ngược mũi tên sang phòng khác. Cần nói rõ: lan truyền chạy ở hub (theo lịch / khi pull), hay mỗi
   repo giữ bản sao cạnh chéo?
2. **Ranh giới M4 và M5.** M4 (quyết định có ngày) được cất ở `kg/claims/` và `claim` cũng là một loại nút của bản đồ M5. Vậy M4 là một
   tủ riêng hay là một phần của M5? Ảnh hưởng tới việc đếm store@1 trong bộ vàng K0 (câu "vì sao" chấm đúng tủ M4 hay M5?).
3. **"Planner không được bỏ kho mặc định" nhưng planner tự chọn intent.** Đổi intent là đổi luôn bộ kho mặc định, nên ràng buộc này
   yếu hơn vẻ ngoài. Có cần giữ intent của bậc 1 (luật) làm sàn khi bậc 2 chạy không?
4. **Ngưỡng chưa có số.** θ, θ_min, "top-1 yếu", N nút đổi để dựng lại tóm tắt cụm (L4) đều chưa có giá trị; theo luật "đo trước",
   nên ghi rõ là K0 sẽ đặt chúng.
5. **"0 token" ở K0/K0b.** Model pipeline không tốn, nhưng soạn ≥ 100 câu vàng (đáp án từ commit thật) và duyệt bảng bí danh 3 game là
   việc của phiên agent — vẫn tốn token phiên. Nên ghi ước lượng riêng để không bị bất ngờ như pilot thẻ (chi phí thật ×5).
6. **Cạnh `refs` (unit→doc) nằm trong danh sách đi ngược khi lan "nghi cũ".** Đi ngược `refs` từ một doc sẽ tới *cả một unit* (một phòng),
   không tới một file cụ thể — kết quả là "phòng X nghi cũ" chung chung. Có lẽ ý là gửi việc cho phòng đó, nhưng nên viết rõ.
7. **Trạng thái tài liệu lệch nhẹ.** Đầu `memory-architecture.md` vẫn ghi KG "chờ Bi chốt §9", trong khi §9 thiết kế đã ghi Bi duyệt
   2026-10-26 và nói nó thay §6–§7 của `memory-architecture.md` khi duyệt — file cũ chưa được cập nhật.
