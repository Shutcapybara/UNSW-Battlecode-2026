#!/bin/bash
# orun.sh VAR GAMESFILE OUTPREFIX SECONDS : repeated capped oracle processes (memory) until the time is up
cd $HOME/mnt/UNSW-Battlecode-2026
end=$(( $(date +%s) + $4 ))
while [ $(date +%s) -lt $end ]; do
  left=$(( end - $(date +%s) ))
  out=$(CAP=20 PYTHONPATH=$HOME/pyk nice -n 10 python3 tools/learn/beds/var_oracle.py maps/live_var/$1.map $2 $3 0 1 $left 2>&1 | tail -1)
  echo "$out"; case "$out" in *"new 0 "*) break;; esac
  n=$(echo "$out" | awk '{print $5, $7}'); set -- "$@"; [ "$(echo $out | awk '{print $5}')" = "$(echo $out | awk '{print $7}')" ] && break
done
