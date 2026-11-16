# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A multi-purpose Discord bot (Python, discord.py 2.7) with features for:
- Steam game lookups, and per-server wishlists with a daily sale check
- music playback
- the Fortnite shop
- CS2 stats
- QR codes
- currency conversion
- upcoming IPOs (Finnhub), with a weekly post
- NFL matchups (ESPN + Sleeper)
- AI chat (Hugging Face)
- keyword-based auto-responses

## Running the Bot

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Requires .env with: BOT_KEY, STEAM_API_KEY, GIPHY_API_KEY, HUGGING_FACE_API_KEY,
# EXCHANGE_RATE_API_KEY, FINNHUB_API_KEY (all read at import time, so all must exist)
python main.py

# Testing mode: skips the scheduled Steam-sale check and weekly IPO post
python main.py --testing
```

Music needs FFmpeg installed on the system.

## Deployment

Production runs on the owner's N100 home server, **not** Docker or Heroku:
- Repo at `~/apps/discord-bot-v2` with a `.venv`, run as systemd unit `discord-bot.service`, logs via `journalctl -u discord-bot.service`.
- `deploy/install.sh` (run once with sudo) installs `discord-bot-update.timer`. Every day at 04:00 UTC the timer runs `deploy/auto-update.sh` as the repo owner (not root). That script:
  - fetches from GitHub and fast-forwards only;
  - reinstalls requirements when `requirements.txt` changed;
  - restarts the bot only when there are new commits.
- The only root access the update job has is a sudoers rule for `systemctl restart discord-bot.service`. Keep it that way; the script runs whatever is pushed to GitHub.
- Pushing to `main` deploys by the next morning. Make sure anything pushed actually runs, including `requirements.txt` changes.

## Architecture

- **`main.py`**: entry point. It does the following:
  - initializes the bot and registers all `!` prefix commands and the `/event` slash command;
  - handles `on_message` for auto-responses;
  - runs two scheduled tasks: `steam_sale` (every 24h, skips the run at startup) and `weekly_ipos` (15:00 UTC daily, posts only on Sundays);
  - in `on_ready`, calls `db.init_db()` and backfills `servers.server_name`.
- **`functions/`**: one feature module per file, imported by `main.py`:
  - `db.py`: SQLite access (`resources/bot.db`). Tables: `servers` (guild → default channel + name), `wishlist` (guild + app_id → game JSON), `steam_users` (username → steam_id for `!cs2`). `init_db()` uses `CREATE TABLE IF NOT EXISTS` and never wipes data.
  - `steam.py`: Steam game search (by app ID), wishlist add/remove/show, CS2 stats, and the sale check that posts to each server's default channel.
  - `playmusic.py`: YouTube audio via `yt_dlp` + FFmpeg with a per-server queue.
    - Searches run in `asyncio.to_thread`.
    - The next song is started from the voice client's `after` callback, which runs on discord.py's audio thread and goes back to the event loop through `asyncio.run_coroutine_threadsafe`.
    - `!skip` just calls `vc.stop()` and lets that callback advance the queue. Don't advance it a second time.
  - `ipo.py`: Finnhub IPO calendar (`!ipos`, `!ipo`, weekly post).
  - `responses.py`: fuzzy-match auto-responses (`difflib.get_close_matches`) against `resources/knowledge.json`. `main.py` uses `knowledge2.json` instead when it exists; it's gitignored.
  - `fortnite.py`, `get_gif.py`, `qr_generator.py`, `currency_conversion.py`, `events.py`, `sport_details.py`: self-contained feature modules.
- **`migrations/`**: hand-run schema migrations. Bump `SCHEMA_VERSION` in `db.py` and add a numbered file for each schema change.
- **`scripts/migrate_json_to_sqlite.py`**: one-off import from the old JSON files. Re-running it brings back old wishlist data (`INSERT OR REPLACE`).
- **`resources/`**: `bot.db` (gitignored, lives only on the server) and `knowledge.json`. `wishlist.json`, `default_channel.json` and `steam-info.json` are legacy files from before SQLite, kept only for the migration script.
- **`deploy/`**: the auto-update script and its installer (see Deployment).
- **`archive/`**, **`bin/`**: old code and install scripts, not used.

## Key Patterns

- Config via `python-decouple`: secrets loaded from `.env` with `config('KEY_NAME')`.
- Bot uses `commands.Bot` with the `!` prefix and `help_command=None` (custom `!help` embed; update it when adding commands). Slash commands use `bot.tree.command`.
- Guild, channel and app IDs are stored as **strings** in the DB. Always `str()` them in queries.
- `on_message` calls `bot.process_commands(ctx)` at the end so auto-responses and `!` commands both work.
- Most feature modules still use blocking `requests` calls inside async commands, which freezes the bot while they wait. New network code should use `asyncio.to_thread` (or aiohttp).
- yt-dlp has to stay fairly recent, because YouTube breaks old versions. Its 2026 releases need Python 3.11 or newer.

## Commit Message Convention

Format: `[type] description` where type is `fix`, `update`, `add`, `remove`, `create`, etc.
