# 🚀 Quick Deployment Guide

## Convert credentials.json to Environment Variable

Run this command to get the single-line JSON for `GOOGLE_CREDENTIALS`:

```bash
python -c "import json; print(json.dumps(json.load(open('credentials.json'))))"
```

Copy the output and use it as the value for `GOOGLE_CREDENTIALS` in Render.

---

## Render Environment Variables

Set these in Render Dashboard → Environment:

```
API_ID= 
API_HASH= 
BOT_TOKEN=
MONGO_URI= 
ADMIN_IDS= 
GOOGLE_CREDENTIALS=<paste the single-line JSON from above>
```

> [!WARNING]
> Replace `GOOGLE_CREDENTIALS` with the actual JSON output from the command above!

---

## Deployment Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

2. **Create Render Service**
   - Go to https://dashboard.render.com/
   - Click "New +" → "Background Worker"
   - Connect your GitHub repo
   - Render will auto-detect `Procfile`

3. **Add Environment Variables** (see above)

4. **Deploy!**
   - Click "Create Background Worker"
   - Monitor logs for success messages

---

## Expected Logs

```
🔑 Attempting Service Account authentication from environment variable...
✅ Service Account authentication successful!
🚀 Starting Bot...
✅ Bot started as @YourBotUsername (ID: ...)
```

---

## Files Created

- ✅ `Procfile` - Worker process definition
- ✅ `render.yaml` - Infrastructure as Code
- ✅ `.gitignore` - Updated with sensitive files
- ✅ `services/drive.py` - Modified for Service Account auth

---

For detailed instructions, see the full deployment guide.
