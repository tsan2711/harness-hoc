# 3. Mổ source (URP 17.5.0, đường dẫn trong `PackageCache/com.unity.render-pipelines.universal@…/Runtime/`)

## 3.1 URP bỏ sort gần→xa trên GPU có HSR
`UniversalRenderPipeline.cs`, khoảng dòng 1675–1680:

```csharp
var commonOpaqueFlags = SortingCriteria.CommonOpaque;
var noFrontToBackOpaqueFlags = SortingCriteria.SortingLayer | SortingCriteria.RenderQueue | SortingCriteria.OptimizeStateChanges | SortingCriteria.CanvasOrder;
bool hasHSRGPU = SystemInfo.hasHiddenSurfaceRemovalOnGPU;
bool canSkipFrontToBackSorting = (baseCamera.opaqueSortMode == OpaqueSortMode.Default && hasHSRGPU) || baseCamera.opaqueSortMode == OpaqueSortMode.NoDistanceSort;
cameraData.defaultOpaqueSortFlags = canSkipFrontToBackSorting ? noFrontToBackOpaqueFlags : commonOpaqueFlags;
```
- Dòng 2: bộ cờ này giống sort opaque thường **trừ** phần khoảng cách (`QuantizedFrontToBack`).
- Dòng 4: `opaqueSortMode == Default` + GPU có HSR ⇒ bỏ sort khoảng cách. Lý do hợp lý cho opaque: HSR làm việc đó rồi, sort chỉ tốn CPU.
- Hệ quả: alpha test (queue 2450) nằm trong dải opaque nên cũng **không được sort gần→xa**, trong khi chính nó là thứ HSR không giúp được.

## 3.2 Pass vẽ chọn cờ
`Passes/DrawObjectsPass.cs`, khoảng dòng 185–187:

```csharp
var sortFlags = (m_IsOpaque) ? cameraData.defaultOpaqueSortFlags : SortingCriteria.CommonTransparent;
if (cameraData.renderer.useDepthPriming && m_IsOpaque && (cameraData.renderType == CameraRenderType.Base || cameraData.clearDepth))
    sortFlags = SortingCriteria.SortingLayer | SortingCriteria.RenderQueue | SortingCriteria.OptimizeStateChanges | SortingCriteria.CanvasOrder;
```
- Transparent luôn đi đường riêng (xa→gần).
- Bật depth priming thì sort khoảng cách cũng bị bỏ: depth đã dựng sẵn, thứ tự không còn quan trọng cho việc loại.

## 3.3 Điều kiện bật depth priming
`UniversalRendererRenderGraph.cs`, `IsDepthPrimingEnabledRenderGraph`:

```csharp
#if UNITY_ANDROID || UNITY_IOS || UNITY_TVOS || UNITY_EMBEDDED_LINUX
            bool depthPrimingRecommended = false;
#else
            bool depthPrimingRecommended = true;
#endif
```
`Auto` chỉ bật khi "recommended"; nền tảng khác phải đặt `Forced`. Cả hai còn cần: không MSAA, không deferred, không WebGL, camera đầu tiên ghi depth.

## 3.4 Vì sao priming cứu được cutout
`Passes/DrawObjectsPass.cs`, ngay sau khi tạo `drawSettings` (khoảng dòng 200–204):

```csharp
if (zWriteOff)
{
    m_RenderStateBlock.depthState = new DepthState(false, CompareFunction.Equal);
    m_RenderStateBlock.mask |= RenderStateMask.Depth;
}
```
- `DepthState(false, …)`: pass màu **không ghi depth**. Depth đã được prepass dựng xong.
- `CompareFunction.Equal`: chỉ fragment đúng bằng depth đã dựng mới qua.
- `mask |= Depth`: đè trạng thái depth khai báo trong shader.

Pass màu không còn phải chờ shader chạy xong mới biết depth cuối, nên test sớm loại được các lớp bị che dù shader có `clip`. Đây là cơ chế chính; mục 3.1–3.2 chỉ nói về sort.

## 3.5 Shader của project mô phỏng
```hlsl
float cov = Coverage(i.uv);      // alpha rẻ, tách khỏi phần đắt
clip(cov - _Cutoff);             // chỉ khi _CUTOUT
for (int k = 0; k < n; k++) a = frac(a * 1.37 + i.uv.y);   // phần đắt
```
Pass `DepthOnly` lặp lại đúng `clip` đó nhưng **không có vòng lặp**. Đó là toàn bộ lý do priming có lãi: prepass rẻ quyết định ai thắng, pass màu chỉ shade người thắng. Nếu `Coverage` đắt ngang phần tô màu, priming mất lãi.
