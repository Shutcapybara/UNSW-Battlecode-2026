# Targets — the analysts' current statistical goals (each analyst writes under its own heading; testers read)

Era column: `pre` = games before the live server adopted `unswbc 1.2.3` rules; `post` = after. Pre-era references are
in `docs/analysis/benchmarks/`; post-era references are published here as they stabilise.

## Director (seed; replaced by the analysts' sections)

| cluster / map | phase | metric | top-10 value | us (pre) | gap | era | query |
|---|---|---|---|---|---|---|---|
| all | r0–25 | total length vs same opposition (field SD) | +0.11 | −0.49 | 0.60 SD | pre | S-1 Q3 |
| all | r50 | same | — | — | 0.80 SD | pre | S-1 Q3 |
| all | r100+ | same | — | — | ~1.0 SD | pre | S-1 Q3 |
| all | r0–150 | transit ends in death within 3 rounds | 0.201 | 0.279 | +0.078 | pre | S-1 Q4 |
| all | r490 | round-limit losses with a material lead | 0.32–0.43 (cheji/Stockfish) | 0.33 (V06), 0.57 (hb1-12) | — | pre | TT concentration |
| all | r490 | **queen length / survival** | unknown | unknown | — | post | **analysts: first target to fill** |

## <analyst lineage A>
## antioch (Claude analyst, replay lead) — 2026-10-01 22:45 ACST

Source: `docs/findings/2026-10-01-antioch-era-and-queen.md`. Era `post` = started ≥ 2026-10-01 06:00Z. Post-change n is
small (1,603 games, 308 top-ten side-games) and five of the top ten have **no** post-change games yet, so every post value
below is **provisional**.

**Endgame and queen** (post, field side-games; round-limit = RL; the queen is the original lowest-id dragon):

| cluster / map | phase | metric | field | top-10 | us | target | era | query |
|---|---|---|---|---|---|---|---|---|
| RL maps exc. Slithery (Portals, Trauma, Schooltime, Default, QoS) | r500 | **queen alive at the end of RL games** | 0.022 | 0.007 | — | **≥ 0.5** (H-Q1 falsifier); each kept queen wins 98 % of RL games outright today | post | queen.py, end_reason = 1 |
| all | r0–150 | queen death round, median | r41 | r41 | — | no queen death before r150 except pocket maps | post | queen.py |
| Slithery, Autarky, PD | r0–5 | queen alive | 0.000 | 0.000 | — | **none possible**: spawn pocket, dies r4–5 (H-Q3 falsified); tiebreak there = longest → total | both | queen.py + probe |
| all | r490 | queen length when alive (RL) | median 10.5 (p75 ~20) | n/a | — | > opponent queen; today any length ≥ 2 suffices (98 % of opponents' queens are dead) | post | queen.py |
| all | r500 | RL losses with a total-length lead | 0.347 | **0.511** | — | ≤ 0.25 (pre-change field was 0.241) | post | queen.py |
| all | r500 | RL win rate | 0.53 | 0.691 | — | — (report it; the gate's win share is old-rule until the frame patch lands) | post | queen.py |
| all | r500 | longest at end (RL), median | 28 | 42.5 | — | ≥ 42 (top-10) | post | queen.py |
| all | r500 | total at end (RL), median | 70 | 98 | — | ≥ 98 (top-10); *map pool changed at the switch, compare on the ten ladder maps only* | post | queen.py |


**Win potential Φ (shaped-reward and early-game benchmark; replaces tempo as the opening guard proposal).** Opponent-relative
shares (total, longest, pearls, territory, deaths), two regimes, no map identity; LOMO AUC at r50 0.86 (elimination maps) /
0.63 (round-limit maps), calibrated; tempo-family own-income AUC 0.64. Coefficients `tools/antioch/phi_post_v1.json`.

| regime | phase | metric | top-10 | r11–30 | field | target | era | query |
|---|---|---|---|---|---|---|---|---|
| elimination maps | r50 / r100 | mean Φ | 0.632 / 0.698 | 0.580 / 0.606 | 0.5 | ≥ top-10 | post | value_target.py |
| round-limit maps | r50 / r100 | mean Φ | 0.546 / 0.570 | 0.522 / 0.535 | 0.5 | ≥ top-10, and the queen (Φ adds `queen_diff` from r250) | post | value_target.py |

**Opening, post-change (S-1 Q3's components; 2,862 post-change corpus games, ten ladder maps).**
- **Field stability at r50:** the 90 % half-width of the field median is ±4–5 % (bed pearls, splits, total) and ±12 %
  (transits). The top-ten percentile is known to ±8 points (about 87 top-ten side-games per map, only 5 teams); ±5 needs
  ~220 per map.
- **The field did not move:** post/pre field medians are 1.00 at r25 and r50 for every component (transits +10 % from
  r100; Trauma and Schooltime +9–20 % at r50). Pre-change opening references stay valid to r50 (agrees with nara N3).
- **"us"** is carthage-00-base's 1.2.3 pool panel (480 side-games), normalised against the post-change field. Its
  opponents are panel bots, so the absolute values are indicative and arm-to-arm deltas are what count.

| component | stat | r25 top-10 / us pctile | r50 top-10 / us pctile | top-10 − us (z) r25 / r50 / r100 | era | query |
|---|---|---|---|---|---|---|
| early portal use | transits (cum.) | 0.79 / 0.56 | 0.67 / 0.47 | **0.69 / 0.56 / 0.41** | post | opening_refs.py table |
| bed conversion | bed pearls (cum.) | 0.68 / 0.60 | 0.66 / 0.56 | 0.23 / **0.31** / 0.21 | post | same |
| | bed capture | 0.60 / 0.60 | 0.62 / 0.61 | 0.21 / 0.21 / −0.02 | post | same |
| production | splits (cum.) | 0.68 / 0.79 | 0.70 / 0.59 | 0.13 / **0.28** / 0.26 | post | same |
| territory | BFS territory | 0.59 / 0.62 | 0.66 / 0.68 | −0.09 / −0.15 / −0.21 (we lead) | post | same |
| outcome | total length | 0.69 / 0.67 | 0.67 / 0.61 | 0.14 / 0.18 / 0.13 | post | same |
| | units | 0.74 / 0.79 | 0.68 / 0.76 | −0.12 / −0.01 / −0.03 | post | same |

**Reading:**
- Phase 1's opening gap (total 0.80 SD at r50 for the live bot) is mostly closed by the prior base: 0.18.
- What remains is portal use first, then bed pearls and production at r50.
- Targets: transits@50 at the top-ten percentile (0.67) without raising transit died3. That is H-S1's job: portal memory
  makes the extra transits safe.

**Disagreement slots:** none yet.


## <analyst lineage B>

## <analyst lineage C>

## himeji (GPT analyst) — unit 1, 1 Oct 2026

**Post era, provisional; no gate substitution.** 400 games / 800 sides; 40 games per map; 88 top-ten sides from
five teams; **0 post-era team-7 games**. Reference freeze: through 13:25:52 UTC, ladder 06:21:07 UTC.
Query: `tools/himeji/post_refs.py` with `reference_data/manifest.json`, then `tools/himeji/audit_tables.py`.
Details and test guidance: `docs/findings/2026-10-01-himeji-post-change-reference-audit.md`.

### Opening: top-ten anchor percentile at r50, four Q3 components

All values are within-map field percentiles of the top-ten median (ties half); bed conversion has two columns.
Every `us` value and `top-10 − us` gap is **NA (no post games)**, not zero. These observed anchors are not an
instruction to reduce an existing bot to a low sample value. Opponent-matched Q3 gaps remain pending.

| Map / current Esquie cluster | top-ten sides | bed pearls | bed capture | splits | transits | territory |
|---|---:|---:|---:|---:|---:|---:|
| Autarky / c1 | 9 | 0.881 | 0.669 | 0.800 | 0.769 | 0.644 |
| Default / c5 | 5 | 0.831 | 0.881 | 0.838 | 0.263 | 0.894 |
| Devil / c0 | 7 | 0.188 | 0.194 | 0.150 | 0.500 | 0.431 |
| Portals / c2 | 7 | 0.562 | 0.519 | 0.519 | 0.350 | 0.500 |
| Prisoners Dilemma / c1 | 10 | 0.562 | 0.438 | 0.475 | 0.812 | 0.575 |
| Queen Of Spades / c4 | 7 | 0.706 | 0.794 | 0.819 | 0.762 | 0.781 |
| Schooltime / c3 | 10 | 0.575 | 0.769 | 0.575 | 0.681 | 0.637 |
| Slithery Fight / c0 | 11 | 0.656 | 0.731 | 0.550 | 0.644 | 0.606 |
| Trauma / c0 | 11 | 0.694 | 0.656 | 0.706 | 0.775 | 0.738 |
| Trophy / c6 | 11 | 0.831 | 0.856 | 0.869 | 0.744 | 0.706 |


Current Esquie k8 memberships are frozen in `tools/himeji/reference_data/cluster_map.csv`; c0 is corridor/kelp,
c1 the open mega-cluster, c2 portal-heavy, c3 Schooltime, c4 QoS, c5 Default, c6 Trophy. Cluster anchors are equal-map
means of the map percentile anchors, in `cluster_references.csv`. The source vectors are frozen with the references.
Opening checkpoints r25/r50/r100/r150/r250 and all 12 BENCHMARKS reference metrics are in `references.csv`.

### Endgame: actual r490, not carried terminal states

| Map | reached-r490 sides (field / top ten) | top-ten queen length median / percentile | top-ten longest median / percentile | top-ten total median / percentile |
|---|---:|---:|---:|---:|
| Autarky | 48 / 4 | 0 / 0.500 | 43.5 / 0.708 | 93.5 / 0.729 |
| Default | 28 / 1 | 0 / 0.500 | 14 / 0.339 | 51 / 0.446 |
| Devil | 12 / 0 | — | — | — |
| Portals | 78 / 7 | 0 / 0.487 | 33 / 0.679 | 65 / 0.654 |
| Prisoners Dilemma | 18 / 1 | 0 / 0.500 | 57 / 0.917 | 76 / 0.972 |
| Queen Of Spades | 22 / 1 | 0 / 0.500 | 18 / 0.750 | 65 / 0.795 |
| Schooltime | 68 / 10 | 0 / 0.493 | 34 / 0.676 | 166 / 0.588 |
| Slithery Fight | 80 / 11 | 0 / 0.500 | 62 / 0.719 | 230 / 0.825 |
| Trauma | 70 / 9 | 0 / 0.421 | 33 / 0.879 | 91 / 0.836 |
| Trophy | 2 / 0 | — | — | — |


Queen survival: **field 14/426; sampled top ten 1/44**. Both groups' unconditional queen-length median is 0;
survivor-only medians are 10 and 39 (the latter n=1). See `endgame.csv` for per-map reach counts and both
material-lead-loss rates. Top-ten end-of-RL losses with a lead: **6/10=60%**; losses among games with a lead:
**6/33=18.2%**. Live us and gaps remain NA. Local tester populations are separate.

### Stability, disagreements and tester handoff

No anchor is stable: median opening 95% cluster-bootstrap percentile interval width **0.441** (maximum 0.888).
Himeji proposes release only after >=200 independent game/series blocks/map, >=50 top-ten sides and five teams/map,
fresh ladder with >=8/10 teams represented globally, interval width <=0.10 and <=0.05 drift on a later window.
These are proposed readiness criteria, not changes to the gate; queen-event precision needs separate assessment.

**Antioch's targets remain above. Disagreement:** field RL win 0.53 needs a restricted-cohort label (complete
both-side field is exactly 0.500); queen length 10.5 is survivor-only end length, not all-side r490; survival >=0.5 is
an intervention aspiration, not a measured percentile. The loss-with-material-lead denominator must be explicit.
**Carthage/Rome decide the operational target** by reporting identical reach-conditioned r490 columns, both
conditional loss rates and paired overall win on seeds 1–3. Reference measurement differences are not bot gains.

H-H1 (L24/L39, proposed 0.5): preserving a larger queen head piece on an escapable split costs less opening
production than blanket queen-nosplit. Falsifier and paired-power calculation are in the finding; suits Rome after
baseline, with Carthage's existing guard/nosplit arms as comparison. Full two-panel seeds 1–3; queen power is not
inherited from the old economy resolution table.


### Unit 2 measurement disagreements — 2026-10-01 15:16 UTC

No new stable anchor; unit-1 targets stay frozen. Audit: `docs/findings/2026-10-02-himeji-queen-censoring-and-tester-readings.md`.
Nara's published targets remain on `r/nara`; Himeji disagrees with reading 13.3% as actual r490 survival: its
available top-ten artifact has 8/60 positives but 5 are early terminal states; actual survival is 3/28 reached sides,
with the joint reached-and-alive event 3/60. Cutlery is 1/5 reached games here, not the reported 5/12; request exact IDs.
Neither 95% survival nor queen length 8 is an observed field-percentile target. One moving, length-39 survivor does not
establish deliberate feeding. Treat both analysts' aspirational targets as hypotheses and retain their disagreement.
Rome 2/480 is a joint event; Carthage 2/219 is conditional. Testers should provide both plus early wins/losses.
Carthage 02 and 06 do not justify changing the gate: gen economy lower bounds −0.352 and −0.054 fail even a proposed
−0.03 guard; 06 overall gen win interval crosses zero. Use predeclared paired overall wins for a proposed endgame
evaluation; reach-conditioned RL wins are diagnostic. H-H1 remains weight 0.5 pending exposure denominators and a
production-preserving test. Nara/Antioch reference and policy-target differences remain explicit, not averaged away.


### Unit 3 local diagnostic — 2026-10-01 15:36 UTC

Live-field anchors and NA live-us gaps are unchanged. On Rome seed-1 non-pocket pool games (n=112), recent-split
queen death incidence is 45/1,249 risk rounds vs 53/12,224 otherwise; grouped by map/phase/length RR 7.24
[95% fixture-bootstrap 5.03,10.08]. This is a local all-split timing association, not a field percentile, a target or
a causal treatment gain. H-H1 weight stays 0.5 pending frozen seeds 2–3 replication and a production-preserving
policy comparison. Query, per-map counts, intervals and limitations: `docs/findings/2026-10-02-himeji-post-split-queen-exposure.md`.


### Unit 4 replication and baseline correction — 2026-10-01 16:16 UTC

Local diagnostic only: Rome held-out seed 2/3 grouped split-risk RR 4.98 [3.16,7.59] / 6.52 [4.41,9.06],
112 non-pocket games per seed, 95% within-seed fixture bootstrap. H-H1 still weight 0.5; policy gain untested.
Official Rome pool expected-score share is 396.5/480=82.6042%, superseding old-decoder 83.6458%; gen pending audit.
These do not replace live-field targets or fill missing team-7 gaps. Query, counts and limitations: `docs/findings/2026-10-02-himeji-replication-and-rome-winner-correction.md`.


### Unit 5 ranked/unranked rule and current disagreements — 2026-10-01 16:40 UTC

User direction: deployed-strength anchors should use recent ranked games; keep unranked live testing separate and
reassess legacy decoy assumptions. The old 400-game mixed freeze is historical/provisional, not reclassified.
Cutlery ranked RL queen survival is 0/31 before13:00 vs9/31 after (14 series each); unranked after2/9. These are
small temporal diagnostics, not causal gains or stable percentile targets. Himeji disagrees with mixing those
cohorts and early endings into Nara's r490 anchor; retain both accounts with the correction here.
Antioch Φ remains a proposal pending active-only checkpoints, exact regime-fit provenance, ECDF percentiles and
uncertainty. Its current query carries terminal states; no gate-reference replacement is justified by AUC alone.
Official Rome local gen is74.4253%; local pool82.6042%, neither fills missing live-team7 gaps.
Evidence and queries: `docs/findings/2026-10-02-himeji-ranked-cohorts-gen-audit-and-readings.md`.


### Unit 6 ranked anatomy and current-cohort disagreement — 2026-10-01 17:20 UTC

Current ladder 17:09:22Z changes five top-ten members; Cutlery rank97 is now a historical case. Preserve old
freezes/cohort labels. Ranked Cutlery invalid split deaths40/62→17/90 (series-bootstrap95% change−62.6 to−28.6pp),
actual queen survival0/31→10/40; unranked2/9. All64 invalid deaths follow split actions, not proof of intentional cull.
These are provisional temporal diagnostics, not new field-percentile targets. H-H1 stays0.5.
Retain Antioch's opening targets, with Himeji disagreement: mixed-ranked field vs local00 cannot quantify improvement
from the old live-us0.80SD gap. Its stability bootstrap resamples sides independently and breaks top10/field overlap;
request whole-series ranked resampling with current ladder before adopting ±8pp precision. Live-us gap remainsNA.
MainD-041 activation14265 at17:00 makes first collected live games next priority; corpus here has0post-team7.
Evidence/query/counts: `docs/findings/2026-10-02-himeji-ranked-cutlery-split-actions.md`. All historical gates/references preserved.


### Unit 7 first-live populations — 2026-10-01 17:39 UTC

Submission 14265 now has 5 ranked games (one series, opponent841, five maps) and 10 unranked games
(one series, opponent249, ten maps), all sideA. This supersedes the *current* “no live games” condition;
historical zero counts stay frozen. Results5–0/1–9 are separate diagnostics, not comparable mode effects.

| Era / population | Phase / component | Available us games | Current field percentile / top-ten-minus-us | Stability |
|---|---|---:|---|---|
| post / ranked | r25/50: bed conversion, production, transit, territory | 5, one series | NA: matched fresh field reference pending | insufficient |
| post / unranked test | r25/50: same four components | 10, one series | NA: separate testing population | insufficient |
| post / ranked | queen alive@490 / reached | 0/1 | no percentile target | insufficient |
| post / unranked test | queen alive@490 / reached | 0/4 (RL-end0/3) | no percentile target | insufficient |

Reproducible raw per-map/structural-group deltas for r25/50/100/150/250 are in `tools/himeji/unit7_audit/`;
the structural groups use Esquie's explicit mappings, leaving unspecified memberships as map singletons.
Uncertainty across series cannot be estimated with one per population. Every field-percentile cell stays missing;
no local panel is substituted. Material-lead loss fractions require checkpoint: unrankedRL r490 is1/2 losses or1/1
leads, versus final-state0/2 losses orNA(0leads). H-H1 and all frozen gates remain unchanged.
Query, ladder, counts, identity and provenance: `docs/findings/2026-10-02-himeji-first-live-ranked-unranked.md`.


### Unit 8 ranked references and analyst ruling — 2026-10-01 18:15 UTC

New provisional ranked-only references:2,072 games/482 series,878 current-top10 sides/9teams; ladder17:51:07Z,
decoded window09:26–15:39Z. Current leader952 absent. See `tools/himeji/unit8_audit/annotated-references.csv` for
154 map×r25/50×metric rows, raw values/field percentiles/counts/95% series-bootstrap CIs and stability labels.
Frozen unit1 signature clusters used; PD10 retained separately/unassigned (95ranked games previously excluded by
Antioch's label filter). Terminal carry explicit:52 ended ranked sides@25,116@50 of4144. All rows remain provisional.

| Map (cluster) | Field games / top10 sides | Bed pearls pct | Splits pct | Transits pct | Territory pct | Total pct |
|---|---:|---:|---:|---:|---:|---:|
| Autarky (c1) | 214 / 90 | 65.2 | 54.7 | 67.1 | 65.3 | 74.4 |
| Default (c5) | 189 / 79 | 53.6 | 52.4 | 45.8 | 58.9 | 62.0 |
| Devil (c0) | 208 / 84 | 66.8 | 67.7 | 50.0 | 70.6 | 67.1 |
| Portals (c2) | 206 / 81 | 43.1 | 44.3 | 33.3 | 50.0 | 46.6 |
| Prisoners Dilemma (c1) | 99 / 51 | 49.5 | 51.0 | 47.5 | 60.6 | 50.5 |
| Prisoners Dilemma 10 (unassigned replay-label variant) | 95 / 40 | 50.0 | 43.4 | 47.1 | 53.7 | 40.5 |
| Queen Of Spades (c4) | 208 / 84 | 58.7 | 53.0 | 60.9 | 69.1 | 54.6 |
| Schooltime (c3) | 201 / 87 | 61.8 | 60.3 | 46.4 | 67.2 | 61.3 |
| Slithery Fight (c0) | 220 / 91 | 60.0 | 58.6 | 52.3 | 55.0 | 57.3 |
| Trauma (c0) | 210 / 82 | 62.9 | 67.1 | 74.2 | 55.2 | 67.0 |
| Trophy (c6) | 222 / 109 | 61.6 | 56.8 | 46.2 | 58.2 | 57.3 |

Live us has one ranked series/five maps. Its observed field percentiles and unmatched raw differences are recorded,
but matched inferential gaps remainNA; absent maps stay missing and unranked is not substituted. No stable target
or current-strength claim follows. Query/era/cohort/counts/uncertainty and limitations: `docs/findings/2026-10-02-himeji-ranked-store-references-and-gate-ruling.md`.

Himeji's ruling on delegated gate question: for predeclared1.2.3 adaptations, overall pool win LB>0/gen>−.02,
economy LB>−.03 both panels, retain material/early/tier2/CPU guards. Queen falsifier is diagnostic, no exemption.
Retain Antioch/Nara sprint-bundle reading with disagreement:05−00 passes retrospective screen,05−04 fails required
pool-positive LB(−.020). 04 can be corrected measurement base with explicit fingerprint; parents cannot be swapped.
Φ remains diagnostic pending validation. These are decision tolerances, not field percentiles; no ledger/bot action.
All historical references/verdicts and H-H1 weight0.5 remain unchanged.


### Unit 9 closeout — 2026-10-01 19:02 UTC

Field targets remain the frozen provisional unit8 ranked references; no local result fills a live-us gap.
For Kyoto cap-lift, official paired pool win is+2.192pp [central90%−1.258,+5.428]/479, gen+.672pp
[−1.815,+3.091]/744. Map–opponent block sensitivity also spans0. Reject remains; earlyp100LB−.024 fails−.02,
and one pool fixture is a1800second runner timeout (unknown cause/outcome). Disagree with the claimed certified
win lever/no off-pool cost: old labels overstate paired pool gain by1.253pp. Retain original Kyoto result historically;
request official rescore and timeout resolution. No post-hoc gate-category change or acceptance implied.
Method/counts/uncertainty/provenance: `docs/findings/2026-10-02-himeji-kyoto-official-caplift-and-closeout.md` and `tools/himeji/unit9_audit/summary.json`.
These are local-panel gate readings, not field percentiles or stable targets. H-H1 stays0.5. User stopped recurring
work; next analysis requires user resumption.
## Nara (glm, P2-A)

**Era rule (unit 1, refined unit 2):** server switched in the 1 Oct 05:54–09:23 UTC window; I adopt the replay
lead's store tag (**post ⟺ started_at ≥ 2026-10-01T06:00Z**, equivalent — no games in the gap) and their
engine-verdict patch as the decoder fix (better than recomputing; my independent derivation agrees: 2,135 rl games,
0 violations). Queen = **original lowest-id initial robot, dead → 0, no inheritance**; then longest, then total.
⚠ Until the verdict patch lands, replay-extracted W-L-D is wrong in queen-decided games (8.2 % of rl games
queen-decided, 4.8 % flipped, full post sample).

**Post-era reference status: NOT stable** (58–132 field sides/map in my samples vs ~1,500 pre). Per-map pre→post
medians (unit 2, corrected): pearls@50 flat on most maps but **Schooltime +67 %/+171 %** at r50/r100 and
**Trauma ×4** at r50 (broad-based, not one team); Slithery −13 %; units@100 flat-to-down (median −3 %);
**own-goal deaths +12 % field-wide** (7/10 maps up 10–24 %) — tier-2 guards need era-matched baselines. Formal
re-derivation when the store rebuild + ≥300 games/map.

| cluster / map | phase | metric | top-10 value | us | gap / target | era | query |
|---|---|---|---|---|---|---|---|
| all | r0–25 | total length vs same opposition (field SD) | +0.11 | −0.49 (pre) | 0.60 SD | pre (carried) | S-1 Q3; post pending store |
| all | r50 | bed pearls ÷ field median | 1.07 | 0.83 (pre) | target ≥ 1.0 | pre (carried) | S-1 Q3; `tools/nara/opening_probe.py` |
| sparse/large (Schooltime, Trauma, QoS) | r50–100 | pearls ÷ field median | +67 %/+171 % (Schooltime, post vs pre field) | — | the era's economy mover; watch item until store volume | post (provisional) | unit 2 §2 table |
| all | r0–150 | own-goal deaths /1k dt | pre-era references stale (+12 % era shift) | — | compare vs era-matched parent only | post | `tools/nara/era_shift_probe.py` |
| **rl maps excl. pockets** (Portals, Trauma, Schooltime; NOT Slithery/Autarky/PD — H-Q3: queen dies r4–5 in a spawn pocket there, mechanically) | r490 | **queen survival** (RL-reached, official winners) | 306/Vibing++ **9/31 ranked RL** (deployed, #1 at 2309 Elo 3 Oct); Sponge #4, fandagong #7 keep queens | **us live: 0/326 (0.0 %, median death r59, h2h 46 %/wall 36 %)** | **target ≥ 0.5** short-term (antioch's line), ≥ 0.9 full build; guard: econ LB > −0.03, elimination wins flat | post | `tools/nara/queen_cause_probe.py --teams 7` |
| all (live) | r0–500 | **win rate, post-era live** | new top ten beat us 76 % of unranked scrims (SSS ×77, horse ×74, ftm ×40, Sponge ×35) | ranked 56.6 % (112/198, mid-field); unranked 23.6 %; loss maps = rl maps (PD 13 %, Trauma 17 %, Autarky 21 %, Portals 21 %) vs Devil 60 %/QoS 57 % | close rl-map deficits first (queen + conversion queue) | post | findings unit 4 §3 |
| rl maps excl. pockets | r490 | **queen length** (fed form) | Cutlery: 22 by r400, up to 65; field 0 | — | ≥ 1 beats every dead queen; **20–30 by r400** is the measured fed form | post | same |
| rl maps | r490 | **queen-decided losses** (ours dead, theirs alive) | — | — | target 0 | post | same (join index winner) |
| all | r490 | longest dragon | 40–46 (cheji/Stockfish, pre); post pending (rl-side samples too small yet) | 25–28 (pre) | post re-derivation when store lands | post-pending | TT method |
| all | r490 | round-limit losses with a material lead | 0.32–0.43 (pre) | 0.33 V06 / 0.57 hb1-12 (pre) | **< 0.10** with a kept queen | post | `tools/tt/endgame_gate.py` |

Design note from the field's reference build (unit 2 §4, mechanism in unit 3 §3): Cutlery's queen is **the crown
from birth** — moves 454/500 rounds, eats 30 pearls (field queen: 3), keeps production-splitting, grows 4→22 by
r400 — and the 13:00Z flip was simply **stopping the invalid-command cull** (65 % of its queen deaths pre-flip),
kept as a state-keyed cull on pocket maps only. No avoidance premium (exposure = teammates). The live arms:
crown-election-to-queen (N6) and queen-keyed enclosure avoidance (unit 3 §1: contact-map queens die to enemies,
corridor/pool-map queens die to geometry — match the mechanism to the map's hazard class; pocket maps: culling is
correct). (design proposal, not field percentiles — H15-05) Note: h2h length is not armor (victim longer 857 / shorter 496) — q_len's value is tiebreak margin and
queen-vs-queen duels, both rising as protectors appear.




### Unit 10 reorientation — 2026-10-03 22:38 UTC

Old per-map references remain frozen/provisional. Current map pool17API names (18decoderlabels) and currenttop10
306/91/264/213/952/842/552/87/82/566 require new matched references. The fresh coverage sample is119games,
123top10sides; terminal rankedRLqueen survival25/53,95%whole-seriesCI[32.3,63.1]%,27series. Unranked9/21,
5series. These observations are not field-percentile targets or r490 estimates. Solequeenwins19/19ranked.
Query `tools/himeji/recent_endgames.py` + `summarize_endgames.py`, post123; population/counts/uncertainty and
sampling caveats in `docs/findings/2026-10-04-himeji-resumed-live-data-and-top-team-regimes.md`. No matched live-us gap inferred; current24hcorpus has0rankedus.
H-H2 proposes repeated hidden behavioral regimes;40independentmatchedseries perregime for a30ppbinaryeffect
(approximate5%two-sided/80%power), held-out repetition and alternatives required; no evidence of deceptiveintent
from155unidentified top10side-games with0matched mode strata. H-H1 remains0.5.


### Unit 11 measurement correction — 2026-10-03 23:08 UTC

No new stable field-percentile target. Frozen references and other analysts' proposed targets remain intact.
Nara's exact737 own-game sample has398 officialRL,72 queen-decided outcomes (70losses/2wins), terminal own queen2/398.
By submission/mode:14265 ranked1/74,unranked1/175;14585 ranked0/40,unranked0/109. These are terminal sample counts,
not r490 estimates or matched field gaps. Current ranked maps include17names. Query/provenance/counts and both
material-lead denominators are in `docs/findings/2026-10-04-himeji-live-queen-audit-and-growth.md`; frozen official rows `tools/himeji/unit11_audit/audit/`.
Disagreement retained: Nara N6 weight increase is not causally supported by #1rank with unknown build identity.
Its log-units guard requires zero/reach/statistic specification and rescore of02/03 before adoption; normalized−.146
cannot be compared directly to log−.10. D-042 and H-H1 weight0.5 unchanged; ask testers for the existing-data rescore.
Four selected ranked long queens show moving queens and late corpse growth, not population percentiles/feeding intent.
Current331-game coverage sample remains descriptive; matched live-us gapsNA; local panels and unranked remain separate.


### Unit12 ruling and live coverage — 2026-10-03 23:36 UTC

L10 estimator ruling: retain the predeclared mean-of-checkpoint-medians econ~; arithmetic mean stays diagnostic.
Independent paired480/1392 read gives0/−.00418; neither panel positive under map/opponent/seat or seed/map90%intervals.
PoolwinLB fails+2pp borderline rule. HOLD/unstacked regardless of proposed units-guard relaxation; D-042 doesnot
reclassify L10 automatically. Keep Nara's proposed logguard alongside Himeji's unresolved zero/reach/weighting objections.
Queries, sourcehashes and bothclusteringintervals: `docs/findings/2026-10-04-himeji-live-coverage-and-L10-ruling.md`.
Tennewrankedown14585games(2series) correct the19h-silence claim:3wins,7actualr490reached/0queenalive,3queenlosses;
2/6RLlosses withtotallead and2/2leads lost, measuredseparatelyatr490/end. Schooltime249–6materialloss followsqueen
selfdeathr0. These are descriptivecasecounts, notpercentiletargets; no livepopulationCI with2series, matchedtop10-usNA.
Map/cohort/source/era/checkpoint fields are frozen in unit12_audit. Currenttop10adds55/drops552; oldanchorsunchanged.
H-H1weight0.5 andH-H2unresolved; requestqueenalive-at-trigger/never-triggered diagnostics forRomeL39/L49.


### Unit13 hypotheses — 2026-10-04 00:08 UTC

User directed hypothesis generation tolead thiscycle; no newstablefieldpercentiletarget.
H-H3 proposedL24/L49,weight0.5: freeonecellinfullqueen spawncycle via legal2+2split/childremoval, retainoriginalhead
andlength3patrol.21Schooltime r0selfcases(6ranked/15unranked) all0emptyadjacentsteps;20opponentsfirstsplit,
18/20aliveactual490. Observationalcasecohort; no causalCI. Fouropencontrolsdifferingeometry preventversioncausality.
H-H4 refinesH-H1/L39/L49,weight0.5unchanged: earlyproduction thenstate-triggeredqueengrowth; all12collectedranked
306/91 Maze/Slitheryqueens splitbefore100,7/11reaching490survive,1earlyelimcensored. Do not imposeuniversalqueenlength.
Fullmechanisms,ledgerlinks,falsifiers,negativecontrols,exposuredefinitions andsamplesizes: `docs/findings/2026-10-04-himeji-pocket-survival-and-phased-growth-hypotheses.md`.
TesterRome alreadyhasL39/L49queued; H-H3fornextfreeassignedtest. Legalchecks then60independentexposedpairs;
10pp pairedbinaryplanning149/306/463 atdiscordance.2/.4/.6 beforeclusterinflation. No acceptanceexemption.
Disagreementpreserved: Nara's logguard cannot be scored fromnormalizedmedianbounds; twoobservedownsubmissions
invalidateitsall14265windowclaim. CurrentfieldgapsremainNA; historicalreferences/peerproposalsunchanged.

### Himeji unit14 — held-out pocket evidence, 4 October00:37UTC

H-H3(L24/L49,.5) now includes repeated space/legality after food:33/34fresh Schooltime sides firstsplit and
all33survive25;29survive490. Ranked23/26 [series95%76.9–100],unranked6/8 [25–100];17games/17series,4hashes,
allreach490,post123. This is a collection-snapshot holdout with repeated geometry, **not a stable percentile target**.
Only2currenttop10sides/no live-us; matchedgapsNA. Query/selection/counts/uncertainty and≥60eligible-pair testcard:
`docs/findings/2026-10-04-himeji-pocket-holdout-and-late-food.md`, `tools/himeji/pocket_holdout.py`,
`pocket_summary.py` and `unit14_audit/`. Fourlate failures/3games:food3→4thenwall;unitlimit legality unresolved.
H-H4 feeding remains separate from sealed-pocket occupancy; no extra tester queue or weight increase.

Retain other analysts' historical targets and disagreement: Nara's737is mixed501/236submissions,2/398notzero;
3/4cited livequeenlosses have terminallead,not4/4. Source FRAME7 bed-label fallback is unverified for pearl
appearances on static TILE(0,0); preserve originunknown before updatedQ3bed percentiles. No frozen reference changed.

### Himeji unit15 — dead-queen conversion reading,4October01:08UTC

H-H5proposedL39/L49,.5: retain normalcrown fallback absentfreshqueenevidence; Rome03REJECTstands. LocalPortals
96pairedfixtures/192replays:95triggerwithqueendead,0livingqueeneligibleturns;pairedscore−21.875pppool
[95%−38.542,−8.333],−27.083gen[−43.750,−10.417],16opponent-seatblocks/panel. Postselecteddiagnostic,
notfieldtarget ordirectfeedingtest. Query/exposure/testsize/falsifier: `docs/findings/2026-10-04-himeji-dead-queen-conversion-reading.md`,
`tools/himeji/rome_trigger_audit.py`, `summarize_rome_trigger.py`, and `unit15_audit/`. H-H1/H-H3/H-H4weights unchanged.
Freshlive14585vs801one rankedseries1–4;queen0/4actual490,1earlyelimcensored;materialleadloss/RLloss3/4 and
lost/RLlead3/3 at490/end. One series/no stableCI; matchedtop10-us gapsNA. Modes/localpopulations separate.
Nara'scorrectionsacknowledged;retainstructuraldisagreement:992701queenlen3/972cellcomponent/MOVEr0isnot4cell
splitpatrol. Unit14's17games/4hashesdo notclosecausality orjustifyuniversal20+/3lengthtargets. Historicalreferencespreserved.


### Himeji unit16 — measurement correction and cap mechanics, 4October01:40UTC

Correct H13/H14's no-bed/non-static-bed inference:10public headers zero all fertility pairs;4local headers retain
fertility.997644's1758fallbackspawns align authored bedcoordinates, but livegeometry differs. No new spawnmechanism
or FRAME7error established. Historical reports preserved; H-H3 requires topology/occupancy, not bedabsence.
Eight isolated1.2.3 mechanics fixtures: splitlegal at63,invalid64; full4-cellqueen allfirststeps collide;
length3safe2steps spend1segment. H-H3 proposedL24/L49 .5: test observable prevention beforegrowth atcap.
>=60independentlate-exposedpairs+controls,win/economyguards; not a universal length2 target or stable fieldpercentile.
Query/era/selection/counts/limits/falsifier/tester: `docs/findings/2026-10-04-himeji-pocket-cap-legality-and-fertility-correction.md`, tools/himeji/unit16_audit/.
Currenttop10adds507/drops82. Store533games/1066sides includes538currenttop10/12own but ends3Oct23:11Z,
coverage-selected330ranked203unranked. No new stable references or matchedlive-us gaps; H-H4/H-H5 separate.


### Himeji unit17 — intervention timing and pocket precursor,4October02:08UTC

Rome04 latecrown tie handoff cannotactbefore250; r150queenparity95/423pool244/994gen cannotfalsifyH-H1.
480/1392localpairs,score−1.354pp[95%−3.125,+.417]/0[−.503,+.503];source/exposuremismatch keepsH-H1.5.
No fieldtarget. H-H3 .5 refined:food-free2step prevention beforegrowth; mealonfirststep→full4→secondstepselfdeath
in1.2.3fixture.4selectedlivefailures/3games(2ranked1unranked),2enginecases establishmechanics only;
>=60independenteligiblepairs+negativecontrols/winguards. Exactquery/counts/era/falsifier/tester `docs/findings/2026-10-04-himeji-rome04-timing-and-pocket-precursors.md`.
NaraL47disagreement:parent+immediatechild excludesdescendants,truncated10rhorizon/mixedmodes preventcausalregret
reading. Retainpeerproposal;requestcorrecteddenominators beforetest. No newstablepercentiles/matchedlive-us gaps.
## chongqing (Claude analyst, replay lead, wave 2) — unit 1, 2026-10-04 00:20 UTC

Source: `docs/findings/2026-10-04-chongqing-era-ladder-queen.md`. Queries: `tools/chongqing/qq.py` + the `qd/qs` queen views
(finding §A). **Cohort note:** the ladder was reset to 1500 on 1 Oct (06:21Z–17:09Z); `cohort`/`crank` in the store are
the **post-reset** ranks (top ten today: Vibing++ 306, forgot to mention 264, SSS 91, Sponge 213, WeHaveQuizzes 87, horse
842, free trip to sydney pls 82, Cache me outside 952, tungtung67 566, fandagong 552). Antioch's and Himeji's sections use
the 06:21Z cohort; five teams overlap. Both labellings stay; say which one a number uses.
**Provisional:** 3,535 of 23,035 in-scope post-change games decoded; the 2–3 Oct ranked bulk is in the queue.

**Endgame / queen (post, ranked, round-limit games, by post-reset cohort; pocket = Slithery, Autarky, PD, PD10).**

| cluster / map | phase | metric | top-10 | field r11–50 | us (live hb1-14) | target | era | query |
|---|---|---|---|---|---|---|---|---|
| non-pocket | end | queen alive at end of RL games | 0.065 (n 231) | 0.040–0.084 | 0.011 (n 89) | ≥ 0.5 excl. pocket (L49 falsifier, unchanged); interim: ≥ top-four keepers' 0.23–0.53 | post | qs §5 |
| non-pocket | end | RL games decided by the queen | 0.013 | 0.000–0.018 | **0.191** | **0** losses on the queen; the ranked field is still ~1 %, our live number is 19 % | post | qs §5 |
| Schooltime, Trauma | all | share of our games decided by the queen | — | — | **0.377 / 0.404** (lost 0.361 / 0.386) | ≤ field 0.05 after H-C1 (Schooltime) and a surviving queen (both) | post | qs §4 |
| Schooltime | r0 | queen dead at round 0 (`self`) | 0.003 (field 2/676) | 0.003 | **0.314** (22/70) | **0** — H-C1 bug | post | qs §4 |
| Default | r0–5 | queen dead by r5 | 0.36 | 0.22–0.24 | 0.25 (13/51, side A) | ≤ 0.05 (H-C3) | post | qs §4 |
| non-pocket | end | longest at end, median | 33 | 26–29 | 27 | ≥ 33 (post-reset top ten; Antioch's 42.5 was the pre-reset converters) | post | qs §5 |
| non-pocket | end | total at end, median | 70 | 60–67 | 69 | ≥ 70 | post | qs §5 |
| non-pocket | end | RL losses with a total lead ÷ RL games | 0.082 | 0.145–0.161 | 0.180 | ≤ 0.08 | post | qs §5 |
| pocket | end | longest / total at end, median | 55 / 138 | 44.5 / 100–124 | 39 / 99 | ≥ 55 / 138 — the pocket maps are pure longest races; the queen is irrelevant there | post | qs §5 |
| all | end | queen death cause, us | — | — | h2h-enemy 0.52, wall 0.27, own 0.14 | wall → ≤ 0.16 (top ten) is the geometry half; h2h-enemy needs distance (H-Q5) | post | qs §4 |

**Opening (S-1 Q3 components):** carried from Antioch's section unchanged (field medians at r25/r50 did not move; transits
the largest top-10 − us component at 0.56 SD). Re-derivation on the post-reset top ten waits for the bulk decode; the
`series` views for post parts bind in `qq.py` (`series` view) when needed.

**Adaptation clock (watch column, H-C4 / H-Q4):** RL non-pocket queen survival by team and day — Vibing++ 0.229 (1 Oct,
ranked, n 48); vs us on 2 Oct: SSS 0.533 (n 30), Sponge 0.700 (10), Vibing++ 4/4, WeHaveQuizzes 0.133, horse 0.125,
forgot to mention 0/16. Trigger for H-Q4 (hunt the enemy queen): ranked top-ten RL survival > 0.10 for a week.

**Disagreement slots:** (1) with Antioch's endgame "top-10" columns — cohort, not field move (above). (2) Himeji's release
criteria are adopted for the per-map columns; none is met yet for the queen columns.

## chongqing (unit 2) — 2026-10-04 02:00 UTC — era `post-m2` (new maps, ≥ 2 Oct 03:49Z), ranked, cohorts = ladder 00:53Z

Source: `docs/findings/2026-10-04-chongqing-unit2-map-era-and-field-queens.md`. **Supersedes unit 1's § 5 table** (which was
`post` = old maps; keep it only for old-map comparisons). Store `games.map_era` ∈ {pre, post, post-m2}; every per-map row
below is a new-map row. n is ranked side-games in the store (post-m2 decode ≈ 1,250 games so far; provisional).

| cluster / map | phase | metric | top-10 (n 489) | r11–50 (n 303) | us carthage-05 (n 85) | target | query |
|---|---|---|---|---|---|---|---|
| all | end | queen alive at end of RL games | **0.444** | 0.274–0.287 | **0.000** | ≥ 0.44 (top-ten median); the L49 "≥ 0.5" is now 1 team-SD above the top ten, not a leap | `qs`: avg(q_alive) where rl |
| all | end | RL games decided by the queen | 0.491 | 0.47–0.53 | 0.357 (all lost) | queen-decided *losses* 0; the share itself will stay ~0.5 while everyone keeps queens | `qs`: reason='queen' |
| Schooltime (new) | r0 | queen dead at round 0 | ~0 | ~0 | **1.00** (23/23) | 0 — Himeji H-H3 (legal r0 split → child sacrifice → freed-cell patrol) | `qs`: qdr = 0 |
| Schooltime, Trauma, Slithery (new) | all | our games lost on the queen | — | — | 0.87 / 0.40 / 0.33 | ≤ 0.05 | `qs` § 4 |
| Trophy (new) | end | RL share | 0.00 | — | 0.00 | Trophy is pure elimination now; queen logic is irrelevant there | `qs`: avg(rl) |
| all | end | RL losses with a total lead ÷ RL losses | pending n | pending n | Schooltime 0.52, Trauma 0.35 | ≤ 0.10 | `qs` |
| all | end | top-ten per-team queen alive (RL, n ≥ 25) | Vibing++ 0.56, Sponge 0.52, 𓎼 0.54, SSS 0.46, ftm 0.37, WHQ 0.21, CMO 0.23 | — | — | adaptation clock; H-Q4 trigger fired (> 0.10) | `qs` by name |

**Opening (S-1 Q3 components), post-m2:** not yet re-derived here — the `post` norms are old-map norms; new per-(map,
map_era) norms need ≥ ~300 field games per new map (decode in progress). Until then use Shenzhen's live top-10 − us at r50
(transits 0.65, total 0.47, units 0.40, splits 0.38, bed 0.33) and Antioch's old-map table, both labelled.

**Disagreement slot:** none new. Agreement with Shenzhen/Himeji/Nara on the map swap, the cage, and the live build.
