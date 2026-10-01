#!/usr/bin/env bash
# TT: wait for map extraction, then the v5 vs v5+map comparison per team.
cd /home/alik/Documents/Projects/2026/wt-tt
until grep -q "MAP EXTRACTION FINISHED" build/tt/run_map.log; do sleep 30; done
for spec in "../wt-hb1/build/hb1 hb62 hb1" "build/tt/team70 team70 tt70" "build/tt/team206 team206 tt206" "build/tt/team264 team264 tt264" "build/tt/team952r team952r tt952"; do
  set -- $spec
  OMP_NUM_THREADS=6 .venv/bin/python tools/tt/q1_mapmem.py $1 build/tt/map/$2 $3 2>&1 | grep -E "v5\+map|Traceback|Error"
done
echo "MAPMEM FINISHED $(date -Is)"
