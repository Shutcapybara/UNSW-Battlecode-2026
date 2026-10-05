# Ladder state (Chair)

Kept by the Chair (Ushijima). Rules: `00-MACRO.md` §1 and D-046. A rung passes only when this file records it.

## Current state (5 Oct 2026 16:24Z)

- **R0 passed 4 Oct 14:28Z (D-053 §A). R1: P-2 failed its confirmation 18:20Z (D-057 §B); rung open, behind R2. R2: development battery running (D-057 §C).**
- **Incumbent of record: `kenma-03-pocket-queen` (17388)**: +0.005 [−0.072, +0.081] over its 129 ranked games; level with 14585 (−0.043) and `bokuto-13-cull` (−0.054 over 120). **Live now: trial 3, `bokuto-18-queenfeed` = submission 17791, since 14:19Z**; look at 60 ranked games (about 17:50Z to 18:10Z; the ladder gives about 16.5 ranked games an hour). **Trials run back to back (D-084 §C):** Daichi applies the end rule at the look (more than 0.03 over the incumbent's statistic) and starts the next trial at once; **trial 4 is `asahi-27-b13-reserve`; trial 5 is Bokuto's latest bundle with a complete card** (D-086 §C; `bokuto-27-exitsplit` qualified but shows no gain over its parent and is not trialled alone). Three targets for candidates: total length near 78 and 154 at rounds 100 and 300; queen alive at round 300 near 0.58; at least 70 % of round-300 leads converted.
- Deadline: handled by the lead; the Chair imposes no freeze (D-050 §2).
- GPU work may run on the Mac's shared memory, natively, under the heavy-job lock (D-050 §3).

| Rung | Adds | Status | Owner | Record |
|---|---|---|---|---|
| R0 | infrastructure | **passed** 4 Oct 14:28Z | Kageyama, Hinata, Asahi, Daichi | D-046, D-051 §5, D-052, D-053 §A |
| R1 | V0 value model | **P-2 failed its one confirmation** (elimination r25 −0.0099 [−0.0152, −0.0049] against −0.01; better than Φ on round-limit maps at every checkpoint). Rung open. Next value artifact: P-6 (V-legal) with a fallback to Φ early on elimination-regime maps | Hinata | D-052 §A, D-057 §B |
| R2 | P1 BC direction head | **By accuracy:** mirror-averaged A1 (A8b) 0.7224; A1 0.7184; A3 0.7145; live prior 0.6977. **In play (seed 1, slot bot, A3 placeholder): pool −6.99 points [−12.87, −1.47], gen −5.60; λ 0.5 worse.** Slot at parity on four maps, both paths. **Selection by accuracy suspended; frozen cohort not read (D-068).** Diagnostics: fallback count, A1 at λ 1, no prior, A1 at λ 1.41, single-team priors (213, 91). **Play diagnostics (D-074 §A): no prior −13.1 points, A1 at λ 1 −13.6, A1 at λ 1.41 −5.9; arms order by sharpness.** Full rows: network 0.7280. **Single-team priors fitted (D-075 §E): team 213 0.7541 on its own rows, team 91 0.7133. A1 on the full rows 0.7379, above the network by +0.0099 (D-076 §D). A1-400 at its entropy-matched λ 1.72: −7.35 points [−12.15, −2.21]; sharpness recovers about half the gap and saturates near λ 1.4 (D-077 §E). **The team-213 prior fails at both weights: −12.50 [−17.28, −7.35] at λ 1, −12.68 [−17.83, −7.54] at λ 1.45 (D-078 §D). The line is paused (D-080 §C): five arms in, all 6 to 14 points below the live prior; the sixth cancelled.** P-9 (a learned cull gate on `bokuto-13-cull` from its own randomisation): **closed at stage S0**, first stage 0.018 against a bar of 0.25 (D-079 §C) | Hinata (owner of the clone in play, D-072 §D), Kageyama, Asahi | D-055 §E, D-057 §C, D-058 §C, D-059 §B, D-063 §C, D-064 §C, D-065 §C–D, D-066 §C–F, D-068, D-074 §A, D-075 §E, D-076 §D, D-077 §E, D-078 §D, D-080 §C |
| R3 | split/size, cull, sprint heads | **offline fits brought forward** (D-067 §E.6): after A1 on the full rows, pooled and by style, every table by phase bucket; no bot yet | Hinata | D-058 §C (arm A9), D-067 |
| R4 | feature blocks | not started | Data, Learner | |
| R5 | V in the search | needs a value model on the legal encoder (V-legal card after the decode, D-052 §A.7) | Hinata | |
| R6 | expert iteration | small scale only, by a later D-record | Learner | |
| R7 | CNN/GRU | allowed on the Mac's GPU (D-050 §3); only if the accuracy-per-KB curve shows the trees saturating | Hinata | |
| R8 | PPO league | allowed on the Mac's GPU (D-050 §3); only if R6 plateaus for two iterations. Scoping card P-7: entry throughput **passed** (D-066 §B); no training approved | Hinata | D-063 §D, D-066 §B |

## R0 exit checklist

| # | Item | Gate | Owner | Status |
|---|---|---|---|---|
| 1 | Post-m2 decode finished | every in-scope post-m2 game and all own games decoded | Kageyama (native Mac job) | **done**: 19,754 of 19,754 (13:55Z) |
| 2 | Frozen splits | manifests with hashes in `docs/learning/splits/` | Chair (maps), Kageyama (series, fixtures, row counts) | **done**: `kageyama-games-v2.json` (126,694 games, 28,602 series, sha ba21ac40…, 0 series across buckets, `consumed_by` column) and `kageyama-fixtures-v2.json` (sha a0385e85…); consumption tags re-checked by Tanaka on all rows |
| 3 | Observation encoder | Python = C++ bit for bit on 1,000 turns | Kageyama | **passed** (D-051 §5): 40,002 turns, 0 mismatches; re-run by Nishinoya on its own fixtures, 1,549 turns, 0 mismatches |
| 4 | Action labeller | agreement with HB-1 labels on Heartbreaker data > 99 % | Kageyama | **passed** (D-051 §5): 100 % of 75,306 Heartbreaker turns; re-run by Nishinoya, 100 % of 31,061 turns |
| 5 | Leakage audit | no held-out map, series or gate fixture in any training set | Kageyama | **passed**: 9 of 9 on manifest v2 (Kageyama), re-run by Nishinoya, 9 of 9; `smoke.parquet` rebuilt train-only |
| 6 | Registry in use | every artifact has an entry in `registry.md` | Chair keeps the file; owners add entries | file created |
| 7 | Gen twins regenerated from `maps/live/` | the swapped maps' twins rebuilt; stale twins excluded until then | Asahi | **done** (D-051 §5): four twins rebuilt in `maps/m2tr/`, on `main` |
| 8 | `battles.json` control and live monitor | built, tested, redeployed; `docs/learning/live.md` refreshing | Daichi | **done** (D-051 §5): redeployed with dispatch off; A/A job enabled by D-051; monitor hourly |
| 9 | `maps/live/` equals the server's maps | map text in post-m2 replays matches the templates | Kageyama | **closed** (D-077 §F): all five hidden layouts rebuilt in `maps/live_var/`; 828 of 828 variant games reproduce turn for turn; the variants carry 14.46 % of ranked games; the pool gets a variant fixture block (D-075 §F) |
| 10 | Interval convention frozen | Tanaka's audit note on D-046 §3 and §4.3 | Tanaka, then Chair | **done** (D-052 §C): map × opponent clusters, seats and seeds together; directional key as sensitivity |

Items 3–5 are the macro's offline gate for R0. Items 1, 2 and 6–10 are prerequisites the Chair added in D-046.
What each blocks: items 1–5 and 9 block the offline gates of R1 and R2; items 7 and 10 block panel gates; item 8
blocks live screens.

## R0 design constraints (adopted from the council intake, Sugawara 10:40Z)

1. **Encode from the IO round block.** The encoder is `encode(block_lines, process_memory)`: its input is the round
   block each dragon process legally received (view, inbox, echoes), rebuilt by
   `tools/team_recon_claude/roundblock.py` through the `recon` callbacks (the hb1 path). C++ parity comes from feeding
   the same block text to the bot's parser. Before use, re-check the block builder against protocol 3 and the
   current sonar rules (tail exit; the last send per direction wins).
2. **Queen-knowledge features from own-view history only** at R0–R2, in training and in deployment. Teachers' sonar
   payloads are unreadable to us, so filling these features from our own relays at deployment would be a
   distribution shift made by the encoder. Echo counts are included from the start. Sonar-relayed knowledge is its
   own R4 block, trained on our own games and self-play.
   - Falsifier: on our own post-deploy games, if view-only and sonar-filled queen-knowledge features agree on more
     than 95 % of turns, the separation is unnecessary.
3. Future-dependent analysis fields are labels only, never inputs (Himeji H23-05, H24-03).

## Outside the ladder (temporary hand rules, D-044 §3)

| Arm | Parent | State | Next | Learned replacement target |
|---|---|---|---|---|
| Cage C+D, E = 0 | carthage-05 | **parked** (D-053 §C): screen HOLD; the gated-reserve card P-3 rejected (map identity); live Schooltime is lost about equally with the cage open (−0.515, 27 games) and closed (−0.436, 24 games) | none | R3/R4 |
| H-KZ12 entry-capacity dial, k = 0/4/8/16 | carthage-05 | k = 16: live 5 Oct 02:13Z to 04:53Z as 16979, **rolled back under D-052 §B (D-075 §A)**: 45 games, −0.263 against 14585's last 120, 95th percentile −0.126; cause not established; local gate hold (Weakhold +28 points), LS-1 75 pairs +0.080 [−0.029, +0.187] | closed for now: the keeper panel shows no queen cost (k = 16 35–33 against carthage-05 32–36; D-076 §C); queen builds use carthage-05 | R4 block "body-conditioned entry capacity" |
| Queen keeping (free lanes) | carthage-05 lineage | `kenma-03-pocket-queen`: pool 220–52, **ladder trial 1 running as 17388**. `bokuto-04-queen`: pool 226–46. **`bokuto-13-cull`: pool 241–31, +5.51 points [+2.19, +9.19], queen alive 58 % of round-limit games; trial 2 and local reference (D-077).** Isolating builds on carthage-05 failed (q1-cage no gain, q2b-crown −2.39); `bokuto-02-vac` alone 195–77. Sugawara: leave-one-out on `bokuto-13-cull` | Daichi (trials), Sugawara (queen owner) | R3/R4 |

| Queen reach veto (H-KZ26), m ∈ {off, 0, 1} | carthage-05 | card P-4 approved for a seed-1 screen (D-054 §C), after the k = 16 gate | Asahi | R4 block "enemy sprint reach" |

## Log

- 5 Oct 16:24Z: D-086. Sugawara's check amends the exit-split finding: the wall-loss gap replicates (132.1 against
  51.3 cells a game) but `bokuto-27-exitsplit` reaches 27 % of the length-3-to-5 wall deaths (at most 7.3 cells a
  game). Its card: qualified, no gain over its parent, below `asahi-27-b13-reserve` head to head. **Trial 4 is
  `asahi-27-b13-reserve`; trial 5 is Bokuto's latest bundle with a complete card.** Trial 3's look is about
  17:50Z to 18:10Z. Seat column asked of Hinata. The contest's page gives 100 M points a turn against our 30 M:
  two checks ordered, limit unchanged until one is in.
- 5 Oct 15:22Z: D-085. Checked reading: against teams at 1725 or above the `bokuto-13-cull` lineage builds no lead
  and loses early fights (carried length lead +0.8 against +41.5 below 1725; conversion equal in both bands).
  Bokuto's finding: walkers die whole at corridor ends (131 cells a game at walls against 51); fix in
  `bokuto-27-exitsplit`, which is trial 4 if it qualifies by trial 3's look. Trial 3 running, no fault.
- 5 Oct 14:23Z: D-084. Trial 3 live: `bokuto-18-queenfeed` = 17791 since 14:19Z. The incumbent is back to level (+0.005
  over 129 games): all three bots that held the slot are indistinguishable on the ladder. Trials back to back;
  Daichi applies the end rule; trial 4 = `asahi-27-b13-reserve`. A second free lane is recommended to the lead
  (addendum written).
- 5 Oct 13:24Z: D-083. **Correction of D-082:** the curve table's queen columns were side-swapped in half the games
  (found by Sugawara, fixed by Hinata). The top ten's winners keep their queen (alive at round 300: 0.58 against
  0.37); ours: 14585 0.06, the incumbent 0.12, `bokuto-13-cull` 0.50. Economy and lead-conversion figures stand.
  Three targets. 17388 active since 12:34Z. `bokuto-13-cull` −0.054 over 120 games. Trial 3 ordered on condition
  for `bokuto-18-queenfeed`. Descriptions that change the diagnosis get a second-lane check before the Chair
  records them.
- 5 Oct 12:28Z: D-082. The curve table (Hinata): among the top ten the winner has the bigger economy (+43 cells at
  round 300) and queen survival does not separate winners from losers; our totals are at the top ten's losers'
  level and `bokuto-13-cull` has the smallest; we lose round-300 leads through the queen rule (converted: 14585
  50 %, 17530 65 %, 17388 74 %). Two targets set for candidates. The reserve hypothesis is refuted. 17388 is not
  yet activated.
- 5 Oct 11:24Z: D-081. **End rule applied: `kenma-03-pocket-queen` (17388) is the incumbent** (+0.117 over the reference;
  `bokuto-13-cull` +0.001 after 60 games, 30–30). The pool and the head-to-heads ranked the two in the wrong order.
  Hypothesis to check: Kenma's reserved unit slot. `bokuto-17-atlas` is below its parent and the atlas is the
  cause (−4.4 points). `qk2` tests the queen race; the pool cannot. The curve table moves to Hinata; Kageyama is
  silent.
- 5 Oct 10:19Z: D-080. Why the local gain does not carry: on the ladder `bokuto-13-cull` is ahead at round 100 and
  loses late by the queen rule (queen alive at the end 17 % against 58 % on the pool; the top teams hide the queen
  and feed her from round 250–300). Cards gain queen-by-round columns and a `qk2` panel; Kageyama builds the curve
  table. The clone-prior line is paused. Map atlases are admissible in free-lane bots under three conditions.
  `kenma-28-harvest-reserve` equals its parent (241–31). Bokuto's fresh session works. The paired live screen is not
  dispatched. Trial 2 at 45 games: 21–24.
- 5 Oct 09:18Z: D-079. Kenma retired (out of credits); its last bot `kenma-28-harvest-reserve` is `bokuto-13-cull` plus
  Kenma's components, 72–30 against carthage-05 where the parent scored 73–29. The BOARD was overwritten twice by
  the old Bokuto session and restored. P-9 closed at its first stage (0.018 against 0.25). Trial 2 interim at 25
  games: 10–15 (not the look). Nothing from any lane is confirmed on the ladder; a paired live screen is drafted.
- 5 Oct 08:18Z: D-078. Trial 1 (`kenma-03-pocket-queen`): 60 games, +0.074 [−0.048, +0.197], no Schooltime game in the
  window. Trial 2 (`bokuto-13-cull`) uploaded as 17530. Tie rule between the trial bots: live decides beyond 0.10,
  else the pool. Variant block: `bokuto-13-cull` 72 of 80 against 63, weighted +5.75 points. The team-213 prior
  fails at both weights (−12.5); one clone arm left. P-9 stage S0 approved.
- 5 Oct 07:24Z: D-077. **`bokuto-13-cull`: pool 241–31, +5.51 points over carthage-05, queen alive in 58 % of
  round-limit games; it is trial 2 and the local reference.** The control window on 14585 is dropped; the end rule
  is applied at trial 2's look. Mac time goes first to the free lanes' candidates. A1-400 at λ 1.72: −7.35
  points; a stop rule for the clone prior after three more arms. R0 item 9 closed (828 of 828). The trajectory
  block is built.
- 5 Oct 06:20Z: D-076. Ratings belong to submissions, so ladder trials cost the incumbent nothing; any candidate
  with a passing probe and a pool not below carthage-05 (paired 5th percentile above −5) may be queued for a
  60-game trial. Trial 2 is `bokuto-13-cull` if its same-host pool reaches 226 wins, else `bokuto-04-queen`. Queen
  builds move to carthage-05: q1-cage, then q2b-crown (Bokuto's queen lines alone); the keeper panel gives no sign
  that k = 16 costs the queen. A1 on the full rows (0.7379) beats the network; entropy-matched weights 1.45 (213)
  and 1.72 (A1-400).
- 5 Oct 05:18Z: D-075. **k = 16 rolled back at 04:53:55Z** (45 ranked games, −0.263 against 14585's last 120; cause
  not established). Kenma's queen bot on trial as 17388 since 05:02Z; `bokuto-04-queen` next; then a control window
  on 14585; best of three becomes the incumbent. Statistic anchored at 1725 for every window. Single-team priors
  fitted (213: 0.7541). The bed schedule is solved; Devil's second layout rebuilt; R0 item 9 reopened.
- 5 Oct 04:33Z: D-074. Clone play diagnostics in (arms order by sharpness). Ladder trial of `kenma-03-pocket-queen`
  approved.
- 5 Oct 03:58Z: D-072. Council dissolved. Owners: Sugawara (queen), Hinata (clone in play), Kageyama (bed layouts).
- 5 Oct 02:22Z: D-069. **k = 16 promoted:** submission 16979 live since 02:13:22Z (LS-1: 75 pairs, +0.080
  [−0.029, +0.187], no fault). Rollback watch on its first 40 ranked games. Learn jobs limited to one fold.
- 5 Oct 01:49Z: D-068. The ten-team clone loses in play as a prior (pool −7.0 points at λ 1). Selection by accuracy
  suspended; the frozen cohort is not read; five play diagnostics ordered. LS-1 ended at 160 games. P-8 stage S0
  approved.
- 5 Oct 00:53Z: D-067. Time and game state: by-phase diagnostic, no-time ablation (T0), conditional phase models
  (T1), behaviour profile by round, card P-8 (latent state) requested, R3 offline brought forward, trajectory
  block for encoder v2. Two free lanes opened outside the ladder.
- 5 Oct 00:36Z: D-066. P-7's entry throughput passes (no training approved). A1 and A3 are selectable; A4–A7 as
  fitted are not (size). Arm A8b added. Full-row jobs: network first, A1 second, 14.4 GiB ceiling. Deploy slot
  accepted; HB-1 input path ordered. The live screen of the clone does not wait for the cohort confirmation.
- 4 Oct 10:50Z: D-046 opens R0. Engine identity across wheels 1.2.3, 1.2.5 and 1.2.9 checked by hash (D-046 §2).
- 4 Oct 10:52Z: D-047. Held-out maps frozen (Maze, Trauma, Trophy). P-1 numbered; council round 1 opened on its gate
  reading; the fit waits for the decode or 5 Oct 00:00Z.
- 4 Oct 17:02Z: D-055. Live-first: upload and live screens no longer wait for the full local gate; LS-1 ordered for
  k = 16. P-5 (R2) and P-6 (V-legal) approved as amended. A/A closed.
- 4 Oct 15:36Z: D-054. P-2's population fixed at 1,327 usable games (scope from manifest v2). P-4 (queen reach veto)
  approved for a screen. Council round 2 on P-5 (R2) and P-6 (V-legal), due 17:00Z. Asahi idle; the lead asked to
  wake it.
- 4 Oct 14:28Z: D-053. **R0 passed.** H-KZ12 k = 16 nominated for the first full gate (seeds 2–3). P-3 rejected (map
  identity); cage work parked. H-KZ26 card requested. D-052 §E withdrawn (variants cannot be rebuilt).
- 4 Oct 13:18Z: D-052. P-2 confirmation terms frozen (spec sha 15d79683…). Rollback rule replaced by a difference
  form. Interval convention frozen. Cage E = 0 screen held. Two map variants to be added to the pool. R0 items 2, 5
  and 10 recorded; items 1 and 9 open.
- 4 Oct 12:22Z: D-051. A/A live job enabled. R0 items 3, 4, 7 and 8 recorded; items 1, 2, 5, 9 and 10 open.
  P-2 confirmation held until D-052 (Tanaka: reserved series in the training rows; Φ not frozen).
- 4 Oct 11:18Z: D-050. Seats named by the lead. No Chair-imposed freeze. GPU work allowed on the Mac. Quota-runner
  condition replaced by a ledger check. R0 items reported by Kageyama and Asahi; none recorded until merged and
  re-run; split manifest v2 requested on Autarky, Maze, Trauma.
- 4 Oct 10:59Z: D-049. Held-out maps corrected to Autarky, Maze, Trauma (Trophy was used in the 10:52Z development
  fits). P-1 closed as failed in development. P-2 is the R1 candidate; its confirmation waits for D-050.
- 4 Oct 10:55Z: D-048. Executor stays in shadow; battles control may deploy with dispatch off; A/A dry run first;
  rollback reference put to the council; Rome may run the cage E = 0 screen until an Evaluator lane exists.
