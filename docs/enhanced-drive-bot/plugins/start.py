"""
Start Plugin
VJ-FILTER-BOT inspired main menu and start handlers
"""

from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from config import Config
from templates.messages import Messages, Emoji
from utils.decorators import admin_command, admin_callback
from utils.logger import setup_logger
from services.database import Database

logger = setup_logger(__name__)

# Bot start time (for uptime)
bot_start_time = datetime.utcnow()

def get_uptime() -> str:
    """Calculate bot uptime (VJ pattern)"""
    delta = datetime.utcnow() - bot_start_time
    
    days = delta.days
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Generate main menu keyboard (VJ-inspired layout)"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"{Emoji.GRANT} Grant Access",
                callback_data="main_grant"
            ),
            InlineKeyboardButton(
                f"{Emoji.FOLDER} Manage Folders",
                callback_data="main_manage"
            )
        ],
        [
            InlineKeyboardButton(
                f"{Emoji.TIMER} Expiry Dashboard",
                callback_data="main_expiry"
            ),
            InlineKeyboardButton(
                "📋 Access Logs",
                callback_data="main_logs"
            )
        ],
        [
            InlineKeyboardButton(
                "🔍 Search User",
                callback_data="main_search"
            ),
            InlineKeyboardButton(
                "⚙️ Settings",
                callback_data="main_settings"
            )
        ],
        [
            InlineKeyboardButton(
                "❓ Help",
                callback_data="main_help"
            ),
            InlineKeyboardButton(
                "📊 Stats",
                callback_data="main_stats"
            )
        ]
    ])

@Client.on_message(filters.command("start") & filters.private)
@admin_command
async def start_command(client: Client, message: Message):
    """
    /start command handler (VJ-style welcome)
    
    Shows main menu with bot info and navigation buttons
    """
    # Get bot info
    me = await client.get_me()
    
    # Format start message
    start_text = Messages.START_MESSAGE.format(
        name=message.from_user.first_name,
        bot_name=me.first_name,
        bot_username=me.username,
        version=Config.BOT_VERSION,
        uptime=get_uptime()
    )
    
    # Send with main menu
    await message.reply_text(
        start_text,
        reply_markup=get_main_menu_keyboard()
    )
    
    logger.info(f"User {message.from_user.id} started the bot")

@Client.on_message(filters.command("help") & filters.private)
@admin_command
async def help_command(client: Client, message: Message):
    """
    /help command handler
    
    Shows help information and available commands
    """
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"{Emoji.BACK} Back to Menu",
                callback_data="main_menu"
            )
        ]
    ])
    
    await message.reply_text(
        Messages.HELP_MESSAGE,
        reply_markup=keyboard
    )

@Client.on_message(filters.command("cancel") & filters.private)
async def cancel_command(client: Client, message: Message):
    """
    /cancel command handler (VJ pattern)
    
    Cancels any ongoing operation and returns to main menu
    """
    db = Database()
    
    # Clear user state
    await db.clear_user_state(message.from_user.id)
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🏠 Main Menu",
                callback_data="main_menu"
            )
        ]
    ])
    
    await message.reply_text(
        Messages.OPERATION_CANCELLED,
        reply_markup=keyboard
    )
    
    logger.info(f"User {message.from_user.id} cancelled operation")

@Client.on_message(filters.command("id"))
async def id_command(client: Client, message: Message):
    """
    /id command handler
    
    Shows user's Telegram ID (available to all users)
    """
    user_id = message.from_user.id
    username = message.from_user.username or "None"
    first_name = message.from_user.first_name
    
    id_text = f"""
🆔 **Your Telegram Information**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 **Name:** {first_name}
🔤 **Username:** @{username}
🆔 **User ID:** `{user_id}`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Note:** User ID is unique and permanent.
"""
    
    # If in a group, show group info too
    if message.chat.type != "private":
        chat_id = message.chat.id
        chat_title = message.chat.title
        
        id_text += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**📱 CHAT INFO**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 **Title:** {chat_title}
🆔 **Chat ID:** `{chat_id}`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    await message.reply_text(id_text)

# ═══════════════════════════════════════
# CALLBACK HANDLERS (VJ Pattern)
# ═══════════════════════════════════════

@Client.on_callback_query(filters.regex("^main_menu$"))
@admin_callback
async def main_menu_callback(client: Client, callback_query: CallbackQuery):
    """Return to main menu"""
    me = await client.get_me()
    
    start_text = Messages.START_MESSAGE.format(
        name=callback_query.from_user.first_name,
        bot_name=me.first_name,
        bot_username=me.username,
        version=Config.BOT_VERSION,
        uptime=get_uptime()
    )
    
    await callback_query.message.edit_text(
        start_text,
        reply_markup=get_main_menu_keyboard()
    )
    
    await callback_query.answer()

@Client.on_callback_query(filters.regex("^main_help$"))
@admin_callback
async def help_callback(client: Client, callback_query: CallbackQuery):
    """Show help from button"""
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"{Emoji.BACK} Back to Menu",
                callback_data="main_menu"
            )
        ]
    ])
    
    await callback_query.message.edit_text(
        Messages.HELP_MESSAGE,
        reply_markup=keyboard
    )
    
    await callback_query.answer()

@Client.on_callback_query(filters.regex("^main_grant$"))
@admin_callback
async def grant_callback(client: Client, callback_query: CallbackQuery):
    """Route to grant module"""
    # Import here to avoid circular imports
    from plugins.grant import show_grant_mode_select
    
    await show_grant_mode_select(client, callback_query)

@Client.on_callback_query(filters.regex("^main_manage$"))
@admin_callback
async def manage_callback(client: Client, callback_query: CallbackQuery):
    """Route to manage module"""
    from plugins.manage import show_folder_list
    
    await show_folder_list(client, callback_query)

@Client.on_callback_query(filters.regex("^main_expiry$"))
@admin_callback
async def expiry_callback(client: Client, callback_query: CallbackQuery):
    """Route to expiry module"""
    from plugins.expiry import show_expiry_dashboard
    
    await show_expiry_dashboard(client, callback_query)

@Client.on_callback_query(filters.regex("^main_logs$"))
@admin_callback
async def logs_callback(client: Client, callback_query: CallbackQuery):
    """Route to logs module"""
    from plugins.logs import show_logs_menu
    
    await show_logs_menu(client, callback_query)

@Client.on_callback_query(filters.regex("^main_search$"))
@admin_callback
async def search_callback(client: Client, callback_query: CallbackQuery):
    """Route to search module"""
    await callback_query.answer(
        "🔍 Search feature coming soon!",
        show_alert=True
    )

@Client.on_callback_query(filters.regex("^main_settings$"))
@admin_callback
async def settings_callback(client: Client, callback_query: CallbackQuery):
    """Route to settings module"""
    from plugins.settings import show_settings_menu
    
    await show_settings_menu(client, callback_query)

@Client.on_callback_query(filters.regex("^main_stats$"))
@admin_callback
async def stats_callback(client: Client, callback_query: CallbackQuery):
    """Route to stats module"""
    from plugins.stats import show_stats_dashboard
    
    await show_stats_dashboard(client, callback_query)

@Client.on_callback_query(filters.regex("^close_menu$"))
@admin_callback
async def close_callback(client: Client, callback_query: CallbackQuery):
    """Close/delete message (VJ pattern)"""
    await callback_query.message.delete()
    await callback_query.answer("Menu closed")

logger.info("✅ Start plugin loaded")
