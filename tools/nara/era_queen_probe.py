"""Nara era+queen probe v2: sprint-formula verification and queen extraction from a replay.

Per game:
  era signal   surviving moves with steps>=2 & paid==0 (impossible pre-change)
  formula      for surviving multi-step moves post-change: free = steps - paid vs min(steps, ceil(L/4)),
               L = length at round start (from the rounds snapshots)
  queens       per team: living lowest-id robot (id, length) on the final snapshot; whether the original
               queen (team's lowest initial id) is alive; its length if alive; longest; total
  verdicts     server winner, old-rule winner (longest->total), living-queen rule, original-queen rule
"""
import json, sys, math
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'tools' / 'leviathan'))
sys.path.insert(0, str(ROOT / 'tools' / 'analysis' / 'features'))

CORPUS = ROOT / 'public_replays' / 'corpus'


def probe(args):
    gid, started, winner_srv = args
    winner_srv = winner_srv.upper() if isinstance(winner_srv, str) else winner_srv
    from frame import decode
    path = CORPUS / 'replays' / f'{gid}.replay'
    if not path.exists():
        return None
    try:
        g = decode(path)
    except Exception as e:
        return dict(game=gid, error=f'{type(e).__name__}: {e}')
    acts = g['events']['actions']
    dead = {(d['round'], d['id']) for d in g['events']['deaths']}
    s0 = 0
    formula_ok = formula_bad = 0
    formula_bad_ex = []
    for a in acts:
        if a['kind'] != 'move' or a.get('steps', 0) < 2 or (a['round'], a['id']) in dead:
            continue
        if a.get('paid') == 0:
            s0 += 1
        # formula check: paid should equal max(0, steps - ceil(L/4)), L at round start
        r = a['round']
        body = g['rounds'][r].get(a['id'])
        if body is not None:
            L = len(body[1])
            free = min(a['steps'], math.ceil(L / 4))
            if a['paid'] == a['steps'] - free:
                formula_ok += 1
            else:
                formula_bad += 1
                if len(formula_bad_ex) < 5:
                    formula_bad_ex.append(dict(r=r, id=a['id'], L=L, steps=a['steps'], paid=a['paid']))
    fin = g['final']
    rounds_fin = g['rounds'][-1]
    out = dict(game=gid, started=started, map=g['map'], winner_srv=winner_srv,
               winner_old=g['winner'], reason=g['reason'], last_round=g['last_round'],
               s0=s0, formula_ok=formula_ok, formula_bad=formula_bad, formula_bad_ex=formula_bad_ex)
    n_init = g['n_initial']
    init_teams = {i: tm for i, tm in ((i, g['rounds'][0][i][0]) for i in range(n_init)) if i in g['rounds'][0]}
    rl = g['reason'] in ('longest', 'total', 'tie')
    out['round_limit'] = rl
    qrule = {}
    for t in ('A', 'B'):
        ids = [i for i, (tm, _) in rounds_fin.items() if tm == t]
        fin_t = fin[t]
        orig = min((i for i, tm in init_teams.items() if tm == t), default=None)
        orig_alive = orig in rounds_fin and rounds_fin[orig][0] == t
        orig_len = len(rounds_fin[orig][1]) if orig_alive else 0
        qid = min(ids) if ids else None
        qrule[t] = dict(
            n=len(ids), queen_id=qid, queen_len=len(rounds_fin[qid][1]) if qid is not None else 0,
            queen_is_initial=qid is not None and qid < n_init,
            orig_id=orig, orig_alive=orig_alive, orig_len=orig_len,
            longest=fin_t['longest'], total=fin_t['total'])
    out['queens'] = qrule
    if rl:
        A, B = qrule['A'], qrule['B']
        out['w_living_queen'] = ('A' if A['queen_len'] > B['queen_len'] else 'B' if B['queen_len'] > A['queen_len'] else 'draw')
        out['w_orig_queen'] = ('A' if A['orig_len'] > B['orig_len'] else 'B' if B['orig_len'] > A['orig_len'] else 'draw')
    return out


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('games', nargs='+', help='game_id[:winner] pairs or file with jsonl rows')
    a = ap.parse_args()
    tasks = []
    for arg in a.games:
        if arg.endswith('.jsonl'):
            for line in open(arg):
                r = json.loads(line)
                if r.get('status') == 'completed':
                    tasks.append((r['game_id'], r['started_at'], r.get('winner')))
        else:
            gid, _, w = arg.partition(':')
            tasks.append((int(gid), '', w or None))
    import multiprocessing as mp
    with mp.Pool(8) as pool:
        for r in pool.imap_unordered(probe, tasks, chunksize=1):
            if r:
                print(json.dumps(r))
