from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.database import db
from services.drive import drive_service
import datetime
import time
import logging

LOGGER = logging.getLogger(__name__)


from utils.time import format_time_remaining, format_duration, format_date
from utils.time import format_time_remaining, format_duration, format_date
from services.broadcast import broadcast
from utils.filters import is_admin


# --- Expiry Dashboard ---
@Client.on_callback_query(filters.regex("^expiry_menu$") & is_admin)
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
    
    # Count expiring soon (within 24h)
    now = time.time()
    expiring_soon = sum(1 for g in grants if g.get('expires_at', 0) - now < 86400 and g.get('expires_at', 0) - now > 0)
    
    text = f"⏰ **Expiry Dashboard** (Page {page}/{total_pages})\n"
    text += f"📊 {len(grants)} active timed grant(s)\n"
    if expiring_soon > 0:
        text += f"⚠️ **{expiring_soon} expiring within 24 hours!**\n"
    text += "\n"
    
    keyboard = []
    for grant in current:
        remaining = format_time_remaining(grant["expires_at"])
        grant_id = str(grant["_id"])
        expires_at = grant.get("expires_at", 0)
        is_expiring = 0 < (expires_at - now) < 86400
        expiry_date = format_date(expires_at)
        
        warn_label = "  ⚠️ EXPIRING SOON" if is_expiring else ""
        
        text += (
            f"📧 `{grant['email']}`{warn_label}\n"
            f"   📂 {grant['folder_name']} | 🔑 {grant['role']}\n"
            f"   ⏳ {remaining} remaining  |  📅 {expiry_date}\n\n"
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
    
    keyboard.append([InlineKeyboardButton("🗑 Bulk Revoke", callback_data="bulk_revoke_menu")])
    keyboard.append([
        InlineKeyboardButton("📥 Bulk Import", callback_data="bulk_import_confirm"),
        InlineKeyboardButton("⬅️ Back", callback_data="main_menu")
    ])
    
    # Store grants in state for pagination/action
    await db.set_state(callback_query.from_user.id, "VIEWING_EXPIRY", {
        "grants": [{**g, "_id": str(g["_id"])} for g in grants]
    })
    
    await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


@Client.on_callback_query(filters.regex(r"^expiry_page_(\d+)$") & is_admin)
async def expiry_pagination(client, callback_query):
    page = int(callback_query.matches[0].group(1))
    user_id = callback_query.from_user.id
    
    state, data = await db.get_state(user_id)
    if state != "VIEWING_EXPIRY": return
    
    await show_expiry_page(callback_query, data["grants"], page)


# --- Extend Grant ---
@Client.on_callback_query(filters.regex(r"^ext_(.+)$") & is_admin)
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
    
    current_expiry = format_date(grant.get('expires_at', 0))
    
    await callback_query.edit_message_text(
        f"🔄 **Extend Access**\n\n"
        f"📧 `{grant['email']}`\n"
        f"📂 {grant['folder_name']}\n"
        f"📅 Current expiry: {current_expiry}\n\n"
        "Add extra time:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("+1 Hour", callback_data=f"extdo_1_{grant_id_prefix}"),
             InlineKeyboardButton("+6 Hours", callback_data=f"extdo_6_{grant_id_prefix}")],
            [InlineKeyboardButton("+1 Day", callback_data=f"extdo_24_{grant_id_prefix}"),
             InlineKeyboardButton("+7 Days", callback_data=f"extdo_168_{grant_id_prefix}")],
            [InlineKeyboardButton("+14 Days", callback_data=f"extdo_336_{grant_id_prefix}"),
             InlineKeyboardButton("+30 Days", callback_data=f"extdo_720_{grant_id_prefix}")],
            [InlineKeyboardButton("⬅️ Back", callback_data="expiry_menu")]
        ])
    )


@Client.on_callback_query(filters.regex(r"^extdo_(\d+)_(.+)$") & is_admin)
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
@Client.on_callback_query(filters.regex(r"^rev_(.+)$") & is_admin)
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


@Client.on_callback_query(filters.regex(r"^revdo_(.+)$") & is_admin)
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
        await broadcast(client, "revoke", {
            "email": grant["email"],
            "folder_name": grant["folder_name"],
            "admin_name": callback_query.from_user.first_name
        })
        
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
@Client.on_callback_query(filters.regex("^bulk_import_confirm$") & is_admin)
async def bulk_import_confirm(client, callback_query):
    """Full Drive scan: count viewers, generate report file, send via Telegram."""
    import os
    import tempfile
    from datetime import datetime
    
    try:
        await callback_query.edit_message_text("📥 **Full Drive Scan Started...**\n⏳ Scanning all folders and permissions...")
    except Exception as e:
        LOGGER.debug(f"Error editing message: {e}")
    
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
    folder_data = []
    
    for i, folder in enumerate(folders):
        try:
            if i % 10 == 0 and i > 0:
                try:
                    await callback_query.edit_message_text(
                        f"📥 **Scanning... ({i}/{len(folders)} folders)**\n"
                        f"👁 Viewers found: {viewer_count}"
                    )
                except Exception as e:
                    LOGGER.debug(f"Error editing progress message: {e}")
            
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
    report_lines.append("  **GOOGLE DRIVE FULL SCAN REPORT**")
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


@Client.on_callback_query(filters.regex("^bulk_import_run$") & is_admin)
async def bulk_import_run(client, callback_query):
    user_id = callback_query.from_user.id
    
    try:
        await callback_query.edit_message_text("📥 **Scanning Drive folders...**\n⏳ Please wait...")
    except Exception as e:
        LOGGER.debug(f"Error editing message: {e}")
    
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
                except Exception as e:
                    LOGGER.debug(f"Error editing progress message: {e}")
            
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
    await broadcast(client, "bulk_import", {
        "imported": imported,
        "skipped": skipped,
        "errors": errors,
        "admin_name": callback_query.from_user.first_name
    })
    
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


# --- Bulk Revoke ---
@Client.on_callback_query(filters.regex("^bulk_revoke_menu$") & is_admin)
async def bulk_revoke_menu(client, callback_query):
    grants = await db.get_active_grants()
    
    if not grants:
        await callback_query.answer("No active grants to revoke.", show_alert=True)
        return
    
    now = time.time()
    expiring_soon = sum(1 for g in grants if 0 < g.get('expires_at', 0) - now < 86400)
    
    await callback_query.edit_message_text(
        "🗑 **Bulk Revoke**\n\n"
        f"📊 Active grants: **{len(grants)}**\n"
        f"⚠️ Expiring soon: **{expiring_soon}**\n\n"
        "Select what to revoke:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(f"🗑 Revoke All ({len(grants)})", callback_data="bulk_revoke_all")],
            [InlineKeyboardButton(f"⚠️ Revoke Expiring Only ({expiring_soon})", callback_data="bulk_revoke_expiring")],
            [InlineKeyboardButton("⬅️ Back", callback_data="expiry_menu")]
        ])
    )


@Client.on_callback_query(filters.regex("^bulk_revoke_(all|expiring)$") & is_admin)
async def bulk_revoke_confirm(client, callback_query):
    revoke_type = callback_query.matches[0].group(1)
    grants = await db.get_active_grants()
    now = time.time()
    
    if revoke_type == "expiring":
        targets = [g for g in grants if 0 < g.get('expires_at', 0) - now < 86400]
        label = "expiring (within 24h)"
    else:
        targets = grants
        label = "all active"
    
    if not targets:
        await callback_query.answer("No matching grants found.", show_alert=True)
        return
    
    await db.set_state(callback_query.from_user.id, "CONFIRM_BULK_REVOKE", {
        "revoke_type": revoke_type,
        "count": len(targets)
    })
    
    await callback_query.edit_message_text(
        f"⚠️ **Confirm Bulk Revoke**\n\n"
        f"This will revoke **{len(targets)}** {label} grants.\n"
        "Access will be removed from Google Drive immediately.\n\n"
        "Are you sure?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Yes, Revoke All", callback_data="bulk_revoke_execute")],
            [InlineKeyboardButton("❌ Cancel", callback_data="expiry_menu")]
        ])
    )


@Client.on_callback_query(filters.regex("^bulk_revoke_execute$") & is_admin)
async def bulk_revoke_execute(client, callback_query):
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)
    
    if state != "CONFIRM_BULK_REVOKE":
        await callback_query.answer("Session expired.", show_alert=True)
        return
    
    revoke_type = data.get("revoke_type", "all")
    grants = await db.get_active_grants()
    now = time.time()
    
    if revoke_type == "expiring":
        targets = [g for g in grants if 0 < g.get('expires_at', 0) - now < 86400]
    else:
        targets = grants
    
    await callback_query.edit_message_text(f"⏳ Revoking {len(targets)} grants...")
    
    success_count = 0
    fail_count = 0
    
    for grant in targets:
        try:
            ok = await drive_service.remove_access(grant["folder_id"], grant["email"])
            if ok:
                await db.revoke_grant(grant["_id"])
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            LOGGER.error(f"Bulk revoke error: {e}")
            fail_count += 1
    
    await db.log_action(
        admin_id=user_id,
        admin_name=callback_query.from_user.first_name,
        action="bulk_revoke",
        details={"type": revoke_type, "success": success_count, "failed": fail_count}
    )
    await broadcast(client, "bulk_revoke", {
        "type": revoke_type,
        "success": success_count,
        "failed": fail_count,
        "admin_name": callback_query.from_user.first_name
    })
    
    await callback_query.edit_message_text(
        "✅ **Bulk Revoke Complete**\n\n"
        f"✅ Revoked: **{success_count}**\n"
        f"❌ Failed: **{fail_count}**",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⏰ Back to Dashboard", callback_data="expiry_menu")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ])
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEW: Notification Alert Action Handlers
# Allows admin to extend/revoke directly from expiry alert messages
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_callback_query(filters.regex(r"^notif_ext_(\d+)_(.+)$") & is_admin)
async def notif_extend_grant(client, callback_query):
    """Extend grant directly from expiry notification message."""
    extra_hours = int(callback_query.matches[0].group(1))
    grant_id_prefix = callback_query.matches[0].group(2)

    # Find grant by ID prefix
    from bson import ObjectId
    grants = await db.get_active_grants()
    grant = next((g for g in grants if str(g["_id"]).startswith(grant_id_prefix)), None)

    if not grant:
        await callback_query.answer("⚠️ Grant not found or already expired.", show_alert=True)
        try:
            await callback_query.message.edit_reply_markup(reply_markup=None)
        except Exception as e:
            LOGGER.debug(f"Error editing reply markup: {e}")
        return

    await db.extend_grant(grant["_id"], extra_hours)
    await db.log_action(
        admin_id=callback_query.from_user.id,
        admin_name=callback_query.from_user.first_name,
        action="extend",
        details={
            "email": grant["email"],
            "folder_name": grant["folder_name"],
            "extended_by": format_duration(extra_hours),
            "source": "notification_alert"
        }
    )

    new_expiry = format_date(grant["expires_at"] + extra_hours * 3600)
    await callback_query.answer(f"✅ Extended! New expiry: {new_expiry}", show_alert=True)
    try:
        await callback_query.message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        LOGGER.debug(f"Error editing reply markup: {e}")


@Client.on_callback_query(filters.regex(r"^notif_rev_(.+)$") & is_admin)
async def notif_revoke_grant(client, callback_query):
    """Revoke grant directly from expiry notification message."""
    grant_id_prefix = callback_query.matches[0].group(1)

    grants = await db.get_active_grants()
    grant = next((g for g in grants if str(g["_id"]).startswith(grant_id_prefix)), None)

    if not grant:
        await callback_query.answer("⚠️ Grant not found or already revoked.", show_alert=True)
        try:
            await callback_query.message.edit_reply_markup(reply_markup=None)
        except Exception as e:
            LOGGER.debug(f"Error editing reply markup: {e}")
        return

    success = await drive_service.remove_access(grant["folder_id"], grant["email"])
    if success:
        await db.revoke_grant(grant["_id"])
        await db.log_action(
            admin_id=callback_query.from_user.id,
            admin_name=callback_query.from_user.first_name,
            action="revoke",
            details={
                "email": grant["email"],
                "folder_name": grant["folder_name"],
                "source": "notification_alert"
            }
        )
        await broadcast(client, "revoke", {
            "email": grant["email"],
            "folder_name": grant["folder_name"],
            "admin_name": callback_query.from_user.first_name
        })
        await callback_query.answer("✅ Access revoked successfully!", show_alert=True)
    else:
        await callback_query.answer("❌ Failed to revoke. Check Drive API.", show_alert=True)

    try:
        await callback_query.message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        LOGGER.debug(f"Error editing reply markup: {e}")
