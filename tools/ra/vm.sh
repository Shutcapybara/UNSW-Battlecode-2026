#!/bin/bash
# one ~170 s chunk on the Cowork VM: vm.sh BOT [PANEL] [JOBS]  (run | extract when complete)
cd "$(dirname "$0")/../.."
export TMPDIR=/tmp RA_HOST=vm
PY=${PY:-/tmp/ra-venv/bin/python}
B=$1; P=${2:-pool}; J=${3:-6}
out=$(timeout 172 $PY tools/ra/lane.py run $B --panel $P --jobs $J --budget 100 2>&1 | grep -v "^\[.*\] [0-9]*/" | tail -1)
echo "$B $P: $out"
if echo "$out" | grep -q " 0 left"; then timeout 25 true; fi
