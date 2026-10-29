# 06 — Chuyển nhà: lớp phủ symlink, submodule hay monorepo

> Bài 6 của chuỗi "migrate thực chiến" (mổ **bước 4** ở [bài 00](00-tong-quan.md): chuyển RAM sang máy khác, tức tách repo).
> Đọc ~15 phút + lab 5 phút. Mang vào: GUID/`.meta` (bài 00), Unity Package Manager (`Packages/manifest.json`), địa chỉ ảo / vật lý của CPU.

## Chuyện mở đầu

10:20 ngày 28/10, Thousandfold và các phòng ban (`depts/`) chuyển sang repo riêng. Code game không đổi dòng nào, selftest 338 ca xanh.
Hôm sau, clone repo game vào một thư mục trống: `kit selftest` không chạy, 21/21 hook phiên hỏng, hook chặn lệnh nguy hiểm tắt im
lặng, commit không qua cổng nào. 14 lỗi. Nhà mới đứng được chỉ vì vẫn dựa vào tường nhà cũ.

## Dừng 30 giây

Bạn có sanne-kit dùng chung cho 3 game. Hình dung ba cách đưa nó vào game: chép thẳng vào `Packages/` mỗi game, trỏ `file:../sanne-kit/…`,
hoặc git URL kèm tag. Với mỗi cách, tự trả lời: sửa một bug trong kit thì phải commit mấy chỗ, clone game sang máy mới thì thiếu gì,
và lúc nào game lặng lẽ chạy bản kit khác hôm qua. Giữ ba câu đó. Cả bài là ba câu này, áp cho chính harness.

---

## Mạch của bài

```
1. Monorepo 4,9 GiB, git chậm                 → tách; nhưng 18 % việc chạm 2 repo → phải chọn cách tách
2. Ba cách: monorepo / submodule / lớp phủ    → lớp phủ thắng vì ngày đầu 0 dòng code đổi → nhưng nó che phụ thuộc
3. Bỏ "2 tuần song song", thay bằng cổng       → cutover xanh, gỡ bản cũ cùng ngày → hôm sau clone đơn lẻ lộ 14 lỗi
4. Nợ phải đo, không cảm                       → công thức có trọng số: 1480,5 → một API + manifest → 383,5
5. Khoá nợ bằng mốc, gỡ từng symlink           → 39 → 18 symlink; 18 cái còn lại có hạn trả, không có "để sau"
```

## 1. Vì sao tách, và tách thì tốn gì

Số đo trước khi tách (`tools/harness/d7-2026-10-28.md`, git cục bộ 28/10):

| Repo | File | Pack cục bộ | `git status` |
|---|---|---|---|
| Seriously (monorepo: 3 game + 7 phòng + harness) | 19.997 | 4,91 GiB | 0,16–0,23 s |
| seriously-thousandfold | 2.221 | 375 MiB | 0,03–0,06 s |
| seriously-depts | 2.609 | 900 MiB | 0,04–0,07 s |

Lợi rõ: clone game nhỏ hơn ~13 lần, git nhanh hơn ~4 lần. Hook và cổng gọi git liên tục, nên 0,2 s → 0,05 s được trả lại ở mọi lượt.

Cái giá đo cùng ngày, bằng **dữ liệu cũ**: lấy 277 việc đã làm (mỗi việc có danh sách file trong `company/records/tasks.jsonl`), gán
từng file vào repo *sau khi tách*, đếm việc chạm hơn một repo:

| | Việc | Chạm > 1 repo |
|---|---|---|
| Tổng 3 tuần | 277 | **49 (18 %)** |
| Tuần 42 → 43 → 44 | 84 → 125 → 68 | 5 % → 21 % → **28 %** (đang tăng) |

Gần hết là cặp art ↔ Thousandfold: phòng art làm model rồi ghi thẳng vào `Thousandfold/Assets/Art/Port`. Kết luận của bản đo: tách được,
nhưng **bắt buộc** `kit commit` tự chia commit theo repo, không thì 1/5 số việc sẽ vấp.

So với Unity: monorepo giống một scene khổng lồ mọi người cùng sửa. Tách repo giống chia thành nhiều scene *additive*: mỗi scene nhẹ,
mở nhanh, nhưng object nào tham chiếu chéo scene thì phải có cơ chế riêng. Con số 18 % chính là "tỉ lệ tham chiếu chéo scene".

## 2. Ba cách tổ chức nhiều repo

### 2a. Giữ monorepo

Một lịch sử, một commit sửa được cả game lẫn tool cùng lúc (*atomic commit*), đường dẫn tương đối luôn đúng. Gãy ở kích thước: clone,
`git status`, CI đều trả theo cả cây. Google, Meta giữ monorepo khổng lồ, nhưng bằng hệ thống file ảo và build system riêng. Với git
thường, thuốc giảm đau là *sparse-checkout* (chỉ checkout vài thư mục) và *partial clone* (`--filter=blob:none`, tải nội dung file khi cần).
Hai thứ này giảm đĩa và `git status`, không giảm việc mọi phiên cùng sửa một lịch sử.

### 2b. Submodule / subtree

*Submodule* = repo cha lưu một **con trỏ** (mã commit, gọi là *gitlink*) tới repo con, đường dẫn ghi trong `.gitmodules`. Ưu: ghim chính
xác bản nào, tái lập được. Gãy:
- Sửa trong repo con xong phải commit **lần nữa** ở repo cha để dời con trỏ (*bump*). Quên bump thì cha vẫn trỏ bản cũ.
- Clone quên `--recurse-submodules` thì thư mục con rỗng. Repo con mặc định ở *detached HEAD*: commit vào đó dễ mất.

*Subtree* = chép hẳn nội dung + lịch sử repo con vào repo cha. Không có con trỏ, clone là đủ. Gãy ở chiều ngược: đẩy sửa đổi về repo
con phải `git subtree split`/`push`, lịch sử hai bên trộn nhau khó đọc.

Seriously bỏ submodule vì `tools/` được nhiều phiên sửa mỗi ngày: mỗi lần sửa tool, mọi repo con dùng nó phải bump. Lab mục 3 đếm: cùng
10 việc, submodule cần 20 commit, lớp phủ 13.

### 2c. Lớp phủ symlink + manifest (cách Seriously chọn)

*Symlink* = một tên file trỏ sang đường dẫn khác. *Lớp phủ* = đặt symlink sao cho đứng ở đâu cũng thấy cây thư mục như monorepo cũ.
Hai chiều, nhìn thật trên máy:

```
Seriously/                       (hub: harness, docs, company)
  Thousandfold -> ../seriously-thousandfold/Thousandfold
  depts        -> ../seriously-depts/depts
seriously-thousandfold/          (repo game)
  Thousandfold/                  (thư mục thật)
  tools     -> ../Seriously/tools      ┐ symlink ngược, gitignored
  docs      -> ../Seriously/docs       │ (ghi vào .git/info/exclude,
  CLAUDE.md -> ../Seriously/CLAUDE.md  ┘  không commit)
```

Đứng trong `seriously-thousandfold/Thousandfold`, lệnh cũ `sh ../tools/claude/kit.sh compile` vẫn đúng. *Manifest*
(`company/workspace.toml`) ghi repo nào gồm thư mục nào, nằm đâu, remote nào. Code dựng lớp phủ (`tools/claude/workspace.py`):

```python
def link(r, root=None, quiet=False):
    for n in overlay_names(r):                          # mọi mục cấp gốc của hub, trừ thư mục của chính repo này
        p = root / n
        if p.is_symlink() and p.resolve() == (HUB / n).resolve():
            continue                                    # đã đúng → không làm gì (chạy lại an toàn)
        if p.exists() or p.is_symlink():
            print(f"  bỏ qua {n}: {root.name} đã có mục riêng tên này")
            continue
        p.symlink_to(os.path.relpath(HUB / n, root))    # đường TƯƠNG ĐỐI: dời cả cặp thư mục vẫn đúng
    write_block(gd / "info" / "exclude", ...)           # tên phủ + bản chép .gitignore hub → git repo tách không thấy chúng
```

Hàm này *idempotent*: chạy lại 10 lần cho cùng kết quả. Đó là điều kiện để lệnh chuyển nhà chạy lại được khi hỏng giữa chừng.

**Chuyển nhà (cutover) làm gì**, theo `workspace.cutover`:
1. Từ chối nếu có tiến trình đang đứng trong thư mục (`lsof -d cwd`), trừ `--force`. Ngày 28/10 dry-run thấy 22 tiến trình trong
   `Thousandfold/`, 10 trong `depts/`.
2. `git filter-repo --path Thousandfold` từ HEAD hub. Phép lọc *tất định*: cùng lịch sử vào → cùng mã commit ra, nên push lên remote là
   *fast-forward*, không ghi đè.
3. `os.rename(hub/Thousandfold, repo_tách/Thousandfold)`: **dời, không xoá**. Cùng ổ đĩa nên gần như tức thì, và mang theo `Library/`,
   file chưa commit của phiên khác (thư mục depts mang theo 449 file đang sửa dở).
4. Hub: `git rm -r --cached` + `.gitignore`. Lịch sử cũ giữ nguyên, không viết lại; tag `pre-split-2026-10-27` đặt từ hôm trước làm điểm quay về.

**Gãy ở đâu.** Lớp phủ đánh lừa con người và script, nhưng không lừa được git: git **không đi qua symlink**.

```
$ git log -- Thousandfold/Assets/a.txt     # ở hub
(rc 0, 0 dòng)                             ← im lặng
$ git add Thousandfold/Assets/a.txt
fatal: pathspec 'Thousandfold/Assets/a.txt' is beyond a symbolic link
```

Lệnh `log` không báo lỗi mà trả rỗng; lệnh nào trộn path qua symlink với path thường thì chết cả lệnh. Trang quản lý (web HQ) gom `depts`
vào cùng một lệnh `git log` nên hiện trống hoạt động git của **cả hub**. Sửa bằng một hàm
dùng chung: tìm repo *thật* chứa file, chạy git ở đó (`tools/company/repos.py`):

```python
def repo_of(path, hub=None):
    """(gốc repo git thật, path tương đối trong repo đó)."""
    h = os.path.realpath(hub or HUB)
    p = os.path.realpath(path if os.path.isabs(path) else os.path.join(h, path))   # đi xuyên symlink
    if p == h or p.startswith(h + os.sep):
        return h, os.path.relpath(p, h)          # nằm hẳn trong hub: khỏi gọi git
    ...
    top = toplevel(d)                            # git rev-parse --show-toplevel ở thư mục VẬT LÝ
```

Đây là chuyện *alias* quen thuộc của CPU: hai địa chỉ ảo cùng trỏ một trang vật lý. Cache đánh chỉ mục theo địa chỉ ảo sẽ coi là hai
dòng khác nhau. Cách chữa giống nhau: **dịch sang địa chỉ vật lý trước khi so** (`realpath`). Hai lỗi họ hàng (đường dẫn hai mặt khi
`cd` qua symlink, biến `GIT_*` của repo này rò sang lệnh git ở repo kia) là chủ đề bài 07.

### So sánh

| Cách | Ưu | Gãy ở đâu | Ở Seriously |
|---|---|---|---|
| Monorepo | commit nguyên tử; đường dẫn luôn đúng | kích thước (4,91 GiB), `git status` 0,2 s, CI chạy cả cây | June, NanoSwarm (đóng băng) vẫn ở đây |
| Monorepo + sparse / partial clone | giảm đĩa, giữ một lịch sử | không giảm việc mọi phiên chung một lịch sử; cấu hình theo máy | không dùng |
| Submodule | ghim đúng commit, tái lập | 2 commit mỗi việc (bump); thư mục rỗng khi quên `--recurse-submodules`; detached HEAD | bỏ: `tools/` đổi hằng ngày |
| Subtree | clone là đủ, không con trỏ | đẩy ngược về repo con rắc rối; lịch sử trộn | không dùng |
| **Lớp phủ symlink + manifest** | 0 dòng code đổi ngày đầu; chuyển dần được | git không đi qua symlink; đường dẫn hai mặt; repo tách không tự đứng được (phụ thuộc bị che) | cách đang dùng, đang trả nợ (mục 4–5) |
| Package có phiên bản (thư viện cài qua tag / registry) | mỗi repo tự đứng, ghim bản | phải tách API rõ, phát hành mỗi lần đổi | sanne-kit; harness đang đi về đây (`kit` cài được, mục 5) |

## 3. "Chạy song song 2 tuần", và thứ thay nó

Thiết kế gốc (`docs/shared/knowledge-graph-design.md` §6.3) ghi: tách xong, giữ bản trong monorepo **chỉ đọc**, chạy song song 2 tuần
(tới 10/11); chỉ gỡ khi cả 2 tuần xanh: selftest mọi repo, 0 tham chiếu gãy, thời gian chờ không xấu đi.

Vì sao 2 tuần (suy luận, không có trong repo): việc định kỳ hằng tuần (weekly, báo cáo) chạy ít nhất 2 lần; đường hiếm (phát hành, CI một
game ít đụng) có cơ hội chạy. Đây là ý của *dual-run* / *strangler fig* (Fowler): đường mới chạy cạnh đường cũ, dời dần, gỡ đường cũ cuối
cùng. Trong game, giống giữ build cũ trên store song song với build mới cho một nhóm nhỏ người chơi.

**Chuyện thật:** sáng 28/10, Bi quyết "không chờ 11/11, đo bằng dữ liệu cũ". 2 tuần song song được thay bằng cổng:
- selftest xanh ở hub, pre-commit chạy được trong 2 repo tách;
- `kit company lint` 0 tham chiếu gãy; `kit company scan` thấy đủ 13 bộ phận như trước;
- bảng D7 ở mục 1, tính từ dữ liệu cũ (sau tách đo lại: 17,8 %, khớp 18 %);
- cutover từ chối khi còn tiến trình trong thư mục.

Cổng xanh, bản cũ gỡ **cùng ngày** (1,5 GB). Lưới an toàn còn lại: lịch sử không viết lại, tag `pre-split`, phép lọc tất định (tách lại ra
đúng mã commit cũ).

**Cái giá.** Những thứ lộ ra *sau* khi gỡ, ghi trong `tools/harness/r11-cutover.md`:
- cạnh "hay sửa cùng nhau" trong đồ thị tri thức bằng 0 **từ đầu** vì `--format=@@` bị git từ chối mà lỗi bị nuốt; chỉ lộ khi chuyển code
  sang hàm mới;
- log vấp của agent bị chia theo repo (repo tách đã có 12 dòng riêng mà bộ đếm ở hub không thấy);
- CI việc "25 test đỏ" được đánh dấu xong vì lệnh kiểm `gh workflow run` luôn trả 0;
- hôm sau: 14 lỗi khi clone đơn lẻ (chuyện mở đầu).

Điểm đáng nhớ nhất: **2 tuần song song cũng không bắt được 14 lỗi kia**. Trong 2 tuần đó mọi phiên vẫn đứng trên lớp phủ, nên mọi đường
`../tools` vẫn đúng. Chạy song song đo *"đường mới chạy được khi dùng thật"*. Nó không đo *"đường mới đứng được một mình"*. Muốn đo cái
sau phải có ca kiểm tường minh: clone vào thư mục trống rồi chạy. Cổng nào chỉ hỏi "có gì hỏng không" sẽ xanh mãi với một hệ đang dựa tường.

## 4. Nợ đo được thay vì cảm giác

"Lớp phủ là nợ kỹ thuật" là một cảm giác. Cảm giác không có cổng, không biết trả đến đâu thì xong. Kế hoạch trả nợ (`tools/harness/symlink-debt-plan.md`)
mở đầu bằng **pha 0 chỉ đọc**: kiểm kê, chốt công thức, rồi **đóng băng** công thức để mọi pha sau đo cùng một thước (như bài 01: đổi thước giữa chừng thì
số trước/sau vô nghĩa).

Công thức (`tools/harness/symlink-debt.md` §4), đơn vị là **dòng** khớp regex trong file tracked, bỏ test:

```
nợ = 2·A + 0,5·B + 1·C + 3·D + 2·E + 3·F + 5·G
```

| Loại | Nghĩa | Trọng số | Vì sao nặng/nhẹ |
|---|---|---|---|
| A | `../tools`, `../docs`, `../company` trong code / hook / CI | 2 | chạy được chỉ nhờ lớp phủ |
| B | cùng mẫu A trong tài liệu chỉ dẫn agent | 0,5 | quy ước, không phải bug |
| C | chuỗi `Thousandfold/`, `depts/` trong code hub | 1 | phụ thuộc symlink phía hub |
| D | gọi `git` không qua `repos.git_in` / `repos.log` | 3 | git không đi qua symlink |
| E | `cd` không `-P`, `os.getcwd()`, `__file__` + `..` không `realpath` | 2 | đường dẫn hai mặt |
| F | (⊂ D) git trong file không xoá `GIT_*` | 3, cộng dồn D | lỗi thật đã gặp: báo nhầm "1836 file đổi" |
| G | phụ thuộc ngoài code: hook git, runner CI, khoá project Claude… | 5 / mục | không regex nào quét thấy |

Một lệnh git trần không xoá `GIT_*` = 6 điểm, nặng nhất, vì nó đã gây lỗi thật. Trọng số đặt theo **lỗi đã xảy ra**, không theo cảm giác "trông xấu".

**Số qua các pha** (`kit symlink-debt`):

| Mốc | Nợ | Ghi chú |
|---|---|---|
| Pha 0 (kiểm kê) | 1480,5 | theo quyết định Q4 (bỏ E nội bộ depts, vô hại khi tách): **1384,5** |
| Pha 2 (một API + manifest) | **383,5** | −72,3 %; cổng −70 % = ≤ 415,35 → đạt |
| Pha 3 (repo tách đứng một mình) | 293 | so pha 0: −78,8 % |
| Pha 4 (gỡ symlink) | 282 | ≤ mốc 293 |

Khoản giảm to nhất đến từ một chỗ: 210/237 dòng loại A là **10 bản sao** cùng một file `.claude/settings.json` (21 hook mỗi bản). Sửa khuôn một lần,
sinh lại 10 bản: −210 dòng. Giống sửa prefab thay vì sửa 10 instance.

Pha 2 không viết lại mọi script mà dồn về **một API** đọc manifest. Vị trí repo không được đoán (`tools/company/repos.py`):

```python
def path_of(name, hub=None, must_exist=True):
    """Thứ tự: biến môi trường → workspace.toml → RepoPathError. Không đoán ../<tên>."""
    ...
    env = list(ENV_HUB) if name in hub_names else [_env_key(name)]     # KIT_REPO_SERIOUSLY_THOUSANDFOLD
    ...
    if rel is None:
        raise RepoPathError(f'không biết repo {name!r} nằm đâu — đã tìm: {"; ".join(tried)}. '
                            f'Sửa: thêm `path = "…"` cho repo này trong company/workspace.toml, hoặc đặt {env[0]}=<thư mục>.')
```

Ba tầng: máy khác bố trí khác thì đặt biến môi trường; mặc định đọc manifest; không có thì lỗi **nói đã tìm ở đâu và sửa thế nào**. Không
có tầng thứ tư "thử `../` xem sao", vì tầng đó chính là lớp phủ đội lốt.

Thước có nhiễu đã biết: regex D đếm cả chữ `git fetch` nằm trong câu `echo`. Công thức đóng băng nên nhiễu giữ nguyên qua các pha, so trước/sau
vẫn đúng. Một cây thước lệch đều đáng tin hơn một cây thước được "chỉnh cho đúng" giữa chừng.

## 5. Khoá mốc, rồi gỡ từng symlink

**Khoá mốc** (*ratchet*): `tools/harness/symlink-debt-baseline.json` lưu 293. Cổng weekly `kit symlink-debt check`: nợ **tăng** so mốc = đỏ;
không có mốc = đỏ. Trả nợ thật thì hạ mốc. Mốc chỉ đi xuống. Cổng bắt ngay lần đầu: giữa phiên pha 4, phòng art commit một script gọi git trần
(+2 D, +2 F), nợ 293 → 305, đỏ. Gửi việc cho art, art sửa sang `repos.git_in`. Đây là kiểu *lint baseline*: không đòi sửa hết nợ cũ ngay,
chỉ cấm thêm nợ mới.

**Đứng một mình (pha 3)** đổi `kit` từ "đường `../tools/claude/kit.sh`" thành **lệnh cài**: shim `~/.local/bin/kit` trỏ vào hub, có phiên bản
(`tools/claude/VERSION` = 1.0.0). Repo tách ghim bản cần trong `kit.toml`; kiểm ở `tools/claude/kit_install.py`:

```python
if w[0] != h[0]:
    return False, f'hub kit {have} khác major với bản ghim {want} ({p}) — checkout hub đúng major hoặc `kit workspace pin` lại'
if h < w:
    return False, f'hub kit {have} cũ hơn bản ghim {want} ({p}) — `git -C {HUB} pull --ff-only` rồi `kit install`'
```

Luật semver: cùng major, hub ≥ bản ghim. Cổng pha 3 chính là ca còn thiếu ở mục 3: clone repo game vào thư mục **trống**, `kit hooks install --here`,
`kit selftest` → xanh 8/8. Rồi cố tình phá (`git rm hub.sh`) → đỏ. Lệnh kiểm phải biết trả sai (bài 08).

**Gỡ từng cái (pha 4).** `kit symlink-debt links` đếm nợ trỏ qua *từng* symlink. Symlink nào 0 nợ thì gỡ, chạy đủ cổng (selftest hub + 2 repo
tách, nợ không tăng, lint, scan, chạy thật hook phiên từ trong game). Đỏ → `kit workspace link` khôi phục. Xanh → ghi tên vào `unlinked` trong
manifest để lệnh link không tạo lại. Kết quả: **39 → 18 symlink** (gỡ 21).

18 cái còn lại, mỗi cái một lý do và một **hạn**: `tools` của repo game còn 57 dòng trỏ qua (hạn 30/11), `docs` 6 dòng (15/11)… Hai ca dạy nhiều nhất:
- `depts/company`: **0 dòng** nợ trong văn bản, nhưng gỡ ra thì test khuôn settings đỏ (`FileNotFoundError`): code sinh file đi qua symlink đó
  bằng đường tính lúc chạy. Regex không thấy phụ thuộc lúc chạy. Thước đo cuối cùng là **gỡ thử + chạy cổng**, không phải đếm chữ.
- `CLAUDE.md`, `.claude`: Claude Code tự nạp `CLAUDE.md` của thư mục tổ tiên. Phụ thuộc nằm trong công cụ, không trong repo. Hạn: khi có cách nạp
  luật chung riêng cho repo.

## So với Unity: Package Manager đã giải bài này

| Cách đưa sanne-kit vào game | Tương ứng ở bài này | Sửa kit thì | Clone máy mới |
|---|---|---|---|
| *Embedded*: chép thư mục vào `Packages/com.sanne.x/` | monorepo (mỗi game một bản chép) | sửa N bản, trôi dần | đủ |
| *Local*: `"file:../../../sanne-kit/Packages/com.sanne.x"` | **lớp phủ**: chạy nhờ thư mục hàng xóm | sửa 1 chỗ, mọi game thấy ngay, kể cả lúc không muốn | thiếu hàng xóm = lỗi resolve |
| *Git package*: URL + tag | submodule (ghim) | commit kit + tag mới + đổi tag ở game | đủ, Unity tự tải |
| Registry (scoped registry, OpenUPM) | `kit` cài được + `kit.toml` ghim | phát hành bản mới | đủ |

Thousandfold dùng dòng thứ ba, thật (`Thousandfold/Packages/manifest.json`):

```json
"com.sanne.core": "https://github.com/tsan2711/sanne-kit.git?path=/Packages/com.sanne.core#core/1.6.0",
```

`?path=` chọn thư mục con trong repo (nhiều package một repo); `#core/1.6.0` là tag. `packages-lock.json` ghi thêm `"hash": "2447df96…"`: tag là tên
người đọc, hash là thứ thật được dùng, giống con trỏ gitlink của submodule. Package git nằm trong `Library/PackageCache`, chỉ đọc. Muốn sửa
thì *embed* tạm (chép vào `Packages/`), tức là quay về monorepo trong lúc sửa. Luật chung của Bi ("cài qua git URL + tag, không embed / copy")
chính là chọn hàng thứ ba thay vì hàng một và hai.

Harness đi đúng đường đó, chậm hơn một bước: hôm nay là hàng hai (lớp phủ), pha 3 thêm phiên bản + ghim (nửa đường sang hàng bốn), pha 5 gỡ
nốt `tools` để repo game chỉ gọi lệnh `kit` đã cài.

## Scale

- **Nhỏ (1 game, 1 người)**: monorepo. Tách chỉ thêm việc.
- **Vừa (Seriously: 3 game, 7 phòng, ~20k file, 18 % việc liên repo)**: tách theo **chủ sở hữu** (game, phòng, harness), manifest ghi vị trí,
  một API gọi git, `kit commit` chia commit theo repo. Lớp phủ dùng làm cầu tạm, có công thức nợ và hạn gỡ.
- **Lớn (hàng trăm repo / hàng triệu file)**: hai cực. Monorepo với hệ file ảo + build system biết đồ thị phụ thuộc (Bazel-style), hoặc
  polyrepo mà mọi phụ thuộc chéo đi qua **artifact có phiên bản** (package registry), không có đường dẫn chéo repo nào. Lớp phủ symlink không
  sống nổi ở cỡ này: không ai kiểm kê được 39 symlink nhân 100.

## Bốn nền tảng

- **Mac** (máy đang chạy): symlink có sẵn; `os.rename` trong cùng ổ APFS gần như tức thì (cutover dời 1,5 GB không chép); `lsof -d cwd` tìm
  tiến trình đứng trong thư mục. Chính `/var` trên Mac là symlink sang `/private/var` (lab in ra cả hai), nên so đường dẫn luôn qua `realpath`.
- **Windows**: tạo symlink cần quyền `SeCreateSymbolicLinkPrivilege`: chạy admin, hoặc bật **Developer Mode** (Windows 10 1703 trở lên).
  Git for Windows mặc định `core.symlinks=false`: symlink trong repo được checkout thành **file chữ** chứa đường đích, script đọc nó như thư mục
  sẽ hỏng khó hiểu. Bật bằng `git config --global core.symlinks true` (+ Developer Mode) rồi clone lại. Thay thế cho thư mục: *junction*
  (`mklink /J`), không cần quyền, nhưng chỉ trỏ ổ cục bộ, và `os.path.islink` trả False với junction (Python 3.12 có `os.path.isjunction`). Python cần `os.symlink(…, target_is_directory=True)` cho
  thư mục. Không có `lsof`: dùng `handle.exe` (Sysinternals). `os.rename` khác ổ đĩa sẽ lỗi, cutover phải ở cùng ổ. Kết luận thực tế: trên Windows,
  lớp phủ là thứ đầu tiên vỡ, nên `path_of` + biến `KIT_REPO_*` (pha 2) quan trọng hơn ở đây.
- **iOS**: không chạy harness trên máy. Build Xcode trên Mac; sản phẩm build (Xcode project, `.ipa`) không cần biết asset đến từ repo nào. Runner CI phải có
  đủ repo ở đúng chỗ: đọc từ manifest / `KIT_REPO_*`, không giả định `../` (repo game dùng runner riêng `bi-mac-thousandfold`).
- **Android**: như iOS, máy không biết gì về repo. Gradle build trên Mac / Linux / Windows; trên runner Windows thì vấp đúng chuyện `core.symlinks`
  ở trên, nên CI repo game gọi `kit ci-unity` (lệnh cài, tìm repo qua manifest) thay vì `$SERIOUSLY_REPO/tools/...` qua lớp phủ.

## Lab

1. `python3 lab/06_chuyen_nha.py`: ba phần.
   - **Lớp phủ**: dựng hub + repo tách trong thư mục tạm; `../tools` từ game vẫn đúng; một file hai đường (logic / vật lý); `git log` qua symlink
     trả 0 dòng mà không báo lỗi, `git add` thì `beyond a symbolic link`; gỡ lớp phủ thì đường `../tools` treo.
   - **Nợ đo được**: đếm A/D/E/F với trọng số thật trên 3 file nhỏ, trước/sau khi chuyển sang `repos.git_in` + `kit`; một phiên thêm một dòng git
     trần → cổng mốc đỏ.
   - **Cái giá**: 10 việc giả, đếm việc chạm > 1 repo và số commit dưới monorepo / tách game / tách game + depts, lớp phủ vs submodule.
2. Trong Seriously: `kit workspace status` (symlink nào còn, phủ đủ chưa, lệch commit hub ↔ repo tách) rồi `kit symlink-debt links` để thấy nợ
   trỏ qua từng symlink. Chọn một symlink còn giữ, đọc hạn của nó ở `tools/harness/symlink-debt.md` §7f, và tự nói phải sửa gì để gỡ được.

## Tóm một dòng

Lớp phủ symlink cho chuyển nhà mà 0 dòng code đổi, nhưng vì thế nó **che** mọi phụ thuộc vào nhà cũ: đo nợ bằng công thức đóng băng, dồn về một
API đọc manifest, khoá mốc chỉ đi xuống, và kiểm "đứng một mình" bằng clone vào thư mục trống, vì chạy song song bao lâu cũng không đo được điều đó.

**Bài sau:** 07 — Lỗi chuyển nhà: đường dẫn 2 mặt, biến môi trường rò.
