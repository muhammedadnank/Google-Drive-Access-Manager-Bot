from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.database import db
from services.drive import drive_service
from services.broadcast import broadcast
from utils.filters import is_admin, check_state
from utils.validators import validate_email
from utils.time import format_duration, format_time_remaining
from utils.states import WAITING_SEARCH_QUERY, WAITING_CONFIRM_REVOKE_ALL
import logging
import time
import re

LOGGER = logging.getLogger(__name__)

# --- Search Entry Points ---
@Client.on_callback_query(filters.regex("^search_user$") & is_admin)
async def search_menu(client, callback_query):
    user_id = callback_query.from_user.id
    # Reset filters
    await db.set_state(user_id, WAITING_SEARCH_QUERY, {"filters": {}})
    
    await callback_query.edit_message_text(
        "🔍 **Search Access**\n\n"
        "Enter **Email** or **Folder Name** to search.\n"
        "Or use **Advanced Filters** for more options.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⚙️ Advanced Filters", callback_data="adv_filters")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ])
    )

@Client.on_message(filters.command("search") & is_admin)
async def search_command(client, message):
    user_id = message.from_user.id
    
    if len(message.command) > 1:
        query = " ".join(message.command[1:])
        await _execute_search(message, user_id, query_text=query)
    else:
        await db.set_state(user_id, WAITING_SEARCH_QUERY, {"filters": {}})
        await message.reply_text(
            "🔍 **Search Access**\n\n"
            "Enter **Email** or **Folder Name**:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⚙️ Advanced Filters", callback_data="adv_filters")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
            ])
        )

@Client.on_message(check_state(WAITING_SEARCH_QUERY) & filters.text & is_admin)
async def handle_search_input(client, message):
    user_id = message.from_user.id
    query = message.text.strip()
    await _execute_search(message, user_id, query_text=query)


# --- Search Execution ---
async def _execute_search(message_or_callback, user_id, query_text=None, page=1):
    # Get state to retrieve filters
    state, data = await db.get_state(user_id)
    filters_dict = data.get("filters", {}) if data else {}
    
    # Build MongoDB Query
    db_query = {}
    
    # 1. Text Search (Email or Folder)
    if query_text:
        # Save query text for pagination
        data["query_text"] = query_text
        await db.set_state(user_id, WAITING_SEARCH_QUERY, data)
        
        regex = {"$regex": re.escape(query_text), "$options": "i"}
        db_query["$or"] = [
            {"email": regex},
            {"folder_name": regex}
        ]
    elif data.get("query_text"):
        # Restore from state if paginating
        query_text = data["query_text"]
        regex = {"$regex": re.escape(query_text), "$options": "i"}
        db_query["$or"] = [
            {"email": regex},
            {"folder_name": regex}
        ]
        
    # 2. Apply Filters
    if filters_dict.get("role"):
        db_query["role"] = filters_dict["role"]
        
    if filters_dict.get("status"):
        if filters_dict["status"] == "active":
             db_query["status"] = "active"
             db_query["expires_at"] = {"$gt": time.time()}
        elif filters_dict["status"] == "expired":
             # Expired can mean status='expired' OR status='active' but time passed
             db_query["$or"] = [
                 {"status": "expired"},
                 {"status": "active", "expires_at": {"$lte": time.time()}}
             ]
        elif filters_dict["status"] == "revoked":
             db_query["status"] = "revoked"

    # Handle UI response
    if hasattr(message_or_callback, 'edit_message_text'):
        reply_func = message_or_callback.edit_message_text
    else:
        reply_func = message_or_callback.reply_text
        
    # Execute DB Search
    results, total = await db.search_grants(db_query, limit=10, skip=(page-1)*10)
    
    if not results:
        text = "🔍 **No results found.**\n\nTry running **Bulk Import** if results are missing."
        await reply_func(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⚙️ Filters", callback_data="adv_filters"),
                 InlineKeyboardButton("🔄 Search Again", callback_data="search_user")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
            ])
        )
        return

    # Display Results
    text = f"🔍 **Search Results** ({total})\n"
    if query_text:
        text += f"Query: `{query_text}`\n"
    if filters_dict:
        filters_str = ", ".join(f"{k}={v}" for k,v in filters_dict.items() if v)
        text += f"Filters: `{filters_str}`\n"
    text += "\n"
    
    for g in results:
        expiry = "♾️"
        if g.get('expires_at'):
             expiry = format_time_remaining(g['expires_at']) if g.get('status') == 'active' else g.get('status').upper()
             
        text += (
            f"📂 `{g.get('folder_name', 'Unknown')}`\n"
            f"👤 `{g['email']}`\n"
            f"🔑 {g.get('role', 'viewer')} | ⏳ {expiry}\n\n"
        )
        
    # Buttons
    buttons = []
    
    # Pagination
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"search_page_{page-1}"))
    if (page * 10) < total:
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"search_page_{page+1}"))
    if nav:
        buttons.append(nav)
        
    # Actions (only if searching by specific email)
    # Check if query looks like email
    if query_text and validate_email(query_text):
        buttons.append([InlineKeyboardButton("🗑 Revoke All for User", callback_data="revoke_all_confirm")])
        # Save results for revoke action
        data["grants"] = results # Only current page, but revoke_all logic handles it?
        # Actually revoke_all needs ALL grants. 
        # The V1 revoke_all logic used 'grants' from state.
        # We should query DB again for ALL grants if they click revoke.
        await db.set_state(user_id, WAITING_SEARCH_QUERY, data)

    buttons.append([InlineKeyboardButton("⚙️ Filters", callback_data="adv_filters")])
    buttons.append([InlineKeyboardButton("🔍 New Search", callback_data="search_user")])
    buttons.append([InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")])
    
    await reply_func(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex(r"^search_page_(\d+)$") & is_admin)
async def search_pagination(client, callback_query):
    page = int(callback_query.matches[0].group(1))
    user_id = callback_query.from_user.id
    
    # We rely on stored state for query/filters
    await _execute_search(callback_query, user_id, page=page)


# --- Filter Menu ---
@Client.on_callback_query(filters.regex("^adv_filters$") & is_admin)
async def adjust_filters(client, callback_query):
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    current_filters = data.get("filters", {}) if data else {}
    
    def icon(k, v):
        return "✅" if current_filters.get(k) == v else "☐"
        
    text = (
        "⚙️ **Advanced Filters**\n\n"
        "Configure your search criteria:"
    )
    
    keyboard = [
        [InlineKeyboardButton("--- Role ---", callback_data="noop")],
        [InlineKeyboardButton(f"{icon('role', 'reader')} Reader", callback_data="filter_role_reader"),
         InlineKeyboardButton(f"{icon('role', 'writer')} Writer", callback_data="filter_role_writer")],
         
        [InlineKeyboardButton("--- Status ---", callback_data="noop")],
        [InlineKeyboardButton(f"{icon('status', 'active')} Active", callback_data="filter_status_active"),
         InlineKeyboardButton(f"{icon('status', 'expired')} Expired", callback_data="filter_status_expired"),
         InlineKeyboardButton(f"{icon('status', 'revoked')} Revoked", callback_data="filter_status_revoked")],
         
        [InlineKeyboardButton("🗑 Clear Filters", callback_data="filter_clear")],
        [InlineKeyboardButton("🔍 Apply & Search", callback_data="filter_apply")]
    ]
    
    await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


@Client.on_callback_query(filters.regex(r"^filter_(role|status)_(.+)$") & is_admin)
async def toggle_filter(client, callback_query):
    category = callback_query.matches[0].group(1)
    value = callback_query.matches[0].group(2)
    user_id = callback_query.from_user.id
    
    state, data = await db.get_state(user_id)
    if not data: data = {}
    filters_dict = data.get("filters", {})
    
    # Toggle logic: if already set, unset. Else set.
    if filters_dict.get(category) == value:
        filters_dict.pop(category, None)
    else:
        filters_dict[category] = value
        
    data["filters"] = filters_dict
    await db.set_state(user_id, WAITING_SEARCH_QUERY, data)
    
    await adjust_filters(client, callback_query)


@Client.on_callback_query(filters.regex("^filter_clear$") & is_admin)
async def clear_filters(client, callback_query):
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    if data:
        data["filters"] = {}
        await db.set_state(user_id, state, data)
    await adjust_filters(client, callback_query)


@Client.on_callback_query(filters.regex("^filter_apply$") & is_admin)
async def apply_filters(client, callback_query):
    user_id = callback_query.from_user.id
    await _execute_search(callback_query, user_id, page=1)


# --- Revoke All Logic (Adapted) ---
@Client.on_callback_query(filters.regex("^revoke_all_confirm$") & is_admin)
async def revoke_all_confirm(client, callback_query):
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    
    query_text = data.get("query_text")
    if not query_text or not validate_email(query_text):
        await callback_query.answer("Can only revoke all by specific Email search.", show_alert=True)
        return

    # Fetch ALL active grants for this email to confirm count
    grants_cursor = db.grants.find({"email": query_text, "status": "active"})
    targets = [g async for g in grants_cursor]
    
    if not targets:
        await callback_query.answer("No active grants to revoke.", show_alert=True)
        return

    await db.set_state(user_id, WAITING_CONFIRM_REVOKE_ALL, {
        "email": query_text,
        "targets": [{**g, "_id": str(g["_id"])} for g in targets]
    })
    
    await callback_query.edit_message_text(
        "⚠️ **Revoke All Access**\n\n"
        f"User: `{query_text}`\n"
        f"This will remove access from **{len(targets)} folders**.\n\n"
        "Are you sure?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Yes, Revoke All", callback_data="revoke_all_execute")],
            [InlineKeyboardButton("❌ Cancel", callback_data="search_user")]
        ])
    )

@Client.on_callback_query(filters.regex("^revoke_all_execute$") & is_admin)
async def revoke_all_execute(client, callback_query):
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    
    if state != WAITING_CONFIRM_REVOKE_ALL:
        await callback_query.answer("Session expired.", show_alert=True)
        return
    
    email = data['email']
    targets = data['targets']
    
    await callback_query.edit_message_text(f"⏳ Revoking access from {len(targets)} folders...")
    
    success_count = 0
    results = []
    
    for grant in targets:
        try:
            # Revoke from Drive
            ok = await drive_service.remove_access(grant['folder_id'], email)
            if ok:
                success_count += 1
                # Mark DB as revoked
                await db.revoke_grant(grant["_id"])
                results.append(f"✅ {grant['folder_name']}")
            else:
                results.append(f"❌ {grant['folder_name']} (failed)")
        except Exception as e:
            LOGGER.error(f"Revoke all error: {e}")
            results.append(f"❌ {grant['folder_name']} (error)")
            
    # Log & Broadcast
    await db.log_action(
        admin_id=user_id, 
        admin_name=callback_query.from_user.first_name,
        action="revoke_all",
        details={"email": email, "folders_removed": success_count, "total_attempted": len(targets)}
    )
    
    await broadcast(client, "bulk_revoke", {
        "type": "revoke_all_user",
        "email": email,
        "success": success_count,
        "failed": len(targets) - success_count,
        "admin_name": callback_query.from_user.first_name
    })
    
    result_text = "\n".join(results[:10])
    if len(results) > 10:
        result_text += f"\n... +{len(results)-10} more"
        
    await callback_query.edit_message_text(
        "✅ **All Access Revoked**\n\n"
        f"`{email}` has been removed from:\n"
        f"{result_text}\n\n"
        f"**{success_count}/{len(targets)}** removed successfully.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 Search Another", callback_data="search_user")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ])
    )
