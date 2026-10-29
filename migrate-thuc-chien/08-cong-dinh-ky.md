# 08 — Cổng định kỳ: lệnh kiểm phải biết trả sai

> Bài 8, bài cuối của chuỗi "migrate thực chiến" (mổ **bước 5** ở [bài 00](00-tong-quan.md): giữ cho các số đã đo không trôi; đo bằng thước của [bài 01](01-do-dung-thu-agent-thay.md)).
> Đọc ~15 phút + lab 5 phút. Mang vào: hit@3 + McNemar (bài 01), doc2query (bài 03), cũ↑ (bài 04), Unity Test Runner, Profiler.

## Chuyện mở đầu

Tối 29/10, cổng pre-push đỏ (cũ↑ 1: một bản cũ xếp trên bản mới) và chặn push của mọi phiên. Nguyên nhân là câu hỏi sinh sẵn cho sổ tay (bài 04).
Tắt nó đi, rồi đặt lại *nền* (số đo chuẩn để so) cho bộ đề recall. Cổng xanh lại. Nhưng nền thời gian được đo lúc máy đang tải nặng:
11,9 → 45,8 ms/truy vấn, nên trần thời gian nới từ 40 lên ~92 ms. Từ hôm đó, recall chậm gấp ba vẫn xanh. Cổng xanh, nhưng không còn bắt được gì.

## Dừng 30 giây

Bạn có job CI chạy test hiệu năng mỗi đêm, đỏ thì chặn merge. Tự liệt kê: cách chứng minh job này *có thể* đỏ; con số nền của nó được đo
trên máy nào, lúc nào, ai đo; điều gì xảy ra khi hai lần chạy cùng một code cho ra một xanh một đỏ; và khi nó đỏ ba tuần liền, ai được
phép tắt nó, theo luật gì. Giữ bốn ý đó. Cả bài đi qua đúng bốn ý này, theo thứ tự.

---

## Mạch của bài

```
1. Lệnh kiểm luôn trả 0 (true, gh workflow run)  → cổng phải chứng minh nó trượt được (kiểm đột biến) → nhưng nó so với một con số nền
2. Nền cũ hoặc đo sai lúc                         → ĐẠT sai (nền 4/33) hoặc trần lỏng (45,8 ms) → nền đúng rồi, nhưng so thẳng thì chập chờn
3. So thẳng với ngưỡng: lệch 1 ca là đổi kết luận  → kiểm định cặp (McNemar) → thước đo thời gian vẫn nhiễu theo tải máy
4. Cổng chập chờn theo tải                        → nới theo tải làm chính test của cổng phụ thuộc máy → người ta bắt đầu lờ cổng đỏ
5. Cổng đỏ lâu thì bị dời, bị accept cho qua       → dời phải có chủ + hạn + số đo; cổng chậm 7 phút thì bị timeout và in kết quả cũ
```

## 1. Lệnh kiểm phải biết trả sai

**Cổng** (*gate*) ở đây = một lệnh tự động trả `exit 0` (đạt) hoặc khác 0 (trượt), đặt ở chỗ không cho đi tiếp nếu trượt: pre-push,
`kit selftest`, việc liên phòng (`kit company send … --check <lệnh>`, bên nhận chỉ được đánh dấu xong khi lệnh đó trả 0).

Một cổng có hai cách hỏng. Hỏng ồn: đỏ khi không có lỗi, người ta thấy ngay. Hỏng im: xanh khi có lỗi, không ai thấy. Bài này nói về
cách thứ hai.

**Chuyện thật 28/10.** Việc "sửa 25 test đỏ" trên CI được giao với `--check "gh workflow run …"`. Lệnh này chỉ *khởi động* một lượt CI
rồi trả 0 ngay, không chờ kết quả. Việc được đánh dấu xong. Kiểm tay lúc 14:40: run vẫn đỏ, 658/678, 15 test trượt
(`tools/harness/r11-cutover.md`). Sửa là chặn ngay ở lúc gửi việc (`tools/company/inbox.py`):

```python
# `gh workflow run` chỉ khởi động run → luôn exit 0, việc CI tự "done" khi run còn đỏ (sự cố 10-28); `gh run watch`
# thì quá trần 300 s của run_check. Check phải đọc KẾT LUẬN run đã xong.
if re.search(r'\bgh\s+(workflow\s+run|run\s+watch)\b', kw.get('check', '')):
    print('FAIL --check "gh workflow run|gh run watch": ... Dùng kết luận run mới nhất, '
          'vd --check "gh run list -R <repo> -w <file>.yml -L1 --json conclusion -q \'.[0].conclusion\' | grep -qx success"')
    return 1
```

Rà toàn hộp thư ngày 29/10: **27/243 việc** không có kiểm tra máy thật. 21 việc không có `check:`, 6 việc có `check: true` (lệnh shell
`true` luôn trả 0). Đó là 11 % số việc mà chữ "xong" chỉ là lời tự khai.

**Cách chứng minh một cổng trượt được: kiểm đột biến.** *Mutation testing* (kiểm đột biến) là kỹ thuật chuẩn để đo chất lượng bộ test:
cố ý cài lỗi nhỏ vào code (đổi `>` thành `>=`, xoá một dòng), chạy lại test. Test vẫn xanh thì nó không bảo vệ dòng đó. Công cụ thật:
PIT (Java), Stryker và Stryker.NET (JS, C#), mutmut (Python).

Với cổng, đột biến đơn giản nhất là **"không làm gì"**. Seriously làm đúng như vậy cho bộ đề chấm agent (`tools/eval/selfcheck.py`):

```python
empty, why_empty = attempt(c, suite, head, None)            # worktree sạch, không ai làm gì
good, why_good = attempt(c, suite, head, 'solution.sh')     # chạy lời giải mẫu cạnh case.toml
ok = good and not empty
print(f"{'OK  ' if ok else 'FAIL'} {c['id']}: không làm → {'ĐẠT (đề lỏng!)' if empty else 'trượt'} ..."
      f" · lời giải → {'đạt' if good else 'TRƯỢT: ' + why_good}")
```

Mỗi bài thi chạy hai lần, không cần agent, 0 token. Không làm mà đạt = đề lỏng. Lời giải mẫu mà trượt = đề sai. Test
`test_every_case_tells_right_from_wrong` (`tools/harness/tests/test_eval.py`) gọi nó trong selftest, nên đề lỏng không vào được repo.

Ở CPU, đây là chuyện *fault injection*: muốn biết bộ kiểm ECC có hoạt động không thì cố ý lật một bit rồi xem nó có báo không. Bộ kiểm
chưa từng báo lần nào thì bạn chưa biết nó còn sống.

## 2. Nền: so với cái gì, đo lúc nào

Phần lớn cổng ở đây không có ngưỡng tuyệt đối mà so với **nền** (*baseline*): "không lùi so với lần đo chuẩn". Nền là dữ liệu. Nó có thể cũ,
và có thể đo sai lúc.

**(a) Nền cũ → ĐẠT sai.** Cổng tìm câu diễn đạt lại (para@3, bài 01) có luật "nền + 15 điểm". Nền viết trong code là 4/33, đo từ trước.
Nền đo lại ngày 28/10 là 6/33. Ngưỡng "4/33 + 15 điểm" ≈ 27,1 %, kết quả 9/33 = 27,3 % vừa vượt, nên cổng ghi **ĐẠT**. Theo nền thật, ngưỡng là 11/33 và 9/33
trượt. Commit `3aaa2442e` sửa:

```python
# ngưỡng (§10): para@3 nền ĐO LẠI 6/33 (10-28) + 15 điểm → ≥ 11/33 (brief R6b); KHÔNG hạ ngưỡng để ra ĐẠT; ...
-PARA3_MIN, KW3_MIN, D7_MAX, CLAIMS_CAP = 4 / 33 + 0.15, 30 / 33, 0.25, 100_000
+PARA3_MIN, KW3_MIN, D7_MAX, CLAIMS_CAP = 11 / 33, 30 / 33, 0.25, 100_000
```

Lỗi gốc: nền nằm ở hai chỗ (hằng số trong `tools/claude/memory_gates.py` và file `company/eval/recall/baseline.json`), đồng bộ bằng tay.
Giống hai bản copy của một cache line mà không có giao thức coherence: một bên ghi, bên kia vẫn đọc giá trị cũ. Sửa đúng là cổng đọc nền
từ **một** file, và file đó ghi kèm ngày đo + commit đo.

**(b) Nền đo lúc máy bận → trần lỏng.** Chuyện mở đầu. Trần thời gian trong `tools/claude/recall_eval.py`:

```python
SLACK_MS = 2.0          # ms/query may rise to 2x baseline before the gate trips
...
cap = max(base['ms'] * SLACK_MS, 40) * load_factor()
```

Nền 11,9 ms → trần = max(23,8; 40) = 40 ms. Nền 45,8 ms (đo lúc tải ~5) → trần 91,6 ms. Lần đo `kit memory-gates` sau đó, máy rảnh hơn:
30,82 ms (`company/state/evals/memory-gates/latest.md`). Nghĩa là còn chừa gần 3 lần chậm đi trước khi cổng đỏ. Backlog đã ghi việc
còn lại: "đo ms lúc máy rảnh rồi đặt lại nền ms".

Quy tắc: **đặt nền là một phép đo**, phải ở điều kiện giống lúc cổng chạy thật hoặc tốt hơn, và ghi kèm điều kiện đó. Unity cũng vậy:
không ai lấy số Profiler trong Editor làm nền cho build trên điện thoại.

## 3. So thẳng với ngưỡng, hay kiểm định thống kê

**Chập chờn quanh ngưỡng.** Cổng "trúng mảnh" (memory-eval, 103 ca) có luật `> 78 %`. Ba lần đo thật: 78,6 % (ĐẠT), 76,7 % (TRƯỢT),
77,7 % (TRƯỢT). Quy ra số ca (suy ra từ 103 ca): 81, 79, 80 ca. Ngưỡng 78 % nằm giữa 80 ca và 81 ca, nên **một ca** quyết định kết luận.
Ngày 29/10, ca rơi là `impact-08`. Đo lại với cặp âm tiết tắt và doc2query tắt: vẫn 77,7 %. Vậy không phải do thay đổi đang xét, mà do chỉ
mục sống (sổ tay, commit) đổi mỗi ngày. Lần ĐẠT 78,6 % trước đó cũng thế: +0,6 điểm, lại sau khi chỉnh một tham số trên chính bộ đề.

**Kiểm định cặp.** Bài 01 đã dạy McNemar: chỉ đếm ca *bất đồng* (nền đúng mà nay sai = mất; nền sai mà nay đúng = được), rồi hỏi "nếu hai
lần chạy tốt như nhau, khả năng chia lệch ít nhất thế này là bao nhiêu" (p). `recall_eval.gate` dùng nó cho nhóm ≥ 30 ca:

```python
if 'per_case' in base:                  # R1: groups with >= GATE_MIN cases are gated by a paired test, not by "one case of slack"
    for g in ('kw', 'para', 'trap'):
        if res.get(f'{g}_n', 0) >= GATE_MIN:
            lost, won, p = mcnemar(sub(base['per_case']), sub(res.get('per_case', {})))
            if lost > won and p < 0.05:
                bad.append(f'McNemar {g}: mất {lost} ca, được {won} ca so với nền (p={p:.3f})')
```

Mất 1 được 0 → p = 1,0 → không đỏ. Mất 8 được 0 → p ≈ 0,008 → đỏ. Nhóm nhỏ (bẫy, 5 ca) không đủ ca để kiểm định, nên dùng luật cũ
"lùi quá một ca" và chỉ coi là chỉ báo.

**Cái giá:** McNemar kém nhạy hơn với lùi nhỏ. Lùi thật 2–3 ca trên 103 ca có thể lọt. Lab mục 3 mô phỏng (tỉ lệ lật mỗi ngày là số ước, không đo): khi không có lùi thật, so thẳng
đỏ giả ~39 % số ngày, McNemar ~0,2 %; khi lùi thật 3 ca, McNemar chỉ bắt ~5 %; lùi 8 ca thì bắt ~68 %. Đổi lại, cổng hết đỏ giả.
Cổng đỏ giả nhiều lần thì người ta học cách bỏ qua nó, và lúc đó nó không chặn được gì nữa. Phép so thẳng `> 78 %` trên memory-eval chưa
được chuyển sang McNemar: đây là việc mở trong backlog 29/10.

## 4. Cổng chập chờn theo tải máy

**Cổng chập chờn** (*flaky*) = cùng code, hai lần chạy, một xanh một đỏ. Thời gian là thước đo nhiễu nhất, vì nó đo cả máy chứ không chỉ code.

Seriously chữa ms đỏ giả bằng cách nới trần theo tải (`recall_eval.py`):

```python
def load_factor():
    """Máy quá tải (loadavg 1 phút > số nhân) làm ms đo tăng theo — nới trần theo tỉ lệ tải thay vì đỏ giả."""
    try:
        return max(1.0, os.getloadavg()[0] / (os.cpu_count() or 1))
    except (OSError, AttributeError):                 # Windows: không có os.getloadavg
        return 1.0
```

*loadavg* = số tiến trình trung bình đang chạy hoặc chờ CPU trong 1 phút. Chia cho số nhân: > 1 nghĩa là đang có hàng đợi.

Hậu quả không ai tính trước: chính unit test của logic cổng giờ phụ thuộc máy. `test_gate_logic` (`tools/harness/tests/test_harness_v3.py`):

```python
base = {..., 'ms': 3.0}
self.assertEqual(len(recall_eval.gate({**ok, 'ms': 80}, base)), 1)   # mong 1 lỗi: 80 ms phải vượt trần
```

Trần = max(3 × 2; 40) × load_factor = 40 × load_factor. Khi máy tải gấp đôi số nhân, trần ≥ 80, 80 ms không vượt, test nhận 0 lỗi thay vì 1.
Backlog ghi đúng triệu chứng đó: "xanh lúc rảnh, đỏ (0 != 1) khi `memory-gates` chạy cùng lúc". Giải thích bằng load_factor là đọc code
suy ra; backlog chỉ ghi đã thấy một lần.

Bài học: **test của logic cổng phải tất định**. Truyền load_factor vào làm tham số (test đặt = 1), đừng để hàm đọc trạng thái máy bên trong.
Cùng lý do Unity khuyên đo hiệu năng bằng số *đếm được* (draw call, số lần cấp phát GC, số tam giác) khi có thể, và chỉ dùng ms khi phải.
Số đếm không đổi theo tải; ms thì đổi.

Các cách khác để đo thời gian mà bớt nhiễu:
- **Đo tương đối:** chạy một tải chuẩn cố định ngay trước, báo `ms_cổng / ms_chuẩn`. Máy chậm thì cả hai cùng chậm.
- **Lặp và lấy trung vị:** bỏ đuôi do máy nghẽn tức thời. Performance Testing package của Unity làm vậy (warmup + nhiều lần đo, báo median).
- **Máy riêng cho đo:** runner CI chỉ chạy job đo, không chạy song song job khác.

## 5. Dời cổng, accept cho qua, cổng chậm

**Dời cổng.** Cổng para "+15 điểm" bị dời ba lần trước khi đạt: 27/10 dời sang đợt việc sau; 28/10 đợt đó không đạt (9/33), lại bị
hạ thành "đo online ở đợt sau nữa", mà ở đợt đó chỉ số liên quan chỉ là *chỉ báo*, không có ngưỡng. Trên giấy, cổng vẫn còn. Thực tế nó
đã bị bỏ. Đến 29/10 nó mới đạt thật (12/33, McNemar p = 0,016 so nền) nhờ một việc riêng nhắm đúng vào nó (bài 02).

**Accept cho qua.** Ba việc trí nhớ được bên giao `accept` dù kết quả ghi rõ không đạt: một việc ghi "para +15 dời", một việc ghi
"cổng ≥ 11 không đạt", một việc ghi "selftest còn đỏ ở việc phiên khác". Ở hướng ngược lại, cổng đúng nhưng người duyệt bỏ qua: kết quả giống hệt cổng lỏng.

Luật đề xuất trong backlog: **dời cổng phải ghi cùng dòng ba thứ**:
- *chủ*: ai (phòng nào) chịu đo lại;
- *hạn*: ngày cụ thể; quá hạn mà chưa có số thì cổng tính là **TRƯỢT**, không phải "chờ";
- *số đo*: con số lúc dời và ngưỡng cần đạt.

Giống một `TODO` trong code game: không có tên người và ngày thì nó sống mãi. Lab mục 5 là một lint cho luật này.

**Cổng chậm thì in kết quả cũ.** Tài liệu thiết kế ghi `kit memory-gates` "0 token, ~20 s". Thực tế chạy 7 phút. Lần đầu bị timeout 170 s
nên không ghi file, và `latest.md` cũ vẫn hiện "ĐẠT" của lần trước. Ai đọc file đó thấy xanh, mà cổng chưa chạy. Sửa (đang mở): ghi mốc thời
gian + commit vào bảng, báo lỗi nếu file cũ hơn HEAD. Đây là *stale read* ở tầng báo cáo: dữ liệu đúng ở một thời điểm, đọc ở thời điểm khác.

## So sánh: các kiểu cổng

| Kiểu | Ưu | Gãy ở đâu | Ở Seriously |
|---|---|---|---|
| Không có lệnh kiểm / `true` | 0 công | không bao giờ trượt; "xong" = lời tự khai | 27/243 việc; nay cần lint `kit company lint` |
| Lệnh kiểm "khởi động" (`gh workflow run`) | trông như có kiểm | chỉ kiểm lệnh chạy được, không kiểm kết quả | sự cố 28/10; nay `inbox.py` từ chối |
| So thẳng với ngưỡng cố định | dễ hiểu | lệch 1 ca đổi kết luận; ngưỡng tính từ nền cũ | memory-eval `> 78 %`; para 4/33 → 11/33 |
| Lùi quá N ca so với nền | chịu được nhiễu nhỏ | N chọn tay; nhóm nhỏ thì N = 1 đã là 20 % | nhóm bẫy 5 ca |
| Kiểm định cặp (McNemar) | đỏ khi lùi có ý nghĩa, không vì 1 ca | kém nhạy với lùi nhỏ; cần lưu kết quả từng ca của nền | `recall_eval.gate`, nhóm ≥ 30 ca |
| Trần thời gian × tải máy | hết đỏ giả lúc máy bận | trần lỏng; test của cổng không còn tất định | `load_factor()`, `test_gate_logic` |
| Kiểm đột biến của chính cổng | chứng minh cổng trượt được | tốn gấp đôi lần chạy; cần lời giải mẫu | `kit eval selfcheck` |

## Scale

- **Nhỏ (một người, vài cổng):** mỗi cổng có một ca "không làm phải trượt" viết tay. Nền trong một file, kèm ngày + commit đo.
- **Vừa (Seriously: ~10 cổng, chạy mỗi push + mỗi 10 ngày):** kiểm đột biến tự động cho bộ đề (`selfcheck`), McNemar cho nhóm ≥ 30 ca,
  lint các lệnh `check:` rỗng / `true` / chỉ-khởi-động, cổng định kỳ ghi mốc thời gian, luật dời cổng (chủ + hạn + số). Đo thời gian trên
  một máy rảnh hoặc đo tương đối.
- **Lớn (công ty game, hàng trăm job CI):** máy đo hiệu năng riêng, cố định phần cứng, chạy lặp; lưu chuỗi thời gian và phát hiện
  *điểm gãy* (*change-point detection*) thay vì so với một nền; tự cách ly test chập chờn (*quarantine*: tự động bỏ khỏi cổng chặn, mở việc
  cho chủ test, có hạn); đo tỉ lệ đỏ giả của từng cổng như một chỉ số.

## Bốn nền tảng

Cổng chạy ở máy dev / CI, nhưng số đo phải đại diện cho nơi game hoặc agent chạy thật.
- **Mac:** như trong repo. `os.getloadavg()` có, nên `load_factor` hoạt động. Mac laptop còn bị hạ xung khi nóng: chạy cổng thời gian khi
  đang cắm sạc, đừng chạy song song build Unity.
- **Windows:** không có `os.getloadavg`, `load_factor` trả 1,0 (code có nhánh đó). Cùng một cổng, Windows không nới trần, nên chặt hơn Mac lúc
  máy bận: cùng code có thể đỏ trên Windows mà xanh trên Mac. Unity Test Runner trên CI Windows: chạy `-batchmode -runTests -testResults <file>.xml`
  rồi đọc file kết quả, kiểm cả *số test đã chạy > 0*: filter sai tên khiến 0 test chạy, và 0 test thì không test nào đỏ.
- **iOS:** đo hiệu năng phải trên máy thật, bản *Development Build* nối Profiler, không phải Editor. Nhiệt là "tải" của điện thoại:
  `ProcessInfo.thermalState` cho biết máy đang bị hạ xung. Ghi nó cùng số đo, bỏ lần đo khi máy nóng.
- **Android:** chênh giữa các máy lớn hơn iOS nhiều, nên nền phải gắn với một model máy cụ thể. Trạng thái nhiệt có
  `PowerManager.getCurrentThermalStatus()` (API 29+). Farm thiết bị trên CI cho số đo lặp lại được hơn máy cầm tay.

**So với Unity.** Performance Testing package (`com.unity.test-framework.performance`) là bản Unity của cổng thời gian: `Measure.Method(...)`
với warmup và số lần đo, xuất kết quả theo nhóm mẫu (*sample group*). So với nền là bước riêng (công cụ báo cáo đọc hai file kết quả). Mọi
bẫy trong bài này đều có mặt ở đó: nền đo trên máy khác, so một lần chạy với ngưỡng phần trăm, job CI chạy chung máy với job khác. Profiler
trong Editor thì giống nền 45,8 ms của Seriously: đo được, nhưng không phải điều kiện thật.

## Lab

1. `python3 lab/08_cong.py`: năm phần.
   - **Đột biến**: bốn lệnh `check:` chạy thật bằng `sh` trong thư mục tạm, ở hai thế giới "đã làm" và "không làm". Lệnh nào đạt cả hai = lỏng.
   - **Nền cũ**: cùng kết quả 9/33, ngưỡng tính từ nền 4/33 cho ĐẠT, từ nền 6/33 cho TRƯỢT.
   - **So thẳng vs McNemar**: mô phỏng 103 ca, mỗi ngày vài ca lật do chỉ mục đổi. Đếm tỉ lệ đỏ giả của `> 78 %` và của McNemar, rồi tỉ lệ
     bắt được khi lùi thật 3 và 8 ca.
   - **Tải máy**: chép công thức trần ms của repo; xem `test_gate_logic` đổi kết quả theo loadavg, và nền 45,8 cho phép chậm bao nhiêu.
   - **Lint dời cổng**: sổ dời có dòng thiếu chủ, thiếu hạn, quá hạn chưa số.
2. Trong Seriously: `python3 tools/eval/selfcheck.py` (cần worktree, vài phút). Rồi đọc `company/state/evals/memory-gates/latest.md` và tự
   trả lời: dòng nào là so thẳng sát ngưỡng, dòng nào không có ngày đo.

## Tóm một dòng

Một cổng chỉ có giá trị khi **chứng minh được nó trượt** (đột biến "không làm"), **so với nền mới, đo đúng điều kiện**, **đỏ theo kiểm định
chứ không theo một ca**, **tất định với tải máy**; và khi phải dời thì dời có chủ, có hạn, có số.

**Bài sau:** hết chuỗi "migrate thực chiến". Đọc lại [bài 00](00-tong-quan.md) để thấy cả mạch năm bước một lần nữa.
