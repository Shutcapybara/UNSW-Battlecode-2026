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

### Test 1 — is the bowl still flat on the prior base? **No — the prior moved the base.**

The four Renoir risk-taking moves and the two Maelle live scans, one knob per version, pool seed-1 screens
(160 paired fixtures vs hb1-14 on the same fixtures):

| version | knob (V06 → here) | same knob on V06/nodevil | pool s1 econ~ [90 %] | units@100 | win [90 %] | tier-2 (per 1k, parent →) |
|---|---|---|---|---|---|---|
| clair-01-threat05 | threat_weight 1.0 → 0.5 | Renoir 17a: +0.012 | −0.000 [−0.024, +0.026] | −0.021 | −0.025 [−0.075, +0.019] | flat |
| clair-02-visit005 | visit_weight 0.15 → 0.05 | Renoir 18a: +0.019 (2 seeds +0.015) | +0.000 [−0.023, +0.019] | +0.060 | −0.044 [−0.100, +0.006] | flat |
| clair-03-trapw20 | trap_weight 30 → 20 | Renoir 14b: +0.017 | **+0.037 [+0.022, +0.076]** | +0.012 | −0.012 [−0.050, +0.025] | clean (h2h +5 %) |
| clair-04-unseen3 | unseen_value 5 → 3 | Renoir 07a: +0.110, churn (units −0.08, h2h +51 %) | **+0.192 [+0.128, +0.279]** | **+0.261** | −0.012 [−0.062, +0.038] | h2h 1.75→2.45 (+40 %), wall +10 %, nb10 28.8→32.3 |
| clair-05-allycrowd | wt_ally 0 → −1.4 | Maelle F2: +0.030 s1, 3-seed REJECT | **+0.057 [+0.002, +0.112]** | +0.152 | **−0.062 [−0.119, −0.006]** | self −8 %, wall −6 %, h2h +10 % |
| clair-06-capsel | capsel 0 → lo48/hi384 | Maelle F5: −0.031 at hi 384 | **+0.037 [−0.000, +0.075]** (p@250 +0.124 [+0.034, +0.175]) | +0.055 | +0.006 [−0.044, +0.056] | h2h +12 %, ally-body +11 % |


**Reading.** The bowl does **not** survive the prior. On V06 these six moves measured +0.012/+0.019/+0.017/+0.110
(churn)/+0.030/−0.031; on hb1-14 four of the six clear +0.03 with two positive lower bounds, and the *shape* of
the biggest one changed: `unseen3`'s +0.192 comes with units +0.26, length +0.13 and births +0.19 — material
growth, not V06's splitting-into-dust (units were −0.08 there). The prior steers the extra production well enough
that it survives. Maelle's `capsel` — a form that *lost at every setting* on nodevil — is now positive with a
strong late signature (p@250 +0.124), consistent with the prior freeing search budget late. The two moves that
stayed flat (threat, revisit) are the two whose V06 effects were smallest. Per the brief: **every "V06 says no"
row measured only as a weight move on the evaluation is re-opened on the prior base** (L20's revival condition —
"a knob shows a consistent seat-independent +0.03" — has fired at screen level four times).

Guards still bite at screen: `unseen3` breaches tier-2 (h2h +40 %), `allycrowd` loses win (−0.062), `capsel`
scrapes the h2h/ally-body guard (+11–12 %), `trapw20` is the cleanest. Extensions (seeds 1–3 + gen) ran for
clair-03/04/05/06 plus the dose arm `clair-09-unseen4` (unseen_value 4). Full D-032 rows:

| version | pool econ~ [90 %] (n=480) | gen econ~ [90 %] (n=744) | other rows | verdict |
|---|---|---|---|---|
| clair-03-trapw20 | **+0.037 [+0.024, +0.054]** (every checkpoint lb > 0) | **+0.022 [+0.013, +0.032]** | length +0.030/+0.042, births +0.048, win +0.006/−0.001, tier-2 clean | **REJECT on one guard**: pool units@100 lb −0.063 (point −0.029) — the first single-knob result to clear both panels' economy with positive lower bounds |
| clair-04-unseen3 | **+0.151 [+0.118, +0.187]** | **+0.065 [+0.046, +0.091]** | units +0.214/+0.100, length +0.141/+0.153, gen win **+0.045 [+0.018, +0.073]** | **REJECT**: tier-2 h2h +37 %, ally-body +10 %, pool win lb −0.027 (noise-level). **Tempo gate: ACCEPT, −3.5 rounds [−4.4, −2.5]** — real net income, not corpse churn; the cost is per-transit deaths +17 % and newborns10 +12 % |
| clair-05-allycrowd | +0.029 [+0.003, +0.054] | **−0.058 [−0.089, −0.029]** (every gen checkpoint negative) | pool units +0.048, gen win −0.030 | REJECT — pool-fitted; Maelle-04's late off-pool loss reproduced on the prior base |
| clair-06-capsel | +0.006 [−0.012, +0.026] (s1's +0.037 was seed noise) | +0.015 [−0.002, +0.035]; p@250 +0.053 pool / +0.043 gen (lb > 0 both); **gen win +0.039 [+0.015, +0.066]** | econ_late +0.022/+0.027 | REJECT (pool econ lb) — a late-phase lever: p@250 positive on both panels, gen win up; hold-shaped under `--phase late`, but per-map tr-inconsistent (below) |
| clair-09-unseen4 | +0.000 [−0.031, +0.036] (s1 screen) | *(full gate in the run log)* | — | null at dose 4: the exploration lever is a **cliff between 4 and 3** on this base, not a slope |

**What the four extensions settle.** (1) L20's revival condition — "a knob shows a consistent seat-independent
+0.03" — is met by trapw20 (+0.037/+0.022 both panels, lb > 0) and materially by unseen3; the bowl is a property
of the *V06 evaluation*, and the direction prior moved the base off it. Every dormant "V06 says no" weight-move
row is re-opened on the prior base. (2) The prior changed the *shape* of the mechanisms, not just their size:
unseen3's economy now comes with material growth (units +0.21) where V06's came from dust; the mouth rule's tax
now lands on productive convoys (Test 3); the crowding cost is still pool-fitted. (3) The two live levers have
clean follow-up forms: trapw20 needs ~+0.03 retention to pass the units lb; unseen3 needs its transit/newborn
churn paid down (L40's fitted mouth cost, L30's siting rule) — and both levers are *map-class* mechanisms (next
section).

### Test 2 — are the two information gains additive?

`clair-07-symseal` = aline-17's change set (symmetry inference + ally right-of-way seal) as a switch on hb1-14.
aline-17 vs its own parent (nodevil, no prior): pool econ +0.025 [+0.005, +0.045], win +6.1 pp, ACCEPT.

**Result (seeds 1–3, both panels): additive off-pool; pool near-miss with one hygiene breach.**

| panel | n | econ~ [90 %] | units@100 | length@100 | win [90 %] | h2h ally |
|---|---|---|---|---|---|---|
| pool | 480 | +0.021 [−0.001, +0.040] | +0.000 [−0.050, +0.080] | +0.030 [−0.026, +0.052] | −0.004 [−0.033, +0.023] | 1.85 → 2.21 (+19 %) |
| gen | 744 | **+0.023 [+0.008, +0.039]** | **+0.062 [+0.021, +0.095]** | **+0.087 [+0.012, +0.120]** | **+0.026 [+0.007, +0.048]** | down |

**Reading.** The two information gains stack where it matters: on the generalisation panel every metric is
positive with a positive lower bound, at aline-17's own magnitudes (her gen: econ +0.012, units +0.076, win
+0.029) — the prior does not consume what symmetry finds (it had not already inferred symmetry). The pool is a
0.001-miss on the economy lower bound with two guard failures: ally head-on +19 % (the prior's traffic +
symmetry's newly paired portals = more crossings; aline-17 on her own base had +7 %) and pool win lb −0.033.
Per-map: dilemma −0.172 and schooltime −0.143 (dilemma is the *other* 32×16 map — hb1-14 runs the D-033 map
identity terms aline's base had removed; the seal/symmetry stack interacts with them), autarky/default/portals/
QoS +0.05..0.07. D-032 verdict: **REJECT by the letter; a stacking candidate, not a dead mechanism.** The h2h
breach is exactly what gustave-07c taxes (L40/S-1 Q4) — the natural next version is symseal + mouthrule on
hb1-14. Combined-panel form (audit b) on this pair: econ~ +0.016 [−0.008, +0.040] — the combined rule is
*stricter* than its point estimates suggest (map-resampling variance), and clair-07 does not accept under it
either; it changes *which question* fails, not this verdict.

**Ledger proposals from this test:** L38 → 0.75 (additivity confirmed off-pool: gen lb > 0 on economy, material
and win; the pool interaction with the D-033 terms is a new, specific question — symmetry on a terms-on base
needs its dilemma/schooltime read before any registration); L33/L40 note: symseal + mouthrule is the obvious
combined mechanism (one fixes what the other breaches).

### Test 3 — does the mouth rule survive the prior?

`clair-08-mouthroute` = gustave-07c (−4 for ending on a portal mouth unless the dragon's own route crosses it
within 3 steps). On its own parent: HOLD — ally h2h −18 % pool / −23 % gen, economy flat.

**Result (seeds 1–3, both panels): the hold does not transfer — REJECT at cost.**

| panel | n | econ~ [90 %] | units@100 | births@100 | win [90 %] | h2h ally |
|---|---|---|---|---|---|---|
| pool | 480 | **−0.078 [−0.096, −0.048]** | −0.086 [−0.139, −0.033] | −0.082 | −0.042 [−0.073, −0.013] | 1.85 → 1.58 (−15 %) |
| gen | 744 | −0.015 [−0.034, −0.003] | +0.029 | −0.007 | +0.006 | 0.98 → 0.81 (−17 %) |

**Reading.** The mechanism still does its job (ally head-on −15 % pool / −17 % gen, the largest h2h cut measured
on this base) but on the prior base the tax lands on *productive* traffic: births −8 %, units −9 %, and the
economy pays −0.078 on the pool — where gustave-07c on its own (nodevil, no prior) parent was flat (+0.001).
The prior's steering legitimately routes through portal mouths far more than V06's did, so a flat −4 there is
no longer taxing loitering; it is taxing the prior's own convoy. **Ledger proposal: L40 → 0.3** (one rejection
on the production base; the anatomy finding — mouth loitering is the h2h channel — stands, and the clair-07
result above says the h2h problem is *larger* on this base (+19 % with symmetry on). Revival form: a mouth cost
fitted to the base's own traffic (gustave-07a's −1.5 dose), or as L33's warding term whose magnitude is fitted
rather than asserted). L33's "prototype without L32" should now name the prior base as its host.

## Per-map decomposition (the lead's direction, 1 Oct: by map as well as collectively)

Tool: `tools/clair/by_map.py` — per-map paired econ deltas with CIs, a **tr-consistency check** (pool delta on
live map M vs gen delta on its transposed twin `var/M_tr`: sign agreement = structure, disagreement = layout
identity — the anti-overfit instrument the OOS rule lacks at this resolution), and an S-1 Q2 slope²-weighted
pooled delta beside the unweighted one (Portals 0.29 counts least, Schooltime 0.49 most).

| lever | where the gain lives (pool; gen tr-twin) | tr-consistency | reading |
|---|---|---|---|
| unseen3 (clair-04) | **trauma +1.64 [+1.61, +1.66]**, queen_of_spades +0.13 (qos_tr **+1.48**), default +0.28 (default_tr +0.43), dilemma_tr +0.13 | big gains AGREE (qos, default, trauma*); devil/autarky disagree only at small magnitudes | a **starved/sparse-opening cluster** mechanism — exactly Esquie's L35 map class (Trauma, QoS, Default; the tempo table has us 26–34 rounds behind on all three). Cutting exploration value makes dragons commit to known food on food-sparse maps; on dense maps it does nothing much (schooltime −0.03). The structure-gated form (L35's recipe: key on the dragon's own food knowledge, not round) should keep the gain and drop the h2h churn that lives on dense portal maps. (*trauma_tr itself reads −0.05 with only n=24; its pool CI is the tightest in the table, so the twin is under-powered, not contradictory — flagged, not counted as agreement.) |
| trapw20 (clair-03) | slithery_fight +0.10, trauma +0.04, autarky +0.02 (autarky_tr +0.013 AGREE), **exactly 0.000** on default/qos/trophy (the penalty never binds differently there) | consistent where it acts | a **corridor/sparse-map** mechanism, inert on dense maps by construction (zero effect = zero overfit surface there). Broad-but-small; no map carries more than a third of the pooled gain. |
| capsel (clair-06) | trauma +0.16 but trauma_tr −0.05; devil +0.08 vs devil_tr +0.81; late p@250 everywhere | incoherent | the pooled late signature is partly layout-dependent — this is what tr-inconsistency looks like, and it strengthens the reject. Also the method note: a lever whose per-map signs do not survive transposition must not be promoted as a global switch. |
| symseal (clair-07) | dilemma −0.17, schooltime −0.14; autarky/default/portals/qos +0.05..0.07 | (Test 2) | the two losses are the dense/identity maps — dilemma is the *other* 32×16 map, where hb1-14's D-033 terms are ON and aline's base had them OFF. Structure interaction, not noise. |

**Why this matters beyond this lane** (L37, tt's per-map rows): the top teams' own spread is per-map — cheji bt
wins 0.97 on QoS and 0.62 on Slithery; Stockfish 0.80 Portals / 0.52 Dilemma — and 50 of 51 top teams carry
significant map fixed effects. A lever that is *inert by construction* on the maps it cannot help (trapw20's
zeros) and *structure-keyed* on the maps it can (unseen3's starved cluster) is the legitimate form of that
specialisation under the OOS rule. The per-map tables for every future Clair candidate go into
`build/clair/bymap-*.txt`; the discipline is: gate on observable structure (D-036), check tr-consistency before
believing any per-map gain, weight pooled claims by Q2 slope² when deciding registration order.

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
| L20 | 0.1 (dormant) → **re-open, 0.3 pending seeds** | this pass, Test 1: four of six single-knob moves screen ≥ +0.03 pool econ on hb1-14 (trapw20 +0.037 lb>0, unseen3 +0.192, allycrowd +0.057, capsel +0.037) where the same knobs measured +0.01–0.03 on V06/nodevil — the revival trigger ("a consistent seat-independent +0.03") has fired at screen level; the extensions at seeds 1–3 decide whether "consistent" holds. |
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

## Standing duty 4 — gate audit (D-032/D-037) — **applied 1 Oct under the lead's authorization**

The lead's instruction (1 Oct, mid-pass): the steward may revise benchmark and validation criteria directly
when the evidence warrants — the goal is winning, and the local gate is an instrument, not an end. Applied to
`docs/analysis/BENCHMARKS.md` §"Start here" (1 Oct revision block) in this branch: (1) the phase-`end` tier
with the cull exemption, (2) either-panel-positive accept with both-panel non-harm, (3) cluster-bootstrap
authority with the borderline rule, (4) the mid-game gap named with its instrument (tempo's net-income curve
extended to r300 as a *new* reference file on the desktop store — the current curve stops at r150 and opening
tempo cannot see mid-game by design). Every flip is listed in the revision block; none of this pass's own
candidates changes verdict under the new rules (a deliberate check that the rules were not written to fit
them). The three findings as analysed before the edit:

**(a) The economy mean is invisible to endgame conversion (L39), and the tier-2 guard outlaws the mechanism.**
Instrument check on this lane's own parent features (pool s1-2, 320 side-games): hb1-14 has 145 round-limit
games, 35 round-limit losses, **21 of them (60 %) with a total-length lead at the end**, and *every*
round-limit loss is a `longest` loss - the crown decides them, exactly L39's claim (tt measured 50 % at s1). A
metric with a 60 % base rate over ~35 events resolves a halving in one panel run; the extractor already carries
the columns (`longest_margin_end`, `total_margin_end`, `reason`).
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
| 1 | **L20 re-opened: the tuning surface on the prior base** | this pass: two knobs clear both panels' economy (trapw20 +0.037/+0.022, unseen3 +0.151/+0.065 tempo-ACCEPT) where V06 measured +0.02 — the cheapest large direction in the programme | (a) trapw20 + a retention nudge (units lb is the only failing guard); (b) unseen3 with its transit/newborn churn paid down (fitted mouth cost / L30 siting); (c) a two-value scan each side of both knobs to map the cliff (dose 4 is null, 3 is huge) | clair follow-up, then lanes |
| 2 | **unseen3 as a structure-gated starved-opening switch (L14 × L35)** | per-map: the whole gain is the starved cluster (trauma +1.64, qos_tr +1.48, default +0.43) — Esquie's L35 class; gate on own food knowledge (esquie-03b's key), not round | unseen cut only when the dragon has seen no food for k rounds / no bed ripening within 8 (esquie-03b's min_age form) — keeps the starved gains, should drop the dense-map h2h churn | clair or M-1 continuation |
| 3 | L39 state-keyed conversion | 0.8 this pass; 60 % of hb1-14's round-limit losses carry a material lead (measured here, 21/35); all four top teams convert | elim-state trigger ("no enemy met for 30+ rounds" for opponent-units ≤5) + co-designed crown/feeder, judged under the proposed phase-`end` tier | tt or re-issue |
| 4 | L27 map-aware prior | every top team's steering uses remembered-map geometry (+0.75–2.59 pp); Ares already keeps the map | tt-09 / tt-11 panel results (running), then map features into the 540-round prior | tt / verso |
| 5 | L38→ stacking: symseal + fitted warding on hb1-14 | Test 2: additive off-pool (all gen lbs positive); symseal's h2h +19 % is exactly what a *fitted* mouth/warding term taxes (Test 3 shows the flat −4 is too blunt on this base) | clair-10 = clair-07 + mouth cost at 07a's −1.5 dose (or fitted to observed mouth traffic), full D-032 | clair follow-up |
| 6 | gate revision (a)+(b)+(c) | the gate cannot see the programme's two biggest live directions: endgame conversion (tt-05 flips to accept-shaped under phase-`end`) and off-pool gains (verso-05); clair-05 shows the gen panel catching what the pool rewards | adopt the three changes in one revision with the re-scored history (this file, standing duty 4); one recompute pass on the desktop | director |
| 7 | L36 opening components | 0.8 measured; gap opens by r25; L35's bed-anticensation and this pass's starved-cluster are two of the four components; production and early-portal use open | per-map r25/r50 percentile targets per component cluster (D-037 as issued) | rc/M-1/K-1 |
| 8 | L33 warding, plain-rule form | S-1 Q4's own-traffic exits; Tests 2+3 jointly say the h2h channel on the prior base is real and needs a *fitted* cost | "don't transit the pair an ally used/is about to use" as a fitted cost on hb1-14 (merges with #5) | re-issue / clair |
| 9 | L30 newborn churn paydown | r3-03 +5 pp win blocked by tier-2; unseen3's newborn cost (+12 %) is the same bill | siting rule for `ACT:tsplit` children (C1-C fix #2), on hb1-14 where the production levers now live | re-issue |
| 10 | L13 momentum scan | 0.4, ownerless since Maelle closed; one cheap scan answers it | momentum_weight/decay scan via alicia-02's runtime overrides on hb1-14 | re-issue |

*(Rows re-scored by this pass: L20 re-opened 0.1 → 0.4 pending the follow-ups; L38 0.7 → 0.75; L40 0.5 → 0.3;
L39 0.7 → 0.8; L12 0.5 → 0.3; L02 0.7 → 0.4; L11 0.35 → 0.3; L34 0.35 → 0.3; L21 0.3 → 0.1 dormant; L14 0.3 → 0.4.
All as proposals in standing duty 1 plus the three test sections; the director applies.)*

## Run log

- 12:16 local — queue launched: parent s1 (both panels) → six knob screens (pool s1) → parent s2, s3 →
  clair-07/08 seeds 1–3 both panels → extract all. ~6,600 games at 9 jobs.
- Screening rule (pre-registered): a Test-1 knob extends to seeds 1–3 + gen only if its pool s1 econ~ point
  estimate ≥ +0.03 (Renoir's V06 effects were +0.01..+0.02, all REJECT; anything ≤ +0.01 reads "bowl holds");
  +0.01..+0.03 adds seed 2 pool only.
