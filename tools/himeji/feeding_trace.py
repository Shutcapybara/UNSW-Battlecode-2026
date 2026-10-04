"""Trace six preselected discovery games, not a population/causal feeding estimate.
Reads existing replay bytes only; no API, simulator, cache, or shared-store writes.
"""
import argparse, collections, hashlib, json, sys
from pathlib import Path

p = argparse.ArgumentParser()
for key in ('repo', 'index', 'pairs', 'out'):
    p.add_argument('--' + key, type=Path, required=True)
a = p.parse_args()
sys.path.insert(0, str(a.repo))
from tools.analysis.features import frame as F
idx = {str(m['game_id']): m for m in map(json.loads, a.index.read_text().splitlines())}
pairs = [p for p in json.loads(a.pairs.read_text())['pairs'] if p['team'] in (112, 952, 55)]
assert len(pairs) == 3
out = []
for pair in pairs:
    for period in ('early', 'late'):
        gid = str(pair[period + '_game']); m = idx[gid]
        path = a.repo / 'public_replays/corpus/replays' / (gid + '.replay')
        assert hashlib.sha256(path.read_bytes()).hexdigest() == m['sha256']
        root = F._reader(path).object(0, 0)
        assert root.num(0, 'I') == 2 and root.child(4).num(0, 'B') & 1
        mh = hashlib.sha256(root.text(0).encode()).hexdigest()
        assert mh == m['map_hash'] == pair['map_hash']
        g = F.decode(path); side = pair['side']
        assert g['winner'].lower() == m['winner'] and m['ranked']
        assert m['team_a' if side == 'A' else 'team_b'] == pair['team']
        q = min(i for i, (t, b) in g['rounds'][0].items() if t == side)
        ev = g['events']; eats = [e for e in ev['eats'] if e['id'] == q]
        acts = [e for e in ev['actions'] if e['id'] == q]
        splits = [e for e in ev['splits'] if e['parent'] == q]
        assert not any(e['id'] == q for e in ev['deaths'])
        q0 = len(g['rounds'][0][q][1]); qe = len(g['rounds'][-1][q][1])
        paid = sum(e.get('paid', 0) for e in acts)
        split_loss = sum(e['before'] - e['parent_len'] for e in splits)
        assert qe == q0 + len(eats) - paid - split_loss
        assert qe == g['final'][side]['queen'] == pair[period + '_queen']
        deaths = {e['id']: e for e in ev['deaths']}
        actions = {(e['round'], e['id']): e for e in ev['actions']}
        # Use donor and birth round from event provenance, never first cell meal by round.
        spawns = collections.defaultdict(list)
        for s in ev['spawns']:
            spawns[(s['donor'], s['round'], tuple(s['cell']))].append(s)
        parents = {e['child']: e['parent'] for e in ev['splits']}
        def from_queen(i):
            while i in parents:
                i = parents[i]
            return i == q
        donor_rows = []
        for donor in sorted({e['donor'] for e in eats if e['origin'] == 'ally_corpse'}):
            de = deaths[donor]; aa = actions.get((de['round'], donor))
            meals = [e for e in eats if e['origin'] == 'ally_corpse' and e['donor'] == donor]
            for e in meals:
                ss = spawns[(donor, e['round']-e['age'], tuple(e['cell']))]
                assert len(ss) == 1 and ss[0]['origin'] == side
            donor_rows.append(dict(donor=donor, death=de, action_on_death_round=aa,
                                   queen_meals=meals, own_turn_death=de['actor'] == donor,
                                   explicit_suicide=bool(aa and aa['kind']=='suicide' and de['actor']==donor),
                                   queen_lineage=from_queen(donor)))
        heads = [s[q][1][0] for s in g['rounds'] if q in s]
        dist = {heads[0]: 0}; todo = collections.deque([heads[0]])
        while todo:
            cell = todo.popleft()
            for nxt in g['nbr'][cell]:
                if nxt is not None and nxt not in dist:
                    dist[nxt] = dist[cell]+1; todo.append(nxt)
        windows = []
        for lo, hi in ((0, 149), (150, 299), (300, 499)):
            ee = [e for e in eats if lo <= e['round'] <= hi]
            aa = [e for e in acts if lo <= e['round'] <= hi]
            windows.append(dict(lo=lo, hi=hi, food=dict(collections.Counter(e['origin'] for e in ee)),
                                commands=dict(collections.Counter(e['kind'] for e in aa)),
                                commanded_steps=sum(e['steps'] for e in aa), paid=sum(e.get('paid',0) for e in aa)))
        r = dict(game=gid, team=pair['team'], period=period, side=side, map=g['map'], map_hash=mh,
                 started_at=m['started_at'], series_id=m['series_id'], opponent=m['team_b' if side=='A' else 'team_a'],
                 ranked=m['ranked'], map_era='post-m2', replay_sha256=m['sha256'], submission=root.text(1 if side=='A' else 2),
                 official_winner=g['winner'], reason=g['reason'], queen_id=q, start_length=q0, end_length=qe,
                 reached490=g['last_round']>=490, length490=len(g['rounds'][490][q][1]) if g['last_round']>=490 else None,
                 food=dict(collections.Counter(e['origin'] for e in eats)), paid=paid, split_loss=split_loss,
                 max_terrain_steps_from_spawn=max(dist.get(h,-1) for h in heads),
                 fraction_round_start_heads_within3=sum(dist.get(h,999)<=3 for h in heads)/len(heads),
                 unique_round_start_heads=len(set(heads)), round_start_head_changes=sum(x!=y for x,y in zip(heads, heads[1:])),
                 commanded_steps=sum(e['steps'] for e in acts), commands=dict(collections.Counter(e['kind'] for e in acts)),
                 windows=windows, queen_eats=eats, queen_splits=splits, donors=donor_rows)
        out.append(r)
        print(gid, period, pair['team'], q0, qe, r['food'], 'paid',paid,'split',split_loss,'heads',len(set(heads)),flush=True)
a.out.write_text(json.dumps(dict(selection='Three independent teams from unit32 outcome-selected discovery pairs; same fullhash/team/seat, different opponent/time; not held-out or causal.', source_pairs_sha256=hashlib.sha256(a.pairs.read_bytes()).hexdigest(), games=out),indent=2)+'\n')
