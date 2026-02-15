# 📂 Google Drive Access Manager Bot

A powerful Telegram bot built with **Pyrofork** to manage Google Drive folder permissions at scale. Multi-email grants, timed expiry, bulk import, **analytics dashboard** — all from Telegram.

> **v2.1.3 Update:** NEW Analytics Dashboard with Top 15 insights, Pagination fixes, and Performance improvements! 📊  
> **v2.1.2 Update:** Database integrity enforcement with duplicate prevention system 🔒  
> **v2.1.1 Update:** Security patches for interactive buttons and improved access control 🔒

---

## 🚀 Features

### ➕ Grant Access (3 Modes)

| Mode | Description |
|------|-------------|
| 👤 One Email → One Folder | Classic single grant |
| 📂 One Email → Multi Folders | Checkbox-style multi-folder selection |
| 👥 Multi Emails → One Folder | Batch grant with duplicate detection |

- Email validation & duplicate access protection
- Duration: 1h, 6h, 1d, 7d, 30d (default), ♾️ Permanent
- Viewers get expiry timer — Editors always permanent


### ⏰ Timed Access & Auto-Expire

- Set expiry timers on viewer grants
- Background task auto-revokes expired access every 5 min
- Logged as auto_revoke with full audit trail

### 📥 Bulk Import & Scan Report

- Full Drive scan → generates drive_scan_report.txt
- Creates 40-day expiry for all new viewer permissions
- Live progress: Scanning... (30/120 folders)
- Skips owners, editors, and duplicates

### 📂 Manage Folders

- Smart numeric sorting ([001-050] → [051-100])
- View users per folder with **expiry date**, change roles (Viewer ↔️ Editor), remove access
- **Revoke All:** Remove access for ALL users in a folder with one click
- Folder caching with configurable TTL + manual 🔄 refresh

### ⏰ Expiry Dashboard

- **[IMPROVED]** Unlimited pagination - access all active grants
- View all active timed grants with time remaining
- **Inline Actions:** Notification messages now include **Extend (+7d)** and **Revoke** buttons directly
- 🔄 Extend access (+1h, +6h, +1d, +7d, +14d, +30d)
- 🗑 Revoke Now — remove access immediately
- **Configurable page size** (5, 10, 20, 30 grants per page)

### 📊 **Analytics Dashboard** ✨ NEW!

Get instant insights into your grant expiry patterns:

#### **⏰ Expiry Timeline**
- ⚠️ Urgent (< 24 hours)
- 📅 This Week (1-7 days)
- 📅 This Month (8-30 days)
- 📅 Later (30+ days)

#### **📂 Top 15 Expiring Folders**
- See which folders have most expiring grants
- Identify popular content
- Plan renewals efficiently

#### **👥 Top 15 Expiring Users**
- Power users with many grants
- Consider permanent access for frequent users
- Easy user management

#### **📥 CSV Export**
- Download complete expiry report
- Excel-ready format with IST timestamps
- Status indicators (Urgent/Week/Month/Later)
- Perfect for auditing and analysis

**Quick Access:** Expiry Dashboard → 📊 Analytics

### 📊 Activity Logs

- Structured log types with icons: ➕ Grant · 🗑 Remove · 🔄 Role Change · ▪️ Auto Revoke · 📥 Bulk Import
- Soft delete — logs are never permanently lost
- Paginated view (configurable per page)
- Filter by action type
- CSV export for custom date ranges

### 📢 Telegram Channel Integration

- Broadcast grants, revokes, and alerts to a configured channel
- Auto-detect channel ID (forward message)
- Logs "PeerIdInvalid" handling with robust resolution
- Daily status summary and error alerts

### 📊 Stats Dashboard (/stats)

- Daily / weekly / monthly activity counts
- **Expiring Soon:** Counter for grants expiring within 24 hours
- Busiest day, most accessed folder
- Active grants overview
- Accessible via button or command

### 🔧 System Monitor (/info)

- Bot uptime, version, Python/Pyrofork version
- Drive API, MongoDB, Telegram connection status
- Auto-expire scheduler status + last run details
- System resources (RAM, CPU, Disk usage)
- Super admin only (first ID in ADMIN_IDS)

### ⚙️ Settings

- Default access role (Viewer/Editor)
- **Folder page size** (3-10 folders per page)
- **Expiry page size** (10-100 grants per page)
- Cache TTL configuration (5-60 minutes)
- Notification toggles
- **Channel Configuration** (ID setup & testing)

### 🔐 Security

- Admin-only access via MongoDB
- Super admin role for system commands
- All credentials via .env
- Email normalization and validation
- **Duplicate prevention system** with unique indexes
- NoSQL injection protection
- Input sanitization

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
2. Enable Google Drive API
3. Create OAuth 2.0 Client ID (Desktop app)
4. Download as credentials.json
5. Run locally once to complete OAuth flow

### 3. Configure

Copy .env.example to .env:

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
│   ├── manage.py       # Folder permission management
│   ├── expiry.py       # Expiry dashboard + bulk import + scan report
│   ├── analytics.py    # 📊 NEW! Analytics dashboard + CSV export
│   ├── stats.py        # /stats analytics dashboard
│   ├── info.py         # /info system monitor
│   ├── settings.py     # Bot settings
│   ├── channel.py      # Channel integration settings
│   ├── search.py       # User search functionality
│   ├── csv_export.py   # CSV export utilities
│   └── logs.py         # Structured activity logs
├── services/
│   ├── database.py     # MongoDB (Motor) — all collections + analytics
│   ├── drive.py        # Google Drive API v3 + caching
│   └── broadcast.py    # Telegram Channel Broadcasting
├── utils/
│   ├── filters.py      # Admin & state filters
│   ├── states.py       # Conversation state constants
│   ├── validators.py   # Email validation
│   ├── time.py         # IST Timezone helpers + safe_edit() utility
│   └── pagination.py   # Pagination + checkbox keyboard + sorting
├── requirements.txt
├── Procfile
└── render.yaml
```

---

## 🎮 Bot Commands

| Command | Access | Description |
|---------|--------|-------------|
| /start | Admin | Main menu with bot info |
| /help | Admin | Feature reference |
| /cancel | Admin | Cancel current operation |
| /stats | Admin | Activity analytics dashboard |
| /info | Super Admin | System monitor |
| /id | Anyone | Show Telegram user ID |

---

## 🏠 Main Menu

```
╔════════════════════════════╗
  🗂 Drive Access Manager
╚════════════════════════════╝

👋 Welcome back, Admin!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 BOT INFO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏷 Name     : Drive Access Manager
👤 Username : @YourBot
🔄 Version  : v2.1.3
⏱️ Uptime   : 3h 24m
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
```
[➕ Grant Access]      [📂 Manage Folders]
[⏰ Expiry Dashboard]  [📋 Access Logs] 
[🔍 Search User]       [📊 Statistics]
[⚙️ Settings]          [💡 Help & Guide]
[🔧 System Info]       [📊 Analytics]
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
| `grants` | Timed access grants with expiry + unique index |

---

## 📊 Analytics Dashboard Preview

```
📊 Expiry Analytics

━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ EXPIRY TIMELINE
━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ < 24 hours:     8 grants
📅 1-7 days:       143 grants
📅 8-30 days:      856 grants
📅 30+ days:       263 grants
📊 Total Active: 1,270

━━━━━━━━━━━━━━━━━━━━━━━━━━
📂 TOP EXPIRING FOLDERS (Top 15)
━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Leo AD 2500 [601-700]
   📊 45 expiring grants
2. Leo AD 2500 [701-800]
   📊 38 expiring grants
...

━━━━━━━━━━━━━━━━━━━━━━━━━━
👥 TOP EXPIRING USERS (Top 15)
━━━━━━━━━━━━━━━━━━━━━━━━━━
1. user1@gmail.com
   📊 12 folders
2. user2@gmail.com
   📊 10 folders
...

[📥 Export Full Report] [🔄 Refresh] [⬅️ Back]
```

---

## 🚀 Deploy

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for Render deployment guide.

### Quick Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. Click the button above
2. Fill in environment variables
3. Deploy!

---

## 🎯 Use Cases

### For Content Creators
- Manage subscriber access to premium content
- Time-limited access to courses/resources
- Automatic expiry for trial periods

### For Teams
- Grant temporary access to contractors
- Manage project-based permissions
- Track access across multiple folders

### For Educators
- Semester-based access to course materials
- Student group management
- Automated cleanup after course end

### For Businesses
- Client access management
- Partner collaboration permissions
- Audit trail for compliance

---

## 📈 Performance

**Tested at Scale:**
- ✅ 1,270+ active grants
- ✅ 4,000+ total grants
- ✅ 120+ folders
- ✅ <1 second response time
- ✅ Background tasks every 5 minutes
- ✅ 87% disk usage optimization

**Optimizations:**
- MongoDB indexing for fast queries
- Folder caching with TTL
- Async/await throughout
- Rate limiting for Drive API
- Efficient pagination

---

## 🔒 Security Features

### Database Level
- ✅ Unique indexes prevent duplicates
- ✅ Email normalization (injection prevention)
- ✅ NoSQL injection protection
- ✅ Type validation on all inputs

### Application Level
- ✅ Admin-only access (`is_admin` filter on all 90+ endpoints)
- ✅ Input sanitization
- ✅ Rate limiting
- ✅ Error handling without stack traces
- ✅ `safe_edit()` helper — graceful Telegram API error handling

### Audit & Compliance
- ✅ Complete activity logs
- ✅ Soft delete (data retention)
- ✅ CSV export for audits
- ✅ Channel broadcasting for transparency

---

## 🆕 What's New in v2.1.3

### ✨ Analytics Dashboard
- **NEW** Visual expiry timeline breakdown
- **NEW** Top 15 expiring folders analysis
- **NEW** Top 15 users with most grants
- **NEW** CSV export with detailed reports
- **NEW** Real-time refresh capability

### 🔧 Bug Fixes & Stability
- **FIXED** `MESSAGE_NOT_MODIFIED` error — all 95 message edit calls now silently handle Telegram's "same content" rejection via `safe_edit()` helper
- **FIXED** IST (Kolkata) timezone with AM/PM format throughout — no more UTC timestamps in UI
- **FIXED** `asyncio.Semaphore` runtime error on startup — lazy initialization inside running event loop
- **FIXED** All admin-only endpoints now properly protected with `is_admin` filter

### 🔧 Improvements
- **FIXED** Pagination now shows all grants (removed 100-grant limit)
- **IMPROVED** Page size now configurable (5-100 grants)
- **IMPROVED** Better performance for large datasets
- **ENHANCED** User interface with clearer sections

### 📊 Analytics Features
- Instant insights into grant patterns
- Identify popular folders
- Track power users
- Export for external analysis
- IST timezone throughout

---

## 📚 Documentation

- [UI Guide](docs/UI_GUIDE.md) - Complete user interface guide
- [Deployment Guide](docs/DEPLOYMENT.md) - Deploy to Render
- [Changelog](docs/CHANGELOG.md) - Version history
- [Database Maintenance](docs/DATABASE_MAINTENANCE.md) - DB management
- [Security Audit](docs/Security%20audit%20report.MD) - Security review

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot/issues)
- **Discussions:** [GitHub Discussions](https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot/discussions)
- **Documentation:** Check `/help` in bot

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

Built with:
- [Pyrofork](https://github.com/Mayuri-Chan/pyrofork) - Telegram Bot Framework
- [MongoDB](https://www.mongodb.com/) - Database
- [Google Drive API](https://developers.google.com/drive) - Drive Integration
- [Motor](https://motor.readthedocs.io/) - Async MongoDB Driver
- [Flask](https://flask.palletsprojects.com/) - Web Framework

---

## ⭐ Star History

If you find this project useful, please consider giving it a ⭐ on GitHub!

---

## 🔮 Roadmap

### v2.2.0 (Planned)
- [ ] Auto-extend rules (automatic renewals)
- [ ] User self-service portal
- [ ] Advanced filtering options
- [ ] Scheduled grants (future start date)
- [ ] Email notifications

### v2.3.0 (Future)
- [ ] Multi-Drive support
- [ ] Shared Drive management
- [ ] REST API for integrations
- [ ] Mobile app
- [ ] Advanced analytics with charts

---

**Version:** v2.1.3  
**Last Updated:** February 15, 2026  
**Status:** ✅ Production Ready

Built with ❤️ using Pyrofork, MongoDB & Google Drive API
