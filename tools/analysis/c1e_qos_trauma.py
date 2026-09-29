#!/usr/bin/env python3
"""C1-E follow-ups (b) Queen Of Spades and (c) Trauma: the same anatomy as the Schooltime
spec (tools/analysis/c1e_schooltime.py), pooled over top-ten ranked wins on each map.

  python tools/analysis/c1e_qos_trauma.py
"""
import collections, json, statistics, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.analysis.c1e_schooltime import analyse


def top_ten_wins(map_name, want=10):
    rows = [json.loads(l) for l in open(ROOT / 'build/c1e/ranked_games.jsonl')]
    lad = sorted((ROOT / 'public_replays/corpus/ladder').glob('*.json'))
    snaps = [(datetime.strptime(p.stem, '%Y%m%dT%H%M%SZ').replace(tzinfo=timezone.utc),
              {e['id']: e['rank'] for e in json.load(open(p)) if not e.get('dev')}) for p in lad]
    def rank_at(tid, when):
        ranks = snaps[0][1]
        for stamp, r in snaps:
            if stamp <= when:
                ranks = r
            else:
                break
        return ranks.get(tid)
    out, teams = [], collections.Counter()
    for r in rows:
        if r['map_name'] != map_name:
            continue
        when = datetime.fromisoformat(r['started_at'].replace('Z', '+00:00'))
        for side, team in (('A', r['team_a']), ('B', r['team_b'])):
            rank = rank_at(team, when)
            if rank is not None and rank <= 10 and r['winner'] == side.lower() and teams[team] < 4:
                out.append((r['game_id'], side, team, rank))
                teams[team] += 1
    return out[:want]


def pool(sel):
    return dict(games=len(sel), teams=sorted({r['team'] for r in sel}),
                units_r100=[r['units'][100] for r in sel], splits=[r['splits_n'] for r in sel],
                pearls_r100=[r['pearls_r100'] for r in sel],
                first_pearl=[r['first_pearl'] for r in sel], first_spawn=[r['first_spawn'] for r in sel],
                split_bins={b: statistics.median([r['split_bins'].get(b, 0) for r in sel]) for b in range(0, 100, 10)},
                units_curve={rr: statistics.median([r['units'][rr] for r in sel])
                             for rr in (0, 5, 20, 40, 50, 60, 70, 80, 90, 100, 200)},
                child_len={k: sum(r['child_len'].get(k, 0) for r in sel) for r in [sel[0]] for k in r['child_len']},
                child_disp=[r['child_displacement_med'] for r in sel],
                children_crossed=[r['children_crossed_portal'] for r in sel],
                newborn_deaths10=[r['newborn_deaths10'] for r in sel],
                pair_within3={rr: statistics.median([r['pair_cov'][rr]['within3'] for r in sel]) for rr in (25, 50, 100)},
                pairs=sel[0]['pairs'], transits=[sum(r['transits'].values()) for r in sel],
                nearest_ally_med=[r['nearest_ally_med'] for r in sel],
                len2_r100=[r['len100']['len2'] for r in sel], big=[r['len100']['big'] for r in sel],
                crown=[r['len100']['crown'] for r in sel],
                heads_on_bed=[r['heads_on_bed'] for r in sel], beds_covered=[r['beds_covered'] for r in sel],
                beds_n=sel[0]['beds_n'], deaths=[sum(r['deaths_by_cause'].values()) for r in sel],
                causes=dict(sum((collections.Counter(r['deaths_by_cause']) for r in sel), collections.Counter())))


def main():
    for name in ('Queen Of Spades', 'Trauma'):
        games = top_ten_wins(name)
        print(f'== {name}: {len(games)} wins', [(g[0], g[2], g[3]) for g in games])
        rows = [analyse(*g) for g in games]
        for r in rows:
            print(json.dumps(r))
        print(f'POOLED-{name} ' + json.dumps(pool(rows)))


if __name__ == '__main__':
    main()
