# 07-08 — Lúc ghi

> Chuỗi 07, bài 8/12. Đọc ~9 phút.
> **Bạn đã biết:** hook = sự kiện → chạy lệnh → in ra thì vào ngữ cảnh; ngưỡng im ([07-04](07-04-ai-bam-nut-tim.md)); nhãn `supersedes`,
> `none` = đã xét ([07-05](07-05-nhan-tren-tai-lieu.md)); cạnh `links` ([07-06](07-06-quan-he-giua-tai-lieu.md)); luật xếp chỉ chạy được
> nếu có người khai ([07-07](07-07-kien-thuc-cu.md)).

## 1. Chuyện mở đầu

Huy viết `docs/giao-dien-moi.md`: "từ nay nút đặt món màu cam, bo góc lớn". Trong kho đã có `docs/giao-dien.md` nói "nút xanh, góc
vuông", và **ba tài liệu khác trỏ tới nó**: checklist kiểm thử giao diện, mẫu câu lệnh sinh ảnh minh hoạ, mẫu email giới thiệu app.
Huy viết xong, lưu, đi tiếp. Không ai khai `supersedes`. Tuần sau người kiểm thử vẫn chấm theo checklist cũ, ảnh minh hoạ vẫn ra nút
xanh — ba tài liệu kia đang **dựa trên cái đã bỏ** mà không ai biết.

## 2. Dừng 30 giây

- Lúc nào người (hay agent) biết rõ nhất tài liệu mới thay tài liệu nào: lúc viết, lúc lưu vào git, hay tuần sau khi có người hỏi?
- Nếu hệ thống **chặn** không cho lưu file tới khi điền `supersedes`, hai tuần sau người viết sẽ làm gì?
- Khi tài liệu mới thay tài liệu cũ, ngoài tài liệu cũ ra, ai cần được báo?

## 3. Hỏi lúc ngữ cảnh đầy nhất (câu hỏi 1)

Lúc viết là lúc người viết vừa đọc chủ đề, đang nghĩ về nó. Một tuần sau, chính họ cũng phải đọc lại mới nhớ. Vậy việc khai báo nên
được **nhắc ngay lúc ghi**.

Công cụ agent có sự kiện "agent vừa dùng công cụ ghi/sửa file". Đặt một hook ở đó:
1. Lọc: chỉ quan tâm tài liệu kiến thức (`docs/**` …). File khác → thoát ngay.
2. Đọc tiêu đề + `keywords` của file vừa ghi → dùng chính công cụ tìm (bài 07-03) tìm tài liệu cùng chủ đề.
3. Có tài liệu **khác**, cùng chủ đề, điểm cao, mà file mới chưa có dòng `supersedes` → in **một dòng**:
   `xét: docs/giao-dien.md — điền supersedes: [...] hoặc supersedes: none`
4. Đã có dòng `supersedes` (kể cả `none`) → im.

Một dòng đó vào ngữ cảnh agent ngay trong lượt (bài 07-04), agent sửa khối nhãn trong vài giây. Đây là chỗ `none` (bài 07-05) phát huy:
nó cho hook biết khi nào phải im.

## 4. Nhắc, đừng chặn (câu hỏi 2)

Hook có thể *chặn* (không cho ghi). Vì sao không nên?
- **Người viết học cách lách.** Bị chặn mãi, ai cũng điền `supersedes: none` cho xong. Câu trả lời rác trông y hệt câu trả lời thật — và
  giờ bạn còn **mất** tín hiệu "chưa xét".
- **Gợi ý sai là chuyện thường.** Trùng chữ ≠ cùng chủ đề. Nhắc sai thì tốn một dòng; chặn sai thì kẹt cả việc.
- **Đóng cứng (ossification).** Một nghiên cứu về trí nhớ agent (SSGM, 2026) chỉ ra: lọc "nhất quán" quá chặt làm kiến thức không đổi
  được nữa — mọi cập nhật đều thành "mâu thuẫn cần xử lý", người ta ngại cập nhật.

Nên: **nhắc một dòng, `none` là câu trả lời hợp lệ, không chặn gì.** Đo bằng *số khai báo mới mỗi tuần*, không đo bằng tỉ lệ tuân thủ.

## 5. Báo tài liệu phụ thuộc (câu hỏi 3)

Khi `giao-dien-moi.md` khai thay `giao-dien.md`, bảng cạnh (bài 07-06) trả ngay "ai trỏ tới `giao-dien.md`?" → checklist, mẫu ảnh, mẫu
email. Hook in thêm:
`có thể đang dựa trên cái cũ: checklist-giao-dien.md, prompt-anh.md, email-gioi-thieu.md`

Hai giới hạn quan trọng:
- **Chỉ một bước.** Đi tiếp "ai trỏ tới checklist" thì danh sách nổ, nhất là khi gặp hub (bài 07-06).
- **Báo, không tự sửa.** Ba tài liệu kia có thể của người khác, và có thể *không* cần đổi. Người viết quyết: sửa, nhờ chủ tài liệu sửa,
  hay bỏ qua.

## 6. Kiểm định kỳ (lint)

Hook chỉ thấy file *vừa ghi*. Có lỗi chỉ thấy khi nhìn cả kho — để một lần quét hằng tuần (gọi là *lint*: kiểm lỗi kiểu dáng, như
kiểm chính tả cho cả cuốn sách):

| Kiểm | Bắt được |
|---|---|
| Hai tài liệu rất giống nhau mà không có cạnh nào nối | hai bản cùng chủ đề sống song song |
| Tài liệu mồ côi (không ai trỏ tới, không trỏ ai) | kiến thức không ai tìm thấy bằng đường cạnh |
| `supersedes` trỏ tới file không tồn tại | đổi tên / xoá mà quên sửa nhãn |
| Vòng "A thay B, B thay A" | khai nhầm |
| Tên trường sai (`superseeds`) | schema trôi (bài 07-05) |

Lint cũng chỉ **báo**, theo nhịp tuần.

## 7. Các cách, trên ca "giao diện mới"

| Cách | Kết quả | Gãy khi |
|---|---|---|
| A. Dặn "nhớ khai supersedes" | thường quên | người viết bận |
| B. Chặn lưu tới khi khai | khai `none` cho xong | sau 2 tuần: rác + đóng cứng |
| C. Hook nhắc 1 dòng lúc ghi, `none` hợp lệ | khai đúng phần lớn ca | gợi ý sai → nhắc thừa 1 dòng (chấp nhận được) |
| D. C + báo phụ thuộc 1 bước | thấy cả 3 tài liệu dựa trên cái cũ | danh sách dài khi gặp hub → giới hạn ≤ 5, bỏ hub |
| E. LLM đọc tài liệu mới, tự điền | ít công | tốn tiền mỗi lần ghi (07-02), tự tin sai |
| F. Chỉ lint tuần | bắt muộn một tuần | cả tuần đã làm theo cái cũ |

**Quy luật:** hỏi đúng lúc ngữ cảnh đầy nhất (lúc ghi), hỏi một dòng, chấp nhận "không" làm câu trả lời; còn sót thì để lưới thưa hơn
(lint tuần) hứng. Không bao giờ chặn.

## 8. Scale

- **Nhỏ:** cách A đủ, người viết nhớ hết.
- **Vừa** (nhiều người, nhiều tài liệu trỏ nhau): C + D là chỗ có lời nhất — người viết bản mới thường không biết ai đang trỏ tới bản cũ.
- **Lớn:** kho nhiều tài liệu trùng chữ → gợi ý thành nhiễu; cần ngưỡng điểm cao hơn, lọc theo phạm vi, và về sau so theo nghĩa thay vì
  theo chữ. Cái vỡ là **độ đúng của gợi ý**, kéo theo người viết nhờn.

## 9. Bốn nền tảng

Hook sau-khi-ghi là chương trình con như bài 07-04: **Windows** bật chậm hơn **Mac**, nên việc *lọc đường dẫn* phải chạy đầu tiên (thoát
trước khi nạp thứ nặng); đường dẫn trên Windows có `\` → chuẩn hoá trước khi so mẫu. **iOS / Android** không có hook, nhưng cùng mẫu có
trong công cụ làm app: đổi một tài nguyên dùng chung (font, bộ icon) thì công cụ **liệt kê** màn hình nào đang dùng nó ("tìm nơi tham
chiếu") thay vì cấm lưu — báo phụ thuộc, người quyết.

## 10. Tóm tắt

Khai báo "cái gì thay cái gì" xảy ra khi hệ thống nhắc một dòng đúng lúc ghi, chấp nhận `none`, báo tài liệu phụ thuộc một bước, và để
lint tuần hứng phần sót; không chặn.

**Thuật ngữ:** write path (đường ghi) · nudge vs gate (nhắc / chặn) · ossification (đóng cứng) · dependents (tài liệu phụ thuộc) · cascade (lan truyền) · orphan (mồ côi) · lint.

**Giờ bạn biết thêm:** làm sao để nhãn ở bài 07-05 *thật sự được điền*, mà không biến thành giấy tờ.

---

> **Ví dụ thật: Seriously làm thế này**
>
> - Seriously đã dùng sự kiện "vừa ghi/sửa file" (`PostToolUse`, lọc công cụ `Write|Edit`) cho các hook khác: tự tạo file `.meta` của
>   Unity, phát hiện agent bị kẹt lặp lại một việc. Hook nhắc `supersedes` là đề xuất (tên dự kiến `tools/claude/supersede_hint.py`), chưa có.
> - Đã có lint tuần cho cả công ty (`kit company lint`): in `WARN`, chỉ chặn khi chạy chế độ `--strict` — đúng tinh thần "báo, không chặn".
>   Các mục kiểm ở §6 dự kiến thêm vào đó.
> - Ghi chú nghiên cứu SSGM (arXiv 2603.11768) nằm trong biên bản tranh luận `docs/shared/memory-debate-2026-10-20.md`.
> - Trong Seriously, tài liệu của phòng khác không được tự sửa (mỗi phiên "nhận" mảng của mình) — lý do thêm vì sao bước báo phụ thuộc
>   chỉ *báo* và gửi việc cho phòng chủ, không tự sửa.

**Bài sau:** [07-09 — Đo](07-09-do.md).
