from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.filters import is_admin
from services.database import db
from config import START_TIME, VERSION
import time
from utils.time import get_uptime

# 🎨 PROFESSIONAL MAIN MENU - Clean & Modern
MAIN_MENU_KEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("✨ Grant Access", callback_data="grant_menu"),
        InlineKeyboardButton("🗂 Manage", callback_data="manage_menu")
    ],
    [
        InlineKeyboardButton("⏰ Expiry", callback_data="expiry_menu"),
        InlineKeyboardButton("📊 Logs", callback_data="logs_menu")
    ],
    [
        InlineKeyboardButton("🔍 Search", callback_data="search_user"),
        InlineKeyboardButton("� Statistics", callback_data="stats_menu")
    ],
    [
        InlineKeyboardButton("⚙️ Settings", callback_data="settings_menu"),
        InlineKeyboardButton("💡 Help & Guide", callback_data="help_menu")
    ]
])


# --- MODERN ID DISPLAY ---
@Client.on_message(filters.command("id"))
async def show_id(client, message):
    user = message.from_user
    
    text = (
        "┏━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃   🆔 YOUR TELEGRAM INFO   ┃\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        "╭─────────────────────╮\n"
        f"│ 👤 Name: {user.first_name}\n"
        f"│ 🆔 User ID: `{user.id}`\n"
        f"│ 📱 Username: @{user.username or 'Not Set'}\n"
        f"│ 🤖 Bot: {'Yes' if user.is_bot else 'No'}\n"
    )
    
    if user.last_name:
        text += f" {user.last_name}"
    
    text += "╰─────────────────────╯\n\n"
    text += "💡 **Tip:** Share your User ID with admins for access requests."
    
    await message.reply_text(text)


# --- PROFESSIONAL START COMMAND ---
@Client.on_message(filters.command("start") & is_admin)
async def start_handler(client, message):
    user = message.from_user
    me = await client.get_me()
    uptime = get_uptime(START_TIME)
    
    # Fetch live stats
    try:
        stats = await db.get_stats()
        active_count = stats.get('active_grants', 0)
        total_actions = stats.get('total', 0)
    except:
        active_count = 0
        total_actions = 0
    
    # Clean, modern welcome message
    text = (
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃  🌟 **GOOGLE DRIVE ACCESS MANAGER** ┃\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"👋 **Welcome back, {user.first_name}!**\n\n"
        "╔════════════════════════════╗\n"
        "║       🤖 BOT STATUS       ║\n"
        "╠════════════════════════════╣\n"
        f"║ 🏷 Bot: **{me.first_name}**\n"
        f"║ 👤 Handle: @{me.username}\n"
        f"║ 🔖 Version: `v{VERSION}`\n"
        f"║ ⏱️ Uptime: `{uptime}`\n"
        "╚════════════════════════════╝\n\n"
        "╔════════════════════════════╗\n"
        "║     📊 QUICK OVERVIEW     ║\n"
        "╠════════════════════════════╣\n"
        f"║ ⏰ Active Grants: **{active_count}**\n"
        f"║ 📝 Total Actions: **{total_actions}**\n"
        "╚════════════════════════════╝\n\n"
        "💡 **Select an option below to get started!**"
    )
    
    await message.reply_text(text, reply_markup=MAIN_MENU_KEYBOARD)


# --- UNAUTHORIZED ACCESS ---
@Client.on_message(filters.command("start") & ~is_admin)
async def unauthorized_start(client, message):
    user = message.from_user
    
    text = (
        "┏━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃   🔒 ACCESS RESTRICTED   ┃\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        "╔══════════════════════════════╗\n"
        "║  ⚠️ UNAUTHORIZED ACCESS      ║\n"
        "╚══════════════════════════════╝\n\n"
        "**Sorry!** You don't have permission to use this bot.\n\n"
        "📌 **What to do:**\n"
        "┣ Contact your system administrator\n"
        "┣ Request access with your User ID\n"
        "┗ Wait for approval\n\n"
        "╭─────────────────────╮\n"
        f"│ 🆔 Your ID: `{user.id}`\n"
        f"│ 👤 Name: {user.first_name}\n"
        "╰─────────────────────╯\n\n"
        "💡 **Tip:** Screenshot this and send to your admin!"
    )
    
    await message.reply_text(text)


# --- MAIN MENU CALLBACK ---
@Client.on_callback_query(filters.regex("^main_menu$") & is_admin)
async def main_menu_callback(client, callback_query):
    await db.delete_state(callback_query.from_user.id)
    user = callback_query.from_user
    
    # Fetch comprehensive live stats
    try:
        logs, total_logs = await db.get_logs(limit=1)
        active_grants = await db.get_active_grants()
        stats = await db.get_stats()
        
        # Calculate expiring soon (within 24h)
        now = time.time()
        expiring_soon = sum(1 for g in active_grants if g.get('expires_at', 0) - now < 86400)
        
        active_count = len(active_grants)
        
    except Exception as e:
        import logging
        logging.error(f"Stats fetch error: {e}")
        active_count = 0
        total_logs = 0
        expiring_soon = 0
    
    # Modern dashboard
    text = (
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃  🌟 **GOOGLE DRIVE ACCESS MANAGER** ┃\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"👋 **Welcome, {user.first_name}!**\n\n"
        f"**📊 LIVE DASHBOARD**\n"
        f"• **Active Grants:** {active_count}\n"
        f"• **Total Logs:** {total_logs}\n"
    )
    
    if expiring_soon > 0:
        text += f"• **⚠️ Expiring Soon:** {expiring_soon}\n"
    
    text += (
        f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✨ **What would you like to do?**"
    )
    
    try:
        await callback_query.edit_message_text(
            text,
            reply_markup=MAIN_MENU_KEYBOARD
        )
    except Exception:
        await callback_query.answer()


# --- MODERN HELP MENU ---
HELP_TEXT = (
    "┏━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
    "┃   📖 HELP & GUIDE      ┃\n"
    "┗━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
    "╔══════════════════════════════╗\n"
    "║     🎯 MAIN FEATURES        ║\n"
    "╚══════════════════════════════╝\n\n"
    "**✨ Grant Access**\n"
    "• Single user → Single folder\n"
    "• Single user → Multiple folders\n"
    "• Multiple users → Single folder\n\n"
    "**🗂 Manage Folders**\n"
    "• View all users with access\n"
    "• Change user roles (Viewer/Editor)\n"
    "• Revoke access instantly\n"
    "• See folder statistics\n\n"
    "**⏰ Expiry Dashboard**\n"
    "• View timed grants\n"
    "• Extend expiry duration\n"
    "• Auto-revoke on expiration\n"
    "• Bulk operations\n\n"
    "**🔍 Search User**\n"
    "• Find by email address\n"
    "• View all user's access\n"
    "• Revoke all access at once\n\n"
    "**📊 Access Logs**\n"
    "• Complete audit trail\n"
    "• Filter by date and type\n"
    "• Export to CSV format\n\n"
    "**⚙️ Settings**\n"
    "┣ 🔧 Default role settings\n"
    "┣ 📄 Pagination size\n"
    "┣ 📢 Channel broadcast config\n"
    "┗ 🔔 Notification toggles\n\n"
    "╔══════════════════════════════╗\n"
    "║      💻 COMMANDS            ║\n"
    "╚══════════════════════════════╝\n\n"
    "`/start`  — 🏠 Main dashboard\n"
    "`/help`   — 📖 This guide\n"
    "`/stats`  — 📈 Activity analytics\n"
    "`/search` — 🔍 Quick user search\n"
    "`/cancel` — ❌ Cancel operation\n"
    "`/id`     — 🆔 Show your Telegram ID\n"
    "`/info`   — ℹ️ System info (admin only)\n\n"
    "╔══════════════════════════════╗\n"
    "║     💡 TIPS & TRICKS        ║\n"
    "╚══════════════════════════════╝\n\n"
    "🔹 Set expiry times for temporary access\n"
    "🔹 Enable channel broadcasts for team visibility\n"
    "🔹 Export logs regularly for compliance\n"
    "🔹 Use search to quickly find user access\n\n"
    "🆘 **Need more help?** Contact your administrator!"
)


@Client.on_callback_query(filters.regex("^help_menu$"))
async def help_menu_callback(client, callback_query):
    await callback_query.edit_message_text(
        HELP_TEXT,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Back to Dashboard", callback_data="main_menu")]
        ])
    )


@Client.on_message(filters.command("help") & is_admin)
async def help_command(client, message):
    await message.reply_text(
        HELP_TEXT,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Main Dashboard", callback_data="main_menu")]
        ])
    )


# --- CANCEL COMMAND ---
@Client.on_message(filters.command("cancel") & is_admin)
async def cancel_command(client, message):
    await db.delete_state(message.from_user.id)
    
    text = (
        "┏━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃  ❌ OPERATION CANCELLED  ┃\n"
        "┗━━━━━━━━━━━━━━━━━━━━┛\n\n"
        "✅ Current operation has been cancelled.\n"
        "🏠 Returning to main dashboard..."
    )
    
    await message.reply_text(text, reply_markup=MAIN_MENU_KEYBOARD)


# --- NOOP CALLBACK ---
@Client.on_callback_query(filters.regex("^noop$"))
async def noop_callback(client, callback_query):
    await callback_query.answer("ℹ️ This is just an indicator", show_alert=False)


# --- QUICK STATS COMMAND ---
@Client.on_message(filters.command("quickstats") & is_admin)
async def quick_stats_command(client, message):
    """Show quick stats in a compact, professional format"""
    try:
        stats = await db.get_stats()
        active_grants = await db.get_active_grants()
        
        now = time.time()
        expiring_today = sum(1 for g in active_grants if 0 < g.get('expires_at', 0) - now < 86400)
        
        text = (
            "┏━━━━━━━━━━━━━━━━━━━┓\n"
            "┃   ⚡ QUICK STATS   ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━┛\n\n"
            f"📊 Today: **{stats.get('today', 0)}** actions\n"
            f"📅 This Week: **{stats.get('week', 0)}** actions\n"
            f"📈 This Month: **{stats.get('month', 0)}** actions\n"
            f"🎯 Total: **{stats.get('total', 0)}** actions\n\n"
            f"⏰ Active Grants: **{stats.get('active_grants', 0)}**\n"
            f"⚠️ Expiring Today: **{expiring_today}**\n\n"
            f"🔝 Top Folder: **{stats.get('top_folder', 'N/A')}**\n"
            f"👑 Top Admin: **{stats.get('top_admin', 'N/A')}**"
        )
        
        await message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 Full Statistics", callback_data="stats_menu")],
                [InlineKeyboardButton("🏠 Dashboard", callback_data="main_menu")]
            ])
        )
    except Exception as e:
        await message.reply_text(f"❌ Error fetching stats: {e}")