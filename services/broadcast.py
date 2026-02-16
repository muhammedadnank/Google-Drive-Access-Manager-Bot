from services.database import db
from typing import Dict, Any, Optional
from pyrogram import Client
from config import ADMIN_IDS
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import PeerIdInvalid, ChannelPrivate
import logging
import time
from utils.time import get_current_time_str, format_date

LOGGER = logging.getLogger(__name__)

async def get_channel_config() -> Dict[str, Any]:
    """Retrieve channel configuration from DB."""
    config = await db.get_setting("channel_config")
    
    if config is None:
        config = {
            "channel_id": None,
            "log_grants": True,
            "log_revokes": True,
            "log_role_changes": True,
            "log_bulk": True,
            "log_alerts": True,
            "log_summary": True
        }
        LOGGER.info("📝 Using default channel config (no config in database)")
    
    if config.get("channel_id"):
        try:
            config["channel_id"] = int(str(config["channel_id"]).strip())
            LOGGER.debug(f"📢 Channel ID loaded from database: {config['channel_id']}")
        except Exception as e:
            LOGGER.error(f"❌ Invalid channel_id format: {e} — value was: {config['channel_id']!r}")
            config["channel_id"] = None
    
    return config

async def verify_channel_access(client: Client) -> None:
    """Verify if bot is admin in the configured channel."""
    config = await get_channel_config()
    channel_id = config.get("channel_id")
    
    if not channel_id:
        LOGGER.info("⚠️ No channel configured for broadcasting")
        return

    try:
        chat = await client.get_chat(channel_id)
        LOGGER.info(f"✅ Peer resolved: {chat.title} ({channel_id})")
    except (PeerIdInvalid, ChannelPrivate):
        LOGGER.warning(f"⚠️ get_chat failed. Trying dialogs to warm cache...")
        resolved = False
        async for dialog in client.get_dialogs():
            if dialog.chat.id == channel_id:
                LOGGER.info(f"✅ Found in dialogs: {channel_id}")
                resolved = True
                break
        if not resolved:
            msg = (
                f"⚠️ **Channel Access Failed**: Could not resolve channel `{channel_id}`.\n\n"
                "Bot is not seeing this channel. Please:\n"
                "1. Make sure bot is **Admin** in the channel.\n"
                "2. Send a message in the channel manually.\n"
                "3. Try using **@username** instead of numeric ID."
            )
            LOGGER.error(msg)
            for admin_id in ADMIN_IDS:
                try:
                    await client.send_message(admin_id, msg)
                except Exception:
                    pass
            return
    except Exception as e:
        LOGGER.error(f"Unexpected error resolving channel: {e}")
        return

    try:
        member = await client.get_chat_member(channel_id, "me")

        if member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            msg = f"⚠️ **Channel Config Error**: Bot is NOT an Admin in channel `{channel_id}`!"
            LOGGER.error(msg)
            for admin_id in ADMIN_IDS:
                try:
                    await client.send_message(admin_id, msg)
                except Exception:
                    pass
        elif not member.privileges.can_post_messages:
            msg = f"⚠️ **Channel Permission Error**: Bot cannot post messages to channel `{channel_id}`!"
            LOGGER.error(msg)
            for admin_id in ADMIN_IDS:
                try:
                    await client.send_message(admin_id, msg)
                except Exception:
                    pass
        else:
            LOGGER.info(f"✅ Channel access verified for {channel_id}")

    except Exception as e:
        msg = (
            f"⚠️ **Channel Access Failed**: Could not connect to channel `{channel_id}`.\n"
            f"Error: `{e}`\n\n"
            "**Troubleshooting:**\n"
            "1. Ensure Bot is **Admin** in the channel.\n"
            "2. Send a message in the channel so the bot sees it.\n"
            "3. Try setting the **Channel Username** (@channel) instead of ID."
        )
        LOGGER.error(msg)
        for admin_id in ADMIN_IDS:
            try:
                await client.send_message(admin_id, msg)
            except Exception:
                pass


def format_admin_name(name: str) -> str:
    """
    Format admin name for better display.
    Handles Malayalam and other Unicode names gracefully.
    """
    if not name:
        return "Unknown Admin"
    if len(name) > 30:
        return name[:27] + "..."
    return name


def format_revoke_type(revoke_type: str) -> tuple[str, str]:
    """Format revoke type with emoji and proper description."""
    type_mapping = {
        "revoke_all_user": ("🗑️ Revoke All", "All folders for user"),
        "revoke_all_folder": ("📂 Folder Cleanup", "All users from folder"),
        "selective_revoke": ("☑️ Selective", "Selected folders only"),
        "auto_revoke": ("⏰ Auto-Expire", "Expired access"),
        "manual_revoke": ("👤 Manual", "Single revoke")
    }
    emoji, desc = type_mapping.get(revoke_type, ("🗑️", revoke_type.replace("_", " ").title()))
    return emoji, desc


async def broadcast(client: Client, event_type: str, details: Dict[str, Any]):
    """
    Broadcast an event to the configured channel.

    Args:
        client: Pyrogram Client
        event_type: 'grant', 'revoke', 'role_change', 'bulk_import', 'bulk_revoke', 'alert', 'test'
        details: Dict containing details (email, folder, admin, etc.)
    """
    config = await get_channel_config()
    channel_id = config.get("channel_id")

    if not channel_id:
        LOGGER.debug(f"📢 Broadcast skipped (no channel configured): {event_type}")
        return

    # Check toggles
    if event_type == "grant" and not config.get("log_grants"): return
    if event_type == "revoke" and not config.get("log_revokes"): return
    if event_type == "role_change" and not config.get("log_role_changes"): return
    if "bulk" in event_type and not config.get("log_bulk"): return
    if event_type == "alert" and not config.get("log_alerts"): return
    # Note: bot_start, test, expiry_reminder always broadcast regardless of toggles

    text = ""
    timestamp = get_current_time_str()
    admin_name = format_admin_name(details.get('admin_name', 'Unknown'))

    if event_type == "grant":
        duration = details.get('duration', 'Permanent')
        role_icon = "👁️" if details.get('role') == 'viewer' else "✏️"
        text = (
            f"✅ **ACCESS GRANTED**\n\n"
            f">**User:** {details.get('email')}\n"
            f">**Folder:** {details.get('folder_name')}\n"
            f">**Role:** {role_icon} {details.get('role', 'viewer').capitalize()}\n"
            f">**Duration:** {duration}\n"
            f">**By:** {admin_name}\n\n"
            f"🕒 {timestamp}"
        )

    elif event_type == "revoke":
        text = (
            f"🗑️ **ACCESS REVOKED**\n\n"
            f">**User:** {details.get('email')}\n"
            f">**Folder:** {details.get('folder_name')}\n"
            f">**By:** {admin_name}\n\n"
            f"🕒 {timestamp}"
        )

    elif event_type == "role_change":
        old_role = details.get('old_role', 'viewer').capitalize()
        new_role = details.get('new_role', 'editor').capitalize()
        text = (
            f"🔄 **ROLE CHANGED**\n\n"
            f">**User:** {details.get('email')}\n"
            f">**Folder:** {details.get('folder_name')}\n"
            f">**Change:** {old_role} ➜ **{new_role}**\n"
            f">**By:** {admin_name}\n\n"
            f"🕒 {timestamp}"
        )

    elif event_type == "bulk_import":
        imported = details.get('imported', 0)
        skipped = details.get('skipped', 0)
        errors = details.get('errors', 0)
        total = imported + skipped + errors
        import_pct = (imported / total * 100) if total > 0 else 0
        text = (
            f"📥 **BULK IMPORT**\n\n"
            f">**Imported:** {imported} ({import_pct:.1f}%)\n"
            f">**Skipped:** {skipped}\n"
            f">**Errors:** {errors}\n"
            f">**Total:** {total}\n"
            f">**By:** {admin_name}\n\n"
            f"🕒 {timestamp}"
        )

    elif event_type == "bulk_revoke":
        revoke_type = details.get('type', 'selective_revoke')
        emoji, type_desc = format_revoke_type(revoke_type)
        success = details.get('success', 0)
        failed = details.get('failed', 0)
        total = success + failed
        success_pct = (success / total * 100) if total > 0 else 0
        email = details.get('email')
        email_line = f">**User:** {email}\n" if email else ""
        text = (
            f"{emoji} **BULK REVOKE**\n\n"
            f"{email_line}"
            f">**Type:** {type_desc}\n"
            f">**Revoked:** {success} ({success_pct:.1f}%)\n"
            f">**Failed:** {failed}\n"
            f">**Total:** {total}\n"
            f">**By:** {admin_name}\n\n"
            f"🕒 {timestamp}"
        )

    elif event_type == "alert":
        severity = details.get('severity', 'info')
        severity_emoji = {
            'info': '💡',
            'warning': '⚠️',
            'error': '❌',
            'critical': '🚨'
        }
        emoji = severity_emoji.get(severity, '📢')
        text = (
            f"{emoji} **SYSTEM ALERT**\n\n"
            f">{details.get('message')}\n\n"
            f"🕒 {timestamp}"
        )

    elif event_type == "test":
        text = (
            f"📢 **TEST MESSAGE**\n\n"
            f">**Status:** Active\n"
            f">**Connection:** Established\n"
            f">**Broadcasting:** Enabled\n\n"
            f"🕒 {timestamp}"
        )

    elif event_type == "bot_start":
        text = (
            f"🚀**Bot Restarted Successfully!**\n\n"
            f">**Bot:** {details.get('bot_name', 'Drive Access Manager')}\n"
            f">**ID:** `{details.get('bot_id', 'Unknown')}`\n"
            f">**Pyrofork:** v{details.get('pyrofork_version', 'Unknown')}\n"
            f">**Status:** Online & Ready\n\n"
            f"🕒 {timestamp}"
        )

    elif event_type == "expiry_reminder":
        grants_count = details.get('grants_count', 0)
        time_remaining = details.get('time_remaining', 'soon')
        text = (
            f"⏰ **EXPIRY REMINDER**\n\n"
            f">**Expiring:** {grants_count} grant(s) {time_remaining}\n"
            f">**Action:** Review expiring grants in dashboard\n\n"
            f"🕒 {timestamp}"
        )

    if not text:
        LOGGER.warning(f"⚠️ Unknown broadcast event type: {event_type}")
        return

    try:
        await client.send_message(channel_id, text)
        LOGGER.info(f"📢 Broadcast sent: {event_type} to channel {channel_id}")
    except Exception as e:
        LOGGER.error(f"❌ Failed to broadcast to channel {channel_id}: {e}")


async def send_daily_summary(client: Client):
    """Send daily activity summary."""
    config = await get_channel_config()
    channel_id = config.get("channel_id")

    if not channel_id or not config.get("log_summary"):
        LOGGER.debug("📊 Daily summary skipped (not configured)")
        return

    now = time.time()
    day_ago = now - 86400

    logs = await db.logs.find({"timestamp": {"$gte": day_ago}}).to_list(length=None)

    if not logs:
        LOGGER.info("📊 Daily summary skipped (no activity)")
        return

    grants = sum(1 for l in logs if l['action'] == 'grant')
    revokes = sum(1 for l in logs if l['action'] in ('revoke', 'auto_revoke'))
    role_changes = sum(1 for l in logs if l['action'] == 'role_change')
    bulk_imports = sum(1 for l in logs if l['action'] == 'bulk_import')
    total_actions = len(logs)

    # Includes permanent (no expiry) grants
    active_grants = await db.grants.count_documents({
        "status": "active",
        "$or": [
            {"expires_at": {"$gt": now}},
            {"expires_at": None},
            {"expires_at": {"$exists": False}}
        ]
    })

    expiring_soon = await db.grants.count_documents({
        "status": "active",
        "expires_at": {"$gt": now, "$lt": now + 86400}
    })

    date_str = format_date(now)

    text = (
        f"📊 **DAILY SUMMARY** — {date_str}\n\n"
        f">**Grants:** {grants}\n"
        f">**Revokes:** {revokes}\n"
        f">**Role Changes:** {role_changes}\n"
        f">**Bulk Imports:** {bulk_imports}\n"
        f">**Total Actions:** {total_actions}\n\n"
        f">**Active Grants:** {active_grants}\n"
        f">**Expiring Soon:** {expiring_soon}\n\n"
        f"🕒 {get_current_time_str()}"
    )

    try:
        await client.send_message(channel_id, text)
        LOGGER.info("📊 Daily summary sent successfully")
    except Exception as e:
        LOGGER.error(f"❌ Failed to send daily summary: {e}")


async def send_weekly_report(client: Client):
    """Send weekly analytics report."""
    config = await get_channel_config()
    channel_id = config.get("channel_id")

    if not channel_id or not config.get("log_summary"):
        return

    now = time.time()
    week_ago = now - (7 * 86400)

    logs = await db.logs.find({"timestamp": {"$gte": week_ago}}).to_list(length=None)

    if not logs:
        return

    total_actions = len(logs)
    grants = sum(1 for l in logs if l['action'] == 'grant')
    revokes = sum(1 for l in logs if l['action'] in ('revoke', 'auto_revoke'))

    active_grants = await db.grants.count_documents({
        "status": "active",
        "$or": [
            {"expires_at": {"$gt": now}},
            {"expires_at": None},
            {"expires_at": {"$exists": False}}
        ]
    })

    admin_counts = {}
    for log in logs:
        admin = log.get('admin_name', 'Unknown')
        admin_counts[admin] = admin_counts.get(admin, 0) + 1

    top_admin = max(admin_counts.items(), key=lambda x: x[1]) if admin_counts else ("N/A", 0)

    text = (
        f"📈 **WEEKLY REPORT** — Last 7 Days\n\n"
        f">**Total Actions:** {total_actions}\n"
        f">**Grants:** {grants}\n"
        f">**Revokes:** {revokes}\n"
        f">**Active Grants:** {active_grants}\n\n"
        f">**Top Admin:** {format_admin_name(top_admin[0])} ({top_admin[1]} actions)\n\n"
        f"🕒 {get_current_time_str()}"
    )

    try:
        await client.send_message(channel_id, text)
        LOGGER.info("📊 Weekly report sent successfully")
    except Exception as e:
        LOGGER.error(f"❌ Failed to send weekly report: {e}")
