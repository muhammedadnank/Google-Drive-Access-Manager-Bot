from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.database import db
from services.drive import drive_service
import datetime
import time
import logging

LOGGER = logging.getLogger(__name__)


from utils.time import format_time_remaining, format_duration


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
    
    dur_text = format_duration(extra_hours)
    
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
    """Full Drive scan: count viewers, generate report file, send via Telegram."""
    import os
    import tempfile
    from datetime import datetime
    
    try:
        await callback_query.edit_message_text("📥 **Full Drive Scan Started...**\n⏳ Scanning all folders and permissions...")
    except Exception:
        pass
    
    folders = await drive_service.list_folders()
    if not folders:
        await callback_query.edit_message_text(
            "❌ No folders found.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Back", callback_data="main_menu")]])
        )
        return
    
    # Get existing tracked grants
    existing_grants = await db.get_active_grants()
    tracked = set()
    for g in existing_grants:
        tracked.add(f"{g['email'].lower()}:{g['folder_id']}")
    
    # Collect scan data
    viewer_count = 0
    already_tracked = 0
    unique_emails = set()
    folder_data = []  # {name, id, viewers: [emails]}
    
    for i, folder in enumerate(folders):
        try:
            if i % 10 == 0 and i > 0:
                try:
                    await callback_query.edit_message_text(
                        f"📥 **Scanning... ({i}/{len(folders)} folders)**\n"
                        f"👁 Viewers found: {viewer_count}"
                    )
                except Exception:
                    pass
            
            perms = await drive_service.get_permissions(folder["id"])
            folder_viewers = []
            
            for perm in perms:
                if perm.get("role") in ("owner", "writer"):
                    continue
                email = perm.get("emailAddress", "").lower()
                if not email:
                    continue
                
                folder_viewers.append(email)
                key = f"{email}:{folder['id']}"
                if key in tracked:
                    already_tracked += 1
                else:
                    viewer_count += 1
                    unique_emails.add(email)
            
            folder_data.append({
                "name": folder["name"],
                "id": folder["id"],
                "viewers": folder_viewers
            })
        except Exception as e:
            LOGGER.error(f"Error scanning {folder['name']}: {e}")
            folder_data.append({"name": folder["name"], "id": folder["id"], "viewers": [], "error": True})
    
    # Generate report file
    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append("  GOOGLE DRIVE FULL SCAN REPORT")
    report_lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 60)
    report_lines.append("")
    report_lines.append(f"Total Folders: {len(folders)}")
    report_lines.append(f"Total Viewer Permissions: {viewer_count + already_tracked}")
    report_lines.append(f"New (not tracked): {viewer_count}")
    report_lines.append(f"Already Tracked: {already_tracked}")
    report_lines.append(f"Unique Emails: {len(unique_emails)}")
    report_lines.append("")
    report_lines.append("=" * 60)
    report_lines.append("  FOLDER-WISE BREAKDOWN")
    report_lines.append("=" * 60)
    
    for fd in folder_data:
        report_lines.append("")
        report_lines.append(f"📂 {fd['name']}")
        report_lines.append(f"   ID: {fd['id']}")
        if fd.get("error"):
            report_lines.append("   ⚠️ Error scanning this folder")
        elif not fd["viewers"]:
            report_lines.append("   No viewer permissions")
        else:
            report_lines.append(f"   Viewers ({len(fd['viewers'])}):")
            for email in fd["viewers"]:
                status = "✓ tracked" if f"{email}:{fd['id']}" in tracked else "● new"
                report_lines.append(f"     - {email} [{status}]")
    
    report_lines.append("")
    report_lines.append("=" * 60)
    report_lines.append("  ALL UNIQUE EMAILS")
    report_lines.append("=" * 60)
    for idx, email in enumerate(sorted(unique_emails), 1):
        report_lines.append(f"  {idx}. {email}")
    
    report_lines.append("")
    report_lines.append("--- End of Report ---")
    
    report_content = "\n".join(report_lines)
    
    # Write to temp file and send
    report_path = os.path.join(tempfile.gettempdir(), "drive_scan_report.txt")
    with open(report_path, "w") as f:
        f.write(report_content)
    
    # Send report file
    await callback_query.message.reply_document(
        document=report_path,
        caption=(
            f"📥 **Drive Scan Report**\n\n"
            f"📂 Folders: **{len(folders)}**\n"
            f"👁 Viewers: **{viewer_count + already_tracked}**\n"
            f"🆕 New: **{viewer_count}** | ⏭ Tracked: **{already_tracked}**\n"
            f"👤 Unique emails: **{len(unique_emails)}**"
        )
    )
    
    # Clean up
    os.remove(report_path)
    
    # Store scan results in state
    await db.set_state(callback_query.from_user.id, "BULK_IMPORT_READY", {
        "viewer_count": viewer_count,
        "already_tracked": already_tracked,
        "unique_emails": len(unique_emails),
        "total_folders": len(folders)
    })
    
    # Show import button
    await callback_query.message.reply_text(
        f"⏰ Import all **{viewer_count}** new viewer grants with **40-day expiry**?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(f"✅ Import {viewer_count} Grants", callback_data="bulk_import_run"),
             InlineKeyboardButton("❌ Cancel", callback_data="expiry_menu")]
        ])
    )


@Client.on_callback_query(filters.regex("^bulk_import_run$"))
async def bulk_import_run(client, callback_query):
    user_id = callback_query.from_user.id
    
    try:
        await callback_query.edit_message_text("📥 **Scanning Drive folders...**\n⏳ Please wait...")
    except Exception:
        pass
    
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
                # Skip owners, editors, and non-user permissions
                if perm.get("role") in ("owner", "writer"):
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
