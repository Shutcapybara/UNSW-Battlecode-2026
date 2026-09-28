#!/bin/bash
# Install or update the JKS hub observer daemon on the Mac (idempotent; Part B §11.6 day-one form).
#   bash tools/hub/bootstrap_mac.sh            # from the repository root
# The only command an operator needs to run (executor.mode = "auto"): after it, the daemon shadows the legacy worker,
# cuts over by itself once the shadow period is clean, and redeploys itself on request (tools/hub/request_redeploy.py).
# What it does: runs the hub tests, initialises the hub root, deploys a frozen copy of tools/hub, installs and
# (re)starts the LaunchAgent au.battlecode.jks-hub (observer mode: no API mutations), runs one cycle with a
# review packet, and kickstarts the legacy live-validation worker if it has exited without a stop request.
set -euo pipefail
REPO="${JKS_REPO:-/Users/alik/Documents/Projects/UNSW-Battlecode-2026}"
HUB="${JKS_HUB_ROOT:-/Users/alik/Documents/Projects/battlecode-hub}"
PY="${JKS_PY:-$REPO/.venv/bin/python}"
LEGACY="${JKS_LEGACY_LIVE:-/Users/alik/Documents/Codex/2026-09-27/your-prompt-is-in-the-markdown-2/outputs/live_validation}"
export JKS_HUB_ROOT="$HUB"
export JKS_AGENT="${JKS_AGENT:-human/operator/bootstrap}"
UID_="$(id -u)"

echo "== hub bootstrap: repo=$REPO hub=$HUB python=$PY"
[ -x "$PY" ] || { echo "python not found at $PY"; exit 1; }
mkdir -p "$HUB"/{app,candidates,tick,review,notify,control,logs,backups,findings}
mkdir -p ~/.config/jkshub && echo "$HUB" > ~/.config/jkshub/root

echo "== tests (gate: the hub's own modules; other lineages' test files run afterwards without gating)"
cd "$REPO"
JKS_HUB_FIXTURE="$REPO/build/hub-fixture" "$PY" -m unittest tests.test_hub_core tests.test_hub_git tests.test_hub_legacy_ops tests.test_hub_executor tests.test_hub_daemon
JKS_HUB_FIXTURE="$REPO/build/hub-fixture" "$PY" -m unittest discover -s tests -p 'test_hub_*.py' 2>&1 | tail -3 || true

echo "== init"
"$PY" -m tools.hub.hubctl --root "$HUB" init >/dev/null
if ! grep -q 'legacy_live' "$HUB/hub.toml"; then echo "hub.toml missing legacy_live"; exit 1; fi

echo "== backup of the legacy record (excluding replays)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
if [ -d "$LEGACY" ]; then
  tar -czf "$HUB/backups/live-$STAMP.tgz" -C "$(dirname "$LEGACY")" --exclude='state/replays' --exclude='state/decoded' --exclude='state/runtime/*/*.replay' "$(basename "$LEGACY")" 2>/dev/null || echo "backup skipped"
  shasum -a 256 "$HUB/backups/live-$STAMP.tgz" > "$HUB/backups/live-$STAMP.sha256" 2>/dev/null || true
fi

echo "== deploy"
SHA="$(git -C "$REPO" rev-parse --short HEAD 2>/dev/null || echo nogit)-$STAMP"
"$PY" -m tools.hub.hubctl --root "$HUB" deploy --sha "$SHA"

echo "== launch agent"
PLIST=~/Library/LaunchAgents/au.battlecode.jks-hub.plist
mkdir -p ~/Library/LaunchAgents
sed -e "s#__PY__#$PY#g" -e "s#__HUB__#$HUB#g" "$HUB/app/current/hub/au.battlecode.jks-hub.plist" > "$PLIST"
launchctl bootout "gui/$UID_/au.battlecode.jks-hub" 2>/dev/null || true
sleep 1
launchctl bootstrap "gui/$UID_" "$PLIST"
launchctl kickstart "gui/$UID_/au.battlecode.jks-hub" || true

echo "== first cycle"
"$PY" -m tools.hub.hubctl --root "$HUB" cycle --packet | head -30

echo "== legacy worker"
STATUS="$LEGACY/state/runner_status.json"
if [ -f "$STATUS" ]; then
  AGE=$(( $(date +%s) - $(stat -f %m "$STATUS") ))
  JOBS=$("$PY" -c "import json,sys;print(len(json.load(open(sys.argv[1])).get('jobs') or {}))" "$STATUS" 2>/dev/null || echo 1)
  REV=$("$PY" -c "import json,sys;print(json.load(open(sys.argv[1])).get('runner_revision',''))" "$STATUS" 2>/dev/null || echo "")
  if [ "$AGE" -gt 120 ] && [ ! -f "$LEGACY/state/runner.stop" ]; then
    echo "legacy runner_status is ${AGE}s old and no stop request: kickstarting au.battlecode.jks-live-validation"
    launchctl kickstart "gui/$UID_/au.battlecode.jks-live-validation" || echo "kickstart failed (is the legacy LaunchAgent loaded?)"
  elif [ "$REV" != "D-009" ] && [ "$JOBS" = "0" ]; then
    echo "legacy worker runs an older runner revision ('$REV') and is idle: restarting it to load system/runner.py"
    launchctl kickstart -k "gui/$UID_/au.battlecode.jks-live-validation" || echo "kickstart -k failed"
  elif [ "$REV" != "D-009" ]; then
    echo "legacy worker runs an older runner revision but has $JOBS job(s) running; requesting a restart between jobs"
    touch "$LEGACY/state/runner.restart"
  else
    echo "legacy worker status age ${AGE}s, revision $REV, jobs $JOBS (stop file present: $([ -f "$LEGACY/state/runner.stop" ] && echo yes || echo no))"
  fi
fi

echo "== done; status:"
"$PY" -m tools.hub.hubctl --root "$HUB" status || true
echo "review packet: $HUB/review/packet-latest.md (mirrored to $REPO/hub-state/review/packet-latest.md)"
