"""Train a small offline fitted-Q policy for Battlecode's opening.

This is intentionally an offline model, not a claim that replay files alone
solve online RL.  It learns from legal actions in strong replays, bootstraps
through each dragon's next observed state, and uses the final result plus
opening progress/safety shaping as the reward.  The exported model is a
linear Q function and can be scored by :mod:`tools.rl_runtime` with only the
Python standard library.

Examples:

  python3 tools/rl_earlygame.py train \
      --replays public_replays/team-306 \
      --out build/rl-earlygame --max-games 80 --max-round 250

  python3 tools/rl_earlygame.py recommend \
      --model build/rl-earlygame/model.json --state state.json

The replay extractor needs the same dependencies as the existing v4 replay
tools, notably ``pycapnp``.  Training needs numpy, pandas and scikit-learn.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

ROOT = Path(__file__).resolve().parents[1]
FEATURE_TOOL = ROOT / "tools" / "team_recon_claude"
if str(FEATURE_TOOL) not in sys.path:
    sys.path.insert(0, str(FEATURE_TOOL))

try:  # Works both as ``python tools/rl_earlygame.py`` and as an import.
    from rl_runtime import (  # noqa: E402
        ACTION_NAMES,
        CANDIDATE_ATTRIBUTES,
        EarlyGameQPolicy,
    )
except ModuleNotFoundError:  # pragma: no cover - import-form convenience
    from tools.rl_runtime import (  # noqa: E402
        ACTION_NAMES,
        CANDIDATE_ATTRIBUTES,
        EarlyGameQPolicy,
    )


MOVE_ACTIONS = ("F", "R", "B", "L")
NON_FEATURE_COLUMNS = {
    "game", "dragon", "map", "map_name", "winner", "side", "win",
    "outcome", "stage", "game_rounds", "y_family", "y_first", "y_nsteps", "y_seq",
    "y_split", "post_died",
}


def _number(value, default=0.0):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return float(default)
    return value if math.isfinite(value) else float(default)


def _hash(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def replay_paths(values):
    paths = []
    for value in values:
        p = Path(value)
        if p.is_dir():
            paths.extend(sorted(p.glob("*.replay")))
            paths.extend(sorted(p.glob("*.replay.gz")))
        elif p.exists():
            paths.append(p)
        else:
            paths.extend(sorted(Path().glob(value)))
    unique = {p.resolve(): p.resolve() for p in paths}
    return sorted(unique.values(), key=lambda p: p.stem)


def _winner_value(result, side):
    winner = result.get("winner")
    if winner == side:
        return 1.0
    if winner in ("A", "B"):
        return -1.0
    return 0.0


def load_replays(paths, sides, max_games, max_round, keep_every):
    """Decode replay actions into local-observation rows.

    Importing ``features_v4`` is delayed until this function runs so that
    ``recommend`` remains usable on a machine without pycapnp.
    """
    try:
        import features_v4
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Training needs the replay dependencies; install pycapnp and rerun."
        ) from exc

    paths = list(paths)[:max_games] if max_games else list(paths)
    rows = []
    manifest = []
    for index, path in enumerate(paths, 1):
        started = time.time()
        for side in sides:
            try:
                raw_rows, game = features_v4.extract(path, side, path.stem)
            except Exception as exc:  # keep one bad replay from killing a pool
                print("skip", path, side, type(exc).__name__, exc, flush=True)
                continue
            result = game.result
            win = _winner_value(result, side)
            map_name = game.board.name or path.stem
            for row in raw_rows:
                row = dict(row)
                round_num = int(_number(row.get("round"), -1))
                if round_num < 0 or round_num > max_round:
                    continue
                if keep_every > 1 and round_num % keep_every:
                    continue
                row.update(
                    game=path.stem,
                    side=side,
                    map_name=map_name,
                    winner=result.get("winner") or "draw",
                    outcome="win" if win > 0 else "loss" if win < 0 else "draw",
                    win=win,
                    game_rounds=int(result.get("rounds") or 500),
                )
                rows.append(row)
            manifest.append({
                "game": path.stem,
                "side": side,
                "map": map_name,
                "winner": result.get("winner"),
                "rounds": result.get("rounds"),
                "rows": sum(1 for r in rows if r.get("game") == path.stem and r.get("side") == side),
                "sha256": _hash(path),
            })
        print("loaded", index, path.name, "rows", len(rows),
              "seconds", round(time.time() - started, 1), flush=True)
    if not rows:
        raise SystemExit("No usable replay action rows were found")
    return pd.DataFrame(rows), manifest


def context_names(frame):
    names = []
    for name in sorted(frame.columns):
        if name in NON_FEATURE_COLUMNS or name.startswith("c") and len(name) > 2 and name[1] in "FRBL" and name[2] == "_":
            continue
        if name.startswith("y_") or name.startswith("priv_"):
            continue
        values = pd.to_numeric(frame[name], errors="coerce")
        if values.notna().any():
            names.append(name)
    names.extend(("phase_0_50", "phase_50_100", "phase_100_250", "round_frac", "is_portal_view"))
    return names


def context_vector(row, names):
    round_num = _number(row.get("round"), 0)
    values = []
    for name in names:
        if name == "phase_0_50":
            value = round_num < 50
        elif name == "phase_50_100":
            value = 50 <= round_num < 100
        elif name == "phase_100_250":
            value = 100 <= round_num < 250
        elif name == "round_frac":
            value = round_num / 500.0
        elif name == "is_portal_view":
            value = _number(row.get("vis_portal"), 0) > 0
        else:
            value = _number(row.get(name), 0)
        values.append(float(value))
    return values


def observed_action(row):
    if row.get("y_family") == "split":
        size = int(_number(row.get("y_split"), 0))
        return "split" if size != 1 else None
    if row.get("y_family") not in ("move", "sprint"):
        return None
    action = str(row.get("y_first", ""))
    return action if action in MOVE_ACTIONS else None


def candidate_values(row, action):
    if action != "split":
        return [
            _number(row.get("c%s_%s" % (action, name)), 0)
            for name in CANDIDATE_ATTRIBUTES
        ] + [0.0]
    size = _number(row.get("y_split"), 0)
    return [0.0] * len(CANDIDATE_ATTRIBUTES) + [size if size >= 2 else 2.0]


def vector(row, action, names):
    return (
        context_vector(row, names)
        + [float(action == name) for name in ACTION_NAMES]
        + candidate_values(row, action)
    )


def legal_actions(row):
    actions = []
    for action in MOVE_ACTIONS:
        if _number(row.get("c%s_block" % action), 0) != 1:
            actions.append(action)
    if (_number(row.get("length"), 0) >= 4 and
            _number(row.get("units"), 0) < _number(row.get("unit_limit"), 64)):
        actions.append("split")
    return actions or ["F"]


def dense_reward(row, action, next_row, final_value):
    """Reward focused on the observed opening leaks.

    The final result is only injected at the r100 checkpoint or trajectory
    end.  Thus earlier actions receive credit through fitted-Q bootstrapping,
    rather than learning a constant win/loss label at every row.
    """
    reward = 0.0
    if next_row is not None:
        du = _number(next_row.get("units"), 0) - _number(row.get("units"), 0)
        dl = _number(next_row.get("length"), 0) - _number(row.get("length"), 0)
        reward += 0.015 * max(-4.0, min(4.0, du))
        reward += 0.008 * max(-8.0, min(8.0, dl))

    candidate = candidate_values(row, action)
    block, portal, pearl, area, eseg = (
        candidate[0], candidate[1], candidate[2], candidate[5], candidate[12]
    )
    if pearl > 0:
        reward += 0.035
    if block == 1:                 # kelp: hard veto should normally remove it
        reward -= 1.0
    if portal == 1:                # portal transit is useful but expensive to risk
        reward -= 0.055
    if action != "split" and area > 0 and area < _number(row.get("length"), 0):
        reward -= 0.08              # low-space / trap proxy
    if eseg > 0:
        reward -= 0.025 * min(eseg, 4.0)
    if action == "split":
        round_num = _number(row.get("round"), 0)
        units = _number(row.get("units"), 0)
        if round_num < 100 and units < 32:
            reward += 0.028           # early population is the main target
        elif round_num < 100:
            reward -= 0.012           # avoid monoculture/overproduction

    current_round = _number(row.get("round"), 0)
    next_round = _number(next_row.get("round"), 9999) if next_row else 9999
    crossed_r100 = current_round < 100 <= next_round
    ended = next_row is None
    if ended and current_round < _number(row.get("game_rounds"), 500) - 1:
        # The dragon stopped producing observations before the match ended;
        # in a replay this is normally a death (including a TLE/invalid
        # action). Keep this separate from the win label so a winning team
        # cannot receive positive credit for throwing away a dragon.
        reward -= 1.25
    if crossed_r100 or ended:
        reward += 1.5 * final_value
    return reward


def transition_rows(frame, names, max_rows=None, seed=0):
    """Return observed-action transitions and their next observation."""
    usable = []
    for _, group in frame.groupby(["game", "side", "dragon"], sort=False):
        group = group.sort_values(["round"]).to_dict("records")
        for index, row in enumerate(group):
            action = observed_action(row)
            if action is None:
                continue
            next_row = group[index + 1] if index + 1 < len(group) else None
            usable.append((row, action, next_row))
    if max_rows and len(usable) > max_rows:
        rng = np.random.default_rng(seed)
        chosen = rng.choice(len(usable), max_rows, replace=False)
        usable = [usable[int(i)] for i in sorted(chosen)]
    return usable


def fit_fqi(transitions, names, final_values, iterations, gamma, alpha):
    X = np.asarray([vector(row, action, names) for row, action, _ in transitions], dtype=np.float64)
    reward = np.asarray([
        dense_reward(row, action, next_row, final_values[row["game"], row["side"]])
        for row, action, next_row in transitions
    ], dtype=np.float64)
    opening_weight = np.asarray([
        2.0 if _number(row.get("round"), 0) < 100 else 1.0
        for row, _, _ in transitions
    ], dtype=np.float64)

    mean = X.mean(axis=0)
    scale = X.std(axis=0)
    scale[scale < 1e-6] = 1.0
    Z = (X - mean) / scale
    model = None
    target = reward.copy()
    for iteration in range(iterations):
        model = Ridge(alpha=alpha, fit_intercept=True)
        model.fit(Z, target, sample_weight=opening_weight)
        if iteration == iterations - 1:
            break
        boot = np.zeros(len(transitions), dtype=np.float64)
        for index, (row, _, next_row) in enumerate(transitions):
            if next_row is None:
                continue
            scores = []
            for action in legal_actions(next_row):
                v = np.asarray(vector(next_row, action, names), dtype=np.float64)
                scores.append(float(model.predict(((v - mean) / scale).reshape(1, -1))[0]))
            boot[index] = max(scores) if scores else 0.0
        target = reward + gamma * np.clip(boot, -2.0, 2.0)
        print("FQI iteration", iteration + 1, "target range",
              round(float(target.min()), 3), round(float(target.max()), 3), flush=True)
    return model, mean, scale, X, reward


def evaluate(model, mean, scale, transitions, names, final_values):
    rows = []
    for row, observed, _ in transitions:
        legal = legal_actions(row)
        scores = []
        for action in legal:
            x = np.asarray(vector(row, action, names), dtype=np.float64)
            z = ((x - mean) / scale).reshape(1, -1)
            scores.append((action, float(model.predict(z)[0])))
        best = max(scores, key=lambda item: item[1])
        rows.append({
            "game": row["game"], "side": row["side"],
            "round": int(_number(row.get("round"), 0)),
            "observed": observed, "predicted": best[0],
            "match": int(best[0] == observed), "best_q": best[1],
            "win": final_values[row["game"], row["side"]],
        })
    if not rows:
        return {"rows": 0}, pd.DataFrame()
    report = pd.DataFrame(rows)
    summary = {
        "rows": int(len(report)),
        "action_match": float(report.match.mean()),
        "action_match_opening": float(report.loc[report["round"] < 100, "match"].mean())
        if (report["round"] < 100).any() else None,
        "mean_best_q_win": float(report.loc[report.win > 0, "best_q"].mean())
        if (report.win > 0).any() else None,
        "mean_best_q_loss": float(report.loc[report.win < 0, "best_q"].mean())
        if (report.win < 0).any() else None,
        "by_round": {
            str(bucket): {
                "rows": int(part.shape[0]),
                "action_match": float(part.match.mean()),
            }
            for bucket, part in report.assign(
                bucket=pd.cut(report["round"], [-1, 49, 99, 249, 500], labels=["0-49", "50-99", "100-249", "250+"])
            ).groupby("bucket", observed=True)
        },
    }
    return summary, report


def distribution_report(frame):
    metrics = [
        "units", "length", "units_frac", "vis_pearls", "free_dirs",
        "vis_portal", "vis_kelp", "near_pearl", "near_enemy_head",
    ]
    out = {}
    for bucket, part in frame.assign(
        stage=pd.cut(frame["round"], [-1, 49, 99, 249, 500], labels=["0-49", "50-99", "100-249", "250+"])
    ).groupby(["outcome", "stage"], observed=True):
        values = {}
        for metric in metrics:
            if metric in part:
                series = pd.to_numeric(part[metric], errors="coerce").dropna()
                if len(series):
                    values[metric] = {
                        "mean": float(series.mean()),
                        "median": float(series.median()),
                        "p90": float(series.quantile(0.9)),
                    }
        out["%s|%s" % bucket] = {"rows": int(len(part)), "metrics": values}
    return out


def export_model(path, model, mean, scale, names, metadata):
    feature_names = (
        list(names) +
        ["action_" + action for action in ACTION_NAMES] +
        ["candidate_" + name for name in CANDIDATE_ATTRIBUTES] +
        ["split_size"]
    )
    payload = {
        "version": 1,
        "kind": "offline_fitted_q_linear",
        "actions": list(ACTION_NAMES),
        "candidate_attributes": list(CANDIDATE_ATTRIBUTES),
        "context_features": list(names),
        "feature_names": feature_names,
        "mean": [float(x) for x in mean],
        "scale": [float(x) for x in scale],
        "coef": [float(x) for x in model.coef_],
        "intercept": float(model.intercept_),
        "metadata": metadata,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    # Verify the dependency-free runtime agrees with sklearn on a few values.
    runtime = EarlyGameQPolicy(payload)
    return payload, runtime


def train(args):
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
    games = sorted(frame.game.unique())
    rng = np.random.default_rng(args.seed)
    rng.shuffle(games)
    n_train = max(1, int(len(games) * 0.70))
    n_val = max(1, int(len(games) * 0.15)) if len(games) >= 3 else 0
    splits = {
        "train": list(games[:n_train]),
        "validation": list(games[n_train:n_train + n_val]),
        "test": list(games[n_train + n_val:]),
    }
    if not splits["test"]:
        splits["test"] = splits["validation"]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "splits.json").write_text(json.dumps(splits, indent=2) + "\n")
    (out / "replay_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    train_frame = frame[frame.game.isin(splits["train"])]
    test_frame = frame[frame.game.isin(splits["test"])]
    train_transitions = transition_rows(train_frame, names, args.max_rows, args.seed)
    test_transitions = transition_rows(test_frame, names, args.max_test_rows, args.seed)
    if len(train_transitions) < 20:
        raise SystemExit("Too few usable transitions; add more replays or raise --max-round")
    print("training transitions", len(train_transitions), "test", len(test_transitions), flush=True)

    model, mean, scale, _, _ = fit_fqi(
        train_transitions, names, final_values, args.iterations, args.gamma, args.alpha
    )
    val_summary, val_rows = evaluate(
        model, mean, scale,
        transition_rows(frame[frame.game.isin(splits["validation"])], names, args.max_test_rows, args.seed),
        names, final_values,
    )
    test_summary, test_rows = evaluate(model, mean, scale, test_transitions, names, final_values)
    metadata = {
        "replays": manifest,
        "games": len(games),
        "rows": int(len(frame)),
        "training_transitions": len(train_transitions),
        "split_games": {key: len(value) for key, value in splits.items()},
        "hyperparameters": {
            "iterations": args.iterations, "gamma": args.gamma,
            "ridge_alpha": args.alpha, "keep_every": args.keep_every,
            "max_round": args.max_round,
        },
        "distribution_report": distribution_report(frame),
        "validation": val_summary,
        "test": test_summary,
        "action_counts": dict(Counter(action for _, action, _ in train_transitions)),
    }
    payload, runtime = export_model(out / "model.json", model, mean, scale, names, metadata)
    # A parity smoke test across a small sample catches accidental export drift.
    parity = []
    for row, _, _ in train_transitions[: min(100, len(train_transitions))]:
        for action in runtime.legal_actions(row):
            x = np.asarray(vector(row, action, names), dtype=np.float64)
            sklearn_score = float(model.predict(((x - mean) / scale).reshape(1, -1))[0])
            parity.append(abs(sklearn_score - runtime.score(row, action)))
    if parity and max(parity) > 1e-6:
        raise AssertionError("exported runtime does not match the fitted model")
    (out / "training_summary.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    if not val_rows.empty:
        val_rows.to_csv(out / "validation_predictions.csv", index=False)
    if not test_rows.empty:
        test_rows.to_csv(out / "test_predictions.csv", index=False)
    print(json.dumps({"validation": val_summary, "test": test_summary,
                      "model": str(out / "model.json")}, indent=2), flush=True)


def recommend(args):
    state_text = sys.stdin.read() if args.state == "-" else Path(args.state).read_text()
    state = json.loads(state_text)
    policy = EarlyGameQPolicy.load(args.model)
    ranked = policy.rank(state)
    print(json.dumps({"action": ranked[0][0], "ranking": [
        {"action": action, "q": score} for action, score in ranked
    ]}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    train_parser = sub.add_parser("train", help="fit the offline opening policy")
    train_parser.add_argument("--replays", nargs="+", required=True)
    train_parser.add_argument("--sides", nargs="+", choices=("A", "B"), default=("A", "B"))
    train_parser.add_argument("--out", type=Path, default=ROOT / "build" / "rl-earlygame")
    train_parser.add_argument("--max-games", type=int, default=80)
    train_parser.add_argument("--max-round", type=int, default=250)
    train_parser.add_argument("--keep-every", type=int, default=1)
    train_parser.add_argument("--max-rows", type=int, default=250000)
    train_parser.add_argument("--max-test-rows", type=int, default=50000)
    train_parser.add_argument("--iterations", type=int, default=5)
    train_parser.add_argument("--gamma", type=float, default=0.98)
    train_parser.add_argument("--alpha", type=float, default=30.0)
    train_parser.add_argument("--seed", type=int, default=20260929)
    train_parser.set_defaults(func=train)
    recommend_parser = sub.add_parser("recommend", help="score one protocol feature state")
    recommend_parser.add_argument("--model", required=True, type=Path)
    recommend_parser.add_argument("--state", required=True,
                                  help="JSON feature row, or - to read stdin")
    recommend_parser.set_defaults(func=recommend)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
