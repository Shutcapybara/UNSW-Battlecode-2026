"""Flatten the legacy live-validation record (`LIVE/state/state.json`) into one row per game.

Reads selected keys only (`results`, `blocks`, `requests`, `experiments`, `seen_series`, `events`); never dumps the
file. Every stage field of the game's own side and of the opponent is flattened to `s{round}_{field}` and
`o{round}_{field}`; block / experiment / arm membership comes from `blocks[].requests`; ranked flags, requester and
Elo changes come from `seen_series`. Missing fields stay missing (NaN), never zero.

Usage:
    python -m tools.analysis.live_record --state LIVE/state/state.json --out build/live_games.parquet
    python -m tools.analysis.live_record --state ... --summary            # print the headline counts
"""
import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

COMPACT = {'Portals', 'Prisoners Dilemma', 'Devil', 'Trophy'}       # <= 625 tiles on the live pool
STAGES = (100, 200, 250, 300, 320, 360, 380, 400, 450, 499)
STAGE_FIELDS = ('units', 'total', 'longest', 'leader', 'peak_units', 'turns', 'cpu_max', 'cpu_recorded', 'splits', 'sonar',
                'pearls', 'pearls_bed', 'fresh_bed', 'deaths', 'death_wall', 'death_h2h', 'death_body', 'death_self',
                'death_invalid', 'length_lost', 'newborn_deaths_10', 'pearls_ally_corpse', 'pearls_enemy_corpse', 'sprints',
                'extra_steps', 'initiated_h2h', 'enemy_h2h', 'friendly_h2h', 'fresh_enemy_corpse', 'fresh_ally_corpse',
                'portal_steps', 'body_ally', 'tle', 'visited_cells')
GAME_FIELDS = ('game_id', 'submission', 'side', 'map_id', 'map_name', 'series', 'requested', 'seed', 'pool', 'verified',
               'origin', 'opponent', 'opponent_submission', 'score', 'longest_margin', 'rounds', 'reason', 'faults', 'turns',
               'caught_errors', 'cpu_max', 'cpu_recorded', 'map_hash', 'replay_sha256', 'decoded_sha256', 'decoder_revision',
               'early_elimination', 'ally_corpse_collections', 'error')


def load_state(path):
    """Load state.json and keep only the keys the analyses use."""
    raw = json.loads(Path(path).read_text())
    return {k: raw.get(k) for k in ('version', 'incumbent', 'updated', 'results', 'blocks', 'requests', 'experiments',
                                    'decisions', 'seen_series', 'events', 'map_ids', 'quota_used')}


def parse_ts(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)
    try:
        return datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except ValueError:
        return None


def block_index(state):
    """game_id -> (block dict, position of the game inside the block's request list)."""
    out = {}
    for b in state.get('blocks') or []:
        pos = 0
        for group in b.get('requests') or []:
            for gid in group:
                out[int(gid)] = (b, pos)
                pos += 1
    return out


def request_index(state):
    """game_id -> (request dict, position inside the request)."""
    out = {}
    for i, r in enumerate(state.get('requests') or []):
        for pos, gid in enumerate(r.get('ids') or []):
            out[int(gid)] = (i, r, pos)
    return out


def series_index(state):
    """game_id -> match payload of the series it belongs to (ranked flag, requester, Elo change, seed, sides)."""
    out = {}
    for sid, payload in (state.get('seen_series') or {}).items():
        if not isinstance(payload, dict):
            continue
        match = payload.get('match') or {}
        for g in payload.get('games') or []:
            try:
                out[int(g['id'])] = dict(series_id=sid, ranked=match.get('ranked'), requested_by=match.get('requestedBy'),
                                         elo_change_a=match.get('eloChangeA'), elo_change_b=match.get('eloChangeB'),
                                         match_seed=match.get('seed'), team_a=match.get('teamAId'), team_b=match.get('teamBId'),
                                         submission_a=match.get('submissionAId'), submission_b=match.get('submissionBId'),
                                         match_map_hash=match.get('mapHash'), started_at=match.get('startedAt'),
                                         completed_at=match.get('completedAt'), series_requested_at=match.get('requestedAt'),
                                         team_a_elo=payload.get('teamAElo'), team_b_elo=payload.get('teamBElo'),
                                         match_winner=match.get('winner'), match_scores_a=match.get('scoresA'), match_scores_b=match.get('scoresB'))
            except (KeyError, TypeError, ValueError):
                continue
    return out


def flatten_game(r, blocks, requests, series, experiments):
    row = {k: r.get(k) for k in GAME_FIELDS}
    row['game_id'] = int(row['game_id'])
    row['requested_ts'] = parse_ts(r.get('requested'))
    row['map_class'] = 'compact' if r.get('map_name') in COMPACT else 'open'
    fin = r.get('final') or {}
    for k in ('units', 'longest', 'total'):
        row['final_' + k] = fin.get(k)
    fl = r.get('first_length') or {}
    row['first_length_10'] = fl.get('10')
    row['first_length_20'] = fl.get('20')
    sd = r.get('self_deaths_by_stage') or {}
    row['self_deaths_total'] = sum(sd.values()) if sd else None
    st = r.get('stats') or {}
    for k in STAGE_FIELDS:
        row['st_' + k] = st.get(k)
    for side_key, prefix in (('stages', 's'), ('opponent_stages', 'o')):
        stages = r.get(side_key) or {}
        for rr in STAGES:
            block = stages.get(str(rr)) or {}
            for k in STAGE_FIELDS:
                row[f'{prefix}{rr}_{k}'] = block.get(k)
    b, pos = blocks.get(row['game_id'], (None, None))
    row['block_id'] = b.get('id') if b else None
    row['block_phase'] = b.get('phase') if b else None
    row['block_control'] = b.get('control') if b else None
    row['block_candidate'] = b.get('candidate') if b else None
    row['block_opponent'] = b.get('opponent') if b else None
    row['block_created'] = b.get('created') if b else None
    row['block_position'] = pos
    row['experiment_id'] = b.get('experiment') if b else None
    if b and row.get('submission') is not None:
        if b.get('candidate') == b.get('control'):
            row['arm'] = 'control'
        elif row['submission'] == b.get('candidate'):
            row['arm'] = 'candidate'
        elif row['submission'] == b.get('control'):
            row['arm'] = 'control'
        else:
            row['arm'] = None
    else:
        row['arm'] = None
    ri = requests.get(row['game_id'])
    row['request_index'] = ri[0] if ri else None
    row['request_at'] = parse_ts(ri[1].get('at')) if ri else None
    row['request_position'] = ri[2] if ri else None
    row['request_count'] = ri[1].get('count') if ri else None
    row['request_status'] = ri[1].get('status') if ri else None
    s = series.get(row['game_id']) or {}
    for k, v in s.items():
        row['series_' + k] = v
    e = experiments.get(row.get('experiment_id')) or {}
    row['experiment_status'] = e.get('status')
    row['experiment_candidate'] = e.get('candidate')
    row['experiment_control'] = e.get('control')
    return row


def games_table(state):
    import pandas as pd
    blocks = block_index(state)
    requests = request_index(state)
    series = series_index(state)
    experiments = {e['id']: e for e in (state.get('experiments') or [])}
    rows = [flatten_game(r, blocks, requests, series, experiments) for r in (state.get('results') or {}).values()]
    df = pd.DataFrame(rows).sort_values('game_id').reset_index(drop=True)
    for col in ('requested_ts', 'request_at'):
        df[col] = pd.to_datetime(df[col], utc=True)
    return df


def summary(df):
    ok = df[df['verified'] == True]  # noqa: E712
    out = dict(games=len(df), verified=int(len(ok)), unverified=int((df['verified'] != True).sum()),
               controlled=int((ok['origin'] == 'controlled').sum()), observational=int((ok['origin'] == 'observational').sum()),
               sides=ok['side'].value_counts().to_dict(), pools=ok['pool'].value_counts().to_dict(),
               submissions=ok['submission'].value_counts().to_dict(), opponents=ok['opponent'].value_counts().to_dict(),
               maps=ok['map_name'].value_counts().to_dict(), reasons=ok['reason'].value_counts().to_dict(),
               first_requested=str(df['requested_ts'].min()), last_requested=str(df['requested_ts'].max()))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--state', required=True)
    ap.add_argument('--out')
    ap.add_argument('--summary', action='store_true')
    args = ap.parse_args()
    df = games_table(load_state(args.state))
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        if args.out.endswith('.parquet'):
            df.to_parquet(args.out, index=False)
        else:
            df.to_csv(args.out, index=False)
    if args.summary or not args.out:
        print(json.dumps(summary(df), indent=1, default=str))


if __name__ == '__main__':
    main()
