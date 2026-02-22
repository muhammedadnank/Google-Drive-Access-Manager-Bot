from pyrogram.enums import ButtonStyle
import csv
import io
import time
from datetime import datetime
from utils.time import IST
from utils.time import safe_edit
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.database import db
from utils.filters import is_admin
import logging

LOGGER = logging.getLogger(__name__)

@Client.on_callback_query(filters.regex("^export_logs$") & is_admin)
async def export_logs_menu(client, callback_query):
    await safe_edit(callback_query, 
        "📤 **Export Access Logs**\n\n"
        "Select the range of logs to export:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Today", callback_data="export_csv_today", style=ButtonStyle.PRIMARY),
             InlineKeyboardButton("This Week", callback_data="export_csv_week", style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("This Month", callback_data="export_csv_month", style=ButtonStyle.PRIMARY),
             InlineKeyboardButton("All Time", callback_data="export_csv_all", style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("⬅️ Back", callback_data="logs_menu", style=ButtonStyle.PRIMARY)]
        ])
    )

@Client.on_callback_query(filters.regex("^export_csv_") & is_admin)
async def execute_export(client, callback_query):
    range_type = callback_query.data.split("_")[2]
    
    # Calculate timestamp filter
    now = time.time()
    query = {}
    
    if range_type == "today":
        start_time = now - 86400
        query = {"timestamp": {"$gte": start_time}}
        filename = f"access_logs_today_{int(now)}.csv"
    elif range_type == "week":
        start_time = now - (86400 * 7)
        query = {"timestamp": {"$gte": start_time}}
        filename = f"access_logs_week_{int(now)}.csv"
    elif range_type == "month":
        start_time = now - (86400 * 30)
        query = {"timestamp": {"$gte": start_time}}
        filename = f"access_logs_month_{int(now)}.csv"
    else:
        filename = f"access_logs_all_{int(now)}.csv"

    await callback_query.answer("⏳ Generating CSV...", show_alert=False)
    status_msg = await callback_query.message.reply_text("⏳ Fetching logs and generating CSV...")

    # Fetch logs
    # Note: get_logs only returns limited logs, we need a new method or use raw db call
    # db.get_logs returns (logs, total_count). 
    # Let's use db.logs.find(query) directly for full export
    
    cursor = db.logs.find(query).sort("timestamp", -1)
    logs = await cursor.to_list(length=None)
    
    if not logs:
        await safe_edit(status_msg, "❌ No logs found for the selected range.")
        return

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(["Timestamp", "Date", "Time", "Admin", "Action", "Goal", "Details"])
    
    for log in logs:
        ts = log.get('timestamp', 0)
        dt = datetime.fromtimestamp(ts, IST)
        date_str = dt.strftime('%d %b %Y')
        time_str = dt.strftime('%I:%M:%S %p')
        
        details = str(log.get('details', ''))
        
        writer.writerow([
            ts,
            date_str,
            time_str,
            f"{log.get('admin_name')} ({log.get('admin_id')})",
            log.get('action'),
            log.get('target', ''),
            details
        ])
    
    output.seek(0)
    
    # Send file
    await client.send_document(
        chat_id=callback_query.from_user.id,
        document=io.BytesIO(output.getvalue().encode('utf-8')),
        file_name=filename,
        caption=f"📊 **Access Logs Export**\n"
                f"Range: {range_type.title()}\n"
                f"Entries: {len(logs)}\n"
                f"Generated at: {datetime.now(IST).strftime('%d %b %Y, %I:%M:%S %p')} IST"
    )
    
    await status_msg.delete()
    # Go back to menu
    await callback_query.message.reply_text(
        "✅ Export sent above.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back to Logs", callback_data="logs_menu", style=ButtonStyle.PRIMARY)]
        ])
    )
