"""Monte-Carlo advantage-weighted regression on replay team outcomes.

The critic predicts retained growth over 10/25 rounds and to r100, plus a
separate final-outcome head. The actor maximises advantage-weighted likelihood
of complete recorded actions. No invented counterfactual rewards or partial
sprint labels; closed-loop games are required to establish improvement.
"""
import copy
import json
from pathlib import Path
import random
import time

import numpy as np
import torch
from torch import nn

from .behavior import (action_coverage_report, cohort_label,
                       phase_behavior_records, phase_behavior_summary)
from .data import atomic_json, targets
from .policy import ACTIONS, Policy, action_mask


def network(inputs, outputs, hidden):
    return nn.Sequential(nn.Linear(inputs, hidden), nn.ReLU(),
                         nn.Linear(hidden, hidden), nn.ReLU(), nn.Linear(hidden, outputs))


def export(model, names, mean, scale, path):
    payload = dict(version=1, kind='growth_awr', actions=list(ACTIONS), features=names,
                   mean=mean.tolist(), scale=scale.tolist(), layers=[
                       dict(weight=layer.weight.detach().cpu().tolist(), bias=layer.bias.detach().cpu().tolist())
                       for layer in model if isinstance(layer, nn.Linear)])
    atomic_json(path, payload)
    return payload


def arrays(games, names, population_weight):
    rows, groups, weights = [], [], []
    for game in games:
        for side in 'AB':
            side_rows = [r for r in game['rows'] if r['side'] == side and r['action'] is not None]
            for row in side_rows:
                rows.append(row)
                groups.append(game['sha256'])
                # Each side-game has equal mass, regardless of swarm size.
                weights.append(1 / len(side_rows))
    if not rows:
        raise ValueError('No supported replay actions in this split')
    x = np.asarray([[float(r.get(k, 0)) for k in names] for r in rows], np.float32)
    if not np.isfinite(x).all():
        raise ValueError('Non-finite observation features')
    return dict(x=x, y=np.asarray([targets(r, population_weight) for r in rows], np.float32),
                action=np.asarray([r['action'] for r in rows], np.int64),
                mask=np.asarray([action_mask(r) for r in rows], bool),
                weight=np.asarray(weights, np.float32), rows=rows, groups=groups)


def top10_winner_arrays(games, names, *, split='train'):
    """Collect winning actions from ranked top-ten public games in one split.

    This subset trains an exploratory tree opponent only. Locked test games are
    never accepted, and each selected winning side-game has equal total weight.
    """
    if split not in ('train', 'validation'):
        raise ValueError('top-team tree data may use train or validation only')
    rows, groups, weights = [], [], []
    for game in games:
        if game.get('split') != split:
            continue
        metadata = game.get('provenance', {}).get('metadata', {})
        if metadata.get('source') != 'public' or metadata.get('ranked') is not True:
            continue
        winner = game.get('result', {}).get('winner')
        if winner not in ('A', 'B'):
            continue
        rank = metadata.get('rank_' + winner.lower())
        if isinstance(rank, bool):
            continue
        try:
            numeric_rank = float(rank)
        except (TypeError, ValueError):
            continue
        if not np.isfinite(numeric_rank) or not numeric_rank.is_integer() or not 1 <= numeric_rank <= 10:
            continue
        side_rows = [row for row in game['rows']
                     if row['side'] == winner and row['action'] is not None]
        if not side_rows:
            continue
        rows.extend(side_rows)
        groups.extend([game['sha256']] * len(side_rows))
        weights.extend([1 / len(side_rows)] * len(side_rows))
    if not rows:
        return None
    x = np.asarray([[float(row.get(name, 0)) for name in names] for row in rows], np.float32)
    if not np.isfinite(x).all():
        raise ValueError('Non-finite top-team observation features')
    return dict(x=x, action=np.asarray([row['action'] for row in rows], np.int64),
                mask=np.asarray([action_mask(row) for row in rows], bool),
                weight=np.asarray(weights, np.float32), rows=rows, groups=groups)


def _tree_payload(tree, names, mean, scale):
    node_probs = np.full((tree.tree_.node_count, len(ACTIONS)), 1e-5, dtype=np.float64)
    values = tree.tree_.value[:, 0, :]
    values = values / np.maximum(values.sum(axis=1, keepdims=True), 1e-12)
    node_probs[:, tree.classes_] += values
    node_probs /= node_probs.sum(axis=1, keepdims=True)
    payload = dict(version=1, kind='imitation_tree', actions=list(ACTIONS), features=names,
        mean=mean.tolist(), scale=scale.tolist(), tree=dict(
            feature=tree.tree_.feature.tolist(), threshold=tree.tree_.threshold.tolist(),
            left=tree.tree_.children_left.tolist(), right=tree.tree_.children_right.tolist(),
            logits=np.log(node_probs).tolist()))
    return payload, node_probs


def _tree_inputs(data, mean, scale):
    return np.clip((data['x'] - mean) / scale, -10, 10).astype(np.float32)


def _tree_metrics(tree, runtime, data, mean, scale, node_probs):
    x = _tree_inputs(data, mean, scale)
    logits = np.asarray([runtime.logits(row) for row in data['rows']])
    leaves = tree.apply(x)
    expected = np.log(node_probs[leaves])
    if not np.allclose(logits, expected, atol=1e-5):
        raise ValueError('tree export parity failed')
    logits[~data['mask']] = -1e9
    probabilities = np.exp(logits - logits.max(axis=1, keepdims=True))
    probabilities /= probabilities.sum(axis=1, keepdims=True)
    nll = float(np.average(-np.log(np.maximum(
        probabilities[np.arange(len(data['action'])), data['action']], 1e-12)),
        weights=data['weight']))
    return dict(validation_nll=nll,
                action_match=float(np.average(logits.argmax(1) == data['action'], weights=data['weight'])))


def distribution_report(games):
    """One observation per side-game/checkpoint, never per actor row."""
    import pandas as pd
    records = []
    for game in games:
        # A map-held-out test remains opaque throughout iterative validation.
        if game.get('split') == 'test':
            continue
        for side in 'AB':
            meta = game.get('provenance', {}).get('metadata', {})
            origin = meta.get('source', 'unknown')
            rank = meta.get('rank_' + side.lower())
            cohort = cohort_label(meta, side)
            winner = game['result']['winner']
            outcome = 'draw' if winner is None else 'win' if winner == side else 'loss'
            for checkpoint in (10, 25, 50, 75, 100):
                current = game['series'][str(checkpoint)] if str(checkpoint) in game['series'] else game['series'][checkpoint]
                previous = game['series'][str(max(0, checkpoint - 10))] if str(max(0, checkpoint - 10)) in game['series'] else game['series'][max(0, checkpoint - 10)]
                stats, before = current[side], previous[side]
                records.append(dict(game=game['sha256'], map=game['map'], side=side, outcome=outcome, cohort=cohort,
                                    team_id=meta.get('team_' + side.lower()),
                                    submission=meta.get('submission_' + side.lower()), rank_snapshot=rank,
                                    ranked_game=meta.get('ranked'), fetched_at=meta.get('fetched_at'),
                                    split=game['split'], checkpoint=checkpoint,
                                    ended_before_checkpoint=game['result']['rounds'] < checkpoint,
                                    **stats, pearls_per_round_10=(stats['pearls'] - before['pearls']) / 10,
                                    pearls_per_dragon_turn=stats['pearls'] / max(1, stats['dragon_turns']),
                                    corpse_pearl_share=stats['pearls_corpse'] / max(1, stats['pearls'])))
    frame = pd.DataFrame(records)
    quantiles = []
    if len(frame):
        # Pandas treats a tuple as one composite column label. Pass a list to
        # request grouping across these five columns.
        group_keys = ['cohort', 'submission', 'rank_snapshot', 'map', 'checkpoint']
        for (cohort, submission, rank_snapshot, map_name, checkpoint), group in frame.groupby(group_keys, dropna=False):
            for outcome in ('all', 'win', 'loss', 'draw'):
                part = group if outcome == 'all' else group[group.outcome == outcome]
                if not len(part):
                    continue
                for metric in ('units', 'total', 'longest', 'pearls', 'pearls_bed', 'pearls_corpse',
                               'pearls_init', 'pearls_unknown', 'corpse_pearl_share', 'deaths',
                               'deaths_wall', 'deaths_self', 'deaths_body', 'deaths_h2h',
                               'deaths_no_action', 'splits', 'pearls_per_round_10', 'pearls_per_dragon_turn'):
                    values = part[metric]
                    timestamps = part['fetched_at'].dropna() if 'fetched_at' in part else []
                    quantiles.append(dict(cohort=cohort,
                                          submission=None if pd.isna(submission) else submission,
                                          rank_snapshot=None if pd.isna(rank_snapshot) else int(rank_snapshot),
                                          fetched_from=min(timestamps) if len(timestamps) else None,
                                          fetched_to=max(timestamps) if len(timestamps) else None,
                                          map=str(map_name), checkpoint=int(checkpoint), outcome=outcome,
                                          metric=metric, n=len(values), mean=float(values.mean()),
                                          std=float(values.std(ddof=0)),
                                          **{f'p{q}': float(values.quantile(q / 100)) for q in (10, 25, 50, 75, 90)}))
    return frame, quantiles


def cohort_summary(frame):
    """Aggregate checkpoint distributions by source cohort and game outcome.

    ``distribution_report`` has already held out locked test games. Filter again
    here so this helper also remains safe when called independently. Each row is
    a side-game observation; the reported spread is descriptive, not a causal or
    independent-game confidence interval.
    """
    frame = frame[frame['split'] != 'test']
    if frame.empty:
        return []

    summaries = []
    grouped = frame.groupby(['cohort', 'checkpoint'], dropna=False)
    base_metrics = ('units', 'total', 'longest', 'pearls', 'pearls_per_round_10',
                    'pearls_per_dragon_turn', 'corpse_pearl_share')
    for (cohort, checkpoint), group in grouped:
        for outcome in ('all', 'win', 'loss', 'draw'):
            part = group if outcome == 'all' else group[group['outcome'] == outcome]
            if part.empty:
                continue
            record = dict(cohort=str(cohort), checkpoint=int(checkpoint), outcome=outcome,
                          side_games=int(len(part)), games=int(part['game'].nunique()),
                          teams=int(part['team_id'].nunique()),
                          submission_identity_fraction=float(part['submission'].notna().mean()),
                          rank_snapshot_fraction=float(part['rank_snapshot'].notna().mean()),
                          ended_early=int(part['ended_before_checkpoint'].sum()))
            metrics = {name: part[name].astype(float) for name in base_metrics}
            turns = part['dragon_turns'].astype(float).clip(lower=1)
            for cause in ('wall', 'self', 'body', 'h2h'):
                metrics[f'deaths_{cause}_per_1000_dragon_turns'] = 1000 * part[f'deaths_{cause}'].astype(float) / turns
            for name, values in metrics.items():
                record[f'{name}_mean'] = float(values.mean())
                record[f'{name}_std'] = float(values.std(ddof=0))
                for q in (10, 25, 50, 75, 90):
                    record[f'{name}_p{q}'] = float(values.quantile(q / 100))
            summaries.append(record)
    return summaries


def win_associations(games):
    """Held-out prediction, explicitly conditional on reaching each checkpoint.

    This measures association, not the causal effect of manufacturing length.
    Final win is never a policy input or an actor reward.
    """
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score, brier_score_loss
    report = {}
    for checkpoint in (25, 50, 75, 100):
        parts = {s: ([], []) for s in ('train', 'validation')}
        for game in games:
            if game['split'] not in parts or game['result']['rounds'] <= checkpoint or game['result']['winner'] is None:
                continue
            series = game['series']
            state = series.get(str(checkpoint)) or series[checkpoint]
            for side, other in (('A', 'B'), ('B', 'A')):
                parts[game['split']][0].append([np.log1p(state[side][m]) - np.log1p(state[other][m]) for m in ('units', 'total', 'longest')])
                parts[game['split']][1].append(int(game['result']['winner'] == side))
        x, y = parts['train']
        vx, vy = parts['validation']
        if len(x) < 20 or len(vx) < 10 or len(set(y)) < 2 or len(set(vy)) < 2:
            report[checkpoint] = dict(status='insufficient_games', train_games=len(x) // 2, validation_games=len(vx) // 2)
            continue
        model = LogisticRegression(C=0.1).fit(x, y)
        probabilities = model.predict_proba(vx)[:, 1]
        report[checkpoint] = dict(train_games=len(x) // 2, validation_games=len(vx) // 2,
            auc=float(roc_auc_score(vy, probabilities)), brier=float(brier_score_loss(vy, probabilities)),
            constant_brier=float(brier_score_loss(vy, np.full(len(vy), np.mean(y)))),
            coefficients=dict(zip(('units', 'total', 'longest'), model.coef_[0].tolist())),
            interpretation='predictive association conditional on survival; not a causal growth reward')
    return report


def fit(games, out, *, device='cuda', hidden=64, batch_size=2048, epochs=12,
        seed=1701, population_weight=0.25, temperature=0.5, learning_rate=0.0003,
        final_test=False, resume=None):
    if device == 'cuda' and not torch.cuda.is_available():
        raise RuntimeError('CUDA required, but unavailable; refusing silent CPU fallback')
    if not (epochs > 0 and batch_size > 0 and temperature > 0 and hidden > 0):
        raise ValueError('epochs, batch size, temperature and hidden width must be positive')
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.set_num_threads(4)
    splits = {s: [g for g in games if g['split'] == s] for s in ('train', 'validation', 'test')}
    if len(splits['train']) < 2 or len(splits['validation']) < 1:
        raise ValueError('Need at least two training games and one independent validation game; collect more replays')
    # Feature schema is constructed only from training observations.
    names = sorted(set.intersection(*(set(g['features']) for g in splits['train'])))
    train = arrays(splits['train'], names, population_weight)
    val = arrays(splits['validation'], names, population_weight)
    mean = np.average(train['x'], axis=0, weights=train['weight']).astype(np.float32)
    scale = np.sqrt(np.average((train['x'] - mean) ** 2, axis=0, weights=train['weight'])).astype(np.float32)
    scale[scale < 1e-5] = 1

    def tensors(a):
        # CPU-resident corpus and bounded GPU minibatches fit a 12 GB 3060.
        return dict(x=torch.from_numpy(np.clip((a['x'] - mean) / scale, -10, 10)),
                    y=torch.from_numpy(a['y']), action=torch.from_numpy(a['action']),
                    mask=torch.from_numpy(a['mask']), weight=torch.from_numpy(a['weight'] / a['weight'].mean()))

    train_t, val_t = tensors(train), tensors(val)
    actor, critic = network(len(names), len(ACTIONS), hidden).to(device), network(len(names), 4, hidden).to(device)
    # A resumed actor must keep its original normalisation and feature contract.
    if resume:
        prior = torch.load(resume, map_location='cpu', weights_only=False)
        if prior['features'] != names or prior['hidden'] != hidden:
            raise ValueError('resume schema/width mismatch')
        mean, scale = prior['mean'], prior['scale']
        train_t, val_t = tensors(train), tensors(val)
        actor.load_state_dict(prior['actor'])
        critic.load_state_dict(prior['critic'])

    def batches(data, shuffle=False):
        order = torch.randperm(len(data['x'])) if shuffle else torch.arange(len(data['x']))
        for start in range(0, len(order), batch_size):
            ids = order[start:start + batch_size]
            yield {k: v[ids].to(device) for k, v in data.items()}

    def critic_loss(b):
        prediction = critic(b['x'])
        growth = (prediction[:, :3] - b['y'][:, :3]).square().mean(1)
        outcome = nn.functional.binary_cross_entropy_with_logits(prediction[:, 3], b['y'][:, 3], reduction='none')
        return growth + outcome

    history = []
    best, best_state = float('inf'), None
    optimizer = torch.optim.AdamW(critic.parameters(), lr=learning_rate)
    for epoch in range(epochs):
        critic.train()
        for b in batches(train_t, True):
            loss = (critic_loss(b) * b['weight']).mean()
            if not torch.isfinite(loss):
                raise ValueError('non-finite critic loss')
            optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(critic.parameters(), 5)
            optimizer.step()
        critic.eval()
        with torch.no_grad():
            sums = [(float((critic_loss(b) * b['weight']).sum()), float(b['weight'].sum())) for b in batches(val_t)]
        score = sum(v for v, _ in sums) / sum(w for _, w in sums)
        if score < best:
            best, best_state = score, copy.deepcopy(critic.state_dict())
        history.append(dict(stage='critic', epoch=epoch + 1, validation_loss=score))
        print(json.dumps(history[-1]), flush=True)
    critic.load_state_dict(best_state)
    critic.eval()
    # Frozen MC baseline. Final win is an auxiliary prediction, never a hand
    # chosen action bonus. The actor optimises the r100 growth component.
    with torch.no_grad():
        advantages = torch.cat([(b['y'][:, 2] - critic(b['x'])[:, 2]).cpu() for b in batches(train_t)])
    train_t['advantage_weight'] = torch.exp(torch.clamp(advantages / temperature, -3, 3))
    optimizer = torch.optim.AdamW(actor.parameters(), lr=learning_rate)
    best, best_state = float('inf'), None
    for epoch in range(epochs):
        actor.train()
        loss_sum, count = 0.0, 0
        for b in batches(train_t, True):
            logits = actor(b['x']).masked_fill(~b['mask'], -1e9)
            ce = nn.functional.cross_entropy(logits, b['action'], reduction='none')
            loss = (ce * b['weight'] * b['advantage_weight']).mean()
            if not torch.isfinite(loss):
                raise ValueError('non-finite actor loss')
            optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(actor.parameters(), 5)
            optimizer.step()
            loss_sum += float(loss.detach())
            count += 1
        actor.eval()
        with torch.no_grad():
            sums = []
            for b in batches(val_t):
                ce = nn.functional.cross_entropy(actor(b['x']).masked_fill(~b['mask'], -1e9), b['action'], reduction='none')
                sums.append((float((ce * b['weight']).sum()), float(b['weight'].sum())))
        score = sum(v for v, _ in sums) / sum(w for _, w in sums)
        if score < best:
            best, best_state = score, copy.deepcopy(actor.state_dict())
        history.append(dict(stage='actor', epoch=epoch + 1, loss=loss_sum / count, validation_nll=score))
        print(json.dumps(history[-1]), flush=True)
        # Recoverable per-epoch checkpoint; never overwrites a promoted bot.
        torch.save(dict(actor=actor.state_dict(), critic=critic.state_dict(), features=names,
                        mean=mean, scale=scale, hidden=hidden, epoch=epoch + 1), out / 'last.pt')
    actor.load_state_dict(best_state)
    actor.eval()
    payload = export(actor, names, mean, scale, out / 'policy.json')
    # Numerical parity against the actual dependency-free deployable runtime.
    runtime = Policy(payload)
    with torch.no_grad():
        expected = actor(val_t['x'][:8].to(device)).cpu().numpy()
    actual = np.asarray([runtime.logits(row) for row in val['rows'][:8]])
    parity = float(np.max(np.abs(expected - actual)))
    if not np.allclose(expected, actual, atol=2e-4, rtol=2e-4):
        raise ValueError(f'export parity failed: {parity}')

    def metrics(a, data):
        correct, weight_sum, ce_sum, mse_sum, brier_sum = 0., 0., 0., 0., 0.
        with torch.no_grad():
            for b in batches(data):
                logits = actor(b['x']).masked_fill(~b['mask'], -1e9)
                prediction = critic(b['x'])
                w = b['weight']
                correct += float(((logits.argmax(1) == b['action']).float() * w).sum())
                ce_sum += float((nn.functional.cross_entropy(logits, b['action'], reduction='none') * w).sum())
                mse_sum += float(((prediction[:, 2] - b['y'][:, 2]).square() * w).sum())
                brier_sum += float(((prediction[:, 3].sigmoid() - b['y'][:, 3]).square() * w).sum())
                weight_sum += float(w.sum())
        return dict(rows=len(a['x']), games=len(set(a['groups'])), action_match=correct / weight_sum,
                    nll=ce_sum / weight_sum, growth_mse=mse_sum / weight_sum, win_brier=brier_sum / weight_sum,
                    causal_policy_improvement_established=False)

    summary = dict(kind='monte_carlo_advantage_weighted_regression', device=device,
                   gpu=torch.cuda.get_device_name() if device == 'cuda' else None,
                   objective=dict(retained_length_weight=1, population_weight=population_weight, horizon=100),
                   validation=metrics(val, val_t), test='locked; use final-test once',
                   parity_max_error=parity, history=history, features=names,
                   settings=dict(hidden=hidden, batch_size=batch_size, epochs=epochs, seed=seed,
                                 temperature=temperature, learning_rate=learning_rate),
                   split_games={s: [g['sha256'] for g in gs] for s, gs in splits.items()},
                   coverage=action_coverage_report(games))
    # Cheap, independent behavioural-replication baseline for the opponent zoo.
    # It is evaluated offline here, but does not bypass the closed-loop gate.
    from sklearn.tree import DecisionTreeClassifier
    tree = DecisionTreeClassifier(max_depth=14, min_samples_leaf=10, random_state=seed)
    tree.fit(train_t['x'].numpy(), train['action'], sample_weight=train['weight'])
    tree_payload, node_probs = _tree_payload(tree, names, mean, scale)
    atomic_json(out / 'tree_policy.json', tree_payload)
    tree_runtime = Policy(tree_payload)
    tree_validation = _tree_metrics(tree, tree_runtime, val, mean, scale, node_probs)
    tree_nll = tree_validation['validation_nll']
    summary['tree_baseline'] = dict(**tree_validation,
        nodes=int(tree.tree_.node_count), kind='unweighted_behavioural_replication')

    # A separate exploratory opponent clones only ranked top-ten winners from
    # training games. It is never selected as the promoted policy from offline
    # metrics; only its closed-loop rollout enters a later collection cycle.
    top10_train = top10_winner_arrays(games, names, split='train')
    top10_val = top10_winner_arrays(games, names, split='validation')
    tree_path = out / 'tree_top10_winners_policy.json'
    minimum_top10_games = 10
    top10_train_games = len(set(top10_train['groups'])) if top10_train else 0
    top10_summary = dict(status='insufficient_training_games', min_train_games=minimum_top10_games,
                         train_games=top10_train_games,
                         train_rows=len(top10_train['action']) if top10_train else 0,
                         validation_games=len(set(top10_val['groups'])) if top10_val else 0,
                         validation_rows=len(top10_val['action']) if top10_val else 0,
                         causal_policy_improvement_established=False)
    if top10_train_games >= minimum_top10_games:
        top10_tree = DecisionTreeClassifier(max_depth=14, min_samples_leaf=10, random_state=seed)
        top10_tree.fit(_tree_inputs(top10_train, mean, scale), top10_train['action'],
                       sample_weight=top10_train['weight'])
        top10_payload, top10_node_probs = _tree_payload(top10_tree, names, mean, scale)
        atomic_json(tree_path, top10_payload)
        top10_summary.update(status='trained_exploratory_zoo_opponent',
                             nodes=int(top10_tree.tree_.node_count),
                             artifact=tree_path.name,
                             training_cohort='public ranked games, winner rank 1-10, train split only')
        if top10_val:
            top10_runtime = Policy(top10_payload)
            top10_summary.update(_tree_metrics(top10_tree, top10_runtime, top10_val,
                                               mean, scale, top10_node_probs))
        else:
            top10_summary['validation_status'] = 'no_held_out_top10_winner_games'
    elif tree_path.exists():
        tree_path.unlink()
    summary['tree_top10_winners'] = top10_summary
    # Both are reviewable artifacts. Offline selection is merely a candidate
    # proposal; promotion still needs independent paired games.
    atomic_json(out / 'neural_policy.json', payload)
    summary['proposed_policy'] = 'neural'
    if tree_nll < summary['validation']['nll']:
        atomic_json(out / 'policy.json', tree_payload)
        summary['proposed_policy'] = 'tree_baseline'
    if final_test and splits['test']:
        test = arrays(splits['test'], names, population_weight)
        summary['test'] = metrics(test, tensors(test))
    torch.save(dict(actor=actor.state_dict(), critic=critic.state_dict(), features=names,
                    mean=mean, scale=scale, hidden=hidden, summary=summary), out / 'model.pt')
    atomic_json(out / 'training_summary.json', summary)
    frame, distributions = distribution_report(games)
    frame.to_csv(out / 'checkpoints.csv', index=False)
    atomic_json(out / 'distributions.json', distributions)
    atomic_json(out / 'cohort_summary.json', cohort_summary(frame))
    phase_records = phase_behavior_records(games)
    atomic_json(out / 'phase_behavior.json', phase_records)
    atomic_json(out / 'phase_behavior_summary.json', phase_behavior_summary(phase_records))
    atomic_json(out / 'win_associations.json', win_associations(games))
    return summary
