# Bài A02c — "Nền" 46.000 token: tờ giấy đã đầy trước khi bạn gõ

> Đọc sau A02b. Số đo từ transcript thật của tác giả; chia token ~ xấp xỉ.

## 1. Câu chuyện: phiên "xin chào" tốn 46.000 token
Phương gõ đúng một chữ "oke" vào phiên mới. Hoá đơn ghi **46.000 token đầu vào**. Phương: "Tôi mới nói một chữ mà?" Phần còn lại là "nền": mọi thứ harness nạp sẵn trước khi bạn mở miệng.

## 2. Dừng 30 giây
- Liệt kê những gì bạn nghĩ nằm trong 46k đó. Đoán thứ **lớn nhất**.
- Đoán chiều: tiếng Việt tốn token **hơn hay kém** tiếng Anh, và gấp bao nhiêu lần cho cùng một ý?
- Nền này trả tiền ở mỗi vòng (A02). Nếu cắt đi 10k token nền, phiên 100 vòng tiết kiệm bao nhiêu token đầu vào (trước cache)?

## 3. Đo thật
**Cỡ nền:** lượt đầu của các phiên Seriously: ~46k (phiên này), 53k–60k (phiên khác). Tức ~23–30% cửa sổ 200k, hoặc ~5% cửa sổ 1M.

**Thành phần nạp vào phiên này** (ký tự của từng "tệp đính kèm" lúc mở phiên, tác giả đo trong transcript):
| Phần | Ký tự | Ghi chú |
|---|---|---|
| Danh sách skill (`skill_listing`) | **19.874** | lớn nhất trong phần đo được; mỗi skill một dòng mô tả |
| Chỉ dẫn (CLAUDE.md + rules) | 12.721 | toàn cục + dự án |
| Snapshot prompt | 8.816 | |
| Output hook SessionStart | 6.703 + 1.162 | session-start.sh in WORKBOARD, trạng thái repo |
| Danh sách agent | 3.852 | |
| Bối cảnh phiên | 3.260 | |
| MEMORY.md (chỉ mục bộ nhớ) | ~4.065 | |
Tổng phần đo được ≈ 56k ký tự; phần còn lại của 46k token là **system prompt và định nghĩa công cụ** (không nằm trong các tệp đính kèm, không đo trực tiếp được ở đây).

**Token tiếng Việt:** câu trả lời tiếng Việt (trộn markdown/đường dẫn) của chính phiên này: 900 ký tự = 545 token → **~1,65–1,72 ký tự/token**. Tiếng Anh thường ~4 ký tự/token. Nghĩa là cùng một ý tiếng Việt tốn gấp **~2–2,5 lần** token so với tiếng Anh (mã nguồn và đường dẫn nằm giữa). Đáp án mục 2(b): **kém hơn** (đắt hơn).

Đáp án 2(c): cắt 10k nền × 100 vòng = **1 triệu token đầu vào** ít hơn trước cache (~100k tương đương sau cache) — đòn tiết kiệm bậc nhất vì tác động mọi vòng của mọi phiên.

## 4. Các cách giảm nền
| Cách | Ưu | Nhược / điểm gãy |
|---|---|---|
| **Rút gọn CLAUDE.md/rules** (chỉ luật mọi phiên cần) | trực tiếp, rẻ | viết ngắn khó hơn viết dài; luật cần thiết bị cắt nhầm |
| **Nạp theo đường dẫn / theo nhu cầu** (rules chỉ nạp khi chạm thư mục liên quan) | nền thay đổi theo việc | phụ thuộc cơ chế nạp; quên nạp = agent không biết luật |
| **Mục lục + đọc khi cần** (như MEMORY.md, INDEX) | nền gần cố định dù kho lớn | chất lượng phụ thuộc dòng mô tả (B01) |
| **Viết tiếng Anh cho phần nạp mọi phiên** | ~2× rẻ hơn | đọc kém tự nhiên với người; có thể tách: luật máy đọc EN, tài liệu người đọc VI |
| **Skill nạp muộn** (chỉ danh sách mô tả ngắn, nội dung nạp khi gọi) | nền rẻ dù nhiều skill | danh sách vẫn phình (19,9k ký tự ở trên!) |
| **Tắt hook in nhiều** (SessionStart in WORKBOARD cả bảng) | trực tiếp | mất thông tin đúng lúc cần |
| **Cache** | giảm hệ số ~10× | không giảm bình phương; vỡ khi nghỉ/sửa phần đầu (A02b) |

**Quy luật:** nền = thuế cố định mỗi vòng. Cắt nền hiệu quả hơn tối ưu bất cứ thứ gì khác trong phiên ngắn; và vì **sửa phần đầu làm vỡ cache**, nền nên ổn định (đừng chèn thời gian/ngẫu nhiên vào phần đầu).

## 5. Scale
| Cỡ | Nền | Hệ quả |
|---|---|---|
| Dự án nhỏ | 10–20k | không đáng lo |
| Monorepo nhiều game/bộ phận (Seriously) | 45–60k | nền chiếm 25–30% cửa sổ 200k; phiên ngắn bị nền chi phối |
| Công ty hàng chục agent | Σ nền × số phiên × số vòng | 1k token nền ≈ nhân với toàn bộ hoạt động → **quản trị nền như quản trị chi phí cố định** |

## 6. Dừng lần hai
- Trong Claude Code gõ `/context`: xem bảng phân bổ nền của bạn. Đối chiếu với bảng mục 3; cái nào bạn chưa biết là đang nạp?
- Đếm ký tự CLAUDE.md và MEMORY.md của bạn (`wc -c`); ước lượng token (÷1,7 cho tiếng Việt). Mỗi dòng bạn viết "cho chắc" tốn bao nhiêu token × số vòng mỗi ngày?
- Chọn 1 mục trong CLAUDE.md và thử đề xuất: cắt hẳn, chuyển sang rules nạp theo đường dẫn, hay đưa vào file đọc-khi-cần?

## 7. Bốn nền tảng
Token đếm giống nhau mọi nền tảng. Khác ở **ai trả**: Mac/Windows (tự bạn); iOS/Android (nếu app gọi API từ server của bạn, nền = system prompt của app: giữ ngắn vì nhân với số người dùng × số lượt). Ngôn ngữ giao diện cho người dùng cuối cũng thay đổi chi phí theo ~2× như trên.

## 8. Tóm tắt
Nền ~46–60k token là thuế mỗi vòng; lớn nhất đo được là danh sách skill và chỉ dẫn; tiếng Việt tốn ~2–2,5× tiếng Anh. Cắt nền ổn định > mọi thủ thuật khác với phiên ngắn.
