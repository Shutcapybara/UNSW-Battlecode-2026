# Chair status — Ushijima (Phase 3)

State: ACTIVE. Updated 4 Oct 2026 11:37Z (unit 2, with the lead's answers). Next self-wake 12:11Z. Branch `r/ushijima`; private tree
`build/ushijima/tree`, committed with `tools/ushijima/commit.sh`; pushes and merges through the keeper.

## Ladder

- **Rung R0, open** (`docs/learning/ladder.md`). Charter: **D-046** in
  `docs/findings/2026-09-28-director-decisions.md`. The prompts' "D-045" means D-046; the existing D-045 (learned-arm
  gate) stands with the amendments in D-046 §4.
- R0 exit needs ten items. Recorded: the registry file and the held-out maps. Reported on lane branches, not yet
  recorded: encoder parity (40,002 turns, 0 mismatches), labels (100 % of 75,306 turns), leakage audit, block
  rebuild (Kageyama); four regenerated twins (Asahi); battles control built (Daichi). Running: the post-m2 decode.
  Open: split manifest v2 on the corrected maps, Nishinoya's re-run of Kageyama's tests, the corpus-wide map check,
  Tanaka's audit note.
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
| Proposal cards | P-1 (R1, GBT): failed in development, closed. P-2 (R1, logistic): development pass under its amended gate; council round 1 open; confirmation not run |
| Screen (seed 1) | cage C+D+E1 and C+D+E3: HOLD (Rome). H-KZ12 k = 4: partial, no verdict (Rome) |
| Evaluator queue (Asahi) | parent panel running since 10:59Z; then P-A01 cage C+D with E = 0 (seed-1 screen); then P-A02 H-KZ12, k = 16 exposure capture first |
| Nominee (full gate) | none |
| Uploaded, inactive | none |
| Live screen | none |

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
| Council, auditor | Tanaka (GPT), `r/tanaka` | ready; asked to audit D-046 §2, §3 and §4.3, and to review P-2 and D-048 §8 by 13:00Z |
| Council, mechanism | Sugawara (Claude), hourly at :25 | active; P-2 and D-048 §8 reviews due 13:00Z |
| Council, probe | Nishinoya (GLM), `r/nishinoya`, native Mac | active; reviews due 13:00Z; asked to re-run Kageyama's parity, label and audit tests |
| Data | Kageyama (Claude), `r/kageyama`, Cowork VM plus cloud container | R0 pipeline built in unit 1; manifest v2 requested |
| Learner | Hinata (Claude), Cowork VM, no branch yet; 2-hourly task at :35 | P-1 closed, P-2 awaiting confirmation; R2 and later need a native session (H8) |
| Evaluator | Asahi, `r/asahi`, native executor `tools/asahi/jobd.py` | parent panel running; P-A01 and P-A02 preregistered |
| Live ops | Daichi (Claude), `r/daichi`, Cowork VM | battles control built, not deployed; monitor running; requests answered in D-048 |

## Human-in-the-loop items (each asked once, in unit 1)

| # | Item | Status |
|---|---|---|
| H1 | Final submission time | closed: the lead handles it; no Chair-imposed freeze (D-050 §2) |
| H2 | Lane names | closed: Kageyama, Hinata, Asahi, Daichi; council Tanaka, Sugawara, Nishinoya (D-050 §1) |
| H3 | Scheduled tasks. The Chair now wakes itself in its own session, and merges lane branches itself, so neither the Chair task nor the coherence edit is needed. **Open: the tasks "Sugawara council unit (:25)", "Daichi Live ops unit (:50)" and "Hinata Learner unit (2-hourly, :35)" are not tied to the Mac.** Sugawara's 11:25Z run ended after 27 s and wrote nothing. Each needs "Require this computer" switched on in the desktop app | open |
| H4 | Native post-m2 decode | done: started by the lead, writer seen at 11:13Z; overlaps Asahi's panel once (D-050 §5) |
| H5 | GPU | closed: GPU work runs on the Mac's shared memory, natively, under the heavy-job lock (D-050 §3) |
| H6 | Live ops credential: nothing needed now. The key stays on the hub, the executor stays in shadow, and Daichi works through hub controls (D-048 §1) | closed |
| H7 | Organisers' rule on training on public replays | proceeding on the assumption that it is allowed (D-050 §8); optional for the lead to confirm |
| H8 | Native execution for the Learner | replaced: jobs go through Asahi's native job daemon (D-050 §8); the lead is asked only if the daemon reload fails |
| H9 | Windows quota runner | closed: the lead does not know of one; replaced by Daichi's ledger check (D-050 §4) |

## Next three decisions

1. **D-051:** after council round 1 closes at 13:00Z, freeze the gate for P-2's confirmation (G-asis, G-amend or an
   amendment), decide the rollback reference (D-048 §8), and freeze the interval convention after Tanaka's audit
   note.
2. **Cage C+D, E = 0:** advance or hold after Asahi's seed-1 screen (P-A01); if it passes the gate, the first live
   screen and promotion decision.
3. **R0 pass:** record the encoder, label and audit gates and the v2 split manifests once they are on `main`,
   re-run by Nishinoya, and the decode is complete. Then the R2 card.

## Cursor

Last BOARD line read: `[2026-10-04 11:20 UTC kageyama → chair, hinata, tanaka] splits manifest …` (main tree), plus
Asahi's two 11:10Z lines on `r/asahi`. Own D-050 lines follow.

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
- Rome's eight `bots/rome-*/hb1_direction_compact.hpp` files in the main tree were replaced by 52-byte symlinks at
  10:40Z by an unknown lane. They are uncommitted and the keeper skips them. Left as they are.
- Split of gate logs from training data: D-046 §3 narrows the Evaluator prompt's "every panel game becomes training
  data" to non-gate panels (seeds ≥ 1000).
