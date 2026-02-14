# 📋 Implementation Guide
## VJ-Enhanced Google Drive Access Manager Bot

---

## 🎯 Quick Start (5 Minutes)

### Step 1: Get Your Files Ready

You need 3 credential files:

1. **Telegram Credentials**
   - Go to https://my.telegram.org/apps
   - Create new application
   - Note down `API_ID` and `API_HASH`

2. **Bot Token**
   - Message [@BotFather](https://t.me/BotFather)
   - Send `/newbot`
   - Follow instructions
   - Copy the bot token

3. **Google Drive API**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create project
   - Enable Google Drive API
   - Create OAuth 2.0 credentials (Desktop app)
   - Download as `credentials.json`

### Step 2: Setup Environment

```bash
# Clone/download the bot files
cd enhanced-drive-bot

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Fill in:
```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
MONGO_URI=your_mongodb_uri
ADMIN_IDS=your_telegram_id
```

### Step 3: Get Your Telegram ID

1. Start [@userinfobot](https://t.me/userinfobot)
2. It will send your ID
3. Add this ID to `ADMIN_IDS` in `.env`

### Step 4: MongoDB Setup

**Option A: MongoDB Atlas (Free, Recommended)**

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create free account
3. Create free cluster (M0)
4. Create database user
5. Get connection string
6. Replace `<password>` in connection string
7. Add to `MONGO_URI` in `.env`

**Option B: Local MongoDB**

```bash
# Install MongoDB
sudo apt install mongodb

# Start MongoDB
sudo systemctl start mongodb

# Connection string
MONGO_URI=mongodb://localhost:27017/
```

### Step 5: Install & Run

```bash
# Install dependencies
pip install -r requirements.txt

# First run (authorize Google Drive)
python bot.py

# Follow browser prompts to authorize
# This creates token.json
```

### Step 6: Test

Send `/start` to your bot in Telegram!

---

## 🏗 File Structure You Received

```
enhanced-drive-bot/
│
├── 📄 bot.py                  # Main bot file ⭐
├── 📄 config.py               # Configuration ⭐
├── 📄 server.py               # Flask server (create this)
│
├── 📁 templates/
│   └── messages.py            # All messages ⭐
│
├── 📁 plugins/
│   └── start.py               # Main menu ⭐
│   └── (create other plugins)
│
├── 📁 services/
│   └── (create database.py, drive.py, broadcast.py)
│
├── 📁 utils/
│   ├── decorators.py          # Admin decorators ⭐
│   ├── validators.py          # Input validation ⭐
│   └── logger.py              # Logging ⭐
│
├── 📄 requirements.txt        # Dependencies ⭐
├── 📄 .env.example           # Environment template ⭐
└── 📄 README.md              # Documentation ⭐

⭐ = Already created for you
```

---

## 🔨 Creating Missing Files

I've provided the core structure. Here's what you need to add:

### 1. Create `server.py` (for deployment)

```python
from flask import Flask
from threading import Thread
from bot import BotCore
import asyncio

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/health')
def health():
    return {"status": "healthy"}

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def run_bot():
    bot = BotCore()
    asyncio.run(bot.start())

if __name__ == "__main__":
    # Start Flask in background
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    
    # Start bot
    run_bot()
```

### 2. Create Database Service (`services/database.py`)

```python
from motor.motor_asyncio import AsyncIOMotorClient
from config import Config
from datetime import datetime

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        
    async def connect(self):
        self.client = AsyncIOMotorClient(Config.MONGO_URI)
        self.db = self.client[Config.DB_NAME]
        
        # Collections
        self.grants = self.db[Config.COLLECTION_GRANTS]
        self.logs = self.db[Config.COLLECTION_LOGS]
        self.settings = self.db[Config.COLLECTION_SETTINGS]
        # ... etc
        
    async def add_log(self, log_data):
        return await self.logs.insert_one(log_data)
        
    async def get_expired_grants(self):
        return await self.grants.find({
            'status': 'active',
            'expiry': {'$lt': datetime.utcnow()}
        }).to_list(None)
        
    # Add more methods as needed
```

### 3. Create Drive Service (`services/drive.py`)

```python
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path

class DriveService:
    def __init__(self):
        self.service = None
        
    async def initialize(self):
        creds = None
        
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json')
            
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json',
                    ['https://www.googleapis.com/auth/drive']
                )
                creds = flow.run_local_server(port=0)
                
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
                
        self.service = build('drive', 'v3', credentials=creds)
        
    async def add_permission(self, folder_id, email, role):
        permission = {
            'type': 'user',
            'role': role,
            'emailAddress': email
        }
        
        result = self.service.permissions().create(
            fileId=folder_id,
            body=permission,
            sendNotificationEmail=False
        ).execute()
        
        return result
        
    # Add more methods
```

### 4. Create Other Plugins

Based on `start.py` pattern, create:
- `plugins/grant.py` - Grant access workflows
- `plugins/manage.py` - Manage folders
- `plugins/expiry.py` - Expiry dashboard
- `plugins/stats.py` - Statistics
- `plugins/settings.py` - Settings menu
- `plugins/logs.py` - Activity logs
- `plugins/broadcast.py` - Broadcasting

Each plugin follows this pattern:

```python
from pyrogram import Client, filters
from utils.decorators import admin_command
from templates.messages import Messages

@Client.on_message(filters.command("yourcommand"))
@admin_command
async def your_handler(client, message):
    await message.reply_text(Messages.YOUR_MESSAGE)
```

---

## 🎨 Customization Guide

### Changing Messages

Edit `templates/messages.py`:

```python
class Messages:
    START_MESSAGE = """
🎉 Welcome to MY CUSTOM BOT!

Your custom text here
    """
```

### Adding New Commands

1. Create handler in appropriate plugin:

```python
@Client.on_message(filters.command("mynew"))
@admin_command
async def my_new_command(client, message):
    await message.reply_text("New command!")
```

2. Add to help message in `templates/messages.py`

3. Reload bot (or use hot reload if implemented)

### Adding Menu Buttons

Edit `start.py`, modify `get_main_menu_keyboard()`:

```python
def get_main_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("My Button", callback_data="my_callback")
        ],
        # ... existing buttons
    ])
```

Then add callback handler:

```python
@Client.on_callback_query(filters.regex("^my_callback$"))
@admin_callback
async def my_callback(client, callback_query):
    await callback_query.message.edit_text("Button clicked!")
```

---

## 🚀 Deployment Guides

### Render.com (Recommended)

1. Push code to GitHub
2. Create Render account
3. New → Web Service
4. Connect GitHub repo
5. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python server.py`
6. Environment Variables:
   - Add all from `.env`
7. Deploy!

### Heroku

```bash
# Login
heroku login

# Create app
heroku create my-drive-bot

# Set config
heroku config:set API_ID=xxx API_HASH=xxx ...

# Deploy
git push heroku main
```

### Railway.app

1. Connect GitHub
2. Deploy from repo
3. Add environment variables
4. Done!

### VPS (Ubuntu 22.04)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv

# Clone repo
git clone <your-repo>
cd enhanced-drive-bot

# Create venv
python3.11 -m venv venv
source venv/bin/activate

# Install
pip install -r requirements.txt

# Setup credentials
# Upload credentials.json, token.json, .env

# Create systemd service
sudo nano /etc/systemd/system/drivebot.service
```

Paste:
```ini
[Unit]
Description=Drive Access Manager Bot
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/enhanced-drive-bot
Environment="PATH=/home/ubuntu/enhanced-drive-bot/venv/bin"
ExecStart=/home/ubuntu/enhanced-drive-bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable drivebot
sudo systemctl start drivebot

# Check status
sudo systemctl status drivebot

# View logs
sudo journalctl -u drivebot -f
```

---

## 🐛 Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'pyrogram'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "credentials.json not found"

**Solution:**
- Download from Google Cloud Console
- Place in project root
- Run `python bot.py` to authorize

### Issue: "Database connection failed"

**Solution:**
- Check `MONGO_URI` in `.env`
- Whitelist your IP in MongoDB Atlas
- Test: `mongosh "your_uri"`

### Issue: "Bot doesn't respond"

**Solution:**
- Check bot token is correct
- Verify your ID is in `ADMIN_IDS`
- Check logs: `tail -f logs/bot_*.log`

### Issue: "Google Drive API quota exceeded"

**Solution:**
- Wait 24 hours for quota reset
- Request quota increase in Cloud Console
- Reduce cache TTL

---

## 📊 Monitoring & Maintenance

### Check Bot Health

```bash
# View logs
tail -f logs/bot_*.log

# Check if running
ps aux | grep python

# Resource usage
htop
```

### Database Maintenance

```python
# Connect to MongoDB
mongosh "your_uri"

# Check collections
use drive_access_bot
show collections

# Count documents
db.grants.countDocuments()
db.logs.countDocuments()

# Clean old logs (older than 90 days)
db.logs.deleteMany({
    timestamp: {
        $lt: new Date(Date.now() - 90*24*60*60*1000)
    }
})
```

### Performance Optimization

1. **Enable caching:**
```env
CACHE_ENABLED=true
CACHE_TTL=3600
```

2. **Adjust page size:**
```env
DEFAULT_PAGE_SIZE=5  # Lower = faster
```

3. **Database indexes:**
```python
# Add in database.py
await self.grants.create_index("status")
await self.grants.create_index("expiry")
await self.logs.create_index("timestamp")
```

---

## 🎓 Learning Resources

### Understanding the Code

1. **Start with `bot.py`** - Main entry point
2. **Read `config.py`** - All settings
3. **Study `start.py`** - See how plugins work
4. **Review `decorators.py`** - Security layer
5. **Check `messages.py`** - All text

### Python Async Programming

- [Asyncio Docs](https://docs.python.org/3/library/asyncio.html)
- [Motor Tutorial](https://motor.readthedocs.io/)

### Pyrogram/Pyrofork

- [Pyrogram Docs](https://docs.pyrogram.org/)
- [Pyrofork Docs](https://pyrofork.mayuri.my.id/)

### Google Drive API

- [Drive API v3](https://developers.google.com/drive/api/v3/reference)

---

## 💡 Next Steps

1. ✅ **Get bot running locally**
2. ✅ **Test basic commands**
3. ✅ **Deploy to cloud**
4. 📝 **Customize messages**
5. 🎨 **Add custom features**
6. 📊 **Monitor and optimize**
7. 🚀 **Share with team**

---

## 📞 Getting Help

If you're stuck:

1. Check logs first
2. Review this guide
3. Read error messages carefully
4. Test with `/id` command
5. Verify all credentials
6. Check MongoDB connection
7. Try in private chat with bot

---

**You now have everything to run and customize your enhanced Drive Access Manager Bot! 🎉**

Happy coding! 🚀
