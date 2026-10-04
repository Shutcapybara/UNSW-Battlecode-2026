#!/usr/bin/env python3
"""P-4 / H-KZ26 event-time labeller (Asahi; frozen before any parent labelling, D-054 §C, Tanaka's amendment 1).

Streams a local engine replay in event order (the same event decoding as tools/learn/rebuild.py, Kageyama's exact
blocks: round = kind 0, turn start = kind 1, action = kind 4, head/tail move = kind 9, split = kind 10, death = 11) and
labels, for each team's ORIGINAL QUEEN (the team's lowest-id initial dragon from the map's DRAGON lines):

- alive_rounds: rounds whose round-start event finds the queen alive (the hazard denominator);
- death: round, engine cause (wall/self/body/h2h/invalid), and the mover whose turn it was (event order in the round);
- strike: the queen died by 'h2h' during the turn of an ENEMY dragon K (the killer), K also died in that same turn, and
  at K's own TurnStart the body-ignoring BFS distance (map edges, wraps, portals; frame.terrain's graph) from K's head
  to the queen's head was >= 2. The killer's action (step count) is recorded as a check: a strike needs >= dist steps.
- other categories, reported: queen_initiated (the queen was the mover), ally_h2h (killer on our team),
  adjacent (distance <= 1), killer_survived, unknown (no TurnStart seen for the killer).

    python tools/asahi/strike_label.py BOT --panel pool|gen|both [--jobs 14]     # writes <run>/strikes.parquet
    python tools/asahi/strike_label.py --replay FILE                              # one replay, printed (hand trace)
"""
from __future__ import annotations

import argparse, collections, glob, hashlib, json, os, sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tools/learn'))
sys.path.insert(0, str(ROOT / 'tools/hub/vendor/leviathan'))
import rebuild as RB  # noqa: E402
from tools.analysis.features.frame import terrain  # noqa: E402

CAUSES = ('wall', 'self', 'body', 'h2h', 'invalid')


def bfs(nbr, a, b):
    if a == b:
        return 0
    seen = {a}
    frontier = [a]
    d = 0
    while frontier:
        d += 1
        nxt = []
        for c in frontier:
            for n in nbr[c]:
                if n is None or n in seen:
                    continue
                if n == b:
                    return d
                seen.add(n)
                nxt.append(n)
        frontier = nxt
    return None


def label(data: bytes) -> dict:
    r = RB.reader(data)
    root = r.object(0, 0)
    mtext = root.text(0)
    m = RB.Map(mtext)
    _, W, H, nbr, _, _ = terrain(mtext)
    team, body, alive = {}, {}, {}
    for i, (t, b) in enumerate(m.dragons):
        team[i], body[i], alive[i] = t, collections.deque(b), True
    queen = {t: min(i for i in team if team[i] == t) for t in 'AB' if any(team[i] == t for i in team)}
    qid = {v: k for k, v in queen.items()}
    alive_rounds = {t: 0 for t in queen}
    ts = {}            # mover id -> (round, own head, {queen id: queen head}) at its latest TurnStart
    action = {}        # mover id -> step count of its latest action
    deaths = []        # (round, id, cause, mover)
    rnd, cur = -1, None
    for e in root.items(3):
        kind = e.num(0, 'H')
        o = e.child(0)
        if kind == 0:
            rnd = o.num(); cur = None
            for t, q in queen.items():
                if alive[q]:
                    alive_rounds[t] += 1
        elif kind == 1:
            cur = o.num()
            ts[cur] = (rnd, body[cur][0], {q: body[q][0] for q in qid if alive[q]})
            action[cur] = None
        elif kind == 4:
            if cur is not None and o.num() == cur and o.has(0):
                a = o.child(0)
                if a.num(0, 'H') == 0:
                    s_, at, word = r.pointer(a.s, a.a + a.dw)
                    action[cur] = ('move', word >> 35)
                elif a.num(0, 'H') == 1:
                    action[cur] = ('split', a.num(4))
                else:
                    action[cur] = ('other', a.num(0, 'H'))
        elif kind == 9:
            i = o.num()
            head, tail = (o.child(0).num(), o.child(0).num(4)), (o.child(1).num(), o.child(1).num(4))
            b = body[i]
            if b[0] != head:
                b.appendleft(head)
            while len(b) > 1 and b[-1] != tail:
                b.pop()
        elif kind == 10:
            pid, cid = o.num(), o.num(4)
            body[pid] = collections.deque((q.num(), q.num(4)) for q in o.items(0))
            body[cid] = collections.deque((q.num(), q.num(4)) for q in o.items(1))
            team[cid], alive[cid] = team[pid], True
        elif kind == 11:
            did = o.num()
            alive[did] = False
            c = o.num(4, 'H')
            deaths.append((rnd, did, CAUSES[c] if c < 5 else 'other', cur))
    out = dict(map=m.name, queens={t: q for t, q in queen.items()}, alive_rounds=alive_rounds, last_round=rnd, sides={})
    for t, q in queen.items():
        row = dict(queen=q, alive_rounds=alive_rounds[t], dead=0, death_round=None, cause=None, mover=None,
                   strike=0, category='alive', dist=None, killer=None, killer_steps=None, killer_died=None)
        qd = [d for d in deaths if d[1] == q]
        if qd:
            rd, _, cause, mover = qd[0]
            row.update(dead=1, death_round=rd, cause=cause, mover=mover, category=cause)
            if cause == 'h2h':
                if mover == q:
                    row['category'] = 'queen_initiated'
                elif mover is None or mover not in ts:
                    row['category'] = 'unknown'
                else:
                    killer_died = any(d[1] == mover and d[0] == rd and d[3] == mover for d in deaths)
                    trd, khead, qheads = ts[mover]
                    dist = bfs(nbr, khead, qheads[q]) if q in qheads else None
                    act = action.get(mover)
                    row.update(killer=mover, killer_died=int(killer_died), dist=dist,
                               killer_steps=act[1] if act and act[0] == 'move' else None)
                    if team[mover] == t:
                        row['category'] = 'ally_h2h'
                    elif dist is None:
                        row['category'] = 'unknown'
                    elif dist <= 1:
                        row['category'] = 'adjacent'
                    elif not killer_died:
                        row['category'] = 'killer_survived'
                    else:
                        row['category'] = 'strike'; row['strike'] = 1
        out['sides'][t] = row
    return out


def one(path):
    try:
        res = label(Path(path).read_bytes())
        return [dict(game=Path(path).stem, side=t, **v) for t, v in res['sides'].items()]
    except Exception as e:  # listed, never dropped silently
        return [dict(game=Path(path).stem, side=None, error=f'{type(e).__name__}: {e}')]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('bot', nargs='?'); ap.add_argument('--panel', default='both'); ap.add_argument('--jobs', type=int, default=14)
    ap.add_argument('--replay')
    a = ap.parse_args()
    sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if a.replay:
        print(json.dumps(label(Path(a.replay).read_bytes()), indent=1, default=str)); print('labeller sha256', sha); return
    import pandas as pd
    sys.path.insert(0, str(ROOT / 'tools/asahi'))
    import panel as P
    jobs = min(a.jobs, int(os.environ.get('ASAHI_MAX_WORKERS', '14')))
    for panel in (['pool', 'gen'] if a.panel == 'both' else [a.panel]):
        root = P.run_root(a.bot, panel)
        reps = sorted(glob.glob(str(root / 'replays/*.replay')))
        with ProcessPoolExecutor(jobs) as ex:
            rows = [r for rs in ex.map(one, reps, chunksize=4) for r in rs]
        S = pd.DataFrame(rows)
        S['labeller_sha256'] = sha
        S.to_parquet(root / 'strikes.parquet', index=False)
        err = S[S['side'].isna()] if 'error' in S else S.iloc[0:0]
        print(panel, len(reps), 'replays;', len(err), 'errors; categories', S.groupby('category').size().to_dict() if 'category' in S else {},
              '; labeller', sha[:16])


if __name__ == '__main__':
    main()
