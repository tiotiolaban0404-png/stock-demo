#!/usr/bin/env python3
"""
Kirim notifikasi demo Stock Analysis ke Telegram channel.
"""
import os
import sys
import json
import urllib.request
import urllib.parse

def send_telegram_message(token, chat_id, text):
    """Kirim pesan ke Telegram channel."""
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    data = urllib.parse.urlencode(payload).encode()
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())

def main():
    token = os.environ.get('TELEGRAM_TOKEN', '')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')

    message = (
        '🚀 STOCK DEMO ANALISIS TERENERBACKUP!\n'
        '📊 Project: sahom-bot — analisis teknikal multi-emiten\n'
        '📊 Deck: EMA20/EMA50, RSI14, MACD, Fibonacci, BUY/SELL/WAIT\n\n'
        '✅ 8 emiten: BBCA, BMRI, TLKM, ASII, AAPL, MSFT, NVDA, GOOGL\n'
        '✅ 4 Indonesia + 4 Wall Street\n'
        '✅ Gap data handling: fallback nama BBRI/BBCA (jika data kosong)\n'
        '✅ Indikator lengkap + risk target\n\n'
        '📖 Demo:\n'
        '  python program_saham.py daftar --file demo/watchlist_demo.txt\n\n'
        '📦 Repo GitHub:\n'
        'https://github.com/tiotiolaban0404-png/stock-demo\n\n'
        '⚠️ Disclaimer: hanya indikator teknikal, bukan rekomendasi investasi.'
    )

    result = send_telegram_message(token, chat_id, message)

    if result.get('ok'):
        msg_id = result.get('result', {}).get('message_id')
        print(f'✅ Promosi Telegram terkirim! (message_id: {msg_id})')
        return 0
    else:
        print(f'❌ Gagal: {result}')
        return 1

if __name__ == '__main__':
    sys.exit(main())
