import time

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
    else:
        return f"{duration_hours // 24}d"

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
