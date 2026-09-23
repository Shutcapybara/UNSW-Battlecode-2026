"""Play both sides on every bundled map and save results and replays."""
from pathlib import Path
import json
import re
import subprocess

root = Path(__file__).resolve().parents[1]
out = root / "build" / "child-comparison"
out.mkdir(parents=True, exist_ok=True)
results = []
for board in sorted((root / "maps").glob("*.map")):
    for a, b in (("fry-v06-one-child", "fry-v07-two-children"), ("fry-v07-two-children", "fry-v06-one-child")):
        label = f"{board.stem}-{a}-vs-{b}"
        match = subprocess.run(
            ["unswbc", "run", str(board), str(root / "bots" / a),
             str(root / "bots" / b), "-o", str(out / f"{label}.replay")],
            cwd=root, text=True, capture_output=True, timeout=180,
        )
        log = match.stdout + match.stderr
        (out / f"{label}.log").write_text(log)
        win = re.search(r"team ([AB]) wins after (\d+) rounds", log)
        draw = re.search(r"draw", log, re.IGNORECASE)
        winner = (a if win[1] == "A" else b) if win else ("draw" if draw else "error")
        if match.returncode:
            winner = "error"
        result = dict(map=board.stem, team_a=a, team_b=b, winner=winner,
                      rounds=int(win[2]) if win else None,
                      head_to_head_deaths=log.count("lost a head-to-head"))
        results.append(result)
        (out / "results.json").write_text(json.dumps(results, indent=2) + "\n")
        print(f"{board.stem}: A={a}, B={b}: {winner}", flush=True)
        if winner == "error":
            raise RuntimeError(f"Match failed; see {out / (label + '.log')}")
print({name: sum(r['winner'] == name for r in results)
       for name in ('fry-v06-one-child', 'fry-v07-two-children', 'draw')}, flush=True)
