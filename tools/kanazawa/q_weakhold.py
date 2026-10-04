"""Kanazawa unit 8: weakhold opening tree entries. For every post-m2 team-7 weakhold game: our queen's first tree entry round,
cell, length, queen death round, winner. Same for the opponent queen."""
import json, sys
from collections import Counter
from pathlib import Path
ROOT = Path.cwd(); sys.path[:0] = [str(ROOT), str(ROOT / 'build/kanazawa/tree')]
from tools.kanazawa.q_cycle import pocket, longest_cycle, CORPUS
from tools.analysis.features.frame import decode
c = Counter()
for line in open(CORPUS / 'index.jsonl'):
    m = json.loads(line)
    if m.get('status') != 'completed' or (m.get('started_at') or '') < '2026-10-02T03:49' or 7 not in (m.get('team_a'), m.get('team_b')): continue
    if m['map_name'] != 'weakhold' or not (CORPUS / 'replays' / f"{m['game_id']}.replay").exists(): continue
    g = decode(str(CORPUS / 'replays' / f"{m['game_id']}.replay")); R = g['rounds']; nbr = g['nbr']; ours = 'A' if m['team_a'] == 7 else 'B'
    res = []
    for side in ('A', 'B'):
        q = min(i for i, (t, _) in R[0].items() if t == side); ent = None; death = None
        for t in range(1, len(R) - 1):
            if q not in R[t + 1]: death = t + 1; break
            if ent: continue
            u = R[t][q][1][0]; v = R[t + 1][q][1][0]
            if v in nbr.get(u, ()):
                P = pocket(nbr, u, v)
                if P is not None and longest_cycle(P + [u], nbr) == 0: ent = (t, u, v, len(R[t][q][1]))
        res.append(('us' if side == ours else 'opp', ent, death))
    win = 'us' if m['winner'] == ours.lower() else 'opp'
    print(m['game_id'], m['started_at'][:16], 'sub', m['sub_a'] if ours == 'A' else m['sub_b'], 'seat', ours, 'win', win, res)
