from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.filters import is_admin
from services.database import db

# Define Main Menu Keyboard
MAIN_MENU_KEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("➕ Grant Access", callback_data="grant_menu"),
        InlineKeyboardButton("📂 Manage Folders", callback_data="manage_menu")
    ],
    [
        InlineKeyboardButton("📊 Access Logs", callback_data="logs_menu"),
        InlineKeyboardButton("⚙️ Settings", callback_data="settings_menu")
    ],
    [
        InlineKeyboardButton("❓ Help", callback_data="help_menu")
    ]
])

# TEMPORARY DEBUG HANDLER - Shows your user ID
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
    await message.reply_text(
        f"👋 **Welcome, {user.first_name}!**\n\n"
        "I am the **Drive Access Manager Bot**.\n"
        "Use the menu below to manage Google Drive permissions.",
        reply_markup=MAIN_MENU_KEYBOARD
    )

@Client.on_message(filters.command("start") & ~is_admin)
async def unauthorized_start(client, message):
    await message.reply_text(
        "🚫 **Access Denied**\n\n"
        "You do not have permission to use this bot.\n"
        "Please contact the administrator.\n\n"
        f"Your ID: `{message.from_user.id}`"
    )

@Client.on_callback_query(filters.regex("^main_menu$") & is_admin)
async def main_menu_callback(client, callback_query):
    await db.delete_state(callback_query.from_user.id)
    await callback_query.edit_message_text(
        "👋 **Drive Access Manager**\n\n"
        "What would you like to do?",
        reply_markup=MAIN_MENU_KEYBOARD
    )

# --- Help ---
HELP_TEXT = (
    "❓ **Help — Drive Access Manager**\n\n"
    "**➕ Grant Access**\n"
    "Grant Viewer or Editor access to a Google Drive folder.\n\n"
    "**📂 Manage Folders**\n"
    "View current permissions, change roles, or revoke access.\n\n"
    "**📊 Access Logs**\n"
    "View a history of all permission changes.\n\n"
    "**⚙️ Settings**\n"
    "Configure default role, page size, and notifications.\n\n"
    "**Commands:**\n"
    "`/start` — Main menu\n"
    "`/help` — This help text\n"
    "`/cancel` — Cancel current operation\n"
    "`/id` — Show your user ID"
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
