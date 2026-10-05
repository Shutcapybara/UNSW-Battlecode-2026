"""Synthetic check of r2_battery.py rev 8 (inventory file, D-066 §C). Invented data only. Run from a scratch dir holding
tools/hinata/{r2_battery.py,r2_bc.py,r2_inventory.json,r2_battery_rev6_synth.py}. Equivalence: rev 8 with an inventory equal to
rev 7's constants reproduces r2_battery_rev7_synth.py's output line for line (run that synth with R2_INVENTORY=<rev7 inventory>).
Expected here (default inventory):
  j  all pooled arms at .80, A8b-A1-400 at .90, A4-400 at 1.00 -> A4-400 role descriptive; selected A8b-A1-400; inventory complete
  k  same without A8b-A3-400                                    -> pooled_missing ['A8b-A3-400'], passes False
  l  cols('A6') / cols('A7') use ts_base's inputs (A1 -> the hb_f_ list)"""
import json, sys, subprocess, shutil, types
from pathlib import Path
S6 = types.SimpleNamespace(); _ns = {'__name__': 'rev6_helpers'}
exec((Path(__file__).parent / 'r2_battery_rev6_synth.py').read_text().split('\na0dir()\n')[0], _ns)
for _k in ('A0', 'n', 'P_of', 'mk', 'a0dir'):
    setattr(S6, _k, _ns[_k])
S6.reset = lambda: shutil.rmtree('runs', ignore_errors=True)
S6.A0['fold'] = ['f%d' % ((i // 10) % 5) for i in range(S6.n)]; S6.a0dir(); y = S6.A0.y_first.to_numpy()
def base(skip=()):
    S6.reset()
    for x in ('A1', 'A3'):
        S6.mk(x, S6.A0, {f'{x}-400': S6.P_of(y, .8), f'{x}-800': S6.P_of(y, .8)}, {})
    S6.mk('A10', S6.A0, {'A10-e4': S6.P_of(y, .8)}, {}); S6.mk('A10b', S6.A0, {'A10b': S6.P_of(y, .8)}, {})
    for k, acc in (('A8b-A1-400', .9), ('A8b-A3-400', .8)):
        if k not in skip:
            S6.mk(k, S6.A0, {k: S6.P_of(y, acc)}, {})
    S6.mk('A4', S6.A0, {'A4-400': S6.P_of(y, 1.0)}, {})
def run(case):
    r = subprocess.run(['python3', 'tools/hinata/r2_battery.py', 'table', '--runs', 'runs', '--a0', 'a0', '--out', 'o.json'], capture_output=True, text=True)
    if r.returncode:
        print(f'== {case}: REFUSED :: {(r.stdout + r.stderr).strip().splitlines()[-1][:160]}'); return
    t = json.load(open('o.json')); s = t['selection']; roles = {x['arm']: x['role'] for x in t['rows'] if x['arm'].startswith(('A4', 'A8b'))}
    print(f"== {case}: selected {s['selected']} pooled_missing {s['pooled_missing']} passes_inventory {not s['pooled_missing']} roles {roles}")
base(); run('j A4 at 1.00 descriptive')
base(skip=('A8b-A3-400',)); run('k A8b-A3-400 missing')
sys.path.insert(0, 'tools/hinata'); import r2_battery as B
print('== l cols A6', B.cols('A6', ['e1'], ['hb_f_a'])[:2], 'A7', B.cols('A7', ['e1'], ['hb_f_a']), 'ts_base', B.TS_BASE)
