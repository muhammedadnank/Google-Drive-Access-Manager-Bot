"""
Modified Drive Service to support token from environment variable.
This allows using OAuth tokens on Render without Service Account.
"""

import os
import asyncio
import pickle
import json
import base64
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

LOGGER = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.pickle'

class DriveService:
    def __init__(self):
        self.creds = None
        self.service = None
        
    def authenticate(self):
        """
        Authenticate with Google Drive API.
        Supports: Service Account, OAuth Token (env), and OAuth Flow (local).
        """
        # Try Service Account authentication first (for Render deployment)
        google_creds_env = os.getenv('GOOGLE_CREDENTIALS')
        
        if google_creds_env:
            try:
                # Production: Load from environment variable
                LOGGER.info("🔑 Attempting Service Account authentication from environment variable...")
                credentials_info = json.loads(google_creds_env)
                self.creds = service_account.Credentials.from_service_account_info(
                    credentials_info,
                    scopes=SCOPES
                )
                self.service = build('drive', 'v3', credentials=self.creds)
                LOGGER.info("✅ Service Account authentication successful!")
                return True
            except Exception as e:
                LOGGER.error(f"❌ Service Account authentication failed: {e}")
                # Fall through to next method
        
        # Try OAuth Token from environment variable (for Render with OAuth)
        token_env = os.getenv('GOOGLE_OAUTH_TOKEN')
        
        if token_env:
            try:
                LOGGER.info("🔑 Attempting OAuth authentication from environment variable...")
                # Decode base64 token
                token_data = base64.b64decode(token_env)
                self.creds = pickle.loads(token_data)
                
                # Refresh if expired
                if self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                    LOGGER.info("✅ Refreshed OAuth token")
                
                self.service = build('drive', 'v3', credentials=self.creds)
                LOGGER.info("✅ OAuth authentication from environment successful!")
                return True
            except Exception as e:
                LOGGER.error(f"❌ OAuth token authentication failed: {e}")
                # Fall through to next method
        
        # OAuth 2.0 authentication (for local development)
        LOGGER.info("🔑 Attempting OAuth 2.0 authentication...")
        
        # Check if token.pickle exists (saved credentials)
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'rb') as token:
                self.creds = pickle.load(token)
        
        # If no valid credentials, let user log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                    LOGGER.info("✅ Refreshed OAuth token")
                except Exception as e:
                    LOGGER.error(f"Failed to refresh token: {e}")
                    self.creds = None
            
            if not self.creds:
                if not os.path.exists(CREDENTIALS_FILE):
                    LOGGER.error(f"❌ Credentials file '{CREDENTIALS_FILE}' not found!")
                    LOGGER.error("Please provide either GOOGLE_CREDENTIALS, GOOGLE_OAUTH_TOKEN env var or credentials.json file")
                    return False
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        CREDENTIALS_FILE, SCOPES)
                    # Run local server for OAuth callback
                    self.creds = flow.run_local_server(port=0)
                    LOGGER.info("✅ OAuth authentication successful")
                except Exception as e:
                    LOGGER.error(f"❌ Failed to authenticate: {e}")
                    return False
            
            # Save credentials for next run
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(self.creds, token)
        
        try:
            self.service = build('drive', 'v3', credentials=self.creds)
            return True
        except Exception as e:
            LOGGER.error(f"❌ Failed to build Drive service: {e}")
            return False

    async def _run_async(self, func, *args, **kwargs):
        """Run blocking function in executor."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

    # --- Core Drive Operations ---
    def _list_folders_sync(self, page_size=100, page_token=None):
        query = "mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = self.service.files().list(
            q=query,
            pageSize=page_size,
            fields="nextPageToken, files(id, name, owners, permissions)",
            pageToken=page_token
        ).execute()
        return results.get('files', []), results.get('nextPageToken')

    async def list_folders(self):
        if not self.service:
            if not self.authenticate(): 
                return []
        
        try:
            folders, _ = await self._run_async(self._list_folders_sync)
            return folders
        except HttpError as error:
            LOGGER.error(f"An error occurred: {error}")
            return []

    def _grant_access_sync(self, folder_id, email, role):
        user_permission = {
            'type': 'user',
            'role': 'writer' if role == 'editor' else 'reader',
            'emailAddress': email
        }
        try:
            return self.service.permissions().create(
                fileId=folder_id,
                body=user_permission,
                fields='id',
                sendNotificationEmail=True
            ).execute()
        except HttpError as error:
            LOGGER.error(f"An error occurred: {error}")
            return None

    async def grant_access(self, folder_id, email, role):
        if not self.service: self.authenticate()
        return await self._run_async(self._grant_access_sync, folder_id, email, role)

    def _get_permissions_sync(self, folder_id):
        try:
            permissions = self.service.permissions().list(
                fileId=folder_id,
                fields="permissions(id, role, type, emailAddress, displayName)"
            ).execute()
            return permissions.get('permissions', [])
        except HttpError as error:
            LOGGER.error(f"An error occurred: {error}")
            return []

    async def get_permissions(self, folder_id):
        if not self.service: self.authenticate()
        return await self._run_async(self._get_permissions_sync, folder_id)

    def _remove_access_sync(self, folder_id, permission_id):
        try:
            self.service.permissions().delete(
                fileId=folder_id,
                permissionId=permission_id
            ).execute()
            return True
        except HttpError as error:
            LOGGER.error(f"An error occurred: {error}")
            return False

    async def remove_access(self, folder_id, email):
        """Removes access for a specific email."""
        perms = await self.get_permissions(folder_id)
        target_perm = next((p for p in perms if p.get('emailAddress') == email), None)
        
        if target_perm:
            return await self._run_async(self._remove_access_sync, folder_id, target_perm['id'])
        return False

    async def change_role(self, folder_id, email, new_role):
        """Updates role for a specific email."""
        perms = await self.get_permissions(folder_id)
        target_perm = next((p for p in perms if p.get('emailAddress') == email), None)
        
        if target_perm:
            new_role_api = 'writer' if new_role == 'editor' else 'reader'
            try:
                await self._run_async(
                    lambda: self.service.permissions().update(
                        fileId=folder_id,
                        permissionId=target_perm['id'],
                        body={'role': new_role_api}
                    ).execute()
                )
                return True
            except Exception:
                return False
        return False
        
drive_service = DriveService()
