#!/usr/bin/env bash
# Run lane.py jobs one after another: tools/rc/queue.sh "BOT PANEL SEEDS" ...  (logs in build/rc/logs/)
cd "$(dirname "$0")/../.."
PY=${PY:-$HOME/Documents/Projects/2026/UNSW-Battlecode-2026/.venv/bin/python}
JOBS=${JOBS:-$(( $(nproc) - 2 ))}
for spec in "$@"; do
    set -- $spec
    echo "$(date +%T) start $spec"
    $PY tools/rc/lane.py run "$1" --panel "$2" --seeds "$3" --jobs "$JOBS" --extract > "build/rc/logs/$1-$2-$3.log" 2>&1
    echo "$(date +%T) done $spec rc=$?"
done
