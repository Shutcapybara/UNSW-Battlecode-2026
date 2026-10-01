#!/usr/bin/env bash
# HB-1 Q5 chain 2: hb1-13 (phased prior) at seed 1, then paired seed 2 for hb1-12, hb1-13 and hb1-10 (D-032).
# Waits for chain 1 (tools/hb1/q4q5_chain.sh, pid in $1) to finish so panels never run concurrently.
cd /home/alik/Documents/Projects/2026/wt-hb1
export RUN_PANEL_TIMEOUT=7200
while [ -n "$1" ] && kill -0 "$1" 2>/dev/null; do sleep 60; done
for spec in "hb1-13-phased-prior 1" "hb1-12-direction-prior 2" "hb1-13-phased-prior 2" "hb1-10-escape-split 2"; do
  set -- $spec
  echo "START $1 seed $2 $(date -Is)"
  .venv/bin/python -m tools.analysis.features.scorecard bots/$1 --parent bots/ares-v06-expanded-search-support \
      --panel z1 --seed $2 --jobs 10 > build/hb1/games/scorecard_$1_s$2.log 2>&1
  echo "DONE $1 seed $2 exit=$? $(date -Is)"
  grep -a -E "GATE" build/hb1/games/scorecard_$1_s$2.log | tail -1
done
echo "CHAIN2 FINISHED $(date -Is)"
