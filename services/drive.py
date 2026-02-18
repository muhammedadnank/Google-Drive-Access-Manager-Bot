"""
Drive Service with per-user OAuth support.
Credentials are stored in MongoDB via services.database.
Falls back to GOOGLE_CREDENTIALS service account env var.
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
    "https://www.googleapis.com/auth/drive.metadata.readonly"
]
REDIRECT_URI = os.environ.get("REDIRECT_URI", "urn:ietf:wg:oauth:2.0:oob")

# Pending OAuth flows: {user_id: flow}
_pending_flows: dict = {}


def get_flow():
    client_id = os.environ.get("G_DRIVE_CLIENT_ID")
    client_secret = os.environ.get("G_DRIVE_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise ValueError("G_DRIVE_CLIENT_ID and G_DRIVE_CLIENT_SECRET must be set.")
    return OAuth2WebServerFlow(
        client_id=client_id,
        client_secret=client_secret,
        scope=OAUTH_SCOPE,
        redirect_uri=REDIRECT_URI,
        access_type="offline",
        prompt="consent",
    )


def start_auth_flow(user_id: int) -> str:
    """Start OAuth flow for a user. Returns the authorization URL."""
    flow = get_flow()
    _pending_flows[user_id] = flow
    return flow.step1_get_authorize_url()


async def finish_auth_flow(user_id: int, code: str, db) -> bool:
    """Exchange code for credentials and save to DB."""
    flow = _pending_flows.get(user_id)
    if not flow:
        return False
    try:
        creds = flow.step2_exchange(code)
        await db.save_gdrive_creds(user_id, creds.to_json())
        del _pending_flows[user_id]
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

        # Fallback: service account from env
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
            folders, _ = await self._throttled_call(self._list_folders_sync, service)
            return folders
        except HttpError as error:
            LOGGER.error(f"list_folders error: {error}")
            return []

    async def get_folders_cached(self, db, force_refresh=False):
        if not force_refresh:
            ttl = await db.get_setting("cache_ttl", 10)
            cached = await db.get_cached_folders(ttl_minutes=ttl)
            if cached:
                LOGGER.info(f"📦 Using cached folders ({len(cached)} items)")
                return cached

        LOGGER.info("🔄 Fetching folders from Drive API...")
        folders = await self.list_folders(db)
        if folders:
            await db.set_cached_folders(folders)
            LOGGER.info(f"💾 Cached {len(folders)} folders")
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


drive_service = DriveService()
