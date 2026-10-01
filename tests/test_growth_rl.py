import copy
import gzip
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.growth_rl.data import bucket, digest, provenance, targets, dataset, team_state
from tools.growth_rl.policy import ACTIONS, Policy, action_mask, observed_index, split_size
from tools.growth_rl.evaluate import gate_report, package
from tools.growth_rl.panel_gate import panel_gate_report


def test_whole_sprint_is_not_relabelled_as_first_move():
    row = dict(length=6, units=3, unit_limit=64, y_family='move', y_seq='FR')
    assert ACTIONS[observed_index(row)] == 'FR'
    row['y_seq'] = 'FRF'
    assert observed_index(row) is None


def test_split_sizes_are_legal_canonical_and_not_teacher_labels():
    row = dict(length=6, units=3, unit_limit=64, y_family='split', y_split=3)
    assert ACTIONS[observed_index(row)] == 'split_half'
    before = action_mask(row)
    row['y_split'] = 999
    assert before == action_mask(row)
    row['length'] = 4
    assert sum(action_mask(row)[20:]) == 1
    row['units'] = 64
    assert not any(action_mask(row)[20:])


def test_split_conserves_material_and_child_death_affects_parent_reward():
    row = dict(target_current=dict(total=12, units=3),
               target_horizons=[dict(total=12, units=4)] * 3, target_win=1.)
    assert targets(row, population_weight=0)[:3] == [0., 0., 0.]
    row['target_horizons'] = [dict(total=8, units=2)] * 3
    assert all(x < 0 for x in targets(row)[:3])
    assert targets(row)[3] == 1.


def test_future_win_does_not_change_growth_reward():
    row = dict(target_current=dict(total=10, units=3),
               target_horizons=[dict(total=15, units=5)] * 3, target_win=0.)
    original = targets(row)
    row['target_win'] = 1.
    assert targets(row)[:3] == original[:3]


def test_holdouts_stable_and_mirrored_fixtures_grouped(tmp_path):
    a, b = tmp_path / 'a.replay', tmp_path / 'b.replay'
    for path, side in ((a, 'A'), (b, 'B')):
        path.with_suffix('.json').write_text(json.dumps(dict(fixture=dict(map='m', teacher='x', opponent='y', seed=1, side=side))))
    assert provenance(a, 'aaa')['group'] == provenance(b, 'bbb')['group']
    first = {str(i): bucket(str(i)) for i in range(100)}
    second = {str(i): bucket(str(i)) for i in range(200)}
    assert all(first[k] == second[k] for k in first)
    assert set(first.values()) == {'train', 'validation', 'test'}


def test_compressed_duplicates_have_same_identity(tmp_path):
    raw, compressed = tmp_path / 'a.replay', tmp_path / 'b.replay.gz'
    raw.write_bytes(b'example replay bytes')
    compressed.write_bytes(gzip.compress(raw.read_bytes()))
    assert digest(raw) == digest(compressed)


def pairs(gain, win=0):
    return [dict(identity=dict(map_hash=f'm{m}', opponent_hash=f'o{o}'),
                 candidate=dict(objective=gain, score=0.5 + win, units=12, total=30),
                 incumbent=dict(objective=0, score=0.5, units=10, total=25))
            for m in range(2) for o in range(2) for _ in range(4)]


def test_promotion_requires_real_growth_and_win_nonregression():
    assert gate_report(pairs(0.2))['promote']
    assert not gate_report(pairs(-0.2))['promote']
    assert not gate_report(pairs(0.2, -0.2))['promote']
    assert not gate_report(pairs(0.2)[:2])['promote']
    assert not gate_report([])['promote']


def panel_pairs(*, pool_growth=0.1, generalization_growth=0.05, score_delta=0,
                units_pct=0, total_pct=0, death_pct=0):
    records = []
    for panel, growth in (('pool', pool_growth), ('generalization', generalization_growth)):
        for map_index in range(4):
            for side in 'AB':
                base_rounds = {}
                candidate_rounds = {}
                for checkpoint in (10, 25, 50, 75, 100):
                    base = dict(units=10, total=20, longest=4, pearls=15, corpse_pearl_share=0.1,
                                growth_objective=0.5, death_rates={k: 1.0 for k in ('wall', 'self', 'body', 'h2h')})
                    candidate = dict(units=10 * (1 + units_pct), total=20 * (1 + total_pct), longest=4,
                                     pearls=15, corpse_pearl_share=0.1, growth_objective=0.5 + growth,
                                     death_rates={k: 1.0 * (1 + death_pct) for k in ('wall', 'self', 'body', 'h2h')})
                    base_rounds[str(checkpoint)] = base
                    candidate_rounds[str(checkpoint)] = candidate
                records.append(dict(identity=dict(panel=panel, map_hash=f'{panel}-m{map_index}',
                                                  opponent_hash='opp', side=side, seed=1),
                                    candidate=dict(score=0.5 + score_delta, checkpoints=candidate_rounds),
                                    incumbent=dict(score=0.5, checkpoints=base_rounds)))
    return records


def test_d032_gate_requires_complete_paired_pool_and_generalization_panels():
    expected = {'pool': 8, 'generalization': 8}
    report = panel_gate_report(panel_pairs(), expected, bootstrap=500)
    assert report['promote']
    assert report['panels']['pool']['metrics']['growth_objective']['lower'] > 0
    assert set(report['panels']['generalization']['per_checkpoint']) == {'10', '25', '50', '75', '100'}
    assert not panel_gate_report(panel_pairs(), {'pool': 9, 'generalization': 8}, bootstrap=500)['promote']


def test_d032_gate_rejects_win_population_material_or_death_regressions():
    expected = {'pool': 8, 'generalization': 8}
    assert not panel_gate_report(panel_pairs(score_delta=-0.03), expected, bootstrap=500)['promote']
    assert not panel_gate_report(panel_pairs(units_pct=-0.03), expected, bootstrap=500)['promote']
    assert not panel_gate_report(panel_pairs(total_pct=-0.03), expected, bootstrap=500)['promote']
    assert not panel_gate_report(panel_pairs(death_pct=0.11), expected, bootstrap=500)['promote']
    assert not panel_gate_report(panel_pairs(generalization_growth=-0.03), expected, bootstrap=500)['promote']


def test_paired_panel_gate_writes_pairs_and_reuses_them_on_resume(tmp_path, monkeypatch):
    from tools.growth_rl import panel_gate
    candidate, incumbent, opponent = (tmp_path / name for name in ('candidate', 'incumbent', 'opponent'))
    for bot in (candidate, incumbent, opponent):
        bot.mkdir()
        (bot / 'bot.toml').write_text('[project]\nlanguage = "py"\n')
        (bot / 'main.py').write_text(bot.name)
    maps = []
    for name in ('pool.map', 'unseen.map'):
        board = tmp_path / name
        board.write_text('MAP 4 4\nMAP_NAME toy\n')
        maps.append(board)
    calls = []

    def fake_run(bot, other, board, side, seed, output, known_hashes=None):
        calls.append(Path(output).name)
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_bytes(Path(output).name.encode())
        return output

    def fake_extract(path, cache):
        is_candidate = Path(path).stem.endswith('candidate')
        rounds = {}
        for checkpoint in (0, 10, 25, 50, 75, 100):
            total = 20 if checkpoint == 0 else (24 if is_candidate else 22)
            stats = dict(units=10, total=total, longest=4, pearls=15, pearls_corpse=1,
                         dragon_turns=100, deaths_wall=1, deaths_self=1, deaths_body=1, deaths_h2h=1)
            rounds[str(checkpoint)] = {'A': stats, 'B': stats}
        return dict(series=rounds, result=dict(rounds=100, winner='A'))

    monkeypatch.setattr(panel_gate, 'run_game', fake_run)
    monkeypatch.setattr(panel_gate, 'extract', fake_extract)
    panel_specs = [
        dict(name='pool', maps=[maps[0]], opponents=[opponent], seeds=[1]),
        dict(name='generalization', maps=[maps[1]], opponents=[opponent], seeds=[1]),
    ]
    report = panel_gate.paired_panel_gate(candidate, incumbent, panel_specs,
        tmp_path / 'evaluation', tmp_path / 'cache', bootstrap=200, jobs=2, min_clusters=1)
    assert report['promote']
    assert len(json.loads((tmp_path / 'evaluation/pairs.json').read_text())) == 4
    assert len(calls) == 8
    panel_gate.paired_panel_gate(candidate, incumbent, panel_specs,
        tmp_path / 'evaluation', tmp_path / 'cache', bootstrap=200, jobs=2, min_clusters=1)
    assert len(calls) == 8


def test_policy_does_not_see_targets_or_map_identity():
    policy = Policy(dict(actions=list(ACTIONS), features=['length'], mean=[0], scale=[1],
                         layers=[dict(weight=[[1]] * len(ACTIONS), bias=list(range(len(ACTIONS))))]))
    row = dict(length=5, units=3, unit_limit=64)
    scores = policy.logits(row)
    row.update(target_win=1, map='Schooltime', y_split=999, target_horizons=[999])
    assert policy.logits(row) == scores


def test_tree_policy_rounds_features_like_float32_training():
    import struct
    raw = 0.9095229
    threshold = struct.unpack('=f', struct.pack('=f', raw))[0]
    left, right = [0.0] * len(ACTIONS), [0.0] * len(ACTIONS)
    left[0], right[1] = 1.0, 1.0
    policy = Policy(dict(actions=list(ACTIONS), features=['value'], mean=[0.0], scale=[1.0], tree=dict(
        feature=[0, -2, -2], threshold=[threshold, -2.0, -2.0],
        left=[1, -1, -1], right=[2, -1, -1], logits=[[0.0] * len(ACTIONS), left, right])))
    # The raw Python double sits just above this split; the training matrix
    # rounded it onto the split, where sklearn takes the left branch.
    assert policy.logits({'value': raw}) == left


def test_existing_dueling_trainer_selected_action_has_advantage_gradient():
    import torch
    sys.path.insert(0, str(ROOT / 'tools'))
    from tools.rl_earlygame_gpu import make_network, loader_for
    model = make_network(torch, torch.nn, 3, 2, 16)
    context, actions = torch.randn(4, 3), torch.randn(4, 5, 2)
    chosen = model(context, actions).gather(1, torch.tensor([[0], [1], [2], [3]])).sum()
    chosen.backward()
    assert sum(float(p.grad.abs().sum()) for p in model.advantage.parameters()) > 0


def toy_game(identity, split):
    rows = []
    for side in 'AB':
        for r in range(16):
            rows.append(dict(game=identity, side=side, dragon=0 if side == 'A' else 1,
                round=r, length=4, units=2, unit_limit=64, action=r % 2,
                target_current=dict(total=8, units=2),
                target_horizons=[dict(total=10 + r, units=3)] * 3,
                target_win=float(side == 'A')))
    stats = dict(total=24, units=6, longest=5, pearls=20, deaths=1, splits=5, dragon_turns=60,
                 pearls_bed=10, pearls_corpse=5, pearls_init=3, pearls_unknown=2,
                 deaths_wall=0, deaths_self=0, deaths_body=1, deaths_body_ally=1,
                 deaths_body_enemy=0, deaths_h2h=0, deaths_h2h_ally=0,
                 deaths_h2h_enemy=0, deaths_no_action=0)
    return dict(sha256=identity, split=split, rows=rows, features=['round', 'length', 'units', 'unit_limit'],
                map='toy', result=dict(winner='A', rounds=100), coverage={'supported': len(rows)},
                series={r: {s: stats for s in 'AB'} for r in range(101)})


def test_team_state_carries_churn_and_death_categories():
    from collections import Counter
    from types import SimpleNamespace
    counters = Counter({('A', 'pearls'): 8, ('A', 'pearls_corpse'): 3,
                        ('A', 'deaths'): 4, ('A', 'deaths_h2h'): 2,
                        ('A', 'deaths_h2h_ally'): 1, ('A', 'turns'): 100})
    game = SimpleNamespace(dragons={1: SimpleNamespace(alive=True, team='A', body=[1, 2, 3])})
    state = team_state(game, 'A', counters)
    assert state['pearls'] == 8
    assert state['pearls_corpse'] == 3
    assert state['deaths'] == 4
    assert state['deaths_h2h'] == 2
    assert state['deaths_h2h_ally'] == 1
    assert state['dragon_turns'] == 100


def test_distribution_report_keeps_map_test_split_opaque():
    from tools.growth_rl.train import distribution_report
    train_game = toy_game('visible', 'train')
    test_game = toy_game('locked', 'test')
    frame, quantiles = distribution_report([train_game, test_game])
    assert set(frame['game']) == {'visible'}
    assert len(frame) == 10  # two sides at five checkpoints
    assert quantiles and all(row['map'] == 'toy' for row in quantiles)


def test_distribution_report_separates_ranked_and_unranked_top_team_games():
    from tools.growth_rl.train import distribution_report
    game = toy_game('public', 'train')
    game['provenance'] = dict(metadata=dict(source='public', rank_a=1, rank_b=17, ranked=False,
                                            team_a=7, team_b=8, submission_a=7001,
                                            fetched_at='2026-09-30T00:00:00Z'))
    frame, quantiles = distribution_report([game])
    assert set(frame['cohort']) == {'top10_unranked', 'other_field_unranked'}
    top = frame[frame['team_id'] == 7].iloc[0]
    assert top['submission'] == 7001 and top['rank_snapshot'] == 1
    assert any(row['submission'] == 7001 and row['rank_snapshot'] == 1 for row in quantiles)


def test_cohort_summary_compares_outcomes_and_excludes_locked_test_rows():
    import pandas as pd
    from tools.growth_rl.train import cohort_summary, distribution_report
    game = toy_game('public', 'train')
    game['provenance'] = dict(metadata=dict(source='public', rank_a=1, rank_b=17, ranked=True,
                                            team_a=7, team_b=8, submission_a=7001,
                                            submission_b=8001))
    frame, _ = distribution_report([game])
    leaked = frame.iloc[[0]].copy()
    leaked['game'] = 'locked-test'
    leaked['split'] = 'test'
    summaries = cohort_summary(pd.concat([frame, leaked], ignore_index=True))
    top_win = next(row for row in summaries if row['cohort'] == 'top10_ranked'
                   and row['outcome'] == 'win' and row['checkpoint'] == 100)
    top_all = next(row for row in summaries if row['cohort'] == 'top10_ranked'
                   and row['outcome'] == 'all' and row['checkpoint'] == 100)
    assert top_win['side_games'] == 1
    assert top_win['games'] == 1
    assert top_all['games'] == 1
    assert top_win['teams'] == 1
    assert top_win['submission_identity_fraction'] == 1.0
    assert top_win['units_mean'] == 6


def test_top10_winner_tree_data_is_train_only_ranked_public_wins():
    from tools.growth_rl.train import top10_winner_arrays

    def ranked_game(identity, split, winner, rank_a, rank_b, ranked=True):
        game = toy_game(identity, split)
        game['result']['winner'] = winner
        game['provenance'] = dict(metadata=dict(source='public', ranked=ranked,
                                                 rank_a=rank_a, rank_b=rank_b))
        return game

    games = [ranked_game('top-win', 'train', 'A', 1, 20),
             ranked_game('low-rank-win', 'train', 'A', 11, 20),
             ranked_game('unranked-win', 'train', 'A', 1, 20, ranked=False),
             ranked_game('loss', 'train', 'B', 1, 20),
             ranked_game('held-out', 'validation', 'A', 2, 20),
             ranked_game('locked', 'test', 'A', 1, 20)]
    names = ['round', 'length', 'units', 'unit_limit']
    train = top10_winner_arrays(games, names)
    validation = top10_winner_arrays(games, names, split='validation')
    assert set(train['groups']) == {'top-win'}
    assert all(row['side'] == 'A' for row in train['rows'])
    assert float(train['weight'].sum()) == pytest.approx(1.0)
    assert set(validation['groups']) == {'held-out'}
    with pytest.raises(ValueError):
        top10_winner_arrays(games, names, split='test')


def test_top10_tree_rollout_has_its_own_behavior_cohort():
    from tools.growth_rl.behavior import cohort_label
    meta = dict(source='local_rollout', actor_side='A',
                opponent_family='top10_ranked_winner_tree')
    assert cohort_label(meta, 'A') == 'learned'
    assert cohort_label(meta, 'B') == 'local_tree_top10_winner'


def test_training_export_parity_and_locked_test(tmp_path):
    import torch
    from tools.growth_rl.train import fit

    def top_team_game(identity, split, rank):
        game = toy_game(identity, split)
        game['provenance'] = dict(metadata=dict(source='public', ranked=True,
                                                 rank_a=rank, rank_b=20))
        return game

    games = [top_team_game(f'train{i}', 'train', i + 1) for i in range(10)]
    games.extend([top_team_game('val', 'validation', 2), toy_game('test', 'test')])
    summary = fit(games, tmp_path, device='cuda' if torch.cuda.is_available() else 'cpu',
                  epochs=2, hidden=8, batch_size=16)
    assert summary['parity_max_error'] < 0.0002
    assert isinstance(summary['test'], str) and summary['test'].startswith('locked')
    assert not summary['validation']['causal_policy_improvement_established']
    top10 = summary['tree_top10_winners']
    assert top10['status'] == 'trained_exploratory_zoo_opponent'
    assert top10['train_games'] == 10 and top10['validation_games'] == 1
    assert np.isfinite(top10['validation_nll'])
    assert (tmp_path / 'tree_top10_winners_policy.json').exists()
    assert summary['split_games']['test'] == ['test']
    bot = package(tmp_path / 'policy.json', tmp_path / 'bot')
    assert (bot / 'main.py').is_file()


def test_config_training_evaluation_and_locked_maps_disjoint():
    config = json.loads((ROOT / 'configs/growth-rl-3060.json').read_text())
    train = set(config['bootstrap']['maps']) | set(config['rollouts']['maps'])
    panels = {p['name']: set(p['maps']) for p in config['evaluation']['panels']}
    generalization = panels['generalization']
    test = set(config['locked_test_maps'])
    assert not train & generalization and not train & test
    assert panels['pool'].isdisjoint(generalization)
    assert all((ROOT / p).exists() for p in train | generalization | panels['pool'] | test)
    assert len(panels['pool']) == 10 and len(generalization) == 29
    assert config['evaluation']['seeds'] == [1, 2, 3]
    assert len(config['evaluation']['opponents']) >= 8
    assert {'mc26_portal_quartet', 'md26_orchard_wide_s0', 'Portals tr'} <= set(config['holdout_map_names'])
    assert config['collection']['ranked_only'] is False
    assert config['collection']['max_downloads'] >= 60


def test_source_hash_ignores_toolkit_generated_copies(tmp_path):
    from tools.growth_rl.evaluate import source_hash
    (tmp_path / 'main.py').write_text('print(1)')
    before = source_hash(tmp_path)
    generated = tmp_path / '.unswbc-build'
    generated.mkdir()
    (generated / 'main.py').write_text('compiled copy')
    assert source_hash(tmp_path) == before


def test_collector_expands_ranked_series_and_records_missing_submission(tmp_path, monkeypatch):
    from tools.growth_rl import collect as module
    monkeypatch.setattr(module.downloader, 'load_api_key', lambda: 'test-placeholder')
    class Client:
        base = 'https://example.test'
        def __init__(self, *args, **kwargs):
            pass
        def get(self, path):
            if path == '/api/v1/ratings':
                return {'ladder': [dict(id=7, rank=1, dev=False)]}
            if path == '/api/v1/teams/7':
                return {'recent': [dict(id=42, replayId=42, ranked=True)]}
            assert path == '/api/v1/battles/42'
            return dict(match=dict(id=42, ranked=True, teamAId=7, teamBId=8, seriesId='series42'),
                        games=[dict(id=42, hasReplay=True)])
        def download_replay(self, gid, path):
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_bytes(b'replay')
    monkeypatch.setattr(module, 'Client', Client)
    report = module.collect(dict(top_n=1, max_downloads=1), tmp_path)
    assert report['downloaded'] == 1
    receipt = json.loads((tmp_path / 'replays/42.json').read_text())
    assert receipt['series_id'] == 'series42'
    assert not receipt['submission_identity_available']


def test_collector_resolves_nested_submission_identity_when_available(tmp_path, monkeypatch):
    from tools.growth_rl import collect as module
    monkeypatch.setattr(module.downloader, 'load_api_key', lambda: 'test-placeholder')
    class Client:
        base = 'https://example.test'
        def __init__(self, *args, **kwargs):
            pass
        def get(self, path):
            if path == '/api/v1/ratings':
                return {'ladder': [dict(id=7, rank=1, dev=False)]}
            if path == '/api/v1/teams/7':
                return {'recent': [dict(id=44, replayId=44, ranked=True)]}
            assert path == '/api/v1/battles/44'
            return dict(match=dict(id=44, ranked=True, seriesId='series44',
                                   teamA=dict(id=7, submission=dict(id=8751)),
                                   teamB=dict(id=8, submissionId=8752)),
                        games=[dict(id=44, hasReplay=True)])
        def download_replay(self, gid, path):
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_bytes(b'replay')
    monkeypatch.setattr(module, 'Client', Client)
    report = module.collect(dict(top_n=1, max_downloads=1), tmp_path)
    assert report['downloaded'] == 1
    receipt = json.loads((tmp_path / 'replays/44.json').read_text())
    assert receipt['team_a'] == 7 and receipt['team_b'] == 8
    assert receipt['submission_a'] == 8751 and receipt['submission_b'] == 8752
    assert receipt['submission_identity_available']


def test_collector_keeps_unranked_top_team_games_when_requested(tmp_path, monkeypatch):
    from tools.growth_rl import collect as module
    monkeypatch.setattr(module.downloader, 'load_api_key', lambda: 'test-placeholder')
    class Client:
        base = 'https://example.test'
        def __init__(self, *args, **kwargs):
            pass
        def get(self, path):
            if path == '/api/v1/ratings':
                return {'ladder': [dict(id=7, rank=1, dev=False)]}
            if path == '/api/v1/teams/7':
                return {'recent': [dict(id=43, replayId=43, ranked=False)]}
            assert path == '/api/v1/battles/43'
            return dict(match=dict(id=43, ranked=False, teamAId=7, teamBId=8),
                        games=[dict(id=43, hasReplay=True)])
        def download_replay(self, gid, path):
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_bytes(b'unranked replay')
    monkeypatch.setattr(module, 'Client', Client)
    report = module.collect(dict(top_n=1, max_downloads=1, ranked_only=False), tmp_path)
    assert report['downloaded'] == 1
    receipt = json.loads((tmp_path / 'replays/43.json').read_text())
    assert receipt['ranked'] is False
    assert receipt['rank_a'] == 1
    assert receipt['watch_team'] == 7


def test_collector_honors_stop_before_network(tmp_path, monkeypatch):
    from tools.growth_rl import collect as module
    stop = tmp_path / 'STOP'
    stop.write_text('stop')
    monkeypatch.setattr(module.downloader, 'load_api_key', lambda: pytest.fail('network setup after stop'))
    report = module.collect({}, tmp_path / 'public', stop_file=stop)
    assert report['status'] == 'stopped'
    assert report['downloaded'] == 0


def test_phase_behavior_uses_full_replay_before_sampling_and_excludes_test(tmp_path, monkeypatch):
    from tools.growth_rl import data as data_module
    from tools.growth_rl.behavior import phase_behavior_records, phase_behavior_summary

    def state(turns, pearls, deaths, wall, self_deaths, body, h2h, splits):
        return dict(dragon_turns=turns, pearls=pearls, deaths=deaths, deaths_wall=wall,
                    units=1, total=10, longest=10, pearls_bed=0, pearls_corpse=0,
                    pearls_init=0, pearls_unknown=0, deaths_self=self_deaths,
                    deaths_body=body, deaths_h2h=h2h, deaths_no_action=0, splits=splits)

    cumulative = {
        0: state(0, 0, 0, 0, 0, 0, 0, 0),
        10: state(10, 2, 0, 0, 0, 0, 0, 0),
        15: state(15, 3, 0, 0, 0, 0, 0, 0),
        25: state(25, 5, 1, 1, 0, 0, 0, 1),
        40: state(40, 6, 1, 1, 0, 0, 0, 1),
        50: state(50, 7, 2, 2, 0, 0, 0, 2),
        65: state(65, 8, 2, 2, 0, 0, 0, 2),
        75: state(75, 9, 2, 2, 0, 0, 0, 3),
        90: state(90, 9, 2, 2, 0, 0, 0, 3),
        100: state(100, 10, 3, 3, 0, 0, 0, 4),
    }
    game = dict(sha256='a' * 64, map='toy', result=dict(rounds=100, winner='A'),
                series={str(round_number): {side: values for side in 'AB'}
                        for round_number, values in cumulative.items()},
                rows=[dict(side='A', dragon=1, round=12, y_family='split', action=20),
                      dict(side='A', dragon=1, round=13, y_family='move', y_seq='FRF', action=None),
                      dict(side='B', dragon=2, round=14, y_family='move', y_seq='F', action=0)])
    replay = tmp_path / 'source.replay'
    replay.write_bytes(b'test replay')
    monkeypatch.setattr(data_module, 'replay_files', lambda roots: [replay])
    monkeypatch.setattr(data_module, 'digest', lambda path: 'a' * 64)
    monkeypatch.setattr(data_module, 'extract', lambda path, cache: copy.deepcopy(game))

    games, audit = data_module.dataset([tmp_path], tmp_path / 'cache', max_games=1, rows_per_side=1)
    assert audit == []
    trained = games[0]
    assert len(trained['rows']) == 2  # one sampled row per side
    assert set(trained['series']) == {str(r) for r in data_module.SERIES_ROUNDS}
    from tools.growth_rl.train import distribution_report
    checkpoints, _ = distribution_report([trained])
    assert len(checkpoints) == 10  # both sides at all five report checkpoints
    phase = next(row for row in trained['phase_behavior']
                 if row['side'] == 'A' and row['phase'] == 'r10-r25')
    assert phase['pearls'] == 3
    assert phase['pearls_per_1000_dragon_turns'] == 200
    assert phase['action_count'] == 2
    assert phase['split_action_share'] == 0.5
    assert phase['sprint_action_share'] == 0.5
    assert phase['supported_action_share'] == 0.5
    assert phase['complete'] is True

    trained['split'] = 'train'
    trained['provenance']['metadata'] = dict(source='public', rank_a=1, rank_b=20, ranked=True)
    locked = copy.deepcopy(trained)
    locked.update(sha256='locked-test', split='test')
    records = phase_behavior_records([trained, locked])
    assert len(records) == 10
    summary = phase_behavior_summary(records)
    top_win = next(row for row in summary if row['map_scope'] == 'map' and row['map'] == 'toy'
                   and row['cohort'] == 'top10_ranked' and row['phase'] == 'r10-r25'
                   and row['outcome'] == 'win' and row['complete'])
    assert top_win['side_games'] == 1
    assert top_win['pearls_per_1000_dragon_turns_p50'] == 200


def test_dataset_fingerprint_tracks_sampling_contract(monkeypatch):
    from tools.growth_rl import data as data_module

    games = [dict(sha256='a' * 64, split='train'), dict(sha256='b' * 64, split='validation')]
    compact = data_module.dataset_fingerprint(games, rows_per_side=96)
    assert compact == data_module.dataset_fingerprint(games, rows_per_side=96)
    assert compact != data_module.dataset_fingerprint(games, rows_per_side=128)
    assert compact != data_module.dataset_fingerprint(list(reversed(games)), rows_per_side=96)
    monkeypatch.setattr(data_module, 'VERSION', data_module.VERSION + 1)
    assert compact != data_module.dataset_fingerprint(games, rows_per_side=96)


def test_action_coverage_report_excludes_locked_test_games():
    from tools.growth_rl.behavior import action_coverage_report
    train = toy_game('train-coverage', 'train')
    validation = toy_game('validation-coverage', 'validation')
    locked = toy_game('locked-coverage', 'test')
    report = action_coverage_report([train, validation, locked])
    assert set(report) == {'train-coverage', 'validation-coverage'}


def test_pending_frozen_gate_resumes_before_newer_cycle_after_downloads(tmp_path):
    from tools.growth_rl.cycle_state import find_pending_cycle, fingerprint_after_completion

    older = tmp_path / '000004'
    newer = tmp_path / '000005'
    for cycle in (older, newer):
        cycle.mkdir()
    (older / 'training').mkdir()
    (older / 'candidate').mkdir()
    (older / 'training' / 'training_summary.json').write_text('{}')
    (older / 'candidate' / 'policy.json').write_text('{}')
    (older / 'cycle.json').write_text(json.dumps(dict(
        fingerprint='old-data', evaluation_hash='same-panel', phase='trained',
        candidate=str(older / 'candidate'))))
    (newer / 'cycle.json').write_text(json.dumps(dict(
        fingerprint='new-data', evaluation_hash='same-panel', phase='training')))

    pending = find_pending_cycle([newer, older], 'new-data', 'same-panel')
    assert pending[0] == older
    assert pending[1]['phase'] == 'trained'
    # Finishing this old frozen candidate must leave new-data eligible for a
    # later training cycle after all pending gates have completed.
    assert fingerprint_after_completion(pending[1], 'new-data') == 'old-data'
    assert fingerprint_after_completion({'fingerprint': 'new-data'}, 'new-data') == 'new-data'


def test_evaluation_fingerprint_ignores_worker_count_but_tracks_gate_semantics():
    from tools.growth_rl.runner import evaluation_fingerprint

    config = dict(seed=1701, training={'device': 'cuda', 'hidden': 64},
                  evaluation={'jobs': 4, 'bootstrap': 4000, 'panels': [{'name': 'pool'}]})
    fewer_workers = copy.deepcopy(config)
    fewer_workers['evaluation']['jobs'] = 2
    assert evaluation_fingerprint(config) == evaluation_fingerprint(fewer_workers)

    changed_gate = copy.deepcopy(fewer_workers)
    changed_gate['evaluation']['bootstrap'] = 2000
    assert evaluation_fingerprint(config) != evaluation_fingerprint(changed_gate)


def test_unfrozen_training_only_resumes_on_its_original_data(tmp_path):
    from tools.growth_rl.cycle_state import find_pending_cycle

    cycle = tmp_path / '000007'
    cycle.mkdir()
    (cycle / 'cycle.json').write_text(json.dumps(dict(
        fingerprint='old-data', evaluation_hash='same-panel', phase='training')))
    assert find_pending_cycle([cycle], 'new-data', 'same-panel') is None
    assert find_pending_cycle([cycle], 'old-data', 'same-panel')[0] == cycle


def test_game_bot_interpreter_prefers_existing_base_python(tmp_path, monkeypatch):
    from tools.growth_rl import evaluate

    base_python = tmp_path / 'python.exe'
    base_python.write_bytes(b'')
    monkeypatch.setattr(evaluate.sys, '_base_executable', str(base_python), raising=False)
    assert evaluate.bot_interpreter() == str(base_python.resolve())


def test_game_bot_interpreter_falls_back_when_base_python_is_missing(tmp_path, monkeypatch):
    from tools.growth_rl import evaluate

    venv_python = tmp_path / 'venv-python.exe'
    monkeypatch.setattr(evaluate.sys, '_base_executable', str(tmp_path / 'missing.exe'), raising=False)
    monkeypatch.setattr(evaluate.sys, 'base_prefix', str(tmp_path / 'empty-base'))
    monkeypatch.setattr(evaluate.sys, 'executable', str(venv_python))
    assert evaluate.bot_interpreter() == str(venv_python)
