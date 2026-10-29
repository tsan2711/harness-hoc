#!/usr/bin/env python3
"""Lab bài 04 — trộn nhiều danh sách xếp hạng: cộng điểm vs RRF, hằng k, trọng số W, hạn ngạch. Chạy: python3 04_rrf.py

Chỉ thư viện chuẩn. Danh sách xếp hạng viết tay, dựng theo đúng hình dạng các ca thật của Seriously (bài 04).
Công thức giống `recall.search`: hạng đếm từ 0, điểm = Σ w / (k + hạng).
"""


def rrf(lists, limit=10):
    """lists = [(w, k, [id, ...])]. Lượt đứng trước thắng khi hoà (thứ tự chèn + sort ổn định), như recall.search."""
    sc = {}
    for w, k, ids in lists:
        for rank, d in enumerate(ids):
            sc[d] = sc.get(d, 0.0) + w / (k + rank)
    return sorted(sc, key=lambda d: -sc[d])[:limit], sc


def pos(order, d):
    return order.index(d) + 1 if d in order else None


# ---------- 1. Hai thang điểm khác nhau ----------
print('== 1. Cộng điểm thô vs trộn theo hạng ==')
BASE = {'p': 24.0, 'q': 22.5, 'r': 21.1, 's': 20.3, 'ANS': 17.0}   # lượt thường: nhiều từ đơn khớp → điểm to
BI = {'ANS': 3.1, 'p': 0.4}                                       # lượt cặp âm tiết: cụm hiếm, ít khớp → điểm nhỏ
summed = sorted(set(BASE) | set(BI), key=lambda d: -(BASE.get(d, 0) + BI.get(d, 0)))
print(f'  cộng điểm thô : {summed}   ANS hạng {pos(summed, "ANS")}  (lượt thường át hết, lượt cặp gần như vô hình)')
mm = lambda s: {d: (v - min(s.values())) / ((max(s.values()) - min(s.values())) or 1) for d, v in s.items()}
nb, ni = mm(BASE), mm(BI)
norm = sorted(set(BASE) | set(BI), key=lambda d: -(nb.get(d, 0) + ni.get(d, 0)))
print(f'  chuẩn hoá 0..1: {norm}   ANS hạng {pos(norm, "ANS")}  (được, nhưng hạng 1 của lượt nào cũng thành 1,0 — kể cả lượt chỉ khớp rác)')
order, _ = rrf([(1.0, 1, sorted(BASE, key=lambda d: -BASE[d])), (1.0, 3, sorted(BI, key=lambda d: -BI[d]))])
print(f'  RRF (k=1 / k=3): {order}   ANS hạng {pos(order, "ANS")}  (không cần biết điểm, chỉ cần thứ tự)')
print('  Thử: đổi BI["ANS"] thành 300 → cộng thô đảo ngược hẳn; RRF không đổi gì.\n')

# ---------- 2. Hằng k: đầu bảng dốc hay phẳng ----------
print('== 2. Hằng k ==  điểm một lượt (w=1) theo hạng 1..5')
for k in (1, 3, 5, 60):
    print(f'  k={k:<3}: ' + '  '.join(f'{1 / (k + r):.3f}' for r in range(5)) + f'   hạng1/hạng2 = ×{(k + 1) / k:.2f}')
# ca từ khoá: lượt gốc đã đúng hạng 1; truy vấn viết lại (w=0.3) không chứa đáp án
base, rew = ['ANS', 'a', 'b', 'c'], ['b', 'a', 'c', 'd']
for k in (1, 5):
    order, _ = rrf([(1.0, k, base), (0.3, k, rew)])
    print(f'  ca từ khoá, k={k}: {order[:4]}  ANS hạng {pos(order, "ANS")}  → đóng góp vào MRR {1 / pos(order, "ANS"):.2f}')
print('  k nhỏ = hạng 1 của lượt chính khó bị chiếm. k lớn (60, mặc định trong bài báo gốc) = phẳng, nhiều lượt "bầu" ngang nhau.')
print('  Thử: đặt w của truy vấn viết lại = 1.0 với k=1 rồi xem ANS còn giữ hạng 1 không.\n')

# ---------- 3. Lưới W/K: thắng para nhưng hỏng bẫy ----------
CASES = [  # (tên, nhóm, lượt thường, lượt cặp âm tiết, đáp án, bản cũ)
    ('para-A', 'para', ['p', 'q', 'r', 's', 'ANS'], ['ANS', 'p'], 'ANS', None),          # đáp án sâu ở lượt thường
    ('para-B', 'para', ['p', 'q', 'r', 's'], ['t', 'ANS'], 'ANS', None),                 # đáp án chỉ có ở lượt cặp, hạng 2
    ('para-C', 'para', ['p', 'q', 'ANS', 'r'], ['ANS', 'q'], 'ANS', None),               # đã top 3, đừng làm hỏng
    ('kw', 'kw', ['ANS', 'a', 'b'], ['c', 'd', 'ANS'], 'ANS', None),                     # từ khoá chuẩn, đã hạng 1
    ('trap', 'trap', ['NEW', 'OLD', 'x'], ['OLD', 'x'], 'NEW', 'OLD'),                    # bản cũ chung cụm từ với câu hỏi
]
print('== 3. Quét lưới W (trọng số lượt cặp) × K (hằng k lượt cặp), BASE_K=1 ==')
print('   W    K | para@3 | kw@3 | cũ↑ | ghi chú')
for W in (0.0, 1.0, 2.0, 3.0):
    for K in (1, 3):
        if W == 0 and K == 1:
            continue
        para = kw = stale = 0
        for name, grp, b, bi, ans, old in CASES:
            order, _ = rrf([(1.0, 1, b)] + ([(W, K, bi)] if W else []))
            hit = (pos(order, ans) or 99) <= 3
            para += hit and grp == 'para'
            kw += hit and grp == 'kw'
            stale += bool(old) and pos(order, old) < pos(order, ans)
        note = 'tắt lượt cặp' if W == 0 else ('← cấu hình Seriously chọn' if (W, K) == (1.0, 3) else '')
        print(f'  {W:3.1f}  {K:3} |  {para}/3   | {kw}/1  |  {stale}  | {note}')
print('  Cột para tăng theo W, nhưng hễ cũ↑ > 0 là cổng đỏ: thắng một chỉ số mà hỏng chỉ số khác thì không tính.')
print('  Thử: thêm ca bẫy thứ hai vào CASES (bản cũ ở hạng 1 lượt cặp, bản mới không có ở lượt cặp) rồi quét lại.\n')

# ---------- 4. Hạn ngạch: 3 chỗ trong L1 ----------
print('== 4. Hạn ngạch khi trộn nhiều kho (như memhub.rrf_merge) ==')
RRF_K, RRF_POS = 1, 0.12
PER = {  # kho → kết quả theo hạng của kho đó. M2 = commit (nhiều, khớp chữ tốt), M3 = sổ tay phòng hỏi, M7 = sổ tay phòng kia
    'M2': ['commit-1', 'commit-2', 'commit-3', 'commit-4', 'commit-5'],
    'M3': ['note-mine-1', 'note-mine-2'],
    'M7': ['note-other-1'],
}


def rrf_merge(stores, per, limit, quota=None):
    sc = {}
    for p, s in enumerate(stores):
        w = 1 / (1 + RRF_POS * p)
        for r, h in enumerate(per.get(s, [])):
            sc[(s, h)] = (w / (RRF_K + r), p, r)
    ranked = sorted(sc, key=lambda x: (-sc[x][0], sc[x][1], sc[x][2]))
    if quota:
        used, out = {}, []
        for s, h in ranked:
            if used.get(s, 0) < quota.get(s, 99):
                used[s] = used.get(s, 0) + 1
                out.append((s, h))
        ranked = out
    return [h for _, h in ranked[:limit]]


stores = ['M2', 'M3', 'M7']
print('  top 3, không hạn ngạch :', rrf_merge(stores, PER, 3), ' ← k=1 đã tự xen kẽ: hạng 1 mỗi kho thắng hạng 2 kho nào')
print('  top 6, không hạn ngạch :', rrf_merge(stores, PER, 6))
print('  top 6, M2 tối đa 2 chỗ :', rrf_merge(stores, PER, 6, quota={'M2': 2}), ' ← XDEPT_QUOTA: trần cho kho to, phần còn lại cho sổ tay')
print('  Thử: xoá M3 khỏi PER (phòng hỏi chưa có sổ tay) rồi xem top 3 có bao nhiêu commit, có và không có quota.')


def merge_tiers(tier1, tier2, extra_cap=2):   # chép nguyên từ memhub.py
    return list(tier1) + [s for s in dict.fromkeys(tier2 or []) if s not in tier1][:extra_cap]


print('  merge_tiers: luật chọn [M3, M2] + model gợi ý [M9, M2, M11, M7] →', merge_tiers(['M3', 'M2'], ['M9', 'M2', 'M11', 'M7']))
print('  Bậc 1 (luật, tất định) là sàn: model chỉ được THÊM tối đa 2 kho, không bỏ, không đảo thứ tự.')
