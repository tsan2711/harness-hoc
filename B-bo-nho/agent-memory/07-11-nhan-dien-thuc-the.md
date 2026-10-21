# 07-11 — Nhận diện thực thể

> Chuỗi 07, bài 11/12. Đọc ~9 phút.
> **Bạn đã biết:** chữ hiếm là tín hiệu mạnh khi tìm ([07-03](07-03-tim-lai.md)); `keywords` khai báo ([07-05](07-05-nhan-tren-tai-lieu.md));
> đồ thị = nút + cạnh, cạnh có sẵn vs cạnh phải đoán ([07-06](07-06-quan-he-giua-tai-lieu.md)); thí nghiệm cần luật thắng ([07-10](07-10-doi-he-thong-an-toan.md)).

## 1. Chuyện mở đầu

Câu ghi trong nhật ký Quán Nhỏ:

> *Sửa src/payment.ts lỗi TS2345 trong PaymentTests, việc VIEC-42; Lan chê ChartLite chậm trên Android Go*

Nhóm muốn máy tự nhặt ra "các **thứ có tên**" trong câu — để tìm theo chúng (chữ hiếm, trọng số cao) và để nối chúng thành đồ thị
(hai thứ cùng xuất hiện trong một đoạn → một cạnh). Một bộ mẫu chữ đơn giản nhặt được: `src/payment.ts`, `TS2345`, `PaymentTests`,
`VIEC-42`. Sót: `Lan`, `ChartLite`, `Android Go`. Sót ChartLite thì không có cạnh nào nối "ChartLite" với "chậm" hay với "Android Go".

## 2. Dừng 30 giây

- Vì sao mẫu chữ bắt giỏi `TS2345` mà mù `ChartLite`?
- "ChartLite", "Chart Lite", "chartlite", "thư viện CL" — *tìm ra* cả bốn là một việc; *biết chúng là một thứ* là việc khác. Khác thế nào?
- Để nối đồ thị kiểu "cùng xuất hiện", có cần biết "Lan **chê** ChartLite" không, hay chỉ cần biết "Lan và ChartLite ở cùng đoạn"?

## 3. Ba việc hay bị gọi chung một tên

| Việc | Vào → ra | Ví dụ |
|---|---|---|
| **Nhận diện thực thể** (NER) | văn bản → các *đoạn chữ* là thực thể + loại | "ChartLite" → `thư viện`; "Lan" → `người` |
| **Gộp thực thể** | nhiều cách viết → **một** nút | "Chart Lite", "chartlite" → nút `chartlite` |
| **Trích quan hệ** | cặp thực thể + câu → cạnh có nhãn | (Lan, **chê**, ChartLite) |

Đồ thị "cùng xuất hiện" chỉ cần **nhận diện + gộp**, không cần trích quan hệ (câu hỏi 3) — đó là lý do nó rẻ. Đồ thị giàu nhãn ("gây ra",
"chê", "thay") cần cả ba, và trích quan hệ gần như buộc phải dùng LLM — đó chính là "cạnh phải đoán" ở bài 07-06.

**Gộp thực thể** hay bị quên mà lại quyết định chất lượng: không gộp thì "ChartLite" và "Chart Lite" là hai nút, mỗi nút nửa số cạnh, đồ
thị gãy làm đôi. Cách gộp rẻ nhất: chuẩn hoá (chữ thường, bỏ dấu, bỏ khoảng trắng) + một bảng bí danh viết tay.

## 4. Bốn cách nhận diện, trên câu ở §1

**Cách 1 — Mẫu chữ (regex).** Mô tả *hình dạng*: "chữ có dấu `/` và đuôi file" = đường dẫn; "TS + 4 số" = mã lỗi; "kết thúc bằng
Tests" = tên bộ test; "VIEC- + số" = mã việc. Câu hỏi 1: `TS2345` có hình dạng; "ChartLite" chỉ là một từ viết hoa, giống chữ đầu câu.
Ưu: cực nhanh, tất định, không cài gì. Gãy: tên riêng tự nhiên.

**Cách 2 — Từ điển thực thể (gazetteer) dựng từ chỗ đã khai.** Nhiều thực thể quan trọng **đã được viết ra ở đâu đó dạng máy đọc**: tên
thư viện trong file khai báo phụ thuộc (`package.json`), tên class trong code, tên màn hình, danh sách thành viên nhóm, `keywords` trong
nhãn tài liệu (bài 07-05). Gom thành danh sách, tìm bằng so khớp chuỗi (có thuật toán quét một lần mà khớp được hàng nghìn tên).
Ưu: tất định, 0 tiền, biết đúng **thuật ngữ nội bộ** mà không model nào biết. Gãy: thực thể mới chưa ai khai; tên trùng từ thường ("Go"
trong "Android Go" hay động từ "go"?).

**Cách 3 — Model nhỏ chạy trên máy.** Model nhận diện thực thể có sẵn (spaCy; cho tiếng Việt có underthesea, VnCoreNLP, các model dựa
PhoBERT; loại tự đặt nhãn như GLiNER — đưa danh sách loại `["thư viện", "người", "nền tảng"]` mà không cần huấn luyện lại).
Ưu: bắt tên tự nhiên; 0 tiền mỗi lần (model chạy trên máy được phép — bài 07-02). Nhược: model thường được dạy trên báo chí với loại
`người / tổ chức / địa danh` — "ChartLite" không thuộc loại nào; câu trộn Việt–Anh–code làm độ chính xác tụt mạnh; thêm vài trăm MB phụ
thuộc; đổi phiên bản model thì kết quả có thể đổi.

**Cách 4 — LLM.** Hỏi "liệt kê thực thể và quan hệ". Tốt nhất về nghĩa, làm luôn cả gộp và quan hệ. Nhưng tốn tiền × mọi đoạn × mỗi lần
kho đổi, không tất định, có thể bịa. Chỉ hợp lý **theo lô, có người duyệt chi phí, kết quả ghi thành file và được review** (bài 07-02).

## 5. Bảng một lần nhìn

| | `TS2345`, đường dẫn | "ChartLite", "Lan" | Thuật ngữ nội bộ | Tiền | Tất định | Gãy khi |
|---|---|---|---|---|---|---|
| 1. Mẫu chữ | ✓ | ✗ | chỉ nếu có khuôn | 0 | ✓ | tên tự nhiên |
| 2. Từ điển từ chỗ đã khai | ✓ (nếu thêm) | ✓ nếu đã khai | **✓** | 0 | ✓ | thực thể mới, từ đa nghĩa |
| 3. Model nhỏ | thường ✗ | ~ | ✗ | 0 (máy) | ~ | câu lẫn code, sai loại |
| 4. LLM | ✓ | ✓ | ~ | cao | ✗ | tiền, bịa |

**Quy luật:** thực thể có khuôn → mẫu chữ; thực thể đã được khai ở đâu đó → từ điển; chỉ phần còn lại mới đáng một model — và **đo xem
phần còn lại có to không trước khi cài** (bài 07-10).

## 6. Scale

- **Nhỏ:** mẫu chữ + vài chục tên viết tay là đủ.
- **Vừa** (vài nghìn tên class, vài chục dự án/thư viện): từ điển vài nghìn mục, quét chục nghìn đoạn trong vài giây. Cái vỡ là **từ đa
  nghĩa** (tên trùng từ thường) → cần ngữ cảnh (viết hoa, đứng gần đường dẫn) hoặc danh sách loại trừ.
- **Lớn:** thực thể mới xuất hiện nhanh hơn người khai → cần model; và **gộp thực thể** thành bài toán chính (hàng nghìn biến thể tên).

## 7. Bốn nền tảng

Mẫu chữ và từ điển là code thuần, giống nhau trên **Windows / Mac**. Model nhỏ thì khác: chạy CPU được cả hai, nhưng cài thư viện học
máy trên Windows hay vướng bản build; Mac chip Apple có đường tăng tốc riêng. Trên **iOS / Android**, nhận diện thực thể có sẵn trong hệ
điều hành: Apple `NaturalLanguage` (tên người, nơi chốn, tổ chức) và Google ML Kit Entity Extraction (địa chỉ, ngày, số điện thoại,
URL…) — chạy trên máy, không cần mạng; nhưng cùng giới hạn cách 3: chỉ biết loại chung, không biết thuật ngữ của app bạn. Phần thuật
ngữ riêng (tên món, tên cửa hàng) luôn là từ điển tay.

## 8. Tóm tắt

Nhận diện thực thể chỉ tìm *đoạn chữ là thực thể*; gộp biến các cách viết thành một nút; trích quan hệ mới cần LLM. Thứ tự rẻ → đắt:
mẫu chữ cho thứ có khuôn, từ điển dựng từ chỗ đã khai cho thuật ngữ nội bộ, model chỉ sau khi đo thấy thiếu.

**Thuật ngữ:** NER (named entity recognition) · span (đoạn chữ) · entity type (loại) · entity resolution (gộp thực thể) · relation extraction (trích quan hệ) · regex · gazetteer (từ điển thực thể) · co-occurrence (cùng xuất hiện).

**Giờ bạn biết thêm:** máy nhặt "các thứ có tên" ra sao, và vì sao ba việc thường bị gọi chung là một lại có giá rất khác nhau.

---

> **Ví dụ thật: Seriously làm thế này**
>
> - Công cụ tìm của Seriously có mẫu chữ `ENTITY` trong `tools/claude/recall.py`: bắt đường dẫn, mã lỗi Unity (`CS0103`), mã lỗi của các
>   bộ sinh code (`STU0xx`, `SSJ0xx`), tên test, mã việc theo ngày. Thực thể bắt được vào cột riêng của chỉ mục với trọng số **×3**.
> - Chạy thử ngày 2026-10-21 trên câu *"Sửa tools/claude/recall.py lỗi CS0103 trong NanoSwarmTests, việc 2026-10-20-art-trellis-thu-1-nha;
>   Bi chê VFX Graph chậm trên June"*: bắt đủ 4 mã máy; **sót "VFX Graph", "June" (tên game), "Bi"** — đúng ca của bài.
> - Nguồn cho từ điển (cách 2) đã có sẵn trong repo: tên game (`*/game.toml`), tên phòng (`depts/*/unit.toml`), tên package dùng chung
>   (`com.sanne.*`), tên class C#, `keywords`, và bảng đồng nghĩa `synonyms.toml` (một bảng bí danh sơ khai). "June" là ví dụ từ đa nghĩa:
>   tên game hay tháng Sáu.
> - Kế hoạch: thử cách 1 + 2 trước cho bước đồ thị (thí nghiệm), đo nhóm câu nhiều bước; cách 3 chỉ khi còn thiếu rõ.

**Bài sau:** [07-12 — Ghép lại](07-12-ghep-lai.md).
