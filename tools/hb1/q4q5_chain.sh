#!/usr/bin/env bash
# HB-1: z1 scorecards (seed 1, parent Ares V06) for the mimic and the three Q5 ports, one after another.
cd /home/alik/Documents/Projects/2026/wt-hb1
for B in hb1-04-deployable hb1-10-escape-split hb1-11-split-gate hb1-12-direction-prior; do
  echo "START $B $(date -Is)"
  .venv/bin/python -m tools.analysis.features.scorecard bots/$B --parent bots/ares-v06-expanded-search-support \
      --panel z1 --seed 1 --jobs 10 > build/hb1/games/scorecard_$B.log 2>&1
  echo "DONE $B exit=$? $(date -Is)"
  grep -a -E "GATE" build/hb1/games/scorecard_$B.log | tail -1
done
echo "CHAIN FINISHED $(date -Is)"
