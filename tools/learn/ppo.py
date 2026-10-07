#!/usr/bin/env python3
"""Small, deploy-encoder PPO prototype for Battlecode self-play.

The policy uses encoder v1 observations and the F/R/L action head from P-7.
It collects one team's decisions against a frozen snapshot in the official
in-process engine, assigns the match result to that team's decisions, and
performs clipped PPO updates with a KL anchor to the initial policy.

This is an experimental trainer, not a candidate bot: the wrapper currently
issues one-step MOVE commands and does not retain a chassis bot's split/search
behaviour. A real P-7 run also needs a selected/distilled actor checkpoint,
its scalar normalization, and the approved evaluation fixture set.
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
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.distributions import Categorical

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/learn'))
import block as B  # noqa: E402
import encode as E  # noqa: E402
from unswbc.engine import EngineModule  # noqa: E402

REL = 'FRL'
REL_TO_LOGIT = (0, 1, 3)  # The fourth A10 output is reverse; P-7 masks it.
ACTION_MIRROR = (0, 2, 1)
MAX_GAMES_PER_PROCESS = 500


class ActorCritic(nn.Module):
    """A10-compatible shared trunk, four direction logits, and a scalar value head."""

    def __init__(self, scalar_mean: np.ndarray | None = None,
                 scalar_std: np.ndarray | None = None):
        super().__init__()
        self.c = nn.Sequential(
            nn.Conv2d(E.N_CH, 32, 3, padding=1), nn.ReLU(),
            nn.Conv2d(32, 32, 3, padding=1), nn.ReLU(), nn.Flatten(),
        )
        # Names and shapes for c.* and h.* match the A10 supervised network,
        # allowing strict=False warm starts from its state_dict.
        self.h = nn.Sequential(nn.Linear(32 * 49 + E.N_SC, 64), nn.ReLU(), nn.Linear(64, 4))
        self.value_head = nn.Linear(64, 1)
        mean = np.zeros(E.N_SC, np.float32) if scalar_mean is None else np.asarray(scalar_mean, np.float32)
        std = np.full(E.N_SC, 100.0, np.float32) if scalar_std is None else np.asarray(scalar_std, np.float32)
        if mean.shape != (E.N_SC,) or std.shape != (E.N_SC,):
            raise ValueError(f'normalizer must contain {E.N_SC} scalar means and standard deviations')
        if not np.isfinite(mean).all() or not np.isfinite(std).all() or (std <= 0).any():
            raise ValueError('scalar normalizer must be finite with positive standard deviations')
        self.register_buffer('scalar_mean', torch.from_numpy(mean.copy()))
        self.register_buffer('scalar_std', torch.from_numpy(std.copy()))

    def forward(self, obs: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        obs = obs.to(dtype=torch.float32)
        n = E.N_CH * 49
        planes = obs[..., :n].reshape(-1, 49, E.N_CH).transpose(1, 2).reshape(-1, E.N_CH, 7, 7)
        scalars = (obs[..., n:] - self.scalar_mean) / self.scalar_std
        hidden = torch.cat([self.c(planes), scalars], dim=1)
        latent = self.h[1](self.h[0](hidden))
        return self.h[2](latent), self.value_head(latent).squeeze(-1)


def legal_logits(logits: torch.Tensor) -> torch.Tensor:
    """Return the conditional F/R/L logits; B is not a P-7 action."""
    return logits[..., list(REL_TO_LOGIT)]


def mirror_observation(obs: np.ndarray) -> np.ndarray:
    """Reflect encoder-v1 observations left-to-right in the egocentric frame."""
    src = np.asarray(obs)
    one = src.ndim == 1
    rows = src.reshape(-1, E.N_CH * 49 + E.N_SC)
    out = rows.copy()
    swap_channel = {
        E.CH.index('kelp_R'): E.CH.index('kelp_L'),
        E.CH.index('kelp_L'): E.CH.index('kelp_R'),
        E.CH.index('portal_R'): E.CH.index('portal_L'),
        E.CH.index('portal_L'): E.CH.index('portal_R'),
        E.CH.index('head_fac_R'): E.CH.index('head_fac_L'),
        E.CH.index('head_fac_L'): E.CH.index('head_fac_R'),
    }
    for row in range(7):
        for col in range(7):
            source = row * 7 + (6 - col)
            dest = row * 7 + col
            for channel in range(E.N_CH):
                out[:, dest * E.N_CH + channel] = rows[:, source * E.N_CH + swap_channel.get(channel, channel)]
    scalar_start = E.N_CH * 49
    scalar_idx = {name: i for i, name in enumerate(E.SC)}
    for left, right in (('exit_R', 'exit_L'), ('exit_L', 'exit_R')):
        out[:, scalar_start + scalar_idx[left]] = rows[:, scalar_start + scalar_idx[right]]
    last = scalar_start + scalar_idx['last_first_rel']
    old_last = rows[:, last].copy()
    out[:, last] = np.where(old_last == 1, 3, np.where(old_last == 3, 1, old_last))
    for name in ('ownq_r', 'enemyq_r', 'home_r', 'mirror_xy_r', 'mirror_y_r'):
        i = scalar_start + scalar_idx[name]
        out[:, i] = np.where(rows[:, i] == E.BIG, E.BIG, -rows[:, i])
    return out[0] if one else out.reshape(src.shape)


class Rollout:
    """Compact completed-game samples; each row is one learner-team decision."""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.obs: list[np.ndarray] = []
        self.actions: list[int] = []
        self.logp: list[float] = []
        self.values: list[float] = []
        self.returns: list[float] = []
        self.games: list[dict] = []

    def add(self, obs, action, logp, value):
        if len(self.obs) >= self.capacity:
            raise RuntimeError(f'rollout exceeded --chunk-decisions={self.capacity}; lower --games-per-update')
        x = np.asarray(obs, dtype=np.int16)
        if x.shape != (49 * E.N_CH + E.N_SC,):
            raise ValueError(f'bad encoder row shape: {x.shape}')
        self.obs.append(x)
        self.actions.append(int(action))
        self.logp.append(float(logp))
        self.values.append(float(value))

    def finish_game(self, start: int, reward: float, meta: dict):
        n = len(self.obs) - start
        self.returns.extend([float(reward)] * n)
        self.games.append({**meta, 'decisions': n, 'score': float(reward)})

    def arrays(self):
        if not self.obs:
            raise RuntimeError('no learner decisions were collected')
        return (
            np.stack(self.obs), np.asarray(self.actions, np.int64),
            np.asarray(self.logp, np.float32), np.asarray(self.values, np.float32),
            np.asarray(self.returns, np.float32),
        )

    def clear(self):
        self.__init__(self.capacity)


def frozen(model: ActorCritic) -> ActorCritic:
    result = copy.deepcopy(model).eval()
    for p in result.parameters():
        p.requires_grad_(False)
    return result


def _tensor_batch(a, device):
    return torch.as_tensor(a, device=device)


def ppo_update(actor: ActorCritic, anchor: ActorCritic, optimizer,
               batch, *, epochs=4, minibatch=512, clip=0.2,
               entropy_coef=0.01, value_coef=0.5, kl_coef=0.02,
               max_kl=0.5, device='cpu') -> dict:
    obs, actions, old_logp, old_values, returns = batch
    # Mirror augmentation is the symmetry treatment required by the P-7 entry
    # ruling. Recompute behavior probabilities on reflected states from the
    # unchanged rollout actor before any update.
    mirrored_obs = mirror_observation(obs)
    mirrored_actions = np.take(np.asarray(ACTION_MIRROR), actions)
    with torch.no_grad():
        mx = _tensor_batch(mirrored_obs, device)
        ml, mv = actor(mx)
        mold_logp = Categorical(logits=legal_logits(ml)).log_prob(
            _tensor_batch(mirrored_actions, device)
        ).cpu().numpy()
    obs = np.concatenate([obs, mirrored_obs])
    actions = np.concatenate([actions, mirrored_actions])
    old_logp = np.concatenate([old_logp, mold_logp.astype(np.float32)])
    old_values = np.concatenate([old_values, mv.cpu().numpy().astype(np.float32)])
    returns = np.concatenate([returns, returns])
    advantages = returns - old_values
    if len(advantages) > 1 and float(advantages.std()) > 1e-8:
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

    xt = _tensor_batch(obs, device)
    at = _tensor_batch(actions, device)
    lpt = _tensor_batch(old_logp, device)
    advt = _tensor_batch(advantages.astype(np.float32), device)
    rt = _tensor_batch(returns, device)
    n = len(obs)
    totals = dict(policy=0.0, value=0.0, entropy=0.0, kl=0.0, updates=0)
    max_seen_kl = 0.0
    stopped_early = False
    for _ in range(epochs):
        order = torch.randperm(n, device=device)
        for start in range(0, n, minibatch):
            ids = order[start:start + minibatch]
            logits, values = actor(xt[ids])
            dist = Categorical(logits=legal_logits(logits))
            logp = dist.log_prob(at[ids])
            ratio = (logp - lpt[ids]).exp()
            unclipped = ratio * advt[ids]
            clipped = ratio.clamp(1.0 - clip, 1.0 + clip) * advt[ids]
            policy_loss = -torch.minimum(unclipped, clipped).mean()
            value_loss = 0.5 * (values - rt[ids]).square().mean()
            entropy = dist.entropy().mean()
            with torch.no_grad():
                ref_logits, _ = anchor(xt[ids])
            ref_logp = torch.log_softmax(legal_logits(ref_logits), dim=-1)
            current_logp = torch.log_softmax(legal_logits(logits), dim=-1)
            probs = current_logp.exp()
            kl = (probs * (current_logp - ref_logp)).sum(-1).mean()
            loss = policy_loss + value_coef * value_loss - entropy_coef * entropy + kl_coef * kl
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            nn.utils.clip_grad_norm_(actor.parameters(), 0.5)
            optimizer.step()
            totals['policy'] += float(policy_loss.detach())
            totals['value'] += float(value_loss.detach())
            totals['entropy'] += float(entropy.detach())
            totals['kl'] += float(kl.detach())
            totals['updates'] += 1
        with torch.no_grad():
            kl_sum = 0.0
            for start in range(0, n, minibatch):
                ids = torch.arange(start, min(start + minibatch, n), device=device)
                logits, _ = actor(xt[ids])
                ref_logits, _ = anchor(xt[ids])
                lp = torch.log_softmax(legal_logits(logits), dim=-1)
                ref_lp = torch.log_softmax(legal_logits(ref_logits), dim=-1)
                kl_sum += float((lp.exp() * (lp - ref_lp)).sum(-1).sum())
            epoch_kl = kl_sum / n
            max_seen_kl = max(max_seen_kl, epoch_kl)
            if epoch_kl > max_kl:
                stopped_early = True
        if stopped_early:
            break
    n_up = max(totals.pop('updates'), 1)
    totals = {k: v / n_up for k, v in totals.items()}
    totals['max_kl'] = max_seen_kl
    totals['stopped_early'] = stopped_early
    return totals


def read_normalizer(path: str | None):
    if path is None:
        return None, None
    obj = json.loads(Path(path).read_text())
    names = obj.get('scalar_names')
    if names is not None and names != E.SC:
        raise ValueError('normalizer scalar_names do not match encoder v1')
    return np.asarray(obj['scalar_mean'], np.float32), np.asarray(obj['scalar_std'], np.float32)


def load_actor(path: str | None, stats_path: str | None, seed: int) -> tuple[ActorCritic, ActorCritic, dict]:
    torch.manual_seed(seed)
    mean, std = read_normalizer(stats_path)
    actor = ActorCritic(mean, std)
    metadata = {'init': 'random', 'scalar_normalizer': 'zero_mean_std_100'}
    if path:
        payload = torch.load(path, map_location='cpu', weights_only=True)
        if isinstance(payload, dict) and 'actor' in payload:
            if payload.get('format') != 'battlecode-ppo-v1':
                raise ValueError('unsupported PPO checkpoint format')
            if payload.get('encoder_version') != E.ENC_VERSION or payload.get('action_order') != list(REL):
                raise ValueError('PPO checkpoint encoder/action contract does not match this trainer')
            if stats_path is not None:
                raise ValueError('checkpoint already carries its scalar normalizer; omit --init-stats')
            mean = np.asarray(payload['scalar_mean'], np.float32)
            std = np.asarray(payload['scalar_std'], np.float32)
            actor = ActorCritic(mean, std)
            actor.load_state_dict(payload['actor'])
            anchor_state = payload.get('anchor')
            anchor = frozen(actor)
            if anchor_state is not None:
                anchor.load_state_dict(anchor_state)
            metadata = dict(payload.get('metadata', {}), resumed_from=str(path))
            return actor, anchor, metadata
        state = payload.get('state_dict', payload) if isinstance(payload, dict) else payload
        if not isinstance(state, dict):
            raise ValueError('initial checkpoint must be an A10 state_dict or a PPO checkpoint')
        result = actor.load_state_dict(state, strict=False)
        missing = [k for k in result.missing_keys if not k.startswith('value_head.')]
        unexpected = list(result.unexpected_keys)
        if missing or unexpected:
            raise ValueError(f'incompatible A10 checkpoint; missing={missing}, unexpected={unexpected}')
        if stats_path is None:
            raise ValueError('an A10 state_dict needs --init-stats with its training-fold scalar mean/std')
        metadata = {'init': 'a10_state_dict', 'source_checkpoint': str(path), 'scalar_normalizer': str(stats_path)}
    anchor = frozen(actor)
    return actor, anchor, metadata


def save_checkpoint(path: Path, actor, anchor, optimizer, update, metadata):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    torch.save({
        'format': 'battlecode-ppo-v1', 'encoder_version': E.ENC_VERSION,
        'action_order': list(REL), 'actor': actor.state_dict(), 'anchor': anchor.state_dict(),
        'optimizer': optimizer.state_dict(), 'update': int(update),
        'scalar_mean': actor.scalar_mean.cpu().tolist(), 'scalar_std': actor.scalar_std.cpu().tolist(),
        'metadata': metadata,
    }, tmp)
    os.replace(tmp, path)


def map_path(value: str) -> Path:
    p = Path(value)
    if not p.is_absolute():
        p = ROOT / p
    p = p.resolve()
    live = (ROOT / 'maps/live').resolve()
    try:
        p.relative_to(live)
    except ValueError as exc:
        raise ValueError(f'training maps must be frozen templates under {live}: {p}') from exc
    if p.suffix != '.map' or not p.is_file():
        raise ValueError(f'not a map file: {p}')
    txt = p.read_text()
    name_line = next((ln.split(maxsplit=1)[1] for ln in txt.splitlines() if ln.startswith('MAP_NAME ')), p.stem)
    heldout = set(json.loads((ROOT / 'docs/learning/splits/heldout-maps.json').read_text())['heldout_maps'])
    if name_line in heldout or p.stem.casefold() in {n.casefold() for n in heldout}:
        raise ValueError(f'refusing held-out training map: {p}')
    return p


def collect_game(engine, actor, opponent, rollout, map_file, seed, learner_team, device, stats):
    encoders, teams = {}, {}
    deaths = {}
    game_start = len(rollout.obs)
    started = time.perf_counter()

    def spawn(dragon_id, raw):
        s = B.parse_spawn(raw.decode() if isinstance(raw, bytes) else raw)
        encoders[dragon_id] = E.Encoder(s)
        teams[dragon_id] = s.team

    def on_death(dragon_id, round_num, reason):
        team = teams.get(dragon_id, '?')
        key = f'{team}:{reason}'
        deaths[key] = deaths.get(key, 0) + 1

    def reply(dragon_id, raw):
        b = B.parse_block(raw)
        if b.ended:
            return b'ENDTURN\n'
        encoder = encoders.get(dragon_id)
        if encoder is None:
            raise RuntimeError(f'engine requested dragon {dragon_id} before spawn callback')
        x = encoder.observe(b)
        is_learner = teams[dragon_id] == learner_team
        policy = actor if is_learner else opponent
        with torch.no_grad():
            obs_t = torch.as_tensor(np.asarray(x, np.float32), device=device).unsqueeze(0)
            logits, value = policy(obs_t)
            dist = Categorical(logits=legal_logits(logits))
            if is_learner:
                action_t = dist.sample()
                action = int(action_t.item())
                logp = float(dist.log_prob(action_t).item())
                rollout.add(x, action, logp, float(value.item()))
            else:
                action = int(dist.probs.argmax(-1).item())
        rel = REL[action]
        encoder.act('move', rel_steps=rel, rnd=b.round)
        abs_dir = E.DIRS[(E.DIRS.index(b.dir) + 'FRBL'.index(rel)) % 4]
        stats['decisions'] += 1
        if is_learner:
            stats['learner_decisions'] += 1
        return f'MOVE {abs_dir}\nPROTOCOL 3\nENDTURN\n'.encode()

    result = engine.run(map_file.read_bytes(), reply, on_death=on_death,
                        bot_spawn=spawn, debug=0, seed=int(seed))
    score = 0.0 if result.winner is None else (1.0 if result.winner == learner_team else -1.0)
    rollout.finish_game(game_start, score, {
        'map': map_file.stem, 'seed': int(seed), 'winner': result.winner,
        'rounds': result.rounds, 'learner_team': learner_team, 'deaths': deaths,
        'seconds': round(time.perf_counter() - started, 3),
    })
    stats['games'] += 1
    stats['rounds'] += int(result.rounds)
    engine._live = None
    if stats['games'] % 4 == 0:
        gc.collect()
    return result


def train(args):
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.set_num_threads(args.threads)
    device = torch.device(args.device)
    actor, anchor, metadata = load_actor(args.init, args.init_stats, args.seed)
    actor.to(device)
    anchor.to(device)
    optimizer = torch.optim.Adam(actor.parameters(), lr=args.lr)
    start_update = 0
    if args.init and Path(args.init).is_file():
        payload = torch.load(args.init, map_location='cpu', weights_only=True)
        if isinstance(payload, dict) and payload.get('format') == 'battlecode-ppo-v1':
            if 'optimizer' in payload:
                optimizer.load_state_dict(payload['optimizer'])
            start_update = int(payload.get('update', 0))
    maps = [map_path(m) for m in args.maps.split(',')]
    if not maps:
        raise ValueError('at least one --maps entry is required')
    if args.games_per_update < 1 or args.games_per_update > MAX_GAMES_PER_PROCESS:
        raise ValueError(f'--games-per-update must be between 1 and {MAX_GAMES_PER_PROCESS}; workers must be recycled')
    if args.chunk_decisions < 1 or args.chunk_decisions > 1_000_000:
        raise ValueError('--chunk-decisions must be in [1, 1000000]')
    if args.team not in ('A', 'B'):
        raise ValueError('--team must be A or B')
    out = Path(args.out)
    checkpoint = out / 'checkpoint.pt'
    runlog = out / 'updates.jsonl'
    metadata.update({
        'method': 'clipped PPO with frozen-policy KL anchor',
        'reward': 'terminal match outcome (+1 win, -1 loss, 0 draw), copied to each learner decision',
        'mirror_augmentation': True,
        'train_maps': [str(m.relative_to(ROOT)) for m in maps],
        'wrapper': 'one-step stochastic F/R/L MOVE; experimental direct-move policy',
        'seed': args.seed,
    })
    stats = {'decisions': 0, 'learner_decisions': 0, 'games': 0, 'rounds': 0}
    engine = EngineModule()
    rng = random.Random(args.seed + 1)
    for update_ix in range(args.updates):
        old_opponent = frozen(actor)
        rollout = Rollout(args.chunk_decisions)
        for game_ix in range(args.games_per_update):
            mf = rng.choice(maps)
            game_seed = rng.randrange(1000, 2**31)
            collect_game(engine, actor, old_opponent, rollout, mf, game_seed,
                         args.team, device, stats)
        if not rollout.obs:
            raise RuntimeError('no decisions for learner team; check --team and engine callbacks')
        batch = rollout.arrays()
        metrics = ppo_update(
            actor, anchor, optimizer, batch, epochs=args.epochs,
            minibatch=args.minibatch, clip=args.clip, entropy_coef=args.entropy,
            value_coef=args.value_coef, kl_coef=args.kl_coef, max_kl=args.max_kl,
            device=device,
        )
        actual_update = start_update + update_ix + 1
        row = {
            'update': actual_update, 'games': rollout.games,
            'learner_decisions': len(rollout.obs), 'all_team_decisions': stats['decisions'],
            'win_share': float(np.mean([(g['score'] + 1.0) / 2.0 for g in rollout.games])),
            'rounds': [g['rounds'] for g in rollout.games], 'matches': rollout.games,
            'metrics': metrics, 'elapsed_seconds': round(sum(g['seconds'] for g in rollout.games), 3),
            'safety_stop': bool(metrics['max_kl'] > args.max_kl),
        }
        print(json.dumps(row, separators=(',', ':')), flush=True)
        out.mkdir(parents=True, exist_ok=True)
        with runlog.open('a') as f:
            f.write(json.dumps(row, separators=(',', ':')) + '\n')
        save_checkpoint(checkpoint, actor, anchor, optimizer, actual_update, metadata)
        del old_opponent, rollout, batch
        gc.collect()
        if row['safety_stop']:
            print(f"stopping after update {actual_update}: rollout KL {metrics['max_kl']:.4f} exceeded "
                  f"--max-kl {args.max_kl:.4f}", file=sys.stderr, flush=True)
            break


def run_recycled_updates(args):
    """Run each PPO update in a fresh process to bound the engine's WASM leak."""
    out = Path(args.out)
    if not out.is_absolute():
        out = (ROOT / out).resolve()
    resume = Path(args.init).resolve() if args.init else None
    init_stats = Path(args.init_stats).resolve() if args.init_stats else None
    option_values = (
        ('--maps', args.maps), ('--out', str(out)),
        ('--games-per-update', args.games_per_update), ('--chunk-decisions', args.chunk_decisions),
        ('--team', args.team), ('--device', args.device), ('--threads', args.threads),
        ('--lr', args.lr), ('--epochs', args.epochs), ('--minibatch', args.minibatch),
        ('--clip', args.clip), ('--entropy', args.entropy), ('--value-coef', args.value_coef),
        ('--kl-coef', args.kl_coef), ('--max-kl', args.max_kl),
    )
    script = str(Path(__file__).resolve())
    for ix in range(args.updates):
        cmd = [sys.executable, script, '--updates', '1', '--seed', str(args.seed + ix)]
        for flag, value in option_values:
            cmd.extend([flag, str(value)])
        if resume is not None:
            cmd.extend(['--init', str(resume)])
        if init_stats is not None:
            cmd.extend(['--init-stats', str(init_stats)])
        subprocess.run(cmd, cwd=ROOT, check=True)
        resume = out / 'checkpoint.pt'
        init_stats = None
        rows = (out / 'updates.jsonl').read_text().splitlines()
        if rows and json.loads(rows[-1]).get('safety_stop'):
            break


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--maps', default='maps/live/default.map', help='comma-separated maps/live/*.map paths (held-out maps refused)')
    ap.add_argument('--out', default='build/learn/ppo/run', help='checkpoint and update log directory')
    ap.add_argument('--init', help='PPO checkpoint or A10 state_dict; omit only for a random-init smoke/prototype')
    ap.add_argument('--init-stats', help='JSON scalar_mean/scalar_std for an A10 state_dict')
    ap.add_argument('--updates', type=int, default=1)
    ap.add_argument('--games-per-update', type=int, default=4)
    ap.add_argument('--chunk-decisions', type=int, default=100_000, help='hard rollout cap, at most 1M rows')
    ap.add_argument('--team', choices=('A', 'B'), default='A')
    ap.add_argument('--seed', type=int, default=7)
    ap.add_argument('--device', default='cpu')
    ap.add_argument('--threads', type=int, default=1)
    ap.add_argument('--lr', type=float, default=3e-4)
    ap.add_argument('--epochs', type=int, default=4)
    ap.add_argument('--minibatch', type=int, default=512)
    ap.add_argument('--clip', type=float, default=0.2)
    ap.add_argument('--entropy', type=float, default=0.01)
    ap.add_argument('--value-coef', type=float, default=0.5)
    ap.add_argument('--kl-coef', type=float, default=0.02)
    ap.add_argument('--max-kl', type=float, default=0.5)
    args = ap.parse_args()
    if args.updates < 1 or args.epochs < 1 or args.minibatch < 1:
        ap.error('--updates, --epochs and --minibatch must be positive')
    if args.init_stats and not args.init:
        ap.error('--init-stats requires --init')
    try:
        if args.games_per_update < 1 or args.games_per_update > MAX_GAMES_PER_PROCESS:
            ap.error(f'--games-per-update must be between 1 and {MAX_GAMES_PER_PROCESS}')
        if args.updates == 1:
            train(args)
        else:
            run_recycled_updates(args)
    except (ValueError, RuntimeError, OSError) as exc:
        ap.error(str(exc))


if __name__ == '__main__':
    main()
