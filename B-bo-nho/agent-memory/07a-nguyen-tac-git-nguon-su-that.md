# 07a — Nguyên tắc: 0 token, git là nguồn sự thật, chỉ mục dựng lại được

> Chuỗi 07 (hiểu hết [06 — kiến trúc đề xuất](06-kien-truc-de-xuat.md)), bài 1/9. Đọc ~10 phút.
> Cần trước: [05a BM25](05a-bm25-va-fts5.md).

## 1. Câu chuyện

Bi mua máy Windows mới, `git clone` Seriously, mở Claude, gõ `kit recall "vì sao bỏ RenderMeshInstanced"`.
Máy mới không có `company/state/recall.sqlite` (file 77 MB, bị `.gitignore` dòng 111 bỏ qua). Lệnh đầu tiên mất ~30 giây:
`recall.py` đọc lại sổ tay, git log, transcript và dựng 20.706 đoạn. Từ lệnh thứ hai thì mất vài chục ms. Câu trả lời giống hệt
câu trả lời trên máy Mac (trừ phần transcript, vì transcript nằm theo máy).

Giờ thử một công ty khác dùng mem0: mỗi lần agent ghi nhớ, một LLM tóm tắt câu chuyện thành "fact" rồi cất vào DB trên cloud.
Đổi máy thì không sao, nhưng hết hạn tài khoản, đổi nhà cung cấp, hay LLM tóm tắt sai một câu — kiến thức đó mất hoặc sai
vĩnh viễn, vì **không còn bản gốc để dựng lại**.

## 2. Dừng 30 giây

Tự nghĩ trong đầu, không cần trả lời:
- Nếu xoá `recall.sqlite` ngay bây giờ, Seriously mất gì?
- Vì sao "LLM tóm tắt lúc ghi" vừa tốn tiền vừa nguy hiểm, kể cả khi LLM rất giỏi?
- "Cùng đầu vào → cùng chỉ mục" có lợi gì cho việc kiểm thử?

## 3. Ba khái niệm

**Nguồn sự thật (source of truth) vs cache.** Nguồn sự thật là thứ mà nếu mất thì mất thật. Cache là thứ tính ra từ nguồn để đọc
nhanh; mất thì tính lại. Ở Seriously: nguồn = file `.md/.toml/.jsonl` trong git + transcript; cache = `recall.sqlite`,
`recall-touch.json`, sau này là vector và bảng `edges`. Câu hỏi 1: xoá sqlite thì **không mất gì**, chỉ mất 30 giây.

**Tất định (deterministic).** Cùng đầu vào → cùng kết quả, mọi lần. BM25, regex, `git log` là tất định. LLM thì không
(cùng câu, hai lần chạy có thể tóm khác nhau). Câu hỏi 3: chỉ mục tất định thì **bộ đo chạy được trong selftest** — điểm đổi
nghĩa là code đổi, không phải "hôm nay model hứng". Không tất định thì mỗi lần đo là một con xúc xắc.

**0 token lúc ghi và lúc tìm thường ngày.** Mỗi lần agent sửa một doc là một lần "ghi". Seriously có hàng chục phiên/ngày, mỗi
phiên sửa vài chục file. Nếu mỗi lần ghi gọi LLM: tiền nhân theo số lần ghi, độ trễ nhân theo số lần ghi, và lỗi tóm tắt
**cộng dồn** không ai thấy. Câu hỏi 2: kể cả LLM đúng 98 %, 2 % sai trên hàng nghìn lần ghi là hàng chục kiến thức hỏng
mà không có bản gốc để so. Ngoại lệ được phép: model **cục bộ** nhỏ (embedding, NER — chạy trên máy, không tốn token), và LLM chạy
**theo lô** có Bi duyệt tiền, kết quả commit vào git (thành nguồn, có diff, có review).

**H-10 — giao diện chuẩn.** Nguyên tắc từ `docs/shared/agent-company-v4.md` §3: dữ liệu công ty chỉ ở dạng mở
(md/toml/jsonl/sqlite trong git) và mọi script đọc transcript Claude Code qua **một adapter** (`tools/claude/transcript.py`).
Trước V4 có 5 script tự parse transcript — Claude Code đổi định dạng là gãy 5 chỗ. Giờ gãy 1 chỗ, và selftest có fixture để biết.

## 4. Bốn cách giữ trí nhớ, thử trên một dữ kiện

Dữ kiện: *"Bi bỏ CPU matrix bake + RenderMeshInstanced, dùng VFX Graph"* (ghi chú thật, 2026-10).

**Cách 1 — Chỉ trong ngữ cảnh phiên.** Agent biết khi Bi vừa nói. `/clear` là mất.
Ưu: 0 cài đặt. Nhược: không qua phiên. Gãy: ngay phiên sau.

**Cách 2 — LLM trích "fact" lúc ghi, lưu DB ngoài (mem0, Letta, Graphiti).**
Ưu: tìm theo nghĩa tốt, có sẵn quan hệ. Nhược: tốn token mỗi lần ghi; fact là bản tóm, mất ngữ cảnh ("vì sao bỏ?" — vì chậm,
Bi chê); DB ngoài git nên không có diff/review. Gãy: LLM tóm sai → không ai phát hiện; đổi nhà cung cấp → di trú dữ liệu.

**Cách 3 — File trong git là nguồn, chỉ mục dựng lại được (cách Seriously).**
Ưu: 0 token, tất định, có lịch sử git, xoá cache vô hại, đo được trong selftest. Nhược: lần dựng đầu chậm (30 s);
không "hiểu nghĩa" sẵn (vá bằng vector cục bộ ở P3). Gãy: nếu ai đó bắt đầu sửa *trong* sqlite mà không sửa file — cache thành nguồn
lén, mất khi dựng lại.

**Cách 4 — DB là nguồn sự thật (không có file).**
Ưu: truy vấn mạnh, giao dịch. Nhược: merge giữa nhiều phiên song song khó (git merge file text thì dễ); không đọc được bằng mắt.
Gãy: hai phiên ghi cùng lúc trên hai máy.

## 5. Bảng một lần nhìn

| | Token lúc ghi | Tất định | Xoá chỉ mục | Qua phiên | Review được |
|---|---|---|---|---|---|
| 1. Ngữ cảnh | 0 | — | — | ✗ | ✗ |
| 2. LLM trích, DB ngoài | cao | ✗ | mất thật | ✓ | khó |
| 3. Git + chỉ mục dựng lại | 0 | ✓ | mất 30 s | ✓ | ✓ diff |
| 4. DB là nguồn | 0 | ✓ | mất thật | ✓ | khó |

**Quy luật:** để cái *đắt* (LLM, người) ở chỗ ghi **một lần và được review**; để cái *rẻ và tất định* chạy ở mọi lần đọc/ghi
thường ngày. Cache phải luôn vứt được.

## 6. Scale

- **Nhỏ** (vài trăm file): cách nào cũng chạy; cách 3 dựng lại < 1 s.
- **Vừa** (cỡ Seriously: 20k đoạn, 77 MB): dựng đầy đủ 28,6 s — vẫn chấp nhận được vì chỉ xảy ra một lần mỗi máy, còn lại là
  *tăng dần* (incremental): `index()` chỉ đọc lại file đổi `mtime:size` (bảng `files`), ~2,7 s khi có thay đổi.
- **Lớn** (hàng triệu đoạn): dựng lại mất giờ. Vẫn giữ nguyên tắc, nhưng cache được *chia sẻ* (build một lần trên CI, máy khác tải
  về). Cái vỡ trước là **thời gian dựng lại**, chứ không phải nguyên tắc.

Đổi cấu trúc bảng thì sao? `recall.py` có `SCHEMA = 3`: tăng số → chỉ mục cũ bị xoá và dựng lại. Không cần "migration" cho cache —
đó chính là phần thưởng của nguyên tắc 2.

## 7. Dừng lần hai — mở Seriously kiểm chứng

- `tools/claude/recall.py` dòng 1–17 (docstring: "writing memory costs 0 model tokens. The raw record stays the source").
- Dòng `SCHEMA = 3` và hàm `connect()`: đổi schema → drop + rebuild.
- `index()`: bảng `files(path, key)` với key = `mtime:size` (sổ tay) hoặc `HEAD` (git log) → chỉ đọc lại cái đổi.
- `git check-ignore -v company/state/recall.sqlite` → `.gitignore:111`.
- `tools/claude/transcript.py`: adapter H-10 duy nhất (commit `8265e7b3a`, `38cc8e24d`).
- Thử: `RECALL_DB=/tmp/x.sqlite python3 tools/claude/recall.py "VFX Graph"` → tự dựng một chỉ mục mới từ số không.

## 8. Bốn nền tảng

- **Mac / Windows** (máy dev): cùng Python + SQLite. Khác: Windows có `mtime` độ phân giải khác và đường dẫn `\` — nên khoá
  `mtime:size` vẫn ổn nhưng đường dẫn trong chỉ mục phải chuẩn hoá. Transcript nằm ở thư mục khác nhau theo OS → lý do có adapter.
- **iOS / Android**: không chạy harness, nhưng nguyên tắc y hệt trong game: **save là nguồn sự thật, mọi thứ khác là cache**
  (bảng tra, atlas, shader cache). Hệ điều hành mobile được phép xoá thư mục cache khi thiếu chỗ (iOS `Caches/`, Android
  `getCacheDir()`) — game nào lỡ để dữ liệu thật trong cache sẽ mất save. Cùng bài học: cache phải vứt được.

## 9. Tóm tắt một dòng

Kiến thức sống ở file trong git (có diff, có review); mọi chỉ mục là cache tất định, 0 token, xoá đi dựng lại được.

**Thuật ngữ:** source of truth (nguồn sự thật) · cache · deterministic (tất định) · incremental index (chỉ mục tăng dần) ·
schema version · adapter. **Bài sau:** [07b — đường đọc đẩy](07b-duong-doc-day.md).
