# 🗂 Drive Access Manager Bot — UI Guide v2.0

> Complete visual reference of every screen, button, and flow.

---

## ✨ What's New in v2.0
**All improvements at a glance**

### 🔧 UX/Flow Improvements
- **Grant Another**: Start a new grant immediately after success — no need for `/start`.
- **Bulk Revoke**: Select and revoke multiple grants at once in Expiry Dashboard.
- **Duration Override**: Option to override template duration during application.
- **User List View**: View full list of users in a folder with roles and expiry.
- **Back Buttons**: Standardized `[⬅️ Back]` across all screens.

### 🆕 New Features
- **Search by Email**: Find all folder access for a specific user in one screen.
- **Expiry Notifications**: Auto-alert admin 24h before access expires.
- **Revoke All**: Remove all access for a user across all folders in one click.
- **Export Logs**: Download access logs as a CSV file.

### 💬 UI Text Polish
- **Timestamps**: Success/error messages now show completion time.
- **Active Expiry**: Confirm screens show the exact expiry date.
- **Descriptive Errors**: "Invalid email format" instead of generic failure.

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
┣ 📝 Total Log Entries: 45
┗ ⚠️ Expiring Soon (24h): 2

▸ Select an option below:
```
```
[➕ Grant Access]      [📂 Manage Folders]
[⏰ Expiry Dashboard]  [📋 Templates]
[📊 Access Logs]       [⚙️ Settings]
[🔍 Search User]       [❓ Help]
```

**Change from v1:**
- Added `⚠️ Expiring Soon` counter.
- Added `[🔍 Search User]` button.

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
[⬅️ Back]
```

### 👤 Single Grant Flow

**Step 1 — Email**
```
📧 Enter User Email

Send the email address to grant access to.
Or /cancel to abort.
```

**Step 2 — Folder**
```
📧 User: john@gmail.com

📂 Select a Folder:
```
```
[Leo AD 2500 [001-050]]
...
[⬅️ Prev] [Next ➡️]
[🔄 Refresh]
[⬅️ Back]
```

**Step 3 — Role**
```
🔑 Select Access Level:
```
```
[👀 Viewer]  [✏️ Editor]
[⬅️ Back]
```

**Step 4 — Duration**
```
⏰ Select Access Duration:
```
```
[1 Hour]          [6 Hours]
[1 Day]           [7 Days]
[✅ 30 Days (Default)] [♾️ Permanent]
[⬅️ Back]
```

**Step 5 — Confirm (IMPROVED)**
```
⚠️ Confirm Access Grant

📧 User: john@gmail.com
📂 Folder: Leo AD 2500 [001-050]
🔑 Role: Viewer
⏳ Duration: ⏰ 30 day(s)
📅 Expires on: 14 Mar 2026 at 09:30

Is this correct?
```
```
[✅ Confirm]  [❌ Cancel]
```

**Step 6 — Success (IMPROVED)**
```
✅ Access Granted Successfully!

User: john@gmail.com
Folder: Leo AD 2500 [001-050]
Role: Viewer
Duration: 30d
Expires: 14 Mar 2026
Granted at: 13 Feb 2026, 09:30
```
```
[➕ Grant Another]  [🏠 Main Menu]
```

---

## 📂 Multi-Folder Grant Flow

**Step 2b — Checkbox Selection**
```
📂 Select Folders (tap to toggle):
```
```
[☑️ Leo AD 2500 [001-050]]
[☐ Leo AD 2500 [051-100]]
...
[✅ Confirm (2 selected)]
[⬅️ Back]
```

**Results (Multi) — IMPROVED**
```
✅ Grant Complete!

📧 john@gmail.com | 🔑 Viewer | ⏳ 30d
📅 Expires: 14 Mar 2026

✅ Leo AD 2500 [001-050] — granted
✅ Leo AD 2500 [101-150] — granted

Completed at: 13 Feb 2026, 09:31
```
```
[➕ Grant Another]  [🏠 Main Menu]
```

---

## 👥 Multi-Email Grant Flow

**Step 3 — Duplicate Detection**
```
⚠️ Confirm Multi-Email Grant

⚠️ 2 already have access (will skip):
   • alice@gmail.com
   • bob@gmail.com

✅ 3 to grant:
   • carol@gmail.com
   ...
```
```
[✅ Grant 3 Users]
[❌ Cancel]
```

**Results**
```
✅ Multi-Email Grant Complete!
...
2/3 granted | 2 skipped (duplicates)
Completed at: 13 Feb 2026, 09:32
```
```
[➕ Grant Another]  [🏠 Main Menu]
```

---

## 📋 Access Templates

**Template List**
```
📌 New Intern    — 5 folder(s) | Viewer | 30d
```

**Apply Template — IMPROVED (Duration Override)**
```
▶️ Apply Template: New Intern
⏳ Default Duration: 30d

⏰ Use template duration or override?
```
```
[✅ Use 30d (Default)]
[⏱ Override Duration]
[⬅️ Back]
```

**Override Screen (NEW)**
```
⏰ Select Custom Duration:
(overrides template default of 30d)
```
```
[1 Hour]   [6 Hours] ...
```

---

## 📂 Manage Folders

**Folder Detail — NEW: User List View**
```
📂 Leo AD 2500 [001-050]
👥 3 users with access:

1. john@gmail.com     🔑 Viewer  ⏳ 29d
2. jane@gmail.com     🔑 Editor  ♾️ Perm
...

▸ Tap a user to manage:
```
```
[👤 john@gmail.com]
[👤 jane@gmail.com]
[🗑 Revoke All in Folder]
[⬅️ Back]
```

**User Actions**
```
👤 john@gmail.com
🔑 Current Role: Viewer
⏳ Expires: 14 Mar 2026 (29d remaining)
```
```
[🔄 Change Role]  [🗑 Remove Access]
[⬅️ Back]
```

---

## ⏰ Expiry Dashboard

**Active Grants**
```
⏰ Expiry Dashboard
📊 12 active timed grant(s)
⚠️ 2 expiring within 24 hours!

📧 john@gmail.com
   ⏳ 29d 12h remaining

📧 sarah@gmail.com  ⚠️ EXPIRING SOON
   ⏳ 18h remaining
```
```
[🔄 Extend...]  [🗑 Revoke]
[🗑 Bulk Revoke Selected]
[📥 Bulk Import]  [⬅️ Back]
```

**Bulk Revoke — NEW**
```
🗑 Bulk Revoke
Select grants to revoke:
```
```
[☑️ john@gmail.com ...]
[🗑 Revoke Selected (2)]
```

---

## 🔍 Search by Email (NEW)

**Search Screen**
```
🔍 Search User Access
Enter an email address to see active permissions.
```

**Results**
```
🔍 Results for: john@gmail.com
📊 3 active grant(s) found:

1. 📂 Leo AD 2500 [001-050] ...
2. 📂 Leo AD 2500 [101-150] ...
```
```
[🗑 Revoke All for this User]
[🔄 Search Another Email]
[⬅️ Back]
```

**Revoke All**
```
⚠️ Revoke All Access
User: john@gmail.com
This will remove access from 3 folders.
```
```
[✅ Yes, Revoke All]
```

---

## 📊 Access Logs

```
📊 Activity Logs (Page 1/5)
...
```
```
[Next ➡️]
[📤 Export as CSV]
[🗑 Clear Logs]
[⬅️ Back]
```

**Export CSV — NEW**
```
📤 Export Access Logs
Export range:
```
```
[Today]      [This Week]
[This Month] [All Time]
```

---

## 🔔 Expiry Notifications (NEW)

Bot automatically sends a notification to the admin 24 hours before any timed grant expires.

**Auto Notification Message**
```
⚠️ Expiry Alert

The following grant expires in ~24 hours:

📧 john@gmail.com
📂 Leo AD 2500 [001-050]
📅 Expires: 14 Feb 2026 at 09:30

Take action:
```
```
[🔄 Extend +7 Days]  [🗑 Revoke Now]
[⏭ Ignore]
```

---

## ⚙️ Settings

```
⚙️ Settings
...
🔹 Expiry Alert Threshold: 24 hours
```
```
[🔔 Toggle Notifications]
[⏰ Change Alert Threshold]
```

**Alert Threshold Setting — NEW**
```
[1 Hour Before]   [6 Hours Before]
[✅ 24 Hours (Default)]
```

---

## 🔧 System Monitor

```
⏰ Scheduler
┣ Auto-expire: runs every 5 min
┗ Expiry-alerts: runs every 5 min
```

---

> 📄 **Drive Access Manager Bot** — UI Guide v2.0
> Built with Pyrogram • MongoDB • Google Drive API
