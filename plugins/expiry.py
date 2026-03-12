import time
import logging
import datetime
from datetime import timezone, timedelta

from pyrogram import Client, filters
from pyrogram.enums import ButtonStyle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from services.database import db
from services.drive import drive_service
from services.broadcast import broadcast
from utils.filters import is_admin
from utils.time import safe_edit, format_time_remaining, format_duration, format_date
from utils.pagination import sort_grants

LOGGER = logging.getLogger(__name__)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# /expiry COMMAND  +  expiry_menu CALLBACK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_message(filters.command("expiry") & filters.private & is_admin)
async def expiry_command(client, message):
    """Entry point via /expiry command."""
    grants = await db.get_active_grants()
    grants = sort_grants(grants, key="folder_name")

    if not grants:
        await message.reply_text(
            "⏰ **Expiry Dashboard**\n\nNo active timed grants.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📥 Bulk Import Existing", callback_data="bulk_import_confirm", style=ButtonStyle.SUCCESS)],
                [InlineKeyboardButton("🏠 Back", callback_data="main_menu", style=ButtonStyle.PRIMARY)]
            ])
        )
        return

    analytics = await db.get_expiry_analytics()
    timeline  = analytics["timeline"]
    analytics_text = (
        "📊 **Quick Analytics**\n"
        f"⚠️ <24h: {timeline['urgent']} | "
        f"📅 Week: {timeline['week']} | "
        f"📅 Month: {timeline['month']} | "
        f"Later: {timeline['later']}\n\n"
    )

    # For /command entry, we need a placeholder message to edit
    msg = await message.reply_text("⏰ Loading expiry dashboard...")
    await _show_expiry_page(msg, grants, 1, analytics_text, is_message=True)


@Client.on_callback_query(filters.regex("^expiry_menu$") & is_admin)
async def expiry_dashboard(client, callback_query):
    """Entry point via inline button."""
    grants = await db.get_active_grants()
    grants = sort_grants(grants, key="folder_name")

    if not grants:
        await safe_edit(callback_query,
            "⏰ **Expiry Dashboard**\n\nNo active timed grants.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📥 Bulk Import Existing", callback_data="bulk_import_confirm", style=ButtonStyle.SUCCESS)],
                [InlineKeyboardButton("🏠 Back", callback_data="main_menu", style=ButtonStyle.PRIMARY)]
            ])
        )
        return

    analytics = await db.get_expiry_analytics()
    timeline  = analytics["timeline"]
    analytics_text = (
        "📊 **Quick Analytics**\n"
        f"⚠️ <24h: {timeline['urgent']} | "
        f"📅 Week: {timeline['week']} | "
        f"📅 Month: {timeline['month']} | "
        f"Later: {timeline['later']}\n\n"
    )
    await _show_expiry_page(callback_query, grants, 1, analytics_text)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Shared Page Renderer
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def _show_expiry_page(target, grants, page, analytics_text="", is_message=False):
    per_page    = 20
    total_pages = (len(grants) + per_page - 1) // per_page
    start       = (page - 1) * per_page
    current     = grants[start:start + per_page]

    now = time.time()
    expiring_soon = sum(
        1 for g in grants if 0 < g.get("expires_at", 0) - now < 86400
    )

    text  = analytics_text
    text += f"⏰ **Expiry Dashboard** (Page {page}/{total_pages})\n"
    text += f"📊 {len(grants)} active timed grant(s)\n"
    if expiring_soon > 0:
        text += f"⚠️ **{expiring_soon} expiring within 24 hours!**\n"
    text += "\n"

    keyboard = []
    for grant in current:
        remaining   = format_time_remaining(grant["expires_at"])
        grant_id    = str(grant["_id"])
        expires_at  = grant.get("expires_at", 0)
        is_expiring = 0 < (expires_at - now) < 86400
        expiry_date = format_date(expires_at)

        warn = "  ⚠️ EXPIRING SOON" if is_expiring else ""
        text += (
            f"📧 `{grant['email']}`{warn}\n"
            f"   📂 {grant['folder_name']} | 🔑 {grant['role']}\n"
            f"   ⏳ {remaining} remaining  |  📅 {expiry_date}\n\n"
        )
        keyboard.append([
            InlineKeyboardButton(f"🔄 Extend {grant['email'][:15]}", callback_data=f"ext_{grant_id}", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("🗑 Revoke", callback_data=f"rev_{grant_id}", style=ButtonStyle.DANGER)
        ])

    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"expiry_page_{page - 1}", style=ButtonStyle.PRIMARY))
    if page < total_pages:
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"expiry_page_{page + 1}", style=ButtonStyle.PRIMARY))
    if nav:
        keyboard.append(nav)

    keyboard.append([
        InlineKeyboardButton("🗑 Bulk Revoke", callback_data="bulk_revoke_menu", style=ButtonStyle.DANGER),
        InlineKeyboardButton("🏠 Back",        callback_data="main_menu",        style=ButtonStyle.PRIMARY)
    ])

    markup = InlineKeyboardMarkup(keyboard)
    if is_message:
        # target is a Message object (from /expiry command)
        try:
            await target.edit_text(text, reply_markup=markup)
        except Exception as e:
            LOGGER.debug(f"Expiry page edit: {e}")
    else:
        await safe_edit(target, text, reply_markup=markup)


@Client.on_callback_query(filters.regex(r"^expiry_page_(\d+)$") & is_admin)
async def expiry_pagination(client, callback_query):
    page   = int(callback_query.matches[0].group(1))
    grants = await db.get_active_grants()
    grants = sort_grants(grants, key="folder_name")
    await _show_expiry_page(callback_query, grants, page)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Extend Grant
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_callback_query(filters.regex(r"^ext_(.+)$") & is_admin)
async def extend_grant_menu(client, callback_query):
    grant_id = callback_query.matches[0].group(1)
    from bson import ObjectId
    grant = await db.grants.find_one({"_id": ObjectId(grant_id)})
    if not grant:
        await callback_query.answer("Grant not found.", show_alert=True)
        return

    remaining = format_time_remaining(grant["expires_at"])
    expiry    = format_date(grant["expires_at"])

    await safe_edit(callback_query,
        f"🔄 **Extend Access**\n\n"
        f"📧 `{grant['email']}`\n"
        f"📂 {grant['folder_name']}\n"
        f"⏳ {remaining} remaining | 📅 Expires {expiry}\n\n"
        "Select extension duration:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("+1h",  callback_data=f"extdo_1_{grant_id}",   style=ButtonStyle.SUCCESS),
             InlineKeyboardButton("+6h",  callback_data=f"extdo_6_{grant_id}",   style=ButtonStyle.SUCCESS),
             InlineKeyboardButton("+1d",  callback_data=f"extdo_24_{grant_id}",  style=ButtonStyle.SUCCESS)],
            [InlineKeyboardButton("+7d",  callback_data=f"extdo_168_{grant_id}", style=ButtonStyle.SUCCESS),
             InlineKeyboardButton("+30d", callback_data=f"extdo_720_{grant_id}", style=ButtonStyle.SUCCESS)],
            [InlineKeyboardButton("⬅️ Back", callback_data="expiry_menu", style=ButtonStyle.PRIMARY)]
        ])
    )


@Client.on_callback_query(filters.regex(r"^extdo_(\d+)_(.+)$") & is_admin)
async def execute_extend(client, callback_query):
    hours    = int(callback_query.matches[0].group(1))
    grant_id = callback_query.matches[0].group(2)
    user_id  = callback_query.from_user.id

    from bson import ObjectId
    grant = await db.grants.find_one({"_id": ObjectId(grant_id)})
    if not grant:
        await callback_query.answer("Grant not found.", show_alert=True)
        return

    new_expiry = grant["expires_at"] + (hours * 3600)
    await db.grants.update_one({"_id": ObjectId(grant_id)}, {"$set": {"expires_at": new_expiry}})
    await db.log_action(user_id, callback_query.from_user.first_name, "extend", {
        "email": grant["email"], "folder_name": grant["folder_name"],
        "extended_hours": hours
    })

    await safe_edit(callback_query,
        f"✅ **Access Extended**\n\n"
        f"📧 `{grant['email']}`\n"
        f"📂 {grant['folder_name']}\n"
        f"⏳ Extended by **+{format_duration(hours)}**\n"
        f"📅 New expiry: {format_date(new_expiry)}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back to Expiry", callback_data="expiry_menu", style=ButtonStyle.PRIMARY),
             InlineKeyboardButton("🏠 Main Menu",       callback_data="main_menu",   style=ButtonStyle.PRIMARY)]
        ])
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Revoke Single Grant
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_callback_query(filters.regex(r"^rev_(.+)$") & is_admin)
async def revoke_grant_confirm(client, callback_query):
    grant_id = callback_query.matches[0].group(1)
    from bson import ObjectId
    grant = await db.grants.find_one({"_id": ObjectId(grant_id)})
    if not grant:
        await callback_query.answer("Grant not found.", show_alert=True)
        return

    await safe_edit(callback_query,
        f"⚠️ **Confirm Revoke**\n\n"
        f"📧 `{grant['email']}`\n"
        f"📂 {grant['folder_name']}\n"
        f"🔑 {grant['role'].capitalize()}\n\n"
        "This will remove Drive access immediately.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🗑 Yes, Revoke", callback_data=f"revdo_{grant_id}", style=ButtonStyle.DANGER),
             InlineKeyboardButton("❌ Cancel",       callback_data="expiry_menu",       style=ButtonStyle.PRIMARY)]
        ])
    )


@Client.on_callback_query(filters.regex(r"^revdo_(.+)$") & is_admin)
async def execute_revoke(client, callback_query):
    grant_id = callback_query.matches[0].group(1)
    user_id  = callback_query.from_user.id

    from bson import ObjectId
    grant = await db.grants.find_one({"_id": ObjectId(grant_id)})
    if not grant:
        await callback_query.answer("Grant not found.", show_alert=True)
        return

    await safe_edit(callback_query, "⏳ Revoking access...")
    drive_service.set_admin_user(user_id)

    # FIX (v2.2.2): pass db so drive_service can fetch OAuth credentials
    success = await drive_service.remove_access(grant["folder_id"], grant["email"], db)

    if success:
        await db.revoke_grant(ObjectId(grant_id))
        await db.log_action(user_id, callback_query.from_user.first_name, "revoke", {
            "email": grant["email"], "folder_name": grant["folder_name"]
        })
        await broadcast(client, "revoke", {
            "email": grant["email"], "folder_name": grant["folder_name"],
            "admin_name": callback_query.from_user.first_name
        })
        await safe_edit(callback_query,
            f"✅ **Access Revoked**\n\n"
            f"📧 `{grant['email']}`\n"
            f"📂 {grant['folder_name']}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back to Expiry", callback_data="expiry_menu", style=ButtonStyle.PRIMARY),
                 InlineKeyboardButton("🏠 Main Menu",       callback_data="main_menu",   style=ButtonStyle.PRIMARY)]
            ])
        )
    else:
        await safe_edit(callback_query, "❌ Failed to revoke access.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu", style=ButtonStyle.PRIMARY)
            ]])
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Bulk Import from Drive
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_callback_query(filters.regex("^bulk_import_confirm$") & is_admin)
async def bulk_import_confirm(client, callback_query):
    await safe_edit(callback_query,
        "📥 **Bulk Import — Drive Scan**\n\n"
        "This will scan ALL folders in your Drive and import existing viewer permissions.\n\n"
        "• Skips owners, editors, and duplicates\n"
        "• Sets 40-day expiry for new viewers\n"
        "• Shows before/after statistics\n\n"
        "⚠️ This may take several minutes for large drives.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Start Import", callback_data="bulk_import_run", style=ButtonStyle.SUCCESS),
             InlineKeyboardButton("❌ Cancel",       callback_data="expiry_menu",    style=ButtonStyle.DANGER)]
        ])
    )


@Client.on_callback_query(filters.regex("^bulk_import_run$") & is_admin)
async def bulk_import_run(client, callback_query):
    user_id = callback_query.from_user.id
    await safe_edit(callback_query, "📥 **Full Drive Scan Started...**\n⏳ Scanning all folders and permissions...")

    drive_service.set_admin_user(user_id)

    try:
        folders = await drive_service.get_all_folders(db)
        if not folders:
            await safe_edit(callback_query, "❌ No folders found in Drive.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🏠 Back", callback_data="main_menu", style=ButtonStyle.PRIMARY)
                ]]))
            return

        total_folders = len(folders)
        imported = 0
        skipped  = 0
        errors   = 0

        for i, folder in enumerate(folders):
            if i % 10 == 0:
                try:
                    await safe_edit(callback_query,
                        f"📥 **Scanning Drive folders...**\n"
                        f"⏳ Progress: {i}/{total_folders} folders\n"
                        f"✅ Imported: {imported} | ⏭ Skipped: {skipped}"
                    )
                except Exception:
                    pass

            try:
                perms = await drive_service.get_permissions(folder["id"], db)
                for p in perms:
                    role  = p.get("role", "")
                    email = p.get("emailAddress", "")
                    if role in ("owner", "writer") or not email:
                        skipped += 1
                        continue

                    exists = await db.grants.find_one({
                        "email": email.lower(), "folder_id": folder["id"], "status": "active"
                    })
                    if exists:
                        skipped += 1
                        continue

                    await db.add_timed_grant(
                        admin_id=user_id, email=email.lower(),
                        folder_id=folder["id"], folder_name=folder["name"],
                        role="viewer", duration_hours=960  # 40 days
                    )
                    imported += 1
            except Exception as e:
                LOGGER.error(f"Bulk import error for folder {folder.get('name')}: {e}")
                errors += 1

        await db.log_action(user_id, callback_query.from_user.first_name, "bulk_import", {
            "folders_scanned": total_folders, "imported": imported,
            "skipped": skipped, "errors": errors
        })

        await safe_edit(callback_query,
            f"✅ **Drive Import Complete!**\n\n"
            f"📂 Folders scanned: **{total_folders}**\n"
            f"✅ Imported: **{imported}**\n"
            f"⏭ Skipped: **{skipped}**\n"
            f"❌ Errors: **{errors}**\n\n"
            f"All imported viewers set to 40-day expiry.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⏰ View Expiry", callback_data="expiry_menu", style=ButtonStyle.PRIMARY)],
                [InlineKeyboardButton("🏠 Main Menu",   callback_data="main_menu",   style=ButtonStyle.PRIMARY)]
            ])
        )

    except Exception as e:
        LOGGER.error(f"Bulk import failed: {e}")
        await safe_edit(callback_query, f"❌ **Import failed.**\n\n`{e}`",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu", style=ButtonStyle.PRIMARY)
            ]])
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Bulk Revoke Menu
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_callback_query(filters.regex("^bulk_revoke_menu$") & is_admin)
async def bulk_revoke_menu(client, callback_query):
    grants  = await db.get_active_grants()
    now     = time.time()
    expiring = [g for g in grants if 0 < g.get("expires_at", 0) - now < 86400]

    await safe_edit(callback_query,
        f"🗑 **Bulk Revoke**\n\n"
        f"📊 Total active timed grants: **{len(grants)}**\n"
        f"⚠️ Expiring within 24h: **{len(expiring)}**\n\n"
        "Select what to revoke:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(f"🗑 Revoke ALL ({len(grants)})",         callback_data="bulk_revoke_all",      style=ButtonStyle.DANGER)],
            [InlineKeyboardButton(f"⚠️ Revoke Expiring Only ({len(expiring)})", callback_data="bulk_revoke_expiring", style=ButtonStyle.DANGER)],
            [InlineKeyboardButton("❌ Cancel", callback_data="expiry_menu", style=ButtonStyle.PRIMARY)]
        ])
    )


@Client.on_callback_query(filters.regex(r"^bulk_revoke_(all|expiring)$") & is_admin)
async def bulk_revoke_execute(client, callback_query):
    mode    = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id

    grants = await db.get_active_grants()
    now    = time.time()

    if mode == "expiring":
        targets = [g for g in grants if 0 < g.get("expires_at", 0) - now < 86400]
        label   = "expiring within 24h"
    else:
        targets = grants
        label   = "all timed"

    await safe_edit(callback_query, f"⏳ Revoking {len(targets)} {label} grant(s)...")

    drive_service.set_admin_user(user_id)
    success_count = 0
    fail_count    = 0

    for grant in targets:
        try:
            # FIX (v2.2.2): pass db
            ok = await drive_service.remove_access(grant["folder_id"], grant["email"], db)
            if ok:
                await db.revoke_grant(grant["_id"])
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            LOGGER.error(f"Bulk revoke error: {e}")
            fail_count += 1

    await db.log_action(user_id, callback_query.from_user.first_name, "bulk_revoke", {
        "mode": mode, "success": success_count, "failed": fail_count
    })
    await broadcast(client, "bulk_revoke", {
        "type": f"bulk_{mode}", "success": success_count, "failed": fail_count,
        "admin_name": callback_query.from_user.first_name
    })

    await safe_edit(callback_query,
        f"✅ **Bulk Revoke Complete!**\n\n"
        f"Mode: **{label}**\n"
        f"✅ Revoked: **{success_count}**\n"
        f"❌ Failed: **{fail_count}**",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⏰ Back to Expiry", callback_data="expiry_menu", style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("🏠 Main Menu",       callback_data="main_menu",   style=ButtonStyle.PRIMARY)]
        ])
    )


# Notification revoke (from expiry notification messages)
@Client.on_callback_query(filters.regex(r"^notif_revoke_(.+)$") & is_admin)
async def notif_revoke_grant(client, callback_query):
    grant_id = callback_query.matches[0].group(1)
    user_id  = callback_query.from_user.id

    from bson import ObjectId
    grant = await db.grants.find_one({"_id": ObjectId(grant_id)})
    if not grant:
        await callback_query.answer("Grant not found.", show_alert=True)
        return

    drive_service.set_admin_user(user_id)
    # FIX (v2.2.2): pass db
    success = await drive_service.remove_access(grant["folder_id"], grant["email"], db)

    if success:
        await db.revoke_grant(ObjectId(grant_id))
        await callback_query.answer("✅ Access revoked.", show_alert=True)
    else:
        await callback_query.answer("❌ Failed to revoke.", show_alert=True)
