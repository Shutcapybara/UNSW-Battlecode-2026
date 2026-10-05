"""D-086 §D fallback: replays carry per-turn points (cpu) only for the fetching team (7). Fast scan of kind-4 events in
every team-7 corpus replay: per game max cpu, turns > 30M (and whether that dragon acted again later), tle turns,
first-turn (round 0/1) max. Resumable, sharded. Usage: scan BUDGET SHARD NSHARD OUT | report OUT"""
import json, gzip, sys, time, collections
from pathlib import Path
sys.path.insert(0, '.'); sys.path.insert(0, 'tools/analysis/features')
def scan(budget, sh, ns, OUT):
    from tools.analysis.features import frame
    OUT = Path(OUT); OUT.mkdir(parents=True, exist_ok=True); t0 = time.time()
    done = {json.loads(l)['gid'] for q in OUT.glob('o_s*.jsonl') for l in open(q)}
    G = []
    for l in open('public_replays/corpus/index.jsonl'):
        if '"team_a": 7,' not in l and '"team_b": 7,' not in l: continue
        r = json.loads(l)
        if r.get('status') == 'completed': G.append((r['game_id'], r.get('started_at'), r['bot_a'] if r['team_a'] == 7 else r['bot_b'], bool(r.get('ranked'))))
    fh = open(OUT / f'o_s{sh}.jsonl', 'a')
    for gid, st, sub, rk in sorted(set(G), reverse=True):
        if gid % ns != sh or gid in done: continue
        if time.time() - t0 > budget: break
        p = Path(f'public_replays/corpus/replays/{gid}.replay')
        if not p.exists(): continue
        try:
            r = frame._reader(p); root = r.object(0, 0); rnd = -1; A = []
            for e in root.items(3):
                k = e.num(0, 'H'); o = e.child(0)
                if k == 0: rnd = o.num()
                elif k == 4:
                    cpu = o.child(1).num(0, 'Q') if o.has(1) else None
                    A.append((rnd, o.num(), cpu, bool(o.num(4, 'B') & 1)))
        except Exception as ex:
            fh.write(json.dumps(dict(gid=gid, err=str(ex)[:80])) + '\n'); continue
        C = [a for a in A if a[2] is not None]
        last = {}
        for a in A: last[a[1]] = max(last.get(a[1], -1), a[0])
        big = [a for a in C if a[2] > 30_000_000]
        fh.write(json.dumps(dict(gid=gid, start=st, sub=sub, ranked=rk, n=len(C), max=max((a[2] for a in C), default=None),
            max01=max((a[2] for a in C if a[0] <= 1), default=None), maxr2=max((a[2] for a in C if a[0] > 1), default=None),
            n30=len(big), big=[[a[0], a[1], a[2], a[3], last[a[1]] > a[0]] for a in sorted(big, key=lambda a: -a[2])[:5]],
            ntle=sum(a[3] for a in C), tle=[[a[0], a[1], a[2]] for a in C if a[3]][:5])) + '\n'); fh.flush()
def report(OUT):
    R = [json.loads(l) for q in Path(OUT).glob('o_s*.jsonl') for l in open(q)]; R = [r for r in R if 'n' in r and r['n']]
    print('games with cpu', len(R), 'ranked', sum(r['ranked'] for r in R))
    print('max cpu', max(r['max'] for r in R), 'turns>30M', sum(r['n30'] for r in R), 'games with >30M', sum(r['n30'] > 0 for r in R), 'tle turns', sum(r['ntle'] for r in R))
    for r in sorted(R, key=lambda r: -r['max'])[:12]: print(r['gid'], r['start'], r['sub'], r['ranked'], r['max'], r['max01'], r['maxr2'], r['n30'], r['big'][:2], r['ntle'], r['tle'][:2])
    T = [r for r in R if r['ntle']]
    print('games with tle', len(T)); [print(r['gid'], r['sub'], r['max'], r['tle']) for r in T[:8]]
if __name__ == '__main__':
    a = sys.argv
    scan(float(a[2]), int(a[3]), int(a[4]), a[5]) if a[1] == 'scan' else report(a[2])
