"""pytest tools/analysis/features/test_features.py  (fixture: fenrir-v18 vs ouroboros-m01, Trophy, seed 1, unswbc 1.2.2)"""
import math
from pathlib import Path

import pytest

from tools.analysis.features.frame import decode
from tools.analysis.features.extract import extract, CHECKPOINTS
from tools.analysis.features.checks import v0_checks
from tools.analysis.features.registry import REGISTRY

FIX = Path(__file__).parent / 'fixtures' / 'trophy_s1_fenrir-v18_ouroboros-m01.replay'


@pytest.fixture(scope='module')
def game():
    return decode(FIX)


@pytest.fixture(scope='module')
def out(game):
    return extract(game)


def test_decode_matches_engine_result(game):
    assert game['map'] == 'Trophy' and game['winner'] == 'A' and game['reason'] == 'elimination'
    last = game['rounds'][-1]
    for t in 'AB':
        assert sum(len(b) for i, (tt, b) in last.items() if tt == t) == game['final'][t]['total']


def test_v0_identities_hold(game, out):
    bad = [c for c in v0_checks(game, out) if c['residual'] != 0]
    assert not bad, bad


def test_shares_in_unit_interval(out):
    for row in out['side_rows']:
        for k, v in row.items():
            if isinstance(v, float) and not math.isnan(v) and ('share' in k or k.startswith(('territory', 'bed_territory'))):
                assert -1e-9 <= v <= 1 + 1e-9, (k, v)


def test_side_rows_are_mirror_consistent(out):
    a, b = out['side_rows']
    for c in CHECKPOINTS:
        assert abs(a[f'total_share@{c}'] + b[f'total_share@{c}'] - 1) < 1e-9
    assert a['won'] + b['won'] == 1


def test_registry_covers_extracted_features(out):
    row = out['side_rows'][0]
    context = {'game', 'map', 'map_class', 'map_hash', 'cells', 'dragons_start', 'beds', 'beds_source', 'bed_capacity', 'rounds', 'reason', 'side', 'bot',
               'opponent', 'won', 'result'}
    missing = [k for k in row if k not in context and k not in REGISTRY]
    assert not missing, missing


def test_sonar_decoded(game):
    s = game['events']['sonar']
    assert s and {'dir', 'origin', 'end', 'hit_kind'} <= set(s[0])
    assert {x['hit_kind'] for x in s} <= {'kelp', 'ally', 'ally_head', 'enemy', 'enemy_head', 'empty', 'unknown'}


# ---- R-4 Part 4: generalisation panel + no-reference degradation -------------

def test_gen_panel_fixtures():
    from tools.analysis.features.run_panel import GEN_MAPS, fixtures, runtime_fingerprint, ZOO
    import itertools
    # GEN_MAPS = all 20 maps/new + the 9 maps/var transpositions, name-flattened in game ids
    assert len([m for m in GEN_MAPS if m.startswith('new/')]) == 20
    assert len([m for m in GEN_MAPS if m.startswith('var/')]) == 9
    # z1 ids are unchanged (replay reuse): compare against the pre-R4 generator
    want = [f's1__{m}__{x}__{y}' for a, b in itertools.combinations(ZOO, 2)
            for m in ['schooltime', 'portals', 'slithery_fight', 'queen_of_spades', 'default',
                      'trophy', 'dilemma', 'autarky', 'devil', 'trauma']
            for x, y in ((a, b), (b, a))]
    got = [f['game'] for f in fixtures('z1') if f['seed'] == 1]
    assert got == want
    # gen round robin: 28 pairs x 29 maps x 2 seats at seed 1
    assert len(fixtures('gen')) == 28 * 29 * 2
    # candidate grid: 8 opponents x 10 live maps x 2 seats = 160 (the Ares V06 protocol)
    assert len(fixtures('z1', bot='bots/whatever-bot')) == 8 * 10 * 2
    assert len(fixtures('z1', bot='bots/whatever-bot', seeds=(1, 2))) == 320
    assert len(fixtures('gen', bot='bots/whatever-bot')) == 8 * 29 * 2
    # slashed map names are flattened into file-safe game ids
    assert all('/' not in f['game'] for f in fixtures('gen'))


def test_runtime_fingerprint_tracks_sources(tmp_path):
    from tools.analysis.features.run_panel import runtime_fingerprint
    d = tmp_path / 'bot'
    d.mkdir()
    (d / 'bot.toml').write_text('[project]\nlanguage = "c++"\ninclude = ["*.cpp"]\n')
    (d / 'main.cpp').write_text('int main() {}\n')
    (d / 'util.hpp').write_text('#pragma once\n')
    fp0 = runtime_fingerprint(d)
    assert len(fp0) == 64
    (d / '.unswbc-build').mkdir()
    (d / '.unswbc-build' / 'bot').write_bytes(b'\x00binary')
    assert runtime_fingerprint(d) == fp0          # build output ignored
    (d / 'util.hpp').write_text('#pragma once\n// edit\n')
    assert runtime_fingerprint(d) != fp0          # header edit moves the fingerprint


def test_no_reference_maps_degrade_gracefully():
    import numpy as np
    import pandas as pd
    from tools.analysis.features.benchmarks import derive, apply_field_rel
    cols = {'pearls@50': 10, 'pearls@100': 20, 'pearls@150': 30, 'pearls@250': 40,
            'bed_pearls@50': 5, 'bed_pearls@100': 5, 'bed_pearls@150': 5, 'bed_pearls@250': 5,
            'pearls_per100dt_0_100': 1, 'births@100': 2, 'total@100': 10, 'units@100': 3,
            'death_wall_per1k': 1, 'death_self_per1k': 1, 'death_ally_body_per1k': 1,
            'death_h2h_ally_per1k': 1, 'death_invalid_per1k': 0, 'death_enemy_body_per1k': 1,
            'death_h2h_enemy_per1k': 1, 'deaths_per1k': 3, 'bed_capacity': 10}
    F = pd.DataFrame([dict(game='g1', side='A', map='Portals', **cols),
                      dict(game='g2', side='A', map='new/md26_promenade_ring_s0', **cols)])
    ref = {'pearls@100': {'Portals': 20}}
    G = derive(F, ref)  # partial reference set: no KeyError
    assert G.loc[0, 'pearls@100|map'] == 1.0
    assert np.isnan(G.loc[1, 'pearls@100|map'])   # unknown map -> unavailable, not a number
    assert 'pearls@50|map' not in G.columns       # unreferenced metric -> column absent
    refs = {'pearls@100': {'Portals': dict(median=20.0, p10=1, p25=1, p75=1, p90=40.0, top10=40.0,
                                           n=10, sorted=[1, 20, 20, 40])}}
    H = apply_field_rel(G, refs)
    assert np.isnan(H.loc[1, 'pearls@100|pct']) and np.isnan(H.loc[1, 'pearls@100|top'])
    assert 'pearls@50|pct' not in H.columns


# ---- R-4 Part 3: scorecard gate and tables -----------------------------------

def _stats(econ=1.0, units=1.0, total=1.0, wall=5.0, self_=3.0, ally=2.0, h2h=1.0, invalid=0.0,
           exp=0.75, n=160):
    cps = {'pearls@50': econ, 'pearls@100': econ, 'pearls@150': econ, 'pearls@250': econ}
    return {'n': n, 'wld': [100, 60, 0], 'exp_share': exp, 'checkpoints': cps,
            'checkpoints_raw': {k: 50.0 for k in cps}, 'economy_mean': econ,
            'tier1': {'units@100|map': units, 'total@100|map': total, 'births@100|map': 1.0},
            'tier1_raw': {'units@100': 10, 'total@100': 30, 'births@100': 20,
                          'pearls@50': 50, 'pearls@100': 50, 'pearls@150': 50, 'pearls@250': 50},
            'tier2': {'death_wall_per1k': wall, 'death_self_per1k': self_,
                      'death_ally_body_per1k': ally, 'death_h2h_ally_per1k': h2h,
                      'death_invalid_per1k': invalid}}


def test_gate_pass_fail_hold():
    from tools.analysis.features.scorecard import gate_line
    base = _stats()
    v, why = gate_line(_stats(econ=1.06), base)
    assert v == 'pass' and '+0.0600' in why
    # economy down or win rate down or a tier-2 rate up >10% -> fail
    assert gate_line(_stats(econ=0.98), base)[0] == 'fail'
    assert gate_line(_stats(exp=0.70), base)[0] == 'fail'
    assert gate_line(_stats(wall=5.6), base)[0] == 'fail'       # +12%
    assert gate_line(_stats(invalid=0.5), base)[0] == 'fail'    # from zero
    # economy up but short of +0.05, everything else fine -> hold (the V06 case)
    v, why = gate_line(_stats(econ=1.0133, units=1.13, exp=0.7625, wall=5.06), base)
    assert v == 'hold' and '+0.0133' in why
    # economy at the bar but dragons falling -> not pass, not fail -> hold
    assert gate_line(_stats(econ=1.06, units=0.99), base)[0] == 'hold'
    assert gate_line(base, None)[0] == 'n/a'


def test_scorecard_tables():
    from tools.analysis.features.scorecard import tier1_rows, tier2_rows, raw_rows
    cs, ps = _stats(econ=1.1, wall=4.0), _stats()
    t1 = tier1_rows(cs, ps)
    assert t1[0][1] == '100–60–0' and 'expected-score points' in t1[0][3]
    assert t1[2][0] == 'Mean of normalized pearl checkpoints' and t1[2][3] == '+0.1000'
    assert any(r[0] == 'Dragons at r100, normalized' for r in t1)
    t2 = tier2_rows(cs, ps)
    assert t2[0] == ('Wall', '5.000', '4.000', '-20.0%')
    assert t2[4] == ('Invalid action', '0.000', '0.000', 'unchanged')
    rr = raw_rows(cs, ps)
    assert len(rr) == 7 and all(r[3] == '+0.0' for r in rr)
