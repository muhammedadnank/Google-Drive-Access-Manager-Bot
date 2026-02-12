# 🔍 Advanced Search — Drive Access Manager Bot

> Powerful filtering and search system for locating grants, users, folders, logs, and activity data instantly.

---

## 🎯 Purpose

As the number of users, folders, and access records grows, basic search becomes insufficient.

Advanced Search allows admins to:

- Locate specific users quickly
- Audit folder permissions
- Filter by role/status/time
- Investigate issues
- Perform targeted bulk actions
- Export filtered results

---

## 🧠 Design Philosophy

The search system is built with **progressive complexity**:

| Level | Description |
|------|-------------|
Basic Search | Fast lookup with minimal input |
Advanced Filters | Optional filters for precision |
Combined Search | Multi-condition query |
Saved Filters | Reusable queries (future) |

Default UI must remain simple.

---

## 🧭 Entry Points

Advanced Search can be accessed from:

- Main Menu → 🔍 Search
- Manage Folders → Search User
- Logs → Filter
- Stats → Drill-down search

---

## 🧪 Basic Search UI

```

🔍 Search

Search by email or folder name:

[________________________]

[Search]
[Advanced Filters ▼]

```

Basic search should:

- Accept partial text
- Be case insensitive
- Match both email and folder name

---

## ⚙ Advanced Filters Panel

Opened when user taps **Advanced Filters**.

```

Advanced Filters

Role:
☑ Viewer
☑ Editor

Status:
☑ Active
☐ Expired
☐ Revoked

Date Range:
From [01 Feb 2026]
To   [13 Feb 2026]

Duration:
☑ Timed
☑ Permanent

Admin:
[All Admins ▼]

[Apply Filters]

```

---

## 🔍 Search Types

---

### 1️⃣ Search by Folder Name

```

Folder: Leo AD 2500

```

Returns all users who have access to matching folders.

Use cases:

- Audit access for specific folder
- Check permission distribution
- Review sensitive folders

---

### 2️⃣ Search by Email

```

Email: [john@gmail.com](mailto:john@gmail.com)

```

Returns all folders user has access to.

Use cases:

- Investigate user permissions
- Troubleshoot access issues
- Review active grants

---

### 3️⃣ Role-Based Filtering

Filter results by role.

```

Show:
☑ Viewers
☑ Editors

```

Use cases:

- Audit editors only
- Check permanent access holders
- Identify risky permissions

---

### 4️⃣ Status Filtering

```

Status:
☑ Active
☐ Expired
☐ Revoked

```

Use cases:

- Find expired users
- Investigate revoked access
- Track system cleanup

---

### 5️⃣ Date Range Search

```

From: 01 Feb 2026
To: 13 Feb 2026

```

Search by:

- Grant date
- Revoke date
- Role change date

Use cases:

- Weekly reports
- Audit history
- Investigate specific time period

---

### 6️⃣ Combined Search (Power Mode)

```

Email: [john@gmail.com](mailto:john@gmail.com)
Folder: Leo AD
Role: Viewer
Status: Active
Date: Last 30 days

```

Returns only results matching ALL conditions.

---

## 📊 Results Display

```

Results (8)

[john@gmail.com](mailto:john@gmail.com)

├ Leo AD 2500 [001-050] | Viewer | 25d left
├ Leo AD 2500 [051-100] | Viewer | 18d left
└ Leo AD 2500 [101-150] | Viewer | 12d left

```

---

## 🧾 Result Actions

Search results allow direct actions:

```

[📊 Export Results]
[🗑 Bulk Revoke]
[🔄 Change Role]

````

Actions apply to filtered results only.

---

## 📤 Export Behavior

Exports should include only filtered results.

Supported formats:

- CSV (default)
- JSON (optional future)
- Excel (future)

Example CSV:

```csv
Email,Folder,Role,Status,Granted,Expires
john@gmail.com,Leo AD 2500 [001-050],Viewer,Active,2026-02-01,2026-03-01
````

---

## ⚡ Performance Strategy

To ensure fast searches even with large datasets:

### Required MongoDB Indexes

```js
db.grants.createIndex({ email: 1 })
db.grants.createIndex({ folder_id: 1 })
db.grants.createIndex({ created_at: -1 })
db.grants.createIndex({ role: 1 })
db.grants.createIndex({ status: 1 })
```

Logs collection:

```js
db.logs.createIndex({ timestamp: -1, action: 1 })
```

---

### Query Optimization Rules

* Always paginate results
* Never return full dataset
* Limit results to 20–50 per page
* Avoid regex unless indexed
* Cache frequent searches (future)

---

## 📄 Pagination UI

```
Results (127)

[Result List]

[⬅ Prev] [Page 1/7] [Next ➡]
```

---

## ⭐ Future Enhancements

---

### Saved Filters

Admins can save frequently used searches:

```
Saved Searches:
• Expiring Soon Users
• Editors Only
• Last Week Activity
```

---

### Smart Search Suggestions

Autocomplete suggestions while typing:

```
jo → john@gmail.com
le → Leo AD 2500 [001-050]
```

---

### Risk Detection Filters

Examples:

* Users with >10 folder access
* Editors with permanent access
* Expired but still active users

---

### Analytics Mode

Convert search results into stats:

```
Viewer count: 45
Editor count: 12
Avg duration: 23 days
```

---

## 🔐 Security Rules

Search results must respect permissions:

* Non-admins cannot search
* Admins only see allowed folders (future multi-admin mode)
* Sensitive logs hidden unless Super Admin

---

## 🏆 Feature Status

| Component         | Status     |
| ----------------- | ---------- |
| Basic Search      | ✅ Ready    |
| Advanced Filters  | ✅ Specced  |
| Combined Search   | ✅ Specced  |
| Pagination        | ✅ Required |
| Export Results    | ✅ Planned  |
| Saved Filters     | ⏳ Future   |
| Smart Suggestions | ⏳ Future   |
| Analytics Mode    | ⏳ Future   |

---

## 📌 Summary

Advanced Search transforms the bot from:

Basic permission tool
→ into
Operational audit system

It enables:

* Fast investigation
* Targeted management
* Data analysis
* Compliance tracking

---

**Drive Access Manager Bot**
Built with Pyrogram · MongoDB · Google Drive API
