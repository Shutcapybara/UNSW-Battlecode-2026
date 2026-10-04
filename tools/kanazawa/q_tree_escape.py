"""Kanazawa unit 6, H-KZ16: how do queens survive a tree pocket (C<=5, acyclic incl. u)? For each first tree entry that is
not followed by a wall death within the window, print queen length trajectory t..t+8, whether the head left the pocket, the
death cause/round, and whether new same-side ids appeared (split). All 190 post-m2 games. Repo root."""
import json, sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
ROOT = Path.cwd(); sys.path[:0] = [str(ROOT), str(ROOT / 'build/kanazawa/tree/tools/kanazawa')]
if (ROOT / 'build/s1-pylib').exists(): sys.path.append(str(ROOT / 'build/s1-pylib'))
CORPUS = ROOT / 'public_replays/corpus'
def one(args):
    gid, ours = args
    import importlib.util as iu
    spec = iu.spec_from_file_location('qc', ROOT / 'build/kanazawa/tree/tools/kanazawa/q_cycle.py'); qc = iu.module_from_spec(spec); spec.loader.exec_module(qc)
    from tools.analysis.features.frame import decode
    g = decode(str(CORPUS / 'replays' / f'{gid}.replay')); R = g['rounds']; nbr = g['nbr']; res = []
    for side in ('A', 'B'):
        q = min(i for i, (t, _) in R[0].items() if t == side)
        d = next((d for d in g['events']['deaths'] if d['id'] == q), None)
        for t in range(1, len(R) - 1):
            if q not in R[t] or q not in R[t + 1]: break
            u, v = R[t][q][1][0], R[t + 1][q][1][0]
            if u == v or v not in nbr.get(u, ()): continue
            P = qc.pocket(nbr, u, v)
            if P is None or qc.longest_cycle(P + [u], nbr): continue
            dr = d['round'] if d else None; cause = d['cause'] if d else None
            if cause == 'wall' and 0 <= dr - (t + 1) <= 6: break
            ids_t = {i for i, (s, _) in R[t].items() if s == side}
            traj = []; left = None
            for r in range(t + 1, min(t + 10, len(R))):
                if q not in R[r]: traj.append('X'); continue
                b = R[r][q][1]; traj.append(len(b))
                if left is None and b[0] not in P: left = r - t
            new = sorted({i for r in range(t + 1, min(t + 10, len(R))) for i, (s, _) in R[r].items() if s == side} - ids_t)
            res.append((gid, 'us' if side == ours else 'opp', t, len(P), traj, left, cause, dr, len(new)))
            break
    return res
metas = []
for line in open(CORPUS / 'index.jsonl'):
    m = json.loads(line)
    if m.get('status') != 'completed' or (m.get('started_at') or '') < '2026-10-02T03:49': continue
    if 7 not in (m.get('team_a'), m.get('team_b')): continue
    if (CORPUS / 'replays' / f"{m['game_id']}.replay").exists(): metas.append((m['game_id'], 'A' if m['team_a'] == 7 else 'B'))
k = max(1, len(metas) // 96); pick = metas[::k][:96] + metas[192:]
with ProcessPoolExecutor(4) as ex:
    for res in ex.map(one, pick):
        for r in res: print(*r)
