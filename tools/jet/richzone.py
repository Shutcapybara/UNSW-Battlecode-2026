"""Rich-zone race: fertile tiles with 0 < maxGap <= 2 x (smallest positive maxGap) form the zone (GAP overrides); per team, first round a head enters,
head-count inside at r30/50/75/100, and pearls eaten inside the zone before r100 / r200.
usage: richzone.py REPLAY [GAP=60]   (import analyse(path, gap))"""
import collections, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'ouroboros'))
import replaystats as rs
SN = (30, 50, 75, 100)
def analyse(path, gap=None):
    rep = rs.load(path); team = {}; nid = 0; zone = set(); head = {}
    lines = rep.map.splitlines(); W, H = map(int, lines[0].split()[1:3])
    tiles = [tuple(map(int, l.split()[1:5])) for l in lines if l.startswith('TILE ')]
    if gap is None: gap = 2 * min(t[3] for t in tiles if t[3] > 0)
    zone = {(x, y) for x, y, a, b in tiles if 0 < b <= gap}
    for line in lines:
        p = line.split()
        if p and p[0] == 'DRAGON': team[nid] = 'AB'[int(p[1])]; head[nid] = (int(p[3]), int(p[4])); nid += 1
    alive = set(head); rnd = 0; actor = -1
    R = {t: dict(first=None, inside={}, eat100=0, eat200=0, eat_all100=0) for t in 'AB'}
    for ev in rep.events:
        w = ev.which()
        if w == 'roundStart':
            rnd = ev.roundStart.round
            if rnd in SN:
                for t in 'AB': R[t]['inside'][rnd] = sum(1 for j in alive if team[j] == t and head[j] in zone)
            if rnd > 200: break
        elif w == 'turnStart': actor = ev.turnStart.id
        elif w == 'dragonUpdate':
            u = ev.dragonUpdate; head[u.id] = (u.head.x, u.head.y)
            t = team.get(u.id)
            if t and head[u.id] in zone and R[t]['first'] is None: R[t]['first'] = rnd
        elif w == 'dragonSplit':
            s = ev.dragonSplit; team[s.childId] = 'AB'[0 if str(s.team) == 'a' else 1]; alive.add(s.childId)
            head[s.childId] = (s.childBody[0].x, s.childBody[0].y); head[s.parentId] = (s.parentBody[0].x, s.parentBody[0].y)
        elif w == 'dragonDeath': alive.discard(ev.dragonDeath.id)
        elif w == 'tileChange' and not ev.tileChange.hasPearl and actor in team:
            c = (ev.tileChange.tile.x, ev.tileChange.tile.y); t = team[actor]
            if rnd < 100: R[t]['eat_all100'] += 1
            if c in zone:
                if rnd < 100: R[t]['eat100'] += 1
                R[t]['eat200'] += 1
    return dict(zone=len(zone), gap=gap, teams=R)
if __name__ == '__main__':
    print(json.dumps(analyse(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else None)))
