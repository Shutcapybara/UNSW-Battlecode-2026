# Expedition — H-1 hypothesis steward, passes 1–2

**2026-10-01, MacBook; branch `r/expedition`.** Evidence cutoff: starting commit
`757315abc`. No previous Expedition pass exists. The ledger's last update was
`53a9833bb`; this pass reconciles its accumulated evidence, including findings
whose addenda supersede their own headlines. Next pass starts from this pass's commit.

**Current state: autonomous CPU campaign active; no gate verdict yet.** The first
pass created and verified the 14 snapshots, reconciled the ledger, and pushed
`d8bbf8628` to `origin/r/expedition`. The user then approved the push and explicitly
requested long-horizon iteration without routine intervention. Their MacBook
instruction and continuation approval govern the execution adaptation: bounded,
serial CPU-only local games, no GPU training. No contest registration, upload,
activation or promotion; shared ledger/gate edits remain proposals. Preserve
unrelated working-tree changes (including files that appear while this work runs).

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
PYTHONPYCACHEPREFIX=/tmp/expedition-pycache .venv/bin/python bots/expedition-00-hb540-control/campaign.py --execute --minutes 20 --max-games 24
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
  for every mechanism below; **not yet measured or accepted**. Search caps retained.

This makes the test a prior-bearing, identity-free HB base test, not a literal
unchanged-hb1-14 gate. Report 01 versus 00 separately; never attribute that delta
to a tested mechanism. No Lune cap change is bundled into this base.

| Requested question | Expedition versions / one mechanism each | Result and proposed weight consequence |
|---|---|---|
| Is the tuning surface still flat on the prior base? | 02 threat weight 1→0.5; 03 revisit 0.15→0.05; 04 trap 30→20; 05 exploration 5→3; 06 Maelle ally target weight −1.4; 07a–e Maelle sparsity selector `(lo,hi)=(48,160),(48,384),(48,768),(160,384),(160,768)` | **UNMEASURED.** No new weight change from these builds. A robust pass reopens the corresponding prior-base question; no passes would bound these tested settings, not establish that every Tyr evaluation is a flat bowl. |
| Are information gains additive? | 08 symmetry inference, exactly the Aline-13 component retained in Aline-17, on 01 | **UNMEASURED.** L38 stays 0.7. The Aline-17 ally right-of-way seal is excluded to isolate symmetry; a later separate seal/stack test is needed to reproduce the full accepted Aline package. |
| Does the mouth rule survive the prior? | 09 Gustave-07c: weight 4, any portal mouth, route exemption within 3 steps, on 01 | **UNMEASURED.** L40 stays 0.5; a hygiene-only hold does not raise it. |

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
  into live scoring but did not alter a sampled decision: seek a binding trap case
  before interpreting a null game result. These are activation checks, not wins.
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
| 3 | L39 conversion | .7×5×4 = 14.0 | TT05 vs HB14 against converting opponents; all-game outcome and feeding-attribution guards | TT |
| 4 | L38 symmetry | .7×4×4 = 11.2 | Expedition-08 vs 01 on both panels, symmetry firing/detection and per-map openings | Expedition |
| 5 | L27 direction prior | .8×4×3 = 9.6 | Same identity-free base and fixtures for HB540 vs Verso800, frozen features and budget | Verso |
| 6 | L40 mouth loitering | .5×4×4 = 8.0 | Expedition-09 vs 01: ally head-on per transit, volume, economy/material guards | Expedition |
| 7 | L29 churn metric | .8×3×3 = 7.2 | Same archived exploration-cut fixtures, gross economy vs net-income tempo and corpse source | S1/R4 |
| 8 | L05 fixable leaks | .8×3×3 = 7.2 | Rebuild trapped/newborn/portal ledger on 01; check whether prior already removed each target | R3 |
| 9 | L02 selective caps | .5×3×4 = 6.0 | Predeclared five-point Expedition-07 scan; equal-source parent, phase and CPU reporting | Expedition |
| 10 | L12 target density | .3×4×4 = 4.8 | Expedition-06 ally-only consumer; compare r100 retention with off-pool r250 cost | Expedition |

Next below the cut: L04 .3×3×5=4.5 (the four prepared parameter ports are cheap
once parent panels exist). L13 remains untested, not silently settled. L31/L32/L33
remain live but cost more and lack a first hard-mode success; no GPU-heavy L34
training is scheduled on this Mac.

**Rows touched:** L02, L12, L16, L21, L34 proposed changes; L03–L05, L11, L13–L14,
L17, L20, L23–L24, L27–L33, L35–L40 reviewed/annotated without additional weight changes.
