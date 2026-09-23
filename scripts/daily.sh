#!/bin/zsh
# MIDDLE STUDIES II 制作ジョブ（launchd: com.monaka.middle-study が 月・水・金 2:00 JST に起動／4:30 がキャッチアップ）
# Claude Code をヘッドレスで起動し、スキル blender-middle-study の手順で1作品を制作・公開する。
# 2026-09-23：第1期（毎日・001〜089）を完結し、第2期（週3本・ii/）へ移行（Ryota決定）。
#
# 注意: launchd起動のプロセスはmacOSのTCC制限でGoogle Drive(CloudStorage)配下を読めない。
# そのためスキル本体は ~/projects/middle-studies/skill/（= ~/.claude/skills/blender-middle-study への
# symlink実体）に置く。CEO/.claude/skills には置かないこと（2026-07-11の障害の根本原因）。

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
export LANG="ja_JP.UTF-8"

# claude 実体の解決（2026-07-27追加）。絶対パス直書きをやめた理由：
# Claude Code の更新で /opt/homebrew/bin/claude の symlink が一時的に消えることがあり、
# 2026-07-21 に routine-watchdog が実際にこれで1回目の実行に失敗した（5分後の再試行で復旧）。
# 監視役を含む5本が同じパスを直書きしていたため、同時に沈黙しうる状態だった。
CLAUDE_BIN=""
for _c in "$(command -v claude 2>/dev/null || true)" \
          /opt/homebrew/bin/claude \
          "$HOME/.local/bin/claude" \
          /opt/homebrew/lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe; do
  if [ -n "$_c" ] && [ -x "$_c" ]; then CLAUDE_BIN="$_c"; break; fi
done
# 見つからなくても止めない（従来どおり実行に失敗させ、各スクリプトのリトライ＋無言失敗ガードに任せる）
[ -n "$CLAUDE_BIN" ] || CLAUDE_BIN="/opt/homebrew/bin/claude"


# Slack Webhook はリポジトリの外から読む。
# 🔴 SKILL.md にも、このスクリプトにも、URLを直書きしない。
#    skill/ は ~/.claude/skills/blender-middle-study/ とハードリンクで public にミラーされ、
#    scripts/ も public。どちらに書いても GitHub の Push Protection が push を拒否し、
#    毎晩のルーティンが公開まで到達できなくなる（2026-07-15に直書きして停止・7/16に解消）。
[ -f "$HOME/.config/monaka/slack.env" ] && source "$HOME/.config/monaka/slack.env"
export SLACK_WEBHOOK="${SLACK_WEBHOOK_SAKUHIN:-}"   # #mona-作品

notify() {
  # 通知到達を最優先。Claudeが起動すらできない失敗でも、このシェルからは必ず1通出す。
  # （2026-07-17 02:05 に claude が EPERM で即死し、どこにも通知が飛ばなかった対策。anime-demoと同じ実装）
  local text="$1"
  local payload
  [ -z "$SLACK_WEBHOOK" ] && { echo "[$(date)] SLACK_WEBHOOK empty — notify skipped" >> "$LOG_FILE"; return 1; }
  payload=$(printf '%s' "$text" | python3 -c 'import json,sys; print(json.dumps({"text": sys.stdin.read()}))')
  curl -sS -m 15 -X POST -H 'Content-type: application/json' --data "$payload" "$SLACK_WEBHOOK" >/dev/null 2>&1
}

CEO_DIR="/Users/shitoryota/Library/CloudStorage/GoogleDrive-ryota4100221@gmail.com/マイドライブ/monaka design./CEO"
SKILL_MD="$HOME/projects/middle-studies/skill/SKILL.md"
LOG_DIR="$HOME/projects/middle-studies/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/$(TZ=Asia/Tokyo date +%F).log"

# 成功ガード：今日すでに完走していたら何もしない（キャッチアップ枠9:00が重複制作しないため）
# II_FORCE=1 のときは飛ばす（2026-09-23：第1期の089が同日朝に完走済みの日に、IIの試作を手で走らせるため）
if [[ -z "${II_FORCE:-}" ]] && grep -q "=== done (exit 0" "$LOG_FILE" 2>/dev/null; then
  echo "[$(date)] already succeeded today — skip (catch-up slot)" >> "$LOG_FILE"
  exit 0
fi

# 制作日ガード（2026-09-23）：月・水・金（JST）以外は何もしない。
# launchd は月水金しか起動しないが、手で叩かれたときに制作日でない日に1本作らないため。
# 意図して作らせたいときは II_FORCE=1 を付ける。
DOW="$(TZ=Asia/Tokyo date +%u)"
if [[ "$DOW" != (1|3|5) && -z "${II_FORCE:-}" ]]; then
  echo "[$(date)] not a production day (dow=$DOW) — skip" >> "$LOG_FILE"
  exit 0
fi

# 二重起動ガード（前日の実行が長引いた場合など）
LOCK="/tmp/middle-study.lock"
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "[$(date)] already running, skip" >> "$LOG_FILE"
  exit 0
fi
trap 'rmdir "$LOCK"' EXIT

if ! head -c 1 "$SKILL_MD" >/dev/null 2>&1; then
  echo "[$(date)] ABORT: skill file unreadable: $SKILL_MD" >> "$LOG_FILE"
  exit 1
fi

# CEO配下はlaunchdから読めないことがあるため、cd失敗時はローカルにフォールバック
cd "$CEO_DIR" 2>/dev/null || cd "$HOME/projects/middle-studies" || exit 1

echo "[$(date)] === MIDDLE STUDY daily start (cwd: $PWD) ===" >> "$LOG_FILE"
OUT_TMP="$(mktemp /tmp/middle-study-out.XXXXXX)"

# Claude利用上限（session limit）に当たった場合は1時間おきに最大10回リトライする。
# 2026-07-11 08:00 の再実行が "You've hit your session limit · resets 12pm" で失敗した対策。
MAX_ATTEMPTS=10
attempt=1
RC=1
while (( attempt <= MAX_ATTEMPTS )); do
  echo "[$(date)] --- attempt $attempt/$MAX_ATTEMPTS ---" >> "$LOG_FILE"
  # II_FORCE=1 のときは AI にも force を渡す（SKILL.md 工程0の「制作日か／今日の分は済んだか」を飛ばす）
  "$CLAUDE_BIN" -p "/blender-middle-study daily${II_FORCE:+ force}" \
    --model claude-opus-5-5 \
    --dangerously-skip-permissions \
    > "$OUT_TMP" 2>&1
  RC=$?
  cat "$OUT_TMP" >> "$LOG_FILE"

  # スラッシュコマンド解決に失敗した場合は、SKILL.md を直接読ませるプロンプトで即リトライ
  if grep -q "Unknown command" "$OUT_TMP"; then
    echo "[$(date)] slash command unresolved — retrying with direct skill prompt" >> "$LOG_FILE"
    "$CLAUDE_BIN" -p "まず「$SKILL_MD」を読み、そこに書かれたパイプラインに厳密に従って daily${II_FORCE:+ force} 実行（今日のMIDDLE STUDIES IIを1作品制作・公開・記録）を完走して。" \
      --model claude-opus-5-5 \
      --dangerously-skip-permissions \
      > "$OUT_TMP" 2>&1
    RC=$?
    cat "$OUT_TMP" >> "$LOG_FILE"
  fi

  # 🔴 完走の証拠があれば、失敗判定に一切かけずに抜ける（2026-09-10追加）。
  #    失敗判定は「AIが吐いた本文を grep する」ので、AI自身が経緯として同じ語を書くと誤爆する。
  #    実際に 2026-09-10 15:03 の回は 075 を完走（MIDDLE_OK・公開もNotionもSlackも済）したのに、
  #    本文中の「12:38 の catch-up は session limit に当たって中断」を掴んで「usage limit hit」と誤判定し、
  #    60分寝てから4回目を起動した＝**同じ日に2作目を作らせかけた**。
  #    成功の判定を失敗の判定より先に置くのが唯一の直し方（順序が仕様）。
  if (( RC == 0 )) && tail -8 "$OUT_TMP" | grep -q "MIDDLE_OK"; then
    echo "[$(date)] MIDDLE_OK 確認 — 完走（以降の再試行判定はしない）" >> "$LOG_FILE"
    break
  fi
  if (( RC == 0 )) && tail -8 "$OUT_TMP" | grep -q "MIDDLE_ANIM_READY"; then
    echo "[$(date)] MIDDLE_ANIM_READY 確認 — 制作は完了。anim はこのシェルが描く" >> "$LOG_FILE"
    break
  fi

  # 利用上限なら1時間待って再試行（上限リセットを跨ぐまで粘る）
  # 🔴 2026-09-10：素の "session limit" では上記のとおり本文に誤爆する。
  #    CLIが出す英文そのものか、**出力の末尾3行**（本当に上限で切れたならそこに出る）だけを見る。
  if grep -qiE "You.?ve hit your [a-z]+ limit|usage limit reached|rate limit exceeded" "$OUT_TMP" \
     || tail -n 3 "$OUT_TMP" | grep -qiE "session limit|usage limit|rate limit"; then
    echo "[$(date)] usage limit hit — sleeping 60min then retrying" >> "$LOG_FILE"
    sleep 3600
    (( attempt++ ))
    continue
  fi

  # 一時的な内部エラー（EPERM等）とネットワーク断・タイムアウトは5分待って再試行。
  # 2026-07-17 02:05 に "An internal error occurred (EPERM)" で1回で即死した対策。
  # 2026-07-30 02:10 の "Request timed out"（約5時間掴んだ末にexit 1）はこの正規表現のどれにも
  # 当たらず、MAX_ATTEMPTS=10 の設計にもかかわらず attempts 1 で即死した。9:00のキャッチアップ枠が
  # 救ったが、予備枠も同じタイムアウトを踏めばその日は丸ごと欠番になる。通信系も同じ枠で拾う。
  if (( RC != 0 )) && grep -qiE "internal error|EPERM|timed out|timeout|ECONNRESET|ETIMEDOUT|ENOTFOUND|network error|fetch failed|connection closed|connection reset|overloaded" "$OUT_TMP"; then
    echo "[$(date)] transient error (internal/network) — sleeping 5min then retrying" >> "$LOG_FILE"
    sleep 300
    (( attempt++ ))
    continue
  fi

  # 🔴 exit 0 を信用しない（2026-08-01追加）。
  #    design-nippo の初回実行で「**AIが権限を求めて止まったのに exit 0**」を実際に踏んだ。
  #    「終わったつもりで終わっていない」は最も気づけない壊れ方なので、完走の証拠を要求する。
  #    ⚠️ **制御フローは変えない**（RCもリトライも触らない）。動いているものを壊さないため。
  #    証拠が無ければ印を置くだけにし、**毎朝10:00のローカル日次点検がその印を拾って通知する**。
  if (( RC == 0 )) && ! tail -8 "$OUT_TMP" | grep -qE "MIDDLE_OK|MIDDLE_ANIM_READY"; then
    echo "[$(date)] exit 0 だが完走の証拠（MIDDLE_OK）が無い" >> "$LOG_FILE"
    touch "$(dirname "$LOG_FILE")/INCOMPLETE-$(TZ=Asia/Tokyo date +%F)"
  fi

  break
done

# 🔴 anim はシェルが描く（2026-09-23）。AI にレンダーを待たせると、ターンを終えてセッションごと死ぬ
#    （第1期 003・062／II 002・005）。AI は still・glb・mask まで作って MIDDLE_ANIM_READY で抜ける。
#    シェルは時間の制限なくレンダーを待てるので、ここで描いてフレーム数を確かめ、公開だけを次のセッションに渡す。
BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"
publish_prompt() {
  echo "まず「$SKILL_MD」を読む。今日のMIDDLE STUDIES IIは、制作（工程1〜5）と anim のレンダーまで終わっている。制作・自己レビュー・レンダーはやり直さない。ii/works/ の最新の作品フォルダ（$(basename "$1")）について、工程6（check.py all が🔴0件→commit & push）→工程7（Notion）→完走の証明 までを完走して。🔴が出たら、直せるもの（works.json の記入漏れ・compose_note・不要ファイル）は直す。anim の描き直しが要る🔴なら直さずに、止まった理由を書いて終わる。"
}
if (( RC == 0 )) && tail -8 "$OUT_TMP" | grep -q "MIDDLE_ANIM_READY"; then
  REQ="$(ls -t "$HOME"/projects/middle-studies/ii/works/*/ANIM_REQUEST 2>/dev/null | head -1)"
  if [[ -z "$REQ" ]]; then
    echo "[$(date)] 🔴 MIDDLE_ANIM_READY なのに ANIM_REQUEST が無い" >> "$LOG_FILE"
    RC=1
  else
    ADIR="$(dirname "$REQ")"
    SAMPLES="$(grep -o 'samples=[0-9]*' "$REQ" | cut -d= -f2)"
    for try in 1 2; do
      echo "[$(date)] anim 開始 $(basename "$ADIR") samples=${SAMPLES:-24}（試行 $try）" >> "$LOG_FILE"
      ( cd "$ADIR" && rm -f loop.mp4 && II_ANIM_SAMPLES="${SAMPLES:-24}" caffeinate -i "$BLENDER" --background --factory-startup \
          --python script.py -- anim 2>&1 | grep -E "anim done|Error|Traceback" >> "$LOG_FILE" )
      NB="$(ffprobe -v error -show_entries stream=nb_frames -of default=nw=1:nk=1 "$ADIR/loop.mp4" 2>/dev/null)"
      echo "[$(date)] anim 終了 nb_frames=${NB:-0}" >> "$LOG_FILE"
      (( ${NB:-0} >= 100 )) && break
    done
    if (( ${NB:-0} >= 100 )); then
      rm -f "$REQ"
      "$CLAUDE_BIN" -p "$(publish_prompt "$ADIR")" --model claude-opus-5-5 --dangerously-skip-permissions > "$OUT_TMP" 2>&1
      RC=$?
      cat "$OUT_TMP" >> "$LOG_FILE"
      if (( RC == 0 )) && tail -8 "$OUT_TMP" | grep -q "MIDDLE_OK"; then
        echo "[$(date)] 公開セッションで MIDDLE_OK 確認 — 完走" >> "$LOG_FILE"
      else
        touch "$(dirname "$LOG_FILE")/INCOMPLETE-$(TZ=Asia/Tokyo date +%F)"
      fi
    else
      echo "[$(date)] 🔴 anim を2回描いても loop.mp4 が120フレームに届かない" >> "$LOG_FILE"
      touch "$(dirname "$LOG_FILE")/INCOMPLETE-$(TZ=Asia/Tokyo date +%F)"
      RC=1
    fi
  fi
fi

# 🔴 レンダー待ちでターンを終えた回の救済（2026-09-23 追加）
#    SKILL.md に「anim は caffeinate -w で同期して待つ」と書いてあっても、AIは
#    「終わると通知が来るので、そのあと点検と公開に進みます」と書いてターンを終える。
#    ヘッドレスではそこでセッションが終わり、公開まで届かない（2026-07-11 003／08-25・26 062／09-23 II 002 の3回目）。
#    文章の指示ではもう防げないので、シェルが拾う：完走の証拠が無く、今日の作品に hero.png がある
#    （＝制作は済んでいる）なら、anim の終了を待ってから「工程5の残りから」で1回だけ起動し直す。
resume_prompt() {
  echo "まず「$SKILL_MD」を読む。今日のMIDDLE STUDIES IIは、前のセッションが工程5（本番レンダー）の途中で終了した。制作・自己レビューはやり直さない。ii/works/ の最新の作品フォルダについて、loop.mp4 を ffprobe で測り nb_frames が尺どおり（24fps×秒）でなければ anim を同期でやり直し（SKILL.md 工程5の caffeinate -w の手順どおり・ターンを終えない）、model.glb が無ければ書き出し、工程6（check.py all が🔴0件→commit & push）→工程7（Notion）→完走の証明 までを完走して。"
}
if (( RC == 0 )) && ! tail -8 "$OUT_TMP" | grep -q "MIDDLE_OK"; then
  LATEST_DIR="$(ls -d "$HOME"/projects/middle-studies/ii/works/[0-9]*_* 2>/dev/null | tail -1)"
  if [[ -n "$LATEST_DIR" && -f "$LATEST_DIR/hero.png" ]] && ! git -C "$HOME/projects/middle-studies" ls-files --error-unmatch "$LATEST_DIR/hero.png" >/dev/null 2>&1; then
    echo "[$(date)] 未公開の作品 $(basename "$LATEST_DIR") が残っている — anim の終了を待って工程5の残りから再開" >> "$LOG_FILE"
    while pgrep -f "script.py -- anim" >/dev/null; do sleep 30; done
    echo "[$(date)] anim 終了を確認 — 再開セッションを起動" >> "$LOG_FILE"
    "$CLAUDE_BIN" -p "$(resume_prompt)" --model claude-opus-5-5 --dangerously-skip-permissions > "$OUT_TMP" 2>&1
    RC=$?
    cat "$OUT_TMP" >> "$LOG_FILE"
    if (( RC == 0 )) && tail -8 "$OUT_TMP" | grep -q "MIDDLE_OK"; then
      echo "[$(date)] 再開セッションで MIDDLE_OK 確認 — 完走" >> "$LOG_FILE"
      rm -f "$(dirname "$LOG_FILE")/INCOMPLETE-$(TZ=Asia/Tokyo date +%F)"
    fi
  fi
fi

# 無言失敗ガード（スクリプト層）：セッション内のAIが送る通知は、セッションが死ぬと飛ばない。
# exitが非0のまま終わったら、このシェルから必ず1通出す。
if (( RC != 0 )); then
  notify "🔴 *MIDDLE STUDIES II（$(TZ=Asia/Tokyo date +%F)）を完走できませんでした*
原因：claude が exit $RC で終了（$attempt 回試行）
ログ末尾：
\`\`\`$(tail -n 6 "$LOG_FILE")\`\`\`
手動再実行：bash ~/projects/middle-studies/scripts/daily.sh"
fi

rm -f "$OUT_TMP"
echo "[$(date)] === done (exit $RC, attempts $attempt) ===" >> "$LOG_FILE"
