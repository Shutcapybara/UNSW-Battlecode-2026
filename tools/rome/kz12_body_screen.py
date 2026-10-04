#!/usr/bin/env python3
"""Summarize the corrected H29 H-KZ12 four-dose seed-1 screen."""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

from tools.rome.dose_screen import METRICS, aggregate, key_frame, paired, read_arm, summarize_pairs

NAMES = {
    "k0": "rome-12-kz12-cb-k0",
    "k4": "rome-13-kz12-cb-k4",
    "k8": "rome-14-kz12-cb-k8",
    "k16": "rome-15-kz12-cb-k16",
}
DOSES = {"k0": 0, "k4": 4, "k8": 8, "k16": 16}
def read_log_index(root: Path, dose: int):
    path = root / "kz12-logs.jsonl"
    if not dose:
        return {}
    if not path.is_file():
        raise FileNotFoundError(f"missing deterministic KZ12 transcript capture: {path}")
    out = {}
    for line in path.read_text().splitlines():
        if line.strip():
            row = json.loads(line)
            if not row.get("official_match") or row.get("errors"):
                raise ValueError(f"KZ12 transcript rerun does not match official fixture: {row.get('game')}")
            out[row["game"]] = [
                (int(d["round"]), int(d["dose"]), int(d["vetoed_directions"]),
                 int(d["fallback"]), int(d["max_selected_Cb"]))
                for d in row["decisions"]
            ]
    expected = {json.loads(line)["game"] for line in (root / "index.jsonl").read_text().splitlines() if line.strip()}
    if set(out) != expected:
        raise ValueError(f"KZ12 transcript fixture mismatch: {len(out)} captures for {len(expected)} panel games")
    return out


def queen_data(root: Path, features: pd.DataFrame, bot_name: str, dose: int):
    from tools.analysis.features.frame import load

    index = {json.loads(s)["game"]: json.loads(s) for s in (root / "index.jsonl").read_text().splitlines() if s.strip()}
    log_index = read_log_index(root, dose)
    totals = Counter()
    by_map = defaultdict(Counter)
    labels = Counter()
    for game in features.game.unique():
        g = load(root / "replays" / f"{game}.replay", cache_dir=root / "frames")
        row = index[game]
        side = "A" if Path(g["botA"]).name == bot_name else "B"
        rounds = g["rounds"]
        ids = [i for i, (team, _) in rounds[0].items() if team == side]
        if not ids:
            continue
        q = min(ids)
        is_reached = len(rounds) > 490
        is_alive = bool(is_reached and q in rounds[490])
        deaths = [d for d in g["events"]["deaths"] if d["id"] == q]
        death = deaths[0] if deaths else None
        log = log_index.get(game, []) if dose else []
        veto_events = [r for r, k, veto, fallback, cap in log if veto > 0]
        m = str(row.get("map", "unknown"))
        mh = str(g.get("map_hash", "unknown"))
        group = by_map[(m, mh)]
        for bucket in (totals, group):
            bucket["games"] += 1
            bucket["reached490"] += int(is_reached)
            bucket["alive490_joint"] += int(is_alive)
            if death:
                bucket["queen_death_" + str(death["cause"])] += 1
            bucket["diagnostic_decisions"] += len(log)
            bucket["vetoed_directions"] += sum(veto for r, k, veto, fallback, cap in log)
            bucket["fallback_turns"] += sum(fallback for r, k, veto, fallback, cap in log)
            bucket["vetoed_turns"] += len(veto_events)
            bucket["max_selected_Cb"] = max([bucket.get("max_selected_Cb", 0)] + [cap for r, k, veto, fallback, cap in log if cap >= 0])
        if death and log:
            immediate = [d for d in log if d[0] == int(death["round"]) ]
            if immediate:
                labels["immediate_" + str(death["cause"])] += 1
                totals["immediate_queen_deaths_after_checked_turn"] += 1
                group["immediate_queen_deaths_after_checked_turn"] += 1
        if veto_events:
            t = min(veto_events)
            if death and int(death["round"]) == t:
                labels["first_veto_immediate_" + str(death["cause"])] += 1
                totals["first_veto_immediate_death"] += 1
                group["first_veto_immediate_death"] += 1
            elif death and t + 1 <= int(death["round"]) <= t + 6:
                labels["six_round_" + str(death["cause"])] += 1
                totals["first_veto_death_within6"] += 1
                totals["first_veto_death_" + str(death["cause"])] += 1
                group["first_veto_death_within6"] += 1
                group["first_veto_death_" + str(death["cause"])] += 1
            elif g["last_round"] >= t + 6:
                labels["first_veto_no_death_within6"] += 1
                totals["first_veto_no_death_within6"] += 1
                group["first_veto_no_death_within6"] += 1
            else:
                labels["first_veto_censored_before6"] += 1
                totals["first_veto_censored_before6"] += 1
                group["first_veto_censored_before6"] += 1
    return dict(totals), {k: dict(v) for k, v in by_map.items()}, dict(labels)


def main():
    ap = argparse.ArgumentParser()
    for panel in ("pool", "gen"):
        for arm in NAMES:
            ap.add_argument(f"--{panel}-{arm}", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    roots = {
        panel: {arm: getattr(a, f"{panel}_{arm}") for arm in NAMES}
        for panel in ("pool", "gen")
    }
    panels, permap, regimes, queen_maps = [], [], [], []
    for panel, rr in roots.items():
        arms = {k: key_frame(read_arm(v, NAMES[k])) for k, v in rr.items()}
        for arm, name in NAMES.items():
            q, qm, qlabels = queen_data(rr[arm], arms[arm], name, DOSES[arm])
            panels.append({"panel": panel, "dose": DOSES[arm], "arm": arm,
                           "absolute": aggregate(arms[arm], METRICS), "queen_and_logs": q,
                           "queen_labels": qlabels})
            for (mapname, map_hash), values in qm.items():
                queen_maps.append({"panel": panel, "dose": DOSES[arm], "map": mapname,
                                   "map_hash": map_hash, **values})
        for arm, dose in DOSES.items():
            if arm == "k0":
                continue
            diff = paired(arms["k0"], arms[arm], METRICS)
            for mapname, rows in diff.groupby("map_arm"):
                permap.append({"panel": panel, "dose": dose, "map": mapname,
                               "map_hash": str(rows.map_hash_arm.iloc[0]), **summarize_pairs(rows, METRICS)})
            for era, rows in diff.groupby("map_era"):
                for regime, rg in rows.groupby("regime"):
                    regimes.append({"panel": panel, "dose": dose, "map_era": era,
                                    "regime": regime, **summarize_pairs(rg, METRICS)})
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({"parent": "carthage-05-free-sprint (Rome dose-0 exact-parity snapshot)",
                                 "map_era": "pool post-m2; gen split stale pre-swap twins from current/unflagged",
                                 "dose_semantics": "H29 candidate-body Cb<k and no eligible cycle; k=0/4/8/16",
                                 "label": "first veto: immediate same-round cause; t+1..t+6 cause; right-censor before t+6",
                                 "seed": 1, "screen_only": True, "panels": panels}, indent=2) + "\n")
    a.out.with_name(a.out.stem + "-permap.csv").write_text(pd.DataFrame(permap).to_csv(index=False))
    a.out.with_name(a.out.stem + "-regime.csv").write_text(pd.DataFrame(regimes).to_csv(index=False))
    a.out.with_name(a.out.stem + "-queen-permap.csv").write_text(pd.DataFrame(queen_maps).to_csv(index=False))
    print(a.out.read_text())


if __name__ == "__main__":
    main()
