# Bài J05 — Eval cho skill: sửa hướng dẫn mà biết chắc nó tốt lên

> **Bạn đã biết** (J02, J04): baseline để so trước–sau; verification cho ra pass/fail từ máy. Giờ áp vào *chính tài liệu hướng dẫn* của agent.

## 1. Câu chuyện
Nhóm có file hướng dẫn "cách sinh icon". Một người sửa thêm 3 đoạn cho "rõ hơn". Tuần sau icon lỗi nhiều hơn, nhưng không ai biết do sửa hay do ngẫu nhiên — mỗi lần chạy agent cho kết quả hơi khác.

## 2. Dừng 30 giây
- Mã nguồn có unit test. Hướng dẫn cho agent (prompt/skill) có gì tương đương?
- Agent chạy cùng việc 10 lần cho kết quả khác nhau. Tăng từ 6/10 lên 7/10 có đáng tin không?
- Nếu agent *biết* nó đang bị chấm, nó cư xử thế nào?

## 3. Cơ chế
**Skill** = file hướng dẫn quy trình nạp vào agent khi gặp loại việc. **Eval** = bộ bài thử + cách chấm tự động.

Khuôn hill-climb cho skill:
1. **Coordinator** viết *rubric* (tiêu chí chấm) và bộ ca thử.
2. **Sub-agent** chạy từng ca trong thư mục có **tên trung tính** — không có chữ "eval"/rubric trong thư mục làm việc hay biến môi trường (nếu có, agent biết mình bị chấm và làm khác → số đo sai; gọi là *rò rỉ đánh giá*).
3. Chạy **nhiều model** → ma trận *skill × model* (skill chỉ tốt trên một model thì mỏng manh).
4. Sửa skill → chạy lại → so với baseline; lặp tới đạt ngưỡng (đây là J01 hill-climb áp vào văn bản).

### So sánh có ý nghĩa thống kê
Số ca ít thì tỉ lệ đạt dao động mạnh. Dùng **khoảng tin cậy Wilson** cho một tỉ lệ (6/10 → khoảng ~[31%, 83%], rộng!) và **Newcombe** cho *hiệu hai tỉ lệ* trước–sau: chỉ kết luận "tốt lên" khi khoảng của hiệu nằm hẳn bên dương. (Plan v1 ghi McNemar — sai vì McNemar dành cho cặp ghép đôi cùng ca; review sửa lại.)
Công thức Wilson cho tỉ lệ p̂ trên n ca: `(p̂ + z²/2n ± z·√(p̂(1−p̂)/n + z²/4n²)) / (1 + z²/n)`, z=1,96 cho 95 %.

```python
from math import sqrt
def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d
    h = z*sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return round(c-h, 2), round(c+h, 2)
print(wilson(6, 10), wilson(60, 100))   # cùng 60% — n khác, độ tin khác
```

### Ngân sách
Eval tốn token. Đặt **trần** (ví dụ 2M token cho đợt đầu, trong trần tuần 5M) và **bắt đầu với 2 skill**, không phủ rộng. Skill cần GPU/tiền ngoài (sinh ảnh) → duyệt riêng.

## 4. Ba cách cập nhật một skill
| Cách | Ưu | Nhược / điểm gãy |
|---|---|---|
| **A. Sửa theo cảm giác** | nhanh | không biết tốt hay tệ; hồi quy âm thầm |
| **B. Chạy thử vài lần bằng mắt** | thấy ca cụ thể | n nhỏ, ồn; người thiên vị bản mình sửa |
| **C. Suite eval + baseline + khoảng tin cậy + cô lập** | quyết định có số; chặn hồi quy | tốn token; phải bảo trì ca thử; rubric sai thì cả bảng sai |

Quy luật: *skill nào được dùng nhiều và hay sai thì xứng đáng có eval; phần còn lại, để A.*

## 5. Scale
- **1–2 skill:** vài chục ca, đủ xem xu hướng.
- **Chục skill, nhiều model:** ma trận lớn → chạy theo tuần, theo ngân sách, chỉ chạy lại skill vừa sửa.
- **Rủi ro lớn nhất:** *rubric là thứ không được kiểm.* Mỗi vài tháng lấy vài ca, chấm tay đối chiếu rubric.

## 6. Ví dụ thật: Seriously làm thế này
P4: dùng sẵn `tools/eval` + `company/evals` + `ab.py` (không xây runner mới); `kit eval run <skill-suite>` ra ma trận; `eval_week_budget = 5M`, đợt đầu ≤ 2M (chủ dự án chốt). Cô lập **chưa đạt**: thư mục tạm + biến môi trường vẫn chứa chữ "eval" → mảng đầu tiên của P4 là sửa chỗ này; cổng review: grep không thấy "eval"/rubric trong cwd + env của sub-agent. Hãy tự chạy `env | grep -i eval` trong một phiên sub-agent để thấy vấn đề.

## 7. Bốn nền tảng
Eval thuần văn bản/script nên giống nhau. Khác biệt chỉ khi ca thử cần chạy sản phẩm (Android/iOS cần thiết bị → chọn ca chạy được trên desktop trước).

**Giờ bạn biết thêm:** skill, eval, rò rỉ đánh giá, ma trận skill×model, Wilson/Newcombe, trần ngân sách.
**Bài sau:** J06 — quyền kiếm được.
