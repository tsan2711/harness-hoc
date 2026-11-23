# Engine core — lộ trình cho principal (thay thế hướng "kỹ năng thời AI" ở mảng engine)

Bắt đầu 2026-11-23. Đối tượng: đã senior→principal, không cần giải thích "cache là gì". Mỗi bài: **mô hình cơ chế → bằng chứng đọc được (IL / asm / LLVM IR / profiler) → điểm gãy → quyết định kiến trúc → thí nghiệm có số đo**.
Quy ước nguồn: `[official]` = docs/staff Unity; `[forum]` = trả lời diễn đàn, chưa xác thực vai trò; `[?]` = suy luận/chưa kiểm — **đừng dựa vào**. Ngày tra: 2026-11-23, Unity đang đổi nhanh, kiểm lại trước khi quyết định.

## Trục 1 — Từ C# đến máy (runtime stack)
| # | Bài | Trạng thái |
|---|---|---|
| 1 | [IL, metadata và RyuJIT: từ C# tới asm](01-il-va-jit.md) | viết |
| 2 | [Mono vs IL2CPP vs CoreCLR trong Unity (6.7 → 7.0)](02-mono-il2cpp-coreclr.md) | viết |
| 3 | [Burst + LLVM: đọc IR, aliasing, vectorization](03-burst-llvm.md) | viết |
| 4 | [GC & bộ nhớ managed/native: Boehm vs generational compacting, pinning, interop, ALC reload](04-gc-bo-nho-managed-native.md) | viết |
| 5 | NativeAOT / ILC / trimming — vì sao nó là họ hàng của IL2CPP, không phải của Mono | chưa |

## Trục 2 — DOTS/ECS ở mức cơ chế
| # | Bài | |
|---|---|---|
| 6 | Archetype, chunk 16 KB, `EntityStorageInfo`, structural change & sync point | chưa |
| 7 | Job scheduler: work stealing, `JobHandle` dependency, safety system (atomic safety handle), false sharing | chưa |
| 8 | Baking, subscene, streaming; ECB playback; system ordering | chưa |
| 9 | Hợp nhất engine & ECS: `EntityId` (6.4+), Entities thành core package, serialization hiện đại hóa | chưa |

## Trục 3 — Engine bên trong
| # | Bài | |
|---|---|---|
| 10 | Render thread, SRP batcher, GPU-driven rendering, BRG | chưa |
| 11 | Asset pipeline, import, serialization, addressables/content | chưa |
| 12 | Nền tảng: Windows/Mac/iOS (JIT cấm trên iOS, W^X, ARM64 vs x64, 16 KB page) + tổng kết đo xuyên stack | chưa |

Mỗi bài kết bằng 1 thí nghiệm trong Thousandfold/Seriously, ghi số vào `log.md`.
