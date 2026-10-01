"""Content-addressed extraction, team-level rewards, and permanent holdouts."""
from collections import Counter
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
FEATURES = ROOT / 'tools' / 'team_recon_claude'
sys.path.insert(0, str(FEATURES))
import features_view as FV
import recon
import roundblock
from .policy import observed_index

VERSION = 2
CHECKPOINTS = (0, 10, 25, 50, 75, 100)
PHASE_WINDOWS = ((0, 10), (10, 25), (25, 50), (50, 75), (75, 100))
# Retain checkpoints plus the preceding 10-round snapshots used by training
# distribution reports. Actor labels already contain their future outcomes.
SERIES_ROUNDS = (0, 10, 15, 25, 40, 50, 65, 75, 90, 100)
# Exclude identity/absolute orientation to discourage memorising public layouts.
EXCLUDED = {'x', 'y', 'xn', 'yn', 'facing_abs'}


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    temp.replace(path)


def digest(path):
    raw = Path(path).read_bytes()
    if raw[:2] == b'\x1f\x8b':
        raw = gzip.decompress(raw)
    return hashlib.sha256(raw).hexdigest()


def dataset_fingerprint(games, rows_per_side):
    """Identify both the replay set and the deterministic actor-row budget."""
    contract = dict(data_version=VERSION, rows_per_side=rows_per_side,
                    games=[(game['sha256'], game['split']) for game in games])
    encoded = json.dumps(contract, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(encoded).hexdigest()


def bucket(identity, salt='growth-v1'):
    """Stable as the corpus grows; never reshuffle an old test game into train."""
    number = int(hashlib.sha256(f'{salt}|{identity}'.encode()).hexdigest()[:8], 16) % 100
    return 'train' if number < 70 else 'validation' if number < 85 else 'test'


def replay_files(roots):
    paths = []
    for root in roots:
        root = Path(root)
        if root.is_dir():
            paths.extend(root.rglob('*.replay'))
            paths.extend(root.rglob('*.replay.gz'))
        elif root.is_file():
            paths.append(root)
    return sorted(set(p.resolve() for p in paths))


def team_state(game, side, counters):
    lengths = [len(d.body) for d in game.dragons.values() if d.alive and d.team == side]
    return dict(units=len(lengths), total=sum(lengths), longest=max(lengths, default=0),
                pearls=counters[side, 'pearls'], deaths=counters[side, 'deaths'],
                pearls_bed=counters[side, 'pearls_bed'],
                pearls_corpse=counters[side, 'pearls_corpse'],
                pearls_init=counters[side, 'pearls_init'],
                pearls_unknown=counters[side, 'pearls_unknown'],
                deaths_wall=counters[side, 'deaths_wall'],
                deaths_self=counters[side, 'deaths_self'],
                deaths_body=counters[side, 'deaths_body'],
                deaths_body_ally=counters[side, 'deaths_body_ally'],
                deaths_body_enemy=counters[side, 'deaths_body_enemy'],
                deaths_h2h=counters[side, 'deaths_h2h'],
                deaths_h2h_ally=counters[side, 'deaths_h2h_ally'],
                deaths_h2h_enemy=counters[side, 'deaths_h2h_enemy'],
                deaths_no_action=counters[side, 'deaths_no_action'],
                splits=counters[side, 'splits'], dragon_turns=counters[side, 'turns'])


def phase_behavior(game):
    """Summarise full-replay event and action rates in fixed turn windows.

    Call this before ``dataset`` downsamples actor rows. Cumulative event
    counters come from the exact reconstructed team states, while action
    shares use every recorded turn in the window.
    """
    series = game['series']

    def state_at(round_number, side):
        snapshot = series.get(str(round_number), series.get(round_number))
        if snapshot is None:
            raise ValueError(f'missing round {round_number} for phase report')
        return snapshot[side]

    final_round = int(game['result']['rounds'])
    all_rows = game.get('rows', [])
    report = []
    counter_names = ('pearls', 'deaths', 'deaths_wall', 'deaths_self',
                     'deaths_body', 'deaths_h2h', 'splits')
    for side in 'AB':
        for start, end in PHASE_WINDOWS:
            before, after = state_at(start, side), state_at(end, side)
            turns = after['dragon_turns'] - before['dragon_turns']
            rows = [row for row in all_rows
                    if row['side'] == side and start <= row['round'] < end]
            move_actions = sum(row.get('y_family') == 'move' for row in rows)
            split_actions = sum(row.get('y_family') == 'split' for row in rows)
            sprint_actions = sum(row.get('y_family') == 'move' and len(row.get('y_seq', '')) > 1
                                 for row in rows)
            supported_actions = sum(row.get('action') is not None for row in rows)
            denominator = turns if turns > 0 else None
            action_denominator = len(rows) if rows else None
            record = dict(side=side, phase=f'r{start}-r{end}', round_start=start,
                          round_end=end, complete=final_round >= end,
                          dragon_turns=turns, action_count=len(rows),
                          move_actions=move_actions, split_actions=split_actions,
                          sprint_actions=sprint_actions, supported_actions=supported_actions)
            for name in counter_names:
                record[name] = after[name] - before[name]
            for name, count in (('pearls_per_1000_dragon_turns', record['pearls']),
                                ('deaths_per_1000_dragon_turns', record['deaths']),
                                ('wall_deaths_per_1000_dragon_turns', record['deaths_wall']),
                                ('self_deaths_per_1000_dragon_turns', record['deaths_self']),
                                ('body_deaths_per_1000_dragon_turns', record['deaths_body']),
                                ('h2h_deaths_per_1000_dragon_turns', record['deaths_h2h']),
                                ('splits_per_1000_dragon_turns', record['splits'])):
                record[name] = 1000 * count / denominator if denominator else None
            record['split_action_share'] = split_actions / action_denominator if action_denominator else None
            record['sprint_action_share'] = sprint_actions / action_denominator if action_denominator else None
            record['supported_action_share'] = supported_actions / action_denominator if action_denominator else None
            report.append(record)
    return report


def extract(path, cache):
    """Run both perspectives once; privileged state is targets/analysis only."""
    sha = digest(path)
    out = Path(cache) / f'{sha}-v{VERSION}.json.gz'
    if out.exists():
        with gzip.open(out, 'rt', encoding='utf-8') as stream:
            return json.load(stream)
    game = recon.Game(path)
    if game.version not in (1, 2):
        raise ValueError(f'unsupported replay version {game.version}')
    procs, rows, series, pending, counters = {}, [], {}, {}, Counter()

    def callback(kind, **info):
        if kind == 'round' and game.round <= 100:
            series[game.round] = {side: team_state(game, side, counters) for side in 'AB'}
        elif kind == 'turn' and 0 <= game.round < 100:
            d = info['dragon']
            proc = procs.setdefault(d.id, FV.Proc(d.id, d.team, game.board.W, game.board.H, game.board.unit_limit))
            lines = roundblock.build_block(game, d, proto3=(d.turns > 0 or d.parent is not None))
            block, _ = FV.parse_block(lines)
            features = proc.features(block)
            row = {k: v for k, v in features.items() if k not in EXCLUDED}
            row.update(dragon=d.id, side=d.team, game=sha,
                       target_current=team_state(game, d.team, counters))
            pending[d.id] = (row, proc, d.facing)
            counters[d.team, 'turns'] += 1
        elif kind == 'action' and info['dragon'].id in pending:
            row, proc, facing = pending.pop(info['dragon'].id)
            action = info['action']
            row['y_family'] = action[0]
            if action[0] == 'move':
                rels = []
                for direction in action[1]:
                    rels.append(FV.abs_to_rel(FV.DIRS[recon.DIRS.index(facing)], FV.DIRS[recon.DIRS.index(direction)]))
                    facing = direction
                row['y_seq'] = ''.join(rels)
                proc.record_action('move', rels=rels)
            elif action[0] == 'split':
                row['y_split'] = action[1]
                proc.record_action('split', split=action[1])
            row['action'] = observed_index(row)
            rows.append(row)
        elif kind == 'pearl_eat' and info['dragon'] is not None and game.round < 100:
            counters[info['dragon'].team, 'pearls'] += 1
            origin = info.get('prov')
            counters[info['dragon'].team, f'pearls_{origin}' if origin in ('bed', 'corpse', 'init') else 'pearls_unknown'] += 1
        elif kind == 'death' and game.round < 100:
            victim = info['dragon']
            reason = info.get('reason')
            reason_metric = {
                'hitWall': 'wall', 'hitSelf': 'self', 'hitOtherBody': 'body',
                'hitHeadToHead': 'h2h', 'noValidAction': 'no_action',
            }.get(reason)
            counters[victim.team, 'deaths'] += 1
            if reason_metric:
                counters[victim.team, f'deaths_{reason_metric}'] += 1
            if reason_metric in ('body', 'h2h'):
                attacker = game.dragons.get(info.get('actor'))
                if attacker is not None:
                    relation = 'ally' if attacker.team == victim.team else 'enemy'
                    counters[victim.team, f'deaths_{reason_metric}_{relation}'] += 1
        elif kind == 'split' and game.round < 100:
            counters[info['parent'].team, 'splits'] += 1

    game.run(callback)
    if game.checks['standings_bad'] or game.checks['step_bad'] or game.checks['init_head_mismatch']:
        raise ValueError(f'reconstruction mismatch: {dict(game.checks)}')
    if not game.result['terminated']:
        raise ValueError('unfinished replay (engine result is not terminated)')
    terminal = {side: team_state(game, side, counters) for side in 'AB'}
    # Absorbing terminal state is explicit, not silently a played round 100.
    # Cumulative events stop at termination. Reports include ended_before_100.
    for r in range(101):
        if r not in series:
            if r >= game.result['rounds']:
                series[r] = terminal
            else:
                raise ValueError(f'missing nonterminal round {r}')
    names = sorted(k for k, v in rows[0].items()
                   if isinstance(v, (int, float)) and k not in {'dragon', 'action'} and not k.startswith('y_')) if rows else []
    for row in rows:
        row['target_horizons'] = [series[min(100, row['round'] + k)][row['side']] for k in (10, 25, 100)]
        row['target_win'] = (0.5 if game.result['winner'] is None else float(game.result['winner'] == row['side']))
    result = dict(version=VERSION, sha256=sha, features=names, rows=rows,
                  map=game.board.name, map_hash=hashlib.sha256(game.rep.map.encode()).hexdigest(),
                  result=game.result, checks=dict(game.checks),
                  series=series, coverage=dict(Counter('supported' if row['action'] is not None else row['y_family'] for row in rows)))
    out.parent.mkdir(parents=True, exist_ok=True)
    temp = out.with_suffix('.tmp')
    with gzip.open(temp, 'wt', encoding='utf-8') as stream:
        json.dump(result, stream, allow_nan=False)
    temp.replace(out)
    return result


def targets(row, population_weight=0.25):
    """Log retained-material growth + configurable log population growth.

    No action-specific rewards. Splitting preserves length; a child's death
    affects the whole team's outcome even when its parent survives.
    """
    current = row['target_current']
    rewards = []
    for future in row['target_horizons']:
        rewards.append(math.log1p(future['total']) - math.log1p(current['total']) + population_weight * (
            math.log1p(future['units']) - math.log1p(current['units'])))
    return rewards + [row['target_win']]


def provenance(path, sha):
    metadata = Path(path).with_suffix('.json')
    payload = json.loads(metadata.read_text(encoding='utf-8')) if metadata.exists() else {}
    # Downloader battle/series identity groups mirrored games where known.
    group = payload.get('series_id') or payload.get('battle_id') or sha
    if payload.get('fixture'):
        group = hashlib.sha256(json.dumps({k: v for k, v in payload['fixture'].items() if k != 'side'}, sort_keys=True).encode()).hexdigest()
    return dict(group=str(group), metadata=payload, path=str(path))


def dataset(roots, cache, max_games=200, rows_per_side=256):
    games, seen, audit = [], set(), []
    # Deterministic reservoir rather than the first N filenames forever.
    paths = replay_files(roots)
    paths.sort(key=lambda p: hashlib.sha256(str(p).encode()).hexdigest())
    for path in paths:
        try:
            sha = digest(path)
            if sha in seen:
                continue
            seen.add(sha)
            data = extract(path, cache)
            data['provenance'] = provenance(path, sha)
            metadata = data['provenance']['metadata']
            if metadata.get('source') == 'evaluation':
                raise ValueError('evaluation replay must never enter the training corpus')
            data['split'] = bucket(data['provenance']['group'])
            data['phase_behavior'] = phase_behavior(data)
            full_series = data['series']
            data['series'] = {
                str(round_number): full_series.get(str(round_number), full_series.get(round_number))
                for round_number in SERIES_ROUNDS
                if full_series.get(str(round_number), full_series.get(round_number)) is not None
            }
            # Bound RAM while preserving both side-games and all checkpoints.
            # Sample only after exact full replay reconstruction and reward
            # labelling; sampling never turns a truncated trajectory into death.
            sampled = []
            for side in 'AB':
                side_rows = [r for r in data['rows'] if r['side'] == side]
                side_rows.sort(key=lambda r: hashlib.sha256(f'{sha}|{side}|{r["dragon"]}|{r["round"]}'.encode()).hexdigest())
                sampled.extend(side_rows[:rows_per_side] if rows_per_side else side_rows)
            data['rows'] = sampled
            games.append(data)
            print(f'extracted {len(games)} {path.name}: {len(data["rows"])} turns', flush=True)
            if max_games and len(games) >= max_games:
                break
        except Exception as exc:
            audit.append(dict(path=str(path), error=f'{type(exc).__name__}: {exc}'))
    return games, audit
