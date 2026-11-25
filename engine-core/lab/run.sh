#!/bin/sh
# Chạy: sh run.sh gpu|jit|gc|order|vec  -> ghi results/<tên>.txt (bài trích số từ đây)
cd "$(dirname "$0")" || exit 1
out="$PWD/results/$1.txt"
{ date +%F; uptime
case $1 in
 gpu)  (cd gpu && swiftc -O main.swift -o lab.out && ./lab.out) ;;
 jit)  (cd jit && dotnet build -c Release -v q --nologo >/dev/null
        for p in 1 0; do echo "== TieredPGO=$p"; DOTNET_TieredPGO=$p dotnet bin/Release/net9.0/jit.dll; done
        echo "== JitDisasm (trich)"; DOTNET_JitStdOutFile="$PWD/asm.out" DOTNET_JitDisasm="Boxed SumN SumLen" dotnet bin/Release/net9.0/jit.dll >/dev/null; grep -c . asm.out) ;;
 gc)   (cd gc && dotnet build -c Release -v q --nologo >/dev/null
        for n in 100000 1000000 8000000; do for m in none young old; do dotnet bin/Release/net9.0/gc.dll $n $m; done; done) ;;
 order) (cd order && dotnet build -c Release -v q --nologo >/dev/null && dotnet bin/Release/net9.0/order.dll
        DOTNET_TieredCompilation=0 DOTNET_JitStdOutFile="$PWD/asm.out" DOTNET_JitDisasm='*Litmus*W*' dotnet bin/Release/net9.0/order.dll >/dev/null; echo "== JitDisasm luong ghi/doc"; grep -E '; Assembly|str |ldr |dmb|stlr|ldar|; Total' asm.out | head -40) ;;
 vec)  (cd vec && clang -O3 -S -o add.out add.c -Rpass=loop-vectorize -Rpass-missed=loop-vectorize -Rpass-analysis=loop-vectorize 2>&1; clang --version | head -1) ;;
esac; } > "$out" 2>&1
cat "$out"
