"""Trial-look curve block (D-085 §A: reached and carried views side by side). Selection identical to p06_column.py
(first series boundary at or after NMIN ranked games of SUB from START). Resumable decode, sharded.
Usage:
  python3 tools/hinata/look.py decode SUB START NMIN BUDGET_S SHARD NSHARD OUTDIR
  python3 tools/hinata/look.py block OUTDIR [POP]        (POP filter for re-reading curves2 rows, e.g. 17530)
Rows: per team per round [units, total, longest, queen_alive, queen_len] (queen = lowest initial dragon id of the team,
curves_qid). Band = opponent elo in the ladder snapshot at game start (< 1725 / >= 1725), as in D-085 §A.
Views at r: reached = games still running at r; carried = every game, value at r or the end state (eliminated side = 0).
CI: series bootstrap 1,000 x seed 7, 5-95 %."""
import json, gzip, sys, os, time, bisect, tempfile, random, collections
from pathlib import Path
sys.path.insert(0, '.'); sys.path.insert(0, 'tools/hinata')
MAP_SWITCH = '2026-10-02T03:49:00'; GRID = list(range(0, 500, 25))
def select(T, START, NMIN):
    games = []
    for l in open('public_replays/corpus/index.jsonl'):
        if '"team_a": 7,' not in l and '"team_b": 7,' not in l: continue
        r = json.loads(l)
        if not (r.get('ranked') and r.get('status') == 'completed' and (r.get('started_at') or '') >= max(MAP_SWITCH, START)): continue
        us = 'a' if r['team_a'] == 7 else 'b'
        if str(r['bot_a'] if us == 'a' else r['bot_b']) != T: continue
        games.append(dict(gid=r['game_id'], series=r['series_id'], start=r['started_at'], team_a=r['team_a'], team_b=r['team_b'], us=us.upper(), pop=T))
    games = sorted({g['gid']: g for g in games}.values(), key=lambda g: (g['start'], g['gid']))
    tr, seen = [], []
    for g in games:
        if g['series'] not in seen:
            if len(tr) >= NMIN: break
            seen.append(g['series'])
        tr.append(g)
    snaps = sorted(Path('public_replays/corpus/ladder').glob('*.json')); keys = [p.stem for p in snaps]; cache = {}
    for g in tr:
        i = bisect.bisect_right(keys, g['start'][:19].replace('-', '').replace(':', '') + 'Z') - 1
        if i not in cache: cache[i] = {t['id']: t['elo'] for t in json.load(open(snaps[i]))} if i >= 0 else {}
        g['elo_a'], g['elo_b'] = cache[i].get(g['team_a']), cache[i].get(g['team_b'])
    return tr, len(tr) >= NMIN
def decode(T, START, NMIN, budget, sh, ns, OUT):
    from tools.analysis.features import frame
    from curves_qid import queen_ids
    OUT = Path(OUT); OUT.mkdir(parents=True, exist_ok=True); t0 = time.time()
    sp = OUT / 'sel.json'
    if not sp.exists():
        sel, complete = select(T, START, NMIN)
        tmp = OUT / f'sel.{os.getpid()}.tmp'  # atomic: shards may race (run shard 0 alone first)
        json.dump(dict(sub=T, start=START, nmin=NMIN, complete=complete, n=len(sel), series=len({g['series'] for g in sel}), games=sel), open(tmp, 'w'))
        os.replace(tmp, sp)
    S = json.load(open(sp)); sel = [g for g in S['games'] if g['gid'] % ns == sh]
    done = {json.loads(l)['gid'] for q in OUT.glob('g_s*.jsonl') for l in open(q)}
    fh = open(OUT / f'g_s{sh}.jsonl', 'a'); n = 0
    def side(R, t, q):
        b = [x for (tt, x) in R.values() if tt == t]
        return [len(b), sum(map(len, b)), max(map(len, b), default=0), int(q in R), len(R[q][1]) if q in R else 0]
    for s in sel:
        if s['gid'] in done: continue
        if time.time() - t0 > budget: break
        p = Path(f"public_replays/corpus/replays/{s['gid']}.replay")
        if not p.exists(): fh.write(json.dumps(dict(s, err='MISSING')) + '\n'); continue
        with tempfile.NamedTemporaryFile(suffix='.replay', dir='/tmp', delete=False) as tf:
            tf.write(gzip.decompress(p.read_bytes())); tn = tf.name
        try:
            fr = frame.decode(tn); QID = queen_ids(frame._reader(tn).object(0, 0).text(0))
        except Exception: fh.write(json.dumps(dict(s, err='DECODE')) + '\n'); os.unlink(tn); continue
        os.unlink(tn)
        R = fr['rounds']; out = dict(s, winner=fr['winner'], reason=fr['reason'], last_round=fr['last_round'], final=fr['final'], map=fr['map'])
        for t in 'AB':
            q = QID.get(t, -1)
            out['c' + t] = {str(r): side(R[r], t, q) for r in GRID if r < len(R) - 1}
            out['c' + t]['end'] = side(R[-1], t, q)
            fq = fr['final'].get(t, {}).get('queen')  # engine guard
            if fq is not None: out.setdefault('guard', {})[t] = int(out['c' + t]['end'][3] == int(fq > 0))
        fh.write(json.dumps(out) + '\n'); fh.flush(); n += 1
    print('shard', sh, 'decoded', n, 'done_before', len(done), 'of', S['n'], 'complete', S['complete'], f'{time.time()-t0:.0f}s')
def block(OUT, POP=None):
    G = [json.loads(l) for q in sorted(Path(OUT).glob('g_s*.jsonl')) for l in open(q)]
    G = [g for g in G if 'err' not in g and (POP is None or g.get('pop') == POP)]
    def band(e): return '<1725' if (e is None or e < 1725) else '>=1725'
    def val(c, r, lr, view):
        if r in c and lr >= int(r): return c[r]
        return None if view == 'reached' else c['end']
    def ci(S, f):
        k = list(S); rng = random.Random(7); bs = []
        for _ in range(1000):
            xs = [x for kk in (rng.choice(k) for _ in k) for x in S[kk]]; bs.append(sum(xs) / len(xs))
        bs.sort(); return bs[49], bs[949]
    rows = collections.defaultdict(list)
    for g in G:
        us = g['us']; th = 'B' if us == 'A' else 'A'
        for b in (band(g['elo_' + th.lower()]), 'all'): rows[b].append((g, g['c' + us], g['c' + th]))
    nguard = sum(len(g.get('guard', {})) for g in G); okguard = sum(sum(g.get('guard', {}).values()) for g in G)
    print(f"games {len(G)}, series {len({g['series'] for g in G})}, queen guard {okguard}/{nguard}")
    for b in ('all', '<1725', '>=1725'):
        L = rows.get(b, [])
        if not L: continue
        W = sum(g['winner'] == g['us'] for g, _, _ in L); n = len(L)
        el = [g for g, _, _ in L if g['winner'] not in (g['us'], 'draw', None) and g['reason'] == 'elimination']
        print(f"== {b}: n {n}/{len({g['series'] for g,_,_ in L})} series, W {W}/{n}; elimination losses {len(el)}, before r300 {sum(g['last_round'] < 300 for g in el)}")
        for view in ('reached', 'carried'):
            for r in ('100', '300'):
                v = [(g, val(X, r, g['last_round'], view), val(Y, r, g['last_round'], view)) for g, X, Y in L]
                v = [t for t in v if t[1] is not None]
                if not v: continue
                S = collections.defaultdict(list)
                for g, x, y in v: S[g['series']].append(x[1] - y[1])
                lo, hi = ci(S, None); m = len(v)
                us_t = sum(x[1] for _, x, _ in v) / m; op_t = sum(y[1] for _, _, y in v) / m
                qa = sum(x[3] for _, x, _ in v) / m; qo = sum(y[3] for _, _, y in v) / m
                line = f"  {view:7s} r{r}: n {m}; total us {us_t:.1f} opp {op_t:.1f} diff {us_t-op_t:+.1f} [{lo:+.1f},{hi:+.1f}]; queen alive us {qa:.2f} opp {qo:.2f}"
                if r == '300':
                    lead = [t for t in v if t[1][1] > t[2][1]]; conv = sum(t[0]['winner'] == t[0]['us'] for t in lead)
                    line += f"; leads {len(lead)}/{m}, converted {conv}/{len(lead)}"
                print(line)
if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'decode': decode(a[1], a[2], int(a[3]), float(a[4]), int(a[5]), int(a[6]), a[7])
    else: block(a[1], a[2] if len(a) > 2 else None)
