#!/usr/bin/env bash
# Pull team-62 replays, the corpus index/ladder and the 27 Sep recon packets from the Mac (HB-1 data recipe).
# Usage: tools/hb1/sync_from_mac.sh [user@mac]   (re-run daily to pick up new games)
set -euo pipefail
M="${1:-alik@192.168.0.86}"
MREPO=/Users/alik/Documents/Projects/UNSW-Battlecode-2026
cd "$(dirname "$0")/../.."
mkdir -p public_replays/corpus experiment_data build/hb1
ssh -- "$M" "cd $MREPO/public_replays/corpus && python3 -c \"
import json
for l in open('index.jsonl'):
    r=json.loads(l)
    if 62 in (r['team_a'],r['team_b']): print('replays/%d.replay'%r['game_id'])\"" > build/hb1/hb62.txt
wc -l build/hb1/hb62.txt
rsync -a --files-from=build/hb1/hb62.txt "$M:$MREPO/public_replays/corpus/" public_replays/corpus/
rsync -a "$M:$MREPO/public_replays/corpus/index.jsonl" "$M:$MREPO/public_replays/corpus/ladder" public_replays/corpus/
rsync -a "$M:$MREPO/experiment_data/team_recon_62_20260927T140359Z" "$M:$MREPO/experiment_data/team_recon_62_20260927_glm" experiment_data/
rsync -a --exclude packed/ --exclude "*/" "$M:$MREPO/public_replays/team-62/" public_replays/team-62/
