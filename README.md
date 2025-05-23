# 🎵 T2MusicBot - Telegram Music Downloader
![T2MusicBot Logo](https://img.shields.io/badge/T2MusicBot-v2.0.0-blueviolet?style=for-the-badge&logo=telegram)

A lightning-fast Telegram bot that downloads and delivers high-quality MP3s with album artwork directly to your Telegram chats. Developed by **Taz**.

## ✨ Features
- 🎧 Ultra high-quality MP3 downloads (320kbps)
- 🖼️ Album artwork included in each track
- 🔍 Smart search handles typos and partial names
- ⚡ Lightning-fast processing & delivery
- 📱 Works seamlessly within Telegram

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- FFmpeg (optional, for audio conversion)
- Telegram Bot API token

### Installation
1. Clone the repository
```bash
git clone https://github.com/Tazhossain/musicbot.git
cd musicbot
```

2. Install required dependencies
```bash
pip install -r requirements.txt
```

3. Set up your Telegram Bot API token
```bash
# Create .env file to add your token
echo "API_TOKEN=YOUR_TELEGRAM_BOT_TOKEN" > .env
```

4. Run the bot
```bash
python bot.py
```

## 🤖 Bot Commands
- `/start` - Display welcome message
- `/help` - Show help information
- `/about` - Bot information
- Simply send any song name to search (e.g., `Blinding Lights The Weeknd`)

## 🏗️ Project Structure
```
t2musicbot/
├── bot.py                 # Main bot code
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── start.sh               # Startup script (for deployment)
├── README.md              # This documentation
└── downloads/             # Temporary download directory (auto-created)
```

## ☁️ Deployment
This bot can be easily deployed on various platforms including Render, Heroku, or your own server.

### Deploying on Render
1. Sign up for a [Render account](https://render.com/)
2. Choose **Background Workers** as your resource type
3. Connect your GitHub repository
4. Set environment variables:
   - `API_TOKEN`: Your Telegram Bot API token
5. Set the start command to `bash start.sh`
6. Deploy!

## 📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [pytubefix](https://github.com/JuanBindez/pytubefix)
- [youtube-search-python](https://github.com/alexmercerind/youtube-search-python)

## 📞 Contact
For issues or suggestions, please open an issue on GitHub.

---
Made with ❤️ by Taz
