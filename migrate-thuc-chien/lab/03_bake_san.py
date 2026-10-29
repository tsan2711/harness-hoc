#!/usr/bin/env python3
"""Lab bài 03 — bake câu hỏi (doc2query), ước token trước khi bật, và lỗ trong khoá cache. Chạy: python3 03_bake_san.py

Không gọi model: câu hỏi "đã bake" được viết sẵn theo đúng kiểu prompt v1/v2 của Seriously. SQLite FTS5 giống `kit recall`.
"""
import hashlib
import math
import re
import sqlite3
import unicodedata

# ---------- 1. Bake ----------
COMMITS = {
    'a1': 'web HQ: emoji → icon, mỗi phòng một icon svg',                       # đáp án (bản mới)
    'b2': 'web HQ: icon chữ cái thay ảnh png cho nhẹ',                          # bản CŨ của cùng quyết định
    'c3': 'recall: thêm lượt cặp âm tiết + RRF',
    'd4': 'giao việc theo phòng: route đọc unit.toml',
    'e5': 'ảnh chụp màn hình preview mỗi ngày cho web HQ',
}
V1 = {  # kiểu v1: được dặn đừng chép, vẫn chép chữ commit
    'a1': ['commit nào đổi emoji sang icon trên web HQ?', 'icon svg cho mỗi phòng ở đâu?'],
    'b2': ['commit nào dùng icon chữ cái trên web HQ?', 'thay ảnh png bằng gì?'],
}
V2 = {  # kiểu v2: theo mục đích, không dùng chữ của commit
    'a1': ['đổi biểu tượng các phòng trên trang quản lý để làm gì?', 'vì sao thay ký tự bằng hình vẽ?',
           'làm giao diện dễ nhận ra từng bộ phận hơn', 'thay ký tự bằng ảnh vẽ cho trang điều hành'],
    'b2': ['đổi biểu tượng các phòng trên trang quản lý để làm gì?', 'vì sao trang tải nhanh hơn?',
           'làm giao diện nhẹ hơn', 'thay ảnh bằng ký tự cho trang điều hành'],
}
Q = 'đổi biểu tượng trên giao diện web từ ký tự sang ảnh vẽ'
STOP = {'tu', 'sang', 'tren', 'cho', 'cua', 'va', 'la', 'mot', 'bang', 'de', 'gi', 'vi', 'sao', 'nao'}


def fold(s):
    s = unicodedata.normalize('NFD', s.lower()).replace('đ', 'd')
    return ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')


def rank(baked):
    c = sqlite3.connect(':memory:')
    c.execute("create virtual table t using fts5(id, body, tokenize='unicode61 remove_diacritics 2')")
    c.executemany('insert into t values (?, ?)', [(h, txt + '\n' + ' '.join(baked.get(h, []))) for h, txt in COMMITS.items()])
    q = ' OR '.join(w for w in (fold(x) for x in re.findall(r'\w+', Q)) if w not in STOP)
    return [h for h, in c.execute('select id from t where t match ? order by bm25(t)', [q])]


print('== 1. Bake ==  câu hỏi:', Q, '  (đáp án = a1, bản cũ = b2)')
for name, baked in [('chỉ chữ commit', {}), ('+ câu kiểu v1 ', V1), ('+ câu kiểu v2 ', V2)]:
    r = rank(baked)
    print(f'  {name}: xếp hạng {r}   a1 ở hạng {r.index("a1") + 1 if "a1" in r else "—"}')
print('  Nhìn b2: v2 kéo cả bản cũ lên theo (cùng câu "để làm gì") = bẫy ở mục 5 của bài.')
print('  Thử: xoá câu đầu của V2["b2"] (không bake câu chung cho bản đã bị thay) rồi chạy lại.\n')


# ---------- 2. Ước token ----------
def estimate(n, chars=170, chars_per_tok=1.0, n_q=2, tok_per_q=35, batch=80, overhead=1500, thinking=0.0):
    """-> (vào, ra, tổng). Hệ số chỉnh theo số thật R6b (≈0,40M): tiếng Việt + khung `mã | …` ≈ 1 ký tự/token. thinking = phần ra là suy nghĩ (đo R6b: 212/341 ≈ 0,62 khi chưa tắt)."""
    calls = math.ceil(n / batch)
    tin = n * chars / chars_per_tok + calls * overhead
    tout = n * n_q * tok_per_q / (1 - thinking)
    return round(tin), round(tout), round(tin + tout)


print('== 2. Ước token ==  (số liệu thô; ở repo thật luôn lấy usage từ --output-format json)')
for label, kw in [('R6b: 1478 commit, 2 câu, tắt thinking', dict(n=1478)),
                  ('như trên nhưng thinking bật', dict(n=1478, thinking=0.62)),
                  ('v2: 4 câu', dict(n=1478, n_q=4)),
                  ('lô 1 commit/lượt (không gộp)', dict(n=1478, batch=1))]:
    i, o, t = estimate(**kw)
    print(f'  {label:38} vào {i:>9,} · ra {o:>7,} · tổng {t:>9,}')
print('  Thử: đặt chars_per_tok=4 (quy tắc tiếng Anh) → ước hụt bao nhiêu so với 0,40M thật? Khoản nào to nhất khi không gộp lô?\n')

# ---------- 3. Khoá cache ----------
store = {}


def key_old(text, prompt_ver):            # như doc2query.py: chỉ băm chữ
    return hashlib.sha1(text.encode()).hexdigest()[:10]


def key_new(text, prompt_ver):            # như Unity Library: băm cả "phiên bản importer"
    return hashlib.sha1((prompt_ver + text).encode()).hexdigest()[:10]


print('== 3. Khoá cache ==')
for key in (key_old, key_new):
    store = {h: key(t, 'v1') for h, t in COMMITS.items()}        # đã bake hết bằng prompt v1
    todo = [h for h, t in COMMITS.items() if store[h] != key(t, 'v2')]   # đổi sang prompt v2
    print(f'  {key.__name__}: đổi prompt v1→v2 → {len(todo)}/{len(COMMITS)} commit cần sinh lại')
print('  Khoá phải chứa MỌI thứ làm đổi đầu ra: chữ, prompt, model, số câu.')
