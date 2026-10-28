# 01 — Đo đúng thứ agent thấy: hit@3, MRR, so cặp, và vì sao số đo phải tất định

> Bài 1 của chuỗi "migrate thực chiến" (mổ **bước 1** ở [bài 00](00-tong-quan.md)). Đọc ~12 phút + lab 5 phút.
> Mang vào: hình "ngữ cảnh = L1, chỉ 3 chỗ" của bài 00; Unity Profiler; biết đọc Python.

## Chuyện mở đầu

27/10, `git push` bị chặn: cổng kiểm báo "para 6/20 < nền 8", tức tìm kiếm *tụt*. Nhưng hôm đó không ai sửa code tìm kiếm. Chạy lại
trên máy thật thì xanh, chạy trong bản checkout sạch thì đỏ. Một con số *nhảy mà code không đổi* thì không đo được gì cả. Cả bài này
là đi từ câu "đo cái gì" tới câu "làm sao để con số đáng tin".

## Dừng 30 giây

Nghĩ về một benchmark FPS trong Unity: bạn đo trong Editor hay trong build, lấy trung bình hay từng frame, chạy 1 lần hay nhiều lần,
và máy đang bận việc khác thì sao. Bốn lựa chọn đó chính là bốn mục dưới đây, chỉ đổi "frame" thành "câu hỏi".

---

## Mạch của bài

```
1. Đo cái agent thật sự thấy (hit@3)  → nhưng hạng 1 và hạng 3 bị tính bằng nhau
2. Thêm vị trí vào điểm (MRR)          → có hai con số trước/sau rồi, so thế nào?
3. So từng câu, không so tổng (McNemar) → mà bao nhiêu câu thì mới đủ để so?
4. Đủ câu (Wilson, ≥ 30 ca)             → đủ câu rồi mà số vẫn nhảy (chuyện mở đầu)
5. Làm cho phép đo tất định             → giờ mới gắn được thành cổng chặn push
```

## 1. Đo cái agent thật sự thấy: hit@k

**Bộ đề vàng** (*gold set*) là một danh sách câu hỏi mà mỗi câu đã biết trước đáp án là đoạn nào. Ở Seriously nó nằm trong
`company/eval/recall/cases.toml`, ví dụ thật:

```toml
{ id = "kw-model-drift", group = "kw",   q = "model_drift models.toml mở phiên",                        gold = ["485170a9"] }
{ id = "para-perf",      group = "para", q = "đo đỉnh hiệu năng ngay lúc bắt đầu phiên chơi",           gold = ["71a03ee7"] }
```

`gold` là mã commit chứa đáp án. Nhóm `kw` dùng đúng chữ trong tài liệu, nhóm `para` (*paraphrase*) nói bằng chữ khác.

**hit@k** = trong k kết quả đầu có đáp án không (có = 1, không = 0), cộng lại trên mọi câu. Trong code chỉ có 2 dòng
(`tools/claude/recall_eval.py`):

```python
first = next((i for i, r in enumerate(rows) if hit(r, case['gold'])), None)   # hạng của đáp án, 0 = đầu tiên
at3[group] += (first is not None and first < 3)                               # hit@3
```

Chọn k bằng bao nhiêu? Bằng **số chỗ thật** trên L1: hook nhét tối đa 3 đoạn vào ngữ cảnh, nên k = 3. Nếu chấm k = 12 thì giống đo FPS
trong Editor, tức là đo một thứ người dùng không thấy. Số thật hôm nay:

| Nhóm (33 câu mỗi nhóm) | @12 | @3 |
|---|---|---|
| kw | 33/33 | 32/33 |
| para | 14/33 | **9/33** |

Với para, 5 câu "trúng" ở @12 thực ra nằm ở hạng 4–12, nên agent không bao giờ đọc tới chúng.

## 2. Thêm vị trí vào điểm: MRR

hit@3 vẫn coi hạng 1 và hạng 3 như nhau. Nhưng agent đọc đoạn đầu kỹ nhất, và đoạn ở hạng 3 còn bị cắt bớt khi ngữ cảnh chật. Giống
cache: trúng L1 khác trúng L3, dù cả hai đều là "hit".

**Reciprocal rank** của một câu = 1 / (hạng tính từ 1). Hạng 1 → 1; hạng 2 → 0,5; hạng 3 → 0,33; không có → 0.
**MRR** (*Mean Reciprocal Rank*) = trung bình các con số đó trên mọi câu.

```python
rr[group].append(1 / (first + 1) if first is not None else 0.0)   # first đếm từ 0, nên +1
mrr = sum(rr[group]) / len(rr[group])
```

Tính tay: 3 câu có đáp án ở hạng 1, 3 và không có → (1 + 0,33 + 0) / 3 = 0,44.

Số thật: kw MRR **0,837**, para **0,216**. Với para, đáp án nếu có thì thường nằm ở hạng thấp, nên MRR cho thấy rõ hơn @3 rằng para yếu.

MRR hợp khi mỗi câu chỉ có **một** đáp án (như ở đây). Bộ đề nhiều đáp án có độ đúng khác nhau thì dùng **nDCG** (cộng điểm của mọi
đáp án, chia theo log của hạng). Các bộ đề lớn ngoài kia như MS MARCO dùng MRR@10, BEIR dùng nDCG@10.

## 3. So từng câu, không so tổng: McNemar

Sửa code xong, para từ 6/33 lên 7/33. Có phải tiến bộ không?

Chưa biết được, vì tổng điểm che mất chuyện bên trong. +1 có thể là được 1, mất 0. Nhưng cũng có thể là được 5, mất 4: sửa một chỗ
làm hỏng 4 câu khác. Giống so 2 bản build bằng FPS trung bình: trung bình tăng mà vẫn có frame spike mới.

**Phép so cặp McNemar** chỉ nhìn các câu **đổi** kết quả:
- n10 = trước trúng, sau trượt (mất)
- n01 = trước trượt, sau trúng (được)

Câu hỏi nó trả lời: *nếu hai bản thật ra tốt như nhau, mỗi câu đổi chiều là tung đồng xu 50/50, thì chia lệch tới mức này hiếm cỡ nào?*
Độ hiếm đó là **p**. p < 0,05 thì coi là khác biệt thật.

```python
def mcnemar(a, b):                       # a, b: {mã câu: trúng?}
    n10 = sum(1 for i in ids if a[i] and not b[i])
    n01 = sum(1 for i in ids if b[i] and not a[i])
    n, k = n10 + n01, min(n10, n01)
    return n10, n01, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n   # nhị thức chính xác, hai phía
```

Số thật (para, nền → hôm nay): **mất 0, được 4, p = 0,125**. Dù được 4 mất 0, vẫn *chưa chắc*: tung 4 đồng xu ra cả 4 sấp thì xác suất
1/16, nhân 2 cho hai phía = 0,125. Phải được **6–0** mới xuống dưới 0,05 (2/64 = 0,031).

Cổng chặn push trong Seriously dùng đúng luật này: chỉ đỏ khi **mất > được và p < 0,05**. Nhờ vậy nó không đỏ vì 1 câu dao động.

## 4. Bao nhiêu câu là đủ: khoảng tin cậy Wilson

9/33 = 27 %. Nhưng nếu đổi sang 33 câu para khác thì có thể ra 20 % hoặc 35 %. **Khoảng tin cậy** cho biết con số thật có thể nằm trong
khoảng nào. Với tỉ lệ, cách tính chuẩn là **Wilson** (tốt hơn công thức sách giáo khoa khi n nhỏ hoặc tỉ lệ gần 0/1).

| Kết quả | Khoảng Wilson 95 % |
|---|---|
| para @3 9/33 | 16 % – 43 % |
| para @3 6/33 | 10 % – 33 % |
| bẫy 3/5 | 30 % – 82 % |

Hai khoảng 6/33 và 9/33 **chồng nhau** rất nhiều, nên chỉ nhìn tỉ lệ thì không phân biệt được. Bẫy 5 câu thì khoảng rộng tới mức vô nghĩa.

Vì vậy luật bộ đề là **mỗi nhóm ≥ 30 câu** (`GATE_MIN = 30` trong code). Nhóm dưới 30 câu chỉ được *báo*, không được *chặn*. Nhóm `trap`
5 câu ở trên in kèm "(chỉ báo, nhóm < 30 ca)".

## 5. Làm cho phép đo tất định

Quay lại chuyện mở đầu. Nguyên nhân: chỉ mục dùng cho eval đọc cả `inbox/`, `reviews/`, `tasks`, là những file thay đổi liên tục và
không phải file nào cũng commit. Máy thật có, bản checkout sạch không có, nên hai bên tìm trên **hai kho khác nhau**.

Ba cách sửa đang có trong code, mỗi cách tương ứng một mẹo benchmark Unity:

| Nguồn nhiễu | Sửa trong `recall_eval.py` | Tương tự benchmark game |
|---|---|---|
| Kho tìm kiếm khác nhau giữa các máy | chỉ index sổ tay + git log (đã commit); kho thật thì **đóng băng** thành `recall-real-snap.sqlite` | đo trên một save cố định, không phải save đang chơi |
| Một lần đo bị máy bận làm chậm | chạy mỗi câu **3 lần, lấy nhanh nhất** | warm-up rồi lấy median/min |
| Máy quá tải làm ms tăng hết | nới trần ms theo `loadavg / số nhân` | không đo khi đang build shader |

**Tất định** (*deterministic*) nghĩa là cùng code + cùng dữ liệu thì luôn ra cùng số. Chỉ khi tất định thì "số tụt" mới có nghĩa là
"code tệ hơn", và lúc đó mới gắn được thành cổng chặn push (`kit selftest` → `recall_eval.py check`).

## So sánh các cách đo

| Cách | Đo được gì | Gãy ở đâu | Dùng khi |
|---|---|---|---|
| hit@12 | có tìm thấy không | đếm cả thứ agent không đọc | hầu như không nên |
| **hit@k, k = số chỗ trên L1** | có lên L1 không | hạng 1 = hạng 3 | chỉ số chính, dễ hiểu |
| **MRR** | lên L1 ở vị trí nào | một đáp án mỗi câu | đi kèm hit@k |
| nDCG | nhiều đáp án, có mức độ | cần chấm độ đúng từng đáp án | bộ đề lớn, nhiều đáp án |
| Chấm tay | đúng ý nhất | không lặp lại được mỗi tuần | lúc dựng bộ đề |
| Đo lúc dùng thật (online) | agent có *mở* đoạn đó không | ít mẫu, nhiễu, khó so | sau cùng (R8 ở Seriously: 25 %) |

## Scale

- **Nhỏ (< 30 câu/nhóm)**: chỉ so cặp từng câu, đọc tận mắt các câu đổi; không đặt cổng tự động.
- **Vừa (30–300, Seriously đang ở đây)**: hit@k + MRR + McNemar làm cổng; Wilson để biết sai số; bộ đề lấy từ commit thật.
- **Lớn (hàng nghìn câu, công cụ tìm kiếm thật)**: nDCG, chấm bằng model (*LLM-as-judge*) có kiểm chéo bằng người, A/B online trên
  người dùng thật. Lúc đó cái khó chuyển từ "đủ câu" sang "đáp án vàng có còn đúng không", vì tài liệu thay đổi.

## Bốn nền tảng

- **Mac** (máy chạy harness): `time.perf_counter` dùng đồng hồ đơn điệu độ phân giải ns; `os.getloadavg()` có sẵn.
- **Windows**: không có `os.getloadavg` (Python báo `AttributeError`). Ai chạy harness trên Windows thì phần nới trần ms phải bắt lỗi
  này và dùng `psutil.cpu_percent()` thay. `perf_counter` dùng QueryPerformanceCounter, vẫn chính xác.
- **iOS / Android**: không chạy eval trên máy. Nhưng cùng nguyên tắc áp cho test hiệu năng game trên thiết bị: Unity Performance Testing
  package đo nhiều mẫu và báo median; máy nóng bị hạ xung (*thermal throttling*), giống "máy quá tải" ở mục 5, nên phải nghỉ máy giữa
  các lần đo và so cặp cùng thiết bị.

## Lab

1. `python3 lab/01_do_recall.py` tính @3, @12, MRR, Wilson, McNemar trên 8 câu đồ chơi. Sửa `RUN_B` để thấy được 3 mất 1 vẫn p = 0,625.
2. Trong Seriously: `python3 tools/claude/recall_eval.py` (0 token, ~20 s) in đúng các dòng số dùng trong bài, kèm danh sách câu trượt.
   Chọn một câu `para-…` trượt, đọc `q` và `gold`, rồi đoán vì sao BM25 trượt. Đó là đề bài của bài 02–03.

## Tóm một dòng

Đo **đúng chỗ** (k = số chỗ trên L1), **có vị trí** (MRR), so **từng câu** (McNemar), **đủ câu** (≥ 30) và **tất định** — thiếu một
trong năm thì con số chỉ là cảm giác.

**Bài sau:** 02 — Tên riêng: vì sao "nhận ra" chưa chắc "tìm ra".
