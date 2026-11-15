# Bài J04 — Verification: để agent tự chạy sản phẩm thật (và giới hạn: đúng ≠ đẹp)

> **Bạn đã biết** (J01, J03): DONE phải do lệnh kiểm quyết định; cổng cứng chặn vi phạm. Câu hỏi còn lại: *lệnh kiểm kiểm cái gì?* Unit test xanh chưa chắc sản phẩm chạy được.

## 1. Câu chuyện
Trợ lý sửa màn hướng dẫn, 40 unit test xanh. Người dùng mở app: nút "Tiếp" bị che bởi một lớp trong suốt, không bấm được. Không test nào bấm thử như người dùng.

## 2. Dừng 30 giây
- Unit test kiểm *hàm* đúng; thứ gì kiểm *sản phẩm* dùng được? Ai/cái gì làm việc đó trong đội bạn?
- Để một agent tự "chơi thử" app, nó cần biết gì về app mà không đọc hết code?
- Máy đo được "đúng"; còn "đẹp" thì sao?

## 3. Cơ chế
**Verification** = agent khởi chạy sản phẩm thật, thao tác như người dùng, thu bằng chứng, rồi một lệnh kết luận pass/fail. Năm động tác chuẩn:
1. **Khởi chạy** (từ trạng thái lạnh — *cold start*, không phụ thuộc phiên trước);
2. **Health check** (đã lên chưa? có exception trong log không?);
3. **Điều khiển** (bấm, kéo, gõ — qua input thật hoặc API test);
4. **Thu bằng chứng** (ảnh chụp, số đo, log) → ra `verdict.json`;
5. **Dọn** (đóng tiến trình, để lần sau lạnh lại).

### Feature Map
Bản đồ mà agent tra thay vì đoán: *để tới màn/trạng thái X thì làm các bước nào, và quan sát được gì khi tới nơi*. Giống sơ đồ ga tàu cho tester. Rủi ro: map lệch source. Giải pháp: **lệnh bảo trì đối chiếu map ↔ source** (đổi tên nút trong code mà map không đổi → lệnh đỏ). Luật kèm theo: **cấm sửa map để che lỗi của game** — map phản ánh sản phẩm, không phải thứ thương lượng.

### Giới hạn: đúng ≠ đẹp
Verification chứng minh *code đúng*, không chứng minh *trông tốt*. Đừng hứa "bỏ người khỏi vòng gu". Làm được: so với **ảnh mẫu đã duyệt** (ref) bằng số — độ lệch màu, SSIM (chỉ số tương đồng cấu trúc ảnh) — và bắt buộc đặt cạnh ref (`compare.jpg`) trước khi báo xong. Làm chưa được: tự chấm gu. Đo lường sai kiểu khác: "3 báo lỗi mơ hồ" không đo được bằng máy → để QA chấm tay, không tính vào check.

## 4. Ba cách kiểm sản phẩm
| Cách | Ưu | Nhược / điểm gãy |
|---|---|---|
| **A. Unit test** | nhanh, rẻ | không thấy lớp phủ che nút, lỗi nối dây, lỗi layout |
| **B. Agent đọc code rồi "suy luận chạy được"** | không cần dựng gì | chính là lời tự khai (J01) |
| **C. Chạy thật + Feature Map + bằng chứng** | thấy lỗi người dùng thấy; lặp lại được | chậm (khởi động engine 40s–3 phút); cần bảo trì map; chưa đo được gu |

Quy luật: *unit test cho logic, verification cho "người dùng đi được hết đường", người cho gu.*

## 5. Scale
- **Prototype:** chưa có gì để kiểm (đồ hoạ tạm) → verification sớm là lãng phí; đợi tới khi có màn thật.
- **Một game có tutorial:** bot đi từ cold start qua hết tutorial, ra verdict + ảnh.
- **Nhiều game:** mỗi game một map + một lệnh `walk`; **gom job** (mỗi lần khởi động Editor tốn phút) — sửa nhiều thứ rồi kiểm một lượt.
- **Đo hiệu năng** phải ở chế độ có cửa sổ (windowed), không phải headless, nếu không số drawcall/render sai.

## 6. Ví dụ thật: Seriously làm thế này
P2: LightRouting trước (đã có scene thật, `TutorialRealInput`, `ThemePlayShots`, `ScenarioTests`). Thousandfold **bỏ khỏi P2** vì đang GDD-first, đồ hoạ chỉ prototype — chưa có gì để kiểm. Check: `walk.py lightrouting` (tên mới, vì `kit verify` đã là cổng merge của thư viện chung) từ cold start → exit 0 + `verdict.json` + ≥ 1 ảnh; đổi tên 1 nút trong source → lệnh bảo trì đỏ. Đoạn "5 động tác" ở plan khớp phần 3 bài này.

## 7. Bốn nền tảng
- **Windows/Mac:** build chạy trực tiếp hoặc Editor; chụp màn hình dễ.
- **Android:** `adb` điều khiển + chụp; cần emulator/thiết bị.
- **iOS:** simulator/XCUITest, ràng buộc ký số và máy Mac → khó tự động nhất, làm sau cùng.

**Giờ bạn biết thêm:** cold start, 5 động tác, Feature Map + lệnh bảo trì, giới hạn "đúng ≠ đẹp", so ref bằng số.
**Bài sau:** J05 — eval cho skill.
