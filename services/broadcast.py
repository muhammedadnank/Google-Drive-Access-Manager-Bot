from services.database import db
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
            f"User: `{details.get('email')}`\n"
            f"Folder: {details.get('folder_name')}\n"
            f"Role: {details.get('role').capitalize()}\n"
            f"Duration: {details.get('duration', 'Permanent')}\n"
            f"By: {details.get('admin_name')}\n\n"
            f"🕒 {timestamp}"
        )
    
    elif event_type == "revoke":
        text = (
            "🗑 **ACCESS REVOKED**\n\n"
            f"User: `{details.get('email')}`\n"
            f"Folder: {details.get('folder_name')}\n"
            f"By: {details.get('admin_name')}\n\n"
            f"🕒 {timestamp}"
        )
        
    elif event_type == "role_change":
        text = (
            "🔄 **ROLE CHANGED**\n\n"
            f"User: `{details.get('email')}`\n"
            f"Folder: {details.get('folder_name')}\n"
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
