#!/usr/bin/env python3
"""
Telegram bulk message sender for stock-demo.
Kirim pesan ke Telegram channel/grup lewat bot token.

Env yang dipakai (jangan hardcode token/chat_id di sini):
  TELEGRAM_TOKEN    -> bot token (hanya dibaca dari env, bukan dari chat)
  TELEGRAM_CHAT_ID  -> chat id / channel id / username (@channel)

Pemakaian:
  cp .env.example .env   (isi TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
  python3 send_bulk.py "pesan 1"
  python3 send_bulk.py "pesan 1" "pesan 2" "pesan 3"
  python3 send_bulk.py --file notes.txt
"""

import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

# ✅ Ambil dari env — jANGAN hardcode token/chat_id di sini
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
BOT_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


def send_message(text: str) -> dict | None:
    """Kirim 1 pesan ke Telegram. Return JSON response atau None."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️  TELEGRAM_TOKEN / TELEGRAM_CHAT_ID belum di-set di env.", file=sys.stderr)
        return None

    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    url = BOT_API + "/sendMessage"
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"   ⚠️  Error: {e}", file=sys.stderr)
    return None


def load_messages(path: str | None) -> list[str]:
    """Baca pesan dari file, satu per baris (komentar # di-ignore)."""
    if path is None:
        return []
    msgs = []
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        msgs.append(line)
    return msgs


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    if args[0] == "--file":
        if len(args) < 2:
            print("butuh --file PATH", file=sys.stderr)
            sys.exit(1)
        messages = load_messages(args[1])
    else:
        messages = args

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️  Telegram not configured (set TELEGRAM_TOKEN / TELEGRAM_CHAT_ID).", file=sys.stderr)
        sys.exit(1)

    print(f"📤 Sending {len(messages)} message(s) to chat_id={TELEGRAM_CHAT_ID}...")
    ok = 0
    for i, text in enumerate(messages, 1):
        resp = send_message(text)
        if resp and resp.get("ok"):
            print(f"  ✅ [{i}/{len(messages)}] msg_id={resp.get('result', {}).get('message_id')}")
            ok += 1
        else:
            print(f"  ❌ [{i}/{len(messages)}] gagal", file=sys.stderr)

    print(f"\n✅ {ok}/{len(messages)} sent.")
    return 0 if ok == len(messages) else 1


if __name__ == "__main__":
    sys.exit(main())
