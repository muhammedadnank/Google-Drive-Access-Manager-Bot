# 📂 Google Drive Access Manager Bot

<div align="center">

![Version](https://img.shields.io/badge/version-2.2.2-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Status](https://img.shields.io/badge/status-production%20ready-success.svg)

**A powerful Telegram bot for managing Google Drive folder permissions at scale**

Built with Pyrofork · MongoDB · Google Drive API

[Features](#-features) • [Installation](#-installation) • [Documentation](#-documentation) • [Support](#-support)

</div>

---

## 📖 Overview

Google Drive Access Manager Bot is a comprehensive solution for managing Google Drive folder permissions through Telegram. With support for multi-email grants, timed expiry, bulk imports, analytics dashboards, and smart selection tools, it simplifies the complex task of access management for teams and organizations.

### Why This Bot?

- ⚡ **Manage at Scale** - Handle hundreds of folders and thousands of permissions effortlessly
- 🤖 **Automated Expiry** - Set time-limited access that auto-revokes when expired
- 📊 **Deep Analytics** - Understand your access patterns with built-in analytics
- 🔒 **Secure by Design** - Database-level duplicate prevention and comprehensive audit trails
- 🎯 **User-Friendly** - Intuitive interface with smart selection tools

---

## ✨ Key Features

### 🎯 Access Management

#### Grant Access (3 Flexible Modes)

| Mode | Description | Use Case |
|------|-------------|----------|
| 👤 **Single Grant** | One email → One folder | Quick individual access |
| 📂 **Multi-Folder** | One email → Multiple folders | Power user setup |
| 👥 **Batch Grant** | Multiple emails → One folder | Team onboarding |

**Features:**
- ✅ Email validation with duplicate detection
- ✅ Role selection (Viewer/Editor)
- ✅ Duration options: 1h, 6h, 1d, 7d, 30d, or ♾️ Permanent
- ✅ Smart duplicate prevention system
- ✅ Inline progress tracking

#### Manage Folders

- 📂 Browse folders with smart numeric sorting
- 👥 View all users with access to each folder
- ⏰ See expiry dates for timed grants
- 🔄 Change roles (Viewer ↔️ Editor)
- 🗑️ Remove individual or all access
- 💾 Folder caching with configurable TTL

### ⏰ Expiry Management

#### Expiry Dashboard
- 📋 View all timed grants with countdown timers
- ⚡ **Unlimited pagination** - no more 100-grant limit
- 📏 Configurable page size (5-100 grants per page)
- 🔄 Extend access with inline buttons (+1h to +30d)
- 🗑️ Quick revoke with confirmation
- 📊 Real-time status updates

#### Auto-Expire System
- 🤖 Background scheduler runs every 5 minutes
- 🔒 Automatically revokes expired viewer access
- 📝 Full audit trail for all auto-revocations
- ⚙️ Zero manual intervention required

### 📊 Analytics & Reporting

#### Analytics Dashboard
Get instant insights into your access patterns:

**⏰ Expiry Timeline**
- ⚠️ **Urgent** - Expiring in < 24 hours
- 📅 **This Week** - 1-7 days remaining
- 📆 **This Month** - 8-30 days
- 🗓️ **Later** - 30+ days

**📊 Top 15 Reports**
- 📂 Most accessed folders
- 👥 Users with most grants
- 📈 Usage pattern analysis
- 📉 Trend identification

**💾 CSV Export**
- Complete data export in Excel format
- IST timestamps for easy sorting
- Status indicators for quick filtering
- Perfect for audits and compliance

### 🔍 Smart Search & Revoke

#### Advanced Search
- 🔎 Search by email or folder name
- 🎯 Filter by role (Reader/Writer)
- 📊 Filter by status (Active/Expired/Revoked)
- 📋 View complete access history

#### Smart Selection Tools ✨ **NEW!**
- ✅ **Select All** - Bulk select all items instantly
- ☐ **Unselect All** - Clear all selections
- 🎯 **Individual Toggle** - Click to toggle any item
- 📊 **Live Counter** - "X selected | Y total"
- 🔄 **Smart Button** - Automatically adapts to selection state

#### Workflow Example
```
1. /search user@example.com
2. Click "☑️ Select & Revoke"
3. Click "✅ Select All" (all 15 folders selected)
4. Unselect folders to keep
5. Click "🗑 Revoke Selected (12)"
6. Confirm → Access revoked!
```

### 📥 Bulk Operations

#### Drive Scan & Import
- 🔍 Full Drive scan with progress tracking
- 📄 Generates detailed scan report
- ⏰ Creates 40-day expiry for new viewers
- ⚡ Live progress: "Scanning... (30/120 folders)"
- 🛡️ Skips owners, editors, and duplicates
- 📊 Shows before/after statistics

### 📝 Activity Logs

- 📋 Structured log types with visual icons
- ✅ Soft delete - no data loss
- 📄 Paginated view with filtering
- 📊 CSV export for date ranges
- 🔍 Search and filter capabilities

**Log Types:**
- ➕ Grant Access
- 🗑️ Remove Access
- 🔄 Role Change
- ▪️ Auto Revoke
- 📥 Bulk Import

### 📢 Telegram Channel Integration

- 📣 Broadcast grants and revokes to channel
- 🤖 Auto-detect channel ID (forward message)
- 🔔 Daily status summaries
- ⚠️ Error alerts and notifications
- 📊 Activity tracking

### 📊 Statistics Dashboard

Access via `/stats` command or main menu button:

- 📈 Activity metrics (daily/weekly/monthly)
- ⚠️ Expiring soon counter (< 24h)
- 📊 Busiest day analysis
- 📂 Most accessed folder
- 👥 Active grants overview
- 📉 Trend visualization

### 🔧 System Monitor

Super admin only (`/info` command):

- ⏱️ Bot uptime and version
- 🐍 Python and Pyrofork versions
- ✅ Service health checks (Drive API, MongoDB, Telegram)
- ⏰ Auto-expire scheduler status
- 💻 System resources (RAM, CPU, Disk)
- 📊 Performance metrics

### ⚙️ Settings & Configuration

- 👁️ Default access role (Viewer/Editor)
- 📏 Folder page size (3-10 per page)
- 📋 Expiry page size (10-100 per page)
- ⏱️ Cache TTL (5-60 minutes)
- 🔔 Notification preferences
- 📢 Channel configuration

### 🗄️ Database Maintenance

#### Duplicate Prevention System
- 🔒 **MongoDB Unique Index** - Database-level enforcement
- 📧 **Email Normalization** - Automatic lowercase conversion
- ⚡ **Race Condition Protection** - Atomic operations
- 🚫 **Bulk Import Protection** - Set-based deduplication

#### Cleanup Tools
- 📊 `check_duplicates.py` - View statistics
- 🧹 `remove_duplicates.py` - Safe cleanup with confirmation
- 🇮🇳 Malayalam language support
- ✅ 67.6% database size reduction achieved

### 🔐 Security Features

#### Authentication System ✨ **NEW!**
- 🔑 **In-Bot OAuth** - `/auth` command for cloud-friendly authorization
- 🔐 **Per-Admin Credentials** - Each admin can connect their own Google account
- 🔄 **Easy Revocation** - `/revoke` command to disconnect anytime
- 📊 **Status Check** - `/authstatus` to view connection status
- 🛡️ **Secure Storage** - Encrypted credential storage in MongoDB
- ⚡ **No File Upload** - Works perfectly on Render/Heroku without file persistence

**Auth Commands:**
- `/auth` - Start Google Drive authorization flow
- `/revoke` - Disconnect your Google account
- `/authstatus` - Check your authorization status

#### Database Level
- ✅ Unique indexes prevent duplicates
- ✅ Email normalization (injection prevention)
- ✅ NoSQL injection protection
- ✅ Type validation on all inputs
- ✅ Atomic operations for race conditions

#### Application Level
- ✅ Admin-only access (90+ protected endpoints)
- ✅ Super admin role for system commands
- ✅ Input sanitization
- ✅ Rate limiting
- ✅ Graceful error handling
- ✅ No stack traces to users

#### Audit & Compliance
- ✅ Complete activity logs
- ✅ Soft delete (data retention)
- ✅ CSV export for audits
- ✅ Channel broadcasting
- ✅ Duplicate cleanup with history

---

## 🚀 Installation

### Prerequisites

Before you begin, ensure you have:

- ✅ Python 3.11 or higher
- ✅ MongoDB database (MongoDB Atlas recommended)
- ✅ Google Cloud Project with Drive API enabled
- ✅ Telegram Bot Token from [@BotFather](https://t.me/BotFather)

### Step 1: Clone Repository

```bash
git clone https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot.git
cd Google-Drive-Access-Manager-Bot
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**
- `pyrofork==2.3.69` - Telegram bot framework
- `motor==3.7.1` - Async MongoDB driver
- `google-api-python-client==2.115.0` - Google Drive API
- `Flask==3.0.0` - Web server for health checks
- And more (see `requirements.txt`)

### Step 3: Google Drive API Setup

#### Option A: In-Bot OAuth (Recommended for Render/Heroku) ✨ **NEW!**

The bot now supports **in-bot OAuth authentication** via the `/auth` command - perfect for cloud deployments!

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Google Drive API**
4. Create **OAuth 2.0 Client ID** (Web application)
5. Add authorized redirect URI: `http://localhost:8080/oauth/callback`
6. Copy **Client ID** and **Client Secret**
7. Add to your `.env` file:
   ```env
   G_DRIVE_CLIENT_ID=your_client_id.apps.googleusercontent.com
   G_DRIVE_CLIENT_SECRET=your_client_secret
   ```
8. Start the bot and use `/auth` command to authorize

**How to use /auth command:**
1. Send `/auth` to the bot
2. Click the authorization link
3. Sign in with Google and grant permissions
4. Copy the **full redirect URL** from browser (even if it shows error)
5. Paste the URL back to the bot
6. Done! ✅

#### Option B: Traditional OAuth (Local Development)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Google Drive API**
4. Create **OAuth 2.0 Client ID** (Desktop app)
5. Download credentials as `credentials.json`
6. Place in project root directory
7. Run locally once to complete OAuth flow:
   ```bash
   python bot.py
   ```
8. A `token.json` file will be generated
9. Upload both files to your deployment platform

### Step 4: Configure Environment

Copy `.env.example` to `.env` and configure:

```env
# Telegram Bot Configuration
API_ID=your_api_id                    # Get from https://my.telegram.org
API_HASH=your_api_hash                # Get from https://my.telegram.org
BOT_TOKEN=your_bot_token              # Get from @BotFather

# Database Configuration
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/dbname

# Admin Configuration
ADMIN_IDS=123456789,987654321         # Comma-separated Telegram user IDs
                                      # First ID is super admin

# Google Drive OAuth (NEW! For /auth command support)
G_DRIVE_CLIENT_ID=your_client_id.apps.googleusercontent.com
G_DRIVE_CLIENT_SECRET=your_client_secret

# Optional: Channel Configuration
CHANNEL_ID=-1001234567890             # Optional: Broadcast channel
```

**Getting Your Telegram User ID:**
1. Start a chat with [@userinfobot](https://t.me/userinfobot)
2. It will reply with your User ID
3. Add to `ADMIN_IDS` in `.env`

### Step 5: Run the Bot

**For Local Development:**
```bash
python bot.py
```

**For Production (with Flask health checks):**
```bash
python server.py
```

**Using Gunicorn (recommended for production):**
```bash
gunicorn server:app --bind 0.0.0.0:8080 --workers 1 --timeout 0
```

---

## 📁 Project Structure

```
Google-Drive-Access-Manager-Bot/
├── bot.py                  # Main bot application with scheduler
├── server.py               # Flask wrapper for deployment
├── config.py               # Environment configuration
├── requirements.txt        # Python dependencies
├── credentials.json        # Google OAuth credentials (not in repo)
├── token.json             # Generated OAuth token (not in repo)
├── .env                   # Environment variables (not in repo)
├── .env.example           # Example environment file
│
├── plugins/               # Feature modules
│   ├── __init__.py
│   ├── start.py          # Welcome, help, cancel handlers
│   ├── auth.py           # ✨ NEW! OAuth authentication (/auth, /revoke)
│   ├── grant.py          # 3-mode grant system
│   ├── manage.py         # Folder management
│   ├── expiry.py         # Expiry dashboard & bulk import
│   ├── analytics.py      # Analytics dashboard & CSV export
│   ├── search.py         # Smart search with Select All
│   ├── stats.py          # Statistics dashboard
│   ├── info.py           # System monitor
│   ├── settings.py       # Bot configuration
│   ├── channel.py        # Channel integration
│   ├── logs.py           # Activity logs
│   └── csv_export.py     # CSV export utilities
│
├── services/             # Core services
│   ├── __init__.py
│   ├── database.py       # MongoDB operations (Motor)
│   ├── drive.py          # Google Drive API with caching
│   └── broadcast.py      # Telegram broadcasting
│
├── utils/                # Utility functions
│   ├── __init__.py
│   ├── filters.py        # Admin & state filters
│   ├── states.py         # Conversation states
│   ├── validators.py     # Email validation
│   ├── time.py           # IST timezone & safe_edit helper
│   └── pagination.py     # Pagination & sorting
│
├── docs/                 # Documentation
│   ├── README.md
│   ├── UI_GUIDE.md
│   ├── DEPLOYMENT.md
│   ├── Changelog.md
│   ├── DATABASE_MAINTENANCE.md
│   ├── DUPLICATE_PREVENTION.md
│   ├── DATABASE_CLEANUP_GUIDE.md
│   ├── Security audit report.MD
│   ├── CODE_ANALYSIS_REPORT.md
│   └── [more documentation files]
│
├── Procfile              # Heroku deployment
└── render.yaml           # Render deployment
```

---

## 🚀 Deployment

### Deploy to Render

Render is the recommended platform for deployment (free tier available).

#### Quick Deploy Button

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

#### Manual Deployment

1. Fork this repository
2. Create account on [Render](https://render.com/)
3. Create new **Web Service**
4. Connect your GitHub repository
5. Configure:
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python server.py`
6. Add environment variables:
   - API_ID, API_HASH, BOT_TOKEN
   - MONGO_URI, ADMIN_IDS
   - **G_DRIVE_CLIENT_ID, G_DRIVE_CLIENT_SECRET** (for /auth command)
7. Deploy!
8. After deployment, use `/auth` command in bot to connect Google Drive

**No need to upload credentials.json or token.json!** ✨  
The new OAuth system handles everything through the bot interface.

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions.

### Deploy to Heroku

1. Create Heroku account
2. Install Heroku CLI
3. Login and create app:
   ```bash
   heroku login
   heroku create your-app-name
   ```
4. Set environment variables:
   ```bash
   heroku config:set API_ID=your_api_id
   heroku config:set API_HASH=your_api_hash
   heroku config:set BOT_TOKEN=your_bot_token
   heroku config:set MONGO_URI=your_mongo_uri
   heroku config:set ADMIN_IDS=your_admin_ids
   heroku config:set G_DRIVE_CLIENT_ID=your_client_id
   heroku config:set G_DRIVE_CLIENT_SECRET=your_client_secret
   ```
5. Deploy:
   ```bash
   git push heroku main
   ```
6. After deployment, use `/auth` command to connect Google Drive

**The new OAuth system means no file uploads needed!** ✨

### Deploy to VPS

For VPS deployment (DigitalOcean, Linode, etc.):

```bash
# Install dependencies
sudo apt update
sudo apt install python3.11 python3-pip git

# Clone and setup
git clone https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot.git
cd Google-Drive-Access-Manager-Bot
pip3 install -r requirements.txt

# Configure .env file
nano .env

# Run with systemd service (recommended)
sudo nano /etc/systemd/system/drive-bot.service
```

**Sample systemd service:**
```ini
[Unit]
Description=Google Drive Access Manager Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Google-Drive-Access-Manager-Bot
ExecStart=/usr/bin/python3 /home/ubuntu/Google-Drive-Access-Manager-Bot/server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable drive-bot
sudo systemctl start drive-bot
```

---

## 🛠️ Maintenance

### Database Cleanup

#### Check Database Statistics

```bash
cd scripts/
python3 check_duplicates.py
```

**Sample Output:**
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

#### Remove Duplicates

```bash
cd scripts/
python3 remove_duplicates.py
```

**Features:**
- 🔄 Interactive confirmation prompts
- 📊 Progress indicators with emoji
- 🇮🇳 Malayalam language support (മലയാളം)
- ✅ Safe operation (doesn't touch Drive permissions)
- 💾 Backup recommendations before execution

See [docs/DUPLICATE_PREVENTION.md](docs/DUPLICATE_PREVENTION.md) for detailed guide.

### Backup & Restore

**Backup MongoDB:**
```bash
mongodump --uri="mongodb+srv://user:pass@cluster.mongodb.net/dbname" --out=./backup
```

**Restore MongoDB:**
```bash
mongorestore --uri="mongodb+srv://user:pass@cluster.mongodb.net/dbname" ./backup
```

---

## 📚 Documentation

### Core Documentation
- [README.md](README.md) - This file (overview & setup)
- [UI Guide](docs/UI_GUIDE.md) - Complete user interface guide
- [Deployment Guide](docs/DEPLOYMENT.md) - Deploy to Render/Heroku
- [Changelog](docs/Changelog.md) - Version history & updates

### Database & Maintenance
- [Database Maintenance](docs/DATABASE_MAINTENANCE.md) - DB management
- [Duplicate Prevention](docs/DUPLICATE_PREVENTION.md) - Prevention system
- [Database Cleanup Guide](docs/DATABASE_CLEANUP_GUIDE.md) - Malayalam instructions

### Security & Quality
- [Security Audit](docs/Security%20audit%20report.MD) - Security review
- [Code Analysis](docs/CODE_ANALYSIS_REPORT.md) - Code quality
- [Error Reports](docs/ERROR_CHECK_SUMMARY.md) - Error handling

---

## 🆕 What's New in v2.2.2

### 🐛 Critical Bug Fix — Revoke Not Working

**Problem:** The "🗑 Revoke" button in the **Expiry Dashboard** was silently failing — access was never actually removed from Google Drive.

**Root Cause:** `drive_service.remove_access()` requires a `db` (database) parameter to fetch Drive credentials, but it was missing in 3 places inside `plugins/expiry.py`:

| Location | Function | Status |
|----------|----------|--------|
| Line 240 | `execute_revoke` (single revoke) | ✅ Fixed |
| Line 613 | `bulk_revoke_execute` (bulk revoke) | ✅ Fixed |
| Line 708 | `notif_revoke_grant` (notification revoke) | ✅ Fixed |

**What was affected:**
- 🗑 Single grant revoke from Expiry Dashboard
- 🗑 Bulk Revoke All / Revoke Expiring Only
- 🗑 Revoke from expiry notification messages

**Not affected:** Revoke via **Manage Folders** menu (that was working correctly).

> ⚠️ **If you were on v2.2.1**, update `plugins/expiry.py` immediately.

---

## 🆕 What's New in v2.2.1

### 🔑 OAuth Authentication System ✨ **MAJOR UPDATE!**
- **NEW** In-bot OAuth with `/auth` command
- **NEW** Cloud-friendly authentication (no file uploads needed!)
- **NEW** Per-admin Google account support
- **NEW** `/revoke` command for easy disconnection
- **NEW** `/authstatus` to check connection status
- **NEW** Encrypted credential storage in MongoDB
- **IMPROVED** Perfect for Render/Heroku deployments

### ✨ Select All Feature
- **NEW** "✅ Select All" button in Select & Revoke interface
- **NEW** "☐ Unselect All" button for bulk deselection
- **NEW** Smart toggle - adapts based on selection state
- **NEW** Real-time counter - "X selected | Y total"
- **IMPROVED** Individual folder toggle with checkbox UI

### 🗄️ Database Cleanup Tools
- **NEW** `check_duplicates.py` - Database statistics viewer
- **NEW** `remove_duplicates.py` - Safe duplicate cleanup
- **NEW** Malayalam language support (മലയാളം)
- **ACHIEVED** 67.6% database reduction (4,010 → 1,299)

### 📚 Documentation Upgrades
- **NEW** Malayalam installation guides
- **NEW** Step-by-step cleanup instructions
- **NEW** Comprehensive troubleshooting
- **IMPROVED** All docs updated with new features

---

## 📊 Statistics

### Project Metrics
- 📁 **Files:** 30+ files across 5 directories
- 📝 **Code:** 5,400+ lines of Python
- 🔧 **Endpoints:** 90+ admin-protected handlers
- 📚 **Docs:** 15+ documentation files
- ⚡ **Async:** 100% async/await architecture
- 🔒 **Security:** 100% admin-protected endpoints
- 📊 **Collections:** 6 MongoDB collections
- 🎯 **Grant Modes:** 4 different workflows
- ⏰ **Expiry Options:** 6 duration choices

### Real-World Performance
- 🌍 **Environment:** Production-tested
- 👥 **Users:** Multiple admin support
- 📂 **Folders:** 120+ actively managed
- 📊 **Grants:** 1,000+ tracked permissions
- ⚡ **Response Time:** <1s average
- 🔄 **Uptime:** 99.9%
- 💾 **Database:** Optimized with indexes
- 🚀 **Scalability:** Handles 1000+ concurrent operations

---

## 🗺️ Roadmap

### v2.3.0 (Q1 2026)
- [ ] 🔄 Invert selection button
- [ ] 🎯 Select by role (readers/editors)
- [ ] ⏰ Select by expiry time
- [ ] 🔄 Batch extend multiple grants
- [ ] 📧 Email notifications to users
- [ ] 📊 Enhanced analytics with charts

### v2.4.0 (Q2 2026)
- [ ] 🤖 Auto-extend rules
- [ ] 📅 Scheduled grants (future start)
- [ ] 👤 User self-service portal
- [ ] 🔗 REST API for integrations
- [ ] 🔔 Webhook support

### v3.0.0 (Future Vision)
- [ ] 🤖 AI-powered access recommendations
- [ ] 🔍 Anomaly detection
- [ ] 📱 Native mobile app
- [ ] 🏢 Multi-tenant support
- [ ] 🌐 Multi-Drive management
- [ ] ☁️ Shared Drive support

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Make** your changes
4. **Test** thoroughly
5. **Commit** (`git commit -m 'Add AmazingFeature'`)
6. **Push** to branch (`git push origin feature/AmazingFeature`)
7. **Open** a Pull Request

### Development Guidelines

- ✅ Follow existing code style and structure
- ✅ Add comments for complex logic
- ✅ Update documentation for new features
- ✅ Test with real data before PR
- ✅ Consider backwards compatibility
- ✅ Add error handling
- ✅ Use async/await consistently

### Bug Reports

Found a bug? Please include:
- 🐛 Clear description
- 📝 Steps to reproduce
- 💻 Expected vs actual behavior
- 📊 Environment details
- 📸 Screenshots (if applicable)

---

## 📞 Support

### Get Help

- 📋 **Issues:** [GitHub Issues](https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot/discussions)
- 📚 **Bot Help:** Type `/help` in the bot
- 📖 **Documentation:** Check [docs/](docs/) folder

### FAQ

**Q: Revoke button in Expiry Dashboard is not working — access is not removed!**  
A: This was a bug in v2.2.1. Update `plugins/expiry.py` to v2.2.2 to fix it. The Manage Folders revoke still worked correctly in v2.2.1.

**Q: How do I authorize Google Drive on Render/Heroku?**  
A: Use the new `/auth` command! Just add `G_DRIVE_CLIENT_ID` and `G_DRIVE_CLIENT_SECRET` to your environment variables, then run `/auth` in the bot.

**Q: Do I need to upload credentials.json anymore?**  
A: No! The new OAuth system (v2.2.1+) handles everything through the bot. Just use `/auth` command.

**Q: How do I get my Telegram User ID?**  
A: Send `/start` to [@userinfobot](https://t.me/userinfobot)

**Q: Can I use a different database?**  
A: Currently only MongoDB is supported. PostgreSQL support is planned.

**Q: Is this free?**  
A: Yes! The bot is open source (MIT License). You only pay for hosting and MongoDB (free tiers available).

**Q: How many folders can I manage?**  
A: No hard limit. Successfully tested with 500+ folders.

**Q: Can multiple admins use the bot?**  
A: Yes! Add all admin IDs to `ADMIN_IDS` (comma-separated). Each admin can connect their own Google account via `/auth`.

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### What This Means

✅ Commercial use  
✅ Modification  
✅ Distribution  
✅ Private use  

**Attribution required** - Please keep credits in the code.

---

## 🙏 Acknowledgments

### Built With Love Using

- [Pyrofork](https://github.com/Mayuri-Chan/pyrofork) - Modern Telegram Bot Framework
- [MongoDB](https://www.mongodb.com/) - NoSQL Database
- [Google Drive API](https://developers.google.com/drive) - Drive Integration
- [Motor](https://motor.readthedocs.io/) - Async MongoDB Driver
- [Flask](https://flask.palletsprojects.com/) - Web Framework for Health Checks

### Special Thanks

- 🌟 All contributors and users who reported issues
- 🐛 Beta testers who helped find bugs
- 💡 Community members who suggested features
- 📚 Open source community for amazing tools

---

## ⭐ Star History

If you find this project useful, please consider giving it a ⭐ on GitHub!

<div align="center">

[![Star History Chart](https://api.star-history.com/svg?repos=muhammedadnank/Google-Drive-Access-Manager-Bot&type=Date)](https://star-history.com/#muhammedadnank/Google-Drive-Access-Manager-Bot&Date)

</div>

---

## 🔗 Quick Links

- [🚀 Get Started](#-installation)
- [✨ View Features](#-key-features)
- [📚 Read Documentation](#-documentation)
- [🚀 Deploy Now](#-deployment)
- [🛠️ Maintenance Scripts](#️-maintenance)
- [🤝 Contribute](#-contributing)
- [📞 Get Support](#-support)

---

<div align="center">

**Version:** v2.2.2  
**Last Updated:** February 19, 2026  
**Status:** ✅ Production Ready  
**Stability:** Stable

Built with ❤️ using Pyrofork, MongoDB & Google Drive API

---

**[⬆ Back to Top](#-google-drive-access-manager-bot)**

</div>
