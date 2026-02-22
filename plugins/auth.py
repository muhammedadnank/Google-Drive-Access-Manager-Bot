from pyrogram.enums import ButtonStyle
"""
Google Drive OAuth Authorization Plugin
Render-compatible: user pastes full redirect URL or just the code.
Admin-only: /auth, /revoke, /authstatus
"""

import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.database import db
from services.drive import start_auth_flow, finish_auth_with_code, has_pending_flow, drive_service
from utils.filters import is_admin
import logging

LOGGER = logging.getLogger(__name__)


@Client.on_message(filters.command("auth") & filters.private & is_admin)
async def cmd_auth(client, message):
    user_id = message.from_user.id

    if await db.has_gdrive_creds(user_id):
        await message.reply_text(
            "✅ **Already authorized!**\n\n"
            "Your Google Drive is connected.\n"
            "Use /revoke to disconnect.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔓 Revoke", callback_data="auth_revoke", style=ButtonStyle.DANGER)
            ]])
        )
        return

    try:
        auth_url = start_auth_flow(user_id)
    except ValueError as e:
        await message.reply_text(
            f"❌ **Configuration Error**\n\n`{e}`\n\n"
            "Set `G_DRIVE_CLIENT_ID` and `G_DRIVE_CLIENT_SECRET` in environment."
        )
        return

    await message.reply_text(
        "🔑 **Authorize Google Drive**\n\n"
        "1️⃣ Click the button below\n"
        "2️⃣ Select your Google account & allow all permissions\n"
        "3️⃣ You'll see an error page — **that's normal!**\n"
        "4️⃣ Copy the **full URL** from your browser address bar\n"
        "5️⃣ Paste that URL here\n\n"
        "📋 The URL looks like:\n"
        "`http://localhost:8080/oauth/callback?code=4/0A...`",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔗 Authorize Google Drive", url=auth_url, style=ButtonStyle.SUCCESS)
        ]])
    )
    LOGGER.info(f"Auth flow started for admin {user_id}")


@Client.on_message(filters.private & filters.text & is_admin)
async def receive_auth_code(client, message):
    user_id = message.from_user.id
    text = message.text.strip()

    if not has_pending_flow(user_id):
        return

    # Extract code from full URL or plain code
    code = None
    if "code=" in text:
        match = re.search(r"code=([^&\s]+)", text)
        if match:
            code = match.group(1)
    elif text.startswith("4/"):
        code = text

    if not code:
        return

    status_msg = await message.reply_text("🔄 **Verifying...**")
    success = await finish_auth_with_code(user_id, code, db)

    if success:
        drive_service.set_admin_user(user_id)
        await status_msg.edit(
            "✅ **Google Drive Connected Successfully!**\n\n"
            "The bot will now use your Google account.\n"
            "Use /revoke to disconnect anytime."
        )
        LOGGER.info(f"Admin {user_id} authorized Google Drive.")
    else:
        await status_msg.edit(
            "❌ **Failed — Code expired or invalid.**\n\n"
            "Please run /auth again and use a fresh URL."
        )


@Client.on_message(filters.command("revoke") & filters.private & is_admin)
async def cmd_revoke(client, message):
    user_id = message.from_user.id
    if not await db.has_gdrive_creds(user_id):
        await message.reply_text("ℹ️ No Google Drive account connected.")
        return
    await db.delete_gdrive_creds(user_id)
    if drive_service._admin_user_id == user_id:
        drive_service._admin_user_id = None
    await message.reply_text("🔓 **Disconnected.**\n\nUse /auth to reconnect.")
    LOGGER.info(f"Admin {user_id} revoked credentials.")


@Client.on_message(filters.command("authstatus") & filters.private & is_admin)
async def cmd_authstatus(client, message):
    try:
        user_id = message.from_user.id
        has_creds = await db.has_gdrive_creds(user_id)
        is_active = drive_service._admin_user_id == user_id
        status = "✅ Connected" if has_creds else "❌ Not Connected"
        active = "🟢 Active" if is_active else ("⚪ Saved, not active" if has_creds else "—")
        await message.reply_text(
            f"**Google Drive Auth Status**\n\n"
            f"Status: {status}\n"
            f"Bot usage: {active}\n\n"
            f"`/auth` — Connect\n`/revoke` — Disconnect"
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"authstatus error: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")


@Client.on_callback_query(filters.regex("^auth_revoke$" ) & is_admin)
async def cb_revoke(client, callback_query):
    user_id = callback_query.from_user.id
    await db.delete_gdrive_creds(user_id)
    if drive_service._admin_user_id == user_id:
        drive_service._admin_user_id = None
    await callback_query.message.edit_text(
        "🔓 **Disconnected.**\n\nUse /auth to reconnect."
    )
