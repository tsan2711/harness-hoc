# 05f — Kiến thức cũ và thay thế: thời gian, mâu thuẫn ngầm, lan truyền

> Đi kèm [05](05-tranh-luan-kg-vs-recall.md) vòng 3, 4, 6. Đây là bài toán Bi thật sự lo nhất.

## 1. Câu chuyện

Ngày 3/10, ghi chú: *"vẽ cỏ bằng CPU matrix bake + RenderMeshInstanced"*. Ngày 9/10, Bi: *"chậm quá, bỏ — dùng VFX Graph"*, ghi vào memory
`feedback_no_rendermeshinstanced`. Ngày 20/10, agent mới hỏi recall "cách vẽ cỏ", nhận 12 đoạn: 7 đoạn từ tuần đầu (nói RenderMeshInstanced,
dài, nhiều chữ trùng), 1 đoạn ngắn nói "bỏ". BM25 xếp đoạn cũ lên đầu. Agent làm lại đúng cái Bi đã cấm.

Không file code nào bị sửa giữa 3/10 và 9/10 — chỉ có *ý* đổi.

## 2. Dừng 30 giây
- Có phải "cái mới nhất luôn đúng" không? Nghĩ một trường hợp cái mới hơn **không** thay cái cũ.
- Khi Bi đổi "vẽ cỏ", những kiến thức *khác* nào cũng cần đổi theo? (ngân sách drawcall? shader? test?)
- Ai nên chịu trách nhiệm đánh dấu "cái cũ hết đúng": người ghi cái mới, người đọc, hay máy?

## 3. Phân loại "cũ"

### 3.1 Theo nguyên nhân
| Loại | Ví dụ | Máy tự phát hiện? |
|---|---|---|
| **Cũ vì đối tượng đổi** | Ghi chú tả `kit.sh` có 3 lệnh, file giờ có 5 | **Có** — so ngày ghi chú với ngày commit file được nhắc |
| **Cũ vì quyết định đổi** | Câu chuyện trên | **Không** — cần hiểu hai câu mâu thuẫn |
| **Cũ vì thế giới đổi** | "Unity 6 chưa hỗ trợ X" — bản mới đã hỗ trợ | Không (thông tin ngoài repo) |

### 3.2 Theo quan hệ giữa cũ và mới (theo survey 2609.08599 — *chỉ từ snippet, chưa xác minh*)
| Quan hệ | Ý | Xử lý đúng |
|---|---|---|
| **Thay theo thời gian** (supersession) | trước đúng, giờ không đúng nữa | giữ cũ làm lịch sử, đánh dấu hết hiệu lực từ ngày X |
| **Sửa sai** (correction) | cái cũ *chưa bao giờ* đúng | đánh dấu sai; không nên dùng kể cả làm lịch sử |
| **Cùng tồn tại** (coexistence) | cả hai đúng trong ngữ cảnh khác | June dùng VContainer + ECS, NanoSwarm dùng OOP — **không** được để cái mới đè cái cũ |
→ *Đáp câu 1 mục 2:* "mới nhất thắng" sai với loại thứ ba. Luật xếp theo ngày (cách D ở vòng 4) chỉ là lưới an toàn.

## 4. Trục thời gian: bitemporal

Mô hình chuẩn trong cơ sở dữ liệu, Graphiti dùng biến thể của nó (theo nguồn thứ cấp):
- **Thời gian hiệu lực** (valid time): khi nào điều này *đúng ngoài đời*. `valid_from = 3/10`, `valid_to = 9/10`.
- **Thời gian ghi nhận** (transaction time): khi nào *hệ thống biết*. Ghi 3/10, đánh dấu hết hiệu lực lúc 9/10.
Không xoá — **đóng cửa sổ hiệu lực**. Lợi: hỏi "hiện tại" chỉ lấy cạnh còn mở; hỏi "hồi 5/10 ta nghĩ gì" vẫn trả được; biết được *vì sao* đã từng làm vậy.

Với Seriously: git đã cho **thời gian ghi nhận** miễn phí (ngày commit). Thứ thiếu là **valid_to** — ai đặt, lúc nào.

## 5. Phát hiện vs phán quyết vs lan truyền

Ba bước, độ khó tăng dần:
1. **Phát hiện ứng viên:** tìm các đoạn *cùng chủ đề* với kiến thức mới. Máy làm tốt — vector đặc biệt giỏi vì "nên" và "cấm" cùng chủ đề nằm gần nhau ([05b](05b-embedding-va-vector.md) §5).
2. **Phán quyết:** cặp này là thay thế / sửa sai / cùng tồn tại / không liên quan? Cần hiểu nghĩa + ngữ cảnh. **STALE** đo đúng chỗ này.
3. **Lan truyền (cascade):** cái cũ bị thay → các kiến thức *dựa trên* nó (ngân sách drawcall tính cho RenderMeshInstanced, test đo nó…) cũng nghi ngờ. *Câu 2 mục 2.*
   STALE ghi nhận model đặc biệt kém ở đây. Đây là chỗ **graph thật sự có giá trị**: nếu có cạnh `dựa trên`, lan truyền = đi theo cạnh.

## 6. STALE (arXiv 2605.06527) — nghiên cứu trúng đúng bài toán

- Tên bài toán: **Implicit Conflict** — quan sát sau làm vô hiệu ký ức trước *mà không có phủ định tường minh* (không ai nói "cái cũ sai").
- 400 kịch bản, 1.200 câu, >100 chủ đề, ngữ cảnh tới 150k token. Ba trục:
  - *State Resolution:* nhận ra niềm tin cũ đã hết đúng.
  - *Premise Resistance:* từ chối câu hỏi **giả định sẵn** điều cũ ("cho tôi số batch RenderMeshInstanced tối ưu" — agent phải nói "đã bỏ cách này").
  - *Implicit Policy Adaptation:* tự áp trạng thái mới vào việc sau, không cần nhắc.
- **Tốt nhất 55,2 %.** Lỗi: chấp nhận tiền đề cũ; không lan cập nhật sang ký ức liên quan; *lấy được* tin mới nhưng *hành vi* không đổi.
- Đề xuất **CUPMem**: củng cố trạng thái có cấu trúc **lúc ghi** + tìm có ý thức lan truyền. Tác giả gọi là bước đầu.

Ba bài học cho ta:
1. *Lấy được* đoạn mới chưa đủ — kể cả khi recall đưa cả đoạn "bỏ" lẫn đoạn cũ, agent vẫn có thể làm theo đoạn cũ. → Nhãn phải **rõ và ở trên đầu** ("ĐÃ THAY BỞI …"), không chỉ xếp lại.
2. Phán quyết lúc **đọc** (mỗi lần hỏi, agent tự cân) kém và lặp lại; phán quyết lúc **ghi** (một lần, khi ngữ cảnh còn nóng) mới bền. → *Đáp câu 3 mục 2: người ghi cái mới.*
3. Không có model nào giải xong → phải có **cơ chế ép** + **đo**, không tin vào "model đủ thông minh".

## 7. Mặt trái: đóng cứng (ossification)
SSGM (2603.11768, snippet): nếu lọc nhất quán quá chặt (mọi thông tin mới trái cái cũ đều bị nghi), hệ thống **không học được gì mới** — kiến thức đóng cứng.
Cũng khó tách "trôi" (agent ghi sai dần) với "cập nhật hợp lệ". → Cơ chế thay thế không được biến thành cổng chặn cái mới; nó chỉ *đánh dấu* cái cũ.

## 8. Thang cách làm (vòng 4) — chi tiết hơn

| Cách | Bước nào nó lo | Chi phí | Chỗ gãy |
|---|---|---|---|
| A. Sửa tại chỗ, một chủ đề một file | loại bỏ bài toán (không còn bản cũ) | 0 | chỉ khi kiến thức nằm ở **một** chỗ; transcript cũ vẫn còn |
| B. Frontmatter `status`, `supersedes`, `valid_to` | lưu phán quyết | nhỏ | quên điền |
| C. Hook nhắc lúc ghi (recall 3 đoạn gần nhất → agent điền B hoặc `none`) | phát hiện + ép phán quyết lúc ghi | nhỏ | agent phán sai (STALE: ~50 %) — vẫn hơn không xét |
| D. Ngày làm lưới | — | ~0 | sai với "cùng tồn tại" |
| E. Lint cặp gần nhau không có cạnh | phát hiện sót | nhỏ | báo nhầm |
| G. Cạnh `dựa trên` + lan truyền | lan truyền | vừa | phải có người/agent khai cạnh |
| F. KG + LLM tự phát hiện | cả ba | cao | STALE cho thấy model kém đúng ở việc này |

Đáp "graph có giải được không" (vòng 3): graph là chỗ **lưu** B và **đi** G. Phát hiện (C, E) và phán quyết vẫn cần thứ khác.

## 9. Scale
- Nhỏ: A gần như đủ — sửa tại chỗ, git giữ lịch sử.
- Vừa (Seriously, nhiều phiên, transcript): transcript không sửa được → cần nhãn `cu` (đã có) + B/C cho sổ tay.
- Lớn (nhiều game, nhiều bộ phận): "cùng tồn tại" thành phổ biến (mỗi game một quy ước) → phải có **phạm vi** (scope) cho mỗi kiến thức: game nào, bộ phận nào.
  Không có phạm vi thì quyết định của June "thay" nhầm quy ước NanoSwarm.

## 10. Dừng lần hai — Seriously
- `tools/claude/recall.py`: `is_stale()` = loại "cũ vì đối tượng đổi" (đoạn `chuyện` nhắc file đổi sau ngày đoạn). `doc_outdated()` + regex `SUPERSEDED` =
  tiêu đề ghi "đã thay bởi / (cũ) / superseded" → nhãn. Comment: chỉ **gắn nhãn**, không hạ hạng, vì hạ hạng làm mất 3 câu diễn đạt lại.
  → Theo bài học STALE 1, nhãn phải nổi bật; kiểm xem `fmt()` in nhãn ra sao.
- `company/eval/recall/cases.toml` nhóm `trap` (5 câu bẫy, có trường `stale`): đây là mầm của bộ "STALE nhỏ".
- Memory tầng 1: `feedback_*.md` không có `supersedes`. Thử tìm hai memory nói ngược nhau — đó là bài tập phán quyết.
- Phạm vi: `recall.py` có `--unit` / `prefer` — mầm của "scope".

## 11. Bốn nền tảng
Thuần dữ liệu + quy ước, giống nhau mọi nơi. Liên hệ game: save game có migration (`com.sanne.save`) là cùng bài toán — dữ liệu cũ phải được *biết* là
cũ (version) và *chuyển* (migration) chứ không để code mới đọc nhầm. Version trong save = `valid_to` trong kiến thức.

## 12. Tóm tắt
Kiến thức cũ có ba nguồn và ba quan hệ; máy phát hiện được ứng viên, phán quyết và lan truyền thì khó (STALE 55 %) → phán quyết **lúc ghi**, đánh dấu
chứ không xoá, không để "mới nhất thắng" đè "cùng tồn tại".

**Thuật ngữ:** supersession · correction · coexistence · bitemporal · valid/transaction time · implicit conflict · premise resistance · cascade · ossification · scope.
**Bài sau:** [05g — đo](05g-do-truy-hoi.md).
