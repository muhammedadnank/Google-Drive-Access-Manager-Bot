# Changelog — Drive Access Manager Bot

## v2.1.1 (Security Update)

### 🔒 Security

- **Interactive Button Protection**: All callback queries in `grant.py`, `expiry.py`, and `settings.py` now explicitly check for admin privileges (`is_admin`). This prevents unauthorized access via forwarded messages or crafted requests.

### 📁 Files Modified
| File | Change |
|------|--------|
| `plugins/grant.py` | Added `is_admin` filter to all callbacks |
| `plugins/expiry.py` | Added `is_admin` filter to all callbacks |
| `plugins/settings.py` | Added `is_admin` filter to all callbacks |
| `README.md` | Version bump and security note |

## v2.1.0 (Improved Edition)

### 🐛 Bug Fixes

- **bot.py**: Removed duplicate `expiry_checker()` function definition — previously the first (incomplete) version was silently overriding the second (full) version with broadcast support
- **grant.py**: Fixed `NameError` — `dur_text` was used inside `broadcast()` call before being defined in `execute_bulk_grant()`
- **broadcast.py**: Removed unreachable duplicate `return config` statement in `get_channel_config()`

### ✨ New Features

1. **Expiry Notification Inline Actions** (`bot.py` + `plugins/expiry.py`)
   - Admins can now **Extend +7 Days** or **Revoke Now** directly from the expiry alert message
   - No need to open the dashboard — act instantly from the notification
   - `notif_ext_` and `notif_rev_` callback handlers added

2. **Template Duration Override** (`plugins/templates.py`)
   - When applying a template, admins can now **override the default duration** before confirming
   - "Override Duration" button appears on the confirmation screen
   - "Reset to Default" option available
   - Original template duration is preserved and shown

3. **Folder User List with Expiry Info** (`plugins/manage.py`)
   - Manage Folders now shows each user's **remaining time** inline (e.g., `⏳ 29d`)
   - Permanent grants shown with `♾️`
   - **Revoke All in Folder** button added — remove all users from a folder in one action

4. **Expiring in 24h Counter in /stats** (`plugins/stats.py`)
   - `/stats` dashboard now shows `⚠️ Expiring in 24h` count

### 🔧 Improvements

- **logs.py**: Timestamps now show full date format (`13 Feb 2026, 08:15` instead of `02-13 08:15`)
- **bot.py**: Expiry notifier now uses TTL-based cleanup instead of size-based — prevents gradual memory leak over long uptime
- **database.py**: Added `get_grants_by_email()`, `get_grants_by_folder()`, `get_expiring_soon_count()` helper methods
- **start.py**: Help text updated with all new features and commands (`/search`, `/stats`, `/info`)
- **utils/states.py**: Added `CONFIRM_FOLDER_REVOKE_ALL` and `WAITING_APPLY_DURATION_OVERRIDE` states
- **config.py**: Version bumped to `2.1.0`

### 📁 Files Modified
| File | Change |
|------|--------|
| `bot.py` | Bug fix (duplicate), improved notifier with action buttons |
| `config.py` | Version bump |
| `services/broadcast.py` | Bug fix (double return) |
| `services/database.py` | 3 new helper methods |
| `plugins/grant.py` | Bug fix (dur_text NameError) |
| `plugins/expiry.py` | New: notification inline action handlers |
| `plugins/manage.py` | Improved: user list with expiry, new: folder revoke all |
| `plugins/templates.py` | New: duration override flow |
| `plugins/stats.py` | Improved: expiring 24h counter |
| `plugins/logs.py` | Improved: full date timestamps |
| `plugins/start.py` | Improved: updated help text |
| `utils/states.py` | 2 new states added |
