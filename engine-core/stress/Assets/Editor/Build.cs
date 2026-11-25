using System.IO;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

/// Dựng toàn bộ project từ code: URP asset, scene rỗng, player settings, rồi build.
public static class Build
{
    const string Scene = "Assets/Generated/Bench.unity";

    static void Setup()
    {
        Directory.CreateDirectory("Assets/Generated/Resources");
        var rd = ScriptableObject.CreateInstance<UniversalRendererData>();
        AssetDatabase.CreateAsset(rd, "Assets/Generated/Resources/Renderer.asset");
        ResourceReloader.ReloadAllNullIn(rd, UniversalRenderPipelineAsset.packagePath);
        var urp = UniversalRenderPipelineAsset.Create(rd);
        urp.supportsHDR = false;
        urp.msaaSampleCount = 1;
        AssetDatabase.CreateAsset(urp, "Assets/Generated/URP.asset");
        GraphicsSettings.defaultRenderPipeline = urp;
        for (int i = 0; i < QualitySettings.names.Length; i++) { QualitySettings.SetQualityLevel(i); QualitySettings.renderPipeline = urp; }
        PlayerSettings.enableFrameTimingStats = true;
        PlayerSettings.macRetinaSupport = false;
        PlayerSettings.runInBackground = true;
        var s = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene);
        EditorSceneManager.SaveScene(s, Scene);
        AssetDatabase.SaveAssets();
    }

    static void Run(BuildTarget target, string path)
    {
        Setup();
        var r = BuildPipeline.BuildPlayer(new[] { Scene }, path, target, BuildOptions.None);
        if (r.summary.result != BuildResult.Succeeded) EditorApplication.Exit(1);
    }

    public static void Mac() => Run(BuildTarget.StandaloneOSX, "Build/stress.app");
}
