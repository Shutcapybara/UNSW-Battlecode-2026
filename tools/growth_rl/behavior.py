"""Full-replay behavior summaries, independent of the trainer runtime."""
from .data import phase_behavior


def action_coverage_report(games):
    """Keep locked test action-coverage counts out of training artifacts."""
    return {game['sha256']: game['coverage'] for game in games
            if game.get('split') in ('train', 'validation')}


def cohort_label(meta, side):
    origin = meta.get('source', 'unknown')
    rank = meta.get('rank_' + side.lower())
    if origin == 'public':
        tier = 'unknown_rank' if rank is None else 'top10' if rank <= 10 else 'other_field'
        ranked = meta.get('ranked')
        return f'{tier}_{"ranked" if ranked else "unranked"}' if isinstance(ranked, bool) else tier
    if origin == 'local_rollout':
        if side != meta.get('actor_side') and meta.get('opponent_family') == 'top10_ranked_winner_tree':
            return 'local_tree_top10_winner'
        return 'learned' if side == meta.get('actor_side') else 'local_opponent'
    return origin


def phase_behavior_records(games):
    """Return one complete-replay behavior record per side-game and phase.

    Locked test games are omitted. ``dataset`` attaches phase counts before
    sampling actor rows, so the rates remain full-replay measurements.
    """
    records = []
    for game in games:
        if game.get('split') == 'test':
            continue
        meta = game.get('provenance', {}).get('metadata', {})
        phases = game.get('phase_behavior')
        if phases is None:
            phases = phase_behavior(game)
        for phase in phases:
            side = phase['side']
            rank = meta.get('rank_' + side.lower())
            records.append({**phase, 'game': game['sha256'], 'map': game.get('map'),
                            'outcome': 'draw' if game['result']['winner'] is None else
                            'win' if game['result']['winner'] == side else 'loss',
                            'cohort': cohort_label(meta, side),
                            'team_id': meta.get('team_' + side.lower()),
                            'submission': meta.get('submission_' + side.lower()),
                            'rank_snapshot': rank, 'ranked_game': meta.get('ranked'),
                            'fetched_at': meta.get('fetched_at'), 'split': game.get('split')})
    return records


def phase_behavior_summary(records):
    """Summarise phase behavior by cohort, outcome, completion, and map.

    Pooled and map-specific distributions are both emitted. These are
    descriptive side-game samples, not independent or causal estimates.
    """
    import pandas as pd
    frame = pd.DataFrame(records)
    if frame.empty:
        return []
    metrics = ('dragon_turns', 'pearls', 'deaths', 'deaths_wall', 'deaths_self',
               'deaths_body', 'deaths_h2h', 'splits', 'action_count', 'move_actions',
               'split_actions', 'sprint_actions', 'supported_actions',
               'pearls_per_1000_dragon_turns', 'deaths_per_1000_dragon_turns',
               'wall_deaths_per_1000_dragon_turns', 'self_deaths_per_1000_dragon_turns',
               'body_deaths_per_1000_dragon_turns', 'h2h_deaths_per_1000_dragon_turns',
               'splits_per_1000_dragon_turns', 'split_action_share',
               'sprint_action_share', 'supported_action_share')
    summaries = []
    for by_map in (False, True):
        keys = ['cohort', 'phase', 'complete'] + (['map'] if by_map else [])
        for key, group in frame.groupby(keys, dropna=False, sort=True):
            values = key if isinstance(key, tuple) else (key,)
            grouping = dict(zip(keys, values))
            for outcome in ('all', 'win', 'loss', 'draw'):
                part = group if outcome == 'all' else group[group.outcome == outcome]
                if part.empty:
                    continue
                record = dict(cohort=str(grouping['cohort']), phase=str(grouping['phase']),
                              complete=bool(grouping['complete']), outcome=outcome,
                              map=str(grouping['map']) if by_map else None,
                              map_scope='map' if by_map else 'all_maps',
                              side_games=int(len(part)), games=int(part['game'].nunique()),
                              teams=int(part['team_id'].nunique()),
                              submission_identity_fraction=float(part['submission'].notna().mean()),
                              rank_snapshot_fraction=float(part['rank_snapshot'].notna().mean()))
                for name in metrics:
                    series = part[name].astype(float).dropna()
                    record[f'{name}_n'] = int(len(series))
                    if series.empty:
                        continue
                    record[f'{name}_mean'] = float(series.mean())
                    record[f'{name}_std'] = float(series.std(ddof=0))
                    for q in (10, 25, 50, 75, 90):
                        record[f'{name}_p{q}'] = float(series.quantile(q / 100))
                summaries.append(record)
    return summaries
