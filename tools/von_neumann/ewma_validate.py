#!/usr/bin/env python3
"""Stage A of the Von Neumann information cycle: validate EWMA choices
against actual dragon data from replays, BEFORE building/consuming any new
field (choices frozen in tools/von_neumann/ewma_frozen.json).

What is simulated (mirrors bots/porthos-x04-policy/swarm.py):
  - position fuzz: EWMA of the dragon's own head position, reset when the
    true head jumps > 3 torus distance in one round (portal jump);
  - observation EWMAs: per-round count of allied / enemy dragon HEADS in the
    dragon's 7x7 visible window, smoothed with retain = 0.5 ** (1 / h).

Ground truth per dragon-round comes from the replay event stream (per-id
heads, teams, splits with child lengths, pearls per actor).  Lengths are
approximated as birth_length + pearls_eaten (sprint costs are not in the
event stream); count-based conclusions transfer to length fields because the
same decay constant governs both.  Each dragon smooths its own position and
its own observed window counts (identity = dragon id, as in swarm.observe).

Metrics per half-life h:
  pos_err      mean torus distance EWMA-position vs true head (tiles)
  est_err_*    mean |EWMA(count) - true current count| (ally / enemy heads)
  contact_lag  mean rounds from a true 0->k enemy entry until EWMA >= 0.5
  ghost        mean rounds after a true k->0 enemy exit until EWMA < half

Usage: .venv/bin/python -m tools.von_neumann.ewma_validate [--replays N]
"""
import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from hydra_replay import Rep  # noqa: E402

HALF_LIVES = (0.5, 1.0, 2.0, 4.0, 8.0, 16.0)
VIEW = 3  # 7x7 window around the head


def torus_d(x1, y1, x2, y2, W, H):
    dx, dy = abs(x1 - x2), abs(y1 - y2)
    return min(dx, W - dx) + min(dy, H - dy)


def load_game(path):
    """-> (W, H, name, rounds); rounds[r] = [(id, team, x, y, len), ...]."""
    rep = Rep(path)
    root = rep.obj(0, 0)
    if root.num(0, "I") not in (0, 1, 2):
        raise ValueError("unsupported replay")
    team_of, live = {}, set()
    W = H = 0
    name = path.stem
    for line in root.text(0).splitlines():
        p = line.split()
        if p and p[0] == "DRAGON":
            team_of[len(team_of)] = "AB"[int(p[1])]
            live.add(len(team_of) - 1)
        elif p and p[0] == "MAP":
            W, H = int(p[1]), int(p[2])
        elif p and p[0] == "MAP_NAME":
            name = p[1]
    rounds = defaultdict(list)
    lens = defaultdict(lambda: 2)
    updates = {}
    round_num = -1
    actor = None

    def flush(r):
        for d, (x, y) in updates.items():
            if d in live:
                rounds[r].append((d, team_of[d], x, y, lens[d]))

    for ev in root.struct_list(3):
        kind, obj = ev.num(0, "H"), ev.child(0)
        ident = obj.num()
        if kind == 0:
            if round_num >= 0:
                flush(round_num)
            round_num = ident
        elif kind == 1:
            actor = ident
        elif kind == 3 and not obj.num(0, "B"):
            lens[actor] += 1
        elif kind == 9:
            head = obj.child(0)
            updates[ident] = (head.num(), head.num(4))
        elif kind == 10:
            child = obj.num(4)
            team_of[child] = team_of[ident]
            live.add(child)
            try:
                lens[child] = len(obj.struct_list(1))
                lens[ident] = len(obj.struct_list(0))
            except ValueError:
                pass
        elif kind == 11:
            live.discard(ident)
    if round_num >= 0:
        flush(round_num)
    return W, H, name, dict(rounds)


def sim_game(W, H, rounds, acc, est):
    """Per-dragon-id simulation: each dragon smooths ITS OWN position and its
    observed window counts, exactly as swarm.observe does for the local
    estimator.  Identity persists across moves (the bot knows its own id)."""
    max_r = max(rounds)
    pos, last_head = {}, {}
    cnt = {"ally": {h: {} for h in HALF_LIVES}, "enemy": {h: {} for h in HALF_LIVES}}
    entry_from, exit_from = {}, {}
    prev_true = {}
    for r in range(max_r + 1):
        roster = rounds.get(r, [])  # [(id, team, x, y, len)]
        by_id = {d: (t, x, y) for d, t, x, y, _ in roster}
        true_counts = {}
        for d, t, x, y, _ in roster:
            a = e = 0
            for d2, t2, x2, y2, _ in roster:
                if d2 == d:
                    continue
                if abs(x2 - x) <= VIEW and abs(y2 - y) <= VIEW:
                    if t2 == t:
                        a += 1
                    else:
                        e += 1
            true_counts[d] = (a, e)
        for d, (t, x, y) in by_id.items():
            a, e = true_counts[d]
            prev = last_head.get(d)
            if prev is None or torus_d(prev[0], prev[1], x, y, W, H) > 3:
                pos[d] = (float(x), float(y))
                for h in HALF_LIVES:
                    cnt["ally"][h][d] = float(a)
                    cnt["enemy"][h][d] = float(e)
            else:
                retain = 0.5 ** (1.0 / 4.0)
                px, py = pos[d]
                pos[d] = (px + (1 - retain) * (x - px), py + (1 - retain) * (y - py))
                for h in HALF_LIVES:
                    k = 0.5 ** (1.0 / h)
                    cnt["ally"][h][d] = k * cnt["ally"][h][d] + (1 - k) * a
                    cnt["enemy"][h][d] = k * cnt["enemy"][h][d] + (1 - k) * e
            last_head[d] = (x, y)
            acc["pos_err"].append(torus_d(pos[d][0] % W, pos[d][1] % H, x, y, W, H))
            for h in HALF_LIVES:
                est["ally"][h].append(abs(cnt["ally"][h][d] - a))
                est["enemy"][h].append(abs(cnt["enemy"][h][d] - e))
            pe = prev_true.get(d, 0)
            if e > 0 and pe == 0:
                for h in HALF_LIVES:
                    entry_from[(h, d)] = r
            if e == 0 and pe > 0:
                for h in HALF_LIVES:
                    exit_from[(h, d)] = (r, pe)
        for d in by_id:
            for h in HALF_LIVES:
                ek = (h, d)
                if ek in entry_from and cnt["enemy"][h][d] >= 0.5:
                    acc["lags"][h].append(r - entry_from.pop(ek))
                if ek in exit_from:
                    r0, k0 = exit_from[ek]
                    if cnt["enemy"][h][d] < max(0.5, k0 * 0.5):
                        acc["ghosts"][h].append(r - r0)
                        del exit_from[ek]
        for ek in list(entry_from):
            if ek[1] not in by_id:
                del entry_from[ek]
        for ek in list(exit_from):
            if ek[1] not in by_id:
                del exit_from[ek]
        prev_true = {d: v[1] for d, v in true_counts.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--replays", type=int, default=14)
    ap.add_argument("--out", default=str(ROOT / "tools/von_neumann/ewma_frozen.json"))
    a = ap.parse_args()
    paths = []
    srcs = [
        ROOT / "experiment_data/porthos-x04-policy_20260925231141141754",  # gauntlet, 13 maps
        ROOT / "experiment_data/von_neumann-x01-frozen_20260926025041568869",  # fresh reserve
        ROOT / "experiment_data/von_neumann-x01-frozen_20260926021700684201",  # dev screen
    ]
    for src in srcs:
        paths.extend(sorted(src.glob("opponents/*/replays/*-candidate-A.replay")))
    step = max(1, len(paths) // a.replays)
    paths = paths[::step][: a.replays]
    print(f"validating on {len(paths)} replays")
    acc = {"pos_err": [], "lags": defaultdict(list), "ghosts": defaultdict(list)}
    est = {"ally": defaultdict(list), "enemy": defaultdict(list)}
    games = []
    for p in paths:
        try:
            W, H, name, rounds = load_game(p)
            assert W and rounds, "empty"
        except Exception as exc:
            print("skip", p.name, exc)
            continue
        games.append(name)
        sim_game(W, H, rounds, acc, est)
    rows = {}
    for h in HALF_LIVES:
        rows[h] = {
            "pos_err": round(statistics.mean(acc["pos_err"]), 3),
            "est_err_enemy": round(statistics.mean(est["enemy"][h]), 3),
            "est_err_ally": round(statistics.mean(est["ally"][h]), 3),
            "contact_lag": round(statistics.mean(acc["lags"][h]), 2) if acc["lags"][h] else None,
            "ghost": round(statistics.mean(acc["ghosts"][h]), 2) if acc["ghosts"][h] else None,
            "n_lag": len(acc["lags"][h]), "n_ghost": len(acc["ghosts"][h]),
            "n_obs": len(est["enemy"][h]),
        }
    # choice rule (pre-stated): short = min contact_lag among h with
    # est_err_enemy <= 1.0; long = min est_err_enemy overall.
    elig = [h for h in HALF_LIVES
            if rows[h]["contact_lag"] is not None and rows[h]["est_err_enemy"] <= 1.0]
    short_h = min(elig, key=lambda h: (rows[h]["contact_lag"], h)) if elig else 2.0
    long_h = min(HALF_LIVES, key=lambda h: (rows[h]["est_err_enemy"], h))
    out = {
        "replays": [p.name for p in paths], "games": games,
        "note": "Half-life validation vs replay ground truth, frozen before any "
                "cycle-2 screen outcome was read. Length approximated birth+pearls; "
                "identity-by-head-cell is the conservative reset model.",
        "half_lives": {str(k): v for k, v in rows.items()},
        "chosen": {"short_h": short_h, "long_h": long_h,
                   "rule": "short = min contact_lag with est_err_enemy<=1.0; long = min est_err_enemy"},
    }
    Path(a.out).write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"half_lives": out["half_lives"], "chosen": out["chosen"]}, indent=2))


if __name__ == "__main__":
    main()
