"""Bounded resumable PPO over C++ semantic candidates, one actor stage at a time.

Full episodes, terminal team reward only, actual-round discounted Monte Carlo returns.
No GAE across flattened dragons; actor/critic losses average team rounds and episodes.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import time
import numpy as np
import torch
from torch import nn
from torch.distributions import Categorical
from collect import episode
from model import Scorer, context_scales, export_header


def team_round_weights(episode_ids, rounds, valid):
    """Equal episode weight, equal active-round weight, then equal dragon decision weight."""
    pairs = [(int(e), int(r)) for e, r, ok in zip(episode_ids, rounds, valid) if ok]
    counts = Counter(pairs)
    round_counts = Counter(e for e, r in counts)
    return np.asarray([1.0 / (counts[(int(e), int(r))] * round_counts[int(e)]) if ok else 0
                       for e, r, ok in zip(episode_ids, rounds, valid)], dtype=np.float32)


def distribution(actor, x, features, mask, stage):
    logits = actor(x, features).masked_fill(~mask, -1e9)
    return Categorical(logits=logits)


def log_prob_entropy(dist, selected, stage):
    logp, entropy = dist.log_prob(selected), dist.entropy()
    if stage == 'sonar':
        # One joint four-ray decision. Do not multiply rewards/losses by send count.
        logp, entropy = logp.sum(dim=-1), entropy.sum(dim=-1)
    return logp, entropy


def train_batch(actor, critic, optimizer, episodes, stage, rng, epochs=3, batch_size=256):
    data = {key: np.concatenate([a[key] for a, summary in episodes]) for key in episodes[0][0]}
    episode_ids = np.concatenate([np.full(len(a['round']), i) for i, (a, s) in enumerate(episodes)])
    if stage == 'action':
        eligible = data['action_mask'].sum(axis=-1) > 1
    else:
        eligible = np.any(data['sonar_mask'].sum(axis=-1) > 1, axis=-1)
    valid = data['actor_valid'] & eligible
    if not valid.any():
        raise ValueError('No valid selectable actor decisions in rollout')
    weights = team_round_weights(episode_ids, data['round'], valid)
    critic_weights = team_round_weights(episode_ids, data['round'], np.ones(len(valid), dtype=bool))
    x = torch.as_tensor(data['x'])
    features = torch.as_tensor(data[stage + '_features'])
    mask = torch.as_tensor(data[stage + '_mask'])
    selected = torch.as_tensor(data['action' if stage == 'action' else 'sonar'])
    old_logp = torch.as_tensor(data[stage + '_logp'])
    if stage == 'sonar':
        old_logp = old_logp.sum(dim=-1)
    returns = torch.as_tensor(data['returns'])
    weights = torch.as_tensor(weights)
    critic_weights = torch.as_tensor(critic_weights)
    scales = torch.as_tensor(context_scales())
    normalized = torch.clamp(x.float() / scales, -8, 8)
    predictions = []
    with torch.no_grad():
        for begin in range(0, len(x), batch_size):
            predictions.append(critic(normalized[begin:begin + batch_size]).squeeze(-1))
    advantage = returns - torch.cat(predictions)
    average = (weights * advantage).sum() / weights.sum()
    variance = (weights * (advantage - average).square()).sum() / weights.sum()
    advantage = (advantage - average) / torch.sqrt(variance + 1e-8)
    actor_scale = weights.mean()
    critic_scale = critic_weights.mean()
    history = []
    for _ in range(epochs):
        order = rng.permutation(len(x))
        totals = Counter()
        for begin in range(0, len(x), batch_size):
            idx = order[begin:begin + batch_size]
            dist = distribution(actor, x[idx], features[idx], mask[idx], stage)
            logp, entropy = log_prob_entropy(dist, selected[idx], stage)
            ratio = torch.exp(logp - old_logp[idx])
            surrogate = torch.minimum(ratio * advantage[idx], torch.clamp(ratio, .8, 1.2) * advantage[idx])
            actor_loss = -(weights[idx] * surrogate).mean() / actor_scale
            entropy_loss = (weights[idx] * entropy).mean() / actor_scale
            value_loss = (critic_weights[idx] * (critic(normalized[idx]).squeeze(-1) - returns[idx]).square()).mean() / critic_scale
            loss = actor_loss + .5 * value_loss - .01 * entropy_loss
            optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(list(actor.parameters()) + list(critic.parameters()), .5)
            optimizer.step()
            totals['actor_loss'] += float(actor_loss.detach()) * len(idx)
            totals['value_loss'] += float(value_loss.detach()) * len(idx)
            totals['entropy'] += float(entropy_loss.detach()) * len(idx)
        history.append({key: value / len(x) for key, value in totals.items()})
    return dict(rows=len(x), selectable=int(valid.sum()), overrides=int((~data['actor_valid']).sum()), losses=history)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--actor', choices=['action', 'sonar'], required=True)
    ap.add_argument('--initial', type=Path, required=True)
    ap.add_argument('--frozen-action', type=Path, help='Sonar-stage retained action actor; omit for fixed incumbent')
    ap.add_argument('--bridge', type=Path, required=True)
    ap.add_argument('--opponents', type=Path, nargs='+', required=True)
    ap.add_argument('--maps', type=Path, nargs='+', required=True)
    ap.add_argument('--updates', type=int, default=2)
    ap.add_argument('--games-per-update', type=int, default=4)
    ap.add_argument('--epochs', type=int, default=3)
    ap.add_argument('--seed', type=int, default=61100)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--resume', action='store_true')
    args = ap.parse_args()
    if args.actor == 'action' and args.frozen_action:
        ap.error('Action stage freezes incumbent sonar; --frozen-action belongs to sonar stage')
    if not 1 <= args.games_per_update <= 16 or not 1 <= args.updates <= 100 or not 1 <= args.epochs <= 10:
        ap.error('Bounded run requires 1..16 games/update, 1..100 updates, 1..10 epochs')
    torch.set_num_threads(1)
    torch.manual_seed(args.seed)
    rng = np.random.default_rng(args.seed)
    args.output.mkdir(parents=True, exist_ok=True)
    def file_id(p):
        return dict(path=str(p.resolve()), sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    manifest = dict(stage=args.actor, seed=args.seed, games_per_update=args.games_per_update,
                    epochs=args.epochs, gamma=.997, shaping='none', terminal_reward=[-1, 0, 1],
                    credit='Complete-episode actual-round Monte Carlo; team-round/episode loss weights',
                    learning_rate=.0003, clip=.2, entropy=.01, value_weight=.5, grad_norm=.5,
                    bridge=file_id(args.bridge), opponents=[file_id(p) for p in args.opponents],
                    maps=[file_id(p) for p in args.maps], initial=file_id(args.initial),
                    frozen_action=file_id(args.frozen_action) if args.frozen_action else 'incumbent',
                    script=file_id(Path(__file__)), model_script=file_id(Path(__file__).with_name('model.py')),
                    collector_script=file_id(Path(__file__).with_name('collect.py')))
    mp = args.output / 'manifest.json'
    if mp.exists():
        if not args.resume or json.loads(mp.read_text()) != manifest:
            ap.error('Resume requires unchanged inputs/configuration; use a new output for changes')
    else:
        mp.write_text(json.dumps(manifest, indent=2) + '\n')
        archive = args.output / 'source-archive'
        archive.mkdir(exist_ok=True)
        for key in ('script', 'model_script', 'collector_script'):
            source = Path(manifest[key]['path'])
            (archive / source.name).write_bytes(source.read_bytes())
    actor = Scorer()
    critic = nn.Sequential(nn.Linear(1193, 32), nn.Tanh(), nn.Linear(32, 1))
    optimizer = torch.optim.Adam(list(actor.parameters()) + list(critic.parameters()), lr=.0003)
    start = 0
    current = args.output / 'latest.pt'
    if args.resume and current.exists():
        state = torch.load(current, map_location='cpu', weights_only=True)
        actor.load_state_dict(state['state']); critic.load_state_dict(state['critic'])
        optimizer.load_state_dict(state['optimizer']); start = state['iteration']
        rng.bit_generator.state = state['numpy_rng']; torch.set_rng_state(state['torch_rng'])
    else:
        initial = torch.load(args.initial, map_location='cpu', weights_only=True)
        if initial['actor'] != args.actor:
            ap.error('Initial checkpoint belongs to the other actor')
        actor.load_state_dict(initial['state'])
    frozen = None
    if args.frozen_action:
        frozen = Scorer(); state = torch.load(args.frozen_action, map_location='cpu', weights_only=True)
        if state['actor'] != 'action':
            ap.error('Frozen action checkpoint is not an action actor')
        frozen.load_state_dict(state['state']); frozen.eval()
        for p in frozen.parameters():
            p.requires_grad_(False)
    for update in range(start, args.updates):
        block = args.output / f'update-{update + 1:03d}'
        block.mkdir(parents=True, exist_ok=True)
        episodes = []
        actor.eval()
        began = time.monotonic()
        for game in range(args.games_per_update):
            fixture = update * args.games_per_update + game
            board = args.maps[(fixture // 2) % len(args.maps)]
            opponent = args.opponents[(fixture // (2 * len(args.maps))) % len(args.opponents)]
            seat = 'A' if fixture % 2 == 0 else 'B'
            seed = args.seed + fixture // 2
            path = block / f'game-{game:02d}'
            path.mkdir(exist_ok=True)
            # Snapshot fixtures within an update so interrupted collection can resume safely.
            if (path / 'summary.json').exists() and (path / 'episode.npz').exists():
                arrays = dict(np.load(path / 'episode.npz'))
                summary = json.loads((path / 'summary.json').read_text())
            else:
                arrays, summary, replay = episode(args.bridge.resolve(), opponent.resolve(), board.resolve(), seed, seat,
                    action_actor=actor.sample if args.actor == 'action' else frozen.greedy if frozen else None,
                    sonar_actor=actor.sample if args.actor == 'sonar' else None)
                np.savez_compressed(path / 'episode.npz', **arrays)
                (path / 'game.replay').write_bytes(replay)
                (path / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
            episodes.append((arrays, summary))
            print('update', update + 1, 'game', game + 1, seat, summary['result']['winner'],
                  summary['decisions'], 'decisions', flush=True)
        collection_seconds = time.monotonic() - began
        began = time.monotonic()
        report = train_batch(actor, critic, optimizer, episodes, args.actor, rng, args.epochs)
        report.update(update=update + 1, collection_seconds=collection_seconds,
                      optimization_seconds=time.monotonic() - began,
                      results=[s['terminal_reward'] for a, s in episodes])
        state = dict(actor=args.actor, state=actor.state_dict(), critic=critic.state_dict(),
                     optimizer=optimizer.state_dict(), iteration=update + 1,
                     numpy_rng=rng.bit_generator.state, torch_rng=torch.get_rng_state())
        torch.save(state, block / 'checkpoint.pt')
        export_header(actor, block / f'{args.actor}_model.hpp', args.actor)
        (block / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        temporary = current.with_suffix('.tmp'); torch.save(state, temporary); temporary.replace(current)
        print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
