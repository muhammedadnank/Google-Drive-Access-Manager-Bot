from pyrogram.enums import ButtonStyle
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.database import db
from services.drive import drive_service
from services.broadcast import broadcast
from utils.filters import is_admin, check_state
from utils.validators import validate_email
from utils.pagination import sort_grants
from utils.time import safe_edit, format_duration, format_time_remaining, format_date
from utils.states import WAITING_SEARCH_QUERY, WAITING_CONFIRM_REVOKE_ALL, WAITING_SELECT_REVOKE
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
    
    await safe_edit(callback_query, 
        "🔍 **Search Access**\n\n"
        "Enter **Email** or **Folder Name** to search.\n"
        "Or use **Advanced Filters** for more options.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⚙️ Advanced Filters", callback_data="adv_filters", style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu", style=ButtonStyle.PRIMARY)]
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
                [InlineKeyboardButton("⚙️ Advanced Filters", callback_data="adv_filters", style=ButtonStyle.PRIMARY)],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu", style=ButtonStyle.PRIMARY)]
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
    results = sort_grants(results, key="folder_name")
    
    if not results:
        text = "🔍 **No results found.**\n\nTry running **Bulk Import** if results are missing."
        await reply_func(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⚙️ Filters", callback_data="adv_filters", style=ButtonStyle.PRIMARY),
                 InlineKeyboardButton("🔄 Search Again", callback_data="search_user", style=ButtonStyle.PRIMARY)],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu", style=ButtonStyle.PRIMARY)]
            ])
        )
        return

    # Display Results
    is_email_search = query_text and validate_email(query_text)
    
    if is_email_search:
        text = f"🔍 **Access Report**\n👤 `{query_text}`\n📊 {total} grant(s) found\n\n"
    else:
        text = f"🔍 **Search Results** ({total})\n"
        if query_text:
            text += f"Query: `{query_text}`\n"
    if filters_dict:
        filters_str = ", ".join(f"{k}={v}" for k,v in filters_dict.items() if v)
        text += f"Filters: `{filters_str}`\n"
    text += "\n"
    
    for g in results:
        status = g.get('status', 'active')
        expires_at = g.get('expires_at')
        
        if not expires_at:
            expiry_line = "⏳ ♾️ Permanent"
        elif status != 'active':
            expiry_line = f"⏳ {status.upper()}"
        else:
            remaining = format_time_remaining(expires_at)
            expiry_date = format_date(expires_at)
            expiry_line = f"📅 {expiry_date} ({remaining} left)"
            
        text += (
            f"📂 `{g.get('folder_name', 'Unknown')}`\n"
            f"🔑 {g.get('role', 'viewer').capitalize()} | {expiry_line}\n\n"
        )
        
    # Buttons
    buttons = []
    
    # Pagination
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"search_page_{page-1}", style=ButtonStyle.PRIMARY))
    if (page * 10) < total:
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"search_page_{page+1}", style=ButtonStyle.PRIMARY))
    if nav:
        buttons.append(nav)
        
    # Actions (only if searching by specific email)
    if is_email_search:
        buttons.append([
            InlineKeyboardButton("☑️ Select & Revoke", callback_data="select_revoke_menu", style=ButtonStyle.DANGER),
            InlineKeyboardButton("🗑 Revoke All", callback_data="revoke_all_confirm", style=ButtonStyle.DANGER)
        ])
        data["grants"] = results
        await db.set_state(user_id, WAITING_SEARCH_QUERY, data)

    buttons.append([InlineKeyboardButton("⚙️ Filters", callback_data="adv_filters", style=ButtonStyle.PRIMARY)])
    buttons.append([InlineKeyboardButton("🔍 New Search", callback_data="search_user", style=ButtonStyle.PRIMARY)])
    buttons.append([InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu", style=ButtonStyle.PRIMARY)])
    
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
        [InlineKeyboardButton(f"{icon('role', 'reader')} Reader", callback_data="filter_role_reader", style=ButtonStyle.PRIMARY),
         InlineKeyboardButton(f"{icon('role', 'writer')} Writer", callback_data="filter_role_writer", style=ButtonStyle.PRIMARY)],
         
        [InlineKeyboardButton("--- Status ---", callback_data="noop")],
        [InlineKeyboardButton(f"{icon('status', 'active')} Active", callback_data="filter_status_active", style=ButtonStyle.SUCCESS),
         InlineKeyboardButton(f"{icon('status', 'expired')} Expired", callback_data="filter_status_expired", style=ButtonStyle.DANGER),
         InlineKeyboardButton(f"{icon('status', 'revoked')} Revoked", callback_data="filter_status_revoked", style=ButtonStyle.DANGER)],
         
        [InlineKeyboardButton("🗑 Clear Filters", callback_data="filter_clear", style=ButtonStyle.DANGER)],
        [InlineKeyboardButton("🔍 Apply & Search", callback_data="filter_apply", style=ButtonStyle.SUCCESS)]
    ]
    
    await safe_edit(callback_query, text, reply_markup=InlineKeyboardMarkup(keyboard))


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
    
    await safe_edit(callback_query, 
        "⚠️ **Revoke All Access**\n\n"
        f"User: `{query_text}`\n"
        f"This will remove access from **{len(targets)} folders**.\n\n"
        "Are you sure?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Yes, Revoke All", callback_data="revoke_all_execute", style=ButtonStyle.DANGER)],
            [InlineKeyboardButton("❌ Cancel", callback_data="search_user", style=ButtonStyle.DANGER)]
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
    
    await safe_edit(callback_query, f"⏳ Revoking access from {len(targets)} folders...")
    
    success_count = 0
    results = []
    
    drive_service.set_admin_user(user_id)
    for grant in targets:
        try:
            # Revoke from Drive
            ok = await drive_service.remove_access(grant['folder_id'], email, db)
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
        
    await safe_edit(callback_query, 
        "✅ **All Access Revoked**\n\n"
        f"`{email}` has been removed from:\n"
        f"{result_text}\n\n"
        f"**{success_count}/{len(targets)}** removed successfully.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 Search Another", callback_data="search_user", style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu", style=ButtonStyle.PRIMARY)]
        ])
    )


# ─────────────────────────────────────────────
# ☑️ SELECT & REVOKE — Individual folder select
# ─────────────────────────────────────────────

def _build_select_revoke_keyboard(grants, selected_ids):
    """
    Build checkbox keyboard for grant selection.
    NOW WITH: Select All / Unselect All toggle button!
    """
    keyboard = []
    
    # Individual folder checkboxes
    for g in grants:
        gid = str(g["_id"])
        checked = "✅" if gid in selected_ids else "☐"
        folder = g.get("folder_name", "Unknown")[:28]
        role = g.get("role", "viewer")[0].upper()
        keyboard.append([
            InlineKeyboardButton(
                f"{checked} {folder} [{role}]",
                callback_data=f"sr_toggle_{gid}",
                style=ButtonStyle.PRIMARY
            )
        ])
    
    # Select All / Unselect All button
    all_selected = len(selected_ids) == len(grants) and len(grants) > 0
    
    if all_selected:
        # If all are selected, show "Unselect All"
        keyboard.append([
            InlineKeyboardButton("☐ Unselect All", callback_data="sr_toggle_all", style=ButtonStyle.PRIMARY)
        ])
    else:
        # If not all selected, show "Select All"
        keyboard.append([
            InlineKeyboardButton("✅ Select All", callback_data="sr_toggle_all", style=ButtonStyle.PRIMARY)
        ])
    
    # Action buttons row
    action_row = []
    if selected_ids:
        action_row.append(InlineKeyboardButton(
            f"🗑 Revoke Selected ({len(selected_ids)})",
            callback_data="sr_confirm",
            style=ButtonStyle.DANGER
        ))
    
    if action_row:
        keyboard.append(action_row)
    
    # Cancel button
    keyboard.append([
        InlineKeyboardButton("❌ Cancel", callback_data="search_user", style=ButtonStyle.DANGER)
    ])
    
    return InlineKeyboardMarkup(keyboard)


@Client.on_callback_query(filters.regex("^select_revoke_menu$") & is_admin)
async def select_revoke_menu(client, callback_query):
    """Show checkbox list of all active grants for the searched email."""
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)

    email = data.get("query_text") if data else None
    if not email or not validate_email(email):
        await callback_query.answer("Search by email first.", show_alert=True)
        return

    # Fetch ALL active grants for this email
    grants = [g async for g in db.grants.find({"email": email, "status": "active"})]
    if not grants:
        await callback_query.answer("No active grants found.", show_alert=True)
        return

    # Store in state with empty selection
    await db.set_state(user_id, WAITING_SELECT_REVOKE, {
        "email": email,
        "grants": [{**g, "_id": str(g["_id"])} for g in grants],
        "selected": []
    })

    keyboard = _build_select_revoke_keyboard(grants, set())
    await safe_edit(
        callback_query,
        f"☑️ **Select Folders to Revoke**\n👤 `{email}`\n\n"
        f"Tap to select/deselect. {len(grants)} active grant(s).",
        reply_markup=keyboard
    )


@Client.on_callback_query(filters.regex(r"^sr_toggle_(.+)$") & is_admin)
async def sr_toggle(client, callback_query):
    """Toggle selection of a grant OR toggle all grants."""
    match_text = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)

    if state != WAITING_SELECT_REVOKE or not data:
        await callback_query.answer("Session expired.", show_alert=True)
        return

    grants = data["grants"]
    selected = set(data.get("selected", []))
    
    # Check if it's "Select All" / "Unselect All"
    if match_text == "all":
        # Toggle all
        all_grant_ids = [str(g["_id"]) for g in grants]
        
        if len(selected) == len(grants):
            # All are selected → Unselect all
            selected.clear()
            await callback_query.answer("✅ All unselected", show_alert=False)
        else:
            # Not all selected → Select all
            selected = set(all_grant_ids)
            await callback_query.answer(f"✅ All {len(grants)} selected", show_alert=False)
    else:
        # Toggle individual grant
        gid = match_text
        if gid in selected:
            selected.discard(gid)
        else:
            selected.add(gid)

    # Update state
    data["selected"] = list(selected)
    await db.set_state(user_id, WAITING_SELECT_REVOKE, data)

    # Rebuild keyboard
    keyboard = _build_select_revoke_keyboard(grants, selected)
    email = data["email"]
    
    await safe_edit(
        callback_query,
        f"☑️ **Select Folders to Revoke**\n👤 `{email}`\n\n"
        f"{len(selected)} selected | {len(grants)} total",
        reply_markup=keyboard
    )


@Client.on_callback_query(filters.regex("^sr_confirm$") & is_admin)
async def sr_confirm(client, callback_query):
    """Confirm and show summary before revoking selected."""
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)

    if state != WAITING_SELECT_REVOKE or not data:
        await callback_query.answer("Session expired.", show_alert=True)
        return

    selected_ids = set(data.get("selected", []))
    grants = data["grants"]
    email = data["email"]
    targets = [g for g in grants if g["_id"] in selected_ids]

    if not targets:
        await callback_query.answer("Nothing selected.", show_alert=True)
        return

    folder_list = "\n".join(f"  • {g.get('folder_name', 'Unknown')}" for g in targets)

    await safe_edit(
        callback_query,
        f"⚠️ **Confirm Revoke**\n\n"
        f"👤 `{email}`\n"
        f"Removing access from **{len(targets)}** folder(s):\n\n"
        f"{folder_list}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Yes, Revoke", callback_data="sr_execute", style=ButtonStyle.DANGER)],
            [InlineKeyboardButton("◀️ Back", callback_data="select_revoke_menu", style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("❌ Cancel", callback_data="search_user", style=ButtonStyle.DANGER)]
        ])
    )


@Client.on_callback_query(filters.regex("^sr_execute$") & is_admin)
async def sr_execute(client, callback_query):
    """Execute selective revoke."""
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)

    if state != WAITING_SELECT_REVOKE or not data:
        await callback_query.answer("Session expired.", show_alert=True)
        return

    selected_ids = set(data.get("selected", []))
    grants = data["grants"]
    email = data["email"]
    targets = [g for g in grants if g["_id"] in selected_ids]

    await safe_edit(callback_query, f"⏳ Revoking {len(targets)} folder(s)...")

    drive_service.set_admin_user(user_id)
    success, failed = 0, 0
    result_lines = []

    for g in targets:
        try:
            ok = await drive_service.remove_access(g["folder_id"], email, db)
            if ok:
                await db.revoke_grant(g["_id"])
                result_lines.append(f"✅ {g.get('folder_name', 'Unknown')}")
                success += 1
            else:
                result_lines.append(f"❌ {g.get('folder_name', 'Unknown')} (failed)")
                failed += 1
        except Exception as e:
            LOGGER.error(f"sr_execute error: {e}")
            result_lines.append(f"❌ {g.get('folder_name', 'Unknown')} (error)")
            failed += 1

    await db.log_action(
        admin_id=user_id,
        admin_name=callback_query.from_user.first_name,
        action="revoke",
        details={"email": email, "folders_removed": success, "total_attempted": len(targets)}
    )

    await broadcast(client, "bulk_revoke", {
        "type": "selective_revoke",
        "email": email,
        "success": success,
        "failed": failed,
        "admin_name": callback_query.from_user.first_name
    })

    summary = "\n".join(result_lines[:15])
    if len(result_lines) > 15:
        summary += f"\n... +{len(result_lines)-15} more"

    await safe_edit(
        callback_query,
        f"✅ **Selective Revoke Complete**\n\n"
        f"👤 `{email}`\n\n"
        f"{summary}\n\n"
        f"**{success}/{len(targets)}** removed successfully.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 Search Again", callback_data="search_user", style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu", style=ButtonStyle.PRIMARY)]
        ])
    )
