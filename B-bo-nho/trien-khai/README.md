# trien-khai/ — Triển khai trí nhớ cho agent: tự chọn kiến trúc của mình

Chuỗi này **không bênh kiến trúc nào**. Nó trải ra *toàn bộ không gian lựa chọn*, từ cách đơn giản nhất (dán lại lịch sử chat) tới
cách nâng cao nhất (trí nhớ quy trình, trí nhớ trong trọng số, nhiều agent chia sẻ), để người đọc tự chọn theo bài toán của mình.

Khác với [agent-memory/ chuỗi 07](../agent-memory/README.md): chuỗi 07 dạy **một** kiến trúc (cách Seriously làm). Ở đây Seriously chỉ là
**một ví dụ trong nhiều ví dụ**, ở bài cuối.

## Luật riêng của chuỗi này (thêm vào khuôn [CACH-HOC.md](../../CACH-HOC.md))

1. **Không có người thắng mặc định.** Mỗi bài ≥ 3 cách; mỗi cách ghi rõ **"hợp khi…"** và **"gãy khi…"**. Không câu nào kiểu "cách X tốt nhất".
2. **Ba kịch bản chạy suốt chuỗi**, cố ý rất khác nhau, để thấy cùng một câu hỏi có đáp án khác nhau:
   - **A — Trợ lý cá nhân của Mai:** một người, chat hằng ngày, cần nhớ sở thích, lịch, chuyện đã kể.
   - **B — Chatbot chăm sóc khách của cửa hàng Lá:** hàng nghìn khách, mỗi khách nhớ riêng, dữ liệu cá nhân nhạy cảm, phải trả lời nhanh.
   - **C — Agent viết code của nhóm 3 người:** nhiều tài liệu, quyết định kỹ thuật, nhiều phiên làm việc, cần biết cái gì đã bị thay.
3. **Số liệu ghi rõ nguồn** và loại: nghiên cứu độc lập / nhà cung cấp tự báo / đo tự làm. Số "tự báo" không dùng để xếp hạng.
4. Giữ khuôn: chuyện → dừng 30 giây → các cách + chỗ gãy → bảng → scale → 4 nền tảng → tóm tắt + thuật ngữ; "Bạn đã biết" / "Giờ bạn biết thêm"; ≤ 10 phút/bài. Đọc **một bài một ngày**.

## Dàn bài

| # | Bài | Ý chính | Trạng thái |
|---|---|---|---|
| **Phần 1 — Nền** ||||
| 01 | [Model không nhớ](01-model-khong-nho.md) | LLM là hàm không trạng thái; ngữ cảnh, token; ba chỗ chứa trí nhớ; vòng ghi → quản lý → đọc | viết rồi |
| 02 | Bản đồ lựa chọn | ba trục: nhớ bao lâu · lưu bằng gì · ai điều khiển; bốn loại nội dung (đang làm / sự kiện / sự thật / cách làm) | chưa |
| **Phần 2 — Chưa cần kho ngoài** ||||
| 03 | Nhét hết vào ngữ cảnh | ngữ cảnh dài, "lạc ở giữa", cache prompt, khi nào thế là đủ | chưa |
| 04 | Tóm tắt và nén | tóm cuốn chiếu, nén khi đầy, xoá kết quả công cụ cũ; mất gì khi tóm | chưa |
| **Phần 3 — Lưu ở đâu** ||||
| 05 | File ghi chú | file hướng dẫn, thư mục trí nhớ agent tự sửa; người đọc được, git được | chưa |
| 06 | Bảng có cấu trúc | hồ sơ người dùng, cột/khoá, SQL; nhanh và chính xác cho câu đã biết trước | chưa |
| 07 | Kho vector | embedding, chia đoạn, tìm gần đúng; đọc theo nghĩa | chưa |
| 08 | Đồ thị tri thức | thực thể + quan hệ + thời gian hiệu lực | chưa |
| **Phần 4 — Tìm lại** ||||
| 09 | Tìm theo chữ | chỉ mục ngược, BM25; mã, tên riêng | chưa |
| 10 | Tìm theo nghĩa | diễn đạt lại, đa ngôn ngữ; chọn model embedding | chưa |
| 11 | Lai và xếp lại | trộn điểm (RRF), reranker, để agent tự tìm nhiều vòng | chưa |
| 12 | Đi theo đồ thị | nhiều bước, GraphRAG, HippoRAG; giá của việc dựng đồ thị | chưa |
| **Phần 5 — Ai điều khiển** ||||
| 13 | Ai quyết ghi gì | người khai · luật cố định · LLM trích tự động · agent tự gọi công cụ | chưa |
| 14 | Ai quyết khi nào đọc | agent tự kéo · hệ thống tự đẩy · trộn; ngân sách thời gian/token | chưa |
| 15 | Cập nhật, mâu thuẫn, quên | thêm/sửa/xoá, thời gian hiệu lực, phai theo thời gian, độ quan trọng, gộp/suy ngẫm | chưa |
| **Phần 6 — Nâng cao** ||||
| 16 | Trí nhớ cách làm | kỹ năng, học từ lần làm hỏng, thư viện kỹ năng | chưa |
| 17 | Trí nhớ trong trọng số | fine-tune, LoRA, học liên tục; khi nào đáng | chưa |
| 18 | Nhiều người, nhiều agent | phạm vi, chia sẻ, quyền, riêng tư, quyền được xoá | chưa |
| 19 | Đo | LoCoMo, LongMemEval, tranh cãi số tự báo; tự xây bộ đo cho mình | chưa |
| **Phần 7 — Chọn** ||||
| 20 | Chọn kiến trúc | cây quyết định theo bài toán; 6 kiến trúc mẫu, ai hợp cái nào | chưa |
| 21 | Hệ thống thật trên bản đồ | ChatGPT, Claude Code, Cursor, Letta, Mem0, Zep, Seriously… đặt lên bản đồ bài 02 | chưa |

## Nguồn khung chung

- *Memory for Autonomous LLM Agents* (arXiv [2603.07670](https://arxiv.org/abs/2603.07670)) — vòng ghi → quản lý → đọc; ba trục phạm vi
  thời gian / chất liệu / chính sách điều khiển. Khung của bài 01–02.
- *A Survey of Agent Memory in the Second Half* (arXiv [2602.06052](https://arxiv.org/abs/2602.06052)) — trí nhớ cách làm, agent tự tiến hoá. Bài 16.
- Survey tháng 12/2025 (arXiv [2512.23343](https://arxiv.org/abs/2512.23343)) — sự kiện vs sự thật; vòng đời mã hoá → củng cố → truy hồi → cập nhật. Bài 02, 15.
