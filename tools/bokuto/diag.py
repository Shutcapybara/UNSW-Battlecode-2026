#!/usr/bin/env python3
"""Per-game diagnostics from replays: queen fate, material curve, pocket harvesting, deaths, conversion.

    python3 tools/bokuto/diag.py BOT REPLAY... [--csv out.csv]

BOT is the bot name prefix whose side is "us" (botA/botB text in the replay header). Prints one line per game and an
aggregate; the aggregate compares us with the opponent on the same games.
"""
import sys, collections, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools/analysis/features'))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools/hub/vendor/ouroboros'))
import frame


def pruned_cells(nbr):
    adj = {c: [n for n in nbr[c] if n is not None] for c in nbr}
    alive = set(nbr); pruned = set(); ch = True
    while ch:
        ch = False
        for c in list(alive):
            if sum(1 for n in adj[c] if n in alive) <= 1:
                alive.discard(c); pruned.add(c); ch = True
    return pruned


def side_stats(g, t, pruned):
    ids = [i for i, (tt, b) in g['rounds'][0].items() if tt == t]
    qid = min(ids)
    qd = [d for d in g['events']['deaths'] if d['id'] == qid]
    fin = g['final'][t]
    deaths = [d for d in g['events']['deaths'] if d['team'] == t]
    eats = [e for e in g['events']['eats'] if e['team'] == t]
    splits = [s for s in g['events']['splits'] if s['team'] == t]
    curve = {}
    for r in (50, 100, 150, 200, 250, 300, 350, 400, 450, 499):
        if r < len(g['rounds']):
            ds = [len(b) for (tt, b) in g['rounds'][r].values() if tt == t]
            curve[r] = (len(ds), sum(ds), max(ds) if ds else 0)
        else:
            curve[r] = (0, 0, 0)
    return dict(
        queen_len=fin['queen'], queen_death=(qd[0]['round'], qd[0]['cause'], qd[0]['length'], qd[0].get('killer_team')) if qd else None,
        units=fin['units'], longest=fin['longest'], total=fin['total'],
        deaths=len(deaths), death_causes=collections.Counter(d['cause'] for d in deaths),
        branch_deaths=sum(1 for d in deaths if d['head'] in pruned),
        eats=len(eats), eat_origin=collections.Counter(e['origin'] for e in eats),
        branch_eats=sum(1 for e in eats if e['cell'] in pruned),
        splits=len(splits), splits_late=sum(1 for s in splits if s['round'] >= 350),
        sendbacks=sum(1 for s in splits if s['round'] + 1 < len(g['rounds']) and s['child'] in g['rounds'][s['round'] + 1]
                      and g['rounds'][s['round'] + 1][s['child']][1][0] in pruned),
        curve=curve)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('bot'); ap.add_argument('replays', nargs='+')
    args = ap.parse_args()
    agg = collections.defaultdict(float); n = 0
    aggo = collections.defaultdict(float)
    wins = 0; reasons = collections.Counter()
    for f in args.replays:
        try:
            g = frame.decode(f)
        except Exception as e:
            print('skip', f, e); continue
        us = 'A' if args.bot in g['botA'] else 'B'
        them = 'B' if us == 'A' else 'A'
        pruned = pruned_cells(g['nbr'])
        s = side_stats(g, us, pruned); o = side_stats(g, them, pruned)
        res = 'W' if g['winner'] == us else ('D' if g['winner'] == 'draw' else 'L')
        wins += res == 'W'; reasons[(res, g['reason'])] += 1; n += 1
        qd = s['queen_death']
        name = Path(f).stem.replace('live+', '')[:46]
        print(f"{name:<46} {res} {g['reason'][:5]:<5} Q{'alive' + str(s['queen_len']) if not qd else 'd' + str(qd[0]) + qd[1][:4] + 'L' + str(qd[2])}"
              f" | long {s['longest']:>2}v{o['longest']:<2} tot {s['total']:>3}v{o['total']:<3} u {s['units']:>2}v{o['units']:<2}"
              f" | eats {s['eats']:>3}v{o['eats']:<3} (br {s['branch_eats']:>3}v{o['branch_eats']:<3}) deaths {s['deaths']:>3}v{o['deaths']:<3} (br {s['branch_deaths']}v{o['branch_deaths']})"
              f" splits {s['splits']:>3}v{o['splits']:<3} sb {s['sendbacks']} late {s['splits_late']}v{o['splits_late']}"
              f" | r200 {s['curve'][200][1]}v{o['curve'][200][1]} r400 {s['curve'][400][1]}v{o['curve'][400][1]}")
        for k in ('longest', 'total', 'units', 'eats', 'branch_eats', 'deaths', 'branch_deaths', 'splits', 'splits_late', 'sendbacks'):
            agg[k] += s[k]; aggo[k] += o[k]
        agg['queen_alive'] += s['queen_death'] is None; aggo['queen_alive'] += o['queen_death'] is None
        if qd: agg['queen_death_round'] += qd[0]; agg['qd_n'] += 1
        for r in (200, 400):
            agg[f'tot{r}'] += s['curve'][r][1]; aggo[f'tot{r}'] += o['curve'][r][1]
    if not n:
        return
    print(f"\n{n} games, {wins} wins ({wins / n:.2f}); reasons {dict(reasons)}")
    print('mean per game         us    them')
    for k in ('queen_alive', 'longest', 'total', 'units', 'tot200', 'tot400', 'eats', 'branch_eats', 'deaths', 'branch_deaths', 'splits', 'splits_late', 'sendbacks'):
        print(f"  {k:<16} {agg[k] / n:7.2f} {aggo[k] / n:7.2f}")
    if agg['qd_n']:
        print(f"  queen death round (when dead): {agg['queen_death_round'] / agg['qd_n']:.0f}")


if __name__ == '__main__':
    main()
