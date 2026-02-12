from services.database import db
from config import ADMIN_IDS
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import PeerIdInvalid, ChannelPrivate
import logging
import time
from utils.time import get_current_time_str

LOGGER = logging.getLogger(__name__)

async def get_channel_config():
    """Retrieve channel configuration from DB."""
    # Assuming we store this in 'settings' collection under 'channel_config'
    # or a separate 'channel_settings' doc.
    # Let's use a simple key-value in 'settings' collection
    config = await db.get_setting("channel_config")
    
    if config and config.get("channel_id"):
        try:
            config["channel_id"] = int(str(config["channel_id"]).strip())
        except:
            pass

    if not config:
        # Default config
        config = {
            "channel_id": None,
            "log_grants": True,
            "log_revokes": True,
            "log_role_changes": True,
            "log_bulk": True,
            "log_alerts": True,
            "log_summary": True
        }
    return config

    return config

async def verify_channel_access(client):
    """Verify if bot is admin in the configured channel."""
    config = await get_channel_config()
    channel_id = config.get("channel_id")
    
    if not channel_id:
        return

    # Step 1: Force resolve the peer first via get_chat
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
                except:
                    pass
            return
    except Exception as e:
        LOGGER.error(f"Unexpected error resolving channel: {e}")
        return

    # Step 2: Now check admin status
    try:
        member = await client.get_chat_member(channel_id, "me")

        if member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            msg = f"⚠️ **Channel Config Error**: Bot is NOT an Admin in channel `{channel_id}`!"
            LOGGER.error(msg)
            for admin_id in ADMIN_IDS:
                try:
                    await client.send_message(admin_id, msg)
                except:
                    pass
        elif not member.privileges.can_post_messages:
            msg = f"⚠️ **Channel Permission Error**: Bot cannot post messages to channel `{channel_id}`!"
            LOGGER.error(msg)
            for admin_id in ADMIN_IDS:
                try:
                    await client.send_message(admin_id, msg)
                except:
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
            except:
                pass

async def broadcast(client, event_type, details):
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
        return

    # Check toggles
    if event_type == "grant" and not config.get("log_grants"): return
    if event_type == "revoke" and not config.get("log_revokes"): return
    if event_type == "role_change" and not config.get("log_role_changes"): return
    if "bulk" in event_type and not config.get("log_bulk"): return
    if event_type == "alert" and not config.get("log_alerts"): return
    
    # Format Message
    text = ""
    timestamp = get_current_time_str()
    
    if event_type == "grant":
        text = (
            "✅ **ACCESS GRANTED**\n\n"
            f"User: {details.get('email')}\n"
            f"Folder: **{details.get('folder_name')}**\n"
            f"Role: {details.get('role').capitalize()}\n"
            f"Duration: {details.get('duration', 'Permanent')}\n"
            f"By: {details.get('admin_name')}\n\n"
            f"🕒 {timestamp}"
        )
    
    elif event_type == "revoke":
        text = (
            "🗑 **ACCESS REVOKED**\n\n"
            f"User: {details.get('email')}\n"
            f"Folder: **{details.get('folder_name')}**\n"
            f"By: **{details.get('admin_name')}**\n\n"
            f"🕒 {timestamp}"
        )
        
    elif event_type == "role_change":
        text = (
            "🔄 **ROLE CHANGED**\n\n"
            f"User: {details.get('email')}\n"
            f"Folder: **{details.get('folder_name')}**\n"
            f"New Role: {details.get('new_role').capitalize()}\n"
            f"By: {details.get('admin_name')}\n\n"
            f"🕒 {timestamp}"
        )
        
    elif event_type == "bulk_import":
        text = (
            "📥 **BULK IMPORT COMPLETED**\n\n"
            f"Imported: {details.get('imported')}\n"
            f"Skipped: {details.get('skipped')}\n"
            f"Errors: {details.get('errors')}\n"
            f"By: {details.get('admin_name')}\n\n"
            f"🕒 {timestamp}"
        )
        
    elif event_type == "bulk_revoke":
        text = (
            "🗑 **BULK REVOKE EXECUTED**\n\n"
            f"Type: {details.get('type')}\n"
            f"Revoked: {details.get('success')}\n"
            f"Failed: {details.get('failed')}\n"
            f"By: {details.get('admin_name')}\n\n"
            f"🕒 {timestamp}"
        )
        
    elif event_type == "alert":
        text = (
            "🔴 **SYSTEM ALERT**\n\n"
            f"{details.get('message')}\n\n"
            f"🕒 {timestamp}"
        )
        
    elif event_type == "test":
        text = (
            "📢 **TEST MESSAGE**\n\n"
            "Drive Access Manager Channel Integration is working correctly.\n\n"
            f"🕒 {timestamp}"
        )
        
    elif event_type == "bot_start":
        text = (
            "✅ **Bot Restarted Successfully!**\n\n"
            f"🤖 **Bot Name:** {details.get('bot_name', 'Unknown')}\n"
            f"🆔 **Bot ID:** `{details.get('bot_id', 'Unknown')}`\n"
            f"🆚 **Pyrogram Version:** v{details.get('pyro_version', 'Unknown')}\n"
            f"📅 **Date:** {timestamp} (IST)"
        )

    if not text:
        return

    try:
        await client.send_message(channel_id, text)
    except Exception as e:
        LOGGER.error(f"Failed to broadcast to channel {channel_id}: {e}")

async def send_daily_summary(client):
    """Send daily activity summary."""
    config = await get_channel_config()
    channel_id = config.get("channel_id")
    
    if not channel_id or not config.get("log_summary"):
        return

    # Calculate stats for last 24h
    now = time.time()
    day_ago = now - 86400
    
    # We need a way to count logs from DB
    # Assuming db.logs has a 'timestamp' field
    logs = await db.logs.find({"timestamp": {"$gte": day_ago}}).to_list(length=None)
    
    if not logs:
        # Optional: Don't send if empty, or send "No activity"
        return

    grants = sum(1 for l in logs if l['action'] == 'grant')
    revokes = sum(1 for l in logs if l['action'] in ('revoke', 'auto_revoke'))
    role_changes = sum(1 for l in logs if l['action'] == 'role_change')
    bulk_imports = sum(1 for l in logs if l['action'] == 'bulk_import')
    
    date_str = time.strftime('%d %b %Y', time.localtime(now))
    
    text = (
        f"📊 **DAILY SUMMARY — {date_str}**\n\n"
        f"➕ Grants: `{grants}`\n"
        f"🗑 Revokes: `{revokes}`\n"
        f"🔄 Role Changes: `{role_changes}`\n"
        f"📥 Bulk Imports: `{bulk_imports}`\n\n"
        f"Total Actions: `{len(logs)}`"
    )
    
    try:
        await client.send_message(channel_id, text)
    except Exception as e:
        LOGGER.error(f"Failed to send daily summary: {e}")
