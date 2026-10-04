# Chair status — Ushijima (Phase 3)

State: ACTIVE. Updated 4 Oct 2026 10:50Z (unit 1, first session). Branch `r/ushijima`; private tree
`build/ushijima/tree`, committed with `tools/ushijima/commit.sh`; pushes and merges through the keeper.

## Ladder

- **Rung R0, open** (`docs/learning/ladder.md`). Charter: **D-046** in
  `docs/findings/2026-09-28-director-decisions.md`. The prompts' "D-045" means D-046; the existing D-045 (learned-arm
  gate) stands with the amendments in D-046 §4.
- R0 exit needs ten items; none is closed except the registry file. The blocking ones are the post-m2 decode, the
  split manifests (D-047) and the encoder.

## Incumbent

- `carthage-05-free-sprint`, submission 14585, live since 2 Oct 04:22Z. Fallback `hb1-14-prior-r540`, 14265.
- Elo trend and drift: not measured. The live monitor does not exist yet (R0 item 8, Live ops). Last audited
  sample: 60 ranked games in 12 series, 37 wins, 12 of 23 losses queen-decided (Himeji H33-02; recovery-selected,
  not a trend).
- Local zero on the live maps (Rome, seeds 1–3): pool 0.804 (656–160–0 of 816), gen 0.746 (1,038–353–1 of 1,392).

## Candidates by stage

| Stage | Candidates |
|---|---|
| Proposal cards | none |
| Screen (seed 1) | cage C+D+E1 and C+D+E3: HOLD (Rome). H-KZ12 k = 4: partial, no verdict (Rome) |
| Evaluator queue | 1. cage C+D with E = 0; 2. H-KZ12 k = 8 and 16 plus gen diagnostics (D-046 §6) |
| Nominee (full gate) | none |
| Uploaded, inactive | none |
| Live screen | none |

## Facts settled this unit

- The engine is the same binary in wheels 1.2.3, 1.2.5 and 1.2.9 (`unswbc_engine.wasm` sha256 `26e68680…a546`). The
  wheels differ only in version string, replay viewer and map templates. Results across them are comparable on the
  same maps.
- Default held-out map draw (D-046 §3): trophy (A), maze (B), trauma (C). Held-out maps stay out of training for
  the whole phase.

## Seats

| Role | Lane | State |
|---|---|---|
| Chair | Ushijima (Claude) | active |
| Council, auditor | Tanaka (GPT), `r/tanaka` | ready; asked to audit D-046 §2, §3 and §4.3 |
| Council, mechanism | Sugawara (Claude) | active; intake answered in D-046 §11 |
| Council, probe | Nishinoya (GLM), `r/nishinoya` | active; probes answered in D-046 §11 |
| Data | not named | R0 items 1–5 and 9 wait |
| Learner | not named | encoder twin, R1 and R2 cards wait |
| Evaluator | not named | queue in D-046 §6 waits |
| Live ops | not named | `battles.json`, monitor and rosters wait |

## Human-in-the-loop items (each asked once, in unit 1)

| # | Item | Status |
|---|---|---|
| H1 | Final submission time in UTC, and which event it belongs to | asked; assuming 2026-10-11 10:30Z |
| H2 | Lane names for Data, Learner, Evaluator and Live ops | asked |
| H3 | Approve the hourly Chair scheduled task; approve the coherence task's instruction change (macro §7) | asked |
| H4 | Start the native decode: `nice -n 15 python3 tools/chongqing/decode.py --jobs 6 --time 3000` from the repo root, about 1 h, when no panel is running (queue 7,617 and growing, Nishinoya probe, unaudited) | asked |
| H5 | Tell the Chair when a GPU machine is available (R6 at scale, R7 and R8 wait for it) | asked |
| H6 | Confirm the hub's API credential is valid for Live ops, and that the executor may leave shadow mode for requested battles | asked |
| H7 | Ask the organisers whether training on other teams' public replays and fielding behaviour clones is allowed; record the answer | asked |

## Next three decisions

1. **D-047:** approve the frozen splits from Data's manifests (maps, series buckets, gate fixtures, hashes), and
   freeze the interval convention after Tanaka's audit.
2. **Cage C+D, E = 0:** advance or hold after the Evaluator's seed-1 screen; if it passes the gate, the first live
   screen and promotion decision.
3. **First council round:** the Learner's R1 and R2 cards (seats: Tanaka, Sugawara, Nishinoya).

## Open flags

- The hub's candidate row for carthage-05 has no submission id although 14585 is live (registry REG-000).
- Kanazawa's two hourly tasks are still enabled. Rome's H-KZ12 screen holds the Mac's CPU at times. Which Phase 2
  lanes continue is the lead's decision.
- Split of gate logs from training data: D-046 §3 narrows the Evaluator prompt's "every panel game becomes training
  data" to non-gate panels (seeds ≥ 1000).
