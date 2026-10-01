"""Rules-era signals per replay (unswbc 1.2.3 change, 1 Oct 2026).

  python3 tools/antioch/era.py <replay> [...]          # one JSON line per replay
  python3 tools/antioch/era.py --index index.jsonl --dir public_replays/corpus/replays --out era.parquet [--jobs N]

Signals (each independent of the verdict text, which the replay does not store):
  sprint_old / sprint_new: sprint moves (steps >= 2, length before >= 5, no eat, survived) whose segment cost matches
    only the old rule (k - 1) or only the new rule (max(0, k - ceil(L/4)), at least 2 kept). L < 5 moves are ambiguous.
  queen_a / queen_b: the 4th int32 of each side's TeamStanding (new in 1.2.3; the old schema has three): the length of
    the team's original lowest-id dragon at the end, 0 if it has died (no succession) or the replay predates the field.
  res_winner / res_reason: the engine's own winner ('A' / 'B' / 'draw') and end reason (0 = elimination, 1 = round
    limit), read from the GameResult struct. The s1 decoder infers the winner with the old tiebreak instead.
era = 'post' if sprint_new > 0 and sprint_old == 0, 'pre' if sprint_old > 0 and sprint_new == 0, else 'mixed'/'none'.
"""
import json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def header(path):
    from tools.analysis.features import frame as F
    root = F._reader(path).object(0, 0)
    res = root.child(4)
    side = [res.child(k) for k in (0, 1)]
    # GameResult data section: terminated (bit 0), endReason u16 @2, union tag u16 @4 (1 = winner), winner u16 @6 (0 = a)
    win = ('A', 'B')[res.num(6, 'H')] if res.num(4, 'H') == 1 else 'draw'
    return dict(version=root.num(0, 'I'), res_winner=win, res_reason=res.num(2, 'H'),
                units_a=side[0].num(0), longest_a=side[0].num(4), total_a=side[0].num(8), queen_a=side[0].num(12),
                units_b=side[1].num(0), longest_b=side[1].num(4), total_b=side[1].num(8), queen_b=side[1].num(12))


def signals(path):
    from tools.analysis.features.frame import decode
    out = dict(file=str(path), game=Path(path).stem)
    try:
        out.update(header(path))
        g = decode(path)
    except Exception as e:
        out['error'] = f'{type(e).__name__}: {e}'
        return out
    eats = {(e['round'], e['id']) for e in g['events']['eats']}
    dead = {(d['round'], d['id']) for d in g['events']['deaths']}
    # length before each action: the snapshot at the start of the round
    old = new = amb = 0
    k_max = 0
    for a in g['events']['actions']:
        if a.get('kind') != 'move' or a.get('steps', 0) < 2 or 'paid' not in a:
            continue
        if (a['round'], a['id']) in eats or (a['round'], a['id']) in dead:
            continue
        snap = g['rounds'][a['round']] if a['round'] < len(g['rounds']) else {}
        if a['id'] not in snap:
            continue
        L, k, paid = len(snap[a['id']][1]), a['steps'], a['paid']
        k_max = max(k_max, k)
        p_old, p_new = k - 1, max(0, k - math.ceil(L / 4))
        if p_old == p_new:
            amb += 1
        elif paid == p_new:
            new += 1
        elif paid == p_old:
            old += 1
    out.update(sprint_old=old, sprint_new=new, sprint_amb=amb, sprint_kmax=k_max, last_round=g['last_round'],
               dec_winner=g['winner'], dec_reason=g['reason'],
               era='post' if new and not old else 'pre' if old and not new else 'mixed' if old and new else 'none')
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('paths', nargs='*')
    ap.add_argument('--index'); ap.add_argument('--dir'); ap.add_argument('--out')
    ap.add_argument('--since', default='')
    ap.add_argument('--jobs', type=int, default=4)
    a = ap.parse_args()
    if not a.index:
        for p in a.paths:
            print(json.dumps(signals(p)))
        return
    import multiprocessing as mp
    import pandas as pd
    idx = [json.loads(l) for l in open(a.index)]
    idx = [r for r in idx if (r.get('finished_at') or '') >= a.since]
    paths = [Path(a.dir) / f"{r['game_id']}.replay" for r in idx]
    paths = [p for p in paths if p.exists()]
    with mp.get_context('fork').Pool(a.jobs) as pool:
        rows = pool.map(signals, paths, chunksize=8)
    df = pd.DataFrame(rows)
    meta = pd.DataFrame(idx)[['game_id', 'finished_at', 'team_a', 'team_b', 'map_name', 'winner', 'ranked']]
    meta['game'] = meta.game_id.astype(str)
    df = df.merge(meta, on='game', how='left')
    df.to_parquet(a.out, index=False)
    print(f'{len(df)} rows -> {a.out}')


if __name__ == '__main__':
    main()
