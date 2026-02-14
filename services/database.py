from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from config import MONGO_URI, ADMIN_IDS
import time
import re
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
        
        # Create Indexes for Search
        await self.grants.create_index("email")
        await self.grants.create_index("folder_id")
        await self.grants.create_index("role")
        await self.grants.create_index("status")
        await self.grants.create_index("granted_at")
        # Compound index for the most common active-grant expiry queries
        await self.grants.create_index([("status", 1), ("expires_at", 1)])
        # Index for log filtering
        await self.logs.create_index("action")
        await self.logs.create_index("timestamp")
        
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
        log_entry = {
            "admin_id": admin_id,
            "admin_name": admin_name,
            "action": action,
            "details": details,
            "timestamp": time.time(),
            "is_deleted": False
        }
        await self.logs.insert_one(log_entry)

    async def get_logs(self, limit=50, skip=0, log_type=None):
        """Get logs, excluding soft-deleted. Optionally filter by action type."""
        query = {"is_deleted": {"$ne": True}}
        if log_type:
            query["action"] = log_type
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
        doc = await self.cache.find_one({"key": "folders"})
        if doc:
            age = time.time() - doc.get("cached_at", 0)
            if age < ttl_minutes * 60:
                return doc.get("folders", [])
        return None

    async def set_cached_folders(self, folders):
        await self.cache.update_one(
            {"key": "folders"},
            {"$set": {"folders": folders, "cached_at": time.time()}},
            upsert=True
        )

    async def clear_folder_cache(self):
        await self.cache.delete_one({"key": "folders"})

    # --- Timed Grants ---
    async def add_timed_grant(self, admin_id, email, folder_id, folder_name, role, duration_hours):
        now = time.time()
        grant = {
            "admin_id": admin_id,
            "email": email,
            "folder_id": folder_id,
            "folder_name": folder_name,
            "role": role,
            "granted_at": now,
            "expires_at": now + (duration_hours * 3600),
            "duration_hours": duration_hours,
            "status": "active"
        }
        await self.grants.insert_one(grant)

    async def get_expired_grants(self):
        return await self.grants.find({
            "status": "active",
            "expires_at": {"$lte": time.time()}
        }).to_list(length=100)

    async def get_active_grants(self):
        return await self.grants.find({
            "status": "active",
            "expires_at": {"$gt": time.time()}
        }).sort("expires_at", 1).to_list(length=100)

    async def mark_grant_expired(self, grant_id):
        await self.grants.update_one(
            {"_id": ObjectId(grant_id) if isinstance(grant_id, str) else grant_id},
            {"$set": {"status": "expired", "expired_at": time.time()}}
        )

    async def mark_grant_revocation_failed(self, grant_id):
        await self.grants.update_one(
            {"_id": ObjectId(grant_id) if isinstance(grant_id, str) else grant_id},
            {"$set": {"status": "revocation_failed", "failed_at": time.time()}}
        )

    async def extend_grant(self, grant_id, extra_hours):
        await self.grants.update_one(
            {"_id": ObjectId(grant_id) if isinstance(grant_id, str) else grant_id},
            {"$inc": {"expires_at": extra_hours * 3600}}
        )

    async def revoke_grant(self, grant_id):
        await self.grants.update_one(
            {"_id": ObjectId(grant_id) if isinstance(grant_id, str) else grant_id},
            {"$set": {"status": "revoked", "revoked_at": time.time()}}
        )

    # --- Stats / Analytics ---
    async def get_stats(self):
        """Get analytics data for /stats command."""
        now = time.time()
        day_ago = now - 86400
        week_ago = now - 604800
        month_ago = now - 2592000
        
        query_base = {"is_deleted": {"$ne": True}}
        
        # Counts by time period
        today_count = await self.logs.count_documents({**query_base, "timestamp": {"$gte": day_ago}})
        week_count = await self.logs.count_documents({**query_base, "timestamp": {"$gte": week_ago}})
        month_count = await self.logs.count_documents({**query_base, "timestamp": {"$gte": month_ago}})
        total_count = await self.logs.count_documents(query_base)
        
        # Active grants
        active_grants = await self.grants.count_documents({"status": "active", "expires_at": {"$gt": now}})
        
        # Most accessed folder (from logs)
        top_folder_pipeline = [
            {"$match": {**query_base, "timestamp": {"$gte": month_ago}}},
            {"$group": {"_id": "$details.folder_name", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 1}
        ]
        top_folder_result = await self.logs.aggregate(top_folder_pipeline).to_list(1)
        top_folder = top_folder_result[0]["_id"] if top_folder_result and top_folder_result[0].get("_id") else "N/A"
        top_folder_count = top_folder_result[0]["count"] if top_folder_result else 0
        
        # Top admin this month
        top_admin_pipeline = [
            {"$match": {**query_base, "timestamp": {"$gte": month_ago}, "admin_id": {"$ne": 0}}},
            {"$group": {"_id": "$admin_name", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 1}
        ]
        top_admin_result = await self.logs.aggregate(top_admin_pipeline).to_list(1)
        top_admin = top_admin_result[0]["_id"] if top_admin_result and top_admin_result[0].get("_id") else "N/A"
        top_admin_count = top_admin_result[0]["count"] if top_admin_result else 0
        
        return {
            "today": today_count,
            "week": week_count,
            "month": month_count,
            "total": total_count,
            "active_grants": active_grants,
            "top_folder": top_folder,
            "top_folder_count": top_folder_count,
            "top_admin": top_admin,
            "top_admin_count": top_admin_count
        }

    # --- Advanced Search ---
    async def search_grants(self, query=None, limit=20, skip=0):
        """Search grants with complex filters."""
        if query is None:
            query = {"status": "active"}
            
        # Support regex for email/folder_name if specified as string
        # (Caller should handle regex construction if needed)
        
        cursor = self.grants.find(query).sort("granted_at", -1).skip(skip).limit(limit)
        total = await self.grants.count_documents(query)
        results = [grant async for grant in cursor]
        return results, total


    async def get_grants_by_email(self, email):
        """Get all active grants for a specific email address (Secured)."""
        if not isinstance(email, str):
            LOGGER.warning(f"❌ Possible NoSQL injection attempt: {email}")
            return []
            
        email = email.strip().lower()
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            return []

        return await self.grants.find({
            "email": email,
            "status": "active"
        }).to_list(length=1000)

    async def get_grants_by_folder(self, folder_id):
        """Get active grants for a specific folder (Limited)."""
        return await self.grants.find({
            "folder_id": folder_id,
            "status": "active"
        }).to_list(length=1000) # Safety limit

    async def get_expiring_soon_count(self, hours=24):
        """Count grants expiring within the given hours."""
        now = time.time()
        return await self.grants.count_documents({
            "status": "active",
            "expires_at": {"$gt": now, "$lt": now + hours * 3600}
        })

db = Database()