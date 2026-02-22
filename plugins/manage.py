from pyrogram.enums import ButtonStyle
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.database import db
from services.drive import drive_service
from utils.states import (
    WAITING_FOLDER_MANAGE, WAITING_USER_MANAGE, WAITING_ACTION_MANAGE
)
from utils.time import safe_edit
from utils.pagination import create_pagination_keyboard, sort_folders
from utils.pagination import natural_sort_key
from utils.filters import is_admin
import logging
import time
from services.broadcast import broadcast
from utils.time import format_timestamp

LOGGER = logging.getLogger(__name__)

# --- Step 1: List Folders ---
@Client.on_callback_query(filters.regex("^manage_menu$") & is_admin)
async def list_manage_folders(client, callback_query):
    user_id = callback_query.from_user.id
    await db.set_state(user_id, WAITING_FOLDER_MANAGE)
    
    await safe_edit(callback_query.message, "📂 Loading folders...")
    
    folders = await drive_service.get_folders_cached(db)
    if not folders:
        await safe_edit(callback_query.message, "❌ No folders found.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Back", callback_data="main_menu", style=ButtonStyle.PRIMARY)]]))
        return

    # Sort folders by name and numeric range
    folders = sort_folders(folders)
    await db.set_state(user_id, WAITING_FOLDER_MANAGE, {"folders": folders})
    
    keyboard = create_pagination_keyboard(
        items=folders,
        page=1,
        per_page=20,
        callback_prefix="manage_folder_page",
        item_callback_func=lambda f: (f['name'], f"man_folder_{f['id']}"),
        back_callback_data="main_menu",
        refresh_callback_data="manage_refresh"
    )
    
    await safe_edit(callback_query.message, 
        "📂 **Select a Folder to Manage**:",
        reply_markup=keyboard
    )

@Client.on_callback_query(filters.regex(r"^manage_folder_page_(\d+)$") & is_admin)
async def manage_folder_pagination(client, callback_query):
    page = int(callback_query.matches[0].group(1))
    user_id = callback_query.from_user.id
    
    state, data = await db.get_state(user_id)
    if state != WAITING_FOLDER_MANAGE or "folders" not in data:
        await callback_query.answer("Session expired.", show_alert=True)
        return

    folders = data["folders"]
    keyboard = create_pagination_keyboard(
        items=folders,
        page=page,
        per_page=20,
        callback_prefix="manage_folder_page",
        item_callback_func=lambda f: (f['name'], f"man_folder_{f['id']}"),
        refresh_callback_data="manage_refresh"
    )
    
    await callback_query.edit_message_reply_markup(reply_markup=keyboard)

# --- Refresh Folders (Manage) ---
@Client.on_callback_query(filters.regex("^manage_refresh$") & is_admin)
async def manage_refresh(client, callback_query):
    user_id = callback_query.from_user.id
    
    await callback_query.answer("🔄 Refreshing folders...")
    await db.clear_folder_cache()
    
    folders = await drive_service.get_folders_cached(db, force_refresh=True)
    if not folders:
        await safe_edit(callback_query, "❌ No folders found.")
        return
    
    folders = sort_folders(folders)
    await db.set_state(user_id, WAITING_FOLDER_MANAGE, {"folders": folders})
    
    keyboard = create_pagination_keyboard(
        items=folders,
        page=1,
        per_page=20,
        callback_prefix="manage_folder_page",
        item_callback_func=lambda f: (f['name'], f"man_folder_{f['id']}"),
        refresh_callback_data="manage_refresh"
    )
    
    await safe_edit(callback_query, 
        "📂 **Select a Folder to Manage** (refreshed):",
        reply_markup=keyboard
    )

# --- Step 2: List Permissions (Users) with expiry info ---
@Client.on_callback_query(filters.regex(r"^man_folder_(.*)$") & is_admin)
async def list_folder_users(client, callback_query):
    folder_id = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id

    state, data = await db.get_state(user_id)
    folder_name = next((f["name"] for f in data.get("folders", []) if f["id"] == folder_id), "Unknown")

    await safe_edit(callback_query.message, f"👥 Fetching users for **{folder_name}**...")

    permissions = await drive_service.get_permissions(folder_id, db)
    users = [p for p in permissions if p.get("role") != "owner"]
    users = sorted(users, key=lambda u: natural_sort_key(u.get("emailAddress", "")))

    if not users:
        await safe_edit(callback_query.message, 
            f"📂 **{folder_name}**\n\nNo users found with access (besides owners).",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="manage_menu", style=ButtonStyle.PRIMARY)]])
        )
        return

    # IMPROVED: Fetch timed grant info to show expiry alongside each user
    active_grants = await db.get_active_grants()
    grant_map = {}
    for g in active_grants:
        if g.get("folder_id") == folder_id:
            grant_map[g["email"].lower()] = g

    viewers = sum(1 for u in users if u.get("role") == "reader")
    editors = sum(1 for u in users if u.get("role") == "writer")

    new_data = {"folder_id": folder_id, "folder_name": folder_name, "users": users}
    await db.set_state(user_id, WAITING_USER_MANAGE, new_data)

    role_icons = {"reader": "👀", "writer": "✏️", "commenter": "💬"}

    def make_user_label(u):
        email = u.get("emailAddress", "No Email")
        role_icon = role_icons.get(u.get("role"), "🔑")
        grant = grant_map.get(email.lower())
        if grant:
            from utils.time import format_time_remaining
            remaining = format_time_remaining(grant["expires_at"])
            label = f"{role_icon} {email} ⏳{remaining}"
        else:
            label = f"{role_icon} {email} ♾️"
        return label, f"man_user_{u.get('id')}"

    keyboard = create_pagination_keyboard(
        items=users, page=1, per_page=15,
        callback_prefix="manage_user_page",
        item_callback_func=make_user_label
    )

    # Add Revoke All in Folder button
    from pyrogram.types import InlineKeyboardButton as IKB
    keyboard.inline_keyboard.append([
        IKB(f"🗑 Revoke All in Folder ({len(users)})", callback_data=f"man_revoke_all_{folder_id}")
    ])
    keyboard.inline_keyboard.append([IKB("⬅️ Back", callback_data="manage_menu")])

    await safe_edit(callback_query.message, 
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
    if state != WAITING_USER_MANAGE: return

    users = data["users"]
    keyboard = create_pagination_keyboard(
        items=users,
        page=page,
        per_page=20,
        callback_prefix="manage_user_page",
        item_callback_func=lambda u: (f"{u.get('displayName', 'User')} ({u.get('emailAddress')})", f"man_user_{u.get('id')}")
    )
    
    await callback_query.edit_message_reply_markup(reply_markup=keyboard)


# --- Step 3: User Actions ---
@Client.on_callback_query(filters.regex(r"^man_user_(.*)$") & is_admin)
async def manage_user_actions(client, callback_query):
    perm_id = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    
    state, data = await db.get_state(user_id)
    user_obj = next((u for u in data["users"] if u["id"] == perm_id), None)
    
    if not user_obj:
        await callback_query.answer("User not found.", show_alert=True)
        return

    # Store selected user
    data["selected_user"] = user_obj
    await db.set_state(user_id, WAITING_ACTION_MANAGE, data)
    
    role = user_obj.get('role', 'unknown')
    email = user_obj.get('emailAddress', 'No Email')
    
    await safe_edit(callback_query.message, 
        f"👤 **User Details**\n\n"
        f"📧 Email: `{email}`\n"
        f"🔑 Role: **{role}**\n"
        f"📂 Folder: `{data['folder_name']}`\n\n"
        "Select Action:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Change Role", callback_data="action_change_role", style=ButtonStyle.PRIMARY),
             InlineKeyboardButton("🗑 Remove Access", callback_data="action_remove_access", style=ButtonStyle.DANGER)],
            [InlineKeyboardButton("⬅️ Back", callback_data="manage_menu", style=ButtonStyle.PRIMARY)]
        ])
    )

# --- Change Role Flow ---
@Client.on_callback_query(filters.regex("^action_change_role$") & is_admin)
async def prompt_change_role(client, callback_query):
    await safe_edit(callback_query.message, 
        "🔑 **Select New Role**:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👀 Viewer", callback_data="set_role_viewer", style=ButtonStyle.PRIMARY),
             InlineKeyboardButton("✏️ Editor", callback_data="set_role_editor", style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("⬅️ Back", callback_data="manage_menu", style=ButtonStyle.PRIMARY)]
        ])
    )

@Client.on_callback_query(filters.regex(r"^set_role_(viewer|editor)$") & is_admin)
async def execute_role_change(client, callback_query):
    new_role = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    
    email = data["selected_user"]["emailAddress"]
    folder_id = data["folder_id"]
    
    await safe_edit(callback_query.message, "⏳ Updating role...")
    drive_service.set_admin_user(user_id)
    success = await drive_service.change_role(folder_id, email, new_role, db)
    
    if success:
         await db.log_action(user_id, callback_query.from_user.first_name, "role_change", 
                             {"email": email, "folder": data["folder_name"], "new_role": new_role})
         await broadcast(client, "role_change", {
             "email": email, 
             "folder_name": data["folder_name"], 
             "new_role": new_role,
             "admin_name": callback_query.from_user.first_name
         })
         await safe_edit(callback_query.message, 
             f"✅ Role updated to **{new_role}** for `{email}`.",
             reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu", style=ButtonStyle.PRIMARY)]])
         )
    else:
         await safe_edit(callback_query.message, "❌ Failed to update role.")

# --- Remove Access Flow ---
@Client.on_callback_query(filters.regex("^action_remove_access$") & is_admin)
async def confirm_remove(client, callback_query):
    await safe_edit(callback_query.message, 
        "⚠️ **Are you sure?**\n"
        "This will revoke access immediately.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🗑 Yes, Remove", callback_data="confirm_remove", style=ButtonStyle.DANGER),
             InlineKeyboardButton("❌ Cancel", callback_data="manage_menu", style=ButtonStyle.DANGER)]
        ])
    )

@Client.on_callback_query(filters.regex("^confirm_remove$") & is_admin)
async def execute_remove(client, callback_query):
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    
    email = data["selected_user"]["emailAddress"]
    folder_id = data["folder_id"]
    
    await safe_edit(callback_query.message, "⏳ Removing access...")
    drive_service.set_admin_user(user_id)
    success = await drive_service.remove_access(folder_id, email, db)
    
    if success:
         await db.log_action(user_id, callback_query.from_user.first_name, "remove", 
                             {"email": email, "folder": data["folder_name"]})
         await broadcast(client, "revoke", {
             "email": email, 
             "folder_name": data["folder_name"], 
             "admin_name": callback_query.from_user.first_name
         })
         removed_at = format_timestamp(time.time())
         await safe_edit(callback_query.message, 
              f"✅ Access removed for `{email}`.\n"
              f"📂 Folder: `{data['folder_name']}`\n"
              f"🕒 Removed at: {removed_at}",
              reply_markup=InlineKeyboardMarkup([
                  [InlineKeyboardButton("📂 Back to Folder", callback_data=f"man_folder_{data['folder_id']}", style=ButtonStyle.PRIMARY)],
                  [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu", style=ButtonStyle.PRIMARY)]
              ])
         )
    else:
         await safe_edit(callback_query.message, 
              "❌ Failed to remove access.",
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu", style=ButtonStyle.PRIMARY)]])
         )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEW: Revoke All in Folder
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_callback_query(filters.regex(r"^man_revoke_all_(.+)$") & is_admin)
async def man_revoke_all_confirm(client, callback_query):
    folder_id = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)

    folder_name = data.get("folder_name", "Unknown")
    users = data.get("users", [])
    # Only revoke non-owners
    targets = [u for u in users if u.get("role") != "owner"]

    await db.set_state(user_id, "CONFIRM_FOLDER_REVOKE_ALL", {
        **data,
        "revoke_targets": targets
    })

    await safe_edit(callback_query, 
        f"⚠️ **Revoke All in Folder**\n\n"
        f"📂 {folder_name}\n"
        f"This will remove access for **{len(targets)} users**.\n\n"
        "Are you sure?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Yes, Revoke All", callback_data="man_revoke_all_execute", style=ButtonStyle.DANGER),
             InlineKeyboardButton("❌ Cancel", callback_data="manage_menu", style=ButtonStyle.DANGER)]
        ])
    )


@Client.on_callback_query(filters.regex("^man_revoke_all_execute$") & is_admin)
async def man_revoke_all_execute(client, callback_query):
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    if state != "CONFIRM_FOLDER_REVOKE_ALL":
        await callback_query.answer("Session expired.", show_alert=True)
        return

    folder_id = data["folder_id"]
    folder_name = data["folder_name"]
    targets = data.get("revoke_targets", [])

    await safe_edit(callback_query, f"⏳ Revoking {len(targets)} users...")

    drive_service.set_admin_user(user_id)
    success_count = 0
    fail_count = 0

    for u in targets:
        email = u.get("emailAddress", "")
        if not email:
            continue
        try:
            ok = await drive_service.remove_access(folder_id, email, db)
            if ok:
                success_count += 1
                # Also revoke from DB timed grants
                active = await db.get_active_grants()
                for g in active:
                    if g["email"].lower() == email.lower() and g["folder_id"] == folder_id:
                        await db.revoke_grant(g["_id"])
            else:
                fail_count += 1
        except Exception as e:
            LOGGER.error(f"Folder revoke all error: {e}")
            fail_count += 1

    await db.log_action(
        admin_id=user_id,
        admin_name=callback_query.from_user.first_name,
        action="bulk_revoke",
        details={"type": "folder_revoke_all", "folder_name": folder_name, "success": success_count, "failed": fail_count}
    )
    await broadcast(client, "bulk_revoke", {
        "type": f"folder_revoke_all ({folder_name})",
        "success": success_count,
        "failed": fail_count,
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
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu", style=ButtonStyle.PRIMARY)]
        ])
    )
    await db.delete_state(user_id)
