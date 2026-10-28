# 00 — Tổng quan: harness sau khi migrate trông ra sao, và 10 bài học lớn nhất

> Bài 0 của chuỗi "migrate thực chiến". Đọc ~12 phút. **Bạn đã biết:** agent là gì (một vòng: đọc → nghĩ → gọi công cụ → đọc kết quả),
> và đại khái "trí nhớ của agent" là chỗ agent tìm lại thứ đã biết (chặng A, B+). Không cần nhớ ký hiệu M1–M11.

## Chuyện mở đầu

Tuần trước, harness của Seriously giống một văn phòng nhỏ dồn hết giấy tờ vào **một cái tủ to** và **một căn phòng** (monorepo).
Tủ càng đầy, agent hỏi "vì sao mình bỏ cách X?" thì càng hay nhận về 12 tờ giấy *gần đúng*. Căn phòng chứa cả 3 game + 7 phòng ban,
clone một lần 4,9 GB.

Trong 3 ngày (26–28/10), ~140 commit, cả văn phòng được **sắp lại tủ** và **chuyển nhà** — mà không ai phải ngừng làm việc.
Bài này là tấm bản đồ: nhìn toàn cảnh trước, các bài sau mới mổ từng mảnh.

## Dừng 30 giây

Tự hình dung trước khi đọc tiếp:
- Nếu bạn chỉ được đưa cho agent **3 tờ giấy** mỗi lần, thì "tìm được trong top 12" còn có ý nghĩa bao nhiêu?
- Bạn chuyển thư mục `Thousandfold/` sang một repo git khác. Đoán xem *loại lỗi nào* sẽ xuất hiện nhiều nhất: lỗi trong code game,
  hay lỗi trong mấy script "nhỏ nhặt" chạy quanh nó?
- Một ý tưởng nghe rất hợp lý ("cho thêm thông tin vào câu hỏi thì tìm tốt hơn"). Bạn đặt cược nó thắng bao nhiêu phần trăm?

(Đáp án nằm rải trong bảng ở mục 3.)

---

## 1. Harness bây giờ — một hình

Harness = mọi thứ bao quanh model để nó làm việc thật. Ở Seriously sau migrate, nó có 4 khối:

```
                ┌──────────────────────── HUB (repo Seriously) ────────────────────────┐
                │  tools/  (kit, hook, cổng)   company/ (sơ đồ, hộp thư, số đo)  docs/  │
                │  Thousandfold ──symlink──┐   depts ──symlink──┐   June/ NanoSwarm/   │
                └──────────────────────────┼───────────────────────┼───── (đóng băng) ──┘
                                           ▼                       ▼
        ../seriously-thousandfold/   (git riêng, CI riêng)   ../seriously-depts/   (git riêng)
           Thousandfold/  + "lớp phủ": tools→hub, docs→hub, company→hub …  (symlink ngược)

  ① ĐỌC   câu hỏi ─► nhận diện tên riêng ─► lễ tân chọn tủ ─► mỗi tủ tìm theo cách của nó ─► trộn ─► bơm ≤ 3 mảnh vào agent
  ② GHI   sửa file/commit ─► cổng pre-commit (ghi sai tủ? tài liệu nào "nghi cũ"?) ─► hết phiên: Stop hook ghi "claim" có ngày
  ③ ĐO    bộ vàng 103 + 33 câu có đáp án ─► `kit memory-gates` (0 token, ~20 s) chấm 6 cổng mỗi 10 ngày
  ④ NHÀ   hub giữ công cụ + chỉ mục chung; mỗi game/phòng ban một repo; `kit commit` tự chia commit theo repo
```

Ví dụ đời thường cho từng khối:
- **① Đọc** = thủ thư. Bạn hỏi "lần trước mình chốt màu lá thế nào?", thủ thư không lục *cả thư viện* mà biết ngay: câu "chốt … thế nào"
  → kệ "quyết định"; có chữ "màu lá" → đúng mục đó. Đưa bạn 3 tờ, không phải 12.
- **② Ghi** = người giữ sổ. Mỗi lần bạn sửa tài liệu A, họ tra "ai đang trích A?" và dán nhãn "có thể cũ" lên những tài liệu đó.
- **③ Đo** = bài kiểm tra định kỳ cho thủ thư, câu hỏi cố định, đáp án biết trước.
- **④ Nhà** = mỗi phòng ban một căn hộ riêng, nhưng hành lang (tools, docs) vẫn chung — đi đâu cũng như cũ.

## 2. Đã migrate những gì (R1 → R11, nói gọn)

| Bước | Làm gì (lời thường) | Kết quả thật |
|---|---|---|
| R1 | Đo đúng thứ agent thấy: chấm "trúng trong 3 tờ đầu", không chấm 12 | có số @3, @12, MRR cho mọi nhóm câu |
| R2 | Bộ đề lớn hơn: mỗi nhóm ≥ 30 câu, lấy từ commit thật | 33 câu diễn đạt lại (para), 103 câu theo mục đích |
| R3 | Nhận diện tên riêng ("bầy" ≠ "bay"), dọn bí danh rác | 85 % câu para nhận ra tên riêng — **nhưng tìm không tốt hơn** → tắt |
| R4 | Bỏ một loại mũi tên khỏi việc lan "nghi cũ"; tham chiếu bằng ID thay đường dẫn | cảnh báo "nghi cũ" **82 → 2** (cả 2 đúng) |
| R5 | Trộn kết quả nhiều tủ | trộn mạnh tay **làm hỏng** nhóm liên phòng (33 → 13 %); hạn ngạch 2 chỗ: 33 → 47 % |
| R6 | Viết lại câu hỏi; doc2query (máy đặt sẵn câu hỏi cho từng commit) | viết lại bằng luật: 6/33 = 6/33 (vô ích); doc2query: 6 → 9/33 |
| R7 | Cuối phiên ghi "claim" (mệnh đề có ngày) | ước ~2k token/ngày trước khi bật → bật |
| R8 | Đo lúc dùng thật: mảnh bơm vào có được agent mở ra không | 25 % (mẫu nhỏ, chưa đặt ngưỡng) |
| R9–R11 | Tách repo: Thousandfold + depts ra repo riêng, hub giữ symlink | clone 4,9 GB → 375 MB; 18 % việc phải sửa 2 repo |

## 3. Mười bài học — mỗi kỹ thuật nhỏ tác động ra sao

Cột "không dùng thì sao" và "cách khác" là chỗ đáng đọc nhất. Mỗi dòng sẽ thành (một phần của) một bài sau.

| # | Kỹ thuật | Ví dụ dễ hình dung | Không dùng thì sao | Cách khác & vì sao không chọn | Số thật |
|---|---|---|---|---|---|
| 1 | **Chấm @3 thay @12** | Thi trắc nghiệm: được khoanh 12 đáp án thì ai cũng "đúng" | Báo cáo đẹp giả: para@12 14/33 trông ổn, nhưng agent chỉ thấy 3 tờ → thật ra 9/33 | Chấm tay từng câu: chính xác nhưng không lặp lại được hằng tuần | kw @12 33/33, @3 32/33; para @12 14, @3 9 |
| 2 | **So cặp (McNemar)** thay so % | Hai học sinh cùng đề: xem *câu nào* đổi đúng/sai, không chỉ tổng điểm | 6→7/33 bị đọc là "tiến bộ" trong khi chỉ là nhiễu | Khoảng tin cậy Wilson: cần ≥ 30 ca/nhóm mới có nghĩa | para "được 4, mất 0", p = 0,125 → *chưa chắc* |
| 3 | **Dọn bí danh trước khi thông minh hơn** | Danh bạ có "BI DUYET" là tên một người → gọi nhầm hoài | Mọi câu có chữ "duyệt" bị link sai thực thể | n-gram trước, dọn sau: thông minh trên dữ liệu bẩn = sai nhanh hơn | `entities.toml` 108 tự sinh + 20 tay |
| 4 | **Bỏ 1 loại cạnh khỏi lan truyền** | Chuông báo cháy nối cả tòa → ai nấu cơm cả tòa sơ tán | 82 cảnh báo, người ta thôi đọc (báo động giả = không báo động) | Giữ hết rồi lọc điểm: vẫn ồn, thêm tham số phải chỉnh | 82 → 2, cả 2 đúng |
| 5 | **ID ổn định (`kg://id`) thay đường dẫn** | Gọi người bằng số CCCD, không bằng địa chỉ nhà | Chuyển nhà (tách repo) là gãy hết liên kết | Đường dẫn tương đối: gãy ngay khi đổi độ sâu thư mục | 36 refs → 0 refs đường dẫn |
| 6 | **Trộn theo thứ hạng (RRF) + hạn ngạch** | Chọn đội tuyển từ 2 lớp: lấy theo *hạng* trong lớp, và mỗi lớp có tối thiểu chỗ | Một tủ "ồn" chiếm hết 3 chỗ | Trộn theo điểm thô: điểm tủ này không so được với tủ kia | xdept 33 → 47 %, ALL 76,7 → 78,6 % |
| 7 | **Ước token *trước* khi bật model** | Hỏi giá trước khi gọi món | Lần thí điểm "thẻ" trước đó lệch chi phí **×5** | Bật rồi xem hoá đơn: tiền đã tiêu | doc2query ước 0,42M, thật 0,40M; thinking ăn 212/341 tok ra → tắt |
| 8 | **Ý "nghe hợp lý" phải qua bộ đề** | Thuốc mới phải thử lâm sàng | Giữ lại 3 tính năng tốn ms mà 0 lợi | Tin trực giác: nhanh, nhưng ở đây trực giác sai 3/4 lần | viết lại câu 6=6; link thực thể 10→11 mà MRR giảm; RRF mạnh làm lùi |
| 9 | **Lớp phủ symlink khi tách repo** | Chuyển nhà nhưng giữ nguyên số phòng trên bản đồ | Phải sửa *mọi* script đang gọi `../tools/...` | Git submodule: mỗi lần sửa tools phải bump con trỏ ở 2 repo; sparse-checkout: vẫn 1 lịch sử, không tách quyền | 338 test xanh sau cutover, lệnh cũ chạy y nguyên |
| 10 | **Một helper `repo_of(path)` dùng chung** | Một bảng chỉ đường "phòng này ở toà nào" | Mỗi script tự đoán → git báo "beyond a symbolic link", web HQ trống trơn | Copy đoạn tìm repo vào từng file: 10 bản, 10 kiểu sai | sửa xong: HQ thấy lại 421 commit Thousandfold/30 ngày |

**Quy luật rút ra:** ở harness, *đo đúng* và *bớt ồn* thắng *thông minh hơn*. Ba trong bốn ý "làm thông minh hơn" (viết lại câu, link
thực thể, trộn mạnh) bị số đo bác; hai việc "bớt" (bỏ cạnh, hạn ngạch) và một việc "đặt sẵn" (doc2query) mới thắng.

## 4. Vấn đề thực tế lúc chuyển nhà (đáp án câu đoán số 2)

Code game không hỏng dòng nào. Gần như **mọi** lỗi nằm ở script quanh nó — vì script ngầm giả định "mọi thứ ở trong một repo":

| Lỗi gặp thật | Vì sao | Sửa | Bài học |
|---|---|---|---|
| `kit` gọi qua symlink tính sai gốc repo | `cd` giữ đường "ảo"; cần `cd -P` / `realpath` | mọi script lấy gốc từ `realpath(__file__)` | Đường dẫn có 2 mặt: logic và vật lý |
| Pre-commit ở repo game báo "1836 file đổi" | hook chạy `git diff` ở hub nhưng mang biến `GIT_INDEX_FILE` của repo game | `_git()` xoá mọi biến `GIT_*` trước khi gọi | Biến môi trường rò giữa repo = lỗi im lặng |
| Cạnh "hay sửa cùng nhau" luôn = 0 **từ ngày đầu** | `--format=@@` git từ chối, script nuốt lỗi | `tformat:@@` → 137 cặp | Migrate làm lộ lỗi cũ: chuyển nhà mới thấy đồ hỏng |
| `a/**/*.md` bỏ sót file nằm thẳng trong `a/` | pathspec thiếu `:(glob)` | `repos.log(glob=True)` | Cú pháp git có "chế độ" ngầm |
| Nhật ký vấp bị chia đôi theo repo | mỗi repo `.git` riêng | luôn ghi vào `.git` của hub | Dữ liệu đo phải có **một** chỗ |
| Việc CI bị đánh dấu "xong" dù test đỏ | lệnh kiểm `gh workflow run` luôn exit 0 | đổi sang `gh run watch --exit-status` | Lệnh kiểm phải *có khả năng* trả sai |
| Clone cả cây làm đầy đĩa (còn 2,4 GB) | clone có checkout | `--no-checkout`, `os.rename` thay vì chép | Ước tài nguyên trước như ước token |
| 22 tiến trình đang đứng trong thư mục | phiên Claude/Unity/Blender đang mở | cutover kiểm `lsof`, từ chối nếu có (trừ `--force`) | Chuyển nhà khi còn người ở = mất đồ |
| Claude mở ở đường mới mất lịch sử phiên | Claude đặt "key" project theo đường vật lý | symlink key mới → key cũ | Công cụ ngoài cũng có giả định về đường dẫn |

## 5. Kiến trúc này hay ở đâu, và cái giá

**Hay:**
- **Tất định trước, model sau.** Phần lớn đường đọc là luật + BM25 (0 token, ~12–23 ms). Model chỉ dùng ở doc2query (chạy *một lần*
  lúc ghi, không phải mỗi câu hỏi) và claim cuối phiên (~2k tok/ngày). So với "mọi câu hỏi gọi model viết lại": rẻ hơn hàng trăm lần,
  và chạy lại cho cùng kết quả → đo được.
- **Mọi bước có cổng số.** Không đạt thì *tắt mặc định*, giữ code sau cờ (`RECALL_FUSE`, `RECALL_ENT`) — không xoá, không cãi nhau.
- **Tách repo mà không đổi thói quen.** Phiên agent vẫn gõ `../tools/claude/kit.sh` như cũ; chỉ git đổi chỗ.

**Cái giá:**
- 18 % việc giờ phải commit ở 2 repo (chủ yếu art ↔ Thousandfold). Không có `kit commit` tự chia thì 1/5 phiên sẽ vấp.
- Câu hỏi diễn đạt lại (para) vẫn yếu: 9/33 trong 3 tờ đầu. Đây là giới hạn của tìm theo chữ — bài sau bàn có nên dùng vector không.
- Lớp phủ symlink chạy tốt trên Mac; Windows thì khó (mục 6).

## 6. Bốn nền tảng

| | Mac (máy đang chạy) | Windows | iOS | Android |
|---|---|---|---|---|
| Symlink (lớp phủ) | có sẵn, git lưu được | cần Developer Mode/quyền admin; git mặc định `core.symlinks=false` → symlink thành file chữ. Thay bằng *junction* (`mklink /J`) cho thư mục | không chạy harness trên máy; build Xcode trên Mac đọc qua symlink bình thường | không chạy harness; Gradle đi theo symlink được, nhưng Unity export nên trỏ đường vật lý |
| `cd -P` / `realpath` | có | Git Bash có; PowerShell dùng `(Get-Item x).Target` | — | — |
| Kiểm "ai đang đứng trong thư mục" | `lsof +D` | Resource Monitor / `handle.exe` (Sysinternals) | — | — |
| Chỗ cần nhớ | đường Claude key theo đường vật lý | đường có `\` và ổ đĩa → `realpath` khác dạng | build cần Mac → harness luôn có 1 máy Mac | CI Android chạy được trên Linux runner rẻ hơn |

## 7. Lộ trình chuỗi này

| Bài | Chủ đề | Từ dòng nào ở mục 3–4 |
|---|---|---|
| 01 | Đo đúng thứ agent thấy: @3, MRR, so cặp, bộ đề ≥ 30 câu | 1, 2, 8 |
| 02 | Tên riêng & bí danh: vì sao "nhận ra" chưa chắc "tìm ra" | 3 |
| 03 | Báo động giả: lan "nghi cũ" và ID ổn định | 4, 5 |
| 04 | Trộn nhiều tủ: RRF, hạn ngạch, khi nào trộn làm hỏng | 6 |
| 05 | Model ở phía ghi: doc2query, claim, ước token trước | 7 |
| 06 | Chuyển nhà: lớp phủ symlink so với submodule/sparse/monorepo | 9, chỉ số D7 |
| 07 | Lỗi chuyển nhà: đường dẫn 2 mặt, biến môi trường rò, lỗi cũ lộ ra | 10, mục 4 |
| 08 | Cổng định kỳ & harness tự kiểm: `memory-gates`, lệnh kiểm phải biết trả sai | mục 4 (CI), mục 5 |

## Tóm một dòng

Migrate thành công không nhờ thêm trí thông minh, mà nhờ **đo đúng chỗ, bớt ồn, ước giá trước, và một lớp phủ để không ai phải đổi thói quen**.

**Giờ bạn biết thêm:** harness có 4 khối (đọc · ghi · đo · nhà); @3 vs @12; vì sao 3/4 ý hay bị bác; lỗi migrate nằm ở script chứ không ở game.

**Bài sau:** [01 — Đo đúng thứ agent thấy](01-do-dung-thu-agent-thay.md) *(sắp viết)*.

## Thuật ngữ

| Từ | Nghĩa thường |
|---|---|
| harness | mọi thứ quanh model: công cụ, hook, cổng, trí nhớ, đo |
| hub | repo trung tâm giữ công cụ + chỉ mục chung |
| monorepo | một repo chứa mọi dự án |
| symlink | "lối tắt" thư mục: mở nó là vào thư mục ở chỗ khác |
| lớp phủ | các symlink ngược trong repo tách để nó *thấy* hub như trước |
| @3 / @12 | đáp án đúng có nằm trong 3 / 12 kết quả đầu không |
| MRR | điểm theo vị trí: đáp án ở hạng 1 = 1, hạng 2 = 0,5, hạng 3 = 0,33 … lấy trung bình |
| McNemar | phép so cặp: chỉ đếm câu *đổi* kết quả giữa trước/sau |
| para | câu hỏi diễn đạt lại, không dùng đúng chữ trong tài liệu |
| bí danh | các cách gọi khác của cùng một thứ |
| RRF | trộn nhiều danh sách theo *thứ hạng*, không theo điểm |
| doc2query | lúc ghi, cho model đoán sẵn "người ta sẽ hỏi gì về đoạn này" rồi lưu kèm |
| claim | một mệnh đề có ngày bắt đầu/hết hiệu lực; cái cũ được đóng ngày chứ không xoá |
| cổng | điều kiện số phải đạt mới sang bước sau |
| nghi cũ | nhãn "có thể đã lỗi thời" dán lên tài liệu B khi thứ B dựa vào (A) vừa sửa mà B chưa sửa theo; máy tìm B bằng cách đi ngược mũi tên "B dựa vào A". Ví dụ: sửa `SwarmPrototype.cs` → GDD trích nó bị nghi cũ. Chuẩn gọi là *stale detection / impact analysis* |
