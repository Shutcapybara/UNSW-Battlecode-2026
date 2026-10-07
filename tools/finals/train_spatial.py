"""Warm-start and train the two-stream finals policy with live PPO and a fixed monitor panel.

This is a research trainer: the monitor is for progress/plateau diagnosis, not promotion.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from concurrent.futures import ProcessPoolExecutor
import hashlib
from itertools import count
import json
import multiprocessing as mp
from pathlib import Path
import shutil
import time

import numpy as np
import torch
from torch import nn
from torch.distributions import Categorical
from torch.nn import functional as F

from collect import SHAPING_ALPHA, SHAPING_NAME, episode
from spatial_model import SpatialPolicy, TYPE_CHANNELS

ROOT = Path(__file__).resolve().parents[2]
GAMMA = 0.997
LEARNING_RATE = 0.0003
PPO_CLIP = 0.2
ENTROPY_COEF = 0.01
VALUE_COEF = 0.5
GRAD_NORM = 0.5


# Rollout workers are deliberately process-isolated.  Each worker owns its
# EngineModule, native bot children, RNG, and read-only policy snapshot.  This
# avoids sharing wasm/engine state or a mutable torch module across games while
# allowing independent episodes to overlap.
_WORKER_POLICY = None


def _actor_kwargs(actor, actor_kind: str | None, *, greedy: bool) -> dict:
    if actor is None or actor_kind is None:
        return {}
    action_view = actor.action_view
    sonar_view = actor.sonar_view
    action_callback = action_view.greedy if greedy else action_view.sample
    sonar_callback = sonar_view.greedy if greedy else sonar_view.sample
    if actor_kind == 'joint':
        return {'action_actor': action_callback, 'sonar_actor': sonar_callback}
    if actor_kind == 'action':
        return {'action_actor': action_callback}
    if actor_kind == 'sonar':
        return {'sonar_actor': sonar_callback}
    raise ValueError(f'unknown actor kind: {actor_kind}')


def _write_episode_artifacts(output: Path, arrays: dict, summary: dict, replay: bytes) -> None:
    """Write one completed rollout so worker failure cannot look complete."""
    output.mkdir(parents=True, exist_ok=True)
    npz_tmp = output / 'episode.npz.tmp'
    with npz_tmp.open('wb') as stream:
        np.savez_compressed(stream, **arrays)
    npz_tmp.replace(output / 'episode.npz')
    replay_tmp = output / 'game.replay.tmp'
    replay_tmp.write_bytes(replay)
    replay_tmp.replace(output / 'game.replay')
    atomic_json(output / 'summary.json', summary)


def _init_rollout_worker(actor_state, worker_threads: int) -> None:
    global _WORKER_POLICY
    torch.set_num_threads(worker_threads)
    if actor_state is None:
        _WORKER_POLICY = None
        return
    policy = SpatialPolicy()
    policy.load_state_dict(actor_state)
    policy.eval()
    _WORKER_POLICY = policy


def _run_rollout_task(spec: dict) -> dict:
    actor = _WORKER_POLICY
    arrays, summary, replay = episode(
        Path(spec['bridge']), Path(spec['opponent']), Path(spec['board']),
        spec['seed'], spec['seat'], gamma=GAMMA, capture=spec['capture'],
        **_actor_kwargs(actor, spec['actor_kind'], greedy=spec['greedy']))
    if spec['output'] is not None:
        if arrays is None:
            raise RuntimeError('training rollout did not capture arrays')
        _write_episode_artifacts(Path(spec['output']), arrays, summary, replay)
    return summary


def _run_rollout_local(spec: dict, actor) -> dict:
    arrays, summary, replay = episode(
        Path(spec['bridge']), Path(spec['opponent']), Path(spec['board']),
        spec['seed'], spec['seat'], gamma=GAMMA, capture=spec['capture'],
        **_actor_kwargs(actor, spec['actor_kind'], greedy=spec['greedy']))
    if spec['output'] is not None:
        if arrays is None:
            raise RuntimeError('training rollout did not capture arrays')
        _write_episode_artifacts(Path(spec['output']), arrays, summary, replay)
    return summary


def _snapshot_policy(actor) -> dict:
    return {name: tensor.detach().cpu().clone() for name, tensor in actor.state_dict().items()}


def run_rollouts(specs: list[dict], actor=None, *, workers: int, threads: int) -> list[dict]:
    """Run independent episodes, returning summaries in input order."""
    if not specs:
        return []
    if workers <= 1:
        return [_run_rollout_local(spec, actor) for spec in specs]

    max_workers = min(workers, len(specs))
    worker_threads = max(1, threads // max_workers)
    actor_state = None if actor is None else _snapshot_policy(actor)
    context = mp.get_context('spawn')
    with ProcessPoolExecutor(
        max_workers=max_workers,
        mp_context=context,
        initializer=_init_rollout_worker,
        initargs=(actor_state, worker_threads),
    ) as pool:
        futures = [pool.submit(_run_rollout_task, spec) for spec in specs]
        return [future.result() for future in futures]


def update_sequence(start: int, target: int, until_stopped: bool):
    """Yield absolute update indices, with an optional genuinely unbounded run."""
    return count(start) if until_stopped else range(start, target)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def file_id(path: Path) -> dict:
    path = path.resolve()
    if not path.is_file():
        raise ValueError(f'input file does not exist: {path}')
    return {'path': str(path), 'sha256': sha256(path)}


def atomic_json(path: Path, value) -> None:
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2) + '\n')
    temp.replace(path)


def team_round_weights(episode_ids, rounds, valid):
    pairs = [(int(e), int(r)) for e, r, ok in zip(episode_ids, rounds, valid) if ok]
    counts = Counter(pairs)
    round_counts = Counter(e for e, r in counts)
    return np.asarray([1.0 / (counts[(int(e), int(r))] * round_counts[int(e)]) if ok else 0.0
                       for e, r, ok in zip(episode_ids, rounds, valid)], dtype=np.float32)


def concat_episodes(files: list[Path]) -> dict:
    loaded = [dict(np.load(path)) for path in files]
    data = {key: np.concatenate([episode[key] for episode in loaded])
            for key in loaded[0] if all(key in episode for episode in loaded)}
    if 'chosen_action_features' not in data:
        rows = np.arange(len(data['action']))
        data['chosen_action_features'] = data['action_features'][rows, data['action']]
    return data


def warmstart(policy: SpatialPolicy, mode: str, files: list[Path], *, epochs: int,
              batch_size: int, seed: int) -> dict:
    """Clone incumbent choices into one or both heads using the same shared encoder."""
    data = concat_episodes(files)
    valid = data['actor_valid'].astype(bool)
    action_eligible = valid & (data['action_mask'].sum(axis=-1) > 1)
    sonar_eligible = valid & np.any(data['sonar_mask'].sum(axis=-1) > 1, axis=-1)
    use_action = mode in ('joint', 'action')
    use_sonar = mode in ('joint', 'sonar')
    if use_action and np.any(data['action'][valid] != 0):
        raise ValueError('action warm-start data must contain baseline choice 0 labels')
    if use_sonar and np.any(data['sonar'][valid] != 0):
        raise ValueError('sonar warm-start data must contain baseline choice 0 labels')
    keep = (action_eligible if use_action else np.zeros_like(valid)) | \
           (sonar_eligible if use_sonar else np.zeros_like(valid))
    indices = np.flatnonzero(keep)
    if len(indices) < 20:
        raise ValueError(f'need at least 20 selectable warm-start turns, got {len(indices)}')
    rng = np.random.default_rng(seed)
    order = rng.permutation(indices)
    n_valid = max(1, min(len(order) - 1, int(round(len(order) * 0.1))))
    validation, training = order[:n_valid], order[n_valid:]
    optimizer = torch.optim.Adam(policy.parameters(), lr=0.001)
    history = []
    policy.train()
    for epoch in range(epochs):
        permutation = rng.permutation(training)
        loss_sum = 0.0
        for begin in range(0, len(permutation), batch_size):
            idx = permutation[begin:begin + batch_size]
            xt = torch.as_tensor(data['x'][idx])
            context = policy.encode(xt)
            losses = []
            if use_action:
                local = np.flatnonzero(action_eligible[idx])
                if len(local):
                    logits = policy.action_head(
                        context[local], torch.as_tensor(data['action_features'][idx][local], dtype=torch.float32))
                    mask = torch.as_tensor(data['action_mask'][idx][local], dtype=torch.bool)
                    labels = torch.as_tensor(data['action'][idx][local], dtype=torch.long)
                    losses.append(F.cross_entropy(logits.masked_fill(~mask, -1e9), labels))
            if use_sonar:
                sf = data['sonar_features'][idx].reshape(-1, 5, 32)
                sm = data['sonar_mask'][idx].reshape(-1, 5)
                sl = data['sonar'][idx].reshape(-1)
                ray_keep = (sm.sum(axis=-1) > 1) & np.repeat(valid[idx], 4)
                if ray_keep.any():
                    repeated_context = context[:, None, :].expand(-1, 4, -1).reshape(-1, 128)
                    action_context = torch.as_tensor(data['chosen_action_features'][idx], dtype=torch.float32)
                    repeated_action = action_context[:, None, :].expand(-1, 4, -1).reshape(-1, 32)
                    logits = policy.sonar_head(repeated_context,
                                               torch.as_tensor(sf, dtype=torch.float32), repeated_action)
                    mask = torch.as_tensor(sm[ray_keep], dtype=torch.bool)
                    labels = torch.as_tensor(sl[ray_keep], dtype=torch.long)
                    losses.append(F.cross_entropy(logits[torch.as_tensor(ray_keep)].masked_fill(~mask, -1e9), labels))
            if not losses:
                continue
            loss = torch.stack(losses).sum()
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            nn.utils.clip_grad_norm_(policy.parameters(), GRAD_NORM)
            optimizer.step()
            loss_sum += float(loss.detach()) * len(idx)
        history.append(loss_sum / len(training))

    policy.eval()
    clone = {}
    with torch.no_grad():
        for kind, eligible, labels_name, features_name, mask_name in (
            ('action', action_eligible, 'action', 'action_features', 'action_mask'),
            ('sonar', sonar_eligible, 'sonar', 'sonar_features', 'sonar_mask')):
            if (kind == 'action' and not use_action) or (kind == 'sonar' and not use_sonar):
                continue
            rows = validation[eligible[validation]]
            if not len(rows):
                clone[kind] = {'validation_rows': 0}
                continue
            if kind == 'action':
                logits = policy(torch.as_tensor(data['x'][rows]),
                                torch.as_tensor(data[features_name][rows], dtype=torch.float32), kind)
                masks = torch.as_tensor(data[mask_name][rows], dtype=torch.bool)
                targets = torch.as_tensor(data[labels_name][rows], dtype=torch.long)
            else:
                x = np.repeat(data['x'][rows], 4, axis=0)
                feats = data[features_name][rows].reshape(-1, 5, 32)
                masks_np = data[mask_name][rows].reshape(-1, 5)
                target_np = data[labels_name][rows].reshape(-1)
                ac = np.repeat(data['chosen_action_features'][rows], 4, axis=0)
                selected_rays = masks_np.sum(axis=-1) > 1
                logits = policy(torch.as_tensor(x[selected_rays]),
                                torch.as_tensor(feats[selected_rays], dtype=torch.float32), kind,
                                torch.as_tensor(ac[selected_rays], dtype=torch.float32))
                masks = torch.as_tensor(masks_np[selected_rays], dtype=torch.bool)
                targets = torch.as_tensor(target_np[selected_rays], dtype=torch.long)
            logits = logits.masked_fill(~masks, -1e9)
            clone[kind] = {'validation_rows': len(targets),
                           'validation_loss': float(F.cross_entropy(logits, targets)),
                           'validation_accuracy': float((logits.argmax(dim=-1) == targets).float().mean())}
    return {
        'mode': mode, 'selectable_turns': len(indices), 'train_turns': len(training),
        'validation_turns': len(validation), 'baseline_clone_train_loss': history,
        'head_diagnostics': clone,
        'interpretation': 'choice cloning diagnostic only; not evidence of match strength',
        'data': [file_id(path) for path in files],
    }


def masked_distribution(logits, mask):
    return Categorical(logits=logits.masked_fill(~mask, -1e9))


def train_batch(policy: SpatialPolicy, optimizer, episodes, mode: str,
                rng: np.random.Generator, *, epochs: int, batch_size: int) -> dict:
    """PPO over a hierarchical dragon-turn choice: action then four conditional sonar rays."""
    if mode not in ('joint', 'action', 'sonar'):
        raise ValueError(f'unknown training mode: {mode}')
    data = {key: np.concatenate([arrays[key] for arrays, summary in episodes])
            for key in episodes[0][0]}
    if 'chosen_action_features' not in data:
        rows = np.arange(len(data['action']))
        data['chosen_action_features'] = data['action_features'][rows, data['action']]
    episode_ids = np.concatenate([np.full(len(arrays['round']), i, dtype=np.int32)
                                  for i, (arrays, summary) in enumerate(episodes)])
    actor_valid = data['actor_valid'].astype(bool)
    action_active = actor_valid & (data['action_mask'].sum(axis=-1) > 1)
    sonar_ray_active = actor_valid[:, None] & (data['sonar_mask'].sum(axis=-1) > 1)
    use_action, use_sonar = mode in ('joint', 'action'), mode in ('joint', 'sonar')
    if not use_action:
        action_active[:] = False
    if not use_sonar:
        sonar_ray_active[:] = False
    sonar_active = sonar_ray_active.any(axis=-1)
    valid = action_active | sonar_active
    if not valid.any():
        raise ValueError('No valid selectable action or sonar decisions in rollout')

    weights = torch.as_tensor(team_round_weights(episode_ids, data['round'], valid))
    critic_weights = torch.as_tensor(team_round_weights(
        episode_ids, data['round'], np.ones(len(valid), dtype=bool)))
    x = torch.as_tensor(data['x'])
    action_features = torch.as_tensor(data['action_features'], dtype=torch.float32)
    action_mask = torch.as_tensor(data['action_mask'], dtype=torch.bool)
    action_selected = torch.as_tensor(data['action'], dtype=torch.long)
    action_old_logp = torch.as_tensor(data['action_logp'], dtype=torch.float32)
    sonar_features = torch.as_tensor(data['sonar_features'], dtype=torch.float32)
    sonar_mask = torch.as_tensor(data['sonar_mask'], dtype=torch.bool)
    sonar_selected = torch.as_tensor(data['sonar'], dtype=torch.long)
    sonar_old_logp = torch.as_tensor(data['sonar_logp'], dtype=torch.float32).sum(dim=-1)
    action_context = torch.as_tensor(data['chosen_action_features'], dtype=torch.float32)
    returns = torch.as_tensor(data['returns'], dtype=torch.float32)
    active_action_t = torch.as_tensor(action_active)
    active_sonar_t = torch.as_tensor(sonar_active)
    with torch.no_grad():
        advantage = returns - policy.value(x)
    weight_sum = weights.sum().clamp_min(1e-8)
    average = (weights * advantage).sum() / weight_sum
    variance = (weights * (advantage - average).square()).sum() / weight_sum
    advantage = (advantage - average) / torch.sqrt(variance + 1e-8)
    actor_scale = weights.mean().clamp_min(1e-8)
    critic_scale = critic_weights.mean().clamp_min(1e-8)
    old_logp = (torch.where(active_action_t, action_old_logp, 0.0) +
                torch.where(active_sonar_t, sonar_old_logp, 0.0))
    history = []
    policy.train()
    for _ in range(epochs):
        order = rng.permutation(len(x))
        totals = Counter()
        for begin in range(0, len(x), batch_size):
            idx_np = order[begin:begin + batch_size]
            idx = torch.as_tensor(idx_np, dtype=torch.long)
            context = policy.encode(x[idx])
            new_logp = torch.zeros(len(idx), dtype=torch.float32)
            entropy = torch.zeros(len(idx), dtype=torch.float32)
            if use_action:
                action_logits = policy.action_head(context, action_features[idx])
                action_dist = masked_distribution(action_logits, action_mask[idx])
                action_logp = action_dist.log_prob(action_selected[idx])
                action_entropy = action_dist.entropy()
                new_logp += torch.where(active_action_t[idx], action_logp, 0.0)
                entropy += torch.where(active_action_t[idx], action_entropy, 0.0)
            if use_sonar:
                sonar_logits = policy.sonar_head(context, sonar_features[idx], action_context[idx])
                sonar_dist = masked_distribution(sonar_logits, sonar_mask[idx])
                sonar_logp = sonar_dist.log_prob(sonar_selected[idx]).sum(dim=-1)
                sonar_entropy = sonar_dist.entropy().sum(dim=-1)
                new_logp += torch.where(active_sonar_t[idx], sonar_logp, 0.0)
                entropy += torch.where(active_sonar_t[idx], sonar_entropy, 0.0)
            log_ratio = new_logp - old_logp[idx]
            ratio = torch.exp(log_ratio)
            clipped = torch.clamp(ratio, 1.0 - PPO_CLIP, 1.0 + PPO_CLIP)
            surrogate = torch.minimum(ratio * advantage[idx], clipped * advantage[idx])
            actor_loss = -(weights[idx] * surrogate).mean() / actor_scale
            entropy_loss = (weights[idx] * entropy).mean() / actor_scale
            value_prediction = policy.value_from_context(context)
            value_loss = (critic_weights[idx] * (value_prediction - returns[idx]).square()).mean() / critic_scale
            loss = actor_loss + VALUE_COEF * value_loss - ENTROPY_COEF * entropy_loss
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            nn.utils.clip_grad_norm_(policy.parameters(), GRAD_NORM)
            optimizer.step()
            approx_kl = torch.exp(log_ratio) - 1.0 - log_ratio
            totals['actor_loss'] += float(actor_loss.detach()) * len(idx)
            totals['value_loss'] += float(value_loss.detach()) * len(idx)
            totals['entropy'] += float(entropy_loss.detach()) * len(idx)
            totals['approx_kl'] += float((weights[idx] * approx_kl).mean().detach() / actor_scale) * len(idx)
            totals['clip_fraction'] += float((weights[idx] * (torch.abs(ratio - 1.0) > PPO_CLIP)).mean() /
                                             actor_scale) * len(idx)
        history.append({key: value / len(x) for key, value in totals.items()})

    action_choices = data['action']
    sonar_choices = data['sonar']
    selected_action_features = data['action_features'][np.arange(len(valid)), action_choices]
    selected_sonar_features = data['sonar_features'][
        np.arange(len(valid))[:, None], np.arange(4)[None, :], sonar_choices]
    action_types = np.argmax(selected_action_features[..., :TYPE_CHANNELS['action']], axis=-1)
    sonar_types = np.argmax(selected_sonar_features[..., :TYPE_CHANNELS['sonar']], axis=-1)
    action_rate = (float(np.mean(action_choices[action_active] == 0))
                   if action_active.any() else None)
    active_rays = sonar_ray_active
    sonar_rate = (float(np.mean(sonar_choices[active_rays] == 0))
                  if active_rays.any() else None)
    decision_count = int(action_active.sum() + active_rays.sum())
    baseline_count = int((action_choices[action_active] == 0).sum() +
                         (sonar_choices[active_rays] == 0).sum())
    return {
        'mode': mode, 'rows': len(x), 'selectable_decisions': int(valid.sum()),
        'active_action_decisions': int(action_active.sum()),
        'active_sonar_rays': int(active_rays.sum()),
        'overrides': int((~actor_valid).sum()), 'ppo_epochs': history,
        'baseline_choice_rate': baseline_count / decision_count if decision_count else None,
        'action_baseline_choice_rate': action_rate, 'sonar_baseline_choice_rate': sonar_rate,
        'action_type_counts': dict(Counter(int(v) for v in action_types[action_active].tolist())),
        'sonar_type_counts': dict(Counter(int(v) for v in sonar_types[active_rays].tolist())),
    }


def monitor_fixtures(maps: list[Path], opponents: list[Path], games: int, seed: int) -> list[dict]:
    fixtures = []
    for i in range(games):
        pair = i // 2
        board = maps[pair % len(maps)]
        opponent = opponents[(pair // len(maps)) % len(opponents)]
        fixtures.append({'index': i, 'map': str(board.resolve()), 'opponent': str(opponent.resolve()),
                         'seed': seed + pair, 'seat': 'A' if i % 2 == 0 else 'B'})
    return fixtures


def result_score(summary: dict) -> float:
    result = summary['result']
    if result['winner'] is None:
        return 0.5
    return 1.0 if result['winner'] == summary['seat'] else 0.0


def eval_actor(actor, actor_kind: str, fixture: dict, bridge: Path, *, greedy: bool):
    arrays, summary, replay = episode(
        bridge.resolve(), Path(fixture['opponent']), Path(fixture['map']), fixture['seed'],
        fixture['seat'], gamma=GAMMA, capture=False,
        **_actor_kwargs(actor, actor_kind, greedy=greedy))
    return summary


def eval_baseline(fixture: dict, bridge: Path) -> dict:
    arrays, summary, replay = episode(
        bridge.resolve(), Path(fixture['opponent']), Path(fixture['map']), fixture['seed'],
        fixture['seat'], gamma=GAMMA, capture=False)
    return summary


def cluster_interval(deltas: list[float], fixtures: list[dict], seed: int) -> list[float] | None:
    grouped = defaultdict(list)
    for fixture, delta in zip(fixtures, deltas):
        grouped[fixture['map']].append(float(delta))
    if len(grouped) < 2:
        return None
    means = np.asarray([np.mean(values) for values in grouped.values()], dtype=np.float64)
    rng = np.random.default_rng(seed)
    draws = rng.choice(means, size=(10000, len(means)), replace=True).mean(axis=1)
    return [float(v) for v in np.quantile(draws, [0.05, 0.95])]


def plateau_status(history: list[dict]) -> dict:
    values = [float(item['eval']['paired_score_delta']) for item in history
              if item.get('eval', {}).get('paired_score_delta') is not None]
    if len(values) < 3:
        return {'monitor_trend': 'insufficient_checkpoints', 'slope_per_update': None}
    recent = np.asarray(values[-3:], dtype=np.float64)
    slope = float(np.polyfit(np.arange(len(recent)), recent, 1)[0])
    if slope > 0.025:
        trend = 'up_on_fixed_monitor'
    elif slope < -0.025:
        trend = 'down_on_fixed_monitor'
    else:
        trend = 'flat_on_fixed_monitor_plateau_candidate'
    return {'monitor_trend': trend, 'slope_per_update': slope}


def _rollout_spec(bridge: Path, fixture: dict, *, actor_kind: str | None,
                  greedy: bool, capture: bool, output: Path | None = None) -> dict:
    return {
        'bridge': str(bridge.resolve()), 'opponent': str(Path(fixture['opponent']).resolve()),
        'board': str(Path(fixture['map']).resolve()), 'seed': int(fixture['seed']),
        'seat': fixture['seat'], 'actor_kind': actor_kind, 'greedy': greedy,
        'capture': capture, 'output': None if output is None else str(output),
    }


def evaluate(actor, actor_kind: str, fixtures: list[dict], references: list[dict], bridge: Path,
             output: Path, update: int, *, workers: int, threads: int) -> dict:
    actor.eval()
    games = []
    eval_dir = output / f'update-{update:03d}' / 'eval'
    eval_dir.mkdir(parents=True, exist_ok=True)
    specs = [_rollout_spec(bridge, fixture, actor_kind=actor_kind, greedy=True, capture=False)
             for fixture in fixtures]
    candidates = run_rollouts(specs, actor, workers=workers, threads=threads)
    for fixture, baseline, candidate in zip(fixtures, references, candidates):
        row = {'fixture': fixture, 'candidate': candidate,
               'candidate_score': result_score(candidate), 'baseline_score': result_score(baseline)}
        games.append(row)
        atomic_json(eval_dir / f"game-{fixture['index']:03d}.json", row)
        print(json.dumps({'kind': 'eval_game', 'update': update, 'fixture': fixture['index'],
                          'seat': fixture['seat'], 'map': Path(fixture['map']).name,
                          'opponent': Path(fixture['opponent']).name,
                          'candidate_score': row['candidate_score'],
                          'baseline_score': row['baseline_score']}), flush=True)
    candidate_scores = [g['candidate_score'] for g in games]
    baseline_scores = [g['baseline_score'] for g in games]
    deltas = [a - b for a, b in zip(candidate_scores, baseline_scores)]
    wins = sum(s == 1.0 for s in candidate_scores)
    draws = sum(s == 0.5 for s in candidate_scores)
    losses = len(games) - wins - draws
    paired_interval = cluster_interval(deltas, fixtures, 91821 + update)
    report = {
        'games': len(games), 'wins': wins, 'draws': draws, 'losses': losses,
        'candidate_score': float(np.mean(candidate_scores)),
        'baseline_score': float(np.mean(baseline_scores)),
        'paired_score_delta': float(np.mean(deltas)),
        'map_cluster_90_interval': paired_interval,
        'interpretation': 'fixed-panel monitoring only; not independent confirmation',
    }
    atomic_json(eval_dir / 'summary.json', report)
    return report


def build_manifest(args, source_files: list[Path]) -> dict:
    input_groups = {}
    for key in ('warmstart_data', 'maps', 'eval_maps', 'opponents', 'eval_opponents'):
        paths = getattr(args, key)
        input_groups[key] = [file_id(p) for p in paths]
    return {
        'format': 'finals-spatial-ppo-v2-joint', 'actor': args.actor, 'seed': args.seed,
        'games_per_update': args.games_per_update, 'ppo_epochs': args.epochs,
        'batch_size': args.batch_size, 'eval_games': args.eval_games,
        'eval_every': args.eval_every, 'warmstart_epochs': args.warmstart_epochs,
        'threads': args.threads, 'workers': args.workers,
        'gamma': GAMMA, 'learning_rate': LEARNING_RATE, 'clip': PPO_CLIP,
        'reward_shaping': SHAPING_NAME, 'shaping_alpha': SHAPING_ALPHA,
        'entropy_coef': ENTROPY_COEF, 'value_coef': VALUE_COEF, 'grad_norm': GRAD_NORM,
        'monitor_seed': args.monitor_seed, 'inputs': input_groups,
        'bridge': file_id(args.bridge),
        'scripts': {p.name: file_id(p) for p in source_files},
    }


def write_metrics(output: Path, row: dict) -> None:
    path = output / 'progress.jsonl'
    rows_by_update = {}
    if path.exists():
        rows_by_update = {int(item['update']): item for item in
                          (json.loads(line) for line in path.read_text().splitlines() if line.strip())}
    rows_by_update[int(row['update'])] = row
    rows = [rows_by_update[key] for key in sorted(rows_by_update)]
    path.write_text(''.join(json.dumps(item, sort_keys=True) + '\n' for item in rows))
    csv_path = output / 'progress.csv'
    columns = ['update', 'train_wins', 'train_draws', 'train_losses', 'train_games',
               'train_reward_sum', 'train_mean_reward', 'train_score',
               'mean_policy_return', 'mean_terminal_return', 'mean_shaping_return',
               'cumulative_train_reward', 'cumulative_train_score', 'selectable_decisions',
               'active_action_decisions', 'active_sonar_rays', 'baseline_choice_rate',
               'action_baseline_choice_rate', 'sonar_baseline_choice_rate',
               'actor_loss', 'value_loss', 'entropy', 'approx_kl',
               'clip_fraction', 'eval_wins', 'eval_draws', 'eval_losses', 'eval_score',
               'baseline_score', 'paired_score_delta', 'ci90_low', 'ci90_high', 'monitor_trend']
    with csv_path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        cumulative_reward = 0.0
        cumulative_games = 0
        for item in rows:
            report = item.get('eval', {})
            metrics = item.get('ppo', {}).get('ppo_epochs', [])
            last = metrics[-1] if metrics else {}
            interval = report.get('map_cluster_90_interval') or [None, None]
            training = item.get('training', {})
            game_count = int(training.get('sampled_games', 0))
            reward_sum = float(training.get('terminal_reward_sum', 0.0))
            cumulative_reward += reward_sum
            cumulative_games += game_count
            writer.writerow({
                'update': item.get('update'), 'train_wins': training.get('wins'),
                'train_draws': training.get('draws'), 'train_losses': training.get('losses'),
                'train_games': game_count, 'train_reward_sum': reward_sum,
                'train_mean_reward': (reward_sum / game_count if game_count else None),
                'train_score': ((training.get('wins', 0) + 0.5 * training.get('draws', 0)) / game_count
                                if game_count else None),
                'mean_policy_return': training.get('mean_policy_return'),
                'mean_terminal_return': training.get('mean_terminal_return'),
                'mean_shaping_return': training.get('mean_shaping_return'),
                'cumulative_train_reward': cumulative_reward,
                'cumulative_train_score': ((cumulative_reward / cumulative_games + 1.0) / 2.0
                                           if cumulative_games else None),
                'selectable_decisions': item.get('ppo', {}).get('selectable_decisions'),
                'active_action_decisions': item.get('ppo', {}).get('active_action_decisions'),
                'active_sonar_rays': item.get('ppo', {}).get('active_sonar_rays'),
                'baseline_choice_rate': item.get('ppo', {}).get('baseline_choice_rate'),
                'action_baseline_choice_rate': item.get('ppo', {}).get('action_baseline_choice_rate'),
                'sonar_baseline_choice_rate': item.get('ppo', {}).get('sonar_baseline_choice_rate'),
                'actor_loss': last.get('actor_loss'), 'value_loss': last.get('value_loss'),
                'entropy': last.get('entropy'), 'approx_kl': last.get('approx_kl'),
                'clip_fraction': last.get('clip_fraction'), 'eval_wins': report.get('wins'),
                'eval_draws': report.get('draws'), 'eval_losses': report.get('losses'),
                'eval_score': report.get('candidate_score'), 'baseline_score': report.get('baseline_score'),
                'paired_score_delta': report.get('paired_score_delta'), 'ci90_low': interval[0],
                'ci90_high': interval[1], 'monitor_trend': item.get('monitor_trend'),
            })


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--actor', choices=['joint', 'action', 'sonar'], default='joint',
                    help='joint shared-encoder training by default; action/sonar are ablations')
    ap.add_argument('--bridge', type=Path, required=True)
    ap.add_argument('--warmstart-data', type=Path, nargs='+', required=True)
    ap.add_argument('--opponents', type=Path, nargs='+', required=True)
    ap.add_argument('--maps', type=Path, nargs='+', required=True, help='training map files')
    ap.add_argument('--eval-opponents', type=Path, nargs='+', required=True)
    ap.add_argument('--eval-maps', type=Path, nargs='+', required=True, help='held-out monitoring map files')
    ap.add_argument('--updates', type=int, default=10,
                    help='total target updates, 1..1000; raise this when resuming')
    ap.add_argument('--until-stopped', action='store_true',
                    help='train continuously until interrupted with Ctrl+C')
    ap.add_argument('--games-per-update', type=int, default=4)
    ap.add_argument('--epochs', type=int, default=3)
    ap.add_argument('--batch-size', type=int, default=256)
    ap.add_argument('--warmstart-epochs', type=int, default=5)
    ap.add_argument('--eval-games', type=int, default=8)
    ap.add_argument('--eval-every', type=int, default=1)
    ap.add_argument('--seed', type=int, default=61600)
    ap.add_argument('--monitor-seed', type=int, default=926100)
    ap.add_argument('--threads', type=int, default=1)
    ap.add_argument('--workers', type=int, default=1,
                    help='isolated concurrent game workers; training uses at most games/update')
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--resume', action='store_true')
    args = ap.parse_args()
    bounded_updates_ok = args.until_stopped or 1 <= args.updates <= 1000
    if not (bounded_updates_ok and 1 <= args.games_per_update <= 16 and
            1 <= args.epochs <= 10 and 1 <= args.warmstart_epochs <= 50 and
            1 <= args.eval_games <= 64 and 1 <= args.eval_every <= 100 and
            1 <= args.threads <= 32 and 1 <= args.workers <= 16):
        ap.error('run limits: updates 1..1000 unless --until-stopped; games/update<=16, '
                 'epochs<=10, eval games<=64')
    args.output = args.output.resolve()
    if not (args.output.is_relative_to(ROOT / 'build') or args.output.is_relative_to(Path('/tmp'))):
        ap.error('generated checkpoints and run data must stay under build/ or /tmp')
    for key in ('bridge', 'opponents', 'eval_opponents', 'maps', 'eval_maps', 'warmstart_data'):
        values = getattr(args, key)
        if values:
            setattr(args, key, [p.resolve() for p in values] if isinstance(values, list) else values.resolve())
    for path in [args.bridge, *args.opponents, *args.eval_opponents, *args.maps, *args.eval_maps,
                 *args.warmstart_data]:
        if not path.is_file():
            ap.error(f'input file does not exist: {path}')
    if any(p.suffix != '.map' for p in args.maps + args.eval_maps):
        ap.error('map inputs must be .map files')
    overlap = {sha256(p) for p in args.maps} & {sha256(p) for p in args.eval_maps}
    if overlap:
        ap.error('training and evaluation maps must be content-distinct')

    torch.set_num_threads(args.threads)
    torch.manual_seed(args.seed)
    rng = np.random.default_rng(args.seed)
    args.output.mkdir(parents=True, exist_ok=True)
    sources = [Path(__file__).resolve(), Path(__file__).with_name('spatial_model.py').resolve(),
               Path(__file__).with_name('collect.py').resolve(),
               (ROOT / 'tools/learn/encode.py').resolve(),
               (ROOT / 'tools/finals/model.py').resolve()]
    manifest = build_manifest(args, sources)
    manifest_path = args.output / 'manifest.json'
    latest = args.output / 'latest.pt'
    if args.resume:
        if not manifest_path.is_file() or not latest.is_file():
            ap.error('--resume requires an existing manifest and latest.pt')
        old_manifest = json.loads(manifest_path.read_text())
        # A run can be extended by raising --updates; all other inputs/configuration stay pinned.
        if old_manifest != manifest:
            ap.error('Resume inputs or training settings differ; use a new output directory')
    elif manifest_path.exists() or any(args.output.iterdir()):
        ap.error('output directory already contains files; use --resume or a new directory')
    else:
        atomic_json(manifest_path, manifest)
        archive = args.output / 'source-archive'
        archive.mkdir()
        for source in sources:
            shutil.copyfile(source, archive / source.name)

    actor = SpatialPolicy()
    optimizer = torch.optim.Adam(actor.parameters(), lr=LEARNING_RATE)
    start = 0
    if args.resume:
        state = torch.load(latest, map_location='cpu', weights_only=True)
        if state.get('format') != 'finals-spatial-ppo-v2-joint' or state.get('actor') != args.actor:
            ap.error('checkpoint format or training mode mismatch')
        actor.load_state_dict(state['actor_state'])
        optimizer.load_state_dict(state['optimizer_state'])
        start = int(state['iteration'])
        rng.bit_generator.state = state['numpy_rng']
        torch.set_rng_state(state['torch_rng'])
        history = [item for item in
                   (json.loads(line) for line in (args.output / 'progress.jsonl').read_text().splitlines()
                    if line.strip()) if int(item['update']) <= start] \
            if (args.output / 'progress.jsonl').exists() else []
    else:
        warm_started = time.monotonic()
        clone_report = warmstart(actor, args.actor, args.warmstart_data,
                                 epochs=args.warmstart_epochs, batch_size=args.batch_size, seed=args.seed)
        clone_report['elapsed_seconds'] = time.monotonic() - warm_started
        atomic_json(args.output / 'warmstart-report.json', clone_report)
        state = {'format': 'finals-spatial-ppo-v2-joint', 'actor': args.actor,
                 'actor_state': actor.state_dict(), 'optimizer_state': optimizer.state_dict(),
                 'iteration': 0, 'numpy_rng': rng.bit_generator.state, 'torch_rng': torch.get_rng_state()}
        torch.save(state, args.output / 'initial.pt')
        temp = latest.with_suffix('.tmp'); torch.save(state, temp); temp.replace(latest)
        history = []
        print(json.dumps({'kind': 'warmstart', **clone_report}), flush=True)

    fixtures = monitor_fixtures(args.eval_maps, args.eval_opponents, args.eval_games, args.monitor_seed)
    fixture_path = args.output / 'monitor-fixtures.json'
    if fixture_path.exists():
        if json.loads(fixture_path.read_text()) != fixtures:
            ap.error('monitor fixture list changed; create a new output directory')
    else:
        atomic_json(fixture_path, fixtures)
    reference_dir = args.output / 'reference'
    reference_dir.mkdir(exist_ok=True)
    references = []
    missing_references = []
    missing_reference_specs = []
    missing_reference_slots = []
    for fixture in fixtures:
        path = reference_dir / f"game-{fixture['index']:03d}.json"
        if path.exists():
            references.append(json.loads(path.read_text()))
        else:
            missing_reference_slots.append(len(references))
            references.append(None)
            missing_references.append(path)
            missing_reference_specs.append(
                _rollout_spec(args.bridge, fixture, actor_kind=None, greedy=True, capture=False))
    if missing_reference_specs:
        new_references = run_rollouts(
            missing_reference_specs, workers=args.workers, threads=args.threads)
        for slot, path, fixture, summary in zip(
                missing_reference_slots, missing_references, [fixtures[i] for i in missing_reference_slots],
                new_references):
            atomic_json(path, summary)
            references[slot] = summary
            print(json.dumps({'kind': 'reference_game', 'fixture': fixture['index'],
                              'score': result_score(summary), 'map': Path(fixture['map']).name,
                              'opponent': Path(fixture['opponent']).name}), flush=True)
    reference_summary = {
        'games': len(references), 'wins': sum(result_score(s) == 1.0 for s in references),
        'draws': sum(result_score(s) == 0.5 for s in references),
        'losses': sum(result_score(s) == 0.0 for s in references),
        'score': float(np.mean([result_score(s) for s in references])),
    }
    atomic_json(reference_dir / 'summary.json', reference_summary)

    for update in update_sequence(start, args.updates, args.until_stopped):
        block = args.output / f'update-{update + 1:03d}'
        block.mkdir(exist_ok=True)
        episodes = []
        actor.eval()
        collection_started = time.monotonic()
        training_summaries = []
        game_records = []
        pending_specs = []
        for game in range(args.games_per_update):
            fixture_ix = update * args.games_per_update + game
            board = args.maps[(fixture_ix // 2) % len(args.maps)]
            opponent = args.opponents[(fixture_ix // (2 * len(args.maps))) % len(args.opponents)]
            seat = 'A' if fixture_ix % 2 == 0 else 'B'
            seed = args.seed + fixture_ix // 2
            path = block / f'game-{game:02d}'
            path.mkdir(exist_ok=True)
            if (path / 'summary.json').exists() and (path / 'episode.npz').exists():
                arrays = dict(np.load(path / 'episode.npz'))
                summary = json.loads((path / 'summary.json').read_text())
                game_records.append((path, arrays, summary))
            else:
                game_records.append((path, None, None))
                pending_specs.append(_rollout_spec(
                    args.bridge,
                    {'opponent': opponent, 'map': board, 'seed': seed, 'seat': seat},
                    actor_kind=args.actor, greedy=False, capture=True, output=path))
        if pending_specs:
            new_summaries = run_rollouts(
                pending_specs, actor, workers=args.workers, threads=args.threads)
            pending_index = 0
            for index, (path, arrays, summary) in enumerate(game_records):
                if summary is None:
                    summary = new_summaries[pending_index]
                    arrays = dict(np.load(path / 'episode.npz'))
                    game_records[index] = (path, arrays, summary)
                    pending_index += 1
        for game, (path, arrays, summary) in enumerate(game_records):
            episodes.append((arrays, summary))
            training_summaries.append(summary)
            print(json.dumps({'kind': 'train_game', 'update': update + 1, 'game': game + 1,
                              'seat': summary['seat'], 'reward': summary['terminal_reward'],
                              'rounds': summary['terminal_round'] + 1, 'decisions': summary['decisions'],
                              'faults': len(summary['faults']),
                              'elapsed_seconds': round(summary['elapsed_seconds'], 2)}), flush=True)
        collection_seconds = time.monotonic() - collection_started
        optimization_started = time.monotonic()
        ppo_report = train_batch(actor, optimizer, episodes, args.actor, rng,
                                 epochs=args.epochs, batch_size=args.batch_size)
        optimization_seconds = time.monotonic() - optimization_started
        rewards = [float(s['terminal_reward']) for s in training_summaries]
        training = {'wins': rewards.count(1.0), 'draws': rewards.count(0.0),
                    'losses': rewards.count(-1.0), 'sampled_games': len(rewards)}
        # Collection's terminal_reward is zero for draws; result metadata disambiguates them.
        training['draws'] = sum(s['result']['winner'] is None for s in training_summaries)
        training['wins'] = sum(s['result']['winner'] == s['seat'] for s in training_summaries)
        training['losses'] = len(rewards) - training['draws'] - training['wins']
        training['terminal_reward_sum'] = float(sum(rewards))
        training['mean_terminal_reward'] = float(np.mean(rewards))
        training['score'] = float((training['wins'] + 0.5 * training['draws']) / len(rewards))
        training['mean_policy_return'] = float(np.mean([
            s['shaping']['mean_policy_return'] for s in training_summaries]))
        training['mean_terminal_return'] = float(np.mean([
            s['shaping']['mean_terminal_return'] for s in training_summaries]))
        training['mean_shaping_return'] = float(np.mean([
            s['shaping']['mean_shaping_return'] for s in training_summaries]))
        prior_reward = sum(float(item.get('training', {}).get('terminal_reward_sum', 0.0))
                           for item in history)
        prior_games = sum(int(item.get('training', {}).get('sampled_games', 0))
                          for item in history)
        cumulative_reward = prior_reward + training['terminal_reward_sum']
        cumulative_games = prior_games + training['sampled_games']
        cumulative_score = ((cumulative_reward / cumulative_games + 1.0) / 2.0
                            if cumulative_games else None)
        update_label = '∞' if args.until_stopped else str(args.updates)
        print(f"REWARD update {update + 1}/{update_label}: "
              f"terminal reward {training['terminal_reward_sum']:+.0f} "
              f"(mean {training['mean_terminal_reward']:+.3f}, "
              f"score {training['score']:.3f}); cumulative "
              f"{cumulative_reward:+.0f} over {cumulative_games} games "
              f"(score {cumulative_score:.3f}); shaped policy return "
              f"{training['mean_policy_return']:+.4f} "
              f"(terminal component {training['mean_terminal_return']:+.4f}, "
              f"potential contribution {training['mean_shaping_return']:+.4f})", flush=True)
        report = {'update': update + 1, 'training': training, 'ppo': ppo_report,
                  'collection_seconds': collection_seconds, 'optimization_seconds': optimization_seconds}
        state = {'format': 'finals-spatial-ppo-v2-joint', 'actor': args.actor,
                 'actor_state': actor.state_dict(), 'optimizer_state': optimizer.state_dict(),
                 'iteration': update + 1, 'numpy_rng': rng.bit_generator.state, 'torch_rng': torch.get_rng_state()}
        torch.save(state, block / 'checkpoint.pt')
        if ((update + 1) % args.eval_every == 0 or
                (not args.until_stopped and update + 1 == args.updates)):
            eval_report = evaluate(actor, args.actor, fixtures, references, args.bridge, args.output, update + 1,
                                   workers=args.workers, threads=args.threads)
            report['eval'] = eval_report
            monitor_history = history + [report]
            report.update(plateau_status(monitor_history))
        else:
            report.update({'monitor_trend': 'not_evaluated_this_update', 'slope_per_update': None})
        atomic_json(block / 'report.json', report)
        history.append(report)
        write_metrics(args.output, report)
        temp = latest.with_suffix('.tmp'); torch.save(state, temp); temp.replace(latest)
        status = {'kind': 'update', 'update': update + 1, 'training': training,
                  'cumulative_train_reward': cumulative_reward,
                  'cumulative_train_score': cumulative_score,
                  'selectable_decisions': ppo_report['selectable_decisions'],
                  'active_action_decisions': ppo_report['active_action_decisions'],
                  'active_sonar_rays': ppo_report['active_sonar_rays'],
                  'baseline_choice_rate': round(ppo_report['baseline_choice_rate'], 4),
                  'action_baseline_choice_rate': ppo_report['action_baseline_choice_rate'],
                  'sonar_baseline_choice_rate': ppo_report['sonar_baseline_choice_rate'],
                  'last_ppo_epoch': ppo_report['ppo_epochs'][-1],
                  'eval': report.get('eval'), 'monitor_trend': report['monitor_trend'],
                  'collection_seconds': round(collection_seconds, 2),
                  'optimization_seconds': round(optimization_seconds, 2)}
        print(json.dumps(status), flush=True)
    print(json.dumps({'kind': 'complete', 'checkpoint': str(latest),
                      'progress': str(args.output / 'progress.csv'),
                      'updates': args.updates, 'last_update': start < args.updates}), flush=True)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nTraining interrupted. The latest completed checkpoint is saved; '
              'restart with the same command plus --resume.', flush=True)
