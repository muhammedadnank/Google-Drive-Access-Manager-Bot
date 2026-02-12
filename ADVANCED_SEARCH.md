# 🔍 Advanced Search Guide

> Powerful filtering and search system for locating grants, users, folders, logs, and activity data instantly.

---

## 🎯 Overview

Advanced Search transforms the bot into an operational audit tool, allowing you to:

- Locate specific users across thousands of folders
- Audit folder permissions by role or status
- Filter grants by expiration status (Active vs Expired)
- Perform bulk actions on search results

---

## 🧭 How to Access

1. Open **Main Menu** (`/start`)
2. Tap **[🔍 Search User]**
3. Select **[🔍 Search by Email/Folder]** or use **[⚙️ Advanced Filters]**

---

## 🔍 Search Methods

### 1. Text Search
Simply type a keyword to find matching records.

- **By Email**: Enter `john` to find `john@gmail.com`, `john.doe@example.com`.
- **By Folder**: Enter `Leo` to find `Leo AD 2500`, `Leo Project`.

> **Note**: Search is case-insensitive.

### 2. Advanced Filters
Tap **[⚙️ Advanced Filters]** to open the filter panel. You can toggle multiple criteria:

| Filter | Options | Description |
|--------|---------|-------------|
| **Role** | `Viewer`, `Editor` | Filter by access level |
| **Status** | `Active`, `Expired`, `Revoked` | Filter by current state |
| **Duration** | `Timed`, `Permanent` | Filter by grant type |
| **Sort** | `Newest`, `Oldest` | Sort results by date |

---

## 📊 Understanding Results

Search results are displayed in a paginated list:

```text
🔍 Results for: "john" (Filters: Active, Viewer)
Found: 5 grants

1. 📂 Leo AD 2500 [001-050]
   👤 john@gmail.com
   🔑 Viewer  ⏳ 25d remaining

2. 📂 Project X
   👤 john.doe@corp.com
   🔑 Editor  ♾️ Permanent
```

### Key Indicators
- ⏳ **25d remaining**: Active grant, expires in 25 days.
- ⚠️ **Expired**: Access has expired but record exists.
- ♾️ **Permanent**: No expiry date (usually Editors).

---

## 🛠 Bulk Actions

Once you have your search results, you can perform actions on them:

- **[🗑 Revoke All Found]**: Revokes access for *all user grants* matching the current search.
- **[📤 Export Verified]**: Downloads a CSV of the search results.

---

## ⚡ Pro Tips

1. **Find "Risky" Access**:
   - Filter by **Role: Editor** + **Duration: Permanent**.
   - This shows everyone who has permanent edit access.

2. **Cleanup Audits**:
   - Filter by **Status: Expired**.
   - Revoke/Delete these records to clean up the database.

3. **User Audit**:
   - Search for a specific email (e.g., `intern@company.com`).
   - Use **[🗑 Revoke All]** to offboard them immediately.

---

**Drive Access Manager Bot** v2.0.5
