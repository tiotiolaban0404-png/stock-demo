#!/usr/bin/env python3
"""
Update crontab to include Telegram group chat IDs for stock-demo.

Env vars:
  TELEGRAM_TOKEN           - bot token from @BotFather
  TELEGRAM_GROUP_CHAT_IDS  - comma-separated chat IDs (private + groups)

Usage:
  TELEGRAM_TOKEN=xxx TELEGRAM_GROUP_CHAT_IDS="7401634640,123456,789012" python3 scripts/update_crontab.py
"""
import os
import sys

def update_crontab():
    token = os.getenv("TELEGRAM_TOKEN", "").strip()
    group_ids = os.getenv("TELEGRAM_GROUP_CHAT_IDS", "").strip()

    if not token:
        print("❌ TELEGRAM_TOKEN not set in env.", file=sys.stderr)
        sys.exit(1)

    # Build the crontab command
    cmd = f'cd /home/ridho/Downloads/stock-demo && TELEGRAM_TOKEN="{token}"'
    if group_ids:
        cmd += f' TELEGRAM_GROUP_CHAT_IDS="{group_ids}"'
    cmd += ' /usr/bin/python3 send_bulk.py "Demo Stock Analysis: see https://github.com/tiotiolaban0404-png/stock-demo"'

    print(f"📝 Generated crontab command:")
    print(f"   {cmd}")
    print()
    print("To install:")
    print(f"   (crontab -l 2>/dev/null; echo '{cmd}') | crontab -")
    return 0

if __name__ == "__main__":
    sys.exit(update_crontab())
