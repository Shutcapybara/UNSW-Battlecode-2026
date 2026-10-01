#!/usr/bin/env bash
# Pull one team's corpus replays plus the corpus index and ladder from the Mac (HB-1 data recipe, any team id).
# Usage: tools/hb1/sync_team.sh TEAM [user@mac]   (re-run to pick up new games; rsync skips what is present)
set -euo pipefail
TEAM="$1"
M="${2:-alik@192.168.0.86}"
MREPO=/Users/alik/Documents/Projects/UNSW-Battlecode-2026
cd "$(dirname "$0")/../.."
mkdir -p public_replays/corpus build/tt
ssh -- "$M" "cd $MREPO/public_replays/corpus && python3 -c \"
import json
for l in open('index.jsonl'):
    r=json.loads(l)
    if $TEAM in (r['team_a'],r['team_b']) and r.get('status')=='completed': print('replays/%d.replay'%r['game_id'])\"" > build/tt/team$TEAM.txt
wc -l build/tt/team$TEAM.txt
rsync -a --files-from=build/tt/team$TEAM.txt "$M:$MREPO/public_replays/corpus/" public_replays/corpus/
rsync -a "$M:$MREPO/public_replays/corpus/index.jsonl" "$M:$MREPO/public_replays/corpus/ladder" public_replays/corpus/
