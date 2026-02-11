# 🔧 OAuth Token Setup for Render (Service Account ഇല്ലാതെ)

## Malayalam Guide

നിങ്ങൾക്ക് Service Account create ചെയ്യാൻ താൽപര്യമില്ലെങ്കിൽ, നിലവിലുള്ള OAuth credentials തന്നെ ഉപയോഗിക്കാം.

---

## Step 1: ലോക്കലിൽ Authenticate ചെയ്യുക

ആദ്യം നിങ്ങളുടെ കമ്പ്യൂട്ടറിൽ ബോട്ട് run ചെയ്യുക:

```bash
cd "/home/adnanxpkd/projects/Google Drive Access Manager"
python3 bot.py
```

ഇത് ബ്രൗസർ തുറന്ന് Google login ചോദിക്കും. Login ചെയ്ത് allow ചെയ്യുക.

അപ്പോൾ `token.pickle` എന്ന ഫയൽ create ആകും.

---

## Step 2: Token Encode ചെയ്യുക

ഈ കമാൻഡ് run ചെയ്യുക:

```bash
python3 -c "import pickle, base64; print(base64.b64encode(open('token.pickle', 'rb').read()).decode())"
```

ഇത് ഒരു long string print ചെയ്യും. അത് copy ചെയ്യുക.

---

## Step 3: Render-ൽ Environment Variable Add ചെയ്യുക

1. Render Dashboard-ൽ പോകുക: https://dashboard.render.com/
2. നിങ്ങളുടെ service select ചെയ്യുക: **google-drive-access-manager-bot**
3. **Environment** tab-ൽ click ചെയ്യുക
4. **Add Environment Variable** click ചെയ്യുക:
   - **Key**: `GOOGLE_OAUTH_TOKEN`
   - **Value**: മുകളിൽ copy ചെയ്ത string paste ചെയ്യുക
5. **Save Changes** click ചെയ്യുക

---

## Step 4: Deploy ചെയ്യുക

Render automatically redeploy ചെയ്യും. Logs-ൽ നോക്കുക:

```
✅ OAuth authentication from environment successful!
```

---

## ⚠️ പ്രധാനപ്പെട്ട കാര്യങ്ങൾ

1. **Token Expiry**: OAuth token കുറച്ച് മാസങ്ങൾക്ക് ശേഷം expire ആകും. അപ്പോൾ വീണ്ടും ഈ process ചെയ്യണം.

2. **Security**: Token secret ആണ്, ആരോടും share ചെയ്യരുത്.

3. **Service Account Better**: Production-ന് Service Account ആണ് നല്ലത്, പക്ഷേ ഇത് temporary solution ആയി use ചെയ്യാം.

---

## English Summary

If you don't want to create a Service Account, you can use your OAuth token:

1. Run bot locally to generate `token.pickle`
2. Encode it: `python3 -c "import pickle, base64; print(base64.b64encode(open('token.pickle', 'rb').read()).decode())"`
3. Add to Render as `GOOGLE_OAUTH_TOKEN` environment variable
4. Bot will use this token instead of Service Account

**Note**: OAuth tokens expire, so you'll need to refresh periodically. Service Account is recommended for production.
