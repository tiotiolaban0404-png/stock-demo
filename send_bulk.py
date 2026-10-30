#!/usr/bin/env python3
"""
Telegram bulk message sender for stock-demo.
Kirim pesan ke Telegram channel/grup lewat bot token.

Env yang dipakai (jangan hardcode token/chat_id di sini):
  TELEGRAM_TOKEN           -> bot token (hanya dibaca dari env, bukan dari chat)
  TELEGRAM_GROUP_CHAT_IDS  -> chat id / channel id / username (@channel) (env)
  TELEGRAM_ALL_DESTINATIONS-> comma-separated chat ids (env override)

Pemakaian:
  cp demo/config.ini.example demo/config.ini
  TELEGRAM_TOKEN=xxx TELEGRAM_GROUP_CHAT_IDS="7401634640,group1_id,group2_id" python3 send_bulk.py "pesan 1"
  python3 send_bulk.py "pesan 1" "pesan 2" "pesan 3"
  python3 send_bulk.py --file notes.txt
"""
import configparser
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "demo" / "config.ini"

def load_destinations():
    """Baca destinaris Telegram dari config.ini + env (prioritas: env > config)."""
    destinations = set()

    # Env override
    all_dest = os.getenv("TELEGRAM_ALL_DESTINATIONS", "").strip()
    if all_dest:
        destinations.update([d.strip() for d in all_dest.split(",") if d.strip()])
        return sorted(destinations)

    # Config file
    if CONFIG_FILE.exists():
        cp = configparser.ConfigParser()
        cp.read(CONFIG_FILE)
        if cp.has_option("telegram", "group_chat_ids"):
            raw = cp.get("telegram", "group_chat_ids").strip()
            if raw:
                destinations.update([d.strip() for d in raw.split(",") if d.strip()])
        if cp.has_option("telegram", "chat_id"):
            raw = cp.get("telegram", "chat_id").strip()
            if raw:
                destinations.add(raw)

    return sorted(destinations)

def send_to_chat(token, chat_id, text, timeout=15):
    """Kirim 1 pesan ke 1 chat id. Return response JSON atau None."""
    if not token or not chat_id:
        return None
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}

def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    # Baca pesan dari --file atau argumen
    if args[0] == "--file":
        if len(args) < 2:
            print("butuh --file PATH", file=sys.stderr)
            sys.exit(1)
        msg_file = args[1]
        messages = []
        for raw in Path(msg_file).read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            messages.append(line)
    else:
        messages = args

    token = os.getenv("TELEGRAM_TOKEN", "").strip()
    destinations = load_destinations()

    if not token:
        print("❌ TELEGRAM_TOKEN belum di-set di env.", file=sys.stderr)
        sys.exit(1)
    if not destinations:
        print("❌ Tidak ada chat_id yang dikonfigurasi.", file=sys.stderr)
        print("   Set TELEGRAM_GROUP_CHAT_IDS atau edit demo/config.ini.example", file=sys.stderr)
        sys.exit(1)

    print(f"📤 Sending {len(messages)} message(s) to {len(destinations)} chat_id(s)...")
    total_ok = 0
    for i, text in enumerate(messages, 1):
        ok_count = 0
        for dest in destinations:
            resp = send_to_chat(token, dest, text)
            if resp and resp.get("ok"):
                msg_id = resp.get("result", {}).get("message_id")
                print(f"  ✅ [{i}/{len(messages)}] chat_id={dest[:10]}... msg_id={msg_id}")
                ok_count += 1
            else:
                detail = resp.get("description", "unknown") if resp else "error"
                print(f"  ❌ [{i}/{len(messages)}] chat_id={dest[:10]}... gagal: {detail}", file=sys.stderr)
        total_ok += ok_count

    print(f"\n✅ {total_ok}/{len(messages) * len(destinations)} sent.")
    return 0 if total_ok == len(messages) * len(destinations) else 1

if __name__ == "__main__":
    sys.exit(main())
