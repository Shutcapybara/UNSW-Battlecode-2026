#!/usr/bin/env python3
"""Summarise paired seed-1 dose screens against the post-M2 Carthage baseline."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.analysis.features.frame import load

STALE = {f"var/{m}_tr" for m in ("autarky", "default", "dilemma", "schooltime", "slithery_fight", "trophy")}
METRICS = ["won", "pearls@50", "pearls@100", "pearls@150", "pearls@250", "units@100", "total@100", "births@100",
           "death_wall_per1k", "death_self_per1k", "death_ally_body_per1k", "death_h2h_ally_per1k", "death_invalid_per1k"]


def read_arm(root: Path, name: str) -> pd.DataFrame:
    f = pd.read_parquet(root / "features" / "features.parquet")
    return f[(f.bot == name) & (f.seed == 1)].copy()


def key_frame(f: pd.DataFrame) -> pd.DataFrame:
    f = f.copy()
    f["fixture"] = list(zip(f.seed, f["map"], f.opponent, f.side))
    f["mapkey"] = f.game.str.split("__").str[1].str.replace("_", "/", n=1)
    f["map_era"] = np.where(f["mapkey"].isin(STALE), "stale pre-swap gen twin", "current or unflagged map")
    f["regime"] = np.where(f.reason == "elimination", "elimination", "round-limit")
    return f


def aggregate(f: pd.DataFrame, cols: list[str]) -> dict:
    out = {"games": int(len(f)), "wins": int((f.result == "win").sum()),
           "losses": int((f.result == "loss").sum()), "draws": int((f.result == "draw").sum()),
           "expected_score": float(f.won.mean()) if len(f) else None}
    for c in cols:
        if c in f and len(f):
            out[c] = float(f[c].mean())
    return out


def queen_summary(root: Path, f: pd.DataFrame, name: str) -> dict:
    idx = {json.loads(s)["game"]: json.loads(s) for s in (root / "index.jsonl").read_text().splitlines() if s.strip()}
    reached = alive = qloss = qgames = qwins = 0
    for game in f.game.unique():
        g = load(root / "replays" / f"{game}.replay", cache_dir=root / "frames")
        side = "A" if Path(g["botA"]).name == name else "B"
        first = g["rounds"][0]
        ids = [i for i, (team, _body) in first.items() if team == side]
        if not ids:
            continue
        qid = min(ids)
        is_reached = len(g["rounds"]) > 490
        reached += int(is_reached)
        alive += int(is_reached and qid in g["rounds"][490])
        row = idx.get(game, {})
        q = "queen" in str(row.get("reason", "")).lower()
        qgames += int(q)
        qloss += int(q and row.get("winner") != side)
        qwins += int(q and row.get("winner") == side)
    return {"queen_reached490": reached, "queen_alive490_joint": alive,
            "queen_survival_reached490": alive / reached if reached else None,
            "queen_decided_games": qgames, "queen_decided_wins": qwins,
            "queen_decided_losses": qloss}


def paired(parent: pd.DataFrame, arm: pd.DataFrame, names: list[str]) -> pd.DataFrame:
    p, a = key_frame(parent), key_frame(arm)
    both = p.merge(a, on="fixture", suffixes=("_parent", "_arm"), validate="one_to_one")
    both["map_era"] = both["map_era_arm"]
    both["regime"] = both["regime_arm"]
    for c in names:
        both["d_" + c] = both[c + "_arm"] - both[c + "_parent"]
    return both


def summarize_pairs(x: pd.DataFrame, names: list[str]) -> dict:
    out = {"games": len(x)}
    for c in names:
        v = x["d_" + c].dropna()
        out["delta_" + c] = float(v.mean()) if len(v) else None
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool-parent", type=Path, required=True)
    ap.add_argument("--gen-parent", type=Path, required=True)
    ap.add_argument("--e1-pool", type=Path, required=True)
    ap.add_argument("--e1-gen", type=Path, required=True)
    ap.add_argument("--e3-pool", type=Path, required=True)
    ap.add_argument("--e3-gen", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    names = {"parent": "carthage-05-free-sprint", "e1": "rome-06-cage-e1", "e3": "rome-07-cage-e3"}
    roots = {"pool_m2": {"parent": a.pool_parent, "e1": a.e1_pool, "e3": a.e3_pool},
             "gen": {"parent": a.gen_parent, "e1": a.e1_gen, "e3": a.e3_gen}}
    reports, maps, regimes = [], [], []
    for panel, rr in roots.items():
        arms = {k: key_frame(read_arm(v, names[k])) for k, v in rr.items()}
        reports.append({"panel": panel, "dose": 0,
                        "absolute": aggregate(arms["parent"], METRICS),
                        "queen": queen_summary(rr["parent"], arms["parent"], names["parent"])})
        for arm in ("e1", "e3"):
            treatment = arms[arm]
            reports.append({"panel": panel, "dose": 1 if arm == "e1" else 3,
                            "absolute": aggregate(treatment, METRICS),
                            "queen": queen_summary(rr[arm], treatment, names[arm])})
            diff = paired(arms["parent"], treatment, METRICS)
            for mapname, d in diff.groupby("map_arm"):
                maps.append({"panel": panel, "dose": 1 if arm == "e1" else 3, "map": mapname,
                             "map_hash": str(d.map_hash_arm.iloc[0]), **summarize_pairs(d, METRICS)})
            groups = [("all", diff)]
            if panel == "gen":
                groups = [(era, d) for era, d in diff.groupby("map_era")]
            for era, d in groups:
                for reg, rg in d.groupby("regime"):
                    regimes.append({"panel": panel, "dose": 1 if arm == "e1" else 3,
                                    "map_era": era, "regime": reg, **summarize_pairs(rg, METRICS)})
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({"map_era": "pool post-m2; gen split by geometry era", "seed": 1,
                                 "note": "screening package effects; E dose is not isolated from C+D vs parent",
                                 "panels": reports}, indent=2) + "\n")
    a.out.with_name(a.out.stem + "-permap.csv").write_text(pd.DataFrame(maps).to_csv(index=False))
    a.out.with_name(a.out.stem + "-regime.csv").write_text(pd.DataFrame(regimes).to_csv(index=False))
    print(a.out.read_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
