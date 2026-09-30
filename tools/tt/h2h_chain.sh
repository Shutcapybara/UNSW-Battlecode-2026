#!/usr/bin/env bash
# TT: does earlier conversion win against an opponent that cannot be eliminated? Head-to-heads on the ten live maps
# (40 fixed fixtures each), after the feed scorecard chain ($1 = its pid).
cd /home/alik/Documents/Projects/2026/wt-tt
while [ -n "$1" ] && kill -0 "$1" 2>/dev/null; do sleep 30; done
export HB_TAG=tt
for spec in "tt-01-feed300 hb1-12-direction-prior tt01-vs-hb112" "hb1-12-direction-prior hb1-04-deployable hb112-vs-hb104" "tt-01-feed300 hb1-04-deployable tt01-vs-hb104"; do
  set -- $spec
  echo "START $3 $(date -Is)"
  .venv/bin/python tools/hb1/h2h.py --arm bots/$1 --opp bots/$2 --seeds 2 --jobs 10 --out $3 > build/tt/h2h_$3.log 2>&1
  echo "DONE $3 exit=$? $(tail -1 build/tt/h2h_$3.log)"
done
echo "H2H CHAIN FINISHED $(date -Is)"
