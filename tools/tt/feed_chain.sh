#!/usr/bin/env bash
# TT: z1 scorecards (seed 1, parent hb1-12) for the feed-timing versions, then their concentration trajectories.
cd /home/alik/Documents/Projects/2026/wt-tt
export RUN_PANEL_TIMEOUT=7200
for B in tt-01-feed300 tt-02-feed250; do
  echo "START $B $(date -Is)"
  .venv/bin/python -m tools.analysis.features.scorecard bots/$B --parent bots/hb1-12-direction-prior \
      --panel z1 --seed 1 --jobs 12 > build/tt/scorecard_$B.log 2>&1
  echo "DONE $B exit=$? $(date -Is)"
  grep -a -E "GATE" build/tt/scorecard_$B.log | tail -1
  .venv/bin/python tools/tt/concentration_bot.py $B build/zoo/z1-$B-* > build/tt/conc_$B.log 2>&1
done
echo "FEED CHAIN FINISHED $(date -Is)"
