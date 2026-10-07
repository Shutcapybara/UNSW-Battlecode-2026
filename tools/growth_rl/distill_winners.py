"""Fine-tune a growth_rl actor on the winning side's supported actions."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from .data import extract
from .evaluate import package
from .policy import ACTIONS, action_mask
from .ppo import export_policy, from_policy, normalized_row, validate_export


def _arrays(records, split, *, root, features, mean, scale, cache, seed_start, train_seed_count):
    rows, actions, masks, weights, groups, opponents = [], [], [], [], [], []
    counts = dict(games=0, winning_games=0, draws=0, winner_rows=0, supported_rows=0,
                  masked_rows=0, unsupported_rows=0)
    for record in records:
        in_train = seed_start <= int(record['seed']) < seed_start + train_seed_count
        if (split == 'train') != in_train:
            continue
        counts['games'] += 1
        if counts['games'] % 32 == 0:
            print(json.dumps(dict(stage='extract', split=split, games=counts['games']),
                             separators=(',', ':')), flush=True)
        replay = Path(record['replay'])
        if not replay.is_absolute():
            replay = root / replay
        game = extract(replay, cache)
        winner = game['result']['winner']
        if winner is None:
            counts['draws'] += 1
            continue
        side_rows = [row for row in game['rows'] if row['side'] == winner]
        counts['winning_games'] += 1
        counts['winner_rows'] += len(side_rows)
        kept = []
        for row in side_rows:
            action = row.get('action')
            if action is None or not isinstance(action, (int, np.integer)) or not 0 <= int(action) < len(ACTIONS):
                counts['unsupported_rows'] += 1
                continue
            mask = action_mask(row)
            if not mask[int(action)]:
                counts['masked_rows'] += 1
                continue
            kept.append((normalized_row(row, features, mean, scale), int(action), mask))
        if not kept:
            continue
        counts['supported_rows'] += len(kept)
        per_row_weight = 1.0 / len(kept)
        group = record['game_sha256']
        for x, action, mask in kept:
            rows.append(x)
            actions.append(action)
            masks.append(mask)
            weights.append(per_row_weight)
            groups.append(group)
            opponents.append(record['opponent'])
    if not rows:
        raise ValueError(f'no supported winning actions in {split} data')
    weights = np.asarray(weights, dtype=np.float32)
    weights /= weights.mean()
    return dict(x=np.stack(rows).astype(np.float32), action=np.asarray(actions, np.int64),
                mask=np.stack(masks).astype(bool), weight=weights, groups=np.asarray(groups),
                opponents=np.asarray(opponents), counts=counts)


def _metrics(actor, base, data, device):
    x = torch.as_tensor(data['x'], dtype=torch.float32, device=device)
    mask = torch.as_tensor(data['mask'], dtype=torch.bool, device=device)
    action = torch.as_tensor(data['action'], dtype=torch.long, device=device)
    weight = torch.as_tensor(data['weight'], dtype=torch.float32, device=device)
    with torch.no_grad():
        logits = actor(x).masked_fill(~mask, -1e9)
        base_logits = base(x).masked_fill(~mask, -1e9)
        ce = F.cross_entropy(logits, action, reduction='none')
        correct = (logits.argmax(-1) == action).float()
    denominator = weight.sum().item()
    return dict(samples=len(data['action']), games=len(set(data['groups'])),
                nll=float((ce * weight).sum().item() / denominator),
                action_match=float((correct * weight).sum().item() / denominator))


def distill(args):
    root = Path(__file__).resolve().parents[2]
    records_path = Path(args.records).resolve()
    out = Path(args.out)
    if not out.is_absolute():
        out = root / out
    out = out.resolve()
    policy_path = Path(args.init_policy).resolve()
    payload = json.loads(policy_path.read_text(encoding='utf-8'))
    if payload.get('kind') not in ('growth_awr', 'growth_ppo'):
        raise ValueError('--init-policy must be a neural growth_awr or growth_ppo artifact')
    hidden = len(payload['layers'][0]['bias'])
    actor, features, mean, scale, _ = from_policy(str(policy_path), allow_random=False,
        hidden=hidden, seed=args.seed)
    device = torch.device(args.device)
    torch.manual_seed(args.seed)
    torch.set_num_threads(args.threads)
    actor.to(device)
    base = copy.deepcopy(actor).eval()
    for parameter in base.parameters():
        parameter.requires_grad_(False)
    records = [json.loads(line) for line in records_path.read_text(encoding='utf-8').splitlines() if line.strip()]
    cache = out / 'cache'
    train = _arrays(records, 'train', root=root, features=features, mean=mean, scale=scale,
                    cache=cache, seed_start=args.seed_start, train_seed_count=args.train_seed_count)
    validation = _arrays(records, 'validation', root=root, features=features, mean=mean, scale=scale,
                         cache=cache, seed_start=args.seed_start, train_seed_count=args.train_seed_count)
    initial = _metrics(actor, base, validation, device)
    x = torch.as_tensor(train['x'], dtype=torch.float32, device=device)
    mask = torch.as_tensor(train['mask'], dtype=torch.bool, device=device)
    actions = torch.as_tensor(train['action'], dtype=torch.long, device=device)
    weights = torch.as_tensor(train['weight'], dtype=torch.float32, device=device)
    optimizer = torch.optim.AdamW(actor.parameters(), lr=args.learning_rate)
    best_nll, best_state, best_epoch, stale, history = initial['nll'], copy.deepcopy(actor.state_dict()), 0, 0, []
    rng = np.random.default_rng(args.seed)
    for epoch in range(args.epochs):
        actor.train()
        order = rng.permutation(len(train['action']))
        for start in range(0, len(order), args.minibatch):
            ids = torch.as_tensor(order[start:start + args.minibatch], dtype=torch.long, device=device)
            logits = actor(x[ids]).masked_fill(~mask[ids], -1e9)
            with torch.no_grad():
                base_logits = base(x[ids]).masked_fill(~mask[ids], -1e9)
            logp = torch.log_softmax(logits, dim=-1)
            base_logp = torch.log_softmax(base_logits, dim=-1)
            per_row_ce = F.cross_entropy(logits, actions[ids], reduction='none')
            kl = (logp.exp() * (logp - base_logp)).sum(-1)
            batch_weights = weights[ids]
            loss = ((per_row_ce + args.kl_coef * kl) * batch_weights).sum() / batch_weights.sum()
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            nn.utils.clip_grad_norm_(actor.parameters(), 0.5)
            optimizer.step()
        actor.eval()
        measured = _metrics(actor, base, validation, device)
        record = dict(epoch=epoch + 1, train_games=train['counts']['winning_games'],
                      train_samples=len(train['action']), **{f'validation_{k}': v for k, v in measured.items()})
        history.append(record)
        print(json.dumps(record, separators=(',', ':')), flush=True)
        if measured['nll'] < best_nll - args.min_delta:
            best_nll, best_state, best_epoch, stale = measured['nll'], copy.deepcopy(actor.state_dict()), epoch + 1, 0
        else:
            stale += 1
        if stale >= args.patience:
            break
    actor.load_state_dict(best_state)
    actor.eval()
    out.mkdir(parents=True, exist_ok=True)
    base_update = int(payload.get('update', 0))
    metadata = dict(method='winner_action_imitation', source_policy=str(policy_path),
                    source_policy_sha256=hashlib.sha256(policy_path.read_bytes()).hexdigest(),
                    source_update=base_update, records=str(records_path),
                    train_seed_start=args.seed_start, train_seed_count=args.train_seed_count,
                    validation_seed_start=args.seed_start + args.train_seed_count,
                    train_counts=train['counts'], validation_counts=validation['counts'])
    exported = export_policy(actor, features, mean, scale, update_ix=base_update, metadata=metadata)
    validate_export(actor, exported, list(train['x'][:32]))
    from .data import atomic_json
    atomic_json(out / 'policy.json', exported)
    package(out / 'policy.json', out / 'bot')
    final = _metrics(actor, base, validation, device)
    summary = dict(kind='winner_action_imitation', input_records=str(records_path),
                   training= train['counts'], validation=validation['counts'],
                   initial_validation=initial, final_validation=final, best_epoch=best_epoch,
                   epochs_run=len(history), history=history, settings=dict(
                       learning_rate=args.learning_rate, minibatch=args.minibatch,
                       kl_coef=args.kl_coef, patience=args.patience, seed=args.seed),
                   policy=str(out / 'policy.json'))
    atomic_json(out / 'summary.json', summary)
    torch.save(dict(actor=actor.state_dict(), features=features, mean=mean, scale=scale,
                    hidden=hidden, summary=summary), out / 'model.pt')
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--records', required=True, help='records.jsonl from collect_winner_games.py')
    parser.add_argument('--init-policy', required=True, help='neural policy to fine-tune')
    parser.add_argument('--out', default='build/growth_rl/ppo/winner-distillation')
    parser.add_argument('--seed-start', type=int, required=True)
    parser.add_argument('--train-seed-count', type=int, required=True)
    parser.add_argument('--device', default='cpu')
    parser.add_argument('--threads', type=int, default=1)
    parser.add_argument('--seed', type=int, default=1901)
    parser.add_argument('--epochs', type=int, default=30)
    parser.add_argument('--minibatch', type=int, default=512)
    parser.add_argument('--learning-rate', type=float, default=0.00005)
    parser.add_argument('--kl-coef', type=float, default=0.01)
    parser.add_argument('--patience', type=int, default=6)
    parser.add_argument('--min-delta', type=float, default=0.0001)
    args = parser.parse_args()
    if min(args.epochs, args.minibatch, args.threads, args.patience, args.train_seed_count) < 1:
        parser.error('epochs, minibatch, threads, patience and train-seed-count must be positive')
    try:
        summary = distill(args)
        print(json.dumps({key: summary[key] for key in
                          ('training', 'validation', 'initial_validation', 'final_validation',
                           'best_epoch', 'epochs_run', 'policy')}, separators=(',', ':')), flush=True)
    except (ValueError, RuntimeError, OSError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
