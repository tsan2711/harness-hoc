# 00 — Toàn cảnh: trí nhớ của agent là một hệ cache, và 3 ngày sửa nó

> Bài 0 của chuỗi "migrate thực chiến". Đọc ~10 phút. Cả bài đi theo **một mạch**: mỗi mục sinh ra vấn đề của mục sau.
> Kiến thức bạn mang vào: CPU cache (L1/L2/L3, dirty, cache line) và Unity (`.meta`/GUID, Profiler, bake lightmap).

## Chuyện mở đầu

Agent hỏi harness: "vì sao mình bỏ cách vẽ lá bằng texture?". Harness trả về 12 đoạn tài liệu *gần đúng*, nhưng agent chỉ đủ chỗ
đọc 3 đoạn. Đoạn đúng nằm ở hạng 7, nên agent không bao giờ thấy nó, rồi tự đoán và làm lại đúng cái sai cũ.

## Dừng 30 giây

Hình dung cửa sổ ngữ cảnh của agent là **L1 cache**, toàn bộ repo là **RAM**. Thử tự vẽ ra: L1 nhỏ cỡ nào, ai quyết định dòng nào được
nạp vào L1, và khi RAM đổi thì dòng cũ trong L1 thành gì. Giữ hình đó trong đầu: cả bài chỉ là đi lần lượt qua từng câu đó.

---

## 1. Tấm bản đồ: harness = một hệ phân cấp bộ nhớ

| CPU | Harness của Seriously | Đặc điểm chung |
|---|---|---|
| Thanh ghi / L1 | **Ngữ cảnh** của agent: chỉ nhét được ~3 đoạn tài liệu mỗi lần hỏi | nhỏ, đắt (token = tiền), nhanh |
| L2/L3 | **Chỉ mục recall**: bảng tra từ khoá → đoạn tài liệu (BM25, giải ở dưới) | to hơn, phải *tra* mới có |
| RAM / đĩa | **Repo**: docs, commit, inbox, code | chứa hết, nhưng agent không đọc nổi hết |
| Bộ nạp (prefetcher) | **Recall**: chọn đoạn nào từ L2/L3 đưa lên L1 | đoán đúng thì nhanh, đoán sai = *cache miss* |
| Dirty bit / invalidation | **Nhãn "nghi cũ"**: tài liệu B dựa vào A, A vừa sửa thì B bị đánh dấu | đọc B thì phải biết B có thể đã cũ |

*BM25* = cách chấm điểm tìm theo chữ: chữ hiếm mà khớp thì điểm cao, chữ phổ biến ("là", "của") gần như 0 điểm. Không dùng model, 0 token, ~20 ms.

Ba ngày migrate (26–28/10) là sửa đúng 4 chỗ trên bản đồ này, theo thứ tự: **đo hit rate → sửa prefetcher → sửa invalidation → chuyển RAM sang máy khác**.

## 2. Bước 1 — Đo sai chỗ (giống Profiler đo trong Editor thay vì trong build)

**Vấn đề.** Trước đây harness được chấm "đáp án đúng có nằm trong 12 kết quả đầu không" (gọi là **@12**). Nhưng L1 chỉ chứa 3, nên
con số @12 giống đo FPS trong Editor: đẹp, mà không phải thứ người chơi thấy.

**Sửa.** Chấm **@3**: đáp án có lọt vào 3 kết quả đầu không, tức là có thật sự lên L1 không.

**Lộ ra gì.** Có hai loại câu hỏi:
- *Câu dùng đúng chữ trong tài liệu* (ví dụ hỏi "SwarmPetal shader"): 32/33 câu trúng ở @3. Tốt.
- *Câu diễn đạt lại* (gọi tắt **para**: hỏi "cánh hoa bay vẽ bằng gì", tài liệu viết "SwarmPetal"): @12 trúng 14/33, nhưng @3 chỉ còn **9/33**.

→ BM25 tìm theo chữ nên câu đổi chữ thì trượt. Đó là vấn đề của bước 2.

**Một chi tiết đo cần biết.** Sửa xong mà para tăng 6 → 7/33 thì *chưa* nói được là tiến bộ. Lý do: có thể được 3 câu mới, mất 2 câu cũ.
Vì vậy harness so **từng câu** trước/sau (phép **McNemar**: chỉ đếm số câu đổi kết quả). Giống so 2 bản build bằng Profiler theo từng
frame chứ không so FPS trung bình. Thêm nữa, mỗi nhóm cần ≥ 30 câu thì phép so mới có nghĩa.

## 3. Bước 2 — Sửa prefetcher: "thông minh hơn" thua, "bake sẵn" thắng

Có 4 ý nghe hợp lý để para tìm tốt hơn. Cả 4 đều được đo bằng @3 + so từng câu ở bước 1:

| Ý tưởng | Tương tự Unity/CPU | Kết quả |
|---|---|---|
| Viết lại câu hỏi bằng luật lúc hỏi | đổi tên biến cho "dễ đoán" | 6/33 → 6/33: **vô ích**, tắt |
| Nhận diện tên riêng ("bầy" ≠ "bay") | thêm bảng tra tên | nhận ra 85 % câu, nhưng **tìm không tốt hơn**, tắt |
| Trộn mạnh kết quả nhiều kho | gộp nhiều cache, mỗi cái một kiểu điểm | câu liên phòng **tụt 33 → 13 %**, tắt |
| **doc2query**: lúc *ghi* commit, model đoán sẵn "người ta sẽ hỏi gì về đoạn này" và lưu kèm | **bake lightmap**: tính đắt một lần lúc build, lúc chạy chỉ đọc | para **6 → 9/33**, giữ |

**Vì sao doc2query thắng.** Vấn đề của para là *chữ trong câu hỏi ≠ chữ trong tài liệu*. Doc2query thêm sẵn "chữ của người hỏi" vào
tài liệu, nên BM25 khớp được, mà lúc hỏi vẫn 0 token. Ba ý kia làm phần *đoán* lúc hỏi, mỗi lần một lần, lại đoán sai.

**Sửa nhỏ cho ý trộn.** Trộn theo *thứ hạng* thay vì điểm thô (**RRF**: mỗi kho xếp hạng riêng, hạng 1 của kho nào cũng ngang nhau),
và kho commit chỉ được giữ tối đa 2 chỗ (*hạn ngạch*, một trần, xem bài 04). Câu liên phòng 33 → 47 %. Giống chia băng thông: không để một kho chiếm hết 3 chỗ L1.

**Giá.** Doc2query gọi model, nên trước khi bật đã *ước* token: 0,42M, thật hết 0,40M. Lần thí điểm trước đó không ước nên lệch ×5.

→ Đã lên đúng đoạn. Nhưng nếu đoạn đó *đã cũ* thì sao? Bước 3.

## 4. Bước 3 — Invalidation: đúng chuyện dirty bit anh đã hỏi

**Cơ chế.** Harness giữ một **đồ thị**: mũi tên "B dựa vào A" (GDD trích `SwarmPrototype.cs`, ADR trích GDD…). Khi commit sửa A, máy đi
*ngược* mũi tên tìm mọi B và dán nhãn **nghi cũ**, giống ghi vào một cache line thì các bản sao của line đó ở core khác bị đánh invalid.

**Vấn đề: báo động giả.** Lúc đầu có **82** cảnh báo nghi cũ, gần hết là sai, nên người ta thôi đọc. Nguyên nhân giống **false sharing**:
một loại mũi tên (`refs`, "có nhắc tới") nối quá rộng, sửa một chỗ thì cả cụm bị đánh invalid dù nội dung chẳng liên quan.

**Sửa.** Bỏ loại mũi tên đó khỏi việc lan nhãn (vẫn giữ để tìm kiếm). 82 → **2**, và cả 2 đều đúng.

**Bài học.** Invalidation quá rộng cũng hỏng như không có invalidation, vì tín hiệu chìm trong nhiễu.

→ Đồ thị dựa vào mũi tên. Mũi tên ban đầu trỏ bằng *đường dẫn file*, mà bước 4 lại chuyển file đi chỗ khác.

## 5. Bước 4 — Chuyển RAM sang máy khác (tách repo)

**Vì sao tách.** Một repo chứa 3 game + 7 phòng ban, mỗi lần clone 4,9 GB. Sau khi tách: Thousandfold và depts thành repo riêng, clone
còn **375 MB**.

**Vấn đề 1: liên kết gãy.** Mũi tên trỏ bằng đường dẫn thì chuyển file là gãy. Cách sửa chính là cách Unity đã làm: mỗi asset có
**GUID trong `.meta`**, scene trỏ GUID chứ không trỏ đường dẫn, nên kéo file sang thư mục khác không gãy gì. Harness làm y vậy với
`kg://id`: 36 tham chiếu bằng đường dẫn → 0.

**Vấn đề 2: script cũ gọi `../tools/...`.** Thay vì sửa mọi script, repo tách có **lớp phủ**: các symlink ngược `tools → hub`,
`docs → hub`. Đứng trong repo game vẫn thấy cây thư mục như cũ (giống mount một ổ mạng vào đúng đường cũ). Hai cách khác đã cân nhắc:
*git submodule* (mỗi lần sửa tools phải cập nhật con trỏ ở 2 repo) và *giữ monorepo* (không giảm 4,9 GB).

**Vấn đề 3: lỗi không nằm trong game.** Code game không hỏng dòng nào. Gần như mọi lỗi nằm ở script xung quanh, vì chúng ngầm coi
"tất cả ở một repo". Ba ví dụ, mỗi cái là một bài học:
- *Đường dẫn có 2 mặt*: đi qua symlink thì `cd` giữ đường "ảo" nên tính sai gốc repo. Sửa: lấy `realpath`.
- *Biến môi trường rò*: hook ở repo game gọi git ở hub nhưng mang theo `GIT_INDEX_FILE` của repo game, nên báo "1836 file đổi". Sửa: xoá mọi biến `GIT_*`.
- *Chuyển nhà làm lộ đồ hỏng cũ*: cạnh "hay sửa cùng nhau" bằng 0 từ ngày đầu do lệnh git sai mà bị nuốt lỗi, đến lúc chuyển mới thấy.

**Giá.** 18 % việc giờ phải commit ở 2 repo, nên `kit commit` tự chia commit theo repo.

## 6. Bước 5 — Giữ cho nó đúng: cổng định kỳ

Mọi số ở trên chỉ đúng tại 28/10. Nếu không đo lại thì nó trôi dần, giống perf regression trong game. Vì vậy `kit memory-gates` chạy
bộ đề có đáp án (103 câu theo mục đích + 33 câu para) mỗi 10 ngày, 0 token, ~20 s, và đỏ nếu tụt ngưỡng. Một chi tiết: **lệnh kiểm phải
có khả năng trả sai**. Có lần việc CI được đánh dấu "xong" dù test đỏ, vì lệnh kiểm `gh workflow run` lúc nào cũng trả 0.

Còn mở: **R8**, tức đoạn bơm lên L1 có được agent *mở ra dùng* không, mới đo được 25 % trên mẫu nhỏ. Khoảng 07/11 sẽ đủ số để đặt ngưỡng.

---

## Cả mạch trong một dòng

```
đo @3 (thấy L1 chỉ 3 chỗ) → lộ para yếu → bake sẵn câu hỏi (doc2query) thắng, đoán lúc hỏi thua
   → đúng đoạn nhưng có thể cũ → nhãn nghi cũ, bỏ false sharing (82→2)
   → nhãn dựa vào liên kết → liên kết bằng ID như GUID Unity → nên chuyển nhà được (4,9 GB→375 MB)
   → chuyển nhà làm lộ lỗi script → cổng định kỳ để không trôi lại
```

**Quy luật chung:** ở harness, *đo đúng chỗ* và *bớt nhiễu* thắng *làm thông minh hơn*; việc đắt thì làm lúc ghi (bake), đừng làm lúc đọc.

## Bốn nền tảng (chỉ chỗ khác nhau)

- **Mac** (máy đang chạy): symlink, `realpath`, `lsof +D` (xem ai đang mở thư mục) đều có sẵn.
- **Windows**: symlink cần Developer Mode, git mặc định `core.symlinks=false` (symlink thành file chữ), nên thư mục dùng *junction* `mklink /J`; xem ai giữ file bằng `handle.exe`.
- **iOS**: không chạy harness trên máy; build Xcode trên Mac đi qua symlink bình thường.
- **Android**: không chạy harness trên máy; Gradle đi theo symlink được, nhưng Unity export nên trỏ đường vật lý; CI chạy được trên Linux runner.

## Các bài sau mổ từng bước

| Bài | Mổ bước nào |
|---|---|
| 01 Đo đúng thứ agent thấy (@3, MRR, McNemar) | bước 1 |
| 02 Tên riêng: vì sao "nhận ra" chưa chắc "tìm ra" | bước 2, hàng 2 |
| 03 Bake sẵn: doc2query, ước token trước | bước 2 |
| 04 Trộn nhiều kho: RRF và hạn ngạch | bước 2 |
| 05 Invalidation: nhãn nghi cũ, false sharing, ID ổn định | bước 3 + 4 |
| 06 Chuyển nhà: lớp phủ symlink vs submodule vs monorepo | bước 4 |
| 07 Lỗi chuyển nhà: đường dẫn 2 mặt, biến môi trường rò | bước 4 |
| 08 Cổng định kỳ: lệnh kiểm phải biết trả sai | bước 5 |
