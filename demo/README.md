# Stock Demo

Demo sederhana dari `sahom-bot` (analisis teknikal saham).
Contoh 8 emiten (4 Indonesia + 4 Wall Street) dengan data riil.

## Cepat mulai

```bash
chmod +x demo/run_demo.sh
./demo/run_demo.sh
```

Atau:

```bash
python3 program_saham.py daftar --file demo/watchlist_demo.txt
```

## Slot Python

Gunakan `/usr/bin/python3` (sistem) yang bawaan `pandas`, `pandas_ta`, `colorama`, `requests`.
Cegah: `saham_env` venv MISSING `colorama` -> jangan dipakai.

## Isi folder demo

| Berkas | Isi |
| --- | --- |
| `watchlist_demo.txt` | 8 kode emiten |
| `config.ini.example` | template konfigurasi (ubah token/chat_id) |
| `run_demo.sh` | script jalankan |
| `example_output.txt` | contoh hasil runs |
| `README.md` | dokumentasi ini |

## Telegram Group Configuration

Script untuk kirim notifikasi ke Telegram group (stockbit, ajaib, pro livin, dst).

### Setup

1. Salin config template:
   ```bash
   cp demo/config.ini.example demo/config.ini
   ```

2. Keluarkan token bot dari @BotFather:
   ```bash
   export TELEGRAM_TOKEN="86565..._p9M"
   ```

3. Tambah bot ke setiap grup, lalu dapatkan chat_id dari:
   `https://api.telegram.org/bot<TOKEN>/getUpdates`

4. Isi group chat IDs (comma-separated):
   ```bash
   export TELEGRAM_GROUP_CHAT_IDS="7401634640,group_stockbit_id,group_ajaib_id,group_prolivin_id"
   ```

5. Update config:
   ```bash
   python3 scripts/update_telegram_config.py
   ```

### Scripts

| File | Deskripsi |
| --- | --- |
| `scripts/update_telegram_config.py` | Update config.ini dengan token + group chat IDs |
| `scripts/test_telegram_chat.py` | Verifikasi chat ID (private + group) |
| `scripts/update_crontab.py` | Generate crontab command untuk scheduled alerts |
| `send_bulk.py` | Kirim pesan ke banyak chat_id sekaligus |

## Catatan

- `TELEGRAM_TOKEN`/`TELEGRAM_CHAT_ID` kosong -> notifikasi Telegram tidak terkirim (aman).
- Sinyal cuma indikator teknikal (tidak rekomendasi investasi).
- Bot harus admin di grup, dan privacy mode di @BotFather harus dimatikan untuk menerima pesan dari grup.
