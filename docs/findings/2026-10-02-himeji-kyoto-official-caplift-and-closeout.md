# Himeji unit 9 — Kyoto cap-lift official outcomes and closeout

**The cap-lift's claimed pool win gain is overstated by the old winner decoder.** Official paired gain is
+2.19 percentage points (central 90% fixture-bootstrap interval −1.26 to +5.43), versus old-rule +3.44pp.
The rejected verdict stands. One omitted fixture was a runner timeout; the panel is incomplete.
The user requested wrap-up and stopped the recurring task; the automation is now PAUSED. No query remains running.

## Official outcome audit

Read all 2,447 available replay headers for `kyoto-01-nodevil` and `kyoto-03-latecap`, pool and gen, seeds1–3,
both seats. All terminated; all official results match the runner index. The reconstructed old-rule winner matches
all 2,447 stored feature outcomes. Thus this is a measured label correction, not an assumed inference-bias allowance.

| Panel / arm | Available n | Old W–L–D | Official W–L–D | Official score (draw=0.5) | Winner flips |
|---|---:|---|---|---:|---:|
| pool baseline | 480 | 401–78–1 | 396–83–1 | 82.6042% | 7 |
| pool cap-lift | 479 | 417–62–0 | 406–73–0 | 84.7599% | 11 |
| gen baseline | 744 | 515–228–1 | 515–228–1 | 69.2876% | 0 |
| gen cap-lift | 744 | 520–223–1 | 520–223–1 | 69.9597% | 0 |

Paired key is `(map, seed, opponent, seat)`, candidate minus baseline. Pool uses the479 common fixtures;
subtracting the two unpaired headline shares is not the paired estimand. Gen uses744.

| Panel | Paired gain | Central90% fixture CI | Central90% map–opponent block CI | Better / worse / same |
|---|---:|---|---|---|
| pool | +2.192pp | [−1.258,+5.428]pp | [−0.731,+5.104]pp | 50 / 39 / 390 |
| gen | +0.672pp | [−1.815,+3.091]pp | [−1.815,+3.024]pp | 62 / 57 / 625 |

Each bootstrap has1,000 draws, seed7. Fixture order is explicitly sorted; finite-draw old-label bounds need not
exactly equal Kyoto's feature-order bootstrap. Blocks retain all seeds and seats for one map–opponent pair
(80 pool /124 gen); the sensitivity is reported alongside the original fixture convention, not chosen after
seeing which passes. Both methods leave pool improvement unresolved. Pool correction changes the paired delta
by−1.253pp; error does not cancel between arms. Trauma changes from old +2.08pp to official−4.17pp (48fixtures),
a descriptive per-map diagnostic, not a multiple-comparison claim.

## Missing fixture and reading

The missing cap-lift result is seed2, Slithery Fight, seatA vs `ouroboros-m01-vibing-mimic`.
Its index records `seconds=1800.1`, `rc=-9`, `reason=timeout`; no replay exists. The runner catches its
1,800-second subprocess deadline and writes that code, so this is a wall-clock runner timeout, not evidence of
an engine turn-budget disqualification. Baseline won the paired game. Counting an eventual candidate loss through
win bounds the complete480-fixture point delta at **+1.979 to +2.188pp**. This is a missing-outcome bound,
not a confidence interval or imputed result. Root cause and reliable completion remain Kyoto's responsibility.
Do not turn the completed-case result into an error-free full-panel acceptance.

Kyoto's economy figures are retained as reported, not re-extracted: pool econ+.015 [−.002,+.033],
late econ+.025 [−.001,+.056], p250+.045 [+.007,+.093], early p100 lower bound−.024;
gen econ approximately0 [−.016,+.018]. The p100 guard already fails−.02. “No off-pool cost” is too strong:
gen win is now measured at+.672pp [−1.815,+3.091], and a near-zero economy estimate is not equivalence.
It narrowly satisfies Himeji's retrospective gen win noninferiority tolerance under this draw, but pool-positive
win, early guard and complete/error-audited panel requirements fail. Historical REJECT is preserved.

A search-cap lift inherited from prior rules is not automatically a1.2.3 adaptation. Declare the applicable gate
before a confirmation test; do not retrofit an arm's category to evade a guard. Do not rerun solely for a more
favourable bootstrap. Kyoto should resolve the missing fixture, replace winner-dependent scores with official
outcomes and predeclare the next contrast/uncertainty scheme before any fresh confirmation. H-H1 remains0.5;
this cap-lift does not test its production-preserving queen-split mechanism. No new hypothesis weight is proposed.

Kyoto02 is still pending. Its no-production-split/tail-shed-above5 stack differs from Carthage's arms; treat it as
its own intervention rather than an exact host replication. Rome L10 has no new paired result in the inspected
status. No result is inferred from progress counts.

## Reproduction and provenance

Read-only queries, two header workers. No simulator, bot run, download, shared-store/norm write or peer edit.
Source Kyoto commit `75cb6c17ac847110d645646f9336117ab2fd171b`, finding §5 and `tools/kyoto/lane.py`.
All source index hashes, feature hashes and individual replay SHA256s are frozen in `tools/himeji/unit9_audit/`.
Index files do not bind engine version or bot build fingerprints;1.2.3 provenance is the tester's recorded engine
and prior pricing checks. Replay hashes pin the observed outcomes; these named-run paths are not fingerprint-keyed
zoo identities. Do not assert cross-host binary identity from arm names alone. All outcomes are **local panels**,
not live ranked or unranked strength estimates, field percentiles or stable targets.

From the Himeji checkout, with the existing main analysis Python, output into a fresh scratch directory:

```sh
PY=/Users/alik/Documents/Projects/UNSW-Battlecode-2026/.venv/bin/python
MAIN=/Users/alik/Documents/Projects/UNSW-Battlecode-2026
RUNS=/Users/alik/Documents/Projects/wt-kyoto/build/kyoto/runs
OUT=/private/tmp/himeji-unit9-reproduce
$PY tools/himeji/audit_paired_headers.py --repo "$MAIN" --runs "$RUNS" --out "$OUT" --jobs 2
$PY tools/himeji/freeze_feature_winners.py --runs "$RUNS" --out "$OUT"
$PY tools/himeji/summarize_paired_headers.py --out "$OUT" --feature-winners "$OUT/feature-winners.json"
```

Header audit checkpoints and refuses changed indexes on resume. Summary validates all2447 labels, unique fixtures,
termination and runner parity before paired comparisons. Source feature parity is independently asserted.
Frozen `header-rows.jsonl`, `paired-rows.jsonl`, `summary.json`, manifests and feature outcomes suffice for review.

## Handoff, frozen cursors and remaining work

Source commits: main`1d838553a`, Antioch`cdac8bd96`, Carthage`3ff5dd9aa`, Nara`21a182700`,
Kyoto`75cb6c17a`; Rome local L10 pool480/480, gen842/1392 at wake. Board cursor is Kyoto18:20 cap-lift result,
prior peer cursors unchanged; Himeji throughH9-05 after publication. Protocol read from origin/main.

Wake snapshot: corpus81,045 games, latest start18:27:11.705Z, index SHA256
`cc0202def565c004efd170be2c0cc7c803d8262e718830c54aed803d560dc51d`.
Ladder `20261001T182238Z.json`, top IDs952/206/801/314/20/213/249/375/87/46.
S-1 games SHA256 remains`bfe4516582393c959f1cbfcf8279946d7c6a01466a5a75f65cd4e7da618e18c2`;
unit8 post decoded window09:26–15:39Z and2,862 games remain the completed reference freeze.
There are28 collected post team7 games:5ranked unchanged,23unranked (13new, not decoded in this unit).
No new live outcome or matched top-ten-minus-us inference is claimed. Historical targets remain provisional.

If resumed by the user, next useful work is the13 new unranked live replays separately from the unchanged ranked
series, new ranked series as collected, PD10 geometry/alias verification, later-window/current-leader references,
and Kyoto's resolved timeout/official rescore. Φ active-only validation/provenance remains pending. Do not redo
finished winner audits or old references merely because time passes. Recurring work stopped at the user's request.
