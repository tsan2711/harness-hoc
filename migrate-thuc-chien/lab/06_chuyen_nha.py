#!/usr/bin/env python3
"""Lab bài 06 — chuyển nhà: lớp phủ symlink, đo nợ, cái giá của tách repo. Chạy: python3 06_chuyen_nha.py

Chỉ thư viện chuẩn. Mọi thứ dựng trong một thư mục tạm, xoá khi xong. Có `git` trên PATH thì phần 1 chạy thêm ca git thật.
"""
import os
import re
import shutil
import subprocess
import tempfile

T = os.path.realpath(tempfile.mkdtemp(prefix='lab06-'))   # Mac: /var → /private/var, chính nó cũng là symlink


def w(path, text=''):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def link(src, dst):
    """symlink tương đối như `kit workspace link`. Windows không có Developer Mode → OSError."""
    try:
        os.symlink(os.path.relpath(src, os.path.dirname(dst)), dst, target_is_directory=os.path.isdir(src))
        return True
    except OSError as e:
        print(f'  KHÔNG tạo được symlink ({e}). Windows: bật Developer Mode, hoặc dùng junction `mklink /J`.')
        return False


# ---------- 1. Lớp phủ: cây nhìn như monorepo, git thì không ----------
print('== 1. Lớp phủ symlink ==')
hub, tf = os.path.join(T, 'Seriously'), os.path.join(T, 'seriously-thousandfold')
w(os.path.join(hub, 'tools/claude/kit.sh'), 'echo kit\n')
w(os.path.join(hub, 'company/workspace.toml'), '[[repo]]\nname = "seriously-thousandfold"\npath = "../seriously-thousandfold"\n')
w(os.path.join(tf, 'Thousandfold/build.sh'), 'sh ../tools/claude/kit.sh compile\n')     # script game leo ra hub
w(os.path.join(tf, 'Thousandfold/Assets/a.txt'), 'asset\n')
ok = link(os.path.join(tf, 'Thousandfold'), os.path.join(hub, 'Thousandfold'))        # hub → repo tách
ok = ok and link(os.path.join(hub, 'tools'), os.path.join(tf, 'tools'))               # repo tách → hub (lớp phủ)
if ok:
    game = os.path.join(hub, 'Thousandfold')
    print('  từ repo tách, ../tools/claude/kit.sh có không:',
          os.path.exists(os.path.join(tf, 'Thousandfold', '..', 'tools/claude/kit.sh')))
    p = os.path.join(game, 'Assets/a.txt')
    print('  đường logic :', os.path.relpath(os.path.abspath(p), T))
    print('  đường vật lý:', os.path.relpath(os.path.realpath(p), T), ' ← hai tên cho một file (bài 07)')

    if shutil.which('git'):
        env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}      # như repos.clean_env()
        g = lambda d, *a: subprocess.run(['git', '-C', d, *a], capture_output=True, text=True, env=env)
        for d in (hub, tf):
            g(d, 'init', '-q')
            g(d, '-c', 'user.email=lab@x', '-c', 'user.name=lab', 'commit', '-q', '--allow-empty', '-m', 'init')
        r = g(hub, 'log', '--oneline', '--', 'Thousandfold/Assets/a.txt')
        print(f'  git log ở hub, path qua symlink → rc {r.returncode}, {len(r.stdout.splitlines())} dòng  ← im lặng, không lỗi')
        r = g(hub, 'add', 'Thousandfold/Assets/a.txt')
        print(f'  git add ở hub, cùng path      → rc {r.returncode}: {r.stderr.strip()[:60]}')
        top = g(os.path.dirname(os.path.realpath(p)), 'rev-parse', '--show-toplevel').stdout.strip()
        print('  repo_of: chạy git ở thư mục VẬT LÝ → gốc =', os.path.basename(top))
    else:
        print('  (không có git trên PATH — bỏ ca git)')

    # clone đơn lẻ = không có lớp phủ
    os.unlink(os.path.join(tf, 'tools'))
    dangling = [f for f in ('Thousandfold/build.sh',)
                for m in re.findall(r'\.\./(tools|docs|company)\S*', open(os.path.join(tf, f), encoding='utf-8').read())
                if not os.path.exists(os.path.join(tf, 'Thousandfold', '..', m))]
    print(f'  gỡ lớp phủ (= clone một mình): {len(dangling)} đường `../tools` trỏ vào chỗ trống')
print('  Thử: thêm `../docs/shared/ui.md` vào build.sh rồi chạy lại; đếm được bao nhiêu chỗ treo?\n')

# ---------- 2. Đo nợ bằng công thức, rồi khoá bằng mốc (ratchet) ----------
print('== 2. Nợ đo được ==')
W = {'A': 2, 'D': 3, 'E': 2, 'F': 3}
RX = {   # rút gọn từ tools/harness/symlink-debt.md mục 4
    'A': re.compile(r'\.\./(tools|docs|company)\b'),
    'D': re.compile(r"[\[(]\s*['\"]git['\"]\s*,"),
    'E': re.compile(r'os\.getcwd\(\)|^(?!.*(realpath|resolve\(\))).*__file__.*\.\.'),
}
SAFE_GIT = re.compile(r"startswith\(\s*['\"]GIT_|repos\.git_in")


def debt(files):
    pts, n = 0.0, {k: 0 for k in W}
    for text in files.values():
        lines = [l for l in text.splitlines() if not l.lstrip().startswith('#')]
        clean_env = bool(SAFE_GIT.search(text))
        for l in lines:
            for k in ('A', 'D', 'E'):
                if RX[k].search(l):
                    n[k] += 1
            if RX['D'].search(l) and not clean_env:
                n['F'] += 1                      # F ⊂ D: git trần ở file không xoá GIT_*
    return sum(W[k] * n[k] for k in n), n


before = {
    'hook.py': "import os, subprocess\nTOP = os.path.join(os.path.dirname(__file__), '..', '..')\n"
               "subprocess.run(['git', 'status'])\ncwd = os.getcwd()\n",
    'ci.sh': 'sh ../tools/claude/ci-unity.sh Thousandfold EditMode\n',
    'post.py': "import subprocess\nsubprocess.run(['git', 'log', '-1'], env={k: v for k, v in env.items() if not k.startswith('GIT_')})\n",
}
after = {
    'hook.py': "import os, repos\nTOP = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..'))\n"
               "repos.git_in('hub', ['status'])\ncwd = repos.here()\n",
    'ci.sh': 'kit ci-unity Thousandfold EditMode\n',
    'post.py': before['post.py'],
}
d0, n0 = debt(before)
d1, n1 = debt(after)
print(f'  trước: {n0} → nợ {d0:g}')
print(f'  sau  : {n1} → nợ {d1:g}  ({(d1 - d0) / d0:+.0%})')
baseline = d1
pr = dict(after, **{'new.py': "import subprocess\nsubprocess.run(['git', 'diff'])\n"})   # một phiên thêm git trần
d2, _ = debt(pr)
print(f'  phiên sau thêm 1 dòng git trần: nợ {d2:g} vs mốc {baseline:g} → {"ĐỎ (tăng)" if d2 > baseline else "xanh"}')
print('  Thử: xoá dòng startswith GIT_ trong post.py → F tăng mấy điểm? Đổi W["F"]=0 thì cổng còn bắt được new.py không?\n')

# ---------- 3. Cái giá của tách: việc chạm > 1 repo, số commit ----------
print('== 3. Cái giá: một việc phải commit ở mấy repo ==')
TASKS = [  # danh sách file mỗi việc (giả, theo dạng tasks.jsonl). Ở repo thật: 49/277 = 18 % chạm > 1 repo.
    ['Thousandfold/Assets/Scripts/Swarm.cs'], ['Thousandfold/Assets/Art/Port/house.glb', 'depts/art/log/port.md'],
    ['tools/claude/recall.py'], ['tools/claude/recall.py', 'Thousandfold/docs/ai/INDEX.md'], ['depts/qa/eval/cases.toml'],
    ['Thousandfold/design/gdd.md'], ['depts/art/themes/a.toml'], ['Thousandfold/Assets/Art/Port/tree.glb', 'depts/art/log/tree.md'],
    ['docs/shared/ui-process.md'], ['Thousandfold/Assets/Tests/EditMode/SwarmTests.cs'],
]
LAYOUT = {
    'monorepo': lambda f: 'hub',
    'tách game': lambda f: 'tf' if f.startswith('Thousandfold/') else 'hub',
    'tách game + depts': lambda f: 'tf' if f.startswith('Thousandfold/') else 'depts' if f.startswith('depts/') else 'hub',
}
print(f'  {"cách chia":18} {"chạm >1 repo":>12} {"commit (lớp phủ)":>17} {"commit (submodule)":>19}')
for name, repo_of in LAYOUT.items():
    touched = [{repo_of(f) for f in t} for t in TASKS]
    multi = sum(len(s) > 1 for s in touched)
    overlay = sum(len(s) for s in touched)                      # kit commit: mỗi repo bị chạm 1 commit
    # submodule: mỗi repo con bị chạm 1 commit + hub luôn phải commit (file của nó, hoặc chỉ để dời con trỏ submodule)
    sub = sum(len(s - {'hub'}) + 1 for s in touched)
    print(f'  {name:18} {multi:>9}/{len(TASKS)} {overlay:>17} {sub:>19}')
print('  Submodule: việc chỉ sửa trong game vẫn cần commit thứ hai ở hub ("bump" con trỏ), nếu không hub trỏ bản cũ.')
print('  Thử: gom `Thousandfold/Assets/Art/Port/` về depts (art là chủ) — tỉ lệ chạm >1 repo đổi ra sao?')

shutil.rmtree(T, ignore_errors=True)
