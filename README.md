# 🤖 Discord-bot v2

This is my multi-purpose Discord bot! This is the second Discord bot I created (new and improved). It utilizes several APIs to display 🎮 game statistics and information. It has basic response 🗣 commands, and it can join your voice channel to play 🎵 music!

# Want to run this bot yourself?

Assuming you have created a new Discord-bot (Application) at https://discord.com/developers/applications, you'll need to do the following.

```bash
# Download the repository
git clone <https-or-ssh>

# Create env file and add the following keys:
BOT_KEY="bot-application-key"
STEAM_API_KEY="steam-api-key"   # for Steam feature

# Follow the "For Dev section below"
```

# 💻 Tech Stack used for this Project:

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

# 👨‍💻 For Dev:

```bash
# To run locally:
py main.py

# Ensure all necessary libraries are installed. See list below:
pip install discord.py
pip install requests
pip install python-decouple
pip install yt_dlp
pip install pynacl
```
