# plugins/favorites.py
# Pinned Root Folders — Pin/Unpin folders, browse sub-folders, grant from favorites

import logging
import time

from pyrogram import Client, filters
from pyrogram.enums import ButtonStyle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from services.database import db
from services.drive import drive_service
from utils.filters import is_admin
from utils.time import safe_edit

LOGGER = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# /favorites — Show pinned root folders
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_message(filters.command("favorites") & filters.private & is_admin)
async def favorites_command(client, message):
    await _show_favorites(message, message.from_user.id, is_message=True)


@Client.on_callback_query(filters.regex("^favorites_menu$") & is_admin)
async def favorites_menu_cb(client, callback_query):
    await _show_favorites(callback_query, callback_query.from_user.id, is_message=False)


async def _show_favorites(target, user_id, is_message=False):
    pins = await db.get_pinned_folders(user_id)

    if not pins:
        text = (
            "📌 **Pinned Folders**\n\n"
            "No folders pinned yet.\n\n"
            "To pin a folder:\n"
            "Go to **Manage** → open any folder → tap ⭐ **Pin This Folder**"
        )
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu", style=ButtonStyle.PRIMARY)
        ]])
    else:
        text = f"📌 **Pinned Folders** ({len(pins)} pinned)\n\nSelect a root folder to browse sub-folders:"
        keyboard = []
        for pin in pins:
            keyboard.append([InlineKeyboardButton(
                f"📁 {pin['folder_name']}",
                callback_data=f"fav_browse_{pin['folder_id']}",
                style=ButtonStyle.PRIMARY
            )])
        keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu", style=ButtonStyle.PRIMARY)])
        kb = InlineKeyboardMarkup(keyboard)

    if is_message:
        await target.reply_text(text, reply_markup=kb)
    else:
        await safe_edit(target, text, reply_markup=kb)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Browse sub-folders of a pinned root folder
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_callback_query(filters.regex(r"^fav_browse_(.+)$") & is_admin)
async def fav_browse_subfolders(client, callback_query):
    folder_id = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id

    await safe_edit(callback_query, "⏳ Loading sub-folders...")

    try:
        drive_service.set_admin_user(user_id)
        subfolders = await drive_service.get_subfolders(folder_id)
    except Exception as e:
        LOGGER.error(f"fav_browse error: {e}")
        await safe_edit(callback_query, "❌ Failed to load sub-folders. Check Drive auth.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📌 Back to Favorites", callback_data="favorites_menu", style=ButtonStyle.PRIMARY)
            ]])
        )
        return

    # Get root folder name from DB
    pins = await db.get_pinned_folders(user_id)
    root_name = next((p["folder_name"] for p in pins if p["folder_id"] == folder_id), "Root Folder")

    if not subfolders:
        await safe_edit(callback_query,
            f"📁 **{root_name}**\n\nNo sub-folders found inside this folder.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔑 Grant to Root Folder",
                    callback_data=f"fav_grant_{folder_id}_{root_name[:30]}",
                    style=ButtonStyle.SUCCESS)],
                [InlineKeyboardButton("📌 Back to Favorites", callback_data="favorites_menu", style=ButtonStyle.PRIMARY)]
            ])
        )
        return

    keyboard = []
    for sf in subfolders[:20]:  # show max 20
        sf_name = sf["name"]
        sf_id = sf["id"]
        keyboard.append([InlineKeyboardButton(
            f"📂 {sf_name}",
            callback_data=f"fav_grant_{sf_id}_{sf_name[:30]}",
            style=ButtonStyle.PRIMARY
        )])

    keyboard.append([InlineKeyboardButton(
        f"🔑 Grant to Root: {root_name[:20]}",
        callback_data=f"fav_grant_{folder_id}_{root_name[:30]}",
        style=ButtonStyle.SUCCESS
    )])
    keyboard.append([InlineKeyboardButton("📌 Back to Favorites", callback_data="favorites_menu", style=ButtonStyle.PRIMARY)])

    count_text = f"(showing {len(subfolders[:20])} of {len(subfolders)})" if len(subfolders) > 20 else f"({len(subfolders)} sub-folders)"
    await safe_edit(callback_query,
        f"📁 **{root_name}**\n\nSub-folders {count_text}:\nSelect a folder to grant access:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# fav_grant — inject folder into grant flow
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_callback_query(filters.regex(r"^fav_grant_([^_]+)_(.+)$") & is_admin)
async def fav_grant_folder(client, callback_query):
    match = callback_query.matches[0]
    folder_id   = match.group(1)
    folder_name = match.group(2)
    user_id     = callback_query.from_user.id

    # Store folder in state, then ask for email (same as normal grant flow)
    from utils.states import WAITING_EMAIL_GRANT
    await db.set_state(user_id, WAITING_EMAIL_GRANT, {
        "folder_id": folder_id,
        "folder_name": folder_name,
        "from_favorites": True
    })

    await safe_edit(callback_query,
        f"📂 **{folder_name}**\n\n"
        "✉️ Enter the **email address** to grant access:",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ Cancel", callback_data="main_menu", style=ButtonStyle.DANGER)
        ]])
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Pin / Unpin a folder (called from manage.py)
# Callback: pin_folder_{folder_id}_{folder_name}
#           unpin_folder_{folder_id}
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_callback_query(filters.regex(r"^pin_folder_([^_]+)_(.+)$") & is_admin)
async def pin_folder(client, callback_query):
    match       = callback_query.matches[0]
    folder_id   = match.group(1)
    folder_name = match.group(2)
    user_id     = callback_query.from_user.id

    pins = await db.get_pinned_folders(user_id)
    if len(pins) >= 20:
        await callback_query.answer("⚠️ Max 20 pinned folders allowed. Unpin one first.", show_alert=True)
        return

    already = any(p["folder_id"] == folder_id for p in pins)
    if already:
        await callback_query.answer("Already pinned!", show_alert=True)
        return

    await db.pin_folder(user_id, folder_id, folder_name)
    await callback_query.answer(f"⭐ '{folder_name}' pinned!", show_alert=True)


@Client.on_callback_query(filters.regex(r"^unpin_folder_(.+)$") & is_admin)
async def unpin_folder(client, callback_query):
    folder_id = callback_query.matches[0].group(1)
    user_id   = callback_query.from_user.id

    await db.unpin_folder(user_id, folder_id)
    await callback_query.answer("📌 Unpinned!", show_alert=True)

    # Refresh favorites menu
    await _show_favorites(callback_query, user_id, is_message=False)
