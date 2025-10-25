# .claude/hooks/on-notification-say.sh
#!/usr/bin/env bash
set -euo pipefail

payload="$(cat)"
message=$(echo "$payload" | jq -r '.message')
# Speak it in background (non-blocking)
/usr/bin/say -v Samantha "$message" &