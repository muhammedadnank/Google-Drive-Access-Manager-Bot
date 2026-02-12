# 📂 Google Drive Access Manager Bot

A Telegram bot built with **Pyrogram** to manage Google Drive folder permissions. Grant/revoke access, manage roles, and track activity logs — all from Telegram.

## 🚀 Features

- **Grant Access** — Add users to Drive folders as Viewer or Editor
- **Manage Permissions** — View, change roles, or remove users
- **Activity Logs** — Track all admin actions with timestamps
- **Settings** — Default roles, page size, notifications
- **Admin Security** — Restricted to configured Telegram admins

## 🛠 Prerequisites

- Python 3.11+
- MongoDB (Atlas recommended)
- Google Cloud Project with Drive API enabled
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)

## ⚙️ Setup

### 1. Clone & Install
```bash
git clone https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot.git
cd Google-Drive-Access-Manager-Bot
pip install -r requirements.txt
```

### 2. Google Drive API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable **Google Drive API**
3. Create **OAuth 2.0 Client ID** (Desktop app)
4. Download as `credentials.json` in project root
5. Run bot once locally to complete OAuth flow

### 3. Configure
Copy `.env.example` to `.env` and fill in:
```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
MONGO_URI=mongodb+srv://...
ADMIN_IDS=your_telegram_user_id
```

### 4. Run
```bash
python server.py    # With Flask health checks (for deployment)
python bot.py       # Standalone (local development)
```

## 📁 Project Structure

```
├── bot.py              # Bot core (Pyrogram client)
├── server.py           # Flask + Bot (for Render deployment)
├── config.py           # Environment configuration
├── plugins/            # Pyrogram plugin handlers
│   ├── start.py        # /start, /help, /cancel, /id
│   ├── grant.py        # Grant access flow
│   ├── manage.py       # Manage folder permissions
│   ├── settings.py     # Bot settings
│   └── logs.py         # Activity logs
├── services/
│   ├── database.py     # MongoDB (Motor)
│   └── drive.py        # Google Drive API
├── utils/
│   ├── filters.py      # Admin & state filters
│   ├── states.py       # State constants
│   ├── validators.py   # Email validation
│   └── pagination.py   # Inline keyboard pagination
├── requirements.txt
├── Procfile            # Render start command
└── render.yaml         # Render deployment config
```

## 🚀 Deploy to Render

See [DEPLOYMENT.md](DEPLOYMENT.md) for full instructions.

## 🎮 Usage

Send `/start` to the bot:
- **➕ Grant Access** — Email → Folder → Role → Confirm
- **📂 Manage Folders** — Browse permissions, change/revoke
- **📊 Logs** — View activity history
- **⚙️ Settings** — Configure defaults

---
Built with ❤️ using Pyrogram & MongoDB
