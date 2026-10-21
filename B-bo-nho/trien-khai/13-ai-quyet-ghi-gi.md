# 13 — Ai quyết ghi gì

> Chuỗi "Triển khai trí nhớ", bài 13/21. Đọc ~10 phút.
> **Bạn đã biết** (bài 02): trục "ai điều khiển" — người, luật, LLM tự động, agent tự quyết; các kho file / bảng / vector / đồ thị (05–08);
> các cách tìm (09–12).

## 1. Chuyện mở đầu

Bốn đội cùng làm trợ lý cho Mai, mỗi đội một kiểu ghi:
- Đội 1: chỉ nhớ khi Mai bấm "nhớ cái này". Sau 3 tháng: 4 dòng.
- Đội 2: lưu nguyên văn mọi tin nhắn. Sau 3 tháng: 20 nghìn đoạn, tìm "dị ứng" ra 40 đoạn chat linh tinh.
- Đội 3: sau mỗi cuộc chat, một LLM rút "sự thật mới". Sau 3 tháng: 600 sự thật, trong đó "Mai thích tôm" (rút từ câu "con mình thích tôm").
- Đội 4: cho agent công cụ `ghi_nhớ()`, để nó tự quyết. Agent ghi 12 lần trong tháng đầu, rồi gần như thôi.

## 2. Dừng 30 giây

- Đội nào ghi *đúng* nhất? Đội nào ghi *đủ* nhất? Có đội nào được cả hai không?
- Đội 3 tốn gì mỗi cuộc chat? Nhân với 10 nghìn khách của cửa hàng Lá thì sao?
- Lỗi "Mai thích tôm" — ai sẽ phát hiện, và khi nào?

## 3. Bốn người ghi

**A. Người khai** (người dùng bấm "nhớ", người viết tài liệu). *Đúng* cao — người biết điều gì quan trọng. *Đủ* thấp — người quên, người bận.
*Hợp khi:* sự thật quan trọng, ít (dị ứng, quyết định kỹ thuật). *Gãy khi:* phụ thuộc thói quen người.

**B. Luật cố định (code).** "Lưu mọi tin nhắn", "mỗi đơn là một sự kiện", "mỗi commit là một bản ghi", "khi người dùng gõ *nhớ rằng…* thì lưu
phần sau". 0 tiền model, tất định, chạy lại ra y hệt. *Hợp khi:* sự kiện có dạng rõ; lưu thô để tìm sau. *Gãy khi:* lưu quá nhiều thứ thô →
gánh nặng chuyển sang khâu tìm; không rút được "sự thật" từ chữ tự do.

**C. LLM rút tự động.** Sau mỗi cuộc chat (hoặc mỗi vài lượt), một LLM đọc lại và trích sự thật mới, so với sự thật cũ, quyết định **thêm / sửa /
xoá / bỏ qua**. Mem0 (arXiv 2504.19413) mô tả đúng vòng này; Zep/Graphiti trích vào đồ thị có thời gian. *Đủ* cao. *Hợp khi:* chữ tự do là nguồn
chính, có ngân sách. *Gãy khi:* tiền × mọi cuộc chat (câu hỏi 2); LLM rút sai một cách tự tin (câu hỏi 3: chỉ phát hiện khi gây hậu quả, vì không
ai đọc lại 600 sự thật); quyết "xoá" sai làm mất thông tin.

**D. Agent tự quyết, bằng công cụ.** Agent có công cụ `ghi_nhớ`, `sửa_nhớ`, `tìm_nhớ` và tự gọi giữa lúc làm việc. MemGPT/Letta (2023) phổ biến
cách này: model tự quản "bộ nhớ chính" luôn trên bàn và "bộ nhớ lưu trữ" ngoài, như hệ điều hành quản RAM và ổ đĩa. Memory tool của Anthropic
là phiên bản file. *Hợp khi:* agent làm việc dài, tự chủ. *Gãy khi:* agent không gọi (bận việc chính, quên — như đội 4); gọi quá nhiều; chất
lượng phụ thuộc model và lời nhắc.

**E. Làm nền / làm lúc rảnh.** Biến thể của C/D: việc ghi chạy **ngoài** cuộc chat — một agent nền đọc lại lịch sử khi người dùng không chờ
(Letta gọi là *sleep-time compute*; Anthropic mô tả quy trình agent chạy theo lô đọc lại phiên cũ để đề xuất cải thiện trí nhớ). Không thêm độ trễ
cho người dùng; kết quả có thể được người duyệt trước khi dùng.

Câu hỏi 1: không ai được cả hai — **đúng** và **đủ** kéo nhau ngược chiều. Hệ thống thật thường trộn: luật cho thứ thô (B), người hoặc LLM cho sự
thật (A/C), và duyệt cho thứ quan trọng.

## 4. Ghi cái gì — vài luật chọn lọc dùng được với mọi người ghi

- **Ghi kèm nguồn**: mỗi sự thật trỏ về đoạn chat/tài liệu sinh ra nó — để kiểm, để sửa (đội 3 lẽ ra thấy "con mình thích tôm").
- **Ghi kèm thời điểm** (bài 08, 15).
- **Ghi kèm độ chắc**: "Mai nói thẳng" vs "suy ra".
- **Không ghi thứ đã có nguồn sự thật** (bài 06): đơn hàng → tra, đừng chép.
- **Không ghi dữ liệu nhạy cảm** nếu không cần (bài 18).

## 5. Bảng một lần nhìn

| Người ghi | Đúng | Đủ | Tiền | Kiểm được | Gãy khi |
|---|---|---|---|---|---|
| A. Người | ✓✓ | ✗ | công người | ✓ | người quên |
| B. Luật | ✓ (thô) | ✓ (thô) | 0 | ✓ | gánh nặng sang tìm |
| C. LLM tự động | ~ | ✓✓ | cao, theo lượng chat | khó | rút sai, tiền |
| D. Agent tự gọi | ~ | ~ | token trong phiên | tuỳ | agent không gọi |
| E. Nền / lúc rảnh | ~ | ✓ | như C, ngoài giờ | ✓ nếu có duyệt | chậm có hiệu lực |

**Quy luật:** chọn người ghi theo **giá của một lần ghi sai** và **giá của một lần quên**. Sai đắt (dị ứng, quyết định) → có người hoặc có duyệt;
quên đắt mà sai rẻ → tự động.

## 6. Ba kịch bản

- **Mai:** B (lưu thô) + C hoặc E (rút sự thật) + A cho điều quan trọng ("nhớ cái này"), có màn hình để Mai xem/sửa.
- **Cửa hàng Lá:** B là chính (sự kiện đơn/khiếu nại); C chỉ một bản tóm ngắn cuối mỗi cuộc chat; tiền × số khách → model nhỏ, rẻ.
- **Nhóm code:** A (người viết tài liệu, quyết định) + B (git) là nền; D cho agent ghi điều nó học trong phiên, người duyệt định kỳ.

## 7. Scale

- **Nhỏ:** A hoặc D là đủ.
- **Vừa:** B + một trong A/C/D.
- **Lớn:** C với mỗi cuộc chat thành khoản chi lớn → model nhỏ, gộp lô, chạy nền (E); và sai số không ai đọc → cần đo (bài 19) và cho người dùng
  sửa. Cái vỡ là **chất lượng sự thật đã ghi**, không phải chỗ chứa.

## 8. Bốn nền tảng

- **Windows / Mac:** C/E chạy được bằng model trên máy (rẻ, riêng tư) nếu chấp nhận chất lượng thấp hơn.
- **iOS / Android:** C bằng model trên máy hợp với việc rút ngắn sự thật; chạy lúc máy rảnh/đang sạc (iOS có tác vụ nền xử lý, Android có
  WorkManager với điều kiện "đang sạc"). Gửi lên máy chủ để rút = gửi dữ liệu cá nhân đi → cần nói rõ với người dùng.

## 9. Tóm tắt

Có bốn người ghi — người, luật, LLM tự động, agent tự gọi — cộng biến thể chạy nền. "Đúng" và "đủ" kéo ngược nhau; chọn theo giá của ghi sai vs
giá của quên; luôn ghi kèm nguồn, thời điểm, độ chắc.

**Thuật ngữ:** write policy (chính sách ghi) · extraction (rút sự thật) · ADD/UPDATE/DELETE/NOOP · MemGPT / Letta · core vs archival memory · sleep-time compute · provenance (nguồn gốc) · confidence (độ chắc).

**Giờ bạn biết thêm:** bên ghi của vòng trí nhớ — ai ghi, ghi gì, và mỗi lựa chọn trả giá ở đâu.

**Bài sau:** [14 — Ai quyết khi nào đọc](14-ai-quyet-khi-nao-doc.md).
