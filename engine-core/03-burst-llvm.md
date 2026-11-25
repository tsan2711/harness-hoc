# Bài 3 — Burst + LLVM: đọc IR, aliasing, vectorization

> Burst là compiler cho tập con C# ("HPC#") dùng **LLVM**: IL → LLVM IR → pass tối ưu → mã máy theo target. Editor: biên dịch bất đồng bộ (vài lần gọi đầu chạy Mono, trừ khi `CompileSynchronously`); player: AOT. `[official]` Nó bổ sung cho Mono/IL2CPP/CoreCLR, không thay thế. Bài này dạy bạn **đọc kết quả** thay vì tin nhãn `[BurstCompile]`.

## 1. Pipeline và hệ quả
IL (từ assembly sau compile) → front-end Burst dựng LLVM IR có **ngữ nghĩa đã thu hẹp**: không managed reference, không GC alloc, không virtual/exception đa hình, `static readonly` được coi là hằng. Vì kiểu dữ liệu đã "phẳng", LLVM làm được thứ RyuJIT/clang-trên-C++-IL2CPP khó làm: **alias analysis chính xác → vectorize**.
Trong Editor: Burst Inspector (menu Jobs → Burst → Open Inspector) có các view: **Assembly**, **.NET IL**, **LLVM IR (Unoptimized)**, **LLVM IR (Optimized)**, **LLVM IR Optimization Diagnostics** `[official, Burst manual]`. Dùng thường xuyên.

## 2. Ba thứ quyết định "có vector hoá hay không"
**(1) Aliasing.** Không chứng minh được con trỏ không chồng nhau thì LLVM thường phải thêm kiểm tra lúc chạy (hoặc bỏ vector hoá) — số đo ở [bài 5](05-lab-cpu-doan-sai.md). **Trước khi đọc asm trong Editor: tắt Safety Checks**, và nhớ Burst Editor biên dịch bất đồng bộ (vài lần chạy đầu là Mono). Job system cho Burst biết: `NativeArray` trong job với `[ReadOnly]` hoặc ghi vào trường riêng → Burst phát thuộc tính `noalias` cho con trỏ (đó là lý do **safety system và hiệu năng liên quan**: ràng buộc dữ liệu = thông tin cho compiler). Ngoài job: `[NoAlias]` trên tham số/field/struct, `Unity.Burst.CompilerServices.Aliasing.ExpectNotAliased/ExpectAliased` để **khẳng định bằng compile-time**.
**(2) Dependency & float semantics.** Reduction (`sum += a[i]`) cần kết hợp lại phép cộng → chỉ hợp lệ khi cho phép reassociate: `[BurstCompile(FloatMode = FloatMode.Fast)]` (đổi lấy kết quả khác bit ở edge case) — mặc định `Default` giữ IEEE nên **không vector hoá reduction float**. `FloatPrecision.Standard` (~3.5 ULP cho một số hàm) vs `High/Medium/Low`.
**(3) Control flow & stride.** Nhánh trong thân vòng lặp ⇒ if-conversion/mask; gather/scatter (index gián tiếp) rất tệ; stride ≠ 1 trên AoS giết băng thông. Đây là lý do SoA/`NativeArray<float>` rời thắng `NativeArray<struct lớn>` (bài 1 bản cũ).

## 3. Công cụ "hứa với compiler"
- `Unity.Burst.CompilerServices.Loop.ExpectVectorized()` — nếu LLVM **không** vector hoá vòng lặp này, **build lỗi** (intrinsic thử nghiệm: cần define `UNITY_BURST_EXPERIMENTAL_LOOP_INTRINSICS`). Biến hồi quy hiệu năng thành test biên dịch.
- `Hint.Likely/Unlikely(cond)`, `Hint.Assume(cond)` (UB nếu sai — chỉ dùng khi chứng minh được).
- `[SkipLocalsInit]`, `[BurstCompile(CompileSynchronously = true)]` (cho test/Editor có kiểm soát), `OptimizeFor` (Performance/Size/FastCompilation) cho thời gian biên dịch (có báo cáo Burst compile 30 s+ trong dự án lớn `[forum, March thread]`).
- `Unity.Mathematics`: `float4` ánh xạ thẳng `<4 x float>`; `math.select` thay nhánh. `float4` thủ công trên AoS có thể thua SoA scalar được LLVM tự vector hoá — đọc asm để chọn.

## 4. Đọc thử ví dụ
```csharp
[BurstCompile(FloatMode = FloatMode.Fast)]
struct Integrate : IJobParallelFor {
  [ReadOnly] public NativeArray<float> vel;  public NativeArray<float> pos;  public float dt;
  public void Execute(int i) { pos[i] += vel[i] * dt; }
}
```
**Dừng 30 giây**: trong Assembly view, bạn kỳ vọng thấy `vfmadd`/`vmulps`/`vaddps` trên `ymm` (AVX2) hay `xmm`? `Execute(i)` được gọi theo batch — vector hoá xảy ra ở **vòng ngoài** nào? (Gợi ý: Burst bọc `Execute` trong vòng lặp của batch; kiểm bằng IR optimized + remark của vectorizer.) Còn trên Apple Silicon/ARM64 sẽ là NEON `fmla v.4s` — Burst biên dịch theo target (đa target x64: SSE2/SSE4/AVX2…, runtime chọn).

## 5. Điểm gãy
| Hiện tượng | Nguyên nhân thường gặp |
|---|---|
| "Burst nhưng không nhanh hơn" | vòng lặp không vector hoá (alias/float/gather); đọc Optimization Diagnostics |
| Kết quả khác Editor vs player | `FloatMode.Fast`, FMA contraction, target khác |
| Compile chậm / script iteration chậm | quá nhiều generic instantiation, `CompileSynchronously` bừa bãi |
| `NativeArray` trong struct lồng nhiều tầng | mất `noalias` (con trỏ bọc trong struct trong struct) — gỡ bằng `[NoAlias]` / truyền pointer |
| Branch-heavy AI trong Burst | không phải việc của SIMD; cần chia batch theo trạng thái trước |

## 6. Thí nghiệm
1. Chọn job thật nóng nhất. Mở Inspector, chụp Assembly + Optimized IR, ghi: độ rộng vector, có `vfmadd`?, số load/store/phần tử.
2. Thêm `Loop.ExpectVectorized()`. Nếu fail: tìm nguyên nhân trong diagnostics, sửa (layout/alias/float mode), ghi lại.
3. Đo p50/p99 job time (đồng hồ trong code, chạy windowed) trước/sau, ghi băng thông ước tính = byte đọc+ghi / thời gian → so với băng thông RAM máy (M-series ~100+ GB/s; PC DDR5 vài chục GB/s/kênh) để biết **compute-bound hay memory-bound**.
4. `log.md`: roofline thô của job đó.

## 7. Đọc thêm
Burst manual (Optimization guidelines, Aliasing, Inspector); LLVM LangRef (`noalias`, `fast` flags, `llvm.fmuladd`); LLVM docs "Auto-Vectorization in LLVM"; Mike Acton / Matt Pharr ISPC paper (cách nghĩ SPMD→SIMD); Agner Fog (instruction tables) khi cần số chu kỳ.
