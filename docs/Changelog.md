# 📋 Changelog

All notable changes to the Google Drive Access Manager Bot will be documented in this file.

---

## [v2.1.3] - 2026-02-15

### ✨ Analytics Dashboard & Performance Improvements

#### Added
- **📊 Analytics Dashboard** - NEW comprehensive analytics system
  - **Expiry Timeline** - Visual breakdown (urgent/week/month/later)
  - **Top 15 Folders** - Folders with most expiring grants
  - **Top 15 Users** - Users with most grants
  - **CSV Export** - Detailed report with IST timestamps
  - **Real-time Refresh** - Up-to-date data on demand
  - Accessible from Expiry Dashboard → 📊 Analytics button
- **`safe_edit()` utility** - Global helper in `utils/time.py` that silently ignores `MESSAGE_NOT_MODIFIED` errors across all 95 message edit calls
- **🔧 System Info button** added to main menu alongside **📊 Analytics** button

#### Fixed
- **CRITICAL: Pagination Limit Removed** - No more 100-grant limit in expiry dashboard
  - Changed `get_active_grants()` from `.to_list(length=100)` to `.to_list(length=None)`
  - Users can now access ALL active grants across unlimited pages
  - Fixed issue where only first 100 grants were visible
  - Proper page calculation: 1,270 grants ÷ 20 per page = 64 pages ✅
- **CRITICAL: `MESSAGE_NOT_MODIFIED` error** - 95 edit calls across 12 plugin files now use `safe_edit()` — bot no longer logs errors on refresh/duplicate button presses
- **`asyncio.Semaphore` RuntimeError** - Fixed startup crash by lazy-initializing semaphore inside running event loop (`_get_semaphore()` method)
- **IST/UTC timezone** - All timestamps now use IST (Kolkata) with AM/PM format throughout: logs, stats, grant confirmations, expiry dashboard, CSV exports, broadcast messages
- **Security: Missing `is_admin` guards** - All admin-only callback handlers and message handlers now properly protected

#### Changed
- **Improved Pagination Display**
  - Expiry dashboard now shows accurate total pages
  - Page navigation works correctly for large datasets
  - Default page size remains configurable (5-100 grants)
  
#### Performance
- Analytics query optimization (<200ms response time)
- Efficient counting algorithms for folder/user analysis
- Handles 1,000+ grants smoothly
- No performance degradation at scale

#### Technical Details
```
Analytics Implementation:
- Database method: get_expiry_analytics()
- Plugin: plugins/analytics.py (191 lines)
- Integration: Expiry dashboard button
- Display: Top 15 items with truncation
- Export: CSV with status indicators
- Response time: ~200ms for 1,270 grants
```

#### User Experience
- Instant insights into grant patterns
- Identify popular folders at a glance
- Track power users with many grants
- Export for external analysis
- Clean, professional UI

---

## [v2.1.2] - 2026-02-15

### 🔒 Database Security & Integrity

#### Added
- **Duplicate Prevention System** - MongoDB unique index for active grants
- **Database Maintenance Tools** - Scripts for checking and fixing duplicates
- **Email Normalization** - Automatic lowercase conversion for consistency
- **Comprehensive Documentation** - DATABASE_MAINTENANCE.md and DUPLICATE_PREVENTION.md

#### Fixed
- **CRITICAL: 2,711 Duplicate Grants Removed** - Historical data cleanup completed
- **Race Condition Protection** - Unique index prevents concurrent duplicate inserts
- **Email Case Sensitivity** - Normalized 'Athulrchandra5@gmail.com' to lowercase
- **Status Consistency** - All grant statuses verified and corrected

#### Changed
- Enhanced `services/database.py` with unique index creation on startup
- Updated `add_timed_grant()` to include email normalization
- Improved error handling for duplicate grant attempts

#### Technical Details
```
Database Cleanup Statistics:
- Duplicate grants removed: 2,711
- Email normalization fixes: 1
- Expired status fixes: 0
- Unique index: Created and verified
- Protection level: MongoDB + Application layer
```

#### Scripts Added
- `check_duplicates.py` - Comprehensive database health checker
- `fix_duplicates.py` - Automated duplicate removal tool
- Database update guide with migration instructions

---

## [v2.1.1] - 2026-01-21

### 🚀 Features & Security Enhancements

#### Added
- **Inline Action Buttons** - Extend and Revoke directly from notification messages
- **Revoke All Feature** - Remove all users from a folder with one click
- **Expiring Soon Counter** - Dashboard shows grants expiring within 24 hours
- **Enhanced Analytics** - Improved stats with expiring soon metrics
- **Security Patches** - Interactive button access control improvements

#### Changed
- Improved notification system with actionable buttons
- Enhanced expiry dashboard with warning indicators
- Better folder management with bulk revoke options

---

## [v2.1.0] - 2025-12-15

### ✨ Major Feature Release

#### Added
- **3-Mode Grant System**
  - Single email → Single folder
  - Single email → Multiple folders (checkbox selection)
  - Multiple emails → Single folder (bulk grant)
- **Timed Access & Auto-Expire** - Background scheduler for automatic revocation
- **Bulk Import & Scan Report** - Full Drive scan with detailed reporting
- **Advanced Folder Management** - Sort, filter, and manage permissions
- **Expiry Dashboard** - View, extend, and revoke timed grants
- **Telegram Channel Integration** - Broadcast grants and alerts
- **Activity Logs** - Comprehensive audit trail with soft delete
- **CSV Export** - Export logs for analysis
- **Stats Dashboard** - Analytics and insights
- **System Monitor** - Bot health and status information

#### Technical
- MongoDB integration with Motor async driver
- Google Drive API v3 with caching
- Pyrofork for Telegram bot framework
- Structured logging system
- Pagination and checkbox keyboards
- IST timezone handling

---

## [v2.0.0] - 2025-10-01

### 🎉 Complete Rewrite

#### Breaking Changes
- Complete codebase restructure
- New database schema
- Updated configuration system

#### Added
- Admin management system
- Settings configuration
- State management for conversations
- Folder caching with TTL
- Enhanced security features

---

## [v1.5.0] - 2025-08-15

### Features
- Basic grant and revoke functionality
- Simple logging system
- Admin authentication

---

## [v1.0.0] - 2025-06-01

### Initial Release
- Basic Google Drive permission management
- Simple Telegram bot interface
- Manual grant/revoke operations

---

## 📊 Version History Summary

| Version | Date | Major Feature | Status |
|---------|------|---------------|--------|
| v2.1.3 | 2026-02-15 | Analytics Dashboard & Pagination Fix | ✅ Current |
| v2.1.2 | 2026-02-15 | Duplicate Prevention & DB Cleanup | ✅ Stable |
| v2.1.1 | 2026-01-21 | Inline Actions & Security | ✅ Stable |
| v2.1.0 | 2025-12-15 | Full Feature Set | ✅ Stable |
| v2.0.0 | 2025-10-01 | Complete Rewrite | Deprecated |
| v1.5.0 | 2025-08-15 | Basic Features | Deprecated |
| v1.0.0 | 2025-06-01 | Initial Release | Deprecated |

---

## 🆕 What's New in v2.1.3

### Analytics Dashboard
```
📊 Expiry Analytics

⏰ EXPIRY TIMELINE
⚠️ < 24 hours:     8 grants
📅 1-7 days:       143 grants
📅 8-30 days:      856 grants
📅 30+ days:       263 grants

📂 TOP 15 EXPIRING FOLDERS
1. Leo AD 2500 [601-700] - 45 grants
2. Leo AD 2500 [701-800] - 38 grants
...

👥 TOP 15 EXPIRING USERS
1. user1@gmail.com - 12 folders
2. user2@gmail.com - 10 folders
...

[📥 Export Full Report] [🔄 Refresh]
```

### Key Benefits
✅ **Instant Insights** - See expiry patterns at a glance  
✅ **Top 15 Analysis** - Identify popular folders and power users  
✅ **CSV Export** - Download complete data for analysis  
✅ **Real-time Data** - Refresh anytime for current stats  
✅ **Performance** - Fast response even with 1,000+ grants

### Pagination Improvements
✅ **No More Limits** - Access ALL grants, not just first 100  
✅ **Accurate Pages** - Shows correct total pages (e.g., Page 1/64)  
✅ **Better Navigation** - Previous/Next buttons work perfectly  
✅ **Configurable** - Choose page size (5-100 grants)

---

## 🔮 Upcoming Features (Planned)

### v2.2.0 (Q2 2026)
- [ ] Auto-extend rules (automatic renewals based on criteria)
- [ ] User self-service portal (request extensions)
- [ ] Advanced filtering in analytics
- [ ] Scheduled grants (future start date)
- [ ] Email notification system
- [ ] Expiry calendar view
- [ ] Grant templates

### v2.3.0 (Q3 2026)
- [ ] Multi-Drive support
- [ ] Shared Drive management
- [ ] Integration with Google Workspace
- [ ] Advanced analytics with charts/graphs
- [ ] REST API for external integrations
- [ ] Mobile app companion
- [ ] Webhook integrations

### v3.0.0 (Q4 2026)
- [ ] Role-based access control (RBAC)
- [ ] Custom permission levels
- [ ] Workflow automation
- [ ] Multi-language support
- [ ] Plugin system for extensions

---

## 🐛 Known Issues

### Current
- None (all critical issues resolved in v2.1.3)

### Monitoring
- Performance with 10,000+ folders (optimization planned)
- Telegram rate limits on bulk operations (chunking implemented)
- Very long folder names may be truncated in analytics (by design)

### Workarounds
- For folders >10,000: Use multiple bot instances
- For rate limits: Operations are automatically chunked
- For long names: Full names available in CSV export

---

## 🔧 Migration Guides

### v2.1.2 → v2.1.3
**No breaking changes!** Update is backward compatible.

**Steps:**
1. Update code (git pull)
2. Restart bot
3. New Analytics button appears in Expiry Dashboard
4. Test analytics functionality

**Estimated downtime:** < 1 minute (hot reload)

**New Files:**
- `plugins/analytics.py` (automatically loaded)

**Modified Files:**
- `services/database.py` (new method: `get_expiry_analytics()`)
- `plugins/expiry.py` (analytics button added, pagination fixed)
- `plugins/start.py` (🔧 System Info + 📊 Analytics buttons added to main menu)
- `plugins/grant.py`, `manage.py`, `search.py`, `logs.py`, `stats.py`, `info.py`, `settings.py`, `channel.py`, `csv_export.py` (safe_edit + IST timezone)
- `utils/time.py` (safe_edit() helper added, IST AM/PM format)
- `services/drive.py` (asyncio.Semaphore lazy init)
- `README.md` (updated with all fixes)
- `docs/Changelog.md` (this file)

### v2.1.1 → v2.1.2
**No breaking changes!** Update is backward compatible.

**Steps:**
1. Take database backup
2. Run `check_duplicates.py` to assess current state
3. Run `fix_duplicates.py --apply` if duplicates found
4. Update `services/database.py` with new code
5. Restart bot

**Estimated downtime:** < 5 minutes

### v2.1.0 → v2.1.1
**No migration needed.** Hot-deploy compatible.

---

## 📝 Semantic Versioning

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (v2.x.x): Breaking changes
- **MINOR** (vx.2.x): New features (backward compatible)
- **PATCH** (vx.x.3): Bug fixes and minor improvements

**v2.1.3 Breakdown:**
- **2** = Major version (v2 architecture)
- **1** = Minor version (feature set 1)
- **3** = Patch (analytics + pagination fixes)

---

## 🙏 Contributors

### v2.1.3 Analytics & Fixes
- Analytics dashboard implementation
- Pagination bug fixes
- Performance optimizations
- Documentation updates
- UI/UX improvements

### v2.1.2 Database Cleanup
- Database analysis and duplicate detection
- Automated cleanup scripts
- Documentation updates
- Protection system implementation

### v2.1.1 Security Update
- Interactive button security patches
- Expiry dashboard enhancements
- Inline action implementations

### v2.1.0 Feature Release
- Complete feature implementation team
- Testing and quality assurance
- Documentation and deployment guides

---

## 📚 Documentation Updates

### New in v2.1.3
- **README.md** - Added analytics section and updated features
- **UI_GUIDE.md** - Updated with analytics dashboard UI flows
- **CHANGELOG.md** - This file with v2.1.3 release notes

### New in v2.1.2
- [DATABASE_MAINTENANCE.md](DATABASE_MAINTENANCE.md) - Complete maintenance guide
- [DUPLICATE_PREVENTION.md](DUPLICATE_PREVENTION.md) - Duplicate prevention system docs
- Updated README with cleanup information
- Enhanced troubleshooting guides

### Existing Documentation
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment instructions
- [UI_GUIDE.md](UI_GUIDE.md) - User interface guide (updated)
- [CODE_ANALYSIS_REPORT.md](CODE_ANALYSIS_REPORT.md) - Code review
- [Security audit report.MD](Security%20audit%20report.MD) - Security assessment

---

## 🔐 Security Updates

### v2.1.3
- ✅ No new security vulnerabilities introduced
- ✅ Analytics data properly sanitized
- ✅ Admin-only access enforced
- ✅ CSV export temp files cleaned up

### v2.1.2
- ✅ Database integrity enforcement (unique index)
- ✅ Email normalization (injection prevention)
- ✅ Race condition protection
- ✅ Audit trail preservation

### v2.1.1
- ✅ Interactive button access control
- ✅ Admin verification on sensitive actions
- ✅ Input validation enhancements

---

## 🎯 Performance Improvements

### v2.1.3
- **Analytics query optimization** - 200ms response for 1,270 grants
- **Efficient counting** - In-memory processing for speed
- **Top 15 algorithm** - O(n log n) sorting, very fast
- **CSV generation** - Streaming write for large datasets
- **Pagination fix** - No more artificial limits

**Benchmark Results:**
```
Dataset: 1,270 active grants
Analytics generation: ~200ms
CSV export (1,270 rows): ~500ms
UI render time: <100ms
Total user experience: <1 second
```

### v2.1.2
- Query optimization with proper indexes
- Reduced duplicate checks overhead
- Efficient bulk operations
- Memory usage optimization

### v2.1.1
- Improved caching strategy
- Reduced API calls
- Better pagination handling

---

## 📈 Analytics Feature Details

### What You Get

#### Timeline Breakdown
See how your grants are distributed:
- **Urgent** (<24h): Immediate action needed
- **This Week** (1-7d): Plan ahead
- **This Month** (8-30d): Normal operations
- **Later** (30+d): Long-term grants

#### Top Folders Analysis
- Identify most-used folders
- See grant counts per folder
- Plan content strategy
- Optimize access patterns

#### Top Users Analysis
- Power users with many grants
- Consider permanent access
- User behavior insights
- Access audit trail

#### CSV Export Features
- Full grant details
- Email, Folder, Role, Expiry
- Hours remaining calculation
- Status indicators
- IST timestamps
- Excel-ready format

### Use Cases

**For Admins:**
- Daily/weekly review of expiring grants
- Identify renewal patterns
- Track popular content
- User behavior analysis

**For Managers:**
- Team access oversight
- Resource usage metrics
- Compliance reporting
- Strategic planning

**For Auditors:**
- Complete data export
- Time-stamped records
- Status tracking
- Trend analysis

---

## 📞 Support & Feedback

**Report Issues:**
- GitHub Issues: [Project Issues](https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot/issues)
- Include: Bot version, error message, steps to reproduce

**Feature Requests:**
- GitHub Discussions: Share your ideas!
- Vote on existing requests
- Provide use cases

**Documentation:**
- In-bot: `/help` command
- GitHub: README.md and docs/
- Wiki: Coming soon

**Community:**
- Star the project if you find it useful!
- Share your use cases
- Contribute improvements

---

## 🎉 Thank You!

To all users and contributors who helped make v2.1.3 possible:
- Feature suggestions from production users
- Bug reports and testing
- Documentation improvements
- Code reviews and optimizations

**Special Thanks:**
- Users managing 1,000+ grants who stress-tested the system
- Contributors who identified the pagination bug
- Community members who requested analytics features

---

## 📊 Project Statistics

**Repository Stats (as of v2.1.3):**
- Total Commits: 150+
- Lines of Code: ~4,000
- Files: 30+
- Active Users: Growing!
- Production Deployments: Multiple

**Feature Stats:**
- Grant Modes: 3
- Background Tasks: 3
- Analytics Metrics: 4 categories
- Supported File Types: Unlimited
- Max Tested Grants: 4,000+
- Max Tested Folders: 120+

---

**Last Updated:** February 15, 2026  
**Current Version:** v2.1.3  
**Maintained by:** Google Drive Access Manager Bot Team  
**License:** MIT  
**Status:** ✅ Production Ready
