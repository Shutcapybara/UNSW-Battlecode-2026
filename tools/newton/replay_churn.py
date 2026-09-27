#!/usr/bin/env python3
"""Newborn churn analysis from replays: per-team child lifespan, death causes
by age. Usage: replay_churn.py <replay> [...]"""
import sys, collections
sys.path.insert(0, 'tools/leviathan')
import replay as rp

CAUSES = ['wall','self','body','head-to-head','invalid']

def scan(path):
    r = rp.Reader(path)
    root = r.object(0, 0)
    teams = {}
    for line in root.text(0).splitlines():
        p = line.split()
        if p and p[0] == 'DRAGON':
            teams[len(teams)] = 'AB'[int(p[1])]
    round_num = 0
    splits = []   # (round, parent_id, child_id)
    deaths = []   # (round, id, cause)
    for event in root.items(3):
        kind, obj = event.num(0, 'H'), event.child(0)
        ident = obj.num()
        if kind == 0:
            round_num = ident
        elif kind == 10:
            child = obj.num(4)
            teams.setdefault(child, teams.get(ident, '?'))
            splits.append((round_num, ident, child))
        elif kind == 11:
            deaths.append((round_num, ident, CAUSES[obj.num(4, 'H')]))
    death_by_id = {}
    for rd, i, c in deaths:
        death_by_id.setdefault(i, (rd, c))
    out = {}
    for t in 'AB':
        sp = [(rd, p, c) for rd, p, c in splits if teams.get(c) == t]
        lifespans = []
        causes = collections.Counter()
        for rd, pid, cid in sp:
            d = death_by_id.get(cid)
            life = (d[0] - rd) if d else None
            lifespans.append(life)
            if d:
                causes[(min(life, 30) // 5 * 5, d[1])] += 1
        init = sum(1 for i, tm in teams.items() if tm == t) - len(sp)
        out[t] = dict(initial=init, splits=len(sp), lifespans=lifespans,
                      causes=causes, teams=teams, deaths=deaths, death_by_id=death_by_id)
    return out

if __name__ == '__main__':
    for path in sys.argv[1:]:
        out = scan(path)
        name = path.split('/')[-1].replace('.replay','')
        opp = path.split('/')[-3]
        print(f"== {name} vs {opp}")
        for t in 'AB':
            d = out[t]
            label = 'candidate' if t == 'A' else 'opponent '
            ls_all = d['lifespans']
            ls = [l for l in ls_all if l is not None]
            alive = len(ls_all) - len(ls)
            ls_sorted = sorted(ls)
            med = ls_sorted[len(ls)//2] if ls else 0
            p75 = ls_sorted[int(len(ls)*0.75)] if ls else 0
            tot = sum(min(l, 50) for l in ls) + 50*alive
            byage = collections.Counter()
            for (age, cause), n in d['causes'].items():
                byage[age] += n
            top = sorted(d['causes'].items(), key=lambda kv: -kv[1])[:3]
            # adult (initial dragon) deaths
            adult_deaths = collections.Counter()
            for i, tm in d['teams'].items():
                pass
            print(f"  {t} {label}: initial={d['initial']} splits={len(ls_all)} "
                  f"children-died={len(ls)} children-alive-end={alive} "
                  f"lifespan med={med} p75={p75} rounds-survived-per-split={tot/max(1,len(ls_all)):.1f}")
            print(f"    deaths-by-age-bucket(5r): {dict(sorted(byage.items()))}")
            print(f"    top (age,cause): {top}")
