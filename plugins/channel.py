from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.database import db
from services.broadcast import broadcast, get_channel_config
from utils.states import WAITING_CHANNEL_ID
from utils.filters import check_state
import logging

LOGGER = logging.getLogger(__name__)

# --- Channel Settings Menu ---
@Client.on_callback_query(filters.regex("^channel_settings$"))
async def channel_settings_menu(client, callback_query):
    config = await get_channel_config()
    
    channel_id = config.get("channel_id")
    status = "🟢 Enabled" if channel_id else "🔴 Not Configured"
    chan_text = f"`{channel_id}`" if channel_id else "None"
    
    # Toggle Icons
    def icon(key):
        return "☑️" if config.get(key) else "☐"
        
    text = (
        "📢 **Channel Integration Settings**\n\n"
        f"Status: **{status}**\n"
        f"Channel ID: {chan_text}\n\n"
        "**Event Broadcast Toggles:**"
    )
    
    keyboard = [
        [InlineKeyboardButton(f"{icon('log_grants')} Indiv. Grants", callback_data="tgl_log_grants"),
         InlineKeyboardButton(f"{icon('log_revokes')} Indiv. Revokes", callback_data="tgl_log_revokes")],
        [InlineKeyboardButton(f"{icon('log_role_changes')} Role Changes", callback_data="tgl_log_role_changes"),
         InlineKeyboardButton(f"{icon('log_bulk')} Bulk Ops", callback_data="tgl_log_bulk")],
        [InlineKeyboardButton(f"{icon('log_alerts')} System Alerts", callback_data="tgl_log_alerts"),
         InlineKeyboardButton(f"{icon('log_summary')} Daily Summary", callback_data="tgl_log_summary")],
        [InlineKeyboardButton("✏️ Set Channel ID", callback_data="set_channel_id")],
        [InlineKeyboardButton("🧪 Send Test Message", callback_data="test_channel_msg")],
        [InlineKeyboardButton("⬅️ Back to Settings", callback_data="settings_menu")]
    ]
    
    await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# --- Toggle Handling ---
@Client.on_callback_query(filters.regex("^tgl_(.+)$"))
async def toggle_log_setting(client, callback_query):
    key = callback_query.matches[0].group(1)
    
    # Get current config
    config = await get_channel_config()
    current_val = config.get(key, False)
    
    # Update config
    config[key] = not current_val
    await db.update_setting("channel_config", config)
    
    await channel_settings_menu(client, callback_query)

# --- Set Channel ID ---
@Client.on_callback_query(filters.regex("^set_channel_id$"))
async def prompt_channel_id(client, callback_query):
    await db.set_state(callback_query.from_user.id, WAITING_CHANNEL_ID)
    await callback_query.message.edit_text(
        "📢 **Set Channel ID**\n\n"
        "Forward a message from your private channel here to auto-detect ID.\n"
        "Or manually enter the Channel ID (e.g., `-1001234567890`).\n\n"
        "⚠️ Bot must be an **Admin** in the channel!",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data="channel_settings")]])
    )

@Client.on_message(check_state(WAITING_CHANNEL_ID))
async def receive_channel_id(client, message):
    user_id = message.from_user.id
    
    channel_id = None
    
    # Auto-detect from forward
    if message.forward_from_chat and message.forward_from_chat.type.name == "CHANNEL":
        channel_id = message.forward_from_chat.id
    
    # Try parsing text
    if not channel_id and message.text:
        try:
            channel_id = int(message.text.strip())
        except ValueError:
            pass
            
    if not channel_id:
        await message.reply_text("❌ Invalid ID or not a channel forward. Try again.")
        return
        
    # Update DB
    config = await get_channel_config()
    config["channel_id"] = channel_id
    await db.update_setting("channel_config", config)
    await db.delete_state(user_id)
    
    await message.reply_text(
        f"✅ Channel ID set to `{channel_id}`!",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📢 Back to Channel Settings", callback_data="channel_settings")]])
    )

# --- Test Message ---
@Client.on_callback_query(filters.regex("^test_channel_msg$"))
async def send_test_message(client, callback_query):
    config = await get_channel_config()
    if not config.get("channel_id"):
        await callback_query.answer("⚠️ Configure Channel ID first!", show_alert=True)
        return
        
    await callback_query.answer("Sending test message...")
    
    try:
        await broadcast(client, "test", {})
        await callback_query.message.reply_text("✅ Test message sent! Check your channel.")
    except Exception as e:
        await callback_query.message.reply_text(f"❌ Failed: {e}")
