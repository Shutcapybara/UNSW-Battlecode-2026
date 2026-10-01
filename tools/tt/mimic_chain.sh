#!/usr/bin/env bash
# TT: z1 scorecards (seed 1, parent Ares V06) and trajectories for the top-team mimics and priors, in the order given.
cd /home/alik/Documents/Projects/2026/wt-tt
export RUN_PANEL_TIMEOUT=7200
for B in "$@"; do
  echo "START $B $(date -Is)"
  .venv/bin/python -m tools.analysis.features.scorecard bots/$B --parent bots/ares-v06-expanded-search-support \
      --panel z1 --seed 1 --jobs 12 > build/tt/scorecard_$B.log 2>&1
  echo "DONE $B exit=$? $(date -Is)"
  grep -a -E "GATE" build/tt/scorecard_$B.log | tail -1
  grep -a -E "^\| Wins" build/tt/scorecard_$B.log | tail -1
  .venv/bin/python tools/tt/concentration_bot.py $B build/zoo/z1-$B-* > build/tt/conc_$B.log 2>&1
done
echo "MIMIC CHAIN FINISHED $(date -Is)"
