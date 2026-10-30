# 🚀 Demo Stock Analysis — Threads / Tweets (Siap Paste)

Repo: https://github.com/tiotiolaban0404-png/stock-demo  
Language: Indonesian

> ⚠️ Ganti token gambar/link sesuai kondisi kamu.  
> Upload screenshot: `assets/screenshots/01_list_view.png`, `02_signal.png`, `03_output.png`.

---

## Thread 1 — "Build technical analysis for stocks with Python"

**Tweet 1/3**
📈 Build technical analysis for Indonesian stocks + Wall Street with Python.
Multi-emiten: EMA20/EMA50, RSI14, MACD, Fibonacci, BUY/SELL/WAIT.
Demo + source code:
https://github.com/tiotiolaban0404-png/stock-demo

**Tweet 2/3**
Gap data handled. BNBR, BWPT → fallback NAMA BBRI/BBCA, indikator None, signal WAIT.
Tidak crash, tidak angka palsu. Output bersih.
https://github.com/tiotiolaban0404-png/stock-demo

**Tweet 3/3**
Full demo: 8 emiten, data real, run script ready.
Star repo kalau kamu pakai Python + yfinance + pandas:
https://github.com/tiotiolaban0404-png/stock-demo

---

## Thread 2 — "How I handle missing stock data"

**Tweet 1/3**
Saat Yahoo Financials tidak punya histori harga untuk ticker tertentu (BNBR, BWPT)... gap data belum bisa jadi masalah.
https://github.com/tiotiolaban0404-png/stock-demo

**Tweet 2/3**
Rulan logika sederhana:
- Cek df is None / df.empty / len(df) < 50
- Kalau gap → status = data_tidak_tersedia, indikator = None, signal = WAIT
- Nama fallback pakai NAMA_MANUAL (BBRI/BBCA)
- Jangan print angka palsu
https://github.com/tiotiolaban0404-png/stock-demo

**Tweet 3/3**
Hasil: pipeline berjalan utuh, exit 0, tanpa error.
Demo: https://github.com/tiotiolaban0404-png/stock-demo

---

## Single tweet (rekomendasi screenshot)

📈 Demo analisis teknikal saham + Wall Street, Python, yfinance + pandas.
- 8 emiten (4 Indonesia + 4 Wall Street)
- EMA20/EMA50, RSI14, MACD, Fibonacci
- Fallback NAMA BBRI/BBCA saat gap data
- Signal BUY/SELL/WAIT + risk target

Star: https://github.com/tiotiolaban0404-png/stock-demo
