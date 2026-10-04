# Chair status — Ushijima (Phase 3)

State: ACTIVE. Updated 4 Oct 2026 10:59Z (unit 1, first session). Branch `r/ushijima`; private tree
`build/ushijima/tree`, committed with `tools/ushijima/commit.sh`; pushes and merges through the keeper.

## Ladder

- **Rung R0, open** (`docs/learning/ladder.md`). Charter: **D-046** in
  `docs/findings/2026-09-28-director-decisions.md`. The prompts' "D-045" means D-046; the existing D-045 (learned-arm
  gate) stands with the amendments in D-046 §4.
- R0 exit needs ten items. Done: the registry file and the held-out maps. Blocking: the post-m2 decode, the series
  and fixture manifests, and the encoder.
- R1: Hinata fitted two cards in development at 10:52Z, as D-047 was being merged. P-1 (GBT) failed on calibration
  and is closed. P-2 (logistic, Φ plus queen terms) passed its own amended gate in development: round-limit ΔAUC
  against Φ +0.020 at r50, +0.056 at r250, +0.102 at r400. That is discovery, not a verdict.
- **D-049** corrects the held-out maps to **Autarky, Maze, Trauma**, because the development fits had used Trophy.
  The verdict on P-2 is one confirmation on those three maps, after council round 1 (reviews due 13:00Z) and D-050.
- **D-048** answers Live ops: executor stays in shadow; the battles control may deploy with dispatch off; an A/A dry
  run comes first; the rollback reference is with the council; Rome may run the cage E = 0 screen until an Evaluator
  lane exists.

## Incumbent

- `carthage-05-free-sprint`, submission 14585, live since 2 Oct 04:22Z. Fallback `hb1-14-prior-r540`, 14265.
- Elo trend and drift (Daichi's monitor, first read 10:50Z, ranked only, series bootstrap 5th/95th percentiles):
  Elo 1744 → 1716 in 24 h, rank 82. Score minus Elo expectation since 2 Oct: −0.037 [−0.079, +0.003] (417 games,
  87 series, 211–206); last 40 games: −0.093 [−0.184, −0.002]. Worst maps: Schooltime −0.45 [−0.52, −0.37],
  weakhold −0.30, Trauma −0.26. Best: Tower Defense +0.37, Queen of Spades +0.23.
- Reading: the incumbent is losing ground as the field adapts. It is not a rollback case (D-048 §7); hb1-14 would
  not be better.
- Local zero on the live maps (Rome, seeds 1–3): pool 0.804 (656–160–0 of 816), gen 0.746 (1,038–353–1 of 1,392).

## Candidates by stage

| Stage | Candidates |
|---|---|
| Proposal cards | P-1 (R1, GBT): failed in development, closed. P-2 (R1, logistic): development pass under its amended gate; council round 1 open; confirmation not run |
| Screen (seed 1) | cage C+D+E1 and C+D+E3: HOLD (Rome). H-KZ12 k = 4: partial, no verdict (Rome) |
| Evaluator queue | 1. cage C+D with E = 0 (Rome may run it as interim Evaluator, D-048 §9); 2. H-KZ12 k = 8 and 16 plus gen diagnostics (D-046 §6) |
| Nominee (full gate) | none |
| Uploaded, inactive | none |
| Live screen | none |

## Facts settled this unit

- The engine is the same binary in wheels 1.2.3, 1.2.5 and 1.2.9 (`unswbc_engine.wasm` sha256 `26e68680…a546`). The
  wheels differ only in version string, replay viewer and map templates. Results across them are comparable on the
  same maps.
- Held-out maps are frozen: Autarky, Maze, Trauma (`docs/learning/splits/heldout-maps.json`, D-049, correcting
  D-046 §3's draw). They stay out of training for the whole phase.

## Seats

| Role | Lane | State |
|---|---|---|
| Chair | Ushijima (Claude) | active |
| Council, auditor | Tanaka (GPT), `r/tanaka` | ready; asked to audit D-046 §2, §3 and §4.3 |
| Council, mechanism | Sugawara (Claude) | active; intake answered in D-046 §11 |
| Council, probe | Nishinoya (GLM), `r/nishinoya` | active; probes answered in D-046 §11 |
| Data | not named | R0 items 1–5 and 9 wait |
| Learner | Hinata (Claude), Cowork VM, no branch yet; 2-hourly task at :35 | P-1 closed, P-2 awaiting confirmation; R2 and later need a native session (H8) |
| Evaluator | not named | queue in D-046 §6 waits |
| Live ops | Daichi (Claude), `r/daichi`, Cowork VM | battles control built, not deployed; monitor running; requests answered in D-048 |

## Human-in-the-loop items (each asked once, in unit 1)

| # | Item | Status |
|---|---|---|
| H1 | Final submission time in UTC, and which event it belongs to | asked; assuming 2026-10-11 10:30Z |
| H2 | Start and name the Data and Evaluator lanes (neither has reported). The Evaluator is the binding constraint: the cage arm has nobody to run it except Rome as a stopgap | asked |
| H3 | Approve the hourly Chair scheduled task; approve the coherence task's instruction change (macro §7) | asked |
| H4 | Start the native decode: `nice -n 15 python3 tools/chongqing/decode.py --jobs 6 --time 3000` from the repo root, about 1 h, when no panel is running (queue 7,617 and growing, Nishinoya probe, unaudited) | asked |
| H5 | Tell the Chair when a GPU machine is available (R6 at scale, R7 and R8 wait for it) | asked |
| H6 | Live ops credential: nothing needed now. The key stays on the hub, the executor stays in shadow, and Daichi works through hub controls (D-048 §1) | closed |
| H7 | Ask the organisers whether training on other teams' public replays and fielding behaviour clones is allowed; record the answer | asked |
| H8 | Start the Learner as a native Claude Code session on the Mac (`../wt-hinata`, branch `r/hinata`) before R2; the Cowork VM cannot do R2 and later | asked |
| H9 | Is the Windows quota runner (a second executor posting battles) switched off? Until confirmed, no candidate arm is dispatched in live tests (D-048 §5) | asked |

## Next three decisions

1. **D-050:** after council round 1 closes at 13:00Z, freeze the gate for P-2's confirmation (G-asis, G-amend or an
   amendment), decide the rollback reference (D-048 §8), and freeze the interval convention after Tanaka's audit
   note.
2. **Cage C+D, E = 0:** advance or hold after the Evaluator's seed-1 screen; if it passes the gate, the first live
   screen and promotion decision. Waits for an Evaluator lane.
3. **Split manifests:** record Data's series-bucket and gate-fixture manifests with hashes. Waits for a Data lane.

## Open flags

- The hub's candidate row for carthage-05 has no submission id although 14585 is live (registry REG-000).
- Kanazawa is wrapping up at the lead's request. Whether Rome and Shenzhen continue is the lead's decision; Rome has
  a narrow interim permission (D-048 §9).
- Split of gate logs from training data: D-046 §3 narrows the Evaluator prompt's "every panel game becomes training
  data" to non-gate panels (seeds ≥ 1000).
