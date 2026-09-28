"""Frozen, seeded Vicious panels. Does not change the shared tournament/ledger."""
import argparse
import concurrent.futures as cf
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'tools')]
from tools.benchmarking.tournament import MatchWorkers, play, atomic_write
from public_replay_review import analyse


def hashes(folder):
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(folder.iterdir()) if p.suffix in ('.py', '.toml')}


def run(args):
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    manifest = out / 'manifest.json'
    if not manifest.exists():
        maps = {}
        for m in args.maps:
            p = ROOT / 'maps' / (m + '.map')
            if not p.exists(): p = ROOT / 'maps/new' / (m + '.map')
            maps[m] = p
        sources = out / 'sources'
        sources.mkdir()
        for b in set(args.arms + args.opps):
            shutil.copytree(ROOT / 'bots' / b, sources / b,
                            ignore=shutil.ignore_patterns('__pycache__', '.unswbc-build'))
        (sources / 'maps').mkdir()
        for m, p in maps.items(): shutil.copy2(p, sources / 'maps' / p.name)
        data = dict(arms=args.arms, opponents=args.opps, maps=list(maps),
                    seats=['A', 'B'], sandbox=args.sandbox, fast=args.fast,
                    source_hashes={b: hashes(sources / b) for b in set(args.arms + args.opps)},
                    map_hashes={m: hashlib.sha256(p.read_bytes()).hexdigest() for m,p in maps.items()},
                    seed='vicious-fixture-v1 (same seed across arms and sides)',
                    engine='unswbc 1.0.0, Vicious fixed-WASI-clock adapter',
                    runner_hash=hashlib.sha256((ROOT/'tools/vicious'/('fast_runner' if args.fast else 'runner')).read_bytes()).hexdigest(), created=time.time())
        atomic_write(manifest, json.dumps(data, indent=2)+'\n')
    data = json.loads(manifest.read_text())
    for b, expected in data['source_hashes'].items():
        if hashes(out / 'sources' / b) != expected: raise ValueError('Frozen source changed: '+b)
    rows = json.loads((out/'results.json').read_text()) if (out/'results.json').exists() else []
    if args.reuse and not rows:
        previous=Path(args.reuse).resolve()
        old=json.loads((previous/'manifest.json').read_text())
        if old['source_hashes'] != data['source_hashes'] or old['map_hashes'] != data['map_hashes']:
            raise ValueError('Reuse requires identical sources and maps')
        (out/'games').mkdir(exist_ok=True)
        for r in json.loads((previous/'results.json').read_text()):
            if r['outcome']=='error':continue
            for k in ('log','replay','stats'):
                if r.get(k):shutil.copy2(previous/'games'/r[k],out/'games'/r[k])
            rows.append(dict(r,reused_from=str(previous),execution='native'))
        atomic_write(out/'results.json',json.dumps(rows,indent=1)+'\n')
    # Reuse compatible individual fixtures while widening a panel. Never count
    # an identical deterministic fixture as additional evidence.
    for previous in args.reuse_panel:
        old=json.loads((previous/'manifest.json').read_text())
        if old['sandbox'] != data['sandbox']:continue
        present={tuple(r[k] for k in ('arm','opponent','map','side')) for r in rows if r['outcome']!='error'}
        (out/'games').mkdir(exist_ok=True)
        for r in json.loads((previous/'results.json').read_text()):
            a,o,m,s=(r[k] for k in ('arm','opponent','map','side'))
            if (a,o,m,s) in present or r['outcome']=='error':continue
            if a not in data['arms'] or o not in data['opponents'] or m not in data['maps']:continue
            if any(old['source_hashes'][b] != data['source_hashes'][b] for b in (a,o)):continue
            if old['map_hashes'][m] != data['map_hashes'][m]:continue
            for k in ('log','replay','stats'):
                if r.get(k):shutil.copy2(previous/'games'/r[k],out/'games'/r[k])
            rows.append(dict(r,reused_from=str(previous)));present.add((a,o,m,s))
        atomic_write(out/'results.json',json.dumps(rows,indent=1)+'\n')
    done = {tuple(r[k] for k in ('arm','opponent','map','side')) for r in rows if r['outcome'] != 'error'}
    fixtures = [(a,o,m,s) for m in data['maps'] for o in data['opponents']
                for s in data['seats'] for a in data['arms'] if a != o and (a,o,m,s) not in done]
    (out/'games').mkdir(exist_ok=True)
    print(f'{len(fixtures)} pending games, {args.jobs} workers, load {os.getloadavg()}', flush=True)
    start = time.monotonic()
    with tempfile.TemporaryDirectory(prefix='vicious-build-') as tmp:
        workers = MatchWorkers(tmp)
        def match(f):
            a,o,m,s = f
            pa,po = (out/'sources'/b for b in (a,o))
            aa,bb = (pa,po) if s == 'A' else (po,pa)
            label = '__'.join(f)
            seed = int.from_bytes(hashlib.sha256(f'vicious-fixture-v1:{o}:{m}'.encode()).digest()[:8],'big')
            runner=ROOT/'tools/vicious'/('fast_runner' if data.get('fast') else 'runner')
            r = play(str(runner),out/'sources/maps'/(m+'.map'),aa,bb,
                     out/'games',label,args.timeout,True,workers,data['sandbox'],seed=seed)
            r.update(arm=a,opponent=o,side=s,seed=str(seed),execution='isolated actors' if data.get('fast') else 'native')
            log=(out/'games'/r['log']).read_text(errors='replace')
            r['faults']={k:log.count(k) for k in ('MC_ERROR','Traceback','ran out of time','timed out')}
            if r['replay'] and r['outcome'] != 'error':
                try:
                    stats=analyse(out/'games'/r['replay'])
                    atomic_write(out/'games'/(label+'.stats.json'),json.dumps(stats,separators=(',',':')))
                    r['stats']=label+'.stats.json'
                except Exception as exc:r['analysis_error']=repr(exc)
            return r
        try:
            with cf.ThreadPoolExecutor(max_workers=args.jobs) as pool:
                queue=iter(fixtures); active={}
                def submit():
                    if args.budget and time.monotonic()-start >= args.budget:return
                    if (out/'STOP').exists():return
                    f=next(queue,None)
                    if f:active[pool.submit(match,f)]=f
                for _ in range(args.jobs):submit()
                while active:
                    finished,_=cf.wait(active,return_when=cf.FIRST_COMPLETED)
                    for future in finished:
                        f=active.pop(future);r=future.result()
                        rows=[x for x in rows if tuple(x[k] for k in ('arm','opponent','map','side')) != f]
                        rows.append(r);atomic_write(out/'results.json',json.dumps(rows,indent=1)+'\n')
                        print(len(rows),*f,r['outcome'],r['rounds'],r['seconds'],r.get('analysis_error',''),r['faults'],flush=True)
                        submit()
        finally:workers.cancel()
    print('Panel stopped/completed; results saved.',flush=True)


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('out');p.add_argument('--arms',nargs='+');p.add_argument('--opps',nargs='+');p.add_argument('--maps',nargs='+')
    p.add_argument('--jobs',type=int,default=2);p.add_argument('--timeout',type=int,default=900)
    p.add_argument('--budget',type=int,default=0);p.add_argument('--sandbox',action='store_true')
    p.add_argument('--fast',action='store_true');p.add_argument('--reuse',type=Path)
    p.add_argument('--reuse-panel',type=Path,action='append',default=[])
    run(p.parse_args())
