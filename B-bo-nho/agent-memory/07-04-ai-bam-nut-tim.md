# 07-04 — Ai bấm nút tìm

> Chuỗi 07, bài 4/12. Đọc ~9 phút.
> **Bạn đã biết:** ngữ cảnh nhỏ và đắt ([07-01](07-01-model-khong-nho.md)); kiến thức ở file trong git ([07-02](07-02-ghi-ra-ngoai.md));
> tìm bằng chỉ mục + BM25 trong mili-giây, trả vài đoạn tốt nhất ([07-03](07-03-tim-lai.md)).

## 1. Chuyện mở đầu

Quán Nhỏ giờ có đủ: ghi chú "bỏ ChartLite vì giật" nằm trong `docs/quyet-dinh.md`, công cụ tìm chạy 50 ms, agent *được phép* gọi nó.
Huy gõ: "thêm biểu đồ doanh thu theo tháng". Agent không tìm gì cả — nó "biết" ChartLite là thư viện phổ biến, viết code dùng
ChartLite luôn. Kiến thức có, công cụ có, **không ai bấm nút**.

## 2. Dừng 30 giây

- Thêm một dòng "nhớ tìm trước khi làm" vào lời dặn của agent — có đủ không? Vì sao?
- Nếu mỗi câu người gõ đều tự kèm 3 đoạn tìm được, cái gì xấu đi?
- Một bước chạy *trước mỗi câu* người gõ được phép chậm bao nhiêu?

## 3. Kéo và đẩy

**Kéo (pull):** agent tự quyết khi nào tìm. Muốn vậy, ba điều phải cùng đúng: (a) agent *nghi* mình thiếu thông tin, (b) agent *nhớ*
là có công cụ tìm, (c) agent hỏi *đúng chữ*. Điều (a) là chỗ gãy: model tự tin nhất đúng lúc nó sai — nó không biết là nó không biết.
Câu hỏi 1: một dòng dặn thêm chỉ giúp (b), không giúp (a).

**Đẩy (push):** hệ thống bao quanh agent tìm *thay* nó, ở những thời điểm biết trước, rồi đặt kết quả lên mặt bàn. Agent không cần
nghi ngờ gì. Ví dụ đời thường: bạn không cần nhớ tra lịch — điện thoại *đẩy* thông báo "15 phút nữa họp".

**Điểm vào** là những thời điểm biết trước đó. Với agent viết code, ba điểm vào tự nhiên:
| Điểm vào | Lấy gì làm câu tìm |
|---|---|
| Nhận một việc (ticket) | tiêu đề, đường dẫn file, mã lỗi trong mô tả việc |
| Mở phiên mới khi còn việc dở hôm qua | tên việc dở, file đang sửa dở |
| Mỗi câu người gõ | chính câu đó |

## 4. Hook — cái móc để đẩy

**Hook** là: *khi sự kiện X xảy ra → chạy lệnh Y*. Ví dụ đời thường: chuông cửa (sự kiện: có người bấm → chạy: chuông kêu), hay bộ lọc
email (sự kiện: thư đến → chạy: gắn nhãn). Các công cụ agent đời mới (Claude Code, Cursor, …) cho đặt hook ở các sự kiện như "mở phiên",
"người vừa gõ một câu", "agent vừa dùng một công cụ".

Mẹo quan trọng: với nhiều công cụ, **lệnh trong hook in ra chữ gì thì chữ đó được thêm vào ngữ cảnh** của agent. Vậy "đẩy" chỉ là: đặt
một hook ở sự kiện "người vừa gõ câu" → lệnh lấy câu đó, gọi công cụ tìm của bài 07-03 → in ra 3 đoạn. Agent đọc câu của Huy *kèm* đoạn
"bỏ ChartLite vì giật", trước khi kịp viết dòng code nào.

## 5. Ba ngân sách (câu hỏi 2 và 3)

Đẩy không miễn phí. Nó trả bằng ba đồng tiền:

**Thời gian.** Hook chạy trước *mỗi* câu, người gõ phải chờ. Dưới ~150 ms thì không ai thấy; 1 giây thì khó chịu; 3 giây thì người tắt
nó đi. Hệ quả: trong hook chỉ *tìm*, không *dựng lại chỉ mục* (việc nặng đó để lúc khác, ví dụ lúc mở phiên). Hook lỗi hoặc quá giờ →
im lặng, không chặn người dùng.

**Token.** 3 đoạn ≈ 600 token. Phiên 40 câu = 24 000 token thêm vào — đáng kể (bài 07-01: token là tiền và chỗ).

**Sự chú ý — đồng đắt nhất.** Nếu câu nào cũng kèm 3 đoạn, phần lớn là nhiễu ("ok", "tiếp đi" cũng kèm 3 đoạn), agent sẽ học cách
**lờ** phần đẩy — như cảnh báo vàng trong trình biên dịch không ai đọc. Đây gọi là *nhờn cảnh báo*. Nên cần **ngưỡng im**:
- bỏ qua câu ngắn và lệnh ("ok", "làm tiếp", "/clear");
- chỉ in đoạn có điểm vượt ngưỡng (khớp chữ hiếm thật), không in "đoạn ít tệ nhất";
- bỏ đoạn agent vừa đọc rồi.

Im lặng đúng lúc quan trọng ngang nói đúng lúc.

## 6. Các cách, thử trên câu "thêm biểu đồ doanh thu theo tháng"

| Cách | Kết quả | Ưu | Gãy khi |
|---|---|---|---|
| A. Dặn "nhớ tìm" | agent không tìm | 0 chi phí | model tự tin |
| B. Đẩy mọi câu, không ngưỡng | có ghi chú đúng; câu "ok" cũng kèm 3 đoạn nhiễu | không sót | ồn → bị lờ; token phình |
| C. Đẩy có ngưỡng + bỏ câu ngắn | có ghi chú đúng; "ok" im | rẻ, đúng chỗ | câu diễn đạt lại (BM25 trượt, 07-03) |
| D. Như C + dựng lại chỉ mục trong hook | như C, luôn mới nhất | không bao giờ cũ | người chờ vài giây mỗi câu |
| E. Hỏi một LLM nhỏ "câu này có cần tìm không" | thường đúng | hiểu ý | tốn tiền mỗi câu, không tất định (07-02) |

**Quy luật:** đừng trông agent nhớ tìm — đẩy ở điểm vào; nhưng trả bằng ba đồng: mili-giây, token, sự chú ý, và đồng thứ ba đắt nhất.

## 7. Scale

- **Nhỏ** (vài phiên/ngày): đẩy lúc nhận việc là đủ.
- **Vừa** (nhiều người, hàng chục phiên/ngày): câu hỏi giữa phiên là chỗ sót lớn nhất; ngưỡng im thành chuyện chính.
- **Lớn** (kho tăng hàng nghìn đoạn/ngày): tìm vẫn nhanh, nhưng tỉ lệ "đoạn đúng chữ mà sai ý" tăng → ngưỡng phải nâng, cần ưu tiên
  đoạn cùng nhóm/dự án với người hỏi. Cái vỡ là **độ đúng của 3 đoạn đầu**, không phải tốc độ.

## 8. Bốn nền tảng

Hook là một chương trình con được bật lên mỗi lần. Trên **Mac** bật Python mất ~20 ms; trên **Windows** bật chương trình con chậm hơn
rõ (thường gấp vài lần) và phần mềm diệt virus có thể quét mỗi lần chạy — ngân sách 150 ms dễ vỡ ở Windows trước, nên đo trên cả hai.
**iOS / Android** không có hook kiểu này, nhưng cùng ý "đẩy ở điểm vào" là gợi ý trong app: mẹo hiện khi người dùng *chạm* nút lần đầu
(điểm vào), không bắt họ tự mở trang hướng dẫn (kéo) — và cũng cần ngưỡng im, không thì người dùng tắt hết thông báo.

## 9. Tóm tắt

Agent không biết lúc nào nó thiếu, nên đừng chờ nó kéo: dùng hook đẩy vài đoạn liên quan ở điểm vào (nhận việc, mở phiên, mỗi câu),
nhanh dưới ~150 ms, ít token, và im khi không chắc.

**Thuật ngữ:** pull / push (kéo / đẩy) · entry point (điểm vào) · hook · latency budget (ngân sách thời gian) · alert fatigue (nhờn cảnh báo) · silence threshold (ngưỡng im).

**Giờ bạn biết thêm:** *ai* đưa kiến thức lên bàn (hệ thống, qua hook), *khi nào* (điểm vào), và cái giá phải giữ.

---

> **Ví dụ thật: Seriously làm thế này**
>
> - Seriously dùng Claude Code. Hook đặt trong `.claude/settings.json`; hook ở sự kiện "người vừa gõ câu" (`UserPromptSubmit`) nhận câu
>   qua đầu vào chuẩn; in ra thì chữ đó vào ngữ cảnh; thoát mã 2 thì chặn câu; quá thời gian thì bị bỏ qua.
> - **Đã đẩy lúc nhận việc:** khi một phòng nhận việc từ hộp thư, công cụ tự in ≤ 3 đoạn liên quan. Tính đến 2026-10-21, **679/867 lần
>   nhận việc (78 %)** có ít nhất một đoạn được đẩy — không cần agent nhớ gì.
> - **Đã đẩy lúc mở phiên có việc dở** (từ 2026-10-16).
> - **Chưa đẩy ở mỗi câu Bi gõ** — đây là bước tiếp theo trong kế hoạch, ngân sách đặt trước: < 150 ms, ≤ 600 token, lỗi thì im.
> - Số đo thật cho ngân sách thời gian: tìm khi cache sẵn **33–70 ms**; ngay sau một commit thì **~1,1 s**, vì một cache phụ (ngày sửa
>   file theo git) bị lệch và phải đọc lại lịch sử — một cái bẫy phải gỡ trước khi đẩy ở mỗi câu.

**Bài sau:** [07-05 — Nhãn trên tài liệu](07-05-nhan-tren-tai-lieu.md).
