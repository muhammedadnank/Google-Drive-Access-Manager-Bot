# 🗄️ Database Maintenance Guide

**Version:** v2.1.1-update  
**Last Updated:** February 15, 2026  
**Status:** Production-Ready with Duplicate Protection

---

## 📊 Overview

This guide covers database maintenance, duplicate prevention, and optimization for the Google Drive Access Manager Bot.

---

## 🔒 Duplicate Prevention System

### Current Protection Status: ✅ **ACTIVE**

The bot now includes **MongoDB-level duplicate prevention** to ensure data integrity.

### What's Protected:

```javascript
Unique Index: [email, folder_id, status]
Condition: status = "active"
```

**This prevents:**
- ✅ Same email + folder getting multiple active grants
- ✅ Race conditions during concurrent admin operations
- ✅ Bulk import creating duplicate entries

**This allows:**
- ✅ Same email accessing different folders
- ✅ Different emails accessing same folder
- ✅ Historical records (expired/revoked status)

---

## 🔍 Checking for Duplicates

### Using the Check Script

```bash
# Set your MongoDB URI
export MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/drive_bot"

# Run the duplicate checker
python check_duplicates.py
```

**Output:**
- Active grant duplicates
- Log entry duplicates
- Email case sensitivity issues
- Status consistency problems
- Database statistics

### Manual MongoDB Check

```javascript
// Connect to MongoDB
use drive_bot

// Find duplicate active grants
db.grants.aggregate([
    {$match: {status: "active"}},
    {$group: {
        _id: {email: "$email", folder_id: "$folder_id"},
        count: {$sum: 1},
        ids: {$push: "$_id"}
    }},
    {$match: {count: {$gt: 1}}}
])

// Check index status
db.grants.getIndexes()
```

---

## 🔧 Fixing Duplicate Issues

### Automated Fix Script

```bash
# Preview changes (dry run - safe)
python fix_duplicates.py --dry-run

# Apply fixes (requires confirmation)
python fix_duplicates.py --apply
```

**What it fixes:**
1. **Duplicate Active Grants** - Keeps oldest, removes rest
2. **Email Normalization** - Converts all to lowercase
3. **Status Consistency** - Updates expired grants
4. **Unique Index** - Creates if missing

### Backup Before Fixing

```bash
# Export MongoDB backup
mongodump --uri="YOUR_MONGO_URI" --out=backup_$(date +%Y%m%d)

# Or use MongoDB Atlas backup feature
```

---

## 📈 Database Statistics

### Collections Overview

| Collection | Purpose | Indexes |
|------------|---------|---------|
| `grants` | Access grants with expiry | 8 indexes including unique |
| `logs` | Audit trail | 2 indexes |
| `admins` | Admin users | 1 index |
| `settings` | Bot configuration | 1 index |
| `states` | Conversation flow | 1 index |
| `cache` | Folder cache | 1 index |

### Index Details

```javascript
// grants collection indexes
db.grants.getIndexes()

[
  {name: "_id_", ...},
  {name: "email_1", ...},
  {name: "folder_id_1", ...},
  {name: "role_1", ...},
  {name: "status_1", ...},
  {name: "granted_at_1", ...},
  {name: "status_1_expires_at_1", ...},
  {
    name: "unique_active_grant",
    key: {email: 1, folder_id: 1, status: 1},
    unique: true,
    partialFilterExpression: {status: "active"}
  }
]
```

---

## 🧹 Database Cleanup

### Remove Soft-Deleted Logs

```javascript
// WARNING: Permanently deletes logs marked as deleted
db.logs.deleteMany({is_deleted: true})
```

### Archive Old Grants

```javascript
// Move expired grants older than 90 days to archive
const cutoff = Date.now()/1000 - (90 * 24 * 3600);

db.grants_archive.insertMany(
  db.grants.find({
    status: {$in: ["expired", "revoked"]},
    granted_at: {$lt: cutoff}
  }).toArray()
);

db.grants.deleteMany({
  status: {$in: ["expired", "revoked"]},
  granted_at: {$lt: cutoff}
});
```

### Remove Duplicate Removed Grants

```javascript
// Clean up grants marked as duplicate_removed after review
db.grants.deleteMany({status: "duplicate_removed"})
```

---

## 🔄 Regular Maintenance Tasks

### Daily

- ✅ Auto-expire scheduler handles expired grants
- ✅ Monitor bot logs for errors

### Weekly

```bash
# Check database health
python check_duplicates.py

# Review statistics
# In bot: /stats command
```

### Monthly

```bash
# Full database backup
mongodump --uri="YOUR_MONGO_URI" --out=monthly_backup_$(date +%Y%m)

# Archive old data (optional)
# Run archive scripts if needed

# Verify index performance
# Check MongoDB Atlas metrics
```

### Quarterly

- Review and update retention policies
- Analyze query performance
- Optimize indexes if needed
- Clean up archived data

---

## 🚨 Emergency Procedures

### Database Restore

```bash
# Restore from backup
mongorestore --uri="YOUR_MONGO_URI" --dir=backup_20260215

# Verify data integrity
python check_duplicates.py
```

### Recreate Indexes

```javascript
// If indexes are corrupted or missing
db.grants.dropIndexes();

// Indexes will be recreated on bot restart
// Or manually:
db.grants.createIndex({email: 1});
db.grants.createIndex({folder_id: 1});
db.grants.createIndex({status: 1});
db.grants.createIndex({granted_at: 1});
db.grants.createIndex({status: 1, expires_at: 1});
db.grants.createIndex(
  {email: 1, folder_id: 1, status: 1},
  {
    unique: true,
    partialFilterExpression: {status: "active"},
    name: "unique_active_grant"
  }
);
```

### Remove Corrupted Data

```javascript
// Find and remove invalid grants
db.grants.deleteMany({
  $or: [
    {email: {$exists: false}},
    {folder_id: {$exists: false}},
    {status: {$exists: false}}
  ]
});
```

---

## 📊 Monitoring Queries

### Active Grants by Status

```javascript
db.grants.aggregate([
  {$group: {_id: "$status", count: {$sum: 1}}},
  {$sort: {count: -1}}
])
```

### Most Accessed Folders

```javascript
db.grants.aggregate([
  {$match: {status: "active"}},
  {$group: {_id: "$folder_name", count: {$sum: 1}}},
  {$sort: {count: -1}},
  {$limit: 10}
])
```

### Email Distribution

```javascript
db.grants.aggregate([
  {$match: {status: "active"}},
  {$group: {_id: "$email", folders: {$sum: 1}}},
  {$sort: {folders: -1}},
  {$limit: 10}
])
```

### Grants Expiring Soon

```javascript
const now = Date.now()/1000;
const tomorrow = now + 86400;

db.grants.find({
  status: "active",
  expires_at: {$gt: now, $lt: tomorrow}
}).sort({expires_at: 1})
```

---

## 🎯 Performance Optimization

### Index Usage Analysis

```javascript
// Check if indexes are being used
db.grants.find({email: "user@example.com"}).explain("executionStats")

// Should show: "stage": "IXSCAN" (index scan)
// Not: "stage": "COLLSCAN" (collection scan)
```

### Slow Query Detection

Enable profiling in MongoDB Atlas:
1. Go to Database → Profiling
2. Enable "Log slow operations"
3. Set threshold (e.g., 100ms)
4. Review slow queries weekly

### Connection Pool Settings

In `config.py`:
```python
MONGO_URI = "mongodb+srv://...?maxPoolSize=50&minPoolSize=10"
```

---

## 📝 Database Schema

### grants Collection

```javascript
{
  _id: ObjectId,
  admin_id: Number,
  email: String (lowercase),
  folder_id: String,
  folder_name: String,
  role: String ("reader" | "writer"),
  granted_at: Number (timestamp),
  expires_at: Number (timestamp),
  duration_hours: Number,
  status: String ("active" | "expired" | "revoked" | "duplicate_removed")
}
```

### logs Collection

```javascript
{
  _id: ObjectId,
  admin_id: Number,
  admin_name: String,
  action: String,
  details: Object,
  timestamp: Number,
  is_deleted: Boolean
}
```

---

## 🔐 Security Best Practices

### Access Control

- ✅ Use strong MongoDB credentials
- ✅ Enable IP whitelisting in Atlas
- ✅ Use read-only users for analytics
- ✅ Rotate credentials quarterly

### Data Protection

- ✅ Enable encryption at rest (Atlas default)
- ✅ Use TLS/SSL connections
- ✅ Regular backups (automated in Atlas)
- ✅ Test restore procedures

### Audit Trail

- ✅ All actions logged in logs collection
- ✅ Soft delete maintains history
- ✅ Admin accountability via admin_id
- ✅ Timestamp tracking on all operations

---

## 🆘 Support & Troubleshooting

### Common Issues

**Issue:** Duplicate grant errors after bot restart
**Solution:** Unique index missing - run `fix_duplicates.py --apply`

**Issue:** Slow query performance
**Solution:** Check index usage with `.explain()`, rebuild if needed

**Issue:** Connection timeout
**Solution:** Check network, verify MongoDB Atlas whitelist, increase pool size

**Issue:** Data inconsistency
**Solution:** Run `check_duplicates.py`, fix issues found

### Getting Help

1. Check logs: `/var/log/bot.log` or bot console
2. Review MongoDB Atlas metrics
3. Run diagnostic scripts
4. Check GitHub issues
5. Contact maintainers

---

## 📚 Related Documentation

- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
- [UI_GUIDE.md](UI_GUIDE.md) - User interface documentation
- [README.md](../README.md) - Main documentation

---

**Maintained by:** Google Drive Access Manager Bot Team  
**Last Review:** February 15, 2026  
**Next Review:** May 15, 2026
