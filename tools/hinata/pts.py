"""D-086 §D: max points (cpu) per dragon-turn in ranked replays, by team. Resumable, sharded.
Usage: python3 tools/hinata/pts.py scan BUDGET_S SHARD NSHARD OUTDIR  |  python3 tools/hinata/pts.py report OUTDIR
Selection: ranked completed games started >= 2026-10-02T03:49 in which a top-ten team (ladder 20261005T162705Z) or team 7 plays,
newest first, capped at 600 games. Per game per team: n dragon-turns with cpu, max cpu, n turns > 30M, max cpu among turns
with tle=False, any tle, and whether a dragon whose turn exceeded 30M was alive at the next round."""
import json, gzip, sys, os, time, tempfile
from pathlib import Path
sys.path.insert(0, '.')
TOP = None
def sel():
    lad = sorted(json.load(open('public_replays/corpus/ladder/20261005T162705Z.json')), key=lambda t: -t['elo'])[:10]
    top = {t['id'] for t in lad} | {7}
    g = []
    for l in open('public_replays/corpus/index.jsonl'):
        r = json.loads(l)
        if r.get('ranked') and r.get('status') == 'completed' and (r.get('started_at') or '') >= '2026-10-02T03:49' and (r['team_a'] in top or r['team_b'] in top):
            g.append((r['started_at'], r['game_id'], r['team_a'], r['team_b']))
    g = sorted(set(g), reverse=True)[:600]
    return g, top
def scan(budget, sh, ns, OUT):
    from tools.analysis.features import frame
    OUT = Path(OUT); OUT.mkdir(parents=True, exist_ok=True); t0 = time.time()
    G, top = sel(); done = {json.loads(l)['gid'] for q in OUT.glob('p_s*.jsonl') for l in open(q)}
    fh = open(OUT / f'p_s{sh}.jsonl', 'a')
    for st, gid, ta, tb in G:
        if gid % ns != sh or gid in done: continue
        if time.time() - t0 > budget: break
        p = Path(f'public_replays/corpus/replays/{gid}.replay')
        if not p.exists(): continue
        with tempfile.NamedTemporaryFile(suffix='.replay', dir='/tmp', delete=False) as tf:
            tf.write(gzip.decompress(p.read_bytes())); tn = tf.name
        try: fr = frame.decode(tn)
        except Exception as e: fh.write(json.dumps(dict(gid=gid, err=str(e)[:80])) + '\n'); continue
        finally: os.unlink(tn)
        ev = fr['events'] if 'events' in fr else fr
        acts = ev['actions']; deaths = {(d['id'], d['round']): d['cause'] for d in ev['deaths']}
        dr = {}
        for d in ev['deaths']: dr[d['id']] = d['round']
        out = dict(gid=gid, start=st, teams={})
        for t in (0, 1):
            A = [a for a in acts if a['team'] == t and a['cpu'] is not None]
            team = ta if t == 0 else tb
            big = [a for a in A if a['cpu'] > 30_000_000]
            surv = [a for a in big if not a['tle'] and dr.get(a['id'], 10**9) > a['round']]
            out['teams'][str(team)] = dict(n=len(A), max=max((a['cpu'] for a in A), default=None),
                maxok=max((a['cpu'] for a in A if not a['tle']), default=None), n30=len(big), n30surv=len(surv),
                ntle=sum(a['tle'] for a in acts if a['team'] == t), maxtle=max((a['cpu'] for a in A if a['tle']), default=None),
                top=team in top)
        fh.write(json.dumps(out) + '\n'); fh.flush()
def report(OUT):
    import collections
    R = [json.loads(l) for q in Path(OUT).glob('p_s*.jsonl') for l in open(q)]
    R = [r for r in R if 'teams' in r]
    by = collections.defaultdict(lambda: dict(g=0, n=0, max=0, maxok=0, n30=0, n30surv=0, ntle=0, maxtle=0, gid=None))
    for r in R:
        for t, v in r['teams'].items():
            if not v['top']: continue
            b = by[t]; b['g'] += 1; b['n'] += v['n']; b['n30'] += v['n30']; b['n30surv'] += v['n30surv']; b['ntle'] += v['ntle']
            if (v['maxok'] or 0) > b['maxok']: b['maxok'], b['gid'] = v['maxok'], r['gid']
            b['max'] = max(b['max'], v['max'] or 0); b['maxtle'] = max(b['maxtle'], v['maxtle'] or 0)
    print('games', len(R))
    for t, b in sorted(by.items(), key=lambda x: -x[1]['maxok']): print(t, b)
if __name__ == '__main__':
    a = sys.argv
    if a[1] == 'scan': scan(float(a[2]), int(a[3]), int(a[4]), a[5])
    else: report(a[2])
