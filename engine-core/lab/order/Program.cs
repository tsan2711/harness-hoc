// (1) store-buffer reorder, (2) false sharing 64 vs 128 byte
using System; using System.Diagnostics; using System.Runtime.InteropServices; using System.Threading;
static class P {
  static int x,y,r1,r2;
  static void Litmus(bool fence) {
    int bad=0, N=200_000; var go=new Barrier(3); var done=new Barrier(3);
    void W(bool first){ for(int i=0;i<N;i++){ go.SignalAndWait();
        if(first){ x=1; if(fence) Interlocked.MemoryBarrier(); r1=y; } else { y=1; if(fence) Interlocked.MemoryBarrier(); r2=x; }
        done.SignalAndWait(); } }
    var a=new Thread(()=>W(true)); var b=new Thread(()=>W(false)); a.Start(); b.Start();
    for(int i=0;i<N;i++){ x=y=0; go.SignalAndWait(); done.SignalAndWait(); if(r1==0&&r2==0) bad++; }
    a.Join(); b.Join(); Console.WriteLine($"litmus fence={fence}: r1=r2=0 xảy ra {bad}/{N}");
  }
  static unsafe void Share(int strideBytes) {
    int s=strideBytes/8; var all=new double[9];
    long* c=(long*)NativeMemory.AlignedAlloc(4096,128); NativeMemory.Clear(c,4096);   // c[0] nam dung bien 128 B
    for(int r=0;r<9;r++){ var ts=new Thread[4]; var sw=Stopwatch.StartNew();
      for(int t=0;t<4;t++){ long* p=c+t*s; ts[t]=new Thread(()=>{ for(int i=0;i<20_000_000;i++) Volatile.Write(ref *p, *p+1); }); ts[t].Start(); }
      foreach(var t in ts) t.Join(); all[r]=sw.Elapsed.TotalMilliseconds; }
    Array.Sort(all); NativeMemory.AlignedFree(c);
    Console.WriteLine($"false-sharing stride={strideBytes,4}B: min={all[0]:F0} median={all[4]:F0} ms");
  }
  static void Main(){ Litmus(false); Litmus(true); foreach(var s in new[]{8,64,128,256}) Share(s); }
}
