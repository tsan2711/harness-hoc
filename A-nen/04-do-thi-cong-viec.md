# Bài A04 — Khi một đường thẳng không đủ: đồ thị công việc

> **Bạn đã biết:** vòng tự chạy = đích + cách kiểm bằng máy + điều kiện dừng; người làm tách khỏi người kiểm; bộ nhớ ghi ra đĩa; có phanh (bài A03).
> Bài này hỏi: **khi có nhiều vòng như thế, chúng nối với nhau thế nào?** Nguồn ý tưởng: bài 14 của khóa *learn-harness-engineering*
> (walkinglabs, MIT), bài "Building Effective Agents" của Anthropic và "The Orchestration Tax" của Addy Osmani; phần so sánh và ví dụ thật là của mình.

## 1. Câu chuyện: Hà và bốn vòng cãi nhau

Hà quản lý bộ phận hỗ trợ khách hàng. Cô dựng bốn vòng tự chạy, mỗi vòng một việc: (1) trả lời nhanh, (2) trả lời cho đủ ý,
(3) tăng tỷ lệ "đã giải quyết", (4) giữ chất lượng.

Sau hai tháng bảng điều khiển của từng vòng đều xanh. Nhưng khách bỏ đi gấp đôi. Điều gì xảy ra:
vòng (3) học được cách **đóng ticket** — khuyên khách đừng hỏi thêm, đánh dấu "đã giải quyết" cho cả việc chưa giải quyết;
vòng (1) và (2) kéo ngược chiều nhau; còn vòng (4) chấm bằng những ticket mà vòng (3) đã làm đẹp sẵn.
Không vòng nào sai theo mục tiêu của nó. **Sai ở chỗ không ai vẽ quan hệ giữa các vòng.**

## 2. Dừng 30 giây — tự nghĩ, không cần trả lời ai

- Trong bốn vòng trên, vòng nào **được phép đổi** mục tiêu của vòng nào? Vòng nào **có quyền cấm** (veto)? Hiện tại đáp án là "không ai cả" — vậy bạn muốn là gì?
- Vòng (3) đo bằng "tỷ lệ đã giải quyết". Ai kiểm xem con số đó còn đo đúng điều công ty quan tâm (khách ở lại) không?
- Một việc cần "nghiên cứu → làm → kiểm → gộp". Kiểm trượt thì quay lại **làm**, hay quay lại **nghiên cứu**? Ai quyết?

## 3. Bốn bộ phận của một đồ thị

Gỡ đồ thị ra chỉ còn bốn thứ, đều dùng chữ thường:

- **Nút (node):** một đơn vị việc có người chịu trách nhiệm. Có thể là mã chạy cố định (chạy test), một lần gọi model, một công cụ (commit),
  một agent đầy đủ có vòng riêng, hoặc **một người** (duyệt — đồ thị dừng chờ bạn gật).
- **Cạnh (edge):** việc chuyển tay giữa các nút: song song (A xong thì B và C cùng chạy), có điều kiện (đạt đi trái, trượt đi phải),
  thử lại (nút chết thì quay về chính nó), lùi (kiểm trượt thì lùi về nút làm, cách đó ba bước).
- **Trạng thái chung:** một "bảng trắng" mọi nút cùng đọc ghi (yêu cầu, ghi chú, phiên bản code, kết quả test). Các nút không gào nhau, chúng đọc bảng.
- **Luật định tuyến:** đi đâu tiếp. "Test đạt → phát hành. Trượt → về nút làm. Thiếu thông tin → về nút nghiên cứu."

Bốn tầng chồng lên nhau, không thay nhau: câu lệnh (prompt) → thông tin (ngữ cảnh) → vòng lặp → **đồ thị**.
Mỗi nút trong đồ thị vẫn có câu lệnh, ngữ cảnh và vòng riêng; đồ thị chỉ quyết định chúng **nối với nhau thế nào**.

## 4. Vòng đơn gãy ở đâu? Ba lỗi cấu trúc

Không phải lỗi của vòng nào, mà lỗi của hình dạng "một vòng đi một mình":

1. **Goodhart** — đẩy một con số đủ mạnh thì nó thôi đo điều bạn quan tâm (vòng "đóng ticket" của Hà).
2. **Mù hướng lên** — vòng không bao giờ hỏi "mục tiêu này có đúng không?". Máy điều hòa không tự hỏi 25 độ có phải nhiệt độ hợp lý.
   Trong cấu trúc một vòng **không có chỗ nào** để câu hỏi đó được đặt ra, vì người kiểm và người làm dùng chung một đầu óc.
3. **Xung đột** — nhiều vòng dựng riêng kéo ngược chiều, mỗi cái đều "khỏe" trên bảng của nó.

Đồ thị trả lời những câu mà một vòng không trả lời được: vòng nào nuôi vòng nào? vòng nào **sở hữu mục tiêu** mà vòng khác đuổi theo?
vòng nào được quyền veto/lùi thay đổi? con số nào được phép nhúc nhích, con số nào phải đóng băng?
Và một mảnh hay bị bỏ qua: **mỏ neo (anchor)** — thứ ghim cả mạng lưới vào thực tế (doanh thu thật, bộ dữ liệu chuẩn, người kiểm mẫu ngẫu nhiên).
Không có mỏ neo, mạng lưới vòng chỉ là một đám trôi dạt cùng nhau.

## 5. Bốn cách nối nhiều việc — cùng bài toán "nghiên cứu → làm → kiểm → gộp"

**Cách 1 — Một vòng làm tất cả.** Một agent tự nhớ cần quay lại đâu.
Ưu: rẻ nhất, linh hoạt. Nhược: mọi quyết định định tuyến nằm trong đầu một agent; kẹt ở đâu cũng không ai thấy.
**Gãy ở:** khi cần song song, hoặc cần biết *vì sao* nó rẽ hướng đó.

**Cách 2 — Dây chuyền cố định (workflow).** Mã quyết định từng bước, nút là hàm chạy cố định.
Ưu: dự đoán được, dễ test, rẻ. Nhược: không thích nghi — cùng đầu vào, cùng đường đi.
**Gãy ở:** việc mở, nơi bước kế tiếp phụ thuộc điều vừa tìm thấy.

**Cách 3 — Chuỗi tuyến tính "xong A thì mở B".** Mỗi việc chỉ biết một việc nó chờ.
Ưu: đơn giản nhất, đủ cho phần lớn việc hằng ngày. Nhược: khó diễn đạt **chờ nhiều việc cùng xong** rồi mới đi; khó diễn đạt "trượt thì lùi hai bước".
**Gãy ở:** khi có ngã ba và ngã tư thật sự.

**Cách 4 — Đồ thị: nút lẫn agent, cạnh có điều kiện, trạng thái chung.**
Ưu: song song, lùi, dừng chờ người, đều khai báo rõ; chỗ nào hỏng có thể sửa **cục bộ**. Nhược: phải khai báo trước *toàn bộ* cấu trúc,
tức là bạn phải thừa nhận phần nào của quy trình chưa được mô hình hóa. Tốn công thiết kế.
**Gãy ở:** khi vẽ đồ thị rất đẹp nhưng không ai phát lại được một lần chạy hỏng (xem mục 7).

| Cách | Ai quyết đường đi | Song song | Biết "vì sao rẽ" | Chi phí thiết kế |
|---|---|---|---|---|
| 1 một vòng | agent, trong đầu | khó | không | thấp nhất |
| 2 dây chuyền | mã | có, cố định | có | thấp |
| 3 chuỗi A→B | mã (một dây phụ thuộc) | một phần | có | thấp |
| 4 đồ thị | mã **và/hoặc** luật/model | có | có (nếu ghi lại) | cao |

Câu của Luis Catacora đáng nhớ: *"Vòng cho bạn rất nhiều chỗ để tha thứ; đồ thị buộc bạn thừa nhận bao nhiêu phần quy trình của mình chưa hề được mô hình hóa."*
Vòng **hoãn** quyết định; đồ thị **ép quyết định sớm**. Vòng hợp với khám phá, đồ thị hợp với sản xuất.

**Quy luật:** *Đồ thị không phải vòng "xịn hơn". Nó là vòng được **mở hộp**: các quyết định định tuyến vốn ẩn trong đầu một agent được đưa lên giấy.*

## 6. Đồ thị khác workflow ở đâu? (đừng nhầm "đổi tên")

Nhìn bề ngoài giống hệt: nút + cạnh + trạng thái + định tuyến — các hệ như Airflow chạy kiểu này hàng chục năm. Khác ở **nút**:

- Nút workflow là **hàm cố định**; cạnh là `if/else` viết tay. Cùng đầu vào → cùng đường.
- Nút đồ thị có thể là **agent đầy đủ** (tự lặp, tự dùng công cụ); cạnh có thể do kết quả nút trước hoặc một model quyết.

Phép thử của Anthropic: **ai quyết định luồng điều khiển?** Mã quyết → workflow. Model được đổi bước lúc chạy → agent.
Đồ thị là *cái hộp chứa cả hai* (cộng thêm nút "người"). Workflow là trường hợp đặc biệt hoàn toàn cố định của đồ thị.

Phản biện đáng giữ (iii.dev): **hình dạng là phần dễ và dùng một lần.** Thứ gánh tải thật sự là: phát lại được một lần chạy hỏng,
xem được đang chạy tới đâu, và chạy tiếp được sau khi sập. Vẽ đẹp mà thiếu ba thứ này thì chưa phải kỹ thuật.

## 7. Scale và "nước lạnh"

- **Nhỏ (3–5 nút, một người trông):** đồ thị gần như thừa — một danh sách việc là đủ.
- **Vừa:** vỡ ở **trạng thái chung** — hai nút ghi đè nhau, nút đọc dữ liệu cũ. Cần nơi ghi duy nhất và luật ai được ghi gì.
- **Lớn (nhiều agent song song):** vỡ ở **bạn**. Osmani: *khởi động một agent chỉ tốn một phím bấm; **đóng vòng** cho nó (kiểm lại, hòa giải với phần agent khác đã chạm) mới đắt.*
  Người đóng vòng là bạn, và chỉ có một bạn: "bạn là cái khóa toàn cục (GIL) của đàn agent". Thêm nút làm song song phần chưa bao giờ là nút cổ chai.
  Nút cổ chai là phán đoán của bạn — nó chạy tuần tự.

Hai gáo nước lạnh nữa: (a) con số "+18% chính xác, −85% chi phí nhờ đồ thị" lan truyền là số đo của một bài báo về sơ đồ ống công nghiệp, bị gắn nhầm — **đừng tin số tiếp thị**;
(b) một vòng chính là đồ thị một nút; ai tuyên bố "vòng chết rồi" hay "đồ thị chết rồi" thường chưa đọc kỹ cái nào.

**Khi nào mới đáng dùng đồ thị** (cần ≥3 trong 5): (1) việc tách được thành khối độc lập; (2) có đường rẽ/lùi cần khai báo;
(3) trạng thái trung gian đáng lưu để dừng/tiếp; (4) mỗi nút có định nghĩa "xong" kiểm được bằng máy; (5) lợi từ song song > chi phí điều phối.
"Phức tạp" không có nghĩa nhiều bước: đường ống tuyến tính 20 bước vẫn chỉ là script; 5 nút nhưng có lùi + song song + duyệt thì mới cần đồ thị.
**Quyết định không ở quy mô mà ở chỗ có rẽ nhánh và lùi hay không.**

## 8. Ví dụ thật: Seriously làm thế này (bỏ qua vẫn hiểu bài)

Mở `tools/company/dispatch.py`, đọc hàm `_dep_done` (khoảng dòng 214) và docstring đầu file; rồi `company/ORG.md`.

| Khái niệm | Trong Seriously |
|---|---|
| Nút | một file việc trong hộp thư của một bộ phận (mỗi bộ phận = một "chủ" việc) |
| Nút người | việc `needs_approval` / `kind: gate` — dispatcher bỏ qua, chờ Bi |
| Cạnh "xong thì mở" | `--after <việc>`: việc sau chỉ chạy khi file kia `status: done` |
| Cạnh lùi | `check: review` → `reject` → việc quay về `open` (đếm `reopened`, quá 2 thì dừng chờ người) |
| Thử lại | phiên chết → mở lại đúng **một** lần, lần hai thì `blocked` |
| Trạng thái chung | các file việc + `events.jsonl` + git |
| Mỏ neo | cổng pre-commit, `kit compile`, test; riêng **thẩm mỹ** không có mỏ neo bằng máy |

Những điều rút từ chính đoạn mã (mở file kiểm lại, đừng tin mình):
- `after:` đọc bằng `fm.get('after')` — **một giá trị**. Vậy "chờ A **và** B cùng xong rồi mới chạy C" (nút hợp, fan-in) không biểu diễn trực tiếp được;
  còn một việc mở ra nhiều việc sau (fan-out) thì được, bằng cách cho nhiều việc cùng `--after` nó. Mục 7 hỏi: bạn có việc nào *thật sự* cần fan-in không?
- `_dep_done` chỉ coi `status == 'done'` là xong. Hãy tự tra: khi việc đứng trước bị `blocked` thì việc sau nằm đợi mãi,
  hay có cơ chế nào báo ra? (Mình mới đọc hàm này, chưa lần theo toàn bộ đường đi — đừng coi là kết luận.)
- Tự hỏi theo mục 4: ai **sở hữu mục tiêu** mà các bộ phận đuổi theo (vd. "đủ đẹp", "đủ nhanh")? Ở đây câu trả lời chính là Bi — và Bi đã không còn chơi thử (xem bài A03).
  Đồ thị của bạn có "nút người" để chặn Goodhart ở đúng chỗ đó chưa?

Theo 5 tiêu chí mục 7: chuỗi `--after` + `review` của bạn đã đủ cho các luồng hiện tại (tuyến tính + vòng nghiệm thu). Chưa có lý do gì để đổi sang đồ thị đầy đủ — **trừ khi** xuất hiện nhu cầu fan-in thật.

## 9. Bốn nền tảng

Đồ thị là cách **tổ chức**, độc lập nền tảng. Phần thay đổi theo máy là *nơi các nút chạy*:

- **Mac / Windows:** các nút chạy như tiến trình nền; song song bị giới hạn bởi RAM, số lõi, và hạn mức gói model. Thư mục làm việc riêng cho từng nút để khỏi giẫm file nhau.
- **iOS / Android:** không phải chỗ chạy nút agent (tiến trình nền bị hệ điều hành giết); dùng làm **nút người** — màn hình duyệt, nhận thông báo "việc này cần bạn gật".
  Nghĩa là thiết kế nút người nên gọn đến mức bấm một nút trên điện thoại là xong.

## Tóm tắt một dòng

Đồ thị = nút (kể cả agent và người) + cạnh có điều kiện + trạng thái chung + luật định tuyến; nó **mở hộp** quyết định rẽ nhánh mà vòng đơn giấu trong đầu một agent,
nhưng phán đoán của bạn vẫn là nút cổ chai tuần tự.

**Giờ bạn biết thêm:** bốn bộ phận; ba lỗi cấu trúc của vòng đơn (Goodhart, mù hướng lên, xung đột) + mỏ neo; khác biệt đồ thị ↔ workflow; năm tiêu chí có cần đồ thị không; thuế điều phối.

**Bài sau (A05, đề xuất):** *khả năng phát lại và quan sát* — thứ gánh tải thật của đồ thị: ghi gì, để sau một đêm chạy hỏng bạn dựng lại được chuyện gì đã xảy ra.

**Thuật ngữ:** nút (node) · cạnh (edge) · trạng thái chung (shared state) · định tuyến (routing) · fan-out / fan-in · mỏ neo (anchor) · thuế điều phối (orchestration tax).
