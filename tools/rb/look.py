#!/usr/bin/env python3
"""rb replay ledger: where a team's pearls and length go, per game and aggregated.

    python tools/rb/look.py REPLAY [REPLAY ...] [--team-bot aline] [--per-game] [--board ROUND]

For the team whose bot path contains --team-bot (default "aline"): pearls eaten by origin (bed / ally corpse /
enemy corpse), length paid for sprints, deaths by cause with the length lost, pearls our deaths dropped and who ate
them, dragon-turns per pearl, bed pearls the enemy took, bed pearls left lying, units/total/longest at checkpoints.
"""
from __future__ import annotations

import argparse, collections, statistics, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.analysis.features.frame import decode  # noqa: E402

CP = (50, 100, 150, 250, 499)


def ledger(path, tag):
    f = decode(path)
    us = 'A' if tag in f['botA'] else 'B' if tag in f['botB'] else None
    if us is None:
        return None
    them = 'B' if us == 'A' else 'A'
    ev = f['events']
    L = collections.Counter()
    L['won'] = f['winner'] == us
    L['opp'] = Path(f['botB' if us == 'A' else 'botA']).name
    L['map'] = f['map']
    for e in ev['eats']:
        side = 'us' if e['team'] == us else 'them'
        o = e['origin']
        L[f'{side}_eat_{o}'] += 1
        for c in CP:
            if e['round'] <= c:
                L[f'{side}_eat@{c}'] += 1
    for a in ev['actions']:
        if a['team'] == us:
            L['us_turns'] += 1
            if a['kind'] == 'move' and a['steps'] > 1:
                L['us_sprints'] += 1; L['us_sprint_len'] += a['steps'] - 1
                if a['round'] < 100:
                    L['us_sprint_len<100'] += a['steps'] - 1
            if a['kind'] == 'split':
                L['us_splits'] += 1
    for d in ev['deaths']:
        if d['team'] != us:
            if d.get('killer_team') == us:
                L['kills'] += 1
            continue
        L[f"death_{d['cause']}"] += 1
        L[f"deathlen_{d['cause']}"] += d['length']
        L['deathlen'] += d['length']
        if d['cause'] in ('h2h', 'body') and d.get('killer_team') == them:
            L['death_enemy'] += 1
        if d['length'] >= 8:
            L[f"bigdeath_{d['cause']}"] += 1
            L['bigdeathlen'] += d['length']
    # snapshots
    for c in CP:
        r = f['rounds'][min(c, len(f['rounds']) - 1)]
        for side, t in (('us', us), ('them', them)):
            lens = [len(b) for tm, b in r.values() if tm == t]
            L[f'{side}_units@{c}'] = len(lens)
    for side, t in (('us', us), ('them', them)):
        L[f'{side}_longest'] = f['final'][t]['longest']; L[f'{side}_total'] = f['final'][t]['total']
    return L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('replays', nargs='+')
    ap.add_argument('--team-bot', default='aline')
    ap.add_argument('--per-game', action='store_true')
    a = ap.parse_args()
    rows = [x for x in (ledger(p, a.team_bot) for p in a.replays) if x]
    if a.per_game:
        for L in rows:
            print(f"{L['map'][:14]:14s} {L['opp'][:14]:14s} {'W' if L['won'] else 'L'} eat@100 {L['us_eat@100']:3d}/{L['them_eat@100']:3d} "
                  f"eat {L['us_eat@499']:4d}/{L['them_eat@499']:4d} longest {L['us_longest']:3d}/{L['them_longest']:3d} total {L['us_total']:4d}/{L['them_total']:4d} "
                  f"deaths w{L['death_wall']} s{L['death_self']} b{L['death_body']} h{L['death_h2h']} lenlost {L['deathlen']} big {L['bigdeathlen']} sprint {L['us_sprint_len']}")
    keys = sorted({k for L in rows for k in L if k not in ('opp', 'map')})
    n = len(rows)
    print(f'{n} games, won {sum(L["won"] for L in rows)}')
    for k in keys:
        v = [float(L[k]) for L in rows]
        print(f'  {k:24s} mean {sum(v) / n:8.2f}  median {statistics.median(v):8.1f}')


if __name__ == '__main__':
    main()
