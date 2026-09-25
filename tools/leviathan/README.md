# Leviathan lab

Run from the repository root. Everything uses Python's standard library plus the
installed `unswbc` runner. No installation or external service is needed.

```sh
PYTHONPYCACHEPREFIX=/tmp/leviathan-pycache python3 -m unittest discover -s tools/leviathan -p 'test_*.py' -v

python3 tools/leviathan/lab.py clone leviathan-v07-local-cache leviathan-v08-earlier-growth \
  --set split_until=290 --hypothesis 'Earlier growth improves final longest length on open maps'

python3 tools/leviathan/lab.py run leviathan-v08-earlier-growth \
  --vs leviathan-v07-local-cache fry-v03-portal-hunters kraken-v03-judge-safe hydra-v06-echo \
  --maps quick --output build/leviathan/v08-quick \
  --hypothesis 'Earlier growth; all other evaluation terms unchanged'

python3 tools/leviathan/lab.py run leviathan-v08-earlier-growth \
  --vs fry-v03-portal-hunters --maps arena,default,queen_of_spades \
  --sandbox --jobs 1 --timeout 600 --output build/leviathan/v08-judge

python3 tools/leviathan/lab.py compare build/leviathan/v03-population build/leviathan/v04-material
python3 tools/leviathan/replay.py build/leviathan/v04-material/000-arena-fry-v03-portal-hunters-vs-leviathan-v04-material.replay
```

`quick`: arena, default_small, default, queen_of_spades.
`holdout`: big_empty, small, schooltime, queen_of_spades_but_she_ages.
`full`: every current `maps/*.map`. Or provide comma-separated map names.
The first holdout results are now known; future tuning needs additional untouched
maps or another validation protocol. `small` is a one-round edge-case map, so its
wins should not carry the same strategic weight as full matches.

Each run saves a manifest, exact source/map snapshots, runner/harness identity,
logs, packed replays, replay diagnostics, incremental results, and a Markdown
report. Source changes during snapshotting abort the run. Worker copies protect
both the source bot folders and parallel builds. Opponent snapshots are never
written back. Existing output directories are rejected. Ctrl+C terminates this
run's workers and keeps completed results.

The comparison command matches common opponent/map/side cases and refuses changed
opponents/maps or mixed native/sandbox modes. Errors remain separate. This is a
paired descriptive comparison, not a statistical test or automatic promotion.
Keep benchmark and holdout results visible when selecting a candidate.

The replay reader supports the field subset used by local format 0/1/2 replays,
including far pointers. It skips sonar encoding differences. Live population is
checked against official final standings, and the harness cross-checks the winner,
round count, and death counts against runner logs. Final lengths are official,
not reconstructed estimates. Missing CPU metrics in replay action records are
supplemented with the runner's rounded summary; absence stays `not recorded`.

The architecture and limitations are in `docs/leviathan/DESIGN.md`; measured
outcomes and candidate selection are in `docs/leviathan/RESULTS.md`.

The four-lineage comparison is documented in `docs/leviathan/LINEAGE_REVIEW.md`.
`lineage_review.py` runs frozen-source round robins; `review_probes.py` reproduces
the review's source findings without changing bots; `review_metrics.py` extracts
birth/survival and movement events. `summarize_review.py` rebuilds the dated
review summary, audits deaths against logs, and checks snapshot consistency.

## Cycle convergence tools

The lab now defaults to a 1,200-second per-game timeout, supports any copied
reference bot as focus, and writes HANDOFF §9.3 `ledger.jsonl`. Missing native
CPU remains null. `--base`, `--cycle`, and `--map-dir` label fixtures; `--set`
merges a Python literal into **only the focus snapshot's** params.py. Source
folders are never mutated. The run manifest records overrides and effective
snapshot hashes. Choose a fresh output path for every run.

```sh
python3 tools/leviathan/lab.py run leviathan-v09-arrival \
  --vs ouroboros-v10-beacon hunter-v14-cpp-hybrid-route-spacing \
       hunter-v20-portal-scouts fry-v14-stateful-size-aware-3 kraken-v04-eval \
  --maps full --jobs 4 --base leviathan-v08-core --cycle 1 \
  --set pearl.prepos=1 --set pearl.confirmed_only=1 \
  --output build/leviathan/my-fresh-G

python3 tools/leviathan/cycle_report.py build/leviathan/my-fresh-G --phases
python3 tools/leviathan/converge.py BASE_G BASE_V --candidate CAND_G CAND_V \
  --output build/leviathan/my-comparison
python3 tools/leviathan/check_equivalence.py REFERENCE_RUN NEUTRAL_RUN
```

`cycle_report.py` provides opponent/class/side splits, per-game CPU percentile
ranges, and round-[0,30) pearl/split/population autopsies. Opening records are
cached within each immutable run. `converge.py` requires the **entire fixture
sets** to match and verifies opponent/map hashes and native/sandbox mode. It
writes every flip, including draws. Score delta uses W=1, D=.5, L=0; net W−L
delta is twice that value. Neither script promotes a bot.

`check_equivalence.py` compares both teams' movement, splits, and sonar events,
with frozen opponent/map hashes. It accepts a common subset and prints its
size, so use a complete planned set when quoting an equivalence gate.

Variant maps for cycle 1 were generated under `build/leviathan/cycle1-maps` by
importing the read-only `tools/ouroboros/mapgen.py` parse/transform/write
functions. No shared map or other line's generated-map directory is changed.
The 22 variants are all current 11 maps transposed and horizontally flipped.
See `docs/leviathan/CONVERGENCE.md` for component interfaces and remaining gaps.

## Riptide C++ experiments

The independent family is documented in `docs/leviathan/RIPTIDE.md`.
For a focus snapshot containing `main.cpp` and `params.h`, `--set key=value`
rewrites exactly one numeric/bool `constexpr auto key` declaration in the copied
header. Unknown keys, nonnumeric values and non-finite numbers are rejected.
Keep literal types consistent with the header and use its documented ranges.
The source directory stays unchanged; parameter-only variants share one folder.
`test_riptide.py` compiles and runs rule checks for both structural versions.

## Charybdis adversarial-search experiments

The new family and its local-game assumptions are documented in
`docs/leviathan/CHARYBDIS.md`. `test_charybdis.py` compiles the focused C++
transition, tactical, and budget-accounting checks. `charybdis_audit.py RUN`
records how often a completely observed duel exists, search runs, and the
selected move differs from immediate evaluation. It reports indicator coverage
instead of assuming every decision was retained in the replay.

`charybdis_report.py` checks complete planned fixture counts, frozen final-source
hashes, the no-search control's equivalence, and replay health before generating
the durable results and a standalone archive. It preserves the two earlier
compute profiles as historical evidence and does not update ACTIVE.
