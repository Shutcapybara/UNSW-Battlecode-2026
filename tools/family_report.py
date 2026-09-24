#!/usr/bin/env python3
"""family_report - aggregate replaystats over a tournament directory.

Runs tools/ouroboros/replaystats.py (read-only) over every .replay in a
tournament output directory and aggregates per-bot style profiles:
peak units, death causes by phase, split counts and child sizes, pearls
eaten, head-to-head trade direction, final standings.

  python3 tools/family_report.py build/crossline-rr1 [--json out.json]

Bots are matched to replays via results.json (replay headers carry worker
temp paths). Only successful matches with replays are included.
"""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools" / "ouroboros"))
import replaystats  # noqa: E402


def main():
    run = Path(sys.argv[1])
    out_json = None
    if "--json" in sys.argv:
        out_json = sys.argv[sys.argv.index("--json") + 1]
    results = json.loads((run / "results.json").read_text())
    agg = defaultdict(lambda: dict(
        games=0, wins=0, deaths=Counter(), phase=Counter(), len_lost=0,
        splits=0, child_sizes=Counter(), pearls=0,
        h2h=Counter(), peak_units=[], final_units=[], final_longest=[],
        final_total=[], struck=0, hit=0, suicides=0))
    skipped = 0
    for m in results:
        if m["outcome"] == "error" or not m.get("replay"):
            skipped += 1
            continue
        path = run / m["replay"]
        if not path.is_file():
            skipped += 1
            continue
        try:
            stats = replaystats.analyse(path)
        except Exception as exc:
            print(f"skip {path.name}: {exc}", file=sys.stderr)
            skipped += 1
            continue
        for side, bot in (("A", m["team_a"]), ("B", m["team_b"])):
            a = agg[bot]
            s = stats["teams"][side]
            fin = stats["standing"][side]
            a["games"] += 1
            a["wins"] += 1 if stats["winner"] == side else 0
            a["deaths"].update(s["deaths"])
            a["phase"].update(s["deaths_phase"])
            a["len_lost"] += s["len_lost"]
            a["splits"] += s["splits"]
            a["child_sizes"].update(s["child_sizes"])
            a["pearls"] += s["pearls"]
            a["h2h"]["up"] += s["h2h_up"]
            a["h2h"]["even"] += s["h2h_even"]
            a["h2h"]["down"] += s["h2h_down"]
            a["struck"] += s["h2h_struck"]
            a["hit"] += s["h2h_hit"]
            a["suicides"] += s["suicides"]
            a["peak_units"].append(s["peak_units"])
            a["final_units"].append(fin["units"])
            a["final_longest"].append(fin["longest"])
            a["final_total"].append(fin["total"])
    med = lambda xs: sorted(xs)[len(xs) // 2] if xs else 0
    print(f"replays skipped: {skipped}\n")
    print(f"{'bot':34s} {'W/g':>7s} {'d/g':>5s} {'h2h':>4s} {'body':>4s} "
          f"{'self':>4s} {'wall':>4s} {'noact':>5s} {'spl/g':>5s} "
          f"{'children':>12s} {'p/g':>5s} {'pkU':>4s} {'finU':>4s} {'finL':>4s}")
    report = {}
    for bot, a in sorted(agg.items(), key=lambda kv: -kv[1]["wins"]):
        g = max(a["games"], 1)
        d = a["deaths"]
        child = ",".join(
            f"{lab}:{n / g:.0f}" for lab, n in (
                ("2", a["child_sizes"].get(2, 0)),
                ("3", a["child_sizes"].get(3, 0)),
                ("4+", sum(v for k, v in a["child_sizes"].items() if k >= 4)))
            if n)
        print(f"{bot:34s} {a['wins']:>3d}/{g:<3d} {sum(d.values()) / g:>5.1f} "
              f"{d.get('h2h', 0) / g:>4.1f} {d.get('body', 0) / g:>4.1f} "
              f"{d.get('self', 0) / g:>4.1f} {d.get('wall', 0) / g:>4.1f} "
              f"{d.get('noaction', 0) / g:>5.1f} {a['splits'] / g:>5.1f} "
              f"{child:>12s} {a['pearls'] / g:>5.1f} {med(a['peak_units']):>4d} "
              f"{med(a['final_units']):>4d} {med(a['final_longest']):>4d}")
        report[bot] = dict(
            games=a["games"], wins=a["wins"],
            deaths_per_game={k: round(v / g, 2) for k, v in d.items()},
            phase_deaths=dict(a["phase"]),
            splits_per_game=round(a["splits"] / g, 1),
            child_sizes={str(k): round(v / g, 1) for k, v in a["child_sizes"].items()},
            pearls_per_game=round(a["pearls"] / g, 1),
            h2h=dict(a["h2h"]), struck=a["struck"], hit=a["hit"],
            suicides=a["suicides"],
            len_lost_per_game=round(a["len_lost"] / g, 1),
            median_peak_units=med(a["peak_units"]),
            median_final_units=med(a["final_units"]),
            median_final_longest=med(a["final_longest"]),
            median_final_total=med(a["final_total"]))
    if out_json:
        Path(out_json).write_text(json.dumps(report, indent=2) + "\n")
        print(f"\nwrote {out_json}")


if __name__ == "__main__":
    main()
