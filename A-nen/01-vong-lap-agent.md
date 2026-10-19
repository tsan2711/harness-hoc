# Bài A01 — Model không nhớ gì, và "agent" thực ra chỉ là một vòng lặp

## 1. Câu chuyện: Lan nhờ "sửa lỗi chính tả ở 3 file"

Lan gõ vào một chatbot thường: *"Sửa lỗi chính tả trong `a.md`, `b.md`, `c.md` giúp mình."*
Chatbot trả lời rất lịch sự: "Bạn dán nội dung các file vào đây nhé." Lan dán ba file, chatbot trả lại ba bản đã sửa,
Lan copy-paste từng cái về chỗ cũ. Xong — nhưng **Lan mới là người làm phần "tay chân"**: mở file, dán, lưu.

Cùng việc đó với một agent (Claude Code): Lan gõ đúng một câu. Agent tự tìm 3 file, tự đọc, tự sửa, tự lưu, tự chạy kiểm tra, rồi báo "xong".

Model là **cùng một model**. Cái khác là gì? Không phải model "thông minh hơn". Là có **một chương trình bao quanh** đang làm phần tay chân thay Lan.
Chương trình đó chính là **harness**, và lõi của nó là một vòng lặp ngắn đến ngạc nhiên.

## 2. Dừng 30 giây — tự dựng trong đầu

Không cần trả lời ai:

- Model chỉ làm được đúng một việc: nhận chữ vào → trả chữ ra. Nó không mở được file, không chạy được lệnh. Hãy tự nghĩ
  **tối thiểu cần thêm những mảnh nào** để "chữ ra" biến thành "file đã được sửa trên đĩa".
- Giả sử model muốn đọc `a.md`, nó "nói" `đọc a.md`. Ai là người thật sự mở file? Ai đưa nội dung lại cho model? Vẽ vòng đó trên giấy nháp (hoặc trong đầu).
- Đoán: vòng này **dừng khi nào**? Nếu không có luật dừng, điều gì xảy ra với hóa đơn của bạn?

(Đáp án ở mục 3. Nếu bạn dựng được vòng "model nói → chương trình làm → kết quả trả lại model → lặp", bạn đã hiểu 80% bài này.)

## 3. Vòng lặp agent — toàn bộ cơ chế

```
messages = [system prompt, yêu cầu của Lan]
lặp:
    reply = model(messages)            # model đọc "tờ giấy", viết thêm chữ
    nếu reply chỉ là chữ thường:  → in cho Lan, DỪNG
    nếu reply xin gọi công cụ (vd. read_file a.md):
        kết quả = harness TỰ chạy công cụ   # model KHÔNG chạy, chỉ xin
        messages += [reply, kết quả]       # nối vào tờ giấy
```

Ba điều then chốt:

1. **Model không có trí nhớ.** Mỗi vòng, harness gửi lại **toàn bộ** tờ giấy (messages) từ đầu. Model "nhớ" file vừa đọc chỉ vì
   nội dung đó đã được nối vào tờ giấy. Hết phiên = vứt tờ giấy = quên sạch (đây là gốc rễ của chặng B bộ nhớ).
2. **Model chỉ *xin* gọi công cụ**; harness mới là bên thực thi. Vì thế harness chen được vào giữa: hỏi quyền, chặn lệnh nguy hiểm,
   chạy hook (chặng C, D).
3. **Điều kiện dừng nằm ở harness**: model nói chữ thường (không xin công cụ), hoặc chạm trần số vòng / token / tiền / thời gian.

Hệ quả về tiền: vòng *n* phải gửi lại cả tờ giấy dài *n* lượt → chi phí tăng gần như **bình phương** theo độ dài phiên
(nhiều caching giảm được, nhưng hình dạng vẫn vậy). Đó là lý do "ngữ cảnh là tiền" ở chặng A bài sau.

## 4. Năm cách dựng "agent" — cùng bài toán sửa 3 file

### Cách 1 — Một phát (one-shot), con người làm tay chân
Chính là chatbot ở câu chuyện. Không có vòng lặp.
- **Ưu:** rẻ, dễ đoán, không thể làm hỏng gì ngoài chữ.
- **Nhược:** người dùng làm hết phần việc thật; không tự kiểm kết quả.
- **Gãy ở:** khi việc có hơn vài bước hoặc phải đọc nhiều file.

### Cách 2 — Dây chuyền cố định (workflow / pipeline)
Lập trình viên viết sẵn: bước 1 liệt kê file → bước 2 gọi model sửa từng file → bước 3 lưu. Model chỉ là một ô trong dây chuyền.
- **Ưu:** dự đoán được, rẻ, dễ test, ít "tự do" nên ít tai nạn.
- **Nhược:** chỉ làm đúng việc đã lên dây chuyền; gặp tình huống ngoài kịch bản (file không tồn tại, cần đọc thêm file khác) là kẹt.
- **Gãy ở:** việc mở (mỗi lần mỗi khác), như sửa code.

### Cách 3 — Vòng lặp công cụ (ReAct / agent loop) ← mục 3 ở trên
Model tự quyết bước kế tiếp mỗi vòng; harness thực thi.
- **Ưu:** linh hoạt, xử lý được tình huống chưa lường; đơn giản về mã (vòng lặp ~50 dòng).
- **Nhược:** khó đoán; có thể đi lạc, lặp vô hạn, làm điều thừa; chi phí tăng theo độ dài (bình phương); chất lượng phụ thuộc mô tả công cụ.
- **Gãy ở:** phiên dài (tờ giấy đầy, model bắt đầu bỏ sót), hoặc công cụ nguy hiểm không có cổng.
- **Đây là lõi của Claude Code.**

### Cách 4 — Lập kế hoạch rồi thực thi (plan-then-execute)
Vòng 1 model chỉ viết kế hoạch (người duyệt được); các vòng sau mới làm theo.
- **Ưu:** người kiểm soát trước khi tốn tiền/sửa file; ít đi lạc.
- **Nhược:** kế hoạch viết khi chưa thấy thực tế thường sai; phải sửa kế hoạch giữa chừng.
- **Gãy ở:** việc mà khám phá quyết định bước sau (debug).
- Trong Claude Code là chế độ plan.

### Cách 5 — Nhiều agent (một điều phối, nhiều thợ)
Agent chính giao việc con cho agent phụ, mỗi người một tờ giấy riêng.
- **Ưu:** mỗi tờ giấy ngắn (rẻ, ít nhiễu); làm song song được.
- **Nhược:** truyền thông tin giữa các tờ giấy là việc khó (mất ngữ cảnh khi giao); tốn công điều phối; lỗi nhân lên.
- **Gãy ở:** khi các việc con phụ thuộc nhau chặt.
- Đây là hướng của "công ty agent" (chặng F).

## 5. Bảng so sánh

| | 1 một phát | 2 dây chuyền | 3 vòng lặp công cụ | 4 plan→làm | 5 nhiều agent |
|---|---|---|---|---|---|
| Ai làm tay chân | người | code cố định | harness theo lệnh model | harness | harness, nhiều tờ giấy |
| Linh hoạt | rất thấp | thấp | **cao** | cao | cao |
| Dễ đoán | **rất cao** | **cao** | thấp | trung bình | thấp |
| Chi phí | rẻ nhất | rẻ | tăng theo độ dài | trung bình | cao tổng, rẻ mỗi tờ |
| Rủi ro tai nạn | không | thấp | **cần cổng** | thấp | cần cổng + điều phối |
| Hợp với | hỏi đáp | việc lặp cố định | việc mở | việc lớn cần duyệt | việc to chia được |

**Quy luật:** càng nhiều tự do cho model thì càng linh hoạt nhưng càng cần *cổng và trần* của harness.
Đa số hệ thống thật là **cách 3 làm lõi**, chen vào vài chỗ cách 2 (việc cố định thì đóng thành script) và cách 4/5 khi việc lớn.

## 6. Scale: cùng vòng lặp, ba cỡ phiên

| Cỡ | Hiện tượng | Cái vỡ |
|---|---|---|
| **5 vòng** (sửa 3 file) | tờ giấy ngắn | không gì |
| **100 vòng** (một tính năng) | tờ giấy ~100k token | tốn tiền, model bỏ sót chi tiết ở giữa |
| **nhiều phiên / ngày / nhiều agent** | tờ giấy bị vứt giữa các phiên | mất bộ nhớ → chặng B; giẫm chân → chặng E |

Điều cần nhớ: vòng lặp **không** đổi khi scale — thứ phải thêm là *cái bao quanh vòng lặp* (cắt tờ giấy, ghi ra ngoài, trần, cổng).

## 7. Dừng lần hai — nhìn vòng lặp trong chính Seriously

Không cần trả lời, mở repo xem:

- Mở `~/.claude-zzd/settings.json` (hoặc `.claude/settings.json` trong Seriously), tìm `hooks`. Mỗi hook là một **chỗ harness chen vào vòng lặp**:
  trước khi chạy công cụ, sau khi chạy, khi bắt đầu phiên, khi dừng. Đối chiếu từng cái với sơ đồ ở mục 3: nó nằm ở dòng nào của vòng lặp?
- Câu "Ngữ cảnh > 120k → bàn giao rồi /clear" trong `Seriously/CLAUDE.md` là luật sinh ra từ đâu trong mục 3? (Gợi ý: từ chi phí bình phương và "tờ giấy" đầy.)
- `kit company send … --check review` giao việc sang phiên khác: đó là cách mấy trong 5 cách?

## 8. Bốn nền tảng

Vòng lặp là logic thuần, giống hệt mọi nơi; chỉ **công cụ** và **chỗ chạy harness** khác:

| | Harness chạy ở đâu | Công cụ "tay chân" khác biệt |
|---|---|---|
| **Mac** | terminal, Claude Code của bạn | shell zsh, file thường |
| **Windows** | terminal / WSL | PowerShell hoặc bash; đường dẫn `\`, file hoa/thường không phân biệt |
| **iOS** | app tự chứa vòng lặp, hoặc gọi API từ xa | không có shell; "công cụ" chỉ là hàm trong app, trong sandbox |
| **Android** | tương tự iOS | không có shell tự do; chạy nền bị OS giới hạn pin/thời gian |

Trên mobile, vòng lặp thường chạy ở **server**, điện thoại chỉ là màn hình + vài công cụ cục bộ (vị trí, ảnh). Lý do: pin, quyền, và key API không nên nằm trong app.

## 9. Tóm tắt một dòng
Agent = model + **vòng lặp do harness chạy** (model xin → harness làm → kết quả nối vào tờ giấy → lặp tới khi dừng). Model không nhớ, không có tay;
mọi "khả năng" đến từ harness; càng cho model tự do càng cần cổng và trần.

**Bài sau (A02):** Ngữ cảnh = tờ giấy + tiền — vì sao dài thì đắt, cắt/nén thế nào.

### Thuật ngữ
- **Harness**: chương trình bao quanh model (vòng lặp, công cụ, quyền, hook).
- **Messages / ngữ cảnh**: toàn bộ chữ gửi cho model mỗi vòng ("tờ giấy").
- **Tool call**: model xin chạy một công cụ; harness thực thi.
- **ReAct**: kiểu vòng lặp "nghĩ → làm → nhìn kết quả → nghĩ tiếp".
- **Trần (limit)**: giới hạn số vòng/token/tiền khiến vòng lặp phải dừng.
