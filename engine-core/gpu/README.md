# Track GPU & rendering — từ nền tới nâng cao
Khuôn: **đố trước (đoán rồi mới đọc) → số đo → cơ chế → chẩn đoán trong game → quy tắc quyết định → bài tập**. Lab: [`../lab/gpu/main.swift`](../lab/gpu/main.swift) (Metal thuần trên M2 — GPU tile-based, **cùng họ** với GPU mobile nhưng không phải Mali/Adreno; kiểm lại trên máy đích).

| # | Bài | Tầng | Trạng thái |
|---|---|---|---|
| G1 | [Frame, bound và giá của một draw call](g1-frame-va-draw-call.md) | nền | viết |
| G2 | [Raster, overdraw, early-Z và HSR](g2-raster-overdraw.md) | nền | viết |
| G3 | [Tile-based GPU: load/store, bandwidth, render pass](g3-tbdr-bandwidth.md) | nền→giữa | viết |
| G4 | [Shader chạy thế nào: SIMD-group, divergence](g4-shader-simd.md) | giữa | viết |
| G5 | [Compute: locality, atomic, threadgroup memory](g5-compute-bo-nho.md) | giữa | viết |
| G6 | Pipeline state, shader variant, PSO stutter trên Android (ưu tiên viết kế) | giữa | chưa |
| G7 | Texture: mip, cache, ASTC/BC, bandwidth sampling (cần lab) | giữa | chưa |
| G8 | Mobile cụ thể: Adreno LRZ, Mali FPK, Vulkan subpass; URP RenderGraph khi nào **không** merge | giữa→cao | chưa |
| G9 | Unity: SRP Batcher, BRG, GPU Resident Drawer | cao | chưa |
| G10 | Lighting: forward+, deferred trên tile GPU, shadow | cao | chưa |
| G11 | GPU-driven: indirect, culling Hi-Z, meshlet, visibility buffer | cao | chưa |
| G12 | Temporal (TAA, upscaling), GI, ray tracing | nâng cao nhất | chưa |

**Giới hạn chung của G1–G5:** mọi số đo từ Metal trên M2, chưa kiểm trên máy Android.
