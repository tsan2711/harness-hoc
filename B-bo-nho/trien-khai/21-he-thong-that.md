# 21 — Hệ thống thật trên bản đồ

> Chuỗi "Triển khai trí nhớ", bài 21/21. Đọc ~10 phút.
> **Bạn đã biết** ([02](02-ban-do-lua-chon.md), [20](20-chon-kien-truc.md)): bản đồ ba trục — phạm vi thời gian, chất liệu, ai điều khiển; vòng
> ghi → quản → đọc; bảy câu hỏi chọn kiến trúc.

Bài cuối không có chuyện mở đầu. Nó đặt các hệ thống có thật lên bản đồ bài 02, để bạn thấy: mỗi hệ thống là **một tổ hợp lựa chọn** cho bài toán
của nó — không cái nào là "cách đúng".

**Lưu ý nguồn:** mô tả dưới đây lấy từ tài liệu công khai của từng bên tới cuối 2026; sản phẩm đổi nhanh — kiểm lại tài liệu gốc trước khi dựa vào.
Số đo do chính bên làm ra công bố được ghi là *tự công bố* và không dùng để so sánh.

## 1. Dừng 30 giây

- Với mỗi hệ thống dưới đây, đoán trước: nó ghi bằng ai, đọc kiểu gì, giữ ở chất liệu nào?
- Hai hệ thống phục vụ cùng một loại người dùng mà chọn khác nhau — vì sao?

## 2. Trợ lý trò chuyện

**ChatGPT (OpenAI).**
- Hai lớp: *saved memories* (sự thật ngắn) và *tham chiếu lịch sử chat*.
- Ghi: người dùng yêu cầu + model tự rút; bản mới tự cập nhật trí nhớ và cho xem nguồn.
- Đọc: sự thật được đặt vào ngữ cảnh (ghim); lịch sử được dùng khi liên quan.
- Quản: người dùng xem/xoá được; muốn xoá hẳn một điều phải xoá cả các cuộc chat là nguồn của nó (bài 15).
- Trên bản đồ: phạm vi dài · chất liệu chữ + tìm kiếm · LLM tự động + người.

**Claude (app của Anthropic).**
- Tìm trong chat cũ bằng **công cụ** (agent tự gọi — bài 14, cách C), có từ 2025; trí nhớ tóm từ chat, tách theo **project**.
- Người dùng xem và sửa được phần trí nhớ.
- Trên bản đồ: phạm vi dài, chia theo project · chữ + tìm · agent gọi + LLM tóm.

**Memory tool + context editing (Anthropic API, 2025).**
- Cho nhà phát triển: agent có công cụ thao tác một thư mục `/memories` (xem, tạo, sửa, chèn, xoá, đổi tên file); kho do nhà phát triển giữ.
- Context editing tự dọn kết quả công cụ cũ khi bàn đầy.
- Trên bản đồ: chất liệu file · agent tự quyết · đọc theo công cụ.

## 3. Agent viết code

**File hướng dẫn trong repo** — `CLAUDE.md` (Claude Code), `AGENTS.md`, rules của Cursor, `copilot-instructions.md`…
- Người viết (agent có thể đề xuất), nạp đầu phiên (ghim), lưu trong git (lịch sử, ghi cùng lúc, phạm vi = repo).
- Tìm thêm bằng agent tự grep/đọc file nhiều vòng thay vì kho vector (bài 11, cách D) — một số công cụ có thêm chỉ mục nghĩa.
- Skill / quy tắc theo đường dẫn được nạp khi cần (lộ dần — bài 14).
- Trên bản đồ: chất liệu file · người + agent · ghim + agent tự tìm.

## 4. Thư viện / dịch vụ trí nhớ

**Letta (trước là MemGPT).**
- Ba tầng: *core* (khối luôn trên bàn, agent tự sửa), *recall* (lịch sử hội thoại), *archival* (kho tìm kiếm lớn).
- Agent tự quản bằng công cụ, như hệ điều hành quản RAM/đĩa; *sleep-time agent* sửa khối trí nhớ chung lúc rảnh (bài 13, cách E).
- Trên bản đồ: chữ + vector · agent tự quyết + chạy nền.

**Mem0.**
- Sau mỗi lượt/phiên, LLM rút sự thật và chọn thêm / sửa / xoá / bỏ qua (bài 13 C, bài 15 D); kho vector, có biến thể đồ thị.
- Đọc: tìm theo câu hỏi.
- Số LoCoMo / LongMemEval cao: *tự công bố*.
- Trên bản đồ: vector (+ đồ thị) · LLM tự động.

**Zep / Graphiti.**
- Đồ thị tri thức có **thời gian hiệu lực** (bitemporal — bài 15 C), LLM trích thực thể và cạnh; tìm lai chữ + nghĩa + đồ thị.
- Số LoCoMo: *tự công bố*, có tranh cãi với số bên thứ ba đo lại.
- Trên bản đồ: đồ thị · LLM tự động · tìm lai.

**A-Mem (nghiên cứu, NeurIPS 2025).**
- Mỗi trí nhớ là một "ghi chú" kiểu Zettelkasten: mô tả, từ khoá, link tới ghi chú liên quan; ghi chú mới có thể làm **sửa** ghi chú cũ.
- Trên bản đồ: ghi chú + link · LLM tự động · tự tổ chức.

**Generative Agents (Stanford 2023, nghiên cứu).**
- Dòng sự kiện (*memory stream*), đọc theo độ mới + quan trọng + liên quan; định kỳ *reflection* rút kết luận bậc cao (bài 15).
- Trên bản đồ: sự kiện + kết luận · LLM tự động · điểm trộn ba yếu tố.

## 5. Một hệ thống nhỏ: Seriously

Seriously là repo nhiều game của một người làm game độc lập, vận hành bằng nhiều phiên agent chạy song song (người viết chuỗi này dùng nó hằng ngày —
nên nó ở đây như **một ví dụ**, không phải khuyến nghị).
- **Chất liệu: file trong git.** Mỗi đơn vị (game, bộ phận) có `CLAUDE.md` → `INDEX.md` (đang làm gì) → thư mục quy tắc → tài liệu chi tiết;
  thư mục `knowledge/` cho bài học.
- **Đọc:** ghim file hướng dẫn ngắn + mục lục; tài liệu chi tiết mở khi cần (lộ dần); hook đầu phiên đặt "việc dở dang" lên bàn (theo sự kiện);
  lệnh tìm chữ cho chuyện cũ trong lưu trữ.
- **Ghi:** agent ghi vào INDEX/knowledge khi xong việc; người duyệt các quyết định lớn; tách rõ "trạng thái công việc" (trong repo) với "sự thật về
  người dùng" (trí nhớ riêng của trợ lý).
- **Cách làm:** quy tắc → hook / kiểm tra trước commit khi lỗi lặp lại (bài 16, cách E); sổ ghi lỗi harness có giới hạn số dòng.
- **Nhiều agent:** bảng nhận việc (ai đang sửa vùng nào), commit nhỏ, kéo trước khi sửa (bài 18).
- **Quên:** chuyển việc xong sang thư mục lưu trữ; ngân sách dòng cho file ghim.
- **Không có:** kho vector, đồ thị, fine-tune — vì câu hỏi chủ yếu là tên file, mã, quyết định gần đây, và kho đủ nhỏ để agent tự tìm.
- Trên bản đồ: chất liệu file · người + agent + luật · ghim + sự kiện + agent tự tìm. **Gãy khi:** kho lớn tới mức tìm chữ hụt; câu diễn đạt lại
  nhiều; phụ thuộc agent tự giữ kỷ luật ghi.

## 6. Bảng một lần nhìn

| Hệ thống | Chất liệu chính | Ai ghi | Đọc kiểu | Hợp bài toán |
|---|---|---|---|---|
| ChatGPT | chữ + tìm | LLM + người | ghim + liên quan | trợ lý một người |
| Claude app | chữ + tìm | agent gọi + LLM tóm | công cụ | trợ lý, chia project |
| Memory tool API | file | agent | công cụ | agent tự xây |
| File hướng dẫn agent code | file trong git | người + agent | ghim + agent tìm | repo code |
| Letta | khối + vector | agent + nền | ghim + công cụ | agent dài hạn |
| Mem0 | vector (+ đồ thị) | LLM tự động | tìm | thêm trí nhớ vào app |
| Zep / Graphiti | đồ thị thời gian | LLM tự động | lai + đồ thị | sự thật đổi theo thời gian |
| A-Mem | ghi chú + link | LLM | tìm + link | nghiên cứu tự tổ chức |
| Generative Agents | dòng sự kiện | luật + LLM | điểm 3 yếu tố | mô phỏng nhân vật |
| Seriously | file trong git | người + agent + luật | ghim + sự kiện + tìm chữ | repo nhiều agent |

**Quy luật cuối:** mỗi hệ thống đúng **cho bài toán của nó**. Đặt bài toán của bạn qua bảy câu hỏi (bài 20), đo trên câu thật (bài 19), rồi chọn —
có thể là một tổ hợp chưa ai đặt tên.

## 7. Tóm tắt chuỗi

Model không nhớ (01). Trí nhớ là ba lựa chọn — giữ bao lâu, giữ bằng gì, ai điều khiển — trên một vòng ghi → quản → đọc (02). Các khối xây: bàn
làm việc, tóm tắt, file, bảng, vector, đồ thị (03–08); tìm theo chữ, nghĩa, lai, đồ thị (09–12); chính sách ghi và đọc (13–14); cập nhật và quên
(15); cách làm (16); trọng số (17); an toàn và phối hợp (18); đo (19); ghép (20). Không có kiến trúc thắng mọi nơi.

**Thuật ngữ:** saved memory · chat history reference · memory tool · context editing · instruction file · core / recall / archival · sleep-time agent · memory stream · Zettelkasten.

**Giờ bạn biết thêm:** cách đọc bất kỳ hệ thống trí nhớ nào bằng cùng một bản đồ — và tự vẽ hệ thống của riêng mình.

**Hết chuỗi.** Quay lại [mục lục](README.md).
