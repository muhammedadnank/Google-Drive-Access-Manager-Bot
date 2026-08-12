<div align="center">

<img src="https://raw.githubusercontent.com/muhammedadnank/Google-Drive-Access-Manager-Bot/main/.github/assets/banner.png" alt="Google Drive Access Manager Bot" width="100%" />

# 📁 Google Drive Access Manager Bot

### *Automate, Schedule & Manage Google Drive Permissions at Scale — Directly from Telegram*

<br />

[![Version](https://img.shields.io/badge/version-2.3.0-blue.svg?style=for-the-badge&logo=git&logoColor=white)](https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot/blob/main/docs/Changelog.md)
[![Python](https://img.shields.io/badge/python-3.11+-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![Framework](https://img.shields.io/badge/framework-Kurigram-26A69A.svg?style=for-the-badge&logo=telegram&logoColor=white)](https://github.com/KurimuzonAkuma/Kurigram)
[![Database](https://img.shields.io/badge/database-MongoDB-47A248.svg?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com)
[![License](https://img.shields.io/badge/license-MIT-orange.svg?style=for-the-badge)](LICENSE)

<br />

[![Stars](https://img.shields.io/github/stars/muhammedadnank/Google-Drive-Access-Manager-Bot?style=social)](https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot/stargazers)
[![Forks](https://img.shields.io/github/forks/muhammedadnank/Google-Drive-Access-Manager-Bot?style=social)](https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot/network/members)
[![Last Commit](https://img.shields.io/github/last-commit/muhammedadnank/Google-Drive-Access-Manager-Bot?style=flat-square&color=brightgreen)](https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot/commits/main)
[![Issues](https://img.shields.io/github/issues/muhammedadnank/Google-Drive-Access-Manager-Bot?style=flat-square&color=yellow)](https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-ff69b4.svg?style=flat-square)](https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot/pulls)

<br />

### ⚡ Highlights

<p align="center">
  <code>👤 Single · 📂 Multi · 👥 Batch Grants</code> &nbsp;|&nbsp;
  <code>✏️ Custom Durations</code> &nbsp;|&nbsp;
  <code>⏰ Auto-Expire Scheduler</code>
  <br /><br />
  <code>📌 Pinned Favorites</code> &nbsp;|&nbsp;
  <code>🔍 Instant Drive Search</code> &nbsp;|&nbsp;
  <code>🗂️ A–Z Group Picker</code> &nbsp;|&nbsp;
  <code>📊 Analytics & CSV Export</code>
</p>

<br />

<p align="center">
  <a href="#-overview">📖 Overview</a> ·
  <a href="#-screenshots">🖼️ Screenshots</a> ·
  <a href="#-features">✨ Features</a> ·
  <a href="#-quick-start">🚀 Quick Start</a> ·
  <a href="#-deployment">🐳 Deployment</a> ·
  <a href="#-packages">📦 Packages</a> ·
  <a href="#-documentation">📖 Docs</a> ·
  <a href="#-faq">❓ FAQ</a>
</p>

</div>

<br />

---

## 📖 Overview

**Google Drive Access Manager Bot** is a full-featured Telegram bot that lets admins manage Google Drive folder permissions entirely from chat — no manual Drive UI needed. It supports multi-mode grants, timed expiry with auto-revoke, bulk import from Drive scans, analytics dashboards, CSV exports, and more.

<table>
<tr>
<td width="50%" valign="top">

**Why Use This Bot?**

| Problem | Solution |
|---|---|
| Managing 100s of permissions manually | Bulk grant/revoke with smart selection |
| Forgetting to remove access after a project | Auto-expiry with background scheduler |
| No visibility into who has access | Analytics dashboard + CSV exports |
| Duplicate access grants | DB-level unique index enforcement |
| Cloud deployment credential headaches | In-bot OAuth via `/auth` |
| Searching 1000+ folders manually | Folder search + pinned favorites |

</td>
<td width="50%" valign="top">

**At a Glance**

| Metric | Value |
|---|---|
| Python files | 30+ |
| Lines of code | 5,400+ |
| Protected endpoints | 90+ |
| MongoDB collections | 6 |
| Grant modes | 3 |
| Expiry durations | 7 |
| Architecture | 100% async/await |

</td>
</tr>
</table>

---

## 🖼️ Screenshots

<div align="center">

| Grant Access | Expiry Dashboard | Analytics |
|:---:|:---:|:---:|
| <img src="https://raw.githubusercontent.com/muhammedadnank/Google-Drive-Access-Manager-Bot/main/.github/assets/grant.png" width="260" alt="Grant Access flow" /> | <img src="https://raw.githubusercontent.com/muhammedadnank/Google-Drive-Access-Manager-Bot/main/.github/assets/expiry.png" width="260" alt="Expiry dashboard" /> | <img src="https://raw.githubusercontent.com/muhammedadnank/Google-Drive-Access-Manager-Bot/main/.github/assets/analytics.png" width="260" alt="Analytics dashboard" /> |
| 3-mode grant flow with role & duration picker | Live countdowns with inline extend/revoke | Expiry timeline, top folders & top users |

| Pinned Favorites | A–Z Folder Picker | System Monitor |
|:---:|:---:|:---:|
| <img src="https://raw.githubusercontent.com/muhammedadnank/Google-Drive-Access-Manager-Bot/main/.github/assets/favorites.png" width="260" alt="Pinned folders" /> | <img src="https://raw.githubusercontent.com/muhammedadnank/Google-Drive-Access-Manager-Bot/main/.github/assets/az-picker.png" width="260" alt="A-Z folder picker" /> | <img src="https://raw.githubusercontent.com/muhammedadnank/Google-Drive-Access-Manager-Bot/main/.github/assets/info.png" width="260" alt="Info command" /> |
| Instant access to root folders you use most | Jump straight to a letter group in huge trees | `/info` — health, versions, RAM/CPU/Disk |

> 📌 **Note:** drop your own PNGs into `.github/assets/` (e.g. `grant.png`, `expiry.png`, `analytics.png`, `favorites.png`, `az-picker.png`, `info.png`, `banner.png`) so the images above render — placeholders won't load until those files exist in the repo.

</div>

---

## ✨ Features

### 🎯 Access Management

<table>
<tr><th>Mode</th><th>Description</th><th>Best For</th></tr>
<tr><td>👤 <b>Single Grant</b></td><td>One email → One folder</td><td>Quick individual access</td></tr>
<tr><td>📂 <b>Multi-Folder</b></td><td>One email → Multiple folders</td><td>Power user onboarding</td></tr>
<tr><td>👥 <b>Batch Grant</b></td><td>Multiple emails → One folder</td><td>Team setup</td></tr>
</table>

All grant flows include email validation, role selection (Viewer/Editor), duration picker, and duplicate detection.

**Duration Options:** `1 hour` · `6 hours` · `1 day` · `7 days` · `30 days` · `♾️ Permanent` · `✏️ Custom (e.g. 59d, 91d, 12h, 2d12h)`

**Folder Management**
- Browse folders with an **A-Z group picker** — jump directly to any letter/number group
- Smart natural sort (numeric-aware)
- View all users with access and their expiry times
- Change role (Viewer ↔ Editor) with one tap
- Remove individual or all access per folder
- Configurable folder cache with adjustable TTL

<br />

<details>
<summary><b>📌 Pinned Folders (<code>/favorites</code>)</b> — click to expand</summary>
<br />

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
</details>

<details>
<summary><b>🔍 Folder Search</b> — click to expand</summary>
<br />

Search folders by name instead of scrolling through the full list.

- Type any keyword (e.g. `AD 2500`, `Hero`) — results appear instantly
- Available from **Grant Access** flow → 🔍 Search Folders button
- Searches across all Drive folders using the Google Drive API
- Shows top 25 matches, ordered by name
</details>

<details>
<summary><b>⏰ Expiry System</b> — click to expand</summary>
<br />

**Expiry Dashboard**
- View all timed grants with live countdown timers
- Unlimited pagination
- Extend access inline: `+1h · +6h · +1d · +7d · +30d`
- Quick revoke with confirmation prompt

**Auto-Expire Scheduler**
- Runs every 5 minutes in the background
- Automatically revokes expired viewer access from Drive
- Full audit trail logged for every auto-revocation
- Zero manual intervention needed
</details>

<details>
<summary><b>🔍 Search & Revoke</b> — click to expand</summary>
<br />

Search grants by email or folder name, then selectively revoke:

- ✅ **Select All** — bulk select everything instantly
- ☐ **Unselect All** — clear all at once
- 🔢 **Live Counter** — "X selected | Y total"
- 🎯 **Individual Toggle** — click any item to toggle
</details>

<details>
<summary><b>📊 Analytics & Reporting</b> — click to expand</summary>
<br />

- **Expiry Timeline** — Urgent (<24h), This Week, This Month, Later
- **Top 15 Most Accessed Folders**
- **Top 15 Users by Grant Count**
- **CSV Export** — full data in Excel-compatible format with IST timestamps
- **Statistics Dashboard** (`/stats`) — daily/weekly/monthly activity metrics
</details>

<details>
<summary><b>📥 Bulk Operations</b> — click to expand</summary>
<br />

- Full Drive scan with live progress indicators
- Before/after import report
- 40-day expiry auto-assigned for imported viewers
- Skips owners, editors, and duplicates automatically
</details>

<details>
<summary><b>📝 Activity Logs</b> — click to expand</summary>
<br />

- Structured log types: Grant, Remove, Role Change, Auto-Revoke, Bulk Import
- Paginated view
- CSV export
- Soft delete — no data loss
</details>

<details>
<summary><b>📢 Channel Integration</b> — click to expand</summary>
<br />

- Broadcast grant/revoke events to a Telegram channel
- Auto-detect channel ID via message forward
- Daily status summaries and error alerts
</details>

---

### 🗂️ Quick Commands

| Command | Description |
|---|---|
| `/start` | Open main menu |
| `/grant` | Grant Drive access (3 modes) |
| `/manage` | Manage folder permissions |
| `/search` | Search grants by email or folder |
| `/expiry` | View & manage timed access |
| `/favorites` | Pinned folders for instant access |
| `/analytics` | Analytics dashboard |
| `/stats` | Activity statistics |
| `/info` | System health monitor |
| `/settings` | Bot configuration |
| `/logs` | Activity log viewer |
| `/auth` | Connect Google Drive (OAuth) |
| `/revoke` | Disconnect Google account |
| `/authstatus` | Check auth status |

### 🔑 Authentication System

In-bot OAuth — no file uploads or manual token management needed.

| Command | Description |
|---|---|
| `/auth` | Start Google Drive authorization |
| `/revoke` | Disconnect your Google account |
| `/authstatus` | Check current authorization status |

### 🔐 Security

- Unique MongoDB indexes prevent duplicate grants
- Email normalization (auto-lowercase) prevents injection
- 90+ admin-protected handler endpoints
- Super admin role for system commands (`/info`)
- Input sanitization and type validation on all inputs
- Complete activity log with soft delete (data retention)

### ⚙️ Settings (`/settings`)

| Setting | Options |
|---|---|
| Default access role | Viewer / Editor |
| Folder page size | 3–10 per page |
| Notification preferences | Toggle on/off |
| Channel configuration | Set/clear broadcast channel |

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

<details>
<summary><b>Option B — Python Direct</b> — click to expand</summary>
<br />

**Step 1 — Clone & Install**
```bash
git clone https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot.git
cd Google-Drive-Access-Manager-Bot
pip install -r requirements.txt
```

**Step 2 — Google Drive API Setup**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project → Enable **Google Drive API**
3. Create an **OAuth 2.0 Client ID** → Web application
4. Add authorized redirect URI: `http://localhost:8080/oauth/callback`
5. Copy **Client ID** and **Client Secret** into `.env`

**Step 3 — Configure Environment**
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

**Step 4 — Run**
```bash
# Development
python bot.py

# Production (with health check server)
python server.py
```

**Step 5 — Connect Google Drive**

Send `/auth` to your bot and follow the link.
</details>

---

## 📁 Project Structure

<details>
<summary><b>Click to expand full file tree</b></summary>

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
</details>

---

## 📦 Packages

All dependencies are in `requirements.txt`.

<table>
<tr><th>Package</th><th>Version</th><th>Purpose</th></tr>
<tr><td colspan="3"><b>Core</b></td></tr>
<tr><td><a href="https://github.com/KurimuzonAkuma/Kurigram">kurigram</a></td><td>latest</td><td>Telegram MTProto bot framework — Pyrofork fork with <code>ButtonStyle</code> support</td></tr>
<tr><td><a href="https://github.com/pyrogram/tgcrypto">TgCrypto</a></td><td>latest</td><td>Fast C-extension encryption required by Kurigram</td></tr>
<tr><td colspan="3"><b>Database</b></td></tr>
<tr><td><a href="https://motor.readthedocs.io/">motor</a></td><td>3.7.1</td><td>Async MongoDB driver built on PyMongo — used for all DB operations</td></tr>
<tr><td colspan="3"><b>Google Drive</b></td></tr>
<tr><td><a href="https://github.com/googleapis/google-api-python-client">google-api-python-client</a></td><td>2.115.0</td><td>Official Google Drive API client</td></tr>
<tr><td><a href="https://google-auth.readthedocs.io/">google-auth</a></td><td>2.27.0</td><td>Google OAuth 2.0 token management</td></tr>
<tr><td><a href="https://github.com/googleapis/oauth2client">oauth2client</a></td><td>4.1.3</td><td>Legacy OAuth credential flow helper</td></tr>
<tr><td><a href="https://github.com/httplib2/httplib2">httplib2</a></td><td>0.22.0</td><td>HTTP client used internally by Google API client</td></tr>
<tr><td colspan="3"><b>Web Server</b></td></tr>
<tr><td><a href="https://flask.palletsprojects.com/">Flask</a></td><td>3.0.0</td><td>Web server for <code>/health</code>, <code>/status</code>, <code>/metrics</code>, <code>/oauth/callback</code></td></tr>
<tr><td><a href="https://gunicorn.org/">gunicorn</a></td><td>21.2.0</td><td>Production WSGI server used in Procfile and Render</td></tr>
<tr><td colspan="3"><b>Utilities</b></td></tr>
<tr><td><a href="https://pypi.org/project/python-dotenv/">python-dotenv</a></td><td>1.0.1</td><td>Loads environment variables from <code>.env</code> file</td></tr>
<tr><td><a href="https://pypi.org/project/psutil/">psutil</a></td><td>5.9.8</td><td>System metrics — CPU, RAM, Disk for <code>/info</code> command</td></tr>
</table>

<details>
<summary><b><code>requirements.txt</code></b> — click to expand</summary>

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
</details>

---

## 🐳 Deployment

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

<details>
<summary><b>Other deployment options</b> — Docker VPS, Railway, Heroku, systemd</summary>
<br />

**Docker (VPS / Self-Hosted)**
```bash
git clone https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot.git
cd Google-Drive-Access-Manager-Bot
cp .env.example .env && nano .env
docker compose up --build -d
docker compose logs -f bot
```
Supported: DigitalOcean, Hetzner, Fly.io, Railway, Coolify, any VPS.

**Railway**

Fork repo → New Project → Deploy from GitHub → Add env vars. Railway auto-detects `Dockerfile` — deploy starts automatically.

**Heroku**
```bash
heroku login
heroku create your-app-name
heroku config:set API_ID=... API_HASH=... BOT_TOKEN=... MONGO_URI=... \
  ADMIN_IDS=... G_DRIVE_CLIENT_ID=... G_DRIVE_CLIENT_SECRET=...
git push heroku main
```

**VPS (systemd)**
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
</details>

---

## 🗺️ Roadmap

<table>
<tr><td width="33%" valign="top">

**v2.3.0 ✅ Released**
- [x] 📌 Pinned Folders
- [x] 🔍 Folder Search
- [x] Sub-folder browsing
- [x] ✏️ Custom duration input
- [x] 🔤 A-Z/0-9 group browsing
- [x] 🔄 Multi-level back/cancel nav
- [ ] Invert selection in bulk revoke
- [ ] Select by role
- [ ] Batch extend multiple grants
- [ ] Email notifications on grant/revoke

</td><td width="33%" valign="top">

**v2.4.0**
- [ ] Auto-extend rules
- [ ] Scheduled grants
- [ ] REST API for integrations

</td><td width="33%" valign="top">

**v3.0.0**
- [ ] Shared Drive support
- [ ] Multi-Drive management
- [ ] Multi-tenant architecture

</td></tr>
</table>

---

## 📚 Documentation

| Document | Description |
|---|---|
| [Changelog](docs/Changelog.md) | Full version history |
| [UI Guide](docs/UI_GUIDE.md) | Interface walkthrough |
| [Deployment Guide](docs/DEPLOYMENT.md) | Platform-specific setup |
| [Database Maintenance](docs/DATABASE_MAINTENANCE.md) | DB management guide |
| [Duplicate Prevention](docs/DUPLICATE_PREVENTION.md) | Prevention system details |

---

## ❓ FAQ

<details>
<summary><b>How do I authenticate Google Drive on Render/Heroku?</b></summary>
<br />
Send <code>/auth</code> to your bot after deploying. Set <code>G_DRIVE_CLIENT_ID</code> and <code>G_DRIVE_CLIENT_SECRET</code> as env vars and follow the OAuth link.
</details>

<details>
<summary><b>Do I need <code>credentials.json</code> or <code>token.json</code>?</b></summary>
<br />
No. The <code>/auth</code> command handles everything through the bot.
</details>

<details>
<summary><b>How many admins can use the bot?</b></summary>
<br />
Unlimited. Add all Telegram user IDs to <code>ADMIN_IDS</code> (comma-separated).
</details>

<details>
<summary><b>How many folders can it manage?</b></summary>
<br />
No hard limit. Tested with 500+ folders.
</details>

<details>
<summary><b>Is this free to run?</b></summary>
<br />
Yes — MIT licensed. Render and MongoDB Atlas both have free tiers sufficient for most deployments.
</details>

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -m 'feat: add your feature'`
4. Push and open a Pull Request

## 📞 Support

- 🐛 **Issues:** [GitHub Issues](https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot/discussions)
- 📖 **Bot Help:** Send `/help` inside the bot

## 📄 License

MIT License — free for commercial use, modification, and distribution.

## 🙏 Built With

<p>
<img src="https://img.shields.io/badge/Kurigram-26A69A?style=flat-square&logo=telegram&logoColor=white" />
<img src="https://img.shields.io/badge/Motor-47A248?style=flat-square&logo=mongodb&logoColor=white" />
<img src="https://img.shields.io/badge/Google_Drive_API-4285F4?style=flat-square&logo=googledrive&logoColor=white" />
<img src="https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white" />
<img src="https://img.shields.io/badge/MongoDB-47A248?style=flat-square&logo=mongodb&logoColor=white" />
</p>

---

<div align="center">

**v2.3.0** · Updated April 2026 · ✅ Production Ready

Built with ❤️ using Kurigram, MongoDB & Google Drive API

⭐ If this project helped you, consider giving it a star!

[⬆ Back to Top](#-google-drive-access-manager-bot)

</div>
