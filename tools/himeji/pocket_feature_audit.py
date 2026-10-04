"""Audit the proposed terrain-only feature on a frozen peer seal selection. No bot/store writes."""
import argparse, collections, csv, hashlib, json, sys
from pathlib import Path
ap = argparse.ArgumentParser()
ap.add_argument('--repo', type=Path, required=True)
ap.add_argument('--selection', type=Path, required=True)
ap.add_argument('--index', type=Path, required=True)
ap.add_argument('--out', type=Path, required=True)
a = ap.parse_args()
sys.path.insert(0, str(a.repo))
from tools.analysis.features import frame as F
idx = {str(r['game_id']): r for r in map(json.loads, a.index.read_text().splitlines())}
out = []

def flood(nbr, head, occ):
    seen = {head}
    todo = [head]
    while todo:
        c = todo.pop()
        for n in nbr.get(c, ()):
            if n is not None and n not in occ and (n not in seen):
                seen.add(n)
                todo.append(n)
    return len(seen) - 1
for row in csv.DictReader(a.selection.open()):
    meta = idx[row['game']]
    p = a.repo / 'public_replays/corpus/replays' / f"{row['game']}.replay"
    assert hashlib.sha256(p.read_bytes()).hexdigest() == meta['sha256']
    g = F.decode(p)
    assert g['winner'].lower() == meta['winner']
    root = F._reader(p).object(0, 0)
    assert hashlib.sha256(root.text(0).encode()).hexdigest() == meta['map_hash']
    side = row['side']
    q = min((i for (i, (t, b)) in g['rounds'][0].items() if t == side))
    s = int(row['seal_start'])
    st = g['rounds'][s]
    head = st[q][1][0]
    groups = {'own': set(st[q][1][1:]), 'ally': set(), 'enemy': set()}
    for (i, (tm, b)) in st.items():
        if i != q:
            groups['ally' if tm == side else 'enemy'].update(b)
    full = set.union(*groups.values())
    counts = {'all_bodies': flood(g['nbr'], head, full), 'peer_minus_own': flood(g['nbr'], head, set().union(*(set(b[1:] if i == q else b) for (i, (tm, b)) in st.items()))), 'true_minus_own': flood(g['nbr'], head, groups['ally'] | groups['enemy']), 'true_minus_ally': flood(g['nbr'], head, groups['own'] | groups['enemy']), 'true_minus_enemy': flood(g['nbr'], head, groups['own'] | groups['ally']), 'own_body_only': flood(g['nbr'], head, groups['own']), 'true_terrain_only': flood(g['nbr'], head, set())}
    out.append({'game': int(row['game']), 'series': meta['series_id'], 'ranked': meta['ranked'], 'started_at': meta['started_at'], 'map': meta['map_name'], 'map_hash': meta['map_hash'], 'own_side': side, 'submission': root.text(1 if side == 'A' else 2), 'queen': q, 'seal_round_peer': s, 'death_round_peer': int(row['death_round']), 'body_head_first': st[q][1], 'counts': counts, 'sha256': meta['sha256'], 'official_winner': g['winner']})
    a.out.write_text(json.dumps({'rows': out, 'scope': '17 selected wall-death states, not incidence or policy effects. Exact flood on ROUND START states to audit peer feature; not exact TurnStart occupancy. Counts exclude starting head; no cap.'}, indent=2) + '\n')
    print(row['game'], meta['map_name'], counts, flush=True)
