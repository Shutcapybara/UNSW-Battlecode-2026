"""Jet local panel runner (Linux VM, unswbc 1.0.0 native).

usage: panel.py OUT --arms A B ... --opps X Y ... --maps m1 m2 ... [--jobs 3]
Each (arm, opp, map, seat) game is played once; seat A means arm is team A.
Results append to OUT/results.jsonl (resumable). Metrics from
tools/ouroboros/replaystats.py are stored per game.  Replays kept in OUT/replays.
"""
import argparse, hashlib, json, os, re, shutil, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'tools' / 'ouroboros'))
import replaystats  # noqa

def src_hash(d):
    h = hashlib.sha256()
    for p in sorted(Path(d).rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts and '.unswbc-build' not in p.parts:
            h.update(str(p.relative_to(d)).encode()); h.update(hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest()

def map_path(m):
    for c in (Path.home() / 'w' / 'maps' / f'{m}.map', REPO / 'maps' / f'{m}.map', REPO / 'maps' / 'new' / f'{m}.map'):
        if c.exists():
            return c
    raise FileNotFoundError(m)

def bot_path(name):
    p = Path(name)
    if p.is_dir(): return p
    q = Path.home() / 'w' / 'bots' / name   # frozen local copies first
    return q if q.is_dir() else REPO / 'bots' / name

lock = threading.Lock()
WS = Path.home() / 'w' / 'ws'

def worker_copy(src):
    t = WS / str(threading.get_ident()) / src.name
    if not t.exists():
        shutil.copytree(src, t, ignore=shutil.ignore_patterns('.unswbc-build', '__pycache__'))
    return t

def play(out, arm, opp, m, seat, timeout, keep):
    key = f'{arm}|{opp}|{m}|{seat}'
    a, b = (arm, opp) if seat == 'A' else (opp, arm)
    pa, pb = worker_copy(bot_path(a)), worker_copy(bot_path(b))
    rp = out / 'replays' / (key.replace('|', '__').replace('/', '_') + '.replay')
    env = dict(os.environ); env['PATH'] = str(Path.home() / 'bcenv' / 'bin') + ':' + env['PATH']
    t0 = time.time()
    try:
        r = subprocess.run([str(Path.home() / 'bcenv/bin/unswbc'), 'run'] + (['-v'] if (a.startswith('jet') or b.startswith('jet')) else []) + [str(map_path(m)), str(pa), str(pb), '-o', str(rp)],
                           capture_output=True, text=True, timeout=timeout, env=env, cwd=str(pa.parent))
        txt = r.stdout + r.stderr
        err = None
        res_lines = [l for l in txt.splitlines() if re.search(r'wins after|draw after', l, re.I)]
        if res_lines: txt = txt + '\n' + res_lines[-1]
    except subprocess.TimeoutExpired as e:
        txt, err = '', 'timeout'
    dt = time.time() - t0
    mm = re.search(r'team ([AB]) wins after (\d+) rounds \(([^)]*)\)', txt)
    md = re.search(r'draw after (\d+) rounds', txt, re.I)
    rec = dict(key=key, arm=arm, opp=opp, map=m, seat=seat, secs=round(dt, 1))
    faults = len(re.findall(r'(Traceback|Error|exception|timed out|crash)', txt))
    rec['fault_lines'] = faults
    rec['jet_ladder'] = txt.count('JET doctrine=ladder'); rec['jet_host'] = txt.count('JET doctrine=host')
    rec['bot_errors'] = txt.count('MC_ERROR') + txt.count('Traceback')
    rec['timeouts'] = txt.count('ran out of time')  # native per-turn wall-clock limit (load-sensitive)
    if mm:
        w = mm.group(1); rec.update(rounds=int(mm.group(2)), how=mm.group(3), winner_team=w,
                                    score=1.0 if w == seat else 0.0)
    elif md:
        rec.update(rounds=int(md.group(1)), how='draw', winner_team=None, score=0.5)
    else:
        rec.update(error=err or 'unparsed', tail=txt[-800:])
    if rp.exists() and 'error' not in rec:
        try:
            s = replaystats.analyse(str(rp))
            me, th = (s['teams']['A'], s['teams']['B']) if seat == 'A' else (s['teams']['B'], s['teams']['A'])
            def comp(t):
                return {k: t[k] for k in ('deaths', 'len_lost', 'splits', 'pearls', 'h2h_up', 'h2h_even', 'h2h_down', 'peak_units', 'curve')}
            rec['me'] = comp(me); rec['them'] = comp(th)
        except Exception as e:  # metrics are optional
            rec['metrics_error'] = repr(e)[:200]
        if not keep:
            rp.unlink()
    with lock:
        with open(out / 'results.jsonl', 'a') as f:
            f.write(json.dumps(rec) + '\n')
    return rec

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out'); ap.add_argument('--arms', nargs='+', required=True)
    ap.add_argument('--opps', nargs='+', required=True); ap.add_argument('--maps', nargs='+', required=True)
    ap.add_argument('--seats', nargs='+', default=['A', 'B'])
    ap.add_argument('--jobs', type=int, default=3); ap.add_argument('--timeout', type=int, default=600)
    ap.add_argument('--no-keep', action='store_true')
    ap.add_argument('--deadline', type=float, default=0, help='stop starting new games after N seconds')
    a = ap.parse_args()
    out = Path(a.out).resolve(); (out / 'replays').mkdir(parents=True, exist_ok=True)
    done = set()
    if (out / 'results.jsonl').exists():
        for l in open(out / 'results.jsonl'):
            r = json.loads(l)
            if 'error' not in r: done.add(r['key'])
    man = out / 'manifest.json'
    if not man.exists():
        json.dump(dict(created=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), runner='unswbc 1.0.0 native linux-x86_64 VM',
                       python='bcenv 3.13', arms={x: src_hash(bot_path(x)) for x in a.arms},
                       opps={x: src_hash(bot_path(x)) for x in a.opps},
                       maps={m: hashlib.sha256(map_path(m).read_bytes()).hexdigest() for m in a.maps}), open(man, 'w'), indent=1)
    jobs = [(arm, o, m, s) for m in a.maps for o in a.opps for s in a.seats for arm in a.arms
            if f'{arm}|{o}|{m}|{s}' not in done and arm != o]
    print(f'{len(jobs)} games to run', flush=True)
    t_start = time.time(); q = list(jobs); qlock = threading.Lock(); cnt = [0]
    def w():
        while True:
            if a.deadline and time.time() - t_start > a.deadline: return
            with qlock:
                if not q: return
                j = q.pop(0)
            r = play(out, *j, a.timeout, not a.no_keep)
            with qlock:
                cnt[0] += 1
                print(cnt[0], r['key'], r.get('score'), r.get('rounds'), r['secs'], flush=True)
    ts = [threading.Thread(target=w) for _ in range(a.jobs)]
    for t in ts: t.start()
    for t in ts: t.join()

if __name__ == '__main__':
    main()
