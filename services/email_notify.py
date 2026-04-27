# services/email_notify.py
"""
Gmail-based email notifications for grant/revoke/expiry/role-change events.
Uses the same oauth2client OAuth token stored in DB — no separate auth needed.
"""

import base64
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import OAuth2Credentials

from services.database import db
from utils.time import format_date

LOGGER = logging.getLogger(__name__)


# ──────────────────────────────────────────
# Gmail Service
# ──────────────────────────────────────────

async def _get_gmail_service(admin_id: int):
    """
    Build Gmail API service using stored oauth2client credentials.
    Same credentials as Drive — no extra auth needed after scope update.
    Returns None if unavailable.
    """
    creds_json = await db.get_gdrive_creds(admin_id)
    if not creds_json:
        LOGGER.warning(f"No credentials for admin {admin_id} — email skipped")
        return None
    try:
        creds = OAuth2Credentials.from_json(creds_json)
        service = build("gmail", "v1", credentials=creds, cache_discovery=False)
        return service
    except Exception as e:
        LOGGER.error(f"Gmail service build failed for admin {admin_id}: {e}")
        return None


def _build_raw_message(to: str, subject: str, html_body: str) -> dict:
    """Encode email as base64 for Gmail API."""
    msg = MIMEMultipart("alternative")
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {"raw": raw}


async def send_email(admin_id: int, to: str, subject: str, html_body: str) -> bool:
    """
    Send email via Gmail API.
    Returns True on success, False on any failure (non-blocking).
    """
    # Check toggle
    settings = await db.get_setting("email_notifications") or {}
    if not settings.get("enabled", True):
        LOGGER.debug("Email notifications disabled in settings — skipping")
        return False

    service = await _get_gmail_service(admin_id)
    if not service:
        return False

    try:
        message = _build_raw_message(to, subject, html_body)
        service.users().messages().send(userId="me", body=message).execute()
        LOGGER.info(f"📧 Email sent → {to} | {subject}")
        return True
    except HttpError as e:
        if e.resp.status == 403:
            LOGGER.error(
                f"❌ Gmail 403 for admin {admin_id} — likely missing gmail.send scope. "
                "Admin must /auth again after scope update."
            )
        elif e.resp.status == 429:
            LOGGER.warning(f"⚠️ Gmail rate limit hit — email to {to} skipped")
        else:
            LOGGER.error(f"❌ Gmail API error sending to {to}: {e}")
        return False
    except Exception as e:
        LOGGER.error(f"❌ Unexpected error sending email to {to}: {e}")
        return False


# ──────────────────────────────────────────
# HTML Template Engine
# ──────────────────────────────────────────

def _wrap_template(header_color: str, header_title: str, content: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body {{ margin:0; padding:20px; background:#f0f2f5; font-family:Arial,sans-serif; }}
  .card {{ max-width:520px; margin:auto; background:#fff; border-radius:10px;
           box-shadow:0 2px 12px rgba(0,0,0,0.1); overflow:hidden; }}
  .header {{ background:{header_color}; color:#fff; padding:20px 24px; }}
  .header h2 {{ margin:0; font-size:18px; font-weight:700; }}
  .body {{ padding:24px; }}
  .row {{ margin:12px 0; display:flex; flex-direction:column; }}
  .label {{ font-size:12px; color:#888; text-transform:uppercase; letter-spacing:.5px; margin-bottom:3px; }}
  .value {{ font-size:15px; color:#111; font-weight:600; }}
  .divider {{ border:none; border-top:1px solid #eee; margin:18px 0; }}
  .badge {{ display:inline-block; padding:3px 12px; border-radius:20px; font-size:13px; font-weight:700; }}
  .badge-viewer  {{ background:#e8f0fe; color:#1a73e8; }}
  .badge-editor  {{ background:#fce8e6; color:#d93025; }}
  .badge-revoked {{ background:#fce8e6; color:#d93025; }}
  .note {{ font-size:13px; color:#666; margin-top:16px; line-height:1.6; }}
  .footer {{ background:#f7f7f7; padding:14px 24px; font-size:12px;
             color:#aaa; text-align:center; border-top:1px solid #eee; }}
</style>
</head>
<body>
<div class="card">
  <div class="header"><h2>{header_title}</h2></div>
  <div class="body">{content}</div>
  <div class="footer">Automated notification · Google Drive Access Manager</div>
</div>
</body>
</html>"""


# ──────────────────────────────────────────
# Email Builders
# ──────────────────────────────────────────

def _grant_html(details: dict) -> tuple[str, str]:
    role = details.get("role", "viewer").lower()
    role_label = role.capitalize()
    badge_class = f"badge-{role}" if role in ("viewer", "editor") else "badge-viewer"
    folder = details.get("folder_name", "Unknown")
    duration = details.get("duration", "Permanent")

    expires_row = ""
    if details.get("expires_at"):
        expires_row = f"""
        <div class="row">
          <span class="label">Expires On</span>
          <span class="value">📅 {format_date(details['expires_at'])}</span>
        </div>"""

    content = f"""
    <p style="margin-top:0;color:#444;">You have been granted access to a Google Drive folder.</p>
    <hr class="divider">
    <div class="row">
      <span class="label">📂 Folder</span>
      <span class="value">{folder}</span>
    </div>
    <div class="row">
      <span class="label">🔑 Role</span>
      <span class="value"><span class="badge {badge_class}">{role_label}</span></span>
    </div>
    <div class="row">
      <span class="label">⏳ Duration</span>
      <span class="value">{duration}</span>
    </div>
    {expires_row}
    <hr class="divider">
    <p class="note">
      The folder should now appear in your
      <strong>Shared with me</strong> section in Google Drive.
      If you don't see it within a few minutes, try refreshing.
    </p>"""

    subject = f"✅ Drive Access Granted — {folder}"
    return subject, _wrap_template("#1a73e8", "✅ Google Drive Access Granted", content)


def _revoke_html(details: dict) -> tuple[str, str]:
    folder = details.get("folder_name", "Unknown")
    reason = details.get("reason", "")
    reason_row = f"""
    <div class="row">
      <span class="label">Reason</span>
      <span class="value">{reason}</span>
    </div>""" if reason else ""

    content = f"""
    <p style="margin-top:0;color:#444;">Your access to a Google Drive folder has been removed.</p>
    <hr class="divider">
    <div class="row">
      <span class="label">📂 Folder</span>
      <span class="value">{folder}</span>
    </div>
    <div class="row">
      <span class="label">Status</span>
      <span class="value"><span class="badge badge-revoked">Access Removed</span></span>
    </div>
    {reason_row}
    <hr class="divider">
    <p class="note">
      If you believe this was a mistake, please contact your administrator.
    </p>"""

    subject = f"🗑️ Drive Access Removed — {folder}"
    return subject, _wrap_template("#d93025", "🗑️ Google Drive Access Removed", content)


def _expiry_warning_html(details: dict) -> tuple[str, str]:
    folder = details.get("folder_name", "Unknown")
    time_remaining = details.get("time_remaining", "soon")
    expires_at = details.get("expires_at")
    expire_row = f"""
    <div class="row">
      <span class="label">⏰ Expires</span>
      <span class="value">📅 {format_date(expires_at)}</span>
    </div>""" if expires_at else ""

    content = f"""
    <p style="margin-top:0;color:#444;">
      Your Google Drive access is expiring <strong>{time_remaining}</strong>.
    </p>
    <hr class="divider">
    <div class="row">
      <span class="label">📂 Folder</span>
      <span class="value">{folder}</span>
    </div>
    {expire_row}
    <hr class="divider">
    <p class="note">
      Contact your administrator to extend access before it expires.
    </p>"""

    subject = f"⏰ Drive Access Expiring Soon — {folder}"
    return subject, _wrap_template("#f9a825", "⏰ Access Expiring Soon", content)


def _role_change_html(details: dict) -> tuple[str, str]:
    folder = details.get("folder_name", "Unknown")
    old_role = details.get("old_role", "viewer").capitalize()
    new_role = details.get("new_role", "editor").capitalize()

    content = f"""
    <p style="margin-top:0;color:#444;">Your access role for a Google Drive folder has been updated.</p>
    <hr class="divider">
    <div class="row">
      <span class="label">📂 Folder</span>
      <span class="value">{folder}</span>
    </div>
    <div class="row">
      <span class="label">🔑 Role Change</span>
      <span class="value">{old_role} ➜ <strong>{new_role}</strong></span>
    </div>
    <hr class="divider">
    <p class="note">
      Your updated permissions are now active in Google Drive.
    </p>"""

    subject = f"🔄 Drive Access Role Updated — {folder}"
    return subject, _wrap_template("#1e8e3e", "🔄 Drive Access Role Updated", content)


# ──────────────────────────────────────────
# Public API
# ──────────────────────────────────────────

async def notify_grant(admin_id: int, details: dict):
    """Call after successful Drive grant. details: email, folder_name, role, duration, expires_at."""
    email = details.get("email")
    if not email:
        return
    subject, body = _grant_html(details)
    await send_email(admin_id, email, subject, body)


async def notify_revoke(admin_id: int, details: dict):
    """Call after Drive access revoked. details: email, folder_name, reason (optional)."""
    email = details.get("email")
    if not email:
        return
    subject, body = _revoke_html(details)
    await send_email(admin_id, email, subject, body)


async def notify_expiry_warning(admin_id: int, details: dict):
    """Call from expiry_notifier. details: email, folder_name, expires_at, time_remaining."""
    email = details.get("email")
    if not email:
        return
    subject, body = _expiry_warning_html(details)
    await send_email(admin_id, email, subject, body)


async def notify_role_change(admin_id: int, details: dict):
    """Call after role update. details: email, folder_name, old_role, new_role."""
    email = details.get("email")
    if not email:
        return
    subject, body = _role_change_html(details)
    await send_email(admin_id, email, subject, body)
