from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.database import db
from services.drive import drive_service
from utils.filters import is_admin, check_state
from utils.validators import validate_email
from utils.time import format_duration
import logging
import time
from services.broadcast import broadcast

LOGGER = logging.getLogger(__name__)

# State constants
WAITING_SEARCH_EMAIL = "WAITING_SEARCH_EMAIL"
WAITING_CONFIRM_REVOKE_ALL = "WAITING_CONFIRM_REVOKE_ALL"

# --- Main Menu Button ---
# (Added in start.py, this plugin handles the callback)

@Client.on_callback_query(filters.regex("^search_user$"))
async def search_user_start(client, callback_query):
    user_id = callback_query.from_user.id
    await db.set_state(user_id, WAITING_SEARCH_EMAIL)
    
    await callback_query.edit_message_text(
        "🔍 **Search User Access**\n\n"
        "Enter an email address to see\n"
        "all their active folder permissions:\n\n"
        "Or /cancel to go back.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Back", callback_data="main_menu")]
        ])
    )

@Client.on_message(filters.command("search") & is_admin)
async def search_command(client, message):
    user_id = message.from_user.id
    
    # Check if email is provided in command
    if len(message.command) > 1:
        email = message.command[1]
        await _perform_search(message, user_id, email)
    else:
        await db.set_state(user_id, WAITING_SEARCH_EMAIL)
        await message.reply_text(
            "🔍 **Search User Access**\n\n"
            "Enter an email address to see active permissions:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
            ])
        )

@Client.on_message(check_state(WAITING_SEARCH_EMAIL) & filters.text)
async def receive_search_email(client, message):
    user_id = message.from_user.id
    email = message.text.strip()
    await _perform_search(message, user_id, email)

async def _perform_search(message_or_callback, user_id, email):
    """Execute the search logic."""
    if not validate_email(email):
        text = "❌ Invalid email format. Please try again."
        if hasattr(message_or_callback, 'edit_message_text'):
             await message_or_callback.edit_message_text(text)
        else:
             await message_or_callback.reply_text(text)
        return

    # Handle message vs callback
    if hasattr(message_or_callback, 'edit_message_text'):
        send_func = message_or_callback.edit_message_text
        msg_obj = message_or_callback.message if hasattr(message_or_callback, 'message') else message_or_callback
    else:
        send_func = message_or_callback.reply_text
        msg_obj = message_or_callback

    status_msg = await msg_obj.reply_text(f"🔍 Searching grants for `{email}`...\n⏳ Scanning checkfolders...")
    
    # 1. Get all folders
    folders = await drive_service.get_folders_cached(db)
    if not folders:
        await status_msg.edit_text("❌ No folders found to search.")
        return

    found_grants = []
    
    # 2. Iterate and check permissions
    # Note: optimizing this by checking our DB grants first might be faster for timed grants,
    # but for accuracy we should check actual Drive permissions or at least our cache.
    # Since get_permissions is an API call, doing it for ALL folders is slow.
    # PROPOSAL: Use db.grants for timed ones, but for permanent ones we might miss them if not tracking.
    # V2.0 Guide implies a "Search by Email" that finds ALL access.
    # To be accurate without hitting API 100 times, we rely on `bulk_import` logic or just do it live.
    # For now, let's try live scan of all folders. If slow, we can optimize later.
    
    count = 0
    total = len(folders)
    
    for folder in folders:
        count += 1
        if count % 10 == 0:
            try:
                await status_msg.edit_text(f"🔍 Searching... ({count}/{total})")
            except:
                pass
                
        perms = await drive_service.get_permissions(folder['id'])
        user_perm = next((p for p in perms if p.get('emailAddress', '').lower() == email.lower()), None)
        
        if user_perm:
            # Check if it has a timed grant entry
            timed_grant = await db.grants.find_one({
                "email": email.lower(),
                "folder_id": folder['id'],
                "status": "active"
            })
            
            expiry_text = "♾️ Permanent"
            if timed_grant:
                remaining = timed_grant['expires_at'] - time.time()
                if remaining > 0:
                    days = int(remaining // 86400)
                    expiry_date = time.strftime('%d %b %Y', time.localtime(timed_grant['expires_at']))
                    expiry_text = f"⏳ {days}d ({expiry_date})"
                else:
                    expiry_text = "⏰ Expired"
            
            found_grants.append({
                "folder_name": folder['name'],
                "folder_id": folder['id'],
                "role": user_perm.get('role'),
                "expiry": expiry_text
            })

    if not found_grants:
        await status_msg.edit_text(
            f"🔍 Results for: `{email}`\n\n"
            "❌ No active access found.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Search Another", callback_data="search_user")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
            ])
        )
        return

    # Save results to state for Revoke All
    await db.set_state(user_id, "VIEWING_SEARCH_RESULTS", {
        "email": email,
        "grants": found_grants
    })
    
    # Format output
    text = f"🔍 Results for: `{email}`\n"
    text += f"📊 **{len(found_grants)} active grant(s) found:**\n\n"
    
    for i, grant in enumerate(found_grants, 1):
        text += (
            f"{i}. 📂 `{grant['folder_name']}`\n"
            f"   🔑 {grant['role']} | {grant['expiry']}\n\n"
        )
    
    await status_msg.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🗑 Revoke All for this User", callback_data="revoke_all_confirm")],
            [InlineKeyboardButton("🔄 Search Another", callback_data="search_user")],
            [InlineKeyboardButton("🏠 Back", callback_data="main_menu")]
        ])
    )

@Client.on_callback_query(filters.regex("^revoke_all_confirm$"))
async def revoke_all_confirm(client, callback_query):
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    
    if state != "VIEWING_SEARCH_RESULTS":
        await callback_query.answer("Session expired.", show_alert=True)
        return
        
    email = data['email']
    count = len(data['grants'])
    
    await db.set_state(user_id, WAITING_CONFIRM_REVOKE_ALL, data)
    
    await callback_query.edit_message_text(
        "⚠️ **Revoke All Access**\n\n"
        f"User: `{email}`\n"
        f"This will remove access from **{count} folders**.\n\n"
        "Are you sure?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Yes, Revoke All", callback_data="revoke_all_execute")],
            [InlineKeyboardButton("❌ Cancel", callback_data="search_user")]
        ])
    )

@Client.on_callback_query(filters.regex("^revoke_all_execute$"))
async def revoke_all_execute(client, callback_query):
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    
    if state != WAITING_CONFIRM_REVOKE_ALL:
        await callback_query.answer("Session expired.", show_alert=True)
        return
    
    email = data['email']
    grants = data['grants']
    
    await callback_query.edit_message_text(f"⏳ Revoking access from {len(grants)} folders...")
    
    success_count = 0
    results = []
    
    for grant in grants:
        try:
            # Revoke from Drive
            ok = await drive_service.remove_access(grant['folder_id'], email)
            if ok:
                success_count += 1
                results.append(f"✅ {grant['folder_name']}")
                
                # Also remove from DB grants if exists
                await db.grants.update_many(
                    {"email": email.lower(), "folder_id": grant['folder_id']},
                    {"$set": {"status": "revoked", "revoked_at": time.time()}}
                )
            else:
                results.append(f"❌ {grant['folder_name']} (failed)")
        except Exception as e:
            LOGGER.error(f"Revoke all error: {e}")
            results.append(f"❌ {grant['folder_name']} (error)")
            
    await db.log_action(
        admin_id=user_id, 
        admin_name=callback_query.from_user.first_name,
        action="revoke_all",
        details={"email": email, "folders_removed": success_count, "total_attempted": len(grants)}
    )
    await broadcast(client, "bulk_revoke", {
        "type": "revoke_all_user",
        "email": email,
        "success": success_count,
        "failed": len(grants) - success_count,
        "admin_name": callback_query.from_user.first_name
    })
    
    result_text = "\n".join(results[:10])
    if len(results) > 10:
        result_text += f"\n... +{len(results)-10} more"
        
    await callback_query.edit_message_text(
        "✅ **All Access Revoked**\n\n"
        f"`{email}` has been removed from:\n"
        f"{result_text}\n\n"
        f"**{success_count}/{len(grants)}** removed successfully.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 Search Another", callback_data="search_user")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ])
    )
