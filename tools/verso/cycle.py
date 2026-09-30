"""Verso cycle driver: the steps of one cycle as resumable commands (each skips work that is already on disk).

    PY=.venv/bin/python
    $PY tools/verso/cycle.py collect  ARM --seeds 101,102 [--jobs 13]        # data games + dump -> arrays
    $PY tools/verso/cycle.py blob     NAME --bot BOT dir=... q=...           # boosters -> head blob + C++ parity
    $PY tools/verso/cycle.py screen   ARM --parent P [--jobs 13]             # pool seed 1, scored
    $PY tools/verso/cycle.py gate     ARM --parent P [--jobs 13]             # D-032: pool + gen, seeds 1-3
    $PY tools/verso/cycle.py tempo    ARM --parent P [--panels pool,gen]     # S-1's tempo gate on the same fixtures
    $PY tools/verso/cycle.py record   ARM                                     # fidelity transcripts of an arm
    $PY tools/verso/cycle.py fidelity ARM --to PREV_ARM                       # decision agreement with PREV_ARM
    $PY tools/verso/cycle.py table                                            # the status table from the scores

Fidelity between cycles is exact and open-loop: the previous cycle's arm is recorded on a frozen set of games
(tools/cx/golden.py), its inputs are replayed into the new arm, and the share of turns with the same command
(sonar ignored) is reported. Heads are fitted with tools/verso/train_heads.py (its arguments differ per head).
"""
from __future__ import annotations

import argparse, gzip, json, os, re, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C
import lane as L

PY = sys.executable
FID = [('trauma', 'B'), ('schooltime', 'A'), ('portals', 'B'), ('big_empty', 'B')]   # vs yuna-v05-core, seed 1
FID_OPP = 'yuna-v05-core'


def sh(*cmd, env=None):
    print('+', ' '.join(str(c) for c in cmd), flush=True)
    subprocess.run([str(c) for c in cmd], check=True, cwd=C.ROOT, env=env)


def arm_env(arm):
    spec = L.arm_full(arm)
    env = {k: v for k, v in os.environ.items() if not k.startswith('VERSO_')}
    if spec['params']:
        env['VERSO_PARAMS'] = spec['params']
    if spec['policy']:
        env['VERSO_POLICY'] = str((C.ROOT / spec['policy']).resolve())
    return spec, env


def cmd_collect(a):
    sh(PY, 'tools/verso/lane.py', 'run', a.arm, '--panel', 'train', '--seeds', a.seeds, '--jobs', a.jobs, '--dump')
    sh('nice', '-n', '19', PY, 'tools/verso/dataset.py', 'build', a.arm, '--jobs', 8)


def cmd_blob(a):
    out = C.MODELS / a.name / f'policy-{a.bot}.bin'
    sh(PY, 'tools/verso/export.py', 'blob', out, *a.heads, '--bot', a.bot)
    chk = C.MODELS / a.name / 'check.npy'
    if chk.exists():
        import numpy as np
        x = np.load(chk)
        n = len(C.schema(a.bot)[1])
        if x.shape[1] != n:  # probe rows written for an older schema: pad with zeros (parity only needs rows)
            x2 = np.zeros((len(x), n), np.float32); x2[:, :min(n, x.shape[1])] = x[:, :n]
            chk = C.MODELS / a.name / f'check-{a.bot}.npy'
            np.save(chk, x2)
        sh(PY, 'tools/verso/export.py', 'parity', out, *a.heads, '--bot', a.bot, '--x', chk)


def cmd_screen(a):
    sh(PY, 'tools/verso/lane.py', 'run', a.arm, '--panel', 'pool', '--seeds', '1', '--jobs', a.jobs, '--extract')
    (C.B / 'scores').mkdir(exist_ok=True)
    sh(PY, 'tools/verso/lane.py', 'score', a.arm, '--parent', a.parent, '--seeds', '1',
       '--json', C.B / 'scores' / f'{a.arm}--{a.parent}--pool-s1.json')


def cmd_tempo(a):
    """S-1's tempo gate (opening: rounds behind the top-ten net-income curve, r10-150) on the paired fixtures."""
    (C.B / 'scores').mkdir(exist_ok=True)
    for panel in a.panels.split(','):
        cd, pd_ = L.RUNS / a.arm / panel, L.RUNS / a.parent / panel
        if not (cd / 'replays').is_dir() or not (pd_ / 'replays').is_dir():
            print(f'[{panel}] replays missing for {a.arm} or {a.parent}; skipped')
            continue
        p = subprocess.run(['nice', '-n', '19', PY, 'tools/s1/tempo_gate.py', str(cd), str(pd_), '--jobs', '8'],
                           capture_output=True, text=True, cwd=C.ROOT)
        (C.B / 'scores' / f'{a.arm}--{a.parent}--tempo-{panel}.txt').write_text(p.stdout + p.stderr)
        for line in p.stdout.splitlines():
            if line.startswith(('tempo delta', 'VERDICT', '  total length', '  win share')):
                print(f'[{panel}] {line}')


def cmd_gate(a):
    sh(PY, 'tools/verso/lane.py', 'run', a.arm, '--panel', 'both', '--seeds', '1,2,3', '--jobs', a.jobs, '--extract')
    (C.B / 'scores').mkdir(exist_ok=True)
    sh(PY, 'tools/verso/lane.py', 'score', a.arm, '--parent', a.parent, '--seeds', '1,2,3',
       '--json', C.B / 'scores' / f'{a.arm}--{a.parent}--d032.json')


def cmd_record(a):
    spec, env = arm_env(a.arm)
    for m, side in FID:
        out = C.B / 'golden' / f'{m}-{side}-1' / f'{a.arm}.jsonl'
        if out.exists():
            continue
        sh('nice', '-n', '19', PY, 'tools/cx/golden.py', 'record', f'maps/{m}.map', f"bots/{spec['bot']}",
           f'bots/{FID_OPP}', '--side', side, '--seed', '1', '--out', out, env=env)


def cmd_fidelity(a):
    spec, env = arm_env(a.arm)
    exe = C.bot_binary(spec['bot'])
    tot = div = 0
    rows = {}
    for m, side in FID:
        tr = C.B / 'golden' / f'{m}-{side}-1' / f'{a.to}.jsonl'
        if not tr.exists():
            raise SystemExit(f'record {a.to} first ({tr})')
        p = subprocess.run(['nice', '-n', '19', PY, 'tools/cx/golden.py', 'replay', str(tr), exe, '--all',
                            '--ignore-sonar'], capture_output=True, text=True, cwd=C.ROOT, env=env)
        mm = re.search(r'replayed (\d+) turns of \d+ dragons.*?: (\d+) divergent', p.stdout + p.stderr)
        if not mm:
            raise SystemExit(p.stdout[-500:] + p.stderr[-500:])
        t, d = int(mm.group(1)), int(mm.group(2))
        rows[f'{m}-{side}'] = dict(turns=t, divergent=d)
        tot += t; div += d
    res = dict(arm=a.arm, to=a.to, turns=tot, divergent=div, agreement=round(1 - div / tot, 4), games=rows)
    (C.B / 'scores').mkdir(exist_ok=True)
    (C.B / 'scores' / f'{a.arm}--{a.to}--fidelity.json').write_text(json.dumps(res, indent=1))
    print(json.dumps(res))


def cmd_table(a):
    import glob
    print('| Arm | Parent | Seeds | Pool d econ~ [90 %] | Pool d win [90 %] | units@100 | length@100 | Gen d econ~ [90 %] | Gen d win | Verdict |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    for f in sorted(glob.glob(str(C.B / 'scores' / '*.json'))):
        r = json.load(open(f))
        if 'pool' not in r or 'boot' not in r.get('pool', {}):
            continue
        b, g = r['pool']['boot'], r.get('gen', {}).get('boot')
        fmt = lambda v: f'{v[0]:+.3f} [{v[1]:+.3f}, {v[2]:+.3f}]'
        print(f"| `{r['bot']}` | `{r['parent']}` | {','.join(map(str, r['seeds']))} | {fmt(b['econ~'])} | {fmt(b['win'])} | "
              f"{b['units100'][0]:+.3f} | {b['total100'][0]:+.3f} | {fmt(g['econ~']) if g else '—'} | "
              f"{fmt(g['win']) if g else '—'} | {r.get('verdict', '')} |")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('collect'); c.add_argument('arm'); c.add_argument('--seeds', required=True); c.add_argument('--jobs', default='13')
    b = sub.add_parser('blob'); b.add_argument('name'); b.add_argument('heads', nargs='+'); b.add_argument('--bot', required=True)
    for n in ('screen', 'gate'):
        s = sub.add_parser(n); s.add_argument('arm'); s.add_argument('--parent', required=True); s.add_argument('--jobs', default='13')
    t = sub.add_parser('tempo'); t.add_argument('arm'); t.add_argument('--parent', required=True); t.add_argument('--panels', default='pool')
    r = sub.add_parser('record'); r.add_argument('arm')
    f = sub.add_parser('fidelity'); f.add_argument('arm'); f.add_argument('--to', required=True)
    sub.add_parser('table')
    a = ap.parse_args()
    globals()['cmd_' + a.cmd](a)


if __name__ == '__main__':
    main()
