#!/usr/bin/env python3
"""Obscur (H-1) runner: tools/verso/lane.py unchanged (panels, D-032 gate), with outputs under build/obscur/ and one
addition — an arm's params may carry SF-1 state weights as `M:<key>=<v>` items, passed to the bot as MAELLE_PARAMS
(e.g. `M:wt_ally=-1.4`); every other item goes to VERSO_PARAMS as in Verso (`p.<knob>=v` sets a base knob).

    PY=.venv/bin/python
    $PY tools/obscur/lane.py arm NAME BOT --params "p.threat_weight=0.5"
    $PY tools/obscur/lane.py run ARM --panel both --seeds 1,2,3 --jobs 8 --extract
    $PY tools/obscur/lane.py score ARM --parent verso-05-hb800-prior --seeds 1,2,3 --json OUT
"""
import os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('VERSO_NICE', '19')
import tools.verso.lane as L  # noqa: E402

L.RUNS = ROOT / 'build/obscur/runs'
L.DUMPS = ROOT / 'build/obscur/dumps'
L.ARMS = ROOT / 'build/obscur/arms.json'

_run_one = L.run_one


def run_one(fx, root, spec, dump=None):
    items = [x for x in spec['params'].split(',') if x]
    m = [x[2:] for x in items if x.startswith('M:')]
    v = [x for x in items if not x.startswith('M:')]
    if m:
        os.environ['OBSCUR_MAELLE'] = ','.join(m)
    spec = dict(spec, params=','.join(v))
    return _run_one(fx, root, spec, dump)


L.run_one = run_one
_sp_run = L.subprocess.run


def sp_run(cmd, *a, **k):
    env = k.get('env')
    if env is not None and os.environ.get('OBSCUR_MAELLE'):
        env['MAELLE_PARAMS'] = os.environ['OBSCUR_MAELLE']
    if k.get('timeout') == 1800:  # shared host: heavy Python opponents exceed 30 min under load
        k['timeout'] = int(os.environ.get('OBSCUR_GAME_TIMEOUT', '7200'))
    return _sp_run(cmd, *a, **k)


L.subprocess.run = sp_run

if __name__ == '__main__':
    L.main()
