#!/usr/bin/env bash
# TT: HB-1 Q1-Q3 for cheji bt (70) and Stockfish (206), after Q0 extraction ($1 = extraction pid to wait for).
cd /home/alik/Documents/Projects/2026/wt-tt
while [ -n "$1" ] && kill -0 "$1" 2>/dev/null; do sleep 30; done
for spec in "70 0.25" "206 0.5"; do
  set -- $spec
  export HB_TEAM=$1 HB_BUILD=tt/team$1 HB_TAG=tt$1 HB_CAP_FACTOR=$2 OMP_NUM_THREADS=8
  L=build/tt/team$1
  echo "START team $1 $(date -Is)"
  .venv/bin/python tools/hb1/q1_decisions.py --jobs 14 > $L/q1.log 2>&1;       echo "  q1 exit=$? $(date -Is)"
  .venv/bin/python tools/hb1/q1_calibration.py > $L/q1cal.log 2>&1;           echo "  q1cal exit=$? $(date -Is)"
  .venv/bin/python tools/hb1/q2_enumerate.py --jobs 14 > $L/q2enum.log 2>&1;  echo "  q2enum exit=$? $(date -Is)"
  .venv/bin/python tools/hb1/q2_command.py --jobs 14 > $L/q2cmd.log 2>&1;     echo "  q2cmd exit=$? $(date -Is)"
  .venv/bin/python tools/hb1/q3_windows.py > $L/q3.log 2>&1;                  echo "  q3 exit=$? $(date -Is)"
  echo "DONE team $1 $(date -Is)"
done
echo "TT Q1-Q3 FINISHED $(date -Is)"
