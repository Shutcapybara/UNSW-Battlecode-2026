"""Run a Godel screen arm to completion, resuming across invocations.

Usage: .venv/bin/python tools/godel/run_screen.py bots/<variant> [config]

Each invocation runs compare_bot.py (or --resume) once. The caller loops
until this prints STATUS complete. compare_bot.py saves after every game, so
a killed call loses at most the in-flight games; resume retries them.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV = dict(os.environ, PATH=os.path.expanduser("~/.local/bin") + ":" + os.environ["PATH"])


def latest_run(name, config_text):
    """Latest run of this bot on THIS config (matched by archived TOML text)."""
    runs = sorted((ROOT / "experiment_data").glob(name + "_*"), key=lambda p: p.name)
    for run in reversed(runs):
        archived = run / "comparison.toml"
        if archived.is_file() and archived.read_text() == config_text:
            return run
    return None


def main():
    bot = Path(sys.argv[1])
    config = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("configs/godel/screen.toml")
    jobs = sys.argv[3] if len(sys.argv) > 3 else None
    config_text = (ROOT / config).read_text()
    name = bot.name
    run = latest_run(name, config_text)
    if run and (run / "progress.json").is_file():
        prog = json.loads((run / "progress.json").read_text())
        if prog.get("status") == "complete":
            print("STATUS complete", prog["wins"], "-", prog["losses"], "-", prog["draws"],
                  "errors", prog["errors"], "analysis_errors", prog["analysis_errors"])
            print("RUN", run)
            return 0
        cmd = [str(ROOT / ".venv/bin/python"), "tools/compare_bot.py", "--resume", str(run)]
    else:
        cmd = [str(ROOT / ".venv/bin/python"), "tools/compare_bot.py", str(bot), "--config", str(config)]
        if jobs:
            cmd += ["--jobs", jobs]
    subprocess.run(cmd, cwd=ROOT, env=ENV)
    run = latest_run(name, config_text)
    prog = json.loads((run / "progress.json").read_text())
    print("STATUS", prog["status"], prog["recorded"], "/", prog["scheduled"],
          prog["wins"], "-", prog["losses"], "-", prog["draws"])
    print("RUN", run)
    return 0 if prog["status"] == "complete" else 1


if __name__ == "__main__":
    sys.exit(main())
