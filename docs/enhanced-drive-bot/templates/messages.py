"""
Message Templates
VJ-FILTER-BOT inspired centralized message management
"""

class Messages:
    """All bot messages in one place (VJ Script.py pattern)"""
    
    # ═══════════════════════════════════════
    # START & HELP MESSAGES
    # ═══════════════════════════════════════
    
    START_MESSAGE = """
╔════════════════════════════╗
  🗂 **Drive Access Manager**
╚════════════════════════════╝

👋 Welcome back, **{name}**!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 **BOT INFO**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏷 **Name**     : {bot_name}
👤 **Username** : @{bot_username}
🔄 **Version**  : {version}
⏱️ **Uptime**   : {uptime}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Use the buttons below to get started! 👇
"""

    HELP_MESSAGE = """
📚 **Help & Commands**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**📋 BASIC COMMANDS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• /start - Show main menu
• /help - This help message
• /cancel - Cancel current operation
• /id - Get your Telegram ID

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**🔑 ACCESS MANAGEMENT**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Use **➕ Grant Access** to give folder permissions
• Use **📂 Manage Folders** to view/edit access
• Use **⏰ Expiry Dashboard** to manage timers

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**📊 ANALYTICS & LOGS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• /stats - View bot statistics
• Use **📋 Access Logs** to see activity history
• Use **🔍 Search User** to find specific grants

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**⚙️ SETTINGS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Configure default role, page size, notifications
• Set up channel broadcasting
• Customize bot behavior

For detailed guides, visit our documentation!
"""

    # ═══════════════════════════════════════
    # GRANT MESSAGES
    # ═══════════════════════════════════════
    
    GRANT_MODE_SELECT = """
➕ **Grant Access**

Choose how you want to grant access:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**📧 ONE EMAIL → ONE FOLDER**
Single email, single folder access

**📂 ONE EMAIL → MULTI FOLDERS**
Single email, multiple folders (checkbox)

**👥 MULTI EMAILS → ONE FOLDER**
Multiple emails, single folder (bulk)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Select a mode to continue:
"""

    GRANT_EMAIL_PROMPT = """
📧 **Enter Email Address**

Please send the email address to grant access:

**Example:** `user@example.com`

Type /cancel to abort.
"""

    GRANT_MULTI_EMAIL_PROMPT = """
📧 **Enter Email Addresses**

Send email addresses (one per line):

**Example:**
```
user1@example.com
user2@example.com
user3@example.com
```

**Limit:** Maximum 50 emails per batch

Type /cancel to abort.
"""

    GRANT_FOLDER_SELECT = """
📂 **Select Folder**

Choose which folder to grant access:

Showing page {current_page} of {total_pages}
"""

    GRANT_ROLE_SELECT = """
🎭 **Select Access Role**

Choose the permission level:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**👁️ VIEWER (Reader)**
• Can view and download files
• Can set expiry timer

**✏️ EDITOR (Writer)**  
• Can view, edit, and upload files
• Always permanent access
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    GRANT_DURATION_SELECT = """
⏰ **Set Access Duration**

Choose how long access should last:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**⏱️ TEMPORARY ACCESS**
• 1 Hour
• 6 Hours
• 1 Day
• 7 Days
• 30 Days

**♾️ PERMANENT ACCESS**
• No expiry (forever)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Note:** Editors always get permanent access
"""

    GRANT_SUCCESS = """
✅ **Access Granted Successfully!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📧 **Email:** `{email}`
📂 **Folder:** {folder_name}
🔑 **Role:** **{role}**
⏰ **Expires:** {expiry}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **Grant ID:** `{grant_id}`
🕐 **Granted at:** {granted_at}

{notification_sent}
"""

    GRANT_MULTI_SUCCESS = """
✅ **Bulk Grant Complete!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📂 **Folder:** {folder_name}
🔑 **Role:** **{role}**
⏰ **Duration:** {duration}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **Results:**
✅ Granted: {granted_count}
⚠️ Skipped (duplicates): {skipped_count}
❌ Failed: {failed_count}

{notification_sent}
"""

    # ═══════════════════════════════════════
    # MANAGE MESSAGES
    # ═══════════════════════════════════════
    
    MANAGE_FOLDER_LIST = """
📂 **Manage Folders**

Total folders: **{total_folders}**
Page {current_page} of {total_pages}

Select a folder to manage access:
"""

    MANAGE_FOLDER_DETAIL = """
📂 **Folder Details**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 **Name:** {folder_name}
🆔 **ID:** `{folder_id}`
👥 **Total Users:** {user_count}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**👥 Users with Access:**

{users_list}

Choose an action below:
"""

    MANAGE_USER_DETAIL = """
👤 **User Access Details**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📧 **Email:** `{email}`
📂 **Folder:** {folder_name}
🔑 **Role:** **{role}**
⏰ **Expiry:** {expiry}
📅 **Granted:** {granted_at}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

What would you like to do?
"""

    REVOKE_CONFIRM = """
⚠️ **Confirm Revoke Access**

Are you sure you want to remove access?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📧 **Email:** `{email}`
📂 **Folder:** {folder_name}
🔑 **Role:** **{role}**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This action cannot be undone!
"""

    REVOKE_SUCCESS = """
✅ **Access Revoked Successfully!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📧 **Email:** `{email}`
📂 **Folder:** {folder_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🕐 **Revoked at:** {revoked_at}
"""

    REVOKE_ALL_CONFIRM = """
⚠️ **REVOKE ALL ACCESS - DANGER ZONE**

You are about to remove ALL user access from this folder!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📂 **Folder:** {folder_name}
👥 **Total Users:** {user_count}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**This will remove:**
{users_preview}

⚠️ **WARNING:** This action cannot be undone!

Type **REVOKE ALL** to confirm, or /cancel to abort.
"""

    # ═══════════════════════════════════════
    # EXPIRY MESSAGES
    # ═══════════════════════════════════════
    
    EXPIRY_DASHBOARD = """
⏰ **Expiry Dashboard**

Active timed grants: **{active_count}**
Expiring soon (24h): **{expiring_soon_count}**

{grants_list}

Use the buttons below to manage expiry.
"""

    EXPIRY_EXTEND_SELECT = """
🔄 **Extend Access**

Current expiry: **{current_expiry}**

How much time to add?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• +1 Hour
• +6 Hours
• +1 Day
• +7 Days
• Make Permanent
━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    EXPIRY_EXTENDED = """
✅ **Access Extended!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📧 **Email:** `{email}`
📂 **Folder:** {folder_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🕐 **Previous Expiry:** {old_expiry}
⏰ **New Expiry:** {new_expiry}
➕ **Added:** {added_duration}
"""

    EXPIRY_NOTIFICATION = """
⏰ **Access Expiring Soon!**

Your access to a folder will expire soon:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📂 **Folder:** {folder_name}
⏰ **Expires in:** {time_remaining}
🔑 **Role:** {role}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Contact an administrator to extend access.
"""

    # ═══════════════════════════════════════
    # BROADCAST MESSAGES
    # ═══════════════════════════════════════
    
    BROADCAST_PROMPT = """
📢 **Broadcast Message**

Send the message you want to broadcast to all admins.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**Supported:**
• Text messages
• Photos with captions
• Documents with captions
━━━━━━━━━━━━━━━━━━━━━━━━━━━

Type /cancel to abort.
"""

    BROADCAST_CONFIRM = """
📢 **Confirm Broadcast**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**Message Preview:**
{message_preview}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Recipients:** {recipient_count} admins

Send this broadcast?
"""

    BROADCAST_PROGRESS = """
📢 **Broadcasting...**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: {total}
✅ Sent: {sent}
❌ Failed: {failed}
⏳ Remaining: {remaining}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please wait...
"""

    BROADCAST_COMPLETE = """
✅ **Broadcast Complete!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 **Total:** {total}
✅ **Sent:** {sent}
❌ **Failed:** {failed}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🕐 **Completed at:** {completed_at}
"""

    # ═══════════════════════════════════════
    # STATS MESSAGES
    # ═══════════════════════════════════════
    
    STATS_DASHBOARD = """
📊 **Statistics Dashboard**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**👥 USERS & ACTIVITY**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 Total Admins: {total_admins}
📊 Total Grants: {total_grants}
✅ Active Grants: {active_grants}
⏰ Expiring Soon (24h): {expiring_soon}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**📈 ACTIVITY**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Today: {today_activity}
📅 This Week: {week_activity}
📅 This Month: {month_activity}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**📂 TOP FOLDERS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{top_folders}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🕐 Last updated: {updated_at}
"""

    # ═══════════════════════════════════════
    # SETTINGS MESSAGES
    # ═══════════════════════════════════════
    
    SETTINGS_MENU = """
⚙️ **Bot Settings**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**📝 CURRENT CONFIGURATION**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎭 **Default Role:** {default_role}
📄 **Page Size:** {page_size} items
⏰ **Default Expiry:** {default_expiry} days

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**🔔 NOTIFICATIONS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Grant Notifications: {grant_notif}
🗑 Revoke Notifications: {revoke_notif}
⏰ Expiry Notifications: {expiry_notif}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**📢 CHANNEL**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Status: {channel_status}
Channel ID: {channel_id}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Use buttons below to modify settings:
"""

    # ═══════════════════════════════════════
    # ERROR MESSAGES
    # ═══════════════════════════════════════
    
    ERROR_GENERIC = """
❌ **Error Occurred**

{error_message}

Please try again or contact support.
"""

    ERROR_PERMISSION_DENIED = """
⛔ **Access Denied**

This command is only available to administrators.

Contact the bot owner for access.
"""

    ERROR_INVALID_EMAIL = """
❌ **Invalid Email**

The email address you provided is not valid.

Please check and try again.
"""

    ERROR_FOLDER_NOT_FOUND = """
❌ **Folder Not Found**

The specified folder could not be found or you don't have access to it.
"""

    ERROR_USER_NOT_FOUND = """
❌ **User Not Found**

No access grant found for this user.
"""

    ERROR_DUPLICATE_ACCESS = """
⚠️ **Duplicate Access**

This user already has access to this folder.

**Current Access:**
• Role: {role}
• Expires: {expiry}
"""

    # ═══════════════════════════════════════
    # INFO MESSAGES
    # ═══════════════════════════════════════
    
    INFO_SYSTEM = """
🔧 **System Information**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**🤖 BOT STATUS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏷 Name: {bot_name}
🆔 Bot ID: `{bot_id}`
👤 Username: @{bot_username}
🔄 Version: {version}
⏱️ Uptime: {uptime}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**📊 STATISTICS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👥 Admins: {admin_count}
📁 Cached Folders: {cached_folders}
✅ Active Grants: {active_grants}
⏰ Scheduled Tasks: {scheduled_tasks}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**🔌 SERVICES**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗄️ Database: {db_status}
📂 Google Drive: {drive_status}
📢 Telegram: {telegram_status}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**⏰ AUTO-EXPIRE SCHEDULER**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: {scheduler_status}
Last Run: {last_run}
Next Run: {next_run}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    # ═══════════════════════════════════════
    # UTILITY MESSAGES
    # ═══════════════════════════════════════
    
    OPERATION_CANCELLED = """
🚫 **Operation Cancelled**

The current operation has been cancelled.

Use /start to return to main menu.
"""

    PROCESSING = """
⏳ **Processing...**

Please wait while we process your request.
"""

    CACHE_REFRESHED = """
✅ **Cache Refreshed!**

Folder cache has been updated with latest data from Google Drive.

Total folders: {folder_count}
"""

# Emojis collection for easy access
class Emoji:
    """Emoji constants (VJ style)"""
    
    # Status
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    PROCESSING = "⏳"
    
    # Actions
    GRANT = "➕"
    REVOKE = "🗑"
    EXTEND = "🔄"
    EDIT = "✏️"
    
    # Objects
    FOLDER = "📂"
    EMAIL = "📧"
    USER = "👤"
    ROLE = "🎭"
    TIMER = "⏰"
    
    # Interface
    BACK = "◀️"
    NEXT = "▶️"
    CLOSE = "❌"
    REFRESH = "🔄"
    SEARCH = "🔍"
