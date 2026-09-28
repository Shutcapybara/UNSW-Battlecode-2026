#!/usr/bin/env python3
"""make_arm.py PARENT NEW 'key=value' ... : copy a bot and append overrides to override.py."""
import sys, shutil, ast
from pathlib import Path
par, new, *kv = sys.argv[1:]
src, dst = Path('bots') / par, Path('bots') / new
if dst.exists(): shutil.rmtree(dst)
shutil.copytree(src, dst, ignore=shutil.ignore_patterns('__pycache__', '.unswbc-build'))
extra = {}
for s in kv:
    k, v = s.split('=', 1)
    try: extra[k] = ast.literal_eval(v)
    except Exception: extra[k] = v
with open(dst / 'override.py', 'a') as f:
    f.write(f'\nOVERRIDE.update({extra!r})  # {new}\n')
(dst / 'README.md').write_text(f'# {new}\n\nParent: `{par}`. Overrides: `{extra!r}`.\nSee experiment_data/temporal_policy_20260927T173800Z_yuna/ for manifests and results.\n')
print(dst, extra)
