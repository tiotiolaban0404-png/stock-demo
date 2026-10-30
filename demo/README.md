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

## Catatan
- `TELEGRAM_TOKEN`/`TELEGRAM_CHAT_ID` kosong -> notifikasi Telegram tidak terkirim (aman).
- Sinyal cuma indikator teknikal (tidak rekomendasi investasi).
