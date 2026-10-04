#!/usr/bin/env python3
"""Summarise the post-M2 carthage-05 baseline by panel and map hash."""
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

BOT = "carthage-05-free-sprint"
METRICS = ["pearls@50", "pearls@100", "pearls@150", "pearls@250",
           "units@100", "total@100", "births@100"]
SWAPPED = ("autarky", "default", "dilemma", "schooltime", "slithery_fight", "trophy")
STALE_TWINS = ({f"var/{x}_tr" for x in SWAPPED}
               | {f"pub/{x}_rec" for x in SWAPPED})


def queen_rows(root: Path, frame: pd.DataFrame) -> pd.DataFrame:
    idx = {json.loads(line)["game"]: json.loads(line)
           for line in (root / "index.jsonl").read_text().splitlines() if line.strip()}
    out = []
    for game in frame.game.unique():
        path = root / "replays" / f"{game}.replay"
        g = load(path, cache_dir=root / "frames")
        side = "A" if Path(g["botA"]).name == BOT else "B" if Path(g["botB"]).name == BOT else None
        if side is None:
            continue
        first = g["rounds"][0]
        queen_ids = [i for i, (team, _body) in first.items() if team == side]
        if not queen_ids:
            continue
        queen = min(queen_ids)
        reached = len(g["rounds"]) > 490
        snap = g["rounds"][490] if reached else {}
        alive = queen in snap
        qlen = len(snap[queen][1]) if alive else 0
        final = g["rounds"][-1]
        final_queens = {}
        for team in ("A", "B"):
            ids = [i for i, (t, _body) in g["rounds"][0].items() if t == team]
            final_queens[team] = len(final[min(ids)][1]) if ids and min(ids) in final else 0
        winner = idx.get(game, {}).get("winner")
        loser = "B" if winner == "A" else "A" if winner == "B" else None
        own_lens = [len(body) for team, body in snap.values() if team == side]
        out.append(dict(game=game, map=g["map"], map_hash=g["map_hash"],
                        queen_reached490=int(reached), queen_alive490=int(alive),
                        queen_len490=qlen, queen_longest490=int(alive and own_lens and qlen == max(own_lens)),
                        reason=idx.get(game, {}).get("reason", ""), rounds=idx.get(game, {}).get("rounds", 0),
                        own_queen_final=final_queens[side], opponent_queen_final=final_queens["B" if side == "A" else "A"],
                        winner_queen_final=final_queens.get(winner, 0) if winner else 0,
                        loser_queen_final=final_queens.get(loser, 0) if loser else 0,
                        queen_decided=int("queen" in str(idx.get(game, {}).get("reason", "")).lower()),
                        queen_verdict_consistent=int(bool(winner in final_queens and "queen" in str(idx.get(game, {}).get("reason", "")).lower()
                                                          and final_queens[winner] > final_queens[loser]))))
    return pd.DataFrame(out)


def map_cluster_ci(frame: pd.DataFrame, panel: str) -> list[float | None]:
    """95% percentile CI for queen-decided share of losses, resampling maps."""
    by_map = frame.assign(
        loss=(frame.result == "loss").astype(int),
        queen_loss=((frame.result == "loss") & (frame.queen_decided == 1)).astype(int),
    ).groupby("map_hash")[["loss", "queen_loss"]].sum().to_numpy(dtype=float)
    if len(by_map) == 0:
        return [None, None]
    rng = np.random.default_rng(44044 if panel == "pool_m2" else 44045)
    sample = rng.integers(0, len(by_map), size=(20000, len(by_map)))
    sums = by_map[sample].sum(axis=1)
    shares = sums[:, 1] / np.maximum(sums[:, 0], 1)
    lo, hi = np.quantile(shares, [0.025, 0.975])
    return [float(lo), float(hi)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool-root", required=True, type=Path)
    ap.add_argument("--gen-root", required=True, type=Path)
    ap.add_argument("--out", default="game_stats/runs/rome-carthage05-post-m2")
    a = ap.parse_args()
    all_map, totals = [], []
    for panel, root in (("pool_m2", a.pool_root), ("gen", a.gen_root)):
        f = pd.read_parquet(root / "features" / "features.parquet")
        f = f[f.bot == BOT].copy()
        q = queen_rows(root, f)
        f = f.merge(q, on=["game", "map", "map_hash"], how="left", suffixes=("", "_q"))
        f["mapkey"] = f.game.str.split("__").str[1].str.replace("_", "/", n=1)
        f["geometry_status"] = f.mapkey.map(lambda k: "stale_gen_twin" if k in STALE_TWINS else "current_or_unflagged")
        for (name, h, status), d in f.groupby(["map", "map_hash", "geometry_status"], dropna=False):
            row = dict(panel=panel, map=name, map_hash=h, geometry_status=status, n=len(d),
                       wins=int((d.result == "win").sum()), losses=int((d.result == "loss").sum()),
                       draws=int((d.result == "draw").sum()), exp_share=float(d.won.mean()))
            for m in METRICS:
                row[m + "_median"] = float(d[m].median())
            reached = d[d.queen_reached490 == 1]
            row.update(queen_reached490=len(reached), queen_joint_reached_alive490=int(d.queen_alive490.sum()),
                       queen_alive490=int(d.queen_alive490.sum()),
                       queen_survival_r490_all=float(d.queen_alive490.mean()) if len(d) else np.nan,
                       queen_survival_reached490=float(reached.queen_alive490.mean()) if len(reached) else np.nan,
                       queen_mean_len490_dead0_all=float(d.queen_len490.mean()) if len(d) else np.nan,
                       queen_mean_len490_dead0_reached=float(reached.queen_len490.mean()) if len(reached) else np.nan,
                       queen_longest490_all_games=int(d.queen_longest490.sum()),
                       queen_longest490_share_all_games=float(d.queen_longest490.mean()) if len(d) else np.nan,
                       queen_longest490_share_when_alive=(float(reached.loc[reached.queen_alive490 == 1, "queen_longest490"].mean())
                                                          if (reached.queen_alive490 == 1).any() else np.nan))
            queen_games = d[d.queen_decided == 1]
            losses = int((d.result == "loss").sum())
            row.update(queen_decided_games=len(queen_games),
                       queen_decided_wins=int((queen_games.result == "win").sum()),
                       queen_decided_losses=int((queen_games.result == "loss").sum()),
                       queen_decided_share_of_losses=(int((queen_games.result == "loss").sum()) / losses if losses else np.nan),
                       queen_verdict_consistent=int(queen_games.queen_verdict_consistent.sum()),
                       queen_winner_len_median=float(queen_games.winner_queen_final.median()) if len(queen_games) else np.nan,
                       queen_loser_len_median=float(queen_games.loser_queen_final.median()) if len(queen_games) else np.nan)
            all_map.append(row)
        totals.append(dict(panel=panel, games=len(f), wins=int((f.result == "win").sum()),
                           losses=int((f.result == "loss").sum()), draws=int((f.result == "draw").sum()),
                           expected_score=float(f.won.mean()), maps=f["map"].nunique(),
                           map_hashes=f.map_hash.nunique()))
        med = {m: float(f[m].median()) for m in METRICS}
        qreach = f[f.queen_reached490 == 1]
        totals[-1]["raw_medians"] = med
        totals[-1]["games_reached490"] = len(qreach)
        totals[-1]["queen_joint_reached_alive490"] = int(f.queen_alive490.sum())
        totals[-1]["queen_alive490_reached"] = int(qreach.queen_alive490.sum())
        totals[-1]["queen_survival_r490_all"] = float(f.queen_alive490.mean()) if len(f) else None
        totals[-1]["queen_survival_reached490"] = float(qreach.queen_alive490.mean()) if len(qreach) else None
        totals[-1]["queen_mean_len490_dead0_all"] = float(f.queen_len490.mean()) if len(f) else None
        totals[-1]["queen_longest490_all_games"] = int(f.queen_longest490.sum())
        totals[-1]["queen_longest490_share_all_games"] = float(f.queen_longest490.mean()) if len(f) else None
        alive490 = f[f.queen_alive490 == 1]
        totals[-1]["queen_longest490_share_when_alive"] = (float(alive490.queen_longest490.mean())
                                                            if len(alive490) else None)
        queen_games = f[f.queen_decided == 1]
        losses = int((f.result == "loss").sum())
        queen_losses = int((queen_games.result == "loss").sum())
        totals[-1].update(queen_decided_games=len(queen_games),
                          queen_decided_wins=int((queen_games.result == "win").sum()),
                          queen_decided_losses=queen_losses,
                          queen_decided_share_of_losses=queen_losses / losses if losses else None,
                          queen_verdict_consistent=int(queen_games.queen_verdict_consistent.sum()),
                          queen_winner_len_median=float(queen_games.winner_queen_final.median()) if len(queen_games) else None,
                          queen_loser_len_median=float(queen_games.loser_queen_final.median()) if len(queen_games) else None,
                          queen_decided_share_of_losses_map_cluster_95ci=map_cluster_ci(f, panel))
        totals[-1]["queen_mean_len490_dead0_reached"] = float(qreach.queen_len490.mean()) if len(qreach) else None
        totals[-1]["stale_gen_twin_games"] = int((f.geometry_status == "stale_gen_twin").sum())
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(all_map).to_csv(out.with_name(out.name + "-permap.csv"), index=False)
    out.write_text(json.dumps(dict(parent=BOT, runtime="unswbc 1.2.3", map_era="post-m2",
                                   panels=totals), indent=2) + "\n")
    print(json.dumps(dict(parent=BOT, runtime="unswbc 1.2.3", map_era="post-m2", panels=totals), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
