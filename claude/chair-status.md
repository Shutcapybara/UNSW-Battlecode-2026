# Chair status — Ushijima (Phase 3)

State: ACTIVE. Updated 4 Oct 2026 15:36Z (unit 6). Next self-wake about 17:05Z. Branch `r/ushijima`; private tree
`build/ushijima/tree`, committed with `tools/ushijima/commit.sh`; pushes and merges through the keeper.

## Ladder

- **R0 passed at 14:28Z (D-053 §A). R1 and R2 are open** (`docs/learning/ladder.md`). Charter: **D-046** in
  `docs/findings/2026-09-28-director-decisions.md`. The prompts' "D-045" means D-046; the existing D-045 (learned-arm
  gate) stands with the amendments in D-046 §4.
- **D-054**: P-2's population is the manifest's (1,327 usable); the queen reach veto (P-4) is approved for a screen;
  council round 2 is open on the R2 card (P-5) and the V-legal card (P-6), due 17:00Z; Asahi is idle and the lead is
  asked to wake it.
- **D-053**: R0 passed; H-KZ12 k = 16 is the first nominee, gated on seeds 2–3; Sugawara's gated-reserve card (P-3)
  rejected for map identity; cage work parked because we lose Schooltime equally with the cage open; a card for
  the queen reach veto (H-KZ26) requested; D-052 §E withdrawn (the two map variants cannot be rebuilt).
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
- Elo trend and drift (Daichi's monitor, 13:53Z, ranked, post-m2, series bootstrap 5th/95th percentiles, inputs
  frozen): since activation −0.013 [−0.041, +0.014] (849 games, 172 series); last 40 games +0.027 [−0.066, +0.114];
  Elo 1721, rank 78 (1742 a day earlier). Schooltime by variant: cage open −0.515 [−0.565, −0.466] (27 games), cage
  closed −0.436 [−0.507, −0.353] (24). Prisoners Dilemma: ten dragons −0.044 [−0.202, +0.109] (23), template −0.166
  [−0.308, −0.010] (24).
- Reading: over the whole window the incumbent plays about at its rating; it lost about 20 Elo in a day. The losses
  are concentrated on queen maps. It is not a rollback case (D-048 §7).
- Local zero on the live maps (Rome, seeds 1–3): pool 0.804 (656–160–0 of 816), gen 0.746 (1,038–353–1 of 1,392).

## Candidates by stage

| Stage | Candidates |
|---|---|
| Proposal cards | P-2 (R1): scorer revision 2 verified by Tanaka on the earlier defects; one defect left (pin the usable ids); then Tanaka's pass line releases the claim. P-4 (queen reach veto): approved for a screen. P-5 (R2) and P-6 (V-legal): council round 2, due 17:00Z |
| Screen (seed 1) | cage C+D with E = 0: HOLD, parked. H-KZ12 curve: pool +1.5 / +0.7 / +2.6 points at k = 4 / 8 / 16, gen flat, no queen response |
| Evaluator queue (Asahi) | **idle since 13:50Z, not acting on BOARD requests.** Waiting: native executor extension; cluster change in `card.py`; parent and k = 16 on seeds 2–3; then the P-4 dial |
| Nominee (full gate) | `asahi-05-kz12-k16` (REG-002), gate on seeds 2–3, not yet run |
| Uploaded, inactive | none |
| Live screen | none. A/A dry run job 952053397eed: 68 of 136 games verified at 15:28Z, 0 runtime faults, deadline 18:54Z |

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
| Council, auditor | Tanaka (GPT), `r/tanaka` | k = 16 forecast 0.35; P-4 amend (0.30); P-2 scorer: earlier repairs verified, pinned-ids defect open; P-5 and P-6 reviews due 17:00Z |
| Council, mechanism | Sugawara (Claude), hourly at :25 | wrote P-4; reviewed P-5 (amend) and P-6 (agree); k = 16 forecast 0.35 |
| Council, probe | Nishinoya (GLM), `r/nishinoya`, native Mac | k = 16 forecast 0.40; P-4 number, P-5 and P-6 reviews due 17:00Z |
| Data | Kageyama (Claude), `r/kageyama`, Cowork VM plus cloud container | explained the scope flag (it follows the live ladder); building a 120-game development teacher set in the cloud; full teacher rows wait for the native executor |
| Learner | Hinata (Claude), Cowork VM; 2-hourly task at :35 | scorer revision 2 and per-cell counts delivered; owes the pinned-ids revision; filed P-5 and P-6 |
| Evaluator | Asahi, `r/asahi`, native executor `tools/asahi/jobd.py` | no commit or job since 13:47Z; status file still lists answered questions |
| Live ops | Daichi (Claude), `r/daichi`, Cowork VM; scheduled runs working | A/A job half done (68 of 136), no faults |

## Human-in-the-loop items (each asked once, in unit 1)

| # | Item | Status |
|---|---|---|
| H1 | Final submission time | closed: the lead handles it; no Chair-imposed freeze (D-050 §2) |
| H2 | Lane names | closed: Kageyama, Hinata, Asahi, Daichi; council Tanaka, Sugawara, Nishinoya (D-050 §1) |
| H3 | Scheduled tasks | closed: Daichi, Sugawara and Hinata units all ran after the lead's fix |
| H4 | Native post-m2 decode | closed: complete, 19,754 of 19,754 (13:55Z) |
| H5 | GPU | closed: GPU work runs on the Mac's shared memory, natively, under the heavy-job lock (D-050 §3) |
| H6 | Live ops credential: nothing needed now. The key stays on the hub, the executor stays in shadow, and Daichi works through hub controls (D-048 §1) | closed |
| H7 | Organisers' rule on training on public replays | proceeding on the assumption that it is allowed (D-050 §8); optional for the lead to confirm |
| H8 | Native execution for the Learner | replaced: jobs go through Asahi's native job daemon (D-050 §8); the lead is asked only if the daemon reload fails |
| H9 | Windows quota runner | closed: the lead does not know of one; replaced by Daichi's ledger check (D-050 §4) |
| H10 | Wake the Asahi (Evaluator) session and point it at D-053 §F and D-054: it has been idle since 13:50Z and holds the gate run and the native executor | asked 15:36Z |

## Next three decisions

1. **D-055 (after 17:00Z):** R2's feature set and offline gate (P-5), and the V-legal design (P-6).
2. **R1 result:** read P-2's confirmation when Tanaka releases it; record R1 pass or fail; score the forecasts
   (Tanaka 0.40, Sugawara 0.50, Nishinoya 0.50).
3. **First nominee:** the k = 16 gate card on seeds 2–3 (forecasts 0.35, 0.40, 0.35), once Asahi runs it; on a pass,
   upload and live screen after the A/A job.

## Cursor

Last BOARD line read: `[2026-10-04 15:29 UTC council:sugawara → tanaka, chair, asahi] P-sugawara-02 (H-KZ26):
Tanaka's AMEND accepted …` (main tree; also Kageyama's two 15:30Z lines). Own D-054 lines follow.

## Open flags

- The hub's candidate row for carthage-05 has no submission id although 14585 is live (registry REG-000).
- H-KZ26 (queen reach veto): card requested from Sugawara (D-053 §E). Kanazawa's closing line reports the premise out of sample:
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
