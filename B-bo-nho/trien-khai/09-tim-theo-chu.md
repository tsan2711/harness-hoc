# 09 — Tìm theo chữ

> Chuỗi "Triển khai trí nhớ", bài 9/21. Đọc ~9 phút.
> **Bạn đã biết** ([05](05-file-ghi-chu.md)–[08](08-do-thi-tri-thuc.md)): bốn kho — file, bảng, vector, đồ thị; vector dở với mã, số, tên riêng.

## 1. Chuyện mở đầu

Agent của nhóm code gặp lỗi `TS2345` trong `src/payment.ts`. Huy hỏi: "lỗi này mình gặp rồi phải không?". Kho vector trả về ba ghi chú về
"lỗi kiểu dữ liệu" nói chung — không cái nào đúng. Lan gõ thử `grep TS2345` trong thư mục ghi chú: ra ngay dòng "TS2345 ở payment.ts: do
truyền chuỗi thay số, sửa bằng parseInt" từ hai tháng trước.

## 2. Dừng 30 giây

- Vì sao lệnh tìm chữ cổ lỗ lại thắng ở đây?
- `grep` đọc lại mọi file mỗi lần tìm. Với 1 triệu đoạn thì sao? Có cách nào "đọc trước một lần"?
- Hỏi "thanh toán bị lỗi" — đoạn có chữ "thanh toán" 30 lần và đoạn có "TS2345" 1 lần, đoạn nào nên đứng trên?

## 3. Khái niệm

**Tìm chính xác (grep).** Quét từng file tìm chuỗi chữ. Đúng tuyệt đối với mã, tên, số (câu hỏi 1: `TS2345` là chuỗi hiếm, gần như chỉ xuất
hiện ở chỗ đúng). Chậm dần khi kho lớn (câu hỏi 2).

**Chỉ mục ngược (inverted index).** Như mục lục cuối sách: với mỗi **từ**, ghi sẵn danh sách đoạn có từ đó. Đọc toàn bộ kho **một lần** để
dựng; sau đó tìm chỉ cần tra vài danh sách — mili giây với hàng triệu đoạn.

**Chấm điểm BM25.** Khi nhiều đoạn khớp, xếp hạng bằng ba ý:
1. **Từ hiếm nặng hơn từ phổ biến** (IDF): "TS2345" nặng hơn "lỗi" rất nhiều (câu hỏi 3).
2. **Lặp lại có ích nhưng bão hoà**: xuất hiện 30 lần không hơn 3 lần là bao.
3. **Đoạn dài bị phạt nhẹ**: đoạn dài dễ chứa mọi từ một cách tình cờ.

BM25 là cách chấm điểm mặc định của hầu hết công cụ tìm chữ (Elasticsearch/OpenSearch, Lucene, SQLite FTS5, Tantivy).

**Tách từ và chuẩn hoá.** Tiếng Việt có dấu và từ ghép: "thanh toán" là một từ hai âm tiết; người gõ có thể không dấu ("thanh toan"). Công
cụ cần bỏ dấu (hoặc lưu cả hai), và chọn tách theo âm tiết hay theo từ.

## 4. Các cách

**A. grep trên file.** *Hợp khi:* vài nghìn file; agent tự gọi như một công cụ. Nhiều agent viết code làm đúng vậy — và làm tốt. *Gãy khi:* kho
lớn (chậm), câu hỏi không chứa đúng chữ.

**B. Chỉ mục ngược nhúng trong ứng dụng** (SQLite FTS5, Tantivy, Lucene). *Hợp khi:* tới vài triệu đoạn, một máy. *Gãy khi:* nhiều máy chủ cùng
ghi.

**C. Máy chủ tìm kiếm** (Elasticsearch/OpenSearch, Meilisearch, Typesense). *Hợp khi:* nhiều người dùng, nhiều máy. *Gãy khi:* thêm hệ thống
vận hành.

**D. Thêm bảng đồng nghĩa.** "giật = lag = chậm". *Hợp khi:* vài chục cặp hay gặp. *Gãy khi:* viết bảng theo đúng các câu đang trượt → điểm
đẹp trên câu đó nhưng không tổng quát (bài 19).

**E. Tìm theo trường.** Tách tiêu đề, nội dung, "thứ có tên" (đường dẫn, mã lỗi) thành các cột riêng, cho cột quan trọng trọng số cao hơn.
*Hợp khi:* có cấu trúc rõ. *Gãy khi:* trọng số chỉnh tay theo cảm tính.

## 5. Giỏi và dở

| Loại câu | Tìm theo chữ |
|---|---|
| Mã, số, tên riêng, đường dẫn | **giỏi nhất** |
| Câu dùng đúng từ trong tài liệu | giỏi |
| Diễn đạt lại ("ngứa" ↔ "nổi mẩn") | **dở** |
| Khác ngôn ngữ | dở |
| Phủ định, thời gian, nhiều bước | không biết (như vector) |

So với bài 07: hai cách **dở ở chỗ ngược nhau** — đó là lý do có bài 11.

## 6. Bảng một lần nhìn

| Cách | Quy mô | Vận hành | Gãy khi |
|---|---|---|---|
| A. grep | nhỏ | 0 | kho lớn, diễn đạt lại |
| B. Chỉ mục nhúng | vừa | thấp | nhiều máy ghi |
| C. Máy chủ tìm | lớn | cao | chi phí vận hành |
| D. + đồng nghĩa | — | thấp | viết theo đề |
| E. + trường | — | thấp | trọng số cảm tính |

**Quy luật:** tìm theo chữ rẻ, nhanh, tất định, giải thích được ("khớp vì có chữ X") và giỏi nhất với mã/tên; nó mù với diễn đạt lại.

## 7. Ba kịch bản

- **Nhóm code:** rất nhiều mã, tên file, tên hàm → tìm theo chữ thường là lớp đầu tiên nên có.
- **Cửa hàng Lá:** mã đơn, tên sản phẩm → tra bảng (bài 06) cho mã; tìm chữ cho "lần nào khách nhắc *bao bì*".
- **Mai:** chat đời thường, nhiều diễn đạt lại → tìm chữ một mình yếu; cần thêm tìm theo nghĩa.

## 8. Scale

- **Nhỏ:** A.
- **Vừa:** B — chỉ mục là **bản sao dựng lại được** từ file/bảng gốc; xoá đi dựng lại không mất gì.
- **Lớn:** C. Cái vỡ là **độ liên quan**: càng nhiều đoạn, càng nhiều đoạn "có đủ chữ nhưng sai ý"; đoạn cũ và mới cùng chủ đề có điểm gần bằng
  nhau (bài 15).

## 9. Bốn nền tảng

- **Windows / Mac:** grep (Mac có sẵn; Windows dùng `findstr` hoặc cài ripgrep), SQLite FTS5 chạy y hệt. Mac có Spotlight, Windows có Windows
  Search — tìm chữ toàn hệ thống có sẵn.
- **iOS:** SQLite FTS5 có sẵn; Core Spotlight cho app đưa nội dung vào ô tìm kiếm của máy.
- **Android:** SQLite FTS (Room hỗ trợ), AppSearch (chỉ mục tìm chữ trên máy của Google).
- Chung: chuẩn hoá Unicode tiếng Việt (cùng chữ "ế" có thể lưu hai kiểu mã) trước khi tách từ, nếu không cùng chữ mà không khớp.

## 10. Tóm tắt

Tìm theo chữ = chỉ mục ngược + BM25 (từ hiếm nặng, lặp bão hoà, đoạn dài phạt). Rẻ, nhanh, giải thích được, giỏi nhất với mã và tên riêng;
mù với diễn đạt lại — đúng chỗ vector giỏi.

**Thuật ngữ:** grep · inverted index · BM25 · IDF · tokenization (tách từ) · normalization (chuẩn hoá) · synonyms · field weighting (trọng số theo trường).

**Giờ bạn biết thêm:** cách tìm lâu đời nhất, vẫn là cách tốt nhất cho một loại câu rất phổ biến trong agent.

**Bài sau:** [10 — Tìm theo nghĩa](10-tim-theo-nghia.md).
