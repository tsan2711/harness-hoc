# Bài D02 — Bốn lớp hay bị gộp làm một: context, transcript, tóm tắt nén, memory

> **Bạn đã biết** (A02, A02d, D01): ngữ cảnh (context) là "tờ giấy" model đọc mỗi lượt và có giới hạn; khi gần đầy thì nén (compaction); cổng gắn vào agent qua bốn mối nối, trong đó nhật ký phiên (transcript) là mối nối nguy hiểm nhất.
> Bài này trả lời một câu: **"transcript là context của phiên, đúng không?"** Gần đúng, nhưng sai ở chỗ quyết định mọi thứ phía sau.

## 1. Câu chuyện
Mai dùng trợ lý AI cả buổi sáng; cuộc trò chuyện dài, trợ lý "nén" hai lần. Chiều Mai hỏi: "sáng nay mình đã quyết gì về cách đặt tên?" Trợ lý trả lời sai, vì bản tóm tắt nén đã bỏ chi tiết đó. Nhưng file nhật ký của buổi sáng vẫn nằm trên đĩa, đủ từng chữ. Câu trả lời đúng **có tồn tại**, chỉ là không nằm ở nơi trợ lý đang nhìn.

## 2. Dừng 30 giây
- Có thứ model **đang đọc** lúc này, và thứ **đã xảy ra** trong cả phiên. Hai thứ đó có bằng nhau không, và khi nào hết bằng nhau?
- Bạn muốn trợ lý nhớ "luôn đặt tên theo kiểu X" sang phiên **tuần sau**. Thứ nào trong hai thứ trên giúp được? Nếu không, cần thứ thứ ba nào?
- Cái dùng để **đo** "phiên đã dài bao nhiêu" nên lấy từ đâu?

## 3. Bốn lớp
```
 ┌──────────────────────────────────────────────────────────────────┐
 │ memory dài hạn   (kho riêng, sống qua nhiều phiên)               │ ④
 └──────────────▲───────────────────────────────┬───────────────────┘
        học từ ─┘                               │ đưa vào lúc bắt đầu
 ┌──────────────┴───────────────────────────────▼───────────────────┐
 │ transcript = bản ghi ĐẦY ĐỦ mọi việc đã xảy ra (chỉ thêm cuối)   │ ②
 └──────────────┬───────────────────────────────────────────────────┘
                │ dựng lại (replay) / rút gọn (nén)
 ┌──────────────▼──────────────┐      ┌──────────────────────────┐
 │ context = thứ model thấy    │◄─────│ tóm tắt nén (thay phần   │ ③
 │ ở lần gọi này               │      │ cũ khi gần đầy)          │
 └─────────────────────────────┘      └──────────────────────────┘
   ①
```

| Lớp | Câu hỏi nó trả lời | Lớn lên thế nào | Mất gì thì sao |
|---|---|---|---|
| ① Context | model thấy gì **bây giờ**? | tăng, rồi bị nén về nhỏ | model "quên"; việc vẫn tiếp tục |
| ② Transcript | **đã xảy ra** gì? | chỉ tăng, không bao giờ bớt | mất khả năng truy vết, replay |
| ③ Tóm tắt nén | phần cũ **đại ý** là gì? | mỗi lần nén thay một khúc | chi tiết cũ chỉ còn trong ② |
| ④ Memory | **bài học** nào đáng mang sang phiên sau? | do một quy trình riêng quyết | phiên sau bắt đầu từ trắng |

Cách đọc: ① là "bộ nhớ làm việc", ② là "sổ nhật ký", ③ là "bản ghi nhớ rút gọn", ④ là "kiến thức đã học". ② là nguồn của ③ và ④, nên **ai đọc ② thì phụ thuộc định dạng của ②**.

## 4. Số đo: ① và ② khác nhau thế nào (một phiên Claude thật, 115 lần gọi model)
Mỗi lần model được gọi, nhật ký ghi `usage` với ba số:

```
input_tokens (mới)   cache_creation (ghi cache)   cache_read (đọc cache)
        2                    24 179                     26 574      →  ① = 50 755 token
        4                     1 488                    167 840      →  ① = 169 332 token
```
- **Context của lần gọi = cộng ba số.** Cache chỉ là cách tính tiền rẻ hơn, không làm tờ giấy ngắn đi.
- Từ 50 755 lên 169 332 sau 115 lần gọi: ① tăng đều rồi sẽ bị nén. Nhưng file ② của cùng phiên có 573 dòng và chỉ tăng.
- **Bẫy đếm đôi:** một câu trả lời của model có nhiều khối nội dung (chữ, nhiều lần gọi tool) nên **cùng một `usage` bị lặp trên nhiều dòng**. Đếm theo dòng sẽ nhân đôi, nhân ba. Phải gộp theo mã của câu trả lời (`message.id`).

Đối chiếu với Codex (nhật ký thật, cùng loại số): `input_tokens` = 18 220 đã **gồm** `cached_input_tokens` = 6 528. Cộng cache thêm như công thức Claude là đếm đôi. Cùng chữ "input", nghĩa khác nhau; đó là lý do định dạng của ② là mối nối nguy hiểm.

## 5. Bốn cách một hệ agent tổ chức ②
| Cách | Mô tả | Ưu | Nhược / điểm gãy |
|---|---|---|---|
| **A. File JSONL cho người ngoài đọc** (Claude Code) | mỗi dòng một sự kiện, đường dẫn đưa cho hook | công cụ ngoài đọc được ngay (distill, recall…) | định dạng riêng của hãng; đổi phiên bản là gãy; to dần |
| **B. Nhật ký sự kiện + trạng thái suy ra** (dsh) | ② là nguồn sự thật; ① là **phép chiếu** từ ②; mỗi request kiểm "bản chiếu khớp bản ghi" | replay, fork, resume, kiểm thử chạy cùng một dòng; kiểm tra tính nhất quán | file nén, hook ngoài không đọc được (`transcript_path` rỗng) |
| **C. SQLite / cơ sở dữ liệu** (Codewhale lưu thread, `session-query` của dsh) | truy vấn được theo thời gian, tìm toàn văn | tìm nhanh, lọc, quan hệ | khó đọc bằng mắt; cần schema và migrate |
| **D. Không giữ ②, chỉ giữ ③** | chỉ lưu bản tóm tắt | nhỏ | mất khả năng truy vết, không dựng lại được |

Quy luật: *càng nhiều quy trình khác (memory, đo, kiểm thử) cần đọc ②, càng nên có giao diện ổn định cho nó (truy vấn hoặc định dạng công khai), thay vì để mỗi nơi tự phân tích file.*

## 6. Memory (④) có hai cách sinh, khác nhau về phụ thuộc
| Cách sinh | Ví dụ | Phụ thuộc ② | Hệ quả khi đổi agent |
|---|---|---|---|
| **Model tự gọi tool để ghi/đọc** | máy chủ memory qua MCP (Engram, Memorix…) | **không** — là tool độc lập | agent nào cũng gọi được |
| **Pipeline rút từ transcript** | chia phiên thành cửa sổ → LLM tóm → trích "claim" → lập chỉ mục tìm kiếm | **có** — đọc thẳng ② | mỗi định dạng ② mới cần bộ đọc mới |

Cách 1 gọn nhưng bị động: model phải nhớ để ghi. Cách 2 chủ động và bao quát hơn (học cả những gì model không nghĩ tới), nhưng bị khoá vào định dạng ②. Hai cách không loại trừ nhau.

## 7. Scale
| Cỡ | Cái gì vỡ |
|---|---|
| Phiên ngắn | ① ≈ ②, không thấy khác biệt |
| Phiên dài (hàng trăm lượt) | ① bị nén, ② còn nguyên → câu hỏi "sáng nay quyết gì" chỉ trả lời được từ ② |
| Hàng nghìn phiên | ② thành kho dữ liệu lớn: cần chỉ mục (C), chính sách giữ/xoá (nhật ký có thể chứa bí mật), và ④ để khỏi đọc lại tất cả |
| Nhiều agent khác định dạng | mỗi bộ đọc ② phải thêm một lần; chi phí tuyến tính theo số định dạng × số nơi đọc |

## 8. Ví dụ thật: Seriously làm thế này (và vì sao migrate phức tạp)
- **① đo từ ②:** `tools/claude/ctxguard.py` gọi `transcript.last_context()` lấy `usage` cuối, cộng ba số; ngưỡng nhắc/chặn trong `company/models.toml` `[context]`: `soft = 180000`, `hard = 240000`, tự nén ở `compact = 260000`.
- **③ có điểm móc:** hook `PreCompact` (`leftover.py compact`) lưu tờ bàn giao *trước khi* nén, để chi tiết không chỉ còn trong ②.
- **④ kiểu rút từ ②:** `distill.py` → claims → `recall.py`, `doc2query.py`, `memhub.py` đọc JSONL Claude trực tiếp. Đây là lý do **15 file** đọc thô định dạng ②, và là lý do nhóm này nên để Claude-only khi thêm Codex.
- **Kiểm chứng tại chỗ:** hàm `request()` trong `tools/claude/transcript.py` trả về mã câu trả lời (`id`) cùng `ctx`. Viết vài dòng Python lấy một file JSONL của bạn, cộng `ctx` theo từng dòng rồi theo từng `id` duy nhất; hai tổng chênh bao nhiêu lần?
- **Vì sao dsh bỏ trống `transcript_path`:** ④ của họ là tool MCP (cách 1), ① là phép chiếu từ ② (cách B), nên chẳng quy trình ngoài nào cần đọc file ②. Của bạn thì cần.

## 9. Bốn nền tảng
- **Mac / Windows / Linux:** vị trí và định dạng ② do agent quyết (`~/.claude/projects/…`, `~/.codex/sessions/Y/M/D/…`); trên Windows là `%USERPROFILE%\…`, cần chuẩn hoá đường dẫn khi đọc.
- **iOS / Android:** agent coding không chạy trên điện thoại. Điểm chung duy nhất: *app game của bạn* cũng có ① (trạng thái đang chạy), ② (log) và ④ (save). Cùng tư duy: log chỉ thêm cuối cho truy vết, trạng thái hiện tại là bản chiếu.

## Tóm tắt
Context là **thứ model đang đọc**, transcript là **thứ đã xảy ra**; nén thu hẹp cái trước, không đụng cái sau. Memory dài hạn hoặc là tool độc lập (không phụ thuộc transcript), hoặc là pipeline rút từ transcript (phụ thuộc định dạng). Harness của bạn chọn cách sau, nên định dạng transcript là chi phí migrate lớn nhất.

**Giờ bạn biết thêm:** phép chiếu (projection), nhật ký chỉ thêm cuối (append-only log), event sourcing, đếm đôi `usage`, hai cách sinh memory.

**Bài sau (D03):** ma trận hỗ trợ cổng × agent — cách biết một cổng "đang sống" trên từng agent.

### Thuật ngữ
- **Context / ngữ cảnh**: toàn bộ chữ model nhận ở một lần gọi.
- **Transcript**: bản ghi đầy đủ phiên, chỉ thêm cuối.
- **Compaction / nén**: thay phần lịch sử cũ bằng bản tóm tắt.
- **Projection / phép chiếu**: trạng thái dựng lại từ nhật ký.
- **Event sourcing**: lưu chuỗi sự kiện làm nguồn sự thật, trạng thái suy ra.
- **MCP**: giao thức cho agent gọi công cụ bên ngoài, ở đây là kho memory.
