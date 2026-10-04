"""Nara queen cause+exposure probe: what kills field queens per map, and how exposed
Cutlery's surviving queen is (min torus-Manhattan distance to enemy heads at checkpoints).
"""
import json, sys, glob, os
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'tools' / 'leviathan'))
sys.path.insert(0, str(ROOT / 'tools' / 'analysis' / 'features'))

CORPUS = Path(os.environ.get('NARA_CORPUS', str(ROOT / 'public_replays' / 'corpus')))
CKPTS = (100, 200, 300)


def cohorts():
    lad = sorted(glob.glob(str(CORPUS / 'ladder' / '*.json')))[-1]
    out = {}
    for r in json.load(open(lad)):
        if r.get('dev') or r.get('rank') is None:
            continue
        rank = r['rank']
        c = 'top10' if rank <= 10 else 'r11_30' if rank <= 30 else 'r31_50' if rank <= 50 else 'other'
        out[r['id']] = dict(rank=rank, cohort=c, name=r['name'])
    return out


def torus_man(a, b, W, H):
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    return min(dx, W - dx) + min(dy, H - dy)


def side_row(g, meta, team_id, coh):
    t = 'A' if meta['team_a'] == team_id else 'B'
    ev = g['events']
    rounds = g['rounds']
    W, H = g['W'], g['H']
    q0 = min(i for i in rounds[0] if rounds[0][i][0] == t)
    d = next((x for x in ev['deaths'] if x['id'] == q0), None)
    row = dict(game=g['id'], team=team_id, side=t, map=g['map'], map_hash=meta.get('map_hash', '')[:10],
               started=meta['started_at'],
               cohort=coh.get(team_id, {}).get('cohort', 'other'),
               name=coh.get(team_id, {}).get('name', str(team_id)),
               q_death_round=d['round'] if d else None,
               q_death_cause=d['cause'] if d else None,
               q_killer_enemy=bool(d and d.get('killer_team') is not None and d['killer_team'] != d['team']),
               q_len490=len(rounds[min(490, len(rounds) - 1)][q0][1]) if q0 in rounds[min(490, len(rounds) - 1)] else 0,
               round_limit=g['reason'] in ('longest', 'total', 'tie', 'queen'),
               last_round=len(rounds) - 2)
    for c in CKPTS:
        r = min(c, len(rounds) - 1)
        qb = rounds[r].get(q0)
        if qb is None:
            row[f'q_exp@{c}'] = None
        else:
            qh = qb[1][0]
            eh = [b[0] for i, (tm, b) in rounds[r].items() if tm != t]
            row[f'q_exp@{c}'] = min((torus_man(qh, x, W, H) for x in eh), default=None)
        # team-mate median exposure at the same checkpoint (queen-specific vs team style)
        mates = [b[0] for i, (tm, b) in rounds[r].items() if tm == t and i != q0]
        if qb is not None and mates:
            eh = [b[0] for i, (tm, b) in rounds[r].items() if tm != t]
            if eh:
                import statistics
                row[f'team_exp@{c}'] = statistics.median(min(torus_man(m, x, W, H) for x in eh) for m in mates)
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
    ap.add_argument('--since', default='2026-10-01T09:23')
    ap.add_argument('--until', default='2100')
    ap.add_argument('--per-team', type=int, default=10)
    ap.add_argument('--teams', default='')
    ap.add_argument('--out', required=True)
    ap.add_argument('--jobs', type=int, default=8)
    a = ap.parse_args()
    coh = cohorts()
    watch = set(coh) | {7, 306}
    only = {int(x) for x in a.teams.split(',') if x}
    sel = [r for r in map(json.loads, open(CORPUS / 'index.jsonl'))
           if a.since <= r['started_at'] < a.until and r.get('status') == 'completed'
           and ((r['team_a'] in watch or r['team_b'] in watch)
                and (not only or r['team_a'] in only or r['team_b'] in only))]
    cnt = collections.Counter()
    random.seed(11)
    random.shuffle(sel)
    picked = []
    for r in sorted(sel, key=lambda x: x['started_at'], reverse=True):
        if max(cnt[r['team_a']], cnt[r['team_b']]) < a.per_team or r['team_a'] == 306 or r['team_b'] == 306:
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
