from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.database import db
from utils.states import WAITING_DEFAULT_ROLE, WAITING_PAGE_SIZE
from utils.time import safe_edit
from utils.filters import is_admin

# --- Settings Menu ---
@Client.on_callback_query(filters.regex("^settings_menu$") & is_admin)
async def view_settings_menu(client, callback_query):
    user_id = callback_query.from_user.id
    
    default_role = await db.get_setting("default_role", "viewer")
    page_size = await db.get_setting("page_size", 5)
    notif = await db.get_setting("notifications", True)
    
    notif_text = "🔔 ON" if notif else "🔕 OFF"
    
    text = (
        "⚙️ **Settings**\n\n"
        f"🔹 **Default Role**: `{default_role}`\n"
        f"🔹 **Folders Per Page**: `{page_size}`\n"
        f"🔹 **Notifications**: {notif_text}\n"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Change Default Role", callback_data="set_def_role")],
        [InlineKeyboardButton("📄 Change Page Size", callback_data="set_page_size")],
        [InlineKeyboardButton(f"Toggle Notifications ({notif_text})", callback_data="toggle_notif")],
        [InlineKeyboardButton("📢 Channel Settings", callback_data="channel_settings")],
        [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
    ])
    
    await safe_edit(callback_query, text, reply_markup=keyboard)

# --- Toggle Notification ---
@Client.on_callback_query(filters.regex("^toggle_notif$") & is_admin)
async def toggle_notifications(client, callback_query):
    current = await db.get_setting("notifications", True)
    await db.update_setting("notifications", not current)
    # Refresh menu
    await view_settings_menu(client, callback_query)

# --- Change Default Role ---
@Client.on_callback_query(filters.regex("^set_def_role$") & is_admin)
async def change_default_role(client, callback_query):
    await safe_edit(callback_query.message, 
        "Select Default Role:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Viewer", callback_data="save_role_viewer"),
             InlineKeyboardButton("Editor", callback_data="save_role_editor")],
            [InlineKeyboardButton("Cancel", callback_data="settings_menu")]
        ])
    )

@Client.on_callback_query(filters.regex(r"^save_role_(viewer|editor)$") & is_admin)
async def save_role(client, callback_query):
    role = callback_query.matches[0].group(1)
    await db.update_setting("default_role", role)
    await callback_query.answer(f"Default role set to {role}!")
    await view_settings_menu(client, callback_query)

# --- Change Page Size ---
@Client.on_callback_query(filters.regex("^set_page_size$") & is_admin)
async def prompt_page_size(client, callback_query):
    await db.set_state(callback_query.from_user.id, WAITING_PAGE_SIZE)
    await safe_edit(callback_query.message, 
        "📄 **Enter Page Size** (3-10):",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data="settings_menu")]])
    )

from utils.filters import check_state
@Client.on_message(check_state(WAITING_PAGE_SIZE) & filters.text & is_admin)
async def set_page_size_handler(client, message):
    try:
        size = int(message.text)
        if 3 <= size <= 10:
            await db.update_setting("page_size", size)
            await db.delete_state(message.from_user.id)
            await message.reply_text(f"✅ Page size updated to {size}!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⚙️ Back to Settings", callback_data="settings_menu")]]))
        else:
            await message.reply_text("❌ Please enter a number between 3 and 10.")
    except ValueError:
        await message.reply_text("❌ Invalid number.")
