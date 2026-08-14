#!/bin/zsh
# =============================================================
# 既存作の作り直し用ドライバ（2026-08-14）
#   zsh scripts/rebuild.sh 023_utsuwa 025_uzu ...
# 各作を still glb → anim の順にレンダーし、OUT から hero/loop/model を作品直下へ配置する。
# 🔴 レンダーは同期実行（#5：バックグラウンドにすると子プロセスごと死ぬ）
# =============================================================
BL="/Applications/Blender.app/Contents/MacOS/Blender"
ROOT="$HOME/projects/middle-studies/works"

for w in "$@"; do
  d="$ROOT/$w"
  [[ -d "$d" ]] || { echo "🔴 no dir: $w"; continue }
  echo "=== $w  $(date +%H:%M:%S) ==="
  ( cd "$d" && "$BL" --background --factory-startup --python script.py -- still glb 2>&1 | grep -E "done|GLB|Error|Traceback" | head -4 )
  ( cd "$d" && "$BL" --background --factory-startup --python script.py -- anim 2>&1 | grep -E "done|Error|Traceback" | head -4 )
  # OUT を探して配置（OUT が作品直下なら何もしない）
  setopt local_options null_glob
  for o in "$d"/out "$d"/out_*; do
    [[ -d "$o" ]] || continue
    p=$(ls -t "$o"/*.png 2>/dev/null | grep -v test | head -1)
    m=$(ls -t "$o"/*.mp4 2>/dev/null | head -1)
    g=$(ls -t "$o"/*.glb 2>/dev/null | head -1)
    [[ -n "$p" ]] && cp "$p" "$d/hero.png"
    [[ -n "$m" ]] && cp "$m" "$d/loop.mp4"
    [[ -n "$g" ]] && cp "$g" "$d/model.glb"
    break
  done
  echo "--- $w 配置完了 $(ls -la $d/hero.png $d/loop.mp4 $d/model.glb 2>/dev/null | awk '{printf "%s ", $5}')"
done
echo "ALL DONE $(date +%H:%M:%S)"
