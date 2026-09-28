"""Per-window team timeline from a replay: units, lengths (sorted), births, deaths by cause, pearls eaten.
usage: timeline.py REPLAY TEAM(A|B) [TO=150] [STEP=10]"""
import collections, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'ouroboros'))
import replaystats as rs
NAMES = {"hitWall": "kelp", "hitSelf": "self", "hitOtherBody": "body", "hitHeadToHead": "h2h", "noValidAction": "noact"}
path, T = sys.argv[1], sys.argv[2]; TO = int(sys.argv[3]) if len(sys.argv) > 3 else 150; ST = int(sys.argv[4]) if len(sys.argv) > 4 else 10
rep = rs.load(path); team, body = {}, {}; nid = 0
for line in rep.map.splitlines():
    if line.startswith('DRAGON '):
        p = line.split(); n = int(p[2]); team[nid] = 'AB'[int(p[1])]
        body[nid] = collections.deque((int(p[3 + 2 * i]), int(p[4 + 2 * i])) for i in range(n)); nid += 1
alive = set(body); rnd = 0; actor = -1
win = collections.Counter(); ate = collections.Counter()
def show():
    for t in 'AB':
        L = sorted((len(body[j]) for j in alive if team[j] == t), reverse=True)
        tag = '*' if t == T else ' '
        print(f"{tag}{t} r{rnd:3d} n{len(L):2d} tot{sum(L):3d} lens{L[:10]} births{win[t,'b']} eat{ate[t]} deaths " + ' '.join(f"{k[1]}:{v}" for k, v in win.items() if k[0] == t and k[1] != 'b'))
    win.clear(); ate.clear()
for ev in rep.events:
    w = ev.which()
    if w == 'roundStart':
        rnd = ev.roundStart.round
        if rnd % ST == 0 and rnd > 0: show()
        if rnd > TO: break
    elif w == 'turnStart': actor = ev.turnStart.id
    elif w == 'dragonUpdate':
        u = ev.dragonUpdate; i = u.id
        if i not in body: continue
        b = body[i]; h = (u.head.x, u.head.y); tl = (u.tail.x, u.tail.y)
        if not b or b[0] != h: b.appendleft(h)
        while len(b) > 1 and b[-1] != tl: b.pop()
    elif w == 'dragonSplit':
        s = ev.dragonSplit; tm = 'AB'[0 if str(s.team) == 'a' else 1]; team[s.childId] = tm; alive.add(s.childId); win[tm, 'b'] += 1
        body[s.parentId] = collections.deque((p.x, p.y) for p in s.parentBody); body[s.childId] = collections.deque((p.x, p.y) for p in s.childBody)
    elif w == 'dragonDeath':
        d = ev.dragonDeath; i = d.id; tm = team.get(i)
        who = 's' if actor == i else ('a' if team.get(actor) == tm else 'e')
        win[tm, NAMES.get(str(d.reason), '?') + '/' + who] += 1; alive.discard(i)
    elif w == 'tileChange':
        if not ev.tileChange.hasPearl and actor in team: ate[team[actor]] += 1
