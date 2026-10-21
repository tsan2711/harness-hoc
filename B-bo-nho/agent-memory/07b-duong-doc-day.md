# 07b — Đường đọc đẩy: hook `UserPromptSubmit`, claim, mở phiên

> Chuỗi 07, bài 2/9. Đọc ~10 phút. Cần trước: [07a](07a-nguyen-tac-git-nguon-su-that.md).

## 1. Câu chuyện

Giữa phiên Thousandfold, Bi gõ: *"sao bầy cánh hoa lại vẽ bằng RenderMeshInstanced?"*. Kho đã có ghi chú *"Bi rejected the CPU
matrix bake + 1023-batch RenderMeshInstanced…"*. Agent không gọi `kit recall` — nó tin vào cái nó nghĩ là đúng, mở code và bắt đầu
"tối ưu" đúng cách Bi đã bỏ. Kiến thức có, công cụ tìm có, nhưng **không ai gọi**.

Cùng tuần đó, mỗi lần một phòng `kit company claim` một việc inbox, `recall.hint()` tự in ≤ 3 đoạn liên quan vào output. Trong
867 lần claim tính đến 2026-10-21, **679 lần (78 %)** có ít nhất một đoạn — không cần agent nhớ gì cả.

## 2. Dừng 30 giây

- Vì sao "dặn agent nhớ gọi recall" (một dòng trong `CLAUDE.md`) gần như không bao giờ đủ?
- Nếu mỗi câu Bi gõ đều kèm 3 đoạn recall, cái gì xấu đi?
- Một hook chạy *trước mỗi câu* được phép chậm bao nhiêu?

## 3. Kéo vs đẩy

**Kéo (pull):** agent tự quyết khi nào tìm. Cần agent (a) nghi ngờ mình thiếu, (b) nhớ có công cụ, (c) hỏi đúng chữ. Ba cái
cùng đúng thì hiếm — model tự tin nhất đúng lúc nó sai. Câu hỏi 1: luật trong `CLAUDE.md` là thêm một thứ để nhớ, chứ không bỏ
được bước (a).

**Đẩy (push):** harness tìm *thay* agent ở những **điểm vào** biết trước, và đặt kết quả vào ngữ cảnh. Agent không cần nghi ngờ.
Seriously có ba điểm vào:

| Điểm vào | Tín hiệu để tìm | Trạng thái |
|---|---|---|
| `claim` việc inbox | đường dẫn, mã, tiêu đề trong file việc | **có** (`hint()` ← `inbox.cmd_claim`, 2026-10-16) |
| Mở phiên có việc dở | file việc dở mà `leftover` ghi lại | **có** (`leftover.recall_line()`, commit `78bb4ec05`) — bài 06 ghi "thiếu" là chụp trước commit này |
| Câu Bi gõ giữa phiên | chính câu đó | **chưa** — đây là việc chính của P1 |

## 4. Hook `UserPromptSubmit` của Claude Code

Claude Code chạy lệnh trong `.claude/settings.json` ở từng sự kiện. `UserPromptSubmit` chạy **sau khi Bi bấm Enter, trước khi
model đọc câu**. Hook nhận JSON qua stdin (có `prompt`, `session_id`, `cwd`). Quy ước:
- thoát 0 + in ra stdout → chữ đó được **thêm vào ngữ cảnh** cùng câu của Bi;
- thoát 2 → chặn câu (không dùng ở đây);
- quá `timeout` (giây, đặt trong settings) → bị bỏ qua.

Seriously đã có hai hook ở sự kiện này: `presence.py prompt` và `ctxguard.py` (timeout 5 s). Thêm `recall.py prompt-hint` là thêm
dòng thứ ba.

## 5. Ba ngân sách — trả lời câu 2 và 3

**Thời gian.** Hook chạy trước *mỗi* câu, Bi chờ trực tiếp. Đo trên máy thật 2026-10-21:
| Bước | Thời gian |
|---|---|
| `import recall` (Python khởi động) | ~20 ms |
| `search()` khi cache `recall-touch.json` còn đúng HEAD | **33–70 ms** |
| `search()` khi HEAD vừa đổi (cache hỏng → `git log` 180 ngày) | **~1 100 ms** |
| `index()` tăng dần | ~2 700 ms |

Vì thế đề xuất: `prompt-hint` **không gọi `index()`** (để SessionStart / hook commit lo), ngân sách < 150 ms p95, timeout 2 s,
lỗi hoặc quá giờ = im. Dòng thứ ba của bảng là bẫy: sau mỗi commit, câu đầu tiên sẽ chậm 1 giây vì nhãn "có thể cũ" cần `git log`.
Cách gỡ: dùng cache cũ khi HEAD lệch (nhãn trễ một commit, chấp nhận được) hoặc tắt nhãn trong đường này.

**Token.** 3 đoạn × ~170 ký tự + nhãn ≈ ≤ 600 token. Mỗi câu Bi gõ thêm 600 token, phiên 40 câu = 24k token — nhiều. Nên cần:

**Ngưỡng im lặng.** Chỉ in khi chắc là có ích:
- bỏ câu < 4 từ và lệnh (`làm tiếp`, `ok`, `/clear`, `/…`) — đó là phần lớn câu Bi gõ;
- chỉ in đoạn có điểm BM25 vượt ngưỡng (từ hiếm trùng thật), không in "đoạn ít tệ nhất";
- bỏ đoạn agent vừa đọc trong phiên (cùng `path`) nếu biết.

Im lặng đúng lúc quan trọng hơn nói đúng lúc: hook ồn thì agent học cách **lờ** nó (như cảnh báo compile vàng không ai đọc).

## 6. Các cách, thử trên câu "sao bầy cánh hoa lại vẽ bằng RenderMeshInstanced?"

| Cách | Kết quả | Ưu | Gãy khi |
|---|---|---|---|
| A. Luật "nhớ gọi recall" | Agent không gọi | 0 chi phí | model tự tin |
| B. Đẩy mọi câu, không ngưỡng | Có ghi chú đúng, kèm 3 đoạn nhiễu ở câu "ok" | không sót | ồn → bị lờ; token phình |
| C. Đẩy có ngưỡng + bỏ lệnh ngắn | Có ghi chú đúng; "ok" im | rẻ, đúng chỗ | câu diễn đạt lại (BM25 trượt — [05a](05a-bm25-va-fts5.md) §4) |
| D. Như C + index trong hook | Như C nhưng chậm 3 s | luôn mới | Bi chờ 3 s mỗi câu |
| E. LLM nhỏ quyết "có cần tìm không" | Tốt | hiểu ý | tốn token mỗi câu, trái 07a |

**Quy luật:** đẩy ở điểm vào, nhưng trả bằng ba đồng tiền — ms, token, sự chú ý — và đồng thứ ba đắt nhất.

## 7. Scale

- **Nhỏ** (vài phiên/ngày): đẩy ở claim là đủ.
- **Vừa** (Seriously: hàng chục phiên/ngày, nhiều phòng): câu giữa phiên là chỗ sót lớn nhất; ngưỡng im lặng thành chuyện chính.
- **Lớn** (nhiều nghìn đoạn mới/ngày): BM25 vẫn ms, nhưng tỉ lệ "đoạn đúng chữ mà sai ý" tăng → ngưỡng phải nâng, cần lọc
  `prefer` theo phòng (`W_UNIT = 8.0`) và về sau là vector (P3). Cái vỡ là **độ chính xác của top-3**, không phải tốc độ.

## 8. Dừng lần hai — mở Seriously kiểm chứng

- `.claude/settings.json` → khối `UserPromptSubmit` (hiện có `presence.py prompt`, `ctxguard.py`).
- `tools/claude/recall.py` `hint()`: lấy ≤ 6 thực thể có `/`, số hoặc `Test` + ≤ 5 từ tiêu đề ≥ 4 chữ cái; `budget=1800` ký tự; bỏ
  chính file việc; ghi `company/state/recall-inject.jsonl`.
- `tools/claude/leftover.py` `recall_line()` — đường mở phiên đã có.
- `recall.inject_rate()` → số dùng trong `kit weekly`; `company/layers.toml` lớp `recall-inject` (mục tiêu ≥ 80 %, hiện 78 %).
- `layerflag.off('recall-inject')` ở đầu `hint()`: công tắc để chạy thử "bỏ nạng" (bài [07h](07h-lo-trinh-pha-va-cong.md)).

## 9. Bốn nền tảng

Hook là tiến trình con: trên **Mac** khởi động Python ~20 ms; trên **Windows** khởi động tiến trình và Python chậm hơn rõ (thường
gấp 2–5 lần) và antivirus có thể quét mỗi lần chạy — ngân sách 150 ms dễ vỡ trước ở Windows, nên đo p95 trên cả hai.
**iOS / Android** không chạy hook, nhưng cùng ý "đẩy ở điểm vào" là gợi ý trong game: tooltip hiện khi người chơi *chạm* vật lần
đầu (điểm vào), không bắt người chơi tự mở trang hướng dẫn (kéo) — và cũng phải có ngưỡng im, không thì người chơi tắt hết.

## 10. Tóm tắt một dòng

Đừng trông agent nhớ tìm: harness tìm thay ở điểm vào (claim, mở phiên, câu hỏi), trong < 150 ms, ≤ 600 token, và im khi không chắc.

**Thuật ngữ:** push vs pull (đẩy / kéo) · hook · entry point (điểm vào) · latency budget (ngân sách thời gian) · p95 · silence
threshold (ngưỡng im lặng) · alert fatigue (nhờn cảnh báo). **Bài sau:** [07c — frontmatter](07c-frontmatter.md).
