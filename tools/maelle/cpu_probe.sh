#!/bin/bash
# usage: probe.sh BOTPATH TAG  -> build/maelle/cpu/TAG/<map>-<seat>.json
PY=/home/alik/Documents/Projects/2026/UNSW-Battlecode-2026/.venv/bin/python
cd /home/alik/Documents/Projects/2026/wt-maelle
B=$1; T=$2; OPP=bots/ares-v06-expanded-search-support
mkdir -p build/maelle/cpu/$T
for m in schooltime portals trauma big_empty new/mc26_far_harbors new/mc26_relay_depots; do
  tag=${m//\//+}
  [ -f build/maelle/cpu/$T/$tag-A.json ] || $PY tools/cx/arena.py maps/$m.map $B $OPP --sandbox --json build/maelle/cpu/$T/$tag-A.json > /dev/null 2>&1 &
  [ -f build/maelle/cpu/$T/$tag-B.json ] || $PY tools/cx/arena.py maps/$m.map $OPP $B --sandbox --json build/maelle/cpu/$T/$tag-B.json > /dev/null 2>&1 &
  wait
done
# summary
$PY - "$T" <<'PY'
import json, glob, sys
T = sys.argv[1]; rows = []
for f in sorted(glob.glob(f'build/maelle/cpu/{T}/*.json')):
    r = json.load(open(f)); seat = f[-6]
    p = r['stats'][seat].get('points', {})
    rows.append((f.split('/')[-1][:-5], p.get('p50', 0), p.get('p99', 0), p.get('max', 0), len(r.get('errors', []))))
for x in rows: print(f'{x[0]:28s} p50={x[1]/1e6:5.2f}M p99={x[2]/1e6:5.2f}M max={x[3]/1e6:5.2f}M errors={x[4]}')
print(f'{T}: CPU max {max(x[3] for x in rows)/1e6:.2f}M over {len(rows)} seats')
PY
