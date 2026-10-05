#!/usr/bin/env python3
"""Copy another lane's bot directory into this worktree's bots/ (untracked, read-only use) so that Asahi's panels can
run it on the same host and harness (Chair 5 Oct 04:18Z, request 3). Symlinks are resolved. Refuses an existing
target and names under asahi-/kageyama-. Writes bots/<name>/.asahi-source.json (source path, time, runtime fingerprint).

    python tools/asahi/copybot.py ../wt-kenma/bots/kenma-03-pocket-queen ../wt-bokuto/bots/bokuto-04-queen
"""
import json, os, re, shutil, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.analysis.features import run_panel as R  # noqa: E402

rc = 0
for src in sys.argv[1:]:
    s = (ROOT / src).resolve()
    name = s.name
    dst = ROOT / 'bots' / name
    if not s.is_dir() or not re.fullmatch(r'[a-z]+-[A-Za-z0-9._-]+', name) or name.startswith(('asahi-', 'kageyama-')):
        print('skip', src); rc = 1; continue
    if dst.exists():
        print('exists, not overwritten', dst); rc = 1; continue
    shutil.copytree(s, dst, symlinks=False, ignore=shutil.ignore_patterns('.unswbc-build', '__pycache__'))
    fp = R.runtime_fingerprint(dst)
    (dst / '.asahi-source.json').write_text(json.dumps(dict(source=str(s), copied=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), fingerprint=fp), indent=1))
    print('copied', s, '->', dst, 'fp', fp[:8])
sys.exit(rc)
