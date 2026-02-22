from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.filters import is_admin
from utils.time import safe_edit
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
        InlineKeyboardButton("📈 Statistics", callback_data="stats_menu")
    ],
    [
        InlineKeyboardButton("⚙️ Settings", callback_data="settings_menu"),
        InlineKeyboardButton("💡 Help & Guide", callback_data="help_menu")
    ],
    [
        InlineKeyboardButton("🔧 System Info", callback_data="info_refresh"),
        InlineKeyboardButton("📊 Analytics", callback_data="analytics_menu")
    ]
])


# --- MODERN ID DISPLAY ---
# ✅ FIXED: Merged into single decorator using OR filter
@Client.on_message(filters.command("id") | (filters.regex(r"(?i)^(?:\.id|id)$") & filters.private))
async def show_id(client, message):
    user = message.from_user

    text = (
        "**🆔 YOUR TELEGRAM INFORMATION**\n\n"
        f"**👤 Name:** {user.first_name}"
    )

    if user.last_name:
        text += f" {user.last_name}"

    text += (
        f"\n**🔑 User ID:** `{user.id}`\n"
        f"**📱 Username:** @{user.username or 'Not set'}\n"
        f"**🤖 Account Type:** {'Bot' if user.is_bot else 'User'}\n\n\n"
        "💡 **Tip:** Share your User ID with admins to request access"
    )

    await message.reply_text(text)


# --- PROFESSIONAL START COMMAND ---
# ✅ FIXED: Merged into single decorator using OR filter
@Client.on_message((filters.command("start") | (filters.regex(r"(?i)^(?:\.start|start)$") & filters.private)) & is_admin)
async def start_handler(client, message):
    user = message.from_user
    import logging
    logging.getLogger(__name__).info(f"✅ /start received from admin user_id={user.id}")
    await db.delete_state(user.id)
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
        f"**🌟 GOOGLE DRIVE ACCESS MANAGER**\n\n\n"
        f"👋 **Welcome back, {user.first_name}!**\n\n"
        f"**🤖 BOT STATUS**\n"
        f"• **Name:** {me.first_name}\n"
        f"• **Handle:** @{me.username}\n"
        f"• **Version:** `v{VERSION}`\n"
        f"• **Uptime:** `{uptime}`\n\n"
        f"**📊 DASHBOARD OVERVIEW**\n"
        f"• **Active Grants:** {active_count}\n"
        f"• **Total Actions:** {total_actions}\n\n\n"
        f"💡 **Select an option below to continue**"
    )

    await message.reply_text(text, reply_markup=MAIN_MENU_KEYBOARD)


# --- UNAUTHORIZED ACCESS ---
# ✅ FIXED: Merged into single decorator using OR filter
@Client.on_message((filters.command("start") | (filters.regex(r"(?i)^(?:\.start|start)$") & filters.private)) & ~is_admin)
async def unauthorized_start(client, message):
    user = message.from_user
    import logging
    logging.getLogger(__name__).info(f"⛔ /start from unauthorized user_id={user.id}")

    text = (
        "**🔒 ACCESS RESTRICTED**\n\n"
        "⚠️ **You are not authorized to use this bot.**\n\n"
        "**📌 What to do:**\n"
        "• Contact your system administrator\n"
        "• Request access with your User ID\n"
        "• Wait for approval\n\n"
        "**🆔 Your Information:**\n"
        f"• **ID:** `{user.id}`\n"
        f"• **Name:** {user.first_name}\n\n"
        "💡 **Tip:** Screenshot this message and send it to your admin"
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
        f"**🌟 GOOGLE DRIVE ACCESS MANAGER**\n\n"
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
        await safe_edit(callback_query,
            text,
            reply_markup=MAIN_MENU_KEYBOARD
        )
    except Exception:
        await callback_query.answer()


# --- MODERN HELP MENU ---
HELP_TEXT = (
    "**      💡 HELP & GUIDE**\n\n"
    "**🎯 MAIN FEATURES**\n\n"
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
    "• Configure default roles\n"
    "• Adjust pagination size\n"
    "• Channel broadcast settings\n"
    "• Notification preferences\n\n\n\n"
    "**💻 AVAILABLE COMMANDS**\n\n"
    "`/start` — Main dashboard\n"
    "`/help` — This help guide\n"
    "`/stats` — Detailed statistics\n"
    "`/search` — Quick user search\n"
    "`/cancel` — Cancel current operation\n"
    "`/id` — Show your Telegram ID\n"
    "`/quickstats` — Quick overview\n\n\n\n"
    "**💎 PRO TIPS**\n\n"
    "• Set expiry times for temporary access\n"
    "• Enable broadcasts for team visibility\n"
    "• Export logs regularly for compliance\n"
    "• Use search for quick access lookups\n\n\n\n"
    "🆘 **Need help?** Contact your administrator"
)


@Client.on_callback_query(filters.regex("^help_menu$") & is_admin)
async def help_menu_callback(client, callback_query):
    await safe_edit(callback_query,
        HELP_TEXT,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Back to Dashboard", callback_data="main_menu")]
        ])
    )


# ✅ FIXED: Merged into single decorator using OR filter
@Client.on_message((filters.command("help") | (filters.regex(r"(?i)^(?:\.help|help)$") & filters.private)) & is_admin)
async def help_command(client, message):
    await message.reply_text(
        HELP_TEXT,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Main Dashboard", callback_data="main_menu")]
        ])
    )


# --- CANCEL COMMAND ---
# ✅ FIXED: Merged into single decorator using OR filter
@Client.on_message((filters.command("cancel") | (filters.regex(r"(?i)^(?:\.cancel|cancel)$") & filters.private)) & is_admin)
async def cancel_command(client, message):
    await db.delete_state(message.from_user.id)

    text = (
        "**❌ OPERATION CANCELLED**\n\n\n"
        "✅ Your current operation has been cancelled.\n"
        "🏠 Returning to main dashboard...\n\n"
        "━━━━━━━━━━━━━━━━━━━━━"
    )

    await message.reply_text(text, reply_markup=MAIN_MENU_KEYBOARD)


# --- NOOP CALLBACK ---
@Client.on_callback_query(filters.regex("^noop$"))
async def noop_callback(client, callback_query):
    await callback_query.answer("ℹ️ This is just an indicator", show_alert=False)


# --- QUICK STATS COMMAND ---
# ✅ FIXED: Merged into single decorator using OR filter
@Client.on_message((filters.command("quickstats") | (filters.regex(r"(?i)^(?:\.quickstats|quickstats)$") & filters.private)) & is_admin)
async def quick_stats_command(client, message):
    """Show quick stats in a compact, professional format"""
    try:
        stats = await db.get_stats()
        active_grants = await db.get_active_grants()

        now = time.time()
        expiring_today = sum(1 for g in active_grants if 0 < g.get('expires_at', 0) - now < 86400)

        text = (
            "**⚡ QUICK STATISTICS**\n\n\n"
            "**📊 Activity Overview**\n"
            f"• **Today:** {stats.get('today', 0)} actions\n"
            f"• **This Week:** {stats.get('week', 0)} actions\n"
            f"• **This Month:** {stats.get('month', 0)} actions\n"
            f"• **All Time:** {stats.get('total', 0)} actions\n\n"
            "**⏰ Grant Status**\n"
            f"• **Active Grants:** {stats.get('active_grants', 0)}\n"
            f"• **Expiring Today:** {expiring_today}\n\n"
            "**🏆 Top Performers**\n"
            f"• **Top Folder:** {stats.get('top_folder', 'N/A')}\n"
            f"• **Top Admin:** {stats.get('top_admin', 'N/A')}\n\n"
        )

        await message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 Full Statistics", callback_data="stats_menu")],
                [InlineKeyboardButton("🏠 Dashboard", callback_data="main_menu")]
            ])
        )
    except Exception as e:
        await message.reply_text(f"❌ **Error fetching statistics**\n\n`{e}`")


# --- ABOUT COMMAND ---
@Client.on_message(filters.command("about") & is_admin)
async def about_command(client, message):
    """Show bot information"""
    me = await client.get_me()
    uptime = get_uptime(START_TIME)

    try:
        stats = await db.get_stats()
        total_actions = stats.get('total', 0)
    except:
        total_actions = 0

    text = (
        "**ℹ️ ABOUT THIS BOT**\n\n\n"
        f"**🤖 Bot Information**\n"
        f"• **Name:** {me.first_name}\n"
        f"• **Username:** @{me.username}\n"
        f"• **Bot ID:** `{me.id}`\n"
        f"• **Version:** `v{VERSION}`\n\n"
        f"**📊 Performance**\n"
        f"• **Uptime:** {uptime}\n"
        f"• **Total Actions:** {total_actions}\n\n"
        f"**🔧 Technology**\n"
        f"• **Framework:** Pyrofork\n"
        f"• **Database:** MongoDB\n"
        f"• **API:** Google Drive API v3\n\n\n"
        "**✨ Features**\n"
        "• Automated access management\n"
        "• Time-based grants with auto-revoke\n"
        "• Complete audit trail & logs\n"
        "• Channel broadcast notifications\n"
        "• Multi-admin support\n\n\n"
        "💙 **Powered by Pyrofork & Google Drive API**"
    )

    await message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Dashboard", callback_data="main_menu")]
        ])
    )
