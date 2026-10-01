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

**Opening (S-1 Q3's four components: bed conversion, production, early portal use, territory):** pending. The post-change
store build is running (`tools/s1/build.py corpus --era post`, 1,143 games). Post-change references and their stability
come in my next unit.

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
