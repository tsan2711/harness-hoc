#!/bin/sh
# sh run.sh build        -> Build/stress.app (Metal)
# sh run.sh bench [tiền tố] -> chạy player có cửa sổ, ghi results/mac/bench.csv + ảnh
cd "$(dirname "$0")" || exit 1
UNITY=${UNITY:-/Applications/Unity/Hub/Editor/$(awk '/^m_EditorVersion:/{print $2}' ProjectSettings/ProjectVersion.txt)/Unity.app/Contents/MacOS/Unity}
case $1 in
 build) "$UNITY" -batchmode -quit -projectPath "$PWD" -executeMethod Build.Mac -logFile "$PWD/Logs/build.log"; rc=$?
        grep -E 'error CS|Shader error|Exception' Logs/build.log | head -20; echo "build rc=$rc"; exit $rc ;;
 bench) mkdir -p results/mac; uptime > results/mac/load.txt
        Build/stress.app/Contents/MacOS/* -screen-width 1280 -screen-height 720 -screen-fullscreen 0 -out "$PWD/results/mac" -only "$2" -logFile "$PWD/Logs/player.log"
        uptime >> results/mac/load.txt; cat results/mac/load.txt results/mac/bench.csv ;;
 *) echo "build | bench" ;;
esac
