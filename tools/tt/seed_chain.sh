#!/usr/bin/env bash
# TT: z1 scorecards (parent Ares V06) for BOT:SEED pairs, in the order given.  tools/tt/seed_chain.sh hb1-19-x:1 hb1-17-y:2
cd /home/alik/Documents/Projects/2026/wt-tt
export RUN_PANEL_TIMEOUT=7200
for BS in "$@"; do
  B=${BS%%:*}; S=${BS##*:}
  echo "START $B s$S $(date -Is)"
  .venv/bin/python -m tools.analysis.features.scorecard bots/$B --parent bots/ares-v06-expanded-search-support \
      --panel z1 --seed $S --jobs 12 > build/tt/scorecard_${B}_s$S.log 2>&1
  echo "DONE $B s$S exit=$? $(date -Is)"
  grep -a -E "GATE" build/tt/scorecard_${B}_s$S.log | tail -1
  grep -a -E "^\| Wins" build/tt/scorecard_${B}_s$S.log | tail -1
done
echo "SEED CHAIN FINISHED $(date -Is)"
