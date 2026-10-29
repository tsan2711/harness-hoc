#!/usr/bin/env python3
"""Lab bài 08 — cổng phải biết trả sai: đột biến "không làm", nền cũ, so thẳng vs McNemar, chập chờn theo tải, lint dời cổng.
Chạy: python3 08_cong.py   (chỉ thư viện chuẩn; phần 1 gọi `sh` thật trong thư mục tạm)
"""
import datetime as dt
import os
import random
import subprocess
import tempfile
from math import comb

# ---------- 1. Đột biến: "không làm" phải trượt ----------
CHECKS = {
    'true':                     'true',                                   # 6 việc thật ở Seriously
    'gh workflow run (giả)':    'echo started >> runs.log',               # khởi động run rồi trả 0, không chờ kết quả
    'có file kết quả':          'test -f result.txt',                     # kiểm có làm, không kiểm làm đúng
    'đọc kết luận run':         'grep -qsx success result.txt',            # kiểu `gh run list ... -q .conclusion | grep -qx success`
}


def world(tmp, kind):
    for f in ('result.txt', 'runs.log'):
        p = os.path.join(tmp, f)
        if os.path.exists(p):
            os.remove(p)
    if kind == 'làm đúng':
        open(os.path.join(tmp, 'result.txt'), 'w').write('success\n')
    elif kind == 'làm hỏng':
        open(os.path.join(tmp, 'result.txt'), 'w').write('failure\n')    # CI chạy xong nhưng đỏ (658/678)


print('== 1. Đột biến ==  mỗi lệnh check chạy ở 3 thế giới; cổng tốt: chỉ "làm đúng" mới đạt')
with tempfile.TemporaryDirectory() as tmp:
    for name, cmd in CHECKS.items():
        res = {}
        for kind in ('không làm', 'làm hỏng', 'làm đúng'):
            world(tmp, kind)
            res[kind] = subprocess.run(['sh', '-c', cmd], cwd=tmp).returncode == 0
        verdict = 'TỐT' if res == {'không làm': False, 'làm hỏng': False, 'làm đúng': True} else 'LỎNG'
        print(f'  {name:24} ' + ' · '.join(f'{k}: {"đạt" if v else "trượt"}' for k, v in res.items()) + f'  → {verdict}')
print('  Thử: thêm check `test -s result.txt` (file không rỗng). Nó bắt được "làm hỏng" không?\n')

# ---------- 2. Nền cũ ----------
print('== 2. Nền cũ ==  luật "nền + 15 điểm", kết quả đo 9/33 (số thật 28/10)')
for base in (4, 6):
    need = base / 33 + 0.15
    print(f'  nền {base}/33 → ngưỡng {need:.1%} (≈ {need * 33:.1f}/33) → 9/33 = {9 / 33:.1%} → {"ĐẠT" if 9 / 33 >= need else "TRƯỢT"}')
print('  Commit 3aaa2442e: nền nằm ở 2 chỗ, một chỗ chưa cập nhật. Thử: đọc nền từ một file có ngày đo.\n')


# ---------- 3. So thẳng vs McNemar ----------
def mcnemar(a, b):                       # chép từ tools/claude/recall_eval.py
    n10 = sum(1 for x, y in zip(a, b) if x and not y)
    n01 = sum(1 for x, y in zip(a, b) if y and not x)
    n = n10 + n01
    if n == 0:
        return n10, n01, 1.0
    k = min(n10, n01)
    return n10, n01, min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)


N, BASE_HITS, FLIP, RUNS = 103, 81, 0.02, 2000      # 81/103 = 78,6 % (lần ĐẠT thật); FLIP = tỉ lệ ca trúng bị lật mỗi ngày do chỉ mục sống (ước, không đo)
rng = random.Random(8)
base = [i < BASE_HITS for i in range(N)]


def day(regress):
    up = FLIP * BASE_HITS / (N - BASE_HITS)           # ca trượt lật lên cùng số lượng kỳ vọng → nhiễu thuần, chất lượng thật không đổi
    cur = [(not h) if rng.random() < (FLIP if h else up) else h for h in base]
    hits = [i for i, h in enumerate(cur) if h]
    for i in rng.sample(hits, regress):              # lùi thật: thêm `regress` ca trượt
        cur[i] = False
    return cur


def gate_flat(cur):
    return sum(cur) / N > 0.78


def gate_mc(cur):
    lost, won, p = mcnemar(base, cur)
    return not (lost > won and p < 0.05)


print(f'== 3. So thẳng vs McNemar ==  {N} ca, nền {BASE_HITS} ca ({BASE_HITS / N:.1%}), mỗi ngày vài ca lật hai chiều (trung bình không đổi), {RUNS} lần')
print(f'  ngưỡng 78 % nằm giữa {int(0.78 * N)} và {int(0.78 * N) + 1} ca: {80 / N:.1%} vs {81 / N:.1%} (đúng 2 số đo thật 77,7 / 78,6)')
for regress in (0, 3, 8):
    runs = [day(regress) for _ in range(RUNS)]
    red_flat = sum(not gate_flat(r) for r in runs) / RUNS
    red_mc = sum(not gate_mc(r) for r in runs) / RUNS
    tag = 'đỏ GIẢ' if regress == 0 else 'bắt được'
    print(f'  lùi thật {regress} ca: {tag:8}  so thẳng {red_flat:6.1%}   McNemar {red_mc:6.1%}')
print('  Thử: FLIP = 0.0 (chỉ mục đóng băng) rồi 0.05. Cổng nào đổi nhiều hơn? Lùi 3 ca có đáng chặn không?\n')

# ---------- 4. Tải máy ----------
SLACK_MS = 2.0


def cap(base_ms, lf):                    # công thức trần trong recall_eval.gate
    return max(base_ms * SLACK_MS, 40) * lf


print('== 4. Tải máy ==  trần = max(nền × 2; 40) × load_factor')
print('  test_gate_logic: nền 3 ms, ms đo 80, mong 1 lỗi')
for lf in (1.0, 1.5, 2.0, 3.0):
    errs = int(80 > cap(3.0, lf))
    print(f'    load_factor {lf:3}: trần {cap(3.0, lf):5.1f} → {errs} lỗi  {"ok" if errs == 1 else "← test ĐỎ GIẢ (0 != 1)"}')
print('  Nền đo lúc rảnh vs lúc tải (số thật 29/10), ms thật sau đó 30,82:')
for b in (11.9, 45.8):
    c = cap(b, 1.0)
    print(f'    nền {b:4} ms → trần {c:5.1f} ms → cho phép chậm {c / 30.82:.1f}× trước khi đỏ')
print('  Thử: sửa cap() nhận lf làm tham số và test luôn truyền lf=1 → test tất định trên mọi máy.\n')

# ---------- 5. Lint dời cổng ----------
TODAY = dt.date(2026, 10, 29)
DEFER = [   # dòng 1–2 phỏng theo chuyện thật cổng para; hạn 11-11 của claims có trong backlog; các hạn khác là ví dụ dựng
    {'cổng': 'para@3 +15', 'dời_sang': 'đợt sau', 'chủ': '', 'hạn': '', 'số': '6/33'},
    {'cổng': 'para@3 +15', 'dời_sang': 'đo online', 'chủ': 'harness', 'hạn': '', 'số': '9/33, cần 11/33'},
    {'cổng': 'claims gate', 'dời_sang': 'đo 14 ngày', 'chủ': 'harness', 'hạn': '2026-11-11', 'số': ''},
    {'cổng': 'trúng mảnh', 'dời_sang': 'McNemar', 'chủ': 'harness', 'hạn': '2026-10-20', 'số': '77,7 % vs 78 %'},
    {'cổng': 'ms recall', 'dời_sang': 'đo lúc rảnh', 'chủ': 'harness', 'hạn': '2026-11-05', 'số': '45,8 ms lúc tải ~5'},
]
print('== 5. Lint dời cổng ==  thiếu chủ/hạn = LỖI; quá hạn = TRƯỢT (không phải "chờ")')
for r in DEFER:
    miss = [k for k in ('chủ', 'hạn', 'số') if not r[k]]
    late = r['hạn'] and dt.date.fromisoformat(r['hạn']) < TODAY
    v = 'TRƯỢT (quá hạn)' if late else ('LỖI thiếu ' + ', '.join(miss) if miss else 'ok')
    print(f'  {r["cổng"]:12} → {r["dời_sang"]:12} {v}')
print('  Thử: đổi TODAY sang 2026-11-12 → dòng claims phải TRƯỢT dù vẫn thiếu số.')
