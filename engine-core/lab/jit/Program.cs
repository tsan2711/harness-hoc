using System; using System.Diagnostics; using System.Runtime.CompilerServices;
interface IDamage { int Apply(int hp); }
struct Fire : IDamage { public int Apply(int hp) => hp - 3; }
struct D0:IDamage{public int Apply(int h)=>h-1;} struct D1:IDamage{public int Apply(int h)=>h-2;} struct D2:IDamage{public int Apply(int h)=>h-4;} struct D3:IDamage{public int Apply(int h)=>h-5;}
struct D4:IDamage{public int Apply(int h)=>h-6;} struct D5:IDamage{public int Apply(int h)=>h-7;} struct D6:IDamage{public int Apply(int h)=>h-8;}
static class P {
  [MethodImpl(MethodImplOptions.NoInlining)] static int Mixed(IDamage[] d, int n) { int h=0; for (int i=0;i<n;i++) h = d[i&4095].Apply(h); return h; }
  [MethodImpl(MethodImplOptions.NoInlining)] static int Boxed(IDamage d, int n) { int h=0; for (int i=0;i<n;i++) h = d.Apply(h); return h; }
  [MethodImpl(MethodImplOptions.NoInlining)] static int Generic<T>(T d, int n) where T:struct,IDamage { int h=0; for (int i=0;i<n;i++) h = d.Apply(h); return h; }
  [MethodImpl(MethodImplOptions.NoInlining)] static int SumLen(int[] a) { int s=0; for (int i=0;i<a.Length;i++) s+=a[i]; return s; }
  [MethodImpl(MethodImplOptions.NoInlining)] static int SumN(int[] a,int n) { int s=0; for (int i=0;i<n;i++) s+=a[i]; return s; }
  static void Bench(string name, Func<int> f) {
    for (int k=0;k<100;k++) f(); System.Threading.Thread.Sleep(300); for (int k=0;k<100;k++) f();
    double best=1e9; for (int r=0;r<15;r++){ var s=Stopwatch.GetTimestamp(); f(); best=Math.Min(best,Stopwatch.GetElapsedTime(s).TotalMilliseconds);} 
    Console.WriteLine($"{name,-8} {best:F3} ms"); }
  static void Main() {
    const int N=10_000_000; var a=new int[1024]; IDamage b=new Fire();   // 4 KB: nam trong L1
    IDamage[] kinds={new Fire(),new D0(),new D1(),new D2(),new D3(),new D4(),new D5(),new D6()}; var rnd=new Random(1);
    var one=new IDamage[4096]; var mix=new IDamage[4096]; for(int i=0;i<4096;i++){ one[i]=b; mix[i]=kinds[rnd.Next(8)]; }
    Bench("boxed", ()=>Boxed(b,N)); Bench("generic", ()=>Generic(new Fire(),N));
    Bench("array1", ()=>Mixed(one,N)); Bench("array8", ()=>Mixed(mix,N));
    Bench("sumLen", ()=>{ int s=0; for(int r=0;r<10_000;r++) s+=SumLen(a); return s; });
    Bench("sumN", ()=>{ int s=0; for(int r=0;r<10_000;r++) s+=SumN(a,a.Length); return s; });
  }
}
