# 07-06 — Quan hệ giữa tài liệu

> Chuỗi 07, bài 6/12. Đọc ~10 phút.
> **Bạn đã biết:** git ghi ai sửa file nào, khi nào ([07-02](07-02-ghi-ra-ngoai.md)); BM25 tìm theo chữ ([07-03](07-03-tim-lai.md));
> nhãn `supersedes` / `scope` trên tài liệu ([07-05](07-05-nhan-tren-tai-lieu.md)).

## 1. Chuyện mở đầu

Minh sắp sửa `src/payment.ts` và hỏi agent: *"trước đây những việc nào đã đổi file này, và vì sao?"*. Tìm theo chữ "payment.ts" ra 15
đoạn — phần lớn là "đã chạy test payment.ts". Câu trả lời thật nằm ở **hai bước**: file → những commit đã sửa nó → việc (ticket) mà mỗi
commit làm. Không có đoạn văn nào chứa cả ba. Thông tin có đủ trong git, nhưng nó nằm ở **quan hệ**, không nằm ở **chữ**.

## 2. Dừng 30 giây

- Muốn trả lời câu trên mà không nhờ LLM đọc gì cả — "commit nào sửa file nào" lấy ở đâu? "commit làm việc nào" lấy ở đâu?
- `README.md` bị sửa trong gần như mọi commit. Đi qua nó để tìm "thứ liên quan" có ích không?
- Cần một phần mềm cơ sở dữ liệu đồ thị riêng, hay một bảng là đủ?

## 3. Đồ thị: nút, cạnh, nhãn

**Đồ thị** là thứ bạn đã thấy: bản đồ tàu điện (ga = *nút*, đường ray nối hai ga = *cạnh*), cây gia phả (người = nút, "là con của" =
cạnh). Khi cạnh có tên loại quan hệ — "là con của", "là vợ/chồng của" — ta gọi đó là **nhãn cạnh**. Đồ thị mà nút là "thứ" (tài liệu,
file, việc, người) và cạnh có nhãn là "quan hệ giữa chúng" thì gọi là **đồ thị tri thức** (knowledge graph).

Với nhóm Quán Nhỏ:
| Nhãn cạnh | Nút → nút | Ý nghĩa |
|---|---|---|
| `touches` | commit → file | commit này sửa file này |
| `implements` | việc → commit | commit này làm việc này |
| `links` | tài liệu → tài liệu/file | tài liệu này nhắc/trỏ tới cái kia |
| `supersedes` | tài liệu → tài liệu | cái này thay cái kia (bài 07-05) |
| `scope` | tài liệu → nền tảng/dự án | đúng ở đâu (bài 07-05) |

## 4. Lưu bằng một bảng

Không cần phần mềm đặc biệt (câu hỏi 3). Một bảng năm cột là đủ:

| src | dst | type | ts | source |
|---|---|---|---|---|
| a1b2c3 | src/payment.ts | touches | 2026-06-02 | git |
| VIEC-42 | a1b2c3 | implements | 2026-06-02 | git |
| docs/thanh-toan-v2.md | docs/thanh-toan.md | supersedes | 2026-06-01 | frontmatter |

`source` ghi cạnh *đến từ đâu* — để biết sửa ở đâu khi sai, và để tắt cả một loại cạnh nếu nó gây nhiễu.

**Đi một bước:** "những commit nào sửa `payment.ts`?" = lấy mọi dòng có `dst = src/payment.ts` và `type = touches`.

**Đi nhiều bước:** "những *việc* nào đã đổi `payment.ts`?" = đi một bước ra commit, rồi từ mỗi commit đi tiếp một bước ra việc. Hoặc
chuỗi thay thế v1 ← v2 ← v3: đi lặp "ai thay cái này?" cho tới khi hết — ra bản mới nhất. Ngôn ngữ truy vấn SQL có sẵn cách viết
"lặp lại" (gọi là truy vấn đệ quy); nhớ đặt **giới hạn độ sâu** (ví dụ ≤ 5 bước) phòng khi ai đó khai nhầm "A thay B, B thay A" thành vòng.

Với vài chục nghìn cạnh, một bảng có chỉ mục trả lời trong mili-giây. Cơ sở dữ liệu đồ thị riêng chỉ đáng khi đi *nhiều* bước trên
*hàng trăm triệu* cạnh.

## 5. Cạnh có sẵn vs cạnh phải đoán (câu hỏi 1)

**Cạnh có sẵn** là quan hệ *đã được viết ra theo dạng máy đọc*, chỉ việc đọc thẳng:
- git ghi sẵn commit nào sửa file nào → `touches`;
- quy ước ghi mã việc trong lời commit (`Task: VIEC-42`) → `implements`;
- link markdown `[xem đây](docs/x.md)` → `links`;
- nhãn `supersedes` / `scope` (bài 07-05).

Đọc chúng tốn 0 đồng, **tất định** (cùng git → cùng bảng — bài 07-02), và **không bao giờ bịa cạnh**.

**Cạnh phải đoán** là quan hệ chỉ nằm trong ý văn: "lỗi A *gây ra* quyết định B". Muốn có thì phải nhờ LLM đọc văn bản rồi suy — tốn
tiền, không tất định, có thể bịa. Đồ thị kiểu này giàu nhãn hơn nhưng đắt và khó tin hơn.

**Cạnh thưa.** Cạnh có sẵn chỉ dày bằng thói quen sinh ra nó: nếu chỉ một phần nhỏ commit ghi mã việc, thì `implements` chỉ phủ phần
nhỏ đó. Cách vá ở **nguồn**: để công cụ commit tự thêm mã việc khi người/agent đang làm một việc — không phải đoán bù về sau.

## 6. Hub (câu hỏi 2)

Có những nút nối với *mọi thứ*: `README.md`, `CHANGELOG.md`, file cấu hình chung — bị sửa ở gần mọi commit. Gọi là **hub**. Đi qua hub
là đi tới bất kỳ đâu, nên "hàng xóm của hub" gần như không mang thông tin — giống chữ "là", "của" trong BM25 (bài 07-03: chữ có mặt khắp
nơi thì vô nghĩa). Cách xử lý cũng giống: khi lần theo cạnh, **hạ trọng số nút nối quá nhiều**, hoặc bỏ hẳn một danh sách hub biết trước.

## 7. Các cách, thử trên câu "việc nào đã đổi payment.ts"

| Cách | Kết quả | Ưu | Gãy khi |
|---|---|---|---|
| 1. BM25 chữ "payment.ts" | 15 đoạn nhắc tên, ít đoạn nói *vì sao* | có sẵn | câu nhiều bước |
| 2. Bảng cạnh, 2 bước: file ← commit ← việc | đúng các việc, kèm commit | tất định, mili-giây | commit không ghi mã việc (cạnh thưa) |
| 3. LLM đọc cả kho, trích đồ thị | cạnh giàu nhãn ("vì", "gây ra") | hiểu ý | tốn tiền, bịa cạnh, không tất định |
| 4. Cơ sở dữ liệu đồ thị riêng | như 2 | truy vấn nhiều bước đẹp | thêm một máy chủ cho một bảng nhỏ |

**Quy luật:** quan hệ đã được viết theo dạng máy đọc (git, link, nhãn, mã việc) thì đọc thẳng thành cạnh — rẻ, đúng, không bịa; chỉ tìm
cách đắt cho phần quan hệ **chưa ai viết ra**.

## 8. Scale

- **Nhỏ** (vài trăm cạnh): nhìn bằng mắt cũng được.
- **Vừa** (vài chục nghìn cạnh): một bảng trong cùng file chỉ mục, dựng lại vài giây. Cái vỡ trước là **hub** và **cạnh thưa**, không
  phải tốc độ.
- **Lớn** (hàng triệu cạnh, đi 3+ bước): số đường đi nổ tung; phải giới hạn bậc, dùng cách đi có trọng số thay vì đi hết (xem
  [05d](05d-knowledge-graph.md)) — lúc này mới bàn cơ sở dữ liệu đồ thị.

## 9. Bốn nền tảng

Bảng SQLite và truy vấn đệ quy chạy giống nhau trên **Windows / Mac / iOS / Android**. Trên **Windows** nhớ chuẩn hoá đường dẫn về `/`,
không thì `src\payment.ts` và `src/payment.ts` thành hai nút. Trong app điện thoại, cùng mô hình "bảng cạnh trong SQLite" hay dùng cho
quan hệ món ↔ nguyên liệu, khách ↔ đơn hàng, cây danh mục — nhỏ, nhanh, không cần thư viện đồ thị.

## 10. Tóm tắt

Đồ thị tri thức = nút + cạnh có nhãn; lưu được bằng một bảng `(src, dst, type, ts, source)`; đọc cạnh có sẵn từ git/link/nhãn thì 0
đồng và không bịa; nhớ hạ trọng số hub và vá cạnh thưa ở nguồn.

**Thuật ngữ:** graph (đồ thị) · node / edge (nút / cạnh) · edge label (nhãn cạnh) · knowledge graph · multi-hop (nhiều bước) · recursive query (truy vấn đệ quy) · hub · sparse edges (cạnh thưa).

**Giờ bạn biết thêm:** cách trả lời câu hỏi nằm ở *quan hệ* chứ không nằm ở *chữ*, mà không cần LLM.

---

> **Ví dụ thật: Seriously làm thế này**
>
> - Trong 180 ngày có **1 516 commit**. Đếm số commit sửa từng file: `docs/ai/WORKBOARD.md` (bảng ai đang làm gì) **102**,
>   `CLAUDE.md` 32, `tools/claude/recall.py` 12. WORKBOARD là hub điển hình — gần như phiên nào cũng sửa.
> - Mã việc trong commit có dạng dòng `Task: <id>` ở cuối lời commit. Chỉ **95/1 516 commit (≈ 6 %)** có dòng này → cạnh `implements`
>   rất thưa. Công cụ commit (`safe_commit.py`) đã tự thêm dòng này khi phiên đang nhận một việc; 6 % phản ánh việc phần lớn commit không
>   đi qua hộp thư việc.
> - Công cụ tìm đã đọc sẵn "commit nào sửa file nào" và các dòng `Task:` (để gắn nhãn "có thể cũ") nhưng chưa lưu thành bảng cạnh. Kế
>   hoạch: thêm bảng `edges` đúng năm cột trên vào cùng file SQLite chỉ mục; truy vấn đệ quy đã chạy thử trên 3 cạnh mẫu.

**Bài sau:** [07-07 — Kiến thức cũ](07-07-kien-thuc-cu.md).
