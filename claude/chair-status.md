# Chair status — Ushijima (Phase 3)

State: ACTIVE (the Chair's device shell still fails after the disk reset; files move by copy and the keeper commits them). Updated 5 Oct 2026 21:51Z (unit 40). Next self-wake about 22:50Z (trial 4's look). Branch `r/ushijima`; private tree
`build/ushijima/tree`, committed with `tools/ushijima/commit.sh`; pushes and merges through the keeper.

## Ladder

- **R0 passed at 14:28Z (D-053 §A). R1 and R2 are open** (`docs/learning/ladder.md`). Charter: **D-046** in
  `docs/findings/2026-09-28-director-decisions.md`. The prompts' "D-045" means D-046; the existing D-045 (learned-arm
  gate) stands with the amendments in D-046 §4.
- **D-090: trial 5 is `bokuto-61-mouth`.** Asahi's card meets the four conditions of D-089 with none on the line:
  probe 14.32 M; pool +0.74 [−4.04, +6.25] against carthage-05; `qk2` 41–27 and head to head 63–39, both above 46.
  **Against the incumbent on `qk2`: +16.18 [+4.41, +29.41], the first interval there that excludes zero.** It is
  named by a second waiver of the twin condition, not a pass: on the pool it is 3.68 points below its atlas-off
  twin (a clear miss), which Sugawara localises to Australia and Slithery Fight through queen deaths; its queen
  dies at walls 10 times on `qk2` against 46's 3. Grounds: the pool has not predicted the ladder and the two
  strong-opponent panels prefer 61; 46 has a known fault on Schooltime that 61 fixes; the miss is localised and
  can be watched. Daichi uploads it at trial 4's look (about 22:15Z or after).
- **D-089: where the incumbent stands, on checked numbers.** Against teams at 1725 or above, in games that
  reached round 300: queen alive at round 300 0.72 (target 0.58); live leads converted 14 of 20 (target 70 %);
  growth between rounds 100 and 300 38.2 a game against 68.2 for the top ten's winners and about 51.6 for all
  top-ten sides. **The queen and the conversion are at target; the remaining gap is mid-game growth.** D-088's
  "20 of 26" and "0.62" are replaced (Sugawara's check, accepted by Hinata). **Every submission at anchor 1725**
  (Daichi): 14585 −0.022 over 1,095 games, 17530 −0.002 over 120 (the −0.054 quoted before was at another
  anchor), 17388 +0.060 over 130, 17791 +0.170 over 65. **Ruling:** the rollback rule D-052 §B binds an incumbent
  left active, not a trial bot; a trial ends at its look or on a fault. **Trial 5:** Sugawara showed that 46's
  twin condition is not a narrow pass but sits on the line (at or below −5 in 88 % of bootstrap seeds), and its
  `gen` panel does too (−5.17). The Chair's "passes narrowly" is withdrawn; the 46 line gets its trial by waiver,
  on stated grounds. Bokuto has fixed two faults in 46's own rule; **trial 5 is `bokuto-61-mouth` if its card
  (about 21:40Z) qualifies it and the Chair confirms on the board, otherwise `bokuto-46-regions`.** New rule: a
  condition within half a point of its threshold goes to the Chair as a waiver or a refusal, never as a pass.
- **D-088: trial 3 won. `bokuto-18-queenfeed` (17791) is the incumbent of record.** 60 ranked games, 32–28
  against a strong field (11 of 12 series against teams at 1725 or above): +0.174 a game against expectation
  [+0.079, +0.282] at anchor 1725, performance rating 1859; +0.114 [−0.004, +0.250] over `kenma-03-pocket-queen`
  (17388: +0.060 [−0.010, +0.132] over 130 games). Daichi applied the rule; Sugawara replicated the numbers. It is
  the first ladder interval of the phase that excludes zero. Caveats: one window; the difference's interval
  touches zero; the winner's own figure is probably somewhat high. **Correction:** the "+0.005 over 129 games"
  recorded for 17388 in D-084 was computed at an anchor near 1765–1770, not 1725; Daichi restates every trialled
  submission at 1725 in one table. Hinata's curve block (unchecked): against stronger teams the queen is alive at
  round 300 in 0.62 of games and 20 of 26 leads were converted, both at target; total length (65 and 116) is
  still at the top ten's losers' line. 0 wins in 11 games on Queen of Spades, Trophy, Default and Stripes.
  **Trial 4 is live: `asahi-27-b13-reserve` = 17940 since 18:25:06Z**, look about 22:15Z; it needs more than
  +0.204; between +0.126 (pooled line + 0.03) and +0.204 counts as unresolved. **Confirmation runs** of the two
  best submissions precede the final activation for the Qualifiers; the cutoff is asked of the lead.
  **Trial 5 is `bokuto-46-regions`, provided its probe and `gen` panel pass; else `bokuto-25-reserve4`.** 46 is
  aimed at those four maps and has the best `qk2` of the lineage (38–30; +11.76 [−2.94, +27.94] against the
  incumbent; queen wall deaths 3 against 9); it is level on the pool and −5.88 [−17.65, +5.88] head to head.
  It missed two point conditions the Chair wrote today by one to two games in 272; both are restated with a
  tolerance (paired 5th percentile above −5), a threshold changed after seeing the number, recorded as such.
  `bokuto-41-atlas0` qualifies but is behind the incumbent on `qk2` and head to head; `bokuto-47-precious` fails
  the pool floor. Bokuto: the lineage's search knobs do not spend the larger compute budget; it is
  building an enemy-response lookahead (`bokuto-52`).
- **D-087: the compute limit is 100 M points a turn, not 30 M.** Checked by two lanes on our own server games
  (turns up to 99.5 M survived; every cut turn records exactly 100,000,000) and by Asahi's local burn test. The
  30 M came from the macro and D-046 and was never checked against the contest's page. **Working ceiling: 60 M
  at the probe.** Our bots spend about 9.8 M on compute and 3.0 M on the output write, so about five times the
  search, or a model of tens of millions of points a turn, now fits; nobody has measured a bot at that size, and
  local cards slow down in proportion. Suggested to Bokuto: a twin with the search knobs raised in two steps.
  **No seat term:** the seat is drawn per series and the higher-rated side wins 61.7 % as A and 60.8 % as B.
  **`bokuto-35-knownbeds` does not qualify** (pool −0.37 [−5.15, +4.78] against carthage-05; −4.41 against its
  parent); its atlas-off twin equals the parent exactly, and the atlas raises ally head-on deaths 86 %. Atlas
  bots must now beat their own twin. Without the atlas, what Bokuto's bundles add over the trial-3 bot nets no
  wins on the pool. **Trial 5 by default `bokuto-41-atlas0`, else `bokuto-25-reserve4`**; after that the queue
  prefers the first qualified bot that uses the larger budget. Trial 3 still runs (50 games at 17:36Z; boundary
  about 18:20Z–18:45Z).
- **D-086: the exit-split finding is checked and is smaller than reported; trial 4 is `asahi-27-b13-reserve`.**
  Sugawara: the wall-loss gap replicates (132.1 cells a game against 51.3), but the code path Bokuto found is one
  of four classes: 46 % of our length-3-to-5 wall deaths are a length-3 dragon that cannot split, 27 % the head
  part after a production split (the only class `bokuto-27-exitsplit` reaches; at most 7.3 cells a game), 20 % at
  the unit cap, 7 % other. Asahi's card for 27: qualified; fewer queen wall deaths and +7 to +10 total length at
  round 300, but no more wins than its parent on any panel, and −10.8 points [−20.6, −1.0] against
  `asahi-27-b13-reserve` head to head. A 60-game trial cannot see a one-change difference of that size, so 27 is
  not trialled alone. **Trial 5 is Bokuto's latest bundle with a complete card** (`bokuto-35-knownbeds`, else 34,
  else 33; atlas conditions of D-080 §D apply). Trial 3's look moves to about 17:50Z–18:10Z (16.5 ranked games an
  hour). **The contest's page gives 100 M points a turn; our documents say 30 M** and our bots peak at 12.8 M:
  two checks ordered (corpus CPU points; a local burn test), limit unchanged until one is in. Seat-by-result
  column asked of Hinata (17530 played 100 of 120 ranked games in seat B). The lead's RL question is noted in §F.
- **D-085: Bokuto found a mechanism for the mid-game gap.** From 17530's 120 ladder games: between rounds 100 and
  300 we lose 131 cells a game at walls against 51 for opponents; 41 % is a walker of length 3–5 dying whole at a
  corridor's dead end, because the lineage's code prefers the wrong split when no move survives. Weakhold: 0 of 6.
  The fix is `bokuto-27-exitsplit` (one change on the trial-3 bot); **it is trial 4 if it qualifies by trial 3's
  look, otherwise `asahi-27-b13-reserve`.** Not yet checked by a second lane (Sugawara asked). **Checked reading
  recorded:** against teams at 1725 or above the `bokuto-13-cull` lineage builds no lead and loses early fights
  (carried lead +0.8 against +41.5 below 1725); it converts leads equally in both bands; the earlier "length lead"
  was survivorship. Trial 3 is running without fault.
- **D-084: trial 3 is live — `bokuto-18-queenfeed` = submission 17791 since 14:19Z** (pool 237–35, probe passed,
  Sugawara's code read found no flaw). Look at 60 ranked games, about 17:20Z. Locally it is not ahead of
  `asahi-27-b13-reserve` (head to head against the incumbent 61–41 against 69–33; fewer wall deaths of the queen,
  more head-on deaths); local numbers have not predicted the ladder four times. **The incumbent is back to level:
  +0.005 [−0.072, +0.081] over 129 games; all three bots that held the slot today are indistinguishable.**
  **Trials now run back to back:** Daichi applies the end rule at the look and starts the next trial at once;
  trial 4 is `asahi-27-b13-reserve`, the one-change test against `bokuto-13-cull`'s 120-game baseline. A second
  builder lane is recommended to the lead; the addendum for it is written.
- **D-083: D-082's queen statements were wrong and are withdrawn.** The curve table's queen columns were
  side-swapped in half the games (Sugawara found it; Hinata fixed it; the end state now matches the engine in
  2,342 of 2,342 cases). Corrected: the top ten's winners keep their queen (alive at round 300: 0.58 against 0.37
  for losers); ours: 14585 0.06, the incumbent 0.12, `bokuto-13-cull` 0.50. The economy and lead-conversion numbers
  stand. **So the winners have both economy and queen; the incumbent has the economy and our worst queen;
  `bokuto-13-cull` has our best queen and smallest economy; no bot of ours has both.** Three targets: total length
  78 and 154 at rounds 100 and 300; queen alive at round 300 near 0.58; 70 % of round-300 leads converted. New
  rule: a description that changes the diagnosis is checked by a second lane before the Chair records it.
  **17388 is active since 12:34:13Z.** `bokuto-13-cull` over 120 ladder games: −0.054 [−0.128, +0.023], level with
  the old incumbent. `asahi-27-b13-reserve` restores the economy locally (round 300: 138.5 against 127.5) and beats
  the incumbent 69–33 head to head. **Trial 3 is ordered on condition: `bokuto-18-queenfeed`** (queen fed from round
  290, queen safety from round 0, the reserve lines) as soon as its probe passes and its pool is not below
  carthage-05; otherwise `asahi-27-b13-reserve`.
- **D-082: the curve table changes the diagnosis** (its two queen statements are withdrawn by D-083)**.** Among the top ten the winner is the side with the bigger
  economy (total length +17 at round 100, +43 at round 300; the round-300 leader wins 73 %), and queen survival
  does not separate winners from losers. Our totals (55–63 at round 100, 103–128 at round 300) are at the level of
  the top ten's losers (61 and 111; winners 78 and 154), and `bokuto-13-cull` has the smallest. We also lose leads
  through the queen rule: round-300 leads converted 50 % (14585), 65 % (17530), 74 % (17388). **Two targets for
  candidates:** growth between rounds 100 and 300, and conversion of leads; a candidate that buys one with the
  other has not gained. This corrects D-080 §A. The lead's curve proposal produced it; it is now a block of every
  trial look. **The reserve hypothesis of D-081 is refuted** (Sugawara): `bokuto-13-cull` already keeps the slot;
  Kenma's bot wins the games decided by the longest dragon. **17388 is not yet activated**: Daichi has been silent
  since 10:56Z and 17530 is still live.
- **D-081: the end rule is applied; `kenma-03-pocket-queen` (17388) is the incumbent.** Trial 2: `bokuto-13-cull`
  30–30 over 60 games, −0.041 [−0.132, +0.062] at rating 1725, +0.001 over the reference: it plays at the old
  incumbent's level. Kenma's bot: +0.117 over the reference [−0.022, +0.260]. Caveats: the interval includes zero,
  its window drew no Schooltime, and nobody maintains it. **The pool and the head-to-heads ranked the two bots in
  the wrong order; three ladder results in a row were not predicted locally.** By opponent rating Kenma's bot does
  best against the stronger half (+0.162), Bokuto's worst (−0.073). Hypothesis under check: the unit slot Kenma's
  bot keeps free all game makes an escape split always available (Sugawara reads the replays; Asahi builds
  `bokuto-13-cull` plus that reserve). `bokuto-17-atlas` is 4.8 points below its parent and the atlas is the whole
  cause. `qk2` (against the two local queen keepers) tests the queen race that the pool cannot: carthage-05 21–47.
  Sugawara's census: our queen's extra deaths are at walls; the top teams feed from about round 300. The curve
  table moves to Hinata; Kageyama has been silent since about 07:00Z (stand-down recommended to the lead). The
  Chair's forecasts were too optimistic on all five of its scored events today.
- **D-080: why the local gain is not carrying.** Two independent reads of 17530's ladder games agree (Bokuto's
  replay read and Hinata's frozen description): the bot is ahead at round 100 and loses late by the queen rule.
  Queen alive at the end: 17 % on the ladder against 58 % on the pool. The top teams hide the queen at length 2–3
  to round 250–300 and then feed her to 30–60; a short queen loses the tiebreak even alive. The pool has no such
  opponent. **Ordered:** queen-by-round columns and a second keeper panel on every card (Asahi); a curve table by
  round from the ranked corpus (Kageyama; the lead's earlier proposal, adopted as a data product); the matched
  comparison as a standing column of trial looks (Hinata). **The clone-prior line is paused** (five arms, all 6–14
  points down; the sixth cancelled). **Ruling:** map atlases are admissible in free-lane bots, on three conditions
  for a trial (`gen` panel, hidden-layout block, a twin with the atlas off). `kenma-28-harvest-reserve` equals its
  parent on our harness. **Bokuto's fresh session works** and is building `bokuto-18` (queen safety, feeding from
  round 280). The paired live screen is not dispatched (a day of games for what a trial gives). Trial 2 at 45
  games: 21–24, −0.087 [−0.178, +0.020]; the look comes at 60.
- **D-079: Kenma is retired; nothing from any lane is confirmed on the ladder yet.** Kenma's last bot,
  `kenma-28-harvest-reserve`, is `bokuto-13-cull` plus Kenma's pocket and reserve: 72–30 against carthage-05 where
  its parent scored 73–29 on the same harness, so a second harness agrees that Bokuto's bot is the strongest
  locally. **Trial 2's interim (25 games, not the look): `bokuto-13-cull` 10–15, −0.193 a game.** If it holds at 60
  games, two local gains in a row failed to carry and the bottleneck is the local pool, not the candidates. The
  BOARD was overwritten a second time by the old Bokuto session (09:05Z) and restored (09:06Z). The cull-gate
  route (P-9) closed at its first stage. To the lead's question: the planned lines have produced no playing
  strength; Asahi, Daichi and Kageyama carry the services. Intentions: no change before the look; the clone-prior
  line pauses at its last arm; no compute for a self-play value model; Daichi drafts a paired live screen.
- **D-078: trial 1's table is in; trial 2 is uploaded.** `kenma-03-pocket-queen` (17388): 60 ranked games, 31–29,
  +0.074 [−0.048, +0.197] at rating 1725, performance 1781; +0.117 [−0.018, +0.269] over 14585's reference; no
  fault; **no Schooltime game in the window**, so its mechanism was not exercised (Daichi checks whether Schooltime
  is still in the ranked draw). **`bokuto-13-cull` is uploaded as submission 17530** (08:14Z); look at 60 games,
  about 11:15Z. **Tie rule, fixed before trial 2's first game:** between the two trial bots the live windows decide
  only beyond 0.10; within that the pool decides (`bokuto-13-cull`). On the 80 variant fixtures Bokuto never saw,
  its bot scores 72 against carthage-05's 63 (8 of the 9 on `schooltime_open4`); weighted by live share +5.75
  points [+2.97, +8.62]. **The team-213 clone fails at both weights (−12.5 points)**; one clone arm is left; my
  forecasts for the clone arms were too optimistic every time. Hinata's next route, P-9 (a learned cull gate for
  `bokuto-13-cull` from the bot's own randomised culls), is approved for its diagnostic stage.
- **D-077: `bokuto-13-cull` is the best bot we have locally and is trial 2.** Asahi's same-host pool: 241–31,
  +5.51 points [+2.19, +9.19] over carthage-05, +2.94 over k = 16; queen-decided 92–2; queen alive in 58 % of
  round-limit games (top ten 24–56 %); probe passed. Cautions: Bokuto developed against this pool; the pool's
  opponents rarely keep queens; the bot is uncommitted (Asahi commits byte copies). **The control window on 14585
  is dropped:** at trial 2's look the best of 17388's window, trial 2's window and 14585's last 120 games becomes
  the incumbent and stays live. **Mac time goes first to the free lanes' candidates**, then the bed-variant
  re-zero, Sugawara's leave-one-out on `bokuto-13-cull`, then the clone arms. **Clone:** the ten-team clone at its
  entropy-matched weight is −7.35 points [−12.15, −2.21]; sharpness recovers about half the gap and stops near
  λ 1.4; the rest is content. Stop rule: if none of the three remaining arms (213 at λ 1 and 1.45, A1-full at 1.76)
  has a paired 5th percentile above −5, the direction-prior line is paused. **Data:** all five bed layouts done
  (828 of 828; 14.5 % of ranked games); 213 and 91 slot bots exported; the trajectory block is built.
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

- **`bokuto-18-queenfeed`, submission 17791, incumbent of record (D-088).** 60 ranked games (14:30Z–17:48Z):
  +0.174 [+0.079, +0.282] at anchor 1725; performance rating 1859; team rating 1838, rank 59, at 17:51Z. Not live
  during trials. Before it: `kenma-03-pocket-queen` (17388), +0.060 [−0.010, +0.132] at 1725 over 130 games.
  Rollback target: `carthage-05-free-sprint` (14585; −0.022 [−0.046, +0.003] at 1725 over 1,095 games), whose
  monitor figures before 02:13Z follow. `bokuto-13-cull` (17530): −0.002 at 1725 over 120 games. **Live now:
  trial 4, `asahi-27-b13-reserve` (17940), since 18:25:06Z; 20 ranked games at 19:52Z, no fault.**
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
| Evaluator queue (Asahi) | Done: `bokuto-61-mouth` complete (probe 14.32 M; pool 228–44; `qk2` 41–27; head to head 63–39; `gen` equal to 46). Queue open: Sugawara's layer removal; Bokuto's next JOB |
| Nominee (full gate) | none. `asahi-05-kz12-k16` (REG-002) was promoted at 02:13Z (D-069) and rolled back at 04:53Z (D-075 §A) |
| Uploaded, inactive | 14585 (carthage-05, incumbent, waiting behind the trials), 16979 (k = 16, rolled back), 14265. The upload fix is deployed (D-073); uploads are open (D-071) |
| Live screen | **Trial 4 live: `asahi-27-b13-reserve` = 17940 since 18:25:06Z**, no fault; look at the first series boundary at or after 60 ranked games (about 22:15Z; server blackouts 19:52–20:12Z and 21:52–22:12Z). End rule: more than 0.03 over 17791's +0.174 at anchor 1725; Daichi also reports against the pooled line (+0.096); +0.126 to +0.204 is unresolved. Trial 3 ended 18:25Z: 17791 +0.174 [+0.079, +0.282], incumbent of record (D-088) |

## Facts settled this unit

- **The compute limit is 100 M points per dragon per turn** (D-087 §A): server rows of our own games and the local
  sandbox agree; a cut turn records exactly 100,000,000. Working ceiling 60 M at the probe. The output write costs
  about 3.0 M of every turn.
- **Seats are drawn per series and carry no measurable advantage** once rating is held (D-087 §B).
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
| Queen owner (was council, mechanism) | Sugawara (Claude), hourly at :25; shell works | amended Hinata's strong-opponent reading and Bokuto's exit-split finding (four classes; 27 reaches one) before the Chair recorded them; reads trial candidates' changes before upload; replicated Hinata's points-limit rows; reviewed the card of `bokuto-35-knownbeds` and withdrew its own bed-prior reading |
| Council, probe | Nishinoya (GLM) | deactivated by the lead |
| Data | Kageyama (Claude), `r/kageyama`; **silent since about 07:00Z** | bed layouts, slot bots and trajectory block done; the export is cancelled and the curve table has moved to Hinata. **Stand-down recommended to the lead (D-081 §D)** |
| Learner; owner of the clone in play | Hinata (Claude), Cowork VM; hourly task at :35 | analysis service of the trials (matched column, curve block). The curve table's queen columns were side-swapped; fixed at source within six minutes of Sugawara's review, with a guard against the engine's queen field. Its descriptions are reviewed by Sugawara before the Chair records them |
| Evaluator | Asahi, `r/asahi`, native executor `tools/asahi/jobd.py`; fresh session after the reset | working: both free-lane pools posted with queen columns; learn-runner library fix; queue as in the table above |
| Live ops | Daichi (Claude), `r/daichi`, Cowork VM; hourly at :50 | trial 3 started 14:19Z (17791); applied the end rule at 18:25Z and started trial 4 (17940) at once; posted every trialled submission at anchor 1725 (`docs/learning/trials-1725.md`); at trial 4's look (about 22:15Z): the table against 17791 and against the pooled line, then trial 5 = `bokuto-61-mouth` (D-090; fingerprint 028c97bf), fallbacks `bokuto-46-regions`, `bokuto-25-reserve4`. D-052 §B does not bind trial bots (D-089 §C) |
| Free lanes (outside the ladder) | Bokuto (Kenma retired, D-079) | **Bokuto: its `bokuto-18-queenfeed` is the incumbent of record. It keeps fixing the 46 line from its own local losses (57 the queen's blind portals, 58 unreachable migration targets, 61 migration into dead-end corridors; 61 is 28–6 locally against carthage-05) and measured that the old search knobs do not spend the larger compute budget.** One builder lane only; a second is recommended to the lead |
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
| H15 | Free lanes | closed: Kenma retired; Bokuto's fresh session started by the lead and working |
| H14 | Mac disk | closed: 74 GB deleted with the lead's approval; 102 GB free |

## Next three decisions

1. **Trial 4's outcome** (look about 22:15Z or after; bar +0.204; +0.126 to +0.204 unresolved), then trial 5 = `bokuto-61-mouth` starts (D-090).
2. **Trial 6:** not named. Candidates: a confirmation window for 17791; whatever Bokuto builds next on the larger compute budget or against the fed queen's deaths.
3. **The schedule of confirmation runs and the final activation**, once the lead gives the seeding cutoff.

Waiting on the lead: **the Qualifiers' seeding cutoff** (the record of 28 Sep says 10 Oct; unverified), so that
confirmation runs and the final activation can be placed. Nothing else blocking. For the lead: a second builder lane (recommended; the free-lane prompt plus
the addendum of 5 Oct); stand down Kageyama's lane (silent since about 07:00Z); the RL question (D-086 §F: the
Chair's reading is given, nothing is ordered; a port lane or a P-7 training run needs the lead's word). Optional: a fresh Chair session,
deleting `~/Desktop/sessiondata.img.bak`.

## Cursor

Last BOARD line read: line 1507 (Sugawara 21:33Z), main tree. Own D-090 line follows (21:50Z).

## Open flags

- **BOARD overwritten a second time at 09:05:05Z** (the old Bokuto session's 08:17Z file); restored 09:06Z; git af5154501 (D-079 §B).
- **BOARD overwritten at 08:17:14Z with its 05:50Z state; restored by the Chair at 08:19Z** (D-078 §F). Likely cause:
  the old Bokuto session sending a stale file through the file bridge. The Chair keeps a full copy of the BOARD in
  its work folder at every unit; git holds each keeper pass.
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
