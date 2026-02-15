"""
Statistics Plugin
"""

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime, timedelta
import config
from utils.filters import is_admin
from services.database import db
import logging

LOGGER = logging.getLogger(__name__)

# Emoji constants
class Emoji:
    BACK = "🔙"

@Client.on_message(filters.command("stats") & filters.private & is_admin)
async def stats_command(client: Client, message):
    """Show comprehensive statistics dashboard"""
    await show_stats_dashboard(client, message)


@Client.on_callback_query(filters.regex("^stats_menu$") & is_admin)
async def stats_menu_callback(client: Client, callback_query: CallbackQuery):
    """Handle stats_menu callback from main menu"""
    await show_stats_dashboard(client, callback_query)


async def show_stats_dashboard(client, update):
    """
    Show comprehensive stats dashboard 
    
    Displays:
    - User & activity stats
    - Grant statistics
    - Daily/weekly/monthly activity
    - Top folders
    - Expiring grants
    """
    
    # db is already initialized in main, so we use the instance
    
    # Get current time periods
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)
    
    try:
        # BASIC STATISTICS
        
        total_admins = len(config.ADMIN_IDS)
        total_grants = await db.grants.count_documents({})
        active_grants = await db.grants.count_documents({'status': 'active'})
        expired_grants = await db.grants.count_documents({'status': 'revoked'})
        
        # Expiring soon (within 24 hours)
        tomorrow = now + timedelta(hours=24)
        expiring_soon = await db.grants.count_documents({
            'status': 'active',
            'expires_at': {
                '$gte': now.timestamp(),
                '$lte': tomorrow.timestamp()
            }
        })
        
        # ACTIVITY STATISTICS
        # Note: timestamp in logs is stored as float (time.time())
        today_ts = today_start.timestamp()
        week_ts = week_start.timestamp()
        month_ts = month_start.timestamp()

        # Today's activity
        today_grants = await db.logs.count_documents({
            'action': 'grant',
            'timestamp': {'$gte': today_ts}
        })
        
        today_revokes = await db.logs.count_documents({
            'action': {'$in': ['revoke', 'auto_revoke']},
            'timestamp': {'$gte': today_ts}
        })
        
        # Weekly activity
        week_grants = await db.logs.count_documents({
            'action': 'grant',
            'timestamp': {'$gte': week_ts}
        })
        
        week_revokes = await db.logs.count_documents({
            'action': {'$in': ['revoke', 'auto_revoke']},
            'timestamp': {'$gte': week_ts}
        })
        
        # Monthly activity
        month_grants = await db.logs.count_documents({
            'action': 'grant',
            'timestamp': {'$gte': month_ts}
        })
        
        month_revokes = await db.logs.count_documents({
            'action': {'$in': ['revoke', 'auto_revoke']},
            'timestamp': {'$gte': month_ts}
        })
        
        # TOP FOLDERS (Most accessed)
        
        pipeline = [
            {'$match': {'action': 'grant'}},
            {'$group': {
                '_id': '$details.folder_id', # Using details.folder_id based on log structure
                'folder_name': {'$first': '$details.folder_name'},
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}},
            {'$limit': 5}
        ]
        
        top_folders_cursor = db.logs.aggregate(pipeline)
        top_folders = await top_folders_cursor.to_list(length=5)
        
        # Format top folders
        if top_folders:
            top_folders_text = "\n".join([
                f"📁 **{folder.get('folder_name', 'Unknown')[:25]}** - {folder['count']} grants"
                for folder in top_folders
            ])
        else:
            top_folders_text = "No data yet"
        
        # GRANT DISTRIBUTION
        
        viewer_grants = await db.grants.count_documents({
            'status': 'active',
            'role': 'reader'
        })
        
        editor_grants = await db.grants.count_documents({
            'status': 'active',
            'role': 'writer'
        })
        
        # AUTO-EXPIRE STATISTICS
        
        auto_revokes_today = await db.logs.count_documents({
            'action': 'auto_revoke',
            'timestamp': {'$gte': today_ts}
        })
        
        auto_revokes_week = await db.logs.count_documents({
            'action': 'auto_revoke',
            'timestamp': {'$gte': week_ts}
        })
        
        # BUILD STATS MESSAGE 
        
        stats_text = f"""
📊 **Statistics Dashboard**


**👥 USERS & GRANTS**

👤 **Total Admins:** {total_admins}
📊 **Total Grants:** {total_grants}
✅ **Active Grants:** {active_grants}
❌ **Expired Grants:** {expired_grants}
⏰ **Expiring Soon (24h):** {expiring_soon}


**📈 ACTIVITY OVERVIEW**

**📅 Today:**
  ➕ Grants: {today_grants}
  🗑 Revokes: {today_revokes}
  🤖 Auto-Revokes: {auto_revokes_today}

**📅 This Week:**
  ➕ Grants: {week_grants}
  🗑 Revokes: {week_revokes}
  🤖 Auto-Revokes: {auto_revokes_week}

**📅 This Month:**
  ➕ Grants: {month_grants}
  🗑 Revokes: {month_revokes}


**🔑 GRANT DISTRIBUTION**

👁️ **Viewers:** {viewer_grants} ({(viewer_grants/active_grants*100) if active_grants > 0 else 0:.1f}%)
✏️ **Editors:** {editor_grants} ({(editor_grants/active_grants*100) if active_grants > 0 else 0:.1f}%)


**📂 TOP FOLDERS**

{top_folders_text}


🕐 **Last Updated:** {now.strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
        
    except Exception as e:
        stats_text = f"""
📊 **Statistics Dashboard**

❌ **Error loading statistics:**
```
{str(e)}
```

Please try again or contact support.
"""
        LOGGER.error(f"Stats error: {e}", exc_info=True)

    # KEYBOARD
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📈 Detailed Stats", callback_data="stats_detailed"),
            InlineKeyboardButton("📊 Export CSV", callback_data="stats_export")
        ],
        [
            InlineKeyboardButton("📅 Daily Report", callback_data="stats_daily"),
            InlineKeyboardButton("📅 Weekly Report", callback_data="stats_weekly")
        ],
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="stats_refresh"),
            # InlineKeyboardButton(f"{Emoji.BACK} Menu", callback_data="main_menu") 
            # Removing back to menu as main_menu callback handler might not exist
        ]
    ])
    
    # Send or edit message
    if isinstance(update, CallbackQuery):
        try:
            await update.message.edit_text(stats_text, reply_markup=keyboard)
        except Exception as e:
            if "MESSAGE_NOT_MODIFIED" not in str(e):
                raise
    else:
        await update.reply_text(stats_text, reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^stats_refresh$") & is_admin)
async def stats_refresh_callback(client: Client, callback_query: CallbackQuery):
    """Refresh stats dashboard"""
    await callback_query.answer("🔄 Refreshing stats...", show_alert=False)
    await show_stats_dashboard(client, callback_query)


@Client.on_callback_query(filters.regex("^stats_detailed$") & is_admin)
async def stats_detailed_callback(client: Client, callback_query: CallbackQuery):
    """Show detailed statistics"""
    
    now = datetime.utcnow()
    
    try:
        # DETAILED STATISTICS
        
        # Average grant duration
        active_grants_list = await db.grants.find({'status': 'active'}).to_list(None)
        
        if active_grants_list:
            total_duration = 0
            temp_grants = 0
            perm_grants = 0
            
            for grant in active_grants_list:
                if 'expires_at' in grant and grant['expires_at']:
                    # Temporary grant
                    # expires_at is float timestamp
                    duration = (grant['expires_at'] - grant.get('granted_at', now.timestamp())) / 86400
                    total_duration += duration
                    temp_grants += 1
                else:
                    # Permanent grant
                    perm_grants += 1
            
            avg_duration = total_duration / temp_grants if temp_grants > 0 else 0
        else:
            avg_duration = 0
            temp_grants = 0
            perm_grants = 0
        
        # Busiest day of the week
        # Mongo $dayOfWeek returns 1 (Sunday) to 7 (Saturday)
        # But we store timestamp as float, so we need to convert to date
        pipeline = [
            {'$match': {'action': 'grant'}},
            {'$project': {
                'dayOfWeek': {'$dayOfWeek': {'$toDate': {'$multiply': ['$timestamp', 1000]}}} 
            }},
            {'$group': {
                '_id': '$dayOfWeek',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}},
            {'$limit': 1}
        ]
        
        busiest_cursor = db.logs.aggregate(pipeline)
        busiest_result = await busiest_cursor.to_list(1)
        
        if busiest_result:
            days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            # Mongo 1-indexed (Sunday=1) -> List 0-indexed
            day_index = busiest_result[0]['_id'] - 1
            if 0 <= day_index < len(days):
                busiest_day = days[day_index]
            else:
                busiest_day = "Unknown"
            busiest_count = busiest_result[0]['count']
        else:
            busiest_day = "N/A"
            busiest_count = 0
        
        # Most active admin
        pipeline = [
            {'$match': {'action': 'grant'}},
            {'$group': {
                '_id': '$admin_name', # Group by admin name
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}},
            {'$limit': 1}
        ]
        
        admin_cursor = db.logs.aggregate(pipeline)
        admin_result = await admin_cursor.to_list(1)
        
        if admin_result:
            most_active_admin = admin_result[0]['_id']
            admin_grant_count = admin_result[0]['count']
        else:
            most_active_admin = "N/A"
            admin_grant_count = 0
        
        # Recent errors (log type filtering)
        # Assuming we don't log errors to DB yet, or if we do, check structure
        # db.logs structure has 'action'. If we log errors, action='error'?
        # Based on services/database.py log_action, we log actions.
        # Errors might not be logged to DB unless explicit.
        # Skipping recent errors part or defaulting to 0
        recent_errors = 0
        
        # Cache statistics
        cached_folders = await db.cache.count_documents({})
        expired_cache = await db.cache.count_documents({
            'cached_at': {'$lt': (now - timedelta(minutes=10)).timestamp()} # Assuming 10m TTL
        })
        
        detailed_text = f"""
📊 **Detailed Statistics**


**⏰ GRANT DURATION ANALYSIS**

⏱️ **Average Duration:** {avg_duration:.1f} days
⏳ **Temporary Grants:** {temp_grants}
♾️ **Permanent Grants:** {perm_grants}


**📈 USAGE PATTERNS**

📅 **Busiest Day:** {busiest_day}
📊 **Busiest Day Grants:** {busiest_count}


**👥 ADMIN ACTIVITY**

👤 **Most Active Admin:** `{most_active_admin}`
📊 **Their Grants:** {admin_grant_count}


**💾 CACHE STATUS**

📁 **Cached Folders:** {cached_folders}
❌ **Expired Cache:** {expired_cache}
✅ **Valid Cache:** {cached_folders - expired_cache}


🕐 **Generated:** {now.strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(f"{Emoji.BACK} Back to Stats", callback_data="stats_refresh")
            ]
        ])
        
        try:
            await callback_query.message.edit_text(detailed_text, reply_markup=keyboard)
        except Exception as edit_err:
            if "MESSAGE_NOT_MODIFIED" not in str(edit_err):
                raise
        
    except Exception as e:
        if "MESSAGE_NOT_MODIFIED" in str(e):
            return
        await callback_query.answer(f"❌ Error: {str(e)[:100]}", show_alert=True)
        LOGGER.error(f"Detailed stats error: {e}", exc_info=True)


@Client.on_callback_query(filters.regex("^stats_daily$") & is_admin)
async def stats_daily_callback(client: Client, callback_query: CallbackQuery):
    """Show daily report"""
    
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_ts = today_start.timestamp()
    
    # Get today's activity by hour
    # Need to convert timestamp (float) to date
    pipeline = [
        {'$match': {
            'action': 'grant',
            'timestamp': {'$gte': today_ts}
        }},
        {'$project': {
             'hour': {'$hour': {'$toDate': {'$multiply': ['$timestamp', 1000]}}}
        }},
        {'$group': {
            '_id': '$hour',
            'count': {'$sum': 1}
        }},
        {'$sort': {'_id': 1}}
    ]
    
    hourly_cursor = db.logs.aggregate(pipeline)
    hourly_data = await hourly_cursor.to_list(None)
    
    # Create hourly chart (text-based)
    hourly_chart = "**Hourly Activity:**\n\n"
    
    if hourly_data:
        max_count = max(item['count'] for item in hourly_data)
        
        for item in hourly_data:
            hour = item['_id']
            count = item['count']
            bar_length = int((count / max_count) * 20) if max_count > 0 else 0
            bar = "█" * bar_length
            hourly_chart += f"`{hour:02d}:00` {bar} {count}\n"
    else:
        hourly_chart += "No activity today yet."
    
    daily_text = f"""
📅 **Daily Report**


**📊 TODAY'S ACTIVITY**

📅 **Date:** {today_start.strftime('%Y-%m-%d')}

{hourly_chart}
"""
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"{Emoji.BACK} Back", callback_data="stats_refresh")
        ]
    ])
    
    try:
        await callback_query.message.edit_text(daily_text, reply_markup=keyboard)
    except Exception as e:
        if "MESSAGE_NOT_MODIFIED" not in str(e):
            raise


@Client.on_callback_query(filters.regex("^stats_export$") & is_admin)
async def stats_export_callback(client: Client, callback_query: CallbackQuery):
    """Export statistics as CSV"""
    
    await callback_query.answer(
        "📊 CSV Export feature\n\nThis will download all statistics as a CSV file.\n\nComing soon!",
        show_alert=True
    )


@Client.on_callback_query(filters.regex("^stats_weekly$") & is_admin)
async def stats_weekly_callback(client: Client, callback_query: CallbackQuery):
    """Show weekly report"""
    from datetime import timedelta
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    week_ts = week_ago.timestamp()

    pipeline = [
        {'$match': {'action': 'grant', 'timestamp': {'$gte': week_ts}}},
        {'$project': {
            'day': {'$dayOfWeek': {'$toDate': {'$multiply': ['$timestamp', 1000]}}}
        }},
        {'$group': {'_id': '$day', 'count': {'$sum': 1}}},
        {'$sort': {'_id': 1}}
    ]
    daily_cursor = db.logs.aggregate(pipeline)
    daily_data = await daily_cursor.to_list(None)

    days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    chart = "**Daily Grants This Week:**\n\n"
    if daily_data:
        max_count = max(item['count'] for item in daily_data)
        for item in daily_data:
            day_name = days[item['_id'] - 1] if 1 <= item['_id'] <= 7 else '?'
            bar = "█" * int((item['count'] / max_count) * 20) if max_count else ""
            chart += f"`{day_name}` {bar} {item['count']}\n"
    else:
        chart += "No activity this week."

    weekly_text = f"📅 **Weekly Report**\n\n{chart}\n🕐 {now.strftime('%Y-%m-%d %H:%M UTC')}"
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(f"{Emoji.BACK} Back", callback_data="stats_refresh")]])
    try:
        await callback_query.message.edit_text(weekly_text, reply_markup=keyboard)
    except Exception as e:
        if "MESSAGE_NOT_MODIFIED" not in str(e):
            raise
