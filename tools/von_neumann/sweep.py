#!/usr/bin/env python3
"""Von Neumann combat sweep driver.

Runs override-only variants of bots/von_neumann-x01-frozen on a fixed config
(default: the 24-game dev screen) with tools/compare_bot.py, and tallies
wins/losses plus per-game combat statistics into tools/von_neumann/sweep_results.json.

A variant is a name -> OVERRIDE dict (params.py override.py mechanism; no
source edits). Code changes get their own frozen bot dirs instead and are run
with run_one() manually.

Usage:
  .venv/bin/python -m tools.von_neumann.sweep run <experiment...>   # run named experiments
  .venv/bin/python -m tools.von_neumann.sweep table                 # print the tally table
  .venv/bin/python -m tools.von_neumann.sweep show <experiment>     # per-fixture detail

Deterministic engine: per-fixture outcomes pair exactly against the baseline
record, so deltas are attributable fixture by fixture.
"""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# Base bot for override-only variants: default the frozen x01 control; set
# VN_BASE=von_neumann-x06-info (etc.) to sweep a newer master source.
BASE = ROOT / "bots" / os.environ.get("VN_BASE", "von_neumann-x01-frozen")
CONFIG = ROOT / os.environ.get("VN_CONFIG", "configs/von_neumann/screen.toml")
OUT = ROOT / "tools" / "von_neumann" / "sweep_results.json"
SCREEN = ROOT / "configs" / "von_neumann" / "screen.toml"

# Baseline screen record (porthos-x04-policy on identical fixtures,
# run porthos-x04-policy_20260925224950114366): 19-5, per-fixture winners
# loaded lazily for pairing.
BASELINE_RUN = ROOT / "experiment_data" / "porthos-x04-policy_20260925224950114366"


def experiments():
    """name -> OVERRIDE dict. Keep every arm's rationale here, in one place."""
    return {
        # --- bounds: the two stances the study must rule on -----------------
        "pacifist": {"attack": 0, "v_hunt": 0},           # never strike, never hunt
        "berserk": {"atk_margin": -99.0, "atk_units": 1},  # trade at every contact
        # --- aggression conditioning (P1 gate shape) -------------------------
        "margin-0": {"atk_margin": 0.0},
        "margin-1": {"atk_margin": 1.0},
        "margin-2": {"atk_margin": 2.0},
        "relax-05": {"aggro_relax": 0.5},
        "relax-25": {"aggro_relax": 2.5},
        "push-0": {"aggro_push": 0.0},
        "push-4": {"aggro_push": 4.0},
        "sat-05": {"aggro_sat": 0.5},
        "sat-09": {"aggro_sat": 0.9},
        "until-100": {"aggro_until": 100},
        "until-300": {"aggro_until": 300},
        # --- threat calibration ------------------------------------------------
        "threat-05": {"w_threat": 0.5},
        "threat-15": {"w_threat": 1.5},
        "peq-09": {"p_eq": 0.9},
        "peq-05": {"p_eq": 0.5},
        "plong-06": {"p_long": 0.6},
        # --- hunting window -----------------------------------------------------
        "hunt-100": {"hunt_from": 100},
        "hunt-300": {"hunt_from": 300},
        "preymin-6": {"prey_min": 6},
        "preymin-10": {"prey_min": 10},
        "huntlen-8": {"hunt_max_len": 8},
        "vhunt-2": {"v_hunt": 2.0},
        # --- extra aggression-shape probes (added 2026-09-26 before any batch-1
        # --- outcome was read: fuller cover of the margin/units/threat axes) ----
        "margin-05neg": {"atk_margin": -0.5},
        "atkunits-1": {"atk_units": 1},
        "atkunits-5": {"atk_units": 5},
        "aggro-off": {"aggro_relax": 0.0, "aggro_push": 0.0},
        "push-1": {"aggro_push": 1.0},
        "pshort-03": {"p_short": 0.3},
        "wthreat-2": {"w_threat": 2.0},
        "hyst-hunt": {"prey_ttl": 30},
        # --- joint hunt pack: motivated by the MC_INTENT trace diagnostic
        # (zero attack-kind selections in 4 traced games -- hunting is
        # value-starved, not condition-starved); added before any hunt-arm
        # outcome was read ---------------------------------------------------
        "huntpack": {"hunt_from": 100, "prey_min": 6, "v_hunt": 2.0, "hunt_max_len": 8},
        # --- cycle 2: information-layer arms (base: von_neumann-x06-info;
        # run with VN_BASE=von_neumann-x06-info) ----------------------------
        "info-build": {"field_dual": 1, "field_room": 1},   # build only: parity
        "grad1": {"w_grad": 1},                              # INFO-1 room-normalised push
        "mb2-2": {"w_mb2": 2.0},                             # INFO-2 margin shift
        "mb2-4": {"w_mb2": 4.0},
        "tf-05": {"w_tf": 0.5},                              # INFO-3 contact-scaled threat
        "tf-10": {"w_tf": 1.0},
        "info-all": {"field_dual": 1, "field_room": 1, "w_grad": 1,
                     "w_mb2": 2.0, "w_tf": 0.5},
        # --- cycle 2 aggression re-test on the info base (union metric;
        # registered in selection_rule_cycle2.json before tf/info-all
        # outcomes were read) ----------------------------------------------
        "re-agro-off": {"aggro_relax": 0.0, "aggro_push": 0.0},
        "re-grad-push4": {"w_grad": 1, "aggro_push": 4.0},
        "re-grad-relax25": {"w_grad": 1, "aggro_relax": 2.5},
        "re-tf-grad": {"w_grad": 1, "w_tf": 0.5},
    }


def variant_dir(name):
    return ROOT / "bots" / (BASE.name.replace("von_neumann", "vn").replace("-x0", "-x0")
                            + "-" + name)


def make_variant(name, override):
    d = variant_dir(name)
    if d.exists():
        shutil.rmtree(d, ignore_errors=True)  # lanes may share arm names
    shutil.copytree(BASE, d, ignore=shutil.ignore_patterns("__pycache__"))
    (d / "override.py").write_text(
        "# Von Neumann sweep variant (auto-generated; reproducible from tools/von_neumann/sweep.py).\n"
        "OVERRIDE = %r\n" % (override,))
    ns = {}
    exec((d / "override.py").read_text(), ns)   # self-check: OVERRIDE must exist
    assert ns.get("OVERRIDE") == override, "override.py did not define OVERRIDE"
    return d


def run_one(bot_dir, config, tag):
    """Run compare_bot detached-style (subprocess, polled); return run dir."""
    env = {
        "PATH": str(Path.home() / ".local" / "bin") + ":" + __import__("os").environ["PATH"],
        "PYTHONPYCACHEPREFIX": "/tmp/vn-pycache",
    }
    cmd = [str(ROOT / ".venv/bin/python"), "tools/compare_bot.py", str(bot_dir),
           "--config", str(config)]
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"{tag}: compare_bot failed\n{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}")
    # newest run dir for this bot name
    name = Path(bot_dir).name
    runs = sorted((ROOT / "experiment_data").glob(name + "_*"))
    if not runs:
        raise RuntimeError(f"{tag}: no run dir found")
    return runs[-1], time.time() - t0


def tally(run_dir):
    botname = name_of(run_dir)
    res = json.loads((run_dir / "results.json").read_text())
    prog = json.loads((run_dir / "progress.json").read_text())
    rows = []
    for r in res:
        rows.append({
            "opponent": r["opponent"], "map": r["map"], "side": r["side"],
            "win": 1 if r["winner"] == botname else 0,
            "rounds": r["rounds"], "reason": r.get("reason"),
            "enemy_kills": r.get("candidate_enemy_kills"),
            "killed_by": r.get("candidate_killed_by_enemy"),
            "team_kills": r.get("candidate_team_kills"),
            "deaths": r.get("candidate_deaths"),
        })
    return {"progress": prog, "rows": rows}


def name_of(run_dir):
    return run_dir.name.rsplit("_", 1)[0]


def load_results():
    return json.loads(OUT.read_text()) if OUT.exists() else {}


def save_results(data):
    OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def cmd_run(names, config=None):
    config = Path(config) if config else CONFIG
    ex = experiments()
    for name in names:
        if name not in ex:
            print(f"unknown experiment {name}; known: {sorted(ex)}")
            continue
        d = make_variant(name, ex[name])
        print(f"[{name}] running screen ...", flush=True)
        run_dir, secs = run_one(d, config, name)
        t = tally(run_dir)
        data = load_results()          # reload + merge: lanes run concurrently
        data[name] = {
            "override": ex[name], "run": run_dir.name, "seconds": round(secs, 1),
            "wins": t["progress"]["wins"], "losses": t["progress"]["losses"],
            "draws": t["progress"]["draws"], "errors": t["progress"]["errors"],
            "rows": t["rows"],
        }
        save_results(data)
        shutil.rmtree(variant_dir(name), ignore_errors=True)
        print(f"[{name}] {t['progress']['wins']}-{t['progress']['losses']}"
              f"-{t['progress']['draws']} ({t['progress']['errors']} errors)"
              f" in {secs:.0f}s  run={run_dir.name}", flush=True)


def baseline_rows():
    res = json.loads((BASELINE_RUN / "results.json").read_text())
    return {(r["opponent"], r["map"], r["side"]): (1 if r["winner"] == "porthos-x04-policy" else 0)
            for r in res}


def cmd_table():
    data = load_results()
    base = baseline_rows()
    print(f"{'experiment':14s} {'W-L-D':>9s} {'vs19-5':>7s} {'flips':>6s}  {'e_kills':>7s} {'k_by':>6s} {'t_kills':>7s} {'deaths':>6s}")
    print(f"{'(baseline x01)':14s} {'19-5-0':>9s} {'   -':>7s} {'    -':>6s}")
    for name in sorted(data):
        d = data[name]
        rows = d["rows"]
        flips = sum(1 for r in rows
                    if r["win"] != base.get((r["opponent"], r["map"], r["side"]), -1))
        ek = sum(r["enemy_kills"] or 0 for r in rows) / len(rows)
        kb = sum(r["killed_by"] or 0 for r in rows) / len(rows)
        tk = sum(r["team_kills"] or 0 for r in rows) / len(rows)
        de = sum(r["deaths"] or 0 for r in rows) / len(rows)
        print(f"{name:14s} {d['wins']}-{d['losses']}-{d['draws']:>3d} {d['wins']-19:>+7d}"
              f" {flips:6d}  {ek:7.1f} {kb:6.1f} {tk:7.1f} {de:6.1f}")


def cmd_show(name):
    data = load_results()
    base = baseline_rows()
    if name not in data:
        print("unknown", name)
        return
    for r in sorted(data[name]["rows"], key=lambda r: (r["opponent"], r["map"], r["side"])):
        b = base.get((r["opponent"], r["map"], r["side"]), -1)
        mark = "=" if r["win"] == b else ("+" if r["win"] > b else "-")
        print(f"{mark} {r['opponent']:26s} {r['map']:16s} {r['side']} r{r['rounds']:>3}"
              f" kills {r['enemy_kills']:>3} lost {r['killed_by']:>3} team {r['team_kills']:>3}"
              f" deaths {r['deaths']:>3} {r['reason']}")




def _valid_override(run_dir):
    """True iff the run's frozen source snapshot has an override.py that
    actually defines OVERRIDE (guards the comment-only generator bug)."""
    botname = name_of(run_dir)
    # noqa: base tracking
    p = run_dir / "sources" / "bots" / botname / "override.py"
    if not p.exists():
        return None
    ns = {}
    try:
        exec(p.read_text(), ns)
    except Exception:
        return False
    return "OVERRIDE" in ns


def cmd_rebuild():
    """Reconstruct sweep_results.json from experiment_data/vn-x01-* run dirs.
    Entries whose frozen override.py failed to define OVERRIDE are dropped
    (the invalidated pre-fix runs; see invalidated_runs.json)."""
    ex = experiments()
    data = {}
    for run_dir in sorted((ROOT / "experiment_data").glob("vn-x01-*")):
        if not (run_dir / "results.json").exists():
            continue
        botname = name_of(run_dir)
        name = None
        for pre in ("vn-x06-info-", "vn-x01-"):
            if botname.startswith(pre):
                name = botname[len(pre):]
                break
        if name is None or name not in ex:
            continue
        v = _valid_override(run_dir)
        if v is not True:
            print(f"drop {run_dir.name}: override invalid ({v})")
            continue
        dup = data.get(name)
        if dup and dup["run"] >= run_dir.name:
            continue
        t = tally(run_dir)
        data[name] = {
            "override": ex[name], "run": run_dir.name,
            "wins": t["progress"]["wins"], "losses": t["progress"]["losses"],
            "draws": t["progress"]["draws"], "errors": t["progress"]["errors"],
            "rows": t["rows"],
        }
    save_results(data)
    print(f"rebuilt {len(data)} valid entries: {sorted(data)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    if sys.argv[1] == "run":
        cmd_run(sys.argv[2:] or sorted(experiments()))
    elif sys.argv[1] == "table":
        cmd_table()
    elif sys.argv[1] == "rebuild":
        cmd_rebuild()
    elif sys.argv[1] == "show":
        cmd_show(sys.argv[2])
    else:
        print(__doc__)
