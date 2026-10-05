# Chair status — Ushijima (Phase 3)

State: ACTIVE (the Chair's device shell still fails after the disk reset; files move by copy and the keeper commits them). Updated 5 Oct 2026 06:20Z (unit 26). Next self-wake about 07:15Z. Branch `r/ushijima`; private tree
`build/ushijima/tree`, committed with `tools/ushijima/commit.sh`; pushes and merges through the keeper.

## Ladder

- **R0 passed at 14:28Z (D-053 §A). R1 and R2 are open** (`docs/learning/ladder.md`). Charter: **D-046** in
  `docs/findings/2026-09-28-director-decisions.md`. The prompts' "D-045" means D-046; the existing D-045 (learned-arm
  gate) stands with the amendments in D-046 §4.
- **D-076: ratings belong to submissions, so trials are free.** The organisers' rating page and Daichi's snapshots
  agree: 14585 came back at 1721 when restored; 17388 runs on its own rating (1767, rank 78, at 05:50Z). A trial
  costs only time on the live slot. Any candidate with a passing probe and a pool not below carthage-05 may be
  queued. **Trial 2 is `bokuto-13-cull`** (70–31–1 against carthage-05 by Bokuto's run) **if Asahi's same-host pool
  reaches 226 wins and its probe passes by 07:45Z; otherwise `bokuto-04-queen`** (probe passed). **Queen:** Sugawara
  showed that 38 of Bokuto's 42 queen-decided pool wins are games carthage-05 also won, so the pool does not show
  that queen keeping wins; builds move to carthage-05 (q1-cage, then q2b-crown = Bokuto's queen lines alone). The
  keeper panel: carthage-05 32–36, k = 16 35–33, our queen alive 0 of 95; no sign that k = 16 costs the queen.
  **Clone:** A1 on the full rows 0.7379 beats the network (+0.0099); entropy-matched weights 1.45 (213) and 1.72
  (A1-400); the λ 1.72 arm runs now, the 213 arms wait for Kageyama's export. Chair's forecasts: −2 and −4 points.
  **First isolating builds (06:19Z):** q1-cage equals carthage-05 on the pool and saves the Schooltime queen in 3 of
  14 games; q2b-crown (Bokuto's queen lines alone) is −2.4 points on the pool and −7.4 on the keeper panel. Neither
  mechanism transfers as one switch; the Chair suggests leave-one-out from the free-lane bot instead.
- **D-075: k = 16 is rolled back.** Daichi restored 14585 at 04:53:55Z under D-052 §B: 45 ranked games, score minus
  expectation −0.263 against 14585's last 120 (95th percentile −0.126); alone 16–28; queen-rule 1–14; no fault. The
  cause is not established (noise, a change in the field, or the veto exposing the queen). **The Kenma trial runs
  as submission 17388 since 05:02Z** (60 ranked games, about 08:00Z). Its statistic is re-anchored at rating 1725
  for every window (an anchor of 1605 would credit the trial bot about +0.16 a game). **`bokuto-04-queen` is the
  second trial** (pool 226–46 = carthage-05; queen-decided 42–4; queen alive in 23 % of round-limit games), then a
  60-game control on 14585; the best of the three windows becomes the incumbent. Kenma's pool is 220–52 (queen logic
  acts on Schooltime only). Single-team priors are fitted: team 213 0.7541 on its own rows; the 213 prior at λ 1
  and at an entropy-matched weight go to play (Chair's forecast: −8 points). **Kageyama solved the bed schedule
  exactly** and rebuilt Devil's second layout (49 % of live Devil games); four maps follow; the pool will be re-zeroed
  on the variants. The keeper is unblocked.
- **D-074:** the clone's play tests are in: no prior −13.1 points, A1 at λ 1 −13.6, A1 at λ 1.41 −5.9, A3 −7.0; the
  arms order by sharpness, not accuracy; no arm reaches the incumbent; the route is Hinata's. The network on the full
  rows reaches 0.7280 with a much sharper prior than the trees. **A ladder trial of `kenma-03-pocket-queen` is
  approved:** active for 60 ranked games after Daichi's reading on 16979, then the incumbent is restored and the
  Chair rules. Bokuto's `bokuto-07-dodge` (60–42 against carthage-05) is next once its checks are posted. The keeper
  is blocked again on a tracked cache file; the lead is asked to untrack the folder.
- **D-073: the hub restarts by itself and is redeployed** (snapshot 67384f265, back at 04:06:45Z): the upload fix, the
  field reserve of 5 and the blinding are live; the redeploy ban is lifted. The lead reset the Cowork session disk at
  about 04:00Z; lanes report whether their shells work; the Chair's own shell still fails (permission error).
- **D-072 (the lead's rulings):** the council is dissolved (GLM and GPT seats deactivated). **Sugawara owns the queen
  problem** (goal in play: more queen-decided wins than losses and a pool not below the parent; it chooses mechanisms
  and queues screens without cards). **Hinata owns the clone in play** (a learned prior not below the incumbent on the
  pool). **Kageyama rebuilds the hidden bed layouts** from pearl appearances, verified by the oracle. One Mac, one
  job at a time: Asahi alternates clone and queen jobs; no job over about 45 minutes.
- **D-071 (the lead does not weigh the live rating):** the bar on uploads is lifted; Daichi restores the intended
  active bot by hand after each upload. H11 now blocks only changes to the hub's own code. The queen defect gets
  owners: on Schooltime our queen kills itself at round 0 in 91 of 91 games, and queen-rule losses are 29 of
  14585's 64 losses; Sugawara reads Kenma's queen logic, Asahi runs Kenma's bot on the pool with queen columns.
- **D-070: the new live bot lost 7 of its first 10 ranked games (Elo 1725 → 1643, rank 90 → 110).** Two series
  against lower-rated teams; no fault. The Chair reads it as noise (the bot equals its parent on 783 of 816 local
  fixtures and scored 46 against 41 in LS-1) and does not change the rollback rule (read at 40 games). Four of the
  seven losses are round-limit games lost on the queen rule with the longer longest dragon: the known weakness,
  which no ladder rung addresses now. LS-1's paired mean is +0.0625 to +0.080 depending on the pairing. The time
  diagnostic: the clone's gain is uniform across phases and time inputs carry 5–7 % of it. Kenma: 58–44 against
  carthage-05, pool 220–52 against 226–46.
- **D-069: k = 16 is live.** Daichi activated submission 16979 (`asahi-05-kz12-k16`) at 02:13:22Z on LS-1's final
  data: 75 pairs, paired mean +0.080 [−0.029, +0.187], no fault; all conditions of D-064 §B hold. LS-1's own frozen
  letter is HOLD; the gain to expect is small and on Weakhold. Rollback watch over the first 40 ranked games, target
  14585; no second promotion before 14:13Z. Learn jobs are now at most one fold so that panels can run between them.
- **D-068: the ten-team clone loses in play as a prior.** Asahi's seed-1 screens of the slot bot with the encoder
  trees: pool −7.0 points [−12.9, −1.5] at λ 1 and −11.8 at λ 0.5; gen −5.6. The free lane's own test of the A1 prior
  lost 42–60. The slot itself is at parity on four maps, so the model is the cause. Leading hypothesis: the clones
  are more accurate but much softer than the Heartbreaker prior, and a pooled ten-team model averages styles.
  **Selection by accuracy is suspended and the frozen cohort is not read.** Ordered: fallback count, A1 at λ 1, no
  prior at all, A1 at λ 1.41, and single-team priors (teams 213 and 91). LS-1 ended at 160 games; Daichi reads the
  promotion conditions at its next unit. P-8 (latent state) approved for its first stage. Free lane Kenma:
  58–44 against the live bot, Schooltime 6–0.
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

- **`carthage-05-free-sprint`, submission 14585, incumbent again since 5 Oct 04:53:55Z (D-075 §A).** `asahi-05-kz12-k16`
  (16979) was live 02:13Z to 04:53Z and is rolled back. The live slot is held by ladder trials: `kenma-03-pocket-queen`
  (17388) since 05:02Z. Our Elo is about 1605 (rank 120) after 16979's window. The figures below are 14585's, before
  02:13Z.
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
| Proposal cards | P-2: failed. P-4: refuted. P-5 (R2): by accuracy A8b 0.7224, A1 0.7184, A4 0.7205 (not selectable), A3 0.7145, live prior 0.6977; **in play the A3 placeholder loses 7 points on the pool; selection suspended (D-068)**. P-6: behind the battery. P-7: entry throughput passed; no training. P-8 (latent state): stage S0 approved |
| Screen (seed 1) | cage C+D with E = 0: HOLD, parked. H-KZ12 curve: pool +1.5 / +0.7 / +2.6 points at k = 4 / 8 / 16, gen flat, no queen response |
| Evaluator queue (Asahi) | Done since 05:18Z: probe of `bokuto-04-queen` (pass); queen-keeper panel for both parents; `asahi-21-q1cage-c05` and `asahi-25-q2bcrown-c05` pools and keeper panels. Order now (D-076): pool and probe of `bokuto-13-cull` (by 07:45Z); A1-400 at λ 1.72; the 213 prior at λ 1 and λ 1.45 when the export lands; `bokuto-02-vac` pool (running); Hinata's one-fold learn jobs between them; variant-map re-zero when `maps/live_var/` lands |
| Nominee (full gate) | none. `asahi-05-kz12-k16` (REG-002) was promoted at 02:13Z (D-069) and rolled back at 04:53Z (D-075 §A) |
| Uploaded, inactive | 14585 (carthage-05, incumbent, waiting behind the trials), 16979 (k = 16, rolled back), 14265. The upload fix is deployed (D-073); uploads are open (D-071) |
| Live screen | **trial 1: `kenma-03-pocket-queen` = 17388, live since 05:02Z** (25 games at 05:34Z, no fault); look at the first series boundary at or after 60 ranked games (about 08:00Z). **Trial 2: `bokuto-13-cull` if its same-host pool reaches 226 wins and its probe passes by 07:45Z, else `bokuto-04-queen`** (D-076 §B). Then a 60-game control on 14585. Statistic: score minus expectation at rating 1725, series bootstrap; best window becomes the incumbent (lead under 0.03 keeps 14585). Further candidates may queue (D-076 §A) |

## Facts settled this unit

- **Each submission has its own ladder rating** (organisers' rating page; Daichi's snapshots). The team's rating is
  the active submission's; re-activation brings a submission's rating back; a new one starts from the rating of the
  submission it replaces and moves fast at first (D-076 §A).
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
| Council, auditor | Tanaka (GPT) | deactivated by the lead; council dissolved (D-072 §B) |
| Queen owner (was council, mechanism) | Sugawara (Claude), hourly at :25; shell works | owns the queen problem (D-072 §C); q1-cage: no gain; q2b-crown: a loss on the pool and the keeper panel; both forecasts failed; next step is its choice (Chair's suggestion: leave-one-out from the free-lane bot) |
| Council, probe | Nishinoya (GLM) | deactivated by the lead |
| Data | Kageyama (Claude), `r/kageyama`, fresh session since 05:00Z | **bed schedule solved; Devil's second layout rebuilt (D-075 §F)**. Next: export the team-213 prior, then the four remaining bed variants into `maps/live_var/`, then the network inference estimate and the trajectory block |
| Learner; owner of the clone in play | Hinata (Claude), Cowork VM; hourly task at :35 | A1-full 0.7379 (beats the network); A11 = A5; λ_match 1.45 (213) and 1.72 (A1-400); arms queued with Asahi; A1-full deploy refit queued |
| Evaluator | Asahi, `r/asahi`, native executor `tools/asahi/jobd.py`; fresh session after the reset | working: both free-lane pools posted with queen columns; learn-runner library fix; queue as in the table above |
| Live ops | Daichi (Claude), `r/daichi`, Cowork VM; hourly at :50; shell works | trial 1 running (17388); statistic script `tools/daichi/trial_d075.py`; holds a byte copy of `bokuto-04-queen` for trial 2; hub items: seat field, end reason `queen`, frozen pairing rule |
| Free lanes (outside the ladder) | Kenma; Bokuto | Kenma: `kenma-03-pocket-queen` on trial; `kenma-21` 60–42 against carthage-05. Bokuto: `bokuto-13-cull` 70–31–1 against carthage-05 by its own run; shell down, trees uncommitted in `../wt-bokuto` |
| Analyst | Shenzhen | stopped by the lead (D-074 §C); units 36–39 uncommitted unless Kageyama ran its commit command (not reported) |

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
| H11 | Confirm the hub runs inside the restart loop (a redeploy exits it) | **closed 04:07Z**: loop started by the lead, redeploy tested (D-073 §A) |
| H12 | The Cowork VM session disk was full | **reset by the lead about 04:00Z**; fresh sessions work (Sugawara, Daichi, Kageyama, Asahi); the Chair's device shell and Bokuto's still fail; the backup image `~/Desktop/sessiondata.img.bak` can be deleted; expect a refill in one to three days |
| H13 | Kageyama cut off | closed: fresh session working since 21:16Z |
| H15 | Free lanes | Kenma and Bokuto both running; Bokuto needs a fresh session to commit its tree |
| H14 | Mac disk | closed: 74 GB deleted with the lead's approval; 102 GB free |

## Next three decisions

1. **Trial 2's bot** at 07:45Z: `bokuto-13-cull` or `bokuto-04-queen` (D-076 §B); then Daichi's table for 17388 at 60
   ranked games (about 08:00Z).
2. **The queen:** Sugawara's next step after q1-cage (no gain) and q2b-crown (a loss): leave-one-out from the
   free-lane bot, or another route of its choosing.
3. **The clone in play:** A1-400 at λ 1.72, then the 213 prior at λ 1 and λ 1.45.

Waiting on the lead: nothing blocking. Optional: a fresh session for Bokuto (its trees are uncommitted) and for the
Chair (no device shell), and deleting `~/Desktop/sessiondata.img.bak`. Unanswered, not acted on: whether Asahi's
cards should carry a curve block (the summary-statistics curve by round).

## Cursor

Last BOARD line read: line 1230 (Asahi 06:19Z, with its sub-lines), main tree. Own D-076 line follows.

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
- **Bed variants, update (D-075 §F):** the schedule is solved and Devil's second layout rebuilt; the discount on the five maps below stands until the pool is re-zeroed on `maps/live_var/`.
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
