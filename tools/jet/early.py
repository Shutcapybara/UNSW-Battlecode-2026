"""Early-game survival anatomy per team from a replay (live-loss question: eliminations before r200).

For each team: units and total length at r50/100/150/200, elimination round (None if alive at end),
deaths before round CUT by cause x mover ('self' = the dying dragon moved, 'ally' = another own
dragon moved, 'enemy' = an enemy moved), age at death, dying length, whether the dying head was
within 2 of a portal endpoint, and friendly head-on counts (h2h deaths where both dragons are
the same team).
usage: early.py REPLAY [CUT]   (import: analyse(path, cut) -> dict)
"""
import collections, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'ouroboros'))
import replaystats as rs
NAMES = {"hitWall": "wall", "hitSelf": "self", "hitOtherBody": "body", "hitHeadToHead": "h2h", "noValidAction": "noaction"}
SNAP = (50, 100, 150, 200)


def analyse(path, cut=200):
    rep = rs.load(path)
    lines = rep.map.splitlines()
    W, H = map(int, lines[0].split()[1:3])
    team, body, born = {}, {}, {}
    portal = set()
    nid = 0
    for line in lines:
        p = line.split()
        if not p: continue
        if p[0] == 'DRAGON':
            n = int(p[2]); team[nid] = 'AB'[int(p[1])]
            body[nid] = collections.deque((int(p[3 + 2 * i]), int(p[4 + 2 * i])) for i in range(n)); born[nid] = 0; nid += 1
        elif p[0] == 'EDGE' and len(p) == 4 and p[2] == '2':  # EDGE idx kind(1 kelp, 2 portal) pid
            idx = int(p[1]); col, row = idx % (W + 1), idx // (W + 1)
            if row % 2 == 0: portal.update({(col % W, (row // 2) % H), (col % W, (row // 2 - 1) % H)})
            else: portal.update({(col % W, ((row - 1) // 2) % H), ((col - 1) % W, ((row - 1) // 2) % H)})

    def near_portal(h):
        for (x, y) in portal:
            dx = abs(x - h[0]); dy = abs(y - h[1])
            if min(dx, W - dx) + min(dy, H - dy) <= 2: return True
        return False
    alive = set(body); rnd = 0; actor = -1; pend = []
    T = {t: dict(deaths=collections.Counter(), ages=[], lens=[], portal=0, friendly_h2h=0, elim=None, snap={}) for t in 'AB'}

    def snapshot(r):
        for t in 'AB':
            ids = [j for j in alive if team.get(j) == t]
            T[t]['snap'][r] = (len(ids), sum(len(body[j]) for j in ids))
    for ev in rep.events:
        w = ev.which()
        if w == 'roundStart':
            rnd = ev.roundStart.round
            if rnd in SNAP: snapshot(rnd)
        elif w == 'turnStart':
            actor = ev.turnStart.id; pend = []
        elif w == 'dragonUpdate':
            u = ev.dragonUpdate; i = u.id
            if i not in body: continue
            b = body[i]; h = (u.head.x, u.head.y); tl = (u.tail.x, u.tail.y)
            if not b or b[0] != h: b.appendleft(h)
            while len(b) > 1 and b[-1] != tl: b.pop()
        elif w == 'dragonSplit':
            s = ev.dragonSplit; tm = 'AB'[0 if str(s.team) == 'a' else 1]
            team[s.childId] = tm; born[s.childId] = rnd; alive.add(s.childId)
            body[s.parentId] = collections.deque((p.x, p.y) for p in s.parentBody)
            body[s.childId] = collections.deque((p.x, p.y) for p in s.childBody)
        elif w == 'dragonDeath':
            d = ev.dragonDeath; i = d.id; tm = team.get(i)
            reason = NAMES.get(str(d.reason), str(d.reason))
            if tm and rnd < cut:
                mover = 'self' if actor == i else ('ally' if team.get(actor) == tm else 'enemy')
                x = T[tm]; x['deaths'][f'{reason}/{mover}'] += 1
                x['ages'].append(rnd - born.get(i, 0)); x['lens'].append(len(body.get(i, ())))
                if body.get(i) and near_portal(body[i][0]): x['portal'] += 1
                if reason == 'h2h':
                    if any(team.get(j) == tm for j, r_ in pend if r_ == 'h2h' and j != i): x['friendly_h2h'] += 1
            pend.append((i, reason))
            alive.discard(i)
            if tm and not any(team.get(j) == tm for j in alive) and T[tm]['elim'] is None: T[tm]['elim'] = rnd
    out = {}
    for t in 'AB':
        x = T[t]; a = sorted(x['ages'])
        out[t] = dict(elim=x['elim'], snap={r: x['snap'].get(r, (0, 0)) for r in SNAP}, n_early_deaths=len(a),
                      deaths=dict(x['deaths']), median_age=a[len(a) // 2] if a else None,
                      median_len=sorted(x['lens'])[len(a) // 2] if a else None,
                      near_portal=x['portal'], friendly_h2h=x['friendly_h2h'])
    return dict(rounds=rnd + 1, W=W, H=H, n_portal_tiles=len(portal), teams=out)


if __name__ == '__main__':
    print(json.dumps(analyse(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 200), indent=1))
