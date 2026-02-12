# 🗂 Drive Access Manager — User Manual

> Complete reference guide for managing Google Drive access via Telegram.

---

## 📖 Table of Contents

1. [🏠 Main Menu](#-main-menu)
2. [➕ Granting Access](#-grant-access)
3. [📂 Managing Folders](#-manage-folders)
4. [⏰ Expiry Dashboard](#-expiry-dashboard)
5. [🔍 Advanced Search](#-advanced-search-new)
6. [📊 Activity Logs](#-activity-logs)
7. [📋 Access Templates](#-access-templates)
8. [⚙️ Settings & Channel](#-settings)

---

## 🏠 Main Menu

Starts the bot and shows the live dashboard.

**Command:** `/start`

```
╔════════════════════════════╗
  🗂 Drive Access Manager
╚════════════════════════════╝

👋 Welcome back, Admin!

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

---

## ➕ Grant Access

The bot offers 3 powerful modes to grant access.

### 1. 👤 One Email → One Folder
*Best for: Standard day-to-day grants.*

1. Select **[👤 One Email → One Folder]**.
2. **Send Email**: Type `user@gmail.com`.
3. **Select Folder**: Choose from the paginated list.
4. **Select Role**: `Viewer` or `Editor`.
5. **Select Duration**: `1 Hour` to `Permanent`.
6. **Confirm**: Review details and confirm.

### 2. 📂 One Email → Multi Folders
*Best for: Giving a user access to a project (multiple folders).*

1. Select **[📂 One Email → Multi Folders]**.
2. **Select Folders**: Tap buttons to toggle `[☑️ Folder Name]`.
3. Tap **[✅ Confirm (X selected)]**.
4. Proceed with Email, Role, and Duration.

### 3. 👥 Multi Emails → One Folder
*Best for: Onboarding a team.*

1. Select **[👥 Multi Emails → One Folder]**.
2. **Send Emails**: Send a list of emails (comma or newline separated).
   ```text
   alice@gmail.com
   bob@company.com
   carol@gmail.com
   ```
3. The bot auto-detects **Duplicates** (users who already have access).
4. Confirm to grant access to the new users only.

---

## 📂 Manage Folders

View and manage users within specific folders.

1. Tap **[📂 Manage Folders]**.
2. Select a folder to view details.

**Folder View:**
```
📂 Leo AD 2500 [001-050]
👥 3 users with access:

1. john@gmail.com     🔑 Viewer  ⏳ 29d
2. jane@gmail.com     🔑 Editor  ♾️ Perm
```

**Actions:**
- Tap a user to **Revoke Access** or **Change Role**.
- Use **[🗑 Revoke All]** to clear the entire folder.

---

## ⏰ Expiry Dashboard

Central hub for managing time-limited access.

1. Tap **[⏰ Expiry Dashboard]**.
2. View lists of **Active Grants** and **Expiring Soon**.

**Actions:**
- **[🔄 Extend]**: Add more time (+1d, +7d, etc.).
- **[🗑 Revoke]**: End access immediately.
- **[🗑 Bulk Revoke]**: Select multiple users to remove at once.

---

## 🔍 Advanced Search (NEW)

Powerful filtering to find specific access records instantly.

**Access:** Main Menu → **[🔍 Search User]**

### 1. Quick Search
Type an **Email** or **Folder Name** to find matches.
- Example: `john` finds `john@gmail.com`.
- Example: `Leo` finds `Leo AD 2500`.

### 2. Advanced Filters
Tap **[⚙️ Advanced Filters]** to narrow down results:

| Filter | Options | Description |
|--------|---------|-------------|
| **Role** | `Viewer`, `Editor` | Filter by access level |
| **Status** | `Active`, `Expired` | Filter by current state |
| **Duration** | `Timed`, `Permanent` | Filter by type |

**Result Actions:**
- **[🗑 Revoke All Found]**: Remove all access for the search results.
- **[📤 Export Verified]**: Download search results as CSV.

---

## 📊 Activity Logs

Audit trail of all actions performed by the bot.

1. Tap **[📊 Access Logs]**.
2. View latest events (Grants, Revokes, Auto-Expires).

**Export Options:**
Tap **[📤 Export as CSV]** to download logs to Telegram:
- `Today`
- `This Week`
- `This Month`
- `All Time`

---

## 📋 Access Templates

Save frequently used settings (Folder Bundles + Role + Duration) for 1-tap improvements.

**Create Template:**
1. Tap **[📋 Templates]** → **[➕ New Template]**.
2. Select Folders (e.g., "Project A Bundle").
3. Set Role & Duration.
4. Save as "Intern Access".

**Apply Template:**
1. Select "Intern Access".
2. Enter Email(s).
3. Done! The user gets access to all folders in the bundle instantly.

---

## ⚙️ Settings

Configure the bot's behavior.

### General Settings
- **Default Role**: Set Viewer or Editor as default.
- **Page Size**: Number of items per page (3-10).
- **Notifications**: Toggle admin alerts.

### 📢 Channel Configuration
Connect a Telegram Channel to receive real-time logs.

1. Go to **Settings** → **[📢 Channel Config]**.
2. Tap **[✏️ Set Channel ID]**.
3. **Forward a message** from your channel to the bot.
4. The bot will auto-detect and save the Channel ID.
   *(Make sure the Bot is an Admin in the channel first!)*

---

**Drive Access Manager Bot** v2.0.5
User Manual
