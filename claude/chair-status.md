# Chair status — Ushijima (Phase 3)

State: ACTIVE. Updated 4 Oct 2026 12:25Z (unit 3). Next self-wake about 13:05Z. Branch `r/ushijima`; private tree
`build/ushijima/tree`, committed with `tools/ushijima/commit.sh`; pushes and merges through the keeper.

## Ladder

- **Rung R0, open** (`docs/learning/ladder.md`). Charter: **D-046** in
  `docs/findings/2026-09-28-director-decisions.md`. The prompts' "D-045" means D-046; the existing D-045 (learned-arm
  gate) stands with the amendments in D-046 §4.
- R0 exit needs ten items. Recorded as passed or done (D-051 §5): encoder parity, action labels, regenerated twins,
  battles control and monitor, registry, held-out maps. Open: the decode (11,455 of 17,206 at 11:50Z), split
  manifest v2 on Autarky/Maze/Trauma, the leakage audit on v2, the corpus-wide map check, and the interval
  convention (D-052).
- **D-051** enables the A/A live job (one arm, 136 dev games), rules on the unexplained quota requests, and holds
  P-2's confirmation until D-052.
- **D-050** records the lead's answers: seats; no Chair-imposed freeze; GPU work on the Mac; a ledger check in place
  of the quota-runner question.
- R1: Hinata fitted two cards in development at 10:52Z, as D-047 was being merged. P-1 (GBT) failed on calibration
  and is closed. P-2 (logistic, Φ plus queen terms) passed its own amended gate in development: round-limit ΔAUC
  against Φ +0.020 at r50, +0.056 at r250, +0.102 at r400. That is discovery, not a verdict.
- **D-049** corrects the held-out maps to **Autarky, Maze, Trauma**, because the development fits had used Trophy.
  The verdict on P-2 is one confirmation on those three maps, after council round 1 (reviews due 13:00Z) and D-051.
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
| Proposal cards | P-1 (R1, GBT): failed in development, closed. P-2 (R1, logistic): development pass under its amended gate; reviews in from Tanaka (amend, hold) and Nishinoya (agree G-amend), Sugawara due 13:00Z; confirmation held |
| Screen (seed 1) | cage C+D+E1 and C+D+E3: HOLD (Rome). H-KZ12 k = 4: partial, no verdict (Rome) |
| Evaluator queue (Asahi) | parent and cage E = 0 seed-1 runs complete; the cage card is queued behind the H-KZ12 runs (asked to bring it forward); H-KZ12 k = 0 pool running since 12:08Z |
| Nominee (full gate) | none |
| Uploaded, inactive | none |
| Live screen | none. A/A dry run (14585 against itself, 136 dev games) enabled by D-051 |

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
| Council, auditor | Tanaka (GPT), `r/tanaka` | three reviews delivered 12:02Z (D-046, D-048, P-2) |
| Council, mechanism | Sugawara (Claude), hourly at :25 | active; P-2 and D-048 §8 reviews due 13:00Z |
| Council, probe | Nishinoya (GLM), `r/nishinoya`, native Mac | P-2 review and the R0 re-run delivered 11:50Z; D-048 review open |
| Data | Kageyama (Claude), `r/kageyama`, Cowork VM plus cloud container | R0 pipeline built in unit 1; manifest v2 requested |
| Learner | Hinata (Claude), Cowork VM, no branch yet; 2-hourly task at :35 | P-1 closed, P-2 awaiting confirmation; R2 and later need a native session (H8) |
| Evaluator | Asahi, `r/asahi`, native executor `tools/asahi/jobd.py` | parent panel running; P-A01 and P-A02 preregistered |
| Live ops | Daichi (Claude), `r/daichi`, Cowork VM; scheduled runs work since the lead's fix (11:50Z unit ran) | control deployed, dispatch off; A/A job enabled (D-051); link item merged |

## Human-in-the-loop items (each asked once, in unit 1)

| # | Item | Status |
|---|---|---|
| H1 | Final submission time | closed: the lead handles it; no Chair-imposed freeze (D-050 §2) |
| H2 | Lane names | closed: Kageyama, Hinata, Asahi, Daichi; council Tanaka, Sugawara, Nishinoya (D-050 §1) |
| H3 | Scheduled tasks | closed for Daichi (its 11:50Z unit ran after the lead's fix); Sugawara's 12:25Z and Hinata's 12:35Z runs are checked at the next unit |
| H4 | Native post-m2 decode | done: started by the lead, writer seen at 11:13Z; overlaps Asahi's panel once (D-050 §5) |
| H5 | GPU | closed: GPU work runs on the Mac's shared memory, natively, under the heavy-job lock (D-050 §3) |
| H6 | Live ops credential: nothing needed now. The key stays on the hub, the executor stays in shadow, and Daichi works through hub controls (D-048 §1) | closed |
| H7 | Organisers' rule on training on public replays | proceeding on the assumption that it is allowed (D-050 §8); optional for the lead to confirm |
| H8 | Native execution for the Learner | replaced: jobs go through Asahi's native job daemon (D-050 §8); the lead is asked only if the daemon reload fails |
| H9 | Windows quota runner | closed: the lead does not know of one; replaced by Daichi's ledger check (D-050 §4) |

## Next three decisions

1. **D-052:** after council round 1 closes at 13:00Z: P-2's remedy and confirmation gate (Tanaka's corrected
   G-amend is the leading option), the rollback reference (difference form, reference window 40 or 120 games), and
   the local interval convention (Tanaka: map × opponent clusters, 136 on the pool).
2. **Cage C+D, E = 0:** advance or hold when Asahi's card lands (runs are complete); if advanced, seeds 2–3, then
   the first live screen and promotion decision.
3. **R0 pass:** needs manifest v2, the audit on v2, the decode and the map check. Then the R2 card.

## Cursor

Last BOARD line read: `[2026-10-04 12:02 UTC council:tanaka → chair, asahi, kageyama] D-046 audit delivered …`
(main tree). Own D-051 lines follow.

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
- Tracked 13 MB model headers in the main tree (`bots/rome-08…15`, `bots/asahi-02…05`) show as modified: something
  replaces them with 52-byte symlinks. They are uncommitted and the keeper skips them. Asahi is asked whether its
  tooling does this.
- Unexplained unranked requests (7 series, 50 games, 2 Oct 12:52Z to 3 Oct 02:42Z) match the quota runner's grid;
  none since. Ruled in D-051 §3; the lead is told once.
- Split of gate logs from training data: D-046 §3 narrows the Evaluator prompt's "every panel game becomes training
  data" to non-gate panels (seeds ≥ 1000).
