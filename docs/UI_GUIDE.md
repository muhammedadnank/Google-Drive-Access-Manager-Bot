# 🎨 UI Guide - Google Drive Access Manager Bot

**Version:** 2.1.3  
**Last Updated:** February 15, 2026  
**Bot Name:** Stories Manager (@StoriesadminBot)

---

## 📋 Table of Contents

1. [Main Menu](#main-menu)
2. [Grant Access Flows](#grant-access-flows)
3. [Manage Folders](#manage-folders)
4. [Expiry Dashboard](#expiry-dashboard)
5. [Activity Logs](#activity-logs)
6. [Search User](#search-user)
7. [Statistics](#statistics)
8. [Settings](#settings)
9. [System Info](#system-info)
10. [Channel Integration](#channel-integration)
11. [Button Reference](#button-reference)
12. [Best Practices](#best-practices)

---

## 🏠 Main Menu

**Command:** `/start`

### Display Format

```
╔════════════════════════════╗
  🗂 Drive Access Manager
╚════════════════════════════╝

👋 Welcome back, Admin!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 BOT INFO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏷 Name     : Stories Manager
👤 Username : @StoriesadminBot
🔄 Version  : 2.1.1
⏱️ Uptime   : 3h 24m
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Button Layout

```
[➕ Grant Access]      [📂 Manage Folders]
[⏰ Expiry Dashboard]  [📋 Access Logs] 
[🔍 Search User]       [📊 Statistics]
[⚙️ Settings]          [💡 Help & Guide]
[🔧 System Info]       [📊 Analytics]
```

### Features Per Button
- **Grant Access** → 3 grant modes (single/multi-folder/bulk)
- **Manage Folders** → View users, change roles, revoke access
- **Expiry Dashboard** → View/extend/revoke timed grants
- **Access Logs** → Activity audit trail with filters
- **Search User** → Find grants by email
- **Statistics** → Analytics dashboard
- **Settings** → Bot configuration
- **Help & Guide** → Command reference
- **System Info** → System monitor (Super Admin only)
- **Analytics** → Expiry analytics with Top 15 folders/users + CSV export

---

## ➕ Grant Access Flows

### Mode Selection Screen

**Callback:** `grant_menu`

```
➕ **Grant Access**

How would you like to grant?

[👤 One Email → One Folder]
[📂 One Email → Multi Folders]  
[👥 Multi Emails → One Folder]
[🏠 Back]
```

---

### Mode 1: Single Email → Single Folder

**Callback:** `grant_mode_single`

#### Step 1: Enter Email
```
👤 **Single Grant Mode**

Send the email address to grant access.

Example: `user@gmail.com`

[❌ Cancel]
```

**Input:** User types email  
**Validation:** Email format check  
**Error:** ❌ Invalid email format!

#### Step 2: Select Folder
```
📂 **Select Folder**

Choose a folder to grant access:

📁 Leo AD 2500 [ 601 - 700 ]
📁 Leo AD 2500 [ 701 - 800 ]
📁 Leo AD 2500 [ 801 - 900 ]

[◀️ Prev] [Next ▶️]
[🏠 Back]
```

**Per Page:** 5 folders (configurable in Settings)  
**Sorting:** Smart numeric sort ([001-050] → [051-100])

#### Step 3: Select Role
```
🔑 **Select Role**

📧 user@gmail.com
📂 Leo AD 2500 [ 601 - 700 ]

Choose access level:

[👁 Viewer] [✏️ Editor]
[⬅️ Back]
```

#### Step 4: Select Duration (Viewer Only)
```
⏰ **Set Duration**

📧 user@gmail.com
📂 Leo AD 2500 [ 601 - 700 ]
🔑 Viewer

How long should access last?

[⏱ 1 Hour]  [⏱ 6 Hours]
[📅 1 Day]   [📅 7 Days]
[📅 30 Days] [♾️ Permanent]
[⬅️ Back]
```

**Note:** Editors always get permanent access (no expiry)

#### Step 5: Confirmation
```
✅ **Confirm Grant**

📧 Email: user@gmail.com
📂 Folder: Leo AD 2500 [ 601 - 700 ]
🔑 Role: Viewer
⏰ Duration: 7 Days

Grant this access?

[✅ Yes, Grant] [❌ Cancel]
```

#### Step 6: Success
```
✅ **Access Granted Successfully!**

📧 user@gmail.com
📂 Leo AD 2500 [ 601 - 700 ]
🔑 Viewer
📅 Expires: 22 Feb 2026, 06:30 PM

[➕ Grant More] [🏠 Home]
```

---

### Mode 2: Single Email → Multiple Folders

**Callback:** `grant_mode_multi`

#### Step 1: Enter Email
```
📂 **Multi-Folder Grant**

Send the email address.

Example: `user@gmail.com`

[❌ Cancel]
```

#### Step 2: Select Multiple Folders
```
📂 **Select Folders** (Page 1/20)

Check folders to grant access:

☑️ Leo AD 2500 [ 601 - 700 ]
☐ Leo AD 2500 [ 701 - 800 ]
☑️ Leo AD 2500 [ 801 - 900 ]
☐ Leo AD 2500 [ 901 - 1000 ]
☐ Leo AD 2500 [ 1001 - 1100 ]

Selected: 2 folder(s)

[◀️ Prev] [Next ▶️]
[✅ Continue] [❌ Cancel]
```

**Interaction:** Click to toggle checkbox  
**Multi-select:** Can select multiple folders across pages  
**Counter:** Shows total selected count

#### Step 3: Select Role
```
🔑 **Select Role**

📧 user@gmail.com
📂 2 folders selected

Choose access level for all:

[👁 Viewer] [✏️ Editor]
[⬅️ Back]
```

#### Step 4: Duration (Viewer Only)
```
⏰ **Set Duration**

📧 user@gmail.com
📂 2 folders selected
🔑 Viewer

How long for all folders?

[⏱ 1 Hour]  [⏱ 6 Hours]
[📅 1 Day]   [📅 7 Days]
[📅 30 Days] [♾️ Permanent]
[⬅️ Back]
```

#### Step 5: Confirmation
```
✅ **Confirm Grant**

📧 Email: user@gmail.com
📂 Folders: 2 selected
   • Leo AD 2500 [ 601 - 700 ]
   • Leo AD 2500 [ 801 - 900 ]
🔑 Role: Viewer
⏰ Duration: 7 Days

Grant access to all?

[✅ Yes, Grant All] [❌ Cancel]
```

#### Step 6: Processing
```
⏳ **Granting Access...**

Progress: 1/2 folders
✅ Leo AD 2500 [ 601 - 700 ]
⏳ Leo AD 2500 [ 801 - 900 ]

Please wait...
```

#### Step 7: Success
```
✅ **Bulk Grant Complete!**

📧 user@gmail.com
✅ Granted: 2 folders
❌ Failed: 0
⏭ Skipped: 0 (duplicates)

📅 All expire: 22 Feb 2026, 06:30 PM

[➕ Grant More] [🏠 Home]
```

---

### Mode 3: Multiple Emails → Single Folder

**Callback:** `grant_mode_bulk`

#### Step 1: Enter Multiple Emails
```
👥 **Multi-Email Grant**

Send multiple email addresses.
Separate with **comma** or **new line**.

Example:
`alice@gmail.com, bob@gmail.com`

Or:
`alice@gmail.com`
`bob@gmail.com`

Max: 50 emails per batch

[❌ Cancel]
```

**Input Validation:**
- Maximum 50 emails per batch
- Maximum 10,000 characters
- Auto-deduplication
- Email format validation

#### Step 2: Validation Results
```
✅ **Email Validation**

✅ Valid: 3 emails
❌ Invalid: 1 email

Valid emails:
• alice@gmail.com
• bob@gmail.com
• charlie@gmail.com

Invalid:
• not-an-email (invalid format)

[✅ Continue with Valid] [❌ Cancel]
```

#### Step 3: Select Folder
```
📂 **Select Folder** (Page 1/20)

Choose ONE folder for all emails:

📁 Leo AD 2500 [ 601 - 700 ]
📁 Leo AD 2500 [ 701 - 800 ]
📁 Leo AD 2500 [ 801 - 900 ]

[◀️ Prev] [Next ▶️]
[⬅️ Back]
```

#### Step 4: Select Role
```
🔑 **Select Role**

👥 3 emails
📂 Leo AD 2500 [ 601 - 700 ]

Choose access level for all:

[👁 Viewer] [✏️ Editor]
[⬅️ Back]
```

#### Step 5: Duration (Viewer Only)
```
⏰ **Set Duration**

👥 3 emails
📂 Leo AD 2500 [ 601 - 700 ]
🔑 Viewer

How long for all emails?

[⏱ 1 Hour]  [⏱ 6 Hours]
[📅 1 Day]   [📅 7 Days]
[📅 30 Days] [♾️ Permanent]
[⬅️ Back]
```

#### Step 6: Confirmation
```
✅ **Confirm Bulk Grant**

👥 Emails: 3
   • alice@gmail.com
   • bob@gmail.com
   • charlie@gmail.com
📂 Folder: Leo AD 2500 [ 601 - 700 ]
🔑 Role: Viewer
⏰ Duration: 7 Days

Grant access to all?

[✅ Yes, Grant All] [❌ Cancel]
```

#### Step 7: Processing with Duplicate Detection
```
⏳ **Granting Access...**

Processing: 2/3 emails

✅ alice@gmail.com - Granted
⏭ bob@gmail.com - Already has access
⏳ charlie@gmail.com - Processing...

Please wait...
```

#### Step 8: Success Summary
```
✅ **Bulk Grant Complete!**

📂 Leo AD 2500 [ 601 - 700 ]
👥 3 emails processed

✅ Granted: 2 emails
⏭ Skipped: 1 (already had access)
❌ Failed: 0

📅 All expire: 22 Feb 2026, 06:30 PM

Details:
✅ alice@gmail.com
⏭ bob@gmail.com (duplicate)
✅ charlie@gmail.com

[➕ Grant More] [🏠 Home]
```

---

## 📂 Manage Folders

**Callback:** `manage_folders`

### Folder List View
```
📂 **Manage Folders** (Page 1/20)

Total: 100 folders

📁 Leo AD 2500 [ 601 - 700 ] (3 users)
📁 Leo AD 2500 [ 701 - 800 ] (5 users)
📁 Leo AD 2500 [ 801 - 900 ] (2 users)
📁 Leo AD 2500 [ 901 - 1000 ] (0 users)
📁 Leo AD 2500 [ 1001 - 1100 ] (7 users)

[◀️ Prev] [Next ▶️]
[🔄 Refresh Cache] [🏠 Back]
```

**Features:**
- Shows user count per folder
- Smart numeric sorting
- Cached with configurable TTL (default 10 min)
- Manual refresh button

### Folder Details View
```
📂 **Folder: Leo AD 2500 [ 601 - 700 ]**

👥 Users with access: 3

1️⃣ vineeth421@gmail.com
   🔑 Viewer | 📅 Expires: 14 Mar 2026
   ⏳ 26d 15h remaining
   [🔄 Change Role] [⏰ Extend] [🗑 Remove]

2️⃣ shabeershajahan005@gmail.com  
   🔑 Viewer | 📅 Expires: 14 Mar 2026
   ⏳ 26d 20h remaining
   [🔄 Change Role] [⏰ Extend] [🗑 Remove]

3️⃣ alice@gmail.com
   🔑 Editor | ♾️ Permanent
   [🔄 Change Role] [🗑 Remove]

[🗑 Revoke All Users] [⬅️ Back]
```

**Actions Per User:**
- **Change Role:** Toggle Viewer ↔️ Editor
- **Extend:** Add more time (timed grants only)
- **Remove:** Revoke access

**Bulk Action:**
- **Revoke All:** Remove ALL users from folder

### Change Role Flow
```
🔄 **Change Role**

📧 vineeth421@gmail.com
📂 Leo AD 2500 [ 601 - 700 ]
🔑 Current: Viewer

Change to:

[✏️ Make Editor]
[❌ Cancel]
```

**Success:**
```
✅ Role changed!

vineeth421@gmail.com is now an Editor
⚠️ Expiry removed (Editors are permanent)

[⬅️ Back to Folder]
```

### Extend Access Flow
```
⏰ **Extend Access**

📧 vineeth421@gmail.com
📂 Leo AD 2500 [ 601 - 700 ]
📅 Current expiry: 14 Mar 2026

Add extra time:

[+1 Hour]    [+6 Hours]
[+1 Day]     [+7 Days]
[+14 Days]   [+30 Days]
[⬅️ Back]
```

**Success:**
```
✅ Extended by 7 Days!

📧 vineeth421@gmail.com
📅 New expiry: 21 Mar 2026

[⬅️ Back to Folder]
```

### Remove Access Flow
```
⚠️ **Remove Access?**

📧 vineeth421@gmail.com
📂 Leo AD 2500 [ 601 - 700 ]

This will revoke access immediately.

[🗑 Yes, Remove] [❌ Cancel]
```

**Success:**
```
✅ Access removed!

vineeth421@gmail.com can no longer access
Leo AD 2500 [ 601 - 700 ]

[⬅️ Back to Folder]
```

### Revoke All Users Flow
```
⚠️ **Revoke ALL Users?**

📂 Leo AD 2500 [ 601 - 700 ]
👥 3 users will lose access:
   • vineeth421@gmail.com
   • shabeershajahan005@gmail.com
   • alice@gmail.com

This action cannot be undone.

[🗑 Yes, Revoke All] [❌ Cancel]
```

**Processing:**
```
⏳ **Revoking All Users...**

Progress: 2/3

✅ vineeth421@gmail.com
✅ shabeershajahan005@gmail.com
⏳ alice@gmail.com

Please wait...
```

**Success:**
```
✅ **Revoke All Complete!**

📂 Leo AD 2500 [ 601 - 700 ]

✅ Revoked: 3 users
❌ Failed: 0

The folder now has no viewer/editor permissions.

[⬅️ Back to Folders]
```

---

## ⏰ Expiry Dashboard

**Callback:** `expiry_menu`

### Main Dashboard View
```
⏰ **Expiry Dashboard** (Page 1/64)
📊 1270 active timed grant(s)
⚠️ **8 expiring within 24 hours!**

📧 `vineeth421@gmai...`  ⚠️ EXPIRING SOON
   📂 Leo AD 2500 [ 601 - 700 ] | 🔑 Viewer
   ⏳ 2h 15m remaining  |  📅 15 Feb 2026, 09:00 PM

[🔄 Extend vineeth421@gmai] [🗑]

📧 `shabeershajahan...`
   📂 Leo AD 2500 [ 701 - 800 ] | 🔑 Viewer
   ⏳ 26d 20h remaining  |  📅 14 Mar 2026

[🔄 Extend shabeershajahanONNO5] [🗑]

📧 `shabeershajahan...`
   📂 Leo AD 2500 [ 801 - 900 ] | 🔑 Viewer
   ⏳ 26d 20h remaining  |  📅 14 Mar 2026

[🔄 Extend shabeershajahan005] [🗑]

[◀️ Prev] [Next ▶️]
[🗑 Bulk Revoke] [📥 Bulk Import]
[⬅️ Back]
```

**Key Features:**
- **20 grants per page** (configurable in Settings)
- **Total pages:** Based on active grants (1270 ÷ 20 = 64 pages)
- **Expiring Soon Alert:** Shows count of grants < 24h
- **Visual Warning:** ⚠️ emoji for urgent expirations
- **Inline Actions:** Extend and Revoke buttons per grant

### Expiry Notification (Auto-sent by Bot)
```
⚠️ **Expiry Alert**

📧 `vineeth421@gmail.com`
📂 Leo AD 2500 [ 601 - 700 ]
🔑 Viewer
⏳ ~2h remaining
📅 Expires: 15 Feb 2026, 09:00 PM

Take action:

[🔄 Extend +7 Days] [🗑 Revoke Now]
[⏭ Ignore]
```

**Notification Timing:**
- Sent 1 hour before expiry
- Only once per grant (TTL-based tracking)
- Maximum 20 notifications per batch

### Bulk Import Feature

#### Step 1: Initiate Scan
```
📥 **Bulk Import Existing Permissions**

This will:
1. Scan ALL folders in your Google Drive
2. Find existing viewer permissions
3. Import them with 40-day expiry
4. Skip already tracked permissions

⏳ Estimated time: 2-5 minutes
(depends on folder count)

[✅ Start Scan] [❌ Cancel]
```

#### Step 2: Scanning Progress
```
📥 **Scanning... (30/120 folders)**
👁 Viewers found: 45
```

**Updates:** Every 10 folders

#### Step 3: Scan Complete with Report
```
📥 **Drive Scan Report**

📂 Folders: **120**
👁 Viewers: **89**
🆕 New: **45** | ⏭ Tracked: **44**
👤 Unique emails: **23**

📄 Detailed report sent as file
```

**File:** `drive_scan_report.txt`

**File Contents:**
```
==========================================================
  **GOOGLE DRIVE FULL SCAN REPORT**
  Generated: 15 Feb 2026, 06:52 PM IST
==========================================================

Total Folders: 120
Total Viewer Permissions: 89
New (not tracked): 45
Already Tracked: 44
Unique Emails: 23

==========================================================
  FOLDER-WISE BREAKDOWN
==========================================================

📂 Leo AD 2500 [ 601 - 700 ]
   ID: 1a2b3c4d5e6f
   Viewers (3):
     - vineeth421@gmail.com [✓ tracked]
     - alice@gmail.com [● new]
     - bob@gmail.com [● new]

📂 Leo AD 2500 [ 701 - 800 ]
   ID: 2b3c4d5e6f7g
   No viewer permissions

==========================================================
  ALL UNIQUE EMAILS
==========================================================
  1. alice@gmail.com
  2. bob@gmail.com
  3. charlie@gmail.com
  ...

--- End of Report ---
```

#### Step 4: Confirmation
```
⏰ Import all **45** new viewer grants with **40-day expiry**?

[✅ Import 45 Grants] [❌ Cancel]
```

#### Step 5: Import Progress
```
📥 **Scanning folders... (30/120)**
✅ Imported: 12 | ⏭ Skipped: 5
```

#### Step 6: Complete
```
📥 **Bulk Import Complete!**

📂 Folders scanned: **120**
✅ Grants imported: **45**
⏭ Already tracked: **44**
❌ Errors: **0**

⏰ All imported grants expire in **40 days**.

[⏰ View Dashboard] [🏠 Main Menu]
```

### Bulk Revoke Menu
```
🗑 **Bulk Revoke**

📊 Active grants: **1270**
⚠️ Expiring soon: **8**

Select what to revoke:

[⚠️ Revoke Expiring Soon (8)]
[📅 Revoke by Date Range]
[📁 Revoke by Folder]
[👤 Revoke by Email Domain]
[⬅️ Back]
```

#### Option 1: Revoke Expiring Soon
```
⚠️ **Revoke Expiring Soon**

8 grants expiring within 24 hours:
• vineeth421@gmail.com (2 folders)
• alice@gmail.com (1 folder)
• bob@gmail.com (5 folders)

Revoke all NOW?

[🗑 Yes, Revoke All 8] [❌ Cancel]
```

#### Option 2: Revoke by Date Range
```
📅 **Revoke by Date Range**

Revoke grants expiring:

[📅 Today]
[📅 This Week]
[📅 This Month]
[📅 Custom Range]
[⬅️ Back]
```

#### Option 3: Revoke by Folder
```
📁 **Revoke by Folder**

Select folder to revoke ALL grants:

📁 Leo AD 2500 [ 601 - 700 ] (3 grants)
📁 Leo AD 2500 [ 701 - 800 ] (5 grants)
📁 Leo AD 2500 [ 801 - 900 ] (2 grants)

[◀️ Prev] [Next ▶️]
[⬅️ Back]
```

#### Option 4: Revoke by Domain
```
👤 **Revoke by Email Domain**

Send domain to revoke (e.g., @gmail.com)

All emails matching this domain will be revoked.

[❌ Cancel]
```

---

## 📋 Activity Logs

**Callback:** `logs_menu`

### Main Logs View
```
📋 **Activity Logs** (Page 1/5)

Total: 93 logs

🔍 Filter: All Actions

➕ **GRANT**
👤 Admin Name
📧 user@gmail.com
📂 Leo AD 2500 [ 601 - 700 ]
🔑 Viewer | ⏰ 7 Days
📅 15 Feb 2026, 06:30 PM

🗑 **REMOVE**
👤 Admin Name
📧 old@gmail.com
📂 Leo AD 2500 [ 801 - 900 ]
📅 15 Feb 2026, 05:15 PM

🔄 **ROLE CHANGE**
👤 Admin Name
📧 editor@gmail.com
📂 Leo AD 2500 [ 601 - 700 ]
🔄 Viewer → Editor
📅 15 Feb 2026, 03:00 PM

[◀️ Prev] [Next ▶️]
[🔍 Filter] [📥 Export CSV] [🗑 Clear Logs]
[⬅️ Back]
```

**Log Types with Icons:**
- ➕ **Grant** - New access granted
- 🗑 **Remove** - Manual revoke
- 🔄 **Role Change** - Viewer ↔️ Editor
- ▪️ **Auto Revoke** - Automatic expiry
- 📥 **Bulk Import** - Mass import
- 📤 **Bulk Revoke** - Mass revoke

### Filter Menu
```
🔍 **Filter Logs**

Current: All Actions

[➕ Grants Only]
[🗑 Removes Only]
[🔄 Role Changes Only]
[▪️ Auto Revokes Only]
[📥 Bulk Imports Only]
[🔄 Show All]
[⬅️ Back]
```

### CSV Export Menu
```
📥 **Export Logs to CSV**

Select time range:

[📅 Today]
[📅 This Week]
[📅 This Month]
[📅 All Time]
[⬅️ Back]
```

**CSV Format:**
```csv
timestamp,admin_name,action,email,folder_name,role,duration,details
2026-02-15 18:30:00,Admin Name,grant,user@gmail.com,Leo AD 2500 [ 601 - 700 ],viewer,7 days,
2026-02-15 17:15:00,Admin Name,remove,old@gmail.com,Leo AD 2500 [ 801 - 900 ],,,
```

### Clear Logs Confirmation
```
⚠️ **Clear All Logs?**

This will soft-delete all 93 logs.
They won't be permanently lost but hidden from view.

[🗑 Yes, Clear] [❌ Cancel]
```

**Success:**
```
✅ **Logs Cleared!**

93 logs soft-deleted.
Database still retains them for recovery.

[⬅️ Back]
```

---

## 🔍 Search User

**Callback:** `search_menu`

### Search Input Screen
```
🔍 **Search User**

Send email address to search grants.

Example: `user@gmail.com`

[❌ Cancel]
```

### Search Results - Found
```
🔍 **Search Results**

📧 vineeth421@gmail.com

Active grants: **2**

1️⃣ 📂 Leo AD 2500 [ 601 - 700 ]
   🔑 Viewer | ⏰ Timed
   📅 Expires: 14 Mar 2026
   ⏳ 26d 15h remaining
   [🔄 Extend] [🗑 Revoke]

2️⃣ 📂 Leo AD 2500 [ 1001 - 1100 ]
   🔑 Editor | ♾️ Permanent
   [🗑 Revoke]

[🗑 Revoke All 2 Grants] [🏠 Home]
```

### Search Results - Not Found
```
🔍 **Search Results**

📧 notfound@gmail.com

❌ No active grants found.

This user has no access to any folders.

[🔍 Search Again] [🏠 Home]
```

### Revoke All from Search
```
⚠️ **Revoke All Grants?**

📧 vineeth421@gmail.com
📊 2 active grants

Folders:
• Leo AD 2500 [ 601 - 700 ]
• Leo AD 2500 [ 1001 - 1100 ]

Remove access from all folders?

[🗑 Yes, Revoke All] [❌ Cancel]
```

---

## 📊 Statistics

**Command:** `/stats` or Callback: `stats_menu`

### Stats Dashboard
```
📊 **Activity Statistics**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 ACTIVITY OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Today: 12 actions
📅 This Week: 87 actions
📅 This Month: 245 actions
📊 All Time: 1,543 actions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ GRANTS STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Active Timed Grants: 1,270
⚠️ Expiring Soon (24h): 8
📂 Tracked Folders: 120

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆 TOP PERFORMERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📂 Most Accessed Folder:
   Leo AD 2500 [ 601 - 700 ]
   (45 actions this month)

👤 Most Active Admin:
   Admin Name
   (123 actions this month)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Last updated: 15 Feb 2026, 06:52 PM

[🔄 Refresh] [🏠 Home]
```

**Metrics Tracked:**
- Daily/Weekly/Monthly action counts
- Active timed grants count
- Expiring soon count (< 24 hours)
- Most accessed folder (by action count)
- Most active admin (by action count)

---

## ⚙️ Settings

**Callback:** `settings_menu`

### Settings Menu
```
⚙️ **Bot Settings**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 CURRENT CONFIGURATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔑 Default Role: Viewer
📄 Folder Page Size: 5 folders/page
📄 Expiry Page Size: 20 grants/page
⏰ Cache TTL: 10 minutes
🔔 Notifications: Enabled

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[🔑 Change Default Role]
[📄 Folder Page Size]
[📄 Expiry Page Size]
[⏰ Cache TTL]
[🔔 Toggle Notifications]
[📢 Channel Settings]
[🏠 Back]
```

### Change Default Role
```
🔑 **Default Access Role**

Current: Viewer

When granting access, what should be the default role?

[👁 Viewer (Recommended)]
[✏️ Editor]
[⬅️ Back]
```

### Folder Page Size
```
📄 **Folder Page Size**

Current: 5 folders/page

How many folders to show per page in Manage Folders?

[3]  [5]  [7]  [10]
[⬅️ Back]
```

### Expiry Page Size
```
📄 **Expiry Page Size**

Current: 20 grants/page

How many grants to show per page in Expiry Dashboard?

[10]  [20]  [30]
[50]  [100]
[⬅️ Back]
```

### Cache TTL
```
⏰ **Cache TTL (Time To Live)**

Current: 10 minutes

How long to cache folder lists before refreshing?

[5 min]  [10 min]  [15 min]
[30 min]  [60 min]
[⬅️ Back]
```

### Toggle Notifications
```
🔔 **Notification Settings**

Current: Enabled

Toggle expiry notifications:

[🔕 Disable Notifications]
[⬅️ Back]
```

When disabled:
```
🔔 **Notification Settings**

Current: Disabled

[🔔 Enable Notifications]
[⬅️ Back]
```

### Channel Settings
```
📢 **Channel Integration**

Current: Not Configured

[📝 Setup Channel ID]
[🔬 Test Channel Access]
[⬅️ Back to Settings]
```

#### Setup Channel ID
```
📢 **Setup Channel ID**

Forward any message from your channel here, or send the channel ID manually.

Format: `-1001234567890`

Channel features:
• Grant/revoke notifications
• Daily summary reports
• Error alerts

[❌ Cancel]
```

**After Setup:**
```
✅ **Channel Configured!**

Channel ID: -1001234567890
Status: Connected ✅

The bot will now broadcast:
• Grant notifications
• Revoke notifications  
• Daily summaries
• Error alerts

[🔬 Send Test Message] [⬅️ Back]
```

#### Test Channel Access
```
🔬 **Testing Channel Access...**

Attempting to send test message...
```

**Success:**
```
✅ **Channel Test Successful!**

Test message sent to channel.
Bot has proper posting permissions.

[⬅️ Back]
```

**Failure:**
```
❌ **Channel Test Failed!**

Error: PeerIdInvalid

Possible issues:
1. Bot not added to channel
2. Incorrect channel ID
3. Bot not made admin

Fix:
1. Add bot to channel
2. Make bot admin
3. Grant "Post Messages" permission
4. Try again

[🔄 Retry] [⬅️ Back]
```

---

## 🔧 System Info

**Command:** `/info` (Super Admin Only)

### System Monitor
```
🔧 **System Information**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 BOT STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏷 Name: Stories Manager
🆔 Bot ID: 8506569349
👤 Username: @StoriesadminBot
🔄 Version: 2.1.1
⏱️ Uptime: 21m
📅 Started: 15 Feb 2026, 06:30 PM

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👥 Admins: 1
📁 Cached Folders: 1
📊 Total Grants: 4,009
✅ Active Grants: 1,270
📋 Total Logs: 93

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔌 SERVICE STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗄️ Database: ✅ Connected
📂 Google Drive: ✅ Connected
📢 Telegram: ✅ Connected

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ AUTO-EXPIRE SCHEDULER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: ✅ Running
Check Interval: Every 5 minutes
Last Run: 15 Feb 2026, 06:50 PM
Processed: 3 grants

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔔 EXPIRY NOTIFIER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: ✅ Running
Check Interval: Every 1 hour
Last Run: 15 Feb 2026, 06:00 PM
Sent: 5 notifications

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💻 SYSTEM RESOURCES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🖥️ OS: Linux 6.8.0-1045-aws
🏗️ Architecture: x86_64
🐍 Python: 3.13.4
📦 Pyrofork: 2.3.69

💾 RAM Usage: 33.0% (9GB / 30GB)
💽 Disk Usage: 87.1% (336GB / 386GB)
⚡ CPU Usage: 41.1%
🧵 CPU Cores: 8

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🕐 Last updated: 15 Feb 2026, 06:52:24 PM

[🔄 Refresh] [🏠 Home]
```

**Access:** Only first admin ID in ADMIN_IDS (Super Admin)

---

## 📢 Channel Integration

### Broadcast Message Formats

#### Grant Notification
```
➕ **Access Granted**

📧 user@gmail.com
📂 Leo AD 2500 [ 601 - 700 ]
🔑 Viewer
⏰ 7 Days
📅 Expires: 22 Feb 2026, 06:30 PM

👤 By: Admin Name
🕐 15 Feb 2026, 06:30 PM
```

#### Revoke Notification
```
🗑 **Access Revoked**

📧 old@gmail.com
📂 Leo AD 2500 [ 801 - 900 ]

👤 By: Admin Name
🕐 15 Feb 2026, 05:15 PM
```

#### Auto-Revoke Notification
```
⏰ **Auto-Expired**

📧 expired@gmail.com
📂 Leo AD 2500 [ 601 - 700 ]

⚙️ By: Auto-Expire System
🕐 15 Feb 2026, 08:00 PM
```

#### Bulk Import Notification
```
📥 **Bulk Import Complete**

✅ Imported: 45 grants
⏭ Skipped: 44 (already tracked)
❌ Errors: 0
📂 Folders: 120

⏰ All expire in 40 days

👤 By: Admin Name
🕐 15 Feb 2026, 07:00 PM
```

#### Daily Summary
```
📊 **Daily Summary**

📅 Date: 15 Feb 2026

━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 TODAY'S ACTIVITY
━━━━━━━━━━━━━━━━━━━━━━━━━━
➕ Grants: 23
🗑 Revokes: 8
🔄 Role Changes: 5
▪️ Auto-Revokes: 3
📊 Total: 39 actions

━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ GRANTS STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Active: 1,270
⚠️ Expiring Soon: 8

━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆 TOP FOLDER TODAY
━━━━━━━━━━━━━━━━━━━━━━━━━━
📂 Leo AD 2500 [ 601 - 700 ]
   (12 actions)

🕐 Generated: 15 Feb 2026, 11:59 PM
```

#### Error Alert
```
⚠️ **System Alert**

Error: Failed to auto-revoke expired grant

📧 user@gmail.com
📂 Leo AD 2500 [ 601 - 700 ]

Please check manually.

🕐 15 Feb 2026, 08:05 PM
```

---

## 🎯 Button Reference

### Complete Button Map

| Button | Callback Data | Action |
|--------|---------------|--------|
| ➕ Grant Access | `grant_menu` | Show grant mode selector |
| 📂 Manage Folders | `manage_folders` | Show folder list |
| ⏰ Expiry Dashboard | `expiry_menu` | Show expiry dashboard |
| 📋 Access Logs | `logs_menu` | Show activity logs |
| 🔍 Search User | `search_menu` | Show search input |
| 📊 Statistics | `stats_menu` | Show stats dashboard |
| ⚙️ Settings | `settings_menu` | Show settings |
| 💡 Help & Guide | `help_menu` | Show help text |
| 🔧 System Info | N/A | Command `/info` only |
| 🏠 Back / Home | `main_menu` | Return to main menu |
| ❌ Cancel | `cancel_flow` | Cancel current operation |

### Grant Mode Buttons

| Button | Callback Data | Mode |
|--------|---------------|------|
| 👤 One Email → One Folder | `grant_mode_single` | Single grant |
| 📂 One Email → Multi Folders | `grant_mode_multi` | Multi-folder |
| 👥 Multi Emails → One Folder | `grant_mode_bulk` | Bulk grant |

### Duration Buttons

| Button | Callback Data | Duration |
|--------|---------------|----------|
| ⏱ 1 Hour | `dur_1` | 1 hour |
| ⏱ 6 Hours | `dur_6` | 6 hours |
| 📅 1 Day | `dur_24` | 1 day |
| 📅 7 Days | `dur_168` | 7 days |
| 📅 30 Days | `dur_720` | 30 days |
| ♾️ Permanent | `dur_perm` | No expiry |

### Pagination Buttons

| Button | Callback Data Pattern | Action |
|--------|----------------------|--------|
| ◀️ Prev | `{context}_page_{page-1}` | Previous page |
| Next ▶️ | `{context}_page_{page+1}` | Next page |

Examples:
- `expiry_page_2` - Expiry dashboard page 2
- `folders_page_5` - Folders list page 5
- `logs_page_3` - Logs page 3

---

## 💡 Best Practices

### For Admins

1. **Default Settings:**
   - Keep default role as "Viewer" (safer)
   - Use 20 grants/page for expiry dashboard (optimal)
   - Set cache TTL to 10 minutes (balance freshness/API calls)

2. **Granting Access:**
   - Use 7-day or 30-day expiry for viewers (recommended)
   - Only use Permanent for editors or long-term viewers
   - Use Bulk Import for initial setup
   - Use Multi-Email mode for same folder, multiple users

3. **Monitoring:**
   - Check Expiry Dashboard daily
   - Review "Expiring Soon" alerts
   - Use Search to audit specific users
   - Export logs monthly for records

4. **Performance:**
   - Refresh folder cache before bulk operations
   - Use pagination for large datasets
   - Monitor disk space (alert at 85%)
   - Run bulk operations during low-usage hours

5. **Security:**
   - Review logs regularly for unusual activity
   - Use channel integration for audit trail
   - Keep admin list minimal
   - Regularly revoke inactive users

### For Developers

1. **Database:**
   - Active grants: 1270 (your scale)
   - Pagination: 20/page = 64 pages ✅
   - Fix `.to_list(length=100)` → `.to_list(length=None)`
   - Index on (email, folder_id, status) for fast queries

2. **Caching:**
   - Folder cache: TTL-based (MongoDB)
   - Notification tracking: In-memory with TTL cleanup
   - Clear cache after bulk operations

3. **Background Tasks:**
   - Expiry checker: Every 5 minutes
   - Expiry notifier: Every 1 hour
   - Daily summary: Every 24 hours
   - Batch size: 100 grants max per check

4. **Error Handling:**
   - Log all Drive API errors
   - Broadcast critical errors to channel
   - Implement retry logic for transient failures
   - Mark grants as "revocation_failed" if Drive API fails

5. **Scaling Considerations:**
   - Current: 4K grants, 1.3K active ✅
   - Optimize at: 5K active (add Redis cache)
   - Shard at: 10K+ active (read replicas)
   - Monitor: RAM, CPU, Disk, API quota

---

## 🎓 UI/UX Principles

### Consistency

- **Icons:** Same icons for same actions across screens
- **Colors:** ✅ success, ❌ error, ⚠️ warning, ℹ️ info
- **Buttons:** Standard [Action Text] format
- **Timestamps:** IST timezone, consistent format

### Clarity

- **Page numbers:** Always show (Page X/Y)
- **Counts:** Show totals (e.g., "1270 grants", "93 logs")
- **Actions:** Clear labels ("Yes, Revoke" not just "Yes")
- **Status:** Use emojis and text together

### Feedback

- **Loading states:** Show progress during long operations
- **Success messages:** Confirm completed actions
- **Error messages:** Explain what went wrong and how to fix
- **Inline actions:** Immediate response to button clicks

### Navigation

- **Back buttons:** Every screen has a way back
- **Breadcrumbs:** Show context ("Folder: Leo AD 2500 [601-700]")
- **Home button:** Quick return to main menu
- **Cancel option:** Always available during input flows

### Accessibility

- **Clear labels:** Descriptive button text
- **Icons with text:** Don't rely on icons alone
- **Pagination:** Show current position clearly
- **Truncation:** Show "..." for long text with full details below

---

## 🔄 Version History

### v2.1.1 (Current)
- ✅ Fixed NoSQL injection vulnerabilities
- ✅ Fixed memory leak in expiry notifier
- ✅ Added security patches for interactive buttons
- ✅ Improved access control

### v2.1.0
- ✅ Added inline action buttons in expiry notifications
- ✅ Added Revoke All functionality
- ✅ Improved analytics with "Expiring Soon" counter
- ✅ Enhanced UI with better formatting

### v2.0.0
- ✅ Complete rewrite with Pyrofork
- ✅ MongoDB integration
- ✅ Plugin-based architecture
- ✅ Telegram channel integration
- ✅ Auto-expiry system

---

## 📞 Support

For issues or questions:
1. Check `/help` command in bot
2. Review [README.md](../README.md)
3. Check [docs/](.) for detailed guides
4. Open issue on GitHub

---

**End of UI Guide v2.1.1**

*Last updated: February 15, 2026*
*Bot: Stories Manager (@StoriesadminBot)*
