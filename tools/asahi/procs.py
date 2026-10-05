#!/usr/bin/env python3
"""List running processes on the Mac whose command line mentions a pattern (default: kenma). Read-only; kills nothing."""
import subprocess, sys
pat = sys.argv[1] if len(sys.argv) > 1 else 'kenma'
out = subprocess.run(['ps', '-axo', 'pid,etime,pcpu,command'], capture_output=True, text=True).stdout.splitlines()
hits = [l for l in out[1:] if pat in l and 'procs.py' not in l]
print(out[0]); print('\n'.join(hits) if hits else f'(no process mentions {pat!r})')
