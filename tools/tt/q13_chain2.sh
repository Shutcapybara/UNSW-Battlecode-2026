#!/usr/bin/env bash
# TT: Q1-Q3 for forgot to mention (264, all games) and Cache me outside (952, ranked games only - see dummy_policy).
cd /home/alik/Documents/Projects/2026/wt-tt
for spec in "264 tt/team264 tt264 0.3" "952 tt/team952r tt952 1"; do
  set -- $spec
  export HB_TEAM=$1 HB_BUILD=$2 HB_TAG=$3 HB_CAP_FACTOR=$4 OMP_NUM_THREADS=8
  L=build/$2
  echo "START team $1 ($2) $(date -Is)"
  .venv/bin/python tools/hb1/q1_decisions.py --jobs 12 > $L/q1.log 2>&1;       echo "  q1 exit=$? $(date -Is)"
  .venv/bin/python tools/hb1/q1_calibration.py > $L/q1cal.log 2>&1;           echo "  q1cal exit=$? $(date -Is)"
  .venv/bin/python tools/hb1/q2_enumerate.py --jobs 12 > $L/q2enum.log 2>&1;  echo "  q2enum exit=$? $(date -Is)"
  .venv/bin/python tools/hb1/q2_command.py --jobs 12 > $L/q2cmd.log 2>&1;     echo "  q2cmd exit=$? $(date -Is)"
  .venv/bin/python tools/hb1/q3_windows.py > $L/q3.log 2>&1;                  echo "  q3 exit=$? $(date -Is)"
  echo "DONE team $1 $(date -Is)"
done
echo "TT Q1-Q3 (chain 2) FINISHED $(date -Is)"
