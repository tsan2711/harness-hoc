# 15 — Cập nhật, mâu thuẫn, quên

> Chuỗi "Triển khai trí nhớ", bài 15/21. Đọc ~10 phút.
> **Bạn đã biết** ([08](08-do-thi-tri-thuc.md), [13](13-ai-quyet-ghi-gi.md)–[14](14-ai-quyet-khi-nao-doc.md)): thời gian hiệu lực trên cạnh;
> ghi kèm nguồn và thời điểm; ADD/UPDATE/DELETE; năm kiểu đọc.

## 1. Chuyện mở đầu

Tháng 3, Mai nói "mình ăn chay". Tháng 7: "mình ăn lại thịt rồi". Trợ lý giữ cả hai câu. Mai hỏi "gợi ý quán tối nay" — trợ lý gợi ý quán chay.
Ở nhóm code, ghi chú tháng 1 viết "dùng ChartLite cho biểu đồ"; ghi chú tháng 4 viết "bỏ ChartLite". Agent tìm "thư viện biểu đồ" — ghi chú tháng
1 khớp hơn (nhiều chữ "biểu đồ" hơn), đứng đầu.

Còn cửa hàng Lá: một khách yêu cầu "xoá hết dữ liệu của tôi". Đội xoá dòng trong bảng khách. Tuần sau, chatbot vẫn trả lời "chị hay mua size M
đúng không ạ?" — sự thật đó nằm trong một bản tóm tắt và trong kho vector.

## 2. Dừng 30 giây

- Khi hai sự thật mâu thuẫn, nên **xoá cái cũ**, hay **giữ cả hai và đánh dấu**? Mỗi cách mất gì?
- Tìm theo độ giống không biết cái nào mới. Phải thêm gì vào khâu tìm?
- Một sự thật được chép vào bao nhiêu nơi? Xoá "hết" nghĩa là xoá ở đâu?

## 3. Cập nhật — bốn cách

**A. Ghi đè.** Giữ một bản, sửa tại chỗ. Đơn giản, bàn luôn sạch. *Gãy khi:* mất lịch sử ("hồi tháng 3 Mai ăn chay phải không?" không trả lời
được); ghi đè sai thì mất luôn bản đúng.

**B. Chỉ thêm, kèm thời điểm; đọc bản mới nhất.** Không xoá; khi đọc lấy bản mới nhất theo chủ đề. *Gãy khi:* phải biết hai câu cùng "chủ đề"
(chay ↔ thịt) — cần khoá chủ đề hoặc LLM nhận ra.

**C. Thời gian hiệu lực (bitemporal).** Mỗi sự thật có "đúng từ – đến" (thời điểm trong đời thật) và "ghi lúc" (thời điểm hệ thống biết). Sự thật
mới không xoá cũ mà **đóng** khoảng hiệu lực của cũ. Zep/Graphiti (arXiv 2501.13956) làm vậy trên cạnh đồ thị. Trả lời được cả "bây giờ" lẫn "hồi
đó". *Gãy khi:* phức tạp; vẫn cần nhận ra hai câu mâu thuẫn.

**D. LLM phân xử.** Khi ghi, LLM so sự thật mới với những sự thật gần nó, chọn thêm / sửa / xoá / bỏ qua (Mem0). *Gãy khi:* LLM phân xử sai; tiền
mỗi lần ghi; và nếu phân xử bằng xoá thì mất lịch sử như A.

Khâu tìm (câu hỏi 2): thêm **thời điểm** vào điểm xếp hạng (mới hơn được cộng), hoặc lọc bản đã hết hiệu lực trước khi xếp hạng, hoặc đánh dấu
"đã thay bởi" để ghi chú cũ trỏ sang ghi chú mới.

## 4. Quên — năm cách

Quên có hai mục đích khác nhau: **để tìm tốt hơn** (bớt nhiễu) và **vì phải xoá** (người dùng yêu cầu, luật, hết hạn lưu trữ).

1. **Phai theo thời gian (decay).** Điểm đọc giảm dần theo tuổi; Generative Agents (Park 2023) trộn độ mới (giảm theo hàm mũ), độ quan trọng, độ
   liên quan. Không xoá, chỉ chìm xuống. *Gãy khi:* điều cũ mà quan trọng (dị ứng) cũng chìm → cần độ quan trọng, hoặc ghim (bài 14).
2. **Hạn sử dụng (TTL).** "Ghi chú phiên" tự xoá sau 30 ngày. Đơn giản. *Gãy khi:* hạn đặt sai cho từng loại.
3. **Gộp (consolidation).** Nhiều mẩu cũ → một bản tóm/kết luận, xoá mẩu (bài 04). Generative Agents gọi bước rút kết luận là *reflection*. *Gãy
   khi:* bản gộp mất chi tiết mà sau này cần.
4. **Dọn bởi người/agent định kỳ.** Đọc lại, xoá trùng, xoá sai. *Gãy khi:* không ai làm.
5. **Xoá theo yêu cầu.** Bắt buộc chính xác (câu hỏi 3).

**Xoá phải lan tới mọi bản sao.** Một sự thật có thể nằm ở: bản gốc (chat), sự thật đã rút, bản tóm, vector, chỉ mục chữ, cạnh đồ thị, cache, bản
sao lưu, log. ChatGPT nói rõ: muốn xoá hẳn một điều nó nhớ, phải xoá cả saved memory lẫn những cuộc chat là nguồn của nó. Thiết kế dễ xoá nhất:
mỗi bản dẫn xuất **ghi lại nó sinh từ nguồn nào** (bài 13) — xoá nguồn thì tìm được và xoá/dựng lại mọi thứ sinh từ nó.

## 5. Bảng một lần nhìn

| Cách | Giữ lịch sử | Trả lời "bây giờ" đúng | Độ phức tạp | Gãy khi |
|---|---|---|---|---|
| A. Ghi đè | ✗ | ✓ | thấp | ghi đè sai |
| B. Thêm + mới nhất | ✓ | ✓ nếu biết chủ đề | thấp | không nhận ra cùng chủ đề |
| C. Hiệu lực | ✓✓ | ✓ | cao | nhận diện mâu thuẫn |
| D. LLM phân xử | tuỳ | ~ | vừa, tốn tiền | phân xử sai |

**Quy luật:** **mâu thuẫn là chuyện thường**, không phải lỗi hiếm — người đổi ý, code đổi hướng. Mọi bản ghi cần thời điểm; mọi bản dẫn xuất cần
trỏ về nguồn, để cập nhật và xoá lan được.

## 6. Ba kịch bản

- **Mai:** B hoặc D cho sở thích; ghim + không phai cho dị ứng; màn hình cho Mai xem và xoá từng điều.
- **Cửa hàng Lá:** xoá theo yêu cầu là bắt buộc (luật bảo vệ dữ liệu cá nhân, ví dụ GDPR ở châu Âu, Nghị định 13/2023 ở Việt Nam) → thiết kế
  "nguồn → bản dẫn xuất" từ ngày đầu; TTL cho chat thô.
- **Nhóm code:** C nhẹ — ghi chú quyết định có "thay bởi →"; git đã giữ lịch sử, nên ghi chú hiện tại có thể ghi đè (A) mà không mất gì.

## 7. Scale

- **Nhỏ:** A hoặc B, dọn tay.
- **Vừa:** B + thời điểm trong điểm xếp hạng; TTL.
- **Lớn:** C hoặc D; xoá lan qua nhiều kho thành một hệ thống riêng (hàng đợi xoá, kiểm xoá xong). Cái vỡ là **số bản sao** của mỗi sự thật.

## 8. Bốn nền tảng

- **Windows / Mac:** dữ liệu cục bộ còn nằm trong bản sao lưu máy (Time Machine, File History) — xoá trong app chưa chắc mất khỏi bản sao lưu.
- **iOS / Android:** bản sao lưu đám mây của máy (iCloud, Google) có thể chứa dữ liệu app; có thể loại file khỏi sao lưu (iOS: cờ "exclude from
  backup"; Android: luật sao lưu trong manifest). Xoá app thường xoá dữ liệu cục bộ, không xoá dữ liệu trên máy chủ.

## 9. Tóm tắt

Cập nhật: ghi đè, thêm + mới nhất, thời gian hiệu lực, LLM phân xử. Quên: phai, hạn, gộp, dọn, xoá theo yêu cầu. Xoá thật phải lan tới mọi bản dẫn
xuất — chỉ làm được nếu mỗi bản dẫn xuất nhớ nguồn của nó.

**Thuật ngữ:** overwrite · append-only · bitemporal (valid time / transaction time) · supersede · decay · TTL · consolidation · reflection · right to erasure · lineage (dòng dõi dữ liệu).

**Giờ bạn biết thêm:** phần "quản lý" của vòng ghi → quản → đọc — chỗ hệ thống trí nhớ hỏng âm thầm nhất.

**Bài sau:** [16 — Trí nhớ cách làm](16-tri-nho-cach-lam.md).
