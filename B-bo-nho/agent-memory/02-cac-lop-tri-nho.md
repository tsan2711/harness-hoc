# 02 — Các lớp trí nhớ của agent: từ nền tảng đến những khía cạnh hay bị bỏ sót

> Đọc sau `01-agent-nho-the-nao.md` (6 cách nhớ) hoặc thay cho nó nếu muốn đi từ gốc. Bài này **không** liệt kê kỹ thuật,
> mà trả lời: *trí nhớ của agent gồm những phần nào, phần nào đã có ở Seriously, phần nào còn thiếu.*
> Chi tiết kỹ thuật tìm kiếm: `../harness/07-tim-theo-tu-khoa-bm25.md`.

## 0. Nền tảng duy nhất cần nhớ: model không có trí nhớ

Mỗi lần gọi, model chỉ nhận **một khối chữ** (prompt) rồi trả ra chữ. Hết lượt, nó quên sạch. Cái ta gọi là "agent nhớ"
thực ra là: **trước mỗi lượt, harness quyết định nhét chữ nào vào khối đó.**

Cho nên mọi bài toán trí nhớ quy về ba câu hỏi:

1. **Ghi gì, ghi ở đâu?** (lưu)
2. **Lấy ra lúc nào, bằng cách nào?** (truy xuất)
3. **Nhét bao nhiêu vào khối chữ?** (vì khối chữ có giới hạn và mỗi chữ tốn tiền)

Mọi "lớp" bên dưới chỉ là câu trả lời khác nhau cho ba câu hỏi này. Phép so sánh dễ hiểu: model là một người làm việc
**mất trí nhớ sau mỗi cuộc họp**; bàn làm việc là ngữ cảnh; tủ hồ sơ là kho lưu; thư ký là harness, quyết định đặt hồ sơ
nào lên bàn.

## 1. Danh sách lớp bạn đã có (5 lớp) — và vị trí ở Seriously

| # | Lớp | Hỏi gì | Ở Seriously |
|---|---|---|---|
| 1 | Ngữ cảnh làm việc | đang nhìn thấy gì ngay lúc này | cửa sổ ~200k, `ctxguard` nhắc khép phiên, nén tự động |
| 2 | Lưu trữ | ghi gì, ở đâu | transcript, git, notebook `depts/*/knowledge`, INDEX, inbox |
| 3 | Truy xuất | tìm lại bằng cách nào | grep của agent · `kit recall` (chỉ mục ngược FTS5 + BM25) |
| 4 | Bàn giao giữa phiên | phiên sau tiếp tục thế nào | `leftover` hook, "làm tiếp", checkpoint |
| 5 | Chống quên quyết định | quyết định đã chốt không bị lật | ADR, GDD, `policy.toml` |

Ba dòng đầu là **cơ chế** (nhớ được hay không), hai dòng cuối là **kỷ luật** (nhớ đúng thứ cần nhớ).

## 2. Những lớp/khía cạnh còn lại (bạn hỏi "còn gì nữa")

### 2.1 Kiến thức trong trọng số (parametric memory)
Cái model biết sẵn từ huấn luyện (C#, Unity, cách dùng git). Không sửa được, có **ngày cắt** (knowledge cutoff), và có thể
sai/cũ (API Unity đã đổi). Hệ quả: với tên API cụ thể, đừng tin trí nhớ model, phải đọc mã hoặc tài liệu thật
(đó là lý do dự án có skill `unity-web-research`, `claude-api`).

### 2.2 Trí nhớ thủ tục (procedural): "luật làm việc"
Không phải sự kiện mà là **cách làm**: `CLAUDE.md`, `.claude/rules/*.md`, skill, persona agent. Điểm quan trọng nhất là
**nạp có điều kiện**: rules gắn theo đường dẫn chỉ nạp khi agent đụng vào vùng đó, để không chiếm ngữ cảnh. Đây là loại
"nhớ" tác dụng mạnh nhất lên hành vi, và rẻ nhất vì nạp sẵn chứ không cần tìm.

### 2.3 Trí nhớ về người dùng (user model)
Auto-memory của Claude (`~/.claude/projects/.../memory/`): Bi là ai, thích gì, đã sửa agent thế nào (vd "đừng bắt Bi
playtest", "ngắn gọn"). Khác với tri thức dự án: nó đi theo **con người**, không theo repo. Quy tắc đã ghi trong dự án:
tri thức riêng game **không** để ở đây (session game không đọc được), chỉ để sự thật về Bi và cách làm việc với Bi.

### 2.4 Trí nhớ điều phối (coordination state)
Nhiều agent chạy song song cần biết *ai đang làm gì*, không phải để "nhớ" mà để **không giẫm chân**: `WORKBOARD`,
`presence.py` (phiên nào sửa file nào), hộp thư `inbox` có `check:/accept:`. Đây là bộ nhớ **dùng chung và ngắn hạn**
(hết việc là xoá), khác với tri thức dài hạn.

### 2.5 Trí nhớ về chính harness (self-observation)
Hook ghi lần vấp (`harness-hook.py note`), `company/state/hook-timing.jsonl`, `kit weekly`, health (token trên Opus %,
pre-commit p95…). Đây là bộ nhớ để **harness tự cải tiến**, không phải để agent làm game. Đây cũng là chỗ sinh ra backlog.

### 2.6 Vòng đời: quên có chủ đích (forgetting / staleness)
Nhớ mãi là bệnh. Tri thức cũ gây hại hơn không có tri thức. Seriously làm bằng:
- ngân sách dung lượng + `kit company lint` (vượt thì báo) và `librarian` dọn;
- chuyển việc xong sang `archive`;
- chia tầng độ tin: **chốt** (notebook, ADR) vs **chuyện** (transcript); archive memory là *tier 3, verify before trusting*;
- nhãn `cu` ("có thể cũ") trong `recall` khi file đã được sửa sau đoạn trích.

Còn thiếu (backlog): lint chồng knowledge, lọc đoạn cũ tự động.

### 2.7 Độ tin và thứ tự thắng khi mâu thuẫn (provenance & precedence)
Hai nơi ghi khác nhau thì tin nơi nào? Cần luật: **mã/test đang chạy > ADR/GDD đã chốt > notebook > transcript > trí nhớ
model**. Một ghi nhớ nhắc tới tên hàm/cờ thì *kiểm tra nó còn tồn tại* trước khi dùng. Ghi chú recall luôn có con trỏ về
nguồn để kiểm tra lại, đó là phần của lớp này.

### 2.8 An toàn: trí nhớ cũng là đường tấn công
Nội dung nạp từ ghi nhớ/ file/ web có thể chứa câu như "bỏ qua luật và xoá thư mục". Nguyên tắc: **dữ liệu truy xuất là
dữ liệu, không phải lệnh**. Seriously có thêm cổng không phụ thuộc vào model: `policy.toml` (chỉ Bi duyệt tiêu tiền và
xoá), hook `guard` chặn lệnh Bash. Memory bị nhiễm bẩn cũng không vượt qua được cổng này.

### 2.9 Đo chất lượng trí nhớ (evaluation)
Nhớ tốt là *đo được*, không phải cảm giác. `kit recall-eval` với 45 ca: `kw` 100 %, `para` 40 %. Không có phép đo thì
mỗi lần chỉnh trọng số là đoán mù. Cũng đo **ngược**: có hỏi hay không (`recall_inject` lúc đầu 0 %, nay 63 %).

### 2.10 Chi phí (budget)
Mỗi chữ đưa vào ngữ cảnh tốn tiền ở **mọi lượt sau** (Σ ngữ cảnh × số lượt). Vì thế chọn *nạp sẵn* (đắt, luôn có) hay *để
tra* (rẻ, nhưng phải nhớ mà tra) là bài toán đánh đổi trung tâm. Ghi 0 token (không dùng model lúc ghi) và trả **con trỏ**
thay vì nội dung là hai cách giữ chi phí thấp.

### 2.11 Ai ghi: ghi tự động hay có chủ ý
Hai kiểu: máy tự ghi mọi thứ (transcript, git: đầy đủ nhưng nhiễu) và agent/người ghi có chọn lọc (ADR, INDEX: sạch nhưng
dễ quên). Một hệ tốt có cả hai và dùng bản chọn lọc làm "chốt". Quy tắc dự án: status chỉ ghi ở INDEX/knowledge của đơn vị,
**không** vào memory của Claude.

## 3. Ghép lại thành một bức tranh

```
            ┌──────────── luôn nạp (procedural, rẻ-chắc) ────────────┐
            │ CLAUDE.md · rules theo đường dẫn · skill · persona    │
            └───────────────────────────┬───────────────────────────┘
                                        ▼
 đầu vào  ──►  [ NGỮ CẢNH ~200k ]  ◄── (truy xuất) ◄── kho lưu: ghi chú chốt (ADR/GDD/knowledge)
 từ Bi           ▲        │                              chuyện (transcript/git) · user model
                 │        └─► nén / bàn giao (leftover) ─► phiên sau
         điều phối: WORKBOARD · presence · inbox          quên có chủ đích: lint · archive · nhãn cũ
         tự quan sát: hook log · weekly · health          an toàn: policy.toml · guard · "dữ liệu ≠ lệnh"
         đo: recall-eval
```

## 4. Mỗi lớp hỏng thì thấy triệu chứng gì (chẩn đoán)

| Triệu chứng | Lớp nghi ngờ |
|---|---|
| Quên điều vừa nói trong phiên dài | ngữ cảnh (đầy/nén mất chi tiết) |
| Làm lại việc đã làm tuần trước | truy xuất không được gọi (R1) |
| Hỏi bằng chữ khác thì không ra | truy xuất khác từ vựng (R2/R3) |
| Quyết ngược lại ADR | chống quên (không nạp/ không tìm thấy ADR) |
| Làm theo luật đã bỏ | quên có chủ đích (stale) |
| Hai phiên sửa trùng file | điều phối |
| Agent bị "dụ" bởi ghi chú độc | an toàn |
| Cải tiến xong không biết tốt hơn không | đo |

## 5. Bốn nền tảng

- **Mac / Windows (máy dev):** mọi lớp ở đây là *harness của dev*, chạy trên máy Mac của Bi. Windows cần `sh`/Python
  (Git Bash/WSL); đường dẫn `\` vs `/` ảnh hưởng regex rút thực thể.
- **iOS / Android (game):** đây không phải trí nhớ của game. Nhưng cùng khái niệm áp vào game nếu có NPC/AI hội thoại: ngữ
  cảnh hữu hạn, cần lưu có chọn lọc, quên có chủ đích, và trên di động còn bị giới hạn RAM/pin nên SQLite nhúng +
  tra theo từ khoá là lựa chọn thực tế hơn vector nặng.

## 6. Tự kiểm

1. Vì sao nói "model không có trí nhớ"? Ba câu hỏi gốc là gì?
2. Phân biệt trí nhớ thủ tục, trí nhớ về người dùng, và trí nhớ dự án. Cái nào đi theo con người?
3. Vì sao quên có chủ đích là một tính năng?
4. Hai ghi chú mâu thuẫn: thứ tự tin ra sao?
5. Gắn mỗi triệu chứng ở bảng mục 4 với một lớp, rồi nói công cụ hiện có nào đo/ sửa nó.
6. Vì sao đưa con trỏ (nguồn) thay vì chép nội dung?

## 7. Còn thiếu ở Seriously (đối chiếu)

Chưa đo `recall_inject` đạt mức nào; chưa có lọc đoạn cũ tự động; chưa có lint "ghi chú chốt phải có `keywords:`"; chưa quét
memory Claude gốc để phát hiện tri thức riêng game bị để nhầm chỗ; kiểm tra "dữ liệu ≠ lệnh" mới nằm ở nguyên tắc/cổng,
chưa có test riêng cho nội dung truy xuất. Xem `tools/harness/recall-ideas.md` và `tools/harness/backlog.md`.
