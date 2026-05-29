"""
One-shot migration: read the legacy JSON files in resources/ and load them into
resources/bot.db. Safe to re-run — each table is repopulated via INSERT OR REPLACE.

Usage (from repo root):
    python scripts/migrate_json_to_sqlite.py
"""
import json
import os
import sys

# Allow running this script from the repo root without installing the package.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from functions import db


RESOURCES = "resources"
DEFAULT_CHANNEL_JSON = os.path.join(RESOURCES, "default_channel.json")
WISHLIST_JSON = os.path.join(RESOURCES, "wishlist.json")
STEAM_INFO_JSON = os.path.join(RESOURCES, "steam-info.json")


def _load_json(path):
  if not os.path.exists(path):
    print(f"[ SKIP ] {path} not found.")
    return None
  with open(path, "r") as f:
    return json.load(f)


def migrate_default_channels():
  data = _load_json(DEFAULT_CHANNEL_JSON)
  if data is None:
    return
  with db.db() as conn:
    for guild_id, channel_id in data.items():
      conn.execute(
        "INSERT INTO servers (guild_id, default_channel_id) VALUES (?, ?) "
        "ON CONFLICT(guild_id) DO UPDATE SET default_channel_id = excluded.default_channel_id",
        (str(guild_id), str(channel_id)),
      )
  print(f"[ OK ] Migrated {len(data)} servers rows (server_name will be backfilled at bot startup).")


def migrate_wishlists():
  data = _load_json(WISHLIST_JSON)
  if data is None:
    return
  count = 0
  with db.db() as conn:
    for guild_id, games in data.items():
      for game in games:
        app_id = str(game["steam_appid"])
        conn.execute(
          "INSERT INTO wishlist (guild_id, app_id, data) VALUES (?, ?, ?) "
          "ON CONFLICT(guild_id, app_id) DO UPDATE SET data = excluded.data",
          (str(guild_id), app_id, json.dumps(game)),
        )
        count += 1
  print(f"[ OK ] Migrated {count} wishlist rows across {len(data)} guilds.")


def migrate_steam_users():
  data = _load_json(STEAM_INFO_JSON)
  if data is None:
    return
  with db.db() as conn:
    for username, steam_id in data.items():
      conn.execute(
        "INSERT INTO steam_users (username, steam_id) VALUES (?, ?) "
        "ON CONFLICT(username) DO UPDATE SET steam_id = excluded.steam_id",
        (username.lower(), str(steam_id)),
      )
  print(f"[ OK ] Migrated {len(data)} steam_users rows.")


def main():
  print("[ LOG ] Initializing database...")
  db.init_db()
  migrate_default_channels()
  migrate_wishlists()
  migrate_steam_users()
  print(f"[ DONE ] DB at {db.DB_PATH}")


if __name__ == "__main__":
  main()
