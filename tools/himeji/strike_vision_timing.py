"""Compare round-start and attacker-TurnStart vision on already verified strikes.
No new replay population; exact actor states are from unit30's raw-event audit.
"""
import argparse, hashlib, json, sys
from pathlib import Path
p = argparse.ArgumentParser()
p.add_argument('--repo', type=Path, required=True)
p.add_argument('--audit', type=Path, required=True)
p.add_argument('--peer', type=Path, required=True)
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
sys.path.insert(0, str(a.repo))
from tools.analysis.features import frame as F
peers = {(r['gid'], r['r'], r['who']): r for r in
         (json.loads(s) for s in a.peer.read_text().splitlines() if s.startswith('{"'))}
rows = []
for r in json.loads(a.audit.read_text())['rows']:
    replay = a.repo / 'public_replays/corpus/replays' / f"{r['game']}.replay"
    assert hashlib.sha256(replay.read_bytes()).hexdigest() == r['replay_sha256']
    root = F._reader(replay).object(0, 0)
    assert hashlib.sha256(root.text(0).encode()).hexdigest() == r['map_hash']
    m = F.terrain(root.text(0))[0]
    st = r['killer_turn_start']
    u, v = st['killer_head'], st['queen_head']
    dx, dy = abs(u[0]-v[0]), abs(u[1]-v[1])
    # Terrain dimensions use the same keys as FRAME's decoded result.
    d = max(min(dx, m['W']-dx), min(dy, m['H']-dy))
    peer = peers[(r['game'], r['death']['round'], r['peer']['who'])]
    rows.append(dict(game=r['game'], series=r['series'], ranked=r['ranked'],
        map=r['map'], map_hash=r['map_hash'], who=r['peer']['who'],
        round=r['death']['round'], queen=r['queen'], killer=r['killer'],
        round_start_cheb=peer['cheb_seq'][-1], round_start_visible=peer['killer_sees_now'],
        attacker_turn_cheb=d, attacker_turn_visible=d <= 3,
        attacker_turn_state=st, queen_last_turn_start=r['queen_last_turn_start']))
summary = {}
for who in ('us', 'opp'):
    rr = [r for r in rows if r['who'] == who]
    summary[who] = dict(n=len(rr), series=len({r['series'] for r in rr}),
        ranked=sum(r['ranked'] for r in rr),
        round_start_visible=sum(r['round_start_visible'] for r in rr),
        attacker_turn_visible=sum(r['attacker_turn_visible'] for r in rr),
        changed=[r['game'] for r in rr if r['round_start_visible'] != r['attacker_turn_visible']])
a.out.write_text(json.dumps(dict(summary=summary, rows=rows,
    contract='Geometric Chebyshev<=3 visibility at attacker TurnStart, not proof of information use, targeting, or absence of shared tracking. Same selected24 cases; no population inference.'), indent=2)+'\n')
print(json.dumps(summary, indent=2))
