from pyrogram import filters
from services.database import db
from config import ADMIN_IDS

async def is_admin_check(_, __, update):
    # Works for both Message and CallbackQuery
    if hasattr(update, "from_user") and update.from_user:
        user_id = update.from_user.id
    else:
        return False

    if user_id in ADMIN_IDS:
        return True
    return await db.is_admin(user_id)

is_admin = filters.create(is_admin_check)


def check_state(target_state):
    async def _check(_, __, update):
        if hasattr(update, "from_user") and update.from_user:
            user_id = update.from_user.id
        else:
            return False

        current_state, _ = await db.get_state(user_id)
        return current_state == target_state

    return filters.create(_check)
