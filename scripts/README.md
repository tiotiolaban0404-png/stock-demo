# Telegram Scripts

Scripts for Telegram group distribution and configuration.

## Files

| File | Description |
| --- | --- |
| `scripts/update_telegram_config.py` | Update `demo/config.ini` with Telegram token + group chat IDs |
| `scripts/test_telegram_chat.py` | Verify chat IDs work (private + groups) |
| `scripts/update_crontab.py` | Generate crontab command for scheduled Telegram alerts |

## Usage

### 1. Setup config
```bash
cp demo/config.ini.example demo/config.ini
```

### 2. Set Telegram credentials (env only - no secrets in repo)
```bash
export TELEGRAM_TOKEN="86565..._p9M"
export TELEGRAM_GROUP_CHAT_IDS="7401634640,group_stockbit,group_ajaib,group_prolivin"
```

### 3. Update config
```bash
python3 scripts/update_telegram_config.py
```

### 4. Test chat IDs
```bash
python3 scripts/test_telegram_chat.py
```

### 5. Update crontab
```bash
python3 scripts/update_crontab.py
```

### 6. Send bulk message
```bash
python3 send_bulk.py "Demo Stock Analysis: https://github.com/tiotiolaban0404-png/stock-demo"
```
