// Live heap vs rác/frame trên CoreCLR GC. args: <số node sống> 
using System; using System.Diagnostics; using System.Linq; using System.Runtime;
class Node { public Node next; public long payload; }
static class P {
  static void Main(string[] a) {
    int live = int.Parse(a[0]); string mode = a.Length > 1 ? a[1] : "none"; // none | young (gia->tre) | old (gia->gia)
    var keep = new Node[live];
    for (int i = 0; i < live; i++) keep[i] = new Node { next = i > 0 ? keep[i-1] : null };
    GC.Collect(); GC.Collect();
    var rnd = new Random(1); var t = new double[2000];
    var p0=GC.GetTotalPauseDuration(); int g0=GC.CollectionCount(0), g1=GC.CollectionCount(1), g2=GC.CollectionCount(2);
    object sink = null;
    for (int f = 0; f < t.Length; f++) {
      long s = Stopwatch.GetTimestamp();
      for (int i = 0; i < 20000; i++) { var n = new Node(); sink = n;           // ~0.8 MB rác/frame
        if (i % 10 == 0) {                                                       // 2000 lan ghi/frame
          if (mode == "young") keep[rnd.Next(live)].next = n;
          else if (mode == "old") keep[rnd.Next(live)].next = keep[rnd.Next(live)]; } }
      t[f] = Stopwatch.GetElapsedTime(s).TotalMilliseconds;
    }
    Array.Sort(t);
    var pause=(GC.GetTotalPauseDuration()-p0).TotalMilliseconds; Console.WriteLine($"pauseTotalMs={pause,7:F0} live={live,9} mode={mode,-5} heapMB={GC.GetTotalMemory(false)/1e6,6:F0} p50={t[1000]:F3} p99={t[1980]:F3} max={t[^1]:F2} gc0/1/2={GC.CollectionCount(0)-g0}/{GC.CollectionCount(1)-g1}/{GC.CollectionCount(2)-g2}");
    GC.KeepAlive(keep); GC.KeepAlive(sink);
  }
}
