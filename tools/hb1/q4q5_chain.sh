#!/usr/bin/env bash
# HB-1: z1 scorecards (seed 1, parent Ares V06) for the three Q5 ports, then the mimic (hb1-04), one at a time.
# RUN_PANEL_TIMEOUT: heavy Slithery Fight fixtures vs the Python Vibing++ mimic run past run_panel's 1800 s on the
# loaded shared desktop. hb1-04 waits for its refill job (tools/hb1/run_panel_long.py) so no fixture runs twice.
cd /home/alik/Documents/Projects/2026/wt-hb1
export RUN_PANEL_TIMEOUT=7200
for B in hb1-10-escape-split hb1-11-split-gate hb1-12-direction-prior hb1-04-deployable; do
  if [ "$B" = hb1-04-deployable ]; then
    while pgrep -f "run_panel_long.py --panel z1 --bot bots/hb1-04" >/dev/null; do sleep 60; done
  fi
  echo "START $B $(date -Is)"
  .venv/bin/python -m tools.analysis.features.scorecard bots/$B --parent bots/ares-v06-expanded-search-support \
      --panel z1 --seed 1 --jobs 10 > build/hb1/games/scorecard_$B.log 2>&1
  echo "DONE $B exit=$? $(date -Is)"
  grep -a -E "GATE" build/hb1/games/scorecard_$B.log | tail -1
done
echo "CHAIN FINISHED $(date -Is)"
