"""Nara era-shift probe: endgame material, death profile, sprint usage — pre vs post, same code.

Per side-game:
  units/total/longest at 100/250/490 (from rounds snapshots)
  deaths by cause to r150 (+ dragon-turns to r150 for rates), length lost to r150
  sprint usage: moves, moves with >=2/>=3 steps, total steps, total paid
  pearls@250; queen columns (q_death_round); round_limit
Winner is NOT recorded here (decoded winner is wrong post-era); join the index by game id.
"""
import json, sys, glob
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'tools' / 'leviathan'))
sys.path.insert(0, str(ROOT / 'tools' / 'analysis' / 'features'))

CORPUS = ROOT / 'public_replays' / 'corpus'
CUT = '2026-10-01T09:23'
CAUSES = ('wall', 'self', 'body', 'h2h', 'invalid')


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
    row = dict(game=g['id'], team=team_id, side=t, map=g['map'], started=meta['started_at'],
               era='post' if meta['started_at'] >= CUT else 'pre',
               cohort=coh.get(team_id, {}).get('cohort', 'other'),
               name=coh.get(team_id, {}).get('name', str(team_id)),
               round_limit=g['reason'] in ('longest', 'total', 'tie'))
    for c in (100, 250, 490):
        r = min(c, len(rounds) - 1)
        lens = [len(body) for i, (tm, body) in rounds[r].items() if tm == t]
        row[f'units@{c}'], row[f'total@{c}'], row[f'longest@{c}'] = (len(lens), sum(lens), max(lens)) if lens else (0, 0, 0)
    # deaths to 150 with dragon-turn denominator
    dt150 = 0
    for r in range(min(150, len(rounds))):
        dt150 += sum(1 for i, (tm, _) in rounds[r].items() if tm == t)
    row['dt150'] = dt150
    for cause in CAUSES:
        row[f'd_{cause}@150'] = sum(1 for d in ev['deaths'] if d['team'] == t and d['round'] <= 150 and d['cause'] == cause)
    row['d_lenlost@150'] = sum(d['length'] for d in ev['deaths'] if d['team'] == t and d['round'] <= 150)
    row['pearls@250'] = sum(1 for e in ev['eats'] if e['team'] == t and e['round'] <= 250)
    # sprint usage (surviving moves only)
    dead = {(d['round'], d['id']) for d in ev['deaths']}
    nm = nm2 = nm3 = tsteps = tpaid = 0
    for a in ev['actions']:
        if a['kind'] != 'move' or a.get('steps', 0) < 1 or (a['round'], a['id']) in dead:
            continue
        nm += 1
        s = a['steps']
        if s >= 2:
            nm2 += 1
        if s >= 3:
            nm3 += 1
        tsteps += s
        tpaid += a.get('paid', 0)
    row.update(moves=nm, mv_ge2=nm2, mv_ge3=nm3, steps=tsteps, paid=tpaid)
    q0 = min(i for i in rounds[0] if rounds[0][i][0] == t)
    row['q_death_round'] = next((d['round'] for d in ev['deaths'] if d['id'] == q0), None)
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
    ap.add_argument('--since', required=True)
    ap.add_argument('--until', default='2100')
    ap.add_argument('--per-team', type=int, default=8)
    ap.add_argument('--out', required=True)
    ap.add_argument('--jobs', type=int, default=8)
    a = ap.parse_args()
    coh = cohorts()
    watch = set(coh) | {7}
    sel = [r for r in map(json.loads, open(CORPUS / 'index.jsonl'))
           if a.since <= r['started_at'] < a.until and r.get('status') == 'completed'
           and (r['team_a'] in watch or r['team_b'] in watch)]
    cnt = collections.Counter()
    random.seed(5)
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
