"""Seeded zoo panel runner (F1 feature lab).

python -m tools.analysis.features.run_panel --panel z1 --jobs 2 [--unswbc PATH]
Round robin of ZOO on LIVE_MAPS, both sides, seed 1; plus seeds 2-3 for STABILITY_PAIRS.
Resumable: skips games whose replay already exists; appends to build/zoo/<panel>/index.jsonl.
"""
import argparse, itertools, json, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ZOO = ['fenrir-v18-arrival-ready-beds', 'yuna-v05-core', 'chaewon-y04-probe', 'sinbad-v07-divecap',
       'gavroche-v32-supported-divecap', 'ouroboros-m01-vibing-mimic', 'kazuha-s01-swarm-dissolve',
       'hunter-v20-portal-scouts']
LIVE_MAPS = ['schooltime', 'portals', 'slithery_fight', 'queen_of_spades', 'default', 'trophy', 'dilemma',
             'autarky', 'devil', 'trauma']
STABILITY_PAIRS = [('fenrir-v18-arrival-ready-beds', 'hunter-v20-portal-scouts'),
                   ('yuna-v05-core', 'sinbad-v07-divecap'),
                   ('gavroche-v32-supported-divecap', 'kazuha-s01-swarm-dissolve'),
                   ('chaewon-y04-probe', 'ouroboros-m01-vibing-mimic')]
RESULT = re.compile(r'team (A|B) wins after (\d+) rounds \(([^)]*)\)')

def fixtures():
    out = []
    for seed, pairs in ((1, list(itertools.combinations(ZOO, 2))), (2, STABILITY_PAIRS), (3, STABILITY_PAIRS)):
        for a, b in pairs:
            for m in LIVE_MAPS:
                for x, y in ((a, b), (b, a)):
                    out.append(dict(map=m, seed=seed, botA=x, botB=y, game=f's{seed}__{m}__{x}__{y}'))
    return out

def run(fx, root, exe, version, no_logs=False):
    rep = root / 'replays' / (fx['game'] + '.replay')
    if rep.exists():
        return None
    t = time.time()
    p = subprocess.run([exe, 'run', '--seed', str(fx['seed'])] + (['--no-logs'] if no_logs else []) + ['--no-indicator', '--no-draw', '-o', str(rep) + '.tmp',
                        f"maps/{fx['map']}.map", f"bots/{fx['botA']}", f"bots/{fx['botB']}"], capture_output=True, text=True, timeout=1800)
    out = p.stdout + p.stderr
    m = RESULT.search(out)
    row = dict(fx, toolkit=version, sandbox=False, logs=not no_logs, host=os.uname().nodename, seconds=round(time.time() - t, 1), rc=p.returncode,
               winner=m.group(1) if m else ('draw' if 'draw' in out.lower() else None),
               rounds=int(m.group(2)) if m else None, reason=m.group(3) if m else out.strip().splitlines()[-1][:200] if out.strip() else '')
    if os.path.exists(str(rep) + '.tmp'):
        os.replace(str(rep) + '.tmp', rep)
    row['replay'] = str(rep.relative_to(root))
    return row

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--panel', default='z1'); ap.add_argument('--jobs', type=int, default=2)
    ap.add_argument('--unswbc', default='unswbc')
    ap.add_argument('--shards', default=None, help='comma list of shard ids to run, with --of N (fixture index mod N)')
    ap.add_argument('--of', type=int, default=1)
    ap.add_argument('--skip', default=None, help='file of game ids already run elsewhere')
    ap.add_argument('--reverse', action='store_true', help='run the shard from the end (to meet another host in the middle)')
    ap.add_argument('--no-logs', action='store_true', help='keep LOG lines out of the replay (features do not use them)')
    ap.add_argument('--out', default=None, help='replay root (default build/zoo/<panel>)')
    a = ap.parse_args()
    root = Path(a.out) if a.out else Path('build/zoo') / a.panel; (root / 'replays').mkdir(parents=True, exist_ok=True)
    version = subprocess.run([a.unswbc, '--version'], capture_output=True, text=True).stdout.strip()
    fx = fixtures()
    if a.shards is not None:
        keep = {int(x) for x in a.shards.split(',')}
        fx = [f for i, f in enumerate(fx) if i % a.of in keep]
    skip = set(open(a.skip).read().split()) if a.skip else set()
    todo = [f for f in fx if f['game'] not in skip and not (root / 'replays' / (f['game'] + '.replay')).exists()]
    if a.reverse:
        todo = todo[::-1]
    print(f'{len(fx)} fixtures, {len(todo)} to run, {version}', flush=True)
    with open(root / 'index.jsonl', 'a') as idx, ThreadPoolExecutor(a.jobs) as ex:
        futs = [ex.submit(run, f, root, a.unswbc, version, a.no_logs) for f in todo]
        for n, fu in enumerate(as_completed(futs), 1):
            try:
                row = fu.result()
            except Exception as e:
                print('ERR', e, flush=True); continue
            if row:
                idx.write(json.dumps(row) + '\n'); idx.flush()
                print(n, row['game'], row['winner'], row['rounds'], row['seconds'], flush=True)

if __name__ == '__main__':
    main()
