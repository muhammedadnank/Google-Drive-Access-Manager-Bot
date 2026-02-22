from pyrogram.enums import ButtonStyle
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.database import db
from utils.filters import is_admin
from utils.time import safe_edit
import logging
import csv
import os
import tempfile
from datetime import datetime, timezone, timedelta

LOGGER = logging.getLogger(__name__)


@Client.on_callback_query(filters.regex("^analytics_menu$") & is_admin)
async def show_analytics_dashboard(client, callback_query):
    """Show the expiry analytics dashboard."""
    
    try:
        await safe_edit(callback_query, 
            "📊 **Loading Analytics...**\n\n⏳ Please wait..."
        )
    except:
        pass
    
    # Get analytics data
    analytics = await db.get_expiry_analytics()
    
    # Build the message
    timeline = analytics["timeline"]
    top_folders = analytics["top_folders"]
    top_users = analytics["top_users"]
    total = analytics["total_active"]
    
    text = "📊 **Expiry Analytics**\n\n"
    
    # Timeline section
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "⏰ EXPIRY TIMELINE\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    text += f"⚠️ < 24 hours:     **{timeline['urgent']}** grants\n"
    text += f"📅 1-7 days:       **{timeline['week']}** grants\n"
    text += f"📅 8-30 days:      **{timeline['month']}** grants\n"
    text += f"📅 30+ days:       **{timeline['later']}** grants\n"
    text += f"📊 **Total Active: {total}**\n\n"
    
    # Top folders section
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "📂 TOP EXPIRING FOLDERS\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    if top_folders:
        for i, folder in enumerate(top_folders[:15], 1):  # Show top 15
            folder_name = folder["name"]
            # Truncate long folder names
            if len(folder_name) > 35:
                folder_name = folder_name[:32] + "..."
            text += f"{i}. {folder_name}\n"
            text += f"   📊 {folder['count']} expiring grants\n"
    else:
        text += "No folders with expiring grants\n"
    
    text += "\n"
    
    # Top users section
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "👥 TOP EXPIRING USERS\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    if top_users:
        for i, (email, count) in enumerate(top_users[:15], 1):  # Show top 15
            # Truncate long emails
            email_display = email
            if len(email_display) > 30:
                email_display = email_display[:27] + "..."
            text += f"{i}. `{email_display}`\n"
            text += f"   📊 {count} folder{'s' if count > 1 else ''}\n"
    else:
        text += "No users with expiring grants\n"
    
    text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    # Buttons
    keyboard = [
        [InlineKeyboardButton("📥 Export Full Report", callback_data="analytics_export", style=ButtonStyle.SUCCESS)],
        [InlineKeyboardButton("🔄 Refresh", callback_data="analytics_menu", style=ButtonStyle.PRIMARY)],
        [InlineKeyboardButton("⬅️ Back", callback_data="expiry_menu", style=ButtonStyle.PRIMARY)]
    ]
    
    await safe_edit(callback_query, 
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@Client.on_callback_query(filters.regex("^analytics_export$") & is_admin)
async def export_analytics_report(client, callback_query):
    """Export detailed analytics report as CSV."""
    
    user_id = callback_query.from_user.id
    
    try:
        await callback_query.answer("📥 Generating report...", show_alert=False)
    except:
        pass
    
    # Get analytics data
    analytics = await db.get_expiry_analytics()
    
    # Get all active grants for detailed report
    grants = await db.get_active_grants()
    
    # Create CSV in temp file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='')
    
    try:
        writer = csv.writer(temp_file)
        
        # Write header
        writer.writerow([
            'Email',
            'Folder Name',
            'Role',
            'Expires At',
            'Hours Remaining',
            'Status'
        ])
        
        # Write data
        import time
        now = time.time()
        
        for grant in grants:
            expires_at = grant.get('expires_at', 0)
            hours_remaining = (expires_at - now) / 3600
            
            # Determine status
            if hours_remaining < 24:
                status = "⚠️ URGENT"
            elif hours_remaining < 168:
                status = "📅 This Week"
            elif hours_remaining < 720:
                status = "📅 This Month"
            else:
                status = "📅 Later"
            
            # Format expiry date
            ist = timezone(timedelta(hours=5, minutes=30))
            expiry_dt = datetime.fromtimestamp(expires_at, ist)
            expiry_str = expiry_dt.strftime("%d %b %Y, %I:%M %p")
            
            writer.writerow([
                grant.get('email', ''),
                grant.get('folder_name', ''),
                grant.get('role', '').capitalize(),
                expiry_str,
                f"{hours_remaining:.1f}",
                status
            ])
        
        temp_file.close()
        
        # Send file to user
        caption = (
            "📊 **Expiry Analytics Report**\n\n"
            f"📊 Total Active Grants: **{analytics['total_active']}**\n"
            f"⚠️ Urgent (<24h): **{analytics['timeline']['urgent']}**\n"
            f"📅 This Week: **{analytics['timeline']['week']}**\n"
            f"📅 This Month: **{analytics['timeline']['month']}**\n"
            f"📅 Later: **{analytics['timeline']['later']}**\n\n"
            f"Generated: {datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%d %b %Y, %I:%M %p')} IST"
        )
        
        await callback_query.message.reply_document(
            document=temp_file.name,
            caption=caption,
            file_name=f"expiry_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        await callback_query.answer("✅ Report sent!", show_alert=False)
        
    except Exception as e:
        LOGGER.error(f"Error exporting analytics: {e}")
        await callback_query.answer("❌ Export failed", show_alert=True)
    
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_file.name)
        except:
            pass
