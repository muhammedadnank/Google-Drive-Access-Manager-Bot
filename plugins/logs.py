from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.database import db
import datetime

# --- View Logs ---
@Client.on_callback_query(filters.regex("^logs_menu$"))
async def view_logs(client, callback_query):
    logs, total = await db.get_logs(limit=50) # Get last 50
    
    if not logs:
        await callback_query.edit_message_text(
            "📊 **Access Logs**\n\nNo activity recorded yet.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Back", callback_data="main_menu")]])
        )
        return

    text = "📊 **Recent Activity**\n\n"
    for log in logs:
        ts = datetime.datetime.fromtimestamp(log['timestamp']).strftime('%Y-%m-%d %H:%M')
        action = log['action'].replace('_', ' ').title()
        details = log.get('details', {})
        email = details.get('email', 'N/A')
        folder = details.get('folder_name', 'N/A')
        role = details.get('role', '') or details.get('new_role', '')
        
        text += f"🔹 **{action}** - `{email}`\n"
        text += f"   📂 {folder}"
        if role: text += f" | 🔑 {role}"
        text += f"\n   🕒 {ts} | 👤 {log.get('admin_name')}\n\n"

    # Save logs to state for pagination
    await db.set_state(callback_query.from_user.id, "VIEWING_LOGS", {"logs": logs})
    
    await show_logs_page(callback_query, logs, 1)

async def show_logs_page(callback_query, logs, page):
    per_page = 5
    start = (page - 1) * per_page
    end = start + per_page
    current_logs = logs[start:end]
    
    total_pages = (len(logs) + per_page - 1) // per_page
    
    text = f"📊 **Activity Logs (Page {page}/{total_pages})**\n\n"
    
    type_icons = {"grant": "➕", "role_change": "🔄", "remove": "🗑"}
    
    for log in current_logs:
        ts = datetime.datetime.fromtimestamp(log['timestamp']).strftime('%m-%d %H:%M')
        log_type = log.get('type', log.get('action', 'unknown'))
        icon = type_icons.get(log_type, "▪️")
        action = log_type.replace('_', ' ').upper()
        details = log.get('details', {})
        email = details.get('email', 'N/A')
        folder = details.get('folder_name', details.get('folder', 'Unknown'))
        
        text += f"{icon} `{action}` → `{email}`\n"
        text += f"   📂 {folder} 🕒 {ts}\n\n"

    buttons = []
    if page > 1:
        buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"log_page_{page-1}"))
    if page < total_pages:
        buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"log_page_{page+1}"))
        
    keyboard = [buttons] if buttons else []
    keyboard.append([InlineKeyboardButton("🗑 Clear Logs", callback_data="clear_logs")])
    keyboard.append([InlineKeyboardButton("🏠 Back", callback_data="main_menu")])
    
    await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

@Client.on_callback_query(filters.regex(r"^log_page_(\d+)$"))
async def logs_pagination(client, callback_query):
    page = int(callback_query.matches[0].group(1))
    user_id = callback_query.from_user.id
    
    state, data = await db.get_state(user_id)
    if state != "VIEWING_LOGS": return
    
    await show_logs_page(callback_query, data["logs"], page)

@Client.on_callback_query(filters.regex("^clear_logs$"))
async def clear_logs_handler(client, callback_query):
    await db.clear_logs()
    await callback_query.answer("Logs cleared!")
    await callback_query.edit_message_text("📊 **Logs Cleared**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Back", callback_data="main_menu")]]))
