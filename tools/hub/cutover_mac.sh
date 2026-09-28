#!/bin/bash
# Manual cutover from the legacy live-validation worker to the hub executor (protocol v2). Run on the Mac.
# Not needed in executor.mode = "auto" (the default): the daemon performs this sequence itself after the shadow period.
#   bash tools/hub/cutover_mac.sh            # refuses unless the hub has >= 3 consecutive clean shadow cycles
#   FORCE=1 bash tools/hub/cutover_mac.sh    # skip the shadow check (director decision required)
set -euo pipefail
REPO="${JKS_REPO:-/Users/alik/Documents/Projects/UNSW-Battlecode-2026}"
HUB="${JKS_HUB_ROOT:-/Users/alik/Documents/Projects/battlecode-hub}"
PY="${JKS_PY:-$REPO/.venv/bin/python}"
LEGACY="${JKS_LEGACY_LIVE:-/Users/alik/Documents/Codex/2026-09-27/your-prompt-is-in-the-markdown-2/outputs/live_validation}"
UID_="$(id -u)"
export JKS_HUB_ROOT="$HUB" JKS_AGENT="${JKS_AGENT:-human/operator/cutover}"
cd "$REPO"

echo "== shadow check"
CLEAN=$("$PY" -m tools.hub.hubctl --root "$HUB" executor status | "$PY" -c "import json,sys;print(json.load(sys.stdin).get('shadow_clean') or 0)")
echo "consecutive clean shadow cycles: $CLEAN"
if [ "${FORCE:-0}" != "1" ] && [ "$CLEAN" -lt 3 ]; then echo "need >= 3 clean shadow cycles (set executor.mode = \"shadow\" in $HUB/hub.toml, re-run bootstrap, wait 30 min) or FORCE=1"; exit 1; fi

echo "== stop the legacy worker gracefully"
touch "$LEGACY/state/runner.stop"
for i in $(seq 1 60); do
  JOBS=$("$PY" -c "import json;print(len(json.load(open('$LEGACY/state/runner_status.json')).get('jobs') or {}))" 2>/dev/null || echo 0)
  OPEN=$("$PY" -c "import json;s=json.load(open('$LEGACY/state/state.json'));print(sum(1 for k in ('upload','switch','intent') if s.get(k)))" 2>/dev/null || echo 0)
  if [ "$JOBS" = "0" ] && [ "$OPEN" = "0" ]; then break; fi
  echo "waiting: jobs=$JOBS open_transactions=$OPEN"; sleep 10
done
if [ "${OPEN:-0}" != "0" ]; then echo "an upload/switch/intent is still open in the legacy state; resolve it first (never cut over with an open transaction)"; rm -f "$LEGACY/state/runner.stop"; exit 1; fi
launchctl bootout "gui/$UID_/au.battlecode.jks-live-validation" 2>/dev/null || true
mkdir -p "$HUB/backups" && cp ~/Library/LaunchAgents/au.battlecode.jks-live-validation.plist "$HUB/backups/" 2>/dev/null || true
echo "legacy worker stopped and unloaded (plist kept in $HUB/backups for rollback)"

echo "== adopt the legacy record into the executor's ledger"
"$PY" -m tools.hub.hubctl --root "$HUB" executor adopt-legacy

echo "== switch the daemon to live"
"$PY" -m tools.hub.hubctl --root "$HUB" executor set-mode live
grep -n 'mode = ' "$HUB/hub.toml"
bash tools/hub/bootstrap_mac.sh
echo "== first live cycle"
sleep 5
"$PY" -m tools.hub.hubctl --root "$HUB" executor status
echo "cutover complete; rollback: bash tools/hub/rollback_mac.sh"
