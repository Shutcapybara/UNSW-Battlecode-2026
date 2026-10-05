"""Bounded Kenma lane games. Native binaries are built under the main checkout build/kenma/bin.
Dry-run first; fingerprints and exact fixtures are saved before launch.
Fresh engine per game; max four workers; stop under 40 GB disk or above 5 GiB RSS.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import threading
import time

ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT.parent / 'UNSW-Battlecode-2026'
MAPS = ['schooltime', 'portals', 'slithery_fight', 'queen_of_spades', 'default', 'trophy',
        'dilemma', 'autarky', 'devil', 'trauma', 'australia', 'islands', 'unsw', 'maze',
        'weakhold', 'stripes', 'tower_defense']
ZOO = ['fenrir-v18-arrival-ready-beds', 'yuna-v05-core', 'chaewon-y04-probe', 'sinbad-v07-divecap',
       'gavroche-v32-supported-divecap', 'ouroboros-m01-vibing-mimic', 'kazuha-s01-swarm-dissolve',
       'hunter-v20-portal-scouts']
RESULT = re.compile(r'(?:team ([AB]) wins|draw) after (\d+) rounds \(([^)]*)\)')
STOP = threading.Event()
ACTIVE = set()
LOCK = threading.Lock()
_QUOTA_CHECKED = 0.0

def fingerprint(src):
    h = hashlib.sha256()
    for p in sorted(src.rglob('*')):
        if p.is_file() and (p.suffix in ('.cpp', '.hpp', '.py', '.h', '.cc') or p.name == 'bot.toml') and '.unswbc-build' not in p.parts:
            h.update(str(p.relative_to(src)).encode() + b'\0' + p.read_bytes() + b'\0')
    return h.hexdigest()

def check_space():
    global _QUOTA_CHECKED
    now = time.monotonic()
    if now - _QUOTA_CHECKED >= 60:
        total = 0
        for p in (MAIN/'build/kenma').rglob('*'):
            try:
                if p.is_file(): total += p.stat().st_size
            except FileNotFoundError:
                pass  # A concurrent atomic result/cache write may rename a temporary file.
        if total > 30 * 10**9:
            raise RuntimeError('STOP: Kenma output exceeds 30 GB')
        _QUOTA_CHECKED = now
    if shutil.disk_usage(MAIN).free < 40 * 10**9:
        raise RuntimeError('STOP: less than 40 GB disk free')
    for p in (ROOT/'claude/kenma-status.md', MAIN/'claude/kenma-status.md'):
        if p.exists() and re.search(r'\bSTOP\b', p.read_text()):
            raise RuntimeError(f'STOP directive: {p}')

def monitor():
    while not STOP.wait(2):
        try:
            check_space()
            rows = [line.split(None, 3) for line in subprocess.check_output(['ps', '-axo', 'pid=,ppid=,rss=,command='], text=True).splitlines()]
            descendants = {os.getpid()} | {int(pid) for pid, pp, rss, cmd in rows
                if '/tools/kenma/' in cmd or '/build/kenma/' in cmd}
            while True:
                more = {int(pid) for pid, pp, rss, cmd in rows if int(pp) in descendants}
                if more <= descendants:
                    break
                descendants |= more
            rss = sum(int(rss) for pid, pp, rss, cmd in rows if int(pid) in descendants)
            if rss > 5 * 1024**2:
                raise RuntimeError(f'STOP: lane RSS {rss/1024**2:.2f} GiB exceeds 5 GiB game budget')
        except Exception as e:
            print(str(e), flush=True)
            STOP.set()
            with LOCK:
                for pid in ACTIVE:
                    try:
                        os.killpg(pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass
            return

def run(fx, args, bins, out):
    if STOP.is_set():
        return None
    check_space()
    key = f"{fx['map'].replace('/', '+')}__s{fx['seed']}__{fx['seat']}__{fx['opp']}"
    dest = out / f'{key}.json'
    if dest.exists():
        previous = json.loads(dest.read_text())
        assert previous['bot'] == args.bot and all(previous[k] == v for k, v in fx.items()), 'Mismatched cached fixture'
        if previous['rc'] == 0 and previous['winner'] and not previous['faults']:
            return previous
        if not args.retry_errors:
            return previous
        stamp = str(time.time_ns())
        attempts = out/'attempts'
        attempts.mkdir(exist_ok=True)
        dest.rename(attempts/f'{key}.{stamp}.json')
        old_log = out/f'{key}.log'
        if old_log.exists():
            old_log.rename(attempts/f'{key}.{stamp}.log')
    a, b = (args.bot, fx['opp']) if fx['seat'] == 'A' else (fx['opp'], args.bot)
    replay = args.keep_replays and fx['seed'] == 1 and fx['map'] in ('live/schooltime', 'live/weakhold')
    cmd = [str(MAIN/'.venv/bin/unswbc'), 'run', '--seed', str(fx['seed']), '--no-logs', '--no-indicator', '--no-draw']
    cmd += ['-o', str(out/f'{key}.replay')] if replay else ['--no-replay']
    cmd += [str(ROOT/'maps'/f"{fx['map']}.map"), bins[a], bins[b]]
    start = time.time()
    with (out/f'{key}.log').open('w') as log:
        p = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        with LOCK:
            ACTIVE.add(p.pid)
        try:
            p.wait(timeout=600)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, signal.SIGTERM)
            p.wait()
        finally:
            with LOCK:
                ACTIVE.discard(p.pid)
    txt = (out/f'{key}.log').read_text()
    match = RESULT.search(txt)
    faults = [ln for ln in txt.splitlines() if re.search(r'(?:error|timed out|timeout|trap|budget|exited|crash)', ln, re.I)]
    row = dict(fx, bot=args.bot, rc=p.returncode, seconds=round(time.time()-start, 2), faults=faults,
               winner=(match.group(1) or 'draw') if match else None,
               rounds=int(match.group(2)) if match else None, reason=match.group(3) if match else None)
    dest.write_text(json.dumps(row, indent=2)+'\n')
    return row

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('bot'); ap.add_argument('--opp', default='carthage-05-free-sprint')
    ap.add_argument('--maps', default=','.join('live/'+m for m in MAPS))
    ap.add_argument('--seeds', default='1,2,3'); ap.add_argument('--jobs', type=int, default=3)
    ap.add_argument('--name', required=True); ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--keep-replays', action='store_true')
    ap.add_argument('--retry-errors', action='store_true', help='rerun failed fixtures, preserving previous attempt records')
    args=ap.parse_args()
    assert 1 <= args.jobs <= 4
    check_space()
    opponents=ZOO if args.opp=='zoo' else args.opp.split(',')
    fixtures=[dict(map=m, seed=int(s), opp=o, seat=t) for s in args.seeds.split(',') for m in args.maps.split(',') for o in opponents for t in 'AB']
    out=MAIN/'build/kenma'/args.name
    sources={b:ROOT/'bots'/b for b in [args.bot]+opponents}
    manifest=dict(bot=args.bot, fingerprints={b:fingerprint(p) for b,p in sources.items()}, fixtures=fixtures,
                  engine=subprocess.check_output([str(MAIN/'.venv/bin/unswbc'),'--version'],text=True).strip(), compiler='clang++ -O2 -std=c++20', sandbox=False)
    print(json.dumps(dict(fixtures=len(fixtures), workers=args.jobs, output=str(out), fingerprints=manifest['fingerprints'])), flush=True)
    if args.dry_run:
        return
    assert os.getpriority(os.PRIO_PROCESS,0)>=15, 'Run with nice -n 15'
    out.mkdir(parents=True, exist_ok=True)
    mp=out/'manifest.json'
    if mp.exists():
        assert json.loads(mp.read_text())==manifest, 'Refusing changed source or fixture manifest'
    else:
        mp.write_text(json.dumps(manifest,indent=2)+'\n')
    os.environ['PYTHONDONTWRITEBYTECODE']='1'
    os.environ['OMP_NUM_THREADS']='1'
    os.environ['OPENBLAS_NUM_THREADS']='1'
    bins={}
    for b, src in sources.items():
        if (src/'main.py').exists():
            bins[b]=str(src/'main.py')
        else:
            binary=MAIN/'build/kenma/bin'/f"{b}-{manifest['fingerprints'][b][:12]}"
            if not binary.exists():
                subprocess.run(['clang++','-O2','-std=c++20',str(src/'main.cpp'),'-o',str(binary)],check=True)
            bins[b]=str(binary)
    threading.Thread(target=monitor,daemon=True).start()
    rows=[]
    with ThreadPoolExecutor(args.jobs) as pool:
        futures=[pool.submit(run,fx,args,bins,out) for fx in fixtures]
        for f in as_completed(futures):
            row=f.result()
            if row:
                rows.append(row)
                print(f"{len(rows)}/{len(fixtures)} {row['map']} s{row['seed']} {row['seat']} vs {row['opp']}: {row['winner']} {row['reason']} {row['seconds']}s faults={len(row['faults'])}",flush=True)
    STOP.set()
    def tally(rs):
        valid=[r for r in rs if r['rc']==0 and r['winner'] and not r['faults']]
        return dict(wins=sum(r['winner']==r['seat'] for r in valid), losses=sum(r['winner'] not in (r['seat'],'draw') for r in valid), draws=sum(r['winner']=='draw' for r in valid), errors=len(rs)-len(valid))
    score=dict(total=tally(rows), by_map={m:tally([r for r in rows if r['map']==m]) for m in args.maps.split(',')},
               by_opponent={o:tally([r for r in rows if r['opp']==o]) for o in opponents}, completed=len(rows), expected=len(fixtures))
    (out/'score.json').write_text(json.dumps(score,indent=2)+'\n')
    print(json.dumps(score),flush=True)
    if score['total']['errors'] or score['completed'] != score['expected']:
        raise SystemExit(1)

if __name__=='__main__':
    main()
