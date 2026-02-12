# 📂 Google Drive Access Manager Bot

A powerful Telegram bot built with **Pyrogram** to manage Google Drive folder permissions. Grant/revoke access with **timed expiry**, manage roles, bulk import existing permissions, and track activity — all from Telegram.

---

## 🚀 Features

### ➕ Grant Access
- 6-step guided flow: Email → Folder → Role → Duration → Confirm → Execute
- Email validation, duplicate access protection
- Duration options: 1h, 6h, 1d, 7d, **30d (default)**, or Permanent

### ⏰ Timed Access & Auto-Expire
- Set expiry timers on any grant
- Background task auto-revokes expired access every 5 minutes
- Logged as `auto_revoke` with full audit trail

### 📥 Bulk Import
- Scan ALL Drive folders and import existing permissions
- Creates **40-day expiry** for every non-owner permission
- Skips duplicates, shows live progress
- Handles 400+ emails across multiple folders

### 📂 Manage Folders
- Browse folders with **smart numeric sorting** (`[001-050]` → `[051-100]`)
- View users with access per folder
- Change roles (Viewer ↔ Editor) or remove access
- Folder caching with configurable TTL + manual refresh

### ⏰ Expiry Dashboard
- View all active timed grants with time remaining
- **Extend** access (+1h, +6h, +1d, +7d)
- **Revoke Now** — remove access immediately

### 📊 Activity Logs
- Structured log types: `grant`, `remove`, `role_change`, `auto_revoke`, `bulk_import`
- Type-specific icons (➕ 🗑 🔄)
- Soft delete — logs are never permanently lost
- Paginated view (5 per page)

### ⚙️ Settings
- Default access role (Viewer/Editor)
- Page size configuration (3-10 folders per page)
- Notification toggles

### 🔐 Security
- Admin-only access (config + MongoDB)
- Unauthorized users see "Access Denied" with their ID
- All credentials in `.env`, never in code

---

## 🛠 Prerequisites

- Python 3.11+
- MongoDB (Atlas recommended)
- Google Cloud Project with Drive API enabled
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)

---

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

---

## 📁 Project Structure

```
├── bot.py              # Bot core + auto-expire background task
├── server.py           # Flask + Bot (for Render deployment)
├── config.py           # Environment configuration
├── plugins/
│   ├── start.py        # /start, /help, /cancel, /id, main menu
│   ├── grant.py        # 6-step grant flow with timed access
│   ├── manage.py       # Folder permission management
│   ├── expiry.py       # Expiry dashboard + bulk import
│   ├── settings.py     # Bot settings
│   └── logs.py         # Structured activity logs
├── services/
│   ├── database.py     # MongoDB (Motor) — grants, cache, logs
│   └── drive.py        # Google Drive API v3 + folder caching
├── utils/
│   ├── filters.py      # Admin & state filters
│   ├── states.py       # Conversation state constants
│   ├── validators.py   # Email validation
│   └── pagination.py   # Pagination + smart folder sorting
├── requirements.txt
├── Procfile            # Render start command
└── render.yaml         # Render deployment config
```

---

## 🎮 Usage

Send `/start` to the bot:

| Menu | Description |
|------|-------------|
| ➕ Grant Access | Email → Folder → Role → Duration → Confirm |
| 📂 Manage Folders | Browse, change roles, revoke access |
| ⏰ Expiry Dashboard | View/extend/revoke timed grants + bulk import |
| 📊 Access Logs | Structured activity history |
| ⚙️ Settings | Default role, page size, notifications |
| ❓ Help | Command reference |

## 🚀 Deploy to Render

See [DEPLOYMENT.md](DEPLOYMENT.md) for full instructions.

---

## 📊 MongoDB Collections

| Collection | Purpose |
|------------|---------|
| `admins` | Admin user IDs |
| `logs` | Activity audit trail (soft delete) |
| `settings` | Bot configuration |
| `states` | Conversation flow state |
| `cache` | Folder cache with TTL |
| `grants` | Timed access grants with expiry |

---

Built with ❤️ using Pyrogram, MongoDB & Google Drive API
