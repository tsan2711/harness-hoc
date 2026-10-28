#!/usr/bin/env python3
"""Lab bài 01 — tự tính hit@k, MRR, McNemar, Wilson trên dữ liệu đồ chơi. Chạy: python3 01_do_recall.py

Công thức chép từ tools/claude/recall_eval.py của Seriously (rút gọn, không phụ thuộc gì).
Sửa RUN_A / RUN_B rồi chạy lại để thấy con số đổi thế nào.
"""
from math import comb

# Mỗi câu hỏi: hạng (0 = đầu tiên) của đoạn đúng trong kết quả trả về; None = không có trong 12 kết quả.
RUN_A = {'q1': 0, 'q2': 5, 'q3': None, 'q4': 1, 'q5': 2, 'q6': None, 'q7': 8, 'q8': 0}   # trước khi sửa
RUN_B = {'q1': 0, 'q2': 2, 'q3': None, 'q4': 1, 'q5': 4, 'q6': 0, 'q7': 1, 'q8': 0}      # sau khi sửa


def hit_at(run, k):
    return sum(1 for r in run.values() if r is not None and r < k)


def mrr(run):
    return sum(1 / (r + 1) if r is not None else 0.0 for r in run.values()) / len(run)


def mcnemar(a, b):
    """Chỉ đếm câu ĐỔI kết quả. -> (chỉ A trúng, chỉ B trúng, p)."""
    n10 = sum(1 for i in a if a[i] and not b[i])
    n01 = sum(1 for i in a if b[i] and not a[i])
    n = n10 + n01
    if n == 0:
        return n10, n01, 1.0
    k = min(n10, n01)
    return n10, n01, min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)


def wilson(h, n, z=1.96):
    p = h / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * ((p * (1 - p) + z * z / (4 * n * n)) / n) ** 0.5
    return (c - r) / d, (c + r) / d


if __name__ == '__main__':
    n = len(RUN_A)
    for name, run in (('A', RUN_A), ('B', RUN_B)):
        lo, hi = wilson(hit_at(run, 3), n)
        print(f'{name}: @3 {hit_at(run, 3)}/{n} · @12 {hit_at(run, 12)}/{n} · MRR {mrr(run):.3f} · Wilson @3 [{lo:.2f}, {hi:.2f}]')
    at3 = lambda run: {q: r is not None and r < 3 for q, r in run.items()}
    lost, won, p = mcnemar(at3(RUN_A), at3(RUN_B))
    print(f'so cặp @3: mất {lost} · được {won} · p = {p:.3f}  ({"chắc" if p < 0.05 else "chưa chắc — có thể là nhiễu"})')
    print('\nThử: cần được bao nhiêu câu, mất 0, để p < 0.05?')
    for w in range(1, 8):
        print(f'  được {w}, mất 0 -> p = {mcnemar({i: False for i in range(w)}, {i: True for i in range(w)})[2]:.4f}')
