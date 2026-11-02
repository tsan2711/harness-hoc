# 01 — Cái thước đo trí nhớ: hit@3, MRR, so cặp, đủ câu, tất định

> Bài 1 của chuỗi "migrate thực chiến". Đọc ~15 phút + lab 5 phút. Viết lại 11-02 cho dễ theo: một ví dụ 8 câu chạy suốt bài.

## Bài này giải bài toán gì

Agent không nhớ gì giữa các phiên. Nên mỗi khi Bi gõ một câu, harness **tìm** trong sổ (ghi chú, commit cũ) những đoạn liên quan, rồi
dán **3 đoạn đầu** vào ngữ cảnh trước khi agent trả lời (lệnh `kit recall`, hook `recall-hint`). Agent chỉ biết những gì nằm trong 3 đoạn đó.

Vậy câu hỏi cả chuỗi bài phải trả lời là: **bộ tìm kiếm có đưa đúng đoạn vào 3 chỗ đó không?** Muốn sửa bộ tìm kiếm (bài 02–04) thì
trước hết phải có **cái thước** đo nó. Bài này là cái thước. Giống trước khi tối ưu game, bạn phải có Profiler đã.

## Chuyện mở đầu

27/10, `git push` bị chặn. Cổng kiểm nói "tìm kiếm tụt: trước tìm đúng 8 câu, giờ 6". Nhưng hôm đó không ai sửa code tìm kiếm. Chạy lại
trên máy Bi thì xanh, chạy trên bản checkout sạch thì đỏ. Cái thước tự co giãn, nên mọi phép đo trước đó đều đáng ngờ.

## Dừng 30 giây

Hình dung bạn đo FPS một cảnh Unity. Đo trong Editor hay trong build. Lấy trung bình hay nhìn từng frame. Đo 10 frame hay 1.000 frame.
Máy đang compile shader lúc đo thì sao. Tự nghĩ xem mỗi lựa chọn sai thì con số nói dối kiểu gì. Năm mục dưới đây chính là năm lựa chọn
đó, chỉ đổi "frame" thành "câu hỏi".

---

## Ví dụ dùng suốt bài

**Bộ đề vàng** (*gold set*) = danh sách câu hỏi mà mỗi câu ta **đã biết trước** đáp án đúng là đoạn nào. Ta cho bộ tìm kiếm chạy từng câu,
xem đáp án đúng đứng **hạng mấy** trong danh sách nó trả về.

8 câu, đo hai lần: bản **A** (trước khi sửa code) và bản **B** (sau khi sửa). Ô là hạng của đáp án đúng; "—" = không có trong 12 kết quả.

| Câu | q1 | q2 | q3 | q4 | q5 | q6 | q7 | q8 |
|---|---|---|---|---|---|---|---|---|
| A (trước) | 1 | 6 | — | 2 | 3 | — | 9 | 1 |
| B (sau)   | 1 | 3 | — | 2 | 5 | 1 | 2 | 1 |

Câu hỏi: **B có tốt hơn A không, và chắc tới đâu?** Năm mục dưới đây trả lời dần.

## 1. Chỉ đếm cái agent thấy: hit@3

**Ý tưởng.** Agent chỉ đọc 3 đoạn đầu. Đáp án đứng hạng 6 thì cũng như không tìm thấy. Nên ta đếm: *đáp án có nằm trong top 3 không?*
Có = 1 điểm, không = 0. Đó là **hit@3** (*trúng trong 3*). Tổng quát là hit@k, với k = số chỗ thật trong ngữ cảnh.

**Trong ví dụ.**
- A: q1, q4, q5, q8 nằm trong top 3 → **4/8**. Nếu đếm lỏng tới top 12 (hit@12) thì được 6/8, vì có thêm q2 (hạng 6) và q7 (hạng 9).
- B: q1, q2, q4, q6, q7, q8 → **6/8**.

Đếm hit@12 là đo cái agent **không thấy**, giống đo FPS trong Editor rồi tin rằng build cũng thế.

**So CPU cache.** Ngữ cảnh giống cache L1: chỉ có 3 ô. Dữ liệu nằm ở RAM (hạng 4–12) thì CPU vẫn phải đợi; với agent còn tệ hơn, nó
không biết là có để mà đợi.

**Code thật** (`tools/claude/recall_eval.py`):

```python
first = next((i for i, r in enumerate(rows) if hit(r, case['gold'])), None)   # hạng của đáp án, 0 = đầu tiên
at3[group] += (first is not None and first < 3)                               # hit@3
```

**Số thật Seriously** (mỗi nhóm 33 câu). Nhóm `kw` hỏi bằng đúng chữ trong tài liệu, nhóm `para` hỏi bằng chữ khác:

| Nhóm | hit@12 | hit@3 |
|---|---|---|
| kw | 33/33 | 32/33 |
| para | 14/33 | **9/33** |

Nếu chỉ nhìn @12 thì para được 14. Nhưng 5 câu trong số đó nằm ở hạng 4–12, nên agent không bao giờ đọc tới.

## 2. Hạng 1 khác hạng 3: MRR

**Vấn đề còn lại.** hit@3 cho hạng 1 và hạng 3 cùng 1 điểm. Nhưng agent đọc kỹ đoạn đầu nhất, còn đoạn thứ 3 hay bị cắt khi ngữ cảnh chật.

**Ý tưởng.** Cho điểm theo hạng: hạng 1 → 1 điểm, hạng 2 → 1/2, hạng 3 → 1/3, … không có → 0. Điểm này gọi là **reciprocal rank**
(nghịch đảo hạng). Lấy trung bình trên mọi câu thì ra **MRR** (*Mean Reciprocal Rank*). MRR = 1 nghĩa là câu nào đáp án cũng đứng đầu.

**Trong ví dụ.**
- A: (1 + 1/6 + 0 + 1/2 + 1/3 + 0 + 1/9 + 1) / 8 = **0,389**
- B: (1 + 1/3 + 0 + 1/2 + 1/5 + 1 + 1/2 + 1) / 8 = **0,567**

```python
rr[group].append(1 / (first + 1) if first is not None else 0.0)   # first đếm từ 0, nên +1
```

**Số thật:** kw MRR 0,837, para **0,216**. Với para, đáp án nếu có thì thường đứng thấp.

MRR hợp khi mỗi câu có **một** đáp án, như ở đây. Bộ đề mỗi câu nhiều đáp án thì dùng **nDCG** (cộng điểm mọi đáp án, chia theo log của
hạng). Các bộ đề công khai: MS MARCO dùng MRR@10, BEIR dùng nDCG@10.

## 3. Tổng tăng chưa chắc là tốt hơn: so cặp McNemar

**Vấn đề.** B được 6/8, A được 4/8, tức +2. Nhưng nhìn lại bảng:
- B **được** 3 câu mà A trượt: q2, q6, q7.
- B **mất** 1 câu mà A trúng: q5 (từ hạng 3 tụt xuống hạng 5).

"+2" che mất chuyện sửa code đã làm hỏng q5. Giống FPS trung bình tăng mà vẫn có frame giật mới.

**Ý tưởng.** Bỏ qua mọi câu không đổi; chỉ nhìn các câu **đổi kết quả** (ở đây là 4 câu: được 3, mất 1). Rồi hỏi: *nếu A và B thật ra
tốt như nhau, mỗi câu đổi chiều chỉ là tung đồng xu, thì ra lệch 3–1 có hiếm không?*

Tung 4 đồng xu, ra lệch ít nhất 3–1 về một phía (cả hai phía): (1 + 4 + 4 + 1) / 16 = 10/16 = **0,625**. Tức 62 % khả năng chỉ là may.
Con số đó là **p**. Quy ước: p < 0,05 mới coi là khác thật. Phép này gọi là **McNemar** (kiểm định so cặp).

Kết luận cho ví dụ: **B có vẻ tốt hơn, nhưng chưa chứng minh được.**

```python
def mcnemar(a, b):                       # a, b: {mã câu: trúng?}
    n10 = sum(1 for i in ids if a[i] and not b[i])   # mất
    n01 = sum(1 for i in ids if b[i] and not a[i])   # được
    n, k = n10 + n01, min(n10, n01)
    return n10, n01, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n
```

**Số thật** (para, nền → hôm nay): được 4, mất 0, p = 0,125. Vẫn chưa chắc. Phải được **6–0** mới có p = 0,031 < 0,05.

**Cổng chặn push** trong Seriously dùng đúng luật này: chỉ đỏ khi **mất > được và p < 0,05**. Một câu dao động không làm đỏ cổng.

## 4. Bao nhiêu câu mới đủ: khoảng tin cậy Wilson

**Vấn đề.** Ví dụ chỉ có 8 câu. A = 4/8 = 50 %. Nhưng nếu ta chọn 8 câu khác, có thể ra 30 % hoặc 70 %.

**Ý tưởng.** **Khoảng tin cậy** cho biết con số thật có thể nằm trong khoảng nào. Với tỉ lệ đúng/sai mà số câu ít, công thức chuẩn là
**Wilson** (sách giáo khoa hay dùng công thức khác, cho kết quả vô lý khi n nhỏ hoặc tỉ lệ gần 0/1).

| Kết quả | Khoảng Wilson 95 % |
|---|---|
| ví dụ A: 4/8 | 26 % – 74 % |
| ví dụ B: 6/8 | 46 % – 88 % |
| thật, para @3 9/33 | 16 % – 43 % |
| thật, para @3 6/33 | 10 % – 33 % |
| thật, nhóm bẫy 3/5 | 30 % – 82 % |

Hai khoảng của A và B chồng lên nhau gần hết, nên với 8 câu thì không phân biệt nổi. Đó cũng là lý do McNemar ở mục 3 nói "chưa chắc".

**Luật bộ đề Seriously:** mỗi nhóm **≥ 30 câu** (`GATE_MIN = 30`). Nhóm ít hơn chỉ được *báo*, không được *chặn push*. Nhóm bẫy 5 câu
in kèm chữ "(chỉ báo, nhóm < 30 ca)".

## 5. Cái thước không được co giãn: đo tất định

Quay lại chuyện mở đầu. Bộ tìm kiếm lúc chấm đọc cả `inbox/`, `reviews/`, sổ việc. Đây là những file đổi liên tục, và không phải file nào
cũng được commit. Máy Bi có chúng, bản checkout sạch thì không. Hai bên **tìm trong hai kho khác nhau**, nên số khác nhau dù code y hệt.

**Tất định** (*deterministic*) = cùng code + cùng dữ liệu thì luôn ra cùng số. Chỉ khi đó "số tụt" mới có nghĩa là "code tệ đi".

| Nguồn nhiễu | Cách sửa trong `recall_eval.py` | Mẹo benchmark game tương ứng |
|---|---|---|
| Kho tìm khác nhau giữa các máy | chỉ dùng sổ tay + git log (đã commit); kho thật thì **chụp đông** thành `recall-real-snap.sqlite` | đo trên một file save cố định, không phải save đang chơi |
| Một lần đo bị máy bận làm chậm | chạy mỗi câu 3 lần, lấy lần nhanh nhất | warm-up rồi lấy median / min |
| Máy quá tải làm mọi thứ chậm | nới trần ms theo `loadavg / số nhân` | không đo lúc đang build shader |

Có cả năm thứ (đếm đúng chỗ, có hạng, so cặp, đủ câu, tất định) thì mới gắn được thành cổng tự động (`kit selftest` gọi
`recall_eval.py check` trước mỗi push).

## So sánh các cách đo

| Cách | Đo được gì | Gãy ở đâu | Dùng khi |
|---|---|---|---|
| hit@12 | có tìm thấy không | đếm cả thứ agent không đọc | hầu như không nên |
| **hit@k, k = số chỗ trong ngữ cảnh** | có lọt vào ngữ cảnh không | hạng 1 = hạng 3 | chỉ số chính |
| **MRR** | lọt vào ở vị trí nào | chỉ hợp một đáp án mỗi câu | đi kèm hit@k |
| nDCG | nhiều đáp án, có mức độ đúng | phải chấm mức độ từng đáp án | bộ đề lớn |
| Chấm tay | đúng ý nhất | không lặp lại mỗi tuần được | lúc dựng bộ đề |
| Đo lúc dùng thật | agent có *mở* đoạn đó ra đọc không | ít mẫu, nhiễu, khó so | sau cùng |

## Scale

- **Nhỏ (< 30 câu mỗi nhóm):** đọc tận mắt từng câu đổi kết quả; không đặt cổng tự động.
- **Vừa (30–300, Seriously đang ở đây):** hit@3 + MRR + McNemar làm cổng; Wilson để biết sai số; câu hỏi lấy từ commit thật.
- **Lớn (hàng nghìn câu, công cụ tìm kiếm thật):** nDCG, model chấm (*LLM-as-judge*) có người kiểm chéo, A/B trên người dùng thật.
  Khi đó cái khó chuyển thành "đáp án vàng còn đúng không", vì tài liệu thay đổi.

## Bốn nền tảng

- **Mac** (máy chạy harness): `time.perf_counter` là đồng hồ đơn điệu, độ phân giải ns; `os.getloadavg()` có sẵn.
- **Windows:** không có `os.getloadavg` (Python báo `AttributeError`). Chạy harness trên Windows thì phần nới trần ms phải bắt lỗi này và
  dùng `psutil.cpu_percent()`. `perf_counter` chạy trên QueryPerformanceCounter, vẫn chính xác.
- **iOS / Android:** không chạy eval trên máy, nhưng cùng nguyên tắc áp cho test hiệu năng game trên thiết bị. Unity Performance Testing
  package đo nhiều mẫu rồi báo median. Máy nóng bị hạ xung (*thermal throttling*), giống "máy quá tải" ở mục 5, nên phải cho máy nghỉ
  giữa các lần đo và so cặp trên cùng một thiết bị.

## Lab

1. `python3 lab/01_do_recall.py`: tính lại mọi con số của ví dụ 8 câu (@3, @12, MRR, Wilson, McNemar). Sửa `RUN_B` (hạng đếm từ 0)
   cho q5 không tụt nữa, chạy lại và xem p đổi thế nào.
2. Trong Seriously: `python3 tools/claude/recall_eval.py` (0 token, ~20 s) in các dòng số thật của bài, kèm danh sách câu trượt.
   Chọn một câu `para-…` trượt, đọc câu hỏi và đáp án trong `company/eval/recall/cases.toml`, rồi đoán vì sao bộ tìm kiếm trượt.
   Đó là đề của bài 02–03.

## Tóm một dòng

Muốn biết bộ tìm kiếm có tốt lên không: đếm **đúng chỗ agent thấy** (hit@3), **có hạng** (MRR), so **từng câu** (McNemar), **đủ câu**
(≥ 30) và đo **tất định**. Thiếu một trong năm thì con số chỉ là cảm giác.

**Bài sau:** 02 — Tên riêng: vì sao "nhận ra" chưa chắc "tìm ra".
