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
