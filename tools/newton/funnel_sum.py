#!/usr/bin/env python3
"""Aggregate Newton SPLITSTAT funnels from /tmp/sinbad-*.log traces.
Usage: funnel_sum.py <ppid>"""
import sys, glob, ast, collections

ppid = sys.argv[1]
tot = collections.Counter()
per = []
for f in glob.glob(f'/tmp/sinbad-{ppid}-A-*.log'):
    last = None
    rounds = 0
    for line in open(f):
        if line.startswith('FUNNEL'):
            last = line
        elif line.startswith('r') and ' act=' in line:
            rounds += 1
    if last:
        d = ast.literal_eval(last.split(' ', 5)[5].strip())
        tot.update(d)
        per.append((f.split('-')[-1][:-4], rounds, d))
print(f"dragons with funnel: {len(per)}")
for me, rounds, d in sorted(per, key=lambda x: -x[1])[:8]:
    print(f"  me={me} turns={rounds} {dict(sorted(d.items()))}")
print("TEAM TOTAL:", dict(sorted(tot.items())))
