#!/usr/bin/env python3
"""Lab bài 05 — nghi cũ (dirty bit theo đồ thị), false sharing, ngày vs supersedes, ID ổn định. Chạy: python3 05_nghi_cu.py

Chỉ thư viện chuẩn. Luật nhãn ở mục 3 chép rút gọn từ tools/claude/recall.py (tier_of, is_stale, thứ tự sắp)."""
import hashlib

# ---------- 1. False sharing theo loại cạnh ----------
# cạnh (A, B, loại) = "A dựa vào B". Sửa B -> A nào nghi cũ?
EDGES = [
    ('adr-economy.md',  'gdd-swarm.md',        'depends_on'),
    ('gdd-swarm.md',    'SwarmPrototype.cs',   'implements'),   # (đơn giản hoá chiều: GDD nói về code)
    ('test-plan.md',    'SwarmPrototype.cs',   'tests'),
    ('INDEX.md',        'gdd-swarm.md',        'refs'),
    ('INDEX.md',        'adr-economy.md',      'refs'),
    ('onboarding.md',   'gdd-swarm.md',        'refs'),
    ('weekly-10-20.md', 'gdd-swarm.md',        'refs'),
    ('roadmap.md',      'SwarmPrototype.cs',   'refs'),
]
STRUCT = ('depends_on', 'implements', 'derived_from', 'tests')        # = REV_TYPES của kg.py


def suspects(changed, types, hops=2):
    out, front = set(), {changed}
    for _ in range(hops):                                              # đi NGƯỢC mũi tên ≤ 2 bước (như thiết kế §4)
        front = {a for a, b, t in EDGES if b in front and t in types} - out
        out |= front
    return sorted(out)


print('== 1. False sharing theo loại cạnh ==  sửa SwarmPrototype.cs')
for name, types in [('lan qua cả refs  ', STRUCT + ('refs',)), ('chỉ cạnh cấu trúc', STRUCT)]:
    s = suspects('SwarmPrototype.cs', types)
    print(f'  {name}: {len(s)} nghi cũ {s}')
print('  INDEX/onboarding/weekly chỉ "nhắc tới" GDD; chúng không sai khi code đổi. Repo thật: bỏ refs -> 82 -> 2.')
print('  Thử: thêm cạnh co_change ("hay sửa cùng nhau") giữa roadmap.md và SwarmPrototype.cs vào STRUCT rồi chạy lại.\n')

# ---------- 2. Hạt file vs băm đoạn ----------
GDD_V1 = {'§3 Kinh tế': 'mỗi đàn ăn 2 đơn vị năng lượng / giây',
          '§9 Ghi chú': 'tham khảo game Pikmin, Nanobots'}
ADR_CITES = '§3 Kinh tế'                          # ADR chỉ trích đúng một đoạn


def h(s):
    return hashlib.sha1(s.replace('\r\n', '\n').encode()).hexdigest()[:8]   # chuẩn hoá xuống dòng: CRLF không làm đổi băm


verified = {'adr': {'file_touched': 1, 'sec_hash': h(GDD_V1[ADR_CITES])}}   # lúc ADR được viết / verify


def check(gdd, gdd_touched):
    by_file = gdd_touched > verified['adr']['file_touched']
    by_sec = h(gdd[ADR_CITES]) != verified['adr']['sec_hash']
    return by_file, by_sec


print('== 2. Hạt file vs băm đoạn ==  ADR trích', ADR_CITES)
for label, edit in [('sửa chính tả §9', ('§9 Ghi chú', 'tham khảo game Pikmin, Nanobots.')),
                    ('đổi số ở §3    ', ('§3 Kinh tế', 'mỗi đàn ăn 3 đơn vị năng lượng / giây'))]:
    g = dict(GDD_V1)
    g[edit[0]] = edit[1]
    f, s = check(g, gdd_touched=2)
    print(f'  {label}: theo ngày cả file -> {"NGHI CŨ" if f else "sạch":7} | theo băm §3 -> {"NGHI CŨ" if s else "sạch"}')
print('  Dòng 1 là false sharing (§3 và §9 "chung một cache line" = cả file). Dòng 2 cả hai cùng bắt được.')
print('  Thử: cho ADR trích thêm §9 (ADR_CITES thành danh sách) và viết lại check().\n')

# ---------- 3. Ngày vs supersedes: dựng lại trap-tunable ----------
CHOT = ('knowledge/', '/docs/ai/', 'docs/shared/')
TOUCH = {'June/docs/ai/tunable-wire.md': '2026-10-07'}             # git log: file này sửa tiếp sau commit
BUCKET = 0.5
ROWS = [  # (kind, ngày, path/mã, các file được nhắc, điểm BM25 âm: nhỏ hơn = tốt hơn)
    ('commit', '2026-10-04', '47c96f29 [Tunable] generator (core 1.6.0)', ["June/docs/ai/tunable-wire.md"], -7.20),
    ('note',   '2026-10-04', 'docs/shared/kit-candidates-2026-10-04.md',   [],                                -7.10),
]
SUPERSEDES = {}   # {id bản mới: [id bản cũ]}


def tier_of(kind, path):                                            # recall.tier_of: chốt theo THƯ MỤC
    return 'chot' if kind == 'note' and any(m in '/' + path for m in CHOT) else 'chuyen'


def label(kind, ts, path, files, fix):
    t = tier_of(kind, path)
    if fix:                                                         # đúng chiều: bị thay = cũ; commit là sự kiện, không "hết đúng"
        old = {o for olds in SUPERSEDES.values() for o in olds}
        return 'cu' if path in old else t
    if t != 'chot' and any(TOUCH.get(f, '') > ts for f in files):    # recall.is_stale: nhắc file sửa sau ngày mảnh
        return 'cu'
    return t


def ranked(fix):
    rows = [(label(k, ts, p, fl, fix), sc, p) for k, ts, p, fl, sc in ROWS]
    rows.sort(key=lambda r: (round(r[1] / BUCKET), r[0] == 'cu', r[0] != 'chot', r[1]))   # thứ tự sắp của recall.search
    return rows


print('== 3. Ngày vs supersedes ==  câu "generator [Tunable] com.sanne.core partial", đáp án = commit 47c96f29')
for fix in (False, True):
    if fix:
        SUPERSEDES['47c96f29 [Tunable] generator (core 1.6.0)'] = ['docs/shared/kit-candidates-2026-10-04.md']
    print('  ' + ('có supersedes, bỏ is_stale cho commit' if fix else 'luật hiện tại (ngày + thư mục)'))
    for i, (lb, sc, p) in enumerate(ranked(fix), 1):
        print(f'    {i}. [{lb:6}] {sc:6.2f}  {p}')
print('  Điểm commit tốt hơn (-7,20 < -7,10) nhưng cùng nấc BUCKET, nên nhãn quyết định thứ tự.')
print('  Thử: đổi BUCKET = 0.1 ở luật hiện tại. Bản cũ còn thắng không? Vì sao sửa BUCKET không phải sửa gốc?\n')

# ---------- 4. ID ổn định ----------
FILES = {'docs/shared/sanne-kit.md', 'Thousandfold/tools/audio/README.md', 'depts/qa/knowledge/plan.md'}
REFS_PATH = ['docs/shared/sanne-kit.md', 'Thousandfold/tools/audio/README.md', 'depts/qa/knowledge/plan.md']
IDS = {'shared:doc/sanne-kit': 'docs/shared/sanne-kit.md',
       'ref/thousandfold-tools-audio': 'Thousandfold/tools/audio/README.md',
       'qa:doc/plan': 'depts/qa/knowledge/plan.md'}                   # như kg/ids.toml: đường dẫn thật ở MỘT chỗ
REFS_ID = ['kg://' + i for i in IDS]


def move(old, new):                                                 # chuyển nhà: Thousandfold/ sang repo tách, gắn dưới games/
    global FILES
    FILES = {p.replace(old, new, 1) if p.startswith(old) else p for p in FILES}
    return old, new


def broken(refs, ids=None):
    res = []
    for r in refs:
        p = ids[r[5:]] if r.startswith('kg://') else r
        if p not in FILES:
            res.append(r)
    return res


print('== 4. ID ổn định ==')
print(f'  trước khi chuyển: gãy theo đường dẫn {len(broken(REFS_PATH))} · gãy theo kg:// {len(broken(REFS_ID, IDS))}')
old, new = move('Thousandfold/', 'games/Thousandfold/')
print(f'  sau khi chuyển  : gãy theo đường dẫn {len(broken(REFS_PATH))} · gãy theo kg:// {len(broken(REFS_ID, IDS))} (chưa sửa bảng)')
IDS = {k: v.replace(old, new, 1) if v.startswith(old) else v for k, v in IDS.items()}   # sửa MỘT bảng, như sửa .meta đi theo file
print(f'  sửa 1 dòng ids  : gãy theo đường dẫn {len(broken(REFS_PATH))} · gãy theo kg:// {len(broken(REFS_ID, IDS))}')
print('  Đường dẫn: phải tìm và sửa mọi chỗ trỏ. kg://: sửa một bảng (repo thật: 36 refs đường dẫn -> 0).')
print('  Thử: thêm 50 tham chiếu cùng trỏ README audio rồi đếm số dòng phải sửa cho mỗi cách.')
