#!/usr/bin/env python3
"""rb lane (Aline lineage) gate: run the D-032 panels for a bot and score it against its parent.

    PY=~/Documents/Projects/2026/UNSW-Battlecode-2026/.venv/bin/python
    $PY tools/rb/gate.py run   BOT [--panel z1|gen|both] [--seeds 1,2,3] [--jobs N]
    $PY tools/rb/gate.py score BOT --parent PARENT [--seeds 1,2,3] [--json OUT]

Panels (fixed): z1 = run_panel.ZOO (8) x 10 live maps x both seats (160 / seed);
gen = GEN_OPPS (4) x maps/new/* + maps/var/*_tr (29) x both seats (232 / seed).
Rows are tools/rb/run.py (lune arena) rows under build/rb/runs/<BOT>-<panel>.jsonl.

Economy, per side-game: each of pearls@50/100/150/250 divided by a per-map reference, then the mean of the four
(econ). Pool reference = the field per-map median (docs/analysis/benchmarks/field_references.json, the
BENCHMARKS yardstick); gen reference = the parent's per-map mean on the common fixtures (1.0 = parent). units@100
and length@100 are normalised the same way. Deltas are paired on (map, side, seed, opp); intervals are a paired
bootstrap over fixtures (2000 resamples, 90 %: 5th..95th percentile).

Gate (D-032): ACCEPT iff pool d(econ) lo > 0; gen d(econ) lo > -0.02; units@100 and length@100 lo >= -0.02
(pool and gen); no tier-2 death rate (wall/self/body/h2h per 1k dragon-turns, pool and gen) up > 10 %; win rate
lo > -0.02 (gen = the panel; pool reported and held to the same bound). HOLD = gate fails only on economy
(flat: pool d(econ) interval straddles 0) and tier-2 is better.
"""
from __future__ import annotations

import argparse, json, os, pathlib, subprocess, sys

import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[2]
RUNS = REPO / "build/rb/runs"
GEN_OPPS = ['yuna-v05-core', 'chaewon-y04-probe', 'fenrir-v18-arrival-ready-beds', 'ares-v06-expanded-search-support']
NAME = {"portals": "Portals", "schooltime": "Schooltime", "default": "Default", "autarky": "Autarky",
        "trauma": "Trauma", "dilemma": "Prisoners Dilemma", "slithery_fight": "Slithery Fight",
        "queen_of_spades": "Queen Of Spades", "trophy": "Trophy", "devil": "Devil"}
ECON = [("p@50", "eaten_r50", "pearls@50"), ("p@100", "eaten_r100", "pearls@100"),
        ("p@150", "eaten_r150", "pearls@150"), ("p@250", "eaten_r250", "pearls@250")]
SCALE = [("units@100", "units_r100", "units@100"), ("length@100", "len_r100", "total@100")]
HYG = ["wall", "self", "body", "h2h"]


def out_path(bot, panel):
    return RUNS / f"{bot}-{panel}.jsonl"


def cmd_run(a):
    panels = ["z1", "gen"] if a.panel == "both" else [a.panel]
    for p in panels:
        cmd = [sys.executable, str(REPO / "tools/rb/run.py"), f"bots/{a.bot}", "--panel", p, "--seeds", a.seeds,
               "--out", str(out_path(a.bot, p)), "--jobs", str(a.jobs)]
        if p == "gen":
            cmd += ["--opps", ",".join(GEN_OPPS)]
        print(" ".join(cmd), flush=True)
        subprocess.run(cmd, cwd=REPO, check=True)


def load(bot, panel, seeds):
    f = out_path(bot, panel)
    rows = {}
    if f.exists():
        for line in f.read_text().splitlines():
            if line.strip():
                d = json.loads(line)
                if d["seed"] in seeds:
                    rows.setdefault((d["map"], d["side"], d["seed"], d["opp"]), d)
    return rows


def win(d):
    return {"win": 1.0, "draw": 0.5, "loss": 0.0}[d["result"]]


def boot(delta, n=2000, seed=11):
    delta = np.asarray(delta, float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(delta), (n, len(delta)))
    m = delta[idx].mean(axis=1)
    return float(delta.mean()), float(np.percentile(m, 5)), float(np.percentile(m, 95))


def cluster_boot(keys, delta, n=2000, seed=13):
    """robustness check: resample (map, side, opp) clusters with all their seeds together"""
    cl = {}
    for i, k in enumerate(keys):
        cl.setdefault((k[0], k[1], k[3]), []).append(i)
    groups = list(cl.values())
    delta = np.asarray(delta, float)
    sums = np.array([delta[g].sum() for g in groups]); cnts = np.array([len(g) for g in groups])
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(groups), (n, len(groups)))
    m = sums[idx].sum(axis=1) / cnts[idx].sum(axis=1)
    return float(np.percentile(m, 5)), float(np.percentile(m, 95))


def panel_stats(C, P, panel):
    keys = sorted(set(C) & set(P))
    if not keys:
        return None
    refs = json.load(open(REPO / "docs/analysis/benchmarks/field_references.json")) if panel == "z1" else None
    pm = {}
    if panel == "gen":
        for _, k, _ in ECON + SCALE:
            for m in {x[0] for x in keys}:
                v = [P[x]["us"][k] for x in keys if x[0] == m]
                pm[(k, m)] = max(1.0, float(np.mean(v)))

    def norm(d, k, ref_name, m):
        x = d["us"][k]
        if panel == "z1":
            r = refs[ref_name][NAME[m]]["median"]
            return x / r if r else np.nan
        return x / pm[(k, m)]

    out = {"n": len(keys)}
    cols = {}
    for lab, k, rn in ECON + SCALE:
        c = np.array([norm(C[x], k, rn, x[0]) for x in keys]); p = np.array([norm(P[x], k, rn, x[0]) for x in keys])
        cols[lab] = (c, p)
        out[lab] = dict(cand=float(np.nanmean(c)), parent=float(np.nanmean(p)), ci=boot(c - p))
    ce = np.mean([cols[l][0] for l, _, _ in ECON], axis=0); pe = np.mean([cols[l][1] for l, _, _ in ECON], axis=0)
    out["econ"] = dict(cand=float(ce.mean()), parent=float(pe.mean()), ci=boot(ce - pe))
    cw = np.array([win(C[x]) for x in keys]); pw = np.array([win(P[x]) for x in keys])
    out["win"] = dict(cand=float(cw.mean()), parent=float(pw.mean()), ci=boot(cw - pw))
    out["cluster"] = {"econ": cluster_boot(keys, ce - pe), "win": cluster_boot(keys, cw - pw),
                      "units@100": cluster_boot(keys, cols["units@100"][0] - cols["units@100"][1]),
                      "length@100": cluster_boot(keys, cols["length@100"][0] - cols["length@100"][1])}
    for side, arr in (("cand", C), ("parent", P)):
        turns = sum(arr[x]["us"]["turns"] for x in keys)
        for h in HYG:
            out.setdefault("hyg", {}).setdefault(h, {})[side] = 1000 * sum(arr[x]["us"]["deaths"].get(h, 0) for x in keys) / max(1, turns)
    out["errors"] = sum(len(C[x].get("errors") or []) for x in keys)
    # per-map econ delta (diagnostic)
    mp = {}
    for i, x in enumerate(keys):
        mp.setdefault(x[0], []).append(ce[i] - pe[i])
    out["map_econ"] = {m: float(np.mean(v)) for m, v in sorted(mp.items())}
    return out


def gate(S):
    why, ok = [], True
    z, g = S.get("z1"), S.get("gen")
    if not z or not g:
        return "INCOMPLETE", ["missing panel"]
    if z["econ"]["ci"][1] <= 0:
        ok = False; why.append(f"pool econ lo {z['econ']['ci'][1]:+.3f} <= 0")
    if g["econ"]["ci"][1] <= -0.02:
        ok = False; why.append(f"gen econ lo {g['econ']['ci'][1]:+.3f} <= -0.02")
    for pn, s in (("pool", z), ("gen", g)):
        for c in ("units@100", "length@100"):
            if s[c]["ci"][1] < -0.02:
                ok = False; why.append(f"{pn} {c} lo {s[c]['ci'][1]:+.3f}")
        for h, v in s["hyg"].items():
            if v["parent"] > 0.05 and v["cand"] > 1.10 * v["parent"]:
                ok = False; why.append(f"{pn} {h} deaths +{100 * (v['cand'] / v['parent'] - 1):.0f}%")
        if s["win"]["ci"][1] <= -0.02:
            ok = False; why.append(f"{pn} win lo {s['win']['ci'][1]:+.3f}")
        if s["errors"]:
            ok = False; why.append(f"{pn} {s['errors']} bot errors")
    if ok:
        return "ACCEPT", why
    econ_only = all(w.startswith("pool econ") for w in why)
    hyg_better = any(v["cand"] < 0.9 * v["parent"] for s in (z, g) for v in s["hyg"].values() if v["parent"] > 0.05)
    if econ_only and z["econ"]["ci"][2] > 0 and hyg_better:
        return "HOLD", why
    return "REJECT", why


def fmt(ci, d=3):
    return f"{ci[0]:+.{d}f} [{ci[1]:+.{d}f},{ci[2]:+.{d}f}]"


def cmd_score(a):
    seeds = [int(s) for s in a.seeds.split(",")]
    S = {}
    for p in ("z1", "gen"):
        s = panel_stats(load(a.bot, p, seeds), load(a.parent, p, seeds), p)
        if s:
            S[p] = s
    v, why = gate(S)
    print(f"== {a.bot} vs {a.parent}, seeds {seeds}")
    for p, s in S.items():
        print(f"[{p}] n={s['n']}  econ {s['econ']['cand']:.3f} vs {s['econ']['parent']:.3f}  d {fmt(s['econ']['ci'])}")
        print("   " + "  ".join(f"{l} {fmt(s[l]['ci'])}" for l, _, _ in ECON))
        print("   " + "  ".join(f"{l} {fmt(s[l]['ci'])}" for l, _, _ in SCALE) + f"  win {s['win']['cand']:.3f} d {fmt(s['win']['ci'])}")
        print("   cluster-bootstrap 90 % (fixture clusters, all seeds together): " + "  ".join(f"{k} [{v[0]:+.3f},{v[1]:+.3f}]" for k, v in s["cluster"].items()))
        print("   tier2/1k " + "  ".join(f"{h} {x['cand']:.2f}/{x['parent']:.2f}" for h, x in s["hyg"].items()) + f"  errors {s['errors']}")
        print("   map econ d " + " ".join(f"{m.split('/')[-1][:14]}:{d:+.3f}" for m, d in s["map_econ"].items()))
    print("VERDICT", v, "; ".join(why))
    S["verdict"], S["why"] = v, why
    if a.json:
        pathlib.Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(a.json).write_text(json.dumps(S, indent=1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run"); r.add_argument("bot"); r.add_argument("--panel", default="both")
    r.add_argument("--seeds", default="1,2,3"); r.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 4) - 2))
    s = sub.add_parser("score"); s.add_argument("bot"); s.add_argument("--parent", required=True)
    s.add_argument("--seeds", default="1,2,3"); s.add_argument("--json")
    a = ap.parse_args()
    cmd_run(a) if a.cmd == "run" else cmd_score(a)


if __name__ == "__main__":
    main()
