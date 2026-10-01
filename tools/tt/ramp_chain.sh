#!/usr/bin/env bash
# TT ramp validation: z1 scorecards vs hb1-14 for the ramp bots, then head-to-heads on the live maps.
cd /home/alik/Documents/Projects/2026/wt-tt
tools/tt/port_chain.sh hb1-14-prior-r540 tt-06-ramp-300-400 tt-07-ramp-250-450
export HB_TAG=tt
for spec in "hb1-14-prior-r540 tt-05-feed300-up hb114-vs-tt05" "tt-06-ramp-300-400 hb1-14-prior-r540 tt06-vs-hb114" "tt-06-ramp-300-400 tt-05-feed300-up tt06-vs-tt05" "tt-07-ramp-250-450 hb1-14-prior-r540 tt07-vs-hb114" "tt-07-ramp-250-450 tt-05-feed300-up tt07-vs-tt05"; do
  set -- $spec
  echo "START h2h $3 $(date -Is)"
  .venv/bin/python tools/hb1/h2h.py --arm bots/$1 --opp bots/$2 --seeds 2 --jobs 12 --out $3 > build/tt/h2h_$3.log 2>&1
  echo "DONE h2h $3 exit=$? $(tail -1 build/tt/h2h_$3.log)"
done
echo "RAMP CHAIN FINISHED $(date -Is)"
