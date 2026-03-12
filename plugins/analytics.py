import csv
import os
import time
import logging
import tempfile
from datetime import datetime, timezone, timedelta

from pyrogram import Client, filters
from pyrogram.enums import ButtonStyle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from services.database import db
from utils.filters import is_admin
from utils.time import safe_edit

LOGGER = logging.getLogger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# /analytics COMMAND  +  analytics_menu CALLBACK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_message(filters.command("analytics") & filters.private & is_admin)
async def analytics_command(client, message):
    """Entry point via /analytics command."""
    msg = await message.reply_text("📊 **Loading Analytics...**\n\n⏳ Please wait...")
    await _send_analytics(msg, is_message=True)


@Client.on_callback_query(filters.regex("^analytics_menu$") & is_admin)
async def show_analytics_dashboard(client, callback_query):
    """Entry point via inline button."""
    try:
        await safe_edit(callback_query, "📊 **Loading Analytics...**\n\n⏳ Please wait...")
    except Exception:
        pass
    await _send_analytics(callback_query)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Shared Analytics Renderer
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def _send_analytics(target, is_message=False):
    analytics   = await db.get_expiry_analytics()
    timeline    = analytics["timeline"]
    top_folders = analytics["top_folders"]
    top_users   = analytics["top_users"]
    total       = analytics["total_active"]

    text  = "📊 **Expiry Analytics**\n\n"

    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "⏰ EXPIRY TIMELINE\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    text += f"⚠️ < 24 hours:     **{timeline['urgent']}** grants\n"
    text += f"📅 1-7 days:       **{timeline['week']}** grants\n"
    text += f"📅 8-30 days:      **{timeline['month']}** grants\n"
    text += f"📅 30+ days:       **{timeline['later']}** grants\n"
    text += f"📊 **Total Active: {total}**\n\n"

    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "📂 TOP EXPIRING FOLDERS\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    if top_folders:
        for i, folder in enumerate(top_folders[:15], 1):
            name = folder["name"]
            if len(name) > 35:
                name = name[:32] + "..."
            text += f"{i}. {name}\n"
            text += f"   📊 {folder['count']} expiring grants\n"
    else:
        text += "No folders with expiring grants\n"

    text += "\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "👥 TOP EXPIRING USERS\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    if top_users:
        for i, (email, count) in enumerate(top_users[:15], 1):
            display = email if len(email) <= 30 else email[:27] + "..."
            text += f"{i}. `{display}`\n"
            text += f"   📊 {count} folder{'s' if count > 1 else ''}\n"
    else:
        text += "No users with expiring grants\n"

    text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 Export Full Report", callback_data="analytics_export", style=ButtonStyle.SUCCESS)],
        [InlineKeyboardButton("🔄 Refresh",            callback_data="analytics_menu",   style=ButtonStyle.PRIMARY)],
        [InlineKeyboardButton("⬅️ Back",               callback_data="expiry_menu",      style=ButtonStyle.PRIMARY)]
    ])

    if is_message:
        try:
            await target.edit_text(text, reply_markup=keyboard)
        except Exception as e:
            LOGGER.debug(f"Analytics edit: {e}")
    else:
        await safe_edit(target, text, reply_markup=keyboard)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CSV Export
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_callback_query(filters.regex("^analytics_export$") & is_admin)
async def export_analytics_report(client, callback_query):
    try:
        await callback_query.answer("📥 Generating report...", show_alert=False)
    except Exception:
        pass

    analytics = await db.get_expiry_analytics()
    grants    = await db.get_active_grants()

    temp_file = tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, newline=""
    )

    try:
        writer = csv.writer(temp_file)
        writer.writerow(["Email", "Folder Name", "Role", "Expires At", "Hours Remaining", "Status"])

        now = time.time()
        for grant in grants:
            expires_at      = grant.get("expires_at", 0)
            hours_remaining = (expires_at - now) / 3600

            if hours_remaining < 24:
                status = "URGENT"
            elif hours_remaining < 168:
                status = "This Week"
            elif hours_remaining < 720:
                status = "This Month"
            else:
                status = "Later"

            expiry_str = datetime.fromtimestamp(expires_at, IST).strftime("%d %b %Y, %I:%M %p")
            writer.writerow([
                grant.get("email", ""),
                grant.get("folder_name", ""),
                grant.get("role", "").capitalize(),
                expiry_str,
                f"{hours_remaining:.1f}",
                status
            ])

        temp_file.close()

        caption = (
            "📊 **Expiry Analytics Report**\n\n"
            f"📊 Total Active: **{analytics['total_active']}**\n"
            f"⚠️ Urgent (<24h): **{analytics['timeline']['urgent']}**\n"
            f"📅 This Week: **{analytics['timeline']['week']}**\n"
            f"📅 This Month: **{analytics['timeline']['month']}**\n"
            f"📅 Later: **{analytics['timeline']['later']}**\n\n"
            f"Generated: {datetime.now(IST).strftime('%d %b %Y, %I:%M %p')} IST"
        )

        await callback_query.message.reply_document(
            document=temp_file.name,
            caption=caption,
            file_name=f"expiry_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        await callback_query.answer("✅ Report sent!", show_alert=False)

    except Exception as e:
        LOGGER.error(f"Analytics export error: {e}")
        await callback_query.answer("❌ Export failed", show_alert=True)
    finally:
        try:
            os.unlink(temp_file.name)
        except Exception:
            pass
