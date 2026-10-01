"""Validate a complete fixed screen and apply its predeclared advancement rules.
Advancement means broader testing only, never statistical acceptance or promotion.
Uses existing replays; stale opening audits are regenerated without new games.
"""
import argparse
import json
import math
import random
from pathlib import Path
from statistics import mean
from collections import Counter
import subprocess
import sys
import campaign as c
import report
import phase_report as phase


def decision(screen, checks):
    failed = [name for name, passed in checks.items() if not passed]
    return dict(screen=screen, failed=failed,
                verdict='NEGATIVE SCREEN; DO NOT ADVANCE' if failed else
                        'ELIGIBLE FOR BROADER TESTING; NOT ACCEPTED')


def map_cluster_uncertainty(items, repeats=10000, rng_seed=20261001):
    """Descriptive percentile intervals, resampling whole paired map clusters.

    Keep every seed, seat and opponent within its selected map. The estimand is
    the fixture-weighted mean delta, so unequal map sizes retain their weights.
    These intervals describe this local map sample, not the contest population.
    They do not participate in any frozen advancement rule.
    """
    if not items or repeats < 100:
        raise ValueError('Need paired observations and at least 100 resamples')
    clusters = {}
    seen = set()
    for x in items:
        key = (x['panel'], tuple(x['key']))
        if key in seen:
            raise ValueError('Duplicate paired fixture')
        seen.add(key)
        values = (c.panel.gate.win(x['child']) - c.panel.gate.win(x['parent']),
                  x['tempo'])
        if not all(math.isfinite(v) for v in values):
            raise ValueError('Nonfinite paired metric')
        clusters.setdefault((x['panel'], x['key'][0]), []).append(values)
    groups = [clusters[k] for k in sorted(clusters)]
    sums = [(len(g), *[sum(v[i] for v in g) for i in range(2)]) for g in groups]
    n = len(items)
    estimates = [sum(g[i + 1] for g in sums) / n for i in range(2)]
    draws = [[], []]
    if len(groups) > 1:
        rng = random.Random(rng_seed)
        for _ in range(repeats):
            selected = rng.choices(sums, k=len(groups))
            count = sum(g[0] for g in selected)
            for i in range(2):
                draws[i].append(sum(g[i + 1] for g in selected) / count)
    def interval(values):
        if not values:
            return None  # One map cannot estimate between-map uncertainty.
        values.sort()
        def quantile(q):
            j = (len(values) - 1) * q
            lo = int(j); hi = min(lo + 1, len(values) - 1)
            return values[lo] + (values[hi] - values[lo]) * (j - lo)
        return [quantile(.025), quantile(.975)]
    return dict(method='paired whole-map cluster percentile bootstrap',
        clusters=len(groups), pairs=n, resamples=repeats, rng_seed=rng_seed,
        metrics={name: dict(mean_delta=estimates[i], interval95=interval(draws[i]))
                 for i, name in enumerate(('expected_score', 'opening_tempo'))},
        limitation='Descriptive only; few fixed maps and related controls cannot establish field '
                   'generalization. Seeds, seats and opponents are kept together within maps. '
                   'Not an advancement test; a single map has no interval.')


def parent_phase_cohort(items, boundary):
    """Keep the same paired fixtures using only the parent's survival boundary."""
    selected = [x for x in items if x['parent']['rounds'] >= boundary]
    return dict(pairs=len(selected), parent_round_boundary=boundary,
        expected_score_delta=mean(c.panel.gate.win(x['child']) - c.panel.gate.win(x['parent'])
                                  for x in selected) if selected else None,
        material_share250_delta=mean(x['candidate_features']['total_share@250'] -
                                     x['parent_features']['total_share@250']
                                     for x in selected) if selected else None,
        longest_margin_end_delta=mean(x['candidate_features']['longest_margin_end'] -
                                      x['parent_features']['longest_margin_end']
                                      for x in selected) if selected else None)


def load_opening(candidate, pn, map_name, seed, rows):
    auditor = c.HERE / 'opening_audit.py'
    dest = c.STORE / f'{candidate}-{pn}-{map_name.replace("/", "+")}-s{seed}-opening.json'
    def valid(data):
        wanted = {key for key in rows[c.panel.PARENT] if key[0] == map_name and key[2] == seed}
        fixtures = {tuple(f['key']): f for f in data.get('fixtures', [])}
        return (data.get('candidate') == candidate and data.get('source_sha256') == c.sha(auditor)
                and data.get('canonical_analysis_sha256') == report.analysis_id()
                and data.get('phase_analysis_sha256') == phase.analysis_id()
                and data.get('tempo_reference_sha256') == c.sha(phase.tempo.REF)
                and set(fixtures) == wanted and all(
                    fixtures[k]['parent_replay_sha256'] == rows[c.panel.PARENT][k]['replay_sha256']
                    and fixtures[k]['candidate_replay_sha256'] == rows[candidate][k]['replay_sha256']
                    for k in wanted))
    data = json.loads(dest.read_text()) if dest.exists() else {}
    if not valid(data):
        log = c.ROOT / 'build/expedition' / (dest.stem + '.log')
        with log.open('w') as out:
            subprocess.run([sys.executable, str(auditor), '--candidate', candidate,
                            '--panel', pn, '--map', map_name, '--seed', str(seed)],
                           stdout=out, stderr=subprocess.STDOUT, check=True)
        data = json.loads(dest.read_text())
    if not valid(data):
        raise ValueError(f'Audit does not match frozen screen: {dest}')
    return data


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--screen', choices=c.SCREENS, required=True)
    args = ap.parse_args()
    screen = args.screen; spec = c.SCREENS[screen]; candidate = spec['candidate']
    frozen = c.STORE / 'screens' / f'{screen}.json'
    if not frozen.exists():
        raise ValueError('Screen has not been started/frozen')
    c.freeze_screen(candidate, screen)
    fixtures = list(c.fixture_order(screen))
    rows = {}
    missing = []
    for pn in c.screen_panels(screen):
        wanted = {k for p, k in fixtures if p == pn}
        rows[pn] = {}
        for bot in (c.panel.PARENT, candidate):
            dest = c.run_dir(bot, pn)
            if json.loads((dest / 'contract.json').read_text()) != c.contract(bot, pn):
                raise ValueError('Frozen panel inputs changed')
            rows[pn][bot] = {k: r for k, r in c.read_rows(bot, pn).items() if k in wanted}
            missing.extend((bot, pn, k) for k in sorted(wanted - rows[pn][bot].keys()))
    if missing:
        print(json.dumps(dict(screen=screen, status='INCOMPLETE; NO SCREEN VERDICT',
                              missing=len(missing), next_missing=missing[0]), indent=2))
        return
    output = dict(screen=screen, candidate=candidate, pairs=len(fixtures), maps={},
                  frozen_contract_sha256=c.sha(frozen), promotion='NOT AUTHORIZED')
    measures = []
    aid = report.analysis_id()
    phase_aid = phase.analysis_id()
    for seed in spec['seeds']:
        for pn, map_name in spec['maps']:
            data = load_opening(candidate, pn, map_name, seed, rows[pn])
            for f in data['fixtures']:
                key = tuple(f['key']); parent = rows[pn][c.panel.PARENT][key]; child = rows[pn][candidate][key]
                pf, _, _ = report.canonical(parent, c.run_dir(c.panel.PARENT, pn), aid)
                cf, _, _ = report.canonical(child, c.run_dir(candidate, pn), aid)
                measures.append(dict(panel=pn, key=key, parent=parent, child=child,
                    tempo=f['tempo_mean']['delta'], first_food_delta=f['events']['first_pearl']['delta'],
                    parent_features=pf, candidate_features=cf,
                    parent_opening=phase.extract(parent, c.run_dir(c.panel.PARENT, pn), phase_aid),
                    child_opening=phase.extract(child, c.run_dir(candidate, pn), phase_aid)))
            output['maps'][f'{map_name}/s{seed}'] = data['cohorts']['all']
            print('Validated', map_name, seed, flush=True)
    def summarize(items):
        return dict(n=len(items), parent_wins=sum(x['parent']['result'] == 'win' for x in items),
            candidate_wins=sum(x['child']['result'] == 'win' for x in items),
            outcomes={arm: {result: sum(x[arm]['result'] == result for x in items)
                           for result in ('win', 'draw', 'loss')} for arm in ('parent', 'child')},
            parent_points=sum(c.panel.gate.win(x['parent']) for x in items),
            candidate_points=sum(c.panel.gate.win(x['child']) for x in items),
            tempo_delta=mean(x['tempo'] for x in items),
            canonical_mean_deltas={k: mean(x['candidate_features'][k] - x['parent_features'][k] for x in items)
                for k in ('total@100', 'total@150', 'total@250', 'kills@150', 'kills@250',
                          'longest_margin_end', 'total_margin_end')},
            midgame_kills_delta=mean((x['candidate_features']['kills@250'] - x['candidate_features']['kills@150']) -
                                    (x['parent_features']['kills@250'] - x['parent_features']['kills@150']) for x in items),
            parent_conditioned_phases={str(boundary): parent_phase_cohort(items, boundary)
                                       for boundary in (250, 400)},
            opening_exposures={arm: phase.summarize([x[arm + '_opening'] for x in items])
                               for arm in ('parent', 'child')},
            r500_material_lead_losses={arm: dict(
                games=sum(x[arm]['rounds'] == 500 for x in items),
                losses_with_material_lead=sum(x[arm]['rounds'] == 500 and x[arm]['result'] == 'loss' and
                    x[feature]['total_margin_end'] > 0 for x in items))
                for arm, feature in (('parent','parent_features'),('child','candidate_features'))},
            end_reasons={arm: dict(Counter(x[arm]['end_reason'] for x in items)) for arm in ('parent','child')},
            better=sum(c.panel.gate.win(x['child']) > c.panel.gate.win(x['parent']) for x in items),
            worse=sum(c.panel.gate.win(x['child']) < c.panel.gate.win(x['parent']) for x in items))
    output['by_seed'] = {str(seed): summarize([x for x in measures if x['key'][2] == seed])
                         for seed in spec['seeds']}
    output['by_map_seed'] = {f'{m}/s{s}': summarize([x for x in measures if x['key'][0] == m and x['key'][2] == s])
                            for _, m in spec['maps'] for s in spec['seeds']}
    output['by_opponent_seed'] = {f'{o}/s{s}': summarize([x for x in measures if x['key'][3] == o and x['key'][2] == s])
                                 for o in sorted({x['key'][3] for x in measures}) for s in spec['seeds']}
    output['by_seat_seed'] = {f'{side}/s{s}': summarize([x for x in measures if x['key'][1] == side and x['key'][2] == s])
                             for side in 'AB' for s in spec['seeds']}
    output['map_cluster_uncertainty'] = dict(
        all=map_cluster_uncertainty(measures),
        by_seed={str(seed): map_cluster_uncertainty([x for x in measures if x['key'][2] == seed])
                 for seed in spec['seeds']},
        by_opponent={o: map_cluster_uncertainty([x for x in measures if x['key'][3] == o])
                     for o in sorted({x['key'][3] for x in measures})})
    output['report_source_sha256'] = c.sha(Path(__file__))
    confirmation_seed = str(spec['seeds'][-1])
    confirm = output['by_seed'][confirmation_seed]
    maps2 = [v for k, v in output['by_map_seed'].items() if k.endswith('/s' + confirmation_seed)]
    if screen == 'mouth-contest-v1':
        devil = [x for x in measures if x['key'][0] == 'devil']
        access = next(x for x in measures if x['key'] ==
                      ('queen_of_spades', 'B', 1, 'gavroche-v32-supported-divecap'))
        checks = dict(devil_parity=all(all(x['parent'][k] == x['child'][k]
                      for k in ('us', 'them', 'result', 'rounds', 'end_reason')) for x in devil),
            discovery_food_delay=access['first_food_delta'] is not None and access['first_food_delta'] < 15,
            confirmation_wins=confirm['candidate_wins'] >= confirm['parent_wins'],
            confirmation_map_wins=all(v['candidate_wins'] >= v['parent_wins'] - 1 for v in maps2),
            confirmation_qos_tempo=output['maps']['queen_of_spades/s2']['tempo_mean']['delta'] <= 0,
            confirmation_quartet_tempo=output['maps']['new/mc26_portal_quartet/s2']['tempo_mean']['delta'] <= 0)
    elif screen in ('explore-frontier-v1', 'food-hold-v1'):
        opps2 = [v for k,v in output['by_opponent_seed'].items() if k.endswith('/s' + confirmation_seed)]
        checks = dict(confirmation_gain=confirm['candidate_points'] > confirm['parent_points'],
            opponent_nonharm=all(v['candidate_points'] >= v['parent_points'] for v in opps2),
            map_guard=all(v['candidate_points'] >= v['parent_points'] - 1 for v in maps2),
            opening_nonharm=confirm['tempo_delta'] <= 0)
        output['opening_nonharm_diagnostic'] = checks['opening_nonharm']
        if screen == 'food-hold-v1':
            output['prior_frontier_rule_comparison'] = decision(screen, checks)
            checks.pop('opening_nonharm')
    else:
        raise ValueError(f'No registered decision rule for {screen}')
    output.update(decision(screen, checks)); output['checks'] = checks
    output['limitations'] = ('Small fixed screen; discovery maps/one confirmation seed do not establish '
                            'generalization. Outcome discordance is reported; no statistical acceptance. '
                            'Arena and canonical metrics remain separate; sandbox and full panels unresolved.')
    dest = c.STORE / f'{screen}-result.json'
    dest.write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({k:v for k,v in output.items() if k != 'maps'},indent=2))
    print('Full report:',dest)


if __name__ == '__main__':
    main()
