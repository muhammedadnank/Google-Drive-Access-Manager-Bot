"""
Google Drive OAuth Authorization Plugin
Admin-only: /auth, /revoke, /authstatus
"""

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.database import db
from services.drive import start_auth_flow, finish_auth_flow, has_pending_flow, drive_service
from utils.filters import is_admin
import logging

LOGGER = logging.getLogger(__name__)


# ─── /auth command ───────────────────────────────────────────────────────────
@Client.on_message(filters.command("auth") & filters.private & is_admin)
async def cmd_auth(client, message):
    user_id = message.from_user.id

    # Already authorized?
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
        await message.reply_text(
            "🔑 **Authorize Google Drive**\n\n"
            "1️⃣ Click the button below to open Google authorization\n"
            "2️⃣ Select your Google account & allow permissions\n"
            "3️⃣ Copy the **authorization code** shown\n"
            "4️⃣ Send the code here in this chat\n\n"
            "⏳ The code starts with `4/`",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔗 Authorize Google Drive", url=auth_url)
            ]])
        )
        LOGGER.info(f"Auth flow started for admin {user_id}")
    except ValueError as e:
        await message.reply_text(
            f"❌ **Configuration Error**\n\n`{e}`\n\n"
            "Make sure `G_DRIVE_CLIENT_ID` and `G_DRIVE_CLIENT_SECRET` are set."
        )


# ─── Receive auth code ───────────────────────────────────────────────────────
@Client.on_message(filters.private & filters.text & is_admin)
async def receive_auth_code(client, message):
    user_id = message.from_user.id
    text = message.text.strip()

    # Only handle if this looks like an OAuth code and a flow is pending
    if not text.startswith("4/") or not has_pending_flow(user_id):
        return

    status_msg = await message.reply_text("🔄 **Verifying code...**")

    success = await finish_auth_flow(user_id, text, db)

    if success:
        # Set this admin as the active Drive user for bot operations
        drive_service.set_admin_user(user_id)
        await status_msg.edit(
            "✅ **Google Drive Connected Successfully!**\n\n"
            "The bot will now use your Google account for all Drive operations.\n"
            "Use /revoke to disconnect anytime."
        )
        LOGGER.info(f"Admin {user_id} successfully authorized Google Drive.")
    else:
        await status_msg.edit(
            "❌ **Invalid or Expired Code**\n\n"
            "Please run /auth again and use a fresh code."
        )


# ─── /revoke command ─────────────────────────────────────────────────────────
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
        "Your credentials have been removed.\n"
        "Use /auth to connect again."
    )
    LOGGER.info(f"Admin {user_id} revoked Google Drive credentials.")


# ─── /authstatus command ─────────────────────────────────────────────────────
@Client.on_message(filters.command("authstatus") & filters.private & is_admin)
async def cmd_authstatus(client, message):
    user_id = message.from_user.id
    has_creds = await db.has_gdrive_creds(user_id)
    is_active = drive_service._admin_user_id == user_id

    if has_creds:
        status = "✅ **Connected**"
        active = "🟢 Active (Bot is using your account)" if is_active else "⚪ Saved but not active"
    else:
        status = "❌ **Not Connected**"
        active = "—"

    await message.reply_text(
        f"**Google Drive Auth Status**\n\n"
        f"Status: {status}\n"
        f"Bot usage: {active}\n\n"
        f"Commands:\n"
        f"`/auth` — Connect Google Drive\n"
        f"`/revoke` — Disconnect"
    )


# ─── Revoke via callback button ──────────────────────────────────────────────
@Client.on_callback_query(filters.regex("^auth_revoke$") & is_admin)
async def cb_revoke(client, callback_query):
    user_id = callback_query.from_user.id
    await db.delete_gdrive_creds(user_id)
    if drive_service._admin_user_id == user_id:
        drive_service._admin_user_id = None
    await callback_query.message.edit_text(
        "🔓 **Google Drive Disconnected**\n\nUse /auth to reconnect."
    )
