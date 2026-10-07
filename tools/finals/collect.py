"""Collect complete team episodes through the native C++ option/sonar bridge.

Actors receive encoder/candidate arrays only. Engine state supplies terminal reward;
per-dragon decisions retain delayed team credit after own death. No shaping or GAE.
"""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import selectors
import subprocess
import sys
import tempfile
import time

import numpy as np
from unswbc.engine import EngineModule


ROOT = Path(__file__).resolve().parents[2]
SHAPING_NAME = 'heartbreaker-potential-v1'
SHAPING_ALPHA = 0.2
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class Lines:
    def __init__(self, process):
        self.process = process
        self.buffer = bytearray()
        self.selector = selectors.DefaultSelector()
        self.selector.register(process.stdout, selectors.EVENT_READ)

    def read(self, timeout=10):
        deadline = time.monotonic() + timeout
        while b'\n' not in self.buffer:
            remaining = deadline - time.monotonic()
            if remaining <= 0 or not self.selector.select(remaining):
                raise TimeoutError('Native bridge reply timeout')
            data = os.read(self.process.stdout.fileno(), 65536)
            if not data:
                raise RuntimeError(f'Native bridge closed stdout (exit {self.process.poll()})')
            self.buffer.extend(data)
        line, _, rest = self.buffer.partition(b'\n')
        self.buffer = bytearray(rest)
        return line

    def close(self):
        self.selector.close()


def credit(rounds, terminal_round, terminal_result, gamma, potentials=None, alpha=0.0):
    """Discount team rewards; optionally add policy-preserving potential differences.

    ``potentials[r]`` is Phi at the start of protocol round r. The terminal transition
    uses Phi=0, including round-limit and elimination endings. Rewards are then folded
    backward so every living or dead dragon's decisions retain team credit.
    """
    rounds = np.asarray(rounds, dtype=np.int32)
    if terminal_round < 0 or not 0 < gamma <= 1 or np.any(rounds < 0) or np.any(rounds > terminal_round):
        raise ValueError('Invalid discount or decisions after termination')
    if potentials is None:
        returns = terminal_result * np.power(gamma, terminal_round - rounds)
    else:
        potentials = np.asarray(potentials, dtype=np.float64)
        if (potentials.shape != (terminal_round + 1,) or not np.isfinite(potentials).all() or
                np.any(np.abs(potentials) > 1.0 + 1e-8)):
            raise ValueError('Potential timeline must contain one finite value in [-1, 1] per played round')
        if not np.isfinite(alpha) or alpha < 0:
            raise ValueError('Shaping scale must be finite and non-negative')
        rewards = np.empty(terminal_round + 1, dtype=np.float64)
        for rnd in range(terminal_round):
            rewards[rnd] = alpha * (gamma * potentials[rnd + 1] - potentials[rnd])
        rewards[terminal_round] = terminal_result - alpha * potentials[terminal_round]
        returns_by_round = np.empty_like(rewards)
        running = 0.0
        for rnd in range(terminal_round, -1, -1):
            running = rewards[rnd] + gamma * running
            returns_by_round[rnd] = running
        returns = returns_by_round[rounds]
    counts = Counter(rounds.tolist())
    weights = np.array([1.0 / counts[int(r)] for r in rounds], dtype=np.float32)
    return returns.astype(np.float32), weights


def _relative_difference(ours, theirs):
    denominator = ours + theirs
    if denominator == 0:
        return 0.0
    return float(np.clip(2.0 * (ours - theirs) / denominator, -2.0, 2.0))


def _symmetric_scale(ours, theirs):
    if ours > 0 and theirs > 0:
        return 1.0 / max(ours, theirs)
    if ours == 0 and theirs == 0:
        return 1.0
    return 0.0


def heartbreaker_potential(ours, theirs, round_index, map_area):
    """Bounded, score-aligned team potential adapted from the documented proposal.

    Team summaries contain queen length, longest living dragon, total living length,
    queen-alive flag, and distinct head-visited tile count. Normalizing the weighted
    sum keeps Phi in [-1, 1], which makes the fixed shaping scale interpretable.
    """
    if map_area <= 0:
        raise ValueError('Map area must be positive')
    r = float(np.clip(round_index, 0, 500))
    q_us, q_them = float(ours['queen']), float(theirs['queen'])
    m_us, m_them = float(ours['longest']), float(theirs['longest'])
    z_us, z_them = float(ours['total']), float(theirs['total'])
    d_q = _relative_difference(q_us, q_them)
    d_m = _relative_difference(m_us, m_them)
    d_z = _relative_difference(z_us, z_them)
    win = np.tanh(d_q + 0.4 * _symmetric_scale(q_us, q_them) * np.tanh(
        d_m + 0.4 * _symmetric_scale(m_us, m_them) * np.tanh(d_z)))
    length = np.tanh(d_z)
    queen = float(ours['queen_alive']) - float(theirs['queen_alive'])
    kill = np.exp(-z_them / 15.0) - np.exp(-z_us / 15.0)
    c_us, c_them = float(ours['visited']), float(theirs['visited'])
    expansion = np.tanh(0.005 * (c_us - c_them))

    s = r / 500.0
    explored = float(np.clip(max(c_us, c_them) / map_area, 0.0, 1.0))
    weights = {
        'win': 1.5 * s * s,
        'length': 1.0,
        'queen': float(np.clip((500.0 - r) / 125.0, 0.0, 1.0)),
        'kill': 0.8 * (1.0 - s ** 3),
        'expansion': (1.0 - explored) * float(np.clip((75.0 - r) / 50.0, 0.0, 1.0)),
    }
    terms = {'win': win, 'length': length, 'queen': queen, 'kill': kill, 'expansion': expansion}
    scale = sum(weights.values())
    if scale <= 0:
        return 0.0
    return float(np.clip(sum(weights[k] * terms[k] for k in terms) / scale, -1.0, 1.0))


def potentials_from_frame(frame, seat, terminal_round):
    """Compute one privileged training potential per pre-action team-round snapshot."""
    if seat not in ('A', 'B') or frame['last_round'] != terminal_round:
        raise ValueError('Replay seat or terminal-round metadata mismatch')
    rounds = frame['rounds']
    if len(rounds) <= terminal_round:
        raise ValueError('Replay is missing a pre-terminal round snapshot')
    initial = rounds[0]
    queens = {}
    for team in ('A', 'B'):
        ids = [dragon for dragon, (owner, body) in initial.items() if owner == team and body]
        if not ids:
            raise ValueError(f'Cannot identify initial queen for team {team}')
        queens[team] = min(ids)

    visited = {'A': set(), 'B': set()}
    potentials = []
    for rnd in range(terminal_round + 1):
        state = rounds[rnd]
        stats = {team: dict(queen=0, longest=0, total=0, queen_alive=False, visited=0)
                 for team in ('A', 'B')}
        for dragon, (team, body) in state.items():
            if not body:
                continue
            visited[team].add(tuple(body[0]))
            length = len(body)
            stats[team]['total'] += length
            stats[team]['longest'] = max(stats[team]['longest'], length)
            if dragon == queens[team]:
                stats[team]['queen'] = length
                stats[team]['queen_alive'] = True
        for team in ('A', 'B'):
            stats[team]['visited'] = len(visited[team])
        other = 'B' if seat == 'A' else 'A'
        potentials.append(heartbreaker_potential(stats[seat], stats[other], rnd,
                                                  frame['W'] * frame['H']))
    return np.asarray(potentials, dtype=np.float64)


def replay_potentials(replay, seat, terminal_round, expected_winner):
    """Decode engine replay snapshots for training-only reward labels."""
    from tools.analysis.features.frame import decode

    with tempfile.TemporaryDirectory(prefix='finals-reward-') as temp_dir:
        path = Path(temp_dir) / 'episode.replay'
        path.write_bytes(replay)
        frame = decode(path)
    winner = 'draw' if expected_winner is None else expected_winner
    if frame['winner'] != winner:
        raise ValueError('Replay winner differs from engine result')
    return potentials_from_frame(frame, seat, terminal_round)


def episode(bridge, opponent, board, seed, seat='A', action_actor=None, sonar_actor=None,
            gamma=0.997, capture=True):
    """Run one official episode.

    ``capture=False`` keeps the replay-backed reward validation and summary but skips
    materializing the training tensors. Evaluation never consumes those tensors, so
    this avoids a substantial allocation/copy path without changing the game.
    """
    engine = EngineModule()
    processes, readers, teams = {}, {}, {}
    rows, faults = [], []
    timing = Counter()
    rng = np.random.default_rng(seed)
    started = time.monotonic()

    def spawn(dragon, raw):
        team = raw.split(b'TEAM ')[1][:1].decode()
        teams[dragon] = team
        executable = bridge if team == seat else opponent
        proc = subprocess.Popen([str(executable)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL)
        processes[dragon] = proc
        readers[dragon] = Lines(proc)
        proc.stdin.write(raw + b'\n')
        proc.stdin.flush()

    def stop(dragon):
        proc = processes.pop(dragon, None)
        reader = readers.pop(dragon, None)
        if reader:
            reader.close()
        if proc:
            if proc.poll() is None:
                proc.kill()
            proc.wait(timeout=5)
            proc.stdin.close()
            proc.stdout.close()

    def died(dragon, rnd, reason):
        stop(dragon)

    def reply(dragon, raw):
        proc = processes[dragon]
        proc.stdin.write(raw + b'\n')
        proc.stdin.flush()
        output = []
        record = None
        begin = time.monotonic()
        try:
            while True:
                line = readers[dragon].read()
                if line.startswith(b'CHOICES '):
                    if teams[dragon] != seat:
                        raise ValueError('Opponent unexpectedly uses collection protocol')
                    encode_start = time.monotonic()
                    data = json.loads(line[len(b'CHOICES '):])
                    x = np.asarray(data['x'], dtype=np.int16)
                    features = np.asarray([c['features'] for c in data['candidates']], dtype=np.float32)
                    if x.shape != (1193,) or not 1 <= len(features) <= 12 or features.shape[1] != 32:
                        raise ValueError('Invalid action feature shape')
                    timing['json_array_seconds'] += time.monotonic() - encode_start
                    inference_start = time.monotonic()
                    choice, logp = (0, 0.0) if action_actor is None else action_actor(x, features, rng)
                    timing['actor_seconds'] += time.monotonic() - inference_start
                    if not 0 <= choice < len(features):
                        raise ValueError('Invalid sampled action')
                    record = dict(id=dragon, round=data['round'], x=x, features=features,
                                  chosen_action_features=features[choice].copy(),
                                  action=choice, action_logp=logp, override=False,
                                  rays=None, sends=None, sonar_logp=None)
                    rows.append(record)
                    proc.stdin.write(f'SELECT {choice}\n'.encode())
                    proc.stdin.flush()
                elif line.startswith(b'PACKETS '):
                    if record is None:
                        raise ValueError('Packets before action proposal')
                    encode_start = time.monotonic()
                    data = json.loads(line[len(b'PACKETS '):])
                    rays = [np.asarray([c['features'] for c in ray], dtype=np.float32) for ray in data['rays']]
                    if len(rays) != 4 or any(not 1 <= len(ray) <= 5 or ray.shape[1] != 32 for ray in rays):
                        raise ValueError('Invalid packet feature shape')
                    timing['json_array_seconds'] += time.monotonic() - encode_start
                    inference_start = time.monotonic()
                    owner = getattr(sonar_actor, '__self__', None)
                    callback_name = getattr(sonar_actor, '__name__', None)
                    conditioned_joint = None
                    if callback_name == 'sample':
                        conditioned_joint = getattr(owner, 'sample_rays_conditioned', None)
                    elif callback_name == 'greedy':
                        conditioned_joint = getattr(owner, 'greedy_rays_conditioned', None)
                    joint = conditioned_joint
                    if joint is None and callback_name == 'sample':
                        joint = getattr(owner, 'sample_rays', None)
                    elif joint is None and callback_name == 'greedy':
                        joint = getattr(owner, 'greedy_rays', None)
                    if sonar_actor is None:
                        selected = [(0, 0.0)] * 4
                    elif joint:
                        if conditioned_joint:
                            selected = joint(record['x'], rays, record['chosen_action_features'], rng)
                        else:
                            selected = joint(record['x'], rays, rng)
                    else:
                        conditioned = getattr(owner, 'sample_conditioned' if callback_name == 'sample' else
                                              'greedy_conditioned' if callback_name == 'greedy' else '', None)
                        if conditioned:
                            selected = [conditioned(record['x'], ray, record['chosen_action_features'], rng)
                                        for ray in rays]
                        else:
                            selected = [sonar_actor(record['x'], ray, rng) for ray in rays]
                    timing['actor_seconds'] += time.monotonic() - inference_start
                    sends = [int(s[0]) for s in selected]
                    if any(not 0 <= s < len(ray) for s, ray in zip(sends, rays)):
                        raise ValueError('Invalid sampled packet')
                    record.update(rays=rays, sends=sends, sonar_logp=[s[1] for s in selected])
                    proc.stdin.write(('SEND ' + ' '.join(map(str, sends)) + '\n').encode())
                    proc.stdin.flush()
                elif line.startswith(b'LOG FC '):
                    if record is None:
                        raise ValueError('Commit before proposal')
                    actual = json.loads(line[len(b'LOG FC '):])
                    record['override'] = actual['override']
                    record['actual'] = actual
                else:
                    output.append(line + b'\n')
                    if line == b'ENDTURN':
                        break
        except Exception as e:
            faults.append(dict(id=dragon, error=type(e).__name__ + ': ' + str(e)))
            # Abort this complete episode; never train on incomplete or faulted games.
            raise
        timing['reply_seconds'] += time.monotonic() - begin
        return b''.join(output)

    try:
        result = engine.run(board.read_bytes(), reply, bot_spawn=spawn, on_death=died, debug=0, seed=seed)
        replay = engine.replay(str(bridge.name if seat == 'A' else opponent.name),
                               str(opponent.name if seat == 'A' else bridge.name))
    finally:
        for dragon in list(processes):
            stop(dragon)
    if faults or any(r['rays'] is None for r in rows):
        raise RuntimeError('Incomplete collection episode')
    reward = 0 if result.winner is None else 1 if result.winner == seat else -1
    # EngineModule.rounds is the final zero-based protocol round label (0..499),
    # while the CLI prints result.rounds + 1 as the number of played rounds.
    decision_rounds = np.asarray([r['round'] for r in rows], dtype=np.int32)
    potentials = replay_potentials(replay, seat, result.rounds, result.winner)
    returns, weights = credit(decision_rounds, result.rounds, reward, gamma,
                              potentials=potentials, alpha=SHAPING_ALPHA)
    terminal_returns, _ = credit(decision_rounds, result.rounds, reward, gamma)
    shaping_returns = returns - terminal_returns
    for row in rows:
        if len(row['actual']['dirs']) > 4:
            raise ValueError('Actual command exceeds recorded path bound')
    # Keep summary diagnostics available for evaluation rollouts, which use
    # capture=False and therefore do not materialize the training mask below.
    action_menu_counts = Counter(len(row['features']) for row in rows)
    arrays = None
    if capture:
        action_features = np.zeros((len(rows), 12, 32), dtype=np.float32)
        action_mask = np.zeros((len(rows), 12), dtype=bool)
        sonar_features = np.zeros((len(rows), 4, 5, 32), dtype=np.float32)
        sonar_mask = np.zeros((len(rows), 4, 5), dtype=bool)
        actual_dirs = np.full((len(rows), 4), -1, dtype=np.int8)
        for i, row in enumerate(rows):
            dirs = row['actual']['dirs']
            actual_dirs[i, :len(dirs)] = dirs
            action_features[i, :len(row['features'])] = row['features']
            action_mask[i, :len(row['features'])] = True
            for ray, feats in enumerate(row['rays']):
                sonar_features[i, ray, :len(feats)] = feats
                sonar_mask[i, ray, :len(feats)] = True
        arrays = dict(x=np.asarray([r['x'] for r in rows]), action_features=action_features,
                      chosen_action_features=np.asarray([r['chosen_action_features'] for r in rows], dtype=np.float32),
                      action_mask=action_mask, action=np.asarray([r['action'] for r in rows]),
                      action_logp=np.asarray([r['action_logp'] for r in rows], dtype=np.float32),
                      sonar_features=sonar_features, sonar_mask=sonar_mask,
                      sonar=np.asarray([r['sends'] for r in rows]),
                      sonar_logp=np.asarray([r['sonar_logp'] for r in rows], dtype=np.float32),
                      actual_act=np.asarray([r['actual']['act'] for r in rows], dtype=np.int8),
                      actual_split=np.asarray([r['actual']['split'] for r in rows], dtype=np.int16),
                      actual_dirs=actual_dirs,
                      actor_valid=np.asarray([not r['override'] for r in rows]), returns=returns,
                      terminal_returns=terminal_returns, shaping_returns=shaping_returns, weight=weights,
                      round=np.asarray([r['round'] for r in rows]), dragon=np.asarray([r['id'] for r in rows]))
    n_team_rounds = len(set(decision_rounds.tolist()))
    mean_by_team_round = lambda values: float(np.sum(weights * values) / max(n_team_rounds, 1))
    summary = dict(map=str(board), map_sha256=hashlib.sha256(board.read_bytes()).hexdigest(), seed=seed, seat=seat,
                   bridge=str(bridge), opponent=str(opponent),
                   result=result.__dict__, terminal_reward=reward, gamma=gamma, terminal_round=result.rounds,
                   shaping=dict(method=SHAPING_NAME, alpha=SHAPING_ALPHA,
                                potential_start=float(potentials[0]),
                                potential_min=float(np.min(potentials)),
                                potential_max=float(np.max(potentials)),
                                mean_policy_return=mean_by_team_round(returns),
                                mean_terminal_return=mean_by_team_round(terminal_returns),
                                mean_shaping_return=mean_by_team_round(shaping_returns)),
                   action_behavior='baseline' if action_actor is None else getattr(action_actor, '__name__', 'actor'),
                   sonar_behavior='baseline' if sonar_actor is None else getattr(sonar_actor, '__name__', 'actor'),
                   decisions=len(rows), overrides=sum(r['override'] for r in rows), faults=faults,
                   action_menu_counts=dict(action_menu_counts),
                   timing=dict(timing), elapsed_seconds=time.monotonic() - started)
    summary['team_reward_timeline'] = [0] * (result.rounds + 1)
    summary['team_reward_timeline'][-1] = reward
    return arrays, summary, replay


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--bridge', type=Path, required=True)
    ap.add_argument('--opponent', type=Path, required=True)
    ap.add_argument('--map', type=Path, required=True)
    ap.add_argument('--seed', type=int, required=True)
    ap.add_argument('--seat', choices=['A', 'B'], default='A')
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    arrays, summary, replay = episode(args.bridge.resolve(), args.opponent.resolve(), args.map.resolve(), args.seed, args.seat)
    np.savez_compressed(args.output / 'episode.npz', **arrays)
    (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    (args.output / 'game.replay').write_bytes(replay)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
