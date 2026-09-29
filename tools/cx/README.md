# tools/cx — C1 chassis instruments (unswbc 1.2.2 venv: `~/.venvs/bc122/bin/python`)

Golden-decision harness (three commands):

    python3 tools/cx/golden.py record maps/trauma.map bots/yuna-v03-core bots/fenrir-v18-arrival-ready-beds --side B --seed 1 --gzip
    python3 tools/cx/golden.py replay build/cx/golden/trauma-B-1/yuna-v03-core.jsonl.gz bots/<your-bot> [--all] [--free-sonar|--ignore-sonar]
    python3 tools/cx/golden.py suite bots/<your-bot> [--transcripts build/cx/golden] [--all]

`record` plays the game through unswbc's own engine and pools (bot unchanged) and stores every dragon's init,
input blocks and replies; `replay` feeds each dragon's inputs to a fresh process of any bot and diffs the
canonical replies (LOG/INDICATOR/DOT/LINE dropped), exit 1 on the first divergence. `suite` (R-4) replays one
bot against every transcript under a directory — the Ares V04 parity run as a command, e.g. a C++ bot against
the Python-recorded reference transcripts — and exits 1 if any diverged. Reference transcripts (yuna-v03-core
vs fenrir-v18, seed 1): build/cx/golden/{schooltime-A,portals-B,slithery_fight-A,trauma-B}-1/.

Also: `arena.py` (one game: units/length r25–r250, pearls at r50/r100/r150/r250, portal steps/deaths, sprint
segments, deaths by cause, sandbox points incl. boot turn; `--json`; `replay_out=`), `bench.py` (map × side ×
seed fixtures in parallel, `--summary X --vs Y` = paired better/same/worse + sign test, `--replay-dir` writes
each .replay), `ablate.py` (exact-pair arm comparison, `--filter live|panel`, `--exclude pub/`),
`benchmarks_table.py` + `cx_f_summary.py` (the C1-F summaries), `meter.py` (sandbox parse/sense/policy/BFS
breakdown; `--mode cxx` for any bot whose sources implement the `CX_METER` stderr protocol, `auto` picks it
when they do), `view.py` (ASCII 7×7 view of a recorded turn), `build_atlas.py` (atlas.hpp from maps/*.map).

C++/Python parity (R-4): every command launches a bot through the same `_resolve`/`Project` path as `unswbc
run`, so a `bot.toml language = "c++"` directory is built once per source fingerprint (headers included) and
handled exactly like a Python one. A compile error aborts loudly — `bench.py` exits 2 before any game,
`run_panel.py` prebuilds serially and exits 2 — rather than scoring a stale build. NB unswbc 1.2.2's sandbox
wasm cache hashes only .c/.cpp files; arena.py purges a bot's cached wasm before every sandbox game so header
edits are not silently ignored. The `CX_METER` protocol: built with `-DCX_METER` (meter.py prepends `#define
CX_METER 1` to main.cpp), the bot prints `CX_METER parse=<us> sense=<us> policy=<us> bfs=<us>` to stderr once
per turn; arena.py collects the lines (`meter_prefix=`) and they never reach the engine or the replay.

Tests: `~/.venvs/bc122/bin/python -m unittest discover -s tools/cx/tests -t .` — the pure post-processing
tests run under plain python3 too; the unswbc-dependent ones skip.
