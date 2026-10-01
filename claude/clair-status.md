# H-1 `clair` status — hypothesis steward (Claude Opus 5.5, macbook)

Lineage **Clair**. Branch `r/clair`, worktree `../wt-clair`, candidate bots `bots/clair-<nn>-<slug>/`
(one mechanism per version, all on `hb1-14-prior-r540`), harness `tools/clair/` (copied from `tools/rc/`,
same D-032 gate, frozen `gen_reference.json`). This is the lane's first pass: the three first-pass tests the
brief names, plus the standing duties (reconcile, settle, contradictions, gate audit, ranked ten).

**Ledger edits are proposed here; the director applies them.** Nothing outside `bots/clair-*`, `tools/clair/`
and this file is touched.

## First pass — the three tests

All three on the same parent (`bots/hb1-14-prior-r540`, untouched), D-032 panels through `tools/clair/lane.py`
(pool = ZOO × 10 live maps × both seats; gen = 4 opponents × 31 off-pool maps × both seats), paired bootstrap
1,000 draws, 90 % intervals. Port validation before any game: `clair-05`/`clair-06` at zero weights replay
hb1-14's golden transcript (devil A s1, 3,754 turns, 125 dragons) **0 divergent**; `clair-04` (a real knob)
diverges, so the harness sees real changes. `clair-07`/`clair-08` are the aline-17 / gustave-07c diff sets
applied to hb1-14 (patch contexts matched exactly, no fuzz residue), compile clean, and diverge from the parent
on smoke fixtures as their mechanisms require.

### Test 1 — is the bowl still flat on the prior base?

The four Renoir risk-taking moves and the two Maelle live scans, one knob per version, scored against hb1-14:

| version | knob (V06 value → here) | its V06/nodevil evidence | pool s1 screen | full D-032 | verdict |

*(table filled when the runs land — screen at seed 1, extension to seeds 1–3 + gen when the pool point estimate
is ≥ +0.03; ≤ +0.01 is "the bowl holds for this knob"; see screening rule in the run log)*

### Test 2 — are the two information gains additive?

`clair-07-symseal` = aline-17's change set (symmetry inference + ally right-of-way seal) as a switch on hb1-14.
aline-17 vs its own parent (nodevil, no prior): pool econ +0.025 [+0.005, +0.045], win +6.1 pp, ACCEPT.

*(results table pending)*

### Test 3 — does the mouth rule survive the prior?

`clair-08-mouthroute` = gustave-07c (−4 for ending on a portal mouth unless the dragon's own route crosses it
within 3 steps). On its own parent: HOLD — ally h2h −18 % pool / −23 % gen, economy flat.

*(results table pending)*

## Standing duty 1 — reconcile (evidence since the last ledger log, 1 Oct 03:00 UTC)

Read for this pass: `origin/r/tt` (new: four-top-team anatomy, tt-01..07 conversion ports, dummy-bot check,
map-memory features, tt-08..11 mimics/priors for "forgot to mention" and "Cache me outside") and `origin/r/alicia`
(alicia-03 REJECT; `s1c` gate-shaped ES: economy +0.016 ± 0.007 per generation over 15 generations; alicia-04 on
panels). `hb1-status` (1 Oct 01:33) and the 11:43 lane-status mtimes are already inside D-039's read. Proposed
row moves, one step per result:

| row | old → new | evidence pointer |
|---|---|---|
| L39 | 0.7 → **0.8** | tt: all four top teams (cheji bt, Stockfish, forgot to mention, Cache me outside) convert, cull small dragons and feed the long one (longest@490 35–46 vs Heartbreaker 13; cull-beside-long-ally tables 6→82 %); four independent convergences on one mechanism is the programme's most robust external finding. The four rule-ports still fail locally — the row's live form is unchanged (own co-designed conversion keyed on state, opponent units at r300). |
| L12 | 0.5 → **0.3** | rc 02b diagnostic: Sciel-03a's +0.067 was a flat ×0.70 value cut (Renoir's churn lever), not a density memory (95.5 % of factor evaluations exactly 0.70); rc 03a/03b measured the density term itself: flat at weight 3 and 6. With Maelle's food_free zero-weight optimum that is the second and third rejection of the *density-as-target-term* form. What survives lives in other rows: remembered-map geometry for steering (see contradiction 1 → L34/L14), verso's tier-4 route features. |
| L02 | 0.7 → **0.4** | two independent rejections of the sparsity-keyed search-budget sub-form: Maelle F5 (lo 48 *and* lo 160, every hi: econ −0.015..−0.031) and Gustave 04a-sparsewide (−0.043). The untested sub-form (volatility keyed on enemy heads in view / corridor degree / pending split) keeps the row alive at 0.4. |
| L11 | 0.35 → **0.3** | rc 06a (≤2-known-beds key) inert; 06b (≤6) = Renoir's flat wait, negative. One rejection of the structure-keyed guard form. L35's age/own-knowledge-keyed anticipation is the adjacent live form. |
| L34 | 0.35 → **0.3** | verso tier questions: the CNN(11×11)+GRU-96 adds ≤ ±0.2 pp at equal data (dropped under the pre-registered rule); probes recover the hand state (compressor, not new state). One rejection of the net-state form at equal data; the row stays alive on the accumulated-state question at larger data and on the undetermined-quarter evidence. |
| L21 | 0.3 → **0.1 (dormant, settled by rule)** | D-032 replaced the +0.05 single-seed bar for lanes (retention clause via units/length lower bounds and per-checkpoint deltas). The row's question — "is +0.05 the right shape" — was answered by decision, not data; record it as settled. Revival trigger: evidence that D-032's interval form accepts churn-shaped gains it should not. |
| L14 | 0.3 → **0.4** | tt internal-map test: cheji bt's steering steers toward cells it has *not* seen (+2.59 pp direction from map-memory features; every top team +0.75–1.36 pp). Exploration driven by remembered map is what the top teams do; the pool's "known maps" penalty is a panel artefact, not a verdict on the mechanism. Re-test on the gen panel / in a map-aware prior (tt-09/11). |
| L04 | 0.3 (no move; pointer) | alicia `s1c` is the first positive continuous signal in the programme (+0.016/gen over 15 gens, gate-shaped reward) but it is a reward slope, not a gate result, and the same lane's s1 reward gains died at the gate (alicia-03: −0.097). Re-score at alicia-04's D-032. |

## Standing duty 2 — rows the data has settled silently

- **L21** (above): settled by D-032, propose dormancy with trigger.
- **L02 sparsity sub-form** (above): two strikes, recorded.
- **L13 momentum**: *not* settled — Maelle's momentum scan was queued and never ran (lane closed). The row
  (0.4) is ownerless; the cheap re-issue is in the ranked ten.
- **L29 corpse-share diagnostic**: D-035 tasked R-4's scorecard with it; `scorecard.py` in main has no
  corpse-share column — an unexecuted director task, listed under the gate audit.
- **L17/L18/L23/L26**: no new evidence; untouched.

## Standing duty 3 — contradictions

1. **"State adds nothing" vs "steering uses remembered map".** Maelle F1–F4 zero-weight optima and rc 03a/03b
   say decayed EW-density features on the value function move nothing; tt's mapmem table says every top team's
   *direction* model gains +0.75–2.59 pp from remembered-map geometry (BFS reach, frontier distance,
   remembered-pearl distance), and verso's tier-4 route features earn a small consistent place (−7 % hindsight
   regret). Not actually in conflict: dead = EW density consumed by the **value**; live = remembered-map geometry
   consumed by the **steering prior**. Decisive test (already running): tt-09 / tt-11 — a map-aware direction
   prior on hb1-14, D-032 both panels; verso's next cycle is the same test with own-data heads. If either passes,
   split L12 into "density-value (dormant)" and "map-prior (live)".
2. **"Conversion ports fail" vs "all four top teams convert"** (tt-01..04 fail; L39 up-weighted). tt's own
   elim-state analysis resolves it: the local panel has no converting opponent (zoo longest 5–24.5 vs top teams
   35–46), so dissolving the swarm only trades elimination wins. The decisive test is not local: it is the ladder
   A/B `tt-05-feed300-up` vs `hb1-14` (break-even locally, top-team profile, both uploadable). This needs the
   executor out of shadow (D-031) or a teammate upload — a director action, not a lane.
3. **Alicia's `s1c` slope vs the measured bowl.** Not yet a contradiction: +0.016/gen on a gate-shaped reward is
   inside the seed-noise regime Renoir measured (+0.07 per seed). Decisive test: alicia-04's D-032 (running).

## Standing duty 4 — gate audit (D-032/D-037)

Three structural findings, each with a proposal. No gate edit is made here; the director decides.

**(a) The economy mean is invisible to endgame conversion (L39), and the tier-2 guard outlaws the mechanism.**
The economy checkpoints stop at r250 and pearls to r250 cannot move for a change that starts at r300 (tt-01/02
measured exactly +0.0000); meanwhile deliberate self-kills are own-body deaths, so every conversion port fails
tier-2 "by construction" (+37..74 %), though BENCHMARKS (30 Sep, point 3) already classifies chosen deaths as
non-hygiene for the top ten. Proposal — add a **phase `end`** to the lane gate (the `--phase late` pattern
extended): for a change that acts only after r250, judge on (i) final-longest / longest@490 delta, pool lb > 0;
(ii) round-limit-losses-with-material-lead rate, delta < 0 (the instrument already exists:
`tools/tt/concentration_bot.py`); (iii) overall win lb > −0.02 and p@50..p@250 as guards; and exempt from the
tier-2 10 % guard any own-body/self deaths the bot logs as deliberate culls (the `ACT:` marker pattern gives the
trace). Re-scored history (from the lanes' published tables, no re-runs): **tt-05-feed300-up flips fail →
accept-shaped endgame hold** (141–19 identical, longest 32 vs 27, lead-losses 8 % vs 50 %, own-body +60 %
cull-exempt); tt-01 flips to hold *pending seeds 2–3* (win −1.88 pp at s1); tt-02 (win −5), tt-03 (no
concentration), tt-04 (material does not arrive) stay fails; hb1-12/14, verso c2-feed140, esquie-03b verdicts
unchanged. Also unexecuted: R-4's corpse-share diagnostic (D-035) — fold it into the same scorecard revision.

**(b) The pool lower bound rejects off-pool gains — the two panels ask different questions and the gate answers
only one.** The pool is 10 known maps (identity-contaminated by rule, L28); the gen panel is the OOS rule's
actual object. Current letter: pool econ lb > 0 *and* gen econ lb > −0.02. Verso cycle 3′ (verso-05, the
registered lane parent): pool econ −0.017 [−0.038, +0.013], gen econ +0.017 [−0.006, +0.040], pool win
+0.033 [+0.003, +0.065] — rejected by the letter, kept by the lead. Proposal — replace the accept condition
with: **combined-panel econ~ lb > 0** (pool + gen fixtures pooled in one bootstrap, maps weighted equally per
D-037's Q2 predictability idea) **and each panel's lb > −0.02 (non-harm) and win lb > −0.02 on each panel**.
Flips (analytical, pending recompute on the desktop where the run data lives): verso-02 (cycle 2) and verso-05
flip REJECT → accept-shaped; aline-17, verso-01, maelle-04, gustave-07c/08a, esquie-03b unchanged (each already
fails or passes under both forms); the four tt ports stay fails (win). Recommendation: adopt with the phase-`end`
change (a) in one revision, since both fix "the gate cannot see the change" cases, and re-issue the recompute to
one lane on the desktop.

**(c) Plain vs fixture-cluster bootstrap: an accept that rests on the plain form.** aline-17's ACCEPT has pool
econ lb +0.005 (plain) and −0.000 (cluster) — under the cluster form the accept letter fails. The cluster form
is the statistically honest one (fixtures within a seed × map cell share the layout; the plain form counts them
as independent). Proposal — the **cluster bootstrap is authoritative for ACCEPT**, with a borderline rule so a
real accept with a hygiene/material corroboration is not chilled: accept when cluster lb > 0, *or* cluster
lb > −0.005 **and** pool win lb > +0.02. Under it: aline-17 stays ACCEPT (cluster −0.000, win lb +0.025);
verso-05 stays rejected under the current letter (pool win lb +0.003) and is adjudicated by (b) instead.
Recommendation: whichever of (b)/(c) is adopted, Aline's accept and Verso's cycle 2/3′ should be re-scored in
the same director note so the registry order reflects one rule.

## Standing duty 5 — the ranked ten (weight × size × cheapness)

| # | row / question | why it ranks | the one experiment | lane |
|---|---|---|---|---|
| 1 | L39 state-keyed conversion | 0.8 after this pass; 50 % of hb1-14's round-limit losses are with a material lead; four top teams converge on it | elim-state trigger on hb1-14: start co-designed crown+feeder when "no enemy met for 30+ rounds" (the observable stand-in for opponent units ≤5 at r300), else default onset; `--phase end` gate | tt (or re-issue) |
| 2 | L27 map-aware prior | the prior is the largest lever measured; +0.75–2.59 pp direction for every top team; Ares already keeps the map | tt-09 / tt-11 panel results (running), then the best donor's map features into the 540-round prior | tt / verso |
| 3 | L38 additivity (this pass) | two accepts that have never been stacked; if additive, the registered bot improves for free | clair-07 full D-032 (running) | clair |
| 4 | L40 mouth rule × prior (this pass) | first off-pool hygiene lever; S-1 Q4 says own-traffic is 2× the top ten | clair-08 full D-032 (running) | clair |
| 5 | L20 bowl on the prior base (this pass) | decides whether ~15 dormant "V06 says no" rows re-open | the six-knob screen (running) | clair |
| 6 | L33 warding, plain-rule form | own-traffic exits are S-1 Q4's concrete target; no lane owns it (rc paused) | "don't transit the pair an ally used/is about to use" as a fitted cost on hb1-14 (no L32 needed — the row says prototype without it) | re-issue |
| 7 | L30 newborn churn paydown | r3-03 is +5 pp win blocked only by the tier-2 guard; the siting rule for `ACT:tsplit` children is specified (C1-C fix #2) and untested on Ares | siting rule on lune/ares base, then re-gate r3-03 | re-issue |
| 8 | L36 opening components | 0.8 measured; the gap opens by r25; D-037 issued but unfilled for bed-conversion and early-transit | per-map r25/r50 percentile targets, one mechanism per component cluster (bed anticipation done by L35; production and early-portal use open) | rc/M-1/K-1 |
| 9 | L13 momentum scan | 0.4, ownerless, one cheap scan answers it | `wt_ally`-style scan of momentum_weight/momentum_decay on hb1-14 through the clair-05 platform (CLAIR_PARAMS-style overrides exist) | clair follow-up |
| 10 | gate revision (a)+(b)+(c) | the gate currently cannot see the programme's two biggest live directions (endgame, off-pool) | adopt the phase-`end` tier + combined-panel accept + cluster-authoritative bootstrap; one recompute pass on the desktop | director |

## Run log

- 12:16 local — queue launched: parent s1 (both panels) → six knob screens (pool s1) → parent s2, s3 →
  clair-07/08 seeds 1–3 both panels → extract all. ~6,600 games at 9 jobs.
- Screening rule (pre-registered): a Test-1 knob extends to seeds 1–3 + gen only if its pool s1 econ~ point
  estimate ≥ +0.03 (Renoir's V06 effects were +0.01..+0.02, all REJECT; anything ≤ +0.01 reads "bowl holds");
  +0.01..+0.03 adds seed 2 pool only.
