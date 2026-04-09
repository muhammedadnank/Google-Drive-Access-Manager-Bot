# 📂 Google Drive Access Manager Bot

<div align="center">

![Version](https://img.shields.io/badge/version-2.3.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![Framework](https://img.shields.io/badge/framework-Kurigram-purple.svg)
![Database](https://img.shields.io/badge/database-MongoDB-brightgreen.svg)
![Docker](https://img.shields.io/badge/docker-supported-2496ED.svg?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Status](https://img.shields.io/badge/status-production%20ready-success.svg)

**A powerful Telegram bot for managing Google Drive folder permissions at scale**

Built with Kurigram · Motor · Google Drive API · MongoDB

[Features](#-features) • [Quick Start](#-quick-start) • [Deployment](#-deployment) • [Packages](#-packages) • [Documentation](#-documentation)

</div>

---

## 📖 Overview

**Google Drive Access Manager Bot** is a full-featured Telegram bot that lets admins manage Google Drive folder permissions entirely from chat — no manual Drive UI needed. It supports multi-mode grants, timed expiry with auto-revoke, bulk import from Drive scans, analytics dashboards, CSV exports, and more.

### Why Use This Bot?

| Problem | Solution |
|---------|----------|
| Managing 100s of folder permissions manually | Bulk grant/revoke with smart selection |
| Forgetting to remove access after projects end | Auto-expiry with background scheduler |
| No visibility into who has access to what | Analytics dashboard + CSV exports |
| Duplicate access grants causing confusion | Database-level unique index enforcement |
| Cloud deployment credential headaches | In-bot OAuth via `/auth` command |
| Searching through 1000+ folders manually | Folder search + pinned favorites for instant access |

---

## ✨ Features

### 🎯 Access Management

#### Three Grant Modes

| Mode | Description | Best For |
|------|-------------|----------|
| 👤 **Single Grant** | One email → One folder | Quick individual access |
| 📂 **Multi-Folder** | One email → Multiple folders | Power user onboarding |
| 👥 **Batch Grant** | Multiple emails → One folder | Team setup |

All grant flows include email validation, role selection (Viewer/Editor), duration picker, and duplicate detection.

#### Duration Options
`1 hour · 6 hours · 1 day · 7 days · 30 days · ♾️ Permanent`

#### Folder Management
- Browse folders with smart numeric sorting
- View all users with access and their expiry times
- Change role (Viewer ↔ Editor) with one tap
- Remove individual or all access per folder
- Configurable folder cache with adjustable TTL

---

### 📌 Pinned Folders (`/favorites`)

Pin frequently used root folders for instant access — no more scrolling through hundreds of folders.

- ⭐ **Pin any folder** from Manage → folder view
- 📁 **Browse sub-folders** of a pinned root folder directly
- 🔑 **Grant access** to root or any sub-folder in one flow
- 📌 **Unpin** anytime from the same folder view
- Up to **20 pinned folders** per admin

**Flow:**
```
Manage → Open Folder → ⭐ Pin Folder
/favorites → Leo AD 2500 → Hero / Villain / Scripts → Grant
```

---

### 🔍 Folder Search

Search folders by name instead of scrolling through the full list.

- Type any keyword (e.g. `AD 2500`, `Hero`) — results appear instantly
- Available from **Grant Access** flow → 🔍 Search Folders button
- Searches across all Drive folders using Google Drive API
- Shows top 25 matches, ordered by name

---

### ⏰ Expiry System

#### Expiry Dashboard
- View all timed grants with live countdown timers
- Unlimited pagination
- Extend access inline: `+1h · +6h · +1d · +7d · +30d`
- Quick revoke with confirmation prompt

#### Auto-Expire Scheduler
- Runs every 5 minutes in background
- Automatically revokes expired viewer access from Drive
- Full audit trail logged for every auto-revocation
- Zero manual intervention needed

---

### 🔍 Search & Revoke

Search grants by email or folder name, then selectively revoke:

- ✅ **Select All** — bulk select everything instantly
- ☐ **Unselect All** — clear all at once
- 🔢 **Live Counter** — "X selected | Y total"
- 🎯 **Individual Toggle** — click any item to toggle

---

### 📊 Analytics & Reporting

- **Expiry Timeline** — Urgent (<24h), This Week, This Month, Later
- **Top 15 Most Accessed Folders**
- **Top 15 Users by Grant Count**
- **CSV Export** — full data in Excel-compatible format with IST timestamps
- **Statistics Dashboard** (`/stats`) — daily/weekly/monthly activity metrics

---

### 📥 Bulk Operations

- Full Drive scan with live progress indicators
- Before/after import report
- 40-day expiry auto-assigned for imported viewers
- Skips owners, editors, and duplicates automatically

---

### 📝 Activity Logs

- Structured log types: Grant, Remove, Role Change, Auto-Revoke, Bulk Import
- Paginated view
- CSV export
- Soft delete — no data loss

---

### 📢 Channel Integration

- Broadcast grant/revoke events to a Telegram channel
- Auto-detect channel ID via message forward
- Daily status summaries and error alerts

---

### 🗂️ Quick Commands

| Command | Description |
|---------|-------------|
| `/favorites` | View and manage pinned root folders |

---

### 🔑 Authentication System

In-bot OAuth — no file uploads or manual token management needed.

| Command | Description |
|---------|-------------|
| `/auth` | Start Google Drive authorization |
| `/revoke` | Disconnect your Google account |
| `/authstatus` | Check current authorization status |

---

### 🔐 Security

- Unique MongoDB indexes prevent duplicate grants
- Email normalization (auto-lowercase) prevents injection
- 90+ admin-protected handler endpoints
- Super admin role for system commands (`/info`)
- Input sanitization and type validation on all inputs
- Complete activity log with soft delete (data retention)

---

### ⚙️ Settings (`/settings`)

| Setting | Options |
|---------|---------|
| Default access role | Viewer / Editor |
| Folder page size | 3–10 per page |
| Notification preferences | Toggle on/off |
| Channel configuration | Set/clear broadcast channel |

---

### 🖥️ System Monitor (`/info`)

- Bot uptime and version
- Python and Kurigram versions
- Service health: Drive API, MongoDB, Telegram
- Auto-expire scheduler status
- RAM, CPU, Disk usage

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- MongoDB database ([Atlas free tier](https://www.mongodb.com/atlas) works)
- Google Cloud Project with Drive API enabled
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)

---

### Option A — Docker 🐳 (Recommended)

```bash
git clone https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot.git
cd Google-Drive-Access-Manager-Bot
cp .env.example .env
nano .env   # fill in your credentials
docker compose up --build -d
```

Check logs:
```bash
docker compose logs -f bot
```

---

### Option B — Python Direct

#### Step 1 — Clone & Install

```bash
git clone https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot.git
cd Google-Drive-Access-Manager-Bot
pip install -r requirements.txt
```

#### Step 2 — Google Drive API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project → Enable **Google Drive API**
3. Create an **OAuth 2.0 Client ID** → Web application
4. Add authorized redirect URI: `http://localhost:8080/oauth/callback`
5. Copy **Client ID** and **Client Secret** into `.env`

#### Step 3 — Configure Environment

```env
# Telegram
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token

# Database
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/dbname

# Admins (comma-separated Telegram user IDs)
ADMIN_IDS=123456789,987654321

# Google Drive OAuth
G_DRIVE_CLIENT_ID=your_client_id.apps.googleusercontent.com
G_DRIVE_CLIENT_SECRET=your_client_secret

# Optional
CHANNEL_ID=-1001234567890
```

#### Step 4 — Run

```bash
# Development
python bot.py

# Production (with health check server)
python server.py
```

#### Step 5 — Connect Google Drive

Send `/auth` to your bot and follow the link.

---

## 📁 Project Structure

```
Google-Drive-Access-Manager-Bot/
├── bot.py                  # Main bot + background schedulers
├── server.py               # Flask wrapper + process manager
├── config.py               # Environment config loader
├── requirements.txt
├── .env.example
├── Dockerfile              # Docker support (v2.2.3)
├── docker-compose.yml
├── .dockerignore
├── Procfile                # Heroku
├── render.yaml             # Render
│
├── plugins/                # Feature handlers
│   ├── start.py            # /start, /help, main menu
│   ├── auth.py             # /auth, /revoke, /authstatus
│   ├── grant.py            # 3-mode grant system
│   ├── manage.py           # Folder management
│   ├── expiry.py           # Expiry dashboard & bulk import
│   ├── analytics.py        # Analytics dashboard
│   ├── search.py           # Search + smart selection revoke
│   ├── stats.py            # /stats dashboard
│   ├── info.py             # /info system monitor
│   ├── settings.py         # Bot settings
│   ├── channel.py          # Channel integration
│   ├── logs.py             # Activity logs
│   └── csv_export.py       # CSV export utilities
│
├── services/
│   ├── database.py         # MongoDB operations (Motor)
│   ├── drive.py            # Google Drive API + cache
│   └── broadcast.py        # Telegram channel broadcasts
│
├── utils/
│   ├── filters.py          # Admin + state filters
│   ├── states.py           # Conversation state management
│   ├── validators.py       # Email validation
│   ├── time.py             # IST timezone + safe_edit helper
│   └── pagination.py       # Pagination + sorting + ButtonStyles
│
└── docs/
    ├── Changelog.md
    ├── UI_GUIDE.md
    ├── DEPLOYMENT.md
    ├── DATABASE_MAINTENANCE.md
    └── DUPLICATE_PREVENTION.md
```

---

## 📦 Packages

All dependencies are in `requirements.txt`.

### Core

| Package | Version | Purpose |
|---------|---------|---------|
| [kurigram](https://github.com/KurimuzonAkuma/Kurigram) | latest | Telegram MTProto bot framework — Pyrofork fork with `ButtonStyle` support |
| [TgCrypto](https://github.com/pyrogram/tgcrypto) | latest | Fast C-extension encryption required by Kurigram |

### Database

| Package | Version | Purpose |
|---------|---------|---------|
| [motor](https://motor.readthedocs.io/) | 3.7.1 | Async MongoDB driver built on PyMongo — used for all DB operations |

### Google Drive

| Package | Version | Purpose |
|---------|---------|---------|
| [google-api-python-client](https://github.com/googleapis/google-api-python-client) | 2.115.0 | Official Google Drive API client |
| [google-auth](https://google-auth.readthedocs.io/) | 2.27.0 | Google OAuth 2.0 token management |
| [oauth2client](https://github.com/googleapis/oauth2client) | 4.1.3 | Legacy OAuth credential flow helper |
| [httplib2](https://github.com/httplib2/httplib2) | 0.22.0 | HTTP client used internally by Google API client |

### Web Server

| Package | Version | Purpose |
|---------|---------|---------|
| [Flask](https://flask.palletsprojects.com/) | 3.0.0 | Web server for `/health`, `/status`, `/metrics`, `/oauth/callback` |
| [gunicorn](https://gunicorn.org/) | 21.2.0 | Production WSGI server used in Procfile and Render |

### Utilities

| Package | Version | Purpose |
|---------|---------|---------|
| [python-dotenv](https://pypi.org/project/python-dotenv/) | 1.0.1 | Loads environment variables from `.env` file |
| [psutil](https://pypi.org/project/psutil/) | 5.9.8 | System metrics — CPU, RAM, Disk for `/info` command |

### `requirements.txt`

```
kurigram
tgcrypto
google-api-python-client==2.115.0
google-auth==2.27.0
motor==3.7.1
python-dotenv==1.0.1
Flask==3.0.0
gunicorn==21.2.0
psutil==5.9.8
oauth2client==4.1.3
httplib2==0.22.0
```

---

## 🚀 Deployment

### Render (Recommended)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. Fork this repo → Create a new **Web Service** on Render
2. Connect your GitHub repo
3. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python server.py`
   - **Health Check Path:** `/health`
4. Add environment variables
5. Deploy → send `/auth` to connect Google Drive

---

### Docker (VPS / Self-Hosted)

```bash
git clone https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot.git
cd Google-Drive-Access-Manager-Bot
cp .env.example .env && nano .env
docker compose up --build -d
docker compose logs -f bot
```

Supported: DigitalOcean, Hetzner, Fly.io, Railway, Coolify, any VPS.

---

### Railway

Fork repo → New Project → Deploy from GitHub → Add env vars.  
Railway auto-detects `Dockerfile` — deploy starts automatically.

---

### Heroku

```bash
heroku login
heroku create your-app-name
heroku config:set API_ID=... API_HASH=... BOT_TOKEN=... MONGO_URI=... \
  ADMIN_IDS=... G_DRIVE_CLIENT_ID=... G_DRIVE_CLIENT_SECRET=...
git push heroku main
```

---

### VPS (systemd)

```bash
sudo apt update && sudo apt install python3.11 python3-pip git -y
git clone https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot.git
cd Google-Drive-Access-Manager-Bot
pip3 install -r requirements.txt
cp .env.example .env && nano .env
```

```ini
# /etc/systemd/system/gdrive-bot.service
[Unit]
Description=Google Drive Access Manager Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Google-Drive-Access-Manager-Bot
ExecStart=/usr/bin/python3 server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable gdrive-bot
sudo systemctl start gdrive-bot
```

---

## 📊 Project Stats

| Metric | Value |
|--------|-------|
| Python files | 30+ |
| Lines of code | 5,400+ |
| Protected endpoints | 90+ |
| MongoDB collections | 6 |
| Grant modes | 3 |
| Expiry durations | 6 |
| Architecture | 100% async/await |

---

## 🗺️ Roadmap

### v2.3.0 ✅ Released
- [x] 📌 Pinned Folders — pin root folders for instant access
- [x] 🔍 Folder Search — filter folders by keyword
- [x] Sub-folder browsing from pinned root folders
- [ ] Invert selection in bulk revoke
- [ ] Select by role (viewers/editors only)
- [ ] Batch extend multiple grants
- [ ] Email notifications to users on grant/revoke

### v2.4.0
- [ ] Auto-extend rules (renew before expiry)
- [ ] Scheduled grants (future start date)
- [ ] REST API for external integrations

### v3.0.0
- [ ] Shared Drive support
- [ ] Multi-Drive management
- [ ] Multi-tenant architecture

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Changelog](docs/Changelog.md) | Full version history |
| [UI Guide](docs/UI_GUIDE.md) | Interface walkthrough |
| [Deployment Guide](docs/DEPLOYMENT.md) | Platform-specific setup |
| [Database Maintenance](docs/DATABASE_MAINTENANCE.md) | DB management guide |
| [Duplicate Prevention](docs/DUPLICATE_PREVENTION.md) | Prevention system details |

---

## ❓ FAQ

**Q: How do I authenticate Google Drive on Render/Heroku?**  
A: Send `/auth` to your bot after deploying. Set `G_DRIVE_CLIENT_ID` and `G_DRIVE_CLIENT_SECRET` as env vars and follow the OAuth link.

**Q: Do I need `credentials.json` or `token.json`?**  
A: No. The `/auth` command handles everything through the bot.

**Q: How many admins can use the bot?**  
A: Unlimited. Add all Telegram user IDs to `ADMIN_IDS` (comma-separated).

**Q: How many folders can it manage?**  
A: No hard limit. Tested with 500+ folders.

**Q: Is this free to run?**  
A: Yes — MIT licensed. Render and MongoDB Atlas both have free tiers sufficient for most deployments.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -m 'feat: add your feature'`
4. Push and open a Pull Request

---

## 📞 Support

- 🐛 **Issues:** [GitHub Issues](https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot/discussions)
- 📖 **Bot Help:** Send `/help` inside the bot

---

## 📄 License

MIT License — free for commercial use, modification, and distribution.

---

## 🙏 Built With

| Library | Role |
|---------|------|
| [Kurigram](https://github.com/KurimuzonAkuma/Kurigram) | Telegram bot framework |
| [Motor](https://motor.readthedocs.io/) | Async MongoDB driver |
| [Google Drive API](https://developers.google.com/drive) | Drive integration |
| [Flask](https://flask.palletsprojects.com/) | Health check web server |
| [MongoDB](https://www.mongodb.com/) | Database |

---

<div align="center">

**v2.2.3** · Updated March 2026 · ✅ Production Ready

Built with ❤️ using Kurigram, MongoDB & Google Drive API

[⬆ Back to Top](#-google-drive-access-manager-bot)

</div>
