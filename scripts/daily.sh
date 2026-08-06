#!/bin/zsh
# MIDDLE STUDIES 日次制作ジョブ（launchd: com.monaka.middle-study が毎日 2:00 JST に起動）
# Claude Code をヘッドレスで起動し、スキル blender-middle-study の手順で1作品を制作・公開する。
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
if grep -q "=== done (exit 0" "$LOG_FILE" 2>/dev/null; then
  echo "[$(date)] already succeeded today — skip (catch-up slot)" >> "$LOG_FILE"
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
  "$CLAUDE_BIN" -p "/blender-middle-study daily" \
    --model claude-opus-5 \
    --dangerously-skip-permissions \
    > "$OUT_TMP" 2>&1
  RC=$?
  cat "$OUT_TMP" >> "$LOG_FILE"

  # スラッシュコマンド解決に失敗した場合は、SKILL.md を直接読ませるプロンプトで即リトライ
  if grep -q "Unknown command" "$OUT_TMP"; then
    echo "[$(date)] slash command unresolved — retrying with direct skill prompt" >> "$LOG_FILE"
    "$CLAUDE_BIN" -p "まず「$SKILL_MD」を読み、そこに書かれたパイプラインに厳密に従って daily 実行（今日のMIDDLE STUDYを1作品制作・公開・記録）を完走して。" \
      --model claude-opus-5 \
      --dangerously-skip-permissions \
      > "$OUT_TMP" 2>&1
    RC=$?
    cat "$OUT_TMP" >> "$LOG_FILE"
  fi

  # 利用上限なら1時間待って再試行（上限リセットを跨ぐまで粘る）
  if grep -qiE "session limit|usage limit|rate limit" "$OUT_TMP"; then
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
  if (( RC == 0 )) && ! tail -8 "$OUT_TMP" | grep -q "MIDDLE_OK"; then
    echo "[$(date)] exit 0 だが完走の証拠（MIDDLE_OK）が無い" >> "$LOG_FILE"
    touch "$(dirname "$LOG_FILE")/INCOMPLETE-$(TZ=Asia/Tokyo date +%F)"
  fi

  break
done

# 無言失敗ガード（スクリプト層）：セッション内のAIが送る通知は、セッションが死ぬと飛ばない。
# exitが非0のまま終わったら、このシェルから必ず1通出す。
if (( RC != 0 )); then
  notify "🔴 *MIDDLE STUDY（$(TZ=Asia/Tokyo date +%F)）を完走できませんでした*
原因：claude が exit $RC で終了（$attempt 回試行）
ログ末尾：
\`\`\`$(tail -n 6 "$LOG_FILE")\`\`\`
手動再実行：bash ~/projects/middle-studies/scripts/daily.sh"
fi

rm -f "$OUT_TMP"
echo "[$(date)] === done (exit $RC, attempts $attempt) ===" >> "$LOG_FILE"
