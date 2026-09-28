"""Known-source conditional replay: drive a local bot with the exact round blocks
the deployed bot received in a public replay, and compare its commands with the
recorded ones.  Each dragon gets its own fresh process (init block + blocks), as on
the judge.  Recorded TLE turns restart that dragon's process (judge behaviour).

    python3 replay_drive.py REPLAY SIDE BOTDIR OUT.json [--max-round R]
"""
import json, subprocess, sys, time, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import recon, roundblock

rep, side, botdir, outp = sys.argv[1:5]
maxr = int(sys.argv[sys.argv.index('--max-round') + 1]) if '--max-round' in sys.argv else 10 ** 9
g = recon.Game(rep)
procs, turns_seen, pend = {}, {}, {}
stats = collections.Counter()
examples = []
t0 = time.time()
LET = {'north': 'N', 'east': 'E', 'south': 'S', 'west': 'W'}


def spawn(d):
    p = subprocess.Popen([sys.executable, '-u', 'main.py'], cwd=botdir, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL, text=True, bufsize=1)
    p.stdin.write(f'ID {d.id}\nTEAM {d.team}\nMAP {g.board.W} {g.board.H}\nUNIT_LIMIT {g.board.unit_limit}\n')
    return p


def ask(p, lines):
    p.stdin.write('\n'.join(lines) + '\n\n')
    p.stdin.flush()
    out = []
    while True:
        s = p.stdout.readline()
        if not s:
            return None
        s = s.rstrip('\n')
        if s == 'ENDTURN':
            return out
        out.append(s)


def parse(out):
    act, sonar = None, []
    for l in out or []:
        q = l.split()
        if not q:
            continue
        if q[0] == 'MOVE' and len(q) == 2:
            act = ('move', q[1])
        elif q[0] == 'SPLIT' and len(q) == 2:
            act = ('split', int(q[1]))
        elif q[0] == 'SONAR':
            sonar.append(tuple(q[1:]))
    return act, sonar


def cb(kind, **k):
    if kind == 'turn':
        d = k['dragon']
        if d.team != side or g.round > maxr:
            pend.clear(); return
        n = turns_seen.get(d.id, 0); turns_seen[d.id] = n + 1
        lines = roundblock.build_block(g, d, proto3=(n > 0 or d.parent is not None))
        if d.id not in procs:
            procs[d.id] = spawn(d)
        pend['d'] = d.id
        pend['out'] = ask(procs[d.id], lines)
    elif kind == 'action' and pend.get('d') == k['dragon'].id:
        d, a = k['dragon'], k['action']
        out = pend.pop('out'); pend.pop('d')
        if a[0] == 'tle':
            stats['recorded_tle'] += 1
            try: procs.pop(d.id).kill()
            except Exception: pass
            return
        mine, _ = parse(out)
        rec = ('move', ''.join(LET[s] for s in a[1])) if a[0] == 'move' else (('split', a[1]) if a[0] == 'split' else (a[0],))
        if mine is None and rec[0] in ('suicide', 'none'):
            ok = True
        else:
            ok = mine == rec
        stats['match' if ok else 'mismatch'] += 1
        if not ok and len(examples) < 10:
            examples.append(dict(round=g.round, dragon=d.id, recorded=str(rec), local=str(mine)))
    elif kind == 'death':
        p = procs.pop(k['dragon'].id, None)
        if p:
            try: p.kill()
            except Exception: pass


g.run(cb)
for p in procs.values():
    try: p.kill()
    except Exception: pass
res = dict(replay=rep, side=side, bot=botdir, stats=dict(stats), agreement=stats['match'] / max(1, stats['match'] + stats['mismatch']),
           examples=examples, secs=round(time.time() - t0), max_round=maxr)
json.dump(res, open(outp, 'w'), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != 'examples'}))
