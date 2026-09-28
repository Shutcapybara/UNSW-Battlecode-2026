"""Crown survival: the longest own dragon at round R0 — does it survive to the end, and how?"""
import collections, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'ouroboros'))
import replaystats as rs
NAMES = {"hitWall": "wall", "hitSelf": "self", "hitOtherBody": "body", "hitHeadToHead": "h2h", "noValidAction": "noaction"}

def analyse(path, r0=400):
    rep = rs.load(path); team, body = {}, {}; nid = 0
    for line in rep.map.splitlines():
        if line.startswith('DRAGON '):
            p = line.split(); n = int(p[2]); team[nid] = 'AB'[int(p[1])]
            body[nid] = collections.deque((int(p[3+2*i]), int(p[4+2*i])) for i in range(n)); nid += 1
    alive = set(body); rnd = 0; crown = {}; out = {}
    for ev in rep.events:
        w = ev.which()
        if w == 'roundStart':
            rnd = ev.roundStart.round
            if rnd == r0 and not crown:
                for t in 'AB':
                    ids = [j for j in alive if team.get(j) == t]
                    if ids: crown[t] = max(ids, key=lambda j: len(body[j]))
                    out[t] = dict(len_r0=len(body[crown[t]]) if t in crown else 0, died=None, died_round=None)
        elif w == 'dragonUpdate':
            u = ev.dragonUpdate; i = u.id
            if i not in body: continue
            b = body[i]; h = (u.head.x, u.head.y); tl = (u.tail.x, u.tail.y)
            if not b or b[0] != h: b.appendleft(h)
            while len(b) > 1 and b[-1] != tl: b.pop()
        elif w == 'dragonSplit':
            s = ev.dragonSplit; team[s.childId] = 'AB'[0 if str(s.team) == 'a' else 1]; alive.add(s.childId)
            body[s.parentId] = collections.deque((p.x, p.y) for p in s.parentBody)
            body[s.childId] = collections.deque((p.x, p.y) for p in s.childBody)
        elif w == 'dragonDeath':
            i = ev.dragonDeath.id
            for t, c in crown.items():
                if c == i and out[t]['died'] is None:
                    out[t]['died'] = NAMES.get(str(ev.dragonDeath.reason), str(ev.dragonDeath.reason)); out[t]['died_round'] = rnd; out[t]['len_at_death'] = len(body[i])
            alive.discard(i)
    for t, c in crown.items():
        if out[t]['died'] is None: out[t]['len_end'] = len(body[c])
    return out

if __name__ == '__main__':
    print(json.dumps(analyse(sys.argv[1]), indent=1))
