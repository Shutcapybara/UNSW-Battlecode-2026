#!/usr/bin/env bash
# TT: z1 scorecard (seed 1) of each BOT against PARENT, then the concentration trajectory of each (and the parent).
# Usage: tools/tt/port_chain.sh PARENT BOT [BOT ...]
cd /home/alik/Documents/Projects/2026/wt-tt
export RUN_PANEL_TIMEOUT=7200
PARENT=$1; shift
for B in "$@"; do
  echo "START $B (parent $PARENT) $(date -Is)"
  .venv/bin/python -m tools.analysis.features.scorecard bots/$B --parent bots/$PARENT \
      --panel z1 --seed 1 --jobs 12 > build/tt/scorecard_$B.log 2>&1
  echo "DONE $B exit=$? $(date -Is)"
  grep -a -E "GATE" build/tt/scorecard_$B.log | tail -1
  .venv/bin/python tools/tt/concentration_bot.py $B build/zoo/z1-$B-* > build/tt/conc_$B.log 2>&1
done
[ -s build/tt/conc_$PARENT.log ] || .venv/bin/python tools/tt/concentration_bot.py $PARENT build/zoo/z1-$PARENT-* > build/tt/conc_$PARENT.log 2>&1
echo "PORT CHAIN FINISHED $(date -Is)"
