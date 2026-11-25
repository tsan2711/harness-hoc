# Bài 5 — Lab CPU: bốn điều dễ đoán sai (số đo thật)
Code: [`lab/`](lab/README.md), output thô: [`lab/results/`](lab/results). **Đo khi load average 30–60:** chỉ tin các chênh lệch lớn hơn ~2×. M2, .NET 9 (CoreCLR) — **không phải** Unity Mono/IL2CPP; dùng để hiểu cơ chế, rồi đo lại trên backend đích.

## 1. Gọi qua interface đã box: chậm hay không?
10M lời gọi (ms, min của 15 lần):
| | Dynamic PGO bật | tắt (`DOTNET_TieredPGO=0`) |
|---|---|---|
| generic `where T: struct` | 4,2 | 4,9 |
| boxed, 1 kiểu | 4,8 | **41,4** |
| mảng `IDamage[4096]`, 1 kiểu | 10,3 | 42,2 |
| mảng `IDamage[4096]`, **8 kiểu xáo trộn** | **211** | 173 |

Cơ chế: Tier0 instrumented ghi nhận kiểu thật; Tier1 sinh **guarded devirtualization** (so method table `cmp x20, x21`, đúng thì inline). Với 8 kiểu trộn, guard đoán trượt phần lớn và CPU còn đoán trượt nhánh: ~20× so với cùng mảng 1 kiểu, PGO không cứu được (còn hơi tệ hơn).
Use case: benchmark 1 loại enemy cho thấy "interface miễn phí"; game thật trộn 8 loại. **Quyết định:** hot loop gom theo kiểu (mỗi loại một mảng), generic-struct. IL2CPP không có PGO runtime nhưng cơ chế dispatch khác CoreCLR — **chưa đo**, đừng bê con số này sang.

Phụ — bounds check (mảng 4 KB trong L1, 10k lượt): `i<a.Length` 5,6 ms, `i<n` 5,9 ms. [Asm Tier1](lab/results/jit-asm.txt) cho thấy vì sao: `SumN` được **loop cloning** — kiểm một lần `a.Length >= n` rồi chạy vòng lặp không check; bản còn `bhs RNGCHKFAIL` chỉ là đường dự phòng.

## 2. Heap sống to có làm GC đắt không?
2.000 frame, mỗi frame 20.000 object ngắn hạn. `young` = 2.000 lần/frame (10 % object mới) ghi vào object già, nên chúng **sống sót**; `old` = cùng số lần ghi nhưng già→già.
| Node sống | none: tổng pause · gc0/1/2 | old | young |
|---|---|---|---|
| 100k | 49 ms · 153/0/0 | 42 ms · 153/0/0 | 5.900 ms · 165/35/**12** |
| 1M | 73 · 153/0/0 | 41 · 153/0/0 | 11.409 · 156/40/**3** |
| 8M | 93 · 153/0/0 | 137 · 153/0/0 | 30.176 · 153/38/**0** |

Đọc được: (a) heap sống lớn gần như không ảnh hưởng khi rác chết trẻ; (b) ghi nhiều vào object già **tự nó** không đắt trong GC (cột `old`; p99 frame tăng vì truy cập ngẫu nhiên); (c) object trẻ bị object già giữ lại mới đắt. **Không** đọc được: vì sao pause tăng theo cỡ heap — ở 8M không hề có gen2, nên "full GC" không giải thích được. `old` cũng không tách được chi phí card marking, vì ghi tham chiếu tới object già không làm bẩn card.
Use case: danh sách sự kiện / cache sống lâu nhận object mới mỗi frame. **Quyết định:** container sống lâu giữ struct hoặc ID. Boehm của Unity là mô hình khác (bài 4), đo riêng.

## 3. "Aliasing chặn vectorization" — không đúng với vòng lặp đơn giản
`pos[i] += vel[i]*dt` (clang 15 -O3, arm64; [remarks](lab/results/vec.txt)): bản có thể alias lẫn `restrict` đều vector hoá. Bản alias thêm **kiểm chồng lấn lúc chạy** rồi chọn đường. `sum_strict` (float) chỉ interleave — IEEE cấm đổi thứ tự cộng; cho `reassociate` thì vector hoá. Gather `a[idx[i]]` không vector hoá.
Phạm vi: đúng cho vòng lặp 2 con trỏ này. `fmla` có được là do clang Apple bật fp-contract mặc định; **đừng suy ra asm của Burst**.
Nơi aliasing đáng lo trong Burst (suy luận, chưa đo): hàm nhận nhiều `float*` không `[NoAlias]`, hoặc hệ số đọc **qua con trỏ** trong vòng lặp (store có thể đè lên nó nên phải load lại). Field `NativeArray` trong job vốn đã được coi là không alias. Kiểm trong Burst Inspector.

## 4. Reorder và false sharing
Litmus store→load (`x=1; r1=y` / `y=1; r2=x`): `r1=r2=0` xảy ra 44/200.000 (lần chạy khác 387), có `MemoryBarrier`: 0. [JitDisasm](lab/results/order.txt) cho thấy `str` đứng trước `ldr`, nên reorder này là của CPU, không phải JIT. x86 cũng cho phép loại reorder này; loại ARM64 mới có (store-store, load-load — bug cờ `ready` tự chế) **chưa đo**.
4 thread × 20M lần ghi, mảng căn 128 B (median): cách 8 B 608 ms · 64 B 127 · 128 B 79 · 256 B 92. Line M2 là 128 B nên 64 B vẫn còn chung line theo cặp.
Use case: `counts[threadIndex]` trong job. **Quyết định:** cộng vào biến cục bộ, ghi một lần; nếu buộc chia sẻ, lấy `[NativeSetThreadIndex]` và stride theo `JobsUtility.CacheLineSize` thay vì hard-code 64 (line khác nhau giữa chip).
