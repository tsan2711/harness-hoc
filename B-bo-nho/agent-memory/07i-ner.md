# 07i — NER: nhận diện thực thể (Bi hỏi 2026-10-20)

> Chuỗi 07, bài 9/9. Đọc ~10 phút. Cần trước: [05d KG](05d-knowledge-graph.md), [05e graph-RAG](05e-graph-rag.md), [07d](07d-bang-edges.md).

## 1. Câu chuyện

Đưa câu này qua regex `ENTITY` đang chạy trong `recall.py`:

> *Sửa tools/claude/recall.py lỗi CS0103 trong NanoSwarmTests, việc 2026-10-20-art-trellis-thu-1-nha; Bi chê VFX Graph chậm trên June*

Kết quả thật (chạy 2026-10-21): `tools/claude/recall.py`, `CS0103`, `NanoSwarmTests`, `2026-10-20-art-trellis-thu-1-nha`.
Bắt được hết **mã máy** (đường dẫn, mã lỗi, tên test, id việc). Sót hết **tên người nói**: `Bi`, `VFX Graph`, `June`. Mà SPRIG
([05e](05e-graph-rag.md) §5.3) — graph-RAG 0 token mà bài 06 muốn thử ở P4(b) — dựng đồ thị từ chính những thực thể này: hai
thực thể cùng đoạn → một cạnh. Sót "VFX Graph" thì không có cạnh nào nối "VFX Graph" với "RenderMeshInstanced".

## 2. Dừng 30 giây

- Vì sao regex giỏi `CS0103` mà mù `VFX Graph`?
- "VFX Graph", "VFXGraph", "Visual Effect Graph", "vfx graph" — tìm ra cả bốn là một việc; biết chúng là **một** thứ là việc khác. Khác
  thế nào?
- SPRIG cần biết "Bi *chê* VFX Graph" hay chỉ cần biết "Bi và VFX Graph cùng đoạn"?

## 3. Ba việc hay bị gọi chung là "NER" — câu hỏi 2 và 3

| Việc | Vào → ra | Ví dụ |
|---|---|---|
| **NER** — nhận diện thực thể có tên (named entity recognition) | văn bản → các *đoạn chữ* + loại | "VFX Graph" → `TECH`; "June" → `GAME` |
| **Gộp thực thể** (entity resolution / linking) | nhiều đoạn chữ → **một** nút | "VFXGraph", "Visual Effect Graph" → nút `vfx-graph` |
| **Trích quan hệ** (relation extraction) | cặp thực thể + câu → cạnh có nhãn | (Bi, **bác bỏ**, RenderMeshInstanced) |

Đồ thị kiểu SPRIG cần **NER + gộp thực thể**, **không cần** trích quan hệ: cạnh chỉ là "cùng xuất hiện". Đó là lý do nó rẻ (câu hỏi 3).
KG kiểu Graphiti/GraphRAG cần cả ba — và trích quan hệ là bước buộc phải dùng LLM.

Gộp thực thể thường bị quên mà lại quyết định chất lượng: không gộp thì "VFX Graph" và "VFXGraph" là hai nút, mỗi nút một nửa số
cạnh, PPR đi lạc. Ở Seriously, gộp rẻ nhất là chuẩn hoá (bỏ dấu, chữ thường, bỏ khoảng trắng — `fold()` đã làm phần dấu) + bảng
bí danh viết tay (như `synonyms.toml`).

## 4. Bốn cách làm NER, trên câu ở §1

**Cách 1 — Regex (đang có).** Mẫu cho thứ có *hình dạng*: `[\w.-]+/…` (đường dẫn), `CS\d{4}`, `S[A-Z]{2}\d+`, `Test\w+`, id việc theo
ngày. Câu hỏi 1: `CS0103` có hình dạng; "VFX Graph" chỉ là hai từ viết hoa, giống "Bi Chê" ở đầu câu.
Ưu: µs, tất định, 0 phụ thuộc. Nhược: chỉ bắt thứ có khuôn. Gãy: tên riêng tự nhiên.

**Cách 2 — Từ điển thực thể (gazetteer) dựng từ repo.** Thực thể quan trọng của Seriously **đã được khai ở đâu đó**: tên game
(`game.toml`), tên phòng (`unit.toml`), package `com.sanne.*`, tên class C# (quét `*.cs`), `keywords:` trong frontmatter (07c), tên
API Unity hay dùng. Gom thành danh sách, tìm bằng so khớp chuỗi (Aho–Corasick: một lần quét, nghìn tên).
Ưu: tất định, 0 token, đúng *thuật ngữ nội bộ* mà không model nào biết ("Thousandfold", "GCLess"). Nhược: phải giữ danh sách. Gãy:
thực thể mới chưa ai khai; tên trùng từ thường ("June" — tháng sáu hay game?).

**Cách 3 — Model nhỏ cục bộ.** Model NER đã huấn luyện, chạy CPU: cho tiếng Việt có underthesea, VnCoreNLP, các model dựa PhoBERT;
đa ngữ và **tự đặt nhãn** có họ GLiNER (đưa danh sách loại như `["game", "công cụ", "người"]`, không cần huấn luyện lại).
Ưu: bắt tên tự nhiên; 0 token (đúng 07a: model cục bộ được phép). Nhược: nhãn huấn luyện là `PER/ORG/LOC` của báo chí — "VFX Graph"
không phải loại nào trong đó; câu trộn Việt–Anh–code làm model chuẩn tụt mạnh; thêm phụ thuộc vài trăm MB; không hoàn toàn tất định
giữa các phiên bản model. Gãy: thuật ngữ nội bộ, câu lẫn code.

**Cách 4 — LLM.** Hỏi "liệt kê thực thể và quan hệ". Ưu: tốt nhất về nghĩa, làm luôn cả gộp và quan hệ. Nhược: token × mọi đoạn ×
mọi lần kho đổi; không tất định; bịa thực thể. Chỉ hợp lệ theo **lô, có Bi duyệt tiền, kết quả commit vào git** (P4(c)).

## 5. Bảng một lần nhìn

| | `CS0103`, đường dẫn | "VFX Graph", "June" | Thuật ngữ nội bộ | Token | Tất định | Gãy khi |
|---|---|---|---|---|---|---|
| 1. Regex | ✓ | ✗ | chỉ nếu có khuôn | 0 | ✓ | tên tự nhiên |
| 2. Gazetteer từ repo | ✓ (nếu thêm) | ✓ nếu đã khai | **✓** | 0 | ✓ | thực thể mới, từ đa nghĩa |
| 3. Model nhỏ | thường ✗ | ~ | ✗ | 0 (CPU) | ~ | câu lẫn code, nhãn lệch miền |
| 4. LLM | ✓ | ✓ | ~ | cao | ✗ | tiền, bịa |

**Quy luật:** thực thể có khuôn → regex; thực thể đã được khai ở đâu đó trong repo → gazetteer; chỉ phần còn lại mới đáng một
model, và đo xem phần còn lại có to không trước khi cài.

Cho Seriously, thứ tự hợp lý ở P4(b): **1 + 2** trước (tất định, 0 token, gần như miễn phí vì nguồn tên đã có), đo `multi`; chỉ khi còn
thiếu rõ mới thử 3. Đây là thí nghiệm, nên luật thắng của P4 (07h) vẫn áp: so với hybrid P3.

## 6. Scale

- **Nhỏ**: regex + vài chục tên tay là đủ.
- **Vừa** (Seriously: vài nghìn tên class, vài chục game/phòng/package): gazetteer vài nghìn mục, quét 20k đoạn trong vài giây. Cái vỡ
  là **từ đa nghĩa** ("June", "Art", "QA" vừa là tên vừa là từ thường) → cần ngữ cảnh (viết hoa, gần đường dẫn) hoặc danh sách loại trừ.
- **Lớn**: thực thể mới xuất hiện nhanh hơn người khai → cần model; và **gộp thực thể** thành bài toán chính (hàng nghìn biến thể tên).

## 7. Dừng lần hai — mở Seriously kiểm chứng

- `tools/claude/recall.py` dòng `ENTITY = re.compile(…)` và hàm `entities()` — cách 1, kết quả vào cột `ent` ×3.
- Chạy lại câu §1: `python3 -c "import sys;sys.path.insert(0,'tools/claude');import recall;print(recall.ENTITY.findall('…'))"`.
- Nguồn cho gazetteer (cách 2): `*/game.toml`, `depts/*/unit.toml`, `~/Documents/GitHub/Unity/sanne-kit/Packages/com.sanne.*` (repo riêng), `keywords:` (07c),
  `company/eval/recall/synonyms.toml` (bảng bí danh — gộp thực thể sơ khai).
- `docs/shared/memory-debate-2026-10-20.md` dòng ~58: ghi chú SPRIG ("chưa có số tin cậy").

## 8. Bốn nền tảng

Regex và gazetteer là Python thuần, giống nhau trên **Windows / Mac**. Model nhỏ (cách 3) thì khác: chạy CPU được cả hai, nhưng cài
PyTorch/ONNX trên Windows hay vướng bản build; trên Mac Apple Silicon có thể dùng tăng tốc riêng (MPS/Core ML). Trên **iOS / Android**,
NER có sẵn trong hệ điều hành: Apple `NaturalLanguage` (`NLTagger` với `.nameType` — người, nơi chốn, tổ chức) và Google ML Kit
**Entity Extraction** (địa chỉ, ngày, số điện thoại, URL…) — chạy trên máy, 0 mạng; nhưng cùng giới hạn như cách 3: chỉ loại thực thể
chung, không biết thuật ngữ của game bạn. Trong game, phần "thuật ngữ riêng" luôn là bảng tay (gazetteer) — tên vật phẩm, NPC, khu vực.

## 9. Tóm tắt một dòng

NER chỉ tìm *đoạn chữ là thực thể*; gộp thực thể biến chúng thành một nút; trích quan hệ mới cần LLM. Với Seriously: regex cho thứ có
khuôn + gazetteer dựng từ repo cho thuật ngữ nội bộ, 0 token; model nhỏ chỉ sau khi đo thấy thiếu.

**Thuật ngữ:** NER · span (đoạn chữ) · entity type (loại thực thể) · entity resolution / linking (gộp / liên kết thực thể) · relation
extraction (trích quan hệ) · gazetteer (từ điển thực thể) · Aho–Corasick · co-occurrence (đồng xuất hiện) · domain shift (lệch miền).
**Hết chuỗi 07.** Quay lại [06](06-kien-truc-de-xuat.md) — giờ mỗi dòng trong đó đều có một bài giải thích.
