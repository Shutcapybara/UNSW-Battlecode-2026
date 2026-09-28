"""Crown lifecycle from a replay: who assumed the crown (ACT:crown), when, at what
length, max length, how it ended.  Usage: crowns.py REPLAY TEAM"""
import collections, sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
import ystats

rep = ystats.load(sys.argv[1]); team = sys.argv[2]
team_of, body = {}, {}
nid = 0
for line in rep.map.splitlines():
    if line.startswith("DRAGON "):
        p = line.split(); n = int(p[2])
        team_of[nid] = "AB"[int(p[1])]
        body[nid] = collections.deque((int(p[3+2*i]), int(p[4+2*i])) for i in range(n)); nid += 1
crowns = {}; rnd = 0; actor = -1
names = {"hitWall": "wall", "hitSelf": "self", "hitOtherBody": "body", "hitHeadToHead": "h2h", "noValidAction": "noaction"}
for ev in rep.events:
    w = ev.which()
    if w == "roundStart": rnd = ev.roundStart.round
    elif w == "turnStart": actor = ev.turnStart.id
    elif w == "dragonUpdate":
        u = ev.dragonUpdate; b = body.get(u.id)
        if b is None: continue
        h = (u.head.x, u.head.y); t = (u.tail.x, u.tail.y)
        if not b or b[0] != h: b.appendleft(h)
        while len(b) > 1 and b[-1] != t: b.pop()
        if u.id in crowns: crowns[u.id]["max"] = max(crowns[u.id]["max"], len(b))
    elif w == "dragonSplit":
        s = ev.dragonSplit
        team_of[s.childId] = "A" if str(s.team) == "a" else "B"
        body[s.parentId] = collections.deque((p.x, p.y) for p in s.parentBody)
        body[s.childId] = collections.deque((p.x, p.y) for p in s.childBody)
        if s.parentId in crowns: crowns[s.parentId].setdefault("splits", []).append((rnd, len(s.childBody)))
    elif w == "dragonDeath":
        d = ev.dragonDeath
        if d.id in crowns:
            crowns[d.id]["end"] = (rnd, names.get(str(d.reason), str(d.reason)), len(body[d.id]), "self-move" if d.id == actor else "by %d" % actor)
    elif w == "dragonLog":
        lg = ev.dragonLog
        if team_of.get(lg.id) == team and "ACT:crown" in lg.text and lg.id not in crowns:
            crowns[lg.id] = dict(r=rnd, len0=len(body[lg.id]), max=len(body[lg.id]))
for i, c in sorted(crowns.items(), key=lambda kv: kv[1]["r"]):
    print(i, c)
