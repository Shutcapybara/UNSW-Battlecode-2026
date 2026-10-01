# M-1 — Map anatomy: why we brick on specific maps, and what local payoff generalises (GLM 5.3)

Lineage: as given by the lead at launch. Bots `bots/<lineage>-<nn>-<slug>/`, branch `r/<lineage>`, worktree
`../wt-<lineage>`, tools `tools/<lineage>/`. Host: preferably the desktop (`~/Documents/Projects/2026/UNSW-Battlecode-2026`,
~2,900 games/h, `--jobs $(( $(nproc) - 2 ))`); the Mac VM is OOM-prone under load and should be used only if the
desktop is unavailable. Read first: `docs/hub/prompts/2026-09-29-R-index.md` (rules, D-032 gate, D-033 base),
`docs/hub/HYPOTHESES.md`, `docs/BASELINES-2026-09-30.md`, `docs/analysis/BENCHMARKS.md` (the per-map references),
`docs/findings/2026-09-30-ra-lane.md` §"Generalisation finding" and its per-map trades (QoS/Trauma up, Devil/Schooltime
down recurs in a third of candidates), `docs/findings/2026-09-30-r1-search-ladder.md` §"Seat and map-family
asymmetry", your own `docs/findings/2026-09-30-r3-ares-leaks.md` (per-map peaks: trapped Slithery 101.5 / Portals 75.7
/ Devil 66.2; portal Portals 57.7; newborn Slithery 70.6), `docs/analysis/C1-pace-targets.md` (targets as functions
of structure), `maps/new/EXPLAINER.md` (the synthetic suite's motif families), and the R-4 scorecard
(`python -m tools.analysis.features.scorecard`, `run_panel --panel gen`).

## The idea (the lead's, 30 Sep)

The programme is in a local minimum: every pooled single change is ±0.02. Local improvements sometimes create
global setbacks, but the maps where we *brick* — where we sit far below the field — are where a mechanism can
have a large effect, and a large local effect is easier to see, understand and then generalise than a small
pooled one. So: diagnose per map, fix per **structural signature**, measure globally. The out-of-sample rule is
not relaxed: a per-map *diagnosis* is fine, a per-map *policy* is forbidden. The bridge between them is the
signature — the observable structure that makes the map what it is — and the test that the fix also pays on
unseen maps with the same signature.

## Part 1 — the brick list (half a day)

Base = the lanes' base: `lune-r1-07-latecap8x-only` with the `W==32 && H==16` terms off (`<lineage>-01-nodevil`;
copy from any lane that has built it, or build it; golden parity of the base against `lune-r1-07`).

1. Run the base on z1 (seeds 1–2, both seats) and the generalisation panel (seed 1). Per map: the BENCHMARKS
   three-number form for every tier-1 and tier-2 metric (absolute, gap to top ten, **field percentile**) on the
   pool; base-normalised raw numbers on the 29 gen maps (no field reference there).
2. Rank maps by how far below the field we are on the economy curve and on win share, and by which tier-2 row is
   the outlier. Expect Slithery, Portals, Schooltime (large/dense), Devil/Trophy transposed (identity loss), and
   whichever gen motifs the base loses (Renoir: `devil_tr`, `trophy_tr`, transposed QoS/Trauma).
3. For every map, pool and gen, compute the **signature vector**: tile count, open-cell share, kelp density,
   corridor degree distribution, portal count and pair geometry, bed count and density, bed cluster spread,
   spawn-to-nearest-bed distance, spawn-to-spawn contact distance, wrap usage. `tools/analysis/features` and
   `maps/new/manifest.json` have most of it; add the rest to `tools/<lineage>/signature.py`.
4. Cluster maps by signature (not by name). Report which gen maps share each brick map's cluster. That table is
   the deliverable of Part 1 and the map for Parts 2–3.

## Part 2 — anatomy of the three worst (one day each)

For each of the three worst pool maps (and, if one of the gen clusters is worse than any pool map, that cluster):

- **Where the games are lost.** The economy curve vs the field on that map by checkpoint; the death ledger by
  class (`tools/analysis/r3_ledger.py`) and by round band; the portal instrument where relevant; seat asymmetry.
  Then read five losses in the visualiser and write what actually happens (the C1-C ledger tells you *what*
  dies; the replay tells you *why*, and the two disagree often enough to make this step mandatory).
- **Which signature feature does the damage.** Say it as a claim about structure: "we lose on maps where kelp
  corridors of degree ≤ 2 hold ≥ 30 % of the open cells" — not "we lose on Slithery". Check the claim against
  the gen maps in the same cluster: do we lose there the same way? If not, the claim is wrong or the cluster is.
- **The candidate mechanism**, keyed on that feature, written down with its expected sign on the map's outlier
  row and on the pooled economy *before* any run.

## Part 3 — local fix, global test (the loop)

For each candidate (one mechanism per version, a `params.hpp` switch, golden parity of the switch-off build):

1. **Local test first**, cheap: that map plus its gen cluster, 8 opponents × both seats × seeds 1–3 (~50 games
   per map). If it does not move the outlier row *and* the map's economy, stop; write the number.
2. **Global test**: the full D-032 accept test (pool + gen, seeds 1–3, paired, interval form). Report three
   things separately: the local gain (the map and its cluster), the global delta (the pooled interval), and the
   **transfer** — does the gain appear on the unseen maps of the same cluster (yes = the signature was right; no =
   it learned the map, reject).
3. Verdicts: **accept** on the D-032 rule; **local hold** when the local gain transfers to its cluster, the
   pooled interval is not negative, and only maps *outside* the cluster pay — that is the case for a
   structure-gated switch (the gate is the signature feature, observable in play, never the map), which is then
   tested as its own version; **reject** when the gain does not transfer or the pooled interval is negative.
4. Keep a running "map × mechanism" table: which mechanisms help which clusters and hurt which. That table is the
   thing the programme does not have and the lanes need — Renoir saw the same QoS/Trauma-vs-Devil/Schooltime trade
   in a third of its candidates without being able to name it.

## Deliverables

`docs/findings/2026-10-0x-<lineage>-map-anatomy.md` (Part 1 brick list and cluster table; Part 2 anatomies with
the structural claims; Part 3 map × mechanism table and verdicts; the ledger rows touched with proposed weights —
L28 and L29 at least, plus a new row per structural claim), `claude/<lineage>-status.md` after every version,
`game_stats/runs/<lineage>-*.json`, `tools/<lineage>/signature.py` (reusable: every future lane should be able to
print a map's signature), bots `<lineage>-01…`. `CANDIDATE.toml` on every accept or local hold. Commit and push
`r/<lineage>` after every version; do not register; do not edit other lanes' trees; never key anything on a map's
name, hash or dimensions.
