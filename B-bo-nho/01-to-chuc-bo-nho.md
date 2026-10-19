# Bài 01 — Tổ chức bộ nhớ: lưu gì, lưu đâu, lấy lại thế nào

## 1. Câu chuyện: Mai và con bug "chỉ lỗi trên iOS"

Thứ Hai, agent **Mai** cùng bạn sửa một bug: game crash khi mở shop, **chỉ trên iOS**. Mất 3 tiếng, Mai tìm ra:
shader dùng `half` precision, iOS Metal làm tròn khác, cách sửa là ép `float` ở một hàm. Bạn: "Tuyệt, nhớ nhé."

Thứ Ba, bạn mở phiên mới. Mai chào, rồi ngồi đọc code từ đầu. Bạn hỏi về bug hôm qua — Mai **không biết gì**.

Vì sao? Model **không có trí nhớ giữa các phiên**. Mỗi phiên là một tờ giấy trắng; "ngữ cảnh" (context window)
là tờ giấy đó, đóng phiên là vứt. Cái bạn tưởng là "nhớ" thực ra chỉ là: *trước khi tờ giấy bắt đầu, có ai đó viết sẵn gì lên nó*.

> **Định nghĩa dùng cả series:** bộ nhớ agent = thứ **ghi ra ngoài** phiên + cơ chế **đưa đúng phần cần** trở lại tờ giấy.
> Mọi kiến trúc "memory" (mem0, Letta, vector DB, CLAUDE.md…) chỉ là các cách khác nhau trả lời ba việc:
> **(1) Lưu cái gì · (2) Lưu ở đâu, hình dạng nào · (3) Lấy lại bằng cách nào.**

## 2. Dừng 30 giây — tự thiết kế trước khi đọc tiếp

Không cần trả lời ai, không cần viết. Chỉ làm vậy trong đầu:

- Bạn là kỹ sư, được giao "cho Mai nhớ bug hôm qua". Ngay lúc này, trong đầu bạn hiện ra **cách làm đầu tiên** là gì?
  Giữ nó lại. (Đa số người nghĩ: "ghi lại toàn bộ cuộc hội thoại rồi nhét vào phiên sau". Hãy giữ ý đó, mục 3 sẽ thử nó.)
- Tưởng tượng 1 năm sau, Mai đã giúp bạn 2.000 phiên. Cách của bạn còn chạy nổi không? **Đoán chỗ nó gãy đầu tiên.**
- Đoán thử: trong 3 tiếng đó, phần nào đáng nhớ — cả 3 tiếng, hay một câu?

(Gợi ý để so đáp án: câu cuối có đáp án "một câu" — và việc *chọn ra câu đó* chính là bài toán khó nhất, để dành bài 04.)

## 3. Năm cách tổ chức — thử từng cách trên đúng câu chuyện Mai

Cùng một dữ kiện cần nhớ: *"iOS crash shop = half precision trong `ShopTint()`, ép float."*

### Cách A — Nhét nguyên văn hội thoại vào phiên sau
Ghi 3 tiếng chat (~60.000 token) rồi dán lại.
- **Ưu:** không mất gì, không cần thiết kế.
- **Nhược:** phiên sau tốn gần hết tờ giấy (context ~200k) chỉ để "nhớ"; 10 phiên = tràn. Đa số nội dung là nhiễu (thử sai, log).
- **Gãy ở:** phiên thứ ~3. Đây là chỗ bạn đoán ở mục 2.

### Cách B — Một file ghi chú to (kiểu `notes.md`), nạp hết mỗi phiên
Sau mỗi phiên, Mai viết thêm vài dòng vào cuối file.
- **Ưu:** đơn giản nhất chạy được thật; con người đọc/sửa được; diff bằng git.
- **Nhược:** file lớn dần, **ai cũng đọc hết dù chỉ cần 1 dòng** → tốn token mỗi phiên; càng dài, model càng bỏ sót dòng ở giữa.
- **Gãy ở:** vài trăm dòng. Rất nhiều dự án dừng ở đây và thấy "agent hay quên" — thực ra là nạp quá nhiều.

### Cách C — Nhiều file nhỏ + một mục lục (index) luôn nạp
Mỗi sự kiện một file (`ios-half-precision.md`), cộng file `INDEX` mỗi dòng một câu mô tả. Phiên mới chỉ nạp INDEX;
Mai đọc dòng "ios crash shop → ios-half-precision.md" rồi **tự mở** file đó khi cần.
- **Ưu:** nạp rẻ (chỉ mục lục), mở đúng chỗ, sửa/xoá từng mục dễ, git-friendly.
- **Nhược:** chất lượng phụ thuộc **dòng mô tả trong INDEX** — viết dở thì Mai không biết file đó tồn tại. INDEX cũng phình ở vài trăm file.
- **Gãy ở:** ~vài trăm mục, hoặc khi mô tả hai mục giống nhau.
- **Đây là cách Seriously đang dùng**: `memory/MEMORY.md` là INDEX, mỗi dòng trỏ một file.

### Cách D — Tìm theo từ khoá (BM25 / grep) trên kho file
Không nạp gì sẵn. Khi cần, Mai tự tìm `"iOS" "crash" "shop"` trong kho.
- **Ưu:** kho to bao nhiêu cũng được; chính xác với từ hiếm (tên hàm, mã lỗi); rẻ, chạy local, không cần model embedding.
- **Nhược:** **phải đoán đúng từ**. Nếu ghi chú viết "Metal làm tròn half" mà Mai tìm "crash iOS" → hụt. Không hiểu đồng nghĩa.
- **Gãy ở:** khi cách diễn đạt lúc ghi ≠ lúc hỏi.

### Cách E — Vector (embedding): tìm theo nghĩa
Mỗi ghi chú → một dãy số (vector) biểu diễn nghĩa; câu hỏi cũng thành vector; lấy cái gần nhất.
"crash iOS shop" tìm ra được "Metal làm tròn half" dù không trùng từ.
- **Ưu:** chịu được diễn đạt khác nhau; tốt cho ghi chú dài, mơ hồ.
- **Nhược:** hay trả về cái **na ná nhưng sai** (bug iOS khác); tệ với mã/định danh chính xác; cần model embedding + kho vector (tốn, thêm một thứ để hỏng); khó giải thích vì sao ra kết quả đó.
- **Gãy ở:** kho nhiều mục giống nhau (nhiễu), hoặc khi cần đúng tuyệt đối một mã lỗi.

*(Đồ thị tri thức, LLM tự tóm tắt… là biến thể mở rộng của C–E, vào bài 03. Nắm 5 cách trên là đủ nền.)*

## 4. Bảng so sánh — nhìn một lần

| | A nguyên văn | B một file | C file + INDEX | D từ khoá | E vector |
|---|---|---|---|---|---|
| Tốn token mỗi phiên | rất cao | cao, tăng dần | **thấp, gần cố định** | ~0 (chỉ khi tìm) | ~0 (chỉ khi tìm) |
| Độ chính xác khi cần mã/tên | cao nhưng ngập | trung bình | cao nếu INDEX tốt | **cao** | thấp |
| Chịu diễn đạt khác | – | thấp | thấp | **rất thấp** | **cao** |
| Con người đọc/sửa | khó | dễ | **dễ** | dễ (kho là file) | khó (số) |
| Hạ tầng thêm | không | không | không | nhỏ | model + DB |
| Điểm gãy | ~3 phiên | ~vài trăm dòng | ~vài trăm mục | khác từ | nhiễu/na ná |

**Quy luật rút ra (nhớ cái này là đủ cho bài 01):**
bộ nhớ có hai phần nên tách riêng — **cái luôn nạp (nhỏ, chọn lọc)** và **cái để tìm khi cần (lớn, rẻ)**.
Cách A/B nhét tất cả vào phần "luôn nạp" nên chết sớm. Cách C là "luôn nạp = mục lục, tìm khi cần = file".

## 5. Scale lên: cùng một câu chuyện, ba cỡ

| Cỡ kho | Mai làm gì | Cách hợp |
|---|---|---|
| **~20 ghi chú** (1 dự án nhỏ, vài tuần) | tất cả vừa tờ giấy | B hoặc C, đừng làm phức tạp |
| **~500 ghi chú** (vài tháng, nhiều mảng) | INDEX bắt đầu dài, hai mục dễ giống | C + D (mục lục + tìm từ khoá) |
| **~50.000** (nhiều agent, nhiều năm, cả công ty) | không ai đọc hết; trùng lặp, mâu thuẫn, lỗi thời | cần phân vùng theo chủ đề/bộ phận, tìm hai tầng, và **quên có chủ đích** (bài 04–05) |

Điều bất ngờ: scale không chủ yếu vỡ vì **dung lượng** mà vì **chất lượng** — ghi chú cũ sai vẫn nằm đó, agent tin nó.
Một kho phình mà không dọn còn tệ hơn kho nhỏ.

## 6. Dừng lần hai — brainstorm cho chính Seriously

Không cần trả lời, chỉ nghĩ rồi mở repo kiểm chứng:

- Mở `~/.claude-zzd/projects/<thu-muc-du-an>/memory/MEMORY.md`. Đó là **cách C**. Nhìn từng dòng:
  dòng nào bạn đọc xong **biết ngay** file đó chứa gì và khi nào cần mở? Dòng nào mơ hồ? (Đó là điểm gãy thật của cách C.)
- Repo này còn có `kit recall "<từ>"` — đó là cách nào trong A–E? (Gợi ý: bài 07 harness, BM25.) Nó bù chỗ yếu nào của C?
- Nhìn `company/archive/memory/`: đây là "quên có chủ đích" ở dạng nào? Vì sao dời đi chứ không xoá?

## 7. Bốn nền tảng — bộ nhớ nằm ở đâu

Nguyên lý giống hệt; khác nhau ở **chỗ file được phép nằm** và **ai chạy agent**:

| | Chỗ lưu | Lưu ý |
|---|---|---|
| **Mac** (Claude Code của bạn) | file thường, `~/.claude-zzd/…/memory/` | tự do đọc/ghi, git được |
| **Windows** | file thường, `%USERPROFILE%\.claude\…` | giống Mac; khác dấu `\` và phân biệt hoa/thường (không phân biệt) → tên file trùng chữ hoa/thường sẽ đụng nhau |
| **iOS** | sandbox của app (`Documents/`, `Application Support/`) | app chỉ thấy vùng của mình; muốn chia sẻ giữa app phải qua iCloud/App Group |
| **Android** | `filesDir` nội bộ / `Room`/SQLite | tương tự iOS; dung lượng & quyền bị OS giới hạn, có thể bị dọn khi máy thiếu bộ nhớ |

Trên mobile, agent nhớ thường = SQLite nhỏ (có sẵn FTS5 cho từ khoá = cách D rẻ gần như miễn phí) thay vì vector DB nặng.

## 8. Tóm tắt một dòng
Model không nhớ; **bộ nhớ = ghi ra ngoài + nạp lại đúng phần**. Tách "luôn nạp (nhỏ)" khỏi "tìm khi cần (lớn)";
file + mục lục (C) là điểm khởi đầu đúng; từ khoá (D) và vector (E) là cách *tìm*, không thay cho việc *tổ chức*.

**Bài sau (02):** Tool call — Mai "mở file", "tìm kiếm" bằng cách nào? Vì sao biến bộ nhớ thành *công cụ agent tự gọi* thay đổi cả thiết kế.

### Thuật ngữ
- **Context window**: lượng chữ model nhìn thấy trong một phiên ("tờ giấy").
- **Token**: đơn vị chữ model đếm, ~¾ một từ tiếng Anh; tiếng Việt tốn hơn.
- **INDEX / mục lục**: file nhỏ luôn nạp, mỗi dòng trỏ tới ghi chú đầy đủ.
- **BM25**: thuật toán xếp hạng theo từ khoá (cách D).
- **Embedding / vector**: dãy số biểu diễn nghĩa của một đoạn chữ (cách E).
