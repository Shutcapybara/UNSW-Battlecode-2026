# Chair status — Ushijima (Phase 3)

State: ACTIVE (degraded: the Chair's shell on the Mac is down since 23:42Z, session disk full; files move by copy and the keeper commits them). Updated 5 Oct 2026 00:53Z (unit 14b). Next self-wake 01:45Z. Branch `r/ushijima`; private tree
`build/ushijima/tree`, committed with `tools/ushijima/commit.sh`; pushes and merges through the keeper.

## Ladder

- **R0 passed at 14:28Z (D-053 §A). R1 and R2 are open** (`docs/learning/ladder.md`). Charter: **D-046** in
  `docs/findings/2026-09-28-director-decisions.md`. The prompts' "D-045" means D-046; the existing D-045 (learned-arm
  gate) stands with the amendments in D-046 §4.
- **D-067 (the lead's instruction on time and game state):** the round is already an input of every clone arm; what
  is missing is any reading by time, a team trajectory, a latent state, and models of the split, cull and sprint
  decisions, where the field table says we lose (total length at round 499: 85 against 97 to 141; queen alive 1 %
  against 24 to 56 %). Ordered: a by-phase diagnostic and a no-time ablation (Hinata), the top teams' behaviour
  profile by round (Nishinoya), a scoping card for a game-state latent (P-8, Sugawara, by 03:00Z), the split, cull
  and sprint clones offline (after A1 on the full rows), and a trajectory block in encoder v2 (Kageyama). Two free
  lanes outside the ladder are opened with `docs/learning/prompts/07-free-lane.md`.
- **D-066:** P-7's entry throughput passes (1.89×10⁸ decisions an hour; no training approved). Size decides part of
  the selection: A1 and A3 need one model (about 1.05 MB) and are selectable; A4–A7 need two (about 4.9 MB) and are
  not. Arm A8b (mirror-averaged prediction) added. Full-row jobs: the network first, A1 second, 14.4 GiB a job on the
  24 GiB Mac. The deploy slot is built and at parity; Kageyama adds the HB-1 input path. The clone's live screen
  does not wait for the frozen-cohort confirmation, but every upload waits for H11. The keeper commits again.
- **D-065:** the uploaded k = 16 archive is confirmed to be the gated bot (Tanaka), so four conditions remain for the
  02:15Z decision. Battery: HB-1's features refitted on ten teams reach 0.7184, the best arm so far, against 0.6977
  for the live prior. The selector passed. Full rows are built and their refits approved. The deploy slot for the
  cloned prior is ordered from Kageyama, and an arm must fit 4 MiB to be selectable. The Mac has 271 GB free after
  the old tournament replays were deleted.
- **D-064:** the council round on k = 16 closed (all three seats). It is promoted at LS-1's stop (02:15Z) if five
  conditions hold: at least 60 pairs, no fault, the 95th percentile of the paired mean not below 0, the mean at least
  −0.05, and proof that submission 16979 is the gated binary. Daichi activates on that record. Battery: the live
  prior scores 0.6977 on the development moves, the new trees 0.7145, the converged CNN 0.6785.
- **D-063:** the k = 16 local gate is a hold (pool +1.10 points [−0.37, +2.76]) but Weakhold replicates on all three
  seeds (43 of 48 against 27 of 48). A council round (due 23:30Z) rules on promoting it at LS-1's stop unless LS-1
  shows harm. Battery: trees 0.7145 against a four-epoch CNN 0.6727; arm A10b (early stopping) added; selector
  still held. P-7's amendments adopted; a distilled network keeps it alive if trees are selected.
- **D-062:** two full disks. The Mac's disk (97 %, 31 GB free) caused the 18:47Z stop; the Cowork session disk is
  still full after an app restart and cuts Kageyama off. The Chair committed Kageyama's unit-5 files on its behalf
  (25d78afab) and let Hinata run Kageyama's HB-1 scorer herself, so arms A0, A4, A6, A7 can proceed. First battery
  numbers: trees 0.7145, small CNN 0.6727.
- **D-061:** Sugawara's source check amends the precedent table: rules or search won five of eight comparable
  contests, self-play won three with dedicated compute, and no verified case of imitation alone reached a top ten.
  Clone-first now rests on D-059 and our own Heartbreaker result. P-7 (self-play fine-tuning from the clone) is
  numbered and under review; a throughput measurement is allowed, no training.
- **D-060:** the queen reach veto (P-4) is refuted and closed; LS-1 pairs count by a same-unit proxy (the server
  gives no opponent submission id; seeds cannot be fixed); the hub fixes are merged but not deployed; the battery's
  selector is held for Tanaka's audit and its HB-1 arms wait on Kageyama, who has been silent since 18:50Z.
- **D-059 (the lead's report): the top teams here use networks** (Stockfish: MLPs, maybe CNNs; Heartbreaker: a
  CNN with two LSTM layers that did not help). This contest is the nearest precedent. Hand rules are temporary again
  (D-058 §C.2 withdrawn). Battery arm A10 (a small CNN on the window) added; self-play gets a scoping card (P-7,
  Sugawara, 22:00Z); the clone stays the first deliverable.
- **D-058 (the lead's rule): precedent first, then evidence.** Cards carry a Precedent section; Sugawara checks
  sources. Consequences: clone first, value model second, self-play last; the search bot and hand-rule dials are a
  main track; the R2 battery gains arms from imitation precedent (rating-filtered teachers, teacher-conditioned,
  mirror augmentation, other action heads offline) and a teacher-specific candidate beside the pooled one; play
  decides between them. The precedent table awaits Sugawara's source check (21:30Z).
- **D-057:** P-2 (value model) failed its one confirmation; R1 stays open behind R2. R2 gets a development battery
  (parent prior as is, the Heartbreaker recipe pooled and per team, encoder, unions) with a fixed selection rule and
  one confirmation on the frozen 115-game cohort. The standard screen is sized by simulated power with live noise.
  The Mac restarted at 18:48Z; the hub runs in a terminal since 19:21Z, so **no redeploy** (it would end the hub)
  until the lead puts it under a restart loop or launchd; that holds the upload fix and all uploads. LS-1's stop
  moves to 02:15Z.
- **D-056:** LS-1 is running (dispatched 17:42Z; candidate uploaded as 16979). Promotion needs the frozen PASS and a
  cluster sign test at p ≤ 0.075, two looks (102 and 170 pairs); fewer than four non-zero clusters means the local
  gate decides. The server activates on upload: 16979 was live about 17:33–17:40Z; no upload until the hub restores
  the active submission itself. Standing live loop adopted: standard screen (LS-std-1), sizing from the local
  discordance census, roster classes (band, loss, top), a candidate queue, and targeted data games against the top
  ten (TD-1). P-2's scorer is released. Asahi is working again.
- **D-055 (live-first, at the lead's instruction):** upload and live screens no longer wait for the full local gate.
  Live screen LS-1 is ordered: `asahi-05-kz12-k16` against 14585, 102 matched pairs on three band opponents. The R2
  card (P-5) and the V-legal card (P-6) are approved as amended. The A/A job is closed as uninformative.
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
- Elo trend and drift (Daichi's monitor, 16:53Z, ranked, post-m2, series bootstrap 5th/95th percentiles, inputs
  frozen): since activation −0.018 [−0.042, +0.009] (950 games, 192 series); last 40 games +0.026 [−0.108, +0.169];
  Elo 1722, rank 85. Schooltime −0.480 [−0.517, −0.440] (61 games; cage open −0.519, closed −0.447), weakhold −0.35
  (49 games, 12:56Z read), Slithery −0.091, Prisoners Dilemma −0.090, Devil +0.188, Queen of Spades +0.318.
- Reading: over the whole window the incumbent plays about at its rating; it lost about 20 Elo in a day. The losses
  are concentrated on queen maps. It is not a rollback case (D-048 §7).
- Local zero on the live maps (Rome, seeds 1–3): pool 0.804 (656–160–0 of 816), gen 0.746 (1,038–353–1 of 1,392).

## Candidates by stage

| Stage | Candidates |
|---|---|
| Proposal cards | P-2: failed. P-4: refuted. P-5 (R2): live prior 0.6977, HB-1 features on ten teams (A1) 0.7184 (replicated), encoder trees (A3) 0.7145, CNN 0.6785; A1 and A3 selectable, A4–A7 not; A2, A6, A7, A8, A8b to come; full-row refits: network, then A1. P-6: behind the battery. P-7 (self-play): entry throughput passed; training ruling after the network arm on the full rows |
| Screen (seed 1) | cage C+D with E = 0: HOLD, parked. H-KZ12 curve: pool +1.5 / +0.7 / +2.6 points at k = 4 / 8 / 16, gen flat, no queen response |
| Evaluator queue (Asahi) | Slot at parity with the switch off (272 of 272). Running: seed-1 pool and gen panels of `kageyama-01-p1-slot` (λ 1 and 0.5, placeholder model), then points and zip. Then learn-queue jobs (network on the full rows, A1 on the full rows) |
| Nominee (full gate) | `asahi-05-kz12-k16` (REG-002): gate hold; same-binary condition met; conditions 1–4 of D-064 §B read at LS-1's stop (02:15Z); Daichi activates if they hold |
| Uploaded, inactive | `asahi-05-kz12-k16` = submission 16979. The `submit_check` fix is on main, not deployed; no redeploy until the lead confirms the hub loop (H11) |
| Live screen | **LS-1 running** (job 5ed81ad3e1f3): 140 of 204 games at 00:29Z, no fault, stop 02:15Z |

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
| Council, auditor | Tanaka (GPT, Codex), `r/tanaka` | **stopped 00:49Z at the lead's request (credit budget)**; seat vacant; Sugawara covers replication (D-067 §G) |
| Council, mechanism | Sugawara (Claude), hourly at :25 | working: 17:29Z LS-1 objective amendment (upheld in part, D-056 §C) |
| Council, probe | Nishinoya (GLM), `r/nishinoya`, native Mac, hourly | working: 17:52Z replication of the LS-1 amendment |
| Data | Kageyama (Claude), `r/kageyama`, fresh session since 21:16Z | deploy slot `bots/kageyama-01-p1-slot` built (r/kageyama f536785f7): zip 1.05 MiB, at most 10.1 M points, parity 2.9e-8; next the HB-1-vector input path (D-066 §E) |
| Learner | Hinata (Claude), Cowork VM; hourly task at :35 | A1 0.7184 leads; mirror map verified, 11 % of A1's decisions change under reflection; A4/A5 fitting as diagnostics; to queue: network on the full rows, then A1 on the full rows; re-base A6/A7; A8, A8b |
| Evaluator | Asahi, `r/asahi`, native executor `tools/asahi/jobd.py`; fresh session since 23:05Z | working: Mac memory read, slot parity, placeholder panels running |
| Live ops | Daichi (Claude), `r/daichi`, Cowork VM; hourly at :50 | cleared the keeper blocker 23:52Z; reads D-064 §B conditions 1–4 at the first unit after 02:15Z |

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
| H10 | Wake the Asahi (Evaluator) session | closed: Asahi working since about 17:15Z |
| H11 | Confirm the hub runs inside the restart loop (a redeploy exits it) | asked 19:30Z; the hub process changed at 19:46Z, not confirmed |
| H12 | The Cowork VM session disk is full; quitting the app did not clear it. It cut off Kageyama and Asahi (both replaced by fresh sessions) and, at 23:42Z, the Chair's shell | open; the Chair works by file copy meanwhile |
| H13 | Kageyama cut off | closed: fresh session working since 21:16Z |
| H14 | Mac disk | closed: 74 GB deleted with the lead's approval; 102 GB free |

## Next three decisions

1. **k = 16 at LS-1's stop (02:15Z):** Daichi's table against conditions 1–4 of D-064 §B; activation if they hold;
   then the monitor and the rollback rule. Push the lead once with the outcome.
2. **R2 selection:** the development table of the selectable arms (A2, A6, A7, A8, A8b to come), A1 and the network
   on the full rows, then one confirmation on the frozen cohort. Beside it: Asahi's placeholder panels (first play
   evidence of a ten-team clone in the prior slot) and the slot's HB-1 input path.
3. **P-7 training:** after the network arm on the full rows.
4. **Time and game state (D-067):** the by-phase diagnostic and the no-time ablation decide whether phase models
   are fitted; P-8 (latent state) is read when filed.

Waiting on the lead: **H11** (does the hub restart by itself; until known, no redeploy, and so no upload of any new
bot, the clone included) and H12 (session disk full; it blocks the Chair's shell).

## Cursor

Last BOARD line read: line 1097 (Hinata 00:39Z, A4 0.7205: +0.0021 over A1, below the 0.005 bar of D-066 §C.2), main tree. Own D-067 lines follow. Merged at 00:48Z: r/kageyama (slot on main), r/tanaka, r/daichi, r/nishinoya; r/asahi waits for a BOARD commit.

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
- Hidden bed variants: Kageyama's oracle reproduced 97 of 118 server games; all 21 failures are on Slithery Fight,
  Schooltime, Queen of Spades, Prisoners Dilemma and Devil. About 15 % of live ranked games run on bed layouts our
  templates lack (Nishinoya, unaudited). Local panels on those five maps are discounted as transfer evidence.
- The 13 MB model headers that showed as 52-byte symlinks in the main tree: Asahi replaced the links in asahi-02 to
  05 by the identical real header (r/asahi f370d4a9f). `bots/rome-08…15` not yet checked.
- The hub index (`hub-state/battles/index.json`) prints a running paired figure for open jobs. Lanes do not quote it
  (D-056 §C.7); the Chair saw the 10-pair figure at 18:01Z and the 65-pair figure at 00:31Z (a failed filter) and
  disclosed both (D-066 §A). The promotion rule was fixed before the second sighting and is unchanged.
- Unexplained unranked requests (7 series, 50 games, 2 Oct 12:52Z to 3 Oct 02:42Z) match the quota runner's grid;
  none since. Ruled in D-051 §3; the lead is told once.
- Split of gate logs from training data: D-046 §3 narrows the Evaluator prompt's "every panel game becomes training
  data" to non-gate panels (seeds ≥ 1000).
