#!/usr/bin/env python3
"""Who initiates head-to-head deaths, by victim age. Usage: h2h_actor.py <replay>"""
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
rnd = 0; born = {}; splits = []; deaths = []
for ev in root.items(3):
    k, o = ev.num(0,'H'), ev.child(0)
    ident = o.num()
    if k == 0: rnd = ident
    elif k == 10:
        teams.setdefault(o.num(4), teams.get(ident,'?'))
        born[o.num(4)] = rnd
        splits.append((rnd, ident, o.num(4)))
    elif k == 11:
        deaths.append((rnd, ident, CAUSES[o.num(4,'H')], None))
# second pass for actor: need turn_id at death time
rnd = 0; turn_id = None; di = 0
deaths2 = []
for ev in root.items(3):
    k, o = ev.num(0,'H'), ev.child(0)
    ident = o.num()
    if k == 0: rnd = ident
    elif k == 1: turn_id = ident
    elif k == 11:
        deaths2.append((rnd, ident, CAUSES[o.num(4,'H')], turn_id))
stats = collections.Counter()
for rnd, ident, cause, actor in deaths2:
    age = rnd - born.get(ident, 0)
    team = teams.get(ident, '?')
    ateam = teams.get(actor, '?') if actor is not None else '?'
    initiator = 'self-ram' if actor == ident else ('enemy-ram' if ateam != team else 'ally-ram')
    stats[(team, cause, initiator, min(age,30)//5*5)] += 1
for k in sorted(stats):
    print(k, stats[k])
