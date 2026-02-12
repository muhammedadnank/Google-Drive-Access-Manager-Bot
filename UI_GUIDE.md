# 🗂 Drive Access Manager Bot — Full UI Guide

> Complete visual reference of every screen, button, and flow in the bot.

---

## 📋 Table of Contents

1. [Main Menu](#-main-menu)
2. [Grant Access Flow](#-grant-access-flow)
3. [Manage Folders](#-manage-folders)
4. [Expiry Dashboard](#-expiry-dashboard)
5. [Bulk Import & Scan](#-bulk-import--scan)
6. [Access Logs](#-access-logs)
7. [Settings](#️-settings)
8. [Help & Commands](#-help--commands)
9. [Access Denied](#-access-denied)

---

## 🏠 Main Menu

> Shown on `/start` — displays live stats and all navigation options.

```
━━━━━━━━━━━━━━━━━━━━━━
🗂 Drive Access Manager
━━━━━━━━━━━━━━━━━━━━━━

👋 Welcome back, Adnan!

📈 Quick Stats
┣ ⏰ Active Timed Grants: 12
┗ 📝 Total Log Entries: 45

▸ Select an option below to get started:
```
```
[➕ Grant Access]     [📂 Manage Folders]
[⏰ Expiry Dashboard] [📊 Access Logs]
[⚙️ Settings]         [❓ Help]
```

---

## ➕ Grant Access Flow

> 6-step guided process: Email → Folder → Role → Duration → Confirm → Done

### Step 1 — Enter Email
```
📧 Enter the email address to grant access to:
```
*User types email like `john@gmail.com`*

### Step 2 — Select Folder
```
📂 Select a Folder for john@gmail.com:
```
```
[Leo AD 2500 [001-050]]
[Leo AD 2500 [051-100]]
[Leo AD 2500 [101-150]]
...
[⬅️ Prev] [📄 2/6] [Next ➡️]
[🔄 Refresh]
[⬅️ Back]
```
*Folders sorted by smart numeric ranges*

### Step 3 — Select Role
```
📂 Folder: Leo AD 2500 [001-050]
📧 User: john@gmail.com

🔑 Select Access Role:
```
```
[👁 Viewer]  [✏️ Editor]
[⬅️ Back]
```

### Step 4a — Duration (Viewer Only)
> Editors skip this step → always permanent

```
📧 User: john@gmail.com
📂 Folder: Leo AD 2500 [001-050]
🔑 Role: Viewer

⏰ Select Access Duration:
```
```
[1 Hour]          [6 Hours]
[1 Day]           [7 Days]
[✅ 30 Days (Default)] [♾ Permanent]
[⬅️ Back]
```

### Step 4b — Editor (No Duration)
> Editors go straight to confirmation as permanent.

```
⚠️ Confirm Access Grant

📧 User: john@gmail.com
📂 Folder: Leo AD 2500 [001-050]
🔑 Role: Editor
⏳ Duration: ♾ Permanent

Is this correct?
```
```
[✅ Confirm]  [❌ Cancel]
```

### Step 5 — Confirm (Viewer with Duration)
```
⚠️ Confirm Access Grant

📧 User: john@gmail.com
📂 Folder: Leo AD 2500 [001-050]
🔑 Role: Viewer
⏳ Duration: 30d

Is this correct?
```
```
[✅ Confirm]  [❌ Cancel]
```

### Step 6 — Success
```
✅ Access Granted Successfully!

User: john@gmail.com
Folder: Leo AD 2500 [001-050]
Role: Viewer
Duration: 30d
```
```
[🏠 Main Menu]
```

### Grant Failed
```
❌ Failed to grant access.
Check logs or credentials.
```
```
[🏠 Main Menu]
```

---

## 📂 Manage Folders

> Browse folders, view users, change roles, remove access.

### Folder List
```
📂 Select a Folder to Manage:
```
```
[Leo AD 2500 [001-050]]
[Leo AD 2500 [051-100]]
[Leo AD 2500 [101-150]]
...
[⬅️ Prev] [📄 2/6] [Next ➡️]
[🔄 Refresh]
[🏠 Back]
```

### Folder — User List
```
📂 Leo AD 2500 [001-050]
Users with access:

1. john@gmail.com — viewer
2. jane@gmail.com — viewer
3. bob@gmail.com — writer
```
```
[john@gmail.com]
[jane@gmail.com]
[bob@gmail.com]
[⬅️ Back]
```

### User Actions
```
👤 john@gmail.com
📂 Leo AD 2500 [001-050]
🔑 Current Role: viewer
```
```
[🔄 Change Role]  [🗑 Remove Access]
[⬅️ Back]
```

### Change Role
```
🔄 Change role for john@gmail.com:
📂 Leo AD 2500 [001-050]

Current: viewer
```
```
[👁 Viewer]  [✏️ Editor]
[Cancel]
```

### Role Changed
```
✅ Role updated!

john@gmail.com → Editor
📂 Leo AD 2500 [001-050]
```

### Confirm Remove
```
⚠️ Remove access for john@gmail.com
from Leo AD 2500 [001-050]?
```
```
[✅ Yes, Remove]  [❌ Cancel]
```

### Access Removed
```
✅ Access removed: john@gmail.com
📂 Leo AD 2500 [001-050]
```

---

## ⏰ Expiry Dashboard

> View, extend, and revoke timed grants.

### Dashboard — Active Grants
```
⏰ Expiry Dashboard (Page 1/3)
📊 12 active timed grant(s)

📧 john@gmail.com
   📂 Leo AD 2500 [001-050] | 🔑 reader
   ⏳ 29d 12h remaining

📧 jane@gmail.com
   📂 Leo AD 2500 [051-100] | 🔑 reader
   ⏳ 15d 4h remaining
```
```
[🔄 Extend john@gma...]  [🗑 Revoke]
[🔄 Extend jane@gma...]  [🗑 Revoke]
[⬅️ Prev]  [Next ➡️]
[📥 Bulk Import]  [🏠 Back]
```

### Dashboard — Empty
```
⏰ Expiry Dashboard

No active timed grants.
```
```
[📥 Bulk Import Existing]
[🏠 Back]
```

### Extend Menu
```
🔄 Extend access for john@gmail.com

📂 Leo AD 2500 [001-050]
⏳ Currently: 29d 12h remaining

Add extra time:
```
```
[+1 Hour]   [+6 Hours]
[+1 Day]    [+7 Days]
[⬅️ Back]
```

### Extended Success
> Toast notification:
```
✅ Extended by 7d!
```

### Revoke Confirm
```
🗑 Revoke access for john@gmail.com?

📂 Leo AD 2500 [001-050]
This will remove access immediately.
```
```
[✅ Yes, Revoke]  [❌ Cancel]
```

### Revoke Success
> Toast notification:
```
✅ Access revoked!
```

---

## 📥 Bulk Import & Scan

> Full Drive scan → report file → import with 40-day expiry.

### Step 1 — Scanning (Progress)
```
📥 Full Drive Scan Started...
⏳ Scanning all folders and permissions...
```
```
📥 Scanning... (30/120 folders)
👁 Viewers found: 85
```
```
📥 Scanning... (80/120 folders)
👁 Viewers found: 280
```

### Step 2 — Report File Sent
> Bot sends `drive_scan_report.txt` as a document:

**Caption:**
```
📥 Drive Scan Report

📂 Folders: 120
👁 Viewers: 400
🆕 New: 380 | ⏭ Tracked: 20
👤 Unique emails: 350
```

**File contents (`drive_scan_report.txt`):**
```
============================================================
  GOOGLE DRIVE FULL SCAN REPORT
  Generated: 2026-02-12 08:30:00
============================================================

Total Folders: 120
Total Viewer Permissions: 400
New (not tracked): 380
Already Tracked: 20
Unique Emails: 350

============================================================
  FOLDER-WISE BREAKDOWN
============================================================

📂 Leo AD 2500 [001-050]
   ID: 1ABC...XYZ
   Viewers (12):
     - john@gmail.com [● new]
     - jane@gmail.com [● new]
     - bob@gmail.com [✓ tracked]

📂 Leo AD 2500 [051-100]
   ID: 2DEF...UVW
   Viewers (8):
     - alice@gmail.com [● new]

📂 Leo AD 2500 [101-150]
   ID: 3GHI...RST
   No viewer permissions

============================================================
  ALL UNIQUE EMAILS
============================================================
  1. alice@gmail.com
  2. bob@gmail.com
  3. jane@gmail.com
  4. john@gmail.com

--- End of Report ---
```

### Step 3 — Import Confirmation
```
⏰ Import all 380 new viewer grants with 40-day expiry?
```
```
[✅ Import 380 Grants]  [❌ Cancel]
```

### Step 4 — Import Progress
```
📥 Scanning Drive folders...
⏳ Please wait...
```
```
📥 Scanning folders... (50/120)
✅ Imported: 150 | ⏭ Skipped: 10
```

### Step 5 — Import Complete
```
📥 Bulk Import Complete!

📂 Folders scanned: 120
✅ Grants imported: 380
⏭ Already tracked: 20
❌ Errors: 0

⏰ All imported grants expire in 40 days.
```
```
[⏰ View Dashboard]
[🏠 Main Menu]
```

---

## 📊 Access Logs

> Paginated activity history with type icons.

### Logs View
```
📊 Activity Logs (Page 1/5)

➕ GRANT → john@gmail.com
   📂 Leo AD 2500 [001-050] 🕒 02-12 08:15

🗑 REMOVE → jane@gmail.com
   📂 Leo AD 2500 [051-100] 🕒 02-11 14:30

🔄 ROLE CHANGE → bob@gmail.com
   📂 Leo AD 2500 [001-050] 🕒 02-11 12:00

▪️ AUTO REVOKE → alice@gmail.com
   📂 Leo AD 2500 [101-150] 🕒 02-10 03:05

▪️ BULK IMPORT → (batch)
   📂 All Folders 🕒 02-09 10:00
```
```
[Next ➡️]
[🗑 Clear Logs]
[🏠 Back]
```

### Logs — Empty
```
📊 Access Logs

No activity recorded yet.
```
```
[🏠 Back]
```

### Logs Cleared
```
📊 Logs Cleared
```
```
[🏠 Back]
```

---

## ⚙️ Settings

### Settings Menu
```
⚙️ Settings

🔹 Default Role: viewer
🔹 Folders Per Page: 5
🔹 Notifications: 🔔 ON
```
```
[🔄 Change Default Role]
[📄 Change Page Size]
[Toggle Notifications (🔔 ON)]
[⬅️ Back]
```

### Change Default Role
```
Select Default Role:
```
```
[Viewer]  [Editor]
[Cancel]
```

### Change Page Size
```
📄 Enter Page Size (3-10):
```
```
[Cancel]
```

### Page Size Updated
```
✅ Page size updated to 8!
```
```
[⚙️ Back to Settings]
```

---

## ❓ Help & Commands

### Help Screen
```
━━━━━━━━━━━━━━━━━━━━━━
❓ Help & Commands
━━━━━━━━━━━━━━━━━━━━━━

➕ Grant Access
┗ Grant Viewer/Editor access with expiry timer

📂 Manage Folders
┗ View permissions, change roles, revoke access

⏰ Expiry Dashboard
┗ View timed grants, extend, revoke, bulk import

📊 Access Logs
┗ Full audit trail of all permission changes

⚙️ Settings
┗ Default role, page size, notifications

━━━━━━━━━━━━━━━━━━━━━━
📌 Commands
━━━━━━━━━━━━━━━━━━━━━━
/start  — Main menu
/help   — This help text
/cancel — Cancel current operation
/id     — Show your Telegram ID
```
```
[🏠 Back to Menu]
```

---

## 🆔 ID Command

> `/id` — Works for any user, no admin check.

```
🆔 Your Telegram Info:

User ID: 123456789
Username: @adnank
First Name: Adnan
Is Bot: False
```

---

## 🔒 Access Denied

> Shown to non-admin users on `/start`.

```
━━━━━━━━━━━━━━━━━━━━━━
🔒 Access Restricted
━━━━━━━━━━━━━━━━━━━━━━

⚠️ You are not authorized to use this bot.
Contact the administrator for access.

🆔 Your ID: 987654321
```

---

## 🚫 Cancel

> `/cancel` — Cancels any active operation.

```
🚫 Operation Cancelled.
```
```
[➕ Grant Access]     [📂 Manage Folders]
[⏰ Expiry Dashboard] [📊 Access Logs]
[⚙️ Settings]         [❓ Help]
```

---

## ⏰ Auto-Expire (Background)

> Runs silently every 5 minutes. No UI — logged only.

- Checks all active grants for expiry
- Revokes expired viewer access via Drive API
- Logs as `auto_revoke` with admin name "Auto-Expire"
- Example log entry:
```
▪️ AUTO REVOKE → john@gmail.com
   📂 Leo AD 2500 [001-050] 🕒 02-12 03:05
```

---

## 🔄 Flow Diagram

```
/start
  │
  ├── ➕ Grant Access
  │     └── Email → Folder → Role
  │           ├── Viewer → Duration → Confirm → ✅
  │           └── Editor → Confirm (Permanent) → ✅
  │
  ├── 📂 Manage Folders
  │     └── Select Folder → Select User
  │           ├── 🔄 Change Role → Viewer/Editor → ✅
  │           └── 🗑 Remove Access → Confirm → ✅
  │
  ├── ⏰ Expiry Dashboard
  │     ├── View Active Grants (paginated)
  │     │     ├── 🔄 Extend (+1h/6h/1d/7d)
  │     │     └── 🗑 Revoke Now → Confirm → ✅
  │     └── 📥 Bulk Import
  │           └── Scan → Report.txt → Import → ✅
  │
  ├── 📊 Access Logs (paginated)
  │     └── 🗑 Clear Logs
  │
  ├── ⚙️ Settings
  │     ├── Default Role
  │     ├── Page Size
  │     └── Notifications Toggle
  │
  └── ❓ Help
```

---

> 📄 Generated for **Drive Access Manager Bot** — Built with Pyrogram, MongoDB & Google Drive API
