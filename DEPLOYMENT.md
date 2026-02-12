# 🚀 Deployment Guide — Render Web Service

## Prerequisites

1. Push code to GitHub
2. Have Google OAuth credentials ready
3. Have MongoDB URI ready

---

## Environment Variables

Set in **Render Dashboard → Environment**:

| Variable | Description |
|----------|-------------|
| `API_ID` | Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | Telegram API Hash |
| `BOT_TOKEN` | Bot token from [@BotFather](https://t.me/BotFather) |
| `MONGO_URI` | MongoDB Atlas connection string |
| `ADMIN_IDS` | Telegram user IDs (comma-separated). First = super admin |
| `GOOGLE_OAUTH_TOKEN` | Base64-encoded OAuth token (see below) |

### Generate `GOOGLE_OAUTH_TOKEN`

Run locally after OAuth setup:
```bash
python3 -c "import pickle, base64; print(base64.b64encode(open('token.pickle','rb').read()).decode())"
```

---

## Deploy Steps

1. **Push to GitHub**
   ```bash
   git add . && git commit -m "Deploy" && git push
   ```

2. **Create Render Web Service**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - **New +** → **Web Service** → Connect repo
   - Settings auto-detected from `render.yaml`

3. **Add Environment Variables** (see table above)

4. **Deploy!** — Monitor logs for:
   ```
   🌐 Starting Flask web server...
   🤖 Starting Telegram bot in main thread...
   ✅ Bot started as @YourBot
   ```

---

## Endpoints

| Path | Description |
|------|-------------|
| `/` | Bot status (JSON) |
| `/health` | Health check for Render |

---

## Architecture

```
┌──────────────────────────────┐
│         Render Web Service   │
├──────────────┬───────────────┤
│  Flask       │  Pyrogram Bot │
│  (daemon)    │  (main thread)│
│              │               │
│  /health ◄───┤  /start       │
│  /  ◄────────┤  /stats       │
│              │  /info        │
│              │  Auto-expire  │
│              │  (5 min loop) │
└──────────────┴───────────────┘
         │              │
    Render Health    MongoDB Atlas
    Check (TCP)      (Motor async)
                        │
                 Google Drive API
                   (OAuth 2.0)
```

- **Flask** runs in a daemon thread (health checks only)
- **Bot** runs in the main thread (asyncio event loop)
- **Auto-expire** scheduler runs every 5 min inside the bot
- `Procfile`: `web: python server.py`

---

## Monitoring

After deployment, use these bot commands to monitor:

| Command | Description |
|---------|-------------|
| `/stats` | Activity analytics (daily/weekly/monthly) |
| `/info` | System health (uptime, DB status, counts) |

Both accessible only to admins (`/info` = super admin only).
