"""Offline deployment check: exact-source zip plus four metered heavy-map games."""
from pathlib import Path
import argparse
import json
import os
import shutil
import subprocess
import sys
import threading
import zipfile

ROOT=Path(__file__).resolve().parents[2]
MAIN=ROOT.parent/'UNSW-Battlecode-2026'
OUT=MAIN/'build/kenma'
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(Path(__file__).parent))
from panel import check_space, monitor, STOP, fingerprint, ACTIVE, LOCK

def run_child(argv):
    """Keep each helper in a process group the aggregate resource guard can stop."""
    if STOP.is_set():
        raise RuntimeError('Deployment resource guard stopped the run')
    env=dict(os.environ, KENMA_DEPLOY_CHILD='1')
    p=subprocess.Popen(argv, start_new_session=True, env=env)
    with LOCK:
        ACTIVE.add(p.pid)
    try:
        rc=p.wait()
    finally:
        with LOCK:
            ACTIVE.discard(p.pid)
    if STOP.is_set():
        raise RuntimeError('Deployment resource guard stopped the run')
    if rc:
        raise subprocess.CalledProcessError(rc, argv)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('bot'); ap.add_argument('--one', nargs=2, metavar=('MAP','SEAT'))
    ap.add_argument('--build', action='store_true', help=argparse.SUPPRESS)
    a=ap.parse_args()
    assert os.getpriority(os.PRIO_PROCESS,0)>=15
    check_space()
    src=ROOT/'bots'/a.bot
    out=OUT/'deploy'/a.bot
    out.mkdir(parents=True,exist_ok=True)
    os.environ['XDG_CACHE_HOME']=str(OUT/'cache')
    os.environ['UNSWBC_WARM']='1'
    os.environ['OMP_NUM_THREADS']='1'
    os.environ['PYTHONDONTWRITEBYTECODE']='1'
    if a.one or a.build:
        assert os.environ.get('KENMA_DEPLOY_CHILD')=='1', 'Internal helpers must run under the parent resource guard'
    else:
        threading.Thread(target=monitor,daemon=True).start()
    if a.build:
        from unswbc import clangtool
        clangtool.build(src)
        return
    if a.one:
        from tools.cx.arena import run_game
        m,seat=a.one
        base=ROOT/'bots/carthage-05-free-sprint'
        ba,bb=(src,base) if seat=='A' else (base,src)
        r=run_game(str(ROOT/'maps/live'/f'{m}.map'),str(ba),str(bb),seed=1,sandbox=True,purge=False)
        r.pop('transcripts',None)
        r['candidate_seat']=seat
        r['candidate_fingerprint']=fingerprint(src)
        (out/f'{m}-{seat}.json').write_text(json.dumps(r,indent=2)+'\n')
        print(json.dumps(dict(map=m,seat=seat,winner=r['winner'],points=r['stats'][seat].get('points'),boot=r['stats'][seat].get('boot'),errors=r['errors'])),flush=True)
        STOP.set()
        return
    # Only copy existing immutable compiler caches; bot builds are fresh in the lane's cache.
    from unswbc import clangtool
    from unswbc.sandbox import compiled_path
    home=clangtool.toolchain()
    for wasm in (home/'clang.wasm',home/'root/bin/wasm-ld'):
        target=compiled_path(wasm)
        original=Path.home()/'.cache/unswbc'/target.name
        if not target.exists() and original.exists():
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(original,target)
    with zipfile.ZipFile(out/f'{a.bot}.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(src.iterdir()):
            if p.is_file() and (p.suffix in ('.cpp','.hpp','.h','.cc','.toml','.md') or p.name=='.gitignore'):
                z.write(p,p.name)
    size=(out/f'{a.bot}.zip').stat().st_size
    assert size<=4*1024**2, f'Archive exceeds cap: {size}'
    print('zip',size,flush=True)
    # Build serially so games never race on the source-only toolkit wasm cache key.
    for b in (src,ROOT/'bots/carthage-05-free-sprint'):
        run_child([sys.executable,'-B',str(Path(__file__).resolve()),b.name,'--build'])
    for m,seat in [('schooltime','A'),('schooltime','B'),('unsw','A'),('unsw','B')]:
        check_space()
        if not (out/f'{m}-{seat}.json').exists():
            run_child([sys.executable,'-B',str(Path(__file__).resolve()),a.bot,'--one',m,seat])
    results=[json.loads((out/f'{m}-{seat}.json').read_text()) for m,seat in [('schooltime','A'),('schooltime','B'),('unsw','A'),('unsw','B')]]
    assert all(r['candidate_fingerprint']==fingerprint(src) for r in results), 'Refusing stale deployment results'
    peak=max(r['stats'][r['candidate_seat']]['points']['max'] for r in results)
    boot=max(r['stats'][r['candidate_seat']]['boot']['max'] for r in results)
    errors=[e for r in results for e in r['errors']]
    summary=dict(bot=a.bot,fingerprint=fingerprint(src),zip_bytes=size,games=4,max_points=peak,max_first_turn_points=boot,errors=errors,passed=peak<30000000 and not errors)
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary),flush=True)
    STOP.set()

if __name__=='__main__':
    main()
