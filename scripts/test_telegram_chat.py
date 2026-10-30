#!/usr/bin/env python3
"""
Test Telegram chat IDs for stock-demo.
Verifies that the bot can reach each configured chat ID.

Env vars:
  TELEGRAM_TOKEN    - bot token from @BotFather
  TELEGRAM_GROUP_CHAT_IDS - comma-separated chat IDs (private + groups)

Usage:
  TELEGRAM_TOKEN=xxx TELEGRAM_GROUP_CHAT_IDS="7401634640,123456,789012" python3 scripts/test_telegram_chat.py
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "demo" / "config.ini"

def load_chat_ids():
    """Load chat IDs from config.ini or env."""
    chat_ids = []

    # Try config.ini first
    if CONFIG_FILE.exists():
        import configparser
        cp = configparser.ConfigParser()
        cp.read(CONFIG_FILE)
        if cp.has_option("telegram", "group_chat_ids"):
            raw = cp.get("telegram", "group_chat_ids").strip()
            if raw:
                chat_ids.extend([gid.strip() for gid in raw.split(",") if gid.strip()])

    # Also check private chat_id in config
    if CONFIG_FILE.exists():
        import configparser
        cp = configparser.ConfigParser()
        cp.read(CONFIG_FILE)
        if cp.has_option("telegram", "chat_id"):
            raw = cp.get("telegram", "chat_id").strip()
            if raw:
                chat_ids.append(raw)

    # Override with env
    env_ids = os.getenv("TELEGRAM_GROUP_CHAT_IDS", "").strip()
    if env_ids:
        chat_ids = [gid.strip() for gid in env_ids.split(",") if gid.strip()]

    return chat_ids

def test_chat_id(token, chat_id, timeout=10):
    """Test a single chat ID via getUpdates (for private) or sendMessage."""
    results = {"chat_id": chat_id, "ok": False, "status": "unknown", "details": ""}

    if not token:
        results["details"] = "No token"
        return results

    # Try sendMessage - works for private chats and groups
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": "🔧 Test ping dari stock-demo"}
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp_data = json.loads(resp.read().decode())
            if resp_data.get("ok"):
                results["ok"] = True
                results["status"] = "success"
                results["details"] = f"message_id={resp_data.get('result', {}).get('message_id')}"
            else:
                results["ok"] = False
                results["status"] = "failed"
                results["details"] = str(resp_data.get("description", "unknown"))
    except Exception as e:
        results["ok"] = False
        results["status"] = "error"
        results["details"] = str(e)

    return results

def main():
    token = os.getenv("TELEGRAM_TOKEN", "").strip()
    chat_ids = load_chat_ids()

    if not token:
        print("❌ TELEGRAM_TOKEN not set in env.")
        sys.exit(1)

    if not chat_ids:
        print("⚠️  No chat IDs configured. Set TELEGRAM_GROUP_CHAT_IDS env var or add to config.ini.")
        sys.exit(1)

    print(f"🔍 Testing {len(chat_ids)} chat ID(s) with Telegram bot...")
    print("=" * 60)

    results = []
    for cid in chat_ids:
        print(f"\n📡 Testing chat_id={cid} ...")
        result = test_chat_id(token, cid)
        results.append(result)
        status_icon = "✅" if result["ok"] else "❌"
        print(f"   {status_icon} {result['status'].upper()} - {result['details']}")

    print("\n" + "=" * 60)
    ok_count = sum(1 for r in results if r["ok"])
    print(f"📊 Result: {ok_count}/{len(results)} chat IDs valid.")

    if ok_count == len(results):
        print("✅ All chat IDs verified. Ready to send messages.")
    else:
        print("⚠️  Some chat IDs failed. Check your configuration.")
        print("   For private chats: the bot must be added to the chat first.")
        print("   For groups: the bot must be added to the group AND have admin rights + be unblocked.")

    return 0 if ok_count == len(results) else 1

if __name__ == "__main__":
    sys.exit(main())
