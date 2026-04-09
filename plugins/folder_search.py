# plugins/folder_search.py
# Folder Search/Filter — type keyword → filtered folder list → grant

import logging

from pyrogram import Client, filters
from pyrogram.enums import ButtonStyle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from services.database import db
from services.drive import drive_service
from utils.filters import is_admin, check_state
from utils.time import safe_edit
from utils.states import WAITING_FOLDER_SEARCH

LOGGER = logging.getLogger(__name__)

MAX_RESULTS = 25  # max folders to show per search


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Entry point — from grant menu
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_callback_query(filters.regex("^folder_search_start$") & is_admin)
async def folder_search_start(client, callback_query):
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)

    # Preserve existing state data (email etc.) but switch to folder search
    await db.set_state(user_id, WAITING_FOLDER_SEARCH, data or {})

    await safe_edit(callback_query,
        "🔍 **Folder Search**\n\n"
        "Type part of the folder name to filter:\n"
        "_(e.g: `AD 2500`, `Hero`, `Project X`)_",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ Cancel", callback_data="main_menu", style=ButtonStyle.DANGER)
        ]])
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Handle typed search query
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_message(filters.private & is_admin & check_state(WAITING_FOLDER_SEARCH))
async def handle_folder_search_input(client, message):
    user_id = message.from_user.id
    query   = (message.text or "").strip()

    if not query or len(query) < 2:
        await message.reply_text("⚠️ Enter at least 2 characters to search.")
        return

    state, data = await db.get_state(user_id)

    searching_msg = await message.reply_text(f"🔍 Searching for **{query}**...")

    try:
        drive_service.set_admin_user(user_id)
        folders = await drive_service.search_folders_by_name(query, max_results=MAX_RESULTS)
    except Exception as e:
        LOGGER.error(f"folder_search error: {e}")
        await searching_msg.edit_text(
            "❌ Search failed. Check Drive authorization.\n"
            "Use /auth to reconnect.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu", style=ButtonStyle.PRIMARY)
            ]])
        )
        return

    if not folders:
        await searching_msg.edit_text(
            f"❌ No folders found matching **{query}**\n\nTry a different keyword.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔍 Search Again", callback_data="folder_search_start", style=ButtonStyle.PRIMARY)],
                [InlineKeyboardButton("🏠 Main Menu",    callback_data="main_menu",           style=ButtonStyle.PRIMARY)]
            ])
        )
        return

    keyboard = []
    for folder in folders:
        f_id   = folder["id"]
        f_name = folder["name"]
        keyboard.append([InlineKeyboardButton(
            f"📂 {f_name}",
            callback_data=f"fsr_pick_{f_id}_{f_name[:30]}",
            style=ButtonStyle.PRIMARY
        )])

    count_note = f"Showing {len(folders)} result(s)" + (" (top matches)" if len(folders) == MAX_RESULTS else "")
    keyboard.append([InlineKeyboardButton("🔍 Search Again", callback_data="folder_search_start", style=ButtonStyle.PRIMARY)])
    keyboard.append([InlineKeyboardButton("🏠 Main Menu",    callback_data="main_menu",           style=ButtonStyle.PRIMARY)])

    await searching_msg.edit_text(
        f"🔍 Results for **{query}**\n_{count_note}_\n\nSelect a folder:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# User picks a folder from search results
# → continues grant flow with selected folder
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_callback_query(filters.regex(r"^fsr_pick_([^_]+)_(.+)$") & is_admin)
async def folder_search_pick(client, callback_query):
    match       = callback_query.matches[0]
    folder_id   = match.group(1)
    folder_name = match.group(2)
    user_id     = callback_query.from_user.id

    state, data = await db.get_state(user_id)
    data = data or {}

    # Determine where to continue based on existing flow
    # If email already set → go to role selection
    # If no email → ask for email
    if data.get("email"):
        # came from multi-folder or grant flow that already has email
        from utils.states import WAITING_ROLE_GRANT
        data["folder_id"]   = folder_id
        data["folder_name"] = folder_name
        await db.set_state(user_id, WAITING_ROLE_GRANT, data)

        from plugins.grant import show_role_selection
        await show_role_selection(callback_query, folder_name)
    else:
        # No email yet — set folder, ask email
        from utils.states import WAITING_EMAIL_GRANT
        data["folder_id"]   = folder_id
        data["folder_name"] = folder_name
        await db.set_state(user_id, WAITING_EMAIL_GRANT, data)

        await safe_edit(callback_query,
            f"📂 **{folder_name}**\n\n"
            "✉️ Enter the **email address** to grant access:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ Cancel", callback_data="main_menu", style=ButtonStyle.DANGER)
            ]])
        )
