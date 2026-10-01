# Expedition — H-1 hypothesis steward, passes 1–8

**2026-10-01, MacBook; branch `r/expedition`.** Initial evidence cutoff:
`757315abc`; Expedition was created in pass 1. The ledger baseline is
`53a9833bb`. Each pass below records its own continuation cutoff, including
findings whose addenda supersede their headlines. Resume from the latest pushed
Expedition commit and the saved fixture index.

**Current state: autonomous CPU campaign active; no gate verdict yet.** The first
pass created and verified the 14 snapshots, reconciled the ledger, and pushed
`d8bbf8628` to `origin/r/expedition`. The user then approved the push and explicitly
requested long-horizon iteration without routine intervention. Their MacBook
instruction and continuation approval govern the execution adaptation: bounded,
serial CPU-only local games, no GPU training. No contest registration, upload,
activation or promotion; shared ledger/gate edits remain proposals. Preserve
unrelated working-tree changes (including files that appear while this work runs).

## Pass 8 — Schooltime tradeoff and trap activation (2026-10-01)

Resumed from `b96493bc9`. No newer committed lane findings; the audited provisional
S1 next-steps and tempo-tool hashes remain unchanged. Batch 009 completed **27
games in 1,265.4 seconds**: its last admitted parent game took 151.7 seconds and
finished after the 20-minute admission budget. This is the declared finish-current-
game behavior, not an overlapping batch. Report validation now covers **235 games,
117 matched pairs plus one parent awaiting its child**, with seven complete
seed-1 map slices. Replay/source attribution, errors and canonical bookkeeping
checks passed. The report retains **233 arena/replay measurement discrepancies**
and their explanations; they are not silently replaced or treated as corrupt games.
Batch 010 resumed that exact child fixture on Slithery Fight, with one CPU worker,
20-minute admission budget and maximum 96 games. Later games in that running batch
are outside this validated snapshot. No GPU work.

### Complete Schooltime seed-1 slice

Eight frozen opponents × both seats, 16 paired fixtures. Parent 01 wins **15/16**;
mouth 09 wins **14/16**. Hygiene and material improve here without a win gain:

| Measure through r150 | Parent 01 | Mouth 09 |
|---|---:|---:|
| Transits | 501 | 457 |
| Transits followed by death within three rounds | 72/501 = 14.37% | 56/457 = 12.25% |
| Ally head-on deaths / dragon turns | 28/79,016 = 0.354 per 1k | 14/80,099 = 0.175 per 1k |
| Own goals / dragon turns | 580/79,016 = 7.340 per 1k | 533/80,099 = 6.654 per 1k |
| Newborn deaths / splits observed by r150 | 319/1,872 = 17.04% | 300/1,802 = 16.65% |
| Mean total length r150 | 206.8125 | 218.8125 |
| Candidate − parent opening tempo | — | **+0.156 rounds (slower)** |

Mean economy delta: **−0.014689 arena / −0.009187 replay**. Raw pearls r25 delta
+0.125; r50 −0.75; mean r50 field-percentile delta −0.009842. The newborn row retains
the pass-7 snapshot-window caveat. This slice qualifies any claim that mouth
routing always lowers material, while still providing no general beneficial
transfer or acceptance evidence. L40 remains 0.5; no retuning from this prefix.

### Trap arm now has a binding recorded-input case

The original broad sample remains **zero trap divergences in 1,316 turns**.
An additional recorded-input fixture, Slithery Fight A seed 1 / Yuna-v03 dragon
360, supplies 423 turns and **two reply divergences**. The first is turn index 166,
round 243: parent 01 moves north; trap20 moves west, with identical sonar output.
All preceding replies match. Later differences may include internal-state effects;
this establishes decision activation, not improved closed-loop performance.

Fixture SHA-256:
`486b93ae2be32f8f2c57631c53438ea4cc58d56620d28f2b9c724cb2a154ac9b`.
Added a targeted regression to `verify.py`, preserving the original sample and
checking exact input hash, reply coverage and first changed decision. Repeated
recorded-input runs agree, no fallback/missing replies occurred, and restoring
trap weight 30 still restores byte-identical parent runtime source. The narrow
activation check, Python compilation and whitespace checks pass; unchanged runtime
snapshots were not rebuilt or edited. Generated inputs/results stay under `build/`.

**Gate audit and reconciliation:** reviewed L04/L05/L29/L36/L40. Activation removes
one interpretation ambiguity for the pending trap performance test; it does not
raise L04's weight. Schooltime adds a map-specific material counterexample, not a
full-panel verdict. Mean/median, opening/tempo, phase/map, complete-seed coverage,
and sandbox guards remain unresolved as previously recorded. No gate relaxation,
shared-ledger edits or historical verdict flips. The pass-6 ranked ten remain current.

Evidence: `build/expedition/audit-010.log`, `phase-schooltime.log`,
`trap-activation-expanded.json`, and the source/replay-keyed report caches.
Reproduce the map audit with `report.py` and `phase_report.py --map schooltime`.
**Next runnable action:** let batch 010 finish without overlap, validate its saved
rows/replays, finish remaining seed-1 pool slices, then the frozen gen and seeds
2–3 before moving to symmetry and the remaining predeclared arms. No promotion.

## Pass 7 — Queen of Spades and newborn observation window (2026-10-01)

Resumed from `c6b8b8f21`. No newer committed lane findings, ledger or gate changes;
the provisional S1 next-steps and tempo-tool hashes are unchanged. All unrelated
edits remain untouched. Batch 008 completed **60 games in 1,142.6 seconds**, stopping
within its admission budget before Schooltime seat B. Its complete saved output
passed source/replay attribution and canonical bookkeeping: **208 games / 104
pairs**, six complete seed-1 maps plus Schooltime seat A. Batch 009 resumed with
one worker, the same 20-minute budget and maximum 96 games. No GPU work.

### Complete Queen of Spades seed-1 slice

Eight frozen opponents × both seats, 16 paired fixtures. Parent 01 wins **16/16**;
mouth 09 wins **12/16**. Four regressions, no improvements (two-sided exact sign
p = 0.125, without map/selection adjustment). This is still one seed, not a gate
rejection or an independent second failure.

| Measure through r150 | Parent 01 | Mouth 09 |
|---|---:|---:|
| Transits | 256 | 160 |
| Transits followed by death within three rounds | 64/256 = 25.00% | 42/160 = 26.25% |
| Ally head-on deaths / dragon turns | 32/20,286 = 1.577 per 1k | 16/16,133 = 0.992 per 1k |
| Own goals / dragon turns | 174/20,286 = 8.577 per 1k | 137/16,133 = 8.492 per 1k |
| Newborn deaths / splits observed by r150 | 110/492 = 22.36% | 97/393 = 24.68% |
| Mean total length r150 | 44.3125 | 36.0625 |
| Candidate − parent opening tempo | — | **+9.083 rounds (slower)** |

Mean economy delta: **−0.252202 arena / −0.258158 replay**. Raw pearls r25 delta
0; r50 delta −4.3125 and mean r50 field-percentile delta −0.141074. Reduced ally
head-on counts do not establish a beneficial transfer: this slice also has less
transit, lower material, slower tempo and fewer wins. **L40 stays 0.5** while the
fixed full panels continue; do not retune against the prefix or relax a guard.

### Gate audit: distinguish snapshot ratios from child survival

The S1/Expedition displayed newborn ratio is deaths observed by r150 divided by
splits observed by r150. It is not a fully observed ten-round death probability:
children born near the cutoff have less follow-up. Audited the same 16 paired
Portals fixtures directly from cached replay frames, using births through r140
and requiring ten observed rounds (birth ≤ min(140, final round − 10)):

| Portals newborn measure | Parent 01 | Mouth 09 |
|---|---:|---:|
| Existing r150 snapshot ratio | 804/1,945 = 41.34% | 518/1,442 = 35.92% |
| Complete ten-round birth cohort | 719/1,709 = 42.07% | 453/1,258 = 36.01% |
| Births excluded for late observation | 236 | 184 |

The direction persists (candidate − parent −5.41 percentage points snapshot,
−6.06 points complete cohort), so this check supplies **no sign reversal**. It
also changes the birth window and is not a replacement estimate for births
through r150. Proposal: label the existing snapshot ratio precisely and show an
explicit full-follow-up birth cohort alongside it; re-score historical panels
before changing any guard threshold or verdict. No shared scorer is edited.

Reproduce from saved evidence with `report.py`,
`phase_report.py --map queen_of_spades`, and the retained small audit
`build/expedition/audit_newborn_window.py`. Results:
`build/expedition/audit-009.log`, `phase-queen_of_spades.log`,
`newborn-window-portals.json`, and the source/replay-keyed report caches.
The source/reference hashes remain those in pass 5.

**Reconciliation and priorities:** reviewed L05/L29/L36/L40; no new independent
full-panel result, historical verdict flip, or proposed weight change. The ranked
ten from pass 6 remain current. Next: finish Schooltime and the remaining seed-1
pool maps, audit completed map slices, then proceed to the predeclared gen panel
and seeds 2–3. No registration or promotion.

## Pass 6 — audit the new S1 handover evidence (2026-10-01)

Resumed from `1a4887f8b`. Batch 007 finished 24 games in 523.0 seconds; all 148
saved games passed canonical attribution/bookkeeping. Batch 008 resumed with
one worker, up to 96 games in the same 20-minute admission budget. The source
contracts and reference hashes still match. Portals is materially slower than
recent maps, so the time budget, not the game cap, may bind.

A new, untracked lane finding appeared:
`docs/findings/2026-10-01-s1-next-steps.md`. It remains untouched and provisional.
Audited source SHA-256:
`547d56e1344edcc97aada2803cd849353feb939630d332c42a3a77ff95f73210`.
Unlike another small Expedition prefix, its completed saved panel supports a
substantial new reconciliation. No extra games were run for this audit.

### What the saved data actually establish

Read `build/s1/tmp/graft/g01` through `g04` portable tempo extracts and the
`atlas-panel` rows in `build/s1/local/sides/*.parquet`. Each graft has exactly the
same **120 unique fixtures**, seed 1, ten maps × six opponents × two seats, as
both hb1-04 and hb1-12. Identity pairing masks only the candidate bot token in
the fixture basename; all per-map cells contain 12 games.

| Policy | Wins / 120 | Better / worse than hb1-04 | Two-sided exact sign-test p |
|---|---:|---:|---:|
| hb1-04 mimic | 77 | — | — |
| hb1-12 direction-prior reference | 101 | — | — |
| g01, handover r150 | 101 | 26 / 2 | 0.0000030324 |
| g02, handover r250 | 95 | 21 / 3 | 0.00027716 |
| g03, handover r350 | 94 | 19 / 2 | 0.00022125 |
| g04, handover r100 | 97 | 23 / 3 | 0.000087976 |

The reported arithmetic checks out. g01 versus hb1-12 has 11 better / 11 worse
fixtures. These are win-count ties, not equivalence tests. The sign tests treat
fixtures as independent; they do not account for map clustering or selection of
the best among four handover settings. This is one-seed pool evidence, not D-032
acceptance, independent-seed confirmation, OOS transfer or upload readiness.

The portable extracts contain names, outcomes and curves, not complete original
runtime-error logs or frozen opponent source manifests. Their hashes preserve
the audited evidence; they do not retroactively certify full run provenance or
sandbox CPU. This audit verifies reported arithmetic and selected feature parity.

**Opening boundary correction:** matched S1 series supply 31 checkpoints r0–150
for income and loss on 120 fixtures: 7,440 scalar comparisons per graft. g02/g03
match hb1-04 exactly. g01 differs in **69 values, all at r150**; every sampled
checkpoint before r150 matches. Its mean tempo delta is **+0.00258196 rounds**,
which displays as +0.00. Thus the reported rounded tempo is correct, while
“identical opening through r150” is too strong: Ares acts at the boundary. This
does not remove the whole-game win gain. It also does not prove every action or
trajectory identical; this audit checked the saved income/loss curves.

**Mechanism attribution:** inspected g01's `main.cpp`: before r150 it runs the
mimic while updating Ares memory; at r150 it switches the **entire policy** to
Ares. This changes mid-game decisions, later split cutoff and crown/feeding
logic together. “The handover works on this panel” is supported; “crown feeding
alone causes the gain” is not isolated. The r150 point estimate being better
than r250/r350 is itself a reason to test the mid-game contribution.

**Packaging correction:** hb1-14 supplies a compact direction prior to Ares
search (`hb1_dir_lambda`), whereas hb1-04/g01 use a full mimic policy and its
wrappers. Substituting the former is a behavioral transfer experiment, not just
packing the same graft into 4 MiB. No uploadable-graft claim is justified yet.

### Expedition Portals slice: outcome and economy disagree

Completed all 16 paired seed-1 Portals fixtures. Parent 01 won **10/16**, mouth
09 **13/16**: four paired improvements and one regression (two-sided sign-test
p = 0.375). Five discordances are insufficient to establish a win gain. The
latest canonical audit snapshot validates **176 games / 88 pairs** overall,
including all five completed map slices; batch 008 is still running.

| Portals measure through r150 | Parent 01 | Mouth 09 |
|---|---:|---:|
| Transits | 2,104 | 1,543 |
| Transits followed by death within three rounds | 908/2,104 = 43.16% | 608/1,543 = 39.40% |
| Ally head-on deaths / dragon turns | 404/37,805 = 10.686 per 1k | 252/31,667 = 7.958 per 1k |
| Own goals / dragon turns | 1,567/37,805 = 41.450 per 1k | 1,075/31,667 = 33.947 per 1k |
| Newborn deaths / splits | 804/1,945 = 41.34% | 518/1,442 = 35.92% |
| Mean total length r150 | 66.625 | 64.375 |
| Candidate − parent opening tempo | — | **+3.098 rounds (slower)** |

Gross economy delta is **−0.201548 arena / −0.207703 replay** under the same
frozen normalisation. Pearls r50 fall by 5.625 (mean field percentile −0.047072);
mean total length r100 falls 52.625→43.625. Thus lower churn and more wins in
this prefix coexist with lower intake and opening material. This is a useful
**L29/L40 gate tension**, not evidence to waive the economy or material guards.
The fixed panel, independent seeds and existing full-gate requirements remain.

All parent games hit the round limit (16 longest-decided). The candidate has
15 round-limit games (14 longest, one total) and one elimination loss. Mean own
longest at r499 falls 29→26.6875, so the win difference cannot be described as
simply growing a larger own crown. The candidate mean carries the terminal
state forward for its one early-ending game. Comparative opponent effects and
paired trajectories would be needed for a causal account. **L40 stays 0.5**.

Evidence: `build/expedition/phase-portals.log`, `portals-terminal.json`,
`audit-008-mid.log`, and
`build/expedition/replay-panels/expedition-09-mouthroute-z1-portals-phase.json`.
Phase/reference hashes are unchanged from pass 5. Next: complete batch 008,
validate its full output, and audit Queen of Spades/Schooltime at complete
map/seed boundaries; continue the predeclared mechanism queue.

### Ledger proposals and the next decisive tests

- **L03 0.7→0.7:** add direct evidence for a useful fixed-round policy handover.
  State-conditioned handover remains untested. Raise its decisive-test priority:
  same crown settings, fixed r150 versus an actor-observable state trigger,
  independent seeds and structural OOS maps. No map-name switch.
- **L39 0.7→0.7; L15 0.3→0.3:** conversion remains plausible, but the whole-policy
  switch is not a crown-only ablation or a test of decaying-consensus crown
  location. Ask S1/TT to compare g01 with only its post-handover crown/feeding
  disabled, keeping the other Ares decisions; retain elimination and total-material
  guards and report material-leading round-limit losses. Owners are recommendations,
  not dispatched tasks. This is the updated rank-3 test below.
- **L31 0.5→0.5; L32 0.4→0.4:** a clock-driven whole-policy switch does not test
  per-dragon state modes, hysteresis, or belief-weighted evaluation. Do not credit
  those mechanisms with this gain.
- **L27 0.8→0.8:** retain the distinction between a learned direction prior and a
  full mimic. The existing L16 increase proposal remains unchanged; no second
  step for the same teacher/transfer family.
- **L36 0.8→0.8:** new split-stall tables agree with our earlier cached audit:
  .107/.089−1 = 20.2% more intake per turn in r20–39; high split rates conditional
  on eligibility do not mean a reluctance to split. The “us” cohort is mixed
  historical team-7 bots, not exact-source Expedition 01. Keep rank 1's matched
  source/cohort test; timing/foraging causality is still an intervention question.
- **L37 0.8→0.8:** the authenticated atlas supersedes “the best local niche has
  no live occupants”: it overlaps the roughly 1960–2040-Elo group. Verified
  **65,412/81,186 = 80.57%** authentic side-games, with 3,006 decoy flags. Treat
  decoy and unranked-variant labels separately. A future authenticated reference
  may restore appropriate SSS/Cutlery samples, but never rebuild this experiment's
  frozen reference in place. Guarded tempo still measures an opening, not all-game
  performance; the graft's win gain and near-zero tempo change illustrate that.

Audit artifacts: `build/expedition/graft-audit.json`, `graft-opening-parity.json`,
`graft-parent-rows.json`, and `s1-next-steps-audited.md`. Extract-set fingerprint:
`745250a3b38d4c5617a9663191bb6522cf5cbe32b881bb11d6c822c87d5637e4`;
parent-row fingerprint:
`5a4cea6787851dc1259c640cb57718c9a17022aeba96f2646b17256d28e053d1`.
The small reproducibility scripts are `build/expedition/audit_graft{,_opening}.py`.
No replay payloads, cache state, or other lane edits are staged.

**Ranked ten:** updated below to include L03's now-cheap handover test, displacing
L12 from the issue list (its prepared Expedition experiment remains queued).
Weights themselves do not change in this pass. Rows reviewed: **L03, L15, L16,
L27, L31, L32, L36, L37, L39, L40**. No historical gate verdict is rewritten.

## Pass 5 — third portal-map slice and bounded throughput (2026-10-01)

Resumed from pushed commit `99fc1b782`. Batch 006 completed 24 games in 99.8
seconds; the 124-game snapshot passed the canonical evidence audit. The remaining
Prisoners Dilemma fixtures then completed and passed phase/bookkeeping checks:
four complete seed-1 maps, **64 pairs / 128 validated games**. Batch 007 continues
on Portals. Full pool and gen coverage remain incomplete.

**Prisoners Dilemma, seed 1, eight opponents × both seats:** parent 01 and mouth
09 each won 15/16. Measures below use identical paired games through r150.

| Measure | Parent 01 | Mouth 09 |
|---|---:|---:|
| Transits | 205 | 126 |
| Transits followed by death within three rounds | 18/205 = 8.78% | 19/126 = 15.08% |
| Ally head-on deaths / dragon turns | 16/17,394 = 0.920 per 1k | 14/15,489 = 0.904 per 1k |
| Own goals / dragon turns | 318/17,394 = 18.282 per 1k | 298/15,489 = 19.239 per 1k |
| Newborn deaths / splits | 185/492 = 37.60% | 194/466 = 41.63% |
| Mean total length at r150 | 19.625 | 18.1875 |
| Candidate − parent opening tempo | — | **+2.768 rounds (slower)** |

The apparent safety improvement on Autarky/Default **does not generalise even to
all completed seed-1 portal maps**: here exposure falls while transit-associated
death incidence rises. Neither the 6.30 percentage-point rate increase nor the
other descriptive differences is an independent-seed estimate. Do not count
maps from this scan as independent rejections. **L40 stays 0.5**, and no variant
is tuned against this prefix.

Matched economy sensitivity on this complete map: arena **−0.008886**, replay
**−0.008457**, using the previously specified four-checkpoint normalisation.
Again no sign reversal. Raw pearls r25 delta **+0.4375**, r50 **−0.6875**; mean
r50 field-percentile delta **−0.009275**. The r25 percentile remains unavailable.
This adds a phase-specific warning: a small early intake gain does not establish
sustained opening benefit. Whole-game wins are unchanged despite slower tempo;
keep outcome, material and hygiene measures distinct. No gate verdict is issued.

### Source reconciliation and run bounds

- No newer committed lane findings, ledger, or gate changes. An unrelated
  working-tree edit to `tools/s1/tempo_gate.py` adds portable `.tempo.json` export
  and import. Reviewed the diff: `extract`, `lag`, and `tempo` formulas are
  unchanged. Left it and the new Ouroboros snapshot untouched.
- Conservative phase-cache hashing detects that source change. New phase hash:
  `e18ca759e9f96c2ade68fa57787537112df68366be87aecdca9fa33e63868d50`;
  current tempo module hash:
  `ebea67941aabc5e14a2e7e5d4a6af9f0a2c4e0beaf7e0959ad9a459d64e5e38c`.
  The frozen reference hash remains unchanged. This is a source-version boundary,
  not a new scoring formula; prior reports remain intact under their old hashes.
- Recent 24-game batches took 99.8–336.4 seconds. Host load at this pass was about
  14 on 18 logical CPUs. Updated the heartbeat to permit **up to 96 games within
  the same 20-minute admission budget**, still one game worker and an exclusive
  lock. The current 24-game batch finishes as launched. A started game may finish
  after the admission budget; reduce the cap if throughput/load warrants it.
  No change to fixture order, source contracts, stopping criteria or GPU policy.

Evidence: `build/expedition/audit-007.log`, `phase-dilemma.log`,
`dilemma-sensitivity.json`, and
`build/expedition/replay-panels/expedition-09-mouthroute-z1-dilemma-phase.json`.
Only this status changes in this pass; shared tools and measured bot snapshots
are untouched. Next: validate the finished Portals batch, complete its map/seed
slice, and continue the fixed panels using the larger bounded invocation below.

**Rows reviewed:** L29/L36/L37 (phase and gate interpretation), L40 (map-dependent
mouth-rule transfer). **Proposed weights and ranked ten remain unchanged**:
there is no independent full-panel result or historical verdict flip to justify
re-ranking or another weight step.

## Pass 4 — second map and measurement sensitivity (2026-10-01)

Resumed from pushed commit `346aef836`; no newer tracked lane, ledger or gate
commits. Unrelated working-tree changes remain untouched. Batch 004 completed
24 games in 223.4 seconds; its 76 saved games passed replay attribution and
bookkeeping. Batch 005 resumed at Devil A, Sinbad under the exclusive lock.
Host load was about 26 on 18 logical CPUs; kept one game worker and the existing
24-game cap rather than increasing concurrency.

**Default, seed 1: complete 16 paired fixtures**, all eight frozen opponents,
both seats. Parent wins 13/16, mouth wins 12/16. Through r150:

| Measure | Parent 01 | Mouth 09 |
|---|---:|---:|
| Transit volume | 707 | 573 |
| Transits followed by death within three rounds | 90/707 = 12.73% | 62/573 = 10.82% |
| Ally head-on deaths / dragon turns | 42/30,231 = 1.389 per 1k | 42/28,850 = 1.456 per 1k |
| Own goals / dragon turns | 98/30,231 = 3.242 per 1k | 75/28,850 = 2.600 per 1k |
| Newborn deaths / splits | 77/527 = 14.61% | 73/479 = 15.24% |
| Mean total length at r150 | 50.375 | 45.6875 |
| Candidate − parent opening tempo | — | **+1.108 rounds (slower)** |

As on Autarky, lower post-transit death incidence accompanies lower transit
volume and retained material. This is a second map within the **same seed and
same experiment**, not an independent rejection. **L40 stays 0.5**; continue the
predeclared panels without tuning against this prefix.

**Zero-portal control:** Devil has zero portal edges. All 16 seed-1 paired
fixtures match on every arena statistic for both teams, outcome, round count,
error list and end reason. This supports the intended inactive mechanism on a
map with no portal mouths; it is not evidence for a strategy gain. The canonical
phase report also matches exactly: zero transits, an unmeasured transit-death
rate (not zero risk), and zero tempo delta. Batch 005
completed its 24 games in 147.9 seconds, bringing saved coverage to 100 games
(50 pairs), all subsequently passing canonical attribution and bookkeeping. Batch 006 resumed on Prisoners Dilemma under the same bounds.

### Gate sensitivity on the completed map slices

`report.py` now displays arena and replay mean-economy deltas on identical paired
fixtures and the same frozen per-map field-median denominators. For each fixture,
normalise pearls at 50/100/150/250 by the corresponding field median, average the
four checkpoint deltas, then average fixtures. These are descriptive point
estimates, not confidence intervals or gate outcomes. Replay measurements do not
silently replace the historical arena diagnostic.

| Map, 16 pairs each | Arena mean-economy delta | Replay mean-economy delta | Raw pearls r25 delta | Raw pearls r50 delta | Mean r50 field-percentile delta |
|---|---:|---:|---:|---:|---:|
| Autarky | −0.001287 | −0.002696 | −0.0625 | +0.5000 | +0.011208 |
| Default | −0.059894 | −0.056943 | 0.0000 | −0.1875 | −0.008366 |

**No sign reversal on either completed map.** The arena/replay discrepancy is
real but does not explain away these two point-estimate declines. This is not a
re-scoring of a historical verdict and supports no retroactive accept/hold flip.

**Reference coverage gap:** the frozen `field_references.json` and
`field_distributions.json` include pearls r50 but no pearls r25. The report
computes empirical percentiles with ties counted half at r50, reports raw r25,
and marks its percentile as unavailable. It does not substitute r50 or infer an
r25 distribution. To fully implement D-037, the director needs a separately
versioned r25 reference derived from the appropriately filtered field corpus;
keep its source/version distinct from this frozen experiment contract. This is
an explicit prerequisite to a full opening-percentile claim, not a gate waiver.

Verification: 11 no-game checks passed; added zero-inflated tie handling and
missing-reference tests. The report records its own source hash separately from
the canonical extraction hash. Existing source-frozen game contracts and all bot
snapshots remain unchanged. Evidence: `build/expedition/phase-default.log`,
`build/expedition/replay-panels/expedition-09-mouthroute-z1-default-phase.json`,
`build/expedition/sensitivity-005.log`, and the latest `<candidate>-report.json`.
The phase/reference hashes remain those recorded in pass 3.

**Reconciliation / ranked ten:** no new independent full-panel result; all
proposed weights and the ranked ten below remain unchanged. Reviewed **L29,
L36, L37, L40**. The apparent hygiene/strength contradiction now has an explicit
exposure and material explanation to test across the remaining maps and seeds.
Next: finish the running mouth batch, validate it, and resume at the next fixture;
refresh phase reports at complete map/seed boundaries. No registration or promotion.

## Pass 3 — first map slice and phase audit (2026-10-01)

Resumed from pushed commit `74d0caaeb`. No tracked lane findings, ledger, or gate
commits changed after that cutoff. A newly present, untracked S1 candidate roster
is treated as provisional evidence and left untouched. Batch 002 completed 24
new games in 265.3 seconds; all 28 then-saved replays passed attribution and
bookkeeping. Batch 003 resumed under the exclusive lock. Host load was about
21 on 18 logical CPUs, so retained one game worker and the 24-game cap.

**First complete map × seed slice:** Autarky, seed 1, eight frozen zoo opponents,
both seats, 16 paired fixtures / 32 games. Parent 01 and mouth 09 each won 16/16.
These are ordered-prefix data, not a completed panel or an independent-seed test.
All figures below use the same paired games and events through r150; a transit
at r150 may be associated with its death up to three rounds later.

| Measure | Parent 01 | Mouth 09 | Interpretation at this resolution |
|---|---:|---:|---|
| Transit volume | 372 | 349 | −6.2%; reduced exposure must accompany the survival number |
| Transits followed by death within 3 rounds | 51/372 = 13.71% | 39/349 = 11.17% | Descriptive improvement, not causal attribution to the portal |
| Ally head-on deaths / dragon turns | 30/49,534 = 0.606 per 1k | 32/48,170 = 0.664 per 1k | All locations, **not** ally head-on per transit |
| Own goals / dragon turns | 565/49,534 = 11.406 per 1k | 528/48,170 = 10.961 per 1k | Modest descriptive improvement |
| Newborn deaths / splits | 200/1,196 = 16.72% | 200/1,114 = 17.95% | Worse ratio despite unchanged death numerator |
| Mean total length at r150 | 73.00 | 65.0625 | −10.9%; prevents treating hygiene alone as success |
| Opening tempo, candidate − parent | — | **+1.028 rounds** | Slower; frozen top-ten Autarky reference, no CI claim |

The retained reference hash is
`c4c4138fd99f45379f58ab9598059d76af1698a4dab9019a055f483561a3740f`.
This slice establishes a measurable mechanism tradeoff, not acceptance or
rejection. **L40 remains 0.5**. Do not terminate the predeclared test based on this
map, make a tuned mouth variant from it, or count it as an independent rejection.

`phase_report.py` now validates source/replay contracts and canonical bookkeeping,
pairs exact fixtures, computes S1 opening tempo, and retains numerators and
exposures for guard rates. It emits no verdict. Its income/loss curves, outcome,
and transit-death rate matched the existing S1 tempo extractor exactly on a
saved pilot replay. Nine no-game tests pass, including unequal exposure pooling
and a no-transit case that must remain unmeasured rather than become zero risk.
No shared tools or measured bot sources changed.

```sh
PYTHONPYCACHEPREFIX=/tmp/expedition-pycache .venv/bin/python bots/expedition-00-hb540-control/phase_report.py --candidate expedition-09-mouthroute --panel z1 --map autarky
```

Evidence: `build/expedition/replay-panels/expedition-09-mouthroute-z1-autarky-phase.json`,
`build/expedition/phase-autarky.log`, and source/replay-keyed `phase-analysis/` caches.
The phase report's analysis hash is
`1848177d5b4b740462d2aad9655e7301fa94c7d0fba3014ec12e61de1e837792`.
Next: finish the current mouth panel, refreshing `report.py` after each batch and
this phase report at completed map/seed stages; then proceed through the existing
queue. All other full-gate requirements and promotion restrictions remain.

### Reconciliation, contradiction and gate notes

- **L29, L36, L37:** the provisional
  `docs/analysis/benchmarks/candidates-2026-10-01.md` points to the existing S1
  atlas: 20,243 games / 247 bots; reported local tempo–strength Spearman −0.84.
  It also lists hb1-04 tempo −10.7 but win share 0.64 versus hb1-12's −3.8 and
  0.84. Tempo is associated with strength, not sufficient to select a winner.
  Retain whole-game and material/conversion guards. Do not switch the frozen
  opponent panel mid-experiment to its proposed 20-bot roster.
- **L39 apparent contradiction:** the existing
  `docs/findings/2026-10-01-s1-atlas.md` reports top-one length share negatively
  associated with strength (local −0.79; live −0.46). That observational,
  aggregate association does not refute TT's late conversion mechanism. Phase
  and selection differ. The decisive test remains a paired conversion ablation
  reporting r490 concentration conditional on survival, all-game outcomes, and
  material-leading round-limit losses, with elimination and total-material guards.
  **L39 stays 0.7**, and a generally higher concentration is not the objective.
- **Gate audit:** S1 `tempo_gate.py` prints its guard rates as context rather than
  including them in the tempo verdict, and its guard display averages side-game
  rates. Expedition's phase audit uses exact paired exposure totals and prints
  no verdict. The two displays answer different aggregation questions; do not
  silently replace historical thresholds. The Autarky slice illustrates why a
  lower post-transit death rate alone is insufficient. No historical verdict flip
  is supported by this slice.

**Weights and ranked ten:** unchanged from pass 1. The existing ranked table
below remains the current issue list; this single-map test supplies no new
independent full-panel result. Rows reviewed: **L29, L36, L37, L39, L40**.

## Pass 2 — durable continuation and measurement audit (2026-10-01)

- Active same-chat heartbeat: `expedition-autonomous-iteration`, every 30 minutes.
  It continues the next decisive work, stays quiet on unchanged state, and reports
  meaningful findings, completed stages, or failures requiring attention. Local
  scheduled work requires the Mac and app to remain running.
- First native throughput pilot: four parent games, Schooltime, seed 1, A/B vs
  Fenrir-18 and Yuna-05; four wins, 500 rounds each, 26.7–48.5 s/game, no bot errors.
  These old rows lack replays and are **throughput evidence only**, at
  `build/expedition/panels/expedition-01-nodevil-d7ba8adac780/z1.jsonl`.
- New replay-saving pilot: parent 01 and mouth 09, Autarky, seed 1, seat A,
  Chaewon-04 and Fenrir-18: **2 paired fixtures / 4 games**, all wins, no errors;
  8.3–16.5 s/game, 48.6 s total with overhead. All four saved replays passed the
  nine extraction checks (36 zero residuals). This tiny, ordered prefix is not a
  strength estimate; no ledger weight or frontier change follows.
- Four of four games differ between arena and canonical replay measurements.
  Concrete same-game example, 09 vs Fenrir: arena intake r100 **81**, replay **86**;
  arena units/length r100 **14/35**, replay **13/33**. The arena infers intake from
  a dragon's later input and sums actors at their turn; replay extraction counts
  events and round-start material. Source inspection explains why the estimands
  differ; no claim that one universal offset reconciles them. Preserve both raw
  sources and re-score the same saved games. Do not silently feed changed metrics
  into historical gate thresholds. No historical accept/hold flips inferred.
- `campaign.py`: serial, bounded, paired fixture resumption, frozen candidate and
  opponent hashes, map/reference/arena hashes and toolkit version; replay hashes,
  both-team errors, exclusive campaign lock, atomic result index, pending-result
  recovery. A failure or orphan replay stops blind reruns for inspection.
- `report.py`: canonical extraction cached by analysis-source and replay hashes,
  attribution/bookkeeping checks, coverage, per-fixture measurement discrepancies.
  Incomplete coverage produces **no gate verdict**. Complete panels permit the
  inherited arena mean-form diagnostic only; all other gate requirements remain.
- Seven no-game tests pass: recovery before/after replay publication and after
  index publication, corrupt/misattributed/error/source-mismatched evidence,
  duplicates, interrupted index writes, and refusal to rerun an orphan replay.
  No shared bot/tool source changed. `PYTHONPYCACHEPREFIX=/tmp/expedition-pycache`
  avoids macOS's default compiled-Python cache outside the allowed folder.

### Next runnable action and continuation contract

Use **campaign.py**, not the older panel.py launcher, for all new games. Queue:
09 mouth, 08 symmetry, 06 crowding, four risk parameters, then all five sparsity
settings. Seed 1 covers both panels before seeds 2–3; every candidate fixture is
paired with the reusable parent. Freeze/validate sources on every continuation;
never combine changed sources. An active lock means leave that batch alone.

```sh
PYTHONPYCACHEPREFIX=/tmp/expedition-pycache .venv/bin/python bots/expedition-00-hb540-control/campaign.py
PYTHONPYCACHEPREFIX=/tmp/expedition-pycache .venv/bin/python bots/expedition-00-hb540-control/campaign.py --execute --minutes 20 --max-games 96
PYTHONPYCACHEPREFIX=/tmp/expedition-pycache .venv/bin/python bots/expedition-00-hb540-control/report.py --candidate expedition-09-mouthroute
PYTHONPYCACHEPREFIX=/tmp/expedition-pycache .venv/bin/python bots/expedition-00-hb540-control/test_campaign.py
```

Live, untracked evidence: `build/expedition/replay-panels/`, `progress.json`, and
`<candidate>-report.json`; pilot log `build/expedition/replay-pilot.log`, audit log
`build/expedition/replay-audit.log`. Reports are snapshots; read the row counts
for current coverage. Contracts give full hashes; parent prefix `d7ba8adac780`,
mouth prefix `4876038b4978`. Generated replays/indices/cache remain out of Git.

At each experimental stage, inspect changed findings since the preceding pass,
reconcile the existing proposals below, and update the ranked ten. Finish
canonical/arena sensitivity, tempo, opening percentiles and guard reporting
before an accept proposal. Neither a one-seed screen nor native CPU timing is
sandbox acceptance. No new independent strategy result in this infrastructure
pass: **all proposed weights and ranked ten below remain unchanged**. Rows
reviewed here: L21/L29/L37 (measurement/gate), L40 (paired pilot still incomplete).

## First-pass experiment contract

The prior donor is `hb1-14-prior-r540`, with its 540-round model unchanged.
Source inspection confirms that it still has the three `32×16` identity terms
and the V06 caps (late 48, sparse 64), as Verso's cycle-2 note also says. D-033
therefore needs an explicit ablation before treating this as an OOS parent:

- `expedition-00-hb540-control`: exact runtime-source copy of hb1-14, provenance only.
- `expedition-01-nodevil`: only those three identity terms disabled. Common parent
  for every mechanism below; **partially measured, not accepted**. Search caps retained.

This makes the test a prior-bearing, identity-free HB base test, not a literal
unchanged-hb1-14 gate. Report 01 versus 00 separately; never attribute that delta
to a tested mechanism. No Lune cap change is bundled into this base.

| Requested question | Expedition versions / one mechanism each | Result and proposed weight consequence |
|---|---|---|
| Is the tuning surface still flat on the prior base? | 02 threat weight 1→0.5; 03 revisit 0.15→0.05; 04 trap 30→20; 05 exploration 5→3; 06 Maelle ally target weight −1.4; 07a–e Maelle sparsity selector `(lo,hi)=(48,160),(48,384),(48,768),(160,384),(160,768)` | **UNMEASURED.** No new weight change from these builds. A robust pass reopens the corresponding prior-base question; no passes would bound these tested settings, not establish that every Tyr evaluation is a flat bowl. |
| Are information gains additive? | 08 symmetry inference, exactly the Aline-13 component retained in Aline-17, on 01 | **UNMEASURED.** L38 stays 0.7. The Aline-17 ally right-of-way seal is excluded to isolate symmetry; a later separate seal/stack test is needed to reproduce the full accepted Aline package. |
| Does the mouth rule survive the prior? | 09 Gustave-07c: weight 4, any portal mouth, route exemption within 3 steps, on 01 | **INCOMPLETE.** Seed-1 map slices above; no gate verdict. L40 stays 0.5; a hygiene-only hold does not raise it. |

The sparsity settings reproduce **all five completed Maelle F5 settings**, rather
than choosing one after seeing a new result. Maelle's original parent used Lune
caps; this transfer uses HB caps, an intentional host/base distinction. Crowding
ports only Maelle's ally grid and target consumer (decay .90, blur 2, saturation .30).
It does not silently enable food, enemy, death, or move-feature consumers.

### Verification completed

- All 14 snapshots compiled natively. The inherited official helper uses C++20
  (`unordered_map::contains`, defaulted comparisons); C++17 compilation fails on
  the unchanged control. Used C++20, preserving the helper and donor source.
- Runtime SHA-256 manifest: `bots/expedition-00-hb540-control/manifest.json`.
  Exact control matches hb1-14; every direction-model header is byte-identical.
- Maelle ally-feature donor parity: **175/175 values identical**, including wrapped
  boundaries, body/head observations, enemy exclusion, and skipped-round decay.
- **1,316 recorded input turns per arm**, six long-lived dragons from Schooltime A,
  Portals B, Trauma B. No missing replies or fallback logs.
- Switching off crowding, sparsity, symmetry, and mouth costs restores **zero
  command/sonar divergences** from 01; enabling identity restores zero divergences
  from 00. Restoring the four parameter-only arms gives byte-identical parent source.
- Enabled command divergences versus 01: threat 1, revisit 9, trap **0**, exploration
  17, crowding 24, sparsity 96/119/120/119/120, symmetry 164, mouth 7. Trap is wired
  into live scoring but did not alter that sample; pass 8 adds a binding trap case
  from additional recorded inputs. These are activation checks, not wins.
- Runtime-source ZIPs are 3,919,960–3,921,422 bytes, below 4 MiB. This is a local
  packaging check, not a judge sandbox CPU probe or confirmation of submission acceptance.
- Required bounded tournament dry run: 01 vs 09, Trauma/Portals/Schooltime,
  both seats, **6 planned matches; none executed**.

Reproduce the no-game checks:

```sh
.venv/bin/python bots/expedition-00-hb540-control/verify.py
.venv/bin/python bots/expedition-00-hb540-control/panel.py expedition-09-mouthroute
.venv/bin/python tools/benchmarking/tournament.py --bots expedition-01-nodevil expedition-09-mouthroute --maps trauma portals schooltime --jobs 1 --dry-run
```

Outputs: `build/expedition/{compile.json,verification.json,verification.log}`.
Recorded inputs: `build/ra/golden/ares06-schooltime-A-1.jsonl` and
`build/cx/golden/{portals-B-1,trauma-B-1}/yuna-v03-core.jsonl.gz`.
Open-loop replay parity verifies implementation, not closed-loop strength.

### Predeclared panel (execution superseded by pass 2 above)

Predeclared panel: seed 1–3, both seats; pool = eight ZOO opponents × ten maps
(**480 fixtures/arm**); gen = four Aline opponents × 29 `maps/new` and transposed
maps (**696/arm**). Exclude `maps/pub/*_rec` under D-029. Opponents and maps are
read from `tools/rb/run.py` and `tools/rb/gate.py`; the dry run prints source-keyed
output paths. There are 12 mechanism candidates plus one reusable parent:
**15,288 games** for all complete panels, before the separate base ablation.
Do not describe this whole scan as a 25-minute task. The pass-2 continuation above
authorizes bounded Mac execution and supersedes the original desktop-only plan.

The original launcher below is retained for provenance. **Use campaign.py above
for new execution**, because these older launch commands do not retain replays:

```sh
# Repeat a bounded invocation to resume; build output stays in Expedition's folder.
.venv/bin/python bots/expedition-00-hb540-control/panel.py expedition-01-nodevil --run --jobs 1 --budget 180
.venv/bin/python bots/expedition-00-hb540-control/panel.py expedition-09-mouthroute --run --jobs 1 --budget 180
.venv/bin/python bots/expedition-00-hb540-control/panel.py expedition-09-mouthroute --score
```

Scoring refuses missing, duplicate, misattributed, or errored fixtures. It labels
the inherited Aline **mean-form** gate explicitly and includes its fixture-cluster
intervals. It does not claim to implement the median-form gate, tempo, per-map
r25/r50 percentiles, or sandbox metering. Those remain required before any accept
proposal. The differing gate implementations below must be resolved in the report,
not hidden by choosing whichever gives a positive verdict.

## Evidence reconciliation — proposals for the director

Current weights are read from the ledger, not copied from stale lane tables. Each
proposed decrement is at most one step; multiple settings in one scan count as one
result. No hypothesis is made dormant by a single experimental rejection.

| Row | Current → proposed | Evidence, number, and interpretation |
|---|---|---|
| L02 | **0.7 → 0.5** | Maelle F5 completed five selector settings; economy −0.020…−0.031 with lo48 and −0.015/−0.029 with lo160. Gustave 04a is corroborating but a different selector (−0.043). Remove the unqualified recommendation to key caps on sparsity. This downweights that tested form, not all volatility/clock selectors. Prior-base question remains open. |
| L12 | **0.5 → 0.3** | Gustave 02b vs 02a: −0.003 [−0.020,+0.023]; 95.5% of factors exactly 0.70. Pure density bonus at weights 3/6: +0.008/−0.005, intervals straddling zero. The old “first state-memory economy gain” attribution is not supported. Maelle crowding still raises material and cuts deaths but loses gen p@250 −0.061; retain it as an unresolved consumer on the new base. |
| L16 | **0.5 → 0.7**, narrowly | Silent row: compact learned direction decisions now run in C++ and transfer. Verso cycle 0: +0.052 [+0.019,+0.081] pool economy, win +0.150; L27 already records this. Replace “no infrastructure” and the R-5 prerequisite. This is not evidence for replacing the whole policy with a weight table. No second increase to L27 for the same result. |
| L21 | **0.3 → 0.1 by superseding rule** | D-032 explicitly replaced the fixed single-seed +0.05 lane gate; this is rule dormancy of that gate shape, not experimental dormancy of retention. Preserve historical verdicts and the separate dev-screen threshold. |
| L34 | **0.35 → 0.3** | Verso “Tier questions”: CNN+GRU equal-data addition ≤±0.2 pp, dropped under its predeclared rule; probes recover reach R² .75 and food density .48. One negative representation result, not proof that all learned memory is useless. TT history gains under 1 pp do not test an internal map or learned long-horizon state. |
| L13 | **0.4 → 0.4** | Do **not** downweight from Maelle's other zero optima. Its final report explicitly lists momentum as **not run**. Monoco target hysteresis 1.25→1.75 lost −0.0435 economy, but is a different consumer. |
| L37 | **0.8 → 0.8; rewrite evidence/claim** | Specialisation remains measured. Q2b/Q2c overturn “Portals is noise”: clean-map Elo slope .42 vs Schooltime .64; map-specific held-out strength adds +.28 skill on Portals. Low global-Elo predictability is not irreducible game randomness. Withdraw the stale 1/9-weight justification pending gate sensitivity analysis. |
| L39 | **0.7 → 0.7; annotate** | TT now finds conversion in four top teams, not two. tt-05 vs hb1-14: both 141–19; r490 longest 27→32, concentration .34→.56, material-leading round-limit losses 50%→8%; elimination W/L 79–5→74–6. Ramps lose 3/9 zoo games. Opponent unit count at r300 is **not directly observable**, explicitly stated by TT; the ledger currently calls it observable. |
| L36, L17 | **0.8 / 0.1 unchanged** | Existing split-stall rows, re-audited below, favour an eligibility/foraging explanation over declining available splits. They do not establish the cause of HB's opening or revive production pressure without a surplus. |
| L23, L40 | **0.3 / 0.5 unchanged** | Gustave 07c is a stateless mouth rule, not evidence that L23's sonar HOLD packet works. Its confirmed hygiene hold must not become the lane's proposed L23 .3→.6 jump. |
| L03, L04, L05, L11, L14, L20, L24, L27–L33, L35, L38 | **unchanged** | Preserve already-incorporated results; qualify consumers and hosts rather than counting the same findings twice. In particular Maelle's unfinished SPSA is “not converged/stopped,” not a completed joint-optimisation rejection. L35 already resolves Esquie's proposed duplicate L31; Gustave's proposed new L30 belongs under existing L31, not production L30. |

Pointers: `claude/{maelle,rc,verso,tt,monoco}-status.md`,
`docs/findings/2026-09-30-{maelle-state-features,rc-lane,s1-Q2-map-predictability}.md`,
and D-032–D-039. The other ledger rows remain unchanged.

### New audit of existing split-stall data

Read 327 cached side-game records under `build/s1/out/splitstall/`; all 165 top-ten
records join to ranked games. Our 162 records include only 43 ranked games and
pool historical team-7 submissions, so the comparison is descriptive, not an
exact-source HB comparison. Source-set SHA-256:
`a95a9519c84db0006286ac4760333acea065af1f1f0bcef946e0f088b2f40a9c`.

| Window | Cohort | Dragon-turns | Length ≥4 | Split when eligible | Split when eligible + ≥2 free head exits | Eats/turn |
|---|---|---:|---:|---:|---:|---:|
| r20–39 | top ten, ranked | 32,735 | 8.18% | 56.63% | 53.87% | .1068 |
| r20–39 | us, mixed modes | 28,914 | 5.10% | 75.64% | 95.25% | .0889 |
| r40–59 | top ten, ranked | 44,283 | 7.97% | 52.15% | 45.99% | .0957 |
| r40–59 | us, mixed modes | 35,194 | 5.24% | 75.34% | 95.10% | .0929 |

Our bots usually take the split when eligible; they reach that length less often.
Two free **head** exits are only a proxy, not a validated safe-child-split test.
Next decisive diagnostic: the same decomposition on exact-source 01 and hb1-14
panels, matched by opponent/map/seat, tracking intake before eligibility and child
survival. Do not turn a pooled correlation into a split-weight patch.
Reproduce: `tools/s1/splitstall.py report`; Expedition's checked audit summary is
`build/expedition/splitstall-audit.json`. No new replay decoding or games were needed.

## Contradictions and the tests that resolve them

1. **Memory works / memory does nothing.** Sciel's scalar value cut, Maelle's ally
   target cost, TT's local-view history, and Aline's inferred map are different
   inputs and consumers. Gustave already supplies the decisive flat-factor control
   for Sciel. Next: 06 and 08 vs 01, with activation histograms and phase metrics;
   TT's pending internal-map feature ablation stays a separate offline question.
2. **“Gate-passing prior” / HB's own HOLD reports.** HB used the old scorecard;
   Verso's own prior passed its D-032 implementation. These are different bases and
   statistical tests. Preserve both records. Compare exact fingerprints on one
   frozen panel and print mean and median estimands, not a merged “HB passed.”
3. **Portals noise / reproducible specialism.** Q2c's cleaned slope gives relative
   squared weight (.42/.64)² = **.431**, versus the old (.16/.49)² = **.107**.
   Re-score identical fixture data under equal, old-Q2, and clean-Q2 weights before
   adopting any. Keep a portal-signature guard so global rating fit cannot erase
   specialist losses.
4. **Endgame conversions fail / top teams all convert.** TT05 breaks even overall
   while changing win modes; “57%” in the older HB12 result is the fraction of
   **round-limit losses** with a material lead, not 57% of all round-limit games.
   Test exact-source conversion against converting opponents with elimination
   guards. First validate an actor-observable enemy-contact proxy; never give the
   bot the replay-only opponent unit count.
5. **Opening production gap / split policy too reluctant.** The cached diagnostic
   supports low eligibility; its cohorts are not a controlled intervention.
   Repeat by exact bot source before changing split thresholds.
6. **Verso cycle 3′: gen +.044 / +.017.** +.044 belongs to the 1,000-round model
   (boot exceeds budget); the uploadable 800-round model is **+.017 [−.006,+.040]**
   vs cycle 2, with pool −.017 [−.038,+.013]. Correct the H-1 example; do not use the
   larger number to justify changing the panel-combination gate.

## Gate audit and proposed text for “How to use it”

**No gate change is ready for adoption.** Preserve previous verdicts; publish
counterfactual re-scores separately. Source audit found:

- `tools/analysis/features/scorecard.py:gate_line` still applies fixed +.05 point
  estimates, not paired intervals. The documentation's “D-032 implemented here”
  statement is false for this checkout.
- Gustave/Maelle use mean-of-checkpoint-**medians**; Aline uses the mean of
  per-game normalized deltas. They are not the same estimand. Maelle-04 flips
  pool sign: median −.012 vs mean +.025, without repairing its other guards.
- `tools/rc/lane.py` gen panel still includes the two reconstructed public maps
  excluded by D-029. Its `gate()` checks gen economy, but not all gen material,
  win, and hygiene guards. Aline's gate checks both panels but does not enforce
  complete fixture coverage itself; Expedition's wrapper does.
- Freeze field references by hash. S1-T excludes SSS/Cutlery; older field
  percentiles still contain mixed-mode references. Rebuilding only one side of a
  comparison would invalidate it. Taxonomy and `claude/{s1,t1}-status.md` are absent
  in this checkout; S1 findings/store documentation were available instead.

**Proposed clarification (director applies):** name the gate implementation,
statistic, reference hashes, fingerprinted parent/candidate, full fixture set,
seeds, missing/error count, and resampling unit in every report. Report per-map
r25/r50 opening percentiles and tempo for opening changes; retain r100/r250,
material, win, and hygiene guards. Run both plain and fixture-cluster intervals.
A single-seed or incomplete panel is a screen, never an accept. Keep registration
and frontier admission separate from lane acceptance.

Three research proposals, not new acceptance rules:

- **Endgame:** add longest/total at r490 among games still running, the number of
  surviving fixtures, paired all-game end outcomes, and material-leading
  round-limit losses (numerator and denominator explicit). Guard total material,
  elimination loss, and overall score. Attribute actual crown-feeding separately
  from accidental own-body deaths; do not exempt every self-death or reward
  concentration obtained by destroying the swarm.
- **Combining panels:** examine an equal-panel mean (each panel 50%, equal map
  weights within panel), with each panel's lower bound >−.02 and all existing
  retention/win/hygiene guards. This removes pool-only primacy but is a new
  objective, so requires historical re-scoring. Aggregate CIs cannot supply the
  combined paired-bootstrap lower bound.
- **Clustering:** group `(map, opponent, seat)` with all seeds together, report
  plain and cluster 90% intervals side by side. Aline's “−.000” is rounded; obtain
  the unrounded bound before making an automatic threshold decision.

### Historical sensitivity register

| Published accept/hold or motivating result | Available counterfactual / limitation | Proposed status change now |
|---|---|---|
| Aline-17 ACCEPT | Plain pool LB +.005; fixture-cluster LB reported −.000. **Potential ACCEPT→not-demonstrated-positive** under mandatory cluster gate; precision/paired rows needed. | None; preserve ACCEPT, flag sensitivity. |
| Verso-01 ACCEPT | Pool +.052 [.019,.081], gen +.013 [−.017,.042]; mean of panel point deltas +.0325. Missing historical paired rows here for combined/cluster/endgame bounds. | None. |
| Gustave-07c HOLD | Pool +.001, gen −.005; equal-panel point −.002. Pool material LBs −.058/−.056 already miss guards; recombining economy alone cannot make ACCEPT. | None. |
| Esquie-03b LOCAL HOLD | +.0018 [−.0024,+.0062], supported local transfer; no new synthetic-signature confirmation in this pass. | None. |
| Lune-07, R3-03, Monoco ra05/09/10 holds or hold-shaped results | Original resolutions/panels differ; no complete matched historical arrays available for the proposed gates. R3-03 own-body +11% remains a guard failure. | None; counterfactual pending. |
| HB12/13/14 old-scorecard HOLDs | Old gate and varying seed coverage; these are not interchangeable with Verso-01's ACCEPT. Need common fixtures and complete gen results. | None. |
| Verso-02 REJECT; Verso-05 lead-retained parent | Equal-panel economy point deltas +.053 / .000 respectively. The latter is **not** +.0135 (which would mix the wrong gen +.044). Intervals and guards cannot be inferred from these averages. | None; preserve explicit lead exception. |
| Maelle-04 REJECT | Changing median to mean flips pool sign (−.012→+.025); gen win −.069 and economy LB −.041 remain failures. | No ACCEPT flip. |
| TT05 old-scorecard FAIL | r490 concentration .34→.56; wins unchanged, own-body +60%. Would gain an endgame signal; cannot become ACCEPT without measured feeding attribution, complete panels, and elimination guard. | No ACCEPT flip. |

No complete “all historical flips” computation is claimed. The missing paired
archives prevent it. This is why these are proposals for re-scoring, not a request
to relax the gate now. Known documented sensitivity and non-flips are explicit above.

## Ranked ten for the next issue

Priority = proposed weight × problem size × cheapness. Size and cheapness are
ordinal planning estimates (1–5; cheapness 5 = existing-data query, 4 = small
mechanism/paired test, 3 = larger validation), not measured utilities. Rankings
reflect the row's highest-value decisive test, not a promise that it will pass.
Owners are recommendations only; no messages or jobs were sent to other lanes.

| Rank | Row | Weight × size × cheapness | One decisive test | Suggested owner |
|---:|---|---:|---|---|
| 1 | L36 opening components | .8×5×5 = 20.0 | Exact-source split-eligibility/intake decomposition, r25–50, ranked controls and matched fixtures | S1 + Expedition |
| 2 | L37 map specialism / gate | .8×4×5 = 16.0 | Re-score paired archives with equal/old-Q2/clean-Q2 weights and cluster intervals; list flips | Expedition + R4 |
| 3 | L39 conversion | .7×5×4 = 14.0 | g01 vs identical post-r150 Ares with crown/feeding disabled; elimination, material and round-limit guards | S1 + TT |
| 4 | L38 symmetry | .7×4×4 = 11.2 | Expedition-08 vs 01 on both panels, symmetry firing/detection and per-map openings | Expedition |
| 5 | L03 phase handover | .7×4×4 = 11.2 | Fixed r150 vs actor-observable state trigger, same crown setting; independent seeds and structural OOS | S1 + TT |
| 6 | L27 direction prior | .8×4×3 = 9.6 | Same identity-free base and fixtures for HB540 vs Verso800, frozen features and budget | Verso |
| 7 | L40 mouth loitering | .5×4×4 = 8.0 | Expedition-09 vs 01: ally head-on per transit, volume, economy/material guards | Expedition |
| 8 | L29 churn metric | .8×3×3 = 7.2 | Same archived exploration-cut fixtures, gross economy vs net-income tempo and corpse source | S1/R4 |
| 9 | L05 fixable leaks | .8×3×3 = 7.2 | Rebuild trapped/newborn/portal ledger on 01; check whether prior already removed each target | R3 |
| 10 | L02 selective caps | .5×3×4 = 6.0 | Predeclared five-point Expedition-07 scan; equal-source parent, phase and CPU reporting | Expedition |

Next below the cut: L12 .3×4×4=4.8 (ally-only prior transfer, already queued);
L04 .3×3×5=4.5 (the four prepared parameter ports are cheap
once parent panels exist). L13 remains untested, not silently settled. L31/L32/L33
remain live but cost more and lack a first hard-mode success; no GPU-heavy L34
training is scheduled on this Mac.

**Rows touched:** L02, L12, L16, L21, L34 proposed changes; L03–L05, L11, L13–L14,
L17, L20, L23–L24, L27–L33, L35–L40 reviewed/annotated without additional weight changes.
