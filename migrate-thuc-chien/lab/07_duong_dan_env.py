#!/usr/bin/env python3
"""Lab bài 07 — đường dẫn hai mặt và biến môi trường rò. Chạy: python3 07_duong_dan_env.py

Chỉ thư viện chuẩn + lệnh `git` và `sh` có sẵn trên máy. Mọi thứ dựng trong một thư mục tạm, chạy xong tự xoá.
Dựng lại đúng hình Seriously sau khi tách repo:
    tmp/Seriously/tools/claude/kit.py           (hub, nơi có tools thật)
    tmp/Seriously/Thousandfold  → ../seriously-thousandfold/Thousandfold    (symlink ở hub)
    tmp/seriously-thousandfold/tools → ../Seriously/tools                   (lớp phủ ở repo tách)
"""
import os
import shutil
import subprocess
import tempfile

GIT_ID = ['-c', 'user.name=lab', '-c', 'user.email=lab@example.com', '-c', 'init.defaultBranch=main', '-c', 'core.hooksPath=']


def git(cwd, *a, env=None):
    return subprocess.run(['git', *GIT_ID, *a], cwd=cwd, capture_output=True, text=True, env=env)


def clean_env():
    """= repos.clean_env() của Seriously: bỏ mọi GIT_* trước khi gọi git sang repo khác."""
    return {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}


def build(tmp):
    hub, split = os.path.join(tmp, 'Seriously'), os.path.join(tmp, 'seriously-thousandfold')
    os.makedirs(os.path.join(hub, 'tools', 'claude'))
    os.makedirs(os.path.join(split, 'Thousandfold'))
    with open(os.path.join(hub, 'tools', 'claude', 'kit.py'), 'w') as f:
        f.write('# kit thật, chỉ có ở hub\n')
    os.symlink('../seriously-thousandfold/Thousandfold', os.path.join(hub, 'Thousandfold'))
    return hub, split


# ---------- 1. Hai mặt của một đường dẫn ----------
def part1(tmp):
    hub, split = build(tmp)
    game = os.path.join(hub, 'Thousandfold')                       # đường LOGIC: đi qua symlink ở hub
    print('1. Hai mặt của đường dẫn')
    print('   đứng ở          :', os.path.relpath(game, tmp))
    print('   abspath(..)     :', os.path.relpath(os.path.abspath(os.path.join(game, '..')), tmp), ' ← cắt chữ, không hỏi đĩa')
    print('   realpath(..)    :', os.path.relpath(os.path.realpath(os.path.join(game, '..')), tmp), ' ← đi theo symlink')
    print('   có ../tools ?   :', os.path.exists(os.path.join(game, '..', 'tools')), ' ← kernel giải ".." theo đường vật lý')

    # shell: `cd ..` dùng $PWD (logic), còn `ls ../tools` để kernel giải (vật lý)
    sh = f'cd "{game}" && echo "   pwd   : $(pwd | sed "s#{tmp}/##")" && echo "   pwd -P: $(pwd -P | sed "s#{tmp}/##")" ' \
         f'&& (ls ../tools >/dev/null 2>&1 && echo "   ls ../tools: có" || echo "   ls ../tools: KHÔNG (rc≠0)") ' \
         f'&& (cd .. && [ -d tools ] && echo "   cd .. && ls tools: có (cd dùng đường logic)")'
    print(subprocess.run(['sh', '-c', sh], capture_output=True, text=True).stdout.rstrip())

    # vá kiểu Seriously: lớp phủ — repo tách có symlink tools → hub
    os.symlink('../Seriously/tools', os.path.join(split, 'tools'))
    print('   + lớp phủ tools → hub: ../tools giờ có =', os.path.exists(os.path.join(game, '..', 'tools')))

    # script gọi QUA lớp phủ tính gốc hub thế nào (kit.sh: cd vs cd -P; Python: abspath vs realpath)
    via = os.path.join(split, 'tools', 'claude', 'kit.py')
    root_abs = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(via)), '..', '..'))
    root_real = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(via)), '..', '..'))
    print('   gọi qua lớp phủ:', os.path.relpath(via, tmp))
    print('     gốc theo abspath(__file__) :', os.path.relpath(root_abs, tmp), ' ← SAI: repo tách, không có company/, state/')
    print('     gốc theo realpath(__file__):', os.path.relpath(root_real, tmp), ' ← đúng hub')
    for flag in ('', '-P'):
        r = subprocess.run(['sh', '-c', f'cd {flag} "$(dirname "{via}")/../.." && pwd'], capture_output=True, text=True)
        print(f'     sh: cd {flag or "  "} …/../.. && pwd    :', os.path.relpath(r.stdout.strip(), tmp))
    return hub, split


# ---------- 2. GIT_INDEX_FILE rò từ hook sang repo khác ----------
HOOK = '''#!/bin/sh
# pre-commit của repo A, hỏi trạng thái repo B (giống kg.py staged hỏi hub khi đang commit repo tách)
echo "   hook thấy GIT_INDEX_FILE=$(echo "$GIT_INDEX_FILE" | sed "s#.*/A/#<A>/#")"
echo "     git -C B diff --cached (để nguyên env): $(git -C "$B" diff --cached --name-only | wc -l | tr -d ' ') file 'đã stage'"
echo "     git -C B diff --cached (bỏ GIT_*)     : $(env -u GIT_INDEX_FILE -u GIT_DIR git -C "$B" diff --cached --name-only | wc -l | tr -d ' ') file 'đã stage'"
'''


def part2(tmp):
    print('\n2. Biến môi trường rò trong git hook')
    a, b = os.path.join(tmp, 'A'), os.path.join(tmp, 'B')
    for d, n in ((a, 3), (b, 40)):
        os.makedirs(d)
        git(d, 'init', '-q')
        for i in range(n):
            with open(os.path.join(d, f'{os.path.basename(d)}{i}.txt'), 'w') as f:
                f.write(str(i))
        git(d, 'add', '-A')
        git(d, 'commit', '-qm', 'init')
    git(b, 'fetch', '-q', a, 'main')                                   # B có đủ object của A (repo tách và hub chung lịch sử)
    print('   B sạch: git -C B diff --cached =', len(git(b, 'diff', '--cached', '--name-only').stdout.split()), 'file')
    hook = os.path.join(a, '.git', 'hooks', 'pre-commit')
    with open(hook, 'w') as f:
        f.write(HOOK)
    os.chmod(hook, 0o755)
    ident = ['-c', 'user.name=lab', '-c', 'user.email=lab@example.com']      # không tắt hooksPath: hook của A phải chạy
    env = {**clean_env(), 'B': b}
    print('   (a) `git commit` thường:')
    open(os.path.join(a, 'moi.txt'), 'w').write('0')   # nội dung trùng file của B → chung blob, như hub và repo tách (filter-repo)
    git(a, 'add', 'moi.txt')
    print(subprocess.run(['git', *ident, 'commit', '-qm', 'a'], cwd=a, capture_output=True, text=True, env=env).stderr.rstrip())  # git chuyển stdout của hook sang stderr
    print('   (b) commit bằng index tạm (cách `kit commit` làm để chỉ commit file của phiên mình):')
    tmp_idx = {**env, 'GIT_INDEX_FILE': os.path.join(a, '.git', 'kit-index')}
    subprocess.run(['git', 'read-tree', 'HEAD'], cwd=a, env=tmp_idx)
    open(os.path.join(a, 'moi2.txt'), 'w').write('1')
    subprocess.run(['git', 'add', 'moi2.txt'], cwd=a, env=tmp_idx)
    print(subprocess.run(['git', *ident, 'commit', '-qm', 'b'], cwd=a, capture_output=True, text=True, env=tmp_idx).stderr.rstrip())


# ---------- 3. Biến thử nghiệm đọc ở hai chỗ, hai luật ----------
def part3(tmp):
    print('\n3. Biến thử nghiệm sót lại: khoá cache và nội dung đọc từ hai nguồn')
    real, exp = os.path.join(tmp, 'commits.jsonl'), os.path.join(tmp, 'ab.jsonl')
    open(real, 'w').write('{"h":"a1","q":["câu thật"]}\n')
    open(exp, 'w').write('{"h":"a1","q":["câu THỬ NGHIỆM"]}\n')
    content = lambda env: open(env.get('D2Q_STORE') or real).read()      # doc2query.STORE (vẫn đọc biến)
    key = lambda env: str(os.path.getsize(real))                        # recall.d2q_key sau 5fc293e51 (không đọc)
    cache = {}

    def recall(env):
        k = key(env)
        if cache.get('k') != k:                                         # khoá đổi mới dựng lại chỉ mục
            cache.update(k=k, body=content(env))
        return cache['body'].strip()
    print('   shell thử nghiệm (D2Q_STORE đặt):', recall({'D2Q_STORE': exp}))
    print('   shell khác     (không đặt)     :', recall({}), ' ← vẫn câu thử nghiệm: khoá không chứa biến')


# ---------- 4. Clone đơn lẻ: thứ chạy được nhờ "hàng xóm" ----------
def part4(tmp, split):
    print('\n4. Clone đơn lẻ vào thư mục trống (không có hub cạnh bên)')
    git(split, 'init', '-q')
    with open(os.path.join(split, '.git', 'info', 'exclude'), 'a') as f:
        f.write('tools\n')                                              # lớp phủ không commit, như Seriously
    with open(os.path.join(split, 'Thousandfold', 'build.sh'), 'w') as f:
        f.write('sh ../tools/claude/kit.sh compile\n')
    git(split, 'add', '-A')
    git(split, 'commit', '-qm', 'game')
    alone = os.path.join(tmp, 'clone-don-le')
    git(tmp, 'clone', '-q', split, alone)
    dangling = []
    for root, _, files in os.walk(alone):
        if '.git' in root:
            continue
        for fn in files:
            for line in open(os.path.join(root, fn)):
                for tok in line.split():
                    if tok.startswith('../') and not os.path.exists(os.path.join(root, os.path.dirname(tok) or '.')):
                        dangling.append(f'{os.path.relpath(os.path.join(root, fn), alone)}: {tok}')
    print('   ở máy dev (có hub + lớp phủ):', os.path.exists(os.path.join(split, 'tools', 'claude', 'kit.py')))
    print('   clone đơn lẻ, đường ../ treo:', dangling or 'không có')


def main():
    tmp = os.path.realpath(tempfile.mkdtemp(prefix='lab07-'))   # macOS: /var → /private/var, realpath để in gọn
    try:
        hub, split = part1(tmp)
        part2(tmp)
        part3(tmp)
        part4(tmp, split)
    finally:
        shutil.rmtree(tmp)
    print('\nThử: ở mục 1 đổi realpath thành abspath trong root_real; ở mục 2 bỏ `env -u` để thấy cả hai dòng như nhau;'
          ' ở mục 3 cho key() đọc D2Q_STORE (hoặc băm cả tên file) để shell thứ hai dựng lại.')


if __name__ == '__main__':
    main()
