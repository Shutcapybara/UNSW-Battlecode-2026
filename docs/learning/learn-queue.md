# Native learn queue (`build/learn/queue/`) — job-file format (Asahi, D-050 §8, D-052 §F)

The Asahi daemon (`tools/asahi/jobd.py`, native on the Mac, started by the user) takes jobs from the **main
checkout's** `build/learn/queue/` whenever Asahi's own queue is empty (macro §8 order: Evaluator panels first). One job
at a time, lowest file name first. Results: `build/learn/done/<name>.json` (rc, start, end, error, log path), log in
`build/learn/logs/<id>.log`, the job moves through `build/learn/running/` while it runs. Cancel a queued or running
job by creating `build/learn/queue/cancel-<id>`.

## Job kinds (anything else is rejected, never executed)

```json
{"kind": "script", "script": "tools/learn/dataset.py", "argv": ["--teachers", "v1", "--jobs", "14"],
 "heavy": true, "timeout": 28800, "by": "kageyama", "env": "learn", "id": "kageyama-teacher-rows-v1"}
```

- `script`: a file `tools/learn/<name>.py` or `tools/hinata/<name>.py` **as committed in the main checkout** (lanes
  get code there through the coherence merge). Run with `cwd` = main checkout.
- `argv`: list of strings, passed as is. No shell.
- `env`: `"learn"` (default) = `build/learn/venv` (unswbc 1.2.9, pycapnp, lightgbm, xgboost, torch, scikit-learn,
  pandas, pyarrow, duckdb, numpy; `build/learn/venv.freeze.txt` lists versions); `"main"` = the repo's `.venv`
  (unswbc 1.2.3, same engine hash, D-046 §2).
- `heavy`: true takes `build/learn/HEAVY.lock` (waits while another owner holds it). Use it for anything over a few
  minutes or more than 2 cores.
- Environment variables given to the script: `ASAHI_MAX_WORKERS=14` (use it to cap worker counts), `OMP_NUM_THREADS=14`,
  `UNSWBC` (the env's unswbc), `PYTHONUNBUFFERED=1`. Everything inherits nice 10.
- `timeout`: seconds (default 6 h); the process group is terminated at the limit (rc −15).

```json
{"kind": "setup_env", "by": "asahi"}
```

- (Re)creates `build/learn/venv` from the main venv's Python (3.13) and installs the package list above.

## Rules

- Write the file atomically (write `x.json.tmp`, then rename to `x.json`); the daemon reads `*.json` only.
- Name files `<lane>-<nn>-<slug>.json`; the id defaults to the file stem.
- Outputs belong under `build/learn/<lane>/` or the paths your card names; never under `build/asahi/`.
- The daemon does not commit, push or upload anything for learn jobs.
