from tools.hub.analysis import layout_assignment, paired_contrast, runtime_sonar


def game(sub, score, *, layout='L', opp=7):
    stages = {str(r): {'units': 4, 'total': 10, 'longest': 8, 'deaths': 2, 'sonar': 12, 'turns': 6}
              for r in (100, 250, 400, 499)}
    return dict(verified=True, origin='controlled', pool='field', own_submission=sub,
                score=score, map_name='Portals', api_side='A', opponent_submission=opp,
                map_hash=layout, seed='s1', requested='t', stages=stages, cpu_max=50_000_000)


def test_paired_contrast_uses_exact_layout_and_opponent_cells():
    rows = [game(1, 1), game(2, 0), game(1, 1, layout='other'), game(2, 0, layout='other')]
    rows += [game(1, 1, opp=8), game(2, 0, opp=9)]
    result = paired_contrast(rows, 1, 2)
    assert result['n_cells'] == 2
    assert result['deltas']['score']['mean_delta'] == 1
    assert result['deltas']['score']['better'] == 2


def test_layout_and_runtime_summaries_keep_games_as_units():
    rows = [game(1, 1), game(1, 0, layout='other')]
    layout = layout_assignment(rows)
    assert layout['repeated_seed_conflicts'] == 1
    rt = runtime_sonar(rows)['1']
    assert rt['n'] == 2 and rt['cpu_max'] == 50_000_000
    assert rt['near_cap_games'] == 0
