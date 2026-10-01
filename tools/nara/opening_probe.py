"""Nara opening probe: S-1 Q3's opening components, pre vs post era, same code both sides.

Per side-game: pearls@50/@100, bed_pearls@50/@100, splits@50, deaths@50, total@100, longest@100,
queen survival/length columns (reuses queen logic), plus round_limit and result.
"""
import json, sys, glob
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'tools' / 'leviathan'))
sys.path.insert(0, str(ROOT / 'tools' / 'analysis' / 'features'))

CORPUS = ROOT / 'public_replays' / 'corpus'
CUT = '2026-10-01T09:23'


def cohorts():
    lad = sorted(glob.glob(str(CORPUS / 'ladder' / '*.json')))[-1]
    out = {}
    for r in json.load(open(lad)):
        if r.get('dev'):
            continue
        rank = r['rank']
        c = 'top10' if rank <= 10 else 'r11_30' if rank <= 30 else 'r31_50' if rank <= 50 else 'other'
        out[r['id']] = dict(rank=rank, cohort=c, name=r['name'])
    return out


def side_row(g, meta, team_id, coh):
    t = 'A' if meta['team_a'] == team_id else 'B'
    ev = g['events']
    rounds = g['rounds']
    n_init = g['n_initial']
    q0 = min(i for i in rounds[0] if rounds[0][i][0] == t)
    row = dict(game=g['id'], team=team_id, side=t, map=g['map'], started=meta['started_at'],
               era='post' if meta['started_at'] >= CUT else 'pre',
               won=(g['winner'] == t), round_limit=g['reason'] in ('longest', 'total', 'tie'),
               cohort=coh.get(team_id, {}).get('cohort', 'other'), rank=coh.get(team_id, {}).get('rank'),
               name=coh.get(team_id, {}).get('name', str(team_id)))
    for c in (50, 100):
        row[f'pearls@{c}'] = sum(1 for e in ev['eats'] if e['team'] == t and e['round'] <= c)
        row[f'bed_pearls@{c}'] = sum(1 for e in ev['eats'] if e['team'] == t
                                     and e['origin'] == 'bed' and e['round'] <= c)
    row['splits@50'] = sum(1 for s in ev['splits'] if s['team'] == t and s['round'] <= 50)
    row['deaths@50'] = sum(1 for d in ev['deaths'] if d['team'] == t and d['round'] <= 50)
    bodies = rounds[min(100, len(rounds) - 1)]
    lens = [len(b[1]) for i, (tmm, b) in bodies.items() if tmm == t] or [0]
    row['longest@100'] = max(lens)
    row['total@100'] = sum(lens)
    # sprint usage: surviving multi-step moves with paid>0 vs free (era signature + behavior)
    row['q_death_round'] = next((d['round'] for d in ev['deaths'] if d['id'] == q0), None)
    for c in (50, 250, 490):
        r = min(c, len(rounds) - 1)
        b = rounds[r].get(q0)
        row[f'q_len@{c}'] = len(b[1]) if b else 0
    return row


def probe(args):
    meta, coh = args
    from frame import decode
    path = CORPUS / 'replays' / f"{meta['game_id']}.replay"
    if not path.exists():
        return []
    try:
        g = decode(path)
    except Exception as e:
        return [dict(game=meta['game_id'], error=f'{type(e).__name__}: {e}')]
    return [side_row(g, meta, tid, coh) for tid in (meta['team_a'], meta['team_b'])]


def main():
    import argparse
    import multiprocessing as mp
    import collections, random
    ap = argparse.ArgumentParser()
    ap.add_argument('--since', default='2026-09-30T00:00')
    ap.add_argument('--until', default='2026-10-01T05:54')
    ap.add_argument('--per-team', type=int, default=6)
    ap.add_argument('--out', required=True)
    ap.add_argument('--jobs', type=int, default=8)
    a = ap.parse_args()
    coh = cohorts()
    watch = set(coh) | {7}
    rows = [json.loads(l) for l in open(CORPUS / 'index.jsonl')]
    sel = [r for r in rows if a.since <= r['started_at'] < a.until and r.get('status') == 'completed'
           and (r['team_a'] in watch or r['team_b'] in watch)]
    cnt = collections.Counter()
    random.seed(2)
    random.shuffle(sel)
    picked = []
    for r in sorted(sel, key=lambda x: x['started_at'], reverse=True):
        if max(cnt[r['team_a']], cnt[r['team_b']]) < a.per_team:
            picked.append(r)
            cnt[r['team_a']] += 1
            cnt[r['team_b']] += 1
    print(f'{len(sel)} in-scope; probing {len(picked)}', file=sys.stderr)
    with mp.Pool(a.jobs) as pool:
        out = [x for chunk in pool.imap_unordered(probe, ((m, coh) for m in picked), chunksize=1) for x in chunk]
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, 'w') as f:
        for r in out:
            f.write(json.dumps(r) + '\n')
    print(f'wrote {len(out)} rows', file=sys.stderr)


if __name__ == '__main__':
    main()
