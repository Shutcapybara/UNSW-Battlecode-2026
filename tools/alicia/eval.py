#!/usr/bin/env python3
"""Alicia (RL-1) checkpoint -> bot directory -> D-032 scorecard. The scoring is tools/rc/lane.py (copied verbatim
from r/rc), so the lane and this one call the same gate code.

    python3 tools/alicia/eval.py make   CKPT.json alicia-03-es-curve-pool --mechanism "..." [--parent alicia-02-tunable]
    python3 tools/alicia/eval.py parity alicia-03-es-curve-pool      # learned part disabled == parent (golden)
    python3 tools/alicia/eval.py panels alicia-03-es-curve-pool [--jobs 14]  # D-032 pool + gen, seeds 1-3
    python3 tools/alicia/eval.py score  alicia-03-es-curve-pool [--parent alicia-01-nodevil]
    python3 tools/alicia/eval.py cpu    alicia-03-es-curve-pool

`make` bakes the checkpoint's parameters into params.hpp as the compiled-in defaults (tune.hpp stays, so
ALICIA_PARAMS set to the parent's values restores the parent exactly: that is the `parity` check).
"""
from __future__ import annotations

import argparse, glob, hashlib, json, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PY = sys.executable
GOLDEN = ROOT / 'build/alicia/golden'


def fingerprint(d):
    h = hashlib.sha256()
    for p in sorted(Path(d).iterdir()):
        if p.suffix in ('.cpp', '.hpp') or p.name == 'bot.toml':
            h.update(p.name.encode() + b'\0' + p.read_bytes() + b'\0')
    return h.hexdigest()


def param_values(bot):
    txt = (ROOT / 'bots' / bot / 'params.hpp').read_text()
    return {m.group(2): m.group(3) for m in re.finditer(r'static (?:inline|constexpr) (double|int) (\w+) = ([^;]+);', txt)}


def cmd_make(a):
    ck = json.loads(Path(a.ckpt).read_text())
    params = ck['params']
    src, dst = ROOT / 'bots' / a.parent, ROOT / 'bots' / a.name
    if dst.exists():
        sys.exit(f'{dst} exists; bot snapshots are immutable')
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns('.unswbc-build', 'CANDIDATE.toml', 'README.md'))
    p = dst / 'params.hpp'
    txt = p.read_text()
    old = param_values(a.parent)
    for k, v in params.items():
        pat = re.compile(rf'(static inline (double|int) {k} = )([^;]+);')
        m = pat.search(txt)
        if not m:
            sys.exit(f'{k} is not a tunable field of {a.parent}')
        lit = str(int(v)) if m.group(2) == 'int' else repr(float(v))
        txt = pat.sub(lambda mm: f'{mm.group(1)}{lit}; // {a.name} (ES {ck["run"]} g{ck["gen"]}; was {old[k]})', txt, count=1)
    p.write_text(txt)
    diff = {k: [old[k], params[k]] for k in sorted(params)}
    (dst / 'CANDIDATE.toml').write_text(
        f'name = "{a.name}"\nlineage = "alicia"\nlane = "rl-1"\nauthor = "claude-opus-5.5/alicia"\nlanguage = "c++"\n'
        f'lineage_parent = "{a.lineage_parent}"\n'
        f'hypothesis = "L16/L04: a jointly learned Ares weight vector (ES on the benchmark-curve reward) beats the hand weights"\n'
        f'mechanism = "{a.mechanism}"\n'
        f'expected_change = "{a.expect}"\npriority = 0\nsupersedes = ""\nstatus = "candidate (not registered)"\n'
        f'fingerprint = "{fingerprint(dst)}"\n\n[training]\nrun = "{ck["run"]}"\nstage = {ck["stage"]}\ngeneration = {ck["gen"]}\n'
        f'checkpoint = "build/alicia/train/{ck["run"]}/ckpt-g{ck["gen"]:02d}.json"\n\n[params]\n'
        + ''.join(f'{k} = {json.dumps(v[1])}  # was {v[0]}\n' for k, v in diff.items())
        + '\n[activation_contract]\nkind = "legacy_none"\n'
          'note = "params-only change (compiled-in defaults); ALICIA_PARAMS is read only in local games"\n')
    (dst / 'README.md').write_text(f'# {a.name}\n\nAlicia (RL-1). {a.mechanism}\n\nParent `{a.parent}` behaviour '
                                   f'is restored exactly by `ALICIA_PARAMS` = the parent values below (golden-checked '
                                   f'by `tools/alicia/eval.py parity`).\n\n| param | parent | this bot |\n|---|---:|---:|\n'
                                   + ''.join(f'| `{k}` | {v[0]} | {v[1]} |\n' for k, v in diff.items()))
    print(f'wrote {dst} ({len(params)} parameters changed)')


def cmd_parity(a):
    """the learned part disabled (ALICIA_PARAMS = parent values) must replay the parent's golden transcripts exactly."""
    old, new = param_values(a.parent), param_values(a.bot)
    changed = {k: old[k] for k in new if new[k] != old.get(k)}
    env = dict(os.environ, ALICIA_PARAMS=';'.join(f'{k}={v}' for k, v in changed.items()))
    bad = 0
    for t in sorted(glob.glob(str(GOLDEN / '*'))):
        r = subprocess.run([PY, 'tools/cx/golden.py', 'replay', t, f'bots/{a.bot}'], cwd=ROOT, env=env,
                           capture_output=True, text=True)
        print(Path(t).name, (r.stdout + r.stderr).strip().splitlines()[-1])
        bad += r.returncode != 0
    print('PARITY', 'OK' if not bad else f'FAILED on {bad} transcripts', f'({len(changed)} params reset)')
    return 1 if bad else 0


def cmd_panels(a):
    subprocess.run([PY, 'tools/rc/lane.py', 'run', a.bot, '--panel', 'both', '--seeds', a.seeds,
                    '--jobs', str(a.jobs), '--extract'], cwd=ROOT, check=True)


def cmd_score(a):
    args = [PY, 'tools/rc/lane.py', 'score', a.bot, '--parent', a.parent, '--seeds', a.seeds]
    if a.json:
        args += ['--json', a.json]
    subprocess.run(args, cwd=ROOT, check=True)


def cmd_cpu(a):
    subprocess.run([PY, 'tools/rc/lane.py', 'cpu', a.bot, '--wall', '100'], cwd=ROOT, check=True)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    m = sub.add_parser('make'); m.add_argument('ckpt'); m.add_argument('name')
    m.add_argument('--parent', default='alicia-02-tunable', help='source directory to copy')
    m.add_argument('--lineage-parent', default='alicia-01-nodevil', help='the behavioural parent (gate baseline)')
    m.add_argument('--mechanism', required=True); m.add_argument('--expect', default='')
    p = sub.add_parser('parity'); p.add_argument('bot'); p.add_argument('--parent', default='alicia-02-tunable')
    r = sub.add_parser('panels'); r.add_argument('bot'); r.add_argument('--seeds', default='1,2,3')
    r.add_argument('--jobs', type=int, default=max(1, (os.cpu_count() or 4) - 2))
    s = sub.add_parser('score'); s.add_argument('bot'); s.add_argument('--parent', default='alicia-01-nodevil')
    s.add_argument('--seeds', default='1,2,3'); s.add_argument('--json')
    c = sub.add_parser('cpu'); c.add_argument('bot')
    a = ap.parse_args()
    sys.exit({'make': cmd_make, 'parity': cmd_parity, 'panels': cmd_panels, 'score': cmd_score, 'cpu': cmd_cpu}[a.cmd](a) or 0)


if __name__ == '__main__':
    main()
