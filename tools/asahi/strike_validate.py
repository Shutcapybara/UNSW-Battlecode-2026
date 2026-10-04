#!/usr/bin/env python3
"""Validation of tools/asahi/strike_label.py on a NON-panel-parent arm (P-4 amendment 1): consistency with the engine
header (queen dead <=> header queen length 0, both sides), killer step count >= BFS distance for every strike, killer
team, and a list of strike / adjacent / killer_survived events for hand tracing.
    python tools/asahi/strike_validate.py BOT"""
import json, sys
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/asahi'))
import panel as P  # noqa: E402

bot = sys.argv[1]
out = {}
for panel in ('pool', 'gen'):
    root = P.run_root(bot, panel)
    S = pd.read_parquet(root / 'strikes.parquet'); Q = pd.read_parquet(root / 'queen.parquet')
    m = S.merge(Q[['game', 'side', 'queen_end', 'last_round']], on=['game', 'side'], how='left')
    dis = m[(m.dead == 1) != (m.queen_end == 0)]
    st = m[m.category == 'strike']
    bad_steps = st[st.killer_steps.isna() | (st.killer_steps < st.dist)]
    out[panel] = dict(sides=len(m), header_disagree=len(dis), header_disagree_rows=dis[['game', 'side', 'dead', 'queen_end', 'cause', 'death_round', 'last_round']].head(10).to_dict('records'),
                      strikes=len(st), strike_steps_lt_dist=len(bad_steps), dist_hist=st.dist.value_counts().sort_index().to_dict(),
                      steps_minus_dist=(st.killer_steps - st.dist).value_counts().sort_index().to_dict(),
                      examples=st[['game', 'side', 'death_round', 'killer', 'dist', 'killer_steps']].head(6).to_dict('records'),
                      killer_survived=m[m.category == 'killer_survived'][['game', 'side', 'death_round', 'killer', 'dist']].head(5).to_dict('records'))
print(json.dumps(out, indent=1, default=str))
(root.parent.parent / 'strike_validation.json').write_text(json.dumps(out, indent=1, default=str))
