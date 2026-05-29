"""
Migration 001: rename guild_config -> servers, add nullable server_name column.

Bumps PRAGMA user_version from 0 to 1. Idempotent — safe to re-run.

Usage (from repo root):
    python3 migrations/001_rename_guild_config_to_servers.py
"""
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from functions.db import DB_PATH

TARGET_VERSION = 1


def migrate():
  conn = sqlite3.connect(DB_PATH)
  try:
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    if version >= TARGET_VERSION:
      print(f"[ SKIP ] DB already at version {version} (>= {TARGET_VERSION}).")
      return

    tables = {row[0] for row in conn.execute(
      "SELECT name FROM sqlite_master WHERE type='table'"
    )}

    if "servers" in tables and "guild_config" not in tables:
      # Schema already matches v1 (e.g. fresh init_db ran before migrations). Just bump version.
      conn.execute(f"PRAGMA user_version = {TARGET_VERSION}")
      conn.commit()
      print(f"[ OK ] Schema already at v{TARGET_VERSION}, version bumped.")
      return

    if "guild_config" not in tables:
      # Fresh DB — nothing to migrate. Stamp the version so we don't re-attempt later.
      conn.execute(f"PRAGMA user_version = {TARGET_VERSION}")
      conn.commit()
      print(f"[ SKIP ] guild_config not present — stamped version {TARGET_VERSION} on fresh DB.")
      return

    conn.executescript(
      f"""
      ALTER TABLE guild_config RENAME TO servers;
      ALTER TABLE servers ADD COLUMN server_name TEXT;
      PRAGMA user_version = {TARGET_VERSION};
      """
    )
    conn.commit()
    print(f"[ OK ] Renamed guild_config -> servers, added server_name. DB now at v{TARGET_VERSION}.")
  finally:
    conn.close()


if __name__ == "__main__":
  migrate()
