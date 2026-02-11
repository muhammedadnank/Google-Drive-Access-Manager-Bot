# 📂 Google Drive Access Manager Bot

A powerful Telegram bot built with **Pyrogram** to manage Google Drive permissions effortlessly. Use it to grant Viewer/Editor access, manage folder permissions, and track activity logs—all from a clean admin dashboard.

## 🚀 Features

- **Grant Access**: Add users to specific Drive folders with Viewer or Editor roles.
- **Manage Permissions**: View who has access to a folder, change roles, or remove users.
- **Activity Logs**: Track all administrative actions with timestamps.
- **Settings**: Customize default roles, page sizes, and notifications.
- **Admin Security**: Restricted to configured Telegram admins.

## 🛠 Prerequisites

- Python 3.11+
- MongoDB (Local or Atlas)
- Google Cloud Project with Drive API enabled
- Telegram Bot Token

## ⚙️ Installation

### 1. Clone & Setup
```bash
git clone https://github.com/yourusername/drive-access-bot.git
cd drive-access-bot
pip install -r requirements.txt
```

### 2. Google Drive API Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project and enable **Google Drive API**.
3. Create a **Service Account** and download the JSON key.
4. Rename the key file to `credentials.json` and place it in the project root.
5. **Important**: Open your Google Drive, right-click the folder(s) you want to manage, and **Share** them with the Service Account email address (give it Editor access).

### 3. Configuration
1. Rename `.env.example` to `.env`.
2. Fill in the details:
   ```env
   API_ID=12345
   API_HASH=abcdef123456
   BOT_TOKEN=123456:ABC-DEF
   MONGO_URI=mongodb+srv://...
   ADMIN_IDS=123456789 (Your Telegram ID)
   ```

### 4. Run the Bot
```bash
python bot.py
```

## 🎮 Usage

Send `/start` to the bot.
- **Grant Access**: Follow the flow to enter an email and select a folder.
- **Manage Folders**: Browse folders, see users, and modify permissions.
- **Logs**: View recent admin actions.

## ⚠️ Troubleshooting

- **Service Account Error**: Ensure `credentials.json` is valid and the service account has access to the target folders.
- **Database Error**: Check `MONGO_URI` and ensure MongoDB is running.
- **Bot Not Responding**: Check if `API_ID` and `API_HASH` are correct.

---
Built with ❤️ using Pyrogram & MongoDB.
