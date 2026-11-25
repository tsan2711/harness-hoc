# Bài 4 — GC và ranh giới managed/native: Boehm vs generational compacting, pinning, interop, ALC

> Bài 2 nói **ai** chạy code của bạn; bài này nói **bộ nhớ của bạn sống ở đâu, ai thu hồi, giá của mỗi thao tác qua ranh giới**. Đây là chỗ Editor (CoreCLR ở 7.0) và player IL2CPP (Boehm `[forum]`) sẽ lệch nhau nhiều nhất.
> Chú thích nguồn: `[official]` docs Unity/Microsoft; `[forum]` trả lời diễn đàn; `[?]` suy luận — kiểm bằng thí nghiệm mục 8.

## 1. Mô hình chi phí: GC trả tiền cho cái gì
| | Boehm (Mono, IL2CPP) | CoreCLR GC |
|---|---|---|
| Phát hiện root | stack/register quét **bảo thủ**; object trên heap thường có GC descriptor nên quét theo kiểu, mảng không chứa tham chiếu không bị quét | **chính xác**: JIT sinh GC info/safepoint, biết chính xác slot nào là tham chiếu |
| Di chuyển object | không | có (compact, hoặc plan "sweep" nếu phân mảnh nhẹ) |
| Thế hệ | không (full mark mỗi lần; có chế độ incremental của Unity) | gen0/1/2 + LOH (≥ 85.000 byte) + POH |
| Cấp phát | free-list theo size class | **bump pointer** trong allocation context ~8 KB/thread |
| Chi phí 1 lần thu | ∝ **toàn bộ heap sống** (mark) | gen0: ∝ **sống sót + root từ card table**, không ∝ heap |
| Write barrier | có khi incremental | có luôn: card marking khi ghi tham chiếu gen cao → gen thấp |
**Dừng 30 giây**: heap 500 MB gần như toàn dữ liệu sống (level, asset managed, cache), mỗi frame sinh 2 MB rác ngắn hạn. Trước khi đọc tiếp, tự dự đoán pause theo từng collector và vì sao CoreCLR **cũng** có thể có một frame 50 ms sau vài phút.

Đáp án: Boehm mỗi lần thu phải mark ~500 MB (incremental chỉ chia nhỏ công việc qua các frame, tổng công vẫn ∝ heap sống, thêm chi phí barrier). CoreCLR gen0 chỉ đụng 2 MB + sống sót; nhưng object sống lâu bị promote gen1→gen2, gen2 chỉ thu khi budget gen2 vượt → một lần **gen2 blocking** (hoặc background gen2 cạnh tranh CPU) vẫn là spike. Generational không xoá spike, nó **hiếm hoá** và đẩy sang concurrent.

## 2. CoreCLR GC — cơ chế cần thuộc
- **Allocation context**: mỗi thread có đoạn bump-allocate; `new` thường = tăng con trỏ + kiểm giới hạn (vài ns). Hết đoạn → vào GC allocator, có thể kích hoạt GC.
- **Gen0 budget** tính theo cỡ L3 cache (cấu hình `GCgen0size`/`GCgen0MaxBudget`); budget lớn = ít GC hơn nhưng mỗi lần cache nguội hơn.
- **Card table + write barrier**: `obj.field = young` tính ra card → khi gen0 GC quét thêm các card bẩn như root. Hệ quả cho game: **ghi tham chiếu vào heap tốn barrier**; struct có tham chiếu copy bằng *bulk barrier*; **struct blittable không barrier**, đây là một lý do thứ hai (ngoài cache) ECS/NativeContainer rẻ.
- **Regions** (mặc định 64-bit từ .NET 7): heap chia vùng nhỏ, thay vì một dải gen liên tục → giảm phân mảnh, trả bộ nhớ về OS linh hoạt hơn.
- **Concurrent/Background GC** chỉ cho gen2; gen0/1 vẫn stop-the-world (nhưng ngắn). `GCSettings.LatencyMode = SustainedLowLatency`, `GC.TryStartNoGCRegion(bytes)` cho đoạn nhạy cảm (nạp màn, boss fight) — chỉ khi **biết chắc** tổng alloc trong đoạn.
- **LOH/POH**: mảng ≥ 85 KB vào LOH, thu cùng gen2, ít bị compact → phân mảnh theo thời gian. **POH** (`GC.AllocateArray<T>(n, pinned: true)`) cho buffer cần địa chỉ cố định mà không làm bẩn gen0.
- Đo: `GC.GetGCMemoryInfo()` (pause durations, fragmentation, gen sizes), `GC.CollectionCount(g)`, `GC.GetAllocatedBytesForCurrentThread()`, `GC.GetTotalAllocatedBytes(false)`. Công cụ EventPipe (`dotnet-counters/-trace`) có chạy với CoreCLR của Unity hay không là `[?]` — thử trước khi lên kế hoạch.

## 3. Boehm trong Unity — hệ quả thực hành
- **Bảo thủ ⇒ giữ nhầm**: một số nguyên/giá trị rác trên stack có thể trùng địa chỉ heap, giữ cả đồ thị object sống. Hiếm nhưng khó tái hiện; triệu chứng: bộ nhớ managed không về dù không còn tham chiếu.
- **Không di chuyển** ⇒ pointer managed ổn định "ngầm", nhưng đừng dựa vào điều đó: code bạn viết chạy cả CoreCLR (di chuyển). Luôn pin tường minh.
- **Heap phân mảnh & không co lại nhanh** `[?]`: kiểm bằng cách mô phỏng cấp phát rồi giải phóng xen kẽ, so reserved với used (API `Profiler.GetTotalReservedMemoryLong`).
- **Incremental GC** (Player Settings) chia mark qua nhiều frame; đổi lấy barrier + tổng thời gian dài hơn. Dùng khi spike là vấn đề, không khi throughput là vấn đề. Cũng cần **tắt** hoặc điều khiển thủ công `GarbageCollector.GCMode` quanh đoạn nhạy cảm.
- IL2CPP vẫn Boehm cho tương lai gần `[forum]` ⇒ mọi chiến lược "gen0 rẻ nên alloc thoải mái" **sai trên iOS/console**. Chuẩn thiết kế: **zero-alloc trong hot path**, bất kể Editor.

## 4. Ba tầng bộ nhớ trong một game Unity
1. **Managed heap** (GC): object C#, string, delegate, mảng managed.
2. **Native do bạn cấp phát** (không GC): `NativeArray/NativeList/UnsafeList…` với allocator `Temp` (≤ 1 frame/trong job, bump), `TempJob` (≈ ≤ 4 frame), `Persistent` (malloc, bạn `Dispose`), và `RewindableAllocator` (arena thủ công, kiểm tra tên/ API trong Collections của bản đang dùng). Burst và job chỉ chạm tầng này.
3. **Native của engine** (texture, mesh, GameObject native, physics): C# chỉ giữ **wrapper** (`UnityEngine.Object` có con trỏ native `m_CachedPtr`). Hai vòng đời khác nhau: wrapper chết bởi GC, đối tượng native chết bởi `Destroy`/unload. `obj == null` bị overload để phản ánh "native đã chết" (fake null): tốn hơn so sánh tham chiếu thuần (chi phí chính xác tuỳ phiên bản — đo trước khi tối ưu) và **không hoạt động với `?.`/`is null`**. Từ 6.4 `InstanceID` → **`EntityId`** `[official]` (6.5: obsolete error; 8 byte, chuẩn bị cho định danh chung UnityObject + Entity `[forum/staff]`) — không cast int, không dùng dấu, không dùng làm thứ tự tạo.
**Quy tắc kiến trúc**: mỗi dữ liệu phải thuộc đúng một tầng theo *vòng đời*, không theo thói quen. Dữ liệu nóng, số lượng lớn, tạo/huỷ theo frame → tầng 2 (hoặc ECS chunk). Dữ liệu cấu hình/ít → tầng 1. Đừng để tầng 2 giữ lại tham chiếu tầng 1.

## 5. Pinning và interop
- `fixed`/`GCHandle.Alloc(.., Pinned)`/POH: pin trong gen0 **làm kẹt compaction** (gen0 phải "né" object bị pin → phân mảnh). Pin ngắn (trong `fixed`) rẻ; pin dài trong gen0 độc hại; pin dài thì cấp phát ở POH ngay từ đầu.
- `UnsafeUtility.PinGCArrayAndGetDataAddress` và bạn bè: nhớ giải phóng handle; leak handle = leak object + chặn ALC unload (mục 6).
- **P/Invoke marshalling**: blittable (int/float/struct tuần tự không tham chiếu) gần như miễn phí; string/bool/mảng non-blittable ⇒ copy/convert. **Hai thứ khác nhau:** `FunctionPointer<T>` của Burst trỏ tới code native, không có delegate cần giữ; còn `Marshal.GetFunctionPointerForDelegate` (reverse P/Invoke) thì **phải** giữ delegate sống, nếu không native gọi vào delegate đã bị thu → crash (IL2CPP: callback static + `[MonoPInvokeCallback]`).
- **Callback native→managed** trên thread khác: cần attach thread vào runtime; GC phải suspend thread đó ở safepoint — thread native dài hạn không "cooperate" có thể kéo dài pause.

## 6. ALC reload và rò rỉ (liên hệ bài 2)
Collectible `AssemblyLoadContext` chỉ unload khi **không còn tham chiếu mạnh tới bất kỳ type/assembly/instance nào bên trong** `[official: .NET unloadability doc]`. Kẻ giữ phổ biến trong Unity: `static` field, event handler đăng ký vào object ngoài ALC, `GCHandle` (kể cả của native callback), thread/timer còn chạy, `ThreadLocal`, `ThreadStatic`, native plugin giữ function pointer vào code bị unload, `UnityEvent` persistent. Pattern đã dùng cho "Enter Play Mode không domain reload" — reset static trong `[RuntimeInitializeOnLoadMethod(SubsystemRegistration)]` — **vẫn cần**; thêm: viết test "reload N lần, đo số ALC/assembly còn sống và managed heap".

## 7. Memory model và kiến trúc CPU (liên quan iOS/Apple Silicon)
x86-64 là **TSO** (store-store, load-load giữ thứ tự); ARM64 là **weak** (cho phép đảo thứ tự nhiều hơn). Code lock-free "chạy trên PC" có thể sai trên iPhone/Mac M-series. .NET đảm bảo `volatile`/`Interlocked`/`Volatile.Read/Write` có acquire/release đúng; C# **không tự bảo vệ** ghi thường. Trong job/Burst: dùng `Interlocked`, `Volatile`, hoặc kiến trúc không chia sẻ (mỗi worker ghi vào slice riêng + merge) — bài 7 sẽ đi tiếp. Tránh `double-checked locking` tự chế.

## 8. Thí nghiệm (đo thật, ghi `log.md`)
**A. Live-heap vs rác/frame.** Dựng scene: giữ sống `L ∈ {50, 200, 800 MB}` object managed (mảng class có tham chiếu, không phải `byte[]` — vì byte[] không phải con trỏ để mark), mỗi frame cấp phát `G ∈ {0, 1 KB, 100 KB, 2 MB}`. Chạy windowed trên Mono player, IL2CPP player, CoreCLR desktop player (6.7, experimental). Ghi p50/p99/max frame, số GC mỗi gen (CoreCLR), thời gian GC đo bằng đồng hồ quanh `GC.Collect`. Kỳ vọng kiểm: Boehm p99 tăng theo L; CoreCLR p99 gần như phẳng theo L nhưng có spike hiếm.
**B. Pin độc.** Pin 10k object nhỏ sống lâu trong gen0 + alloc tải đều → đo phân mảnh (`GCMemoryInfo.FragmentedBytes`). So với cấp POH.
**C. ALC leak.** Plugin giữ 1 static event; reload 20 lần ở Unity 7.0 alpha; đo tăng bộ nhớ và số assembly. Sửa, đo lại.
**D. Barrier.** Hai vòng lặp 1M phần tử: struct có field `object` vs struct blittable; đo ghi.
Kết quả mỗi thí nghiệm: 1 bảng + 1 câu "cơ chế giải thích" — nếu không giải thích được bằng mục 1–5 thì ghi là **chưa hiểu**, đừng đoán.

## 9. Đọc thêm
dotnet/runtime `docs/design/coreclr/botr/garbage-collection.md`; Konrad Kokosa "Pro .NET Memory Management" (nặng nhưng là chuẩn); Maoni Stephens blog (kiến trúc sư GC); Boehm–Weiser "Garbage Collection in an Uncooperative Environment"; docs Unity "Incremental garbage collection".
