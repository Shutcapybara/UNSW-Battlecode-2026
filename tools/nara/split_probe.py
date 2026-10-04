"""Nara split-opportunity probe (L47 decomposition, first slice).

For every split event in a sample of games: map, phase, parent length before, and outcomes within 10 rounds:
parent died, any child died, pearls the parent lineage kept. 'Regret candidate' = parent died within 10r while
neither child outlived it by material (child_len sum < parent_len_before) — the state where holding (not
splitting) plausibly retained more material.
"""
import json, sys, glob
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'tools' / 'leviathan'))
sys.path.insert(0, str(ROOT / 'tools' / 'analysis' / 'features'))

CORPUS = ROOT / 'public_replays' / 'corpus'


def cohorts():
    lad = sorted(glob.glob(str(CORPUS / 'ladder' / '*.json')))[-1]
    out = {}
    for r in json.load(open(lad)):
        if r.get('dev') or r.get('rank') is None:
            continue
        out[r['id']] = r['rank']
    return out


def probe(args):
    meta, = args
    from frame import decode
    path = CORPUS / 'replays' / f"{meta['game_id']}.replay"
    if not path.exists():
        return []
    try:
        g = decode(path)
    except Exception:
        return []
    ev = g['events']
    rounds = g['rounds']
    deaths = {(d['id']): d for d in ev['deaths']}
    out = []
    for s in ev['splits']:
        r0 = s['round']
        r1 = min(r0 + 10, len(rounds) - 1)
        parent, child = s['parent'], s['child']
        pd = deaths.get(parent)
        cd = deaths.get(child)
        pd10 = bool(pd and r0 <= pd['round'] <= r0 + 10)
        cd10 = bool(cd and r0 <= cd['round'] <= r0 + 10)
        # lineage length kept at r0+10 (or at death): use rounds snapshots
        par_len = child_len = 0
        b = rounds[r1].get(parent)
        if b is not None and b[0] == s['team']:
            par_len = len(b[1])
        b = rounds[r1].get(child)
        if b is not None and b[0] == s['team']:
            child_len = len(b[1])
        regret = pd10 and (par_len + child_len) < s['before']
        phase = 'r0-50' if r0 <= 50 else 'r50-150' if r0 <= 150 else 'r150+'
        out.append(dict(game=g['id'], map=g['map'], round=r0, phase=phase, team=s['team'],
                        before=s['before'], parent_died10=pd10, child_died10=cd10,
                        kept=par_len + child_len, regret=int(regret)))
    return out


def main():
    import argparse
    import multiprocessing as mp
    import collections, random
    ap = argparse.ArgumentParser()
    ap.add_argument('--since', default='2026-10-02T00:00')
    ap.add_argument('--per-team', type=int, default=3)
    ap.add_argument('--out', default='build/nara/split_opp.jsonl')
    ap.add_argument('--jobs', type=int, default=6)
    a = ap.parse_args()
    watch = set(cohorts())
    sel = [r for r in map(json.loads, open(CORPUS / 'index.jsonl'))
           if a.since <= r['started_at'] and r.get('status') == 'completed'
           and (r['team_a'] in watch or r['team_b'] in watch)]
    cnt = collections.Counter()
    random.seed(21)
    random.shuffle(sel)
    picked = []
    for r in sorted(sel, key=lambda x: x['started_at'], reverse=True):
        if max(cnt[r['team_a']], cnt[r['team_b']]) < a.per_team:
            picked.append(r)
            cnt[r['team_a']] += 1
            cnt[r['team_b']] += 1
    print(f'{len(sel)} in-scope; probing {len(picked)}', file=sys.stderr)
    with mp.Pool(a.jobs) as pool:
        rows = [x for chunk in pool.imap_unordered(probe, ((m,) for m in picked), chunksize=1) for x in chunk]
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, 'w') as f:
        for r in rows:
            f.write(json.dumps(r) + '\n')
    # rollup
    agg = collections.defaultdict(lambda: [0, 0, 0])
    for r in rows:
        k = (r['map'], r['phase'])
        agg[k][0] += 1
        agg[k][1] += r['regret']
        agg[k][2] += int(r['parent_died10'])
    print(f"{'map':<20} {'phase':<8} {'splits':>7} {'regret':>7} {'%':>6} {'pdied10%':>8}")
    for k in sorted(agg):
        n, reg, pd = agg[k]
        if n >= 20:
            print(f"{k[0]:<20} {k[1]:<8} {n:>7} {reg:>7} {100*reg/n:>5.0f}% {100*pd/n:>7.0f}%")


if __name__ == '__main__':
    main()
