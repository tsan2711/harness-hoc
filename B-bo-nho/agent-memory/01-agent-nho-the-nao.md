# 01 · Agent "nhớ" bằng cách nào — và Seriously nên nhớ kiểu gì

> Viết 2026-10-15 cho Bi. Nguồn ghi ngay sau từng ý (§9 có danh sách đầy đủ). Số liệu "đo trong repo" là đo thật
> hôm nay bằng script đọc transcript; số liệu có chữ *ước* là ước lượng, chưa đo.
> Bài đi kèm: phương án cho công ty ở `Seriously/docs/shared/memory-options.md`.

---

## 0. Vấn đề gốc: model không có trí nhớ

Mỗi lần Claude trả lời, nó chỉ thấy **những gì nằm trong ngữ cảnh lượt đó** (prompt + lịch sử phiên + file đã đọc). Hết phiên
(`/clear`, mở phiên mới) là sạch. Model không tự học từ phiên trước — trọng số không đổi khi bạn dùng nó.

Vậy "agent nhớ" luôn có nghĩa: **ai đó cất thông tin ra ngoài, rồi lần sau đưa lại vào ngữ cảnh**. Mọi hệ nhớ chỉ khác nhau
ở ba câu hỏi:

1. **Cất cái gì** — bản gốc (nguyên văn) hay bản đã tóm tắt / đã rút "fact"?
2. **Lúc nào tốn công** — lúc ghi (tóm tắt, rút fact, dựng đồ thị) hay lúc đọc (tìm, lọc, xếp hạng)?
3. **Đưa lại vào bằng cách nào** — nạp sẵn mỗi phiên, hay agent tự tìm khi cần?

Ví dụ trong repo: phiên hôm qua sửa `PlaySession.cs` vì lỗi `QaReport` trượt. Hôm nay một phiên khác chạm lại file đó. Nó
"nhớ" được chuyện hôm qua chỉ khi (a) có ai ghi lại ở đâu đó, và (b) phiên hôm nay biết đi tìm / được đưa sẵn.

---

## 1. Sáu cách "nhớ"

### 1.1 Ngữ cảnh (context window) — nhớ trong phiên

Tất cả những gì trong phiên hiện tại. Nhanh nhất, chính xác nhất, nhưng **đắt dần**: mỗi lượt đọc lại toàn bộ ngữ cảnh.
Harness v3 đo: 53 % token nằm ở phần trên mốc 100k (`harness-v3-design.md` §1). Vì thế mới có `ctxguard` 120k/180k.
Cửa sổ to (1M) không phải trí nhớ — là trí nhớ ngắn hạn đắt tiền.

### 1.2 File nạp sẵn — "ghi chú dán trên tủ lạnh"

`CLAUDE.md`, `.claude/rules/`, `MEMORY.md`. Claude Code nạp **mỗi phiên**, không cần tìm.
- Claude Code nạp `CLAUDE.md` từ thư mục hiện tại trở lên lúc mở phiên; `CLAUDE.md` thư mục con và rules có `paths:` nạp khi
  chạm file khớp. Auto memory: chỉ **200 dòng đầu hoặc 25 KB đầu** của `MEMORY.md`; các file chủ đề (`feedback_*.md`…) không nạp
  sẵn, Claude tự mở khi cần. [Claude Code docs — memory]
- Ở Seriously: memory gốc ~3,4 KB (~1k token), CLAUDE.md gốc + toàn cục ~10k token trong bữa nạp 47k.
- **Điểm yếu:** tốn token mỗi phiên dù không dùng; phình là bị cắt (200 dòng); và memory gắn theo **đường dẫn thư mục mở
  phiên** — phiên mở trong `NanoSwarm/` không đọc được memory của phiên mở ở gốc (chính MEMORY.md gốc ghi điều này).

### 1.3 File để tra — "sổ tay trên kệ"

GDD, ADR, `depts/*/knowledge/*.md`, `docs/ai/INDEX.md`. Không nạp sẵn; agent mở khi cần, bắt đầu từ INDEX.
Repo này có 38 file sổ tay (~121 KB) chỉ riêng `depts/*/knowledge`. Đây là **"điều đã chốt"**: có người chủ, có ngày, có
git. Điểm mạnh: đúng (đã qua duyệt), bền, định dạng mở. Điểm yếu: chỉ chứa thứ **ai đó nhớ ra để ghi**.

### 1.4 Tìm theo từ khoá (lexical / BM25 / grep)

Đánh chỉ mục mọi chữ; truy vấn tìm đoạn chứa đúng các chữ đó, xếp bằng BM25 (chữ hiếm + lặp nhiều → điểm cao).
- `grep` là phiên bản không chỉ mục. Claude Code chọn cách này cho code: Boris Cherny (người làm Claude Code) kể bản đầu dùng
  "RAG + vector db cục bộ" nhưng **agentic search** (để model tự grep/glob/đọc nhiều vòng) "generally works better", lại đơn
  giản hơn và không dính lỗi bảo mật / dữ liệu cũ / độ tin cậy. [X, bcherny]
- `kit recall` của Seriously = SQLite FTS5 (BM25) trên transcript + sổ tay + git log.
- **Mạnh:** tên riêng, mã lỗi, đường dẫn: `kit recall "index.lock"` → 12 kết quả đúng. **Yếu:** diễn đạt lại. Thử hôm nay:
  `"commit cuốn nhầm thay đổi của phiên khác"` → **0 kết quả**, dù tài liệu ghi "commit cuốn hunk phiên khác". Thêm: chỉ mục bỏ
  dấu nên `"thư viện nhớ"` khớp nhầm "thư viện **nhỏ**" (đo trong repo).

### 1.5 Tìm theo ý nghĩa (embedding / vector)

Một model nhỏ biến mỗi đoạn văn thành dãy số (vector) sao cho câu cùng ý nằm gần nhau. Truy vấn → vector → lấy đoạn gần nhất.
- Bắt được diễn đạt lại ("commit cuốn nhầm" ≈ "commit cuốn hunk phiên khác"). Hỏng ở chỗ ngược lại: mã lỗi, tên file, số
  — vector làm "mờ" chúng. Nên các hệ tốt dùng **lai (hybrid)**: BM25 + vector, rồi trộn thứ hạng.
- **sqlite-vec**: extension C không phụ thuộc, chạy Mac/Linux/Windows, cả mobile và WASM; hiện tìm vét cạn (brute force);
  ghép được với FTS5 thành hybrid ngay trong SQLite. [alexgarcia.xyz]
- **qmd** (Tobi Lütke): CLI cục bộ cho ghi chú markdown = FTS5 + sqlite-vec với model embedding ~300M + mở rộng truy vấn bằng
  LLM nhỏ + trộn thứ hạng (RRF) + reranker 0,6B; tải ~2 GB model GGUF lần đầu. [github tobi/qmd]
- Tốn: không tốn token Claude, nhưng tốn CPU/GPU máy lúc ghi (tính vector) và đĩa.

### 1.6 Đồ thị tri thức (knowledge graph)

Rút ra **thực thể** (file, người, hệ thống) và **quan hệ** ("PlaySession.cs —sửa bởi→ commit 785b0330 —vì→ QaReport trượt").
Hỏi "cái gì liên quan X" thì đi theo cạnh.
- **Graphiti / Zep**: đồ thị có **hai trục thời gian** — lúc sự việc đúng (`t_valid`, `t_invalid`) và lúc hệ ghi nhận
  (`t'_created`, `t'_expired`). Cạnh mới mâu thuẫn cạnh cũ → hệ dùng **LLM** so sánh và đánh dấu cạnh cũ hết hiệu lực, không
  xoá — giữ lịch sử. [arXiv 2501.13956]
- Mạnh nhất ở câu hỏi "trước đây đúng, giờ còn đúng không". Đắt: mỗi lần ghi gọi LLM rút thực thể + kiểm mâu thuẫn.

### 1.7 Để LLM tóm tắt lúc ghi

Sau mỗi đoạn hội thoại / mỗi lệnh, gọi LLM viết lại thành "fact" ngắn rồi cất fact (thường kèm vector).
- **mem0**: mỗi cặp tin nhắn + tóm tắt hội thoại → LLM rút fact ứng viên → tìm fact tương tự đã có → LLM chọn
  **ADD / UPDATE / DELETE / NOOP**. Bài báo nói so với nạp cả lịch sử thì p95 trễ thấp hơn 91 %, token thấp hơn > 90 %.
  [arXiv 2504.19413] (Lưu ý: "rẻ hơn" là so với nhét cả lịch sử vào ngữ cảnh, không phải so với "không tóm tắt".)
- **claude-mem** (plugin Claude Code): 5 hook (SessionStart, UserPromptSubmit, PostToolUse, Stop, SessionEnd) bắt mọi lần
  dùng tool, gọi Claude qua Agent SDK nén mỗi kết quả tool (1k–10k token) thành ~500 token "quan sát", cất SQLite + Chroma
  (vector); cũ thì nén thêm. [augmentcode, datacamp]
- **Letta (MemGPT)**: ba tầng — *core memory* (khối chữ dán sẵn trong prompt, agent tự sửa bằng tool `memory_replace`…),
  *archival* (vector db, agent tự tìm), *recall* (toàn bộ lịch sử). Bản mới có **sleep-time agent**: agent thứ hai chạy nền,
  chuyên sửa trí nhớ cho agent chính. [letta.com]

---

## 2. Zero-Mem là gì (đã đọc bài gốc arXiv 2607.29377)

**"Zero-Mem: Zero-Token Memory Operations for LLM Agents"** — Xiao và cộng sự, nộp 31/07/2026. [arXiv]

Ý chính: **không bước nào ngoài bước trả lời cuối được gọi LLM hay tiêu token LLM**.
- **Cất bản gốc** (trace tương tác nguyên văn) làm nguồn sự thật — không tóm tắt.
- Tổ chức hai cách song song:
  - **đồ thị thực thể–ngữ cảnh**: thực thể rút bằng NER **không sinh** (ví dụ spaCy) — model nhỏ gắn nhãn tên riêng, không phải LLM;
  - **phân tầng thời gian**: lượt → cửa sổ ngắn → *episode* (đoạn cùng một chuyện, có ranh giới phiên/thời gian) → vùng lân cận.
- Chỉ mục: **BM25 + embedding dày (BGE-M3)**. → **Zero-Mem CÓ dùng vector.** "Zero-token" = không tốn token LLM, không phải
  "không vector". Đây là chỗ thiết kế hiện tại của Seriously hiểu hụt (xem §6).
- Lúc đọc: cân hai góc nhìn, lấy từ cả hai, đi theo cấu trúc để kéo thêm quan hệ / ngữ cảnh quanh đó; **hiệu chỉnh tất định**
  (không LLM): bỏ bằng chứng sai nguồn / ngoài phạm vi câu hỏi, xếp theo chủ thể, thời gian, kiểu câu trả lời; sau khi LLM trả
  lời thì cắt câu trả lời về đúng phần có bằng chứng.
- Kết quả: LoCoMo (hội thoại nhiều phiên) F1 66,65 so với 57,75 của bản tốt kế tiếp (GAM); HotpotQA F1 72,07 (GPT-4o-mini).
  Chi phí thao tác nhớ: Zero-Mem 0 token, 0,22 s/câu; LightMem 569k token, 0,51 s; GAM 18,55 triệu token, 6 s.
  Giảm 57,6 % thời gian so với baseline nhanh nhất.
- Giới hạn (tự suy, bài không có mục giới hạn): benchmark là **hỏi–đáp trên hội thoại**, không phải agent code; vẫn tốn máy
  chạy encoder; code "sau peer review". Có bản cộng đồng: `ptaranat/zeromem` (Rust), `woolcoxm/zero-mem-pi`.

---

## 3. Đánh đổi — bảng so

| Cách | Tốn lúc ghi | Tốn lúc đọc | Thông tin **cũ** | Thông tin **sai** | Model mạnh lên thì |
|---|---|---|---|---|---|
| Ngữ cảnh | 0 | rất đắt, mỗi lượt | không cũ | không | cửa sổ to hơn nhưng vẫn trả tiền mỗi lượt |
| File nạp sẵn | người/agent viết tay | mỗi phiên, dù không cần | **cao** nếu không ai sửa | thấp (đã duyệt) | ít cần nhắc → nên **cắt bớt** (là "nạng") |
| Sổ tay để tra | viết tay | chỉ khi mở | trung bình (có git, có chủ) | thấp | **giữ** — là sự thật đã chốt |
| BM25 / grep | 0 token, rẻ máy | 1 lệnh, ~1,5k token | không lọc (trả cả cũ lẫn mới) | không bịa (nguyên văn) | model tự grep giỏi hơn → **càng hợp** |
| Vector | 0 token, tốn máy + đĩa | 1 lệnh | như trên | không bịa, nhưng có thể "gần nghĩa mà sai" | vẫn có ích cho diễn đạt lại |
| Đồ thị | LLM rút thực thể (Zep) hoặc NER (Zero-Mem) | đi đồ thị | **tốt nhất** nếu có trục thời gian | rút sai = cạnh sai, khó thấy | rút tốt hơn; nhưng cái giá LLM-lúc-ghi vẫn còn |
| LLM tóm tắt lúc ghi | **mỗi lần ghi 1+ lượt LLM** | rẻ (fact ngắn) | fact cũ nếu UPDATE trượt | **tóm tắt = diễn giải lại**; mất chi tiết vĩnh viễn | tóm tắt cũ do model yếu viết vẫn nằm đó → **nợ** |

Hai nguyên tắc rút ra:
1. **Giữ bản gốc, đừng chỉ giữ bản tóm tắt.** Tóm tắt có thể làm lại bằng model tốt hơn; bản gốc mất thì mất. Đây là lý do
   Zero-Mem và Claude Code (grep trên file thật) đều nghiêng về "giữ nguyên văn, tìm cho giỏi".
2. **Tốn lúc đọc tốt hơn tốn lúc ghi** khi phần lớn thứ được ghi không bao giờ được đọc lại. Trong repo: 543 transcript /
   14 ngày; số lần tra lại chuyện cũ lúc đó rất thấp (§6) — *cập nhật 10-19: `recall_inject` tự chèn gợi ý khi nhận việc, đo 63 %*. Tóm tắt cả 543 bằng LLM là trả tiền cho thứ
   không ai đọc.

---

## 4. Các công cụ code agent thật sự nhớ thế nào

| Công cụ | Cách nhớ | Nguồn |
|---|---|---|
| **Claude Code** | `CLAUDE.md` (người viết) + auto memory `MEMORY.md` (Claude viết, nạp 200 dòng/25 KB đầu) + rules theo `paths:`. **Không** có chỉ mục vector; tìm code bằng grep/glob/đọc. | Claude Code docs; X bcherny |
| **Cursor** | Rules (`.cursor/rules/*.mdc`, nạp luôn / theo glob / theo mô tả / khi @). Tính năng **Memories đã bị gỡ từ 2.1** (cuối 2025), người dùng được bảo xuất memories sang Rules. | forum.cursor.com; cursor.com/docs |
| **Devin** | **Knowledge**: mỗi mục có *trigger* mô tả khi nào dùng; Devin tự kéo vào khi việc khớp trigger (theo nghĩa, không theo từ khoá); tự **đề xuất** mục mới từ phản hồi trong chat, người duyệt; tự đọc `CLAUDE.md`/`AGENTS.md`/`.cursorrules`. | docs.devin.ai |
| **claude-mem** | hook + LLM nén mỗi kết quả tool + vector (Chroma). | §1.7 |
| **Letta** | agent tự sửa khối nhớ; sleep-time agent chạy nền. | §1.7 |

Điều đáng chú ý: **hai công cụ code lớn nhất đều đi về "file người duyệt + agent tự tìm"**; Cursor còn *gỡ* trí nhớ tự sinh.
Hệ "LLM tự rút fact" mạnh ở chatbot nhớ người dùng (sở thích, tên, lịch), nơi không có git.

---

## 5. Áp vào Seriously: hiện có gì

| Lớp (giả thuyết phiên trước) | Thứ đang chạy | Nhận xét |
|---|---|---|
| Chuyện đã xảy ra | `kit recall` = FTS5 trên transcript 60 ngày + sổ tay + git log 180 ngày, 0 token, `company/state/recall.sqlite` 16 MB | chạy được; lúc đầu ít ai gọi; nay có recall-inject (63 %) |
| Điều đã chốt | GDD, ADR, `depts/*/knowledge`, `docs/ai/INDEX.md` | đã có, đã có lint ngân sách |
| Về Bi | Claude Code auto memory (`MEMORY.md` 17 dòng) + `~/.claude/CLAUDE.md` | gắn theo thư mục mở phiên; phiên game không thấy memory gốc |

## 6. Ba phát hiện khi đo (2026-10-15)

1. **(Lúc viết) không ai dùng recall — nay đã có recall-inject 63 %.** 14 ngày, 543 transcript của repo: lệnh `kit recall` thật chỉ xuất hiện trong ~6 phiên — đều là phiên
   **dựng/kiểm** recall. Phiên làm việc thường: 0. Thiết kế §5.7 hứa `leftover.py` gợi ý recall — chưa làm.
2. **Zero-Mem bị hiểu hụt.** Bài gốc dùng BM25 + vector + NER + phân tầng thời gian. Seriously chỉ lấy BM25 và nói "Zero-Mem".
3. **Tín hiệu "trượt ≥ 30 % thì làm vector" không thể bật**, vì không có gì đo trượt. Thử tay: 3/5 truy vấn kiểu từ khoá trúng,
   2/5 truy vấn diễn đạt lại trượt hoặc khớp nhầm.

→ Vấn đề lớn nhất **không phải** chọn thư viện, mà là: (a) agent không được nhắc / đưa sẵn trí nhớ đúng lúc, (b) không đo.

---

## 7. Bốn nền tảng (Windows · Mac · iOS · Android)

Bộ nhớ agent không phụ thuộc nền tảng chạy game, nhưng *công cụ* thì có:

| | Mac (máy Bi, M2) | Windows | iOS | Android |
|---|---|---|---|---|
| Claude Code memory ở đâu | `~/.claude/projects/<đường-dẫn>/memory/` | `%USERPROFILE%\.claude\projects\...` | không có Claude Code; app Claude có memory riêng phía server | như iOS |
| SQLite FTS5 | có sẵn trong Python | có sẵn | có (SQLite hệ thống) | có |
| sqlite-vec | chạy (brute force, C) | chạy | chạy (tác giả nói chạy cả mobile) | chạy |
| Model embedding cục bộ | Metal (llama.cpp / MLX) nhanh | CUDA nếu có GPU NVIDIA, không thì CPU | Core ML | LiteRT / NNAPI |
| Ý nghĩa cho game | — | — | NPC "nhớ" người chơi trên máy: FTS5 + vector nhỏ là đủ, không cần gọi LLM | như iOS |

Chỗ giống: SQLite + FTS5 + sqlite-vec là bộ **chạy mọi nơi** — cùng một file `.sqlite` mang qua 4 nền tảng.
Chỗ khác: tính embedding nhanh hay chậm tuỳ có GPU/NPU; trên mobile nên dùng model embedding nhỏ (vài chục–vài trăm MB).

---

## 8. Tự kiểm tra

1. Vì sao "Zero-Mem tốn 0 token" mà vẫn dùng vector? → Token = token **LLM**. Embedding chạy bằng model encoder cục bộ, tính
   bằng máy, không tính tiền token.
2. mem0 nói "tiết kiệm > 90 % token". So với cái gì? → So với nhét toàn bộ lịch sử vào ngữ cảnh. So với Zero-Mem (0 token lúc
   ghi), mem0 đắt hơn.
3. Truy vấn `"CS0246 PlaySession"` nên dùng BM25 hay vector? → BM25: mã lỗi, tên file là chữ chính xác.
4. Vì sao Cursor gỡ Memories mà vẫn giữ Rules? → (suy luận) Rules có người viết, có git, sửa được; memory tự sinh khó kiểm,
   dễ cũ. Cùng lý do Seriously để "điều đã chốt" ở sổ tay có chủ.
5. Một fact trong MEMORY.md viết lúc 10-01 nói "Thousandfold dùng X"; 10-12 đã đổi sang Y. Cách nào phát hiện? → So ngày sửa
   (git) của fact với ngày sửa của file/sổ tay nó nói tới — nếu file đổi sau thì gắn nhãn "có thể cũ". Graphiti làm việc này bằng
   `t_invalid`; Seriously làm được bằng git, 0 token.

## 9. Lab (15 phút, ở gốc repo)

```sh
sh tools/claude/kit.sh recall "index.lock"                                # từ khoá: trúng
sh tools/claude/kit.sh recall "commit cuốn nhầm thay đổi của phiên khác"  # diễn đạt lại: trượt
sh tools/claude/kit.sh recall "cuốn hunk"                                 # đúng chữ trong tài liệu: trúng
sh tools/claude/kit.sh recall "thư viện nhớ"                              # bỏ dấu: khớp nhầm "nhỏ"
```
Tự đặt 5 câu hỏi bạn biết đáp án ("vì sao bỏ mem0", "commit nào thêm ctxguard"…), ghi xem kết quả đúng nằm trong 12 dòng
không. Đó chính là cách đo "nhớ đúng" ở `memory-options.md`.

## 10. Thuật ngữ

| Từ | Nghĩa |
|---|---|
| Ngữ cảnh (context) | mọi chữ model thấy trong một lượt |
| BM25 / FTS5 | xếp hạng theo từ khoá / chỉ mục toàn văn của SQLite |
| Embedding / vector | dãy số biểu diễn ý của đoạn văn; câu cùng ý → vector gần nhau |
| Hybrid + RRF | chạy cả từ khoá lẫn vector, trộn thứ hạng (Reciprocal Rank Fusion) |
| Reranker | model nhỏ chấm lại top-N kết quả cho chuẩn hơn |
| NER | nhận diện thực thể (tên riêng, file, mã) bằng model nhỏ, không sinh chữ |
| Episode | một "chuyện" liền mạch (Zero-Mem); ở Seriously gần nhất là **một việc trong hộp thư** |
| Bi-temporal | hai trục thời gian: lúc sự việc đúng / lúc hệ ghi nhận |
| Recall@k | câu trả lời đúng có nằm trong k kết quả đầu không |

## 11. Nguồn

- Zero-Mem: https://arxiv.org/abs/2607.29377 · bản HTML https://arxiv.org/html/2607.29377v1 · cộng đồng
  https://github.com/ptaranat/zeromem · https://github.com/woolcoxm/zero-mem-pi
- mem0: https://arxiv.org/abs/2504.19413
- Zep / Graphiti: https://arxiv.org/abs/2501.13956 · https://help.getzep.com/graphiti/getting-started/overview
- Letta: https://www.letta.com/blog/agent-memory/ · https://www.letta.com/blog/sleep-time-compute/
- claude-mem: https://www.augmentcode.com/learn/claude-mem-persistent-memory-claude-code ·
  https://www.datacamp.com/tutorial/claude-mem-guide · https://github.com/thedotmack/claude-mem
- qmd: https://github.com/tobi/qmd
- sqlite-vec: https://alexgarcia.xyz/blog/2024/sqlite-vec-stable-release/index.html ·
  https://alexgarcia.xyz/blog/2024/sqlite-vec-hybrid-search/index.html
- Claude Code memory: https://code.claude.com/docs/en/memory · agentic search: https://x.com/bcherny/status/2017824286489383315
- Cursor: https://forum.cursor.com/t/custom-modes-and-memories-gone-in-2-1/143744 · https://cursor.com/docs/context/rules
- Devin: https://docs.devin.ai/product-guides/knowledge (bản mirror https://cognitionai.mintlify.app/product-guides/knowledge)
