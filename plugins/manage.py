import logging
import time

from pyrogram import Client, filters
from pyrogram.enums import ButtonStyle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from services.database import db
from services.drive import drive_service
from services.broadcast import broadcast
from utils.states import WAITING_FOLDER_MANAGE, WAITING_USER_MANAGE, WAITING_ACTION_MANAGE
from utils.time import safe_edit, format_timestamp, format_time_remaining
from utils.pagination import create_pagination_keyboard, sort_folders, natural_sort_key
from plugins.grant import build_az_group_keyboard, filter_folders_by_group
from utils.filters import is_admin

LOGGER = logging.getLogger(__name__)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# /manage COMMAND  +  manage_menu CALLBACK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_message(filters.command("manage") & filters.private & is_admin)
async def manage_command(client, message):
    """Entry point via /manage command."""
    user_id = message.from_user.id
    await db.set_state(user_id, WAITING_FOLDER_MANAGE)

    msg = await message.reply_text("📂 Loading folders...")

    folders = await drive_service.get_folders_cached(db)
    if not folders:
        await safe_edit(msg, "❌ No folders found.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 Back", callback_data="main_menu", style=ButtonStyle.PRIMARY)
            ]]))
        return

    folders = sort_folders(folders)
    await db.set_state(user_id, WAITING_FOLDER_MANAGE, {"folders": folders})

    keyboard = create_pagination_keyboard(
        items=folders, page=1, per_page=20,
        callback_prefix="manage_folder_page",
        item_callback_func=lambda f: (f['name'], f"man_folder_{f['id']}"),
        back_callback_data="main_menu",
        refresh_callback_data="manage_refresh"
    )
    await safe_edit(msg, "📂 **Select a Folder to Manage:**", reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^manage_menu$") & is_admin)
async def list_manage_folders(client, callback_query):
    """Entry point via inline button."""
    user_id = callback_query.from_user.id
    await db.set_state(user_id, WAITING_FOLDER_MANAGE)

    # FIX: safe_edit(callback_query, ...) — not callback_query.message
    await safe_edit(callback_query, "📂 Loading folders...")

    folders = await drive_service.get_folders_cached(db)
    if not folders:
        await safe_edit(callback_query, "❌ No folders found.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 Back", callback_data="main_menu", style=ButtonStyle.PRIMARY)
            ]]))
        return

    folders = sort_folders(folders)
    await db.set_state(user_id, WAITING_FOLDER_MANAGE, {"folders": folders})

    keyboard = create_pagination_keyboard(
        items=folders, page=1, per_page=20,
        callback_prefix="manage_folder_page",
        item_callback_func=lambda f: (f['name'], f"man_folder_{f['id']}"),
        back_callback_data="main_menu",
        refresh_callback_data="manage_refresh"
    )
    await safe_edit(callback_query, "📂 **Select a Folder to Manage:**", reply_markup=keyboard)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Folder Pagination & Refresh
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_callback_query(filters.regex(r"^manage_az_([^_]+)_(\d+)$") & is_admin)
async def manage_az_folder_list(client, callback_query):
    """Show folders for a specific A-Z group in manage flow."""
    group  = callback_query.matches[0].group(1)
    page   = int(callback_query.matches[0].group(2))
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)

    if state != WAITING_FOLDER_MANAGE or "folders" not in data:
        await callback_query.answer("Session expired. Please /manage again.", show_alert=True)
        return

    filtered = filter_folders_by_group(data["folders"], group)
    keyboard = create_pagination_keyboard(
        items=filtered, page=page, per_page=15,
        callback_prefix=f"manage_az_{group}",
        item_callback_func=lambda f: (f["name"], f"man_folder_{f['id']}"),
        back_callback_data="manage_back_to_az",
        refresh_callback_data=None
    )
    await safe_edit(callback_query,
        f"📂 **[{group}] Folders** ({len(filtered)} total):\nTap a folder to manage:",
        reply_markup=keyboard
    )


@Client.on_callback_query(filters.regex("^manage_back_to_az$") & is_admin)
async def manage_back_to_az(client, callback_query):
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    if state != WAITING_FOLDER_MANAGE or "folders" not in data:
        await callback_query.answer("Session expired.", show_alert=True)
        return
    keyboard = build_az_group_keyboard(data["folders"], back_cb="main_menu", context="manage")
    await safe_edit(callback_query,
        "📂 **Select a Folder to Manage:**\nChoose a letter/number group:",
        reply_markup=keyboard
    )


@Client.on_callback_query(filters.regex("^manage_refresh$") & is_admin)
async def manage_refresh(client, callback_query):
    user_id = callback_query.from_user.id
    await callback_query.answer("🔄 Refreshing...")
    await db.clear_folder_cache()

    folders = await drive_service.get_folders_cached(db, force_refresh=True)
    if not folders:
        await safe_edit(callback_query, "❌ No folders found.")
        return

    folders = sort_folders(folders)
    await db.set_state(user_id, WAITING_FOLDER_MANAGE, {"folders": folders})

    keyboard = create_pagination_keyboard(
        items=folders, page=1, per_page=20,
        callback_prefix="manage_folder_page",
        item_callback_func=lambda f: (f['name'], f"man_folder_{f['id']}"),
        back_callback_data="main_menu",
        refresh_callback_data="manage_refresh"
    )
    await safe_edit(callback_query, "📂 **Select a Folder to Manage** (refreshed):", reply_markup=keyboard)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Step 2: List Users in Folder
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_callback_query(filters.regex(r"^man_folder_(.*)$") & is_admin)
async def list_folder_users(client, callback_query):
    folder_id = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)

    folder_name = next(
        (f["name"] for f in data.get("folders", []) if f["id"] == folder_id), "Unknown"
    )

    # FIX: safe_edit(callback_query, ...) — not callback_query.message
    await safe_edit(callback_query, f"👥 Fetching users for **{folder_name}**...")

    permissions = await drive_service.get_permissions(folder_id, db)
    users = [p for p in permissions if p.get("role") != "owner"]
    users = sorted(users, key=lambda u: natural_sort_key(u.get("emailAddress", "")))

    if not users:
        await safe_edit(callback_query,
            f"📂 **{folder_name}**\n\nNo users found with access (besides owners).",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("⬅️ Back", callback_data="manage_menu", style=ButtonStyle.PRIMARY)
            ]])
        )
        return

    # Show expiry info alongside each user
    active_grants = await db.get_active_grants()
    grant_map = {
        g["email"].lower(): g
        for g in active_grants if g.get("folder_id") == folder_id
    }

    viewers = sum(1 for u in users if u.get("role") == "reader")
    editors = sum(1 for u in users if u.get("role") == "writer")

    await db.set_state(user_id, WAITING_USER_MANAGE, {
        "folder_id": folder_id, "folder_name": folder_name, "users": users
    })

    role_icons = {"reader": "👀", "writer": "✏️", "commenter": "💬"}

    def make_user_label(u):
        email = u.get("emailAddress", "No Email")
        icon = role_icons.get(u.get("role"), "🔑")
        grant = grant_map.get(email.lower())
        if grant:
            remaining = format_time_remaining(grant["expires_at"])
            return f"{icon} {email} ⏳{remaining}", f"man_user_{u.get('id')}"
        return f"{icon} {email} ♾️", f"man_user_{u.get('id')}"

    keyboard = create_pagination_keyboard(
        items=users, page=1, per_page=15,
        callback_prefix="manage_user_page",
        item_callback_func=make_user_label
    )
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(
            f"🗑 Revoke All in Folder ({len(users)})",
            callback_data=f"man_revoke_all_{folder_id}",
            style=ButtonStyle.DANGER
        )
    ])
    # Pin / Unpin button
    is_pinned = await db.is_folder_pinned(user_id, folder_id)
    pin_label = "📌 Unpin Folder" if is_pinned else "⭐ Pin Folder"
    pin_cb    = f"unpin_folder_{folder_id}" if is_pinned else f"pin_folder_{folder_id}_{folder_name[:30]}"
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(pin_label, callback_data=pin_cb, style=ButtonStyle.PRIMARY)
    ])
    keyboard.inline_keyboard.append([
        InlineKeyboardButton("⬅️ Back", callback_data="manage_menu", style=ButtonStyle.PRIMARY)
    ])

    await safe_edit(callback_query,
        f"📂 **{folder_name}**\n"
        f"👥 {len(users)} users | 👀 {viewers} viewers | ✏️ {editors} editors\n\n"
        "Tap a user to manage (⏳ = timed, ♾️ = permanent):",
        reply_markup=keyboard
    )


@Client.on_callback_query(filters.regex(r"^manage_user_page_(\d+)$") & is_admin)
async def manage_user_pagination(client, callback_query):
    page = int(callback_query.matches[0].group(1))
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)

    if state != WAITING_USER_MANAGE:
        return

    keyboard = create_pagination_keyboard(
        items=data["users"], page=page, per_page=15,
        callback_prefix="manage_user_page",
        item_callback_func=lambda u: (
            f"{u.get('emailAddress', 'Unknown')}",
            f"man_user_{u.get('id')}"
        )
    )
    try:
        await callback_query.edit_message_reply_markup(reply_markup=keyboard)
    except Exception as e:
        LOGGER.debug(f"User page edit: {e}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Step 3: User Actions
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_callback_query(filters.regex(r"^man_user_(.*)$") & is_admin)
async def manage_user_actions(client, callback_query):
    perm_id = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)

    user_obj = next((u for u in data.get("users", []) if u["id"] == perm_id), None)
    if not user_obj:
        await callback_query.answer("User not found.", show_alert=True)
        return

    data["selected_user"] = user_obj
    await db.set_state(user_id, WAITING_ACTION_MANAGE, data)

    role  = user_obj.get("role", "unknown")
    email = user_obj.get("emailAddress", "No Email")

    # FIX: safe_edit(callback_query, ...) — not callback_query.message
    await safe_edit(callback_query,
        f"👤 **User Details**\n\n"
        f"📧 Email: `{email}`\n"
        f"🔑 Role: **{role}**\n"
        f"📂 Folder: `{data['folder_name']}`\n\n"
        "Select Action:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Change Role",    callback_data="action_change_role",   style=ButtonStyle.PRIMARY),
             InlineKeyboardButton("🗑 Remove Access",  callback_data="action_remove_access", style=ButtonStyle.DANGER)],
            [InlineKeyboardButton("⬅️ Back",           callback_data="manage_menu",          style=ButtonStyle.PRIMARY)]
        ])
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Change Role Flow
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_callback_query(filters.regex("^action_change_role$") & is_admin)
async def prompt_change_role(client, callback_query):
    # FIX: safe_edit(callback_query, ...) — not callback_query.message
    await safe_edit(callback_query,
        "🔑 **Select New Role:**",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👀 Viewer", callback_data="set_role_viewer", style=ButtonStyle.PRIMARY),
             InlineKeyboardButton("✏️ Editor", callback_data="set_role_editor", style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("⬅️ Back",   callback_data="manage_menu",    style=ButtonStyle.PRIMARY)]
        ])
    )


@Client.on_callback_query(filters.regex(r"^set_role_(viewer|editor)$") & is_admin)
async def execute_role_change(client, callback_query):
    new_role = callback_query.matches[0].group(1)
    user_id  = callback_query.from_user.id
    state, data = await db.get_state(user_id)

    email     = data["selected_user"]["emailAddress"]
    folder_id = data["folder_id"]

    # FIX: safe_edit(callback_query, ...) — not callback_query.message
    await safe_edit(callback_query, "⏳ Updating role...")
    drive_service.set_admin_user(user_id)
    success = await drive_service.change_role(folder_id, email, new_role, db)

    if success:
        # Sync role in DB timed grants
        active = await db.get_active_grants()
        for g in active:
            if g["email"].lower() == email.lower() and g["folder_id"] == folder_id:
                await db.grants.update_one({"_id": g["_id"]}, {"$set": {"role": new_role}})

        await db.log_action(user_id, callback_query.from_user.first_name, "role_change",
                            {"email": email, "folder_name": data["folder_name"], "new_role": new_role})
        await broadcast(client, "role_change", {
            "email": email, "folder_name": data["folder_name"],
            "new_role": new_role, "admin_name": callback_query.from_user.first_name
        })
        await safe_edit(callback_query,
            f"✅ Role updated to **{new_role}** for `{email}`.\n"
            f"📂 Folder: `{data['folder_name']}`",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📂 Back to Folder", callback_data=f"man_folder_{folder_id}", style=ButtonStyle.PRIMARY)],
                [InlineKeyboardButton("🏠 Main Menu",      callback_data="main_menu",               style=ButtonStyle.PRIMARY)]
            ])
        )
    else:
        await safe_edit(callback_query, "❌ Failed to update role.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu", style=ButtonStyle.PRIMARY)
            ]])
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Remove Access Flow
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_callback_query(filters.regex("^action_remove_access$") & is_admin)
async def confirm_remove(client, callback_query):
    # FIX: safe_edit(callback_query, ...) — not callback_query.message
    await safe_edit(callback_query,
        "⚠️ **Are you sure?**\n"
        "This will revoke access immediately.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🗑 Yes, Remove", callback_data="confirm_remove", style=ButtonStyle.DANGER),
             InlineKeyboardButton("❌ Cancel",       callback_data="manage_menu",   style=ButtonStyle.PRIMARY)]
        ])
    )


@Client.on_callback_query(filters.regex("^confirm_remove$") & is_admin)
async def execute_remove(client, callback_query):
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)

    email     = data["selected_user"]["emailAddress"]
    folder_id = data["folder_id"]

    # FIX: safe_edit(callback_query, ...) — not callback_query.message
    await safe_edit(callback_query, "⏳ Removing access...")
    drive_service.set_admin_user(user_id)
    success = await drive_service.remove_access(folder_id, email, db)

    if success:
        active = await db.get_active_grants()
        for g in active:
            if g["email"].lower() == email.lower() and g["folder_id"] == folder_id:
                await db.revoke_grant(g["_id"])

        await db.log_action(user_id, callback_query.from_user.first_name, "remove",
                            {"email": email, "folder_name": data["folder_name"]})
        await broadcast(client, "revoke", {
            "email": email, "folder_name": data["folder_name"],
            "admin_name": callback_query.from_user.first_name
        })
        removed_at = format_timestamp(time.time())
        await safe_edit(callback_query,
            f"✅ Access removed for `{email}`.\n"
            f"📂 Folder: `{data['folder_name']}`\n"
            f"🕒 Removed at: {removed_at}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📂 Back to Folder", callback_data=f"man_folder_{folder_id}", style=ButtonStyle.PRIMARY)],
                [InlineKeyboardButton("🏠 Main Menu",      callback_data="main_menu",               style=ButtonStyle.PRIMARY)]
            ])
        )
    else:
        await safe_edit(callback_query, "❌ Failed to remove access.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu", style=ButtonStyle.PRIMARY)
            ]])
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Revoke All in Folder
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_callback_query(filters.regex(r"^man_revoke_all_(.+)$") & is_admin)
async def man_revoke_all_confirm(client, callback_query):
    folder_id = callback_query.matches[0].group(1)
    user_id   = callback_query.from_user.id
    state, data = await db.get_state(user_id)

    folder_name = data.get("folder_name", "Unknown")
    targets = [u for u in data.get("users", []) if u.get("role") != "owner"]

    await db.set_state(user_id, "CONFIRM_FOLDER_REVOKE_ALL", {
        **data, "revoke_targets": targets
    })

    await safe_edit(callback_query,
        f"⚠️ **Revoke All in Folder**\n\n"
        f"📂 {folder_name}\n"
        f"This will remove access for **{len(targets)} user(s)**.\n\n"
        "Are you sure?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Yes, Revoke All", callback_data="man_revoke_all_execute", style=ButtonStyle.DANGER),
             InlineKeyboardButton("❌ Cancel",           callback_data="manage_menu",           style=ButtonStyle.PRIMARY)]
        ])
    )


@Client.on_callback_query(filters.regex("^man_revoke_all_execute$") & is_admin)
async def man_revoke_all_execute(client, callback_query):
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)

    if state != "CONFIRM_FOLDER_REVOKE_ALL":
        await callback_query.answer("Session expired.", show_alert=True)
        return

    folder_id   = data["folder_id"]
    folder_name = data["folder_name"]
    targets     = data.get("revoke_targets", [])

    await safe_edit(callback_query, f"⏳ Revoking access for {len(targets)} user(s)...")

    drive_service.set_admin_user(user_id)
    success_count = 0
    fail_count    = 0

    for u in targets:
        email = u.get("emailAddress", "")
        if not email:
            continue
        try:
            ok = await drive_service.remove_access(folder_id, email, db)
            if ok:
                success_count += 1
                active = await db.get_active_grants()
                for g in active:
                    if g["email"].lower() == email.lower() and g["folder_id"] == folder_id:
                        await db.revoke_grant(g["_id"])
            else:
                fail_count += 1
        except Exception as e:
            LOGGER.error(f"Revoke all error ({email}): {e}")
            fail_count += 1

    await db.log_action(
        admin_id=user_id,
        admin_name=callback_query.from_user.first_name,
        action="bulk_revoke",
        details={"type": "folder_revoke_all", "folder_name": folder_name,
                 "success": success_count, "failed": fail_count}
    )
    await broadcast(client, "bulk_revoke", {
        "type": f"folder_revoke_all ({folder_name})",
        "success": success_count, "failed": fail_count,
        "admin_name": callback_query.from_user.first_name
    })

    revoked_at = format_timestamp(time.time())
    await safe_edit(callback_query,
        f"✅ **Folder Revoke Complete**\n\n"
        f"📂 {folder_name}\n"
        f"✅ Revoked: **{success_count}**\n"
        f"❌ Failed: **{fail_count}**\n"
        f"🕒 {revoked_at}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📂 Back to Folders", callback_data="manage_menu", style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("🏠 Main Menu",       callback_data="main_menu",   style=ButtonStyle.PRIMARY)]
        ])
    )
    await db.delete_state(user_id)
