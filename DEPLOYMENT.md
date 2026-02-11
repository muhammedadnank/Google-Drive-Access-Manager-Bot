# 🚀 Quick Deployment Guide - Render Web Service

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
   git commit -m "Add Render web service configuration"
   git push origin master
   ```

2. **Create Render Web Service**
   - Go to https://dashboard.render.com/
   - Click "New +" → "Web Service"
   - Connect your GitHub repo: `muhammedadnank/Google-Drive-Access-Manager-Bot`
   - Render will auto-detect `Procfile` and `render.yaml`

3. **Configure Service**
   - **Name**: `drive-access-manager-bot`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt` (auto-detected)
   - **Start Command**: `python server.py` (auto-detected from Procfile)
   - **Plan**: Free

4. **Add Environment Variables** (see above)

5. **Deploy!**
   - Click "Create Web Service"
   - Monitor logs for success messages

---

## Expected Logs

```
🌐 Starting Flask web server...
🤖 Starting Telegram bot...
🔑 Attempting Service Account authentication from environment variable...
✅ Service Account authentication successful!
🚀 Starting Bot...
✅ Bot started as @YourBotUsername (ID: ...)
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
```

---

## Web Service Endpoints

Once deployed, your service will have these endpoints:

- **`/`** - Home page with bot status
- **`/health`** - Health check endpoint (used by Render)
- **`/status`** - Detailed status information

You can access them at: `https://your-service-name.onrender.com/`

---

## Files Created

- ✅ `server.py` - Flask web server with bot integration
- ✅ `Procfile` - Web service process definition
- ✅ `render.yaml` - Infrastructure as Code (web service)
- ✅ `.gitignore` - Updated with sensitive files
- ✅ `services/drive.py` - Modified for Service Account auth
- ✅ `requirements.txt` - Added Flask and gunicorn

---

For detailed instructions, see the full deployment guide.
