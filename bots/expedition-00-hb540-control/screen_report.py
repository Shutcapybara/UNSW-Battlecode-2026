"""Validate a complete fixed screen and apply its predeclared advancement rules.
Advancement means broader testing only, never statistical acceptance or promotion.
Uses existing replays; stale opening audits are regenerated without new games.
"""
import argparse
import json
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
    for seed in spec['seeds']:
        for pn, map_name in spec['maps']:
            data = load_opening(candidate, pn, map_name, seed, rows[pn])
            for f in data['fixtures']:
                key = tuple(f['key']); parent = rows[pn][c.panel.PARENT][key]; child = rows[pn][candidate][key]
                pf, _, _ = report.canonical(parent, c.run_dir(c.panel.PARENT, pn), aid)
                cf, _, _ = report.canonical(child, c.run_dir(candidate, pn), aid)
                measures.append(dict(panel=pn, key=key, parent=parent, child=child,
                    tempo=f['tempo_mean']['delta'], first_food_delta=f['events']['first_pearl']['delta'],
                    parent_features=pf, candidate_features=cf))
            output['maps'][f'{map_name}/s{seed}'] = data['cohorts']['all']
            print('Validated', map_name, seed, flush=True)
    def summarize(items):
        return dict(n=len(items), parent_wins=sum(x['parent']['result'] == 'win' for x in items),
            candidate_wins=sum(x['child']['result'] == 'win' for x in items),
            parent_points=sum(c.panel.gate.win(x['parent']) for x in items),
            candidate_points=sum(c.panel.gate.win(x['child']) for x in items),
            tempo_delta=mean(x['tempo'] for x in items),
            canonical_mean_deltas={k: mean(x['candidate_features'][k] - x['parent_features'][k] for x in items)
                for k in ('total@100', 'total@150', 'total@250', 'kills@150', 'kills@250',
                          'longest_margin_end', 'total_margin_end')},
            midgame_kills_delta=mean((x['candidate_features']['kills@250'] - x['candidate_features']['kills@150']) -
                                    (x['parent_features']['kills@250'] - x['parent_features']['kills@150']) for x in items),
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
    confirm = output['by_seed']['2']
    maps2 = [v for k, v in output['by_map_seed'].items() if k.endswith('/s2')]
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
    elif screen == 'explore-frontier-v1':
        opps2 = [v for k,v in output['by_opponent_seed'].items() if k.endswith('/s2')]
        checks = dict(confirmation_gain=confirm['candidate_points'] > confirm['parent_points'],
            opponent_nonharm=all(v['candidate_points'] >= v['parent_points'] for v in opps2),
            map_guard=all(v['candidate_points'] >= v['parent_points'] - 1 for v in maps2),
            opening_nonharm=confirm['tempo_delta'] <= 0)
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
