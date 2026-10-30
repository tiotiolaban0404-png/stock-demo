#!/usr/bin/env python3
"""
Update Telegram configuration for stock-demo.
Add multiple Telegram chat IDs (private + groups) for distribution.

Env vars (no hardcoded secrets):
  TELEGRAM_TOKEN    - bot token from @BotFather
  TELEGRAM_GROUP_CHAT_IDS - comma-separated chat IDs (private + groups)

Usage:
  cp demo/config.ini.example demo/config.ini
  TELEGRAM_TOKEN=xxx TELEGRAM_GROUP_CHAT_IDS="7401634640,group_stockbit_id,group_ajaib_id" python3 scripts/update_telegram_config.py
"""
import configparser
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "demo" / "config.ini"

GROUP_CHAT_IDS_ENV = "TELEGRAM_GROUP_CHAT_IDS"

def load_config(path: Path) -> configparser.ConfigParser:
    cp = configparser.ConfigParser()
    if path.exists():
        cp.read(path)
    return cp

def save_config(cp: configparser.ConfigParser, path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        cp.write(f, space_around_delimiters=False)

def main():
    if not CONFIG_FILE.exists():
        print(f"❌ config.ini not found at {CONFIG_FILE}")
        sys.exit(1)

    cp = load_config(CONFIG_FILE)

    # Get token and chat IDs from env
    token = os.getenv("TELEGRAM_TOKEN", "").strip()
    group_ids_str = os.getenv(GROUP_CHAT_IDS_ENV, "").strip()

    if not token:
        print("⚠️  TELEGRAM_TOKEN not set in env. Skipping token update.")
    else:
        cp.set("telegram", "token", token)
        print(f"✅ Telegram token updated ({len(token)} chars)")

    # Parse group chat IDs (comma-separated)
    group_ids = [gid.strip() for gid in group_ids_str.split(",") if gid.strip()] if group_ids_str else []
    if group_ids:
        cp.set("telegram", "group_chat_ids", ",".join(group_ids))
        print(f"✅ Group chat IDs configured: {len(group_ids)} group(s)")
    else:
        cp.remove_option("telegram", "group_chat_ids")
        print("⚠️  No group chat IDs set in env. Skipping group config.")

    save_config(cp, CONFIG_FILE)
    print(f"\n✅ Config saved to {CONFIG_FILE}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
