from pyrogram import filters
from services.database import db
from config import ADMIN_IDS

async def is_admin_check(_, __, message):
    user_id = message.from_user.id if message.from_user else None
    if not user_id:
        return False
    # Check if in config or db
    if user_id in ADMIN_IDS:
        return True
    return await db.is_admin(user_id)

is_admin = filters.create(is_admin_check)


def check_state(target_state):
    async def _check(_, __, message):
        user_id = message.from_user.id if message.from_user else None
        if not user_id:
            return False
        
        current_state, _ = await db.get_state(user_id)
        return current_state == target_state

    return filters.create(_check)
