"""Count JET doctrine lines per map: jet-bot (seat A) vs control (seat B). Resumable."""
import json, subprocess, sys, time, threading, re
from pathlib import Path
bot, ctrl, out = sys.argv[1], sys.argv[2], Path(sys.argv[3]).resolve()
maps = sys.argv[4].split(','); deadline = float(sys.argv[5]) if len(sys.argv) > 5 else 0
REPO = Path(__file__).resolve().parents[2]; H = Path.home()
done = set(json.loads(l)['map'] for l in open(out)) if out.exists() else set()
q = [m for m in maps if m not in done]; lock = threading.Lock(); t0 = time.time()
def mp(m):
    for c in (H / 'w/maps' / f'{m}.map', REPO / 'maps' / f'{m}.map', REPO / 'maps/new' / f'{m}.map'):
        if c.exists(): return c
def w():
    while True:
        if deadline and time.time() - t0 > deadline: return
        with lock:
            if not q: return
            m = q.pop(0)
        env = {'PATH': str(H / 'bcenv/bin') + ':/usr/bin:/bin', 'HOME': str(H)}
        r = subprocess.run([str(H / 'bcenv/bin/unswbc'), 'run', '-v', str(mp(m)), str(H / 'w/bots' / bot), str(H / 'w/bots' / ctrl), '--no-replay'], capture_output=True, text=True, env=env)
        t = r.stdout + r.stderr
        rec = dict(map=m, ladder=t.count('JET doctrine=ladder'), host=t.count('JET doctrine=host'),
                   result=(re.findall(r'team [AB] wins after \d+ rounds|draw after \d+ rounds', t) or ['?'])[-1], errors=t.count('MC_ERROR') + t.count('Traceback'))
        with lock:
            open(out, 'a').write(json.dumps(rec) + '\n'); print(rec, flush=True)
ts = [threading.Thread(target=w) for _ in range(3)]
[x.start() for x in ts]; [x.join() for x in ts]
