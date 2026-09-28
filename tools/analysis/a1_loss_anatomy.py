"""A1 — loss anatomy on the live record (handoff §3.1).

Per source (own submission) with >= MIN_N verified controlled FIELD games:
loss split by reason, map class and opponent; median elimination round; longest margin in
round-limit losses; stage medians for wins vs losses (ours and opponent's); deaths per 1k turns
by cause; newborn deaths; first stage at which the eventual loser trails on total length.

Unit of independence: the game. All arms are side A. Verified games only; opponents pooled
across their submissions EXCEPT where noted (opponent_submission column shown in the opponent
table so version mixing is visible).
"""
import statistics
from collections import Counter, defaultdict

from live_load import STAGES, field_controlled, load, map_class, per_1k, stage

MIN_N = 20


def med(vs, nd=1):
    vs = [v for v in vs if v is not None]
    return round(statistics.median(vs), nd) if vs else None


def share(vs):
    vs = [v for v in vs if v is not None]
    return round(sum(vs) / len(vs), 2) if vs else None


def first_trailing_stage(g):
    """First stage r where the eventual loser's total < winner's total (None if never/no data)."""
    won = (g.get('score') or 0) >= 0.5
    for r in STAGES:
        lo, hi = stage(g, r, 'total', 'opp' if won else 'self'), stage(g, r, 'total', 'self' if won else 'opp')
        if lo is not None and hi is not None and lo < hi:
            return r
    return None


def survival(games, cls):
    """Share of games with our units > 0 at each stage (snapshot semantics)."""
    sub = [g for g in games if map_class(g) == cls]
    out = {}
    for r in STAGES:
        vals = [stage(g, r, 'units') for g in sub]
        vals = [v for v in vals if v is not None]
        out[r] = (round(sum(1 for v in vals if v > 0) / len(vals), 2), len(vals)) if vals else None
    return out


def source_table(rows):
    losses = [g for g in rows if (g.get('score') or 0) == 0]
    wins = [g for g in rows if (g.get('score') or 0) == 1]
    elim = [g for g in losses if g.get('reason') == 'elimination']
    rl = [g for g in losses if g.get('reason') == 'roundLimit']
    t = dict(
        n=len(rows), share=share([g.get('score') for g in rows]),
        losses=len(losses), elim=len(elim), rl=len(rl),
        elim_round_med=med([g.get('rounds') for g in elim], 0),
        elim_round_compact_med=med([g.get('rounds') for g in elim if map_class(g) == 'compact'], 0),
        elim_round_open_med=med([g.get('rounds') for g in elim if map_class(g) == 'open'], 0),
        rl_margin_med=med([g.get('longest_margin') for g in rl], 0),
        win_margin_med=med([g.get('longest_margin') for g in wins], 0),
    )
    for cls in ('compact', 'open'):
        sub = [g for g in rows if map_class(g) == cls]
        if not sub:
            continue
        sl = [g for g in sub if (g.get('score') or 0) == 0]
        se = [g for g in sl if g.get('reason') == 'elimination']
        t[cls] = dict(
            n=len(sub), share=share([g.get('score') for g in sub]), losses=len(sl), elim=len(se),
            units_r100=med([stage(g, 100, 'units') for g in sub]),
            opp_units_r100=med([stage(g, 100, 'units', 'opp') for g in sub]),
            total_r250=med([stage(g, 250, 'total') for g in sub]),
            opp_total_r250=med([stage(g, 250, 'total', 'opp') for g in sub]),
        )
    # wins vs losses stage medians
    for name, grp in (('win', wins), ('loss', losses)):
        if not grp:
            continue
        t[name] = dict(
            units_r100=med([stage(g, 100, 'units') for g in grp]),
            opp_units_r100=med([stage(g, 100, 'units', 'opp') for g in grp]),
            total_r250=med([stage(g, 250, 'total') for g in grp]),
            opp_total_r250=med([stage(g, 250, 'total', 'opp') for g in grp]),
            longest_r400=med([stage(g, 400, 'longest') for g in grp]),
            opp_longest_r400=med([stage(g, 400, 'longest', 'opp') for g in grp]),
            longest_r499=med([stage(g, 499, 'longest') for g in grp]),
            opp_longest_r499=med([stage(g, 499, 'longest', 'opp') for g in grp]),
        )
    # deaths per 1k turns (whole-game, from final stats where richer)
    def stats_med(key):
        return med([round(1000 * (g.get('stats', {}).get(key) or 0) / g['turns'], 1) for g in rows if g.get('turns')])
    t['deaths_1k'] = dict(wall=stats_med('death_wall'), h2h=stats_med('death_h2h'), self_=stats_med('death_self'),
                          body=stats_med('death_body'), invalid=stats_med('death_invalid'),
                          newborn10=med([stage(g, 499, 'newborn_deaths_10') for g in rows], 0))
    # first trailing stage of the eventual loser
    for cls in ('compact', 'open'):
        tr = [first_trailing_stage(g) for g in rows if map_class(g) == cls]
        tr = [x for x in tr if x is not None]
        if tr:
            t.setdefault('first_trail', {})[cls] = dict(
                med=med(tr, 0), at_or_before_250=round(sum(1 for x in tr if x <= 250) / len(tr), 2), n=len(tr))
    return t


def opponent_table(rows):
    cells = defaultdict(list)
    for g in rows:
        cells[(g['opponent'], g.get('opponent_submission'))].append(g)
    return [(o, os_, len(v), share([g.get('score') for g in v]),
             sum(1 for g in v if (g.get('score') or 0) == 0 and g.get('reason') == 'elimination'))
            for (o, os_), v in sorted(cells.items())]


def main():
    games = load()
    rows = field_controlled(games)
    by_sub = defaultdict(list)
    for g in rows:
        by_sub[g['submission']].append(g)
    big = {s: v for s, v in by_sub.items() if len(v) >= MIN_N}
    print(f"# A1 loss anatomy — verified controlled field games, side A, n={len(rows)} total\n")
    print("sources >= {} field games: {}\n".format(MIN_N, {s: len(v) for s, v in sorted(big.items())}))
    for s, v in sorted(big.items()):
        t = source_table(v)
        print(f"## submission {s} (n={t['n']}, share {t['share']})\n")
        print(f"- losses {t['losses']}: elimination {t['elim']} (median round {t['elim_round_med']}; "
              f"compact {t['elim_round_compact_med']} / open {t['elim_round_open_med']}), roundLimit {t['rl']}"
              f" (longest margin median {t['rl_margin_med']}); win margin median {t['win_margin_med']}")
        for cls in ('compact', 'open'):
            c = t.get(cls)
            if c:
                print(f"- {cls}: n={c['n']} share {c['share']} losses {c['losses']} elim {c['elim']} | "
                      f"units r100 {c['units_r100']} vs opp {c['opp_units_r100']} | total r250 {c['total_r250']} vs opp {c['opp_total_r250']}")
        for name in ('win', 'loss'):
            w = t.get(name)
            if w:
                print(f"- {name}: units r100 {w['units_r100']}/{w['opp_units_r100']} total r250 {w['total_r250']}/{w['opp_total_r250']} "
                      f"longest r400 {w['longest_r400']}/{w['opp_longest_r400']} r499 {w['longest_r499']}/{w['opp_longest_r499']} (ours/opp)")
        d = t['deaths_1k']
        print(f"- deaths/1k turns: wall {d['wall']} h2h {d['h2h']} self {d['self_']} body {d['body']} invalid {d['invalid']}; newborn<=10 median {d['newborn10']}")
        ft = t.get('first_trail', {})
        for cls, f in ft.items():
            print(f"- eventual loser first trails on total at r{f['med']} median ({cls}; <=r250 in {f['at_or_before_250']} of games, n={f['n']})")
        print("- opponents (team, their submission, n, share, our elim losses):")
        for o, os_, n, sh, el in opponent_table(v):
            print(f"    - {o} sub {os_}: n={n} share={sh} elim_losses={el}")
        print()


if __name__ == '__main__':
    main()
