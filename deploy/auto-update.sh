#!/usr/bin/env bash
# Pulls the latest code and restarts the bot, but only if there are new commits.
# Runs daily via discord-bot-update.timer (set up by deploy/install.sh).
#
# Run by hand:
#   deploy/auto-update.sh            # update now
#   DRY_RUN=1 deploy/auto-update.sh  # show what would change, touch nothing
#
# Logs: journalctl -u discord-bot-update.service
#
# Everything is inside main() on purpose: bash then reads the whole script
# before running it, so `git pull` replacing this file mid-run is harmless.
set -euo pipefail

main() {
  local service="${BOT_SERVICE:-discord-bot.service}"
  local repo_dir
  repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  local venv_dir="${VENV_DIR:-$repo_dir/.venv}"
  cd "$repo_dir"

  git fetch --quiet

  local old new upstream
  old="$(git rev-parse HEAD)"
  new="$(git rev-parse '@{u}')"
  upstream="$(git rev-parse --abbrev-ref '@{u}')"

  # Nothing new upstream (also covers having local-only commits)
  if git merge-base --is-ancestor "$new" "$old"; then
    echo "Up to date with $upstream at $(git rev-parse --short HEAD). Nothing to do."
    return 0
  fi

  echo "New commits on $upstream:"
  git log --oneline "$old..$new"

  if [[ -n "${DRY_RUN:-}" ]]; then
    echo "DRY_RUN: would pull, reinstall requirements if changed, and restart $service."
    return 0
  fi

  trap 'echo "[ ERROR ] Update failed - $service was NOT restarted." >&2' ERR

  # Fast-forward only: refuses (and fails loudly) instead of merging if the
  # N100 copy has its own commits or edits that conflict.
  git merge --ff-only --quiet "$new"
  echo "Updated $(git rev-parse --short "$old") -> $(git rev-parse --short "$new")."

  if ! git diff --quiet "$old" "$new" -- requirements.txt; then
    echo "requirements.txt changed - installing dependencies..."
    "$venv_dir/bin/pip" install --quiet -r requirements.txt
  fi

  echo "Restarting $service..."
  sudo -n systemctl restart "$service"

  sleep 10
  if systemctl is-active --quiet "$service"; then
    echo "$service is running."
  else
    echo "[ ERROR ] $service is not running after restart. Check: journalctl -u $service -n 50" >&2
    return 1
  fi
}

main "$@"
