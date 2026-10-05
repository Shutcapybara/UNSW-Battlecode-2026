"""Synthetic check of r2_battery.py rev 7 (Tanaka 22:25Z: full-data A10b missing from POOLED/PLANNED). Invented data only
(100 rows, 4 teams, 10 series); no real outputs read. Reuses the rev 6 synth's A0 and helpers. Run from a scratch dir holding
tools/hinata/{r2_battery.py,r2_bc.py,r2_battery_rev6_synth.py}. Expected:
  a  complete old inventory at .80 + A10b at 1.00 -> selected A10b, A10b pooled, passes inventory (pooled_missing [])
  b  same without A10b                            -> pooled_missing ['A10b'], note INCOMPLETE, passes False
  c  A10b-f25 at 1.00 instead of A10b             -> A10b-f25 role descriptive, not pooled, not selected; pooled_missing ['A10b']
  d  an undeclared name 'A10b-f75'                -> REFUSED
  e  an undeclared size 'A3-200'                  -> REFUSED
 D-064 §C (teacher-specific): teams by rating 1,2,3,0; A2 team 0 is made best (1.00), others .90; A6 .90
  f  A2+A6 inventory, cohort counts {0: 6, 1: 12, 2: 12, 3: 12}  -> best is an eligible team (not team 0), goes_forward True
  g  same, cohort counts {0: 12, ...}                           -> best A2-400[team 0], goes_forward True
  h  same, no --cohort-series                                   -> goes_forward False, ts_missing names the counts
  i  A7/A7fix only (full support)                               -> no teacher-specific candidate; A7fix role descriptive"""
import json, sys, subprocess, shutil, io, contextlib
from pathlib import Path
sys.argv = ['x']
import types   # take only the rev 6 synth's helpers (A0, P_of, mk, a0dir); its cases encode rev 6 rules and are not run
S6 = types.SimpleNamespace(); _ns = {'__name__': 'rev6_helpers'}
exec((Path(__file__).parent / 'r2_battery_rev6_synth.py').read_text().split('\na0dir()\n')[0], _ns)
for _k in ('A0', 'n', 'P_of', 'mk', 'a0dir'):
    setattr(S6, _k, _ns[_k])
S6.reset = lambda: shutil.rmtree('runs', ignore_errors=True)
S6.A0['fold'] = ['f%d' % ((i // 10) % 5) for i in range(S6.n)]; S6.a0dir(); y = S6.A0.y_first.to_numpy()
def base(with_a10b=True, extra=None):
    S6.reset()
    for x in ('A1', 'A3', 'A4', 'A5'):
        S6.mk(x, S6.A0, {f'{x}-400': S6.P_of(y, .8), f'{x}-800': S6.P_of(y, .8)}, {})
    S6.mk('A10', S6.A0, {'A10-e4': S6.P_of(y, .8)}, {})
    if with_a10b:
        S6.mk('A10b', S6.A0, {'A10b': S6.P_of(y, 1.0)}, {}, mb={'A10b': 5})
    for k, v in (extra or {}).items():
        S6.mk(k, S6.A0, {k: S6.P_of(y, 1.0)}, {})
def run(case, extra=()):
    r = subprocess.run(['python3', 'tools/hinata/r2_battery.py', 'table', '--runs', 'runs', '--a0', 'a0', '--out', 'o.json', *extra], capture_output=True, text=True)
    if r.returncode:
        print(f'== {case}: REFUSED :: {(r.stdout + r.stderr).strip().splitlines()[-1][:160]}'); return
    t = json.load(open('o.json')); s = t['selection']; roles = {x['arm']: x['role'] for x in t['rows'] if x['arm'].startswith('A10')}
    print(f"== {case}: selected {s['selected']} pooled_missing {s['pooled_missing']} passes {s['passes']} note {s.get('note')} roles {roles}")
base(); run('a complete + A10b 1.00')
base(False); run('b A10b missing')
base(False, {'A10b-f25': 1}); run('c f25 1.00, no A10b')
base(True, {'A10b-f75': 1}); run('d undeclared A10b-f75')
base(True, {'A3-200': 1}); run('e undeclared A3-200')

import numpy as np
def P_team0(acc0, acc):
    P = S6.P_of(y, acc); m = (S6.A0.team == '0').to_numpy(); P[m] = S6.P_of(y[m], acc0); return P
def ts_base():
    S6.reset(); s6 = S6.A0[S6.A0.team.isin(['1', '2', '3'])]
    S6.mk('A2', S6.A0, {'A2-400': P_team0(1.0, .9), 'A2-800': P_team0(1.0, .9)}, {})
    S6.mk('A6', s6, {'A6-400': S6.P_of(s6.y_first.to_numpy(), .9), 'A6-800': S6.P_of(s6.y_first.to_numpy(), .9)}, dict(teams_top3=['1', '2', '3']))
def tsrun(case, extra=()):
    r = subprocess.run(['python3', 'tools/hinata/r2_battery.py', 'table', '--runs', 'runs', '--a0', 'a0', '--out', 'o.json', *extra], capture_output=True, text=True)
    if r.returncode:
        print(f'== {case}: REFUSED :: {(r.stdout + r.stderr).strip().splitlines()[-1][:160]}'); return
    t = json.load(open('o.json')); s = t['teacher_specific']['selection']; roles = {x['arm']: x['role'] for x in t['rows']}
    print(f"== {case}: best {s and s['best']['cand']} goes_forward {s and s['goes_forward']} ts_missing {s and s['ts_missing']} roles {roles}")
Path('cs_a.json').write_text(json.dumps({'0': 6, '1': 12, '2': 12, '3': 12})); Path('cs_b.json').write_text(json.dumps({'0': 12, '1': 12, '2': 12, '3': 12}))
ts_base(); tsrun('f team 0 has 6 cohort series', ['--cohort-series', 'cs_a.json'])
ts_base(); tsrun('g team 0 has 12 cohort series', ['--cohort-series', 'cs_b.json'])
ts_base(); tsrun('h no cohort counts')
S6.reset(); S6.mk('A7', S6.A0, {'A7-400': S6.P_of(y, .9), 'A7fix-400': S6.P_of(y, 1.0)}, dict(teams_top3=['1', '2', '3'])); tsrun('i A7/A7fix only')
