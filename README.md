# 📂 Google Drive Access Manager Bot

A powerful Telegram bot built with **Pyrofork** to manage Google Drive folder permissions at scale. Multi-email grants, timed expiry, bulk import, **analytics dashboard**, **smart selection tools** — all from Telegram.

> **v2.1.4 Update:** Select All/Unselect All feature + Database Cleanup Tools 🎯  
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

### 🔍 Search & Revoke ✨ **UPGRADED!**

#### Smart Selection Tools
- **✅ Select All** - Bulk select all folders with one click
- **☐ Unselect All** - Deselect everything instantly
- **Individual Toggle** - Click any folder to toggle selection
- **Smart Button** - Automatically switches between Select/Unselect All
- **Selection Counter** - Shows "X selected | Y total" in real-time

#### Search Features
- Search by email or folder name
- Advanced filters (Role: Reader/Writer, Status: Active/Expired/Revoked)
- View all active grants for any user
- **Select & Revoke** - Choose specific folders to revoke
- **Revoke All** - Remove all access for a user

#### Workflow Example
```
1. /search user@example.com
2. Click "☑️ Select & Revoke"
3. Click "✅ Select All" (all folders selected)
4. Click unwanted folders to unselect
5. Click "🗑 Revoke Selected (5)"
6. Confirm → Done!
```

### ⏰ Expiry Dashboard

- **[IMPROVED]** Unlimited pagination - access all active grants
- View all active timed grants with time remaining
- **Inline Actions:** Notification messages now include **Extend (+7d)** and **Revoke** buttons directly
- 🔄 Extend access (+1h, +6h, +1d, +7d, +14d, +30d)
- 🗑 Revoke Now — remove access immediately
- **Configurable page size** (5, 10, 20, 30 grants per page)

### 📊 **Analytics Dashboard** ✨ 

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

### 🗄️ Database Maintenance ✨ **NEW!**

#### Duplicate Prevention System
- **MongoDB Unique Index** - Prevents duplicate active grants at database level
- **Email Normalization** - Automatic lowercase conversion
- **Race Condition Protection** - Atomic operations prevent concurrent duplicates
- **Bulk Import Protection** - Set-based deduplication during imports

#### Cleanup Tools
- **Check Duplicates Script** - View database statistics
- **Remove Duplicates Script** - Safe cleanup with confirmation
- **Backup Friendly** - Always recommends backup before operations
- **Audit Trail** - Soft-delete duplicate entries for history

**Performance Impact:** Minimal write overhead (+1ms), 20x faster reads

See [docs/DUPLICATE_PREVENTION.md](docs/DUPLICATE_PREVENTION.md) for details.

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
│   ├── analytics.py    # 📊 Analytics dashboard + CSV export
│   ├── stats.py        # /stats analytics dashboard
│   ├── info.py         # /info system monitor
│   ├── settings.py     # Bot settings
│   ├── channel.py      # Channel integration settings
│   ├── search.py       # ✨ User search with Select All feature
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
├── scripts/            # ✨ NEW! Maintenance scripts
│   ├── check_duplicates.py     # Database statistics tool
│   └── remove_duplicates.py    # Duplicate cleanup script
├── docs/              # Comprehensive documentation
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
| /search | Admin | Search grants by email/folder |
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
🔄 Version  : v2.1.4
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
- ✅ 4,000+ total grants (after duplicate cleanup: 1,299)
- ✅ 120+ folders
- ✅ <1 second response time
- ✅ Background tasks every 5 minutes
- ✅ 87% disk usage optimization
- ✅ 67.6% database size reduction after cleanup

**Optimizations:**
- MongoDB indexing for fast queries
- Folder caching with TTL
- Async/await throughout
- Rate limiting for Drive API
- Efficient pagination
- Duplicate prevention at database level

---

## 🔒 Security Features

### Database Level
- ✅ Unique indexes prevent duplicates
- ✅ Email normalization (injection prevention)
- ✅ NoSQL injection protection
- ✅ Type validation on all inputs
- ✅ Atomic operations for race condition prevention

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
- ✅ Duplicate cleanup with audit trail

---

## 🆕 What's New in v2.1.4

### ✨ Select All Feature
- **NEW** "✅ Select All" button in Select & Revoke interface
- **NEW** "☐ Unselect All" button for quick deselection
- **NEW** Smart toggle - button changes based on selection state
- **NEW** Real-time counter showing "X selected | Y total"
- **IMPROVED** Individual folder toggle with checkbox UI

### 🗄️ Database Cleanup Tools
- **NEW** `check_duplicates.py` - View database statistics
- **NEW** `remove_duplicates.py` - Safe duplicate cleanup script
- **NEW** Malayalam language support in scripts
- **NEW** Comprehensive documentation in [DUPLICATE_PREVENTION.md](docs/DUPLICATE_PREVENTION.md)
- **ACHIEVED** 67.6% database size reduction (4,010 → 1,299 entries)

### 📚 Documentation Upgrades
- **NEW** Complete installation guides in Malayalam
- **NEW** Step-by-step cleanup instructions
- **NEW** Troubleshooting guides
- **IMPROVED** All documentation updated with new features

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

---

## 📚 Documentation

### Core Documentation
- [README.md](README.md) - This file (overview & setup)
- [UI Guide](docs/UI_GUIDE.md) - Complete user interface guide
- [Deployment Guide](docs/DEPLOYMENT.md) - Deploy to Render
- [Changelog](docs/Changelog.md) - Version history

### Database & Maintenance
- [Database Maintenance](docs/DATABASE_MAINTENANCE.md) - DB management guide
- [Duplicate Prevention](docs/DUPLICATE_PREVENTION.md) - Duplicate prevention system
- [Database Cleanup Guide](docs/DATABASE_CLEANUP_GUIDE.md) - Malayalam cleanup instructions

### Security & Code Quality
- [Security Audit](docs/Security%20audit%20report.MD) - Security review
- [Code Analysis](docs/CODE_ANALYSIS_REPORT.md) - Code quality report
- [Error Reports](docs/ERROR_CHECK_SUMMARY.md) - Error handling analysis

### Scripts & Tools
- `scripts/check_duplicates.py` - Database statistics tool
- `scripts/remove_duplicates.py` - Duplicate cleanup script with Malayalam UI

---

## 🛠️ Maintenance Scripts

### Check Database Statistics

```bash
cd scripts/
python3 check_duplicates.py
```

**Output:**
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

### Remove Duplicate Entries

```bash
cd scripts/
python3 remove_duplicates.py
```

**Features:**
- Interactive confirmation
- Progress indicators
- Malayalam language support
- Safe operation (doesn't affect Drive permissions)
- Backup recommendations

See [docs/DUPLICATE_PREVENTION.md](docs/DUPLICATE_PREVENTION.md) for detailed instructions.

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Development Guidelines
- Follow existing code style
- Add comments for complex logic
- Update documentation
- Test with real data
- Consider backwards compatibility

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot/issues)
- **Discussions:** [GitHub Discussions](https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot/discussions)
- **Documentation:** Check `/help` in bot
- **Email:** support@example.com (if applicable)

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

Special thanks to all contributors and users who reported issues and suggested improvements!

---

## ⭐ Star History

If you find this project useful, please consider giving it a ⭐ on GitHub!

---

## 🔮 Roadmap

### v2.2.0 (Planned)
- [ ] Advanced selection tools (Invert selection, Select by role)
- [ ] Batch operations (Extend multiple grants at once)
- [ ] Auto-extend rules (automatic renewals)
- [ ] User self-service portal
- [ ] Scheduled grants (future start date)

### v2.3.0 (Future)
- [ ] Email notifications to users
- [ ] Multi-Drive support
- [ ] Shared Drive management
- [ ] REST API for integrations
- [ ] Mobile app
- [ ] Advanced analytics with charts
- [ ] Integration with Google Workspace Admin

### v3.0.0 (Vision)
- [ ] AI-powered access recommendations
- [ ] Automated compliance checking
- [ ] Role-based access control (RBAC)
- [ ] Multi-tenant support
- [ ] Enterprise features

---

## 📊 Statistics

**Project Metrics:**
- 📁 15+ files
- 📝 5,000+ lines of code
- 🔧 90+ admin endpoints
- 📚 10+ documentation files
- ⚡ 100% async/await
- 🔒 100% admin-protected endpoints
- 📊 6 MongoDB collections
- 🎯 4 grant modes
- ⏰ 6 expiry duration options

**Real-World Usage:**
- 🌍 Production-tested
- 👥 Multiple admin users
- 📂 120+ folders managed
- 📊 1,000+ grants tracked
- ⚡ <1s average response time
- 🔄 99.9% uptime

---

**Version:** v2.1.4  
**Last Updated:** February 15, 2026  
**Status:** ✅ Production Ready

Built with ❤️ using Pyrofork, MongoDB & Google Drive API

---

## 🌟 Quick Links

- [Installation Guide](#-setup)
- [Feature List](#-features)
- [Documentation](#-documentation)
- [Deployment](#-deploy)
- [Maintenance Scripts](#️-maintenance-scripts)
- [Support](#-support)

---

**Need help?** Check out our [comprehensive documentation](docs/) or open an [issue](https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot/issues)!
