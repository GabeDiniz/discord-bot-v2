from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(_REPO_ROOT, "resources", "bot.db")
SCHEMA_VERSION = 1  # bump and add a migration file under migrations/ for each schema change


def init_db():
  with sqlite3.connect(DB_PATH) as conn:
    conn.executescript(
      """
      CREATE TABLE IF NOT EXISTS servers (
        guild_id TEXT PRIMARY KEY,
        default_channel_id TEXT NOT NULL,
        server_name TEXT
      );
      CREATE TABLE IF NOT EXISTS wishlist (
        guild_id TEXT NOT NULL,
        app_id TEXT NOT NULL,
        data TEXT NOT NULL,
        PRIMARY KEY (guild_id, app_id)
      );
      CREATE TABLE IF NOT EXISTS steam_users (
        username TEXT PRIMARY KEY,
        steam_id TEXT NOT NULL
      );
      """
    )
    # Stamp the schema version for fresh DBs so future migrations skip correctly.
    # Existing DBs get their version bumped by their own migration files.
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    if version == 0:
      conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")


@contextmanager
def db():
  conn = sqlite3.connect(DB_PATH)
  conn.row_factory = sqlite3.Row
  try:
    yield conn
    conn.commit()
  finally:
    conn.close()


# ========================================
# servers helpers
# ========================================
def upsert_server(guild_id: str, channel_id: str, server_name: str) -> None:
  """Insert or update a server's default channel and name."""
  with db() as conn:
    conn.execute(
      "INSERT INTO servers (guild_id, default_channel_id, server_name) VALUES (?, ?, ?) "
      "ON CONFLICT(guild_id) DO UPDATE SET "
      "  default_channel_id = excluded.default_channel_id, "
      "  server_name = excluded.server_name",
      (str(guild_id), str(channel_id), server_name),
    )


def update_server_name(guild_id: str, server_name: str) -> None:
  """Update only the display name for a server. No-op if the row doesn't exist."""
  with db() as conn:
    conn.execute(
      "UPDATE servers SET server_name = ? WHERE guild_id = ?",
      (server_name, str(guild_id)),
    )


def get_server(guild_id: str) -> dict | None:
  """Return the full row for a server as a dict, or None."""
  with db() as conn:
    row = conn.execute(
      "SELECT guild_id, default_channel_id, server_name FROM servers WHERE guild_id = ?",
      (str(guild_id),),
    ).fetchone()
    return dict(row) if row else None


def get_default_channel(guild_id: str) -> str | None:
  with db() as conn:
    row = conn.execute(
      "SELECT default_channel_id FROM servers WHERE guild_id = ?",
      (str(guild_id),),
    ).fetchone()
    return row["default_channel_id"] if row else None


def get_all_default_channels() -> dict[str, str]:
  with db() as conn:
    rows = conn.execute("SELECT guild_id, default_channel_id FROM servers").fetchall()
    return {row["guild_id"]: row["default_channel_id"] for row in rows}


# ========================================
# wishlist helpers
# ========================================
def add_wishlist_game(guild_id: str, app_id: str, game: dict) -> bool:
  """Returns True if inserted, False if already present."""
  with db() as conn:
    cur = conn.execute(
      "INSERT OR IGNORE INTO wishlist (guild_id, app_id, data) VALUES (?, ?, ?)",
      (str(guild_id), str(app_id), json.dumps(game)),
    )
    return cur.rowcount > 0


def remove_wishlist_game_by_name(guild_id: str, game_name: str) -> str | None:
  """Removes the first game matching the case-insensitive name. Returns the removed game's name, or None."""
  needle = game_name.lower().strip()
  with db() as conn:
    rows = conn.execute(
      "SELECT app_id, data FROM wishlist WHERE guild_id = ?",
      (str(guild_id),),
    ).fetchall()
    for row in rows:
      game = json.loads(row["data"])
      if game["name"].lower().strip() == needle:
        conn.execute(
          "DELETE FROM wishlist WHERE guild_id = ? AND app_id = ?",
          (str(guild_id), row["app_id"]),
        )
        return game["name"]
  return None


def get_wishlist(guild_id: str) -> list[dict]:
  with db() as conn:
    rows = conn.execute(
      "SELECT data FROM wishlist WHERE guild_id = ?",
      (str(guild_id),),
    ).fetchall()
    return [json.loads(row["data"]) for row in rows]


def get_all_wishlists() -> dict[str, list[dict]]:
  with db() as conn:
    rows = conn.execute("SELECT guild_id, data FROM wishlist").fetchall()
  result: dict[str, list[dict]] = {}
  for row in rows:
    result.setdefault(row["guild_id"], []).append(json.loads(row["data"]))
  return result


# ========================================
# steam_users helpers
# ========================================
def get_steam_id(username: str) -> str | None:
  with db() as conn:
    row = conn.execute(
      "SELECT steam_id FROM steam_users WHERE username = ?",
      (username.lower(),),
    ).fetchone()
    return row["steam_id"] if row else None
