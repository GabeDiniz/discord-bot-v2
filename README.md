# 🤖 Discord-bot v2

This is my multi-purpose Discord bot! This is the second Discord bot I created (new and improved). It uses several APIs to show 🎮 game stats and info, 📈 upcoming IPOs and 🏈 NFL matchups, has basic 🗣 auto-responses, and can join your voice channel to play 🎵 music!

# 🧨 List of Commands

```
# Text Commands:
- !help | !help-music                     - list of commands
- !steamgame <app-id>                      - details for a Steam game (and whether it's on sale)
- !addwishlist <app-id>                    - add a Steam game to the server's communal wishlist
- !removewishlist <game-name> | !wishlist  - remove a game / show the wishlist
- !cs2 <name>                              - CS2 stats (only for registered players, see "CS2 players" below)
- !fn-shop                                 - today's Fortnite item shop
- !play <song or YouTube link>             - play a song, or add it to the queue
- !skip | !leave                           - skip the current song / leave the voice channel
- !gif                                     - a random GIF
- !qr <link> [fg-hex] [bg-hex]             - make a QR code, e.g. !qr https://example.com #000000 #FFFFFF
- !convert <amount> <from> <to>            - currency conversion, e.g. !convert 20 USD CAD
- !ipos [days]                             - upcoming stock IPOs in the next N days (default 7)
- !ipo <ticker>                            - details for one upcoming IPO
- !p <prompt>                              - ask the AI (Hugging Face)
- !nfl_week | !nfl_matchups                - this week's NFL games / our Sleeper league matchups

# Slash Commands:
- /event <date> <time> <description>       - create a Server Event (date YYYY-MM-DD, time HH:MM, EST)
```

### Automatic posts

- **Wishlist sales:** once a day the bot checks every server's wishlist and posts any games on sale. They go to the channel where `!addwishlist` was first used in that server.
- **Weekly IPOs:** every Sunday at 15:00 UTC the bot posts the next week's IPOs to that same channel.
- **Auto-responses:** messages that closely match a question in `resources/knowledge.json` get the matching reply.

# Want to run this bot yourself?

You'll need a bot application from https://discord.com/developers/applications, Python 3.10+ and FFmpeg (for music).

```bash
git clone <https-or-ssh>
cd discord-bot-v2

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Music needs FFmpeg on the machine
sudo apt install ffmpeg      # macOS: brew install ffmpeg
```

Create a `.env` file in the project root:

```bash
BOT_KEY="discord-bot-token"
STEAM_API_KEY="steam-api-key"                 # !steamgame, wishlist, !cs2
GIPHY_API_KEY="giphy-api-key"                 # !gif (api.giphy.com)
HUGGING_FACE_API_KEY="hugging-face-token"     # !p
EXCHANGE_RATE_API_KEY="exchangerate-api-key"  # !convert (exchangerate-api.com)
FINNHUB_API_KEY="finnhub-api-key"             # !ipos, !ipo, weekly IPO post (finnhub.io)
```

All six keys must be set, or the bot won't start. If you don't use a feature, any placeholder value works.

Then run it:

```bash
python main.py            # normal
python main.py --testing  # skips the automatic wishlist-sale and IPO posts
```

The database (`resources/bot.db`, SQLite) is created automatically on first start.

# 🖥 Hosting (how I run it)

The bot runs 24/7 on a small home server (an N100 mini PC) as a systemd service, and it updates itself from GitHub every night.

- **Bot service:** `/etc/systemd/system/discord-bot.service`, running `main.py` from the project's `.venv`.
- **Auto-update:** `deploy/install.sh` sets up `discord-bot-update.timer`. Every day at 04:00 UTC it runs `deploy/auto-update.sh`, which works like this:
  - If GitHub has new commits, it pulls them, reinstalls packages when `requirements.txt` changed, and restarts the bot.
  - If nothing changed, it does nothing.
  - If the server's copy has conflicting local changes, it stops and leaves the bot running as it was.

```bash
# One-time setup on the server
sudo deploy/install.sh

# Day to day
systemctl list-timers discord-bot-update.timer      # next scheduled update
sudo systemctl start discord-bot-update.service     # update right now
DRY_RUN=1 deploy/auto-update.sh                     # preview an update without changing anything
journalctl -u discord-bot-update.service            # update history
journalctl -u discord-bot.service -f                # live bot logs
sudo systemctl restart discord-bot.service          # manual restart
```

# 💻 Tech Stack used for this Project:

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white) ![Bash Script](https://img.shields.io/badge/bash_script-%23121011.svg?style=for-the-badge&logo=gnu-bash&logoColor=white) ![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)

# 👨‍💻 For Dev

### Database

`resources/bot.db` has three tables:

| Table | What's in it |
|---|---|
| `servers` | `guild_id`, `default_channel_id` (where sale/IPO posts go), `server_name` (filled in automatically on startup) |
| `wishlist` | one row per game per server: `guild_id`, `app_id`, `data` (Steam game details as JSON) |
| `steam_users` | `username` (lowercase) → `steam_id`, used by `!cs2` |

To view or edit it:

```bash
cp resources/bot.db resources/bot.db.bak   # back up first
sqlite3 resources/bot.db
```
```sql
.headers on
.mode column
SELECT * FROM servers;
UPDATE servers SET default_channel_id = '123456789' WHERE guild_id = '987654321';  -- IDs are text, keep the quotes
```

### CS2 players

There's no command for registering players yet. Add them straight to the database:

```sql
INSERT INTO steam_users (username, steam_id) VALUES ('name', '7656119xxxxxxxxxx');
```

### Schema changes

Bump `SCHEMA_VERSION` in `functions/db.py` and add a migration file under `migrations/`, like `migrations/001_rename_guild_config_to_servers.py`. Run migrations by hand with `python3 migrations/<file>.py` before restarting the bot.
