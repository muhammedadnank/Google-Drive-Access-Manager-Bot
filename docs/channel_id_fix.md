# 🔧 Fix: Channel ID Not Persisting After Bot Restart

## 🐛 Problem Analysis

### Issue Description:
Channel ID സെറ്റ് ചെയ്താൽ work ചെയ്യുന്നു, but bot restart ചെയ്യുമ്പോൾ channel ID വീണ്ടും set ചെയ്യണം.

### Root Cause:

**The code is working correctly!** ✅ 

Actually, the issue is **NOT** with the code — it's likely one of these scenarios:

---

## 🔍 Possible Causes & Solutions

### Cause 1: Database Not Connected ❌

**Issue:** MongoDB connection failing silently

**Check:**
```python
# In bot.py line 185
await db.init()
```

**Verify:**
```bash
# Check MongoDB logs
# Look for connection errors
```

**Test:**
```python
# Add this after db.init() in bot.py
config = await db.get_setting("channel_config")
print(f"Current channel config: {config}")
```

**Fix:** Ensure MongoDB URI is correct in `.env`:
```env
MONGO_URI=mongodb://localhost:27017/drive_bot
# OR for cloud MongoDB
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/drive_bot
```

---

### Cause 2: Session File Reset 🔄

**Issue:** Using file-based Pyrogram session which resets

**Check if this file exists:**
```
drive_bot.session
```

**Problem:** If this file is deleted/reset on restart, settings might reset.

**Fix:** This shouldn't affect MongoDB settings, but check if you're running in a container that resets filesystem.

---

### Cause 3: Multiple Bot Instances 🤖🤖

**Issue:** Running multiple bot instances with different databases

**Symptoms:**
- Set channel in Instance A
- Restart uses Instance B (different database)

**Check:**
```bash
# Are you running multiple bots?
ps aux | grep bot.py
```

**Fix:** Ensure you're using the same MongoDB database and session.

---

### Cause 4: Code Actually Has a Bug 🐛

**Let me check the actual issue:**

Looking at `services/broadcast.py` line 11-37:

```python
async def get_channel_config():
    config = await db.get_setting("channel_config")
    
    if config and config.get("channel_id"):
        try:
            config["channel_id"] = int(str(config["channel_id"]).strip())
        except:
            pass

    if not config:  # ⚠️ THIS IS THE BUG!
        # Default config
        config = {
            "channel_id": None,
            "log_grants": True,
            # ...
        }
    return config

    return config  # Also duplicate return
```

### 🎯 THE ACTUAL BUG:

**Line 24-35:** If `config` is `None` (not set), it returns default with `channel_id: None`

**BUT:** The bug is the condition check!

```python
if not config:
    # Returns default with channel_id: None
```

This should be checking if config exists OR if it's an empty dict!

---

## ✅ Proper Fix

### Fix 1: Update `services/broadcast.py`

**Current Code (Lines 11-37):**
```python
async def get_channel_config():
    """Retrieve channel configuration from DB."""
    config = await db.get_setting("channel_config")
    
    if config and config.get("channel_id"):
        try:
            config["channel_id"] = int(str(config["channel_id"]).strip())
        except:
            pass

    if not config:
        # Default config
        config = {
            "channel_id": None,
            "log_grants": True,
            "log_revokes": True,
            "log_role_changes": True,
            "log_bulk": True,
            "log_alerts": True,
            "log_summary": True
        }
    return config

    return config  # Unreachable duplicate
```

**Fixed Code:**
```python
async def get_channel_config():
    """Retrieve channel configuration from DB."""
    config = await db.get_setting("channel_config")
    
    # Default config if nothing exists
    if config is None:
        config = {
            "channel_id": None,
            "log_grants": True,
            "log_revokes": True,
            "log_role_changes": True,
            "log_bulk": True,
            "log_alerts": True,
            "log_summary": True
        }
    
    # Ensure channel_id is integer if exists
    if config.get("channel_id"):
        try:
            config["channel_id"] = int(str(config["channel_id"]).strip())
        except Exception as e:
            LOGGER.error(f"Invalid channel_id format: {e}")
            config["channel_id"] = None
    
    return config
```

**Changes:**
1. Fixed `if not config:` → `if config is None:` (handles empty dict properly)
2. Removed duplicate return statement
3. Moved channel_id conversion AFTER default config
4. Added error logging for invalid channel_id

---

### Fix 2: Add Verification in `bot.py`

Add this after `db.init()` to verify settings are loading:

**Location:** `bot.py` after line 185

```python
async def main():
    # Connect to MongoDB
    await db.init()
    
    # 🆕 ADD THIS: Verify channel config loads
    try:
        channel_config = await db.get_setting("channel_config")
        if channel_config:
            LOGGER.info(f"✅ Channel config loaded: ID={channel_config.get('channel_id')}")
        else:
            LOGGER.info("⚠️ No channel config found - using defaults")
    except Exception as e:
        LOGGER.error(f"❌ Failed to load channel config: {e}")
    
    # Authenticate Drive Service
    if drive_service.authenticate():
        LOGGER.info("✅ Google Drive Service authenticated!")
    # ... rest of code
```

---

### Fix 3: Ensure Settings Are Actually Saving

Update `plugins/channel.py` to add confirmation logging:

**Location:** `plugins/channel.py` lines 93-96

```python
# Current code:
config = await get_channel_config()
config["channel_id"] = channel_id
await db.update_setting("channel_config", config)
await db.delete_state(user_id)

# 🆕 ADD VERIFICATION:
config = await get_channel_config()
config["channel_id"] = channel_id
await db.update_setting("channel_config", config)

# Verify it was saved
saved_config = await db.get_setting("channel_config")
LOGGER.info(f"✅ Channel ID saved: {saved_config.get('channel_id')}")

await db.delete_state(user_id)
```

---

## 🧪 Testing Procedure

### Test 1: Check Database Connection

```python
# Create test_db.py
import asyncio
from services.database import db
from config import MONGO_URI

async def test():
    print(f"Testing MongoDB: {MONGO_URI}")
    await db.init()
    
    # Try saving a test setting
    await db.update_setting("test_key", "test_value")
    
    # Try reading it back
    value = await db.get_setting("test_key")
    print(f"Test value: {value}")
    
    if value == "test_value":
        print("✅ Database is working!")
    else:
        print("❌ Database NOT saving properly!")
    
    # Test channel config specifically
    test_config = {"channel_id": -1001234567890, "log_grants": True}
    await db.update_setting("channel_config", test_config)
    
    loaded = await db.get_setting("channel_config")
    print(f"Channel config saved: {loaded}")

asyncio.run(test())
```

**Run:**
```bash
python test_db.py
```

---

### Test 2: Check Settings Persistence

```bash
# 1. Start bot
python bot.py

# 2. Set channel ID via bot
# Use /start → Settings → Channel Settings

# 3. Check database directly (using MongoDB shell or GUI)
# If using CLI:
mongosh
use drive_bot
db.settings.find({key: "channel_config"})

# 4. Restart bot
# Check if channel_id still shows

# 5. Check logs
tail -f bot.log | grep "Channel"
```

---

## 📋 Complete Fix Checklist

Apply these changes:

### Step 1: Fix broadcast.py ✅
```python
# File: services/broadcast.py
# Replace lines 11-37 with fixed version above
```

### Step 2: Add Verification in bot.py ✅
```python
# File: bot.py
# Add channel config verification after db.init()
```

### Step 3: Add Logging in channel.py ✅
```python
# File: plugins/channel.py
# Add save verification in receive_channel_id()
```

### Step 4: Test Database Connection ✅
```bash
python test_db.py
```

### Step 5: Verify MongoDB ✅
```bash
# Check if MongoDB is actually running
systemctl status mongodb
# OR
ps aux | grep mongo
```

### Step 6: Check Environment Variables ✅
```bash
# Verify .env file
cat .env | grep MONGO_URI
```

---

## 🚀 Quick Fix Implementation

### Create Fixed Files:

#### 1. Fixed broadcast.py
```python
# services/broadcast.py
from services.database import db
from config import ADMIN_IDS
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import PeerIdInvalid, ChannelPrivate
import logging
import time
from utils.time import get_current_time_str

LOGGER = logging.getLogger(__name__)

async def get_channel_config():
    """Retrieve channel configuration from DB."""
    config = await db.get_setting("channel_config")
    
    # Initialize default config if nothing exists
    if config is None:
        config = {
            "channel_id": None,
            "log_grants": True,
            "log_revokes": True,
            "log_role_changes": True,
            "log_bulk": True,
            "log_alerts": True,
            "log_summary": True
        }
        LOGGER.info("Using default channel config")
    
    # Convert channel_id to int if it exists
    if config.get("channel_id"):
        try:
            config["channel_id"] = int(str(config["channel_id"]).strip())
            LOGGER.debug(f"Channel ID loaded: {config['channel_id']}")
        except Exception as e:
            LOGGER.error(f"Invalid channel_id format: {e}")
            config["channel_id"] = None
    
    return config

# ... rest of the file remains the same
```

---

## 🎯 Most Likely Issue

Based on the code analysis, the issue is:

### **The `if not config:` check on line 24**

```python
if not config:  # ❌ WRONG
```

This will trigger even if `config = {}` (empty dict), because empty dict is falsy in Python!

**Should be:**
```python
if config is None:  # ✅ CORRECT
```

### Example Scenario:

```python
# When channel_id is set:
config = {"channel_id": -1001234567890, "log_grants": True}
await db.update_setting("channel_config", config)

# On restart, MongoDB returns:
config = {"channel_id": -1001234567890, "log_grants": True}

# But if somehow it returns empty dict:
config = {}

# Original code: if not config → TRUE! (empty dict is falsy)
# So it resets to defaults!

# Fixed code: if config is None → FALSE (empty dict is not None)
# Settings preserved!
```

---

## 🛠️ Apply The Fix

### Quick Command:

```bash
# Backup first
cp services/broadcast.py services/broadcast.py.backup

# Apply fix manually or use this:
```

I'll create the fixed file:
