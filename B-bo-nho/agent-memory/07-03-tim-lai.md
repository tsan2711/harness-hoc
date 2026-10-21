# 07-03 — Tìm lại

> Chuỗi 07, bài 3/12. Đọc ~10 phút.
> **Bạn đã biết:** model không nhớ, ngữ cảnh nhỏ và đắt ([07-01](07-01-model-khong-nho.md)); kiến thức nằm ở file text trong git,
> chỉ mục là cache dựng lại được ([07-02](07-02-ghi-ra-ngoai.md)).

## 1. Chuyện mở đầu

Sau một năm, kho Quán Nhỏ có 400 file ghi chú, mỗi file trung bình 1 000 token. Agent cần trả lời "vì sao không dùng ChartLite?".
Câu trả lời nằm trong *một đoạn ba dòng* của *một* file. Làm sao lấy đúng ba dòng đó lên mặt bàn, mà không bê cả tủ lên?

## 2. Dừng 30 giây

- 400 file × 1 000 token = 400 000 token. Đổ hết vào ngữ cảnh thì sao?
- Tìm đúng chữ "ChartLite" ra 37 chỗ. Chỗ nào nên đọc trước?
- Hỏi "sao biểu đồ bị giật?" — không có chữ "ChartLite" nào trong câu. Tìm bằng chữ thì ra gì?

## 3. Bốn bước tiến, mỗi bước vá chỗ gãy của bước trước

**Bước 1 — Đọc hết.** Đổ cả kho vào ngữ cảnh. Câu hỏi 1: 400k token vượt sức chứa của nhiều model, và kể cả vừa thì mỗi câu hỏi tốn
tiền cho 400k token, chậm, và model bỏ sót chi tiết ở giữa. Chỉ dùng được khi kho còn bé.

**Bước 2 — Tìm đúng chữ (grep).** Quét mọi file, lấy dòng có chữ "ChartLite". Rẻ, chính xác. Hai chỗ gãy:
- **Quá nhiều kết quả, không thứ tự** (câu hỏi 2): 37 chỗ, trong đó 30 chỗ chỉ là "import ChartLite" trong code cũ.
- **Phải quét lại toàn bộ kho mỗi lần.** Kho to thì chậm.

**Bước 3 — Chỉ mục ngược (inverted index).** Giống mục lục cuối sách: không phải "trang 5 có những chữ gì", mà ngược lại — "chữ
*ChartLite* có ở trang 5, 17, 203". Lập một lần (đó chính là cache ở bài 07-02), sau đó tìm một chữ chỉ là tra một dòng, không quét kho.

Để chỉ mục hữu ích, trước hết **cắt văn bản thành đoạn** (chunk — vài câu đến một mục). Lý do: trả về cả file 1 000 token thì lại
bê tủ lên bàn; trả về đúng đoạn 3 dòng thì vừa mặt bàn.

**Bước 4 — Chấm điểm để xếp thứ tự.** Có chỉ mục rồi, câu hỏi còn lại: trong các đoạn khớp, đoạn nào lên đầu? Ba ý thường thức:
1. **Chữ hiếm đáng giá hơn chữ phổ biến.** Đoạn khớp "ChartLite" (có ở 37/20 000 đoạn) đáng hơn đoạn khớp "biểu đồ" (có ở 2 000
   đoạn). Chữ có mặt khắp nơi như "là", "của" gần như không nói gì.
2. **Lặp nhiều thì liên quan hơn — nhưng có trần.** Đoạn nhắc "ChartLite" 3 lần liên quan hơn đoạn nhắc 1 lần; nhắc 30 lần không hơn
   bao nhiêu so với 5 lần.
3. **Đoạn ngắn khớp thì đậm đặc hơn đoạn dài khớp.** Một chữ trong đoạn 3 dòng có nghĩa hơn cùng chữ trong đoạn 3 trang.

Công thức gói ba ý này tên là **BM25** — gần như mọi ô tìm kiếm bạn từng dùng đều dựa trên nó. Muốn xem toán: [05a](05a-bm25-va-fts5.md).

## 4. Những chỉnh nhỏ mà quan trọng

- **Bỏ dấu khi so** (tiếng Việt): người gõ "bieu do" vẫn phải ra "biểu đồ". Nhưng giữ thêm một bản có dấu để "cá" không lẫn "cả".
- **Câu hỏi nhiều chữ:** đòi đoạn có *tất cả* các chữ (AND) trước; không ra gì thì nới thành *bất kỳ* chữ nào (OR).
- **Đồng nghĩa viết tay:** "giật", "lag", "chậm" là một nhóm. Rẻ, nhưng chỉ vá được những cặp bạn nghĩ ra.

Câu hỏi 3 lộ **giới hạn gốc** của tìm theo chữ: "sao biểu đồ bị giật?" không có chữ nào trùng với ghi chú "bỏ ChartLite vì *lag* trên
Android đời cũ" (trừ khi có nhóm đồng nghĩa). Đây là bài toán **diễn đạt lại**. Cách vá là tìm theo *nghĩa* — biến mỗi đoạn thành một
dãy số (vector) sao cho câu cùng ý nằm gần nhau ([05b](05b-embedding-va-vector.md)). Chuỗi này để vector làm phần thí nghiệm ở bài
07-10; trước hết phải làm tốt phần chữ.

## 5. Bảng một lần nhìn

| | Câu "vì sao bỏ ChartLite" | Câu "sao biểu đồ giật" | Tốc độ ở 20 000 đoạn | Gãy khi |
|---|---|---|---|---|
| 1. Đọc hết | ✓ (nếu vừa) | ✓ (nếu vừa) | rất chậm, rất đắt | kho to hơn ngữ cảnh |
| 2. Grep | 37 chỗ, không thứ tự | ✗ | chậm dần theo kho | nhiều kết quả, diễn đạt lại |
| 3. Chỉ mục ngược | 37 chỗ, nhanh | ✗ | mili-giây | vẫn chưa có thứ tự |
| 4. Chỉ mục + BM25 | đoạn đúng lên đầu | ✗ (trừ khi có đồng nghĩa) | mili-giây | diễn đạt lại |

**Quy luật:** đừng bê tủ lên bàn — cắt thành đoạn, lập mục lục ngược, chấm điểm để chỉ vài đoạn tốt nhất lên bàn. Chữ hiếm là tín hiệu
mạnh nhất; tìm theo chữ thì mù với cách nói khác.

## 6. Scale

- **Nhỏ** (vài trăm đoạn): grep là đủ, có khi đọc hết cũng được.
- **Vừa** (chục nghìn đoạn): BM25 vẫn mili-giây. Cái vỡ là **thứ tự**: nhiều đoạn cùng chủ đề (bản cũ, bản mới, câu nói vu vơ) chen
  nhau vào top. Bài 07-05 và 07-07 lo chuyện này.
- **Lớn** (triệu đoạn): vẫn nhanh (máy tìm kiếm web chạy trên nguyên lý này), nhưng tỉ lệ "đúng chữ sai ý" tăng → cần thêm tín hiệu
  ngoài chữ.

## 7. Bốn nền tảng

BM25 có sẵn trong **SQLite** (phần FTS5) — thư viện cơ sở dữ liệu có mặt trên cả **Windows, Mac, iOS, Android**. Nên cùng một cách tìm
chạy được ở máy dev lẫn trong app điện thoại (ô tìm món ăn trong app Quán Nhỏ có thể dùng đúng nó, chạy không cần mạng). Khác biệt
nhỏ: cách cắt từ tiếng Việt (theo khoảng trắng) giống nhau mọi nơi; bỏ dấu thì tự làm cho chắc, đừng tin vào cài đặt ngôn ngữ của từng
máy.

## 8. Tóm tắt

Tìm lại = cắt đoạn → chỉ mục ngược → chấm điểm BM25 (chữ hiếm, lặp có trần, đoạn ngắn) → lấy vài đoạn đầu; tất cả là cache dựng lại
được; điểm yếu là câu diễn đạt lại.

**Thuật ngữ:** chunk (đoạn) · grep · inverted index (chỉ mục ngược) · BM25 · IDF (độ hiếm) · AND / OR · synonym (đồng nghĩa) · paraphrase (diễn đạt lại).

**Giờ bạn biết thêm:** làm sao lấy đúng vài đoạn trong cả kho, nhanh, rẻ, tất định — và chỗ nó mù.

---

> **Ví dụ thật: Seriously làm thế này**
>
> - Công cụ tìm của Seriously (`tools/claude/recall.py`, lệnh `kit recall "<câu>"`) dùng đúng các bước trên: SQLite FTS5 + BM25,
>   trên **20 706 đoạn** cắt từ sổ tay, tài liệu, lịch sử git và transcript.
> - Mỗi đoạn có ba "cột" chữ với trọng số khác nhau: bản bỏ dấu (×1), bản giữ dấu (×1,5), và các *thực thể* như đường dẫn file, mã lỗi
>   (×3 — vì chúng hiếm và chính xác; bài 07-11 nói kỹ).
> - Câu nhiều chữ: AND trước, không ra thì OR. Đồng nghĩa: 29 nhóm viết tay trong `company/eval/recall/synonyms.toml`.
> - Tìm mất **33–70 ms** khi chỉ mục đã sẵn.
> - Giới hạn đã đo: trên bộ câu kiểm tra, câu dùng đúng chữ trúng **20/20**, câu diễn đạt lại chỉ trúng **9/20** — đúng chỗ mù của tìm
>   theo chữ.

**Bài sau:** [07-04 — Ai bấm nút tìm](07-04-ai-bam-nut-tim.md).
