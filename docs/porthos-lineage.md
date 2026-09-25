# Porthos lineage — stable executable intentions

**Started:** 2026-09-26 (cycle 3) · **Mission:** the next-generation handoff
(`docs/monte_christo-execution-handoff.md`): formalise the execution layer
of `monte_christo-v01-core` around a small, stable set of executable
intentions, then run controlled feature/executor comparisons.
**Context docs:** the avery lineage handoff (environment facts),
`docs/monte_christo.md`, `docs/monte_christo-messaging.md`.

## Environment facts used (from the avery handoff, verified this cycle)

- `export PATH="$HOME/.local/bin:$PATH"` before anything; unswbc 1.0.0.
- Run comparisons with the repo venv directly:
  `PYTHONPYCACHEPREFIX=/tmp/monte-pycache .venv/bin/python tools/compare_bot.py bots/<dir> --config <toml>`.
- Foreground shell cap ~300 s: run comparisons detached, poll
  `experiment_data/<run>/progress.json`.
- Stream equivalence:
  `.venv/bin/python tools/monte_christo/messaging/action_equivalence.py <base-run> <candidate-run> --out <json> --include-sonar`
  (source-matched replays; asserts opponent hashes match between runs).
- No pytest in the venv: `.venv/bin/python -m unittest tests.test_porthos_intentions`.
- Live shared workspace: another lineage (aramis) is attempting the same
  handoff concurrently — see "Field notes" below. Never commit other
  lineages' directories or root attachment copies.

## Versions

| Version | Change | Verification | Verdict |
|---|---|---|---|
| porthos-x01-frozen | Byte-identical copy of monte_christo-v01-core; Porthos-owned external control | parity by construction | frozen control |
| porthos-x02-intentions | Six-stage contract + six-intention menu (gather, scout, attack, retreat, feed_ally, reproduce); executor set E0, policy P0 | **24/24 identical full move/split/sonar streams** vs v01 on the 4-map parity screen; 182-game gauntlet check below; 15 scenario/contract tests pass | **E0/P0 baseline** |

## Measured records

- x02 native gauntlet (configs/monte_christo/gauntlet.toml: sinbad-v03,
  tew-v12, avery-v06, drake-v05, ouroboros-v13, hunter-v20, hydra-v09 x all
  13 maps x both sides = 182 games): **112–70–0**, 0 errors, 0 analysis
  errors, 0 runtime faults. Run
  `experiment_data/porthos-x02-intentions_20260925160727903654` (run id
  `b8ddf9221373468fbbb591f87d15acbf`).  Weakest matchups: avery-v06,
  sinbad-v03, tew-v12 at 14–12 each; the mid-cycle maps autarky/dilemma
  dominate the loss list.
- v01 control on the identical config: **112–70–0** (run
  `monte_christo-v01-core_20260925162941686304`, run id
  `8ad69be23596485e8104f5938287bb83`).  **Stream equivalence: 182/182
  identical complete move/split/sonar streams** between the two runs
  (`build/porthos/gauntlet-stream-equivalence.json`).  Combined with the
  24/24 parity screen, the x02 semantic layer has zero measured behaviour
  divergence at gauntlet scale.
- Judge (sandbox) fixtures (configs/monte_christo/sandbox.toml: hunter-v20
  x arena/stronghold x both sides; run
  `porthos-x02-intentions_20260925165410390209`, run id
  `3a7d76d2aff1432d9b70e2992cd20b6b`): 2–2, 0 faults.  **29,200 metered
  turns: median 29.71M, p99 50.23M, max 72.87M CPU points; max memory
  22.1 MB.**  The 100M/48MB budget keeps a 27.1M margin on the worst
  measured turn (v07's messaging stack peaked at 97.44M; x02 carries none
  of that).  Stronghold fixtures ran the full 500 rounds crowded; arena
  covered short elimination openings.

## Architecture (contract version 1, all stamps v1)

Frozen from v01 (byte-identical): protocol, world, tactics, comms, radio,
roles, diagnostics, risk_features.  New modules in
`bots/porthos-x02-intentions/`:

- `targets.py` — candidate support (target search), verbatim extraction +
  inert `MEM["kind"]` annotation.
- `intentions.py` — the menu and availability probes; stable candidate
  records; FEED_ALLY donation exclusive; RETREAT escape split flagged
  emergency.
- `features.py` — global features before candidates (contract-sanctioned),
  per-candidate mechanical previews; previews commit nothing.
- `decision.py` — policy P0: the v01 scoring field, expression-order
  identical (incl. the crowding loop kept in decision for float-association
  parity); despair gate `-900` admits the emergency split at `-500`.
- `executors.py` — E0: one executor per intention; execution record =
  command, predicted outcome, status/reason, trade class, path cells,
  report requests, diagnostics.  No-surviving-move selections are recorded
  (`status=fallback`, `reason=no-surviving-move`) and still emit a valid
  command.  Intentional sacrifices/trades are explicit, never filtered.
- `main.py` — six-stage assembly; crown handoff sonar attached at commit
  for ANY split (legacy parity); `LOG MC_INTENT` behind
  `P["intent_trace"]` (default 0, asserted by tests).

## Field notes

- `bots/aramis-x01-extracted` (another agent's mechanical extraction of the
  same parent) was stream-verified here as cross-lineage evidence: 24/24
  identical streams vs v01 (report `build/porthos/parity-aramis-x01.json`).
  `bots/aramis-x02-intentions` exists but is incomplete (no main.py, no
  README, uncommitted).  Porthos does not build on aramis directories; the
  verification stands as independent confirmation that the v01 behaviour is
  refactor-stable.
- The v01 behaviour survived TWO independent structural decompositions with
  identical streams — strong evidence the engine + bot are deterministic
  and the parity harness is trustworthy.

## Next steps (the controlled-comparison programme)

1. **First controlled feature comparison (P0 vs P1, E0 frozen).** Candidate
   from cross-line evidence: the avery-v08 crown-race envelope (earlier
   crown banking, wider feed window/range) as a pure policy-parameter
   change.  Executor proposals must remain unchanged on identical recorded
   inputs.  The weakest x02 matchups (avery-v06, sinbad-v03, tew-v12 at
   14–12; autarky/dilemma losses) are the fixtures to watch.
2. **First controlled executor comparison (E0 vs E1, P0 frozen).**
   Candidate: GATHER self-routing — the executor receives the nominated
   target and chooses its own bounded route (avery's trauma starvation
   evidence motivates frontier-sweep routing on kelp-maze maps).  Measure
   the executor's own objective (pearls reached/route cost) plus outcomes.
3. **2×2** E0/E1 x P0/P1 before any promotion; fresh map families for final
   selection (the 13 current maps are development evidence).  A second
   judge-budget check belongs to any E1 candidate (current margin 27.1M).
4. Keep `porthos-x01-frozen` as the external control throughout; never edit
   a measured version — copy with a new number.

## Files

- Bots: `bots/porthos-x01-frozen`, `bots/porthos-x02-intentions` (README
  carries the contract mapping and divergence record).
- Tests: `tests/test_porthos_intentions.py` (15 checks).
- Config: `configs/porthos/parity.toml` (3 refs x 4 maps x both sides).
- Reports: `build/porthos/parity-aramis-x01.json`,
  `build/porthos/parity-porthos-x02.json`, gauntlet stream check above.
- Runs: `experiment_data/porthos-x02-intentions_*` (24-game parity,
  182-game gauntlet), v01 control runs listed there.
