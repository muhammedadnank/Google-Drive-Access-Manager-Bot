"""
Admin Decorators
VJ-FILTER-BOT inspired authorization system
"""

from functools import wraps
from pyrogram import Client
from pyrogram.types import Message, CallbackQuery

from config import Config
from templates.messages import Messages
from utils.logger import logger

def admin_only(func):
    """
    Admin verification decorator (VJ-inspired)
    
    Only allows administrators to execute the command.
    Sends error message to non-admins.
    
    Usage:
        @Client.on_message(filters.command("admin_cmd"))
        @admin_only
        async def admin_command(client, message):
            # Your admin code here
    """
    @wraps(func)
    async def wrapper(client: Client, message: Message):
        user_id = message.from_user.id
        
        # Check if user is admin
        if user_id not in Config.ADMIN_IDS:
            await message.reply_text(
                Messages.ERROR_PERMISSION_DENIED,
                quote=True
            )
            logger.warning(f"Unauthorized access attempt by {user_id}")
            return
        
        # User is admin, proceed
        return await func(client, message)
    
    return wrapper


def super_admin_only(func):
    """
    Super admin verification decorator
    
    Only allows the first admin (super admin) to execute.
    Used for system-critical commands.
    
    Usage:
        @Client.on_message(filters.command("system_cmd"))
        @super_admin_only
        async def system_command(client, message):
            # Your super admin code here
    """
    @wraps(func)
    async def wrapper(client: Client, message: Message):
        user_id = message.from_user.id
        
        # Check if user is super admin
        if user_id != Config.SUPER_ADMIN_ID:
            await message.reply_text(
                "⛔ **Super Admin Only!**\n\n"
                "This command requires super admin privileges.\n\n"
                "Only the bot owner can use this command.",
                quote=True
            )
            logger.warning(f"Unauthorized super admin access by {user_id}")
            return
        
        # User is super admin, proceed
        return await func(client, message)
    
    return wrapper


def callback_admin_only(func):
    """
    Admin verification for callback queries (VJ pattern)
    
    Only allows administrators to use inline buttons.
    
    Usage:
        @Client.on_callback_query(filters.regex("^admin_"))
        @callback_admin_only
        async def admin_callback(client, callback_query):
            # Your callback code here
    """
    @wraps(func)
    async def wrapper(client: Client, callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        
        # Check if user is admin
        if user_id not in Config.ADMIN_IDS:
            await callback_query.answer(
                "⛔ Admin only!",
                show_alert=True
            )
            logger.warning(f"Unauthorized callback by {user_id}: {callback_query.data}")
            return
        
        # User is admin, proceed
        return await func(client, callback_query)
    
    return wrapper


def require_state(required_state):
    """
    State verification decorator
    
    Ensures user is in the correct conversation state.
    
    Args:
        required_state: The state user must be in
    
    Usage:
        @Client.on_message(filters.text & filters.private)
        @require_state("AWAITING_EMAIL")
        async def handle_email(client, message):
            # User is in correct state
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(client: Client, message: Message):
            from services.database import Database
            
            db = Database()
            user_state = await db.get_user_state(message.from_user.id)
            
            if user_state != required_state:
                # User not in correct state, ignore
                return
            
            return await func(client, message)
        
        return wrapper
    return decorator


def rate_limit(max_requests: int = 10, time_window: int = 60):
    """
    Rate limiting decorator (VJ-inspired)
    
    Prevents command spam by limiting requests per time window.
    
    Args:
        max_requests: Maximum requests allowed
        time_window: Time window in seconds
    
    Usage:
        @Client.on_message(filters.command("grant"))
        @rate_limit(max_requests=5, time_window=60)
        async def grant_command(client, message):
            # Limited to 5 requests per minute
    """
    from datetime import datetime, timedelta
    from collections import defaultdict
    
    # Store requests per user
    requests = defaultdict(list)
    
    def decorator(func):
        @wraps(func)
        async def wrapper(client: Client, message: Message):
            if not Config.RATE_LIMIT_ENABLED:
                return await func(client, message)
            
            user_id = message.from_user.id
            now = datetime.utcnow()
            cutoff = now - timedelta(seconds=time_window)
            
            # Clean old requests
            requests[user_id] = [
                req_time for req_time in requests[user_id]
                if req_time > cutoff
            ]
            
            # Check limit
            if len(requests[user_id]) >= max_requests:
                await message.reply_text(
                    "⏳ **Rate Limit Exceeded!**\n\n"
                    f"Please wait {time_window} seconds before trying again.\n\n"
                    "This limit prevents spam and ensures smooth operation.",
                    quote=True
                )
                logger.warning(f"Rate limit hit by {user_id}")
                return
            
            # Add current request
            requests[user_id].append(now)
            
            return await func(client, message)
        
        return wrapper
    return decorator


def log_command(command_name: str = None):
    """
    Command logging decorator
    
    Automatically logs command usage to database.
    
    Args:
        command_name: Name to log (defaults to function name)
    
    Usage:
        @Client.on_message(filters.command("stats"))
        @log_command("stats")
        async def stats_command(client, message):
            # Command usage is automatically logged
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(client: Client, message: Message):
            from services.database import Database
            
            cmd_name = command_name or func.__name__
            
            # Log command usage
            try:
                db = Database()
                await db.log_command_usage(
                    user_id=message.from_user.id,
                    username=message.from_user.username,
                    command=cmd_name,
                    timestamp=datetime.utcnow()
                )
            except Exception as e:
                logger.error(f"Failed to log command usage: {e}")
            
            return await func(client, message)
        
        return wrapper
    return decorator


def error_handler(func):
    """
    Global error handler decorator (VJ pattern)
    
    Catches and handles exceptions gracefully.
    
    Usage:
        @Client.on_message(filters.command("risky_cmd"))
        @error_handler
        async def risky_command(client, message):
            # Any errors will be caught and handled
    """
    @wraps(func)
    async def wrapper(client: Client, message: Message):
        try:
            return await func(client, message)
            
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            
            error_msg = Messages.ERROR_GENERIC.format(
                error_message=str(e)
            )
            
            try:
                await message.reply_text(error_msg, quote=True)
            except:
                # Even error message failed, just log
                logger.error("Failed to send error message to user")
    
    return wrapper


def callback_error_handler(func):
    """
    Error handler for callback queries
    
    Catches and handles callback errors gracefully.
    
    Usage:
        @Client.on_callback_query(filters.regex("^btn_"))
        @callback_error_handler
        async def button_callback(client, callback_query):
            # Errors are handled automatically
    """
    @wraps(func)
    async def wrapper(client: Client, callback_query: CallbackQuery):
        try:
            return await func(client, callback_query)
            
        except Exception as e:
            logger.error(f"Callback error in {func.__name__}: {e}", exc_info=True)
            
            try:
                await callback_query.answer(
                    "❌ An error occurred. Please try again.",
                    show_alert=True
                )
            except:
                logger.error("Failed to send error alert")
    
    return wrapper


# Combination decorators for common patterns
def admin_command(func):
    """
    Combined decorator for admin commands
    
    Applies: admin_only + error_handler + log_command
    
    Usage:
        @Client.on_message(filters.command("admin_cmd"))
        @admin_command
        async def my_admin_command(client, message):
            # Fully protected admin command
    """
    from datetime import datetime
    
    return error_handler(
        log_command(func.__name__)(
            admin_only(func)
        )
    )


def admin_callback(func):
    """
    Combined decorator for admin callbacks
    
    Applies: callback_admin_only + callback_error_handler
    
    Usage:
        @Client.on_callback_query(filters.regex("^admin_"))
        @admin_callback
        async def admin_button(client, callback_query):
            # Fully protected admin callback
    """
    return callback_error_handler(
        callback_admin_only(func)
    )
