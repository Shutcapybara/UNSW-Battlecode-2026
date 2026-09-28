"""Newborn survival and crowding at death, per team, from a replay.

For each team: births (splits), deaths of dragons within AGE rounds of birth by
cause, and for self-inflicted deaths (self/body/wall/noaction) the number of
own-team heads within torus distance R of the dying head ("crowding").
usage: newborn.py REPLAY   (import: analyse(path) -> dict)
"""
import collections, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'ouroboros'))
import replaystats as rs
AGE, R = 20, 3
NAMES = {"hitWall": "wall", "hitSelf": "self", "hitOtherBody": "body", "hitHeadToHead": "h2h", "noValidAction": "noaction"}


def analyse(path):
    rep = rs.load(path)
    W, H = map(int, rep.map.splitlines()[0].split()[1:3])
    team, body, born = {}, {}, {}
    nid = 0
    for line in rep.map.splitlines():
        if line.startswith('DRAGON '):
            p = line.split(); n = int(p[2])
            team[nid] = 'AB'[int(p[1])]
            body[nid] = collections.deque((int(p[3 + 2 * i]), int(p[4 + 2 * i])) for i in range(n))
            born[nid] = 0; nid += 1
    T = {t: dict(births=0, young_deaths=collections.Counter(), old_deaths=collections.Counter(),
                 crowd=[], crowd_young=[], lifespans=[]) for t in 'AB'}
    alive = set(body); rnd = 0

    def tdist(a, b):
        dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1]); return min(dx, W - dx) + min(dy, H - dy)
    for ev in rep.events:
        w = ev.which()
        if w == 'roundStart':
            rnd = ev.roundStart.round
        elif w == 'dragonUpdate':
            u = ev.dragonUpdate; i = u.id
            if i not in body: continue
            b = body[i]; h = (u.head.x, u.head.y); t = (u.tail.x, u.tail.y)
            if not b or b[0] != h: b.appendleft(h)
            while len(b) > 1 and b[-1] != t: b.pop()
        elif w == 'dragonSplit':
            s = ev.dragonSplit; tm = 'AB'[0 if str(s.team) == 'a' else 1]
            team[s.childId] = tm; born[s.childId] = rnd; alive.add(s.childId)
            body[s.parentId] = collections.deque((p.x, p.y) for p in s.parentBody)
            body[s.childId] = collections.deque((p.x, p.y) for p in s.childBody)
            T[tm]['births'] += 1
        elif w == 'dragonDeath':
            d = ev.dragonDeath; i = d.id; tm = team.get(i)
            reason = NAMES.get(str(d.reason), str(d.reason))
            if tm:
                age = rnd - born.get(i, 0)
                young = age <= AGE and born.get(i, 0) > 0
                (T[tm]['young_deaths'] if young else T[tm]['old_deaths'])[reason] += 1
                if born.get(i, 0) > 0: T[tm]['lifespans'].append(age)
                if reason in ('self', 'body', 'wall', 'noaction') and body.get(i):
                    h = body[i][0]
                    c = sum(1 for j in alive if j != i and team.get(j) == tm and body.get(j) and tdist(body[j][0], h) <= R)
                    T[tm]['crowd'].append(c)
                    if young: T[tm]['crowd_young'].append(c)
            alive.discard(i)
    out = {}
    for t in 'AB':
        x = T[t]
        ys = sum(v for k, v in x['young_deaths'].items() if k != 'h2h')
        ls = sorted(x['lifespans'])
        out[t] = dict(births=x['births'], young_deaths=dict(x['young_deaths']), old_deaths=dict(x['old_deaths']),
                      young_self_inflicted=ys, young_self_rate=round(ys / max(1, x['births']), 3),
                      median_life=ls[len(ls) // 2] if ls else None,
                      crowd_mean=round(sum(x['crowd']) / max(1, len(x['crowd'])), 2), n_self_deaths=len(x['crowd']),
                      crowd_young_mean=round(sum(x['crowd_young']) / max(1, len(x['crowd_young'])), 2))
    return dict(rounds=rnd + 1, W=W, H=H, teams=out)


if __name__ == '__main__':
    print(json.dumps(analyse(sys.argv[1]), indent=1))
