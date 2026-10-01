# Expedition — H-1 hypothesis steward, passes 1–17

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

**Execution root changed during pass 15:** use the attached
`/Users/alik/.codex/worktrees/expedition-publish/UNSW-Battlecode-2026` explicitly.
The shared project was switched to main by another workflow, which stashed its
work as `mac-checkout-wip`. Do not switch it back, edit it, or apply/drop its
stashes. Only Expedition's latest files were recovered into the isolated checkout.
Its `build` and `.venv` symlinks point to the preserved original data/environment;
keep them untracked. The declared HB17 opponent's runtime files were materialized
from TT `1673a7ce3` locally, without its registration file; keep that dependency
untracked too. All six original source contracts and the fixed mouth-screen
contract still match exactly. The heartbeat now targets this isolated path and
pushes scoped commits from detached HEAD to origin/r/expedition. This supersedes
pass 14's instruction to run games from the shared project directory.

## Pass 17 — close the opponent-dependent exploration screen; test production choice

**2026-10-01; isolated checkout, starting from `dfc7d42e2`.** No changes to shared
main, stashes, other lanes, or dependency symlinks. Batch 019 completed **79 games
in 1,178.9 seconds**; `audit-020-frontier.json` validates 141 records / 70 pairs,
with 136 arena/replay discrepancies. Batch 020 finished the remaining **19 games
in 172.9 seconds**. The final `audit-021-final-frontier.json` validates **160
games / 80 exact pairs**, with **155** discrepancies preserved. Source/replay
hashes, fixture attribution, errors and canonical bookkeeping pass. Discrepancies
remain differences between arena-inferred turn-time intake/material and replay
events/round-start snapshots, not overwritten measurements.

### Frozen frontier verdict: negative, do not advance

`screen_report.py --screen explore-frontier-v1` reports **NEGATIVE SCREEN; DO NOT
ADVANCE**. Discovery wins are **20 parent / 19 candidate**, confirmation **18/21**.
The confirmation gain, map-loss bound and mean opening-tempo guard pass; the
opponent nonharm check fails. All original rules remain unchanged. This completes
the additional bounded screen, not the full D-032 pool/gen panels or sandbox gate.

| Opponent | Seed 1 parent / 05 | Seed 2 parent / 05 | Both seeds |
|---|---:|---:|---:|
| HB17 stronger prior | 8 / 12 | 6 / 11 | 14 / 23 |
| g01 mimic→Ares r150 | 12 / 7 | 12 / 10 | 24 / 17 |

Each opponent has 20 pairs per seed. The direction of the opponent split repeats:
+4/+5 wins against HB17, −5/−2 against g01. This does not identify which opponent
component causes it; HB ancestry, opening, middle-game interaction and later
conversion differ together. Aggregate wins **38/40** hide that tradeoff. There
are 20 improved, 18 worsened and 42 tied paired outcomes across the two seeds.

| Map | Seed 1 parent / 05 | Seed 2 parent / 05 |
|---|---:|---:|
| Autarky | 0 / 0 | 2 / 1 |
| Default | 2 / 3 | 2 / 2 |
| Devil | 2 / 2 | 1 / 1 |
| Dilemma | 2 / 1 | 2 / 1 |
| Portals | 4 / 2 | 1 / 1 |
| Queen of Spades | 3 / 3 | 2 / 2 |
| Schooltime | 4 / 1 | 2 / 3 |
| Slithery Fight | 1 / 1 | 2 / 4 |
| Trauma | 2 / 3 | 2 / 3 |
| Trophy | 0 / 3 | 2 / 3 |

Each cell uses four pairs. Schooltime reverses its first-seed net loss; Dilemma's
loss and Trauma's gain repeat. Do not turn these tiny slices into named-map
rules. Prior claims based on the discovery prefix are now explicitly qualified
by confirmation; in particular Schooltime is not uniformly harmed.

### Phase and uncertainty audit

Mean opening tempo is **−8.823 / −2.567 rounds** in seeds 1/2 (faster), while
r100 material is +7.700/+3.275 and r250 material +11.950/+6.725. Final longest-
margin delta is −1.175/+1.150; final total-margin delta +39.100/+4.450. Credited
kills gained between r150 and r250 change by +.700/+.475; this is an observed
pressure proxy, not proof of purposeful aggression. These measures can improve
without a reliable win gain or nonharm against both styles.

Whole-map cluster bootstrap: pooled expected-score delta **+.025**, descriptive
95% interval **[−.1125, +.175]**; confirmation +.075 **[−.05, +.225]**. Pooled
tempo −5.695 **[−14.673, +1.394]**. Ten fixed maps and two related controls cannot
establish contest generalization. Opponent score intervals also overlap zero
(HB17 lower bound exactly zero); the repeated direction is a useful diagnostic,
not a claim of statistical certainty. The failed fixed opponent check does not
require significance and is not relaxed because its interval crosses zero.

The closing reporter also retains raw newborn/ally-collision exposures and
parent-conditioned phase cohorts: include a fixture when the **parent** reaches
r250/r400, regardless of the candidate's survival. This avoids changing the
cohort by candidate success; it is not causal isolation of a game phase. Unit
coverage verifies that a candidate's early win remains in its parent's late
cohort and that absent cohorts are unmeasured, not zero. The reporter records
its source hash; final outputs remain under ignored `build/expedition/`.

The completed exposure audit does **not** reproduce a uniform newborn-death
penalty: newborn deaths per split are .402→.382 in discovery and .384→.382 in
confirmation. Ally head-ons per 1,000 opening dragon-turns are 1.223→2.240 and
2.063→2.170 respectively. Ratios use pooled raw counts/exposures, not averages
of game percentages. The parent's r400 cohorts also reverse by seed: score
delta −.250 (20 pairs) then +.227 (22 pairs), with longest-margin deltas −6.150
and +3.727. These contradictions prevent a blanket late-conversion explanation;
retain the opponent split and inspect mechanisms rather than labeling every
changed loss an opening or endgame failure.

### Independent next mechanism, declared before new games

Prepared **expedition-11-foodhold** from immutable 01, not from 05. Before r150,
retain the parent's already-selected one-step move when it eats an observed
pearl, passes the existing known-state simulation and room requirement, and has
a fully represented body. Only ordinary splitting is deferred. No new route or
score is forced; partial-body opening rescue/production and emergency escape
splits are preserved. The simulation cannot guarantee safety against an unseen
or moving enemy. No map names, exploration-dose tuning, training or GPU.

This tests a different production decision motivated by S1's observational split
restraint, with explicit risks of reduced expansion or repeated meal-taking. It
is not evidence that copying a top team's split percentage would work. Late
concentration, midgame pressure, and independent architectures remain competing
priorities rather than being explained away by one opening change.

Native builds and guard-boundary checks pass. On **1,316 recorded turns**, five
commands change; switching the mechanism off exactly reproduces 01. Runtime ZIP
size is **3,920,519 bytes**. Recorded activation does not establish strength;
local native execution does not establish sandbox validity. **30 no-game tests
pass**, including fresh-seed/panel isolation and parent-defined phase cohorts.
Runtime hashes are frozen in the new source manifest.

The prospective `production-contract.md` fixes **food-hold-v1**, panel
**production-v1**, all ten maps, both controls, both seats, fresh seeds **3 and 4**:
80 pairs / 160 games. Seed 4 confirms seed 3; these are fresh to Expedition's
challenge, not globally unseen maps or opponents. Positive confirmation score,
neither opponent harmed, and no map losing more than one point are required for
broader testing. **Tempo becomes diagnostic for this new screen**, with the old
frontier rule reported alongside it on the same data. That prospective change
recognizes that faster opening and winning are distinct; it cannot rescue 05's
failed opponent check and does not modify shared benchmarks or historical gates.

### Parallel cutoff, ledger and next research

Read-only fetch about 09:29 UTC: TT advances to **463575bde** (hb1-24 portal rule
restricted to W+H ≤56); Obscur **a8bf0a566**, HB **bfd67c37b**, Clair **0c55d4b4f**
are unchanged. TT's latest source is a candidate, not a newly reported strength
result. A structural threshold can still fit known maps even without map names;
require unseen topology before adopting such a selector. Do not duplicate
Obscur's donor-regime experiment while waiting for its outcome. No other chats
were messaged or their work edited.

Ledger proposals only: L20 reopening remains supported as an economy/tempo
observation, but its strength transfer is explicitly opponent-dependent here.
Add the repeated g01 regression to L29/L36 rather than proclaiming a universal
exploration gain. Keep L39 concentration/conversion and L03 pressure open; no
numeric posterior change from this small two-seed screen. L40's repaired mouth
screen stays complete and limited; its old negative transfer evidence stands.

Ranked ten:
1. Test the frozen food-hold production mechanism on fresh seeds and both styles.
2. L39: state-driven concentration/delivery, using late wins and longest margin.
3. L03: active middle-game pressure versus merely producing more material.
4. L29/L36: explain the repeated HB17/g01 split without fitting map-specific rules.
5. L27: compare independent donor/coordination architectures after Obscur's results.
6. L37: Dilemma/transposed-map failure and information limits.
7. L38: finish frozen symmetry transfer, including collision costs.
8. L14/L20: finish original prior-base trap/exploration scans; preserve their scope.
9. L02: finish cap scans and distinguish actual bounds from nominal parameters.
10. L40/gates: preserve the mouth repair, unfamiliar-map validation and sandbox obligations.

Next runnable action: run **food-hold-v1**, never restart the now-complete
explore-frontier-v1 screen or the default mouth queue. Use
`campaign.py --screen food-hold-v1 --execute --minutes 20 --max-games 96` under
the shared exclusive lock. After each batch run
`report.py --candidate expedition-11-foodhold --panel production-v1` and preserve
a new audit snapshot. At all 80 pairs, apply `screen_report.py --screen food-hold-v1`.
Do not alter the runtime, seed set or rules from a partial result.

## Pass 16 — faster openings can lose the length race (2026-10-01)

Continued in the isolated checkout from `88e4911ee`; the shared main checkout,
its stashes and the three untracked dependencies remain untouched. Batch 018
owned the exclusive game lock on entry, so no overlapping batch was started.
The frozen 05/01 stronger-opponent screen stays unchanged through both seeds.


Batch 018 closed **62 games / 31 matched pairs in 1,137.1 seconds**. The saved
`audit-019-frontier.json` validates all 62 indexed records, with **59** arena/replay
measurement discrepancies preserved and no source/replay/attribution/bookkeeping
failures. These retain different estimands: inferred turn-time intake/material
versus replay events/round-start snapshots. The partial aggregate is **18 parent / 13 candidate wins**, with five improved
and ten worsened fixtures; it is not a complete-seed comparison. Confirmation
has not started at this snapshot; 49 of 80 pairs remain. Batch **019-frontier** subsequently resumed the
exact missing Slithery B/g01 parent fixture, one worker, the same 20-minute and
96-game bounds. Its lock is now active; do not launch overlapping games.

### Map and phase evidence

Completed first-seed slices already show that productive opening choices need
not win. Schooltime is **4 parent / 1 candidate wins** in four pairs, although
05's opening tempo is **3.568 rounds faster**. All eight games reach r500. In
seat B versus HB17, 05 has total-material margin **+150** at termination but
longest-dragon margin **−22** and loses; 01 wins with margins +3 and +24. In
seat A versus HB17, 05 has more r100 material (99 versus 52) and higher r250
material share (.351 versus .289), yet finishes at longest margin −18 versus
+15. Seat A versus g01 also changes from win to loss (longest margin +18 to −4).
This is observed phase/conversion evidence, not proof that a particular action
or concentration rule caused the regression. Do not call better tempo a strength
improvement. Saved replay-backed details: `frontier-schooltime-s1-phases.json`
and the corresponding opening audit under `build/expedition/`.

Other completed first-seed slices: Portals **4/2** despite tempo **−4.167**;
QoS **3/3** with tempo **−7.296**; Default **2/3** with tempo **−20.026**.
Positive delta means slower. These four slices have four paired fixtures each;
keep the remaining maps and seed 2, rather than selecting the favorable maps.
Autarky is 0/0 and **+5.410** rounds slower; Devil 2/2 and **+9.824**;
Dilemma 2/1 and **+7.014**. These complete opening slices are heterogeneous even
before later phases. No screen or full D-032 verdict is available from this prefix.

### Gate audit and implementation

Added the uncertainty analysis required by the already-frozen frontier contract:
10,000 deterministic whole-map bootstrap resamples, retaining every paired seed,
seat and opponent within each selected map. Reports cover expected-score and
opening-tempo deltas overall, by seed and by opponent. Intervals describe the
sampled maps and related local controls, not the contest field; single-map
intervals are unavailable. Unequal map sizes retain fixture weights. These
intervals **do not alter or participate in the frozen advancement rules**.
Explicit win/draw/loss counts and the report-source hash are now included.

All **28 no-game tests pass**. New tests verify that repeating observations over
seeds cannot invent independent maps or narrow the interval, draw scoring and
unequal cluster weighting, single-map uncertainty, and rejection of missing,
duplicate or nonfinite pairs. Bot runtime files and contracts are unchanged.
The original mean/median, tempo, opening/phase/map, canonical-versus-arena and
sandbox obligations remain; no acceptance, registration or promotion.

### New parallel-work cutoff and competing explanations

Origin refreshed about 09:04 UTC: TT **17514485b**, Obscur **a8bf0a566**;
HB **bfd67c37b** and Clair **0c55d4b4f** are unchanged. Read-only inspection,
no merge or messages to other chats. These are their reports, not Expedition
replications:

- TT's r150 Cache-me-outside and forgot-to-mention handovers score 232/320 and
  234/320 against V06's 244/320, despite stronger economy. Its portal-feeding
  rule reports a Portals gain but a Default leak; the new hb1-23 area denominator
  is an implementation, not yet evidence of a transferable gain. The frozen
  Expedition HB17 control stays fixed, not replaced during this experiment.
- Obscur proposes parent-conditioned r250 material share and r400 late-win
  cohorts, minimum useful effect sizes, and unseen map twins. Parent conditioning
  avoids selecting a changing candidate survivor set; it still measures a
  baseline-defined cohort, not pure causal phase attribution. Its tool resamples
  **map × opponent × seat** clusters with seeds together, which is a different
  uncertainty assumption from Expedition's whole-map resampling. Do not equate
  their confidence intervals or silently import the new gate.
- Obscur is testing regime-dependent donor priors and proposes split restraint,
  stronger converter opponents, and opponent-type inference. Avoid duplicating
  its donor experiment before reading results. Its retrospective gate agreement
  is useful calibration, not independent validation of a rule chosen using those
  same historical outcomes. Our old failed verdicts remain unchanged.

**Ledger proposals:** retain L20 reopening and downward L40 review; add text to
L36/L39 that opening improvement and material accumulation can coexist with a
lost length race against stronger controls. No numerical posterior change from
this small first-seed sample. S1's split-restraint association remains a mechanism
to test, not an instruction to copy an observed split rate.

Ranked ten after this reconciliation:
1. Complete 05's frozen stronger-opponent screen; separate map, phase and outcome.
2. L39: state-triggered concentration/delivery, with longest-margin and late wins.
3. L36: resource-aware split restraint/child placement versus forgone parent food.
4. L03: midgame pressure and elimination, rather than population alone.
5. L29/L37: prospectively compare phase metrics and map twins on held-out evidence.
6. L27: read Obscur donor-regime results; seek a distinct architecture, not a clone.
7. L37: diagnose Dilemma/transpose failures across mechanisms.
8. L38: finish frozen symmetry information/collision transfer.
9. L14/L20/L02: finish prior-base exploration/trap/cap scans without another dose sweep.
10. L40: preserve the completed mouth repair and unfinished full panels; no automatic sequel.

Next runnable action: inspect active batch 019-frontier; after it releases the
lock, run `report.py --candidate expedition-05-explore3 --panel frontier-v1`,
preserve its audit snapshot, then resume only missing fixed fixtures with
`campaign.py --screen explore-frontier-v1 --execute --minutes 20 --max-games 96`.
Apply `screen_report.py --screen explore-frontier-v1` only after all 80 pairs are
present. No new mechanism is admitted before this bounded screen is completed.

## Pass 15 — finish the bounded test; challenge the base with stronger opposition

**User clarification:** local iteration is allowed when it helps win, but the
current strategy is behind the curve. Do not confuse repairing an inherited
regression, outperforming old opponents, or improving an opening statistic with
catching the competitive frontier. Keep local hypotheses accountable to broader
alternatives and unfamiliar opposition. This supplements pass 14's research reset.

Batch 015 completed **92 games in 1,168.2 seconds**, respecting the 20-minute
admission bound. `audit-016.json` validates **74 matched pairs** (66 pool, 8 gen)
from 391 indexed records, with **388** arena/replay discrepancies preserved.
Source/replay hashes, attribution and canonical bookkeeping pass. Batch 016
resumes the remaining fixed screen, one CPU worker; no overlapping game batch.

Completed seed-1 map slices, 01 parent / 10 candidate wins:

| Map | Pairs | Parent | Candidate | Opening tempo delta |
|---|---:|---:|---:|---:|
| Queen of Spades | 16 | 16 | 16 | 0.000 |
| Portals | 16 | 10 | 12 | +0.112 |
| Devil | 16 | 15 | 15 | 0.000 |
| Portal Quartet | 8 | 8 | 7 | +0.647 |

All four opening audits validate their sources/replays and bookkeeping. Positive
tempo delta is slower. The first-seed aggregate is **49 / 50 wins**, a single
net win, with costs and benefits on different maps. QoS seed 2 also has 16/16
wins and exactly equal measured opening trajectories. The remaining confirmation
slices must finish; no advancement verdict from this prefix. The numerical
checks stay those fixed before games, including Quartet's confirmation tempo.

**Confirmation map update:** Portals seed 2 finishes **14 parent / 13 candidate**
wins, despite the seed-1 gain. Tempo is +0.122569 rounds slower, with identical
reported food/loss/split/material values through r100; by r150 bed food is −.875
and total material −1.1875 on average. Of the five changed outcomes, the first
whole-state/food divergence is r110 (Chaewon A, loss), r136 (Yuna B, loss),
r171 (Gavroche A, gain), r197 (Sinbad A, gain), r241 (Fenrir B, loss). The last
three have equal pre-r150 states: the opening curve alone cannot explain them.
These outcome-selected traces describe timing, not an action-score attribution.
Evidence: `mouthcontest-portals-s2-opening.log` and
`portals-confirmation-divergence.json` under `build/expedition/`.

**Fixed-game coverage now complete:** batch 016 stopped at 72 games / 1,180.0
seconds under the admission budget; isolated batch 017 finished the last four
games in 95.6 seconds. Final report `audit-018-final-mouth.json` validates all
**112 paired screen fixtures** (96 pool, 16 gen), within **467 indexed records**,
with **464** arena/replay discrepancies retained. Both original full panels
remain incomplete; this is complete screen coverage only. Aggregate wins are
49/50 in discovery and **49/49 in confirmation**. Confirmation Quartet is 3/4,
which offsets Portals' 14/13; QoS is 16/16 and Devil 16/16. Devil has exact arena
stat/outcome/round/termination parity on all 32 fixtures. The closing screen
report now passes every predeclared check: **ELIGIBLE FOR BROADER TESTING; NOT
ACCEPTED**. QoS confirmation tempo remains unchanged and Quartet confirmation
tempo is −1.478748 rounds faster, so both opening guards pass. Across 112 games
there are only five improvements and four regressions versus 01; confirmation
wins are tied. This establishes a limited repair with no demonstrated reliable
strength gain. No automatic mouth successor or broad expansion is scheduled.

The richer phase diagnostics stay mixed: mean final total-margin delta is
−2.821 / +3.661 across seeds 1/2; longest-margin delta −1.143 / +.179;
r150–250 credited-kill delta +.964 / −.339. Kills are an observed pressure proxy,
not a claim of deliberate aggression. The final structured decision and full
map/opponent/seat splits are in `mouth-contest-v1-result.json`; the broader full
D-032 panels and sandbox checks remain unfinished. No rule was changed.

The source-isolated canonical hash returns to the original `0a8122e…`; the first
702 common old/new canonical cache records compare exactly equal. Keep both
cache versions. The declared TT opponent is locally materialized from its Git
commit because the publication branch deliberately excludes unrelated TT merges.
The two current control fingerprints are HB17 `5ec09f086b40…` and g01
`4ce9231d8b43…`, fully stored in the new run contracts.

**Next independent experiment is running:** after 017 released the shared game
lock, batch **018-frontier** started `explore-frontier-v1`, maximum 96 games in
20 minutes, one CPU game worker. It does not depend on a favorable mouth verdict;
closing replay analysis runs alongside it. Never overlap another game batch.
Use `report.py --candidate expedition-05-explore3 --panel frontier-v1` after its
batch and keep all partial-map results explicitly descriptive.

### Fresh opposition experiment, declared before execution

Prepared `frontier-contract.md` and screen **explore-frontier-v1**. It tests the
already-frozen **expedition-05-explore3** against 01, on every one of the ten
LIVE maps, both seats, seeds 1 and 2, against **hb1-17-prior-lam20** and
**ouroboros-g01-hbmimic-ares-r150**: 80 fixtures/arm, 160 new games before reuse.
This answers an outstanding prior-base question while challenging reliance on
the older roster. It is an additional bounded screen, not a mouth sequel,
parameter sweep, replacement of full pool/gen evidence or contest promotion.

Clair's exploration finding motivates the mechanism; TT motivates the stronger
prior reference; S1's candidate list and graft results motivate the second style.
Source inspection confirms HB17's lambda 2.0 and g01's r150 switch. Their README
and registry prose partly describe ancestors, so frozen runtime fingerprints are
authoritative. No training or GPU is required. We have not changed either control.

The advancement rule requires positive seed-2 expected-score gain, neither
opponent harmed, no map losing more than one expected-score point, and no slower
overall opening tempo. Equality is not improvement. Full map/opponent/seat and
seed breakdowns, middle/final material and termination accompany the opening
curve. Both controls still share local HB/Ares ancestry; a pass will require
more diverse authenticated opposition and unfamiliar topology, not an assertion
that these controls represent today's contest leaders. The S1 recommendation of
three or more seeds remains appropriate for broader validation; our two seeds
are explicitly screening only.

Campaign tooling stores the challenge under its own `frontier-v1` panel and
freezes its source/map/opponent/reference hashes separately. All **six existing
parent/09/10 source contracts still compare exactly equal** after this addition.
The report supports explicitly selected panels and cannot call a complete
challenge a full D-032 pass. `screen_report.py` refuses incomplete coverage,
refreshes stale replay-backed opening audits and applies the declared screen
checks; its output is only eligibility for broader testing or a negative screen.
**25 no-game tests pass**, including old-panel invariance, roster coverage,
parent/candidate pairing, panel isolation and prevention of an original-gate
verdict on selected coverage. A planning-only challenge run starts no games.

**First frontier audit:** `frontier-first-slices.json` validates 17 matched
pairs from 35 records (33 arena/replay discrepancies), still only a partial
first seed. Completed first-seed slices have parent/05 wins: Autarky **0/0 of
4 each**, Default **2/3**, Devil **2/2**, Dilemma **2/1**. Autarky's parent was
16/16 against the old roster; the new 0/4 does not estimate contest strength,
but it directly demonstrates that the old unbeaten map score did not transfer
to these controls. The Default gain cancels the Dilemma loss on this prefix.
Keep all ten maps and both seeds; do not select or tune against the prefix.

### Parallel-work check and reconciliation

Refreshed origin refs without merging. TT `1673a7ce3`, HB `bfd67c37b`, Obscur
`a9e6fa647`, Clair `0c55d4b4f` are unchanged since pass 14; no new remote branch
result supersedes that reconciliation. Newly reviewed local S1 candidate/ratings
work remains untouched. Its 20,243-game candidate list explicitly warns that
within-band ratings overlap, map rankings correlate only moderately, and most
opponents represent second-tier styles. The local Elo script now includes
Expedition rows but has no field calibration; do not use its single pooled
rating as the research objective or infer causality from a partial campaign.

Ranked next work (priority, not a new posterior-weight claim):
1. L36/L20: 05 versus stronger/different opening opposition, with actual wins.
2. L36: resource-aware child placement and the parent's forgone food opportunity.
3. L03: turn middle-game material into pressure/eliminations, not just population.
4. L39: state-triggered concentration and delivery for round-limit conversion.
5. L37: Dilemma and transpose failure across otherwise useful mechanisms.
6. L38: frozen symmetry information gain versus allied collision cost.
7. L14/L20: finish frozen explore/trap replication on the identity-free base.
8. L27: compare opening architectures/stronger priors, without GPU training.
9. L29/L37: independent opponent/reference checks and a versioned midgame curve.
10. L02/L40: finish cap scans and existing mouth evidence without automatic tuning.

No new numeric ledger proposal this pass. The L20 reopening and downward L40
review remain proposals; original failed gates remain failed. Full mean/median,
map/phase, canonical-versus-arena and sandbox questions remain visible. Next:
inspect and validate batch 018-frontier after it finishes. Resume `campaign.py --screen explore-frontier-v1 --execute --minutes
20 --max-games 96` only after its lock is free, until the 80 fixed pairs finish. Publish only scoped changes through the attached publication worktree.

## Pass 14 — bounded behavior test and wider research reset (2026-10-01)

**Standing direction, updated by the user:** each pass must revisit fresh ideas,
competing explanations and newly arrived work, not default to increasingly local
variants of the last experiment. Sunk effort is not a reason to prioritize a
mechanism. Periodically review TT, HB, Obscur, Clair and other emerging work;
record cutoffs, distinguish lane reports from replication, and preserve their
files. The 30-minute heartbeat now includes these instructions, the per-map and
phase objectives, and prospective benchmark revision. No chat messages were sent.

Created **expedition-10-mouthcontest**, a single behavior change from frozen 09:
apply its existing mouth penalty only where a visible allied head occupies the
proposed final cell or can reach it through one known step, including paired
portals. It uses no map names. This is a congestion hypothesis; unseen allies,
sprints and uncertainty about ally intentions remain limitations. The original
09 is unchanged. The fixed contract is in the new bot's README and runtime hashes
in source-manifest.json, both written before games.

**Bounded screen:** `mouth-contest-v1`, two seats, all original opponents on
Queen of Spades / Portals / Devil / Portal Quartet, seeds 1 and 2 = **112 pairs**.
Seed 1 is discovery; seed 2 is confirmation, with no intervening source tuning.
Both must complete. Advancement requires the declared food-access repair,
no-portal parity, nonnegative aggregate confirmation wins with no map worse by
more than one win, and no slower confirmation opening tempo on QoS or Quartet.
It is a screen, not D-032 acceptance. Existing full panels remain unchanged;
focused scheduling reuses their exact rows and does not count absent games as
complete. Campaign/report tools now explicitly support the new candidate and
freeze the screen's declaration, fixture list and runtime fingerprint.

Verification: **22 no-game tooling tests pass**; native topology checks include
remote portal landings, blocked/unknown/unpaired edges, wrapped geometry, occupied
mouths and enemy exclusion. **1,316 recorded turns**, 7 command/sonar differences
from 09 and zero from 01. Switching off the ally condition reproduces 09 exactly;
switching off the mouth penalty reproduces 01. The small sample therefore verifies
wiring but warns the condition may remove nearly all useful mouth behavior.
Runtime archive **3,921,304 bytes**, unchanged HB540 direction model, no GPU.
Evidence: `build/expedition/mouth-contest-verification.{json,log}`.

Batch 014 completed **96 games in 839.3 seconds**. Its 09 validation now passes
on **598 games / 299 pairs** (pool 160, gen 139), with **594** arena/replay
measurement discrepancies retained (`audit-015.{json,log}`). Gen wins are 93
parent / 90 mouth: the previous two Quartet regressions plus Causeway Portal B
versus Fenrir. These remain partial panels, not a gate verdict.

The concurrent TT merge added a map filter to run_panel.py, changing the broad
analysis-source hash to `5cfbc573…` and forcing cache regeneration even though
extraction code did not change. The 502 old/new canonical cache records are
**all exactly equal** (`canonical-bridge-015.json`); retain both versions.
After lock release, batch 015 launched
10's focused screen with one worker, maximum 96 games and 20-minute admission
budget. Resume by screen name, not by the default queue. No game overlap.

Publication safety: a concurrent keeper stashed tracked workspace edits during
this pass (`keeper checkout_main`). Only our six tooling files were recovered
from that stash; unrelated entries and the stash remain untouched. The shared
branch also contains TT/Obscur merges not yet on origin/r/expedition. Publish
scoped changes from the attached `expedition-publish` worktree based on
origin/r/expedition; do not push the shared checkout's mixed HEAD. Games continue
in the original project path because their contracts and replay store live there.

**First directly checked repair:** QoS B / Gavroche seed 1, 10 now moves N at r33,
then W through the portal at r34 and eats bed food at r34, as 01 does. 09 first
ate at r49. Both 01 and 10 win this fixture. The 10 replay hash is
`5ad2c740b7fc55589f2d5fb5ea40360becbb55e616278ac3c48f7ae78f01197a`;
01's is the previously frozen `36ee7796…`. Full events are saved in
`build/expedition/mouthcontest-gavroche-access.json`. This confirms the intended
access repair on a design fixture, not out-of-sample strength or a gate pass.

**Completed discovery slice:** all 16 QoS seed-1 pairs pass replay/source,
attribution and canonical bookkeeping checks in opening_audit.py. Both 01 and
10 win 16/16. Mean opening tempo delta is exactly 0, and every individual
reported opening delta (curve, first events and five-round checkpoints) is zero.
This is recovery of the parent's behavior, not improvement over it; the other
maps and confirmation seed remain decisive. Evidence:
`build/expedition/replay-panels/expedition-10-mouthcontest-z1-queen_of_spades-s1-opening.json`.

### Parallel-work review and genuinely different alternatives

Read current local TT/HB/Obscur and the unmerged Clair remote-tracking branch;
do not import its benchmark edits into our frozen experiments. Cutoffs:
TT `1673a7ce3`, HB `bfd67c37b`, Obscur `a9e6fa647`, Clair `0c55d4b4f`.
These are available local refs, not a claim that remote servers were freshly
polled. Clair's status and benchmark version are saved under `build/expedition/`
for reproducible comparison. None of these lane results is an Expedition rerun.

- **Clair:** full-panel unseen3 reports economy +.151/+.065 and opening tempo
  −3.5 rounds, while h2h rises 37% and newborn deaths rise 12%; trap20 reports
  positive economy on both panels but fails a units guard. This contradicts a
  universal prior-base flat-bowl claim. Its base retains the HB identity terms,
  and its gen panel has 31 maps versus our 29, so do not merge scores. Prioritize
  our already-frozen explore/trap arms when the broader scan resumes; no new
  dose sweep is justified merely by Clair's best result.
- **Obscur:** the mouth rule loses economy/wins on its HB800/prior base too;
  all six seed-1 arms lose economy on Dilemma and its transpose. That points to
  an unsolved structural failure, rather than another small mouth-weight edit.
  Symmetry's gen gains come with more allied head-ons: information and safe use
  of it remain separate mechanisms.
- **TT:** a fast CMO opening handed to Ares at r300 improves conversion but
  reaches only 121 wins versus HB540's 141; adding the HB prior after r300 gives
  122. Early material is not sufficient for later elimination. Its portal feeding
  selector gains on Portals but loses elsewhere; avoid a global round switch.
  The new paired endgame evaluator is useful precedent, but its fixture bootstrap
  and hard-coded map regimes need separate scrutiny before adopting it here.
- **HB:** unfading beats fading the prior across both reported seeds. The late
  economy dip can be inherited from the opening's population, so a late symptom
  does not by itself justify changing late behavior.
- **Gate review:** Clair's 1-Oct branch adds endgame/cull treatment, either-panel
  economy acceptance and cluster-bootstrap authority, while explicitly leaving
  r150–250 under-instrumented. Treat this as a versioned proposed comparison for
  Expedition. Preserve historical gate results and collect an independent bridge;
  do not call a printed old-gate line the only definition of success.

Fresh candidates to weigh after this bounded screen: **resource-aware child
placement** (child's reachable food and parent's forgone intake, not just empty
room); **midgame pressure** (whether food/territory becomes enemy eliminations);
**state-triggered conversion** (whether a surviving material lead can still be
turned into a winning longest dragon). These are different causal interventions,
not successors that automatically inherit 10. Freeze the next mechanism only
after comparing its information value with existing ready arms and new evidence.

### Reconciled ranked ten and gate state

1. L36: parent/child food opportunity at splitting; inspect Trauma and Dilemma.
2. L37: explain Dilemma's structural failure across mechanisms and transpose.
3. L39: conversion trigger and delivery, distinct from full-policy handover.
4. L03: midgame pressure/retention versus mere early population growth.
5. L20/L14: reproduce the explore/trap effects on the identity-free HB540 base
   using frozen 05/04; Clair is evidence to reopen, not an acceptance shortcut.
6. L38: information gain from frozen symmetry 08 and its collision cost.
7. L27: stronger/map-aware prior versus larger opening population; CPU-only ports.
8. L40: finish the bounded 10 test and 09 evidence; **no automatic mouth sequel**.
9. L29/L37: versioned midgame net-income reference and benchmark predictivity.
10. L02: complete prior-base cap scans with the effective clamp verified.

Ledger changes remain proposals: L20 should be reopened in light of Clair's
reported full panels; L40 deserves downward review from the independent negative
09/Obscur/Clair evidence, without treating unlike bases as pooled replication.
No numeric ledger edit, acceptance, promotion or sandbox-validity claim this pass.
Mean/median discrepancies, per-map cancellation, tempo versus wins, phase guards,
reference representativeness and CPU sandbox cost remain explicit constraints.

Next runnable action: finish batch 015, run report.py for 10, audit complete
map/seed slices, then resume `campaign.py --screen mouth-contest-v1 --execute
--minutes 20 --max-games 96` until the fixed 112 pairs are complete. Judge its
predeclared screen, then choose among the distinct mechanisms above; re-review
parallel work before allocating the next batch. The original scans remain due,
but ordered completion is not a reason to ignore higher-value new evidence.

## Pass 13 — S1 reference integrated; first gen transfer contrast (2026-10-01)

The user explicitly highlighted `docs/findings/2026-10-01-s1-next-steps.md` as a
reference on top-bot behavior. Its unchanged source and consequences are recorded
in the pass-12 reference addendum: exact-source foraging/split timing, separate
midgame/crown contributions, map-dependent timing hypotheses, and authenticated
references/representative controls. This refines the existing L36/L03/L39/L37 work;
it does not require copying the source's best observed switch time into a new bot.

Batch 013 completed **96 games in 1,114.1 seconds**. Report validation passes on
**502 games / 251 matched pairs**: pool 160 pairs and gen 91. Source/replay hashes,
attribution, errors and canonical bookkeeping pass. **498** arena/replay measurement
discrepancies remain explicit; no historical metric has been silently replaced.
The free lock allowed batch 014 to resume the exact Seam Market A / Yuna parent
fixture with one CPU worker, 20-minute admission budget and maximum 96 games.

The frozen gen panel now has **11 complete seed-1 map slices**, Seam Market partly
observed (3 of 8 pairs), and 17 unobserved maps. Current gen wins are **58 parent /
56 mouth**, with 0 improvements, 2 regressions and 89 ties. This is an ordered
partial panel, not a gen gate verdict or a strength estimate.

Both regressions are on the complete **Portal Quartet** slice: parent 8/8 wins,
mouth 6/8. One regression is against Chaewon and one against Yuna; Ares and Fenrir
remain 2/2 each for both bots. Across both seats, each opponent cell has lower raw
r100 pearls and r250 material for the candidate. The other ten complete gen maps
have unchanged win counts. Do not infer identical behavior from identical outcomes.

This is a concrete structural-transfer question for the map board: the +3-win
Portals discovery does not yet transfer to Portal Quartet. Keep both results and
trace the quartet's tempo, transit exposure and material trajectory before making
a mechanism claim. It is still one seed with four opponents and cannot settle a
universal portal rule. Raw gen features remain raw until the appropriate frozen
parent-reference analysis; no field reference is invented.

Evidence: `build/expedition/audit-014.json`, `audit-014.log`, and batch-013's saved
index/replays. Later batch-014 results are outside this snapshot. No tool behavior
or measured candidate changed in this pass; previous 19 checks remain applicable.
All unrelated files are preserved, including the user-highlighted S1 document.

**Reconciliation:** add Portal Quartet to L40's map-transfer questions; keep the
pass-11 all-pool board and ranked ten, now informed by the S1 behavior reference.
No weight/gate/acceptance change. Tempo stays the opening goal, winning the overall
goal; midgame/endgame and benchmark validity remain active research questions.
Next: finish and validate batch 014, audit the quartet's opening/phase contrast,
and continue the predeclared paired campaign. No registration or promotion.

## Pass 12 — opening access, later divergence, and win-first validation (2026-10-01)

Resumed from `bca4da4b3`. Batch 013 still owns the exclusive campaign lock, so no
second batch was started. This pass uses existing, source/replay-validated Queen
of Spades seed-1 evidence; the latest complete cross-panel report remains **406
games / 203 pairs** from pass 11. Current gen games continue on one CPU worker.
Measured bot snapshots and all unrelated work remain unchanged.

**New standing user instruction:** winning is the objective. Benchmark and
validation criteria may be revised when evidence justifies doing so; local
evaluation can be outgrown or wrong. Existing gates are testable proxies, not an
immutable definition of success. This authorizes evidence-backed revisions to
Expedition's evaluation without routine intervention. Preserve prior contracts and
scores so comparisons remain interpretable; version revised criteria and bridge
old/new results instead of rewriting historical verdicts. Shared lane/ledger
changes remain proposals in this status, and contest promotion remains prohibited.

### User-highlighted reference: S1 next steps, 1 October

Re-read `docs/findings/2026-10-01-s1-next-steps.md` at the user's suggestion.
Its hash remains `547d56e1344edcc97aada2803cd849353feb939630d332c42a3a77ff95f73210`;
pass 6 already independently checked the graft arithmetic and opening-boundary
claims. The file is other-lane work and remains untouched. Use it as a primary
research reference alongside BENCHMARKS, with these concrete consequences:

1. **Foraging and split timing (L36):** the observed top teams decline eligible
   splits more often and eat more afterward. Test exact-source Expedition 01's
   opportunity cost of splitting versus continuing a nearby food run, by map and
   r20–39/r40–59 windows, including safe child intake and full-follow-up survival.
   Prioritize Trauma and Dilemma, where the source reports large early intake gaps.
   Do not infer that more splits is the target, or that the observed .53 versus
   .27 next-five-round intake is a causal benefit of declining: those states were
   selected by different policies. Separate bed/enemy income from recycled food.
2. **Midgame and crown conversion (L03/L39):** g01's win improvement with nearly
   unchanged opening is direct motivation for separate later-phase work. The
   full-Ares handover changes more than crown behavior. Test handover and crown
   contribution separately rather than attributing the whole gain to feeding.
3. **Map-dependent timing (L37):** r150 wins overall in that screen, while Portals
   favors r250; Schooltime/Devil remain weaknesses. Treat this as a discovery
   signature for structural/state-dependent phase transitions, not a validated
   map-name switch table. Confirm on unused fixtures and protect the opening.
4. **Reference and roster quality:** the authenticated atlas says the strong local
   family resembles live ranks 11–30 more than several leading behavioral niches.
   For the next reference/roster version, use authenticated field games and seek
   representative stronger/diverse controls, with old/new benchmark comparisons.
   Do not silently rebuild references inside the current paired experiment.

These directions refine the existing ranked work, without changing weights or
claiming that the 61.6 MB full-mimic graft transfers unchanged to Expedition's
compact direction-prior base. The observed QoS food-access trace supplies a
concrete local foraging example; it does not settle the separate split-timing test.

### Queen of Spades: separate early access cost from all four losses

Added `opening_audit.py`: complete map/seed coverage is required, sources/replays
and canonical bookkeeping are checked, and five-round trajectories are retained
for all 16 pairs, each starting side, and individual fixtures. Outcome-selected
cohorts are labelled post-hoc. Missing first events are omitted only as matched
pairs and their missing counts are explicit, never replaced with zero.

Across all 16 fixtures, candidate minus parent at r50 is:

| Cumulative or state measure | Mean difference |
|---|---:|
| Bed food collected | −4.1875 |
| Enemy-corpse food | .0000 |
| Ally-corpse food | −.1250 |
| Length lost to deaths | −.8125 |
| Splits | −1.6875 |
| Transits | −.5625 |
| Total length at checkpoint | −3.6875 |

The food shortfall is principally bed intake and occurs despite lower cumulative
length loss, consistent with an access/production cost rather than simply more
early deaths. At r25 these audited measures are equal; the mean bed-intake gap is
−.0625 at r30 and −1.375 at r40. By r100 bed intake is −9.5 and total length −7.5.
These are observations, not an action-score attribution or a material-balance
identity between differently timed counters/snapshots.

First food and first split are each delayed **.9375 rounds** across all games,
with the entire delay coming from **Gavroche, side B** (+15 rounds). Side A has
no first-food delay; side B averages +1.875. This rules out an explanation that
all four win regressions stem from delayed first food.

The earliest differing five-round aggregate checkpoint and actual round-start
state divergence differ, so both were audited on the four win regressions:

| Fixture | First changed audited checkpoint | First changed round-start state | First differing move round |
|---|---:|---:|---:|
| Yuna, A | 70 | 70 | 69 |
| Gavroche, B | 35 | 34 | 33 |
| Kazuha, B | 115 | 106 | 105 |
| Yuna, B | None through r150 | 214 | 213 |

In particular, Yuna B's recorded round-start states match through r213 and its
opening measurements match through r150, yet the match outcome reverses. An
opening-only guard cannot detect that loss. Aggregate checkpoint equality also
cannot establish trajectory equality (Kazuha diverges before its counters do).

### Concrete access trace: Gavroche B

Both replays have identical round-start dragon states and pearl positions through
r33. At r33 dragon 1 starts at **(4,4)**. Parent 01 moves north to **(4,3)**, a portal
mouth; mouth 09 moves west to **(3,4)**. The parent's next west move crosses from
(4,3) to **(8,33)** and eats bed food at r34. Mouth 09's first food is instead at
r49, eaten by dragon 3. At r50 the parent has collected 16 bed pearls versus 1,
made 9 splits versus 1, and has 19 total length versus 7; it has also lost more
length, 9 versus 2. Avoiding losses is not sufficient if access/production suffers.

This locates a useful first-action contrast consistent with penalizing a portal
approach. It does **not** show the bot's known-portal state, chosen target, score
terms or which route exemption failed. Next mechanism audit: reconstruct that
recorded decision's observation/target/exemption state before proposing any new
behavior. Do not patch a map-specific direction or assume all QoS losses share it.

### Tempo remains the chosen opening goal; later phases remain open

The user clarified that the benchmark document records deliberate exploration of
summary statistics and the selection of a tempo curve as the early goal. Read
`docs/analysis/BENCHMARKS.md` (SHA-256
`b108d1b165f9361d2e662bb22c056a8655fa720ef98876987661e9534fee5095`),
including its 30 September revision. Its current opening objective is tempo over
r10–150; the older gross-economy summary is explicitly superseded for opening
optimization. Tempo's income excludes recycled own corpses and adjusts for
unrecovered losses. Preserve that rationale; do not treat another gross-economy
summary as a replacement merely because it is convenient to score.

The opening audit now includes the **full paired tempo-lag curve** at r10,20,…,150,
its mean, component trajectories and exact reference hash. It applies the existing
S1 lag function per fixture before aggregation. QoS candidate-minus-parent lag is
0 at r10/r20, **+.156 at r30, +7.500 at r50, +13.437 at r100, +15.662 at r150**;
the 15-checkpoint mean is **+9.082835**, matching the independently saved phase
audit within 1e−12. This is growing opening lag, not just a single endpoint loss.
New maps use the matched parent curve with explicit provisional labeling; no
nonexistent top-team reference is invented.

The research program now states three distinct phase questions on each map:

- **Opening:** improve the chosen tempo curve and understand its income/loss
  components, with matched fixtures and the established opening safeguards.
  A better opening curve is an early goal, not proof of a complete winning policy.
- **Midgame:** retain useful material and access as contact, crowding and opponent
  adaptation change. Diagnose r150/r250/r400 transitions, survival, territory and
  productive resource access against the same opponents. These are candidate
  diagnostics, not an already-validated replacement scalar objective. QoS Yuna B's
  first divergence at r214 belongs in this separate investigation.
- **Endgame:** convert surviving resources into the actual win conditions, tracking
  elimination and round-limit outcomes, longest/total margins and conversion of
  leads. Report the survivor count for late checkpoints alongside all-fixture
  outcomes so early elimination is not filtered away. Do not infer strength from
  concentration produced by destroying the swarm.

Keep the game's actual outcome above the full program, tempo as the current
opening objective, and midgame/endgame as unresolved problems. A change aimed at
one phase needs checks for damage to the others; phase boundaries and map win modes
must be reported rather than assumed interchangeable. Criteria may still evolve
under the preceding user authorization, with evidence and versioned comparisons.

### Benchmarks must earn their role

Overall Expedition triage leads with paired win/score outcomes and their map,
opponent, side and seed dependence. Tempo remains the primary opening objective;
economy, material and hygiene diagnose mechanisms and risks; a positive proxy is not success, and a negative proxy alone
must not terminate investigation of a credible winning specialist.

Current benchmark-challenge register:

| Potential failure of evaluation | Evidence now | Decisive follow-up / current consequence |
|---|---|---|
| Economy misses a winning specialist | Portals +3 wins while canonical economy −.2077; one seed | Confirm win direction across seeds/opponents and structural portal maps; retain as an active specialist question, not an accepted result. |
| Production/tempo overstates competitive benefit | Trauma faster/more material, one fewer win | Trace survival/conversion and replicate; do not call proxy gains strength. |
| Opening-only validation misses later damage | QoS Yuna B first state divergence r214, outcome loss | Retain late-phase/outcome evaluation and trace r213 decision; early metrics alone are insufficient. |
| Pooled score hides map/matchup effects | QoS carries four-win deficit; Slithery has cancelling matchup changes | Keep map × opponent × side reporting, concentration diagnostics and collective results together. |
| Fixed roster or local engine loses relevance | Known dated-field authenticity/reference limitations; no new direct proof this pass | Compare source-matched candidate rankings against stronger/relevant controls or independent held-out results before replacing the roster; no silent reference swap. |

A revised benchmark/criterion should state the failure being corrected, why the
new measure better predicts winning, new roster/maps/seeds/reference hashes, and
old/new candidate rankings on common evidence. Then check on evidence not used to
choose the revision. Record changed conclusions, including favored candidates
that worsen. Revision need not wait for an impossible perfect local proxy, but
requires a concrete comparison, not retrospective relief for a failed gate.
There is **no justification yet to reverse the whole-panel mouth conclusion**:
the complete seed-1 pool has both fewer actual wins and lower economy. Current
contracts continue while the benchmark itself remains open to challenge.

**Verification and reproducibility:** 19 no-game tests pass, including paired
missing-event handling and unequal-array refusal; whitespace checks pass. The
full opening/tempo-curve audit re-ran successfully after the checks. Evidence:
`build/expedition/opening-queen-of-spades.log`, the source-keyed
`*-queen_of_spades-s1-opening.json`, `qos-gavroche-first-divergence.json` and
`qos-regressions-first-divergence.json`. Trace scripts/logs stay under `build/`.
No games were added by these audits. The new tracked tool reproduces all-map/seat
opening trajectories with `opening_audit.py --map queen_of_spades`.

**Reconciliation:** refine the pass-11 QoS board entry to an access-cost case plus
separate later divergences; all numerical map/collective results remain unchanged.
L29/L36/L37/L40 gain these annotations, with no weight change. Ranked ten remain
current; L37 now includes explicit win-predictive benchmark challenge. The latest
user instruction supersedes treating an inherited gate as a permanent veto on
research or future evaluation revisions. Next: validate batch 013 when it finishes,
continue the frozen paired campaign, and audit the r33/r213 decisions before any
new candidate. No shared gate/ledger changes or contest promotion.

## Pass 11 — map-level research is a standing requirement (2026-10-01)

**User steering:** work the problem by map as well as collectively. Map-specific
strength, including gaps among strong teams, is useful signal; do not dismiss it
as noise or optimize only the pooled number. This governs future Expedition passes.
Each meaningful stage must update the all-map view below, inspect opponent/seat
concentration, and connect differences to mechanisms while retaining the frozen
collective panels and guards.

Existing external-team context is the dated repository finding
`docs/findings/2026-09-30-s1-Q2-map-predictability.md`, especially Q2c sections 4–5.
Its cleaned held-out analysis reports a larger improvement from map-specific team
strength on Portals and Slithery than elsewhere. Its examples include cheji bt's
QoS 0.97 versus Elo-expected 0.77, but Slithery 0.63 versus expected 0.78; calc's
Autarky 0.91 versus expected 0.72, but Slithery 0.61 versus expected 0.72. These are
attributed historical observations, not fresh live ranks or evidence that our
candidate will transfer. Keep the historical field study distinct from the frozen
local opponent roster; local matchup cells are not rankings of the current top teams.

### Current all-map research board

Mouth 09 versus parent 01: **16 matched fixtures per map, seed 1 only**. Economy
is canonical replay mean normalized delta; tempo is candidate minus parent rounds
(positive = slower). Material is mean total-length delta at r150. Every map remains
exploratory until additional seed/structural evidence and guards are assessed.

| Map | Wins parent→09 | Economy | Tempo | Material | Mechanism to investigate |
|---|---:|---:|---:|---:|---|
| Autarky | 16→16 | −.0027 | +1.028 | −7.94 | Win ceiling masks an opening/material cost; inspect opponent and seat exposure. |
| Default | 13→12 | −.0569 | +1.108 | −4.69 | Lower transit exposure accompanies lost intake; trace route versus resource access. |
| Devil | 15→15 | .0000 | .000 | .00 | No-portal negative control; preserve exact null behavior. |
| Dilemma | 15→15 | −.0085 | +2.768 | −1.44 | Fewer transits but greater death fraction; audit conditional exposure and early contact. |
| Portals | 10→13 | −.2077 | +3.098 | −2.25 | More wins despite economy loss; distinguish survival/concentration from general strength. |
| Queen of Spades | 16→12 | −.2582 | +9.083 | −8.25 | Access-cost trace on Gavroche B; other loss divergences extend to r214 (pass 12). |
| Schooltime | 15→14 | −.0092 | +.156 | +12.00 | More material does not convert to wins; inspect length concentration and late losses. |
| Slithery Fight | 12→12 | +.0030 | +.116 | −3.00 | Offsetting matchup changes and increased collision/churn; inspect density and routing. |
| Trauma | 12→11 | +.0582 | −1.447 | +8.56 | Faster production with more own goals/newborn deaths; trace net survival and conversion. |
| Trophy | 13→13 | −.0774 | +4.686 | −5.63 | Collision savings cost opening material in an early-contact map. |
| Collective, equal maps | 137→133 | −.0559 | — | — | Keep full-panel win, economy, material and hygiene guards alongside every map finding. |

**First map questions:** Queen of Spades' opening cost, Portals' win/economy
tradeoff, Slithery's collision increase, and Trauma's production/churn tradeoff.
These priorities select replay analyses, not new map-specific constants or a
change to the fixed game queue. Lower-priority maps and negative controls remain
in every report; a specialist gain cannot disappear into an average, and a pooled
gain cannot conceal a large map regression.

### Reporting implemented, not just a change in narrative

`report.py` now includes every planned map for **both pool and gen**, even with
zero games. Each map has exact paired coverage, missing-pair counts, per-seed
coverage, opponent and starting-side breakdowns, win points including half-point
draws, paired improvements/regressions/ties, raw opening intake and r100/r250
material deltas. Existing pool mean/median economy and reference percentiles stay
alongside this view; gen raw metrics are not assigned invented field references.

The same report includes the collective result and a leave-one-map-out diagnostic
to expose concentration. That diagnostic uses available paired fixtures; it is
**not held-out validation**, an alternative gate, or grounds to exclude an awkward
map. Complete-seed flags describe coverage, not confirmed specialism. Missing data
are null, not a zero effect. Row indexes for each pair of bots are read before
slower canonical extraction, reducing staggered snapshot skew during active games.

Verification: **17 no-game tests passed**. New cases check a pooled zero hiding
opposite map effects, missing-map visibility, single-seed incompleteness, opponent
coverage, half-point draws and exclusion of unpaired games. Whitespace checks pass.
No bot runtime, measured snapshot, frozen contract, shared ledger or gate changed.

### First matchup and concentration findings

The expanded report validates batch 012's **406 games / 203 pairs**: pool 160
pairs and gen 43, with 402 arena/replay measurement discrepancies retained.
Batch 012 completed 96 games in 1,057.8 seconds; the lock was free and batch 013
resumed the exact gen fixture with one CPU worker and the same bounded settings.
The report contains all 10 pool and 29 gen maps. Gen has five complete seed-1
map slices, one partial slice and 23 unobserved maps; none are collapsed into
zero-effect rows. Map, opponent and seat partition counts reconcile exactly.

- **Queen of Spades:** A is 8→7 wins; B 8→5. Regressions are Gavroche (one),
  Kazuha (one), and Yuna (both sides). This is not solely one opponent or one
  starting side, but the larger B cost needs explicit confirmation.
- **Portals:** A is 5→6; B 5→7. Improvements occur against Chaewon, Fenrir,
  Gavroche and Yuna; one regression occurs against Sinbad. This breadth is useful
  exploratory evidence, still only two fixtures per opponent.
- **Slithery:** each seat has unchanged win totals, yet opponent outcomes change:
  Chaewon 2→0, Sinbad 2→1, and one improvement each against Fenrir, Gavroche and
  Yuna. Flat map totals conceal substantial matchup changes.
- **Trauma:** A improves 6→7 but B falls 6→4. The improvement is against Gavroche;
  regressions are Kazuha and Sinbad. Check side-dependent access and survival
  before claiming a general production benefit.

Leaving out Queen of Spades makes the pooled win delta zero; leaving out Portals
makes it −.048611. Thus the aggregate four-win deficit is highly concentrated,
while economy remains a separate concern. **Keep both maps in the evaluation**;
this sensitivity directs mechanism work and does not justify excluding either.
The immutable audit snapshot is `build/expedition/audit-013-map-diagnostics.json`
with its corresponding log. Later batch-013 games are outside this snapshot.

### Preventing overfit while using map differences

- Freeze each future behavior proposal's mechanism, observable trigger, primary
  metric, expected map/phase signature and failure conditions before its games.
  Prefer transferable features such as portal geometry, resource access,
  bottlenecks and observed crowding over constants selected to fit map names.
- Seed 1 findings above are discovery evidence. Keep the present candidate frozen
  for seeds 2–3 and structural/transposed gen comparisons; check both starting
  sides and whether a result is concentrated in one opponent. Additional seeds
  reduce seed sensitivity but do not create a new opponent/map sample.
- If later behavior choices use those confirmation results, those data become
  development data for that new version. Reserve new untouched validation before
  claiming a transferable improvement. Track viewed data; do not relabel already
  inspected gen slices as an untouched holdout.
- Report every predeclared map and all original collective guards. Treat this
  board as multiple exploratory comparisons; inspect sign/size stability and
  matched replay mechanisms, with fixture-cluster uncertainty at full coverage.
  Any formal map-specific acceptance rule is a proposal requiring predeclaration
  and multiplicity treatment, not a threshold chosen after seeing these results.

**Reconciliation:** L37's decisive work now explicitly includes map × opponent
specialism and mechanism transfer, alongside historical weighting/cluster re-scores.
L36/L38/L40 gain map/phase signatures; planning weights and the ranked ten remain
unchanged. Map-aware analysis is now a permanent requirement, not a reason to
relax gates or abandon the collective evaluation. Next: continue batch 013 and the
frozen gen/remaining-seed campaign, tracing the named map × opponent × side
contrasts against replay mechanisms before proposing a new version. No registration
or promotion.

## Pass 10 — first complete seed-1 pool and cohort-correct weights (2026-10-01)

Resumed from `c164ddf31`. No newer committed lane findings; the audited provisional
S1 next-steps and tempo-tool hashes are unchanged. Batch 011 completed **59 games
in 1,170.4 seconds**, ending before Trophy B / Hunter. It left **310 games / 155 matched pairs**. The concurrent audit validated 312
records with those same 155 pairs: its later child-index read included two newly
finished Trophy children after its parent-index read. This is a staggered report
snapshot, not missing or orphaned parent games. Source/replay, errors, attribution
and canonical bookkeeping checks passed, with **308** explicitly retained
arena/replay measurement discrepancies. All unrelated edits and measured runtime
sources remain untouched. The free lock permitted batch 012 to resume with one CPU worker,
20-minute admission budget and maximum 96 games.

Batch 012's first ten games finished Trophy and the seed-1 pool. The new
`pool_screen.py` independently validates all **320 games / 160 exact pairs** in
that pool, requires complete fixed coverage before describing a pool result, and
keeps generalization games outside this screen. Batch 012 is now running the
predeclared gen fixtures. Seeds 2–3, full gen coverage and sandbox guards remain
outstanding; this is not complete D-032 evidence.

### Complete seed-1 pool screen

Ten frozen maps × eight opponents × both seats. Parent 01 wins **137/160**, mouth
09 **133/160** (no draws): 12 paired improvements and 16 regressions, with 132 ties.
Equal-map win delta is −0.025. Economy deltas use all 160 normalized rows per side:

| Measurement | Mean economy delta | Mean of checkpoint-median differences |
|---|---:|---:|
| Arena | −.056038 | −.062544 |
| Canonical replay | −.055938 | −.057967 |

Thus the three earlier map-level median sign reversals do **not** reverse the
pooled economy sign. Pooled medians are computed from pooled normalized rows;
they are not averages of the ten map medians. These are descriptive point
estimates from one seed, without an acceptance claim or independent-seed interval.

### Q2 weighting correction and actual same-fixture sensitivity

Re-read the original Q2 slope table and its Q2c addendum. The published
(.16/.49)² = .107 Portals/Schooltime illustration mixed the **top-50-pairs** Portals
slope with the **in-scope** Schooltime slope. Within-cohort ratios are:

- Old in-scope: (.29/.49)² = **.350**.
- Old top-50 pairs: (.16/.47)² = **.116**.
- Clean sample excluding SSS/STAR/Cutlery: (.42/.64)² = **.431**.

The old “about one-ninth” number remains close to the coherent top-50 comparison,
but must not be described as the same-cohort predecessor of the clean estimate.
`pool_screen.py` records all rounded source slopes and the source SHA-256
`7eccf8b55040e6de6bc6af54bfee2eb4aefaa010042e0a8fea551e436c2f9ad3`,
refuses a changed Q2 source, and normalizes squared slopes separately per cohort.
On the identical 160 paired fixtures:

| Map-weight policy | Arena mean economy | Replay mean economy | Win-point delta |
|---|---:|---:|---:|
| Equal | −.056038 | −.055938 | −.025000 |
| Old in-scope slope² | −.051549 | −.051194 | −.039467 |
| Old top-50-pair slope² | −.064676 | −.064616 | −.070570 |
| Clean-sample slope² | −.050276 | −.049902 | −.035129 |

**No point-sign reversal under any tested weighting.** These are counterfactual
weights from a win-predictability study, not validated economy reliability weights.
Do not adopt any weights or change a guard from this screen. The source correction
also applies to the earlier status comparison, now clarified below.

### Newly completed map slices

All three have 16 seed-1 pairs. Slithery Fight remains **12→12 wins**, with three
paired improvements offset by three regressions; replay mean economy +.002977.
Through r150 its transit count is **233→235**, deaths within three rounds of
transit **40/233 (17.17%)→53/235 (22.55%)**, ally head-on rate **.330→.398 per 1k
dragon turns**, own-goal rate **25.656→27.318**, and newborn snapshot ratio
**2,236/4,467 (50.06%)→2,398/4,610 (52.02%)**. Mean total length is
**168.125→165.125**, tempo **+0.116 rounds slower**. Mouth routing does not uniformly
reduce transit exposure or improve the intended safety metrics.

Trophy remains **13→13 wins**, one improvement and one regression; replay mean
economy −.077416. Through r150, transits **163→146**, transit-associated deaths
**49/163 (30.06%)→31/146 (21.23%)**, ally head-on rate **.576→.228 per 1k turns**,
own-goal rate **2.078→1.276**, newborn snapshot ratio **118/1,126 (10.48%)→110/1,072
(10.26%)**. Mean total length **95.0625→89.4375**, tempo **+4.686 rounds slower**.
Collision reductions coexist with opening/material costs.

Trauma wins **12→11** (one improvement, two regressions), despite replay mean
economy **+.058207**, mean total length r150 **26.9375→35.5**, and tempo **−1.447
rounds (faster)**. Through r150, transits **145→136**, no transit-associated deaths
or ally head-on deaths on either side, own goals **35/14,579→57/15,424 dragon turns**
(**2.401→3.696 per 1k**), and newborn snapshot deaths/splits **6/188 (3.19%)→22/271
(8.12%)**. Better opening production does not by itself establish better survival
or match outcomes. Newborn and transit association caveats remain those in passes 7–8.

**Verification and evidence:** Python compilation and whitespace checks pass;
checked weight normalization, within-cohort Portals/Schooltime ratios and invalid
weight-vector rejection. All ten maps have 16 pairs. Equal-weight map means match
independently pooled means within 1e−12. Saved evidence: `build/expedition/audit-012.json`,
`pool-seed1-screen.log`, the source-keyed `*-seed1-pool-screen.json`, and
`phase-{slithery_fight,trauma,trophy}.log`. Reproduce with `report.py`,
`pool_screen.py`, and the three corresponding `phase_report.py --map` invocations.

**Ledger/gate reconciliation:** L29/L37/L40 gain complete-seed descriptive evidence
and the cohort correction; no weights change. Keep the pass-6 ranked ten. The L37
current-screen counterfactual is now computed; historical verdict re-scores,
multi-seed clusters and the full-panel estimand/guard audit remain outstanding.
No historical accept flips, no gate relaxation, no shared ledger/gate edits, and no
registration, upload or promotion. **Next runnable action:** finish the active gen
batch, validate saved evidence, continue the frozen gen panel and seeds 2–3, then
symmetry and the remaining predeclared arms.

## Pass 9 — paired mean/median economy sensitivity (2026-10-01)

Resumed from `c6d518cd8`; no newer committed lane findings, and the provisional S1
next-steps and tempo-tool hashes remain unchanged. Batch 010 completed **16 games
in 1,236.1 seconds**; a 155.3-second admitted game finished beyond the budget.
The saved index validates **251 games / 125 matched pairs plus one parent**:
seven complete seed-1 map slices and 13 Slithery Fight pairs. Source/replay hashes,
errors, attribution and canonical bookkeeping pass; **249 arena/replay measurement
discrepancies** remain explicit. No gen games yet; pool requires 480 pairs and gen
696 pairs for this candidate. There is no complete-panel or sandbox verdict.

The lock was free. Batch 011 resumed the exact missing mouth-09 Slithery Fight B
fixture against Ouroboros, with one worker, maximum 96 games and the same 20-minute
admission budget. Recent Slithery Fight throughput is much slower than the early
24-game batches: the admission timer, not the maximum count, bounds current work.
No overlapping campaign or GPU work; all unrelated edits remain preserved.

### Same games, same references, different economy statistic

Extended `report.py` to show both the mean of normalized paired checkpoint deltas
and the mean of four **candidate-minus-parent checkpoint medians**, separately
for arena intake and canonical replay intake. The median is taken per side at
each checkpoint before averaging; it is neither a median of paired differences
nor a median of per-game economy means. Both statistics use exactly the same
matched fixtures and frozen field denominators. Checked all four economy fields:
`field_references.json` medians equal `map_reference_medians.json` values on every
listed map, so the differences below are not a denominator substitution.

Each completed slice has 16 pairs, eight opponents × both seats, seed 1 only:

| Map | Arena mean | Arena median form | Replay mean | Replay median form |
|---|---:|---:|---:|---:|
| Autarky | −.001287 | +.013223 | −.002696 | +.009435 |
| Default | −.059894 | −.079430 | −.056943 | −.084095 |
| Devil | .000000 | .000000 | .000000 | .000000 |
| Dilemma | −.008886 | +.019061 | −.008457 | +.021264 |
| Portals | −.201548 | −.203544 | −.207703 | −.212597 |
| Queen of Spades | −.252202 | −.118145 | −.258158 | −.148846 |
| Schooltime | −.014689 | +.003575 | −.009187 | +.025172 |

**Three of seven complete map slices change sign under the statistic choice**,
in both measurement pipelines. This is an observed sensitivity, not evidence to
choose the more favorable statistic. No historical or current ACCEPT flips are
claimed: these are map-level points without complete panels, independent-seed
uncertainty or the other guard decisions. The incomplete Slithery slice is kept
in the machine report with its 13-pair coverage; it is excluded from this table.
Do not average these map medians and call that a pooled checkpoint median.

Verification: **15 no-game tests pass**, including hand-checked mean/median sign
reversal, distinction from median paired differences, checkpoint aggregation order,
and refusal of missing/nonfinite inputs. On all eight available map slices the
new mean calculation matches the previous report mean within 1e−12. Existing
means, arena rows, replay caches, runtime sources, contracts and gates are unchanged.
Re-ran report validation with the extended output. Evidence is retained in
`build/expedition/audit-011.json`, `audit-011-estimands.json`, their corresponding
logs, and `test-012.log`; reproduce with `report.py` and `test_campaign.py`.

**Reconciliation and gate proposal:** L37 now has direct Expedition evidence that
specifying the economy statistic is necessary; retain its 0.8 planning weight and
the pass-6 ranked ten. L29/L40 annotations gain this sensitivity, with no weight
changes or retrospective gate relaxation. The proposal remains to name and report
both statistics, preserve existing verdicts and separately re-score historical
paired archives. Full-panel median/cluster intervals, opening/tempo, phase/map
and sandbox guards remain required before any acceptance proposal. No shared
ledger or gate edits, registration, upload or promotion.

**Next runnable action:** let batch 011 finish, validate its exact saved pairs,
complete the Slithery Fight/Trauma/Trophy seed-1 slices and continue the frozen gen
panel and seeds 2–3. Then proceed through symmetry and the remaining fixed arms.

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
   squared weight (.42/.64)² = **.431**. The published old (.16/.49)² =
   **.107** mixed cohorts: coherent old ratios are **.350** in-scope or **.116**
   top-50 pairs. Pass 10 re-scores the complete seed-1 Expedition pool under equal
   and all three coherent slope² policies: no economy point-sign flip. Historical
   verdict re-scoring remains outstanding; adopt none from this screen. Keep a portal-signature guard so global rating fit cannot erase
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
| 2 | L37 map specialism / gate | .8×4×5 = 16.0 | Map × opponent mechanism contrasts, confirmed across seeds/structural maps; retain historical weight/cluster re-scores | Expedition + R4 |
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
