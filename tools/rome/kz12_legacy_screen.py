#!/usr/bin/env python3
"""D-044 seed-1 response curve for Rome's H-KZ12 directed tree-entry dial."""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.analysis.features.frame import load
from tools.rome.dose_screen import METRICS, aggregate, key_frame, paired, read_arm, summarize_pairs

NAMES = {
    "parent": "carthage-05-free-sprint",
    "k5": "rome-09-kz12-k5",
    "k8": "rome-10-kz12-k8",
    "k16": "rome-11-kz12-k16",
}
DOSES = {"k5": 5, "k8": 8, "k16": 16}


def small_tree_entry(nbr, u: int, v: int, length: int, k: int):
    """Return exact (C, tree) when C<k and the decoded map is fully known."""
    seen = {u, v}
    pocket = [v]
    for c in pocket:
        for n in nbr.get(c, ()):
            if n is None or n == u or n in seen:
                continue
            seen.add(n)
            pocket.append(n)
            if len(pocket) >= k:
                return None
    nodes = [u, *pocket]
    members = set(nodes)
    best = 0
    # Directed simple-cycle search over the replay's legal movement graph.
    # It stops as soon as any cycle can hold the queen's post-move length.
    need = length + 1
    if len(nodes) < need:
        return len(pocket), True
    for start in nodes:
        path = [start]
        used = {start}

        def dfs(c):
            for n in nbr.get(c, ()):
                if n is None or n not in members:
                    continue
                if n == start and len(path) >= need:
                    return True
                if n in used:
                    continue
                used.add(n)
                path.append(n)
                if dfs(n):
                    return True
                path.pop()
                used.remove(n)
            return False

        if dfs(start):
            return len(pocket), False
    return len(pocket), True


def queen_diagnostics(root: Path, features: pd.DataFrame, bot_name: str, dose: int):
    idx = {json.loads(s)["game"]: json.loads(s) for s in (root / "index.jsonl").read_text().splitlines() if s.strip()}
    out = defaultdict(int)
    for game in features.game.unique():
        g = load(root / "replays" / f"{game}.replay", cache_dir=root / "frames")
        side = "A" if Path(g["botA"]).name == bot_name else "B"
        rounds, nbr = g["rounds"], g["nbr"]
        q = min(i for i, (team, _) in rounds[0].items() if team == side)
        reached = len(rounds) > 490
        alive = reached and q in rounds[490]
        out["games"] += 1
        out["reached490"] += int(reached)
        out["alive490"] += int(alive)
        deaths = [d for d in g["events"]["deaths"] if d["id"] == q]
        death = deaths[0] if deaths else None
        if death:
            out["death_" + str(death["cause"])] += 1
        if dose <= 0:
            continue
        first = None
        for t in range(1, len(rounds) - 1):
            if q not in rounds[t] or q not in rounds[t + 1]:
                break
            old, new = rounds[t][q][1], rounds[t + 1][q][1]
            u, v = old[0], new[0]
            if u == v:
                continue
            res = small_tree_entry(nbr, u, v, len(new), dose)
            if res is not None:
                first = (t + 1, res[0])
                break
        if first:
            out["first_tree_entry"] += 1
            if death and 0 <= int(death["round"]) - first[0] <= 8:
                out["queen_death_within8_after_entry"] += 1
                out["entry_death_" + str(death["cause"])] += 1
    return dict(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool-parent", type=Path, required=True)
    ap.add_argument("--gen-parent", type=Path, required=True)
    ap.add_argument("--pool-k5", type=Path, required=True)
    ap.add_argument("--gen-k5", type=Path, required=True)
    ap.add_argument("--pool-k8", type=Path, required=True)
    ap.add_argument("--gen-k8", type=Path, required=True)
    ap.add_argument("--pool-k16", type=Path, required=True)
    ap.add_argument("--gen-k16", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    roots = {
        "pool_m2": {"parent": a.pool_parent, "k5": a.pool_k5, "k8": a.pool_k8, "k16": a.pool_k16},
        "gen": {"parent": a.gen_parent, "k5": a.gen_k5, "k8": a.gen_k8, "k16": a.gen_k16},
    }
    reports, permap, regimes, queens = [], [], [], []
    for panel, rr in roots.items():
        arms = {k: key_frame(read_arm(v, NAMES[k])) for k, v in rr.items()}
        for k, name in NAMES.items():
            dose = DOSES.get(k, 0)
            reports.append({"panel": panel, "dose": dose, "arm": k,
                            "absolute": aggregate(arms[k], METRICS),
                            "queen": queen_diagnostics(rr[k], arms[k], name, dose)})
        for arm, dose in DOSES.items():
            diff = paired(arms["parent"], arms[arm], METRICS)
            for mapname, rows in diff.groupby("map_arm"):
                permap.append({"panel": panel, "dose": dose, "map": mapname,
                               "map_hash": str(rows.map_hash_arm.iloc[0]), **summarize_pairs(rows, METRICS)})
            for era, rows in diff.groupby("map_era"):
                for regime, rg in rows.groupby("regime"):
                    regimes.append({"panel": panel, "dose": dose, "map_era": era,
                                    "regime": regime, **summarize_pairs(rg, METRICS)})
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({"parent": NAMES["parent"], "seed": 1,
                                 "map_era": "pool post-m2; gen split stale pre-swap twins from current/unflagged",
                                 "screen_only": True,
                                 "dose_semantics": "veto if inclusive C(u->v) < k and P+u has no cycle >= queen length + 1",
                                 "panels": reports}, indent=2) + "\n")
    a.out.with_name(a.out.stem + "-permap.csv").write_text(pd.DataFrame(permap).to_csv(index=False))
    a.out.with_name(a.out.stem + "-regime.csv").write_text(pd.DataFrame(regimes).to_csv(index=False))
    print(a.out.read_text())


if __name__ == "__main__":
    main()
