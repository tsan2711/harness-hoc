# 07-07 — Kiến thức cũ

> Chuỗi 07, bài 7/12. Đọc ~10 phút.
> **Bạn đã biết:** BM25 cho điểm theo chữ ([07-03](07-03-tim-lai.md)); hệ thống chỉ đẩy ~3 đoạn đầu ([07-04](07-04-ai-bam-nut-tim.md));
> nhãn `status / supersedes / scope` ([07-05](07-05-nhan-tren-tai-lieu.md)); bảng cạnh tra được "ai thay cái này" ([07-06](07-06-quan-he-giua-tai-lieu.md)).

## 1. Chuyện mở đầu

Agent hỏi "luồng thanh toán hiện tại?". Công cụ tìm trả ba đoạn đầu:

| # | Đoạn | Điểm BM25 | Loại |
|---|---|---|---|
| 1 | `docs/thanh-toan.md` (tháng 3) — "khách trả khi nhận món" | 14,2 | tài liệu chính thức |
| 2 | chat tháng 6: "Lan bảo chuyển hết sang trả trước…" | 13,9 | câu nói trong phiên |
| 3 | `docs/thanh-toan-v2.md` (tháng 6) — "chỉ nhận trả trước qua ví" | 11,0 | tài liệu chính thức |

*(số minh hoạ)* Bản đúng **có** trong top 3, nhưng đứng cuối; bản cũ đứng đầu, mang vẻ "tài liệu chính thức", không có gì báo nó hết
hạn. Agent đọc dòng 1 và tin. **Tìm thấy chưa đủ — thứ tự và nhãn quyết định agent tin cái gì.**

## 2. Dừng 30 giây

- Sao không đơn giản "cái mới nhất lên đầu"?
- Nhãn "ĐÃ THAY BỞI …" đặt ở **đầu** dòng hay **cuối** dòng — khác gì với một người (hay một model) đọc lướt?
- Có vài luật xếp hạng, luật nào cũng "đúng". Thứ tự áp chúng có quan trọng không?

## 3. Ba kiểu "cũ" khác nhau

| Kiểu | Ví dụ | Nên làm gì với bản cũ |
|---|---|---|
| **Thay thế** | thanh toán v2 thay v1 | giữ, gắn nhãn "đã thay bởi v2" — vì có khi câu hỏi chính là "trước đây làm sao" |
| **Sửa sai** | ghi chú "API trả về mili-giây" — thật ra là giây | bỏ hẳn khỏi kết quả; nó chưa từng đúng |
| **Cùng tồn tại** | "Android: nút cam" và "iOS: nút xanh" | không cái nào cũ; chọn theo phạm vi người hỏi |

Một hệ thống chỉ biết "cũ / mới" sẽ xử sai ít nhất hai trong ba kiểu.

## 4. Vì sao "mới nhất thắng" sai (câu hỏi 1)

- **Câu gốc thường giải thích đầy đủ nhất.** Ghi chú viết lúc quyết định có cả "vì sao"; những lần nhắc về sau ngắn và thiếu ngữ cảnh.
  Đẩy bản mới lên trên chỉ vì nó mới thường làm *mất* câu trả lời tốt.
- **Cùng tồn tại bị đè.** Luật iOS viết hôm qua sẽ "thắng" luật Android viết tháng trước, dù câu hỏi là về Android.
- **Mới ≠ đúng.** Bản mới có thể là một câu hỏi, một ý thử, hay một lần sửa sai *bị sai*.

Ngày tháng là đoán; **khai báo** (`supersedes`, `scope`, `status`) mang *ý định* của người viết. Ngày chỉ nên là thứ phân xử cuối cùng
khi mọi thứ khác bằng nhau (gọi là *tie-break*).

## 5. Xếp hạng = tìm + luật

Tách làm hai câu hỏi:
- BM25 trả lời "đoạn nào **nói về** câu hỏi?"
- Một chuỗi **luật** trả lời "trong số đó, đoạn nào **nên tin**?"

**Xô điểm.** BM25 hiếm khi cho hai đoạn điểm bằng nhau tuyệt đối, nên luật phụ sẽ không bao giờ có tác dụng nếu xếp thẳng theo điểm.
Mẹo: gom các đoạn chênh nhau rất ít (ví dụ < 0,5 điểm) vào cùng một "xô" coi như ngang nhau, rồi áp luật trong xô. Nhờ vậy luật chỉ đổi
thứ tự những đoạn *gần bằng nhau*, không bao giờ đẩy một đoạn khớp yếu lên trên một đoạn khớp mạnh.

**Chuỗi luật đề xuất**, luật trên thắng luật dưới:
| # | Luật | Làm gì |
|---|---|---|
| 1 | Khớp phạm vi | đoạn cùng phạm vi với người hỏi được ưu tiên (nhẹ) |
| 2 | `status: wrong` | loại khỏi kết quả |
| 3 | Bị thay thế | gắn nhãn **ĐÃ THAY BỞI <bản mới>**, và kéo bản mới vào top nếu chưa có (tra bằng bảng cạnh, bài 07-06) |
| 4 | Tài liệu chính thức > câu nói trong phiên | trong cùng xô |
| 5 | Ngày | chỉ là tie-break cuối |

Áp vào chuyện mở đầu: dòng 1 mang nhãn "ĐÃ THAY BỞI docs/thanh-toan-v2.md", v2 đứng ngay cạnh. Agent thấy cả hai và thấy quan hệ.

**Thứ tự có quan trọng** (câu hỏi 3). Đảo luật 1 và 3: câu hỏi về Android gặp nhãn "ĐÃ THAY BỞI" một tài liệu iOS — đúng về quan hệ
nhưng sai phạm vi, agent bỏ luật Android còn hiệu lực. Lọc *phạm vi* phải chạy trước luật *thời gian*.

## 6. Nhãn đặt đầu dòng (câu hỏi 2)

```
2026-03-02  ĐÃ THAY BỞI docs/thanh-toan-v2.md · docs/thanh-toan.md
    …khách trả tiền khi nhận món…
```
- Người và model đều đọc lướt phần đầu; nhãn ở cuối thường bị đọc *sau* khi đã tin nội dung.
- Kết quả đẩy có ngân sách ký tự (bài 07-04) và thường bị cắt từ cuối — nhãn cuối dòng có thể bị cắt mất.
- Nhãn đứng trước nội dung **định khung** cách đọc: "đây là lịch sử".

## 7. Còn cách "để LLM tự phán lúc đọc"?

Đưa hai đoạn cho model, hỏi "cái nào còn đúng?". Nghe hợp lý, nhưng một nghiên cứu năm 2026 về kiến thức cũ ngầm (STALE, xem
[05f](05f-ky-uc-cu-va-thay-the.md)) đo được: phán lúc đọc chỉ đúng khoảng **55 %** — gần tung đồng xu — vì đoạn cũ thường không có dấu
hiệu gì là cũ. Thêm nữa là tốn tiền mỗi câu và không tất định. Lý do này là vì sao phán quyết "cũ/mới" nên làm **lúc ghi** (người viết
biết rõ nhất), còn lúc đọc chỉ *hiển thị* nhãn — bài sau.

## 8. Bảng một lần nhìn — trên ca thanh toán

| Cách | Agent tin | Gãy khi |
|---|---|---|
| A. BM25 thuần | bản cũ | luôn, với ca thay thế |
| B. Mới nhất lên đầu | bản mới (ca này) | câu diễn đạt lại, cùng tồn tại, bản mới sai |
| C. Xô + tài liệu > chat, chưa có nhãn khai báo | bản cũ | khi không ai sửa tiêu đề bản cũ |
| D. Chuỗi luật 1–5 | thấy cả hai, bản cũ mang nhãn đầu dòng | không ai khai `supersedes` (→ bài 07-08) |
| E. LLM xếp lại / phán | thường đúng | ~55 % ở ca cũ ngầm; tốn tiền mỗi câu |

**Quy luật:** thứ tự kết quả phải dựa vào thứ được **khai** (phạm vi, thay thế, sửa sai), không dựa vào thứ được **đoán** (ngày, giọng
văn); lọc phạm vi trước, nhãn đặt đầu.

## 9. Scale

- **Nhỏ:** BM25 thuần ổn — ít bản trùng chủ đề.
- **Vừa:** nhiều phiên nói về cùng chuyện → chuỗi luật thành cần thiết.
- **Lớn:** 3 dòng không đủ chứa "bản cũ + bản mới + hàng xóm" → gộp thành một dòng ("X — ĐÃ THAY BỞI Y"); và khi thêm cách tìm khác
  (vector), điểm đổi thang nên phải chỉnh lại cỡ xô.

## 10. Bốn nền tảng

Toán xếp hạng không khác gì trên **Windows / Mac / iOS / Android**. Một bẫy: sắp chuỗi tiếng Việt theo bảng chữ cái phụ thuộc cài đặt
ngôn ngữ của máy — đừng dùng chữ làm khoá sắp, dùng số và đúng/sai. Trong app, cùng bài học ở **danh sách thông báo**: lọc theo phạm vi
(cửa hàng người dùng đang chọn) trước, ưu tiên thứ được đánh dấu quan trọng sau, ngày chỉ là tie-break.

## 11. Tóm tắt

Có ba kiểu cũ (thay thế, sửa sai, cùng tồn tại); "mới nhất thắng" sai cả ba; sau khi tìm, một chuỗi luật có thứ tự dựa trên nhãn khai
báo quyết định agent tin gì, và nhãn đặt ở đầu dòng.

**Thuật ngữ:** supersede / correct / coexist (thay / sửa sai / cùng tồn tại) · rerank (xếp lại) · bucket (xô điểm) · rule cascade (chuỗi luật) · tie-break · framing (định khung).

**Giờ bạn biết thêm:** cách biến "tìm thấy" thành "tin đúng cái".

---

> **Ví dụ thật: Seriously làm thế này**
>
> - Công cụ tìm của Seriously đã có xô điểm (0,5) và luật "tài liệu chính thức trước câu nói trong phiên" trong cùng xô.
> - Đã có nhãn yếu **"có thể cũ"**: một đoạn chat nhắc tới một file mà file đó bị sửa *sau* ngày của đoạn chat. Nhãn này chỉ hạ hạng
>   trong cùng xô — vì khi thử hạ hạng mạnh theo tuổi, bộ câu kiểm tra **mất 3 câu diễn đạt lại** (đúng lý do "câu gốc đầy đủ nhất" ở §4).
> - Kết quả đẩy có ngân sách **1 800 ký tự**, cắt theo dòng từ cuối — lý do nhãn phải đứng đầu.
> - Bộ câu kiểm tra có nhóm "bẫy" (cặp cũ/mới thật); hiện trúng **4/5**. Chuỗi luật 1–5 là đề xuất, chưa vào code; luật 3 cần nhãn
>   `supersedes` (bài 07-05) và bảng cạnh (bài 07-06) có trước.

**Bài sau:** [07-08 — Lúc ghi](07-08-luc-ghi.md).
