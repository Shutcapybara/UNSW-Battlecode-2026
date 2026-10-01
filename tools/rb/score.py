#!/usr/bin/env python3
"""Lune scorecard: one row per arm, deltas against a base arm, on the live pool (field-normalised,
BENCHMARKS three-number form) and on the generalisation panel (normalised by the base arm's per-map mean,
since those maps have no field reference). Reads tools/cx/bench.py rows (tools/lune/run.py writes them).

    python3 tools/lune/score.py --arm L0=game_stats/runs/r1-L0-*.jsonl --arm L1=... --base L0 [--panel live|gen|all]
        [--probe L0=game_stats/runs/r1-probe-L0.jsonl ...] [--json OUT] [--md OUT] [--split side|size]

Duplicated fixtures (same map, side, seed, opponent) across files are counted once (first file wins).
"""
from __future__ import annotations

import argparse, bisect, glob, json, math, pathlib, statistics, sys

REPO = pathlib.Path(__file__).resolve().parents[2]
BENCH = REPO / "docs/analysis/benchmarks"
NAME = {"portals": "Portals", "schooltime": "Schooltime", "default": "Default", "autarky": "Autarky",
        "trauma": "Trauma", "dilemma": "Prisoners Dilemma", "slithery_fight": "Slithery Fight",
        "queen_of_spades": "Queen Of Spades", "trophy": "Trophy", "devil": "Devil"}
ECON = [("pearls@50", "eaten_r50"), ("pearls@100", "eaten_r100"), ("pearls@150", "eaten_r150"),
        ("pearls@250", "eaten_r250")]
SCALE = [("units@100", "units_r100"), ("total@100", "len_r100"), ("births@100", "births_r100")]
HYG = ["wall", "self", "body", "h2h", "no_action"]


def load(spec):
    rows, seen = [], set()
    for pat in spec.split(","):
        for f in sorted(glob.glob(str(REPO / pat)) or glob.glob(pat)):
            for line in open(f):
                if not line.strip():
                    continue
                d = json.loads(line)
                k = (d["map"], d["side"], d["seed"], d["opp"])
                if k in seen:
                    continue
                seen.add(k); rows.append(d)
    return rows


def key(d):
    return (d["map"], d["side"], d["seed"], d["opp"])


def pct(dist, x):
    lo, hi = bisect.bisect_left(dist, x), bisect.bisect_right(dist, x)
    return (lo + (hi - lo) / 2) / len(dist)


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def sign_p(b, w):
    n = b + w
    if n == 0:
        return 1.0
    k = min(b, w)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def score_arm(rows, refs, dists, base_means=None):
    """base_means: {(metric, map): mean} for maps without a field reference (generalisation panel)."""
    out = {"n": len(rows)}
    w = sum(r["result"] == "win" for r in rows); l = sum(r["result"] == "loss" for r in rows)
    dr = len(rows) - w - l
    out["wld"] = f"{w}-{l}-{dr}"; out["xs"] = (w + 0.5 * dr) / max(1, len(rows))
    for metric, k in ECON + SCALE:
        norm, top, pc, raw = [], [], [], []
        for r in rows:
            x = r["us"].get(k)
            if x is None:
                continue
            raw.append(x)
            fname = NAME.get(r["map"])
            if fname and fname in refs.get(metric, {}):
                ref = refs[metric][fname]
                if ref["median"]:
                    norm.append(x / ref["median"])
                if ref.get("top10"):
                    top.append(x / ref["top10"])
                dist = dists.get(metric, {}).get(fname)
                if dist:
                    pc.append(pct(dist, x))
            elif base_means is not None:
                bm = base_means.get((k, r["map"]))
                if bm:
                    norm.append(x / bm)
        out[metric] = {"raw_mean": mean(raw), "norm": mean(norm), "top10": mean(top),
                       "pct": statistics.median(pc) if pc else None}
    econ = [out[m]["norm"] for m, _ in ECON]
    out["econ_mean"] = mean(econ) if all(e is not None for e in econ) else None
    turns = sum(r["us"]["turns"] for r in rows)
    out["turns"] = turns
    for c in HYG:
        out[f"{c}_per1k"] = 1000 * sum(r["us"]["deaths"].get(c, 0) for r in rows) / max(1, turns)
    out["errors"] = sum(len(r.get("errors") or []) for r in rows)
    return out


def paired(rows, base_rows, k):
    b = {key(r): r for r in base_rows}
    better = worse = same = 0
    for r in rows:
        o = b.get(key(r))
        if not o:
            continue
        x, y = r["us"].get(k), o["us"].get(k)
        if x is None or y is None:
            continue
        better += x > y; worse += x < y; same += x == y
    return better, same, worse, sign_p(better, worse)


def probe_stats(spec):
    rows = load(spec)
    pts = [r["us"]["points"] for r in rows if r["us"].get("points")]
    if not pts:
        return None
    return {"games": len(pts), "p50": statistics.median(p["p50"] for p in pts), "p99": max(p["p99"] for p in pts),
            "max": max(p["max"] for p in pts), "boot_max": max(r["us"]["boot"]["max"] for r in rows if r["us"].get("boot")),
            "worst": max(rows, key=lambda r: r["us"]["points"]["max"])["map"],
            "errors": sum(len(r.get("errors") or []) for r in rows)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", action="append", required=True, help="LABEL=glob[,glob]")
    ap.add_argument("--base", required=True)
    ap.add_argument("--panel", default="all", choices=["live", "gen", "all"])
    ap.add_argument("--probe", action="append", default=[])
    ap.add_argument("--split", default=None, choices=[None, "side", "size"])
    ap.add_argument("--json")
    ap.add_argument("--md")
    a = ap.parse_args()
    refs = json.load(open(BENCH / "field_references.json"))
    dists = {m: {k: sorted(v) for k, v in d.items()} for m, d in json.load(open(BENCH / "field_distributions.json")).items()}
    arms = dict(x.split("=", 1) for x in a.arm)
    data = {lab: load(spec) for lab, spec in arms.items()}
    panels = ["live", "gen"] if a.panel == "all" else [a.panel]
    result, md = {}, []
    for panel in panels:
        sel = (lambda r: r["map"] in NAME) if panel == "live" else (lambda r: r["map"] not in NAME)
        groups = {"all": lambda r: True}
        if a.split == "side":
            groups = {"A": lambda r: r["side"] == "A", "B": lambda r: r["side"] == "B"}
        for g, gsel in groups.items():
            base_rows = [r for r in data[a.base] if sel(r) and gsel(r)]
            common = set(map(key, base_rows))
            for lab in data:
                common &= set(map(key, (r for r in data[lab] if sel(r) and gsel(r))))
            bm = {}
            for _, k in ECON + SCALE:
                for m in {r["map"] for r in base_rows}:
                    v = [r["us"][k] for r in base_rows if r["map"] == m and key(r) in common and r["us"].get(k) is not None]
                    if v and mean(v):
                        bm[(k, m)] = mean(v)
            tab = {}
            for lab, rows in data.items():
                rs = [r for r in rows if sel(r) and gsel(r) and key(r) in common]
                s = score_arm(rs, refs if panel == "live" else {}, dists if panel == "live" else {}, bm)
                brs = [r for r in base_rows if key(r) in common]
                for k in ("units_r100", "len_r100", "eaten_r100", "eaten_r250"):
                    s[f"pair_{k}"] = paired(rs, brs, k)
                tab[lab] = s
            result[f"{panel}:{g}"] = tab
            md.append(render(panel, g, tab, a.base, len(common)))
    probes = {x.split("=", 1)[0]: probe_stats(x.split("=", 1)[1]) for x in a.probe}
    if probes:
        result["cpu"] = probes
        md.append("\n**CPU (sandbox judge points per turn)**\n\n| arm | games | p50 | p99 | max | boot max | worst map | errors |\n|---|---:|---:|---:|---:|---:|---|---:|")
        for lab, p in probes.items():
            if p:
                md.append(f"| {lab} | {p['games']} | {p['p50']/1e6:.2f} M | {p['p99']/1e6:.2f} M | {p['max']/1e6:.2f} M | "
                          f"{p['boot_max']/1e6:.2f} M | {p['worst']} | {p['errors']} |")
    text = "\n".join(md)
    print(text)
    if a.json:
        pathlib.Path(a.json).write_text(json.dumps(result, indent=1, default=str))
    if a.md:
        pathlib.Path(a.md).write_text(text + "\n")


def render(panel, g, tab, base, n):
    b = tab[base]
    def f(v, d=3):
        return "–" if v is None else f"{v:.{d}f}"
    def dlt(lab, get, d=3):
        x, y = get(tab[lab]), get(b)
        if lab == base or x is None or y is None:
            return f(x, d)
        return f"{f(x, d)} ({x - y:+.{d}f})"
    norm_label = "÷ field median" if panel == "live" else f"÷ {base} per-map mean"
    lines = [f"\n**{panel} panel{'' if g == 'all' else ' seat ' + g} — {n} common fixtures per arm; tier 1 {norm_label}**\n",
             "| arm | W–L–D | exp. score | econ mean | p@50 | p@100 | p@150 | p@250 | dragons@100 | length@100 | births@100 |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for lab in tab:
        s = tab[lab]
        lines.append(f"| {lab} | {s['wld']} | {dlt(lab, lambda t: t['xs'])} | {dlt(lab, lambda t: t['econ_mean'])} | "
                     + " | ".join(dlt(lab, lambda t, m=m: t[m]['norm']) for m in
                                  ["pearls@50", "pearls@100", "pearls@150", "pearls@250", "units@100", "total@100", "births@100"]) + " |")
    if panel == "live":
        lines += ["", "Three-number form (mean ratio to field top-ten median / median field percentile):", "",
                  "| arm | p@50 | p@100 | p@150 | p@250 | dragons@100 | length@100 |", "|---|---|---|---|---|---|---|"]
        for lab, s in tab.items():
            lines.append(f"| {lab} | " + " | ".join(f"{f(s[m]['top10'], 2)} / {f(s[m]['pct'], 2)}" for m in
                         ["pearls@50", "pearls@100", "pearls@150", "pearls@250", "units@100", "total@100"]) + " |")
    lines += ["", "Tier 2 per 1,000 dragon-turns (body = ally + enemy body; arena does not split them) and paired fixtures vs base (better/same/worse, sign-test p):", "",
              "| arm | wall | self | body | h2h | invalid | errors | dragons@100 pairs | length@100 pairs |", "|---|---:|---:|---:|---:|---:|---:|---|---|"]
    for lab, s in tab.items():
        def rel(c):
            x, y = s[f"{c}_per1k"], b[f"{c}_per1k"]
            return f"{x:.2f}" + ("" if lab == base or not y else f" ({100 * (x - y) / y:+.0f}%)")
        pu, pl = s["pair_units_r100"], s["pair_len_r100"]
        lines.append(f"| {lab} | {rel('wall')} | {rel('self')} | {rel('body')} | {rel('h2h')} | {s['no_action_per1k']:.2f} | {s['errors']} | "
                     + ("–" if lab == base else f"{pu[0]}/{pu[1]}/{pu[2]} p={pu[3]:.3f}") + " | "
                     + ("–" if lab == base else f"{pl[0]}/{pl[1]}/{pl[2]} p={pl[3]:.3f}") + " |")
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
