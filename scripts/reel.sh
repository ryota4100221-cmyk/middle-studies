#!/bin/zsh
# MIDDLE STUDIES REEL 制作ジョブ（launchd: com.monaka.reel が 毎晩23:00 JST に起動／23:50 がキャッチアップ）
# Claude Code をヘッドレスで起動し、reel/SKILL.md の手順で15秒のモーショングラフィックスを1本作って公開する。
# 2026-09-29 新設（Ryota指示）。骨格は scripts/daily.sh（MIDDLE STUDIES II）と同じ＝踏んだ罠の対策をそのまま持つ。
#
# 🔴 main(23:00) と catchup(23:50) は日付境界の同じ側に置く（ログは起動時の暦日で開く＝跨ぐと二重実行）。
# 🔴 launchd は Google Drive 配下を読めない（TCC）。手順は ~/projects/middle-studies/reel/SKILL.md に置く。

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
export LANG="ja_JP.UTF-8"

CLAUDE_BIN=""
for _c in "$(command -v claude 2>/dev/null || true)" \
          /opt/homebrew/bin/claude \
          "$HOME/.local/bin/claude" \
          /opt/homebrew/lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe; do
  if [ -n "$_c" ] && [ -x "$_c" ]; then CLAUDE_BIN="$_c"; break; fi
done
[ -n "$CLAUDE_BIN" ] || CLAUDE_BIN="/opt/homebrew/bin/claude"

# Webhook はリポジトリの外から読む（public リポに URL を書くと push が止まる）
[ -f "$HOME/.config/monaka/slack.env" ] && source "$HOME/.config/monaka/slack.env"
export SLACK_WEBHOOK="${SLACK_WEBHOOK_SAKUHIN:-}"   # #mona-作品（失敗時だけ）

ROOT="$HOME/projects/middle-studies"
SKILL_MD="$ROOT/reel/SKILL.md"
LOG_DIR="$ROOT/reel/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/$(TZ=Asia/Tokyo date +%F).log"

notify() {
  [ -z "$SLACK_WEBHOOK" ] && { echo "[$(date)] SLACK_WEBHOOK empty — notify skipped" >> "$LOG_FILE"; return 1; }
  local payload
  payload=$(printf '%s' "$1" | /usr/bin/python3 -c 'import json,sys; print(json.dumps({"text": sys.stdin.read()}))')
  curl -sS -m 15 -X POST -H 'Content-type: application/json' --data "$payload" "$SLACK_WEBHOOK" >/dev/null 2>&1
}
# 合図は「最後の空でない行が、ちょうどその語だけ」（説明文の中の語を拾わない＝II 007 の事故）
last_is() {
  [[ "$(grep -v '^[[:space:]]*$' "$2" | tail -1 | tr -d '[:space:]*`')" == "$1" ]]
}

if [[ -z "${REEL_FORCE:-}" ]] && grep -q "=== done (exit 0" "$LOG_FILE" 2>/dev/null; then
  echo "[$(date)] already succeeded today — skip (catch-up slot)" >> "$LOG_FILE"
  exit 0
fi
LOCK="/tmp/middle-reel.lock"
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "[$(date)] already running, skip" >> "$LOG_FILE"
  exit 0
fi
trap 'rmdir "$LOCK"' EXIT
if ! head -c 1 "$SKILL_MD" >/dev/null 2>&1; then
  echo "[$(date)] ABORT: skill file unreadable: $SKILL_MD" >> "$LOG_FILE"
  notify "🔴 *MIDDLE STUDIES REEL（$(TZ=Asia/Tokyo date +%F)）*：手順書が読めない（$SKILL_MD）"
  exit 1
fi

cd "$ROOT" || exit 1
git pull -q --ff-only >> "$LOG_FILE" 2>&1
git -C "$HOME/projects/middle-studies-reel" pull -q --ff-only >> "$LOG_FILE" 2>&1

echo "[$(date)] === REEL daily start ===" >> "$LOG_FILE"
OUT_TMP="$(mktemp /tmp/middle-reel-out.XXXXXX)"
PROMPT="まず「$SKILL_MD」を読み、その手順どおりに今日の MIDDLE STUDIES REEL を1本制作・公開して。${REEL_FORCE:+（工程0の「今日の分は済んでいるか」は飛ばしてよい）} 🔴 これは無人の夜間実行で、人は見ていない。質問せず、レンダーは同期で待ち、ターンを途中で終えない。止めるときは SKILL.md 工程7のとおり Slack へ通知してから終わる。完走したときだけ、最後の行に REEL_OK とだけ書く。"

MAX_ATTEMPTS=6
attempt=1
RC=1
while (( attempt <= MAX_ATTEMPTS )); do
  echo "[$(date)] --- attempt $attempt/$MAX_ATTEMPTS ---" >> "$LOG_FILE"
  caffeinate -i "$CLAUDE_BIN" -p "$PROMPT" --model claude-opus-5-5 --dangerously-skip-permissions > "$OUT_TMP" 2>&1
  RC=$?
  cat "$OUT_TMP" >> "$LOG_FILE"

  # 成功の判定を失敗の判定より先に（本文中の "limit" 等への誤爆で2本目を作らせない＝daily.sh 2026-09-10）
  if (( RC == 0 )) && last_is REEL_OK "$OUT_TMP"; then
    echo "[$(date)] REEL_OK 確認 — 完走" >> "$LOG_FILE"
    break
  fi
  if grep -qiE "You.?ve hit your [a-z]+ limit|usage limit reached|rate limit exceeded" "$OUT_TMP" \
     || tail -n 3 "$OUT_TMP" | grep -qiE "session limit|usage limit|rate limit"; then
    echo "[$(date)] usage limit hit — sleeping 60min then retrying" >> "$LOG_FILE"
    sleep 3600; (( attempt++ )); continue
  fi
  if (( RC != 0 )) && grep -qiE "internal error|EPERM|timed out|timeout|ECONNRESET|ETIMEDOUT|ENOTFOUND|network error|fetch failed|connection closed|connection reset|overloaded" "$OUT_TMP"; then
    echo "[$(date)] transient error — sleeping 5min then retrying" >> "$LOG_FILE"
    sleep 300; (( attempt++ )); continue
  fi
  # exit 0 でも完走の証拠が無ければ失敗扱い（「終わったつもり」を通さない）
  if (( RC == 0 )); then
    echo "[$(date)] exit 0 だが REEL_OK が無い" >> "$LOG_FILE"
    RC=9
  fi
  break
done

# 無言失敗ガード：セッションが死ぬとAIの通知は飛ばない。シェルから必ず1通出す
if (( RC != 0 )); then
  notify "🔴 *MIDDLE STUDIES REEL（$(TZ=Asia/Tokyo date +%F)）を完走できませんでした*
原因：exit $RC（$attempt 回試行）
ログ末尾：
\`\`\`$(tail -n 6 "$LOG_FILE")\`\`\`
手動再実行：REEL_FORCE=1 zsh ~/projects/middle-studies/scripts/reel.sh"
fi

rm -f "$OUT_TMP"
echo "[$(date)] === done (exit $RC, attempts $attempt) ===" >> "$LOG_FILE"
