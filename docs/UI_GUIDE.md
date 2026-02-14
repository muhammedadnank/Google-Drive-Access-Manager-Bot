# 🗂 Drive Access Manager — User Manual

> **Version:** v2.1.1  
> **Updated:** 14 Feb 2026

This manual provides a complete guide to using the Google Drive Access Manager Bot on Telegram. It covers all commands, workflows, and administrative features.

---

## 📖 Table of Contents

1. [🚀 Getting Started](#-getting-started)
2. [🎮 Command Reference](#-command-reference)
3. [🏠 Main Menu Dashboard](#-main-menu-dashboard)
4. [➕ Granting Access (Detailed)](#-granting-access-detailed)
5. [📂 Folder Management](#-folder-management)
6. [⏰ Expiry & Auto-Revoke](#-expiry--auto-revoke)
7. [🔍 Advanced Search](#-advanced-search)
8. [📊 Activity Logs & Export](#-activity-logs--export)
9. [📢 Channel Integrations](#-channel-integrations)
10. [❓ Troubleshooting](#-troubleshooting)

---

## 🚀 Getting Started

1. **Start the Bot**: Open the bot in Telegram and tap **Start**.
2. **Authorize**: If you are an admin, you will see the Main Menu. unauthorized users will see their User ID.

---

## 🎮 Command Reference

| Command | Permission | Description |
|---------|------------|-------------|
| `/start` | Admin | Opens the Main Menu Dashboard. |
| `/stats` | Admin | Shows daily/weekly activity analytics + **Expiring in 24h** count. |
| `/search` | Admin | Quick access to User Search. |
| `/cancel` | Admin | Cancels the current operation (e.g., stops inputting an email). |
| `/id` | Anyone | Displays your Telegram User ID (useful for adding new admins). |
| `/info` | Super Admin | Displays system status (System Health, API Status). |

---

## 🏠 Main Menu Dashboard

The command center for all operations.

**Bot Response:**
```text
👋 Welcome back, Admin!

📈 Quick Stats
┣ ⏰ Active Timed Grants: 12
┣ 📝 Total Log Entries: 145
┗ ⚠️ Expiring Soon (24h): 2

▸ Select an option below:
```

**Buttons:**
- **[➕ Grant Access]**: Start the grant workflow.
- **[📂 Manage Folders]**: View folders and users.
- **[⏰ Expiry Dashboard]**: Manage active timer-based grants.
- **[ Access Logs]**: View or export audit trails.
- **[⚙️ Settings]**: Configure bot behavior and Channels.
- **[🔍 Search User]**: Find specific grants.
- **[❓ Help]**: Show quick help text.

---

## ➕ Granting Access (Detailed)

### Mode 1: One Email → One Folder
**Use Case:** Giving a single user access to a specific folder.

1. **Input Email**: Send `john.doe@gmail.com`.
2. **Select Folder**: Choose `[Project Alpha]` from the list.
3. **Select Role**: `Viewer` (Read-only) or `Editor` (Read/Write).
4. **Select Duration**:
   - `1 Hour` / `6 Hours` (Short term)
   - `1 Day` / `7 Days` / `30 Days` (Standard)
   - `Permanent` (No expiry)
5. **Confirmation**:
   ```text
   ⚠️ Confirm Access Grant
   📧 User: john.doe@gmail.com
   📂 Folder: Project Alpha
   🔑 Role: Viewer
   ⏳ Duration: 30 Days
   ```
6. **Success**: Access is applied instantly.

### Mode 2: Multi-Folder Grant
**Use Case:** Giving a user access to multiple folders at once.

1. **Select Folders**: Tap folders to toggle selection:
   - `[☑️ Project Alpha]`
   - `[☑️ Project Beta]`
   - `[☐ Project Gamma]`
2. **Confirm**: Tap `[✅ Confirm (2 selected)]`.
3. Proceed with Role and Duration selection.

### Mode 3: Multi-Email Grant
**Use Case:** Adding a team to a folder.

1. **Input Emails**: Send a list:
   ```text
   alice@company.com
   bob@company.com
   charlie@gmail.com
   ```
2. **Duplicate Check**: The bot will warn if any user *already* has access and skip them.
3. **Confirm**: Grants access to all new users in one batch.

---

## 📂 Folder Management

View who has access to a specific folder.

**Path:** Main Menu → `[📂 Manage Folders]` → Select Folder.

**Folder Details View:**
```text
📂 Project Alpha [001-050]
👥 3 users with access:

1. alice@company.com  🔑 Viewer  ⏳ 29d
2. bob@company.com    🔑 Editor  ♾️ Perm
3. admin@gmail.com    🔑 Owner   ♾️ Perm
```

**Actions:**
- Tap a user to **Revoke Access** or **Change Role**.
- **[🗑 Revoke All]**: Removes EVERYONE (except Owners) from the folder.

---

## ⏰ Expiry & Auto-Revoke

Manage time-limited access.

**Path:** Main Menu → `[⏰ Expiry Dashboard]`

**Features:**
1. **Active Grants**: Shows extensive list of all timed grants.
2. **Expiring Soon**: Highlights grants expiring in <24 hours.
3. **Bulk Actions**:
   - **[🗑 Bulk Revoke]**: Select multiple users to remove immediately.
   - **[🔄 Extend]**: Add time to a grant (e.g. +7 Days).

**🆕 Notification Inline Actions:**
When an expiry alert is sent to the channel or admin, it now includes **Action Buttons**:
- **[🔄 Extend +7 Days]**: Instantly add a week time.
- **[🗑 Revoke Now]**: Remove access immediately.

**Bulk Import:**
Use `[📥 Bulk Import]` to scan your Google Drive for existing permissions and sync them to the bot's database.

---

## 🔍 Advanced Search

Find specific access records instantly.

**Path:** Main Menu → `[🔍 Search User]`

**Search Methods:**
- **By Email**: Type `alice` to find `alice@company.com`.
- **By Folder**: Type `Alpha` to find `Project Alpha`.

**Advanced Filters Panel:**
Toggle filters to narrow down results:
- **Role**: `Viewer` or `Editor`
- **Status**: `Active`, `Expired`, or `Revoked`
- **Type**: `Timed` or `Permanent`

**Results & Actions:**
```text
🔍 Results for: "alice"
Found: 2 active grants

1. 📂 Project Alpha | Viewer | 25d left
2. 📂 Project Beta  | Editor | Permanent
```
- **[🗑 Revoke All Found]**: Instantly revoke all grants matching the search.
- **[📤 Export Verified]**: Download the search result list as a CSV file.

---

## 📊 Activity Logs & Export

Keep an audit trail of every action.

**Path:** Main Menu → `[📊 Access Logs]`

**Log Events Tracked:**
- ➕ **Grant**: New access given.
- 🗑 **Revoke**: Access removed.
- 🔄 **Update**: Role changed or time extended.
- ▪️ **Auto-Revoke**: Bot automatically removed expired user.

**CSV Export:**
Tap `[📤 Export as CSV]` to download the full log file.
- Support ranges: `Today`, `Week`, `Month`, `All Time`.
- File format: `access_logs_2026-02-14.csv` (Excel compatible).

---

## 📢 Channel Integrations

Connect a Telegram Channel to receive real-time alerts.

**Setup:**
1. Go to **Settings** → **[📢 Channel Config]**.
2. Add the Bot to your Channel as an **Administrator**.
3. Forward a message from the Channel to the Bot.
4. The bot saves the Channel ID (`-100xxxx`).

**What is Logged?**
The bot sends formatted messages to the channel for:
- ✅ **New Grants**: With User, Folder, Role, and Duration.
- 🗑 **Revokes**: When access is removed.
- ⚠️ **Expiry Alerts**: 24h before a user expires (includes **Action Buttons**).
- 🤖 **System Alerts**: Startup messages or errors.

---

## ❓ Troubleshooting

**Q: "PeerIdInvalid" Error?**
**A:** This happens if the bot hasn't "seen" the channel yet.
- **Fix:** Restart the bot using your hosting panel. The bot will auto-detect the channel on startup.

**Q: Google Drive Scan Failed?**
**A:** Check `credentials.json` or Service Account permissions.
- **Fix:** Ensure the Service Account is an **Editor** on the folders you want to manage.

**Q: How to add a new Admin?**
**A:**
1. Ask the new user to send `/id` to the bot.
2. Add their ID to the `ADMIN_IDS` list in your configuration (`.env` or Config Var).
3. Restart the bot.

---

**Power User Commands:**
- `/stats` - View detailed analytics.
- `/info` - View system health and uptime.

---
*Generated by Drive Access Manager Bot v2.1.1*
