# Porthos lineage — stable executable intentions

**Started:** 2026-09-26 (cycle 3) · **Mission:** the next-generation handoff
(`docs/monte_christo-execution-handoff.md`): formalise the execution layer
of `monte_christo-v01-core` around a small, stable set of executable
intentions, then run controlled feature/executor comparisons.
**Cycle 2:** communication v2 (directional density), policy P1
(game-relative decisions: phase, saturation, confinement), portal recon
executors — measured records below.
**Context docs:** the avery lineage handoff (environment facts),
`docs/monte_christo.md`, `docs/monte_christo-messaging.md`,
`docs/strategy-execution-handoff.md`.

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
| porthos-x03-swarm | Communication v2: directional length density (quadrant ally/enemy segment counts, `T_SWARM=7`) + monte_christo aggregate density (`T_DENSITY=6`) on idle radio rays; features v2 (phase/saturation/room-ratio globals + preview facts) computed but unused by policy; P0/E0 frozen | screen 15–9; gauntlet 113–69 (vs 112–70 control); sandbox clean; 20 swarm/radio/feature tests pass | **state/radio control** — comms v2 is win-neutral, carries the information layer for later policies |
| porthos-x04-policy | x03 with decision.py replaced by policy P1: early-saturation aggression (foragers), confinement-gated REPRODUCE, progress term scaled by resource factor | screen 19–5; gauntlet **126–56** (+13 over x03, gains spread across 5 of 7 refs); reserve 22–14 (= x03); sandbox clean | **P1 promoted over P0** on current evidence (reserve maps are development evidence, see §8.5 debt below) |
| porthos-x05-recon | x03 + intentions v2 (portal-recon objective candidates) + executors E2 (`preview_recon` self-routing, dive on portal cell) + decision v3 (one recon scoring branch); P0 base policy | screen 15–9; gauntlet 113–69 (net zero vs x03; tew −4, ouroboros −2 matchup regression); sandbox clean; trace shows real objective activity (84 approaches on trauma) | executor comparison recorded, **not promoted** — win-neutral with matchup risk |

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

## Measured records (cycle 2: x03/x04/x05)

- 24-game screen (configs/porthos/parity.toml fixtures): v01 baseline
  14–10; x03 15–9, x04 19–5, x05 15–9.  Runs
  `porthos-x03-swarm_20260925224950114152`,
  `porthos-x04-policy_20260925224950114366`,
  `porthos-x05-recon_20260925224950114045`.
- 182-game gauntlet (same config as the x02 record above), all runs 0
  errors / 0 faults:
  - x03 **113–69** (`porthos-x03-swarm_20260925231141136153`).
  - x04 **126–56** (`porthos-x04-policy_20260925231141141754`).
    Per-opponent delta vs x03: avery +2, drake +3, hunter 0, hydra −1,
    ouroboros +3, sinbad +4, tew +2.
  - x05 **113–69** (`porthos-x05-recon_20260925231141137130`).
    Per-opponent delta vs x03: tew −4, ouroboros −2, others ≈ + — net zero
    with matchup risk.
  - The 2 sinbad/big_empty timeouts per run were parallel-load wall-clock
    artifacts; retried via `--resume`, all runs complete.
- Judge sandbox (configs/monte_christo/sandbox.toml: hunter-v20 x
  arena/stronghold x both sides, candidate-side turns only), all 2–2 with
  0 faults:
  - x03 (`porthos-x03-swarm_20260926001639596856`): 31,547 turns, median
    34.31M, p99 55.34M, max 73.86M CPU points; max memory 22.1 MB.
  - x04 (`porthos-x04-policy_20260926001248106136`): 31,959 turns, median
    34.09M, p99 56.09M, max 71.12M; 22.1 MB.
  - x05 (`porthos-x05-recon_20260926001941372618`): 29,956 turns, arena
    median ~28M, stronghold median ~35M, max 76.88M; 22.2 MB.
  - Budget 100M/48MB: worst measured turn across the cycle leaves a 23.1M
    margin (x05 stronghold-B).
- Reserve validation (configs/porthos/reserve.toml.disabled: sinbad-v03-hunt,
  hunter-v20-portal-scouts, drake-v11-satutfix x 6 aramis reserve/frontier
  maps x both sides = 36 games): x03 **22–14**
  (`porthos-x03-swarm_20260926003350054457`), x04 **22–14**
  (`porthos-x04-policy_20260926003350054276`).  Identical per-cell records,
  but 22/36 individual games flipped winner between the two versions and
  35/36 differ in round count — P1 changes play substantially on these
  maps while the matchup balance nets out.  Per-opponent (both versions):
  drake 12–0, hunter 6–6, sinbad 4–8; weakest map:
  frontier_reserve_gated_rooms 2–4.
  **Caveat:** these maps are development evidence — the aramis lineage
  developed on them; a genuinely fresh map family is still owed before any
  final selection (handoff §8.5).
  The six custom map files are not present in this checkout, so the preserved
  `configs/porthos/reserve.toml.disabled` is an unavailable historical config,
  not a runnable current selection.
- Executor-objective evidence (x05): diagnostic variant
  `bots/porthos-x05-recon-trace` (`override.py {"intent_trace": 1}`, never
  deploy) on trauma recorded 84 `portal-approach` executions and 104
  predicted `dive` outcomes — the recon objective is exercised in real
  games; dives mostly complete via the legacy adjacent-dive path once in
  range.

## Architecture (cycle 2)

All three versions keep the six-stage contract and stamps from x02; only
the named modules change.

- **Communication v2 (x03, inherited by x04/x05).**  `swarm.py`: each
  observer counts visible ally/enemy segments in the four map-relative
  quadrants around itself (game-relative directional density, no cardinal
  directions in the execution layer).  Packet `T_SWARM=7`:
  `x:6 y:6 round:9 ally:4 enemy:4 quadrant:2 sender:13`.  Senders rotate
  quadrants per turn for coverage, but jump to the enemy-heaviest quadrant
  on contact using RAW counts (`swarm.CUR`) — an earlier EWMA-diluted
  signal was too sluggish and was fixed.  `density.py` (from
  monte_christo-v07, aggregate counts only; schedule/trace/gradient
  stripped) provides `T_DENSITY=6`.  `radio.py` `_reserve()` parks both
  packets on idle rays first and displaces only FOOD — never
  CROWN/PREY/PORTAL — with single-slot alternation by round parity.
  Messages are thus tagged and rotated by scenario, as briefed.
- **Features v2 (x03).**  `features.py` adds globals: game phase/early
  flag, dragon saturation, per-area stats, room ratio, alive counts and
  total lengths; and preview facts: child_room, swarm_gain, res_factor.
  P0 consumes none of them — they exist so P1-class policies compare
  against a frozen executor baseline.
- **Policy P1 (x04, decision.py only).**  `POLICY_VERSION 2`.  Three
  game-relative mechanisms, all parameterised in `P`:
  - early-saturation aggression (`aggro_until=200, aggro_sat=0.7,
    aggro_relax=1.5, aggro_push=2.0`): foragers at the dragon cap early in
    the game push into and trade against enemy density to gain space;
  - confinement-gated REPRODUCE (`split_room_norm=16,
    split_room_floor=0.3, split_sat_w=2.0`): splitting is damped by the
    relative space (room ratio) around the dragon;
  - progress term scaled by the preview `res_factor`.
  main.py `choose()` now receives the full global feature frame `gf`
  instead of `gf["threat"]`.
- **Portal recon (x05).**  Intentions v2: `recon_portals` nominates
  unpaired portal CELLs as objective-level SCOUT candidates, gated to
  foragers of length 3–6 with ≥4 units on maps ≥300 tiles before round 400
  and `MEM["tval"] < recon_tval=4.0` (deconflicts from target search).
  Executors E2: `preview_recon` self-routes via `tx.rev_dist` (a
  bfs-first-step approach was buggy for adjacent portals) and dives when
  standing on the portal cell.  Decision v3 adds one scoring branch:
  `recon_val*gamma^steps + recon_info_w*sector_unseen_frac −
  p_dive*V(L)/2`.  Portals are treated as worth exploring even when the
  exit is unknown, per the brief.

## Field notes (cycle 2)

- `timeout` does not exist on macOS — use the shell tool's own timeout.
- The sandbox x05 run died under contention from the concurrent
  athos/aramis lineage at 3/4 games; `--resume` completed it cleanly.
  Resume works per-run directory and is the right recovery for any
  interrupted comparison.
- Another lineage is using `javert_reserve_*` maps — do not touch those;
  Porthos reserve fixtures come from `configs/aramis/reserve_maps` +
  `frontier_reserve_maps`.
- Shared workspace discipline unchanged: commit only porthos bot dirs,
  `configs/porthos/`, `tests/test_porthos_*.py`, and
  `docs/porthos-lineage.md`.

## Next steps (updated)

1. **2×2 combination** P1 x E2 (x04 policy + x05 recon executors) — run
   only if the matchup-risk read on x05 (tew −4, ouroboros −2) justifies
   it; otherwise keep recon shelved and combine P1 with communication-only
   x03 state.
2. **Genuinely fresh map family** for final selection — the reserve set is
   development evidence (handoff §8.5 debt remains open).
3. **Parameter sweeps** of P1 (`aggro_*`, `split_room_*`) as `override.py`
   variants rather than new bot copies, now that the policy is the
   promoted layer.
4. Keep `porthos-x01-frozen` as the external control throughout; never edit
   a measured version — copy with a new number.

## Files

- Bots: `bots/porthos-x01-frozen`, `bots/porthos-x02-intentions`,
  `bots/porthos-x03-swarm`, `bots/porthos-x04-policy`,
  `bots/porthos-x05-recon` (READMEs carry the contract mapping and
  divergence record); `bots/porthos-x05-recon-trace` is a diagnostic-only
  variant, never deploy.
- Tests: `tests/test_porthos_intentions.py` (15 checks),
  `tests/test_porthos_swarm.py` (20 checks).
- Config: `configs/porthos/parity.toml` (3 refs x 4 maps x both sides),
  `configs/porthos/smoke.toml`, `configs/porthos/reserve.toml.disabled`.
- Reports: `build/porthos/parity-aramis-x01.json`,
  `build/porthos/parity-porthos-x02.json`, gauntlet stream check above.
- Runs: `experiment_data/porthos-x02-intentions_*`,
  `experiment_data/porthos-x03-swarm_*`,
  `experiment_data/porthos-x04-policy_*`,
  `experiment_data/porthos-x05-recon_*` (screens, gauntlets, sandbox,
  reserve; ids in the measured records above).
