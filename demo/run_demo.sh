#!/usr/bin/env bash
# run_demo.sh - jalankan demo saham (stock-demo)
set -euo pipefail

cd "$(dirname "$0")/.."

# pakai python3 sistem (colorama/requests/pandas/pandas_ta tersedia)
# Cegah: venv saham_env NGAK punya colorama -> jangan dipakai
export TELEGRAM_TOKEN=""
export TELEGRAM_CHAT_ID=""

# salin config.example -> config.ini (biar enak dijalankan)
cp demo/config.ini.example demo/config.ini

python3 program_saham.py daftar --file demo/watchlist_demo.txt
