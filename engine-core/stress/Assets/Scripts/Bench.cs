using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Text;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

/// Chạy lần lượt các cấu hình, đo GPU/CPU frame time bằng FrameTimingManager, chụp ảnh, ghi CSV rồi thoát.
/// Tham số: -out <thư mục> -only <tiền tố tên cấu hình>
public sealed class Bench : MonoBehaviour
{
    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    static void Boot() => new GameObject("bench").AddComponent<Bench>();

    const int Warm = 40, Samples = 120, Rounds = 3;
    enum Kind { Opaque, Cutout, Additive }

    class Cfg { public string name; public Action build; public float scale = 1; public DepthPrimingMode priming = DepthPrimingMode.Disabled; public OpaqueSortMode sort = OpaqueSortMode.Default;
                public readonly List<double> gpu = new(), cpu = new(), wall = new(); }

    readonly List<GameObject> spawned = new();
    Camera cam; Shader shader; Mesh quad, octagon;
    float H, W;

    // Đầu dò thứ tự vẽ: tắt depth test, mỗi lớp một màu nhị phân -> màu ở giữa màn là lớp được vẽ SAU CÙNG
    IEnumerator Probe(string outDir)
    {
        var sb = new StringBuilder("# 8 lớp, 0 = gần camera nhất, 7 = xa nhất\nkind,mode,dz,last_drawn_layer\n");
        var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
        urp.renderScale = 1;
        ((UniversalRendererData)urp.rendererDataList[0]).depthPrimingMode = DepthPrimingMode.Disabled;
        foreach (var kind in new[] { Kind.Opaque, Kind.Cutout })
            foreach (var (mode, sort, b2f) in new[] { ("auto", OpaqueSortMode.Default, false), ("b2f", OpaqueSortMode.Default, true), ("f2bsort", OpaqueSortMode.FrontToBack, false) })
                foreach (float dz in new[] { 0.1f, 2f, 20f, 100f })
                {
                    cam.opaqueSortMode = sort;
                    Layers(kind, 8, b2f, dz, probe: true);
                    for (int i = 0; i < 5; i++) yield return null;
                    yield return new WaitForEndOfFrame();
                    var tex = ScreenCapture.CaptureScreenshotAsTexture();
                    var p = tex.GetPixel(tex.width / 2, tex.height / 2);
                    int idx = (p.r > .5f ? 1 : 0) + (p.g > .5f ? 2 : 0) + (p.b > .5f ? 4 : 0);
                    sb.Append($"{kind},{mode},{dz.ToString(System.Globalization.CultureInfo.InvariantCulture)},{idx}\n");
                    Destroy(tex);
                    Clear();
                }
        File.WriteAllText(Path.Combine(outDir, "probe.csv"), sb.ToString());
    }

    IEnumerator Start()
    {
        string outDir = Arg("-out") ?? Application.persistentDataPath;
        string only = Arg("-only") ?? "";
        Directory.CreateDirectory(outDir);
        QualitySettings.vSyncCount = 0; Application.targetFrameRate = -1;

        cam = new GameObject("cam").AddComponent<Camera>();
        cam.orthographic = true; cam.orthographicSize = 5; cam.transform.position = new Vector3(0, 0, -10);
        cam.clearFlags = CameraClearFlags.SolidColor; cam.backgroundColor = Color.black;
        H = 10; W = H * Screen.width / Screen.height;
        shader = Resources.Load<Shader>("Layer");
        quad = Poly(4, Mathf.PI / 4, Mathf.Sqrt(2));                               // hình vuông cạnh 2
        octagon = Poly(8, Mathf.PI / 8, 1f / Mathf.Cos(Mathf.PI / 8));             // bát giác ngoại tiếp đường tròn bán kính 1

        var all = Configs().FindAll(c => c.name.StartsWith(only));
        if (only == "" || only == "probe") yield return Probe(outDir);
        // xen kẽ nhiều vòng: trôi nhiệt / tải nền chia đều cho mọi cấu hình
        for (int round = 0; round < Rounds; round++)
            foreach (var c in all)
            {
                Apply(c);
                for (int i = 0; i < Warm; i++) yield return null;
                var ft = new FrameTiming[1];
                for (int i = 0; i < Samples; i++)
                {
                    yield return null;
                    c.wall.Add(Time.unscaledDeltaTime * 1000.0);   // đồng hồ tường, đối chiếu khi FrameTimingManager im lặng
                    FrameTimingManager.CaptureFrameTimings();
                    if (FrameTimingManager.GetLatestTimings(1, ft) == 1 && ft[0].gpuFrameTime > 0) { c.gpu.Add(ft[0].gpuFrameTime); c.cpu.Add(ft[0].cpuMainThreadFrameTime); }
                }
                if (round == 0) { ScreenCapture.CaptureScreenshot(Path.Combine(outDir, c.name + ".png")); yield return null; }
                Clear();
            }

        var sb = new StringBuilder($"# {SystemInfo.graphicsDeviceName} | {SystemInfo.graphicsDeviceType} | {Screen.width}x{Screen.height} | Unity {Application.unityVersion} | hasHSR={SystemInfo.hasHiddenSurfaceRemovalOnGPU}\n");
        sb.Append("config,samples,gpu_ms_p25,gpu_ms_median,gpu_ms_p75,cpu_main_ms_median,wall_ms_median\n");
        foreach (var c in all)
            sb.Append($"{c.name},{c.gpu.Count},{Pct(c.gpu, .25):F3},{Pct(c.gpu, .5):F3},{Pct(c.gpu, .75):F3},{Pct(c.cpu, .5):F3},{Pct(c.wall, .5):F3}\n");
        File.WriteAllText(Path.Combine(outDir, "bench.csv"), sb.ToString().Replace(";", ","));
        Application.Quit();
    }

    List<Cfg> Configs()
    {
        var list = new List<Cfg>();
        void Add(string n, Action b, float scale = 1, DepthPrimingMode p = DepthPrimingMode.Disabled) => list.Add(new Cfg { name = n, build = b, scale = scale, priming = p });

        // I1: lớp che nhau. auto = để URP sort; b2f = ép xa->gần bằng renderQueue
        foreach (Kind k in Enum.GetValues(typeof(Kind)))
            foreach (int n in new[] { 1, 4, 16 })
            {
                var kind = k; int count = n;
                Add($"layers-{k}-{n}-auto", () => Layers(kind, count, false));
                if (n > 1 && k != Kind.Additive) Add($"layers-{k}-{n}-b2f", () => Layers(kind, count, true));
            }
        // I1b: ép URP sort gần->xa (mặc định nó bỏ sort này khi GPU có HSR)
        foreach (Kind k in new[] { Kind.Opaque, Kind.Cutout })
        {
            var kind = k;
            foreach (float dz in new[] { 0.1f, 20f })
            {
                float d = dz; string tag = dz < 1 ? "near" : "far";
                Add($"layers-{k}-16-f2bsort-{tag}", () => Layers(kind, 16, false, d));
                list[list.Count - 1].sort = OpaqueSortMode.FrontToBack;
                Add($"layers-{k}-16-auto-{tag}", () => Layers(kind, 16, false, d));
            }
        }
        // I1c: quét số lớp phải shade hết -> đọc độ dốc, không đọc một điểm
        foreach (int n in new[] { 1, 2, 4, 8, 16, 32 }) { int count = n; Add($"sweep-additive-{n}", () => Layers(Kind.Additive, count, false)); }
        Add("empty", () => { });
        foreach (int cell in new[] { 64, 8, 4, 2 })
        {
            int c = cell;
            Add($"deriv-grid-{cell}px-iter256", () => { Grid(c, 256); spawned[0].GetComponent<MeshRenderer>().sharedMaterial.EnableKeyword("_DERIV"); });
        }
        foreach (int cell in new[] { 64, 2 })
        {
            int c = cell;
            Add($"big-grid-{cell}px-iter512", () => Grid(c, 512));
            Add($"big-deriv-grid-{cell}px-iter512", () => { Grid(c, 512); spawned[0].GetComponent<MeshRenderer>().sharedMaterial.EnableKeyword("_DERIV"); });
        }
        // I2: depth priming có cứu được cutout không
        Add("priming-Opaque-16-b2f", () => Layers(Kind.Opaque, 16, true), 1, DepthPrimingMode.Forced);
        Add("priming-Cutout-16-b2f", () => Layers(Kind.Cutout, 16, true), 1, DepthPrimingMode.Forced);
        Add("priming-Cutout-16-auto", () => Layers(Kind.Cutout, 16, false), 1, DepthPrimingMode.Forced);
        Add("priming-Cutout-1-auto", () => Layers(Kind.Cutout, 1, false), 1, DepthPrimingMode.Forced);
        // I3: glow additive. Quad vs bát giác, và render scale để kiểm "có phải nghẽn fill không"
        foreach (int n in new[] { 100, 400 })
            foreach (float s in new[] { 1f, 0.5f })
            {
                int count = n;
                Add($"glow-quad-{n}-s{s * 100:F0}", () => Glows(count, quad), s);
                Add($"glow-oct-{n}-s{s * 100:F0}", () => Glows(count, octagon), s);
            }
        Add("glowheavy-quad-100", () => Glows(100, quad, 128));
        Add("glowheavy-oct-100", () => Glows(100, octagon, 128));
        // I4: tam giác nhỏ. Cùng diện tích phủ, đổi cỡ ô; iter 0 để tách phần hình học khỏi phần fragment
        foreach (int cell in new[] { 64, 16, 8, 4, 2 })
            foreach (int iter in new[] { 0, 64, 256 })
            {
                int c = cell, it = iter;
                Add($"grid-{cell}px-iter{iter}", () => Grid(c, it));
            }
        return list;
    }

    void Apply(Cfg c)
    {
        var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
        urp.renderScale = c.scale;
        cam.opaqueSortMode = c.sort;
        var data = (UniversalRendererData)urp.rendererDataList[0];
        data.depthPrimingMode = c.priming;
        c.build();
    }

    Material Mat(Kind k, int iter, Color col, bool radial = false)
    {
        var m = new Material(shader);
        m.SetColor("_Color", col); m.SetFloat("_Iter", iter); m.SetFloat("_Radial", radial ? 1 : 0);
        m.SetFloat("_Cutoff", -1);   // không bao giờ discard thật: hình giống hệt opaque
        if (k == Kind.Cutout) { m.EnableKeyword("_CUTOUT"); m.renderQueue = 2450; }
        else if (k == Kind.Additive)
        {
            m.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha); m.SetFloat("_DstBlend", (float)BlendMode.One); m.SetFloat("_ZWrite", 0);
            m.renderQueue = 3000;
        }
        else m.renderQueue = 2000;
        return m;
    }

    void Spawn(Mesh mesh, Material mat, Vector3 pos, Vector3 scale)
    {
        var go = new GameObject("q", typeof(MeshFilter), typeof(MeshRenderer));
        go.GetComponent<MeshFilter>().sharedMesh = mesh;
        go.GetComponent<MeshRenderer>().sharedMaterial = mat;
        go.transform.position = pos; go.transform.localScale = scale;
        spawned.Add(go);
    }

    void Layers(Kind k, int n, bool forceBackToFront, float dz = 0.1f, bool probe = false)
    {
        var shared = Mat(k, probe ? 0 : 64, new Color(0.2f, 0.5f, 0.3f, 0.1f));
        if (probe) shared.SetFloat("_ZTest", (float)CompareFunction.Always);
        var order = new int[n]; for (int i = 0; i < n; i++) order[i] = i;
        var rnd = new System.Random(3);
        for (int i = n - 1; i > 0; i--) { int j = rnd.Next(i + 1); (order[i], order[j]) = (order[j], order[i]); }
        foreach (int i in order)                             // i = 0 gần camera nhất
        {
            var m = shared;
            if (forceBackToFront) { m = new Material(shared); m.renderQueue = shared.renderQueue + (n - 1 - i); }
            Spawn(quad, m, new Vector3(0, 0, i * dz), new Vector3(W / 2, H / 2, 1));
            if (probe)
            {
                var pb = new MaterialPropertyBlock();
                pb.SetColor("_Color", new Color(i & 1, (i >> 1) & 1, (i >> 2) & 1, 1));
                spawned[spawned.Count - 1].GetComponent<MeshRenderer>().SetPropertyBlock(pb);
            }
        }
    }

    void Glows(int n, Mesh mesh, int iter = 16)
    {
        var m = Mat(Kind.Additive, iter, new Color(1f, 0.6f, 0.2f, 0.15f), radial: true);
        var rnd = new System.Random(7);
        for (int i = 0; i < n; i++)
        {
            var p = new Vector3((float)(rnd.NextDouble() - .5) * W, (float)(rnd.NextDouble() - .5) * H, (float)rnd.NextDouble());
            Spawn(mesh, m, p, new Vector3(1.2f, 1.2f, 1));   // bán kính 1.2 đơn vị = 86 px ở 720p
        }
    }

    void Grid(int cellPx, int iter)
    {
        int nx = Screen.width / cellPx, ny = Screen.height / cellPx;
        var v = new Vector3[(nx + 1) * (ny + 1)]; var uv = new Vector2[v.Length]; var t = new int[nx * ny * 6];
        for (int y = 0; y <= ny; y++) for (int x = 0; x <= nx; x++)
        {
            int i = y * (nx + 1) + x;
            uv[i] = new Vector2((float)x / nx, (float)y / ny);
            v[i] = new Vector3((uv[i].x - .5f) * W, (uv[i].y - .5f) * H, 0);
        }
        for (int y = 0, k = 0; y < ny; y++) for (int x = 0; x < nx; x++)
        {
            int a = y * (nx + 1) + x, b = a + 1, c = a + nx + 1, d = c + 1;
            t[k++] = a; t[k++] = c; t[k++] = b; t[k++] = b; t[k++] = c; t[k++] = d;
        }
        var mesh = new Mesh { indexFormat = IndexFormat.UInt32 };
        mesh.vertices = v; mesh.uv = uv; mesh.triangles = t;
        Spawn(mesh, Mat(Kind.Opaque, iter, Color.gray), Vector3.zero, Vector3.one);
    }

    static Mesh Poly(int n, float offset, float radius)
    {
        var v = new Vector3[n]; var uv = new Vector2[n]; var t = new int[(n - 2) * 3];
        for (int i = 0; i < n; i++)
        {
            float a = offset + i * Mathf.PI * 2 / n;
            v[i] = new Vector3(Mathf.Cos(a), Mathf.Sin(a)) * radius;
            uv[i] = new Vector2(v[i].x, v[i].y) * 0.5f + Vector2.one * 0.5f;
        }
        for (int i = 0; i < n - 2; i++) { t[i * 3] = 0; t[i * 3 + 1] = i + 2; t[i * 3 + 2] = i + 1; }
        return new Mesh { vertices = v, uv = uv, triangles = t };
    }

    void Clear() { foreach (var g in spawned) DestroyImmediate(g); spawned.Clear(); }

    static double Pct(List<double> l, double p)
    {
        if (l.Count == 0) return -1;
        var a = l.ToArray(); Array.Sort(a); return a[(int)((a.Length - 1) * p)];
    }

    static string Arg(string key)
    {
        var a = Environment.GetCommandLineArgs();
        int i = Array.IndexOf(a, key);
        return i >= 0 && i + 1 < a.Length ? a[i + 1] : null;
    }
}
