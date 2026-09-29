"""CUDA-backed offline fitted-Q trainer for the Battlecode opening.

This is conservative fitted Q-learning over replay data, not online
environment interaction. It reuses the replay decoder and reward shaping in
``rl_earlygame.py`` but replaces the small linear model with a dueling neural
Q-function. The default network and batch size are suitable for an RTX 3060.

Train with:

  python3 tools/rl_earlygame_gpu.py train \
      --replays public_replays/team-306 \
      --out build/rl-earlygame-gpu --max-games 120

The checkpoint is intended for experiments and training. The JSON policy from
``rl_earlygame.py`` remains the deployment fallback when the tournament
process cannot import PyTorch.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

from rl_earlygame import (  # noqa: E402
    ACTION_NAMES,
    CANDIDATE_ATTRIBUTES,
    context_names,
    context_vector,
    dense_reward,
    legal_actions,
    load_replays,
    replay_paths,
    transition_rows,
    vector,
)


def require_torch():
    try:
        import torch
        import torch.nn as nn
        from torch.utils.data import DataLoader, TensorDataset
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "GPU training needs PyTorch. Install a CUDA build, for example "
            "with: pip install torch --index-url "
            "https://download.pytorch.org/whl/cu128"
        ) from exc
    return torch, nn, DataLoader, TensorDataset


def action_features(row, names):
    context_size = len(names)
    return np.asarray([
        vector(row, action, names)[context_size:]
        for action in ACTION_NAMES
    ], dtype=np.float32)


def prepared_arrays(transitions, names, final_values):
    context_size = len(names)
    action_index = {name: index for index, name in enumerate(ACTION_NAMES)}
    contexts, chosen, chosen_indices, current_all, current_masks = [], [], [], [], []
    next_contexts, next_all, next_masks = [], [], []
    rewards, dones, weights = [], [], []
    for row, action, next_row in transitions:
        current = action_features(row, names)
        contexts.append(np.asarray(context_vector(row, names), dtype=np.float32))
        chosen.append(current[action_index[action]])
        chosen_indices.append(action_index[action])
        current_all.append(current)
        current_masks.append(np.asarray([
            candidate in legal_actions(row) for candidate in ACTION_NAMES
        ], dtype=np.bool_))
        if next_row is None:
            next_contexts.append(np.zeros(context_size, dtype=np.float32))
            next_all.append(np.zeros_like(current))
            next_masks.append(np.zeros(len(ACTION_NAMES), dtype=np.bool_))
            dones.append(1.0)
        else:
            next_contexts.append(np.asarray(context_vector(next_row, names), dtype=np.float32))
            next_candidates = action_features(next_row, names)
            next_all.append(next_candidates)
            next_masks.append(np.asarray([
                action in legal_actions(next_row) for action in ACTION_NAMES
            ], dtype=np.bool_))
            dones.append(0.0)
        rewards.append(dense_reward(
            row, action, next_row, final_values[row["game"], row["side"]]
        ))
        weights.append(2.0 if float(row.get("round", 0)) < 100 else 1.0)
    return {
        "context": np.asarray(contexts, dtype=np.float32),
        "chosen": np.asarray(chosen, dtype=np.float32),
        "chosen_index": np.asarray(chosen_indices, dtype=np.int64),
        "current_all": np.asarray(current_all, dtype=np.float32),
        "current_mask": np.asarray(current_masks, dtype=np.bool_),
        "next_context": np.asarray(next_contexts, dtype=np.float32),
        "next_all": np.asarray(next_all, dtype=np.float32),
        "next_mask": np.asarray(next_masks, dtype=np.bool_),
        "reward": np.asarray(rewards, dtype=np.float32),
        "done": np.asarray(dones, dtype=np.float32),
        "weight": np.asarray(weights, dtype=np.float32),
    }


def make_network(torch, nn, context_size, action_size, hidden):
    class DuelingQ(nn.Module):
        def __init__(self):
            super().__init__()
            self.state = nn.Sequential(
                nn.Linear(context_size, hidden),
                nn.LayerNorm(hidden),
                nn.GELU(),
                nn.Linear(hidden, hidden),
                nn.GELU(),
            )
            self.value = nn.Sequential(
                nn.Linear(hidden, hidden // 2), nn.GELU(), nn.Linear(hidden // 2, 1)
            )
            self.advantage = nn.Sequential(
                nn.Linear(hidden + action_size, hidden),
                nn.GELU(),
                nn.Linear(hidden, hidden // 2),
                nn.GELU(),
                nn.Linear(hidden // 2, 1),
            )

        def forward(self, context, action):
            single = action.dim() == 2
            if single:
                action = action.unsqueeze(1)
            h = self.state(context)
            count = action.shape[1]
            h = h.unsqueeze(1).expand(-1, count, -1)
            advantages = self.advantage(torch.cat([h, action], dim=-1)).squeeze(-1)
            value = self.value(self.state(context)).squeeze(-1).unsqueeze(1)
            q = value + advantages - advantages.mean(dim=1, keepdim=True)
            return q[:, 0] if single else q

    return DuelingQ()


def loader_for(torch, DataLoader, TensorDataset, arrays, batch_size, shuffle):
    tensors = (
        torch.from_numpy(arrays["context"]),
        torch.from_numpy(arrays["chosen"]),
        torch.from_numpy(arrays["current_all"]),
        torch.from_numpy(arrays["current_mask"]),
        torch.from_numpy(arrays["next_context"]),
        torch.from_numpy(arrays["next_all"]),
        torch.from_numpy(arrays["next_mask"]),
        torch.from_numpy(arrays["reward"]),
        torch.from_numpy(arrays["done"]),
        torch.from_numpy(arrays["weight"]),
    )
    return DataLoader(
        TensorDataset(*tensors), batch_size=batch_size, shuffle=shuffle,
        num_workers=0, pin_memory=True,
    )


def split_games(frame, seed):
    games = sorted(frame.game.unique())
    rng = np.random.default_rng(seed)
    rng.shuffle(games)
    train_count = max(1, int(len(games) * 0.70))
    val_count = max(1, int(len(games) * 0.15)) if len(games) >= 3 else 0
    split = {
        "train": list(games[:train_count]),
        "validation": list(games[train_count:train_count + val_count]),
        "test": list(games[train_count + val_count:]),
    }
    if not split["test"]:
        split["test"] = split["validation"]
    return split


def train_network(args):
    torch, nn, DataLoader, TensorDataset = require_torch()
    if args.device == "cuda" and not torch.cuda.is_available():
        raise SystemExit("--device cuda was requested but CUDA is unavailable")
    device = torch.device(
        "cuda" if args.device == "auto" and torch.cuda.is_available() else
        args.device if args.device != "auto" else "cpu"
    )
    if device.type == "cuda":
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        print("CUDA", torch.cuda.get_device_name(0), flush=True)
    else:
        print("WARNING: running the GPU trainer on CPU", flush=True)

    paths = replay_paths(args.replays)
    if not paths:
        raise SystemExit("No replay files found")
    frame, manifest = load_replays(
        paths, args.sides, args.max_games, args.max_round, args.keep_every
    )
    names = context_names(frame)
    final_values = {
        (entry["game"], entry["side"]): (1.0 if entry["winner"] == entry["side"] else
                                           -1.0 if entry["winner"] in ("A", "B") else 0.0)
        for entry in manifest
    }
    split = split_games(frame, args.seed)
    train_transitions = transition_rows(
        frame[frame.game.isin(split["train"])], names, args.max_rows, args.seed
    )
    val_transitions = transition_rows(
        frame[frame.game.isin(split["validation"])], names, args.max_test_rows, args.seed
    )
    test_transitions = transition_rows(
        frame[frame.game.isin(split["test"])], names, args.max_test_rows, args.seed
    )
    if len(train_transitions) < 32:
        raise SystemExit("Too few transitions; add replay files or raise --max-round")
    print("transitions", len(train_transitions), "validation", len(val_transitions),
          "test", len(test_transitions), flush=True)

    arrays = prepared_arrays(train_transitions, names, final_values)
    val_arrays = prepared_arrays(val_transitions, names, final_values) if val_transitions else None
    test_arrays = prepared_arrays(test_transitions, names, final_values) if test_transitions else None
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "splits.json").write_text(json.dumps(split, indent=2) + "\n")
    (out / "replay_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    action_size = len(ACTION_NAMES) + len(CANDIDATE_ATTRIBUTES) + 1
    model = make_network(torch, nn, len(names), action_size, args.hidden).to(device)
    target = make_network(torch, nn, len(names), action_size, args.hidden).to(device)
    target.load_state_dict(model.state_dict())
    target.eval()
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay
    )
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")
    train_loader = loader_for(
        torch, DataLoader, TensorDataset, arrays, args.batch_size, True
    )
    amp_enabled = device.type == "cuda"
    step = 0
    history = []
    started = time.time()
    for epoch in range(args.epochs):
        model.train()
        totals = Counter()
        batches = 0
        for batch in train_loader:
            (context, chosen, current_all, current_mask, next_context, next_all,
             next_mask, reward, done, weight) = [
                 item.to(device, non_blocking=True) for item in batch
             ]
            optimizer.zero_grad(set_to_none=True)
            with torch.amp.autocast(device_type="cuda", enabled=amp_enabled):
                q_chosen = model(context, chosen)
                with torch.no_grad():
                    online_next = model(next_context, next_all)
                    online_next = online_next.masked_fill(~next_mask, -1e9)
                    next_index = online_next.argmax(dim=1)
                    target_next = target(next_context, next_all)
                    next_q = target_next.gather(1, next_index[:, None]).squeeze(1)
                    target_q = reward + args.gamma * (1.0 - done) * next_q
                td = torch.nn.functional.smooth_l1_loss(
                    q_chosen, target_q, reduction="none"
                )
                td_loss = (td * weight).mean()
                # Conservative-Q regularization over the fixed action menu.
                # Runtime legality still removes kelp actions; the reward
                # shaping makes their learned score unattractive as well.
                q_all = model(context, current_all).masked_fill(~current_mask, -1e9)
                cql_loss = (
                    torch.logsumexp(q_all / args.cql_temperature, dim=1)
                    * args.cql_temperature - q_chosen
                ).mean()
                loss = td_loss + args.cql_alpha * cql_loss
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip)
            scaler.step(optimizer)
            scaler.update()
            step += 1
            if step % args.target_update == 0:
                target.load_state_dict(model.state_dict())
            totals["loss"] += float(loss.detach().cpu())
            totals["td_loss"] += float(td_loss.detach().cpu())
            totals["cql_loss"] += float(cql_loss.detach().cpu())
            batches += 1
        row = {
            "epoch": epoch + 1,
            "loss": totals["loss"] / max(1, batches),
            "td_loss": totals["td_loss"] / max(1, batches),
            "cql_loss": totals["cql_loss"] / max(1, batches),
            "seconds": time.time() - started,
        }
        history.append(row)
        print(json.dumps(row), flush=True)

    def evaluate_arrays(eval_arrays):
        if eval_arrays is None or not len(eval_arrays["context"]):
            return {"rows": 0}
        model.eval()
        with torch.no_grad():
            contexts = torch.from_numpy(eval_arrays["context"]).to(device)
            all_actions = torch.from_numpy(eval_arrays["current_all"]).to(device)
            mask = torch.from_numpy(eval_arrays["current_mask"]).to(device)
            q = model(contexts, all_actions).masked_fill(~mask, -1e9).cpu().numpy()
        best = q.argmax(axis=1)
        selected = eval_arrays["chosen_index"]
        return {
            "rows": int(len(best)),
            "action_match": float(np.mean(best == selected)),
            "mean_best_q": float(q[np.arange(len(q)), best].mean()),
        }

    metadata = {
        "kind": "offline_cql_dueling_q",
        "device": str(device),
        "cuda_name": torch.cuda.get_device_name(0) if device.type == "cuda" else None,
        "games": int(frame.game.nunique()),
        "rows": int(len(frame)),
        "train_transitions": len(train_transitions),
        "validation": evaluate_arrays(val_arrays),
        "test": evaluate_arrays(test_arrays),
        "hyperparameters": {
            "epochs": args.epochs, "batch_size": args.batch_size,
            "hidden": args.hidden, "gamma": args.gamma,
            "learning_rate": args.learning_rate, "weight_decay": args.weight_decay,
            "cql_alpha": args.cql_alpha, "target_update": args.target_update,
            "max_round": args.max_round, "keep_every": args.keep_every,
        },
        "action_names": list(ACTION_NAMES),
        "candidate_attributes": list(CANDIDATE_ATTRIBUTES),
        "context_features": list(names),
        "history": history,
        "action_counts": dict(Counter(action for _, action, _ in train_transitions)),
    }
    checkpoint = {
        "state_dict": model.state_dict(),
        "context_features": names,
        "actions": list(ACTION_NAMES),
        "candidate_attributes": list(CANDIDATE_ATTRIBUTES),
        "hidden": args.hidden,
        "metadata": metadata,
    }
    torch.save(checkpoint, out / "model.pt")
    model.eval()
    traced = torch.jit.trace(
        model,
        (torch.zeros(1, len(names), device=device),
         torch.zeros(1, len(ACTION_NAMES), action_size, device=device)),
    )
    traced.save(str(out / "model.ts"))
    (out / "training_summary.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps({"model": str(out / "model.pt"), "summary": metadata}, indent=2), flush=True)


def recommend(args):
    torch, nn, _DataLoader, _TensorDataset = require_torch()
    checkpoint = torch.load(args.model, map_location="cpu", weights_only=False)
    names = checkpoint["context_features"]
    action_size = len(ACTION_NAMES) + len(CANDIDATE_ATTRIBUTES) + 1
    model = make_network(torch, nn, len(names), action_size, checkpoint["hidden"])
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    state = json.loads(sys.stdin.read() if args.state == "-" else Path(args.state).read_text())
    context = torch.from_numpy(np.asarray([context_vector(state, names)], dtype=np.float32))
    candidates = torch.from_numpy(action_features(state, names)[None, ...])
    with torch.no_grad():
        scores = model(context, candidates)[0].tolist()
    allowed = set(legal_actions(state))
    ranking = sorted(
        ((action, float(score)) for action, score in zip(ACTION_NAMES, scores)
         if action in allowed),
        key=lambda item: item[1], reverse=True,
    )
    print(json.dumps({"action": ranking[0][0], "ranking": [
        {"action": action, "q": score} for action, score in ranking
    ]}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    train = sub.add_parser("train")
    train.add_argument("--replays", nargs="+", required=True)
    train.add_argument("--sides", nargs="+", choices=("A", "B"), default=("A", "B"))
    train.add_argument("--out", type=Path, default=ROOT / "build" / "rl-earlygame-gpu")
    train.add_argument("--device", choices=("auto", "cuda", "cpu"), default="auto")
    train.add_argument("--max-games", type=int, default=120)
    train.add_argument("--max-round", type=int, default=250)
    train.add_argument("--keep-every", type=int, default=1)
    train.add_argument("--max-rows", type=int, default=250000)
    train.add_argument("--max-test-rows", type=int, default=50000)
    train.add_argument("--epochs", type=int, default=12)
    train.add_argument("--batch-size", type=int, default=2048)
    train.add_argument("--hidden", type=int, default=256)
    train.add_argument("--learning-rate", type=float, default=2e-4)
    train.add_argument("--weight-decay", type=float, default=1e-5)
    train.add_argument("--gamma", type=float, default=0.98)
    train.add_argument("--cql-alpha", type=float, default=0.10)
    train.add_argument("--cql-temperature", type=float, default=1.0)
    train.add_argument("--target-update", type=int, default=500)
    train.add_argument("--grad-clip", type=float, default=5.0)
    train.add_argument("--seed", type=int, default=20260929)
    train.set_defaults(func=train_network)
    recommend_parser = sub.add_parser("recommend")
    recommend_parser.add_argument("--model", required=True, type=Path)
    recommend_parser.add_argument("--state", required=True, help="JSON row, or - for stdin")
    recommend_parser.set_defaults(func=recommend)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
