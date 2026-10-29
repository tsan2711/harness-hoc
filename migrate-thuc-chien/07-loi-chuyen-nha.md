# 07 — Lỗi chuyển nhà: đường dẫn hai mặt, biến môi trường rò

> Bài 7 của chuỗi "migrate thực chiến" (mổ **bước 4** ở [bài 00](00-tong-quan.md): tách repo, phần *lỗi lòi ra sau khi chuyển*).
> Đọc ~14 phút + lab 5 phút. Mang vào: lớp phủ symlink (bài 06), khoá cache phải chứa mọi thứ làm đổi đầu ra (bài 03), Unity GUID/.meta, `Library/`.

## Chuyện mở đầu

Chiều 28/10, vài giờ sau khi `Thousandfold/` chuyển sang repo riêng. Một phiên commit **một** file trong repo game. Hook kiểm trước
commit gọi `kg.py staged` để hỏi "file nào đang đổi", và nhận về **1.836 file**. Code không sai dòng nào. Lệnh git chạy ở hub nhưng
mang theo biến `GIT_INDEX_FILE` của repo game, nên đọc nhầm index (danh sách file đã stage) của repo khác. Cùng ngày còn hai lỗi
cùng họ: script gọi qua symlink tính sai gốc repo, và test để lại 13 file khoá rác trong thư mục trạng thái thật.

## Dừng 30 giây

Bạn chuyển `Assets/Art` ra thành package riêng, nối lại bằng symlink. Tự liệt kê ba thứ: cái gì trong project nhớ vị trí bằng
**đường dẫn** thay vì GUID; tiến trình nào (Editor, script build, CI) đang mang **ngữ cảnh ngầm** (thư mục làm việc, biến môi trường)
mà bạn chưa từng truyền vào tường minh; và làm sao **chứng minh** package mới chạy được khi không có project cũ nằm cạnh.
Giữ ba ý đó. Cả bài đi qua đúng ba ý, theo thứ tự.

---

## Mạch của bài

```
1. Symlink làm đường dẫn có hai mặt      → ".." logic ≠ ".." vật lý → script tính sai gốc repo
2. Sửa: realpath / cd -P                 → gốc đúng, nhưng "hàng xóm ../" vẫn là phụ thuộc ngầm → ghi vào manifest
3. Thư mục đúng rồi, git vẫn đi nhầm     → GIT_INDEX_FILE / GIT_DIR của hook rò sang repo khác
4. Môi trường = trạng thái toàn cục ngầm  → một cửa duy nhất gọi git; biến thử nghiệm sót lại cũng là rò
5. Chứng minh đã hết                     → clone đơn lẻ + thư mục tạm; nhưng test cũng rò ra trạng thái thật
```

## 1. Đường dẫn có hai mặt

Sau khi tách (bài 06), máy dev có hình này:

```
Seriously/Thousandfold        → symlink tới ../seriously-thousandfold/Thousandfold
seriously-thousandfold/tools  → symlink tới ../Seriously/tools        (lớp phủ, không commit)
```

Một đường dẫn qua symlink có hai cách đọc:

- **Logic**: chuỗi ký tự bạn đã đi qua. `Seriously/Thousandfold/..` = `Seriously`. Shell giữ nó trong biến `$PWD`; `pwd` in nó ra;
  `cd ..` của shell cắt chữ trên `$PWD`. Python `os.path.abspath` và `normpath` cũng chỉ **cắt chữ**, không hỏi đĩa.
- **Vật lý**: chỗ dữ liệu thật nằm. Kernel giải `..` từ inode thật, nên `open("../tools/x")`, `ls ../tools`, `git -C ..` đều đi
  theo mặt này. `Seriously/Thousandfold/..` vật lý = `seriously-thousandfold`. `pwd -P`, `cd -P`, `os.path.realpath`,
  `Path.resolve()` trả mặt này.

Hai mặt trùng nhau cho đến ngày có symlink. Lab mục 1 in ra đúng điều đó:

```
pwd   : Seriously/Thousandfold
pwd -P: seriously-thousandfold/Thousandfold
ls ../tools: KHÔNG (rc≠0)                  ← kernel đi đường vật lý
cd .. && ls tools: có                      ← cd của shell đi đường logic
```

Cùng một chữ `..`, hai lệnh liền nhau ra hai thư mục. Đây là lý do lớp phủ symlink tồn tại: thay vì sửa mọi `../tools`, repo tách
có sẵn `tools → hub` để mặt vật lý cũng tìm thấy.

**Lỗi thật thứ nhất: tính gốc repo.** `tools/claude/kit.sh` tìm gốc hub bằng:

```sh
R=$(cd "$(dirname "$0")/../.." && pwd)
```

Gọi qua lớp phủ (`seriously-thousandfold/tools/claude/kit.sh`) thì `cd` logic leo hai bậc ra `seriously-thousandfold`, không phải
hub. Từ đó `$R/company/state/…` trỏ vào chỗ không có. Commit `2686381e0` (28/10) sửa:

```sh
R=$(cd -P "$(dirname "$0")/../.." && pwd)  # -P: gọi qua symlink lớp phủ (repo tách) vẫn ra hub thật
```

Phía Python có cùng lỗi dưới dạng khác: `os.path.abspath(__file__)`. Commit đó đổi 72 dòng trong 56 file sang `realpath`:

```python
-REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
+REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..'))
```

Chỉ `realpath` ở **bên trong** là bắt buộc: nó biến `seriously-thousandfold/tools/claude` thành `Seriously/tools/claude` trước khi
cắt `..`. `abspath` bên ngoài lúc đó vô hại vì đoạn còn lại không đi qua symlink nào.

**Quy tắc.** Đường dẫn dùng để *hiển thị* thì giữ mặt logic (người đọc quen tên đó). Đường dẫn dùng để *tính* (gốc repo, so hai
đường có phải một chỗ, làm khoá cache) thì luôn lấy mặt vật lý, và lấy **một lần** ở cửa vào.

**Cái giá của realpath.** Mặt vật lý lộ ra những chỗ trước đây không thấy. Claude Code lưu lịch sử và memory theo khoá là đường vật
lý của project. Mở phiên ở `Seriously/Thousandfold` nhưng Claude dùng đường thật thì khoá thành
`-Unity-seriously-thousandfold-Thousandfold`, khác khoá cũ, mất hết lịch sử. Bản sửa (`workspace link` → `claude_keys`) tạo symlink
khoá mới → khoá cũ. Unity Hub nhận diện project theo đường dẫn cũng mắc đúng chuyện này.

## 2. "Hàng xóm `../`" là phụ thuộc ngầm

`realpath` cho gốc đúng. Nhưng nhiều code còn giả định *thứ gì nằm cạnh gốc*: `kit.sh` tìm thư viện `sanne-kit` ở `$R/../sanne-kit`,
script art tìm `../../Seriously-worker/…`. Không ai khai báo các giả định này; chúng đúng vì máy của Bi xếp thư mục như vậy.

Sổ nợ `tools/harness/symlink-debt.md` đo thử một **clone đơn lẻ** của repo game vào thư mục trống (không hub cạnh bên). Kết quả:
**14 mục hỏng**, trong đó `sh ../tools/claude/kit.sh` rc 127, 21/21 hook trong `.claude/settings.json` trỏ `$CLAUDE_PROJECT_DIR/../tools/…`,
và hook chặn lệnh nguy hiểm (`company_hook.py guard`) rc 2 vì không có file; sổ ghi kết luận: **guard tắt**. Lỗi thứ ba đáng sợ
nhất: cổng bảo vệ không chạy, và không có gì đỏ để báo.

Sửa ở commit `7aee544ca`: vị trí mọi repo ghi vào một manifest, `company/workspace.toml`, và một hàm tra:

```python
def path_of(name, hub=None, must_exist=True):
    """Gốc thư mục (realpath) của repo `name` trong workspace. Thứ tự: biến môi trường → workspace.toml → RepoPathError.
    ...
    Không đoán ../<tên>: repo không có khoá path trong manifest = lỗi."""
```

Ba điểm đáng chép:

1. **Thứ tự cố định**: biến môi trường (`KIT_REPO_<TÊN>`, cho máy khác / CI) thắng manifest; manifest thắng… không gì cả. Không có
   bước "đoán `../`".
2. **Lỗi nói đã tìm ở đâu và sửa thế nào**: `không biết repo 'x' nằm đâu — đã tìm: $KIT_REPO_X; …/workspace.toml (không có khoá path).
   Sửa: thêm path = "…" …`. Một lỗi rõ tốn 10 giây; một đường dẫn đoán sai tốn cả buổi.
3. **Trả realpath**: kết quả đi thẳng vào phép tính, không mang mặt logic.

Đây đúng là cách Unity xử lý asset: tham chiếu bằng **GUID** trong `.meta`, bảng GUID → đường dẫn nằm ở `AssetDatabase`. Di chuyển
file trong Editor thì GUID giữ nguyên, mọi prefab trỏ tới vẫn đúng. Thứ gãy là thứ đi bằng đường dẫn trần: `Resources.Load("Art/x")`,
`AssetDatabase.LoadAssetAtPath`, chuỗi đường dẫn trong script build. Seriously đi cùng hướng với tham chiếu chéo repo: `kg://<repo>/<id>`
thay cho `../../../depts/…` (bài 05 nói phần ID ổn định).

## 3. Thư mục đúng rồi, git vẫn đi nhầm

Đây là lỗi 1.836 file ở phần mở đầu. Tài liệu `githooks` của git nói thẳng: trước khi chạy hook, git **export** các biến như
`GIT_DIR`, `GIT_INDEX_FILE` để lệnh git *bên trong hook* tìm đúng repo. Ý tốt, với giả định hook chỉ làm việc với repo của chính nó.

Các biến này **thắng** `-C`. `git -C <B> diff --cached` khi `GIT_INDEX_FILE` đang trỏ index của A: git đổi thư mục sang B, đọc HEAD
của B, nhưng so với index của A. Kết quả là mọi khác biệt giữa hai cây, báo như "đã stage".

Có một chi tiết làm lỗi này sống lâu. Lab mục 2 cho thấy:

```
(a) git commit thường:   hook thấy GIT_INDEX_FILE=.git/index
     git -C B diff --cached (để nguyên env): 0 file           ← may mắn
(b) commit bằng index tạm: hook thấy GIT_INDEX_FILE=<A>/.git/kit-index
     git -C B diff --cached (để nguyên env): 42 file          ← rò
     git -C B diff --cached (bỏ GIT_*)     : 0 file
```

Với commit thường, git đặt giá trị **tương đối** `.git/index`; sau `-C B` nó tự rơi vào index của B, đúng do trùng hợp. Nhưng
`kit commit` dùng **index tạm** (để chỉ commit file của phiên mình khi nhiều phiên cùng sửa cây), `git commit <path>` cũng thế, và
khi đó git đặt **đường tuyệt đối**. Lỗi chỉ hiện khi đồng thời có (a) hook gọi git sang repo khác và (b) index tạm. Trước khi tách
repo, (a) không xảy ra vì chỉ có một repo. Chuyển nhà không tạo lỗi; nó làm lỗi có điều kiện để hiện.

Nếu hai repo không chung lịch sử, triệu chứng khác: `fatal: unable to read <mã blob>` (index trỏ object mà kho B không có). Hub và
repo tách sinh ra bằng `filter-repo` nên chung blob, và lỗi hiện dưới dạng *số sai*, khó thấy hơn một lỗi đỏ.

**Sửa ở commit `0c2fda4f4`**: một hàm shell, `tools/claude/lib/git.sh`:

```sh
git_in() {
  _gi_d=$1; shift
  ( unset GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_CONFIG GIT_CONFIG_PARAMETERS GIT_CONFIG_COUNT GIT_OBJECT_DIRECTORY GIT_DIR \
          GIT_WORK_TREE GIT_IMPLICIT_WORK_TREE GIT_GRAFT_FILE GIT_INDEX_FILE GIT_NO_REPLACE_OBJECTS GIT_REPLACE_REF_BASE \
          GIT_PREFIX GIT_INTERNAL_SUPER_PREFIX GIT_SHALLOW_FILE GIT_COMMON_DIR GIT_QUARANTINE_PATH
    exec git -C "$_gi_d" "$@" )
}
git_here() { command git "$@"; }
```

- Danh sách xoá lấy từ `git rev-parse --local-env-vars` (git tự in ra những biến "gắn với một repo"), cộng hai biến nội bộ. Giữ
  `GIT_AUTHOR_*`, `GIT_SSH*`: danh tính và mạng không gắn với repo nào.
- `unset` nằm trong **subshell** `( … )`, nên chỉ lệnh git đó mất biến; script gọi vẫn còn nguyên.
- `git_here` là lối ngược lại, **cố ý giữ** môi trường: hook làm việc với chính repo của nó thì *phải* đọc `GIT_INDEX_FILE` tạm, không
  thì nó kiểm index chính thay vì đúng thứ sắp commit. Tách hai tên để người đọc code thấy ngay lệnh nào được phép mang ngữ cảnh.

Phía Python (commit `7aee544ca`) là `repos.git_in`, và commit `add3f4145` chuyển ~25 file sang dùng nó:

```python
def clean_env(extra=None):
    """os.environ bỏ mọi GIT_* (GIT_DIR/GIT_INDEX_FILE của hook không được rò sang repo khác) + extra."""
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env.update(extra or {})
    return env
```

```python
-        return subprocess.run(['git', '-C', repo, *args], capture_output=True, text=True, timeout=timeout).stdout
+        return repos.git_in(repo, list(args), timeout=timeout).stdout
```

Lúc đổi, việc này còn lôi ra một lỗi không liên quan đến môi trường: `kit commit` chia commit theo repo viết `rc = rc or commit_one(…)`.
`or` của Python ngắt mạch, nên push repo đầu thất bại (`rc` ≠ 0) thì **không gọi** `commit_one` cho các repo sau, im lặng bỏ commit của
chúng. Sửa thành gọi trước rồi mới gộp `rc`.

## 4. Môi trường là trạng thái toàn cục ngầm

Nhìn rộng ra, biến môi trường là một **biến toàn cục**: mọi tiến trình con thừa kế, không ai khai báo, không xuất hiện trong chữ ký
hàm. Đọc `git_in(repo, args)` bạn biết nó phụ thuộc `repo` và `args`; đọc `subprocess.run(['git', ...])` bạn không biết nó còn phụ thuộc
mười mấy biến mà tiến trình cha có thể đã đặt. Trong CPU, đây giống **thanh ghi trạng thái ngầm** (cờ làm tròn của FPU, chế độ
denormal): một hàm đặt, hàm khác ở rất xa đổi kết quả mà không có dòng code nào nối hai bên.

Hai cách chống, Seriously dùng cả hai:

- **Một cửa duy nhất.** Mọi lệnh git đi qua `git_in`. Thêm một chỗ gọi git trần là thêm một chỗ rò. Sổ nợ đếm bằng regex: dòng gọi git
  không qua cửa (loại D) giảm **129 → 24**, trong đó dòng nằm ở file không xoá `GIT_*` (loại F) **107 → 23** sau pha 2. Từ pha 1, cổng
  pre-commit chặn nợ *mới*, nên con số chỉ đi xuống (bài 08 nói cách làm cổng đó).
- **Danh sách trắng thay vì danh sách đen**, khi cần chắc tuyệt đối: chạy với môi trường rỗng rồi chỉ thêm biến cần (`env -i`). Seriously
  *không* làm vậy cho git vì sẽ mất `HOME`, SSH agent, danh tính.

**Biến thử nghiệm sót lại** là cùng bệnh, ở dạng mình tự gây. Khi so hai bản câu hỏi sinh sẵn (bài 03), có thêm biến `D2Q_STORE` để
trỏ sang kho A/B. Commit `5fc293e51` (29/10) bỏ nó khỏi hàm làm **khoá** chỉ mục:

```python
 def d2q_key():
-    p = os.environ.get('D2Q_STORE') or os.path.join(REPO, 'company', 'memory', 'd2q', 'commits.jsonl')
+    p = os.path.join(REPO, 'company', 'memory', 'd2q', 'commits.jsonl')
```

Nhưng đọc code hiện tại thì `tools/claude/doc2query.py:17` vẫn còn `STORE = os.environ.get('D2Q_STORE') or …`, tức **nội dung** vẫn
nghe theo biến còn **khoá** thì không. Theo luật ở bài 03 ("khoá phải chứa mọi thứ làm đổi đầu ra"), đây là một lỗ: một shell còn sót
`D2Q_STORE` mà dựng lại chỉ mục chung thì nhét câu thử nghiệm vào, và mọi phiên khác sau đó dùng tiếp vì khoá không đổi. Lab mục 3
diễn lại chuyện này. (Suy luận từ code; repo không ghi lần nào nó xảy ra thật.)

Hai chỗ khác trong repo có cùng mùi "một khái niệm, hai luật": `clean_env` của Python xoá **mọi** `GIT_*` (cả `GIT_AUTHOR_*`), còn
`git_in` của shell giữ danh tính; và gốc hub từng có hai tên biến, `COMPANY_TOP` và `KIT_HUB` (giờ gộp, tên sau là bí danh). Quy tắc
rút ra: mỗi biến môi trường đọc **ở một chỗ**, sớm, rồi truyền tiếp bằng tham số. Biến thử nghiệm có ngày hết hạn ghi cạnh nó.

## 5. Chứng minh đã hết: clone đơn lẻ và thư mục tạm

Máy dev là nơi tệ nhất để kiểm lỗi chuyển nhà: hub nằm cạnh, lớp phủ có sẵn, biến môi trường đã đặt từ tuần trước. Mọi giả định ngầm
đều *đúng* ở đó. Hai kỹ thuật:

- **Clone đơn lẻ**: `git clone` repo vào thư mục trống, không có gì cạnh bên, rồi chạy selftest/hook. Đây là cách sổ nợ tìm ra 14 mục
  ở mục 2. Lab mục 4 làm phiên bản nhỏ: commit một `build.sh` gọi `../tools/claude/kit.sh`; trên máy dev chạy được, clone đơn lẻ thì treo.
- **Thư mục tạm có cấu trúc giả**: `tools/harness/tests/test_repos_paths.py` dựng hub + repo tách giả trong `tempfile`, rồi **cố ý gây
  lỗi** để chứng minh cổng bắt được:

```python
def test_strips_leaked_git_env(self):                      # vi phạm: GIT_DIR/GIT_INDEX_FILE rò từ hook cha
    leak = {'GIT_DIR': '/nonexistent', 'GIT_INDEX_FILE': '/nonexistent/index'}
    with mock.patch.dict(os.environ, leak):
        raw = subprocess.run(['git', '-C', self.sib, 'rev-parse', '--show-toplevel'], capture_output=True, text=True)
        self.assertNotEqual(raw.returncode, 0, 'không xoá GIT_* thì git đi sai repo')
        r = repos.git_in(self.sib, ['rev-parse', '--show-toplevel'])
        self.assertEqual((r.returncode, r.stdout.strip()), (0, self.sib), r.stderr)
```

Dòng `assertNotEqual(raw…)` quan trọng không kém dòng sau: nó chứng minh môi trường giả **thật sự gây lỗi** cho git trần. Thiếu dòng
đó, nếu `mock` không có tác dụng thì test vẫn xanh mà không kiểm gì (bài 08: lệnh kiểm phải biết trả sai).

**Nhưng test cũng rò.** Kiểm cuối 28/10 tìm thấy **13 file** `post-check.tmp*.lock` trong `company/state/` thật. Nguồn: test commit
vào repo tạm, hook sau commit chạy `post_check.py`, mà `post_check.py` lấy thư mục trạng thái từ `realpath(__file__)`, tức hub thật,
rồi đặt tên khoá theo tên repo vừa commit (`tmpXXXX`). Thư mục tạm cô lập *dữ liệu của test*, không cô lập *đường dẫn mà code tự tính*.
Sửa ở `5b8cdd0a0`:

```python
    if REPO != TOP:   # only the hub or a split repo linked to it; a test's temp repo must not leave locks in company/state
        ...
        if REPO not in repos.all_repos(TOP):
            return 0
```

Cách tổng quát hơn là cho mọi đường trạng thái đi qua một biến (Seriously có `COMPANY_TOP`, `RECALL_DB`, `PRESENCE_STATE`…) và test
luôn đặt biến đó vào thư mục tạm. Lại là môi trường, nhưng lần này **tường minh**: test đặt, code đọc ở một chỗ.

Trên macOS có thêm một bẫy nhỏ: `tempfile.mkdtemp()` trả `/var/folders/…`, mà `/var` là symlink tới `/private/var`. Test so
`realpath(x) == tmp` sẽ đỏ nếu `tmp` chưa qua `realpath`. Lab gọi `os.path.realpath(tempfile.mkdtemp())` ngay dòng đầu vì vậy.

## So sánh các cách

| Cách | Ưu | Gãy ở đâu | Ở Seriously |
|---|---|---|---|
| Đường tương đối theo quy ước (`../tools`, `../sanne-kit`) | không cần cấu hình | clone đơn lẻ, máy khác, symlink | trước tách: 237 dòng `../tools…` trong code/hook (210 là 10 bản sao `settings.json`) |
| `abspath` / `cd` (mặt logic) | giữ tên người dùng thấy | sai gốc khi gọi qua symlink | 93 dòng loại E ở đo đầu |
| `realpath` / `cd -P` (mặt vật lý) | gốc thật, so sánh đúng | lộ đường vật lý: khoá theo đường đổi (memory Claude, Unity Hub) | `2686381e0`: 72 dòng `realpath(__file__)` + `kit.sh` |
| Manifest + biến ghi đè (`path_of`) | tường minh, lỗi nói cách sửa | phải giữ manifest; mỗi máy một biến | `7aee544ca`, `company/workspace.toml` |
| Xoá biến repo trước git sang repo khác (`git_in`) | chặn rò `GIT_*` | quên một chỗ là rò, cần cổng đếm | D 129 → 24, F 107 → 23 |
| Môi trường trắng (`env -i`, sandbox) | không gì rò | mất biến cần (HOME, SSH, danh tính) | không dùng |

## Unity gặp đúng chuyện này

| Seriously | Unity |
|---|---|
| `path_of(tên)` thay `../tên` | GUID trong `.meta` thay đường dẫn; thứ đi bằng chuỗi đường dẫn (`Resources.Load`, `LoadAssetAtPath`, script build) mới gãy khi dời |
| `realpath(__file__)` để tìm gốc, không dựa vào cwd | `Application.dataPath` (Editor: `<project>/Assets`) thay vì `Directory.GetCurrentDirectory()`; batchmode trên CI thì cwd là chỗ runner gọi |
| khoá memory Claude theo đường vật lý | `Library/` và Unity Hub gắn với vị trí project; dời project thường kéo theo import lại một phần (theo kinh nghiệm, không đo ở Seriously). Lúc tách, worker Unity của game cũng được chuyển `Library/` sang chỗ mới và ghi chú "Unity có thể import lại một lần" |
| `GIT_INDEX_FILE` rò từ hook | biến môi trường của tiến trình cha rò vào Unity batchmode trên CI (vd. `UNITY_*`, `JAVA_HOME` cho Android build): build trên máy dev xanh, trên runner đỏ |

## Scale

- **Nhỏ (một repo, không symlink)**: hai mặt trùng nhau, `GIT_*` chỉ trỏ chính repo. Chỉ cần `realpath` ở cửa vào của script là đủ phòng xa.
- **Vừa (Seriously: hub + 2 repo tách + sanne-kit, 39 symlink lúc đầu → 18 sau khi gỡ)**: manifest + một cửa gọi git + cổng đếm nợ
  (`kit symlink-debt`, điểm nợ có trọng số **1.480,5 → 479,5** sau pha 2). Clone đơn lẻ làm bài kiểm định kỳ.
- **Lớn (monorepo hàng nghìn người, build hệ thống)**: build *kín* (*hermetic*): mỗi bước chạy trong sandbox chỉ thấy file đã khai báo, môi
  trường lọc theo danh sách trắng (Bazel có `--incompatible_strict_action_env`), không đường tuyệt đối trong đầu ra. Đó là phiên bản đầy
  đủ của `git_in` + `path_of`.

## Bốn nền tảng

- **Mac**: `/var`, `/tmp`, `/etc` là symlink tới `/private/…`, nên `realpath` của file tạm khác chuỗi `tempfile` trả. APFS mặc định không
  phân biệt hoa thường: `Seriously` và `seriously-…` khác tên nên không đụng, nhưng hai đường khác hoa thường có thể là một file; so đường
  bằng `os.path.samefile` khi nghi.
- **Windows**: symlink cần Developer Mode, git mặc định `core.symlinks=false` (symlink thành file chữ), nên lớp phủ thường là *junction*
  (`mklink /J`). `os.path.realpath` giải junction từ Python 3.8. Không có `cd -P`; PowerShell `(Get-Item x).Target` hoặc `Resolve-Path`.
  Tên biến môi trường không phân biệt hoa thường (`Path` = `PATH`), nên lọc theo tiền tố phải so không phân biệt hoa thường.
- **iOS**: không chạy harness trên máy. Nhưng chính app gặp "chuyển nhà": thư mục sandbox của app có mã UUID và **đổi sau mỗi lần cài
  lại/cập nhật**. Không lưu đường tuyệt đối vào save; lưu tương đối so với `Application.persistentDataPath` rồi ghép lại lúc chạy.
- **Android**: `/sdcard` là symlink tới `/storage/emulated/0` (qua `/storage/self/primary`), cùng một file có nhiều tên, đúng chuyện hai
  mặt. `Application.streamingAssetsPath` nằm *trong APK* (`jar:file://…`), không mở bằng `File.ReadAllText` được, phải dùng
  `UnityWebRequest`. App trên máy không có biến môi trường để cấu hình; cấu hình đi bằng define lúc build.

## Lab

1. `python3 lab/07_duong_dan_env.py`: bốn phần, tự dựng và tự xoá thư mục tạm.
   - **Hai mặt**: `pwd` vs `pwd -P`, `ls ../tools` vs `cd .. && ls tools`; rồi gọi script qua lớp phủ, so gốc theo `abspath` / `realpath`,
     `cd` / `cd -P`.
   - **Rò `GIT_INDEX_FILE`**: hook pre-commit thật của repo A hỏi repo B. Commit thường: 0 file (may mắn nhờ đường tương đối). Commit
     bằng index tạm: 42 file "đã stage" ở B; xoá biến: 0.
   - **Biến thử nghiệm**: khoá không đọc `D2Q_STORE` còn nội dung thì đọc; shell thứ hai nhận câu thử nghiệm.
   - **Clone đơn lẻ**: tìm đường `../` treo sau khi clone vào thư mục trống.
2. Trong một bản clone Seriously: `python3 tools/harness/tests/test_repos_paths.py`, rồi tạm sửa `clean_env` trả `dict(os.environ)` và chạy lại.
   Test nào đỏ, và dòng `assertNotEqual` nào bảo đảm test đó không xanh giả? (Hoàn lại sau khi thử.)

## Tóm một dòng

Symlink cho một chỗ hai tên: **tính** bằng tên vật lý (`realpath`, `cd -P`), **tìm hàng xóm** qua manifest chứ không đoán `../`, và coi biến
môi trường là biến toàn cục: xoá `GIT_*` trước khi git sang repo khác, đọc mỗi biến ở một chỗ, rồi chứng minh bằng clone đơn lẻ.

**Bài sau:** 08 — Cổng định kỳ: lệnh kiểm phải biết trả sai.
