#!/usr/bin/env python3
"""Lab bài 02 — vì sao tìm theo từng âm tiết tiếng Việt trượt, và cặp âm tiết cứu được. Chạy: python3 02_am_tiet.py

Dùng SQLite FTS5 (cùng loại chỉ mục với `kit recall`), tokenizer unicode61 bỏ dấu như harness.
"""
import re
import sqlite3
import unicodedata

DOCS = [
    ('A', 'HQ: thay emoji bằng icon trên giao diện, mỗi phòng một biểu tượng'),                    # đáp án
    ('B', 'đổi màu ảnh nền web sang tông ấm'),
    ('C', 'giao việc vẽ tượng đài; biểu quyết đổi diện mạo trang web; ký tên; ảnh tự vẽ, đổi ảnh'),  # mồi: đủ âm tiết, sai nghĩa
    ('D', 'đổi tên phòng ban'),
    ('E', 'chụp ảnh màn hình mỗi ngày'),
]
Q = 'đổi biểu tượng trên giao diện web từ ký tự sang ảnh vẽ'
STOP = {'tu', 'sang', 'tren', 'cho', 'cua', 'va', 'la', 'mot', 'bang'}


def fold(s):
    s = unicodedata.normalize('NFD', s.lower()).replace('đ', 'd')
    return ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')


c = sqlite3.connect(':memory:')
c.execute("create virtual table t using fts5(id, body, tokenize='unicode61 remove_diacritics 2')")
c.executemany('insert into t values (?, ?)', DOCS)
ws = [fold(w) for w in re.findall(r'\w+', Q)]

single = ' OR '.join(w for w in ws if w not in STOP)
pairs = ' OR '.join(f'"{a} {b}"' for a, b in zip(ws, ws[1:]) if not (a in STOP and b in STOP))


def show(name, q):
    rows = c.execute('select id, round(bm25(t), 2) from t where t match ? order by bm25(t)', [q]).fetchall()
    print(f'{name}: {rows}   (BM25 âm hơn = khớp tốt hơn)')


print('câu hỏi :', Q)
print('từng âm tiết:', single)
show('  -> xếp hạng', single)
print('cặp liền kề :', pairs)
show('  -> xếp hạng', pairs)
print('\nThử: thêm vào DOCS một tài liệu chứa "giao diện" nhưng nói chuyện khác — cặp âm tiết có còn đưa A lên đầu không?')
