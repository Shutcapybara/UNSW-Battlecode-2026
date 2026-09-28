"""Corpse capture accounting: who eats the pearls left by a team's dead dragons.

For each team T: segments lost in deaths (from round FROM), how many of those corpse
cells were later eaten by T's longest dragon ("crown"), by other T dragons, by the
enemy, or never. Pearls on a corpse cell are attributed on first removal after the
death (a later regrowth on a fertile tile would be mis-attributed only if the corpse
was never eaten; corpse entries expire after TTL rounds).
usage: corpse.py REPLAY [FROM]
"""
import collections, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'ouroboros'))
import replaystats as rs
TTL = 60


def analyse(path, frm=350):
    rep = rs.load(path)
    team, body = {}, {}
    nid = 0
    for line in rep.map.splitlines():
        if line.startswith('DRAGON '):
            p = line.split(); n = int(p[2])
            team[nid] = 'AB'[int(p[1])]
            body[nid] = collections.deque((int(p[3 + 2 * i]), int(p[4 + 2 * i])) for i in range(n)); nid += 1
    alive = set(body); rnd = 0; actor = -1
    corpse = {}  # cell -> (team, round)
    C = {t: collections.Counter() for t in 'AB'}
    for ev in rep.events:
        w = ev.which()
        if w == 'roundStart':
            rnd = ev.roundStart.round
        elif w == 'turnStart':
            actor = ev.turnStart.id
        elif w == 'dragonUpdate':
            u = ev.dragonUpdate; i = u.id
            if i not in body: continue
            b = body[i]; h = (u.head.x, u.head.y); t = (u.tail.x, u.tail.y)
            if not b or b[0] != h: b.appendleft(h)
            while len(b) > 1 and b[-1] != t: b.pop()
        elif w == 'dragonSplit':
            s = ev.dragonSplit
            team[s.childId] = 'AB'[0 if str(s.team) == 'a' else 1]; alive.add(s.childId)
            body[s.parentId] = collections.deque((p.x, p.y) for p in s.parentBody)
            body[s.childId] = collections.deque((p.x, p.y) for p in s.childBody)
        elif w == 'dragonDeath':
            i = ev.dragonDeath.id; tm = team.get(i)
            if tm and rnd >= frm and body.get(i):
                C[tm]['lost_segments'] += len(body[i])
                for c in body[i]: corpse[c] = (tm, rnd)
            alive.discard(i)
        elif w == 'tileChange':
            tc = ev.tileChange
            if tc.hasPearl: continue
            c = (tc.tile.x, tc.tile.y)
            if c not in corpse: continue
            tm, r0 = corpse.pop(c)
            if rnd - r0 > TTL or actor not in alive: C[tm]['expired_or_unknown'] += 1; continue
            et = team.get(actor)
            if et != tm:
                C[tm]['eaten_by_enemy'] += 1
            else:
                longest = max((j for j in alive if team.get(j) == tm), key=lambda j: len(body.get(j, ())), default=-1)
                C[tm]['eaten_by_own_crown' if actor == longest else 'eaten_by_own_other'] += 1
    for tm, _ in corpse.values():
        C[tm]['never_eaten'] += 1
    return {t: dict(C[t]) for t in 'AB'}


if __name__ == '__main__':
    print(json.dumps(analyse(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 350), indent=1))
