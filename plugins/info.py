"""
System Information Plugin
Enhanced with comprehensive bot status
"""

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime
import config
from services.database import db
from utils.time import IST
from utils.time import safe_edit
import platform
import psutil
import sys
import pyrogram
import logging

LOGGER = logging.getLogger(__name__)

# Emoji constants
class Emoji:
    BACK = "🔙"

def is_super_admin(user_id):
    """
    Check if user is super admin.
    In this bot, super admin is the first admin in ADMIN_IDS or explicitly defined.
    If ADMIN_IDS is a set, there is no 'first', so we might check if user is in ADMIN_IDS 
    and maybe checking config.SUPER_ADMIN_ID if it existed.
    For now, any admin can view info, but maybe restrict detailed config?
    Let's just use regular admin check for simplicity or update config to have super admin.
    """
    return user_id in config.ADMIN_IDS

# Helper for admin check filter
from utils.filters import is_admin

@Client.on_message(filters.command("info") & filters.private & is_admin)
async def info_command(client: Client, message):
    """
    System information and bot status
    """
    await show_info_dashboard(client, message)


async def show_info_dashboard(client, update):
    
    # Get bot info
    me = await client.get_me()
    
    # Calculate uptime
    # Using config.START_TIME (float)
    start_dt = datetime.fromtimestamp(config.START_TIME, tz=IST)
    uptime_delta = datetime.now(IST) - start_dt
    days = uptime_delta.days
    hours = uptime_delta.seconds // 3600
    minutes = (uptime_delta.seconds % 3600) // 60
    
    if days > 0:
        uptime = f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        uptime = f"{hours}h {minutes}m"
    else:
        uptime = f"{minutes}m"
    
    # System info
    uname = platform.uname()
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    cpu_percent = psutil.cpu_percent(interval=None) # interval=None to be non-blocking
    
    # Python info
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    # Database stats
    try:
        # Count documents
        total_grants = await db.grants.count_documents({})
        active_grants = await db.grants.count_documents({'status': 'active'})
        total_logs = await db.logs.count_documents({})
        cached_folders = await db.cache.count_documents({})
        
        # Check database connection
        db_status = "✅ Connected"
    except Exception as e:
        db_status = f"❌ Error: {str(e)[:30]}"
        total_grants = active_grants = total_logs = cached_folders = 0
    
    # Drive API status
    try:
        from services.drive import drive_service
        if drive_service.service:
            drive_status = "✅ Connected"
        else:
             # Try simple check
             if drive_service.creds and drive_service.creds.valid:
                 drive_status = "✅ Creds Valid"
             else:
                 drive_status = "❌ Not Connected"
    except Exception as e:
        drive_status = f"❌ Error: {str(e)[:30]}"
    
    # Telegram connection status
    telegram_status = "✅ Connected" if me else "❌ Disconnected"
    
    # Scheduler status (Assuming simple check)
    scheduler_status = "✅ Running" # Since we are running modules
    
    # Build info message
    info_text = f"""
🔧 **System Information**

**🤖 BOT STATUS**

🏷 **Name:** {me.first_name}
🆔 **Bot ID:** `{me.id}`
👤 **Username:** @{me.username}
🔄 **Version:** {config.VERSION}
⏱️ **Uptime:** {uptime}
📅 **Started:** {start_dt.strftime('%d %b %Y, %I:%M %p')}


**📊 STATISTICS**

👥 **Admins:** {len(config.ADMIN_IDS)}
📁 **Cached Folders:** {cached_folders}
📊 **Total Grants:** {total_grants}
✅ **Active Grants:** {active_grants}
📋 **Total Logs:** {total_logs}


**🔌 SERVICE STATUS**

🗄️ **Database:** {db_status}
📂 **Google Drive:** {drive_status}
📢 **Telegram:** {telegram_status}


**💻 SYSTEM RESOURCES**

🖥️ **OS:** {uname.system} {uname.release}
🏗️ **Architecture:** {uname.machine}
🐍 **Python:** {python_version}
📦 **Pyrogram:** {pyrogram.__version__}

💾 **RAM Usage:** {ram.percent}% ({ram.used // (1024**3)}GB / {ram.total // (1024**3)}GB)
💽 **Disk Usage:** {disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)
⚡ **CPU Usage:** {cpu_percent}%
🧵 **CPU Cores:** {psutil.cpu_count()}


🕐 Last updated: {datetime.now(IST).strftime('%d %b %Y, %I:%M:%S %p')}
"""
    
    # Keyboard
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="info_refresh"),
            # InlineKeyboardButton("📊 Stats", callback_data="stats_refresh") # Cross-plugin callback might work
        ],
        [
            InlineKeyboardButton("⚙️ Config", callback_data="info_config"),
            InlineKeyboardButton("📋 Logs", callback_data="info_logs")
        ],
        # [
        #     InlineKeyboardButton(f"{Emoji.BACK} Main Menu", callback_data="main_menu")
        # ]
    ])
    
    if isinstance(update, CallbackQuery):
        try:
            await safe_edit(update.message, info_text, reply_markup=keyboard)
        except Exception as e:
            if "MESSAGE_NOT_MODIFIED" not in str(e):
                raise
    else:
        await update.reply_text(info_text, reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^info_refresh$") & is_admin)
async def info_refresh_callback(client: Client, callback_query):
    """Refresh info display"""
    
    # Send processing message
    await callback_query.answer("🔄 Refreshing...", show_alert=False)
    await show_info_dashboard(client, callback_query)


@Client.on_callback_query(filters.regex("^info_config$") & is_admin)
async def info_config_callback(client: Client, callback_query):
    """Show configuration details"""
    
    # We can read from config.py variables
    # config.py doesn't have all these structured in a Config class in the file I read,
    # but I'll use what's available or safe defaults
    
    config_text = f"""
⚙️ **Bot Configuration**

**🔐 SECURITY**

👥 **Admin Count:** {len(config.ADMIN_IDS)}


**🗄️ DATABASE**

URI: `{config.MONGO_URI[:15]}...` (Hidden)

"""
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"{Emoji.BACK} Back to Info", callback_data="info_refresh")
        ]
    ])
    
    try:
        await safe_edit(callback_query.message, config_text, reply_markup=keyboard)
    except Exception as e:
        if "MESSAGE_NOT_MODIFIED" not in str(e):
            raise


@Client.on_callback_query(filters.regex("^info_logs$") & is_admin)
async def info_logs_callback(client: Client, callback_query):
    """Show recent error logs"""
    
    await callback_query.answer("📋 Fetching logs...", show_alert=False)

    try:
        # Read recent logs
        import os
        
        # We don't have a guaranteed log file path from config, but bot.py configures logging usually
        # bot.py logging.basicConfig doesn't specify filename, so it logs to stderr/stdout
        # So we can't read from a file unless we know where it is.
        # But we can read from DB logs!
        
        recent_logs, total = await db.get_logs(limit=10)
        
        log_lines = []
        for log in recent_logs:
            ts = datetime.fromtimestamp(log['timestamp']).strftime('%I:%M %p')
            log_lines.append(f"`{ts}` **{log.get('action', 'INFO')}**: {str(log.get('details', ''))[:50]}")
            
        logs_content = "\n".join(log_lines) if log_lines else "No recent logs in DB."

        logs_text = f"""
📋 **Recent DB Logs**


{logs_content}


📊 **Total DB Logs:** {total}
🕐 **Last Update:** {datetime.now().strftime('%I:%M:%S %p')}
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="info_logs"),
                InlineKeyboardButton(f"{Emoji.BACK} Back", callback_data="info_refresh")
            ]
        ])
        
        try:
            await safe_edit(callback_query.message, logs_text, reply_markup=keyboard)
        except Exception as edit_err:
            if "MESSAGE_NOT_MODIFIED" not in str(edit_err):
                raise
        
    except Exception as e:
        await callback_query.answer(f"❌ Error: {str(e)}", show_alert=True)
