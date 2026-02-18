"""
Google Drive OAuth Authorization Plugin
Uses localhost redirect (OOB deprecated by Google).
Admin-only: /auth, /revoke, /authstatus
"""

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.database import db
from services.drive import start_auth_flow, wait_for_auth_code, has_pending_flow, drive_service
from utils.filters import is_admin
import asyncio
import logging

LOGGER = logging.getLogger(__name__)


@Client.on_message(filters.command("auth") & filters.private & is_admin)
async def cmd_auth(client, message):
    user_id = message.from_user.id

    if await db.has_gdrive_creds(user_id):
        await message.reply_text(
            "✅ **Already authorized!**\n\n"
            "Your Google Drive is connected.\n"
            "Use /revoke to disconnect and re-authorize.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔓 Revoke", callback_data="auth_revoke")
            ]])
        )
        return

    try:
        auth_url = start_auth_flow(user_id)
    except ValueError as e:
        await message.reply_text(
            f"❌ **Configuration Error**\n\n`{e}`\n\n"
            "Make sure `G_DRIVE_CLIENT_ID` and `G_DRIVE_CLIENT_SECRET` are set."
        )
        return

    status_msg = await message.reply_text(
        "🔑 **Authorize Google Drive**\n\n"
        "1️⃣ Click the button below\n"
        "2️⃣ Select your Google account & allow permissions\n"
        "3️⃣ You'll be redirected — authorization completes automatically\n\n"
        "⏳ Waiting for authorization... (5 min timeout)",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔗 Authorize Google Drive", url=auth_url)
        ]])
    )

    # Wait for code in background
    asyncio.create_task(_wait_and_confirm(user_id, status_msg))
    LOGGER.info(f"Auth flow started for admin {user_id}")


async def _wait_and_confirm(user_id: int, status_msg):
    """Background task: wait for OAuth code, then confirm."""
    success = await wait_for_auth_code(user_id, db, timeout=300)

    if success:
        drive_service.set_admin_user(user_id)
        try:
            await status_msg.edit(
                "✅ **Google Drive Connected Successfully!**\n\n"
                "The bot will now use your Google account for all Drive operations.\n"
                "Use /revoke to disconnect anytime."
            )
        except Exception:
            pass
        LOGGER.info(f"Admin {user_id} authorized Google Drive.")
    else:
        try:
            await status_msg.edit(
                "⏰ **Authorization Timed Out**\n\n"
                "Please run /auth again."
            )
        except Exception:
            pass


@Client.on_message(filters.command("revoke") & filters.private & is_admin)
async def cmd_revoke(client, message):
    user_id = message.from_user.id

    if not await db.has_gdrive_creds(user_id):
        await message.reply_text("ℹ️ No Google Drive account connected.")
        return

    await db.delete_gdrive_creds(user_id)
    if drive_service._admin_user_id == user_id:
        drive_service._admin_user_id = None

    await message.reply_text(
        "🔓 **Google Drive Disconnected**\n\n"
        "Use /auth to connect again."
    )
    LOGGER.info(f"Admin {user_id} revoked Google Drive credentials.")


@Client.on_message(filters.command("authstatus") & filters.private & is_admin)
async def cmd_authstatus(client, message):
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


@Client.on_callback_query(filters.regex("^auth_revoke$") & is_admin)
async def cb_revoke(client, callback_query):
    user_id = callback_query.from_user.id
    await db.delete_gdrive_creds(user_id)
    if drive_service._admin_user_id == user_id:
        drive_service._admin_user_id = None
    await callback_query.message.edit_text(
        "🔓 **Google Drive Disconnected**\n\nUse /auth to reconnect."
    )
