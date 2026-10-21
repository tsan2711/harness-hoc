# 07-05 — Nhãn trên tài liệu

> Chuỗi 07, bài 5/12. Đọc ~9 phút.
> **Bạn đã biết:** kiến thức ở file trong git, chỉ mục là cache ([07-02](07-02-ghi-ra-ngoai.md)); BM25 xếp đoạn theo chữ khớp
> ([07-03](07-03-tim-lai.md)); hệ thống đẩy vài đoạn đầu lên ngữ cảnh ([07-04](07-04-ai-bam-nut-tim.md)).

## 1. Chuyện mở đầu

Tháng 3, Lan viết `docs/thanh-toan.md`: "khách trả tiền khi nhận món". Tháng 6, quán đổi: chỉ nhận trả trước qua ví. Minh viết
`docs/thanh-toan-v2.md`. File cũ vẫn nằm đó, không ai sửa — nó **không hề biết mình đã cũ**.

Agent được hỏi "luồng thanh toán hiện tại?". File cũ dài hơn, nhắc chữ "thanh toán" nhiều hơn → BM25 cho nó lên đầu. Hệ thống đẩy
nó lên bàn. Agent viết code cho luồng đã bỏ.

Máy không thể biết "cũ" bằng cách đọc chữ. Ai đó phải **nói** cho nó, theo cách máy đọc được chắc chắn.

## 2. Dừng 30 giây

- Khi có bản mới, nên ghi "tôi đã bị thay" vào **file cũ**, hay "tôi thay file kia" vào **file mới**? Cái nào ít bị quên hơn?
- Bỏ trống một ô trong phiếu khảo sát, và đánh dấu "không" vào ô đó — có giống nhau không?
- Quán có luật "app Android: nút đặt món màu cam" và "app iOS: nút đặt món màu xanh". Cái nào thay cái nào?

## 3. Khái niệm

**Metadata — dữ liệu *về* dữ liệu.** Hộp thuốc có thuốc (nội dung) và chữ in trên vỏ: hạn dùng, liều, nhà sản xuất (metadata). Thùng
đồ khi chuyển nhà có đồ bên trong và nhãn "bếp — dễ vỡ" bên ngoài. Nhãn giúp người khác quyết định mà không phải mở thùng.

**Frontmatter** là cách gắn nhãn cho file văn bản: một khối ở đầu file, giữa hai dòng `---`, mỗi dòng `tên: giá trị`. Người đọc lướt
qua; máy đọc chắc chắn, không phải đoán.

**Schema** là bản hợp đồng cho nhãn: có những trường nào, mỗi trường nhận giá trị gì. Không có schema thì người viết `cu`, người viết
`old`, người viết `đã bỏ` — máy không gom được.

Bốn trường đủ cho trí nhớ của agent:
```yaml
---
status: active                    # active | superseded | wrong
supersedes: [docs/thanh-toan.md]  # tôi thay file nào; hoặc: none
scope: [android, ios]             # đúng ở đâu; hoặc [all]
keywords: [thanh toán, ví, trả trước]
---
```

| Trường | Trả lời câu | Vì sao cần |
|---|---|---|
| `status` | còn dùng không? | `wrong` khác `superseded`: ghi *sai* thì bỏ hẳn; bị *thay* thì vẫn là lịch sử đúng tại thời điểm đó |
| `supersedes` | tôi thay cái nào? | xem §4 |
| `scope` | đúng ở đâu? | câu hỏi 3: luật Android và luật iOS **cùng đúng**, không cái nào thay cái nào — chỉ khác phạm vi |
| `keywords` | tôi *về* chủ đề gì? | đoạn *về* chủ đề nên thắng đoạn chỉ *nhắc qua* chủ đề; chỉ mục cho từ khoá khai báo trọng số cao hơn chữ thường |

## 4. Ghi ở đâu — và để máy suy ngược

Ba chỗ có thể ghi "v2 thay v1":

**(a) Trên file cũ:** `superseded_by: thanh-toan-v2.md`. Người viết v2 phải nhớ tới v1, mở nó ra sửa. Có khi v1 thuộc người khác,
không tiện sửa. Hai file phải cùng đúng → dễ lệch.

**(b) Trên file mới:** `supersedes: [thanh-toan.md]`. Người viết v2 đang nghĩ đúng về chủ đề đó, đang ở trong file đó. **Một chỗ ghi.**

**(c) Một sổ riêng** liệt kê mọi cặp thay thế. Tách khỏi tài liệu → ai cũng quên cập nhật.

Chọn (b) (câu hỏi 1). Phần còn lại để **chỉ mục suy ngược**: đọc "v2 thay v1" → ghi nhớ trong chỉ mục "v1 bị v2 thay" → khi v1 lên kết
quả tìm, gắn nhãn *ĐÃ THAY BỞI v2*. File cũ không cần sửa chữ nào. Đúng tinh thần bài 07-02: nguồn ghi một lần, cache tính phần còn lại.

**Quy luật:** cái máy *không* suy ra được (ý định, phạm vi) thì người viết khai **một lần, ở chỗ đang viết**; cái suy ra được (chiều
ngược, ngày sửa, ai sửa) thì để máy tính.

## 5. "Chưa trả lời" ≠ "trả lời là không" (câu hỏi 2)

- **Không có dòng `supersedes`:** chưa ai xét. Có thể có bản cũ, có thể không.
- **`supersedes: none`:** người viết *đã xét* và khẳng định không thay gì.

Phân biệt này rẻ mà rất có lợi: hệ thống biết nên *nhắc* ai (file chưa có dòng) và nên *im* với ai (đã ghi `none`). Không có giá trị
`none` thì hoặc nhắc mãi (ồn — bài 07-04), hoặc người viết phải bịa một giá trị cho xong. Trong lập trình, đây là chuyện `null` (chưa có)
khác `[]` (có, và rỗng).

## 6. Các cách, thử trên ca "thanh toán v1/v2"

| Cách | Kết quả | Ưu | Gãy khi |
|---|---|---|---|
| 1. Không gì cả | v1 lên đầu, không nhãn | 0 công | luôn |
| 2. Sửa tiêu đề v1 thành "(cũ)", máy bắt chữ "(cũ)" | có nhãn *nếu* ai nhớ sửa | không cần schema | phải sửa file cũ; viết "(old)" là trượt |
| 3. Frontmatter `supersedes` trên v2 + suy ngược | v1 mang nhãn, v2 được biết tới | một chỗ ghi, máy đọc chắc | quyết định mới không có file riêng (chỉ có trong một lần commit) |
| 4. Hỏi LLM "file nào mới hơn" lúc đọc | thường đúng | không ai phải khai | phán sai khá thường (bài 07-07); tốn tiền mỗi câu |

Điểm gãy của cách 3 đáng nhớ: nếu quyết định mới chỉ nằm trong lời ghi của một commit ("đổi sang trả trước"), không có file mới nào
để gắn nhãn. Cách vá rẻ nhất là một luật viết: **mỗi chủ đề một file sống, đổi quyết định thì sửa file đó** (git giữ bản cũ hộ bạn).

## 7. Scale

- **Nhỏ** (vài chục tài liệu): nhìn là biết cũ/mới; nhãn là thừa.
- **Vừa** (vài trăm tới vài nghìn): lợi ích đến từ việc *áp dần* — mỗi tài liệu mới có khối nhãn sẵn trong mẫu. Không cần điền ngược cho
  tài liệu cũ: suy ngược lo phần đó.
- **Lớn** (nhiều người viết): schema **trôi** — người viết `superseeds`, người viết `scope: [Android]` chữ hoa. Cần một bước kiểm định
  kỳ: tên trường đúng, giá trị hợp lệ, đường dẫn trong `supersedes` còn tồn tại (bài 07-08). Cái vỡ là **tính nhất quán của nhãn**.

## 8. Bốn nền tảng

Frontmatter là text thuần, giống hệt trên **Windows / Mac**; bẫy duy nhất là xuống dòng `\r\n` của Windows — giá trị đọc ra có thể dính
`\r` nếu không cắt khoảng trắng. Trên **iOS / Android**, cùng ý tưởng có ở gói tài nguyên tải thêm của app: bản cập nhật mới mang
**manifest** nói "tôi thay gói nào", chứ không ai sửa gói cũ đã phát hành — đúng mô hình (b): khai ở cái mới, suy ngược cái cũ.

## 9. Tóm tắt

Máy không đọc ra được "cũ"; người viết khai một lần trên file mới (`status / supersedes / scope / keywords`, `none` = đã xét), chỉ
mục suy ngược để file cũ tự mang nhãn.

**Thuật ngữ:** metadata · frontmatter · schema · supersede (thay thế) · scope (phạm vi) · reverse edge (suy ngược) · null vs empty.

**Giờ bạn biết thêm:** cách để người viết *nói* cho máy biết tài liệu nào thay tài liệu nào, đúng ở đâu, nói về gì.

---

> **Ví dụ thật: Seriously làm thế này**
>
> - Hiện chỉ **1** file trong Seriously có `keywords:` và **2** file có `status/scope` — schema mới đề xuất ngày 2026-10-20, chưa áp rộng.
> - `keywords:` đã chạy: từ khoá khai báo được đưa vào cột "thực thể" của chỉ mục với trọng số ×3.
> - Cách 2 đang chạy: `recall.py` bắt các chữ "(cũ)", "đã thay bởi", "superseded" trong tiêu đề để gắn nhãn.
> - Ca bẫy có thật trong bộ câu kiểm tra: tài liệu "chọn hướng art" cho game Thousandfold (2026-10-11) đã bị thay bởi hướng "Sky" vài
>   ngày sau — nhưng quyết định mới chỉ nằm trong **một commit** (`d9e331fe`), không có file mới. Hỏi "hướng art hiện tại" thì file cũ
>   lên đầu. Đúng điểm gãy của cách 3, và là lý do Seriously đặt luật "một chủ đề một file sống".

**Bài sau:** [07-06 — Quan hệ giữa tài liệu](07-06-quan-he-giua-tai-lieu.md).
