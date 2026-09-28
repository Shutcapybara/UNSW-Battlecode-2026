#!/bin/bash
# Roll dispatch back to the legacy worker. Run on the Mac.
set -euo pipefail
REPO="${JKS_REPO:-/Users/alik/Documents/Projects/UNSW-Battlecode-2026}"
HUB="${JKS_HUB_ROOT:-/Users/alik/Documents/Projects/battlecode-hub}"
PY="${JKS_PY:-$REPO/.venv/bin/python}"
LEGACY="${JKS_LEGACY_LIVE:-/Users/alik/Documents/Codex/2026-09-27/your-prompt-is-in-the-markdown-2/outputs/live_validation}"
UID_="$(id -u)"
export JKS_HUB_ROOT="$HUB"
OPEN=$("$PY" -m tools.hub.hubctl --root "$HUB" executor status | "$PY" -c "import json,sys;s=json.load(sys.stdin);print(len(s.get('open_intents') or [])+len(s.get('open_transactions') or []))")
if [ "$OPEN" != "0" ]; then echo "the hub executor has $OPEN open intents/transactions; let it reconcile (or resolve by hand in hub.sqlite) before rolling back"; exit 1; fi
"$PY" -m tools.hub.hubctl --root "$HUB" executor set-mode off
"$PY" -m tools.hub.hubctl --root "$HUB" executor release-legacy
touch "$HUB/control/stop"; sleep 3
launchctl bootout "gui/$UID_/au.battlecode.jks-hub" 2>/dev/null || true
launchctl bootstrap "gui/$UID_" ~/Library/LaunchAgents/au.battlecode.jks-hub.plist
rm -f "$LEGACY/state/runner.stop"
PLIST=~/Library/LaunchAgents/au.battlecode.jks-live-validation.plist
[ -f "$PLIST" ] || cp "$HUB/backups/au.battlecode.jks-live-validation.plist" "$PLIST"
launchctl bootstrap "gui/$UID_" "$PLIST" 2>/dev/null || launchctl kickstart "gui/$UID_/au.battlecode.jks-live-validation"
echo "legacy worker restored; hub daemon back in observer mode"
