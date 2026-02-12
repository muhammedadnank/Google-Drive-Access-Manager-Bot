from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.database import db
from services.drive import drive_service
from utils.states import (
    WAITING_FOLDER_MANAGE, WAITING_USER_MANAGE, WAITING_ACTION_MANAGE
)
from utils.pagination import create_pagination_keyboard, sort_folders
import logging
import time
from services.broadcast import broadcast

LOGGER = logging.getLogger(__name__)

# --- Step 1: List Folders ---
@Client.on_callback_query(filters.regex("^manage_menu$"))
async def list_manage_folders(client, callback_query):
    user_id = callback_query.from_user.id
    await db.set_state(user_id, WAITING_FOLDER_MANAGE)
    
    await callback_query.message.edit_text("📂 Loading folders...")
    
    folders = await drive_service.get_folders_cached(db)
    if not folders:
        await callback_query.message.edit_text("❌ No folders found.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Back", callback_data="main_menu")]]))
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
    
    await callback_query.message.edit_text(
        "📂 **Select a Folder to Manage**:",
        reply_markup=keyboard
    )

@Client.on_callback_query(filters.regex(r"^manage_folder_page_(\d+)$"))
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
@Client.on_callback_query(filters.regex("^manage_refresh$"))
async def manage_refresh(client, callback_query):
    user_id = callback_query.from_user.id
    
    await callback_query.answer("🔄 Refreshing folders...")
    await db.clear_folder_cache()
    
    folders = await drive_service.get_folders_cached(db, force_refresh=True)
    if not folders:
        await callback_query.edit_message_text("❌ No folders found.")
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
    
    await callback_query.edit_message_text(
        "📂 **Select a Folder to Manage** (refreshed):",
        reply_markup=keyboard
    )

# --- Step 2: List Permissions (Users) ---
@Client.on_callback_query(filters.regex(r"^man_folder_(.*)$"))
async def list_folder_users(client, callback_query):
    folder_id = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    
    state, data = await db.get_state(user_id)
    folder_name = next((f['name'] for f in data.get("folders", []) if f['id'] == folder_id), "Unknown")
    
    await callback_query.message.edit_text(f"👥 Fetching users for **{folder_name}**...")
    
    permissions = await drive_service.get_permissions(folder_id)
    # Filter out 'owner' usually, just show user/group
    users = [p for p in permissions if p.get('role') != 'owner']
    
    if not users:
         await callback_query.message.edit_text(
             f"📂 **{folder_name}**\n\nNo users found with access (besides owners).",
             reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="manage_menu")]])
         )
         return

    # Count by role
    viewers = sum(1 for u in users if u.get('role') == 'reader')
    editors = sum(1 for u in users if u.get('role') == 'writer')

    # Update state
    new_data = {"folder_id": folder_id, "folder_name": folder_name, "users": users}
    await db.set_state(user_id, WAITING_USER_MANAGE, new_data)
    
    role_icons = {'reader': '👀', 'writer': '✏️', 'commenter': '💬'}
    keyboard = create_pagination_keyboard(
        items=users,
        page=1,
        per_page=20,
        callback_prefix="manage_user_page",
        item_callback_func=lambda u: (
            f"{role_icons.get(u.get('role'), '🔑')} {u.get('emailAddress', 'No Email')}",
            f"man_user_{u.get('id')}"
        )
    )
    
    await callback_query.message.edit_text(
        f"📂 **{folder_name}**\n"
        f"👥 {len(users)} users | 👀 {viewers} viewers | ✏️ {editors} editors\n\n"
        "Select a user to manage:",
        reply_markup=keyboard
    )

@Client.on_callback_query(filters.regex(r"^manage_user_page_(\d+)$"))
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
@Client.on_callback_query(filters.regex(r"^man_user_(.*)$"))
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
    
    await callback_query.message.edit_text(
        f"👤 **User Details**\n\n"
        f"📧 Email: `{email}`\n"
        f"🔑 Role: **{role}**\n"
        f"📂 Folder: `{data['folder_name']}`\n\n"
        "Select Action:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Change Role", callback_data="action_change_role"),
             InlineKeyboardButton("🗑 Remove Access", callback_data="action_remove_access")],
            [InlineKeyboardButton("⬅️ Back", callback_data="manage_menu")]
        ])
    )

# --- Change Role Flow ---
@Client.on_callback_query(filters.regex("^action_change_role$"))
async def prompt_change_role(client, callback_query):
    await callback_query.message.edit_text(
        "🔑 **Select New Role**:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👀 Viewer", callback_data="set_role_viewer"),
             InlineKeyboardButton("✏️ Editor", callback_data="set_role_editor")],
            [InlineKeyboardButton("⬅️ Back", callback_data="manage_menu")]
        ])
    )

@Client.on_callback_query(filters.regex(r"^set_role_(viewer|editor)$"))
async def execute_role_change(client, callback_query):
    new_role = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    
    email = data["selected_user"]["emailAddress"]
    folder_id = data["folder_id"]
    
    await callback_query.message.edit_text("⏳ Updating role...")
    
    success = await drive_service.change_role(folder_id, email, new_role)
    
    if success:
         await db.log_action(user_id, callback_query.from_user.first_name, "role_change", 
                             {"email": email, "folder": data["folder_name"], "new_role": new_role})
         await broadcast(client, "role_change", {
             "email": email, 
             "folder_name": data["folder_name"], 
             "new_role": new_role,
             "admin_name": callback_query.from_user.first_name
         })
         await callback_query.message.edit_text(
             f"✅ Role updated to **{new_role}** for `{email}`.",
             reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]])
         )
    else:
         await callback_query.message.edit_text("❌ Failed to update role.")

# --- Remove Access Flow ---
@Client.on_callback_query(filters.regex("^action_remove_access$"))
async def confirm_remove(client, callback_query):
    await callback_query.message.edit_text(
        "⚠️ **Are you sure?**\n"
        "This will revoke access immediately.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🗑 Yes, Remove", callback_data="confirm_remove"),
             InlineKeyboardButton("❌ Cancel", callback_data="manage_menu")]
        ])
    )

@Client.on_callback_query(filters.regex("^confirm_remove$"))
async def execute_remove(client, callback_query):
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    
    email = data["selected_user"]["emailAddress"]
    folder_id = data["folder_id"]
    
    await callback_query.message.edit_text("⏳ Removing access...")
    
    success = await drive_service.remove_access(folder_id, email)
    
    if success:
         await db.log_action(user_id, callback_query.from_user.first_name, "remove", 
                             {"email": email, "folder": data["folder_name"]})
         await broadcast(client, "revoke", {
             "email": email, 
             "folder_name": data["folder_name"], 
             "admin_name": callback_query.from_user.first_name
         })
         removed_at = time.strftime('%d %b %Y, %H:%M', time.localtime(time.time()))
         await callback_query.message.edit_text(
              f"✅ Access removed for `{email}`.\n"
              f"📂 Folder: `{data['folder_name']}`\n"
              f"🕒 Removed at: {removed_at}",
              reply_markup=InlineKeyboardMarkup([
                  [InlineKeyboardButton("📂 Back to Folder", callback_data=f"man_folder_{data['folder_id']}")],
                  [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
              ])
         )
    else:
         await callback_query.message.edit_text(
              "❌ Failed to remove access.",
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]])
         )
