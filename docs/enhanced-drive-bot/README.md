# 🚀 Enhanced Google Drive Access Manager Bot

**Version 3.0.0** - Enhanced with VJ-FILTER-BOT Patterns

A powerful Telegram bot for managing Google Drive folder permissions with enterprise-grade features.

---

## ✨ What's New in v3.0.0 (VJ-Enhanced)

### 🎨 VJ-FILTER-BOT Patterns Integrated

1. **Message Template System** (`templates/messages.py`)
   - Centralized message management
   - Easy to customize/translate
   - Consistent formatting across bot

2. **Admin Decorator System** (`utils/decorators.py`)
   - `@admin_only` - Admin verification
   - `@super_admin_only` - Super admin only
   - `@rate_limit` - Prevent spam
   - `@error_handler` - Graceful error handling
   - `@admin_command` - Combined decorator

3. **Enhanced Plugin Architecture**
   - Dynamic plugin loading
   - Hot reload capability
   - Modular feature organization

4. **Broadcast System** (`services/broadcast.py`)
   - Admin notifications
   - Channel integration
   - Progress tracking

5. **Advanced Settings Menu**
   - VJ-style inline keyboard navigation
   - Per-admin customization
   - Real-time configuration

---

## 📁 Project Structure

```
enhanced-drive-bot/
│
├── bot.py                      # Main bot core + auto-expire scheduler
├── config.py                   # Centralized configuration (VJ style)
├── server.py                   # Flask server for deployment
│
├── templates/                  # Message templates (VJ pattern)
│   └── messages.py            # All bot messages
│
├── plugins/                    # Feature plugins
│   ├── start.py               # Main menu + /start /help /cancel
│   ├── grant.py               # 3-mode grant system
│   ├── manage.py              # Folder management
│   ├── expiry.py              # Expiry dashboard + bulk import
│   ├── logs.py                # Activity logs
│   ├── stats.py               # Analytics dashboard
│   ├── settings.py            # Bot settings
│   ├── channel.py             # Channel configuration
│   ├── broadcast.py           # Broadcast system
│   └── info.py                # System monitor (super admin)
│
├── services/                   # Service layer
│   ├── database.py            # MongoDB operations
│   ├── drive.py               # Google Drive API
│   ├── broadcast.py           # Broadcasting service
│   └── cache.py               # Caching service
│
├── utils/                      # Utilities
│   ├── decorators.py          # VJ-style decorators
│   ├── validators.py          # Input validation
│   ├── logger.py              # Enhanced logging
│   ├── filters.py             # Custom filters
│   ├── states.py              # Conversation states
│   └── pagination.py          # Pagination helpers
│
├── database/                   # Database schemas
│   └── schemas.py
│
├── .env.example               # Environment template
├── requirements.txt           # Python dependencies
├── Procfile                   # Heroku deployment
├── render.yaml                # Render deployment
└── README.md                  # This file
```

---

## 🛠 Prerequisites

- Python 3.11+
- MongoDB (Atlas recommended)
- Google Cloud Project with Drive API
- Telegram Bot Token

---

## ⚙️ Installation

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd enhanced-drive-bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Google Drive API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable **Google Drive API**
4. Create **OAuth 2.0 Client ID** (Desktop app)
5. Download `credentials.json` to project root
6. Run locally once to complete OAuth:

```bash
python bot.py
```

Follow the browser prompts to authorize. This creates `token.json`.

### 4. Configure Environment

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Telegram Credentials
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token

# Admin IDs (comma-separated, first is super admin)
ADMIN_IDS=123456789,987654321

# MongoDB
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/
DB_NAME=drive_access_bot

# Channel (optional)
CHANNEL_ID=-1001234567890
CHANNEL_ENABLED=false

# Features
ENABLE_AUTO_EXPIRE=true
ENABLE_BULK_IMPORT=true
ENABLE_ANALYTICS=true
ENABLE_BROADCAST=true

# Settings
DEFAULT_ROLE=reader
DEFAULT_EXPIRY_DAYS=30
DEFAULT_PAGE_SIZE=5

# Notifications
AUTO_EXPIRE_NOTIFICATIONS=true
GRANT_NOTIFICATIONS=true
REVOKE_NOTIFICATIONS=true

# Rate Limiting
RATE_LIMIT_ENABLED=true
MAX_REQUESTS_PER_MINUTE=10

# Logging
LOG_LEVEL=INFO
```

### 5. Run Bot

**Local Development:**
```bash
python bot.py
```

**With Flask (Production):**
```bash
python server.py
```

---

## 🎮 Bot Commands

### Basic Commands

| Command | Access | Description |
|---------|--------|-------------|
| `/start` | Admin | Main menu with bot info |
| `/help` | Admin | Feature reference |
| `/cancel` | Admin | Cancel current operation |
| `/id` | Anyone | Show Telegram user ID |

### Admin Commands

| Command | Access | Description |
|---------|--------|-------------|
| `/stats` | Admin | Activity analytics |
| `/broadcast` | Admin | Broadcast to all admins |
| `/info` | Super Admin | System monitor |

---

## 📚 Features Guide

### ➕ Grant Access (3 Modes)

**1. One Email → One Folder**
- Classic single grant
- Email validation
- Duration selection
- Duplicate detection

**2. One Email → Multiple Folders**
- Checkbox-style multi-select
- Same email, different folders
- Batch processing

**3. Multiple Emails → One Folder**
- Bulk grant from list
- Up to 50 emails per batch
- Duplicate and invalid detection
- Progress tracking

### 📂 Manage Folders

- View all Drive folders
- See users per folder
- Change roles (Viewer ↔ Editor)
- Remove individual access
- **Revoke All** - Remove all users at once
- Folder caching with manual refresh

### ⏰ Expiry Dashboard

- View all timed grants
- See time remaining
- **Inline Actions:**
  - Extend (+1h, +6h, +1d, +7d)
  - Revoke immediately
- Auto-expire notifications

### 📋 Activity Logs

- Structured log types:
  - ➕ Grant
  - 🗑 Remove
  - 🔄 Role Change
  - ⏰ Auto Revoke
  - 📥 Bulk Import
- Soft delete (never lost)
- Paginated view
- CSV export

### 📊 Analytics

- Daily/weekly/monthly activity
- Expiring soon counter
- Busiest day tracking
- Most accessed folder
- Real-time statistics

### 📢 Broadcast System

- Notify all admins
- Channel integration
- Progress tracking
- Error handling

### ⚙️ Settings

- Default access role
- Page size (3-10 items)
- Notification toggles
- Channel configuration
- Feature enable/disable

---

## 🔐 Admin System (VJ Pattern)

### Decorator Usage

```python
from utils.decorators import admin_command, admin_callback

# For commands
@Client.on_message(filters.command("admin_cmd"))
@admin_command
async def my_command(client, message):
    # Fully protected with error handling + logging
    pass

# For callbacks
@Client.on_callback_query(filters.regex("^btn_"))
@admin_callback
async def my_callback(client, callback_query):
    # Admin-only with error handling
    pass

# Custom decorators
@admin_only  # Just admin check
@super_admin_only  # Super admin only
@rate_limit(max_requests=5, time_window=60)  # Rate limiting
@error_handler  # Error handling
@log_command("command_name")  # Usage logging
```

---

## 📝 Message Templates (VJ Pattern)

### Using Templates

```python
from templates.messages import Messages, Emoji

# Simple usage
await message.reply_text(Messages.OPERATION_CANCELLED)

# With formatting
text = Messages.GRANT_SUCCESS.format(
    email="user@example.com",
    folder_name="Documents",
    role="Viewer",
    expiry="2026-03-15",
    grant_id="abc123",
    granted_at="2026-02-13 10:30",
    notification_sent="✅ Notification sent"
)

# Using emojis
button_text = f"{Emoji.GRANT} Grant Access"
```

### Customizing Messages

Edit `templates/messages.py`:

```python
class Messages:
    START_MESSAGE = """
    Your custom welcome message here
    Use {variables} for dynamic content
    """
```

---

## 🚀 Deployment

### Render

1. Push code to GitHub
2. Connect Render to your repo
3. Configure environment variables
4. Deploy!

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
python server.py
```

### Heroku

```bash
git push heroku main
```

Uses `Procfile`:
```
web: python server.py
```

### VPS (Ubuntu)

```bash
# Install Python 3.11+
sudo apt update
sudo apt install python3.11 python3.11-venv

# Create venv
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run with systemd
sudo nano /etc/systemd/system/drivebot.service
```

Service file:
```ini
[Unit]
Description=Drive Access Manager Bot
After=network.target

[Service]
User=your-user
WorkingDirectory=/path/to/bot
Environment="PATH=/path/to/bot/venv/bin"
ExecStart=/path/to/bot/venv/bin/python bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable drivebot
sudo systemctl start drivebot
```

---

## 🔧 Development

### Adding New Features

1. **Create Plugin** (`plugins/my_feature.py`):

```python
from pyrogram import Client, filters
from utils.decorators import admin_command
from templates.messages import Messages

@Client.on_message(filters.command("myfeature"))
@admin_command
async def my_feature(client, message):
    await message.reply_text("My feature!")
```

2. **Add Message Templates** (`templates/messages.py`):

```python
class Messages:
    MY_FEATURE_MSG = """
    My feature message with {variable}
    """
```

3. **Hot Reload** (no restart needed):

Bot automatically loads new plugins!

### Database Operations

```python
from services.database import Database

db = Database()

# Add log
await db.add_log({
    'type': 'my_action',
    'data': 'something',
    'timestamp': datetime.utcnow()
})

# Query
results = await db.logs_collection.find({'type': 'my_action'}).to_list(10)
```

---

## 📊 MongoDB Collections

| Collection | Purpose |
|-----------|---------|
| `admins` | Admin user IDs |
| `grants` | Active/expired grants with timers |
| `logs` | Activity audit trail (soft delete) |
| `settings` | Bot configuration |
| `states` | Conversation flow states |
| `cache` | Folder cache with TTL |
| `broadcasts` | Broadcast history |

---

## 🐛 Troubleshooting

### Bot won't start

```bash
# Check config
python -c "from config import Config; Config.print_config()"

# Check credentials
ls -la credentials.json token.json

# Check logs
tail -f logs/bot_*.log
```

### Database connection failed

- Verify `MONGO_URI` in `.env`
- Check MongoDB Atlas IP whitelist
- Test connection: `mongosh "your_mongo_uri"`

### Google Drive API errors

- Regenerate `token.json` (delete old one)
- Check API quotas in Cloud Console
- Verify `credentials.json` is valid

### Plugin not loading

- Check syntax errors: `python -m py_compile plugins/my_plugin.py`
- See logs: Bot shows loaded plugins on startup
- File must be `plugins/*.py` (not `_*.py`)

---

## 🎯 Best Practices

### 1. Security
- Never commit `.env`, `credentials.json`, `token.json`
- Use strong MongoDB passwords
- Limit admin access
- Enable rate limiting

### 2. Performance
- Use caching for folder lists
- Batch database operations
- Set appropriate page sizes
- Monitor auto-expire scheduler

### 3. Monitoring
- Check logs regularly
- Monitor MongoDB usage
- Track API quotas
- Review error alerts

---

## 📄 License

MIT License - See LICENSE file

---

## 🙏 Credits

- **VJ-FILTER-BOT** - Architecture patterns and inspiration
- **Pyrogram** - Telegram MTProto library
- **Motor** - Async MongoDB driver
- **Google Drive API** - File management

---

## 📞 Support

- **Issues**: GitHub Issues
- **Updates**: Follow @YourChannel
- **Contact**: @YourUsername

---

## 🔄 Changelog

### v3.0.0 (2026-02-13) - VJ-Enhanced
- ✨ Added VJ-FILTER-BOT patterns
- 🎨 Message template system
- 🔐 Decorator-based admin system
- 📢 Broadcast system
- ⚙️ Enhanced settings menu
- 📊 Improved analytics
- 🔄 Hot reload plugins
- 📝 Comprehensive logging

### v2.1.0
- Inline action buttons
- Revoke all feature
- Expiring soon counter

### v2.0.0
- Initial public release

---

**Built with ❤️ using Pyrogram, MongoDB & Google Drive API**

**Enhanced with VJ-FILTER-BOT patterns** 🚀
