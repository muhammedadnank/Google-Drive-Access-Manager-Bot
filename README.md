# 📂 Google Drive Access Manager Bot

A powerful Telegram bot built with **Pyrogram** to manage Google Drive folder permissions at scale. Multi-email grants, access templates, timed expiry, bulk import, analytics — all from Telegram.

---

## 🚀 Features

### ➕ Grant Access (3 Modes)
| Mode | Description |
|------|-------------|
| 👤 One Email → One Folder | Classic single grant |
| 📂 One Email → Multi Folders | Checkbox-style folder selection |
| 👥 Multi Emails → One Folder | Batch grant with duplicate detection |

- Email validation & duplicate access protection
- Duration: 1h, 6h, 1d, 7d, **30d (default)**, ♾ Permanent
- **Viewers** get expiry timer, **Editors** always permanent

### 📋 Access Templates
- **Create**: Name → multi-folder checkbox → role → duration → save
- **Apply**: Select template → enter email(s) → duplicate check → batch execute
- Bundle-based access: one template grants to N folders at once
- Example: `New Intern → 5 folders | Viewer | 30d`

### ⏰ Timed Access & Auto-Expire
- Set expiry timers on viewer grants
- Background task auto-revokes expired access every 5 min
- Logged as `auto_revoke` with full audit trail

### 📥 Bulk Import & Scan Report
- Full Drive scan → generates `drive_scan_report.txt`
- Creates 40-day expiry for all viewer permissions
- Live progress: `Scanning... (30/120 folders)`

### 📂 Manage Folders
- Smart numeric sorting (`[001-050]` → `[051-100]`)
- Change roles (Viewer ↔ Editor) or remove access
- Folder caching with configurable TTL + manual refresh

### 📊 Activity Logs & Analytics
- Structured log types with icons (➕ 🗑 🔄)
- Soft delete — logs are never permanently lost
- `/stats` — daily/weekly/monthly counts, top folder, top admin

### 🔧 System Monitor
- `/info` — bot uptime, Python/Pyrogram version, DB status, collection counts
- Super admin only (first admin in ADMIN_IDS)

### ⚙️ Settings
- Default role, page size, notifications toggle

### 🔐 Security
- Admin-only access via MongoDB
- Super admin for system commands
- All credentials in `.env`

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
4. Download as `credentials.json`
5. Run locally once to complete OAuth flow

### 3. Configure
Copy `.env.example` to `.env`:
```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
MONGO_URI=mongodb+srv://...
ADMIN_IDS=your_telegram_user_id
```

### 4. Run
```bash
python server.py    # With Flask health checks (deployment)
python bot.py       # Standalone (local dev)
```

---

## 📁 Project Structure

```
├── bot.py              # Bot core + auto-expire scheduler
├── server.py           # Flask + Bot (Render deployment)
├── config.py           # Environment configuration
├── plugins/
│   ├── start.py        # /start, /help, /cancel, /id, main menu
│   ├── grant.py        # 3-mode grant flow (single/multi-folder/multi-email)
│   ├── templates.py    # Access templates (create/apply/delete)
│   ├── manage.py       # Folder permission management
│   ├── expiry.py       # Expiry dashboard + bulk import + scan report
│   ├── stats.py        # /stats analytics dashboard
│   ├── info.py         # /info system monitor
│   ├── settings.py     # Bot settings
│   └── logs.py         # Structured activity logs
├── services/
│   ├── database.py     # MongoDB (Motor) — all collections
│   └── drive.py        # Google Drive API v3 + caching
├── utils/
│   ├── filters.py      # Admin & state filters
│   ├── states.py       # Conversation state constants
│   ├── validators.py   # Email validation
│   └── pagination.py   # Pagination + checkbox keyboard + sorting
├── requirements.txt
├── Procfile
└── render.yaml
```

---

## 🎮 Bot Commands

| Command | Access | Description |
|---------|--------|-------------|
| `/start` | Admin | Main menu with live stats |
| `/help` | Admin | Feature reference |
| `/cancel` | Admin | Cancel current operation |
| `/stats` | Admin | Activity analytics dashboard |
| `/info` | Super Admin | System monitor |
| `/id` | Anyone | Show Telegram user ID |

---

## 🏠 Main Menu

```
[➕ Grant Access]      [📂 Manage Folders]
[⏰ Expiry Dashboard]  [📋 Templates]
[📊 Access Logs]       [⚙️ Settings]
[❓ Help]
```

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
| `templates` | Access templates (folder bundles) |

---

## 🚀 Deploy

See [DEPLOYMENT.md](DEPLOYMENT.md) for Render deployment guide.

---

Built with ❤️ using Pyrogram, MongoDB & Google Drive API
