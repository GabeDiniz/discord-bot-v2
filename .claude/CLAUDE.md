# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A multi-purpose Discord bot (Python, discord.py) with features for Steam game lookups, wishlists with daily sale checking, music playback, Fortnite shop, CS2 stats, QR code generation, currency conversion, AI chat (HuggingFace), and keyword-based auto-responses.

## Running the Bot

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally (requires .env with BOT_KEY, STEAM_API_KEY, GIPHY_API_KEY, HUGGING_FACE_API_KEY)
python main.py

# Run in testing mode (skips Steam sale checks in the 24h loop)
python main.py --testing

# Docker
docker build -t discord-bot . && docker run discord-bot
```

## Architecture

- **`main.py`** — Entry point. Initializes the bot, registers all `!` prefix commands and `/` slash commands, handles the `on_message` event for auto-responses, and runs a 24-hour background loop (`steam_sale`) to check wishlist games for discounts.
- **`functions/`** — Each file is a feature module imported by `main.py`:
  - `steam.py` — Steam game search (by app ID), per-server wishlist management, CS2 stats, and sale checking logic.
  - `playmusic.py` — YouTube audio playback via `yt_dlp` + FFmpeg with per-server queue management.
  - `responses.py` — Fuzzy-match auto-responses using `difflib.get_close_matches` against a JSON knowledge base.
  - `fortnite.py`, `get_gif.py`, `qr_generator.py`, `currency_conversion.py`, `events.py`, `sport_details.py` — Self-contained feature modules.
- **`resources/`** — Runtime JSON data: `knowledge.json`/`knowledge2.json` (auto-response knowledge base), `wishlist.json` (per-server wishlists), `default_channel.json` (where sale announcements are posted), `steam-info.json` (CS2 user mappings).
- **`archive/`** — Deprecated/old code, not used by the bot.

## Key Patterns

- Config via `python-decouple`: secrets loaded from `.env` using `config('KEY_NAME')`.
- Bot uses `commands.Bot` with `!` prefix. Slash commands use `bot.tree.command`.
- Wishlists are per-guild, keyed by `guild_id` as strings, persisted to `resources/wishlist.json`.
- The `on_message` handler calls `bot.process_commands(ctx)` at the end to allow both auto-responses and `!` commands to coexist.
- Music playback requires FFmpeg installed on the system.

## Commit Message Convention

Format: `[type] description` where type is `fix`, `update`, `add`, etc.
