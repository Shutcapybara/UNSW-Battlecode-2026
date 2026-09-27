#!/usr/bin/env python3
"""Death/unit timeline from a replay, per team. Usage: timeline.py <replay>"""
import sys, collections
sys.path.insert(0, 'tools/leviathan')
import replay as rp
CAUSES = ['wall','self','body','head-to-head','invalid']
r = rp.Reader(sys.argv[1]); root = r.object(0,0)
teams = {}
for line in root.text(0).splitlines():
    p = line.split()
    if p and p[0] == 'DRAGON':
        teams[len(teams)] = 'AB'[int(p[1])]
rnd = 0; turn_id = None
events = []
live = collections.Counter()
for t in teams.values(): live[t] += 1 if t else 0
alive = {i for i in teams}
for ev in root.items(3):
    k, o = ev.num(0,'H'), ev.child(0)
    ident = o.num()
    if k == 0: rnd = ident
    elif k == 1: turn_id = ident
    elif k == 10:
        teams.setdefault(o.num(4), teams.get(ident,'?'))
        alive.add(o.num(4))
    elif k == 11:
        cause = CAUSES[o.num(4,'H')]
        victim_team = teams.get(ident,'?')
        actor_team = teams.get(turn_id,'?') if turn_id is not None else '?'
        events.append((rnd, victim_team, cause, ident == turn_id, actor_team))
        alive.discard(ident)
buckets = collections.defaultdict(lambda: collections.Counter())
unitcurve = {}
for rnd, vt, cause, selfram, at in events:
    b = rnd // 25
    buckets[(vt, b)][cause if selfram else cause+'(enemy)' if at != vt else cause] += 1
print("round-bucket: team deaths by cause [self-ram merged; (enemy)=enemy initiated]")
for (vt, b) in sorted(buckets):
    print(f"  r{b*25:3d}-{b*25+24:3d} team {vt}: {dict(buckets[(vt,b)])}")
# unit curve every 50 rounds
print("units curve (from death/split events):")
# recompute population over time
pop = {t: 0 for t in 'AB'}
counts = collections.Counter(teams.values())
cur = dict(counts)
pop_curve = []
last_r = 0
i = 0
for rnd, vt, cause, sr, at in events:
    while last_r < rnd:
        if last_r % 50 == 0:
            pop_curve.append((last_r, dict(cur)))
        last_r += 1
    cur[vt] -= 1
while last_r <= 500:
    if last_r % 50 == 0:
        pop_curve.append((last_r, dict(cur)))
    last_r += 1
print('  ' + ' '.join(f"r{r}:A{c['A']}/B{c['B']}" for r, c in pop_curve))
