#!/bin/bash
# one chunk on the Cowork VM: vm3.sh BOT [PANEL] [JOBS] [BUDGET] [SHARD k/n]
cd "$(dirname "$0")/../.."
export TMPDIR=/tmp RA_HOST=vm
PY=${PY:-/tmp/ra-venv/bin/python}
B=$1; P=${2:-pool}; J=${3:-6}; BU=${4:-100}; SH=${5:+--shard $5}
timeout 168 $PY tools/ra/lane.py run $B --panel $P --jobs $J --budget $BU $SH > /tmp/ra-last.log 2>&1
n=$(ls build/ra/runs/$B/$P/replays 2>/dev/null | grep -c '\.replay$')
echo "$B $P: $n replays; load $(cut -d' ' -f1 /proc/loadavg)"
