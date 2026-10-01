"""Seeded zoo panel runner (F1 feature lab).

python -m tools.analysis.features.run_panel --panel z1 --jobs 2 [--unswbc PATH]
Round robin of ZOO on LIVE_MAPS, both sides, seed 1; plus seeds 2-3 for STABILITY_PAIRS.
Resumable: skips games whose replay already exists; appends to build/zoo/<panel>/index.jsonl.

--panel gen plays GEN_MAPS (maps/new/*.map all 20 + maps/var/*_tr.map) with the
same ZOO and both seats (seed 1). --bot bots/<candidate> plays that one bot
against every ZOO opponent (both seats, --seed list, default 1) instead of the
round robin — the R-task scorecard grid — under build/zoo/<panel>-<bot>-<fp8>/
where fp8 keys the directory to the bot's runtime-source fingerprint, so a
replay set is reused only while the sources are untouched.
"""
import argparse, hashlib, itertools, json, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ZOO = ['fenrir-v18-arrival-ready-beds', 'yuna-v05-core', 'chaewon-y04-probe', 'sinbad-v07-divecap',
       'gavroche-v32-supported-divecap', 'ouroboros-m01-vibing-mimic', 'kazuha-s01-swarm-dissolve',
       'hunter-v20-portal-scouts']
LIVE_MAPS = ['schooltime', 'portals', 'slithery_fight', 'queen_of_spades', 'default', 'trophy', 'dilemma',
             'autarky', 'devil', 'trauma']
GEN_MAPS = ([f'var/{p.stem}' for p in sorted(Path('maps/var').glob('*_tr.map'))]
            + [f'new/{p.stem}' for p in sorted(Path('maps/new').glob('*.map'))])
STABILITY_PAIRS = [('fenrir-v18-arrival-ready-beds', 'hunter-v20-portal-scouts'),
                   ('yuna-v05-core', 'sinbad-v07-divecap'),
                   ('gavroche-v32-supported-divecap', 'kazuha-s01-swarm-dissolve'),
                   ('chaewon-y04-probe', 'ouroboros-m01-vibing-mimic')]
RESULT = re.compile(r'team (A|B) wins after (\d+) rounds \(([^)]*)\)')

# runtime-source fingerprint: SHA-256 over the sorted source names and contents
# (bot.toml plus every c/c++/python source), name and bytes NUL-separated — the
# convention the Ares findings quote. Any source edit moves the panel directory.
FP_SUFFIXES = ('.c', '.cc', '.cpp', '.cxx', '.c++', '.h', '.hh', '.hpp', '.hxx', '.py')


def runtime_fingerprint(botdir):
    root = Path(botdir)
    names = sorted(p.relative_to(root).as_posix() for p in root.rglob('*')
                   if p.is_file() and (p.suffix in FP_SUFFIXES or p.name == 'bot.toml')
                   and '.unswbc-build' not in p.parts)
    h = hashlib.sha256()
    for n in names:
        h.update(n.encode())
        h.update(b'\0')
        h.update((root / n).read_bytes())
        h.update(b'\0')
    return h.hexdigest()


def bot_path(name):
    """ZOO members are bare names under bots/; anything else is used as given."""
    return name if '/' in str(name) else f'bots/{name}'


def fixtures(panel='z1', bot=None, seeds=(1,)):
    out = []
    bot = str(bot)[len('bots/'):] if bot and str(bot).startswith('bots/') else bot
    if bot:
        maps = LIVE_MAPS if panel == 'z1' else GEN_MAPS
        seed_pairs = [(s, [(bot, z) for z in ZOO]) for s in seeds]
    elif panel == 'z1':
        maps = LIVE_MAPS
        seed_pairs = ((1, list(itertools.combinations(ZOO, 2))), (2, STABILITY_PAIRS), (3, STABILITY_PAIRS))
    else:
        maps = GEN_MAPS
        seed_pairs = [(1, list(itertools.combinations(ZOO, 2)))]
    for seed, pairs in seed_pairs:
        for a, b in pairs:
            for m in maps:
                for x, y in ((a, b), (b, a)):
                    out.append(dict(map=m, seed=seed, botA=x, botB=y,
                                    game=f's{seed}__{m.replace("/", "_")}__{Path(x).name}__{Path(y).name}'))
    return out

def run(fx, root, exe, version, no_logs=False):
    rep = root / 'replays' / (fx['game'] + '.replay')
    if rep.exists():
        return None
    t = time.time()
    p = subprocess.run([exe, 'run', '--seed', str(fx['seed'])] + (['--no-logs'] if no_logs else []) + ['--no-indicator', '--no-draw', '-o', str(rep) + '.tmp',
                        f"maps/{fx['map']}.map", bot_path(fx['botA']), bot_path(fx['botB'])], capture_output=True, text=True, timeout=int(os.environ.get('RUN_PANEL_TIMEOUT', 1800)))
    out = p.stdout + p.stderr
    m = RESULT.search(out)
    row = dict(fx, toolkit=version, sandbox=False, logs=not no_logs, host=os.uname().nodename, seconds=round(time.time() - t, 1), rc=p.returncode,
               winner=m.group(1) if m else ('draw' if 'draw' in out.lower() else None),
               rounds=int(m.group(2)) if m else None, reason=m.group(3) if m else out.strip().splitlines()[-1][:200] if out.strip() else '')
    if os.path.exists(str(rep) + '.tmp'):
        os.replace(str(rep) + '.tmp', rep)
    row['replay'] = str(rep.relative_to(root))
    return row

def prebuild(bots):
    """Build every bot once, serially, before the parallel games start: two
    concurrent `unswbc run` processes racing on the same .unswbc-build caused
    Ares V04's transient startup error. A compile error fails loudly here
    instead of as one failed fixture per game."""
    try:
        from unswbc.project import Project
    except ImportError as e:
        print(f"WARN prebuild skipped ({e}); first parallel games may race on .unswbc-build")
        return
    for b in sorted(set(bots)):
        d = Path(bot_path(b))
        if not (d / 'bot.toml').is_file():
            continue
        try:
            Project.from_dir(d).compile()
        except Exception as e:  # ProjectError, ToolError, ...: any build failure is loud
            raise SystemExit(f'BUILD FAILED {b}: {e}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--panel', default='z1', choices=['z1', 'gen']); ap.add_argument('--jobs', type=int, default=2)
    ap.add_argument('--unswbc', default='unswbc')
    ap.add_argument('--bot', default=None, help='play this bot against every ZOO opponent instead of the round robin')
    ap.add_argument('--seed', default=None, help='comma list of seeds for --bot mode (default 1)')
    ap.add_argument('--shards', default=None, help='comma list of shard ids to run, with --of N (fixture index mod N)')
    ap.add_argument('--of', type=int, default=1)
    ap.add_argument('--skip', default=None, help='file of game ids already run elsewhere')
    ap.add_argument('--reverse', action='store_true', help='run the shard from the end (to meet another host in the middle)')
    ap.add_argument('--no-logs', action='store_true', help='keep LOG lines out of the replay (features do not use them)')
    ap.add_argument('--out', default=None, help='replay root (default build/zoo/<panel>[-<bot>-<fp8>])')
    a = ap.parse_args()
    bot = a.bot
    seeds = tuple(int(s) for s in a.seed.split(',')) if a.seed else (1,)
    if a.out:
        root = Path(a.out)
    elif bot:
        fp8 = runtime_fingerprint(bot)[:8]
        root = Path('build/zoo') / f'{a.panel}-{Path(bot).name}-{fp8}'
    else:
        root = Path('build/zoo') / a.panel
    (root / 'replays').mkdir(parents=True, exist_ok=True)
    version = subprocess.run([a.unswbc, '--version'], capture_output=True, text=True).stdout.strip()
    fx = fixtures(a.panel, bot, seeds)
    if a.shards is not None:
        keep = {int(x) for x in a.shards.split(',')}
        fx = [f for i, f in enumerate(fx) if i % a.of in keep]
    skip = set(open(a.skip).read().split()) if a.skip else set()
    todo = [f for f in fx if f['game'] not in skip and not (root / 'replays' / (f['game'] + '.replay')).exists()]
    if a.reverse:
        todo = todo[::-1]
    prebuild({f[b] for f in fx for b in ('botA', 'botB')})
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
