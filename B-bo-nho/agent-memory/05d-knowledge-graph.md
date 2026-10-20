# 05d — Knowledge graph: nút, cạnh, gộp thực thể, đi trên đồ thị

> Đi kèm [05](05-tranh-luan-kg-vs-recall.md) vòng 2 và 5.

## 1. Câu chuyện

Agent sửa `tools/claude/kit.sh`. Bi hỏi: "sửa vậy có phạm quyết định nào không?". Đáp án nằm ở ADR-0028 ("agent không mở Editor"), mà ADR-0028
không nhắc chữ nào trong diff. Nó chỉ nối với `kit.sh` qua một chuỗi: ADR-0028 → quy định lệnh `kit unity` → lệnh đó nằm trong `kit.sh`.
BM25 không thấy; vector cũng không (ADR nói về "Editor", diff nói về "case $1"). Một tấm **bản đồ quan hệ** thì đi được.

## 2. Dừng 30 giây
- Bạn sẽ vẽ bản đồ này bằng những loại "chấm" nào và những loại "mũi tên" nào?
- Ai vẽ mũi tên? Nếu vẽ tay, bao lâu thì bản đồ sai? Nếu để máy vẽ, nó vẽ sai kiểu gì?
- "stash", "git stash", "cất tạm thay đổi" — một chấm hay ba chấm?

## 3. Cấu tạo

- **Nút (node / entity):** một *thứ*: file, ADR, bộ phận, việc, commit, khái niệm ("git stash"), người.
- **Cạnh (edge / relation):** quan hệ **có hướng, có nhãn** giữa hai nút: `ADR-0028 —quy định→ kit unity`, `task-45 —sửa→ kit.sh`, `ADR-20 —thay thế→ ADR-12`.
- **Bộ ba (triple):** (chủ thể, quan hệ, đối tượng). Cả KG = một tập bộ ba.
- **Thuộc tính:** nút/cạnh mang dữ liệu thêm (ngày, nguồn, độ tin). Mô hình này gọi là *property graph*. (Một họ khác là RDF/ontology — chuẩn hoá chặt
  hơn, hợp dữ liệu liên tổ chức; quá nặng cho ta.)
- **Schema:** danh sách loại nút và loại cạnh được phép. Không có schema → máy (hoặc LLM) sinh ra 300 loại cạnh gần giống nhau ("sửa", "chỉnh", "cập nhật") → đồ thị rối.

Lưu ở đâu: không cần graph database. Hai bảng SQLite là đủ cho cỡ ta:
```sql
nodes(id, type, name)            edges(src, dst, type, ts, source)
```
Đi k bước = truy vấn đệ quy (`WITH RECURSIVE`) hoặc vài vòng lặp Python.

## 4. Gộp thực thể (entity resolution) — chỗ quyết định chất lượng

Câu 3 mục 2. Văn bản viết cùng một thứ bằng nhiều cách. Muốn đồ thị có ích, chúng phải về **một nút**. Ba bước:
1. **Chặn (blocking):** chỉ so các cặp có khả năng giống (cùng chữ đầu, cùng loại) — tránh so mọi cặp.
2. **So khớp (matching):** quyết "cùng hay khác". Bằng luật (đường dẫn y hệt → cùng), từ điển tay, embedding (gần → cùng), hoặc hỏi LLM.
3. **Gộp (merging):** nhập nút, nối lại cạnh.

Hai loại lỗi, **ngược chiều nhau**:
| Lỗi | Ví dụ | Hậu quả |
|---|---|---|
| **Gộp thiếu** (under-merge) | "stash" và "git stash" là hai nút | Hỏi "stash" không tới được kiến thức gắn ở "git stash" → giống BM25 trượt |
| **Gộp nhầm** (over-merge) | "git stash" và "git stash pop" là một nút; hoặc "Grass.shader" của Thousandfold và của June | Kéo kiến thức **sai** vào kết quả, và **không ai thấy** — tệ hơn trượt |

Đây là luận điểm 1 Bi đồng ý ở vòng 5: muốn gộp đúng cách nói khác nhau, phải *hiểu nghĩa* → embedding hoặc LLM. Nghĩa là graph không thoát được bài toán
của vector; nó **dời bài toán sang lúc dựng**.

## 5. Ai vẽ cạnh: tất định vs LLM

| | Tất định (script) | LLM trích xuất |
|---|---|---|
| Nguồn | link markdown, `Task:` trailer, `git log --name-only`, `unit.toml`, đường dẫn trong văn bản | đọc văn bản tự do |
| Phủ | chỉ quan hệ **đã ghi có cấu trúc** | cả quan hệ ngầm ("ghi chú này phản đối quyết định kia") |
| Đúng | gần tuyệt đối | tuỳ model; bịa và gộp nhầm |
| Chi phí | ~0 | token mỗi đoạn; dựng lại = trả lại |
| Tất định | chạy lại y hệt | chạy lại có thể khác |
| Git | dựng từ git, không cần lưu | phải lưu kết quả (vào git để duyệt) |
| Biến thể giữa | **NER + đồng xuất hiện**: một model nhỏ nhận diện thực thể (không LLM), hai thực thể cùng đoạn → cạnh "liên quan". Rẻ, phủ rộng hơn tất định, nhãn cạnh nghèo (chỉ "cùng xuất hiện"). SPRIG dùng kiểu này. | |

## 6. Đi trên đồ thị

- **Láng giềng k bước:** từ nút trong câu hỏi, lấy mọi nút cách ≤ k cạnh. k = 1 đã nhiều; k = 3 thường kéo nửa kho → cần xếp hạng.
- **Đường đi có nhãn:** chỉ đi theo `chi phối`, `sửa` — trả lời đúng loại câu hỏi ("ADR nào chi phối file này").
- **Personalized PageRank (PPR):** đặt "người đi bộ" ở các nút hạt giống (seed — nút khớp câu hỏi, do BM25/vector tìm). Mỗi bước, người đó đi ngẫu nhiên
  theo một cạnh, hoặc với xác suất α (vd 0,15–0,5) **nhảy về hạt giống**. Chạy lâu, đếm nơi người đó hay ghé → điểm. Nút gần hạt giống, nhiều đường nối tới → điểm cao.
  Hay vì: tự cân "gần" và "nhiều đường", không cần chọn k; nhảy về hạt giống giữ cho kết quả không trôi xa câu hỏi.
  Đây là lõi của HippoRAG và SPRIG ([05e](05e-graph-rag.md)).

Chú ý: hầu hết cách đi đều **cần hạt giống**, mà hạt giống đến từ BM25/vector. Graph thường *đứng sau* tìm kiếm, không thay nó. Seed sai → đi đúng
đường tới chỗ sai.

## 7. Graph giỏi gì, dở gì

| Giỏi | Dở |
|---|---|
| Câu **quan hệ / nhiều bước** ("việc nào sửa module mà ADR-12 chi phối") | Câu một bước có lỗ từ vựng — vẫn phụ thuộc seed |
| Giải thích được (chỉ ra đường đi) | Dựng & giữ cập nhật tốn công; schema trôi |
| Lưu quan hệ "thay thế" và thời gian ([05f](05f-ky-uc-cu-va-thay-the.md)) | Không tự *phát hiện* mâu thuẫn |
| Lint cấu trúc (doc mồ côi, link gãy) | Gộp nhầm âm thầm |

## 8. Scale
- Nhỏ: tất định đủ; KG gần như = mục lục có mũi tên.
- Vừa (Seriously): vài chục nghìn nút; vấn đề là **nút trung tâm** (hub) — `kit.sh`, `CLAUDE.md` nối với mọi thứ, đi qua chúng thì "mọi thứ liên quan mọi thứ".
  Cần hạ trọng số hub (giống IDF của BM25).
- Lớn: gộp thực thể thành việc chính; schema cần người giữ; LLM-trích tốn tiền theo kho.

## 9. Dừng lần hai — Seriously
Cạnh tất định đã có sẵn, chưa ai nối thành đồ thị:
- `company/records/tasks.jsonl` (biên bản việc) + trailer `Task:` trong commit (`kit commit`) → `việc —commit→ commit`.
- `git log --name-only` → `commit —sửa→ file`. `recall.py` `last_touch()` đã đọc cái này để gắn nhãn `cu`.
- Cột `ent` trong `recall.py` (`entities()`) → `đoạn —nhắc→ thực thể`.
- `company/units/*/unit.toml`, `company/org.json` → `bộ phận —thuộc→ game`.
- Link markdown trong `docs/`, `depts/*/knowledge/`.
Câu hỏi để tự kiểm: trong 5 nguồn trên, nguồn nào cho cạnh "**thay thế**"? (Không nguồn nào — xem 05f.)

## 10. Bốn nền tảng
Graph lưu bằng SQLite → chạy như nhau trên Windows/Mac/iOS/Android. Graph database chuyên dụng (Neo4j…) là server — chỉ hợp desktop/cloud, không hợp
chạy trên điện thoại. NER model nhỏ chạy được trên cả bốn (như embedding, 05b §9). LLM-trích thì chạy cloud hoặc máy mạnh.

## 11. Tóm tắt
KG = bộ ba (chủ thể, quan hệ, đối tượng); giá trị nằm ở gộp thực thể đúng và cạnh đúng; đi bằng láng giềng hoặc PPR từ hạt giống do tìm kiếm đưa.

**Thuật ngữ:** node · edge · triple · property graph · schema · entity resolution · blocking · over/under-merge · NER · co-occurrence · PPR · hub.
**Bài sau:** [05e — graph-RAG](05e-graph-rag.md).
