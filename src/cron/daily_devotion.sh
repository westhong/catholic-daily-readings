#!/bin/bash
set -euo pipefail

SESSION="${1:-}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
ENV_FILE="${HERMES_ENV_FILE:-/home/jarvis/.hermes/.env}"
DEFAULT_CHAT_ID="-1003336338866"
DEFAULT_TOPIC_ID="17"

read_env_value() {
  local key="$1"
  python3 - "$ENV_FILE" "$key" <<'PY'
from pathlib import Path
import sys

env_file = Path(sys.argv[1])
key = sys.argv[2]
if not env_file.exists():
    print("")
    raise SystemExit(0)
for line in env_file.read_text().splitlines():
    if not line or line.lstrip().startswith('#') or '=' not in line:
        continue
    k, v = line.split('=', 1)
    if k.strip() == key:
        print(v.strip())
        raise SystemExit(0)
print("")
PY
}

BOT_TOKEN="$(read_env_value TELEGRAM_BOT_TOKEN)"
CHAT_ID="$(read_env_value CATHOLIC_CHAT_ID)"
TOPIC_ID="$(read_env_value CATHOLIC_TOPIC_ID)"
CHAT_ID="${CHAT_ID:-$DEFAULT_CHAT_ID}"
TOPIC_ID="${TOPIC_ID:-$DEFAULT_TOPIC_ID}"

if [[ -z "$SESSION" ]]; then
  echo "Usage: $0 [office|lauds|daytime|vespers|compline]" >&2
  exit 1
fi

if [[ -z "$BOT_TOKEN" ]]; then
  echo "TELEGRAM_BOT_TOKEN not found in $ENV_FILE" >&2
  exit 1
fi

TODAY=$(TZ="America/Edmonton" date +"%Y年%-m月%-d日")
WEEKDAY=$(TZ="America/Edmonton" date +"%A")

send_text() {
  local payload response
  payload=$(python3 - "$CHAT_ID" "$TOPIC_ID" "$1" <<'PY'
import json
import sys

print(json.dumps({
    'chat_id': sys.argv[1],
    'message_thread_id': int(sys.argv[2]),
    'text': sys.argv[3],
}, ensure_ascii=False))
PY
)
  response=$(curl -fsS -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
    -H "Content-Type: application/json" \
    -d "$payload") || return 1
  printf '%s' "$response" | grep -q '"ok":true' || {
    echo "Telegram send failed: $response" >&2
    return 1
  }
}

if command -v python3 >/dev/null 2>&1; then
  eval "$(python3 "$SCRIPT_DIR/fetch_daily_reading.py" "$SESSION")"
else
  REF="Psalm 23:1"
  CHINESE="耶和華是我的牧者，我必不致缺乏。"
  ENGLISH="The Lord is my shepherd; I shall not want."
fi

case "$SESSION" in
  lauds)
    TEXT="🌅 晨禱 Morning Prayer — Lauds

📅 ${TODAY} ${WEEKDAY}

━━━━━━━━━━━━━━━

📖 今日經文
${REF}

『${CHINESE}』

${ENGLISH}

━━━━━━━━━━━━━━━

🙏 今日靈修主題
全心倚靠上主
Trust in the Lord with all your heart

願祢在這一天開始時，將心交托給天主。祂的話語是腳前的燈，是路上的光。

願主的平安與您同在。✝️"
    ;;
  daytime)
    TEXT="☀️ 日間祈禱 Daytime Prayer

📅 ${TODAY} ${WEEKDAY}

━━━━━━━━━━━━━━━

📖 日間經文
${REF}

『${CHINESE}』

${ENGLISH}

━━━━━━━━━━━━━━━

🙏 中午默想邀請
在忙碌的一天中，停下來一分鐘，將心向天主敞開。

願主引導您今天的每一步。✝️"
    ;;
  vespers)
    TEXT="🌇 晚禱 Evening Prayer — Vespers

📅 ${TODAY} ${WEEKDAY}

━━━━━━━━━━━━━━━

📖 晚禱經文
${REF}

『${CHINESE}』

${ENGLISH}

━━━━━━━━━━━━━━━

🙏 晚間反省
回顧今天，在哪裡看見天主的恩典？

感謝今天所有的恩典，大的小的都算。✝️"
    ;;
  compline)
    TEXT="🌙 夜禱 Night Prayer — Compline

📅 ${TODAY} ${WEEKDAY}

━━━━━━━━━━━━━━━

📖 夜禱經文
${REF}

『${CHINESE}』

${ENGLISH}

━━━━━━━━━━━━━━━

🙏 安息祈禱
將這一天交托給天主，安心入睡。

晚安，願天主守護您的安眠。✝️
🌙 Nunc Dimittis"
    ;;
  office)
    TEXT="📖 誦讀日課 Office of Readings

📅 ${TODAY} ${WEEKDAY}

━━━━━━━━━━━━━━━

📖 讀經經文
${REF}

『${CHINESE}』

${ENGLISH}

━━━━━━━━━━━━━━━

🙏 靈修思考
默想天主的話語，使心靈得滋養。

願主藉祂的聖言照亮您的道路。✝️"
    ;;
  *)
    echo "Usage: $0 [office|lauds|daytime|vespers|compline]" >&2
    exit 1
    ;;
esac

send_text "$TEXT"
echo "✅ ${SESSION} devotion sent from Hermes at $(date)"
