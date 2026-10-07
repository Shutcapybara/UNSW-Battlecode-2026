"""On-policy PPO fine-tuning for the deployable growth_rl policy wrapper.

Rollouts use the same v4 view features, process memory, action vocabulary,
split mask, and command decoder as bot_main.py. One team's shared actor is
trained from match outcome against a small frozen-policy or native-bot league;
a separate frozen initial actor supplies the KL anchor. This is local training
code only.
"""
from __future__ import annotations

import argparse
import copy
import gc
import json
import os
import random
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.distributions import Categorical

from . import data as D
from .evaluate import package
from .policy import ACTIONS, Policy, action_mask, numeric, split_size
from tools.learn.block import parse_spawn
from unswbc.engine import EngineModule

FV = D.FV
MAX_GAMES_PER_PROCESS = 500
DEFAULT_HIDDEN = 64


def network(inputs: int, outputs: int, hidden: int) -> nn.Sequential:
    return nn.Sequential(nn.Linear(inputs, hidden), nn.ReLU(),
                         nn.Linear(hidden, hidden), nn.ReLU(), nn.Linear(hidden, outputs))


class Rollout:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.x, self.mask, self.action = [], [], []
        self.logp, self.value, self.reward = [], [], []
        self.games = []

    def add(self, x, mask, action, logp, value):
        if len(self.x) >= self.capacity:
            raise RuntimeError(f'rollout exceeded {self.capacity:,} decisions; reduce games per update')
        index = len(self.x)
        self.x.append(np.asarray(x, dtype=np.float32))
        self.mask.append(np.asarray(mask, dtype=bool))
        self.action.append(int(action))
        self.logp.append(float(logp))
        self.value.append(float(value))
        return index

    def finish(self, start, reward, meta, local_rewards=None):
        count = len(self.x) - start
        local_rewards = local_rewards or {}
        self.reward.extend(float(reward) + float(local_rewards.get(index, 0.0))
                           for index in range(start, len(self.x)))
        self.games.append({**meta, 'decisions': count, 'reward': float(reward)})

    def arrays(self):
        if not self.x:
            raise RuntimeError('the learner team produced no rollout decisions')
        return (np.stack(self.x), np.stack(self.mask), np.asarray(self.action, np.int64),
                np.asarray(self.logp, np.float32), np.asarray(self.value, np.float32),
                np.asarray(self.reward, np.float32))


def normalized_row(row, features, mean, scale):
    values = np.asarray([numeric(row.get(name, 0.0)) for name in features], dtype=np.float64)
    return np.clip((values - mean) / scale, -10.0, 10.0).astype(np.float32)


def from_policy(path: str | None, *, allow_random: bool, hidden: int, seed: int):
    torch.manual_seed(seed)
    if path:
        payload = json.loads(Path(path).read_text(encoding='utf-8'))
        if payload.get('kind') not in ('growth_awr', 'growth_ppo') or 'layers' not in payload:
            raise ValueError('--init-policy must be a neural growth_awr/growth_ppo policy.json')
        if payload.get('actions') != list(ACTIONS):
            raise ValueError('initial policy action vocabulary differs from growth_rl')
        features = list(payload['features'])
        mean = np.asarray(payload['mean'], np.float32)
        scale = np.asarray(payload['scale'], np.float32)
        if mean.shape != (len(features),) or scale.shape != mean.shape or (scale <= 0).any():
            raise ValueError('initial policy has an invalid feature normalizer')
        dims = [len(payload['layers'][0]['weight'][0]), len(payload['layers'][0]['bias'])]
        if len(payload['layers']) != 3 or dims[1] != hidden:
            raise ValueError(f'initial policy must have three linear layers and hidden width {hidden}')
        actor = network(len(features), len(ACTIONS), hidden)
        state = actor.state_dict()
        for index, layer in zip((0, 2, 4), payload['layers']):
            state[f'{index}.weight'] = torch.as_tensor(layer['weight'], dtype=torch.float32)
            state[f'{index}.bias'] = torch.as_tensor(layer['bias'], dtype=torch.float32)
        actor.load_state_dict(state)
        return actor, features, mean, scale, payload
    if not allow_random:
        raise ValueError('pass --init-policy for clone warm-start, or --allow-random-init for a plumbing smoke')
    return None, None, None, None, {'kind': 'random_init_smoke'}


def discover_features(row):
    return sorted(name for name, value in row.items()
                  if isinstance(value, (int, float, np.number)) and name not in D.EXCLUDED and
                  name not in ('dragon', 'action') and not name.startswith('y_'))


def freeze(model):
    result = copy.deepcopy(model).eval()
    for parameter in result.parameters():
        parameter.requires_grad_(False)
    return result


def _masked(model, x, mask):
    logits = model(x).masked_fill(~mask, -1e9)
    return logits


def update(actor, anchor, critic, optimizer, batch, *, epochs, minibatch, clip,
           entropy_coef, value_coef, kl_coef, max_kl, device):
    x, mask, actions, old_logp, old_value, rewards = batch
    xt = torch.as_tensor(x, dtype=torch.float32, device=device)
    mt = torch.as_tensor(mask, dtype=torch.bool, device=device)
    at = torch.as_tensor(actions, dtype=torch.long, device=device)
    old_logp_t = torch.as_tensor(old_logp, dtype=torch.float32, device=device)
    reward_t = torch.as_tensor(rewards, dtype=torch.float32, device=device)
    value_t = torch.as_tensor(old_value, dtype=torch.float32, device=device)
    advantage = reward_t - value_t
    if advantage.numel() > 1 and float(advantage.std(unbiased=False)) > 1e-8:
        advantage = (advantage - advantage.mean()) / (advantage.std(unbiased=False) + 1e-8)

    n = len(x)
    totals = dict(policy=0.0, value=0.0, entropy=0.0, kl=0.0, batches=0)
    max_seen_kl = 0.0
    stopped = False
    for _ in range(epochs):
        order = torch.randperm(n, device=device)
        for start in range(0, n, minibatch):
            ids = order[start:start + minibatch]
            logits = _masked(actor, xt[ids], mt[ids])
            distribution = Categorical(logits=logits)
            new_logp = distribution.log_prob(at[ids])
            ratio = torch.exp(new_logp - old_logp_t[ids])
            policy_loss = -torch.minimum(ratio * advantage[ids],
                ratio.clamp(1.0 - clip, 1.0 + clip) * advantage[ids]).mean()
            values = critic(xt[ids]).squeeze(-1)
            value_loss = 0.5 * (values - reward_t[ids]).square().mean()
            entropy = distribution.entropy().mean()
            with torch.no_grad():
                anchor_logits = _masked(anchor, xt[ids], mt[ids])
            logp = torch.log_softmax(logits, dim=-1)
            anchor_logp = torch.log_softmax(anchor_logits, dim=-1)
            kl = (logp.exp() * (logp - anchor_logp)).sum(-1).mean()
            loss = policy_loss + value_coef * value_loss - entropy_coef * entropy + kl_coef * kl
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            nn.utils.clip_grad_norm_(list(actor.parameters()) + list(critic.parameters()), 0.5)
            optimizer.step()
            totals['policy'] += float(policy_loss.detach())
            totals['value'] += float(value_loss.detach())
            totals['entropy'] += float(entropy.detach())
            totals['kl'] += float(kl.detach())
            totals['batches'] += 1
        with torch.no_grad():
            kl_sum = 0.0
            for start in range(0, n, minibatch):
                ids = torch.arange(start, min(start + minibatch, n), device=device)
                logits = _masked(actor, xt[ids], mt[ids])
                anchor_logits = _masked(anchor, xt[ids], mt[ids])
                lp = torch.log_softmax(logits, dim=-1)
                anchor_lp = torch.log_softmax(anchor_logits, dim=-1)
                kl_sum += float((lp.exp() * (lp - anchor_lp)).sum(-1).sum())
            epoch_kl = kl_sum / n
            max_seen_kl = max(max_seen_kl, epoch_kl)
            if epoch_kl > max_kl:
                stopped = True
                break
        if stopped:
            break
    count = max(totals.pop('batches'), 1)
    metrics = {key: value / count for key, value in totals.items()}
    metrics.update(kl_to_anchor=max_seen_kl, stopped_early=stopped)
    return metrics


def export_policy(actor, features, mean, scale, *, update_ix, metadata):
    layers = []
    for layer in actor:
        if isinstance(layer, nn.Linear):
            layers.append(dict(weight=layer.weight.detach().cpu().tolist(),
                               bias=layer.bias.detach().cpu().tolist()))
    return dict(version=1, kind='growth_ppo', actions=list(ACTIONS), features=list(features),
                mean=np.asarray(mean, np.float32).tolist(), scale=np.asarray(scale, np.float32).tolist(),
                layers=layers, update=int(update_ix), metadata=metadata)


def validate_export(actor, payload, samples):
    """Check that the dependency-free deployed policy matches the PPO actor."""
    runtime = Policy(payload)
    if not samples:
        raise ValueError('cannot validate an export without rollout observations')
    normalized = np.stack(samples[:min(len(samples), 32)]).astype(np.float32, copy=False)
    mean = np.asarray(payload['mean'], dtype=np.float32)
    scale = np.asarray(payload['scale'], dtype=np.float32)
    rows = [dict(zip(payload['features'],
                     (mean + scale * vector).astype(np.float32).tolist())) for vector in normalized]
    actual = np.asarray([runtime.logits(row) for row in rows], dtype=np.float32)
    with torch.no_grad():
        expected = actor(torch.as_tensor(normalized, dtype=torch.float32,
                                         device=next(actor.parameters()).device)).cpu().numpy()
    if not np.isfinite(actual).all() or not np.allclose(expected, actual, atol=2e-4, rtol=2e-4):
        error = float(np.max(np.abs(expected - actual)))
        raise ValueError(f'PPO policy export parity failed: max logit error {error:g}')
    masks = np.stack([action_mask(row) for row in rows])
    expected_choice = np.argmax(np.where(masks, expected, -1e9), axis=1)
    actual_choice = np.asarray([runtime.choose(row) for row in rows])
    if not np.array_equal(expected_choice, actual_choice):
        raise ValueError('PPO policy export action-selection parity failed')


def save(path, actor, anchor, critic, optimizer, *, features, mean, scale, hidden, update_ix, metadata):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    torch.save(dict(format='growth-ppo-v1', actor=actor.state_dict(), anchor=anchor.state_dict(),
                    critic=critic.state_dict(), optimizer=optimizer.state_dict(),
                    features=list(features), mean=np.asarray(mean, np.float32).tolist(),
                    scale=np.asarray(scale, np.float32).tolist(), hidden=int(hidden),
                    update=int(update_ix), metadata=metadata), tmp)
    os.replace(tmp, path)


def load_resume(path):
    payload = torch.load(path, map_location='cpu', weights_only=True)
    if payload.get('format') != 'growth-ppo-v1':
        raise ValueError('unsupported PPO resume checkpoint')
    features = list(payload['features'])
    hidden = int(payload['hidden'])
    actor = network(len(features), len(ACTIONS), hidden)
    anchor = network(len(features), len(ACTIONS), hidden)
    critic = network(len(features), 1, hidden)
    actor.load_state_dict(payload['actor'])
    anchor.load_state_dict(payload['anchor'])
    critic.load_state_dict(payload['critic'])
    return actor, anchor, critic, features, np.asarray(payload['mean'], np.float32), \
        np.asarray(payload['scale'], np.float32), payload


def load_opponent_policies(paths, *, features, mean, scale, hidden, device):
    """Load frozen deployable policies for a small PPO league.

    League actors must use the exact same feature order and normalizer as the
    learner, since every callback is encoded by the learner's deploy wrapper.
    """
    opponents = []
    for path in paths:
        path = Path(path).resolve()
        actor, opp_features, opp_mean, opp_scale, payload = from_policy(
            str(path), allow_random=False, hidden=hidden, seed=0)
        if opp_features != features:
            raise ValueError(f'opponent policy feature order differs from learner: {path}')
        if not np.array_equal(opp_mean, mean) or not np.array_equal(opp_scale, scale):
            raise ValueError(f'opponent policy normalizer differs from learner: {path}')
        actor.to(device)
        opponents.append((f"{payload.get('kind')}-u{payload.get('update', 'awr')}", freeze(actor)))
    return opponents


def load_external_bots(paths):
    """Resolve frozen native bot folders to commands usable by an engine callback."""
    bots = []
    for item in paths:
        folder = Path(item).resolve()
        if not folder.is_dir():
            raise ValueError(f'external opponent must be a bot directory: {folder}')
        built = folder / '.unswbc-build'
        executable = next((candidate for candidate in (built / 'bot', built / 'bot.exe')
                           if candidate.is_file()), None)
        if executable:
            bots.append((folder.name, (str(executable),), str(folder)))
            continue
        entry = folder / 'main.py'
        if entry.is_file():
            bots.append((folder.name, (sys.executable, '-u', str(entry)), str(folder)))
            continue
        raise ValueError(f'bot folder has no built executable or main.py: {folder}')
    return bots


def collect_game(engine, holder, opponent, rollout, map_file, seed, learner_team, device,
                 reward_growth=0.0, reward_survival=0.0, reward_early_deaths=0.0,
                 reward_death_event=0.0, reward_wall_death_event_multiplier=1.0,
                 reward_self_death_event_multiplier=1.0,
                 reward_body_death_event_multiplier=1.0,
                 external_opponent=None):
    encoders, teams, external_processes = {}, {}, {}
    deaths = Counter()
    turns = Counter()
    early_deaths = Counter()
    early_turns = Counter()
    last_learner_action = {}
    local_rewards = Counter()
    death_events = Counter()
    unknown_death_reasons = Counter()
    start = len(rollout.x)
    started = time.perf_counter()
    opponent_temperature = holder['opponent_temperature']

    def spawn(dragon_id, raw):
        text = raw.decode() if isinstance(raw, bytes) else raw
        spec = parse_spawn(text)
        teams[dragon_id] = spec.team
        if external_opponent is not None and spec.team != learner_team:
            command, cwd = external_opponent[1], external_opponent[2]
            process = subprocess.Popen(command, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.DEVNULL)
            process.stdin.write(raw if isinstance(raw, bytes) else raw.encode())
            process.stdin.flush()
            external_processes[dragon_id] = process
        else:
            encoders[dragon_id] = FV.Proc(spec.id, spec.team, spec.W, spec.H, spec.unit_limit)

    def reply(dragon_id, raw):
        lines = raw.decode().splitlines() if isinstance(raw, bytes) else raw.splitlines()
        if lines and lines[0].startswith('ENDGAME'):
            return b'ENDTURN\n'
        team = teams.get(dragon_id)
        if team is not None:
            turns[team] += 1
        if dragon_id in external_processes:
            process = external_processes[dragon_id]
            try:
                packet = raw if isinstance(raw, bytes) else raw.encode()
                process.stdin.write(packet + (b'' if packet.endswith(b'\n') else b'\n') + b'\n')
                process.stdin.flush()
                output = []
                while True:
                    line = process.stdout.readline()
                    if not line:
                        break
                    output.append(line)
                    if line.strip() == b'ENDTURN':
                        break
                return b''.join(output) if output else b'ENDTURN\n'
            except (BrokenPipeError, OSError):
                return b'ENDTURN\n'
        block, _ = FV.parse_block(lines)
        if int(block['round']) < 100:
            early_turns[teams[dragon_id]] += 1
        row = encoders[dragon_id].features(block)
        if holder['actor'] is None:
            features = discover_features(row)
            mean = np.zeros(len(features), dtype=np.float32)
            scale = np.ones(len(features), dtype=np.float32)
            actor = network(len(features), len(ACTIONS), holder['hidden'])
            critic = network(len(features), 1, holder['hidden']).to(device)
            actor = actor.to(device)
            holder.update(actor=actor, anchor=freeze(actor).to(device), critic=critic,
                          features=features, mean=mean, scale=scale)
            # The first opponent policy is the same frozen initial actor.
            if opponent is None:
                opponent_model = freeze(actor)
            else:
                opponent_model = opponent
            holder['opponent_model'] = opponent_model
        actor = holder['actor']
        features, mean, scale = holder['features'], holder['mean'], holder['scale']
        x = normalized_row(row, features, mean, scale)
        mask = action_mask(row)
        is_learner = teams[dragon_id] == learner_team
        policy = actor if is_learner else holder.get('opponent_model', opponent or actor)
        with torch.no_grad():
            tensor = torch.as_tensor(x, dtype=torch.float32, device=device).unsqueeze(0)
            mask_tensor = torch.as_tensor(mask, dtype=torch.bool, device=device).unsqueeze(0)
            logits = _masked(policy, tensor, mask_tensor)
            distribution = Categorical(logits=logits / max(opponent_temperature, 1e-6)) if (not is_learner and opponent_temperature > 0) else Categorical(logits=logits)
            if is_learner:
                choice_t = distribution.sample()
                choice = int(choice_t.item())
                logp = float(distribution.log_prob(choice_t).item())
                value = float(holder['critic'](tensor).squeeze(-1).item())
                last_learner_action[dragon_id] = rollout.add(x, mask, choice, logp, value)
            else:
                choice = int(logits.argmax(-1).item()) if opponent_temperature <= 0 else int(distribution.sample().item())
        action = ACTIONS[choice]
        if action.startswith('split_'):
            size = split_size(action, int(block['length']))
            encoders[dragon_id].record_action('split', split=size)
            command = f'SPLIT {size}'
        else:
            directions = []
            facing = block['dir']
            for relative in action:
                facing = FV.rel_to_abs(facing, relative)
                directions.append(facing)
            encoders[dragon_id].record_action('move', rels=list(action))
            command = 'MOVE ' + ''.join(directions)
        return f'{command}\nPROTOCOL 3\nENDTURN\n'.encode()

    def on_death(dragon_id, round_num, reason):
        team = teams.get(dragon_id)
        if team is not None:
            deaths[team] += 1
            if round_num < 100:
                early_deaths[team] += 1
            if team == learner_team and round_num < 100 and reward_death_event > 0:
                reason_name = {
                    'W': 'wall', 'S': 'self', 'B': 'body', 'O': 'body',
                    'H': 'h2h', 'I': 'invalid', 'A': 'invalid',
                    'hitWall': 'wall', 'hitSelf': 'self', 'hitOtherBody': 'body',
                    'hitHeadToHead': 'h2h', 'noValidAction': 'invalid',
                }.get(str(reason))
                if reason_name in ('wall', 'self', 'body', 'h2h'):
                    action_index = last_learner_action.pop(dragon_id, None)
                    if action_index is not None:
                        cause_multiplier = {
                            'wall': reward_wall_death_event_multiplier,
                            'self': reward_self_death_event_multiplier,
                            'body': reward_body_death_event_multiplier,
                        }.get(reason_name, 1.0)
                        local_rewards[action_index] -= reward_death_event * cause_multiplier
                        death_events[reason_name] += 1
                else:
                    unknown_death_reasons[str(reason)] += 1
        process = external_processes.pop(dragon_id, None)
        if process is not None:
            process.kill()
            process.wait()

    try:
        result = engine.run(map_file.read_bytes(), reply, on_death=on_death,
                            bot_spawn=spawn, debug=0, seed=int(seed))
    finally:
        for process in external_processes.values():
            process.kill()
            process.wait()
        external_processes.clear()
    score = 0.5 if result.winner is None else float(result.winner == learner_team)
    outcome_reward = score * 2.0 - 1.0
    if learner_team == 'A':
        own_length, own_longest = result.a_length, result.a_longest
        opponent_deaths, own_deaths = deaths['B'], deaths['A']
        own_turns, opponent_turns = turns['A'], turns['B']
    else:
        own_length, own_longest = result.b_length, result.b_longest
        opponent_deaths, own_deaths = deaths['A'], deaths['B']
        own_turns, opponent_turns = turns['B'], turns['A']
    growth_signal = (np.log1p(max(0, own_length)) - np.log1p(8.0) +
                     0.25 * (np.log1p(max(0, own_longest)) - np.log1p(1.0)))
    prior_turns, prior_death_rate = 256.0, 0.02
    own_rate = (own_deaths + prior_turns * prior_death_rate) / (own_turns + prior_turns)
    opponent_rate = (opponent_deaths + prior_turns * prior_death_rate) / (opponent_turns + prior_turns)
    survival_signal = float(np.clip(10.0 * (opponent_rate - own_rate), -0.05, 0.05))
    early_rate = ((early_deaths[learner_team] + 64.0 * 0.002) /
                  (early_turns[learner_team] + 64.0))
    early_death_signal = float(np.clip(-1000.0 * early_rate, -100.0, 0.0))
    shaped_reward = (outcome_reward + reward_growth * growth_signal +
                     reward_survival * survival_signal + reward_early_deaths * early_death_signal)
    rollout.finish(start, shaped_reward, dict(map=map_file.stem, seed=int(seed), winner=result.winner,
        rounds=result.rounds, learner_team=learner_team, opponent=holder.get('opponent_label'),
        outcome_reward=outcome_reward, growth_signal=float(growth_signal),
        survival_signal=survival_signal, own_deaths=own_deaths, opponent_deaths=opponent_deaths,
        own_turns=own_turns, opponent_turns=opponent_turns,
        own_early_deaths=early_deaths[learner_team], own_early_turns=early_turns[learner_team],
        early_death_signal=early_death_signal, death_events=dict(death_events),
        unknown_death_reasons=dict(unknown_death_reasons),
        death_event_penalty=float(sum(local_rewards.values())),
        reward=shaped_reward, seconds=round(time.perf_counter() - started, 3)), local_rewards)
    engine._live = None
    return result


def match_metrics(actor, critic, anchor, optimizer, rollout, args, device):
    batch = rollout.arrays()
    metrics = update(actor, anchor, critic, optimizer, batch, epochs=args.epochs,
        minibatch=args.minibatch, clip=args.clip, entropy_coef=args.entropy,
        value_coef=args.value_coef, kl_coef=args.kl_coef, max_kl=args.max_kl, device=device)
    scores = [(game.get('outcome_reward', game['reward']) + 1.0) / 2.0 for game in rollout.games]
    return dict(metrics=metrics, learner_decisions=len(rollout.x), games=rollout.games,
                win_share=float(np.mean(scores)), rounds=[game['rounds'] for game in rollout.games])


def train(args):
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.set_num_threads(args.threads)
    device = torch.device(args.device)
    out = Path(args.out)
    if not out.is_absolute():
        out = D.ROOT / out
    out = out.resolve()
    maps = [D.ROOT / 'maps/live' / item.strip() for item in args.maps.split(',')]
    heldout = {'autarky', 'maze', 'trauma'}
    for path in maps:
        if path.suffix != '.map' or not path.is_file() or path.parent.resolve() != (D.ROOT / 'maps/live').resolve():
            raise ValueError(f'training map must be a maps/live/*.map template: {path}')
        if path.stem.casefold() in heldout:
            raise ValueError(f'refusing held-out map: {path.stem}')
    if args.games_per_update < 1 or args.games_per_update > MAX_GAMES_PER_PROCESS:
        raise ValueError(f'--games-per-update must be in [1, {MAX_GAMES_PER_PROCESS}]')
    if not 1 <= args.chunk_decisions <= 1_000_000:
        raise ValueError('--chunk-decisions must be in [1, 1000000]')
    if args.team not in ('A', 'B'):
        raise ValueError('--team must be A or B')

    resume_state = None
    if args.resume:
        actor, anchor, critic, features, mean, scale, resume_state = load_resume(args.resume)
        hidden = int(resume_state['hidden'])
        init_meta = dict(resumed_from=str(Path(args.resume).resolve()))
    else:
        actor, features, mean, scale, source = from_policy(args.init_policy,
            allow_random=args.allow_random_init, hidden=args.hidden, seed=args.seed)
        hidden = args.hidden
        anchor = freeze(actor) if actor is not None else None
        critic = network(len(features), 1, hidden) if features is not None else None
        init_meta = dict(initial_policy=source.get('kind'), source_policy=args.init_policy)
    if actor is not None:
        actor.to(device)
        anchor.to(device)
        critic.to(device)
    optimizer = torch.optim.Adam(list(actor.parameters()) + list(critic.parameters()), lr=args.lr) if actor is not None else None
    if resume_state and 'optimizer' in resume_state:
        optimizer.load_state_dict(resume_state['optimizer'])
    start_update = int(resume_state.get('update', 0)) if resume_state else 0
    opponent_paths = [item.strip() for item in args.opponent_policies.split(',') if item.strip()]
    bot_paths = [item.strip() for item in args.opponent_bots.split(',') if item.strip()]
    if (opponent_paths or bot_paths) and actor is None:
        raise ValueError('--opponent-policies and --opponent-bots require a neural learner policy')
    fixed_opponents = load_opponent_policies(opponent_paths, features=features, mean=mean,
        scale=scale, hidden=hidden, device=device) if opponent_paths else []
    external_opponents = load_external_bots(bot_paths) if bot_paths else []
    metadata = dict(init_meta, reward='terminal match result plus growth, death-rate, and local death-event shaping',
                    reward_shaping=dict(growth=args.reward_growth, survival=args.reward_survival,
                                        early_deaths=args.reward_early_deaths,
                                        death_event=args.reward_death_event,
                                        wall_death_event_multiplier=args.reward_wall_death_event_multiplier,
                                        self_death_event_multiplier=args.reward_self_death_event_multiplier,
                                        body_death_event_multiplier=args.reward_body_death_event_multiplier,
                                        death_event_signal='local penalty on the learner action immediately before a wall, self, body, or head-to-head death during rounds 0-99',
                                        early_death_signal='negative smoothed learner deaths per 1000 learner turns during rounds 0-99; 64-turn prior at 2%, capped at 100',
                                        survival_signal='smoothed opponent minus learner death rate; 256-turn prior at 2%, scaled by 10 and capped at +/-0.05'),
                    objective='team outcome; shared decision actor', wrapper='growth_rl bot_main.py v4 features and action decoder',
                    mask='growth_rl.policy.action_mask: structural split legality; fatal moves remain learnable',
                    map_names=[path.stem for path in maps], seed=args.seed,
                    opponent_pool=[label for label, _ in fixed_opponents] +
                                  [label for label, _, _ in external_opponents] + ['current_snapshot'],
                    opponent_sampling='stratified' if args.stratified_league else 'uniform')
    holder = dict(actor=actor, anchor=anchor, critic=critic, features=features, mean=mean, scale=scale,
                  hidden=hidden, opponent_temperature=args.opponent_temperature)
    engine = EngineModule()
    rng = random.Random(args.seed + 1)
    for step in range(args.updates):
        current = holder['actor']
        league = list(fixed_opponents)
        league.extend(external_opponents)
        current_opponent = None
        if current is not None:
            current_opponent = ('current_snapshot', freeze(current))
            league.append(current_opponent)
        if (args.stratified_league and fixed_opponents and external_opponents and
                args.games_per_update > len(fixed_opponents)):
            hard_pool = list(external_opponents)
            if current_opponent is not None:
                hard_pool.append(current_opponent)
            opponent_schedule = list(fixed_opponents)
            opponent_schedule.extend(rng.choice(hard_pool)
                                     for _ in range(args.games_per_update - len(fixed_opponents)))
            rng.shuffle(opponent_schedule)
        else:
            opponent_schedule = [rng.choice(league) for _ in range(args.games_per_update)]
        rollout = Rollout(args.chunk_decisions)
        for selected in opponent_schedule:
            if league:
                if len(selected) == 3:
                    opponent_label, _, _ = selected
                    opponent, external_opponent = None, selected
                else:
                    opponent_label, opponent = selected
                    external_opponent = None
            else:
                opponent_label, opponent, external_opponent = 'bootstrap_self', None, None
            holder['opponent_label'] = opponent_label
            holder['opponent_model'] = opponent
            collect_game(engine, holder, opponent, rollout, rng.choice(maps), rng.randrange(1000, 2**31),
                         args.team, device, reward_growth=args.reward_growth,
                         reward_survival=args.reward_survival,
                         reward_early_deaths=args.reward_early_deaths,
                         reward_death_event=args.reward_death_event,
                         reward_wall_death_event_multiplier=args.reward_wall_death_event_multiplier,
                         reward_self_death_event_multiplier=args.reward_self_death_event_multiplier,
                         reward_body_death_event_multiplier=args.reward_body_death_event_multiplier,
                         external_opponent=external_opponent)
            if len(rollout.x) >= args.chunk_decisions:
                break
        actor, anchor, critic = holder['actor'], holder['anchor'], holder['critic']
        if actor is None:
            raise RuntimeError('random-init rollout failed to initialize an actor')
        if anchor is None:
            holder['anchor'] = anchor = freeze(actor)
        if critic is None:
            holder['critic'] = critic = network(len(holder['features']), 1, hidden).to(device)
            optimizer = torch.optim.Adam(list(actor.parameters()) + list(critic.parameters()), lr=args.lr)
        elif optimizer is None:
            optimizer = torch.optim.Adam(list(actor.parameters()) + list(critic.parameters()), lr=args.lr)
        actor.to(device); anchor.to(device); critic.to(device)
        actual_update = start_update + step + 1
        report = match_metrics(actor, critic, anchor, optimizer, rollout, args, device)
        report.update(update=actual_update, all_team_decisions=sum(game['decisions'] for game in rollout.games),
                      reward_growth=args.reward_growth, reward_survival=args.reward_survival,
                      reward_early_deaths=args.reward_early_deaths,
                      reward_death_event=args.reward_death_event,
                      reward_wall_death_event_multiplier=args.reward_wall_death_event_multiplier,
                      reward_self_death_event_multiplier=args.reward_self_death_event_multiplier,
                      reward_body_death_event_multiplier=args.reward_body_death_event_multiplier,
                      safety_stop=bool(report['metrics']['kl_to_anchor'] > args.max_kl))
        print(json.dumps(report, separators=(',', ':')), flush=True)
        out.mkdir(parents=True, exist_ok=True)
        with (out / 'updates.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(report, separators=(',', ':')) + '\n')
        payload = export_policy(actor, holder['features'], holder['mean'], holder['scale'],
                                update_ix=actual_update, metadata=metadata)
        validate_export(actor, payload, rollout.x)
        D.atomic_json(out / 'policy.json', payload)
        save(out / 'checkpoint.pt', actor, anchor, critic, optimizer, features=holder['features'],
             mean=holder['mean'], scale=holder['scale'], hidden=hidden,
             update_ix=actual_update, metadata=metadata)
        package(out / 'policy.json', out / 'bot')
        start_update = actual_update
        del opponent, rollout
        gc.collect()
        if report['safety_stop']:
            print(f"stopping: KL {report['metrics']['kl_to_anchor']:.4f} exceeded max {args.max_kl:.4f}",
                  file=sys.stderr, flush=True)
            break


def recycled_train(args):
    out = Path(args.out)
    if not out.is_absolute():
        out = D.ROOT / out
    out = out.resolve()
    resume = Path(args.resume).resolve() if args.resume else None
    options = (
        ('--maps', args.maps), ('--out', str(out)), ('--games-per-update', args.games_per_update),
        ('--opponent-policies', args.opponent_policies),
        ('--opponent-bots', args.opponent_bots),
        ('--chunk-decisions', args.chunk_decisions), ('--team', args.team), ('--device', args.device),
        ('--threads', args.threads), ('--lr', args.lr), ('--epochs', args.epochs),
        ('--minibatch', args.minibatch), ('--clip', args.clip), ('--entropy', args.entropy),
        ('--value-coef', args.value_coef), ('--kl-coef', args.kl_coef), ('--max-kl', args.max_kl),
        ('--opponent-temperature', args.opponent_temperature), ('--hidden', args.hidden),
        ('--reward-growth', args.reward_growth), ('--reward-survival', args.reward_survival),
        ('--reward-early-deaths', args.reward_early_deaths),
        ('--reward-death-event', args.reward_death_event),
        ('--reward-wall-death-event-multiplier', args.reward_wall_death_event_multiplier),
        ('--reward-self-death-event-multiplier', args.reward_self_death_event_multiplier),
        ('--reward-body-death-event-multiplier', args.reward_body_death_event_multiplier),
    )
    for ix in range(args.updates):
        cmd = [sys.executable, '-m', 'tools.growth_rl.ppo', '--updates', '1', '--seed', str(args.seed + ix)]
        for flag, value in options:
            cmd.extend([flag, str(value)])
        if args.stratified_league:
            cmd.append('--stratified-league')
        if ix == 0 and args.init_policy:
            cmd.extend(['--init-policy', str(Path(args.init_policy).resolve())])
        elif resume is not None:
            cmd.extend(['--resume', str(resume)])
        elif ix == 0 and args.allow_random_init:
            cmd.append('--allow-random-init')
        subprocess.run(cmd, cwd=D.ROOT, check=True)
        resume = out / 'checkpoint.pt'
        rows = (out / 'updates.jsonl').read_text(encoding='utf-8').splitlines()
        if rows and json.loads(rows[-1]).get('safety_stop'):
            break


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--maps', default='default.map', help='comma-separated maps/live/*.map files')
    parser.add_argument('--out', default='build/growth_rl/ppo/run')
    parser.add_argument('--init-policy', help='neural growth_awr/growth_ppo policy.json warm start')
    parser.add_argument('--resume', help='this trainer\'s checkpoint.pt')
    parser.add_argument('--opponent-policies', default='',
                        help='comma-separated neural policy.json files added to the current-snapshot self-play pool')
    parser.add_argument('--opponent-bots', default='',
                        help='comma-separated built bot directories added to the current-snapshot league')
    parser.add_argument('--stratified-league', action='store_true',
                        help='include each frozen neural baseline in every update; sample remaining games from hard opponents')
    parser.add_argument('--allow-random-init', action='store_true', help='only for plumbing smoke runs')
    parser.add_argument('--updates', type=int, default=1)
    parser.add_argument('--games-per-update', type=int, default=4)
    parser.add_argument('--chunk-decisions', type=int, default=100_000)
    parser.add_argument('--team', choices=('A', 'B'), default='A')
    parser.add_argument('--seed', type=int, default=1701)
    parser.add_argument('--device', default='cpu')
    parser.add_argument('--threads', type=int, default=1)
    parser.add_argument('--hidden', type=int, default=DEFAULT_HIDDEN)
    parser.add_argument('--lr', type=float, default=3e-4)
    parser.add_argument('--epochs', type=int, default=4)
    parser.add_argument('--minibatch', type=int, default=512)
    parser.add_argument('--clip', type=float, default=0.2)
    parser.add_argument('--entropy', type=float, default=0.01)
    parser.add_argument('--value-coef', type=float, default=0.5)
    parser.add_argument('--kl-coef', type=float, default=0.02)
    parser.add_argument('--max-kl', type=float, default=0.5)
    parser.add_argument('--opponent-temperature', type=float, default=0.0)
    parser.add_argument('--reward-growth', type=float, default=0.0,
                        help='terminal growth shaping coefficient; based on final team length/longest relative to the initial board')
    parser.add_argument('--reward-survival', type=float, default=0.0,
                        help='terminal survival shaping coefficient; multiplies the smoothed, capped death-rate difference')
    parser.add_argument('--reward-early-deaths', type=float, default=0.0,
                        help='terminal penalty per smoothed learner death per 1000 action turns during rounds 0-99')
    parser.add_argument('--reward-death-event', type=float, default=0.0,
                        help='local penalty on the learner action immediately before a D-032 death before round 100')
    parser.add_argument('--reward-wall-death-event-multiplier', type=float, default=1.0,
                        help='multiplier for wall-death local penalties')
    parser.add_argument('--reward-self-death-event-multiplier', type=float, default=1.0,
                        help='multiplier for self-death local penalties')
    parser.add_argument('--reward-body-death-event-multiplier', type=float, default=1.0,
                        help='multiplier for body-death local penalties; D-032 measures body deaths separately')
    args = parser.parse_args()
    if args.updates < 1 or args.epochs < 1 or args.minibatch < 1 or args.hidden < 1:
        parser.error('--updates, --epochs, --minibatch and --hidden must be positive')
    if bool(args.init_policy) + bool(args.resume) + bool(args.allow_random_init) != 1:
        parser.error('choose exactly one of --init-policy, --resume, or --allow-random-init')
    if args.games_per_update < 1 or args.games_per_update > MAX_GAMES_PER_PROCESS:
        parser.error(f'--games-per-update must be in [1,{MAX_GAMES_PER_PROCESS}]')
    if args.reward_body_death_event_multiplier < 0:
        parser.error('--reward-body-death-event-multiplier must be nonnegative')
    if args.reward_self_death_event_multiplier < 0:
        parser.error('--reward-self-death-event-multiplier must be nonnegative')
    if args.reward_wall_death_event_multiplier < 0:
        parser.error('--reward-wall-death-event-multiplier must be nonnegative')
    try:
        if args.updates == 1:
            train(args)
        else:
            recycled_train(args)
    except (ValueError, RuntimeError, OSError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
