# Bài 2 — Mono vs IL2CPP vs CoreCLR trong Unity (6.7 → 7.0)

> Ba "execution engine" khác hẳn về JIT/AOT, GC, interop, giới hạn ngôn ngữ. Quyết định kiến trúc (alloc policy, generics, reflection, hot-reload, code Burst) phụ thuộc vào cái nào chạy **ở player đích**, không phải ở Editor.
> Nguồn ngày 2026-11-23: docs.unity.com (6000.7, 7000.0), Unity Discussions "CoreCLR, Scripting, and .NET Update – October 2026" và "…March 2026". Mọi chỗ có `[forum]`/`[?]` cần kiểm lại.

## 1. Bản đồ hiện trạng
| | Mono | IL2CPP | CoreCLR |
|---|---|---|---|
| Biên dịch | JIT | **AOT**: C# → IL → C++ → native bằng compiler nền tảng | JIT, tiered, RyuJIT |
| GC | Boehm (bảo thủ, không di chuyển, không thế hệ) | **Boehm, "foreseeable future"** `[forum]` | generational, precise, compacting |
| Nền tảng | Win/macOS/Linux/Android armv7 | rộng nhất, **bắt buộc iOS & hầu hết console** | desktop Win/macOS Arm64/Linux (7.0 docs) |
| API level | tới .NET Standard 2.1 | như vậy | `[official]` chỉ .NET Standard API level cho tới nay |
| Ngôn ngữ | C# 9 | C# 9 | alpha: **C# 9**; mục tiêu .NET 10 / C# 14 `[official: "incrementally"]` |
| Hot reload | domain reload (Unity không hỗ trợ edit-and-continue) | — | **ALC reload** thay domain reload |
| Burst | dùng được | dùng được | dùng được (docs: "any backend") |

Trạng thái: 6.7 LTS có **CoreCLR desktop player (experimental)** + IL2CPP iOS (experimental, bản "updated IL2CPP"); Editor 6.7 vẫn Mono. **Unity 7.0 alpha: CoreCLR editor, Mono bị gỡ**; docs 7000.0 chỉ liệt kê CoreCLR + IL2CPP. 7.0 chưa có ngày phát hành công khai ("We cannot commit to a public date yet"). Mục tiêu 7.0 chỉ là **performance parity** — đừng kỳ vọng nhanh hơn ngay. Kế hoạch tháng 3 (CoreCLR editor ở 6.8) đã bị thay bằng 7.0.

## 2. Hai thứ nhìn giống nhau nhưng khác bản chất
**(a) Cùng IL, khác bộ tối ưu** (bài 1): Mono JIT (mini) < RyuJIT tiered+PGO về chất lượng code trung bình; IL2CPP = clang/MSVC trên C++ sinh ra — nghĩa là có thể inline xuyên method, loại bỏ code chết mạnh, nhưng **không** có PGO runtime và không devirtualize theo profile.
**(b) Check an toàn bị chuyển thành code**: IL2CPP phát null-check và array-bounds tường minh trong C++ (divide-by-zero check **mặc định tắt**); có thể tắt theo method/type bằng `[Il2CppSetOption(Option.NullChecks, false)]` (cùng `ArrayBoundsChecks`, `DivideByZeroChecks`) — đổi an toàn lấy tốc độ, chỉ nên ở hot path đã kiểm chứng. CoreCLR dựa vào guard page + bounds-check elimination của JIT.

## 3. GC — chỗ đổi lớn nhất và dễ hiểu lầm nhất
- **Boehm**: quét **bảo thủ** (mọi từ trong stack trông giống con trỏ là root) → có thể giữ rác sống nhầm; **không di chuyển** object → pointer tới managed memory không "vỡ" nhưng **phân mảnh**; stop-the-world, có chế độ incremental của Unity (chia mark). Không có gen0 rẻ → mỗi alloc/frame đều đáng sợ.
- **CoreCLR GC**: precise (JIT báo GC info cho từng safepoint), **generational** (gen0/1/2, LOH/POH), **compacting**, concurrent/background gen2, từ .NET 7 dùng **regions**. Hệ quả: alloc ngắn hạn rẻ hơn rất nhiều, nhưng object **di chuyển** → code native giữ địa chỉ managed phải `pin` (`fixed`, `GCHandle.Pinned`, POH `GC.AllocateArray(pinned:true)`).
- **Cú sốc kiến trúc**: Editor/standalone dùng CoreCLR GC, **IL2CPP vẫn Boehm** `[forum]` → hành vi alloc/pause giữa Editor và player có thể lệch *nhiều hơn* hôm nay chứ không ít hơn. Quy tắc: **zero-alloc trong hot path vẫn bắt buộc**, đừng "tận dụng gen0 rẻ" rồi chỉ đo ở Editor.
- Chưa có: kế hoạch tối ưu GC/JIT sau 7.0 chỉ "under evaluation" `[forum]`.

## 4. Domain reload → AssemblyLoadContext (ALC)
`[official, staff]`: "domain reloads are gone in Unity 7. It's ALC reload instead." (chuỗi giao diện còn ghi "domain reload"). Khác biệt cơ chế: AppDomain không có trong .NET Core; ALC cho phép **unload collectible assembly** nếu không còn tham chiếu sống. Rủi ro tương tự cũ: static field, event handler, thread, `GCHandle`, native callback giữ ALC lại → unload thất bại/leak. Pattern "static state phải reset" (Enter Play Mode không reload domain) **vẫn áp dụng**. Chưa có tăng tốc iteration nhìn thấy được `[official: parity only]`; live code iteration "long term".

## 5. Điểm gãy khi chuyển
| Rủi ro | Vì sao |
|---|---|
| Reflection/`Emit`/dynamic method | IL2CPP không hỗ trợ `Reflection.Emit`; stripping cần `link.xml`/`[Preserve]` |
| Generic instantiation không thấy lúc build | Từ 2022.1 IL2CPP có full generic sharing: không crash nữa nhưng **chậm âm thầm** (tìm `_gshared`/rgctx trong `il2cppOutput`) |
| `GCHandle`/pinning/marshalling native | CoreCLR GC di chuyển; P/Invoke & function pointer khác marshaller |
| Thread/timing/finalizer | finalizer thread, tiered JIT warmup trên frame đầu |
| Intel Mac x64 | không hỗ trợ ở 7.0 alpha `[secondary]` |
| Tool/package dùng `AppDomain`, `Mono.Cecil`, Mono-specific API | gãy với CoreCLR |
| Code kiểm thử/benchmark chỉ ở Editor | Editor ≠ player nữa về cả JIT lẫn GC |

## 6. Quyết định (dành cho dự án mobile/PC của Bi)
1. **iOS/console không có JIT** → IL2CPP là đường duy nhất; mọi tối ưu "dựa PGO/tiered" chỉ có ở desktop CoreCLR. Thiết kế hot path theo mô hình **AOT + Burst**, coi CoreCLR là bonus cho Editor/PC.
2. Hot path nên sống trong Burst/jobs (không phụ thuộc backend). Phần managed còn lại: không alloc, không LINQ, không closure.
3. Giữ `link.xml`/`[Preserve]` và AOT-generic hint có test (build IL2CPP trong CI), vì đây là thứ gãy đầu tiên.
4. Ghi nhớ **hai ngày chưa biết**: ngày 7.0 stable, ngày IL2CPP "updated" cho từng nền tảng. Đừng khóa lộ trình vào chúng.

## 7. Thí nghiệm
1. Cùng 1 scene benchmark (alloc nhỏ mỗi frame + 1 job Burst + 1 vòng lặp managed) chạy trên **Mono player**, **IL2CPP player**, **CoreCLR desktop player (6.7, experimental)**. Ghi: p50/p99 frame, GC.Collect count/pause (`ProfilerRecorder` "GC Reserved/Used Memory", `GC.CollectionCount`), thời gian frame đầu.
2. Dựng lại 1 test reflection + generic: xem cái nào gãy trên IL2CPP khi strip high.
3. `log.md`: backend nào cho số tệ nhất ở đâu, vì cơ chế gì (GC? JIT warmup? bounds-check?).

## 8. Đọc thêm
Unity Discussions threads trên (đọc cả page 2); docs.unity.com → Scripting backends 6000.7 & 7000.0; dotnet/runtime `docs/design/features/unloadability.md`, `docs/design/coreclr/botr/garbage-collection.md`; Unity blog về IL2CPP internals (series cũ — kiến trúc còn đúng, chi tiết cần kiểm).
