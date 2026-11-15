# Bài J02 — Đo niềm tin trước khi migrate: baseline và cái bẫy "con số sai nền"

> **Bạn đã biết** (J00–J01): niềm tin dựa vào bằng chứng máy đo; vòng lặp tạo ra bằng chứng đó. Giờ: *đo cái gì* để biết hệ thống đang đáng tin hơn hay kém đi.

## 1. Câu chuyện
Một nhóm đầu tư hai tuần xây hệ thống kiểm tra tự động cho trợ lý AI. Cuối tháng sếp hỏi: "Có tốt lên không?" Không ai trả lời được — chưa từng đo trước khi xây. Tệ hơn: họ từng ghi "trợ lý vấp 171 lần/ngày", sau mới biết số đó đếm nhầm gộp nhiều nguồn; thật là ~22/ngày.

## 2. Dừng 30 giây
- Muốn biết "đáng tin hơn chưa" cần ít nhất mấy mốc số và đo vào lúc nào?
- Nghĩ 3 con số *dễ đo nhưng vô nghĩa* (ví dụ: số dòng code agent viết). Vì sao dễ bị "chơi" (tăng số mà không tốt lên)?
- Nếu một chỉ số chưa có nguồn dữ liệu, nên điền gì vào ô đó?

## 3. Cơ chế
**Baseline** = số đo *trước* khi thay đổi, trên cùng cách đo với *sau*. Không baseline thì mọi so sánh là cảm giác.

**Chọn chỉ số tốt** — ba điều kiện: (1) lấy từ nguồn đã có (log, git) không cần ai nhập tay; (2) khó "chơi" mà không tốt thật; (3) gắn với *hậu quả* chứ không với *hoạt động*. Năm chỉ số trong plan:
1. % việc "done" bị review đảo/reject.
2. % mảng agent tự khai done mà chạy lại lệnh kiểm thì **đỏ** (đo trực tiếp độ lệch lời khai ↔ thực tế).
3. Commit bị revert/sửa lại trong ≤ 48 giờ.
4. Số lần người phải can thiệp tay/tuần.
5. Số "vấp" (lỗi hay lặp) mỗi ngày.

**Luật Goodhart**: "khi một chỉ số trở thành mục tiêu, nó không còn là chỉ số tốt". Ví dụ: nếu thưởng cho "ít commit bị revert", agent (hay người) sẽ ngại commit. Cách giảm: dùng *nhiều* chỉ số kéo nhau (revert thấp nhưng số việc xong cũng phải giữ), và chỉ số lấy từ nguồn agent không ghi được.

**Trung thực về dữ liệu thiếu**: chỉ số (4) chưa có nguồn → ghi `n/a` + lý do, và **không cho quyết định nào dựa vào nó** (P5(b) bị cấm dùng chỉ số 4 tới khi có). Điền số bịa vào ô trống là cách hỏng niềm tin nhanh nhất.

**Sai nền** (con số 171 vs 22,4): trước khi tin một số, truy ngược nó tới *nguồn gốc* và kiểm bằng tay một mẫu. Quy tắc review của plan: người review chạy lại **1 chỉ số bằng tay**, phải khớp ±5 %.

## 4. Ba cách đo, so sánh
| Cách | Ưu | Nhược / điểm gãy |
|---|---|---|
| **A. Cảm giác / hỏi người dùng** | nhanh, bắt được gu | không so sánh được trước–sau; thiên kiến gần đây |
| **B. Đếm hoạt động** (số commit, số dòng) | dễ | đo *bận*, không đo *tốt*; Goodhart ăn ngay |
| **C. Đếm hậu quả từ nguồn gốc** (revert, độ lệch khai ↔ đo, can thiệp) | gắn với niềm tin thật | cần nguồn log sạch; vài chỉ số chưa có dữ liệu |

Quy luật: *đo hậu quả, không đo hoạt động; thiếu thì ghi thiếu.*

## 5. Scale
- **Dự án nhỏ:** 2–3 chỉ số, tính tay từ git log là đủ.
- **Nhiều game, nhiều phiên:** cần lệnh tính tự động theo cửa sổ (14 ngày gần nhất) và file lưu có phiên bản để so sánh.
- **Rất lớn:** mẫu nhỏ ồn → cần khoảng tin cậy (J05), và theo dõi *xu hướng* hơn giá trị tuyệt đối.

## 6. Ví dụ thật: Seriously làm thế này
P0 (đã xong, commit `071557c3d`): lệnh `kit weekly` in 5 chỉ số + `company/records/trust-baseline.json` (14 ngày gần nhất). Phát hiện sai nền: con số 171 trong backlog → đo lại ~22,4/ngày. Chỉ số (4) `n/a`. Việc nên làm: mở file baseline, tìm ô `n/a` và đọc lý do đã ghi.

## 7. Bốn nền tảng
Chỉ số lấy từ git + log nên độc lập OS. Lưu ý duy nhất: múi giờ/định dạng ngày trong log khác nhau giữa máy → chuẩn hoá về UTC trước khi tính "≤ 48 giờ".

**Giờ bạn biết thêm:** baseline, đo hậu quả vs hoạt động, Goodhart, `n/a` có lý do, sai nền.
**Bài sau:** J03 — thang cưỡng chế.
