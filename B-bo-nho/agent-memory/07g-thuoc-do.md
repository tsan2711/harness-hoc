# 07g — Thước đo mới: held-out, multi, stale; chỉ số dùng thật

> Chuỗi 07, bài 7/9. Đọc ~10 phút. Cần trước: [05g đo truy hồi](05g-do-truy-hoi.md).

## 1. Câu chuyện

Bộ đo `company/eval/recall/` có 45 câu. Số nền trong `baseline.json`: từ khoá **20/20**, diễn đạt lại **9/20**, bẫy **4/5**,
`cũ↑` 0, 8,9 ms/câu. Ai đó thêm 6 nhóm đồng nghĩa vào `synonyms.toml`; para lên 12/20. Vui. Nhưng đọc kỹ: cả 6 nhóm được viết khi
**nhìn** đúng 3 câu para đang trượt. Hỏi Bi một câu diễn đạt lại *mới* — vẫn trượt như cũ.

Cùng tuần, một thay đổi khác giữ nguyên 9/20, cổng selftest xanh. Thực ra nó **được 2 câu, mất 2 câu** — hai câu bị mất là hai câu
Bi hay hỏi nhất.

## 2. Dừng 30 giây

- Vì sao điểm tăng trên bộ câu mà mình đã nhìn khi chỉnh không chứng minh gì?
- `hint()` chỉ đưa 3 đoạn cho agent. Bộ đo chấm "trúng nếu đúng trong 12 đầu". Lệch ở đâu?
- Recall đạt 100 % trên bộ đo, nhưng agent vẫn mở transcript thô mỗi ngày. Bộ đo thiếu gì?

## 3. Bốn lỗ của bộ đo hiện tại

**Lỗ 1 — Rò rỉ (leakage), câu hỏi 1.** Nhóm `kw` và `para` là bộ **phát triển**: được chỉnh theo. Điểm trên bộ phát triển đo "mình
khớp bộ đề giỏi cỡ nào", không đo "mình tìm giỏi cỡ nào". Cần nhóm **`para-heldout`** (15–20 câu): rút từ câu thật Bi/agent đã gõ
trong transcript, **không ai được nhìn khi chỉnh**, chỉ báo số. Như đề thi khác đề luyện.

**Lỗ 2 — Sai ngưỡng k, câu hỏi 2.** recall@12 hỏi "có trong 12 không", còn đường đẩy (bài 07b) chỉ đưa **3**. Một đoạn đứng thứ 7 được
tính "trúng" nhưng agent không bao giờ thấy. Báo **cả recall@3** (cái agent thật sự nhận) **và recall@12** (cái `kit recall` thủ công
thấy).

**Lỗ 3 — Thiếu loại câu.** 45 câu đều là câu **một bước**: một đoạn chứa câu trả lời. Không có câu "ADR nào chi phối file này",
"việc nào đã đổi module này", "X thay quyết định nào" — đúng loại câu mà `edges` (07d) và graph-RAG (05e) hứa giúp. Không có nhóm
**`multi`** (≥ 10 câu) thì không thể chứng minh hay bác bỏ hứa hẹn đó. Bẫy cũ chỉ có 5 cặp; cần **`stale`** 10–15 cặp quyết định đổi
*có thật trong git*, đo `cũ@3` (bản cũ trong top 3 mà không mang nhãn).

**Lỗ 4 — Không đo dùng thật, câu hỏi 3.** Bộ vàng đo khả năng; không đo hành vi. Cần chỉ số từ đời thật trong `kit weekly`:
| Chỉ số | Nguồn | Nghĩa |
|---|---|---|
| `inject_rate` theo `src` (claim / start / prompt) | `company/state/recall-inject.jsonl` | đường đẩy có đưa được gì không (hiện claim: 679/867 = 78 %) |
| lần mở transcript thô / tuần | **chưa có nguồn tự động** — phải đếm lệnh Read/grep vào `*.jsonl` trong transcript | đẩy tốt thì agent ít phải đào |
| số `supersedes` mới / tuần | git diff frontmatter | đường ghi (07f) có sống không |
| cảnh báo lint E | `kit company lint` | kho có tự mâu thuẫn tăng lên không |

## 4. So từng câu, không so tổng — chuyện "được 2 mất 2"

Tổng 9/20 → 9/20 giấu được thay đổi bên trong. `recall_eval.py` nên in **danh sách câu đổi trạng thái** (trượt→trúng, trúng→trượt)
cho mỗi lần chạy. Lý do thống kê ([05g](05g-do-truy-hoi.md)): với 20 câu, một câu = 5 điểm %; chênh 1–2 câu là nằm trong nhiễu. Cái
đáng tin là *câu nào* đổi và vì sao — đọc được bằng mắt.

Seriously đã có một mẹo chống nhiễu: chạy lại bộ đo với kho **×5 nhiễu cố định** (`x5_kw_hit` 19, `x5_para_hit` 8, `x5_trap_hit` 3 trong
`baseline.json`) — thay đổi chỉ tốt ở kho nhỏ mà tệ khi kho to sẽ bị cổng bắt.

## 5. Bộ đo như hợp đồng

Một bộ đo chỉ phân xử được nếu nó được **viết trước** khi biết kết quả và **không đổi** theo kết quả. Ba điều khoản:
1. **Câu từ nguồn thật** (git log, docs, transcript), có `gold` là đường dẫn/băm cụ thể — không phải "agent thấy hợp lý".
2. **Vai rõ ràng**: nhóm phát triển được chỉnh theo; held-out thì không; thêm câu vào held-out chỉ khi chưa ai chạy cấu hình mới trên nó.
3. **Luật thắng đặt trước** (bài [07h](07h-lo-trinh-pha-va-cong.md)): "vector được vào nếu para-heldout +≥ 3 câu, kw không lùi" —
   ghi *trước* thí nghiệm.

## 6. Các cách, trên ca "thêm 6 nhóm đồng nghĩa"

| Bộ đo | Kết luận | Gãy khi |
|---|---|---|
| A. Tổng recall@12 trên kw+para | "+3 câu, tốt" | rò rỉ — đồng nghĩa viết theo đề |
| B. A + held-out | "dev +3, held-out +0 → không tổng quát" | held-out quá nhỏ (< 10) |
| C. B + recall@3 | thấy thêm: 1 trong 3 câu được chỉ lên hạng 9 — agent vẫn không thấy | — |
| D. C + so từng câu | thấy câu nào mất | phải đọc, không tự động hoá hết |
| E. D + chỉ số dùng thật | biết agent có đỡ đào transcript không | trễ 1–2 tuần, nhiều yếu tố khác lẫn vào |

**Quy luật:** đo đúng cái agent nhận (k = 3), trên câu không ai chỉnh theo, so từng câu; rồi kiểm lại bằng hành vi thật.

## 7. Scale

- **Nhỏ** (vài chục câu): mỗi câu ~3–5 %; chỉ tin chênh lớn và danh sách câu đổi.
- **Vừa** (Seriously sau P0: ~45 + 20 + 10 + 15 ≈ 90 câu): đủ để phân xử chênh ≥ 3 câu trong một nhóm.
- **Lớn** (hàng trăm câu, nhiều người thêm): bộ đo **mục** — gold trỏ file đã đổi tên, câu hết nghĩa. Cần kiểm gold còn tồn tại trong
  selftest và hạn rà định kỳ. Cái vỡ là **độ tươi của bộ đo**.

## 8. Dừng lần hai — mở Seriously kiểm chứng

- `company/eval/recall/cases.toml` đầu file: định nghĩa `kw / para / trap`, "trúng nếu BẤT KỲ gold nào có trong 12 kết quả đầu".
- `company/eval/recall/baseline.json`: số nền và các khoá `x5_*`.
- `tools/claude/recall_eval.py`: `score()` (nhóm, `stale`, `stale_above` = `cũ↑`), `gate()` (cổng lùi so với nền), `scale()` (×5).
- `company/eval/recall/synonyms.toml`: tự đối chiếu nhóm nào sinh ra để vá câu nào.
- `python3 tools/claude/recall.py` có `inject_rate()` — số `kit weekly` đang đọc.

## 9. Bốn nền tảng

Bộ đo chạy offline trên một chỉ mục riêng (`recall-eval.sqlite`, chỉ sổ tay + git, **không** transcript vì transcript khác nhau theo
máy) → cùng số trên **Mac và Windows** — điều kiện để cổng selftest công bằng. Đo **thời gian** thì khác: ms/câu trên Windows sẽ cao
hơn, nên cổng thời gian phải ghi máy đo. Trên **iOS / Android**, bài học tương ứng là test hiệu năng game: đo trên máy thật yếu nhất
bạn hỗ trợ, tách bộ "đã tối ưu theo" và bộ "chưa từng nhìn" (cảnh mới, thiết bị mới), và so từng cảnh chứ không so FPS trung bình.

## 10. Tóm tắt một dòng

Bộ đo tốt = câu thật, có nhóm held-out không ai chỉnh theo, có câu nhiều bước và cặp cũ/mới thật, chấm ở k = 3, so từng câu, và
được kiểm lại bằng chỉ số dùng thật.

**Thuật ngữ:** held-out · dev set (bộ phát triển) · leakage (rò rỉ) · recall@k · multi-hop · pre-registration (đặt luật trước) ·
per-case diff (so từng câu) · online metric (chỉ số dùng thật). **Bài sau:** [07h — lộ trình pha](07h-lo-trinh-pha-va-cong.md).
