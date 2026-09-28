"""Closed-loop fixture runner (resumable).  python3 closed_loop.py OUTDIR WORKERS"""
import csv, itertools, json, os, subprocess, sys, time, hashlib, re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
workers = int(sys.argv[2])
L = Path('/home/claude/local')
arms = json.loads(os.environ['ARMS'])
opps = json.loads(os.environ['OPPS'])
maps = sorted((L / 'mapsP').glob('*.map'))
fixtures = []
for mp, opp, arm, side in itertools.product(maps, opps, arms, 'AB'):
    seed = int(hashlib.sha256(f'{mp.name}|{opp}|{side}'.encode()).hexdigest()[:6], 16)  # same seed across arms
    fixtures.append((arm, opp, mp, side, seed))
done = set()
res = out / 'results.csv'
if res.exists():
    done = {(r['arm'], r['opp'], r['map'], r['side']) for r in csv.DictReader(res.open())}


def run(f):
    arm, opp, mp, side, seed = f
    key = (arm, opp, mp.name, side)
    if key in done:
        return None
    a, b = (arm, opp) if side == 'A' else (opp, arm)
    rp = out.resolve() / 'replays' / f'{arm}__{opp}__{mp.stem}__{side}.replay'
    rp.parent.mkdir(exist_ok=True)
    t = time.time()
    p = subprocess.run(['/home/claude/bcenv/bin/unswbc', 'run', str(mp), str(L / 'bots' / a), str(L / 'bots' / b), '-o', str(rp),
                        '--seed', str(seed), '--no-logs', '--no-draw'], capture_output=True, text=True, timeout=1500, cwd=L)
    tail = (p.stdout + p.stderr).strip().splitlines()[-3:]
    m = re.search(r'team (A|B) wins', '\n'.join(tail))
    w = m.group(1) if m else ('draw' if 'draw' in '\n'.join(tail).lower() else 'error')
    return dict(arm=arm, opp=opp, map=mp.name, side=side, seed=seed, winner=w,
                result=('W' if w == side else 'L' if w in 'AB' else w), secs=round(time.time() - t), tail=' | '.join(tail)[-200:])


with ThreadPoolExecutor(workers) as ex:
    for r in ex.map(run, fixtures):
        if r is None:
            continue
        new = not res.exists()
        with res.open('a', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=list(r)); 
            if new: w.writeheader()
            w.writerow(r)
        print(r['arm'], r['opp'], r['map'], r['side'], r['result'], r['secs'], flush=True)
