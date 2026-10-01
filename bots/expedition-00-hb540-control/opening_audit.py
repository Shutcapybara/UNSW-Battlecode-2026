#!/usr/bin/env python3
"""Explain one map's opening trajectories using exact paired saved replays.
All-game and seat comparisons are primary; outcome-selected cohorts are explicitly
post-hoc descriptions. No games, bot changes, gate decisions or causal claims.
"""
import argparse
import json
from pathlib import Path
from statistics import mean, median
import campaign as c
import report
import phase_report as phase

COUNTERS = ('c_eats_bed', 'c_eats_enemy_corpse', 'c_eats_ally_corpse',
            'c_length_lost', 'c_splits', 'c_deaths', 'c_transits', 'c_own_goals')
STATES = ('total', 'units', 'longest')
EVENTS = ('first_pearl', 'first_split', 'first_death', 'beds_reached@50', 'beds_reached@100')


def paired_measure(parent, child):
    if len(parent) != len(child):
        raise ValueError('Opening comparison requires aligned pairs')
    pairs = [(a, b) for a, b in zip(parent, child) if a is not None and b is not None]
    return dict(paired=len(pairs), missing_pairs=len(parent) - len(pairs),
        parent=mean(a for a, b in pairs) if pairs else None,
        candidate=mean(b for a, b in pairs) if pairs else None,
        delta=mean(b - a for a, b in pairs) if pairs else None)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--map', required=True)
    ap.add_argument('--panel', choices=('z1', 'gen', c.CHALLENGE_PANEL), default='z1')
    ap.add_argument('--seed', type=int, choices=(1, 2, 3), default=1)
    ap.add_argument('--candidate', choices=c.CANDIDATES, default=c.QUEUE[0])
    args = ap.parse_args()
    wanted = {k for k in c.expected(args.panel, [args.seed]) if k[0] == args.map}
    if not wanted:
        raise ValueError('Map not in frozen panel')
    rows, data = {}, {}
    aid, paid = report.analysis_id(), phase.analysis_id()
    for bot in (c.panel.PARENT, args.candidate):
        dest = c.run_dir(bot, args.panel)
        if json.loads((dest / 'contract.json').read_text()) != c.contract(bot, args.panel):
            raise ValueError('Frozen inputs changed')
        rows[bot] = {k: r for k, r in c.read_rows(bot, args.panel).items() if k in wanted}
        if set(rows[bot]) != wanted:
            raise ValueError(f'Incomplete map/seed: {bot}: {len(rows[bot])}/{len(wanted)}')
        data[bot] = {}
        for k, row in rows[bot].items():
            report.canonical(row, dest, aid)
            tempo_input = phase.extract(row, dest, paid)
            cache = c.STORE / 'phase-analysis' / paid / (row['replay_sha256'] + '.json')
            saved = json.loads(cache.read_text())
            side = next(s for s in saved['sides'] if s['side'] == row['side'])
            series = {s['round']: s for s in saved['series'] if s['side'] == row['side']}
            data[bot][k] = dict(side=side, series=series, tempo_input=tempo_input)
    parent, child = rows[c.panel.PARENT], rows[args.candidate]
    pd, cd = data[c.panel.PARENT], data[args.candidate]
    refs = json.loads(phase.tempo.REF.read_text())['maps']
    mapname = pd[next(iter(wanted))]['side']['map']
    if mapname in refs:
        ref, reference_kind = refs[mapname], 'frozen top10'
    else:
        ref = {f: [median(pd[k]['tempo_input'][f][i] for k in wanted) for i in range(31)]
               for f in ('income', 'loss')}
        reference_kind = 'matched parent median for this seed; provisional'
    for arm in (pd, cd):
        for k, value in arm.items():
            tinput = value['tempo_input']
            value['lag_curve'] = {int(t): phase.tempo.lag(
                tinput['income'][i] - (tinput['loss'][i] - ref['loss'][i]), ref['income'], t)
                for i, t in zip(phase.tempo.IDX, phase.tempo.TS)}
    def describe(keys):
        keys = sorted(keys)
        return dict(paired=len(keys),
            tempo_mean=paired_measure([mean(pd[k]['lag_curve'].values()) for k in keys],
                                      [mean(cd[k]['lag_curve'].values()) for k in keys]),
            tempo_curve={str(int(t)): paired_measure([pd[k]['lag_curve'][int(t)] for k in keys],
                                                     [cd[k]['lag_curve'][int(t)] for k in keys])
                         for t in phase.tempo.TS},
            events={f: paired_measure([pd[k]['side'].get(f) for k in keys],
                                      [cd[k]['side'].get(f) for k in keys]) for f in EVENTS},
            checkpoints={str(r): {f: paired_measure(
                [pd[k]['series'][r].get(f, 0) if f in COUNTERS else pd[k]['series'][r][f] for k in keys],
                [cd[k]['series'][r].get(f, 0) if f in COUNTERS else cd[k]['series'][r][f] for k in keys])
                for f in COUNTERS + STATES} for r in range(0, 151, 5)})
    worse = {k for k in wanted if c.panel.gate.win(child[k]) < c.panel.gate.win(parent[k])}
    cohorts = {'all': wanted, 'seat_A': {k for k in wanted if k[1] == 'A'},
               'seat_B': {k for k in wanted if k[1] == 'B'},
               'posthoc_outcome_regressions': worse, 'posthoc_other_outcomes': wanted - worse}
    out = dict(map=args.map, seed=args.seed, panel=args.panel, candidate=args.candidate,
        parent=c.panel.PARENT, paired=len(wanted), source_sha256=c.sha(Path(__file__)),
        canonical_analysis_sha256=aid, phase_analysis_sha256=paid,
        tempo_reference=reference_kind, tempo_reference_sha256=c.sha(phase.tempo.REF),
        cohorts={name: describe(keys) for name, keys in cohorts.items()},
        fixtures=[dict(key=k, parent_result=parent[k]['result'], candidate_result=child[k]['result'],
            parent_replay_sha256=parent[k]['replay_sha256'], candidate_replay_sha256=child[k]['replay_sha256'],
            **describe([k])) for k in sorted(wanted)],
        limitations='DESCRIPTIVE; NO GATE VERDICT. Outcome cohorts are selected after observing results and '
        'cannot establish predictive or causal effects. Checkpoints are cumulative or carried terminal states; '
        'first-event measures omit pairs missing either event and expose that count. No action-score telemetry '
        'is present: intake or transit changes do not prove a particular route or mouth penalty caused them.')
    dest = c.STORE / f'{args.candidate}-{args.panel}-{args.map.replace("/", "+")}-s{args.seed}-opening.json'
    dest.write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps({k: v for k, v in out.items() if k != 'fixtures'}, indent=2))
    print('Fixture trajectories:', dest)


if __name__ == '__main__':
    main()
