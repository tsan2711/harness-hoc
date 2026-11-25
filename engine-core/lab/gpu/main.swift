import Metal
import Foundation
let src = """
#include <metal_stdlib>
using namespace metal;
struct V { float4 p [[position]]; float2 uv; };
vertex V vs(uint vid [[vertex_id]], constant float &z [[buffer(0)]]) {
  float2 q = float2((vid<<1)&2, vid&2); V o; o.p=float4(q*2-1, z, 1); o.uv=q; return o; }
float work(float2 uv){ float a=uv.x; for(int i=0;i<64;i++) a=fract(a*1.37+uv.y); return a; }
fragment float4 fsOpaque(V i [[stage_in]]) { return float4(work(i.uv),0,0,1); }
fragment float4 fsDiscard(V i [[stage_in]]) { float a=work(i.uv); if(a<-1) discard_fragment(); return float4(a,0,0,1); }
[[early_fragment_tests]] fragment float4 fsDiscardEarly(V i [[stage_in]]) { float a=work(i.uv); if(a<-1) discard_fragment(); return float4(a,0,0,1); }
fragment float4 fsBlend(V i [[stage_in]]) { return float4(work(i.uv),0,0,0.5); }
// divergence: mode 0 = cả SIMD-group cùng nhánh, 1 = xen kẽ từng lane
kernel void diverge(device float *o [[buffer(0)]], constant uint &mode [[buffer(1)]], uint id [[thread_position_in_grid]]) {
  uint sel = mode==0 ? (id/1024)&1 : id&1; float a=float(id&255)*0.01;
  if(sel) { for(int i=0;i<256;i++) a=fract(a*1.37+0.1); } else { for(int i=0;i<256;i++) a=fract(a*1.91+0.3); }
  o[id]=a; }
kernel void gatherK(device const float *in [[buffer(0)]], device float *o [[buffer(1)]], device const uint *idx [[buffer(2)]], uint id [[thread_position_in_grid]]) { o[id]=in[idx[id]]*2; }
kernel void histGlobal(device const uint *in [[buffer(0)]], device atomic_uint *h [[buffer(1)]], uint id [[thread_position_in_grid]]) {
  atomic_fetch_add_explicit(&h[in[id]&15],1,memory_order_relaxed); }
kernel void histLocal(device const uint *in [[buffer(0)]], device atomic_uint *h [[buffer(1)]], threadgroup atomic_uint *l [[threadgroup(0)]],
  uint id [[thread_position_in_grid]], uint lid [[thread_index_in_threadgroup]], uint n [[threads_per_threadgroup]]) {
  if(lid<16) atomic_store_explicit(&l[lid],0,memory_order_relaxed); threadgroup_barrier(mem_flags::mem_threadgroup);
  atomic_fetch_add_explicit(&l[in[id]&15],1,memory_order_relaxed); threadgroup_barrier(mem_flags::mem_threadgroup);
  if(lid<16) atomic_fetch_add_explicit(&h[lid],atomic_load_explicit(&l[lid],memory_order_relaxed),memory_order_relaxed); }
"""
let dev = MTLCreateSystemDefaultDevice()!, q = dev.makeCommandQueue()!
let lib = try! dev.makeLibrary(source: src, options: nil)
let W=2048, H=2048
func tex(_ f:MTLPixelFormat,_ s:MTLStorageMode)->MTLTexture{ let d=MTLTextureDescriptor.texture2DDescriptor(pixelFormat:f,width:W,height:H,mipmapped:false); d.usage = .renderTarget; d.storageMode=s; return dev.makeTexture(descriptor:d)! }
let color=tex(.rgba8Unorm,.private), depth=tex(.depth32Float,.private)
let ds: MTLDepthStencilState = { let d=MTLDepthStencilDescriptor(); d.depthCompareFunction = .less; d.isDepthWriteEnabled=true; return dev.makeDepthStencilState(descriptor:d)! }()
func pso(_ fs:String,blend:Bool=false)->MTLRenderPipelineState{ let d=MTLRenderPipelineDescriptor(); d.vertexFunction=lib.makeFunction(name:"vs"); d.fragmentFunction=lib.makeFunction(name:fs)
  d.colorAttachments[0].pixelFormat = .rgba8Unorm; d.depthAttachmentPixelFormat = .depth32Float
  if blend { let c=d.colorAttachments[0]!; c.isBlendingEnabled=true; c.sourceRGBBlendFactor = .sourceAlpha; c.destinationRGBBlendFactor = .oneMinusSourceAlpha }
  return try! dev.makeRenderPipelineState(descriptor:d) }
// Gửi liên tiếp 50 buffer, bỏ 10 đầu, lấy (khoảng thời gian 40 buffer cuối)/40. Không lấy end-start từng buffer: chúng chồng pha nhau.
// Lặp 5 đợt, báo median [min..max].
func samples(_ make:()->MTLCommandBuffer)->[Double]{ var r:[Double]=[]; for _ in 0..<5 { var cs:[MTLCommandBuffer]=[]; for _ in 0..<50 { let c=make(); c.commit(); cs.append(c) }; cs.last!.waitUntilCompleted()
  r.append((cs[49].gpuEndTime-cs[9].gpuEndTime)*1000/40) }; return r.sorted() }
func median(_ make:()->MTLCommandBuffer)->Double{ samples(make)[2] }
func stat(_ make:()->MTLCommandBuffer)->String{ let t=samples(make); return String(format:"%.2f [%.2f..%.2f]",t[2],t[0],t[4]) }
func pass(_ load:MTLLoadAction,_ store:MTLStoreAction)->MTLRenderPassDescriptor{ let p=MTLRenderPassDescriptor(); p.colorAttachments[0].texture=color; p.colorAttachments[0].loadAction=load; p.colorAttachments[0].storeAction=store
  p.depthAttachment.texture=depth; p.depthAttachment.loadAction=load; p.depthAttachment.storeAction=store; p.depthAttachment.clearDepth=1; return p }
func layers(_ p:MTLRenderPipelineState,_ order:[Float])->String{ stat { let c=q.makeCommandBuffer()!; let e=c.makeRenderCommandEncoder(descriptor:pass(.clear,.store))!
  e.setRenderPipelineState(p); e.setDepthStencilState(ds); for var z in order { e.setVertexBytes(&z,length:4,index:0); e.drawPrimitives(type:.triangle,vertexStart:0,vertexCount:3) }; e.endEncoding(); return c } }
let f2b:[Float]=(0..<16).map{0.1+Float($0)*0.05}, b2f=Array(f2b.reversed())
for (name,p) in [("opaque",pso("fsOpaque")),("discard",pso("fsDiscard")),("discard+earlyTests",pso("fsDiscardEarly")),("blend",pso("fsBlend",blend:true))] {
  print("overdraw16 \(name): 1layer=\(layers(p,[0.5]))  f2b=\(layers(p,f2b))  b2f=\(layers(p,b2f)) ms (median [min..max])") }
let op=pso("fsOpaque")
// bandwidth: 16 draw full-screen blend, 1 pass vs 16 pass; fragment rẻ hơn không đổi giữa các cấu hình
let bl=pso("fsBlend",blend:true)
// depthMode: nil = không gắn depth; false = gắn, ghi, store=dontCare; true = gắn, ghi, load/store
func bwPSO(_ withDepth:Bool)->MTLRenderPipelineState{ let d=MTLRenderPipelineDescriptor(); d.vertexFunction=lib.makeFunction(name:"vs"); d.fragmentFunction=lib.makeFunction(name:"fsBlend")
  d.colorAttachments[0].pixelFormat = .rgba8Unorm; if withDepth { d.depthAttachmentPixelFormat = .depth32Float }
  let c=d.colorAttachments[0]!; c.isBlendingEnabled=true; c.sourceRGBBlendFactor = .sourceAlpha; c.destinationRGBBlendFactor = .oneMinusSourceAlpha
  return try! dev.makeRenderPipelineState(descriptor:d) }
let always: MTLDepthStencilState = { let d=MTLDepthStencilDescriptor(); d.depthCompareFunction = .always; d.isDepthWriteEnabled=true; return dev.makeDepthStencilState(descriptor:d)! }()
for (dn,depthMode) in [("chỉ màu",Bool?.none),("màu + depth dontCare",Bool?.some(false)),("màu + depth load/store",Bool?.some(true))] {
  let p=bwPSO(depthMode != nil)
  for (name,split) in [("16 draw, 1 pass",false),("16 pass x 1 draw",true)] {
    let t=stat { let c=q.makeCommandBuffer()!; var z:Float=0.5
      func draw(_ first:Bool,_ n:Int){ let pd=MTLRenderPassDescriptor(); pd.colorAttachments[0].texture=color; pd.colorAttachments[0].loadAction = first ? .clear : .load; pd.colorAttachments[0].storeAction = .store
        if let keep=depthMode { pd.depthAttachment.texture=depth; pd.depthAttachment.clearDepth=1; pd.depthAttachment.loadAction = (!first && keep) ? .load : .clear; pd.depthAttachment.storeAction = keep ? .store : .dontCare }
        let e=c.makeRenderCommandEncoder(descriptor:pd)!; e.setRenderPipelineState(p); if depthMode != nil { e.setDepthStencilState(always) }
        e.setVertexBytes(&z,length:4,index:0); for _ in 0..<n { e.drawPrimitives(type:.triangle,vertexStart:0,vertexCount:3) }; e.endEncoding() }
      if split { for i in 0..<16 { draw(i==0,1) } } else { draw(true,16) }; return c }
    print("bandwidth \(dn), \(name): \(t) ms") } }
// CPU encode: N draw vs instanced
for n in [1000,10000] { for inst in [false,true] { var best=1e9; for _ in 0..<10 { let c=q.makeCommandBuffer()!; let e=c.makeRenderCommandEncoder(descriptor:pass(.clear,.dontCare))!; e.setRenderPipelineState(op); var z:Float=0.5
  e.setScissorRect(MTLScissorRect(x:0,y:0,width:1,height:1)); let s=DispatchTime.now().uptimeNanoseconds
  if inst { e.setVertexBytes(&z,length:4,index:0); e.drawPrimitives(type:.triangle,vertexStart:0,vertexCount:3,instanceCount:n) } else { for _ in 0..<n { e.setVertexBytes(&z,length:4,index:0); e.drawPrimitives(type:.triangle,vertexStart:0,vertexCount:3) } }
  best=min(best,Double(DispatchTime.now().uptimeNanoseconds-s)/1e6); e.endEncoding(); c.commit(); c.waitUntilCompleted() }
  print(String(format:"cpu encode n=%d instanced=%@: %.3f ms",n,inst ? "yes":"no",best)) } }
// compute
let N=1<<22
func cp(_ n:String)->MTLComputePipelineState{ try! dev.makeComputePipelineState(function:lib.makeFunction(name:n)!) }
func run(_ p:MTLComputePipelineState,_ bufs:[MTLBuffer],_ extra:UInt32?=nil,tg:Int=0)->Double{ median { let c=q.makeCommandBuffer()!; let e=c.makeComputeCommandEncoder()!; e.setComputePipelineState(p)
  for (i,b) in bufs.enumerated(){ e.setBuffer(b,offset:0,index:i) }; if var x=extra { e.setBytes(&x,length:4,index:bufs.count) }; if tg>0 { e.setThreadgroupMemoryLength(tg,index:0) }
  e.dispatchThreads(MTLSize(width:N,height:1,depth:1),threadsPerThreadgroup:MTLSize(width:256,height:1,depth:1)); e.endEncoding(); return c } }
func buf(_ a:[UInt32])->MTLBuffer{ a.withUnsafeBytes{ dev.makeBuffer(bytes:$0.baseAddress!,length:$0.count,options:.storageModeShared)! } }
let out=dev.makeBuffer(length:N*4,options:.storageModeShared)!, inb=dev.makeBuffer(length:N*4,options:.storageModeShared)!
let dv=cp("diverge"); print("simd width=\(dv.threadExecutionWidth)")
print(String(format:"diverge coherent=%.2f ms  per-lane=%.2f ms", run(dv,[out],0), run(dv,[out],1)))
let seq=Array(0..<UInt32(N)); var g=SystemRandomNumberGenerator(); let rnd=seq.shuffled(using:&g); let gk=cp("gatherK")
print(String(format:"gather 4M sequential=%.2f ms random=%.2f ms", run(gk,[inb,out,buf(seq)]), run(gk,[inb,out,buf(rnd)])))
let data=buf(rnd), h=dev.makeBuffer(length:64,options:.storageModeShared)!
print(String(format:"histogram16 global-atomic=%.2f ms threadgroup=%.2f ms", run(cp("histGlobal"),[data,h]), run(cp("histLocal"),[data,h],tg:64)))
print("GPU: \(dev.name)")
