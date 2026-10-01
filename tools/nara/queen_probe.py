"""Nara queen anatomy: per-side tracking of the ORIGINAL queen (lowest initial id) through the game.

Emits one row per side-game:
  team, cohort, map, era, won, round_limit
  q_death_round (None = survived), q_alive490, q_len@{50,100,250,490} (0 if dead), q_max_len
  q_eats (pearls eaten by the queen robot), q_head_moves (rounds with a head-cell change)
  longest@490, total@490, n@490
"""
import json, sys, glob
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'tools' / 'leviathan'))
sys.path.insert(0, str(ROOT / 'tools' / 'analysis' / 'features'))

CORPUS = ROOT / 'public_replays' / 'corpus'
CUT = '2026-10-01T09:23'   # first post-change game (rules switch in the 05:54-09:23 maintenance window)
CKPTS = (50, 100, 250, 490)


def cohorts():
    lad = sorted(glob.glob(str(CORPUS / 'ladder' / '*.json')))[-1]
    rows = json.load(open(lad))
    out = {}
    for r in rows:
        if r.get('dev'):
            continue
        rank = r['rank']
        c = 'top10' if rank <= 10 else 'r11_30' if rank <= 30 else 'r31_50' if rank <= 50 else 'other'
        out[r['id']] = dict(rank=rank, cohort=c, name=r['name'])
    return out


def side_row(g, meta, team_id, coh):
    t = 'A' if meta['team_a'] == team_id else 'B'
    rounds = g['rounds']
    n_init = g['n_initial']
    first = rounds[0]
    q0 = min(i for i in first if first[i][0] == t)
    died = next((d['round'] for d in g['events']['deaths'] if d['id'] == q0), None)
    row = dict(game=g['id'], team=team_id, side=t, map=g['map'], started=meta['started_at'],
               era='post' if meta['started_at'] >= CUT else 'pre',
               won=(g['winner'] == t), round_limit=g['reason'] in ('longest', 'total', 'tie'),
               cohort=coh.get(team_id, {}).get('cohort', 'other'), rank=coh.get(team_id, {}).get('rank'),
               name=coh.get(team_id, {}).get('name', str(team_id)), q0=q0, q_death_round=died)
    for c in CKPTS:
        r = min(c, len(rounds) - 1)
        body = rounds[r].get(q0)
        row[f'q_len@{c}'] = len(body[1]) if body else 0
    lens = [len(rounds[r][q0][1]) for r in range(len(rounds)) if q0 in rounds[r]]
    row['q_max_len'] = max(lens) if lens else 0
    row['q_eats'] = sum(1 for e in g['events']['eats'] if e['id'] == q0)
    hm = 0
    prev = None
    for r in range(len(rounds)):
        b = rounds[r].get(q0)
        head = b[1][0] if b else None
        if head is not None and prev is not None and head != prev:
            hm += 1
        if head is not None:
            prev = head
        if b is None:
            prev = None
    row['q_head_moves'] = hm
    fin = g['final'][t]
    row['longest@490'], row['total@490'], row['n@490'] = fin['longest'], fin['total'], fin['units']
    # does the queen hold top rank in the team at the end?
    last = rounds[-1]
    if q0 in last:
        my = len(last[q0][1])
        row['q_is_longest490'] = int(my == fin['longest'])
        row['q_share490'] = round(my / max(1, fin['total']), 3)
    else:
        row['q_is_longest490'] = 0
        row['q_share490'] = 0.0
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
    ap = argparse.ArgumentParser()
    ap.add_argument('--since', default='2026-10-01T09:23')
    ap.add_argument('--until', default='2100')
    ap.add_argument('--per-team', type=int, default=10)
    ap.add_argument('--out', default='build/nara/queen_post.jsonl')
    ap.add_argument('--jobs', type=int, default=8)
    a = ap.parse_args()
    coh = cohorts()
    watch = set(coh) | {7}
    rows = [json.loads(l) for l in open(CORPUS / 'index.jsonl')]
    sel = [r for r in rows if a.since <= r['started_at'] < a.until and r.get('status') == 'completed'
           and (r['team_a'] in watch or r['team_b'] in watch)]
    # cap per team so one farm does not eat the sample
    import collections, random
    random.seed(1)
    cnt = collections.Counter()
    random.shuffle(sel)
    picked = []
    for r in sorted(sel, key=lambda x: x['started_at'], reverse=True):
        k = max(cnt[r['team_a']], cnt[r['team_b']])
        if k < a.per_team:
            picked.append(r)
            cnt[r['team_a']] += 1
            cnt[r['team_b']] += 1
    print(f'{len(sel)} in-scope games since {a.since}; probing {len(picked)}', file=sys.stderr)
    with mp.Pool(a.jobs) as pool:
        out = [x for chunk in pool.imap_unordered(probe, ((m, coh) for m in picked), chunksize=1) for x in chunk]
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, 'w') as f:
        for r in out:
            f.write(json.dumps(r) + '\n')
    print(f'wrote {len(out)} side rows to {a.out}', file=sys.stderr)


if __name__ == '__main__':
    main()
