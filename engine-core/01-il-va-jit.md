# Bài 1 — IL, metadata và RyuJIT: một dòng C# đi qua những gì

> Mục tiêu: nhìn một vòng lặp C# và **đoán được** IL, asm, chỗ bounds-check, chỗ copy struct — rồi kiểm lại bằng công cụ.

## 1. Mô hình thực thi của IL (ECMA-335)
- IL là **stack machine có kiểu**: `ldarg/ldloc` đẩy lên evaluation stack, `add/mul` pop 2 push 1. Stack không tồn tại lúc chạy; JIT **importer** biến nó thành cây/ SSA (HIR). Hệ quả: số lệnh IL **không** tương quan với chi phí — chỉ hình dạng dữ liệu và call mới quan trọng.
- Metadata là phần quyết định ngữ nghĩa: bảng `TypeDef/MethodDef/Field/MemberRef/TypeSpec/MethodSpec`. Một lệnh `call` mang **token** tới metadata, không mang địa chỉ → binding trễ, nên có R2R/AOT/trimming/IL2CPP đều làm việc trên metadata + IL.
- Quan trọng với game: IL phân biệt **value type vs reference type** ở mức lệnh: `ldobj/stobj/ldelema` (struct in-place) vs `ldelem.ref`; `box/unbox.any` (alloc heap!) ; `constrained. callvirt` (gọi interface/virtual trên generic T mà không box nếu T là struct).
- `callvirt` luôn **null-check** kể cả cho method không virtual — C# compiler phát `callvirt` để có NRE đồng nhất.

## 2. Đọc thử: vòng lặp tích phân vị trí
```csharp
for (int i = 0; i < n; i++) pos[i] += vel[i] * dt;   // float3[] , float3 là struct 12 byte
```
IL (minh hoạ, rút gọn — hãy tự sinh lại bằng ILSpy/SharpLab, đừng tin bản này):
```
ldarg pos ; ldloc i ; ldelema float3     // địa chỉ managed phần tử (có bounds check)
dup ; ldobj float3                        // copy 12 byte lên stack
ldarg vel ; ldloc i ; ldelem float3       // copy
ldarg dt  ; call float3::op_Multiply(float3, float)
call float3::op_Addition(float3,float3)
stobj float3
```
**Dừng 30 giây** (không có đáp án trong câu hỏi, so ở mục 5): với `Unity.Mathematics.float3` có `op_Multiply` là hàm static nhỏ — ở Mono JIT, IL2CPP, CoreCLR, Burst, mỗi nơi inline nó ở tầng nào? Ai đảm bảo? Bounds check của `pos[i]` và `vel[i]` bị loại ở đâu?

## 3. RyuJIT (CoreCLR) — pipeline cần thuộc
`Importer → Inliner → Morph → SSA/Value Numbering → Loop opts (hoist, clone, unroll) → CSE → Assertion prop / Range-check elimination → Lowering → LSRA (linear scan regalloc) → Codegen`.
- **Inlining** là tối ưu quyết định nhất: heuristic theo kích thước IL, `[MethodImpl(AggressiveInlining)]`, không inline qua EH/ `try`, method có `localloc` (quy tắc EH đổi theo phiên bản: .NET 10 inline được try/finally), callvirt chưa devirtualize.
- **Tiered compilation** `[official: Microsoft docs]`: Tier0 (minopts, nhanh, không inline) → sau **30 lần gọi** + timer ~100 ms background → Tier1. **OSR** (.NET 7+) cho phép method đang chạy vòng lặp lâu vào Tier1 giữa chừng. **Dynamic PGO** (mặc định từ .NET 8): Tier0 instrumented → Tier1 dùng profile (guarded devirtualization, hot/cold layout).
- **ReadyToRun (R2R)**: code tiền-biên-dịch, chất lượng thấp hơn Tier1, được rejit khi nóng. NativeAOT: không JIT, toàn bộ closed-world (chưa viết).
- **Reified generics**: kiểu giá trị → code chuyên biệt cho từng instantiation; kiểu tham chiếu → **chia sẻ code canonical (`__Canon`)** + tra runtime dictionary. Hệ quả: `List<float3>` nhanh, `List<MyClass>` chia code nhưng có tra từ điển; generic virtual method chậm. IL2CPP cũng có generic sharing (xem bài 2).
- **Bounds-check elimination**: `for (i=0;i<arr.Length;i++) arr[i]` bị loại; `i<n` không chứng minh được thì JIT vẫn có thể **loop cloning** (bản nhanh không check sau một lần kiểm trước vòng lặp) — số đo ở [bài 5](05-lab-cpu-doan-sai.md). `Span<T>`/`ref` locals/`MemoryMarshal.GetReference` để vượt — đổi lấy an toàn.

## 4. Điểm gãy thường gặp trong game
| Triệu chứng | Cơ chế |
|---|---|
| Frame đầu chậm, rồi nhanh | Tier0 → Tier1 / JIT warmup (Mono JIT, CoreCLR); IL2CPP không có |
| Operator nhỏ của struct không inline | Mono JIT inline kém hơn RyuJIT; Burst/LLVM thường inline (có ngưỡng chi phí) — xem asm |
| `foreach` trên `List<T>` alloc | struct enumerator OK; qua `IEnumerable<T>` thì **box** |
| Lambda **có capture**, hoặc method group → delegate (`Sort(Compare)`) | alloc mỗi lần (lambda không capture được Roslyn cache) |
| Cast interface trên struct | `box` — kiểm bằng IL, không bằng cảm giác |
| Generic constraint `where T: struct, IFoo` | `constrained. callvirt` → không box, JIT/Burst chuyên biệt hoá |

## 5. Đáp án mục 2 + cách kiểm
- Inline `op_Multiply`: Mono = có nhưng bảo thủ; RyuJIT = Tier1 có (và Tier0 không); IL2CPP = **C++ compiler** (clang/MSVC) inline sau khi il2cpp phát C++; Burst = LLVM inliner (mạnh nhưng không "luôn": có ngưỡng chi phí). Tức là cùng một IL, **bốn bộ tối ưu khác nhau** — benchmark ở Editor Mono **không** dự đoán được player IL2CPP.
- Công cụ: **ILSpy** (tab IL), **SharpLab.io** (C# → IL → JIT asm, chọn Release), `DOTNET_JitDisasm=MethodName` (.NET 7+, chỉ với runtime thật), **Burst Inspector** (bài 3), file `.cpp` của IL2CPP (`Library/Bee/artifacts/...` hoặc thư mục build `il2cppOutput`).

## 6. Thí nghiệm (số đo CoreCLR đối chiếu: [bài 5](05-lab-cpu-doan-sai.md))
1. Lấy 1 vòng lặp nóng thật. Ghi IL (ILSpy) → đánh dấu mọi `box`, `callvirt`, `ldelema`, `newobj`.
2. Chạy cùng benchmark trên: Editor Mono, player Mono, player IL2CPP (`kit unity test --windowed`). 3 số, 1 bảng. Giải thích chênh lệch bằng IL/asm, không bằng phỏng đoán.
3. Ghi vào `log.md`: "IL cho thấy… / số đo… / giả thuyết sai ở…".

## 7. Đọc thêm
ECMA-335 (Partition I & III); dotnet/runtime `docs/design/coreclr/jit/` (ryujit-overview.md); "Performance Improvements in .NET N" của Stephen Toub (mỗi năm — nguồn tốt nhất về JIT thực tế); `docs/design/features/OnStackReplacement.md`.
