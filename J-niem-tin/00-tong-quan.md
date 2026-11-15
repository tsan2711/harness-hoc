# Bài J00 — Vì sao "review chặt hơn" không đủ: bốn mắt xích của niềm tin vào agent

> **Bạn đã biết** (A01–A04): agent là vòng lặp *model → công cụ → kết quả → model*; hook là mã tự chạy ở một điểm của vòng; vòng ngoài có thể tự chạy mà không cần người ngồi cạnh.
> Chuỗi J này là *hệ quả*: khi agent chạy nhiều giờ, nhiều phiên, **dựa vào đâu để tin kết quả?**

## 1. Câu chuyện (≤ 5 dòng)
Minh giao trợ lý AI việc "sửa màn hướng dẫn". Trợ lý báo: "Xong, đã test." Minh mở game: nút bấm không phản ứng. Lần sau Minh review kỹ hơn, đọc từng dòng diff. Tuần sau trợ lý làm 10 việc cùng lúc; Minh review không kịp. Hai lựa chọn: tin mù, hoặc thành nút cổ chai của chính hệ thống mình dựng.

## 2. Dừng 30 giây
- Con người review được tối đa bao nhiêu thay đổi/ngày? Nếu agent làm gấp 10 lần thì review tăng 10 lần được không?
- "Agent nói đã test" khác "máy đã test" ở chỗ nào — ai là người *khai*, ai là người *đo*?
- Nghĩ một luật bạn đã dặn agent bằng lời ("nhớ chạy test trước khi commit") mà nó vẫn quên. Lần quên thứ ba, bạn làm gì?

## 3. Một mạch nhân quả, bốn bước
```
agent tự khai "xong"  ──(không tin được)──►  ① máy tự chạy sản phẩm thật để kiểm
luật dặn bằng lời bị quên ──(lặp lại)────►  ② đẩy luật lên thành cổng cứng (máy chặn)
skill/hướng dẫn viết cho agent ─(sửa mà không biết tốt lên hay tệ đi)─► ③ eval cho skill
agent làm tốt, nhưng quyền vẫn cố định ──►  ④ quyền nới/siết theo số đo
```
Giải thuật ngữ:
- **Verification (kiểm chứng)**: agent tự khởi chạy phần mềm thật, bấm thử, chụp ảnh/đo số — thay vì chỉ đọc code rồi tuyên bố đúng. Giống tester chạy app, không phải reviewer đọc code.
- **Cổng cứng (hard gate)**: đoạn mã *từ chối* hành động (commit, ghi file) khi vi phạm. Khác *nhắc* (soft) là lời khuyên. Giống `-Werror` của compiler so với warning.
- **Skill**: file hướng dẫn quy trình mà agent nạp khi gặp loại việc đó. **Eval** = bộ bài thử có chấm điểm tự động để biết skill sửa xong có tốt lên không (như unit test cho prompt).
- **Autonomy (mức tự chủ)**: agent được làm gì không cần hỏi. L1 hỏi mọi thứ → L3 tự làm cả việc dài.

Điểm mấu chốt: niềm tin **không** đến từ việc người đọc kỹ hơn. Nó đến từ chỗ *bằng chứng do máy tạo ra, lặp lại được*. Người chỉ còn xử lý cái máy không đo được (gu, tiền, xoá dữ liệu).

## 4. Ba cách tạo niềm tin, so trên cùng một dữ kiện ("agent báo xong 10 việc")
| Cách | Ưu | Nhược / điểm gãy |
|---|---|---|
| **A. Người review từng việc** | bắt được lỗi tinh tế, gu | tuyến tính theo số việc; mệt → duyệt qua loa (rubber stamping) |
| **B. Agent khác review agent làm** | scale được, rẻ hơn người | cùng "thiên kiến" model; reviewer đọc lời tự khai chứ không chạy sản phẩm |
| **C. Máy kiểm bằng lệnh (exit 0/≠0), người chỉ duyệt phần máy không đo được** | scale phẳng; lặp lại được | chỉ kiểm được cái *viết được thành lệnh*; kiểm sai thứ vẫn xanh |

Quy luật: *càng nhiều việc, càng phải chuyển từ A → B → C; nhưng C chỉ đáng tin khi chính lệnh kiểm đã được kiểm (J03, J05).*

## 5. Scale
- **Một người + một agent, việc nhỏ:** A là đủ, đừng xây gì.
- **Nhiều phiên song song, chạy đêm:** A sụp trước; B gãy vì reviewer vẫn tin lời khai; cần C.
- **Nhiều đội/nhiều game:** vấn đề đổi chất — không còn là "việc này đúng chưa" mà "**bao nhiêu quyền** cho agent này, dựa vào lịch sử nào" (J06).

## 6. Bản đồ chuỗi J
| Bài | Câu hỏi |
|---|---|
| J01 | Vì sao **vòng lặp** là xương sống — và vòng nào mới là vòng đúng |
| J02 | Đo **trước** khi sửa: nếu không có baseline, migrate tốt hay tệ không ai biết |
| J03 | Thang cưỡng chế: luật từ lời nhắc → cổng cứng, không chặn nhầm |
| J04 | Verification: agent tự chạy sản phẩm; đúng ≠ đẹp |
| J05 | Eval cho skill: hill-climb tới ngưỡng |
| J06 | Quyền kiếm được + phạm vi ghi + ranh giới cô lập thật |

## 7. Ví dụ thật: Seriously làm thế này
Plan `tools/harness/wip/trust-migration-plan.md` (2026-11-14) gồm P0–P6, đúng bốn mắt xích trên cộng một pha đo (P0) và một pha dọn vòng lặp (P3/P6). Nguồn cảm hứng là hai video của một kỹ sư (bản tóm tắt AI, không kiểm được từng con số) — nên plan **không** copy mục tiêu "1000 PR/tháng". Dừng lại mở file, đếm: pha nào là *đo*, pha nào là *cổng*, pha nào là *quyền*?

## 8. Bốn nền tảng
Không phụ thuộc OS: lệnh kiểm là exit code. Khác biệt chỉ ở *cách khởi chạy sản phẩm thật*: Windows/Mac chạy build desktop hoặc Editor batchmode; Android cần emulator/thiết bị (`adb`); iOS khó tự động nhất (simulator, ký số) — nên verification iOS thường là mảng làm sau cùng.

**Giờ bạn biết thêm:** niềm tin = bằng chứng máy tạo, lặp lại được; bốn mắt xích verification → cổng → eval → quyền.
**Bài sau:** J01 — vòng lặp.
