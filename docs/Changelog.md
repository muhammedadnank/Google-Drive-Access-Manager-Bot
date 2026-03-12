# Changelog

All notable changes to **Google Drive Access Manager Bot** are documented here.  
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [v2.2.3] — 2026-03-12

### ✨ Added

#### New Bot Commands
All major features are now accessible via direct `/command` — previously only reachable through inline menu buttons.

| Command | Plugin | Description |
|---------|--------|-------------|
| `/grant` | `grant.py` | Grant Drive access |
| `/manage` | `manage.py` | Manage folder permissions |
| `/expiry` | `expiry.py` | Expiry dashboard |
| `/logs` | `logs.py` | Activity logs |
| `/analytics` | `analytics.py` | Analytics & CSV export |
| `/settings` | `settings.py` | Bot settings |

#### Docker Support
- **`Dockerfile`** — Python 3.11.9-slim base image, non-root `botuser` for security, real `HEALTHCHECK` via curl
- **`docker-compose.yml`** — single-command local/VPS deploy with automatic log rotation (`max-size: 10m`, `max-file: 3`)
- **`.dockerignore`** — properly excludes `.env`, `*.session`, `credentials.json`, `__pycache__`, `.git`, IDE files

#### server.py Enhancements
- **`/metrics` endpoint** — new endpoint returning `active_grants`, `expiring_soon`, `bot_running`, `restart_count`
- **`/status` endpoint** — now returns `uptime`, `uptime_secs`, `restart_count`, `bot_pid`, `last_exit_code`, `version`, `python`
- **Startup banner** — logs Python version, platform info, and PID on every launch
- **Exponential backoff** — restart delay: `5s → 10s → 20s → 40s → max 60s`; resets to `5s` after ≥5 min stable run

#### grant.py Enhancements
- Mode label shown in email prompt (`👤 Single` / `📂 Multi-Folder` / `👥 Batch`) for user context
- Confirmation messages now include `🕐 Granted at` / `🕐 Completed` timestamps
- Email auto-lowercased on receive for consistency and security

---

### 🐛 Fixed

#### grant.py
| # | Bug | Fix |
|---|-----|-----|
| 1 | **`toggle_folder` inverted label** — `answer()` was called *after* mutating `selected` set, so "Selected"/"Deselected" was always wrong | Capture `is_now_selected` **before** `add()`/`discard()` |
| 2 | **`select_duration` duplicated logic** — manually re-implemented `format_duration()` inline | Replaced with `format_duration(duration_hours)` call |
| 3 | **`import re` / `import time` inside function bodies** | Moved to top-level imports |
| 4 | **`cancel_flow`** passed `callback_query.message` to `safe_edit` | Now passes `callback_query` directly (consistent with all other handlers) |

#### manage.py — 12 locations
`safe_edit(callback_query.message, ...)` → `safe_edit(callback_query, ...)` across:

`list_manage_folders` · `list_folder_users` · `manage_user_actions` · `prompt_change_role` · `execute_role_change` · `execute_remove` · `confirm_remove` · all success/error responses

#### expiry.py — 3 locations
`remove_access()` was missing the required `db` argument (needed for OAuth credential lookup), causing silent failures on revoke:
- `execute_revoke`
- `bulk_revoke_execute`
- `notif_revoke_grant`

#### stats.py — 5 locations
`safe_edit(update.message, ...)` / `safe_edit(callback_query.message, ...)` → correct form in all stats rendering handlers

#### info.py — 3 locations
`safe_edit(update.message, ...)` / `safe_edit(callback_query.message, ...)` → correct form in `show_info_dashboard`, config view, logs view

#### channel.py — 1 location
`safe_edit(callback_query.message, ...)` → `safe_edit(callback_query, ...)` in channel settings handler

#### settings.py
`check_state` import was placed mid-file (after function definitions using it) — moved to top-level imports

#### pagination.py
- All item buttons were unstyled (Telegram dark/default color) — added `ButtonStyle.PRIMARY` to item rows, nav, refresh, and back buttons
- Page indicator (e.g. `3/4`) now uses `ButtonStyle.DANGER` (red) for clear visual distinction
- Checkbox selected folders use `ButtonStyle.SUCCESS` (green); unselected use `ButtonStyle.PRIMARY` (blue)
- `create_pagination_keyboard` and `create_checkbox_keyboard` now accept optional `*_style` parameters for per-call customization

#### server.py
| # | Bug | Fix |
|---|-----|-----|
| 1 | `/health` always returned `200 OK` even when bot subprocess was dead | Now polls `bot_process.poll()` — returns `503` if not running |
| 2 | `bot_status["running"]` dict had threading race condition | Replaced with `threading.Event` (`_bot_running`, `_shutdown`) |
| 3 | `stream_output(pipe, label)` — `label` param passed but never used | Now appears as `[BOT]` prefix in all streamed log lines |
| 4 | Restart delay was always fixed at `5s` regardless of crash frequency | Replaced with exponential backoff |

---

### 🔧 Changed

- **`/oauth/callback`** page replaced with dark-themed HTML — auto-selects URL on load, copy button with visual feedback, step-by-step instructions
- **BotFather `/setcommands`** updated with 6 new commands (see below)

---

### 📋 Updated BotFather Command List

```
start - 🏠 Main dashboard
grant - ➕ Grant Drive access
manage - 🗂 Manage folder permissions
expiry - ⏰ Expiry dashboard
search - 🔍 Search user by email
stats - 📈 View statistics
analytics - 📊 Analytics & CSV export
logs - 📝 Activity logs
settings - ⚙️ Bot settings
auth - 🔑 Connect Google account
authstatus - ✅ Check auth status
revoke - 🔓 Disconnect Google account
info - 🖥 System monitor
quickstats - ⚡ Quick stats overview
cancel - ❌ Cancel current operation
help - 💡 Help & guide
id - 🆔 Show your Telegram user ID
about - ℹ️ About this bot
```

---

## [v2.2.2] — Initial Release

### ✨ Added
- **Plugins** — Grant, Manage, Expiry, Analytics, Logs, Settings, Search, Stats, Auth, Info, Channel
- **MongoDB** — timed grants with auto-expiry checker (every 5 min via background task)
- **Google Drive OAuth** — Render-compatible URL paste flow, credential stored in MongoDB
- **Expiry notifier** — hourly check with inline action buttons (Extend +7d / Revoke Now / Ignore)
- **Bulk operations** — bulk revoke all / bulk revoke expiring; bulk import from Drive scan
- **Scheduled reports** — daily summary (24h) + weekly report (7d) via broadcast service
- **Render deployment** — `render.yaml`, `Procfile`, `gunicorn` in requirements
- **Flask web server** — `/health`, `/status`, `/oauth/callback` endpoints
- **Pagination** — `create_pagination_keyboard` and `create_checkbox_keyboard` utilities
- **Natural sort** — folder names sorted with numeric awareness (`[1]`, `[2]`, `[10]` not `[1]`, `[10]`, `[2]`)

---

[v2.2.3]: https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot/releases/tag/v2.2.3
[v2.2.2]: https://github.com/muhammedadnank/Google-Drive-Access-Manager-Bot/releases/tag/v2.2.2
