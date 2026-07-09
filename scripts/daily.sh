#!/bin/zsh
# MIDDLE STUDIES 日次制作ジョブ（launchd: com.monaka.middle-study が毎日 2:00 JST に起動）
# Claude Code をヘッドレスで起動し、スキル blender-middle-study の手順で1作品を制作・公開する。

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
export LANG="ja_JP.UTF-8"

CEO_DIR="/Users/shitoryota/Library/CloudStorage/GoogleDrive-ryota4100221@gmail.com/マイドライブ/monaka design./CEO"
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

cd "$CEO_DIR" || exit 1

echo "[$(date)] === MIDDLE STUDY daily start ===" >> "$LOG_FILE"
/opt/homebrew/bin/claude -p "/blender-middle-study daily" \
  --dangerously-skip-permissions \
  >> "$LOG_FILE" 2>&1
echo "[$(date)] === done (exit $?) ===" >> "$LOG_FILE"
