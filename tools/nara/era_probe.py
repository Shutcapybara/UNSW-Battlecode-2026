"""Nara era probe: when did the live server switch to unswbc 1.2.3 rules?

Signals per game (decoded from the replay bytes):
  s0        moves with steps>=2 and paid==0  — impossible under the old sprint rule (x steps cost x-1)
  anom      moves with paid != steps-1       — any old-rule violation (broader)
  mismatch  round-limit games where the server winner differs from the old-rule decoded winner
            (queen -> longest -> total vs longest -> total)
  queenflip round-limit games where longest-order != queen-order (the rule bites), any era
  extra     words present in the final-result block beyond units/longest/total (queen length?)

Usage (from the main checkout, which owns public_replays/):
  python tools/nara/era_probe.py --since "2026-09-30 00:00" --every-h 2 --per 16 --out build/nara/era_probe.jsonl
"""
import argparse, json, sys, collections
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'tools' / 'leviathan'))
sys.path.insert(0, str(ROOT / 'tools' / 'analysis' / 'features'))

CORPUS = ROOT / 'public_replays' / 'corpus'


def load_index(since_dt):
    rows = []
    for line in open(CORPUS / 'index.jsonl'):
        r = json.loads(line)
        if r.get('status') != 'completed':
            continue
        st = datetime.fromisoformat(r['started_at'].replace('Z', '+00:00'))
        if st >= since_dt:
            rows.append((st, r))
    rows.sort(key=lambda x: x[0])
    return rows


def probe_one(args):
    from frame import decode
    st, r = args
    path = CORPUS / 'replays' / f"{r['game_id']}.replay"
    if not path.exists():
        return None
    try:
        g = decode(path)
    except Exception as e:
        return dict(game=r['game_id'], started=r['started_at'], error=f'{type(e).__name__}: {e}')
    acts = g['events']['actions']
    dead = {(d['round'], d['id']) for d in g['events']['deaths']}
    moves = [a for a in acts if a['kind'] == 'move' and a.get('steps', 0) >= 2
             and (a['round'], a['id']) not in dead]
    s0 = sum(1 for a in moves if a.get('paid') == 0)
    anom = sum(1 for a in moves if a.get('paid') != a['steps'] - 1)
    out = dict(game=r['game_id'], started=r['started_at'], map=g['map'],
               ranked=r.get('ranked'), winner_srv=r['winner'], winner_dec=g['winner'],
               reason=g['reason'], last_round=g['last_round'], s0=s0, anom=anom,
               n_moves=len(moves))
    # tiebreak: queen (lowest-id live robot) vs longest, on the final snapshot
    fin = g['rounds'][-1]
    live = {t: [i for i, (tm, _) in fin.items() if tm == t] for t in (0, 1)}
    q = {}
    for t, ids in live.items():
        if ids:
            qid = min(ids)
            q[t] = dict(id=qid, length=len(fin[qid][1]))
    out['queens'] = q
    out['final'] = g['final']
    rl = g['reason'] in ('longest', 'total', 'tie')
    if rl and q.get(0) and q.get(1):
        out['queenflip'] = (q[0]['length'] > q[1]['length']) != (g['final']['A']['longest'] > g['final']['B']['longest'])
        out['mismatch'] = (r['winner'] != g['winner'])
    else:
        out['queenflip'] = None
        out['mismatch'] = None
    # extra words in the result block?
    try:
        from replay import unpack
        import struct
        res = None
        # cheap re-open only when needed is skipped; use frame's internals via decode result only
    except Exception:
        pass
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--since', default='2026-09-30 00:00')
    ap.add_argument('--every-h', type=float, default=2.0)
    ap.add_argument('--per', type=int, default=16)
    ap.add_argument('--out', default='build/nara/era_probe.jsonl')
    ap.add_argument('--jobs', type=int, default=8)
    a = ap.parse_args()
    since = datetime.fromisoformat(a.since).replace(tzinfo=timezone.utc)
    rows = load_index(since)
    # bucket by every_h, sample up to per games (deterministic stride)
    buckets = collections.defaultdict(list)
    for item in rows:
        b = int((item[0] - since).total_seconds() // (a.every_h * 3600))
        buckets[b].append(item)
    sample = []
    for b in sorted(buckets):
        lst = buckets[b]
        step = max(1, len(lst) // a.per)
        sample.extend(lst[::step][:a.per])
    print(f'{len(rows)} games since {since}; sampling {len(sample)}', file=sys.stderr)
    import multiprocessing as mp
    with mp.Pool(a.jobs) as pool:
        results = [r for r in pool.imap_unordered(probe_one, sample, chunksize=1) if r]
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, 'w') as f:
        for r in sorted(results, key=lambda x: x['started']):
            f.write(json.dumps(r) + '\n')
    # hourly rollup
    agg = collections.defaultdict(lambda: dict(n=0, s0=0, anom=0, nm=0, mism=0, flip=0, rl=0))
    for r in results:
        if 'error' in r:
            continue
        h = r['started'][:13]
        d = agg[h]
        d['n'] += 1
        d['s0'] += r['s0']
        d['anom'] += r['anom']
        if r['reason'] in ('longest', 'total', 'tie'):
            d['rl'] += 1
            if r['queenflip']:
                d['flip'] += 1
            if r['mismatch']:
                d['mism'] += 1
    print(f"{'hour(UTC)':<15} {'n':>4} {'s0/mv':>7} {'anom/mv':>8} {'rl':>4} {'flip':>5} {'mism':>5}")
    for h in sorted(agg):
        d = agg[h]
        print(f"{h:<15} {d['n']:>4} {d['s0']/max(1,d['n']):>7.2f} {d['anom']/max(1,d['n']):>8.2f} "
              f"{d['rl']:>4} {d['flip']:>5} {d['mism']:>5}")


if __name__ == '__main__':
    main()
