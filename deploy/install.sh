#!/usr/bin/env bash
# One-time setup on the N100 for daily auto-updates:
#   cd ~/apps/discord-bot-v2 && sudo deploy/install.sh
#
# Creates:
#   /etc/systemd/system/discord-bot-update.service  runs deploy/auto-update.sh as the repo owner (not root)
#   /etc/systemd/system/discord-bot-update.timer    fires daily at 04:00 (+ up to 10 min random delay)
#   /etc/sudoers.d/discord-bot-update               lets that user run exactly one root command:
#                                                   `systemctl restart discord-bot.service`
#
# Re-run any time; it overwrites the files above.
#
# Useful commands:
#   systemctl list-timers discord-bot-update.timer     # next/last run
#   sudo systemctl start discord-bot-update.service    # update right now
#   journalctl -u discord-bot-update.service           # update history
#
# Uninstall:
#   sudo systemctl disable --now discord-bot-update.timer
#   sudo rm /etc/systemd/system/discord-bot-update.{service,timer} /etc/sudoers.d/discord-bot-update
#   sudo systemctl daemon-reload
set -euo pipefail

BOT_SERVICE="discord-bot.service"
UPDATE_TIME="*-*-* 04:00:00"   # systemd OnCalendar format

if [[ $EUID -ne 0 ]]; then
  echo "Run with sudo: sudo $0" >&2
  exit 1
fi

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OWNER="$(stat -c %U "$REPO_DIR")"
SYSTEMCTL="$(command -v systemctl)"

if ! systemctl cat "$BOT_SERVICE" >/dev/null 2>&1; then
  echo "Can't find $BOT_SERVICE - is the bot service installed?" >&2
  exit 1
fi
if ! sudo -u "$OWNER" git -C "$REPO_DIR" rev-parse '@{u}' >/dev/null 2>&1; then
  echo "The checked-out branch in $REPO_DIR has no upstream (git push -u / git branch --set-upstream-to)." >&2
  exit 1
fi

chmod +x "$REPO_DIR/deploy/auto-update.sh"

cat > /etc/systemd/system/discord-bot-update.service <<EOF
[Unit]
Description=Pull discord-bot-v2 from git and restart it if there are new commits
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
User=$OWNER
ExecStart=$REPO_DIR/deploy/auto-update.sh
EOF

cat > /etc/systemd/system/discord-bot-update.timer <<EOF
[Unit]
Description=Daily auto-update for discord-bot-v2

[Timer]
OnCalendar=$UPDATE_TIME
RandomizedDelaySec=10min
# If the N100 was off at 04:00, run once it's back up
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Sudoers rule: validate before installing so a typo can't break sudo
SUDOERS_TMP="$(mktemp)"
trap 'rm -f "$SUDOERS_TMP"' EXIT
echo "$OWNER ALL=(root) NOPASSWD: $SYSTEMCTL restart $BOT_SERVICE" > "$SUDOERS_TMP"
visudo -cf "$SUDOERS_TMP" >/dev/null
install -m 0440 -o root -g root "$SUDOERS_TMP" /etc/sudoers.d/discord-bot-update

systemctl daemon-reload
systemctl enable --now discord-bot-update.timer

echo "Installed. Updates run as '$OWNER' from $REPO_DIR."
systemctl list-timers --no-pager discord-bot-update.timer
