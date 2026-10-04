# Chair status — Ushijima (Phase 3)

State: ACTIVE. Updated 4 Oct 2026 13:18Z (unit 4). Next self-wake about 14:20Z. Branch `r/ushijima`; private tree
`build/ushijima/tree`, committed with `tools/ushijima/commit.sh`; pushes and merges through the keeper.

## Ladder

- **Rung R0, open** (`docs/learning/ladder.md`). Charter: **D-046** in
  `docs/findings/2026-09-28-director-decisions.md`. The prompts' "D-045" means D-046; the existing D-045 (learned-arm
  gate) stands with the amendments in D-046 §4.
- R0 exit needs ten items. Eight are recorded (encoder parity, labels, leakage audit on manifest v2, split
  manifests v2, twins, battles control and monitor, registry, interval convention). Open: the decode (stopped at
  its time limit, about 4,800 games queued) and the two map variants (item 9).
- **D-052** closes council round 1: P-2's one confirmation is specified (1,328 ranked, series-clean held-out games;
  spec sha 15d79683…); the rollback rule is now a difference against the replaced submission's last 120 games;
  local gates use map × opponent clusters; the cage E = 0 screen is held; two live map variants join the pool.
- **D-051** enabled the A/A live job (running since 12:54Z, 136 dev games, deadline 18:54Z).
- **D-050** records the lead's answers: seats; no Chair-imposed freeze; GPU work on the Mac; a ledger check in place
  of the quota-runner question.
- R1: P-1 (GBT) failed in development. P-2 (logistic, Φ plus queen terms) replicates in development (Tanaka, to
  3e-16): round-limit ΔAUC against Φ +0.020 at r50, +0.056 at r250, +0.102 at r400. Its one confirmation is released
  when Hinata's scorer is fixed and passes Tanaka's audit and the population is decoded. V0b uses replay truth of
  both teams, so it is a training-time critic; R5 needs a value model on the legal encoder (V-legal card).
- **D-049** fixed the held-out maps: Autarky, Maze, Trauma.
- **D-048** answers Live ops: executor stays in shadow; the battles control may deploy with dispatch off; an A/A dry
  run comes first; the rollback reference is with the council; Rome may run the cage E = 0 screen until an Evaluator
  lane exists.

## Incumbent

- `carthage-05-free-sprint`, submission 14585, live since 2 Oct 04:22Z. Fallback `hb1-14-prior-r540`, 14265.
- Elo trend and drift (Daichi's monitor, 12:56Z, ranked, post-m2, series bootstrap 5th/95th percentiles, inputs
  frozen): since 2 Oct −0.022 [−0.053, +0.007] (690 games, 140 series); last 40 games −0.006 [−0.092, +0.065];
  Elo 1720, rank 81. Worst maps: Schooltime −0.47 [−0.52, −0.42] (41 games), weakhold −0.35 [−0.43, −0.25] (49),
  Trauma −0.19 [−0.31, −0.06] (41). Best: Tower Defense +0.41, Queen of Spades +0.30.
- Reading: the incumbent is losing ground as the field adapts. It is not a rollback case (D-048 §7); hb1-14 would
  not be better.
- Local zero on the live maps (Rome, seeds 1–3): pool 0.804 (656–160–0 of 816), gen 0.746 (1,038–353–1 of 1,392).

## Candidates by stage

| Stage | Candidates |
|---|---|
| Proposal cards | P-1 (R1, GBT): failed in development, closed. P-2 (R1, logistic): confirmation specified in D-052 §A, waiting for the scorer audit and the decode. Expected next: V-legal card and R2 card (Hinata), caged-queen reserve card (Sugawara) |
| Screen (seed 1) | cage C+D with E = 0: **HOLD** (Asahi; Schooltime queen alive 4 of 15, pool +2.2 points [−0.4, +5.2], Portals −8 of 32). Rome's E = 1 and E = 3 packages: HOLD. H-KZ12: 39.3 firings per 1,000 queen decisions at k = 16; curve running |
| Evaluator queue (Asahi) | 1. native executor extension (critical path, D-052 §F); 2. cage diagnosis; 3. the two map variants in the pool and the parent on them; 4. H-KZ12 curve (k = 8 capture running since 13:03Z); 5. the caged-queen reserve arm when its card exists |
| Nominee (full gate) | none |
| Uploaded, inactive | none |
| Live screen | none. A/A dry run job 952053397eed accepted 12:54Z (14585, dev opponents, 136 games, deadline 18:54Z) |

## Facts settled this unit

- The engine is the same binary in wheels 1.2.3, 1.2.5 and 1.2.9 (`unswbc_engine.wasm` sha256 `26e68680…a546`). The
  wheels differ only in version string, replay viewer and map templates. Results across them are comparable on the
  same maps.
- Held-out maps are frozen: Autarky, Maze, Trauma (`docs/learning/splits/heldout-maps.json`, D-049, correcting
  D-046 §3's draw). They stay out of training for the whole phase.
- The server runs the same engine: Kageyama reproduced 4 of 4 post-m2 server games turn for turn (87,830 turns).

## Seats

| Role | Lane | State |
|---|---|---|
| Chair | Ushijima (Claude) | active |
| Council, auditor | Tanaka (GPT), `r/tanaka` | round 1 reviews delivered; next: re-audit of Hinata's fixed scorer, then the pass line that releases the confirmation |
| Council, mechanism | Sugawara (Claude), hourly at :25, scheduled runs working (12:30Z unit) | round 1 reviews delivered; asked to write the caged-queen reserve card |
| Council, probe | Nishinoya (GLM), `r/nishinoya`, native Mac | P-2 review, addendum and the R0 re-runs delivered |
| Data | Kageyama (Claude), `r/kageyama`, Cowork VM plus cloud container | manifest v2, audit, map check and teacher list v1 (1,925 sides, 1,735 games) delivered; teacher rows wait for the native environment; two variant map files requested |
| Learner | Hinata (Claude), Cowork VM; 2-hourly task at :35, scheduled runs working (12:43Z unit) | P-2 confirmation prepared; two scorer defects to fix; then V-legal and R2 cards |
| Evaluator | Asahi, `r/asahi`, native executor `tools/asahi/jobd.py` | cage card delivered; H-KZ12 exposure and parity delivered; executor extension not started |
| Live ops | Daichi (Claude), `r/daichi`, Cowork VM; scheduled runs working | 14585 linked in the hub; A/A job running; monitor inputs frozen per run; asked to split Schooltime and Prisoners Dilemma by variant and to re-simulate the rollback rule |

## Human-in-the-loop items (each asked once, in unit 1)

| # | Item | Status |
|---|---|---|
| H1 | Final submission time | closed: the lead handles it; no Chair-imposed freeze (D-050 §2) |
| H2 | Lane names | closed: Kageyama, Hinata, Asahi, Daichi; council Tanaka, Sugawara, Nishinoya (D-050 §1) |
| H3 | Scheduled tasks | closed: Daichi, Sugawara and Hinata units all ran after the lead's fix |
| H4 | Native post-m2 decode | **re-opened 13:18Z:** the run ended at its 50-minute limit with about 4,800 games queued. One more run needed: `nice -n 15 python3 tools/chongqing/decode.py --jobs 6 --time 3000` from the repo root. It blocks P-2's confirmation and R0 |
| H5 | GPU | closed: GPU work runs on the Mac's shared memory, natively, under the heavy-job lock (D-050 §3) |
| H6 | Live ops credential: nothing needed now. The key stays on the hub, the executor stays in shadow, and Daichi works through hub controls (D-048 §1) | closed |
| H7 | Organisers' rule on training on public replays | proceeding on the assumption that it is allowed (D-050 §8); optional for the lead to confirm |
| H8 | Native execution for the Learner | replaced: jobs go through Asahi's native job daemon (D-050 §8); the lead is asked only if the daemon reload fails |
| H9 | Windows quota runner | closed: the lead does not know of one; replaced by Daichi's ledger check (D-050 §4) |

## Next three decisions

1. **Cage, next arm:** council round 2 on Sugawara's card for a reserve only while the queen is caged, after
   Asahi's diagnosis of the E = 0 screen.
2. **R1 result:** read P-2's confirmation when it runs; record R1 pass or fail; score the forecasts.
3. **R2 card:** council round on Hinata's behaviour-cloning direction head, once the teacher rows exist. R0 pass
   is recorded when the decode and the two map variants are done.

## Cursor

Last BOARD line read: `[2026-10-04 12:56 UTC daichi → chair, tanaka, sugawara] D-051 §4 done …` (main tree), plus
Asahi's three 12:25Z lines (merged 13:12Z). Own D-052 lines follow.

## Open flags

- The hub's candidate row for carthage-05 has no submission id although 14585 is live (registry REG-000).
- H-KZ26 (queen reach veto) has no tester and no card. Kanazawa's closing line reports the premise out of sample:
  our queen is struck in 64 of 635 reach opportunities (10.1 %) against 49 of 2,768 (1.8 %) for field queens, 201
  fresh team-7 games. It needs a card (a `temporary` dial, or the R4 block "enemy sprint reach").
- Kanazawa has closed at the lead's request. Whether Rome and Shenzhen continue is the lead's decision. Rome's interim
  permission has lapsed (D-050 §1).
- All five lane branches (`r/daichi`, `r/kageyama`, `r/asahi`, `r/tanaka`, `r/nishinoya`) were merged to `main` by
  Chair request at 11:32Z and 11:35Z. The Chair merges at each unit; BOARD.md is written only in the main tree
  (D-050 §8).
- Asahi found that the `dragons` table marks the queen dead on 24 of 544 pool sides where the engine's result block
  has it alive. Queen-survival numbers built from that table undercount; Kageyama is asked to diagnose.
- Tracked 13 MB model headers in the main tree (`bots/rome-08…15`, `bots/asahi-02…05`) show as modified: something
  replaces them with 52-byte symlinks. They are uncommitted and the keeper skips them. Asahi is asked whether its
  tooling does this.
- Unexplained unranked requests (7 series, 50 games, 2 Oct 12:52Z to 3 Oct 02:42Z) match the quota runner's grid;
  none since. Ruled in D-051 §3; the lead is told once.
- Split of gate logs from training data: D-046 §3 narrows the Evaluator prompt's "every panel game becomes training
  data" to non-gate panels (seeds ≥ 1000).
