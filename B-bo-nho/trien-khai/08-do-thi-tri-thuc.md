# 08 — Đồ thị tri thức

> Chuỗi "Triển khai trí nhớ", bài 8/21. Đọc ~10 phút.
> **Bạn đã biết** ([06](06-bang-co-cau-truc.md)–[07](07-kho-vector.md)): bảng tra đúng câu biết trước dạng; vector tìm theo nghĩa nhưng
> không biết thời gian và dở với câu nhiều bước; sự kiện vs sự thật (bài 02).

## 1. Chuyện mở đầu

Mai từng kể: tháng 3 "mình chuyển sang ở Đà Nẵng", tháng 5 "công ty mình ở gần biển", tháng 9 "mình chuyển lại Hà Nội rồi". Tháng 10 Mai hỏi
"cuối tuần này gần chỗ mình có gì chơi?". Kho vector trả về câu tháng 5 (gần nghĩa nhất với "gần chỗ mình") — gợi ý đi biển Mỹ Khê. Mai đang
ở Hà Nội.

## 2. Dừng 30 giây

- Để trả lời đúng, hệ thống cần biết những *thứ* gì và những *mối liên hệ* gì giữa chúng?
- "Mai ở Đà Nẵng" — câu này đúng hay sai? (Gợi ý: hỏi thêm "khi nào?".)
- Ai sẽ biến các câu chat tự do thành các mối liên hệ đó — và việc đó tốn gì?

## 3. Khái niệm

**Đồ thị tri thức (knowledge graph)** lưu thế giới dưới dạng:
- **Nút (node)** = một *thực thể*: người, nơi, thư viện, đơn hàng. (`Mai`, `Đà Nẵng`, `Hà Nội`)
- **Cạnh (edge)** = một *quan hệ* có tên giữa hai nút: `Mai —sống_ở→ Đà Nẵng`. Bộ ba (nút, quan hệ, nút) gọi là **triple**.

Câu hỏi 1: cần nút `Mai`, các nút nơi chốn, và cạnh `sống_ở`.

**Thời gian hiệu lực.** Câu hỏi 2: "Mai sống ở Đà Nẵng" *đã từng* đúng (tháng 3–9). Đồ thị tốt gắn cho mỗi cạnh **khi nào nó đúng**:
`sống_ở Đà Nẵng [03/2026 → 09/2026]`, `sống_ở Hà Nội [09/2026 → nay]`. Có hệ còn lưu hai mốc riêng (**bitemporal**): *lúc điều đó đúng
ngoài đời* và *lúc hệ thống biết được* — để trả lời cả "hôm qua hệ thống tin gì?". Zep/Graphiti (arXiv 2501.13956) là ví dụ công khai của
đồ thị có thời gian kiểu này.

**Gộp thực thể (entity resolution).** "Đà Nẵng", "ĐN", "Da Nang", "thành phố biển" phải về cùng **một** nút; không gộp thì đồ thị gãy vụn.

**Cách lưu:** cơ sở dữ liệu đồ thị (Neo4j, Kùzu, FalkorDB…) hoặc đơn giản là **một bảng cạnh** trong cơ sở dữ liệu thường (`nguồn · quan_hệ ·
đích · từ_lúc · đến_lúc · bằng_chứng`). Với vài triệu cạnh, một bảng thường vẫn đủ.

## 4. Các cách dựng đồ thị (câu hỏi 3)

**A. Từ dữ liệu đã có cấu trúc.** Bảng đơn hàng đã có `khách → đặt → đơn → chứa → sản phẩm`; git có `commit → sửa → file`; tài liệu có link
`file A → trỏ tới → file B`. Chép ra thành cạnh bằng code. *Hợp khi:* có sẵn. Rẻ, tất định (chạy lại ra y hệt), đúng. *Gãy khi:* quan hệ
quan trọng chỉ nằm trong chữ tự do.

**B. Người khai.** Người dùng/người viết điền quan hệ ("tài liệu này *thay* tài liệu kia"). *Hợp khi:* ít quan hệ, rất quan trọng. *Gãy khi:*
không ai khai.

**C. Luật + nhận diện thực thể.** Nhận ra các "thứ có tên" trong chữ (bằng mẫu chữ, từ điển, hoặc model nhỏ — bài 12), nối hai thứ **cùng
xuất hiện** trong một đoạn. Không biết quan hệ là gì, chỉ biết "có liên quan". *Hợp khi:* cần đồ thị rẻ, nhiều. *Gãy khi:* cần biết *loại*
quan hệ (sống ở / từng sống ở / ghét).

**D. LLM trích.** Đưa từng đoạn chat cho LLM: "liệt kê thực thể, quan hệ, thời gian". Ra đồ thị giàu nhất. *Hợp khi:* chữ tự do là nguồn
chính (kịch bản Mai). *Gãy khi:* tốn tiền × mỗi đoạn × mỗi lần dựng lại; LLM bịa hoặc gán sai quan hệ, khó kiểm; tên quan hệ trôi
(`sống_ở`, `ở_tại`, `cư_trú`) nếu không có danh sách cố định.

## 5. Bảng một lần nhìn

| Cách dựng | Tiền | Đúng | Giàu quan hệ | Gãy khi |
|---|---|---|---|---|
| A. Từ dữ liệu có cấu trúc | ~0 | ✓ | chỉ cái có sẵn | quan hệ nằm trong chữ |
| B. Người khai | công người | ✓ | ít | không ai khai |
| C. Cùng xuất hiện | ~0 | vừa | ✗ (chỉ "liên quan") | cần loại quan hệ |
| D. LLM trích | cao | vừa, khó kiểm | ✓✓ | tiền, bịa, tên trôi |

**Quy luật:** đồ thị đáng giá khi câu hỏi **đi qua quan hệ** hoặc **phụ thuộc thời gian**; dựng từ cái có sẵn trước, chỉ trả tiền LLM cho
phần quan hệ thật sự nằm trong chữ tự do.

## 6. Ba kịch bản

- **Mai:** chuyện của Mai là chữ tự do và đổi theo thời gian → D + thời gian hiệu lực là điểm mạnh thật của đồ thị; hoặc đơn giản hơn: vài
  khoá hồ sơ có `cập_nhật_lúc` (bài 06) giải được `nơi_ở` mà không cần đồ thị.
- **Cửa hàng Lá:** quan hệ đã nằm trong bảng đơn hàng → A; hiếm khi cần D.
- **Nhóm code:** git + link + "tài liệu nào thay tài liệu nào" → A + B; D chỉ khi muốn quan hệ trong chữ thảo luận.

## 7. Scale

- **Nhỏ:** thường không cần đồ thị — một cột `cập_nhật_lúc` hoặc vài link là đủ.
- **Vừa:** bảng cạnh trong cơ sở dữ liệu có sẵn.
- **Lớn:** gộp thực thể thành bài toán chính; **nút trung tâm (hub)** — nút nối với rất nhiều thứ (như `Mai` trong đồ thị của Mai, hay một file
  ai cũng sửa) — làm mọi phép đi theo cạnh nổ ra quá nhiều. Với D, giá dựng lại thành rào cản.

## 8. Bốn nền tảng

- **Windows / Mac:** Neo4j chạy cả hai (cần Java); Kùzu/bảng cạnh trong SQLite nhẹ và nhúng được. LLM trích chạy trên máy được nhưng chậm.
- **iOS / Android:** cơ sở dữ liệu đồ thị chuyên dụng hiếm trên điện thoại; bảng cạnh trong SQLite là cách thực tế. Trích bằng LLM trên máy
  chậm và tốn pin → hoặc làm trên máy chủ, hoặc chỉ dùng A/B/C.

## 9. Tóm tắt

Đồ thị tri thức lưu thực thể và quan hệ, và — điểm hay bị bỏ qua — **thời gian hiệu lực** của quan hệ. Dựng từ dữ liệu có cấu trúc thì rẻ
và đúng; dựng bằng LLM thì giàu nhưng đắt và khó kiểm; gộp thực thể quyết định chất lượng.

**Thuật ngữ:** knowledge graph · node · edge · triple · temporal validity (thời gian hiệu lực) · bitemporal · entity resolution · hub · co-occurrence.

**Giờ bạn biết thêm:** kho thứ tư — lưu quan hệ và thời gian — và bốn cách dựng nó với giá rất khác nhau. Xong phần "lưu ở đâu"; phần sau là
"tìm lại thế nào".

**Bài sau:** [09 — Tìm theo chữ](09-tim-theo-chu.md).
