from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, ADMIN_IDS
import time
import logging

LOGGER = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self._client = None
        self.db = None
        self.admins = None
        self.logs = None
        self.settings = None
        self.states = None
        self.cache = None
        self.grants = None

    async def init(self):
        """Initialize database connection and verify indices."""
        if not MONGO_URI:
            LOGGER.error("MONGO_URI is not set!")
            return

        self._client = AsyncIOMotorClient(MONGO_URI)
        self.db = self._client.drive_bot
        
        self.admins = self.db.admins
        self.logs = self.db.logs
        self.settings = self.db.settings
        self.states = self.db.states
        self.cache = self.db.cache
        self.grants = self.db.grants

        # Bootstrap initial admins from config
        if ADMIN_IDS:
            for admin_id in ADMIN_IDS:
                await self.add_admin(admin_id, "Config Admin")
        
        LOGGER.info("Database initialized successfully.")

    # --- Admin Management ---
    async def is_admin(self, user_id):
        return await self.admins.find_one({"user_id": int(user_id)}) is not None

    async def add_admin(self, user_id, name):
        if not await self.is_admin(user_id):
            await self.admins.insert_one({
                "user_id": int(user_id),
                "name": name,
                "added_at": time.time()
            })
            return True
        return False

    async def remove_admin(self, user_id):
        result = await self.admins.delete_one({"user_id": int(user_id)})
        return result.deleted_count > 0

    async def get_all_admins(self):
        cursor = self.admins.find({})
        return [admin async for admin in cursor]

    # --- Logging ---
    async def log_action(self, admin_id, admin_name, action, details):
        """
        Log an administrative action with structured type.
        action: 'grant' | 'remove' | 'role_change'
        details: dict containing email, folder_name, role, etc.
        """
        log_entry = {
            "type": action,
            "admin_id": admin_id,
            "admin_name": admin_name,
            "action": action,
            "details": details,
            "timestamp": time.time(),
            "is_deleted": False
        }
        await self.logs.insert_one(log_entry)

    async def get_logs(self, limit=50, skip=0, log_type=None):
        """Get logs, excluding soft-deleted. Optionally filter by type."""
        query = {"is_deleted": {"$ne": True}}
        if log_type:
            query["type"] = log_type
        cursor = self.logs.find(query).sort("timestamp", -1).skip(skip).limit(limit)
        total = await self.logs.count_documents(query)
        logs = [log async for log in cursor]
        return logs, total

    async def clear_logs(self):
        """Soft delete all logs."""
        await self.logs.update_many(
            {"is_deleted": {"$ne": True}},
            {"$set": {"is_deleted": True, "deleted_at": time.time()}}
        )

    # --- Settings ---
    async def get_setting(self, key, default=None):
        doc = await self.settings.find_one({"key": key})
        return doc["value"] if doc else default

    async def update_setting(self, key, value):
        await self.settings.update_one(
            {"key": key},
            {"$set": {"value": value}},
            upsert=True
        )

    # --- State Management (For Conversation Flow) ---
    async def set_state(self, user_id, state, data=None):
        if data is None:
            data = {}
        await self.states.update_one(
            {"user_id": int(user_id)},
            {"$set": {"state": state, "data": data, "updated_at": time.time()}},
            upsert=True
        )

    async def get_state(self, user_id):
        doc = await self.states.find_one({"user_id": int(user_id)})
        if doc:
            return doc.get("state"), doc.get("data", {})
        return None, {}

    async def delete_state(self, user_id):
        await self.states.delete_one({"user_id": int(user_id)})

    # --- Folder Cache ---
    async def get_cached_folders(self, ttl_minutes=10):
        """Return cached folders if fresh (within TTL), else None."""
        doc = await self.cache.find_one({"key": "folders"})
        if doc:
            age = time.time() - doc.get("cached_at", 0)
            if age < ttl_minutes * 60:
                return doc.get("folders", [])
        return None

    async def set_cached_folders(self, folders):
        """Store folder list with current timestamp."""
        await self.cache.update_one(
            {"key": "folders"},
            {"$set": {"folders": folders, "cached_at": time.time()}},
            upsert=True
        )

    async def clear_folder_cache(self):
        """Invalidate folder cache."""
        await self.cache.delete_one({"key": "folders"})

    # --- Timed Grants ---
    async def add_timed_grant(self, admin_id, email, folder_id, folder_name, role, duration_hours):
        """Store a timed grant with expiry."""
        grant = {
            "admin_id": admin_id,
            "email": email,
            "folder_id": folder_id,
            "folder_name": folder_name,
            "role": role,
            "granted_at": time.time(),
            "expires_at": time.time() + (duration_hours * 3600),
            "duration_hours": duration_hours,
            "status": "active"
        }
        await self.grants.insert_one(grant)

    async def get_expired_grants(self):
        """Get grants past their expiry time."""
        return await self.grants.find({
            "status": "active",
            "expires_at": {"$lte": time.time()}
        }).to_list(length=100)

    async def get_active_grants(self):
        """Get all active timed grants for dashboard."""
        return await self.grants.find({
            "status": "active",
            "expires_at": {"$gt": time.time()}
        }).sort("expires_at", 1).to_list(length=100)

    async def mark_grant_expired(self, grant_id):
        """Mark a grant as auto-revoked."""
        from bson import ObjectId
        await self.grants.update_one(
            {"_id": ObjectId(grant_id) if isinstance(grant_id, str) else grant_id},
            {"$set": {"status": "expired", "revoked_at": time.time()}}
        )

    async def extend_grant(self, grant_id, extra_hours):
        """Extend a grant's expiry."""
        from bson import ObjectId
        await self.grants.update_one(
            {"_id": ObjectId(grant_id) if isinstance(grant_id, str) else grant_id},
            {"$inc": {"expires_at": extra_hours * 3600}}
        )

    async def revoke_grant(self, grant_id):
        """Manually revoke a timed grant."""
        from bson import ObjectId
        await self.grants.update_one(
            {"_id": ObjectId(grant_id) if isinstance(grant_id, str) else grant_id},
            {"$set": {"status": "revoked", "revoked_at": time.time()}}
        )

db = Database()
