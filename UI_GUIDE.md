# 🗂 Drive Access Manager Bot — Full UI Guide

> Complete visual reference of every screen, button, and flow.

---

## 📋 Table of Contents

1. [Main Menu](#-main-menu)
2. [Grant Access — Mode Selector](#-grant-access--mode-selector)
3. [Single Grant Flow](#-single-grant-flow)
4. [Multi-Folder Grant Flow](#-multi-folder-grant-flow)
5. [Multi-Email Grant Flow](#-multi-email-grant-flow)
6. [Access Templates](#-access-templates)
7. [Manage Folders](#-manage-folders)
8. [Expiry Dashboard](#-expiry-dashboard)
9. [Bulk Import & Scan](#-bulk-import--scan)
10. [Access Logs](#-access-logs)
11. [Settings](#️-settings)
12. [/stats Analytics](#-stats-analytics)
13. [/info System Monitor](#-info-system-monitor)
14. [Help & Commands](#-help--commands)
15. [Access Denied](#-access-denied)
16. [Flow Diagram](#-flow-diagram)

---

## 🏠 Main Menu

> `/start` — Shows live stats and navigation.

```
╔════════════════════════════╗
  🗂 Drive Access Manager
╚════════════════════════════╝

👋 Welcome back, Adnan!

📈 Quick Stats
┣ ⏰ Active Timed Grants: 12
┗ 📝 Total Log Entries: 45

▸ Select an option below:
```
```
[➕ Grant Access]      [📂 Manage Folders]
[⏰ Expiry Dashboard]  [📋 Templates]
[📊 Access Logs]       [⚙️ Settings]
                [❓ Help]
```

---

## ➕ Grant Access — Mode Selector

```
➕ Grant Access

How would you like to grant?
```
```
[👤 One Email → One Folder]
[📂 One Email → Multi Folders]
[👥 Multi Emails → One Folder]
[🏠 Back]
```

---

## 👤 Single Grant Flow

### Step 1 — Email
```
📧 Enter User Email

Send the email address to grant access to.
Or /cancel to abort.
```

### Step 2 — Folder
```
📧 User: john@gmail.com

📂 Select a Folder:
```
```
[Leo AD 2500 [001-050]]
[Leo AD 2500 [051-100]]
...
[⬅️ Prev] [2/6] [Next ➡️]
[🔄 Refresh]
[🏠 Back]
```

### Step 3 — Role
```
📧 User: john@gmail.com
📂 Folder: Leo AD 2500 [001-050]

🔑 Select Access Level:
```
```
[👀 Viewer]  [✏️ Editor]
[⬅️ Back]
```

### Step 4 — Duration (Viewer only)
```
⏰ Select Access Duration:
```
```
[1 Hour]          [6 Hours]
[1 Day]           [7 Days]
[✅ 30 Days (Default)] [♾ Permanent]
[⬅️ Back]
```

### Step 5 — Confirm
```
⚠️ Confirm Access Grant

📧 User: john@gmail.com
📂 Folder: Leo AD 2500 [001-050]
🔑 Role: Viewer
⏳ Duration: ⏰ 30 day(s)

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

---

## 📂 Multi-Folder Grant Flow

### Step 2b — Checkbox Selection
```
📧 User: john@gmail.com

📂 Select Folders (tap to toggle):
```
```
[☑️ Leo AD 2500 [001-050]]
[☐ Leo AD 2500 [051-100]]
[☑️ Leo AD 2500 [101-150]]
[☐ Leo AD 2500 [151-200]]
...
[⬅️ Prev] [1/6] [Next ➡️]
[✅ Confirm (2 selected)]
[⬅️ Back]
```

### Confirm (Multi)
```
⚠️ Confirm Access Grant

📧 User: john@gmail.com
📂 Folders (2):
   • Leo AD 2500 [001-050]
   • Leo AD 2500 [101-150]
🔑 Role: Viewer
⏳ Duration: ⏰ 30 day(s)
```

### Results (Multi)
```
✅ Grant Complete!

📧 john@gmail.com | 🔑 Viewer | ⏳ 30d

✅ Leo AD 2500 [001-050] — granted
✅ Leo AD 2500 [101-150] — granted

2/2 folders granted.
```

---

## 👥 Multi-Email Grant Flow

### Step 1 — Enter Emails
```
👥 Multi-Email Grant

Send multiple email addresses.
Separate with comma or new line.

Example:
alice@gmail.com, bob@gmail.com
```

### Step 2 — Email List + Folder
```
👥 5 emails ready:
   • alice@gmail.com
   • bob@gmail.com
   • carol@gmail.com
   • dave@gmail.com
   • eve@gmail.com

📂 Select a Folder:
```

### Step 3 — Duplicate Detection
```
⚠️ Confirm Multi-Email Grant

📂 Folder: Leo AD 2500 [001-050]
🔑 Role: Viewer
⏳ Duration: 30d

⚠️ 2 already have access (will skip):
   • ~~alice@gmail.com~~
   • ~~bob@gmail.com~~

✅ 3 to grant:
   • carol@gmail.com
   • dave@gmail.com
   • eve@gmail.com
```
```
[✅ Grant 3 Users]
[❌ Cancel]
```

### Results
```
✅ Multi-Email Grant Complete!

📂 Leo AD 2500 [001-050] | 🔑 Viewer | ⏳ 30d

✅ carol@gmail.com
✅ dave@gmail.com
❌ eve@gmail.com — failed

2/3 granted | 2 skipped (duplicates)
```

---

## 📋 Access Templates

### Template List
```
📋 Access Templates (3)

📌 New Intern — 5 folder(s) | Viewer | 30d
📌 Course Launch — 3 folder(s) | Viewer | 7d
📌 Editor Access — 2 folder(s) | Editor | ♾ Permanent
```
```
[▶️ New Intern]        [🗑]
[▶️ Course Launch]     [🗑]
[▶️ Editor Access]     [🗑]
[➕ Create Template]
[🏠 Back]
```

### Create Template — Name
```
📋 Create Template

Enter a name for this template:
Example: New Intern, Course Launch, Paid User
```

### Create Template — Folder Checkbox
```
📋 Template: New Intern

📂 Select folders (tap to toggle):
```
```
[☑️ Leo AD 2500 [001-050]]
[☑️ Leo AD 2500 [051-100]]
[☐ Leo AD 2500 [101-150]]
...
[✅ Confirm (2 selected)]
[⬅️ Back]
```

### Create Template — Role + Duration
```
📋 Template: New Intern
📂 2 folders | 🔑 Viewer

⏰ Select Duration:
```

### Template Saved
```
✅ Template Saved!

📌 New Intern
📂 Folders (2):
   • Leo AD 2500 [001-050]
   • Leo AD 2500 [051-100]
🔑 Role: Viewer
⏳ Duration: 30d
```

### Apply Template
```
▶️ Apply Template: New Intern

📂 Folders (2):
   • Leo AD 2500 [001-050]
   • Leo AD 2500 [051-100]
🔑 Role: Viewer
⏳ Duration: 30d

📧 Enter email(s) to grant access:
(comma or newline separated for multiple)
```

### Apply — Results
```
✅ Template Applied: New Intern

📧 3 email(s) × 📂 2 folder(s)
🔑 Viewer | ⏳ 30d

✅ Granted: 5
⏭ Skipped: 1
❌ Failed: 0
```

---

## 📂 Manage Folders

### Folder List
```
📂 Select a Folder to Manage:
```
```
[Leo AD 2500 [001-050]]
[Leo AD 2500 [051-100]]
...
[⬅️ Prev] [2/6] [Next ➡️]
[🔄 Refresh]
[🏠 Back]
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

---

## ⏰ Expiry Dashboard

### Active Grants
```
⏰ Expiry Dashboard (Page 1/3)
📊 12 active timed grant(s)

📧 john@gmail.com
   📂 Leo AD 2500 [001-050] | 🔑 reader
   ⏳ 29d 12h remaining
```
```
[🔄 Extend john@gma...]  [🗑 Revoke]
[📥 Bulk Import]  [🏠 Back]
```

### Extend Menu
```
🔄 Extend access for john@gmail.com
Add extra time:
```
```
[+1 Hour]   [+6 Hours]
[+1 Day]    [+7 Days]
[⬅️ Back]
```

---

## 📥 Bulk Import & Scan

### Scan Progress
```
📥 Scanning... (80/120 folders)
👁 Viewers found: 280
```

### Report File (`drive_scan_report.txt`)
```
GOOGLE DRIVE FULL SCAN REPORT
Total Folders: 120
Total Viewer Permissions: 400
New: 380 | Tracked: 20

FOLDER-WISE BREAKDOWN
📂 Leo AD 2500 [001-050]
   - john@gmail.com [● new]
   - jane@gmail.com [✓ tracked]

ALL UNIQUE EMAILS
  1. alice@gmail.com
  2. bob@gmail.com
```

### Import Complete
```
📥 Bulk Import Complete!

📂 Folders scanned: 120
✅ Grants imported: 380
⏭ Already tracked: 20
❌ Errors: 0

⏰ All expire in 40 days.
```

---

## 📊 Access Logs

```
📊 Activity Logs (Page 1/5)

➕ GRANT → john@gmail.com
   📂 Leo AD 2500 [001-050] 🕒 02-12 08:15

🗑 REMOVE → jane@gmail.com
   📂 Leo AD 2500 [051-100] 🕒 02-11 14:30

🔄 ROLE CHANGE → bob@gmail.com
   📂 Leo AD 2500 [001-050] 🕒 02-11 12:00
```
```
[Next ➡️]
[🗑 Clear Logs]
[🏠 Back]
```

---

## ⚙️ Settings

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

---

## 📊 /stats Analytics

```
╔══════════════════════╗
  📊 Activity Dashboard
╚══════════════════════╝

📅 Activity Count
┣ Today: 5
┣ This Week: 23
┣ This Month: 87
┗ All Time: 150

📂 Top Folder (This Month)
┗ Leo AD 2500 [001-050] (32 actions)

👤 Top Admin (This Month)
┗ Adnan (45 actions)

━━━━━━━━━━━━━━━━━━━━━━
📈 System Counts
━━━━━━━━━━━━━━━━━━━━━━
┣ ⏰ Active Timed Grants: 12
┗ 📋 Templates: 3
```

---

## 🔧 /info System Monitor

> Super admin only (first admin in ADMIN_IDS)

```
━━━━━━━━━━━━━━━━━━━━━━
🔧 System Monitor
━━━━━━━━━━━━━━━━━━━━━━

🤖 Bot Status
┣ Uptime: 2d 5h 30m
┣ Python: 3.12.0
┗ Pyrogram: 2.0.106

🗄 Database
┣ Status: ✅ Connected
┣ Admins: 1
┣ Logs: 150
┣ Grants (active): 12
┣ Grants (total): 85
┗ Templates: 3

⏰ Scheduler
┗ Auto-expire: runs every 5 min
```

---

## ❓ Help & Commands

```
╔══════════════════════╗
  ❓ Help & Commands
╚══════════════════════╝

➕ Grant Access
┗ 3 modes: single, multi-folder, multi-email

📂 Manage Folders
┗ View permissions, change roles, revoke

📋 Templates
┗ Create & apply access presets

⏰ Expiry Dashboard
┗ Timed grants, extend, revoke, bulk import

📊 Access Logs
┗ Full audit trail

⚙️ Settings
┗ Default role, page size, notifications

━━━━━━━━━━━━━━━━━━━━━━
📌 Commands
━━━━━━━━━━━━━━━━━━━━━━
/start  — Main menu
/help   — This help text
/cancel — Cancel current operation
/stats  — Activity analytics
/info   — System monitor (super admin)
/id     — Show your Telegram ID
```

---

## 🆔 /id Command

```
🆔 Your Telegram Info:

User ID: 123456789
Username: @adnank
First Name: Adnan
Is Bot: False
```

---

## 🔒 Access Denied

```
╔══════════════════════╗
  🔒 Access Restricted
╚══════════════════════╝

⚠️ You are not authorized to use this bot.
Contact the administrator for access.

🆔 Your ID: 987654321
```

---

## 🔄 Flow Diagram

```
/start
  │
  ├── ➕ Grant Access
  │     ├── 👤 Single: Email → Folder → Role → Duration → Confirm
  │     ├── 📂 Multi-Folder: Email → ☑️ Folders → Role → Duration → Confirm
  │     └── 👥 Multi-Email: Emails → Folder → Role → Duration
  │            → Duplicate Check → Confirm → Batch Execute
  │
  ├── 📋 Templates
  │     ├── ➕ Create: Name → ☑️ Folders → Role → Duration → Save
  │     ├── ▶️ Apply: Template → Email(s) → Dup Check → Execute
  │     └── 🗑 Delete
  │
  ├── 📂 Manage Folders
  │     └── Folder → User → Change Role / Remove
  │
  ├── ⏰ Expiry Dashboard
  │     ├── Extend (+1h/6h/1d/7d)
  │     ├── Revoke Now
  │     └── 📥 Bulk Import → Scan → Report → Import
  │
  ├── 📊 Access Logs → Paginated → Clear
  ├── ⚙️ Settings → Role / Page Size / Notifications
  ├── /stats → Analytics Dashboard
  ├── /info → System Monitor
  └── ❓ Help
```

---

## ⏰ Background Tasks

| Task | Interval | Action |
|------|----------|--------|
| Auto-Expire | 5 min | Revokes expired viewer grants via Drive API |

---

> 📄 **Drive Access Manager Bot** — Built with Pyrogram, MongoDB & Google Drive API
