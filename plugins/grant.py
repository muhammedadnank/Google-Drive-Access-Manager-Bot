from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.database import db
from services.drive import drive_service
from utils.states import (
    WAITING_EMAIL_GRANT, WAITING_FOLDER_GRANT,
    WAITING_ROLE_GRANT, WAITING_CONFIRM_GRANT
)
from utils.filters import check_state
from utils.validators import validate_email
from utils.pagination import create_pagination_keyboard
import logging

LOGGER = logging.getLogger(__name__)

# --- Step 1: Request Email ---
@Client.on_callback_query(filters.regex("^grant_menu$"))
async def start_grant_flow(client, callback_query):
    user_id = callback_query.from_user.id
    await db.set_state(user_id, WAITING_EMAIL_GRANT)
    
    await callback_query.message.edit_text(
        "📧 **Enter User Email**\n\n"
        "Please send the email address you want to grant access to.\n"
        "Or /cancel to abort.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_flow")]
        ])
    )

# --- Step 2: Receive Email & Show Folders ---
@Client.on_message(check_state(WAITING_EMAIL_GRANT) & filters.text)
async def receive_email(client, message):
    email = message.text.strip()
    if not validate_email(email):
        await message.reply_text("❌ Invalid email format. Please try again.")
        return

    user_id = message.from_user.id
    
    # Store email and fetch folders
    await db.set_state(user_id, WAITING_FOLDER_GRANT, {"email": email})
    
    msg = await message.reply_text("📂 Fetching folders from Google Drive...")
    
    folders = await drive_service.list_folders()
    if not folders:
        await msg.edit_text("❌ No folders found or error connecting to Drive API.")
        await db.delete_state(user_id)
        return

    # Store folders temporarily in state data for easy pagination without re-fetching?
    # For large lists, fetching again might be better, but let's cache in state for now.
    # Actually, let's keep it simple: fetch and paginate.
    # Storing 100 folders in state might be heavy for Mongo if huge.
    # Better to fetch page-wise? API supports tokens.
    # For this implementation, let's assume <100 folders and store in state for simplicity.
    
    await db.set_state(user_id, WAITING_FOLDER_GRANT, {"email": email, "folders": folders})
    
    keyboard = create_pagination_keyboard(
        items=folders,
        page=1,
        per_page=20,
        callback_prefix="grant_folder_page",
        item_callback_func=lambda f: (f['name'], f"sel_folder_{f['id']}")
    )
    
    await msg.edit_text(
        f"📧 User: `{email}`\n\n"
        "📂 **Select a Folder**:",
        reply_markup=keyboard
    )

# --- Pagination Handler for Folders ---
@Client.on_callback_query(filters.regex(r"^grant_folder_page_(\d+)$"))
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
        item_callback_func=lambda f: (f['name'], f"sel_folder_{f['id']}")
    )
    
    try:
        await callback_query.edit_message_reply_markup(reply_markup=keyboard)
    except:
        pass # Message not modified

# --- Step 3: Select Role ---
@Client.on_callback_query(filters.regex(r"^sel_folder_(.*)$"))
async def select_folder(client, callback_query):
    folder_id = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    
    state, data = await db.get_state(user_id)
    if state != WAITING_FOLDER_GRANT:
        await callback_query.answer("Invalid state.", show_alert=True)
        return

    # Find folder name
    folder_name = next((f['name'] for f in data.get("folders", []) if f['id'] == folder_id), "Unknown")
    
    # Update state
    new_data = {"email": data["email"], "folder_id": folder_id, "folder_name": folder_name}
    await db.set_state(user_id, WAITING_ROLE_GRANT, new_data)
    
    await callback_query.edit_message_text(
        f"📧 User: `{data['email']}`\n"
        f"📂 Folder: **{folder_name}**\n\n"
        "🔑 **Select Access Level**:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👀 Viewer", callback_data="role_viewer"),
             InlineKeyboardButton("✏️ Editor", callback_data="role_editor")],
            [InlineKeyboardButton("⬅️ Back", callback_data="grant_menu")]
        ])
    )

# --- Step 4: Confirm ---
@Client.on_callback_query(filters.regex(r"^role_(viewer|editor)$"))
async def select_role(client, callback_query):
    role = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    
    state, data = await db.get_state(user_id)
    if state != WAITING_ROLE_GRANT: return

    data["role"] = role
    await db.set_state(user_id, WAITING_CONFIRM_GRANT, data)
    
    await callback_query.edit_message_text(
        "⚠️ **Confirm Access Grant**\n\n"
        f"📧 User: `{data['email']}`\n"
        f"📂 Folder: `{data['folder_name']}`\n"
        f"🔑 Role: **{role.capitalize()}**\n\n"
        "Is this correct?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Confirm", callback_data="grant_confirm"),
             InlineKeyboardButton("❌ Cancel", callback_data="cancel_flow")]
        ])
    )

# --- Step 5: Execute ---
@Client.on_callback_query(filters.regex("^grant_confirm$"))
async def execute_grant(client, callback_query):
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    
    if state != WAITING_CONFIRM_GRANT: return

    await callback_query.edit_message_text("⏳ Processing request...")
    
    success = await drive_service.grant_access(data["folder_id"], data["email"], data["role"])
    
    if success:
        # Log action
        await db.log_action(
            admin_id=user_id,
            admin_name=callback_query.from_user.first_name,
            action="grant_access",
            details=data
        )
        
        await callback_query.edit_message_text(
            "✅ **Access Granted Successfully!**\n\n"
            f"User: `{data['email']}`\n"
            f"Folder: `{data['folder_name']}`\n"
            f"Role: {data['role'].capitalize()}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]])
        )
    else:
        await callback_query.edit_message_text(
            "❌ **Failed to grant access.**\nCheck logs or credentials.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]])
        )
    
    await db.delete_state(user_id)

@Client.on_callback_query(filters.regex("^cancel_flow$"))
async def cancel_flow(client, callback_query):
    await db.delete_state(callback_query.from_user.id)
    await callback_query.answer("Cancelled.")
    await callback_query.message.edit_text("🚫 Operation Cancelled.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]]))
