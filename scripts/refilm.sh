#!/bin/zsh
# =============================================================
# MIDDLE STUDIES II — 既存作品の動画をプロダクトフィルムに作り直す（2026-09-23）
#   zsh scripts/refilm.sh 001 002 003 ...
# 1本ずつ：AI が script.py に SHOTS を足して動画レビュー → REFILM_READY で抜ける
#          → このシェルが anim を描く → check.py film → commit & push
# 🔴 静止画（hero.png）・ルック・造形は変えない。作り直すのは動画だけ。
# 🔴 anim は AI に待たせない（daily.sh と同じ理由：レンダー待ちでターンを終えて死ぬ）。
# =============================================================
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
export LANG="ja_JP.UTF-8"
ROOT="$HOME/projects/middle-studies"
SKILL_MD="$ROOT/skill/SKILL.md"
BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"
CLAUDE_BIN="$(command -v claude || echo /opt/homebrew/bin/claude)"
LOG="$ROOT/logs/refilm-$(TZ=Asia/Tokyo date +%F).log"
cd "$ROOT" || exit 1

for id in "$@"; do
  D="$(ls -d "$ROOT"/ii/works/${id}_* 2>/dev/null | head -1)"
  [[ -d "$D" ]] || { echo "[$(date)] 🔴 $id が無い" >> "$LOG"; continue; }
  NAME="$(basename "$D")"
  echo "[$(date)] === $NAME 開始 ===" >> "$LOG"
  OUT="$(mktemp /tmp/refilm.XXXXXX)"
  "$CLAUDE_BIN" -p "まず「$SKILL_MD」を読み、工程4-b（動画を組む）と技術の正典を把握する。
いまから公開済みの作品 ii/works/$NAME の**動画だけ**をプロダクトフィルム（10〜12秒・3〜4カット・最後は hero の構図で1秒以上止まる）に作り直す。
🔴 変えないもの：hero.png・model.glb・ルック（色・舞台・光・素材）・造形。hero.png は描き直さない。
手順：
1. script.py を読み、動きとカメラの作りを把握する。雛形 ii/template.py の「動画＝プロダクトフィルム」節（SHOTS・ease・ease_out・orbit・shots モード・II_ANIM_SAMPLES/II_ANIM_LONG を読む anim）を移植する。物の動きは今のものを全体の進み T に合わせて残してよい。
2. 最後のカットの終わりは、今の hero と同じカメラ（位置・注視点・レンズ・f値・フレーム）にする。STILL_FRAME＝最後のフレーム。確かめ方：最後のフレームを長辺1600で描き（testhero 相当）、python3 ii/scripts/check.py の distance/signature で hero.png と比べて 0.08 以下。
3. -- shots → python3 ii/scripts/contact.py ii/works/$NAME → _contact.png を Read して判定。REVIEW.md の末尾に「## film round N」で記録（最低2周・最後の周に「直すこと」を残さない＝直したら描き直して確かめる）。寄り・中・引きを混ぜ、1つはマクロ。前のカットと画を変える。舞台の端・暗部が写らないか。
4. 長辺1080で1フレーム描いて秒数を測り、秒/フレーム×フレーム数が120分以内のサンプル数を決め、echo \"samples=N\" > ii/works/$NAME/ANIM_REQUEST。
5. ii/works.json の該当行に \"film\": {\"sec\": 秒, \"shots\": [カットの型の名前…]} を足す。loop_seconds があれば消す。
6. anim は描かない。git も触らない。最後の行に REFILM_READY とだけ出して終わる。" \
    --model claude-opus-5-5 --dangerously-skip-permissions > "$OUT" 2>&1
  cat "$OUT" >> "$LOG"
  if ! tail -8 "$OUT" | grep -q "REFILM_READY" || [[ ! -f "$D/ANIM_REQUEST" ]]; then
    echo "[$(date)] 🔴 $NAME：AI が REFILM_READY まで届かなかった。飛ばす" >> "$LOG"
    rm -f "$OUT"; continue
  fi
  SAMPLES="$(grep -o 'samples=[0-9]*' "$D/ANIM_REQUEST" | cut -d= -f2)"
  cp "$D/loop.mp4" "/tmp/${NAME}_loop_before.mp4" 2>/dev/null
  for try in 1 2; do
    echo "[$(date)] anim 開始 $NAME samples=${SAMPLES:-24}（試行 $try）" >> "$LOG"
    ( cd "$D" && rm -f loop.mp4 && II_ANIM_SAMPLES="${SAMPLES:-24}" caffeinate -i "$BLENDER" --background --factory-startup \
        --python script.py -- anim 2>&1 | grep -E "anim done|Error|Traceback" >> "$LOG" )
    NB="$(ffprobe -v error -show_entries stream=nb_frames -of default=nw=1:nk=1 "$D/loop.mp4" 2>/dev/null)"
    echo "[$(date)] anim 終了 nb_frames=${NB:-0}" >> "$LOG"
    (( ${NB:-0} >= 100 )) && break
  done
  rm -f "$D/ANIM_REQUEST"
  if (( ${NB:-0} < 100 )); then
    echo "[$(date)] 🔴 $NAME：anim が描けなかった。元の loop.mp4 に戻す" >> "$LOG"
    cp "/tmp/${NAME}_loop_before.mp4" "$D/loop.mp4" 2>/dev/null
    git checkout -- "$D/script.py" ii/works.json 2>/dev/null
    rm -f "$OUT"; continue
  fi
  python3 ii/scripts/check.py film "$D/loop.mp4" "$D/hero.png" >> "$LOG" 2>&1
  FRC=$?
  if (( FRC != 0 )); then
    echo "[$(date)] 🔴 $NAME：check.py film が🔴。公開しない（新しい loop.mp4 は $D に残す）" >> "$LOG"
    # 🔴 works.json のこの作品の行だけ、公開済みの内容に戻す（戻さないと、次の作品の commit に混ざって
    #    「サイトの動画は旧版なのに記録だけ film」になる＝2026-09-24 に 001・003 で実際に起きた）
    python3 - "$id" <<'PY'
import json, subprocess, sys
wid = sys.argv[1]
head = json.loads(subprocess.run(["git", "show", "HEAD:ii/works.json"], capture_output=True, text=True).stdout)
cur = json.load(open("ii/works.json"))
old = next((w for w in head if w["id"] == wid), None)
cur = [old if (w["id"] == wid and old) else w for w in cur]
json.dump(cur, open("ii/works.json", "w"), ensure_ascii=False, indent=2); open("ii/works.json", "a").write("\n")
PY
    rm -f "$OUT"; continue
  fi
  git add "$D/script.py" "$D/loop.mp4" "$D/REVIEW.md" ii/works.json
  git commit -q -m "II $NAME：動画をプロダクトフィルムに作り直し（静止画は据え置き）

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>" && git push -q origin main
  echo "[$(date)] ✅ $NAME 公開（push $?）" >> "$LOG"
  rm -f "$OUT"
done
echo "[$(date)] === refilm 全件終了 ===" >> "$LOG"
