#!/usr/bin/env bash
# z1 scorecards (seed 1, parent Ares V06) for the uploadable direction-prior bots, comparable with hb1-12's.
cd /home/alik/Documents/Projects/2026/wt-tt
export RUN_PANEL_TIMEOUT=7200
for B in "$@"; do
  echo "START $B $(date -Is)"
  .venv/bin/python -m tools.analysis.features.scorecard bots/$B --parent bots/ares-v06-expanded-search-support \
      --panel z1 --seed 1 --jobs 12 > build/tt/scorecard_$B.log 2>&1
  echo "DONE $B exit=$? $(date -Is)"
  grep -a -E "GATE" build/tt/scorecard_$B.log | tail -1
done
echo "UPLOAD CHAIN FINISHED $(date -Is)"
