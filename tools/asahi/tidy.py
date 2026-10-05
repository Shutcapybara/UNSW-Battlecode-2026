#!/usr/bin/env python3
"""Move untracked copies of other lanes' bot directories out of the Asahi worktree (into build/asahi/_old/), so that
merge_main is not blocked by "untracked working tree files would be overwritten" (job 193, 5 Oct 03:54Z). Refuses any
directory that git tracks, and any name that is not bots/kageyama-*. Used because the coordinator's VM shell is down.

    python tools/asahi/tidy.py kageyama-01b-p1-slot-fb kageyama-02b-p1-hb1-fb
"""
import re, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
old = ROOT / 'build/asahi/_old'
old.mkdir(parents=True, exist_ok=True)
rc = 0
for name in sys.argv[1:]:
    d = ROOT / 'bots' / name
    if not re.fullmatch(r'kageyama-[A-Za-z0-9._-]+', name) or not d.is_dir():
        print('skip (name or missing)', name); rc = 1; continue
    tracked = subprocess.run(['git', 'ls-files', f'bots/{name}'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if tracked:
        print('skip (tracked)', name); rc = 1; continue
    dest = old / f'{name}-{time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())}'
    shutil.move(str(d), str(dest))
    print('moved', name, '->', dest)
sys.exit(rc)
