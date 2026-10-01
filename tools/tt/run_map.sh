#!/usr/bin/env bash
# TT: extract map-memory features for a game subset per team (Heartbreaker as the control).
cd /home/alik/Documents/Projects/2026/wt-tt
for spec in "hb62 ../wt-hb1/build/hb1 400" "team70 build/tt/team70 400" "team206 build/tt/team206 400" "team264 build/tt/team264 400" "team952r build/tt/team952r 598"; do
  set -- $spec
  OUT=build/tt/map/$1; mkdir -p $OUT
  .venv/bin/python - "$2" "$OUT" "$3" <<'PY'
import json, sys, pandas as pd
src, out, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
g = pd.read_parquet(f'{src}/games.parquet').query("set == 'corpus'").sort_values('game')
g = g.iloc[::max(1, len(g) // n)].head(n)
json.dump({str(int(r.game)): r.side for r in g.itertuples()}, open(f'{out}/sides.json', 'w'))
open(f'{out}/paths.txt', 'w').write('\n'.join(g.path))
print(out, len(g), 'games')
PY
  echo "START $1 $(date -Is)"
  xargs -a $OUT/paths.txt .venv/bin/python tools/tt/features_map.py $OUT/v6 $OUT/sides.json --jobs 12 > $OUT/extract.log 2>&1
  echo "DONE $1 parquets $(ls $OUT/v6/*.parquet 2>/dev/null | wc -l) errors $(ls $OUT/v6/*.error 2>/dev/null | wc -l) $(date -Is)"
done
echo "MAP EXTRACTION FINISHED $(date -Is)"
