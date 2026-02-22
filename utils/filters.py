from pyrogram import filters
from services.database import db
from config import ADMIN_IDS


async def is_admin_check(_, __, update):
    # Works for both Message and CallbackQuery
    if hasattr(update, "from_user") and update.from_user:
        user_id = update.from_user.id
    else:
        return False

    # First check: is user in ADMIN_IDS from config (no DB needed)
    if user_id in ADMIN_IDS:
        return True

    # Second check: DB lookup — only if DB is initialized
    try:
        if db.admins is None:
            return False
        return await db.is_admin(user_id)
    except Exception:
        return False


is_admin = filters.create(is_admin_check)


def check_state(target_state):
    async def _check(_, __, update):
        if hasattr(update, "from_user") and update.from_user:
            user_id = update.from_user.id
        else:
            return False

        # Never capture slash-commands in state handlers.
        text = getattr(update, "text", None)
        if isinstance(text, str) and text.strip().startswith("/"):
            return False

        try:
            if db.states is None:
                return False
            current_state, _ = await db.get_state(user_id)
            return current_state == target_state
        except Exception:
            return False

    return filters.create(_check)
