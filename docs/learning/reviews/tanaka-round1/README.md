# Tanaka round 1 audit receipts

`p2-audit.json` and `p2-table.csv` reproduce the frozen development prediction metrics and count split overlap. The original training rows and OOF predictions remain in the main checkout's ignored `build/hinata/v0/fit-lq/`; their full hashes are in the receipt. No held-out outcomes were read.

`rollback-audit.json` records the start-time-cutoff reconstruction, independent bootstrap and normal plug-in power assumptions. `rollback-residuals.json` freezes the derived 596-game population used in that reconstruction, with game/series IDs, attribution and residuals; it contains no replay payload. It reproduces the reported first/last-40 summaries, but is not the old monitor's 417-game collection snapshot. `engines.json` records local artifact hashes.

From the Tanaka worktree, with the main checkout's Python environment:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 nice -n 10 /Users/alik/Documents/Projects/UNSW-Battlecode-2026/.venv/bin/python tools/tanaka/p2_audit.py --repo /Users/alik/Documents/Projects/UNSW-Battlecode-2026 --out /tmp/tanaka-p2-reproduction
nice -n 10 /Users/alik/Documents/Projects/UNSW-Battlecode-2026/.venv/bin/python tools/tanaka/rollback_audit.py --input docs/learning/reviews/tanaka-round1/rollback-residuals.json --out /tmp/tanaka-rollback-reproduction.json
```

P-2 uses NumPy, pandas, PyArrow and SciPy (one worker); rollback reproduction uses only Python's standard library. The P-2 job recomputes calibration slopes for audit, not a new value model. The original audit's sandbox disallowed changing process priority; it completed on one worker. Subsequent audits ran at nice 10. No heavy panel, decode, training or confirmation job was launched.
