import time
from datetime import datetime, timezone, timedelta


async def safe_edit(target, text, reply_markup=None, **kwargs):
    """Edit a message, silently ignoring MESSAGE_NOT_MODIFIED errors."""
    try:
        if reply_markup is not None:
            kwargs["reply_markup"] = reply_markup
        # target can be callback_query, message, or callback_query.message
        if hasattr(target, "edit_message_text"):
            return await target.edit_message_text(text, **kwargs)
        else:
            return await target.edit_text(text, **kwargs)
    except Exception as e:
        if "MESSAGE_NOT_MODIFIED" not in str(e):
            raise

IST = timezone(timedelta(hours=5, minutes=30))

def get_current_time_str():
    """Get current time string in IST (Kolkata) with AM/PM."""
    return datetime.now(IST).strftime('%d %b %Y, %I:%M %p')

def format_timestamp(ts):
    """Format Unix timestamp to IST string with AM/PM."""
    return datetime.fromtimestamp(ts, IST).strftime('%d %b %Y, %I:%M %p')

def format_date(ts):
    """Format Unix timestamp to IST date string."""
    return datetime.fromtimestamp(ts, IST).strftime('%d %b %Y')

def get_uptime(start_timestamp):
    """Calculate formatted uptime string."""
    uptime_secs = int(time.time() - start_timestamp)
    days = uptime_secs // 86400
    hours = (uptime_secs % 86400) // 3600
    minutes = (uptime_secs % 3600) // 60
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    return f"{hours}h {minutes}m"

def format_duration(duration_hours):
    """Format duration hours for display."""
    if duration_hours == 0:
        return "♾ Permanent"
    elif duration_hours < 24:
        return f"{duration_hours}h"
    elif duration_hours % 24 == 0:
        return f"{duration_hours // 24}d"
    else:
        days = duration_hours // 24
        hours = duration_hours % 24
        return f"{days}d {hours}h"

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

def parse_custom_duration(text: str):
    """
    Parse a custom duration string into total hours.
    Returns total hours (int) or None if invalid.
    Examples:
        '45' -> 1080 (45 days)
        '45d' / '45 days' -> 1080
        '12h' / '12 hours' -> 12
        '1d 12h' -> 36
    """
    import re
    if not text or not isinstance(text, str):
        return None

    clean_text = text.strip().lower()

    if "-" in clean_text:
        return None

    if clean_text.isdigit():
        days = int(clean_text)
        if 0 < days <= 3650:
            return days * 24
        return None

    days_match = re.search(r'(\d+)\s*(?:d|day|days)', clean_text)
    hours_match = re.search(r'(\d+)\s*(?:h|hr|hrs|hour|hours)', clean_text)

    if not days_match and not hours_match:
        return None

    total_hours = 0
    if days_match:
        total_hours += int(days_match.group(1)) * 24
    if hours_match:
        total_hours += int(hours_match.group(1))

    if 0 < total_hours <= 87600:
        return total_hours

    return None

