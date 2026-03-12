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
from utils.time import safe_edit
from utils.filters import check_state
from utils.validators import validate_email
from utils.pagination import create_pagination_keyboard, create_checkbox_keyboard, sort_folders
import logging
from utils.time import format_duration, format_timestamp, format_date
from services.broadcast import broadcast
from utils.filters import is_admin

LOGGER = logging.getLogger(__name__)





# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Step 1: Mode Selector
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_callback_query(filters.regex("^grant_menu$") & is_admin)
async def start_grant_flow(client, callback_query):
    user_id = callback_query.from_user.id
    await db.delete_state(user_id)
    
    await safe_edit(callback_query, 
        "➕ **Grant Access**\n\n"
        "How would you like to grant?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👤 One Email → One Folder", callback_data="grant_mode_single", style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("📂 One Email → Multi Folders", callback_data="grant_mode_multi", style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("👥 Multi Emails → One Folder", callback_data="grant_mode_bulk", style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("🏠 Back", callback_data="main_menu", style=ButtonStyle.PRIMARY)]
        ])
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Multi-Email Mode: Enter Email List
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_callback_query(filters.regex("^grant_mode_bulk$") & is_admin)
async def grant_mode_bulk(client, callback_query):
    user_id = callback_query.from_user.id
    await db.set_state(user_id, WAITING_MULTI_EMAIL_INPUT, {"mode": "bulk"})
    
    await safe_edit(callback_query, 
        "👥 **Multi-Email Grant**\n\n"
        "Send multiple email addresses.\n"
        "Separate with **comma** or **new line**.\n\n"
        "Example:\n"
        "`alice@gmail.com, bob@gmail.com`\n\n"
        "Or:\n"
        "`alice@gmail.com`\n"
        "`bob@gmail.com`",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_flow", style=ButtonStyle.DANGER)]
        ])
    )


@Client.on_message(check_state(WAITING_MULTI_EMAIL_INPUT) & filters.private & filters.text & is_admin)
async def receive_multi_emails(client, message):
    """Parse comma/newline separated emails."""
    user_id = message.from_user.id
    raw = message.text.strip()
    
    # Security: Limit input size to prevent DoS
    if len(raw) > 10000:
        await message.reply_text("❌ Input too large (max 10,000 chars).")
        return

    # Split by comma or newline
    import re
    parts = re.split(r'[,\n]+', raw)
    # Security: Limit email length
    emails = [e.strip().lower() for e in parts if e.strip() and len(e.strip()) <= 254]
    
    # Security: Limit max emails per batch
    MAX_BULK_EMAILS = 50
    if len(emails) > MAX_BULK_EMAILS:
        await message.reply_text(f"❌ Too many emails! Maximum {MAX_BULK_EMAILS} allowed per batch.")
        return

    # Validate each
    valid = []
    invalid = []
    for email in emails:
        if validate_email(email):
            if email not in valid:  # deduplicate
                valid.append(email)
        else:
            invalid.append(email)
    
    if not valid:
        await message.reply_text(
            "❌ No valid emails found. Please try again.\n\n"
            f"Invalid: {', '.join(invalid) if invalid else 'none'}"
        )
        return
    
    msg = await message.reply_text("📂 Loading folders...")
    
    folders = await drive_service.get_folders_cached(db)
    if not folders:
        await safe_edit(msg, "❌ No folders found.")
        await db.delete_state(user_id)
        return
    
    folders = sort_folders(folders)
    
    invalid_text = f"\n\n⚠️ Skipped invalid: {', '.join(invalid)}" if invalid else ""
    
    await db.set_state(user_id, WAITING_MULTI_EMAIL_FOLDER, {
        "emails": valid, "folders": folders, "mode": "bulk"
    })
    
    keyboard = create_pagination_keyboard(
        items=folders, page=1, per_page=20,
        callback_prefix="bulk_folder_page",
        item_callback_func=lambda f: (f['name'], f"bulk_sel_{f['id']}"),
        back_callback_data="grant_menu"
    )
    
    await safe_edit(msg, 
        f"👥 **{len(valid)} emails** ready:\n"
        + "\n".join(f"   • `{e}`" for e in valid[:10])
        + (f"\n   ... +{len(valid)-10} more" if len(valid) > 10 else "")
        + invalid_text
        + "\n\n📂 **Select a Folder**:",
        reply_markup=keyboard
    )


@Client.on_callback_query(filters.regex(r"^bulk_folder_page_(\d+)$") & is_admin)
async def bulk_folder_pagination(client, callback_query):
    page = int(callback_query.matches[0].group(1))
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    if state != WAITING_MULTI_EMAIL_FOLDER: return
    
    keyboard = create_pagination_keyboard(
        items=data["folders"], page=page, per_page=20,
        callback_prefix="bulk_folder_page",
        item_callback_func=lambda f: (f['name'], f"bulk_sel_{f['id']}"),
        back_callback_data="grant_menu"
    )
    try:
        await callback_query.edit_message_reply_markup(reply_markup=keyboard)
    except Exception as e:
        LOGGER.debug(f"Error editing reply markup: {e}")


@Client.on_callback_query(filters.regex(r"^bulk_sel_(.+)$") & is_admin)
async def bulk_select_folder(client, callback_query):
    folder_id = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    if state != WAITING_MULTI_EMAIL_FOLDER: return
    
    folder_name = next((f['name'] for f in data.get("folders", []) if f['id'] == folder_id), "Unknown")
    
    data["folder_id"] = folder_id
    data["folder_name"] = folder_name
    await db.set_state(user_id, WAITING_MULTI_EMAIL_ROLE, data)
    
    await safe_edit(callback_query, 
        f"👥 **{len(data['emails'])} emails** → 📂 **{folder_name}**\n\n"
        "🔑 **Select Access Role**:\n"
        "_(applies to all emails)_",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👀 Viewer", callback_data="bulk_role_viewer", style=ButtonStyle.PRIMARY),
             InlineKeyboardButton("✏️ Editor", callback_data="bulk_role_editor", style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("⬅️ Back", callback_data="grant_menu", style=ButtonStyle.PRIMARY)]
        ])
    )


@Client.on_callback_query(filters.regex(r"^bulk_role_(viewer|editor)$") & is_admin)
async def bulk_select_role(client, callback_query):
    role = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    if state != WAITING_MULTI_EMAIL_ROLE: return
    
    data["role"] = role
    
    if role == "editor":
        # Editors permanent — skip duration, go to duplicate check
        data["duration_hours"] = 0
        await _bulk_duplicate_check(callback_query, user_id, data)
        return
    
    await db.set_state(user_id, WAITING_MULTI_EMAIL_DURATION, data)
    
    await safe_edit(callback_query, 
        f"👥 {len(data['emails'])} emails → 📂 {data['folder_name']}\n"
        f"🔑 Role: **Viewer**\n\n"
        "⏰ **Select Duration**:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("1 Hour", callback_data="bulk_dur_1", style=ButtonStyle.PRIMARY),
             InlineKeyboardButton("6 Hours", callback_data="bulk_dur_6", style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("1 Day", callback_data="bulk_dur_24", style=ButtonStyle.PRIMARY),
             InlineKeyboardButton("7 Days", callback_data="bulk_dur_168", style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("✅ 30 Days (Default)", callback_data="bulk_dur_720", style=ButtonStyle.SUCCESS),
             InlineKeyboardButton("♾ Permanent", callback_data="bulk_dur_0", style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("⬅️ Back", callback_data="grant_menu", style=ButtonStyle.PRIMARY)]
        ])
    )


@Client.on_callback_query(filters.regex(r"^bulk_dur_(\d+)$") & is_admin)
async def bulk_select_duration(client, callback_query):
    duration = int(callback_query.matches[0].group(1))
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    if state != WAITING_MULTI_EMAIL_DURATION: return
    
    data["duration_hours"] = duration
    await _bulk_duplicate_check(callback_query, user_id, data)


async def _bulk_duplicate_check(callback_query, user_id, data):
    """Check for duplicates before confirmation."""
    await safe_edit(callback_query, "🔍 Checking for duplicates...")
    
    emails = data["emails"]
    folder_id = data["folder_id"]
    
    existing_perms = await drive_service.get_permissions(folder_id, db)
    existing_emails = {p.get('emailAddress', '').lower() for p in existing_perms if p.get('emailAddress')}
    
    duplicates = [e for e in emails if e in existing_emails]
    new_emails = [e for e in emails if e not in existing_emails]
    
    data["new_emails"] = new_emails
    data["duplicates"] = duplicates
    await db.set_state(user_id, WAITING_MULTI_EMAIL_CONFIRM, data)
    
    dur_text = format_duration(data.get("duration_hours", 0))
    
    text = "⚠️ **Confirm Multi-Email Grant**\n\n"
    text += f"📂 Folder: `{data['folder_name']}`\n"
    text += f"🔑 Role: **{data['role'].capitalize()}**\n"
    text += f"⏳ Duration: **{dur_text}**\n"
    
    if data.get("duration_hours", 0) > 0:
        import time
        expiry_ts = time.time() + (data["duration_hours"] * 3600)
        expiry_date = format_date(expiry_ts)
        text += f"📅 Expires on: {expiry_date}\n"
    
    text += "\n"
    
    if duplicates:
        text += f"⚠️ **{len(duplicates)} already have access** (will skip):\n"
        text += "\n".join(f"   • ~~{e}~~" for e in duplicates[:5])
        if len(duplicates) > 5:
            text += f"\n   ... +{len(duplicates)-5} more"
        text += "\n\n"
    
    if new_emails:
        text += f"✅ **{len(new_emails)} to grant**:\n"
        text += "\n".join(f"   • `{e}`" for e in new_emails[:10])
        if len(new_emails) > 10:
            text += f"\n   ... +{len(new_emails)-10} more"
    else:
        text += "❌ All emails already have access!"
    
    buttons = []
    if new_emails:
        buttons.append([InlineKeyboardButton(f"✅ Grant {len(new_emails)} Users", callback_data="bulk_confirm", style=ButtonStyle.SUCCESS)])
    buttons.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_flow", style=ButtonStyle.DANGER)])
    
    await safe_edit(callback_query, text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^bulk_confirm$") & is_admin)
async def execute_bulk_grant(client, callback_query):
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    if state != WAITING_MULTI_EMAIL_CONFIRM: return
    
    new_emails = data.get("new_emails", [])
    folder_id = data["folder_id"]
    folder_name = data["folder_name"]
    role = data["role"]
    duration_hours = data.get("duration_hours", 0)
    
    await safe_edit(callback_query, 
        f"⏳ **Granting access to {len(new_emails)} users...**"
    )
    
    # BUG FIX: dur_text defined BEFORE use in broadcast call
    dur_text = format_duration(duration_hours)
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
                    details={"email": email, "folder_id": folder_id,
                             "folder_name": folder_name, "role": role,
                             "duration_hours": duration_hours, "mode": "multi_email"}
                )
                await broadcast(client, "grant", {
                    "email": email,
                    "folder_name": folder_name,
                    "role": role,
                    "duration": dur_text,
                    "admin_name": callback_query.from_user.first_name
                })
                results.append(f"✅ {email}")
            else:
                results.append(f"❌ {email} — failed")
        except Exception as e:
            LOGGER.error(f"Bulk grant error for {email}: {e}")
            results.append(f"❌ {email} — error ({str(e)})")
    
    granted = sum(1 for r in results if r.startswith("✅"))
    skipped = len(data.get("duplicates", []))
    
    import time
    completed_at = format_timestamp(time.time())
    expiry_str = ""
    if duration_hours > 0:
        expiry_ts = time.time() + (duration_hours * 3600)
        expiry_str = f"📅 Expires: {format_date(expiry_ts)}\n"

    await safe_edit(callback_query, 
        f"{'✅' if granted > 0 else '❌'} **Multi-Email Grant Complete!**\n\n"
        f"📂 `{folder_name}` | 🔑 {role.capitalize()} | ⏳ {dur_text}\n"
        f"{expiry_str}\n"
        + "\n".join(results)
        + f"\n\n**{granted}/{len(new_emails)}** granted"
        + (f" | {skipped} skipped (duplicates)" if skipped else "")
        + f"\nCompleted at: {completed_at}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Grant Another", callback_data="grant_menu", style=ButtonStyle.SUCCESS),
             InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu", style=ButtonStyle.PRIMARY)]
        ])
    )
    
    await db.delete_state(user_id)


@Client.on_callback_query(filters.regex(r"^grant_mode_(single|multi)$") & is_admin)
async def grant_mode_select(client, callback_query):
    mode = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    
    await db.set_state(user_id, WAITING_EMAIL_GRANT, {"mode": mode})
    
    await safe_edit(callback_query, 
        "📧 **Enter User Email**\n\n"
        "Send the email address to grant access to.\n"
        "Or /cancel to abort.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_flow", style=ButtonStyle.DANGER)]
        ])
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Step 2: Receive Email & Show Folders
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(check_state(WAITING_EMAIL_GRANT) & filters.private & filters.text & is_admin)
async def receive_email(client, message):
    email = message.text.strip()
    if not validate_email(email):
        await message.reply_text("❌ Invalid email format. Please try again.")
        return

    user_id = message.from_user.id
    state, prev_data = await db.get_state(user_id)
    mode = prev_data.get("mode", "single") if prev_data else "single"
    
    msg = await message.reply_text("📂 Loading folders...")
    
    folders = await drive_service.get_folders_cached(db)
    if not folders:
        await safe_edit(msg, "❌ No folders found or error connecting to Drive API.")
        await db.delete_state(user_id)
        return

    folders = sort_folders(folders)
    
    if mode == "multi":
        # Multi-folder: show checkbox keyboard
        await db.set_state(user_id, WAITING_MULTISELECT_GRANT, {
            "email": email, "folders": folders, "selected": [], "mode": mode
        })
        
        keyboard = create_checkbox_keyboard(folders, set(), page=1)
        
        await safe_edit(msg, 
            f"📧 User: `{email}`\n\n"
            "📂 **Select Folders** (tap to toggle):",
            reply_markup=keyboard
        )
    else:
        # Single folder: original flow
        await db.set_state(user_id, WAITING_FOLDER_GRANT, {"email": email, "folders": folders, "mode": mode})
        
        keyboard = create_pagination_keyboard(
            items=folders,
            page=1,
            per_page=20,
            callback_prefix="grant_folder_page",
            item_callback_func=lambda f: (f['name'], f"sel_folder_{f['id']}"),
            back_callback_data="main_menu",
            refresh_callback_data="grant_refresh"
        )
        
        await safe_edit(msg, 
            f"📧 User: `{email}`\n\n"
            "📂 **Select a Folder**:",
            reply_markup=keyboard
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Single Mode: Folder Pagination
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_callback_query(filters.regex(r"^grant_folder_page_(\d+)$") & is_admin)
async def grant_folder_pagination(client, callback_query):
    page = int(callback_query.matches[0].group(1))
    user_id = callback_query.from_user.id
    
    state, data = await db.get_state(user_id)
    if state != WAITING_FOLDER_GRANT or "folders" not in data:
        await callback_query.answer("Session expired. Please restart.", show_alert=True)
        return

    folders = data["folders"]
    keyboard = create_pagination_keyboard(
        items=folders,
        page=page,
        per_page=20,
        callback_prefix="grant_folder_page",
        item_callback_func=lambda f: (f['name'], f"sel_folder_{f['id']}"),
        refresh_callback_data="grant_refresh"
    )
    
    try:
        await callback_query.edit_message_reply_markup(reply_markup=keyboard)
    except Exception as e:
        LOGGER.debug(f"Message not modified: {e}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Single Mode: Refresh Folders
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_callback_query(filters.regex("^grant_refresh$") & is_admin)
async def grant_refresh(client, callback_query):
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    
    if state != WAITING_FOLDER_GRANT:
        await callback_query.answer("Session expired.", show_alert=True)
        return
    
    await callback_query.answer("🔄 Refreshing folders...")
    await db.clear_folder_cache()
    
    folders = await drive_service.get_folders_cached(db, force_refresh=True)
    if not folders:
        await safe_edit(callback_query, "❌ No folders found.")
        return
    
    folders = sort_folders(folders)
    email = data.get("email", "")
    await db.set_state(user_id, WAITING_FOLDER_GRANT, {"email": email, "folders": folders, "mode": data.get("mode", "single")})
    
    keyboard = create_pagination_keyboard(
        items=folders,
        page=1,
        per_page=20,
        callback_prefix="grant_folder_page",
        item_callback_func=lambda f: (f['name'], f"sel_folder_{f['id']}"),
        refresh_callback_data="grant_refresh"
    )
    
    await safe_edit(callback_query, 
        f"📧 User: `{email}`\n\n"
        "📂 **Select a Folder** (refreshed):",
        reply_markup=keyboard
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Multi Mode: Toggle Folder Checkbox
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_callback_query(filters.regex(r"^tgl_(.+)$") & is_admin)
async def toggle_folder(client, callback_query):
    folder_id = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    
    state, data = await db.get_state(user_id)
    if state != WAITING_MULTISELECT_GRANT:
        await callback_query.answer("Session expired.", show_alert=True)
        return
    
    selected = set(data.get("selected", []))
    
    # Toggle
    if folder_id in selected:
        selected.discard(folder_id)
    else:
        selected.add(folder_id)
    
    data["selected"] = list(selected)
    await db.set_state(user_id, WAITING_MULTISELECT_GRANT, data)
    
    # Re-render (determine current page from folder position)
    folders = data["folders"]
    per_page = 15
    folder_index = next((i for i, f in enumerate(folders) if f["id"] == folder_id), 0)
    current_page = (folder_index // per_page) + 1
    
    keyboard = create_checkbox_keyboard(folders, selected, page=current_page, per_page=per_page)
    
    try:
        await callback_query.edit_message_reply_markup(reply_markup=keyboard)
    except Exception as e:
        LOGGER.debug(f"Error editing reply markup: {e}")
    
    await callback_query.answer(f"{'☑️ Selected' if folder_id in selected else '☐ Deselected'} ({len(selected)} total)")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Multi Mode: Pagination
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_callback_query(filters.regex(r"^mf_page_(\d+)$") & is_admin)
async def multi_folder_page(client, callback_query):
    page = int(callback_query.matches[0].group(1))
    user_id = callback_query.from_user.id
    
    state, data = await db.get_state(user_id)
    if state != WAITING_MULTISELECT_GRANT:
        await callback_query.answer("Session expired.", show_alert=True)
        return
    
    folders = data["folders"]
    selected = set(data.get("selected", []))
    
    keyboard = create_checkbox_keyboard(folders, selected, page=page)
    
    try:
        await callback_query.edit_message_reply_markup(reply_markup=keyboard)
    except Exception as e:
        LOGGER.debug(f"Error editing reply markup: {e}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Multi Mode: Confirm Folder Selection → Role
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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
    
    folders = data["folders"]
    selected_folders = [f for f in folders if f["id"] in selected_ids]
    
    # Move to role selection
    new_data = {
        "email": data["email"],
        "mode": "multi",
        "folders_selected": selected_folders
    }
    await db.set_state(user_id, WAITING_ROLE_GRANT, new_data)
    
    folder_list = "\n".join(f"   • {f['name']}" for f in selected_folders)
    
    await safe_edit(callback_query, 
        f"📧 User: `{data['email']}`\n"
        f"📂 **Folders ({len(selected_folders)}):**\n{folder_list}\n\n"
        "🔑 **Select Access Role**:\n"
        "_(applies to all selected folders)_",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👀 Viewer", callback_data="role_viewer", style=ButtonStyle.PRIMARY),
             InlineKeyboardButton("✏️ Editor", callback_data="role_editor", style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("⬅️ Back", callback_data="grant_menu", style=ButtonStyle.PRIMARY)]
        ])
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Single Mode: Select Folder → Role
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_callback_query(filters.regex(r"^sel_folder_(.*)$") & is_admin)
async def select_folder(client, callback_query):
    folder_id = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    
    state, data = await db.get_state(user_id)
    if state != WAITING_FOLDER_GRANT:
        await callback_query.answer("Invalid state.", show_alert=True)
        return

    folder_name = next((f['name'] for f in data.get("folders", []) if f['id'] == folder_id), "Unknown")
    
    new_data = {
        "email": data["email"],
        "mode": "single",
        "folder_id": folder_id,
        "folder_name": folder_name
    }
    await db.set_state(user_id, WAITING_ROLE_GRANT, new_data)
    
    await safe_edit(callback_query, 
        f"📧 User: `{data['email']}`\n"
        f"📂 Folder: **{folder_name}**\n\n"
        "🔑 **Select Access Level**:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👀 Viewer", callback_data="role_viewer", style=ButtonStyle.PRIMARY),
             InlineKeyboardButton("✏️ Editor", callback_data="role_editor", style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("⬅️ Back", callback_data="grant_menu", style=ButtonStyle.PRIMARY)]
        ])
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Step 4: Select Duration (Viewers only)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_callback_query(filters.regex(r"^role_(viewer|editor)$") & is_admin)
async def select_role(client, callback_query):
    role = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    
    state, data = await db.get_state(user_id)
    if state != WAITING_ROLE_GRANT: return

    data["role"] = role
    mode = data.get("mode", "single")
    
    # Build folder display text
    if mode == "multi":
        folders = data.get("folders_selected", [])
        folder_text = f"📂 **Folders ({len(folders)}):**\n" + "\n".join(f"   • {f['name']}" for f in folders)
    else:
        folder_text = f"📂 Folder: `{data.get('folder_name', 'Unknown')}`"
    
    # Editors are always permanent — skip duration
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
                 InlineKeyboardButton("❌ Cancel", callback_data="cancel_flow", style=ButtonStyle.DANGER)]
            ])
        )
        return
    
    # Viewers get duration selection
    await db.set_state(user_id, WAITING_DURATION_GRANT, data)
    
    await safe_edit(callback_query, 
        f"📧 User: `{data['email']}`\n"
        f"{folder_text}\n"
        f"🔑 Role: **Viewer**\n\n"
        "⏰ **Select Access Duration**:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("1 Hour", callback_data="dur_1", style=ButtonStyle.PRIMARY),
             InlineKeyboardButton("6 Hours", callback_data="dur_6", style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("1 Day", callback_data="dur_24", style=ButtonStyle.PRIMARY),
             InlineKeyboardButton("7 Days", callback_data="dur_168", style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("✅ 30 Days (Default)", callback_data="dur_720", style=ButtonStyle.SUCCESS),
             InlineKeyboardButton("♾ Permanent", callback_data="dur_0", style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("⬅️ Back", callback_data="grant_menu", style=ButtonStyle.PRIMARY)]
        ])
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Step 5: Confirm
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_callback_query(filters.regex(r"^dur_(\d+)$") & is_admin)
async def select_duration(client, callback_query):
    duration_hours = int(callback_query.matches[0].group(1))
    user_id = callback_query.from_user.id
    
    state, data = await db.get_state(user_id)
    if state != WAITING_DURATION_GRANT: return

    data["duration_hours"] = duration_hours
    await db.set_state(user_id, WAITING_CONFIRM_GRANT, data)
    
    # Format duration
    if duration_hours == 0:
        dur_text = "♾ Permanent"
    elif duration_hours < 24:
        dur_text = f"⏰ {duration_hours} hour(s)"
    else:
        dur_text = f"⏰ {duration_hours // 24} day(s)"
    
    mode = data.get("mode", "single")
    if mode == "multi":
        folders = data.get("folders_selected", [])
        folder_text = f"📂 **Folders ({len(folders)}):**\n" + "\n".join(f"   • {f['name']}" for f in folders)
    else:
        folder_text = f"📂 Folder: `{data.get('folder_name', 'Unknown')}`"
    
    # Calculate expiry date
    import time
    expiry_date_str = ""
    if duration_hours > 0:
        expiry_ts = time.time() + (duration_hours * 3600)
        expiry_date_str = format_timestamp(expiry_ts)
        
    confirm_msg = (
        "⚠️ **Confirm Access Grant**\n\n"
        f"📧 User: `{data['email']}`\n"
        f"{folder_text}\n"
        f"🔑 Role: **{data['role'].capitalize()}**\n"
        f"⏳ Duration: **{dur_text}**"
    )
    
    if expiry_date_str:
        confirm_msg += f"\n📅 Expires on: {expiry_date_str}"
        
    confirm_msg += "\n\nIs this correct?"
    
    await safe_edit(callback_query, 
        confirm_msg,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Confirm", callback_data="grant_confirm", style=ButtonStyle.SUCCESS),
             InlineKeyboardButton("❌ Cancel", callback_data="cancel_flow", style=ButtonStyle.DANGER)]
        ])
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Step 6: Execute Grant
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_callback_query(filters.regex("^grant_confirm$") & is_admin)
async def execute_grant(client, callback_query):
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    
    if state != WAITING_CONFIRM_GRANT: return

    mode = data.get("mode", "single")
    
    if mode == "multi":
        await _execute_multi_grant(client, callback_query, user_id, data)
    else:
        await _execute_single_grant(client, callback_query, user_id, data)
    
    await db.delete_state(user_id)


async def _execute_single_grant(client, callback_query, user_id, data):
    """Execute grant for a single folder."""
    await safe_edit(callback_query, "⏳ Processing request...")
    drive_service.set_admin_user(user_id)
    
    # 1. Atomic Check: Verify against DB first to prevent race conditions
    # If a grant is already active in DB, skip Drive API call to avoid duplicates
    existing_db = await db.grants.find_one({
        "email": data["email"],
        "folder_id": data["folder_id"],
        "status": "active"
    })
    
    if existing_db:
         await safe_edit(callback_query, f"⚠️ Access already exists for `{data['email']}` (checked via DB).")
         return

    # 2. Check Drive API for existing permissions (Double check)
    try:
        existing_perms = await drive_service.get_permissions(data["folder_id"], db)
        existing = next((p for p in existing_perms if p.get('emailAddress', '').lower() == data['email'].lower()), None)
        
        if existing:
            current_role = existing.get('role', 'unknown')
            await safe_edit(callback_query, 
                f"⚠️ **User Already Has Access!**\n\n"
                f"📧 `{data['email']}`\n"
                f"📂 `{data['folder_name']}`\n"
                f"🔑 Current Role: **{current_role}**\n\n"
                f"No changes made."
            )
            return
    except Exception as e:
        LOGGER.error(f"Error checking permissions: {e}")
        # Proceed with caution if check fails, or abort? 
        # For now, we proceed to try granting, as API might have failed temporarily.

    # 3. Grant Access
    success = await drive_service.grant_access(data["folder_id"], data["email"], data["role"], db)
    
    if success:
        duration_hours = data.get("duration_hours", 0)
        
        if duration_hours > 0:
            await db.add_timed_grant(
                admin_id=user_id,
                email=data["email"],
                folder_id=data["folder_id"],
                folder_name=data["folder_name"],
                role=data["role"],
                duration_hours=duration_hours
            )
        
        await db.log_action(
            admin_id=user_id,
            admin_name=callback_query.from_user.first_name,
            action="grant",
            details=data
        )
        
        dur_text = format_duration(duration_hours)
        await broadcast(client, "grant", {
            "email": data["email"],
            "folder_name": data["folder_name"],
            "role": data["role"],
            "duration": dur_text,
            "admin_name": callback_query.from_user.first_name
        })
        
        # Calculate dates
        import time
        now = time.time()
        granted_at = format_timestamp(now)
        expiry_str = ""
        
        if duration_hours > 0:
            expiry_ts = now + (duration_hours * 3600)
            expiry_date = format_date(expiry_ts)
            expiry_str = f"Expires: {expiry_date}\n"
        
        await safe_edit(callback_query, 
            "✅ **Access Granted Successfully!**\n\n"
            f"User: `{data['email']}`\n"
            f"Folder: `{data['folder_name']}`\n"
            f"Role: {data['role'].capitalize()}\n"
            f"Duration: {dur_text}\n"
            f"{expiry_str}"
            f"Granted at: {granted_at}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Grant Another", callback_data="grant_menu", style=ButtonStyle.SUCCESS),
                 InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu", style=ButtonStyle.PRIMARY)]
            ])
        )
    else:
        await safe_edit(callback_query, 
            "❌ **Failed to grant access.**\nCheck logs or credentials.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu", style=ButtonStyle.PRIMARY)]])
        )


async def _execute_multi_grant(client, callback_query, user_id, data):
    """Execute grant for multiple folders in a loop."""
    folders = data.get("folders_selected", [])
    email = data["email"]
    role = data["role"]
    duration_hours = data.get("duration_hours", 0)
    dur_text = format_duration(duration_hours)
    drive_service.set_admin_user(user_id)
    
    await safe_edit(callback_query, 
        f"⏳ **Granting access to {len(folders)} folders...**"
    )
    
    results = []
    
    for folder in folders:
        try:
            # Check duplicate
            existing_perms = await drive_service.get_permissions(folder["id"], db)
            existing = next((p for p in existing_perms if p.get('emailAddress', '').lower() == email.lower()), None)
            
            if existing:
                results.append(f"⚠️ {folder['name']} — already has access")
                continue
            
            success = await drive_service.grant_access(folder["id"], email, role, db)
            
            if success:
                # Timed grant
                if duration_hours > 0:
                    await db.add_timed_grant(
                        admin_id=user_id,
                        email=email,
                        folder_id=folder["id"],
                        folder_name=folder["name"],
                        role=role,
                        duration_hours=duration_hours
                    )
                
                # Log per folder
                await db.log_action(
                    admin_id=user_id,
                    admin_name=callback_query.from_user.first_name,
                    action="grant",
                    details={
                        "email": email,
                        "folder_id": folder["id"],
                        "folder_name": folder["name"],
                        "role": role,
                        "duration_hours": duration_hours,
                        "mode": "multi_folder"
                    }
                )
                await broadcast(client, "grant", {
                    "email": email,
                    "folder_name": folder["name"],
                    "role": role,
                    "duration": dur_text,
                    "admin_name": callback_query.from_user.first_name
                })
                
                results.append(f"✅ {folder['name']} — granted")
            else:
                results.append(f"❌ {folder['name']} — failed")
                
        except Exception as e:
            LOGGER.error(f"Error granting {email} to {folder['name']}: {e}")
            results.append(f"❌ {folder['name']} — error")
    
    results_text = "\n".join(results)
    granted = sum(1 for r in results if r.startswith("✅"))
    
    import time
    completed_at = format_timestamp(time.time())
    expiry_str = ""
    if duration_hours > 0:
        expiry_ts = time.time() + (duration_hours * 3600)
        expiry_str = f"📅 Expires: {format_date(expiry_ts)}\n"
    
    await safe_edit(callback_query, 
        f"{'✅' if granted > 0 else '❌'} **Grant Complete!**\n\n"
        f"📧 `{email}` | 🔑 {role.capitalize()} | ⏳ {dur_text}\n"
        f"{expiry_str}\n"
        f"{results_text}\n\n"
        f"**{granted}/{len(folders)}** folders granted.\n"
        f"Completed at: {completed_at}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Grant Another", callback_data="grant_menu", style=ButtonStyle.SUCCESS),
             InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu", style=ButtonStyle.PRIMARY)]
        ])
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Cancel Flow
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_callback_query(filters.regex("^cancel_flow$") & is_admin)
async def cancel_flow(client, callback_query):
    await db.delete_state(callback_query.from_user.id)
    await callback_query.answer("Cancelled.")
    await safe_edit(callback_query.message, 
        "🚫 Operation Cancelled.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu", style=ButtonStyle.PRIMARY)]])
    )
