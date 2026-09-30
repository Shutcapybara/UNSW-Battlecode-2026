#!/bin/sh
# rb run queue: process build/rb/queue.txt lines "BOT PANEL SEEDS" in order, one at a time; append to add work.
# Done lines are recorded in build/rb/queue.done. Run from the repo root: nohup tools/rb/queue.sh &
PY=${PY:-$HOME/Documents/Projects/2026/UNSW-Battlecode-2026/.venv/bin/python}
Q=build/rb/queue.txt; D=build/rb/queue.done
touch $Q $D
while true; do
  line=$(grep -vxFf $D $Q | head -1)
  if [ -z "$line" ]; then sleep 30; continue; fi
  set -- $line
  echo "$(date +%T) start $line"
  $PY tools/rb/gate.py run $1 --panel $2 --seeds $3 --jobs ${JOBS:-14} > build/rb/log-$1-$2-$3.txt 2>&1
  echo "$line" >> $D
  echo "$(date +%T) done $line"
done
