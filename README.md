# 📂 Google Drive Access Manager Bot

<div align="center">

![Version](https://img.shields.io/badge/version-2.2.2-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![Framework](https://img.shields.io/badge/framework-Kurigram-purple.svg)
![Database](https://img.shields.io/badge/database-MongoDB-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Status](https://img.shields.io/badge/status-production%20ready-success.svg)

**A powerful Telegram bot for managing Google Drive folder permissions at scale**

Built with Kurigram · Motor · Google Drive API · MongoDB

[Features](#-features) • [Quick Start](#-quick-start) • [Deployment](#-deployment) • [Documentation](#-documentation) • [Support](#-support)

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

### ⏰ Expiry System

#### Expiry Dashboard
- View all timed grants with live countdown timers
- Unlimited pagination (no 100-grant cap)
- Configurable page size (5–100 per page)
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

**Smart Selection Tools**
- ✅ **Select All** — bulk select everything instantly
- ☐ **Unselect All** — clear all at once
- 🔢 **Live Counter** — "X selected | Y total"
- 🎯 **Individual Toggle** — click any item to toggle

**Workflow Example**
```
/search user@example.com
→ Click "☑️ Select & Revoke"
→ Click "✅ Select All"
→ Uncheck folders to keep
→ Click "🗑 Revoke Selected (12)"
→ Confirm → Done ✅
```

---

### 📊 Analytics & Reporting

#### Analytics Dashboard
- **Expiry Timeline** — Urgent (<24h), This Week, This Month, Later
- **Top 15 Most Accessed Folders**
- **Top 15 Users by Grant Count**
- **CSV Export** — full data in Excel-compatible format with IST timestamps

#### Statistics Dashboard (`/stats`)
- Daily / weekly / monthly activity metrics
- Expiring soon counter (<24h)
- Busiest day and most accessed folder
- Active grants overview

---

### 📥 Bulk Operations

#### Drive Scan & Import
- Full Drive scan with live progress ("Scanning... 30/120 folders")
- Generates detailed before/after import report
- Creates 40-day expiry for newly imported viewers
- Skips owners, editors, and duplicates automatically

---

### 📝 Activity Logs

- Structured log types: Grant, Remove, Role Change, Auto-Revoke, Bulk Import
- Soft delete — no data loss
- Paginated view with filtering
- CSV export for custom date ranges

---

### 📢 Channel Integration

- Broadcast grant/revoke events to a Telegram channel
- Auto-detect channel ID via message forward
- Daily status summaries and error alerts

---

### 🔑 Authentication System

The bot supports **in-bot OAuth** — no file uploads or manual token management needed.

| Command | Description |
|---------|-------------|
| `/auth` | Start Google Drive authorization |
| `/revoke` | Disconnect your Google account |
| `/authstatus` | Check current authorization status |

Each admin can link their own Google account. Credentials are stored encrypted in MongoDB — works perfectly on Render, Railway, Heroku.

---

### 🔐 Security

**Database Level**
- Unique MongoDB indexes prevent duplicate grants
- Email normalization (auto-lowercase) prevents injection
- Atomic operations protect against race conditions

**Application Level**
- 90+ admin-protected handler endpoints
- Super admin role for system commands (`/info`)
- Input sanitization and type validation on all inputs
- Rate limiting and graceful error handling
- No stack traces exposed to users

**Audit & Compliance**
- Complete activity log with soft delete (data retention)
- CSV export for audits
- Channel broadcast for visibility

---

### ⚙️ Settings

Configurable via bot UI (`/settings`):

| Setting | Options |
|---------|---------|
| Default access role | Viewer / Editor |
| Folder page size | 3–10 per page |
| Expiry page size | 10–100 per page |
| Cache TTL | 5–60 minutes |
| Notification preferences | Toggle on/off |
| Channel configuration | Set/clear broadcast channel |

---

### 🖥️ System Monitor (`/info` — super admin only)

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

### Step 1 — Clone Repository

```bash
git clone https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot.git
cd Google-Drive-Access-Manager-Bot
```

### Step 2 — Install Dependencies

```bash
pip install -r requirements.txt
```

**Key dependencies:**
- `kurigram` — Telegram bot framework (Pyrofork fork)
- `motor==3.7.1` — Async MongoDB driver
- `google-api-python-client==2.115.0` — Google Drive API
- `Flask==3.0.0` — Health check web server

---

### Step 3 — Google Drive API Setup

#### Option A: In-Bot OAuth ✅ Recommended (Render / Railway / Heroku)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable **Google Drive API**
4. Create an **OAuth 2.0 Client ID** → Web application
5. Add authorized redirect URI: `http://localhost:8080/oauth/callback`
6. Copy **Client ID** and **Client Secret** into `.env`

Then after deploying, send `/auth` to your bot and follow the link.

#### Option B: Traditional OAuth (Local development)

1. Create an **OAuth 2.0 Client ID** → Desktop app
2. Download as `credentials.json` and place in project root
3. Run `python bot.py` once locally — a `token.json` is generated
4. Upload both files to your hosting platform

---

### Step 4 — Configure Environment

Copy `.env.example` to `.env`:

```env
# Telegram
API_ID=your_api_id           # https://my.telegram.org
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token     # @BotFather

# Database
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/dbname

# Admins (comma-separated Telegram user IDs; first ID = super admin)
ADMIN_IDS=123456789,987654321

# Google Drive OAuth
G_DRIVE_CLIENT_ID=your_client_id.apps.googleusercontent.com
G_DRIVE_CLIENT_SECRET=your_client_secret

# Optional
CHANNEL_ID=-1001234567890   # Broadcast channel (optional)
```

> **Getting your Telegram User ID:** Start a chat with [@userinfobot](https://t.me/userinfobot)

---

### Step 5 — Run

```bash
# Development
python bot.py

# Production (with Flask health check)
python server.py

# Production with Gunicorn
gunicorn server:app --bind 0.0.0.0:8080 --workers 1 --timeout 0
```

---

## 📁 Project Structure

```
Google-Drive-Access-Manager-Bot/
├── bot.py                  # Main bot + auto-expire scheduler
├── server.py               # Flask wrapper for deployment
├── config.py               # Environment config loader
├── requirements.txt
├── .env.example
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
│   └── pagination.py       # Pagination + sorting
│
└── docs/                   # Extended documentation
    ├── UI_GUIDE.md
    ├── DEPLOYMENT.md
    ├── Changelog.md
    ├── DATABASE_MAINTENANCE.md
    └── DUPLICATE_PREVENTION.md
```

---

## 🚀 Deployment

### Render (Recommended)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

**Manual setup:**
1. Fork this repo → Create a new **Web Service** on Render
2. Connect your GitHub repo
3. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python server.py`
4. Add environment variables: `API_ID`, `API_HASH`, `BOT_TOKEN`, `MONGO_URI`, `ADMIN_IDS`, `G_DRIVE_CLIENT_ID`, `G_DRIVE_CLIENT_SECRET`
5. Deploy → then send `/auth` to your bot to connect Google Drive

> No `credentials.json` or `token.json` needed — the `/auth` command handles everything.

---

### Heroku

```bash
heroku login
heroku create your-app-name
heroku config:set API_ID=... API_HASH=... BOT_TOKEN=... MONGO_URI=... ADMIN_IDS=... \
  G_DRIVE_CLIENT_ID=... G_DRIVE_CLIENT_SECRET=...
git push heroku main
```

After deploy → send `/auth` to connect Google Drive.

---

### VPS (DigitalOcean, Linode, etc.)

```bash
sudo apt update && sudo apt install python3.11 python3-pip git
git clone https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot.git
cd Google-Drive-Access-Manager-Bot
pip3 install -r requirements.txt
cp .env.example .env && nano .env
```

**Recommended: run as a systemd service**

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

## 🛠️ Database Maintenance

### Check for Duplicates

```bash
python3 scripts/check_duplicates.py
```

```
📊 DATABASE STATISTICS
==================================================
ACTIVE              :   1240
EXPIRED             :     16
REVOKED             :     43
DUPLICATE_REMOVED   :      0  ✅
TOTAL               :   1299
==================================================
```

### Remove Duplicates

```bash
python3 scripts/remove_duplicates.py
```

- Interactive confirmation prompts
- Progress indicators
- Malayalam language support (മലയാളം)
- Safe — does not touch actual Drive permissions
- Achieved 67.6% database size reduction in production (4,010 → 1,299)

### Backup / Restore

```bash
# Backup
mongodump --uri="mongodb+srv://user:pass@cluster.mongodb.net/dbname" --out=./backup

# Restore
mongorestore --uri="mongodb+srv://user:pass@cluster.mongodb.net/dbname" ./backup
```

See [docs/DATABASE_MAINTENANCE.md](docs/DATABASE_MAINTENANCE.md) for detailed guide.

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
| Test coverage | Production-tested |

---

## 🗺️ Roadmap

### v2.3.0 (Q1 2026)
- [ ] Invert selection in bulk revoke
- [ ] Select by role (viewers/editors only)
- [ ] Select by expiry window
- [ ] Batch extend multiple grants
- [ ] Email notifications to users on grant/revoke
- [ ] Enhanced analytics with visual charts

### v2.4.0 (Q2 2026)
- [ ] Auto-extend rules (renew before expiry)
- [ ] Scheduled grants (future start date)
- [ ] User self-service portal
- [ ] REST API for external integrations
- [ ] Webhook support

### v3.0.0 (Future)
- [ ] Shared Drive support
- [ ] Multi-Drive management
- [ ] AI-powered access recommendations
- [ ] Anomaly detection
- [ ] Multi-tenant architecture

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [UI Guide](docs/UI_GUIDE.md) | Full interface walkthrough |
| [Deployment Guide](docs/DEPLOYMENT.md) | Render / Heroku step-by-step |
| [Changelog](docs/Changelog.md) | Version history |
| [Database Maintenance](docs/DATABASE_MAINTENANCE.md) | DB management guide |
| [Duplicate Prevention](docs/DUPLICATE_PREVENTION.md) | Prevention system details |
| [Security Audit](docs/Security%20audit%20report.MD) | Security review |

---

## ❓ FAQ

**Q: Revoke button in Expiry Dashboard isn't working — access stays in Drive.**  
A: This was a bug in v2.2.1. Fixed in v2.2.2 — update `plugins/expiry.py`.

**Q: How do I authenticate Google Drive on Render/Heroku?**  
A: Use `/auth` command. Set `G_DRIVE_CLIENT_ID` and `G_DRIVE_CLIENT_SECRET` as env vars, then send `/auth` to the bot and follow the link.

**Q: Do I still need `credentials.json` or `token.json`?**  
A: No. The `/auth` command (available since v2.2.1) handles everything through the bot.

**Q: How many admins can use the bot?**  
A: Unlimited. Add all admin Telegram user IDs to `ADMIN_IDS` (comma-separated). Each can link their own Google account via `/auth`.

**Q: How many folders can it manage?**  
A: No hard limit. Tested successfully with 500+ folders.

**Q: Is MongoDB the only supported database?**  
A: Yes, currently. PostgreSQL support may be considered in future versions.

**Q: Is this free to run?**  
A: Yes. MIT licensed. Render and MongoDB Atlas both offer free tiers sufficient for small-to-medium deployments.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes, test with real data
4. Commit: `git commit -m 'feat: add your feature'`
5. Push and open a Pull Request

**Guidelines:** Follow existing async/await patterns, add error handling, update docs for new features, maintain backwards compatibility.

**Bug reports** should include: steps to reproduce, expected vs actual behavior, environment details, and screenshots if applicable.

---

## 📞 Support

- 🐛 **Issues:** [GitHub Issues](https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot/discussions)
- 📖 **Bot Help:** Send `/help` inside the bot

---

## 📄 License

MIT License — free for commercial use, modification, and distribution. Attribution required (keep credits in code).

---

## 🙏 Built With

- [Kurigram](https://github.com/KurimuzonAkuma/Kurigram) — Telegram bot framework
- [Motor](https://motor.readthedocs.io/) — Async MongoDB driver
- [Google Drive API](https://developers.google.com/drive) — Drive integration
- [Flask](https://flask.palletsprojects.com/) — Health check web server
- [MongoDB](https://www.mongodb.com/) — Database

---

<div align="center">

**v2.2.2** · Updated March 2026 · ✅ Production Ready

Built with ❤️ using Kurigram, MongoDB & Google Drive API

[⬆ Back to Top](#-google-drive-access-manager-bot)

</div>
