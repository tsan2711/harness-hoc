# 06 — Kiến trúc memory đề xuất (bản chụp 2026-10-20)

> Kết quả của [05 — tranh luận](05-tranh-luan-kg-vs-recall.md). Bản sống nằm ở repo Seriously: `docs/shared/memory-architecture-proposal.md`.
> Khái niệm: [05a BM25](05a-bm25-va-fts5.md) · [05b vector](05b-embedding-va-vector.md) · [05c hybrid](05c-hybrid-rrf-reranker.md) · [05d KG](05d-knowledge-graph.md) · [05e graph-RAG](05e-graph-rag.md) · [05f kiến thức cũ](05f-ky-uc-cu-va-thay-the.md) · [05g đo](05g-do-truy-hoi.md).


> Kết quả của `memory-debate-2026-10-20.md` (lý lẽ, research, vị thế hai phía) + nối `memory-options.md` (PA2).
> **Chưa áp vào code.** Phiên refactor đọc file này trước, làm theo pha, mỗi pha có cổng đo.
> Bài học nền cho Bi: `~/Documents/Learning/harness-hoc/B-bo-nho/agent-memory/05*.md`.

## 0. Nguyên tắc (giữ từ H-10 + rút từ tranh luận)

1. **0 token lúc ghi và lúc tìm thường ngày.** Model cục bộ (embedding/NER) được; LLM chỉ chạy theo lô, kết quả commit vào git, Bi duyệt chi phí.
2. **Git là nguồn sự thật.** Mọi chỉ mục (`recall.sqlite`, vector, graph) dựng lại được từ git + transcript; xoá đi không mất gì.
3. **Đẩy, không chờ kéo.** Kiến thức liên quan phải tự tới agent ở các điểm vào (câu hỏi, nhận việc, mở phiên), không trông agent nhớ gọi.
4. **Phán quyết "cũ/mới" ở lúc ghi, đánh dấu chứ không xoá.** Lúc đọc chỉ hiển thị nhãn (STALE: phán lúc đọc ~55 %).
5. **Không "mới nhất thắng" mù.** Phân biệt thay thế / sửa sai / cùng tồn tại; mỗi kiến thức có phạm vi (game, bộ phận).
6. **Chọn công cụ theo loại câu, quyết bằng đo.** Vector/graph chỉ vào sau thí nghiệm có luật thắng đặt trước.

## 1. Hiện trạng đúng (sửa lại so với lúc tranh luận)

| Có rồi | Ở đâu |
|---|---|
| FTS5 BM25, cột `text` (bỏ dấu) / `acc` (giữ dấu, ×1,5) / `ent` (thực thể, ×3), AND → OR | `tools/claude/recall.py` `search()` |
| Đồng nghĩa 29 nhóm, viết tay | `company/eval/recall/synonyms.toml` |
| Nhãn `có thể cũ`: đoạn chuyện nhắc file đổi sau ngày đoạn; doc có tiêu đề "đã thay bởi / (cũ) / superseded" | `is_stale()`, `doc_outdated()` — **chỉ nhãn, không hạ hạng** |
| Đưa sẵn ≤ 3 đoạn khi `claim` việc inbox | `hint(task_path)` ← `inbox.cmd_claim`, log `company/state/recall-inject.jsonl` |
| Bộ đo 45 câu (kw 20 · para 20 · trap 5), cổng lùi selftest | `company/eval/recall/cases.toml`, `baseline.json` |
| Hook `UserPromptSubmit` (presence, ctxguard) — **chưa có recall** | `.claude/settings.json` |

Thiếu: đẩy kiến thức khi hỏi giữa phiên; cạnh "thay thế" tường minh; phạm vi; câu nhiều bước và bộ held-out trong bộ đo; số đo dùng thật trong `kit weekly`.

## 2. Kiến trúc đích

```
                ┌──────────── ĐƯỜNG GHI ────────────┐            ┌──────────── ĐƯỜNG ĐỌC ────────────┐
 agent ghi doc/ │ frontmatter: status, supersedes,  │            │ điểm vào:                          │
 memory/ADR ───▶│ scope, keywords                   │            │  • UserPromptSubmit (câu của Bi)   │
                │ hook nhắc lúc ghi: recall 3 đoạn  │            │  • claim việc inbox (có rồi)       │
                │ gần nhất → điền supersedes|none   │            │  • SessionStart có việc dở         │
                └──────────────┬────────────────────┘            └──────────────┬─────────────────────┘
                               ▼                                                ▼
             ┌─────────────── recall.sqlite (dựng lại từ git) ─────────────────────────┐
             │ chunks (FTS5: text/acc/ent)   │ edges(src,dst,type,ts,source)          │
             │ [P3] vec(chunk_id, emb)       │   commit→file, task→commit, doc→link,  │
             │                               │   doc→supersedes→doc, doc→scope        │
             └───────────────┬─────────────────────────────────────────────┬────────────┘
                             ▼                                             ▼
             tìm: BM25 (+đồng nghĩa) [∥ vector → RRF]  →  mở rộng 1 bước theo edges  →  luật xếp
             (chốt > chuyện; supersedes → nhãn "ĐÃ THAY BỞI X" + đẩy X lên; scope khớp được ưu tiên)
                             ▼
             in ≤ 3 đoạn, nhãn ở đầu dòng, ≤ 600 token
```

### 2.1 Mô hình dữ liệu
**Frontmatter** (doc trong `docs/`, `depts/*/knowledge/`, ADR, memory tầng 1):
```yaml
status: active | superseded | wrong        # wrong = sửa sai: không dùng cả làm lịch sử
supersedes: [docs/shared/old.md]           # hoặc: none (đã xét, không thay gì)
scope: [thousandfold] | [all]              # cùng tồn tại giữa game không bị đè
keywords: [...]                            # đã có (cc86fac), vào cột ent ×3
```
Doc cũ **không cần sửa**: cạnh `supersedes` lưu ở doc mới; recall tự suy ngược "X bị Y thay".

**Bảng `edges`** trong `recall.sqlite`, dựng bởi script, 0 token:
| type | Nguồn | Dùng cho |
|---|---|---|
| `touches` commit→file | `git log --name-only` (đã đọc trong `last_touch()`) | nhãn cũ; "ai đã sửa file này" |
| `implements` task→commit | trailer `Task:` | "việc nào đã đổi module này" |
| `links` doc→doc/file | link markdown, đường dẫn trong văn bản | mở rộng hàng xóm; lint mồ côi |
| `supersedes` doc→doc | frontmatter | nhãn + đẩy bản mới; lan truyền |
| `scope` doc→unit/game | frontmatter, đường dẫn (`depts/x`, `June/`) | lọc cùng tồn tại |

Không có graph DB, không LLM trích. Hub (`CLAUDE.md`, `kit.sh`) bị hạ trọng số khi mở rộng (như IDF).

### 2.2 Đường đọc
1. **Hook `UserPromptSubmit` → `recall.py prompt-hint`** (mới): lấy câu của Bi, bỏ câu < 4 từ / lệnh (`làm tiếp`, `/…`), gọi `search()` **không** gọi `index()` (index nặng; để SessionStart/hook commit lo), in ≤ 3 đoạn nếu điểm vượt ngưỡng, không thì im. Ngân sách < 150 ms, timeout 2 s, lỗi = im.
   Log cùng `recall-inject.jsonl` (`src: prompt`).
2. `hint()` cho claim giữ nguyên; thêm đường **SessionStart có việc dở** (`leftover` biết việc → `hint()` trên file việc).
3. **Luật xếp** (thứ tự): khớp `scope` → đoạn có `status: wrong` loại khỏi top → đoạn bị `supersedes` mang nhãn **`ĐÃ THAY BỞI <path>`** ở đầu dòng và bản thay được kéo vào top nếu chưa có → chốt trên chuyện cùng bucket → `có thể cũ` (file đổi) giữ nhãn như nay.
   Không hạ hạng mù theo ngày (đã đo: mất 3 câu para).
4. **Mở rộng 1 bước**: khi đoạn top là doc/file có cạnh `supersedes`/`links` mạnh → thêm tối đa 1 đoạn hàng xóm vào ngân sách 3.

### 2.3 Đường ghi (vòng thay thế)
| Bước | Cơ chế | Khi nào |
|---|---|---|
| A | Một chủ đề một file sống; sửa tại chỗ (git giữ lịch sử) | luật trong `.claude/rules/` |
| B | Frontmatter `status/supersedes/scope` | khi tạo doc/ADR/memory mới |
| C | **Hook nhắc lúc ghi** (PostToolUse Write/Edit trên `docs/**`, `depts/*/knowledge/**`, memory): chạy recall trên tiêu đề + keywords, nếu có đoạn cùng chủ đề điểm cao mà frontmatter chưa có `supersedes` → in 1 dòng "xét: X, Y — điền supersedes hoặc none" | mỗi lần ghi doc kiến thức |
| E | `kit company lint`: cặp doc rất giống nhau (BM25 chéo, sau là cosine) mà không có cạnh → cảnh báo; doc mồ côi; `supersedes` trỏ file không tồn tại | lint tuần |
| G | Lan truyền: khi doc Y `supersedes` X, liệt kê doc `links`→X → báo "có thể dựa trên cái cũ" | trong hook C |
| D | Ngày chỉ là tie-break | trong xếp |

Không làm cổng chặn (tránh đóng cứng — SSGM): hook C/E chỉ nhắc, `none` là câu trả lời hợp lệ.

### 2.4 Đo (trọng tài)
Bộ đo mới trong `company/eval/recall/`:
| Nhóm | Cỡ | Vai |
|---|---|---|
| kw, para (có) | 20 + 20 | phát triển — được chỉnh đồng nghĩa theo |
| `para-heldout` (mới) | 15–20 | rút từ câu thật trong transcript; **không ai chỉnh theo**; chỉ báo |
| `multi` (mới) | ≥ 10 | câu nhiều bước thật ("ADR nào chi phối file này", "việc nào đổi module này", "X thay quyết định nào") |
| `stale` (mở rộng trap) | 10–15 cặp | quyết định đổi có thật trong git; đo `cũ@3` + nhãn có hiện |
Chỉ số: recall@3 (cái `hint` thật sự đưa) + recall@12 + `cũ@3` theo nhóm; so **từng câu**. `kit weekly`: `inject_rate` theo `src`, lần mở transcript thô, số `supersedes` mới, cảnh báo lint E.

## 3. Lộ trình theo pha

| Pha | Việc | Cổng qua pha |
|---|---|---|
| **P0 — Thước đo** | Thêm `para-heldout`, `multi`, `stale`; recall@3 + so từng câu trong `recall_eval.py`; chỉ số dùng thật vào `kit weekly` | Bộ đo chạy trong selftest; có số nền cho mọi nhóm |
| **P1 — Đẩy** | `prompt-hint` + hook `UserPromptSubmit`; hint cho việc dở lúc SessionStart; `layers.toml` thêm lớp `recall-prompt` có `remove_test` | < 150 ms p95; sau 14 ngày: tỉ lệ đoạn được agent dùng/nhắc > 0, không tăng token phiên rõ rệt |
| **P2 — Thay thế lúc ghi** | Frontmatter B; bảng `edges` (supersedes, scope, links, touches, implements); luật xếp 2.2.3; hook C + lan truyền G; lint E; áp cho memory tầng 1 | `cũ@3` nhóm stale = 0; para/kw không lùi |
| **P3 — Vector** (thí nghiệm) | sqlite-vec + model đa ngữ nhỏ cục bộ, RRF với BM25; viết lại luật bucket theo điểm RRF | Luật thắng đặt trước: `para-heldout` +≥ 3 câu, kw không lùi, < 300 ms |
| **P4 — Graph-RAG** (thí nghiệm) | (a) mở rộng theo `edges` (có từ P2); (b) SPRIG-like: NER + PPR, 0 token; (c) chỉ khi Bi duyệt tiền: LLM-trích theo lô trên một phần kho | So với **hybrid P3**, không với BM25: nhóm `multi` +≥ 2 câu, nhóm khác không lùi ≥ 1 câu |

P0 trước hết vì không có `multi`/`heldout` thì P3/P4 không phân xử được. P1 và P2 độc lập với kết quả tranh luận KG — làm được ngay.
Cổng PA2.4 cũ ("vector chỉ sau 14 ngày đưa-sẵn") **thay** bằng cổng P3 ở trên (lý do: cổng cũ không gắn với chất lượng tìm).

## 4. File sẽ đụng

| Pha | File |
|---|---|
| P0 | `company/eval/recall/cases.toml`, `tools/claude/recall_eval.py`, `baseline.json`, script weekly |
| P1 | `tools/claude/recall.py` (`prompt_hint`), `.claude/settings.json`, `company/layers.toml`, `tools/claude/leftover.py` |
| P2 | `recall.py` (`edges`, xếp, `fmt` nhãn), hook mới `tools/claude/supersede_hint.py`, `.claude/rules/` (luật A/B), `kit company lint`, `_template/` frontmatter |
| P3 | `recall.py` (vec + RRF), phụ thuộc sqlite-vec + model (ghi vào `memory-options.md`) |
| P4 | script dựng graph riêng, chỉ sau cổng |

Sửa `tools/` → `kit selftest`.

## 5. Không làm (và vì sao)
- Graphiti / mem0 / Letta / claude-mem: LLM lúc ghi, dữ liệu ngoài git (H-10). Không đổi.
- Hạ hạng theo ngày: đã đo mất câu para; sai với cùng tồn tại.
- Để agent tự phán mâu thuẫn lúc đọc: STALE ~55 %.
- Graph DB server: thừa với cỡ kho; SQLite đủ.

## 6. Chờ Bi chốt
1. Ép khai `supersedes` (hook nhắc, không chặn) — đồng ý?
2. Memory tầng 1 dùng chung frontmatter `status/supersedes` — đồng ý?
3. Thay cổng PA2.4 bằng cổng P3 — đồng ý?
4. P4(c) LLM-trích theo lô: có chi tiền không (ước lượng trước khi chạy)?
5. Còn giữ "KG tốt hơn rất nhiều" cho câu một bước, hay thu về câu nhiều bước? (quyết nhóm `multi` cần to cỡ nào)
