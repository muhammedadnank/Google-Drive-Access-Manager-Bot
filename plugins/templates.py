from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.database import db
from services.drive import drive_service
from utils.states import (
    WAITING_TEMPLATE_NAME, WAITING_TEMPLATE_FOLDERS,
    WAITING_TEMPLATE_ROLE, WAITING_TEMPLATE_DURATION,
    WAITING_APPLY_EMAIL, WAITING_APPLY_CONFIRM
)
WAITING_APPLY_DURATION_OVERRIDE = "WAITING_APPLY_DURATION_OVERRIDE"
from utils.filters import check_state, is_admin
from utils.validators import validate_email
from utils.pagination import create_checkbox_keyboard, sort_folders
import logging
import re

LOGGER = logging.getLogger(__name__)


def _format_duration(h):
    if h == 0: return "♾ Permanent"
    elif h < 24: return f"{h}h"
    else: return f"{h // 24}d"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Templates Menu
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_callback_query(filters.regex("^templates_menu$"))
async def templates_menu(client, callback_query):
    templates = await db.get_templates()
    
    if not templates:
        await callback_query.edit_message_text(
            "📋 **Access Templates**\n\n"
            "No templates created yet.\n"
            "Templates let you save folder + role + duration presets.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Create Template", callback_data="create_template")],
                [InlineKeyboardButton("🏠 Back", callback_data="main_menu")]
            ])
        )
        return
    
    text = f"📋 **Access Templates** ({len(templates)})\n\n"
    keyboard = []
    
    for t in templates:
        folders_count = len(t.get("folders", []))
        dur = _format_duration(t.get("duration_hours", 0))
        text += f"📌 **{t['name']}** — {folders_count} folder(s) | {t['role'].capitalize()} | {dur}\n"
        keyboard.append([
            InlineKeyboardButton(f"▶️ {t['name']}", callback_data=f"apply_tpl_{t['name'][:30]}"),
            InlineKeyboardButton("🗑", callback_data=f"del_tpl_{t['name'][:30]}")
        ])
    
    keyboard.append([InlineKeyboardButton("➕ Create Template", callback_data="create_template")])
    keyboard.append([InlineKeyboardButton("🏠 Back", callback_data="main_menu")])
    
    await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Create Template: Step 1 — Name
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_callback_query(filters.regex("^create_template$"))
async def create_template_start(client, callback_query):
    user_id = callback_query.from_user.id
    await db.set_state(user_id, WAITING_TEMPLATE_NAME)
    
    await callback_query.edit_message_text(
        "📋 **Create Template**\n\n"
        "Enter a name for this template:\n"
        "Example: `New Intern`, `Course Launch`, `Paid User`",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel", callback_data="templates_menu")]
        ])
    )


@Client.on_message(check_state(WAITING_TEMPLATE_NAME) & filters.text)
async def receive_template_name(client, message):
    name = message.text.strip()[:40]
    user_id = message.from_user.id
    
    if not name:
        await message.reply_text("❌ Name cannot be empty.")
        return
    
    # Check duplicate
    existing = await db.get_template(name)
    if existing:
        await message.reply_text(
            f"⚠️ Template `{name}` already exists. Choose a different name."
        )
        return
    
    msg = await message.reply_text("📂 Loading folders...")
    
    folders = await drive_service.get_folders_cached(db)
    if not folders:
        await msg.edit_text("❌ No folders found.")
        await db.delete_state(user_id)
        return
    
    folders = sort_folders(folders)
    
    await db.set_state(user_id, WAITING_TEMPLATE_FOLDERS, {
        "name": name, "folders": folders, "selected": []
    })
    
    keyboard = create_checkbox_keyboard(folders, set(), page=1)
    
    await msg.edit_text(
        f"📋 Template: **{name}**\n\n"
        "📂 **Select folders** (tap to toggle):",
        reply_markup=keyboard
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Create Template: Step 2 — Folder Checkbox
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_callback_query(filters.regex(r"^tpl_tgl_(.+)$"))
async def template_toggle_folder(client, callback_query):
    folder_id = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    if state != WAITING_TEMPLATE_FOLDERS: return
    
    selected = set(data.get("selected", []))
    if folder_id in selected:
        selected.discard(folder_id)
    else:
        selected.add(folder_id)
    
    data["selected"] = list(selected)
    await db.set_state(user_id, WAITING_TEMPLATE_FOLDERS, data)
    
    folders = data["folders"]
    per_page = 15
    folder_index = next((i for i, f in enumerate(folders) if f["id"] == folder_id), 0)
    current_page = (folder_index // per_page) + 1
    
    keyboard = create_checkbox_keyboard(
        folders, selected, page=current_page, per_page=per_page,
        callback_prefix="tpl_mf_page",
        toggle_prefix="tpl_tgl_",
        confirm_callback="tpl_confirm_folders"
    )
    
    try:
        await callback_query.edit_message_reply_markup(reply_markup=keyboard)
    except Exception:
        pass
    
    await callback_query.answer(f"{'☑️' if folder_id in selected else '☐'} ({len(selected)} selected)")


@Client.on_callback_query(filters.regex(r"^tpl_mf_page_(\d+)$"))
async def template_folder_page(client, callback_query):
    page = int(callback_query.matches[0].group(1))
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    if state != WAITING_TEMPLATE_FOLDERS: return
    
    keyboard = create_checkbox_keyboard(
        data["folders"], set(data.get("selected", [])), page=page,
        callback_prefix="tpl_mf_page",
        toggle_prefix="tpl_tgl_",
        confirm_callback="tpl_confirm_folders"
    )
    try:
        await callback_query.edit_message_reply_markup(reply_markup=keyboard)
    except Exception:
        pass


@Client.on_callback_query(filters.regex("^tpl_confirm_folders$"))
async def template_confirm_folders(client, callback_query):
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    if state != WAITING_TEMPLATE_FOLDERS: return
    
    selected_ids = set(data.get("selected", []))
    if not selected_ids:
        await callback_query.answer("⚠️ Select at least one folder!", show_alert=True)
        return
    
    folders = data["folders"]
    selected_folders = [f for f in folders if f["id"] in selected_ids]
    
    data["selected_folders"] = selected_folders
    await db.set_state(user_id, WAITING_TEMPLATE_ROLE, data)
    
    folder_list = "\n".join(f"   • {f['name']}" for f in selected_folders[:8])
    if len(selected_folders) > 8:
        folder_list += f"\n   ... +{len(selected_folders)-8} more"
    
    await callback_query.edit_message_text(
        f"📋 Template: **{data['name']}**\n"
        f"📂 **Folders ({len(selected_folders)}):**\n{folder_list}\n\n"
        "🔑 **Select Role**:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👀 Viewer", callback_data="tpl_role_viewer"),
             InlineKeyboardButton("✏️ Editor", callback_data="tpl_role_editor")],
            [InlineKeyboardButton("⬅️ Cancel", callback_data="templates_menu")]
        ])
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Create Template: Step 3 — Role
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_callback_query(filters.regex(r"^tpl_role_(viewer|editor)$"))
async def template_select_role(client, callback_query):
    role = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    if state != WAITING_TEMPLATE_ROLE: return
    
    data["role"] = role
    
    if role == "editor":
        # Editors always permanent — save immediately
        data["duration_hours"] = 0
        await _save_template(callback_query, user_id, data)
        return
    
    await db.set_state(user_id, WAITING_TEMPLATE_DURATION, data)
    
    await callback_query.edit_message_text(
        f"📋 Template: **{data['name']}**\n"
        f"📂 {len(data['selected_folders'])} folders | 🔑 Viewer\n\n"
        "⏰ **Select Duration**:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("1 Hour", callback_data="tpl_dur_1"),
             InlineKeyboardButton("6 Hours", callback_data="tpl_dur_6")],
            [InlineKeyboardButton("1 Day", callback_data="tpl_dur_24"),
             InlineKeyboardButton("7 Days", callback_data="tpl_dur_168")],
            [InlineKeyboardButton("✅ 30 Days (Default)", callback_data="tpl_dur_720"),
             InlineKeyboardButton("♾ Permanent", callback_data="tpl_dur_0")],
            [InlineKeyboardButton("⬅️ Cancel", callback_data="templates_menu")]
        ])
    )


@Client.on_callback_query(filters.regex(r"^tpl_dur_(\d+)$"))
async def template_select_duration(client, callback_query):
    duration = int(callback_query.matches[0].group(1))
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    if state != WAITING_TEMPLATE_DURATION: return
    
    data["duration_hours"] = duration
    await _save_template(callback_query, user_id, data)


async def _save_template(callback_query, user_id, data):
    """Save the template to database."""
    folders_to_save = [{"id": f["id"], "name": f["name"]} for f in data["selected_folders"]]
    
    await db.save_template(
        name=data["name"],
        folders=folders_to_save,
        role=data["role"],
        duration_hours=data["duration_hours"],
        created_by=callback_query.from_user.first_name
    )
    
    await db.delete_state(user_id)
    
    dur = _format_duration(data["duration_hours"])
    folder_list = "\n".join(f"   • {f['name']}" for f in folders_to_save[:5])
    if len(folders_to_save) > 5:
        folder_list += f"\n   ... +{len(folders_to_save)-5} more"
    
    await callback_query.edit_message_text(
        "✅ **Template Saved!**\n\n"
        f"📌 **{data['name']}**\n"
        f"📂 Folders ({len(folders_to_save)}):\n{folder_list}\n"
        f"🔑 Role: {data['role'].capitalize()}\n"
        f"⏳ Duration: {dur}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Templates", callback_data="templates_menu")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ])
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Delete Template
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_callback_query(filters.regex(r"^del_tpl_(.+)$"))
async def delete_template(client, callback_query):
    name = callback_query.matches[0].group(1)
    await db.delete_template(name)
    await callback_query.answer(f"🗑 Deleted: {name}")
    # Refresh menu
    await templates_menu(client, callback_query)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Apply Template: Step 1 — Select Template
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_callback_query(filters.regex(r"^apply_tpl_(.+)$"))
async def apply_template_start(client, callback_query):
    name = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    
    template = await db.get_template(name)
    if not template:
        await callback_query.answer("Template not found!", show_alert=True)
        return
    
    dur = _format_duration(template.get("duration_hours", 0))
    folders = template.get("folders", [])
    folder_list = "\n".join(f"   • {f['name']}" for f in folders[:5])
    if len(folders) > 5:
        folder_list += f"\n   ... +{len(folders)-5} more"
    
    await db.set_state(user_id, WAITING_APPLY_EMAIL, {
        "template_name": template["name"],
        "folders": template["folders"],
        "role": template["role"],
        "duration_hours": template.get("duration_hours", 0)
    })
    
    await db.set_state(user_id, WAITING_APPLY_EMAIL, {
        "template_name": template["name"],
        "folders": template["folders"],
        "role": template["role"],
        "duration_hours": template.get("duration_hours", 0),
        "original_duration_hours": template.get("duration_hours", 0)
    })

    await callback_query.edit_message_text(
        f"▶️ **Apply Template: {template["name"]}**\n\n"
        f"📂 Folders ({len(folders)}):\n{folder_list}\n"
        f"🔑 Role: {template["role"].capitalize()}\n"
        f"⏳ Default Duration: {dur}\n\n"
        "📧 **Enter email(s)** to grant access:\n"
        "_(comma or newline separated for multiple)_\n\n"
        "⏰ You can override the duration before confirming.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel", callback_data="templates_menu")]
        ])
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Apply Template: Step 2 — Receive Emails + Duplicate Check
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(check_state(WAITING_APPLY_EMAIL) & filters.text)
async def apply_template_emails(client, message):
    user_id = message.from_user.id
    raw = message.text.strip()
    
    parts = re.split(r'[,\n]+', raw)
    emails = list(dict.fromkeys(e.strip().lower() for e in parts if e.strip()))  # deduplicate, preserve order
    
    valid = [e for e in emails if validate_email(e)]
    invalid = [e for e in emails if not validate_email(e)]
    
    if not valid:
        await message.reply_text("❌ No valid emails found. Try again.")
        return
    
    state, data = await db.get_state(user_id)
    
    msg = await message.reply_text("🔍 Checking for duplicates...")
    
    # Check duplicates per folder
    folders = data["folders"]
    all_new = []
    all_dupes = set()
    
    for folder in folders:
        try:
            perms = await drive_service.get_permissions(folder["id"])
            existing = {p.get('emailAddress', '').lower() for p in perms if p.get('emailAddress')}
            for email in valid:
                if email in existing:
                    all_dupes.add(email)
        except Exception:
            pass
    
    new_emails = [e for e in valid if e not in all_dupes]
    duplicates = list(all_dupes)
    
    data["emails"] = valid
    data["new_emails"] = new_emails
    data["duplicates"] = duplicates
    await db.set_state(user_id, WAITING_APPLY_CONFIRM, data)
    
    dur = _format_duration(data.get("duration_hours", 0))
    
    text = f"⚠️ **Apply Template: {data['template_name']}**\n\n"
    text += f"📂 {len(folders)} folder(s) | 🔑 {data['role'].capitalize()} | ⏳ {dur}\n\n"
    
    if duplicates:
        text += f"⚠️ **{len(duplicates)} already have access** (will skip):\n"
        text += "\n".join(f"   • ~~{e}~~" for e in duplicates[:5])
        if len(duplicates) > 5:
            text += f"\n   ... +{len(duplicates)-5} more"
        text += "\n\n"
    
    if invalid:
        text += f"❌ Invalid emails skipped: {', '.join(invalid)}\n\n"
    
    if new_emails:
        text += f"✅ **{len(new_emails)} to grant** across {len(folders)} folders:\n"
        text += "\n".join(f"   • `{e}`" for e in new_emails[:10])
        if len(new_emails) > 10:
            text += f"\n   ... +{len(new_emails)-10} more"
    else:
        text += "❌ All emails already have access in all folders!"
    
    buttons = []
    if new_emails:
        total_ops = len(new_emails) * len(folders)
        dur_display = _format_duration(data.get("duration_hours", 0))
        original_dur = _format_duration(data.get("original_duration_hours", data.get("duration_hours", 0)))
        override_label = f" (overridden from {original_dur})" if data.get("duration_hours") != data.get("original_duration_hours") else ""
        buttons.append([InlineKeyboardButton(
            f"✅ Grant {total_ops} ops | ⏳ {dur_display}{override_label}",
            callback_data="apply_tpl_confirm"
        )])
        buttons.append([InlineKeyboardButton("⏱ Override Duration", callback_data="tpl_dur_override")])
    buttons.append([InlineKeyboardButton("❌ Cancel", callback_data="templates_menu")])

    await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Apply Template: Step 3 — Execute
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_callback_query(filters.regex("^apply_tpl_confirm$"))
async def apply_template_execute(client, callback_query):
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    if state != WAITING_APPLY_CONFIRM: return
    
    new_emails = data.get("new_emails", [])
    folders = data["folders"]
    role = data["role"]
    duration_hours = data.get("duration_hours", 0)
    template_name = data["template_name"]
    
    total = len(new_emails) * len(folders)
    await callback_query.edit_message_text(
        f"⏳ **Applying template: {template_name}**\n"
        f"Processing {total} operations..."
    )
    
    granted = 0
    failed = 0
    skipped = 0
    
    for email in new_emails:
        for folder in folders:
            try:
                # Check duplicate per folder
                perms = await drive_service.get_permissions(folder["id"])
                existing = next((p for p in perms if p.get('emailAddress', '').lower() == email), None)
                
                if existing:
                    skipped += 1
                    continue
                
                success = await drive_service.grant_access(folder["id"], email, role)
                if success:
                    granted += 1
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
                        details={"email": email, "folder_id": folder["id"],
                                 "folder_name": folder["name"], "role": role,
                                 "duration_hours": duration_hours, "mode": "template",
                                 "template": template_name}
                    )
                else:
                    failed += 1
            except Exception as e:
                LOGGER.error(f"Template apply error {email} → {folder['name']}: {e}")
                failed += 1
    
    dur = _format_duration(duration_hours)
    
    await callback_query.edit_message_text(
        f"{'✅' if granted > 0 else '❌'} **Template Applied: {template_name}**\n\n"
        f"📧 {len(new_emails)} email(s) × 📂 {len(folders)} folder(s)\n"
        f"🔑 {role.capitalize()} | ⏳ {dur}\n\n"
        f"✅ Granted: **{granted}**\n"
        f"⏭ Skipped: **{skipped}**\n"
        f"❌ Failed: **{failed}**",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Templates", callback_data="templates_menu")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ])
    )
    
    await db.delete_state(user_id)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEW: Duration Override for Template Apply
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_callback_query(filters.regex("^tpl_dur_override$"))
async def template_duration_override(client, callback_query):
    """Show duration override screen when applying a template."""
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    if state != WAITING_APPLY_CONFIRM:
        await callback_query.answer("Session expired.", show_alert=True)
        return

    original_dur = _format_duration(data.get("original_duration_hours", data.get("duration_hours", 0)))

    await callback_query.edit_message_text(
        f"⏰ **Override Duration**\n\n"
        f"Template default: **{original_dur}**\n"
        f"Select a custom duration:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("1 Hour", callback_data="tpl_ovr_dur_1"),
             InlineKeyboardButton("6 Hours", callback_data="tpl_ovr_dur_6")],
            [InlineKeyboardButton("1 Day", callback_data="tpl_ovr_dur_24"),
             InlineKeyboardButton("7 Days", callback_data="tpl_ovr_dur_168")],
            [InlineKeyboardButton("14 Days", callback_data="tpl_ovr_dur_336"),
             InlineKeyboardButton("30 Days", callback_data="tpl_ovr_dur_720")],
            [InlineKeyboardButton("♾ Permanent", callback_data="tpl_ovr_dur_0")],
            [InlineKeyboardButton(f"↩️ Use Default ({original_dur})", callback_data="tpl_ovr_reset")],
        ])
    )


@Client.on_callback_query(filters.regex(r"^tpl_ovr_dur_(\d+)$"))
async def template_apply_override_duration(client, callback_query):
    """Apply the overridden duration and return to confirmation screen."""
    new_duration = int(callback_query.matches[0].group(1))
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    if state != WAITING_APPLY_CONFIRM:
        await callback_query.answer("Session expired.", show_alert=True)
        return

    data["duration_hours"] = new_duration
    await db.set_state(user_id, WAITING_APPLY_CONFIRM, data)

    dur_label = _format_duration(new_duration)
    await callback_query.answer(f"⏳ Duration set to {dur_label}")

    # Re-show confirmation screen with updated duration
    await _show_apply_confirmation(callback_query, data)


@Client.on_callback_query(filters.regex("^tpl_ovr_reset$"))
async def template_apply_reset_duration(client, callback_query):
    """Reset to original template duration."""
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    if state != WAITING_APPLY_CONFIRM:
        await callback_query.answer("Session expired.", show_alert=True)
        return

    data["duration_hours"] = data.get("original_duration_hours", 0)
    await db.set_state(user_id, WAITING_APPLY_CONFIRM, data)
    await callback_query.answer("↩️ Reset to default duration")
    await _show_apply_confirmation(callback_query, data)


async def _show_apply_confirmation(callback_query, data):
    """Helper: render the apply confirmation message with current duration."""
    new_emails = data.get("new_emails", [])
    duplicates = data.get("duplicates", [])
    invalid = data.get("invalid", [])
    folders = data["folders"]
    dur = _format_duration(data.get("duration_hours", 0))
    original_dur = _format_duration(data.get("original_duration_hours", data.get("duration_hours", 0)))

    text = f"⚠️ **Apply Template: {data['template_name']}**\n\n"
    text += f"📂 {len(folders)} folder(s) | 🔑 {data['role'].capitalize()} | ⏳ {dur}\n"

    if data.get("duration_hours") != data.get("original_duration_hours"):
        text += f"_⏱ Duration overridden (template default: {original_dur})_\n"

    text += "\n"

    if duplicates:
        text += f"⚠️ **{len(duplicates)} already have access** (will skip):\n"
        text += "\n".join(f"   • ~~{e}~~" for e in duplicates[:5])
        if len(duplicates) > 5:
            text += f"\n   ... +{len(duplicates)-5} more"
        text += "\n\n"

    if new_emails:
        total_ops = len(new_emails) * len(folders)
        text += f"✅ **{len(new_emails)} to grant** across {len(folders)} folders:\n"
        text += "\n".join(f"   • `{e}`" for e in new_emails[:10])
        if len(new_emails) > 10:
            text += f"\n   ... +{len(new_emails)-10} more"
    else:
        text += "❌ All emails already have access in all folders!"

    buttons = []
    if new_emails:
        total_ops = len(new_emails) * len(folders)
        buttons.append([InlineKeyboardButton(
            f"✅ Grant {total_ops} ops | ⏳ {dur}",
            callback_data="apply_tpl_confirm"
        )])
        buttons.append([InlineKeyboardButton("⏱ Override Duration", callback_data="tpl_dur_override")])
    buttons.append([InlineKeyboardButton("❌ Cancel", callback_data="templates_menu")])

    await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))
