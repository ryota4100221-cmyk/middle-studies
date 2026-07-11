#!/bin/zsh
# MIDDLE STUDIES 日次制作ジョブ（launchd: com.monaka.middle-study が毎日 2:00 JST に起動）
# Claude Code をヘッドレスで起動し、スキル blender-middle-study の手順で1作品を制作・公開する。
#
# 注意: launchd起動のプロセスはmacOSのTCC制限でGoogle Drive(CloudStorage)配下を読めない。
# そのためスキル本体は ~/projects/middle-studies/skill/（= ~/.claude/skills/blender-middle-study への
# symlink実体）に置く。CEO/.claude/skills には置かないこと（2026-07-11の障害の根本原因）。

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
export LANG="ja_JP.UTF-8"

CEO_DIR="/Users/shitoryota/Library/CloudStorage/GoogleDrive-ryota4100221@gmail.com/マイドライブ/monaka design./CEO"
SKILL_MD="$HOME/projects/middle-studies/skill/SKILL.md"
LOG_DIR="$HOME/projects/middle-studies/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/$(TZ=Asia/Tokyo date +%F).log"

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
  /opt/homebrew/bin/claude -p "/blender-middle-study daily" \
    --model claude-opus-4-8 \
    --dangerously-skip-permissions \
    > "$OUT_TMP" 2>&1
  RC=$?
  cat "$OUT_TMP" >> "$LOG_FILE"

  # スラッシュコマンド解決に失敗した場合は、SKILL.md を直接読ませるプロンプトで即リトライ
  if grep -q "Unknown command" "$OUT_TMP"; then
    echo "[$(date)] slash command unresolved — retrying with direct skill prompt" >> "$LOG_FILE"
    /opt/homebrew/bin/claude -p "まず「$SKILL_MD」を読み、そこに書かれたパイプラインに厳密に従って daily 実行（今日のMIDDLE STUDYを1作品制作・公開・記録）を完走して。" \
      --model claude-opus-4-8 \
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

  break
done

rm -f "$OUT_TMP"
echo "[$(date)] === done (exit $RC, attempts $attempt) ===" >> "$LOG_FILE"
