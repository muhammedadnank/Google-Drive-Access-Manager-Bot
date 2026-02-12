from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.database import db
from services.drive import drive_service
import datetime
import time
import logging

LOGGER = logging.getLogger(__name__)


def format_time_remaining(expires_at):
    """Format remaining time as human-readable string."""
    remaining = expires_at - time.time()
    if remaining <= 0:
        return "⏰ Expired"
    
    hours = int(remaining // 3600)
    minutes = int((remaining % 3600) // 60)
    
    if hours >= 24:
        days = hours // 24
        hours = hours % 24
        return f"{days}d {hours}h"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


# --- Expiry Dashboard ---
@Client.on_callback_query(filters.regex("^expiry_menu$"))
async def expiry_dashboard(client, callback_query):
    grants = await db.get_active_grants()
    
    if not grants:
        await callback_query.edit_message_text(
            "⏰ **Expiry Dashboard**\n\n"
            "No active timed grants.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📥 Bulk Import Existing", callback_data="bulk_import_confirm")],
                [InlineKeyboardButton("🏠 Back", callback_data="main_menu")]
            ])
        )
        return
    
    # Paginate: show first page
    await show_expiry_page(callback_query, grants, 1)


async def show_expiry_page(callback_query, grants, page):
    per_page = 5
    total_pages = (len(grants) + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    current = grants[start:end]
    
    text = f"⏰ **Expiry Dashboard** (Page {page}/{total_pages})\n"
    text += f"📊 {len(grants)} active timed grant(s)\n\n"
    
    keyboard = []
    for grant in current:
        remaining = format_time_remaining(grant["expires_at"])
        grant_id = str(grant["_id"])
        
        text += (
            f"📧 `{grant['email']}`\n"
            f"   📂 {grant['folder_name']} | 🔑 {grant['role']}\n"
            f"   ⏳ {remaining} remaining\n\n"
        )
        
        keyboard.append([
            InlineKeyboardButton(f"🔄 Extend {grant['email'][:15]}", callback_data=f"ext_{grant_id[:20]}"),
            InlineKeyboardButton(f"🗑 Revoke", callback_data=f"rev_{grant_id[:20]}")
        ])
    
    # Pagination
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"expiry_page_{page-1}"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"expiry_page_{page+1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([
        InlineKeyboardButton("📥 Bulk Import", callback_data="bulk_import_confirm"),
        InlineKeyboardButton("🏠 Back", callback_data="main_menu")
    ])
    
    # Store grants in state for pagination/action
    await db.set_state(callback_query.from_user.id, "VIEWING_EXPIRY", {
        "grants": [{**g, "_id": str(g["_id"])} for g in grants]
    })
    
    await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


@Client.on_callback_query(filters.regex(r"^expiry_page_(\d+)$"))
async def expiry_pagination(client, callback_query):
    page = int(callback_query.matches[0].group(1))
    user_id = callback_query.from_user.id
    
    state, data = await db.get_state(user_id)
    if state != "VIEWING_EXPIRY": return
    
    await show_expiry_page(callback_query, data["grants"], page)


# --- Extend Grant ---
@Client.on_callback_query(filters.regex(r"^ext_(.+)$"))
async def extend_grant_menu(client, callback_query):
    grant_id_prefix = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    
    state, data = await db.get_state(user_id)
    if state != "VIEWING_EXPIRY": return
    
    # Find matching grant
    grant = next((g for g in data["grants"] if str(g["_id"]).startswith(grant_id_prefix)), None)
    if not grant:
        await callback_query.answer("Grant not found.", show_alert=True)
        return
    
    await callback_query.edit_message_text(
        f"🔄 **Extend Access**\n\n"
        f"📧 `{grant['email']}`\n"
        f"📂 {grant['folder_name']}\n\n"
        "How long to extend?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("+1 Hour", callback_data=f"extdo_1_{grant_id_prefix}"),
             InlineKeyboardButton("+6 Hours", callback_data=f"extdo_6_{grant_id_prefix}")],
            [InlineKeyboardButton("+1 Day", callback_data=f"extdo_24_{grant_id_prefix}"),
             InlineKeyboardButton("+7 Days", callback_data=f"extdo_168_{grant_id_prefix}")],
            [InlineKeyboardButton("⬅️ Back", callback_data="expiry_menu")]
        ])
    )


@Client.on_callback_query(filters.regex(r"^extdo_(\d+)_(.+)$"))
async def execute_extend(client, callback_query):
    extra_hours = int(callback_query.matches[0].group(1))
    grant_id_prefix = callback_query.matches[0].group(2)
    user_id = callback_query.from_user.id
    
    state, data = await db.get_state(user_id)
    if state != "VIEWING_EXPIRY": return
    
    grant = next((g for g in data["grants"] if str(g["_id"]).startswith(grant_id_prefix)), None)
    if not grant:
        await callback_query.answer("Grant not found.", show_alert=True)
        return
    
    await db.extend_grant(grant["_id"], extra_hours)
    
    if extra_hours < 24:
        dur_text = f"{extra_hours}h"
    else:
        dur_text = f"{extra_hours // 24}d"
    
    await db.log_action(
        admin_id=user_id,
        admin_name=callback_query.from_user.first_name,
        action="extend",
        details={"email": grant["email"], "folder_name": grant["folder_name"], "extended_by": dur_text}
    )
    
    await callback_query.answer(f"✅ Extended by {dur_text}!")
    
    # Refresh dashboard
    grants = await db.get_active_grants()
    if grants:
        await show_expiry_page(callback_query, grants, 1)
    else:
        await callback_query.edit_message_text(
            "⏰ **Expiry Dashboard**\n\nNo active timed grants.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Back", callback_data="main_menu")]])
        )


# --- Revoke Grant ---
@Client.on_callback_query(filters.regex(r"^rev_(.+)$"))
async def revoke_grant_confirm(client, callback_query):
    grant_id_prefix = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    
    state, data = await db.get_state(user_id)
    if state != "VIEWING_EXPIRY": return
    
    grant = next((g for g in data["grants"] if str(g["_id"]).startswith(grant_id_prefix)), None)
    if not grant:
        await callback_query.answer("Grant not found.", show_alert=True)
        return
    
    await callback_query.edit_message_text(
        f"⚠️ **Revoke Access Now?**\n\n"
        f"📧 `{grant['email']}`\n"
        f"📂 {grant['folder_name']}\n\n"
        "This will remove access immediately.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🗑 Yes, Revoke", callback_data=f"revdo_{grant_id_prefix}"),
             InlineKeyboardButton("⬅️ Back", callback_data="expiry_menu")]
        ])
    )


@Client.on_callback_query(filters.regex(r"^revdo_(.+)$"))
async def execute_revoke(client, callback_query):
    grant_id_prefix = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    
    state, data = await db.get_state(user_id)
    if state != "VIEWING_EXPIRY": return
    
    grant = next((g for g in data["grants"] if str(g["_id"]).startswith(grant_id_prefix)), None)
    if not grant:
        await callback_query.answer("Grant not found.", show_alert=True)
        return
    
    # Remove access from Drive
    success = await drive_service.remove_access(grant["folder_id"], grant["email"])
    
    if success:
        await db.revoke_grant(grant["_id"])
        
        await db.log_action(
            admin_id=user_id,
            admin_name=callback_query.from_user.first_name,
            action="revoke",
            details={"email": grant["email"], "folder_name": grant["folder_name"]}
        )
        
        await callback_query.answer("✅ Access revoked!")
    else:
        await callback_query.answer("❌ Failed to revoke.", show_alert=True)
    
    # Refresh dashboard
    grants = await db.get_active_grants()
    if grants:
        await show_expiry_page(callback_query, grants, 1)
    else:
        await callback_query.edit_message_text(
            "⏰ **Expiry Dashboard**\n\nNo active timed grants.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📥 Bulk Import Existing", callback_data="bulk_import_confirm")],
                [InlineKeyboardButton("🏠 Back", callback_data="main_menu")]
            ])
        )


# --- Bulk Import Existing Permissions ---
@Client.on_callback_query(filters.regex("^bulk_import_confirm$"))
async def bulk_import_confirm(client, callback_query):
    await callback_query.edit_message_text(
        "📥 **Bulk Import Existing Permissions**\n\n"
        "This will scan ALL your Drive folders and create\n"
        "**40-day expiry timers** for every existing permission.\n\n"
        "⚠️ Owners will be skipped.\n"
        "⚠️ Already tracked grants will be skipped.\n\n"
        "This may take a while with many folders.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Start Import", callback_data="bulk_import_run"),
             InlineKeyboardButton("❌ Cancel", callback_data="expiry_menu")]
        ])
    )


@Client.on_callback_query(filters.regex("^bulk_import_run$"))
async def bulk_import_run(client, callback_query):
    user_id = callback_query.from_user.id
    
    await callback_query.edit_message_text("📥 **Scanning Drive folders...**\n⏳ Please wait...")
    
    # Get all folders
    folders = await drive_service.list_folders()
    if not folders:
        await callback_query.edit_message_text(
            "❌ No folders found.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Back", callback_data="main_menu")]])
        )
        return
    
    # Get existing tracked grants to avoid duplicates
    existing_grants = await db.get_active_grants()
    tracked = set()
    for g in existing_grants:
        tracked.add(f"{g['email'].lower()}:{g['folder_id']}")
    
    imported = 0
    skipped = 0
    errors = 0
    total_folders = len(folders)
    
    for i, folder in enumerate(folders):
        try:
            # Update progress every 10 folders
            if i % 10 == 0 and i > 0:
                try:
                    await callback_query.edit_message_text(
                        f"📥 **Scanning folders... ({i}/{total_folders})**\n"
                        f"✅ Imported: {imported} | ⏭ Skipped: {skipped}"
                    )
                except Exception:
                    pass
            
            perms = await drive_service.get_permissions(folder["id"])
            
            for perm in perms:
                # Skip owners and non-user permissions
                if perm.get("role") == "owner":
                    continue
                
                email = perm.get("emailAddress", "").lower()
                if not email:
                    continue
                
                # Skip already tracked
                key = f"{email}:{folder['id']}"
                if key in tracked:
                    skipped += 1
                    continue
                
                # Create 40-day timed grant
                await db.add_timed_grant(
                    admin_id=user_id,
                    email=email,
                    folder_id=folder["id"],
                    folder_name=folder["name"],
                    role=perm.get("role", "reader"),
                    duration_hours=40 * 24  # 40 days
                )
                tracked.add(key)
                imported += 1
                
        except Exception as e:
            LOGGER.error(f"Error scanning folder {folder['name']}: {e}")
            errors += 1
    
    # Log the bulk import action
    await db.log_action(
        admin_id=user_id,
        admin_name=callback_query.from_user.first_name,
        action="bulk_import",
        details={"imported": imported, "skipped": skipped, "errors": errors, "folders_scanned": total_folders}
    )
    
    await callback_query.edit_message_text(
        "📥 **Bulk Import Complete!**\n\n"
        f"📂 Folders scanned: **{total_folders}**\n"
        f"✅ Grants imported: **{imported}**\n"
        f"⏭ Already tracked: **{skipped}**\n"
        f"❌ Errors: **{errors}**\n\n"
        f"⏰ All imported grants expire in **40 days**.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⏰ View Dashboard", callback_data="expiry_menu")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ])
    )
