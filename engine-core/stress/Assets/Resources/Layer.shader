Shader "Stress/Layer"
{
    Properties { _Color("Color", Color)=(1,1,1,1) _Cutoff("Cutoff", Float)=-1 _Iter("Iter", Float)=64 _Radial("Radial", Float)=0
                 _SrcBlend("Src", Float)=1 _DstBlend("Dst", Float)=0 _ZWrite("ZWrite", Float)=1 _ZTest("ZTest", Float)=4 }
    SubShader
    {
        Tags { "RenderPipeline"="UniversalPipeline" }
        HLSLINCLUDE
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
        CBUFFER_START(UnityPerMaterial)
        float4 _Color; float _Cutoff; float _Iter; float _Radial; float _SrcBlend; float _DstBlend; float _ZWrite;
        CBUFFER_END
        struct A { float4 pos : POSITION; float2 uv : TEXCOORD0; };
        struct V { float4 pos : SV_POSITION; float2 uv : TEXCOORD0; };
        V vert(A i) { V o; o.pos = TransformObjectToHClip(i.pos.xyz); o.uv = i.uv; return o; }
        // alpha rẻ (đứng thay cho 1 lần đọc texture), tách khỏi phần tô màu đắt
        float Coverage(float2 uv) { return _Radial > 0.5 ? saturate(1 - length(uv * 2 - 1)) : 1; }
        ENDHLSL

        Pass
        {
            Tags { "LightMode"="UniversalForward" }
            Blend [_SrcBlend] [_DstBlend]  ZWrite [_ZWrite]  ZTest [_ZTest]  Cull Off
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma multi_compile_local_fragment _ _CUTOUT
            #pragma multi_compile_local_fragment _ _DERIV
            half4 frag(V i) : SV_Target
            {
                float cov = Coverage(i.uv);
            #ifdef _CUTOUT
                clip(cov - _Cutoff);
            #endif
                float a = i.uv.x;
                int n = (int)_Iter;
                for (int k = 0; k < n; k++) a = frac(a * 1.37 + i.uv.y);
                float3 rgb = _Color.rgb * (0.9 + 0.1 * a);
            #ifdef _DERIV
                // đạo hàm của KẾT QUẢ vòng lặp: GPU buộc phải chạy cả vòng lặp trên helper lane của quad 2x2
                rgb += fwidth(a) * 1e-6;
                rgb.b += 0.3;   // dấu nhìn thấy được trong ảnh: variant _DERIV đã chạy thật
            #endif
                return half4(rgb, _Color.a * cov);
            }
            ENDHLSL
        }
        Pass
        {
            Tags { "LightMode"="DepthOnly" }
            ZWrite On  ColorMask R  Cull Off
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma multi_compile_local_fragment _ _CUTOUT
            half4 frag(V i) : SV_Target
            {
            #ifdef _CUTOUT
                clip(Coverage(i.uv) - _Cutoff);
            #endif
                return 0;
            }
            ENDHLSL
        }
    }
}
