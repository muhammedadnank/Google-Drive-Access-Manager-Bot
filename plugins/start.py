from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.filters import is_admin
from services.database import db
from config import START_TIME, VERSION
import time
from utils.time import get_uptime

# Define Main Menu Keyboard
MAIN_MENU_KEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("➕ Grant Access", callback_data="grant_menu"),
        InlineKeyboardButton("📂 Manage Folders", callback_data="manage_menu")
    ],
    [
        InlineKeyboardButton("⏰ Expiry Dashboard", callback_data="expiry_menu"),
        InlineKeyboardButton("📋 Templates", callback_data="templates_menu")
    ],
    [
        InlineKeyboardButton("📊 Access Logs", callback_data="logs_menu"),
        InlineKeyboardButton("⚙️ Settings", callback_data="settings_menu")
    ],
    [
        InlineKeyboardButton("🔍 Search User", callback_data="search_user"),
        InlineKeyboardButton("❓ Help", callback_data="help_menu")
    ]
])


# --- Show User ID ---
@Client.on_message(filters.command("id"))
async def show_id(client, message):
    user = message.from_user
    await message.reply_text(
        f"🆔 **Your Telegram Info:**\n\n"
        f"User ID: `{user.id}`\n"
        f"Username: @{user.username or 'N/A'}\n"
        f"First Name: {user.first_name}\n"
        f"Is Bot: {user.is_bot}"
    )

@Client.on_message(filters.command("start") & is_admin)
async def start_handler(client, message):
    user = message.from_user
    me = await client.get_me()
    uptime = get_uptime(START_TIME)
    
    text = (
        "╔════════════════════════════╗\n"
        "  🗂 **Drive Access Manager**\n"
        "╚════════════════════════════╝\n\n"
        f"👋 Welcome back, **{user.first_name}**!\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🤖 **BOT INFO**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏷 **Name**     : {me.first_name}\n"
        f"👤 **Username** : @{me.username}\n"
        f"🔄 **Version**  : v{VERSION}\n"
        f"⏱️ **Uptime**   : {uptime}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    
    await message.reply_text(text, reply_markup=MAIN_MENU_KEYBOARD)

@Client.on_message(filters.command("start") & ~is_admin)
async def unauthorized_start(client, message):
    await message.reply_text(
        "╔══════════════════════╗\n"
        "  🔒 **Access Restricted**\n"
        "╚══════════════════════╝\n\n"
        "⚠️ You are not authorized to use this bot.\n"
        "Contact the administrator for access.\n\n"
        f"🆔 Your ID: `{message.from_user.id}`"
    )

@Client.on_callback_query(filters.regex("^main_menu$") & is_admin)
async def main_menu_callback(client, callback_query):
    await db.delete_state(callback_query.from_user.id)
    user = callback_query.from_user
    
    # Fetch live stats
    logs, total_logs = await db.get_logs(limit=1)
    active_grants = await db.get_active_grants()
    
    # Calculate expiring soon (within 24h)
    now = time.time()
    expiring_soon = sum(1 for g in active_grants if g['expires_at'] - now < 86400)
    
    stats_text = (
        f"📈 **Quick Stats**\n"
        f"┣ ⏰ Active Timed Grants: `{len(active_grants)}`\n"
        f"┣ 📝 Total Log Entries: `{total_logs}`\n"
        f"┗ ⚠️ Expiring Soon (24h): `{expiring_soon}`"
    )
    
    try:
        await callback_query.edit_message_text(
            f"╔════════════════════════════╗\n"
            f"  🗂 **Drive Access Manager**\n"
            f"╚════════════════════════════╝\n\n"
            f"👋 Welcome back, **{user.first_name}**!\n\n"
            f"{stats_text}\n\n"
            f"▸ Select an option below:",
            reply_markup=MAIN_MENU_KEYBOARD
        )
    except Exception:
        await callback_query.answer()

# --- Help ---
HELP_TEXT = (
    "╔══════════════════════╗\n"
    "  ❓ **Help & Commands**\n"
    "╚══════════════════════╝\n\n"
    "**➕ Grant Access**\n"
    "┗ Grant Viewer/Editor access with expiry timer\n\n"
    "**📂 Manage Folders**\n"
    "┗ View permissions, change roles, revoke access\n\n"
    "**⏰ Expiry Dashboard**\n"
    "┗ View timed grants, extend, revoke, bulk import\n\n"
    "**📊 Access Logs**\n"
    "┗ Full audit trail of all permission changes\n\n"
    "**⚙️ Settings**\n"
    "┗ Default role, page size, notifications\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "📌 **Commands**\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "`/start` — Main menu\n"
    "`/help` — This help text\n"
    "`/cancel` — Cancel current operation\n"
    "`/id` — Show your Telegram ID"
)

@Client.on_callback_query(filters.regex("^help_menu$"))
async def help_menu_callback(client, callback_query):
    await callback_query.edit_message_text(
        HELP_TEXT,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Back to Menu", callback_data="main_menu")]
        ])
    )

@Client.on_message(filters.command("help") & is_admin)
async def help_command(client, message):
    await message.reply_text(
        HELP_TEXT,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ])
    )

# --- Cancel Command ---
@Client.on_message(filters.command("cancel") & is_admin)
async def cancel_command(client, message):
    await db.delete_state(message.from_user.id)
    await message.reply_text(
        "🚫 **Operation Cancelled.**",
        reply_markup=MAIN_MENU_KEYBOARD
    )

# --- Noop (page indicator button) ---
@Client.on_callback_query(filters.regex("^noop$"))
async def noop_callback(client, callback_query):
    await callback_query.answer()
