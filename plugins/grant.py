import re
import time
import logging

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle

from services.database import db
from services.drive import drive_service
from utils.states import (
    WAITING_EMAIL_GRANT, WAITING_FOLDER_GRANT, WAITING_MULTISELECT_GRANT,
    WAITING_ROLE_GRANT, WAITING_DURATION_GRANT, WAITING_CONFIRM_GRANT,
    WAITING_MULTI_EMAIL_INPUT, WAITING_MULTI_EMAIL_FOLDER,
    WAITING_MULTI_EMAIL_ROLE, WAITING_MULTI_EMAIL_DURATION,
    WAITING_MULTI_EMAIL_CONFIRM
)
from utils.time import safe_edit, format_duration, format_timestamp, format_date
from utils.filters import check_state, is_admin
from utils.validators import validate_email
from utils.pagination import create_pagination_keyboard, create_checkbox_keyboard, sort_folders
from services.broadcast import broadcast

LOGGER = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# A-Z Group Helpers (shared by grant + manage)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_first_char(name: str) -> str:
    """Return uppercase first letter or '0-9' for numeric names."""
    c = name.strip()[0].upper() if name.strip() else "#"
    return "0-9" if c.isdigit() else (c if c.isalpha() else "#")


def build_az_group_keyboard(folders, back_cb="main_menu", context="grant"):
    """
    Build A-Z group selector keyboard.
    Shows only groups that have folders.
    context: "grant" or "manage" — sets the callback prefix.
    """
    # Count folders per group
    from collections import Counter
    counts = Counter(get_first_char(f["name"]) for f in folders)
    groups = sorted(counts.keys(), key=lambda x: ("~" if x == "0-9" else x))

    cb_prefix = f"{context}_az"
    keyboard = []

    # 3 buttons per row
    row = []
    for g in groups:
        row.append(InlineKeyboardButton(
            f"{g} ({counts[g]})",
            callback_data=f"{cb_prefix}_{g}_1",
            style=ButtonStyle.PRIMARY
        ))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    # Favorites + Search shortcuts
    keyboard.append([
        InlineKeyboardButton("📌 Favorites",      callback_data="favorites_menu",      style=ButtonStyle.SUCCESS),
        InlineKeyboardButton("🔍 Search Folders", callback_data="folder_search_start", style=ButtonStyle.PRIMARY),
    ])
    keyboard.append([
        InlineKeyboardButton("⬅️ Back", callback_data=back_cb, style=ButtonStyle.PRIMARY)
    ])
    return InlineKeyboardMarkup(keyboard)


def filter_folders_by_group(folders, group: str):
    """Filter folders belonging to a group (letter or '0-9')."""
    return [f for f in folders if get_first_char(f["name"]) == group]



# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# /grant COMMAND  +  grant_menu CALLBACK  →  Mode Selector
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_message(filters.command("grant") & filters.private & is_admin)
async def grant_command(client, message):
    """Entry point via /grant command."""
    user_id = message.from_user.id
    await db.delete_state(user_id)

    await message.reply_text(
        "➕ **Grant Access**\n\n"
        "How would you like to grant?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👤 One Email → One Folder",   callback_data="grant_mode_single", style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("📂 One Email → Multi Folders", callback_data="grant_mode_multi",  style=ButtonStyle.SUCCESS)],
            [InlineKeyboardButton("👥 Multi Emails → One Folder", callback_data="grant_mode_bulk",   style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("🏠 Back", callback_data="main_menu", style=ButtonStyle.DANGER)]
        ])
    )


@Client.on_callback_query(filters.regex("^grant_menu$") & is_admin)
async def start_grant_flow(client, callback_query):
    """Entry point via inline button from main menu."""
    user_id = callback_query.from_user.id
    await db.delete_state(user_id)

    await safe_edit(callback_query,
        "➕ **Grant Access**\n\n"
        "How would you like to grant?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👤 One Email → One Folder",   callback_data="grant_mode_single", style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("📂 One Email → Multi Folders", callback_data="grant_mode_multi",  style=ButtonStyle.SUCCESS)],
            [InlineKeyboardButton("👥 Multi Emails → One Folder", callback_data="grant_mode_bulk",   style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("🏠 Back", callback_data="main_menu", style=ButtonStyle.DANGER)]
        ])
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MODE: Single (👤) & Multi-Folder (📂) — shared email entry
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_callback_query(filters.regex(r"^grant_mode_(single|multi)$") & is_admin)
async def grant_mode_select(client, callback_query):
    mode = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    await db.set_state(user_id, WAITING_EMAIL_GRANT, {"mode": mode})

    mode_label = "👤 Single Grant" if mode == "single" else "📂 Multi-Folder Grant"

    await safe_edit(callback_query,
        f"**{mode_label}**\n\n"
        "📧 **Enter the user's email address:**\n\n"
        "Or /cancel to abort.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_flow", style=ButtonStyle.DANGER)]
        ])
    )


# ── Step 2: Receive email ──────────────────────────────────────

@Client.on_message(check_state(WAITING_EMAIL_GRANT) & filters.private & filters.text & is_admin)
async def receive_email(client, message):
    email = message.text.strip().lower()
    if not validate_email(email):
        await message.reply_text(
            "❌ **Invalid email format.**\n\n"
            "Please send a valid email (e.g. `user@gmail.com`)."
        )
        return

    user_id = message.from_user.id
    state, prev_data = await db.get_state(user_id)
    mode = prev_data.get("mode", "single") if prev_data else "single"

    msg = await message.reply_text("📂 Loading folders...")

    folders = await drive_service.get_folders_cached(db)
    if not folders:
        await safe_edit(msg, "❌ No folders found or Drive API error.")
        await db.delete_state(user_id)
        return

    folders = sort_folders(folders)

    if mode == "multi":
        # Multi-folder: checkbox keyboard
        await db.set_state(user_id, WAITING_MULTISELECT_GRANT, {
            "email": email, "folders": folders, "selected": [], "mode": mode
        })
        keyboard = create_checkbox_keyboard(folders, set(), page=1)
        await safe_edit(msg,
            f"📧 User: `{email}`\n\n"
            "📂 **Select Folders** (tap to toggle ☑️/☐):\n"
            "Press ✅ Confirm when done.",
            reply_markup=keyboard
        )
    else:
        # Single: A-Z group picker
        await db.set_state(user_id, WAITING_FOLDER_GRANT, {
            "email": email, "folders": folders, "mode": mode
        })
        keyboard = build_az_group_keyboard(folders, back_cb="grant_menu", context="grant")
        await safe_edit(msg,
            f"📧 User: `{email}`\n\n"
            "📂 **Select a Folder:**\n"
            "Choose a letter/number group or use shortcuts:",
            reply_markup=keyboard
        )


# ── Single mode: folder pagination ────────────────────────────

@Client.on_callback_query(filters.regex(r"^grant_az_([^_]+)_(\d+)$") & is_admin)
async def grant_az_folder_list(client, callback_query):
    """Show folders for a specific A-Z group with pagination."""
    group  = callback_query.matches[0].group(1)   # e.g. "A", "B", "0-9"
    page   = int(callback_query.matches[0].group(2))
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)

    if state != WAITING_FOLDER_GRANT or "folders" not in data:
        await callback_query.answer("Session expired. Please /grant again.", show_alert=True)
        return

    filtered = filter_folders_by_group(data["folders"], group)
    keyboard = create_pagination_keyboard(
        items=filtered, page=page, per_page=15,
        callback_prefix=f"grant_az_{group}",
        item_callback_func=lambda f: (f["name"], f"sel_folder_{f['id']}"),
        back_callback_data="grant_back_to_az",
        refresh_callback_data=None
    )
    await safe_edit(callback_query,
        f"📧 User: `{data.get('email', '')}`\n\n"
        f"📂 **[{group}] Folders** ({len(filtered)} total):",
        reply_markup=keyboard
    )


@Client.on_callback_query(filters.regex("^grant_back_to_az$") & is_admin)
async def grant_back_to_az(client, callback_query):
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    if state != WAITING_FOLDER_GRANT or "folders" not in data:
        await callback_query.answer("Session expired.", show_alert=True)
        return
    keyboard = build_az_group_keyboard(data["folders"], back_cb="grant_menu", context="grant")
    await safe_edit(callback_query,
        f"📧 User: `{data.get('email', '')}`\n\n"
        "📂 **Select a Folder:**\n"
        "Choose a letter/number group or use shortcuts:",
        reply_markup=keyboard
    )


# ── Single mode: refresh folders ──────────────────────────────

@Client.on_callback_query(filters.regex("^grant_refresh$") & is_admin)
async def grant_refresh(client, callback_query):
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)

    if state != WAITING_FOLDER_GRANT:
        await callback_query.answer("Session expired.", show_alert=True)
        return

    await callback_query.answer("🔄 Refreshing...")
    await db.clear_folder_cache()
    drive_service._mem_folders = []  # clear RAM cache too

    folders = await drive_service.get_folders_cached(db, force_refresh=True)
    if not folders:
        await safe_edit(callback_query, "❌ No folders found.")
        return

    folders = sort_folders(folders)
    email = data.get("email", "")
    await db.set_state(user_id, WAITING_FOLDER_GRANT, {
        "email": email, "folders": folders, "mode": data.get("mode", "single")
    })

    keyboard = create_pagination_keyboard(
        items=folders, page=1, per_page=20,
        callback_prefix="grant_folder_page",
        item_callback_func=lambda f: (f['name'], f"sel_folder_{f['id']}"),
        back_callback_data="grant_menu",
        refresh_callback_data="grant_refresh"
    )
    await safe_edit(callback_query,
        f"📧 User: `{email}`\n\n"
        "📂 **Select a Folder** (refreshed):",
        reply_markup=keyboard
    )


# ── Single mode: folder selected → role ───────────────────────

@Client.on_callback_query(filters.regex(r"^sel_folder_(.*)$") & is_admin)
async def select_folder(client, callback_query):
    folder_id = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)

    if state != WAITING_FOLDER_GRANT:
        await callback_query.answer("Session expired.", show_alert=True)
        return

    folder_name = next((f['name'] for f in data.get("folders", []) if f['id'] == folder_id), "Unknown")
    await db.set_state(user_id, WAITING_ROLE_GRANT, {
        "email": data["email"], "mode": "single",
        "folder_id": folder_id, "folder_name": folder_name
    })

    await safe_edit(callback_query,
        f"📧 User: `{data['email']}`\n"
        f"📂 Folder: **{folder_name}**\n\n"
        "🔑 **Select Access Level:**",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👀 Viewer", callback_data="role_viewer", style=ButtonStyle.PRIMARY),
             InlineKeyboardButton("✏️ Editor", callback_data="role_editor", style=ButtonStyle.DANGER)],
            [InlineKeyboardButton("⬅️ Back",   callback_data="grant_menu",  style=ButtonStyle.SUCCESS)]
        ])
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MODE: Multi-Folder (📂) — checkbox selection
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_callback_query(filters.regex(r"^tgl_(.+)$") & is_admin)
async def toggle_folder(client, callback_query):
    """Toggle a folder checkbox in multi-folder mode."""
    folder_id = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)

    if state != WAITING_MULTISELECT_GRANT:
        await callback_query.answer("Session expired.", show_alert=True)
        return

    selected = set(data.get("selected", []))

    # FIX: capture is_now_selected BEFORE mutating, for correct answer text
    if folder_id in selected:
        selected.discard(folder_id)
        is_now_selected = False
    else:
        selected.add(folder_id)
        is_now_selected = True

    data["selected"] = list(selected)
    await db.set_state(user_id, WAITING_MULTISELECT_GRANT, data)

    folders = data["folders"]
    per_page = 15
    folder_index = next((i for i, f in enumerate(folders) if f["id"] == folder_id), 0)
    current_page = (folder_index // per_page) + 1

    keyboard = create_checkbox_keyboard(folders, selected, page=current_page, per_page=per_page)
    try:
        await callback_query.edit_message_reply_markup(reply_markup=keyboard)
    except Exception as e:
        LOGGER.debug(f"Checkbox edit: {e}")

    # FIX: use is_now_selected (captured before mutation) — previously used folder_id in selected
    # which was always True after add / always False after discard → wrong label
    await callback_query.answer(
        f"{'☑️ Selected' if is_now_selected else '☐ Deselected'} ({len(selected)} total)"
    )


@Client.on_callback_query(filters.regex(r"^mf_page_(\d+)$") & is_admin)
async def multi_folder_page(client, callback_query):
    page = int(callback_query.matches[0].group(1))
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)

    if state != WAITING_MULTISELECT_GRANT:
        await callback_query.answer("Session expired.", show_alert=True)
        return

    keyboard = create_checkbox_keyboard(
        data["folders"], set(data.get("selected", [])), page=page
    )
    try:
        await callback_query.edit_message_reply_markup(reply_markup=keyboard)
    except Exception as e:
        LOGGER.debug(f"Multi-folder page edit: {e}")


@Client.on_callback_query(filters.regex("^confirm_multi_folders$") & is_admin)
async def confirm_multi_folders(client, callback_query):
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)

    if state != WAITING_MULTISELECT_GRANT:
        await callback_query.answer("Session expired.", show_alert=True)
        return

    selected_ids = set(data.get("selected", []))
    if not selected_ids:
        await callback_query.answer("⚠️ Select at least one folder!", show_alert=True)
        return

    selected_folders = [f for f in data["folders"] if f["id"] in selected_ids]
    await db.set_state(user_id, WAITING_ROLE_GRANT, {
        "email": data["email"], "mode": "multi",
        "folders_selected": selected_folders
    })

    folder_list = "\n".join(f"   • {f['name']}" for f in selected_folders)
    await safe_edit(callback_query,
        f"📧 User: `{data['email']}`\n"
        f"📂 **Folders ({len(selected_folders)}):**\n{folder_list}\n\n"
        "🔑 **Select Access Role:**\n"
        "_(applies to all selected folders)_",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👀 Viewer", callback_data="role_viewer", style=ButtonStyle.PRIMARY),
             InlineKeyboardButton("✏️ Editor", callback_data="role_editor", style=ButtonStyle.DANGER)],
            [InlineKeyboardButton("⬅️ Back",   callback_data="grant_menu",  style=ButtonStyle.SUCCESS)]
        ])
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SHARED: Role → Duration → Confirm → Execute
# (used by both Single and Multi-Folder modes)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_callback_query(filters.regex(r"^role_(viewer|editor)$") & is_admin)
async def select_role(client, callback_query):
    role = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)

    if state != WAITING_ROLE_GRANT:
        return

    data["role"] = role
    mode = data.get("mode", "single")

    if mode == "multi":
        folders = data.get("folders_selected", [])
        folder_text = (
            f"📂 **Folders ({len(folders)}):**\n"
            + "\n".join(f"   • {f['name']}" for f in folders)
        )
    else:
        folder_text = f"📂 Folder: `{data.get('folder_name', 'Unknown')}`"

    # Editors are always permanent — skip duration picker
    if role == "editor":
        data["duration_hours"] = 0
        await db.set_state(user_id, WAITING_CONFIRM_GRANT, data)
        await safe_edit(callback_query,
            "⚠️ **Confirm Access Grant**\n\n"
            f"📧 User: `{data['email']}`\n"
            f"{folder_text}\n"
            f"🔑 Role: **Editor**\n"
            f"⏳ Duration: **♾ Permanent**\n\n"
            "Is this correct?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Confirm", callback_data="grant_confirm", style=ButtonStyle.SUCCESS),
                 InlineKeyboardButton("❌ Cancel",  callback_data="cancel_flow",   style=ButtonStyle.DANGER)]
            ])
        )
        return

    # Viewers → duration picker
    await db.set_state(user_id, WAITING_DURATION_GRANT, data)
    await safe_edit(callback_query,
        f"📧 User: `{data['email']}`\n"
        f"{folder_text}\n"
        f"🔑 Role: **Viewer**\n\n"
        "⏰ **Select Access Duration:**",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("1 Hour",  callback_data="dur_1",   style=ButtonStyle.PRIMARY),
             InlineKeyboardButton("6 Hours", callback_data="dur_6",   style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("1 Day",   callback_data="dur_24",  style=ButtonStyle.PRIMARY),
             InlineKeyboardButton("7 Days",  callback_data="dur_168", style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("✅ 30 Days (Default)", callback_data="dur_720", style=ButtonStyle.SUCCESS),
             InlineKeyboardButton("♾ Permanent",          callback_data="dur_0",   style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("⬅️ Back", callback_data="grant_menu", style=ButtonStyle.DANGER)]
        ])
    )


@Client.on_callback_query(filters.regex(r"^dur_(\d+)$") & is_admin)
async def select_duration(client, callback_query):
    duration_hours = int(callback_query.matches[0].group(1))
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)

    if state != WAITING_DURATION_GRANT:
        return

    data["duration_hours"] = duration_hours
    await db.set_state(user_id, WAITING_CONFIRM_GRANT, data)

    # FIX: use format_duration() instead of duplicating logic manually
    dur_text = format_duration(duration_hours)

    mode = data.get("mode", "single")
    if mode == "multi":
        folders = data.get("folders_selected", [])
        folder_text = (
            f"📂 **Folders ({len(folders)}):**\n"
            + "\n".join(f"   • {f['name']}" for f in folders)
        )
    else:
        folder_text = f"📂 Folder: `{data.get('folder_name', 'Unknown')}`"

    expiry_line = ""
    if duration_hours > 0:
        expiry_ts = time.time() + (duration_hours * 3600)
        expiry_line = f"\n📅 Expires on: {format_timestamp(expiry_ts)}"

    await safe_edit(callback_query,
        "⚠️ **Confirm Access Grant**\n\n"
        f"📧 User: `{data['email']}`\n"
        f"{folder_text}\n"
        f"🔑 Role: **{data['role'].capitalize()}**\n"
        f"⏳ Duration: **{dur_text}**"
        f"{expiry_line}\n\n"
        "Is this correct?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Confirm", callback_data="grant_confirm", style=ButtonStyle.SUCCESS),
             InlineKeyboardButton("❌ Cancel",  callback_data="cancel_flow",   style=ButtonStyle.DANGER)]
        ])
    )


@Client.on_callback_query(filters.regex("^grant_confirm$") & is_admin)
async def execute_grant(client, callback_query):
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)

    if state != WAITING_CONFIRM_GRANT:
        return

    mode = data.get("mode", "single")
    if mode == "multi":
        await _execute_multi_grant(client, callback_query, user_id, data)
    else:
        await _execute_single_grant(client, callback_query, user_id, data)

    await db.delete_state(user_id)


# ─── Single Grant Executor ────────────────────────────────────

async def _execute_single_grant(client, callback_query, user_id, data):
    await safe_edit(callback_query, "⏳ Processing request...")
    drive_service.set_admin_user(user_id)

    email       = data["email"]
    folder_id   = data["folder_id"]
    folder_name = data["folder_name"]
    role        = data["role"]
    duration_hours = data.get("duration_hours", 0)

    # 1. DB-level duplicate check (fast, atomic)
    existing_db = await db.grants.find_one({
        "email": email, "folder_id": folder_id, "status": "active"
    })
    if existing_db:
        await safe_edit(callback_query,
            f"⚠️ **Already Active in DB**\n\n"
            f"`{email}` already has active access to `{folder_name}`.\n"
            f"No changes made.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Grant Another", callback_data="grant_menu", style=ButtonStyle.SUCCESS),
                 InlineKeyboardButton("🏠 Main Menu",    callback_data="main_menu",   style=ButtonStyle.PRIMARY)]
            ])
        )
        return

    # 2. Drive API double-check (avoids Drive-level duplicates)
    try:
        existing_perms = await drive_service.get_permissions(folder_id, db)
        existing = next(
            (p for p in existing_perms if p.get('emailAddress', '').lower() == email.lower()),
            None
        )
        if existing:
            await safe_edit(callback_query,
                f"⚠️ **User Already Has Access on Drive**\n\n"
                f"📧 `{email}`\n"
                f"📂 `{folder_name}`\n"
                f"🔑 Current Role: **{existing.get('role', 'unknown')}**\n\n"
                f"No changes made.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ Grant Another", callback_data="grant_menu", style=ButtonStyle.SUCCESS),
                     InlineKeyboardButton("🏠 Main Menu",    callback_data="main_menu",   style=ButtonStyle.PRIMARY)]
                ])
            )
            return
    except Exception as e:
        LOGGER.error(f"Permission check error for {email}: {e}")
        # Continue — transient API error; grant will fail cleanly if it's a real issue

    # 3. Grant access
    success = await drive_service.grant_access(folder_id, email, role, db)

    if success:
        if duration_hours > 0:
            await db.add_timed_grant(
                admin_id=user_id, email=email,
                folder_id=folder_id, folder_name=folder_name,
                role=role, duration_hours=duration_hours
            )
        await db.log_action(
            admin_id=user_id,
            admin_name=callback_query.from_user.first_name,
            action="grant",
            details=data
        )
        dur_text = format_duration(duration_hours)
        await broadcast(client, "grant", {
            "email": email, "folder_name": folder_name,
            "role": role, "duration": dur_text,
            "admin_name": callback_query.from_user.first_name
        })

        now = time.time()
        expiry_line = ""
        if duration_hours > 0:
            expiry_line = f"📅 Expires: {format_date(now + duration_hours * 3600)}\n"

        await safe_edit(callback_query,
            "✅ **Access Granted Successfully!**\n\n"
            f"📧 User: `{email}`\n"
            f"📂 Folder: `{folder_name}`\n"
            f"🔑 Role: {role.capitalize()}\n"
            f"⏳ Duration: {dur_text}\n"
            f"{expiry_line}"
            f"🕐 Granted at: {format_timestamp(now)}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Grant Another", callback_data="grant_menu", style=ButtonStyle.SUCCESS),
                 InlineKeyboardButton("🏠 Main Menu",    callback_data="main_menu",   style=ButtonStyle.PRIMARY)]
            ])
        )
    else:
        await safe_edit(callback_query,
            "❌ **Failed to grant access.**\n\nCheck Drive credentials or logs.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu", style=ButtonStyle.PRIMARY)]
            ])
        )


# ─── Multi-Folder Grant Executor ─────────────────────────────

async def _execute_multi_grant(client, callback_query, user_id, data):
    folders        = data.get("folders_selected", [])
    email          = data["email"]
    role           = data["role"]
    duration_hours = data.get("duration_hours", 0)
    dur_text       = format_duration(duration_hours)

    drive_service.set_admin_user(user_id)
    await safe_edit(callback_query,
        f"⏳ **Granting access to {len(folders)} folders...**"
    )

    results = []
    for folder in folders:
        try:
            existing_perms = await drive_service.get_permissions(folder["id"], db)
            existing = next(
                (p for p in existing_perms if p.get('emailAddress', '').lower() == email.lower()),
                None
            )
            if existing:
                results.append(f"⚠️ {folder['name']} — already has access")
                continue

            success = await drive_service.grant_access(folder["id"], email, role, db)
            if success:
                if duration_hours > 0:
                    await db.add_timed_grant(
                        admin_id=user_id, email=email,
                        folder_id=folder["id"], folder_name=folder["name"],
                        role=role, duration_hours=duration_hours
                    )
                await db.log_action(
                    admin_id=user_id,
                    admin_name=callback_query.from_user.first_name,
                    action="grant",
                    details={
                        "email": email, "folder_id": folder["id"],
                        "folder_name": folder["name"], "role": role,
                        "duration_hours": duration_hours, "mode": "multi_folder"
                    }
                )
                await broadcast(client, "grant", {
                    "email": email, "folder_name": folder["name"],
                    "role": role, "duration": dur_text,
                    "admin_name": callback_query.from_user.first_name
                })
                results.append(f"✅ {folder['name']}")
            else:
                results.append(f"❌ {folder['name']} — failed")
        except Exception as e:
            LOGGER.error(f"Multi-grant error for {email} → {folder['name']}: {e}")
            results.append(f"❌ {folder['name']} — error")

    granted = sum(1 for r in results if r.startswith("✅"))
    now = time.time()
    expiry_line = ""
    if duration_hours > 0:
        expiry_line = f"📅 Expires: {format_date(now + duration_hours * 3600)}\n"

    await safe_edit(callback_query,
        f"{'✅' if granted > 0 else '❌'} **Multi-Folder Grant Complete!**\n\n"
        f"📧 `{email}` | 🔑 {role.capitalize()} | ⏳ {dur_text}\n"
        f"{expiry_line}\n"
        + "\n".join(results)
        + f"\n\n**{granted}/{len(folders)}** folders granted."
        + f"\n🕐 Completed: {format_timestamp(now)}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Grant Another", callback_data="grant_menu", style=ButtonStyle.SUCCESS),
             InlineKeyboardButton("🏠 Main Menu",    callback_data="main_menu",   style=ButtonStyle.PRIMARY)]
        ])
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MODE: Batch Grant (👥) — multi-email → one folder
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_callback_query(filters.regex("^grant_mode_bulk$") & is_admin)
async def grant_mode_bulk(client, callback_query):
    user_id = callback_query.from_user.id
    await db.set_state(user_id, WAITING_MULTI_EMAIL_INPUT, {"mode": "bulk"})

    await safe_edit(callback_query,
        "👥 **Batch Grant — Multi-Email**\n\n"
        "Send multiple email addresses.\n"
        "Separate with **comma** or **new line**.\n\n"
        "**Example (comma):**\n"
        "`alice@gmail.com, bob@gmail.com`\n\n"
        "**Example (lines):**\n"
        "`alice@gmail.com`\n"
        "`bob@gmail.com`\n\n"
        "_(Max 50 emails per batch)_",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_flow", style=ButtonStyle.DANGER)]
        ])
    )


@Client.on_message(check_state(WAITING_MULTI_EMAIL_INPUT) & filters.private & filters.text & is_admin)
async def receive_multi_emails(client, message):
    """Parse comma/newline separated emails and validate."""
    user_id = message.from_user.id
    raw = message.text.strip()

    if len(raw) > 10000:
        await message.reply_text("❌ Input too large (max 10,000 characters).")
        return

    parts = re.split(r'[,\n]+', raw)
    emails = [e.strip().lower() for e in parts if e.strip() and len(e.strip()) <= 254]

    MAX_BULK_EMAILS = 50
    if len(emails) > MAX_BULK_EMAILS:
        await message.reply_text(f"❌ Too many emails! Maximum **{MAX_BULK_EMAILS}** per batch.")
        return

    valid, invalid = [], []
    for email in emails:
        if validate_email(email) and email not in valid:
            valid.append(email)
        else:
            invalid.append(email)

    if not valid:
        invalid_list = ", ".join(invalid) if invalid else "none"
        await message.reply_text(
            f"❌ **No valid emails found.**\n\nInvalid: `{invalid_list}`"
        )
        return

    msg = await message.reply_text("📂 Loading folders...")

    folders = await drive_service.get_folders_cached(db)
    if not folders:
        await safe_edit(msg, "❌ No folders found.")
        await db.delete_state(user_id)
        return

    folders = sort_folders(folders)
    await db.set_state(user_id, WAITING_MULTI_EMAIL_FOLDER, {
        "emails": valid, "folders": folders, "mode": "bulk"
    })

    invalid_text = f"\n\n⚠️ Skipped invalid: `{', '.join(invalid)}`" if invalid else ""
    keyboard = create_pagination_keyboard(
        items=folders, page=1, per_page=20,
        callback_prefix="bulk_folder_page",
        item_callback_func=lambda f: (f['name'], f"bulk_sel_{f['id']}"),
        back_callback_data="grant_menu"
    )
    await safe_edit(msg,
        f"👥 **{len(valid)} valid emails:**\n"
        + "\n".join(f"   • `{e}`" for e in valid[:10])
        + (f"\n   ... +{len(valid) - 10} more" if len(valid) > 10 else "")
        + invalid_text
        + "\n\n📂 **Select a Folder:**",
        reply_markup=keyboard
    )


@Client.on_callback_query(filters.regex(r"^bulk_folder_page_(\d+)$") & is_admin)
async def bulk_folder_pagination(client, callback_query):
    page = int(callback_query.matches[0].group(1))
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)

    if state != WAITING_MULTI_EMAIL_FOLDER:
        return

    keyboard = create_pagination_keyboard(
        items=data["folders"], page=page, per_page=20,
        callback_prefix="bulk_folder_page",
        item_callback_func=lambda f: (f['name'], f"bulk_sel_{f['id']}"),
        back_callback_data="grant_menu"
    )
    try:
        await callback_query.edit_message_reply_markup(reply_markup=keyboard)
    except Exception as e:
        LOGGER.debug(f"Bulk folder page edit: {e}")


@Client.on_callback_query(filters.regex(r"^bulk_sel_(.+)$") & is_admin)
async def bulk_select_folder(client, callback_query):
    folder_id = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)

    if state != WAITING_MULTI_EMAIL_FOLDER:
        return

    folder_name = next((f['name'] for f in data.get("folders", []) if f['id'] == folder_id), "Unknown")
    data["folder_id"]   = folder_id
    data["folder_name"] = folder_name
    await db.set_state(user_id, WAITING_MULTI_EMAIL_ROLE, data)

    await safe_edit(callback_query,
        f"👥 **{len(data['emails'])} emails** → 📂 **{folder_name}**\n\n"
        "🔑 **Select Access Role:**\n"
        "_(applies to all emails)_",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👀 Viewer", callback_data="bulk_role_viewer", style=ButtonStyle.PRIMARY),
             InlineKeyboardButton("✏️ Editor", callback_data="bulk_role_editor", style=ButtonStyle.DANGER)],
            [InlineKeyboardButton("⬅️ Back",   callback_data="grant_menu",       style=ButtonStyle.SUCCESS)]
        ])
    )


@Client.on_callback_query(filters.regex(r"^bulk_role_(viewer|editor)$") & is_admin)
async def bulk_select_role(client, callback_query):
    role = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)

    if state != WAITING_MULTI_EMAIL_ROLE:
        return

    data["role"] = role

    if role == "editor":
        # Editors are always permanent
        data["duration_hours"] = 0
        await _bulk_duplicate_check(callback_query, user_id, data)
        return

    await db.set_state(user_id, WAITING_MULTI_EMAIL_DURATION, data)
    await safe_edit(callback_query,
        f"👥 {len(data['emails'])} emails → 📂 {data['folder_name']}\n"
        f"🔑 Role: **Viewer**\n\n"
        "⏰ **Select Duration:**",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("1 Hour",  callback_data="bulk_dur_1",   style=ButtonStyle.PRIMARY),
             InlineKeyboardButton("6 Hours", callback_data="bulk_dur_6",   style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("1 Day",   callback_data="bulk_dur_24",  style=ButtonStyle.PRIMARY),
             InlineKeyboardButton("7 Days",  callback_data="bulk_dur_168", style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("✅ 30 Days (Default)", callback_data="bulk_dur_720", style=ButtonStyle.SUCCESS),
             InlineKeyboardButton("♾ Permanent",          callback_data="bulk_dur_0",   style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("⬅️ Back", callback_data="grant_menu", style=ButtonStyle.PRIMARY)]
        ])
    )


@Client.on_callback_query(filters.regex(r"^bulk_dur_(\d+)$") & is_admin)
async def bulk_select_duration(client, callback_query):
    duration = int(callback_query.matches[0].group(1))
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)

    if state != WAITING_MULTI_EMAIL_DURATION:
        return

    data["duration_hours"] = duration
    await _bulk_duplicate_check(callback_query, user_id, data)


async def _bulk_duplicate_check(callback_query, user_id, data):
    """Check Drive for existing access before showing confirmation."""
    await safe_edit(callback_query, "🔍 Checking for duplicates...")

    emails    = data["emails"]
    folder_id = data["folder_id"]

    existing_perms  = await drive_service.get_permissions(folder_id, db)
    existing_emails = {p.get('emailAddress', '').lower() for p in existing_perms if p.get('emailAddress')}

    duplicates = [e for e in emails if e in existing_emails]
    new_emails = [e for e in emails if e not in existing_emails]

    data["new_emails"] = new_emails
    data["duplicates"] = duplicates
    await db.set_state(user_id, WAITING_MULTI_EMAIL_CONFIRM, data)

    dur_text = format_duration(data.get("duration_hours", 0))

    text  = "⚠️ **Confirm Batch Grant**\n\n"
    text += f"📂 Folder: `{data['folder_name']}`\n"
    text += f"🔑 Role: **{data['role'].capitalize()}**\n"
    text += f"⏳ Duration: **{dur_text}**\n"

    if data.get("duration_hours", 0) > 0:
        expiry_ts = time.time() + (data["duration_hours"] * 3600)
        text += f"📅 Expires on: {format_date(expiry_ts)}\n"

    text += "\n"

    if duplicates:
        text += f"⚠️ **{len(duplicates)} already have access** (will skip):\n"
        text += "\n".join(f"   • ~~{e}~~" for e in duplicates[:5])
        if len(duplicates) > 5:
            text += f"\n   ... +{len(duplicates) - 5} more"
        text += "\n\n"

    if new_emails:
        text += f"✅ **{len(new_emails)} to grant:**\n"
        text += "\n".join(f"   • `{e}`" for e in new_emails[:10])
        if len(new_emails) > 10:
            text += f"\n   ... +{len(new_emails) - 10} more"
    else:
        text += "❌ **All emails already have access!**"

    buttons = []
    if new_emails:
        buttons.append([
            InlineKeyboardButton(
                f"✅ Grant to {len(new_emails)} User(s)",
                callback_data="bulk_confirm",
                style=ButtonStyle.SUCCESS
            )
        ])
    buttons.append([
        InlineKeyboardButton("❌ Cancel", callback_data="cancel_flow", style=ButtonStyle.DANGER)
    ])

    await safe_edit(callback_query, text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^bulk_confirm$") & is_admin)
async def execute_bulk_grant(client, callback_query):
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)

    if state != WAITING_MULTI_EMAIL_CONFIRM:
        return

    new_emails     = data.get("new_emails", [])
    folder_id      = data["folder_id"]
    folder_name    = data["folder_name"]
    role           = data["role"]
    duration_hours = data.get("duration_hours", 0)
    dur_text       = format_duration(duration_hours)

    await safe_edit(callback_query,
        f"⏳ **Granting access to {len(new_emails)} user(s)...**"
    )

    drive_service.set_admin_user(user_id)
    results = []

    for email in new_emails:
        try:
            success = await drive_service.grant_access(folder_id, email, role, db)
            if success:
                if duration_hours > 0:
                    await db.add_timed_grant(
                        admin_id=user_id, email=email,
                        folder_id=folder_id, folder_name=folder_name,
                        role=role, duration_hours=duration_hours
                    )
                await db.log_action(
                    admin_id=user_id,
                    admin_name=callback_query.from_user.first_name,
                    action="grant",
                    details={
                        "email": email, "folder_id": folder_id,
                        "folder_name": folder_name, "role": role,
                        "duration_hours": duration_hours, "mode": "multi_email"
                    }
                )
                await broadcast(client, "grant", {
                    "email": email, "folder_name": folder_name,
                    "role": role, "duration": dur_text,
                    "admin_name": callback_query.from_user.first_name
                })
                results.append(f"✅ {email}")
            else:
                results.append(f"❌ {email} — failed")
        except Exception as e:
            LOGGER.error(f"Batch grant error for {email}: {e}")
            results.append(f"❌ {email} — error")

    granted  = sum(1 for r in results if r.startswith("✅"))
    skipped  = len(data.get("duplicates", []))
    now      = time.time()
    expiry_line = ""
    if duration_hours > 0:
        expiry_line = f"📅 Expires: {format_date(now + duration_hours * 3600)}\n"

    await safe_edit(callback_query,
        f"{'✅' if granted > 0 else '❌'} **Batch Grant Complete!**\n\n"
        f"📂 `{folder_name}` | 🔑 {role.capitalize()} | ⏳ {dur_text}\n"
        f"{expiry_line}\n"
        + "\n".join(results)
        + f"\n\n**{granted}/{len(new_emails)}** granted"
        + (f" | {skipped} skipped (duplicates)" if skipped else "")
        + f"\n🕐 Completed: {format_timestamp(now)}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Grant Another", callback_data="grant_menu", style=ButtonStyle.SUCCESS),
             InlineKeyboardButton("🏠 Main Menu",    callback_data="main_menu",   style=ButtonStyle.PRIMARY)]
        ])
    )
    await db.delete_state(user_id)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Cancel Flow
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_callback_query(filters.regex("^cancel_flow$") & is_admin)
async def cancel_flow(client, callback_query):
    await db.delete_state(callback_query.from_user.id)
    await callback_query.answer("Cancelled.")
    await safe_edit(callback_query,
        "🚫 **Operation Cancelled.**\n\nReturning to main menu.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu", style=ButtonStyle.PRIMARY)]
        ])
    )
