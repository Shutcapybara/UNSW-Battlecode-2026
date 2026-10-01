"""HB-1: run tools.analysis.features.run_panel with a longer per-game timeout (its 1800 s is hard-coded).

    .venv/bin/python tools/hb1/run_panel_long.py <run_panel args...>     (env HB1_PANEL_TIMEOUT, default 7200)

Heavy fixtures (Slithery Fight vs the Python Vibing++ mimic on the loaded shared desktop) run past 1800 s; the
scorecard then refuses to score. This fills the missing fixtures in place without editing the shared tool.
"""
import os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
_run = subprocess.run


def run(*a, **k):
    if k.get('timeout') == 1800:
        k['timeout'] = int(os.environ.get('HB1_PANEL_TIMEOUT', 7200))
    return _run(*a, **k)


subprocess.run = run
from tools.analysis.features import run_panel  # noqa: E402

sys.argv = ['run_panel'] + sys.argv[1:]
run_panel.main()
