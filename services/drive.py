"""
Drive Service with per-user OAuth support.
Uses a Render-compatible redirect URI approach:
- Redirect URI points to the bot's own Render URL
- OR user manually pastes the full redirect URL / code into the bot
"""

import os
import asyncio
import json
import logging
from httplib2 import Http
from oauth2client.client import OAuth2WebServerFlow, FlowExchangeError, OAuth2Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

LOGGER = logging.getLogger(__name__)

OAUTH_SCOPE = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/gmail.send",   # email notifications
]

# Pending OAuth flows: {user_id: flow}
_pending_flows: dict = {}


def _get_redirect_uri():
    """
    Use RENDER_EXTERNAL_URL if available (production),
    otherwise localhost (local dev).
    """
    render_url = os.environ.get("RENDER_EXTERNAL_URL", "").rstrip("/")
    if render_url:
        return f"{render_url}/oauth/callback"
    return "http://localhost:8080/oauth/callback"


def start_auth_flow(user_id: int) -> str:
    """Start OAuth flow. Returns authorization URL."""
    client_id = os.environ.get("G_DRIVE_CLIENT_ID")
    client_secret = os.environ.get("G_DRIVE_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise ValueError("G_DRIVE_CLIENT_ID and G_DRIVE_CLIENT_SECRET must be set.")

    flow = OAuth2WebServerFlow(
        client_id=client_id,
        client_secret=client_secret,
        scope=OAUTH_SCOPE,
        redirect_uri=_get_redirect_uri(),
        access_type="offline",
        prompt="consent",
    )
    _pending_flows[user_id] = flow
    return flow.step1_get_authorize_url()


async def finish_auth_with_code(user_id: int, code: str, db) -> bool:
    """Exchange authorization code for credentials and save to DB."""
    flow = _pending_flows.pop(user_id, None)
    if not flow:
        return False
    try:
        creds = flow.step2_exchange(code)
        await db.save_gdrive_creds(user_id, creds.to_json())
        LOGGER.info(f"✅ OAuth success for user {user_id}")
        return True
    except FlowExchangeError as e:
        LOGGER.error(f"FlowExchangeError for {user_id}: {e}")
        return False


def has_pending_flow(user_id: int) -> bool:
    return user_id in _pending_flows


async def get_user_service(user_id: int, db):
    """Build Drive service for a specific user from stored credentials."""
    creds_json = await db.get_gdrive_creds(user_id)
    if not creds_json:
        return None
    try:
        creds = OAuth2Credentials.from_json(creds_json)
        if creds.access_token_expired:
            creds.refresh(Http())
            await db.save_gdrive_creds(user_id, creds.to_json())
            LOGGER.info(f"🔄 Refreshed token for user {user_id}")
        return build("drive", "v3", credentials=creds, cache_discovery=False)
    except Exception as e:
        LOGGER.error(f"Failed to build Drive service for {user_id}: {e}")
        return None


class DriveService:
    def __init__(self):
        self._admin_user_id = None

    def set_admin_user(self, user_id: int):
        self._admin_user_id = user_id

    async def _get_service(self, db):
        if self._admin_user_id:
            svc = await get_user_service(self._admin_user_id, db)
            if svc:
                return svc

        google_creds_env = os.getenv("GOOGLE_CREDENTIALS")
        if google_creds_env:
            try:
                from google.oauth2 import service_account
                info = json.loads(google_creds_env)
                creds = service_account.Credentials.from_service_account_info(
                    info, scopes=["https://www.googleapis.com/auth/drive"]
                )
                return build("drive", "v3", credentials=creds, cache_discovery=False)
            except Exception as e:
                LOGGER.error(f"Service account auth failed: {e}")

        LOGGER.error("No valid Drive credentials available.")
        return None

    _semaphore = None
    _mem_folders: list = []       # in-process RAM cache
    _mem_cache_at: float = 0.0    # when it was cached
    _mem_cache_ttl: int = 300     # 5 min RAM TTL

    def _get_semaphore(self):
        if DriveService._semaphore is None:
            DriveService._semaphore = asyncio.Semaphore(10)
        return DriveService._semaphore

    async def _run_async(self, func, *args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

    async def _throttled_call(self, func, *args, **kwargs):
        async with self._get_semaphore():
            return await self._run_async(func, *args, **kwargs)

    def _list_folders_sync(self, service, page_token=None):
        query = "mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = service.files().list(
            q=query, pageSize=100,
            fields="nextPageToken, files(id, name, owners, permissions)",
            pageToken=page_token
        ).execute()
        return results.get("files", []), results.get("nextPageToken")

    async def list_folders(self, db):
        service = await self._get_service(db)
        if not service:
            return []
        try:
            all_folders = []
            page_token = None
            while True:
                folders, next_token = await self._throttled_call(
                    self._list_folders_sync, service, page_token
                )
                all_folders.extend(folders)
                LOGGER.info(f"📂 Fetched {len(folders)} folders (total so far: {len(all_folders)})")
                if not next_token:
                    break
                page_token = next_token
            return all_folders
        except HttpError as error:
            LOGGER.error(f"list_folders error: {error}")
            return []

    async def get_folders_cached(self, db, force_refresh=False):
        import time as _time

        # Layer 1: in-process RAM cache (fastest — no DB/API hit)
        if not force_refresh:
            age = _time.time() - DriveService._mem_cache_at
            if DriveService._mem_folders and age < DriveService._mem_cache_ttl:
                LOGGER.info(f"⚡ RAM cache hit ({len(DriveService._mem_folders)} folders, {int(age)}s old)")
                return DriveService._mem_folders

        # Layer 2: MongoDB cache
        if not force_refresh:
            ttl = await db.get_setting("cache_ttl", 10)
            cached = await db.get_cached_folders(ttl_minutes=ttl)
            if cached:
                LOGGER.info(f"📦 MongoDB cache hit ({len(cached)} folders)")
                DriveService._mem_folders = cached        # warm up RAM cache
                DriveService._mem_cache_at = _time.time()
                return cached

        # Layer 3: Drive API (slowest — only on cache miss/expiry)
        LOGGER.info("🔄 Fetching ALL folders from Drive API (cache miss)...")
        folders = await self.list_folders(db)
        if folders:
            DriveService._mem_folders = folders
            DriveService._mem_cache_at = _time.time()
            await db.set_cached_folders(folders)
            LOGGER.info(f"💾 Cached {len(folders)} folders (RAM + MongoDB)")
        return folders

    def _grant_access_sync(self, service, folder_id, email, role):
        user_permission = {
            "type": "user",
            "role": "writer" if role == "editor" else "reader",
            "emailAddress": email,
        }
        try:
            return service.permissions().create(
                fileId=folder_id, body=user_permission,
                fields="id", sendNotificationEmail=True,
            ).execute()
        except HttpError as error:
            LOGGER.error(f"grant_access error: {error}")
            return None

    async def grant_access(self, folder_id, email, role, db):
        service = await self._get_service(db)
        if not service:
            return None
        return await self._throttled_call(self._grant_access_sync, service, folder_id, email, role)

    def _get_permissions_sync(self, service, folder_id):
        try:
            result = service.permissions().list(
                fileId=folder_id,
                fields="permissions(id, role, type, emailAddress, displayName)"
            ).execute()
            return result.get("permissions", [])
        except HttpError as error:
            LOGGER.error(f"get_permissions error: {error}")
            return []

    async def get_permissions(self, folder_id, db):
        service = await self._get_service(db)
        if not service:
            return []
        return await self._throttled_call(self._get_permissions_sync, service, folder_id)

    def _remove_access_sync(self, service, folder_id, permission_id):
        try:
            service.permissions().delete(fileId=folder_id, permissionId=permission_id).execute()
            return True
        except HttpError as error:
            LOGGER.error(f"remove_access error: {error}")
            return False

    async def remove_access(self, folder_id, email, db):
        perms = await self.get_permissions(folder_id, db)
        target = next((p for p in perms if p.get("emailAddress") == email), None)
        if target:
            service = await self._get_service(db)
            return await self._throttled_call(self._remove_access_sync, service, folder_id, target["id"])
        return True

    async def change_role(self, folder_id, email, new_role, db):
        perms = await self.get_permissions(folder_id, db)
        target = next((p for p in perms if p.get("emailAddress") == email), None)
        if target:
            service = await self._get_service(db)
            new_role_api = "writer" if new_role == "editor" else "reader"
            try:
                await self._throttled_call(
                    lambda: service.permissions().update(
                        fileId=folder_id, permissionId=target["id"],
                        body={"role": new_role_api}
                    ).execute()
                )
                return True
            except Exception as e:
                LOGGER.error(f"change_role error: {e}")
                return False
        return False
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ADD THESE TWO METHODS inside your DriveService class
# in services/drive.py
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def search_folders_by_name(self, query: str, db, max_results: int = 25) -> list:
        """
        Search Drive folders whose name contains `query` (case-insensitive).
        Returns list of {"id": ..., "name": ...}
        """
        service = await self._get_service(db)
        if not service:
            return []

        safe_query = query.replace("'", "\\'")
        q = (
            f"mimeType='application/vnd.google-apps.folder' "
            f"and name contains '{safe_query}' "
            f"and trashed=false"
        )

        def _search():
            results = service.files().list(
                q=q,
                pageSize=max_results,
                fields="files(id, name)",
                orderBy="name"
            ).execute()
            return results.get("files", [])

        return await self._throttled_call(_search)

    async def get_subfolders(self, parent_folder_id: str, db=None) -> list:
        """
        Returns immediate sub-folders of a given parent folder.
        Returns list of {"id": ..., "name": ...}
        """
        service = await self._get_service(db)
        if not service:
            return []

        q = (
            f"'{parent_folder_id}' in parents "
            f"and mimeType='application/vnd.google-apps.folder' "
            f"and trashed=false"
        )

        def _fetch():
            results = service.files().list(
                q=q,
                pageSize=100,
                fields="files(id, name)",
                orderBy="name"
            ).execute()
            return results.get("files", [])

        return await self._throttled_call(_fetch)
        


drive_service = DriveService()
