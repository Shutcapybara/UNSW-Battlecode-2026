# R-2c — Open exploration lane, ledger-guided (Opus 5.5, desktop, Claude Code) — lane `rc`, lineage **Cézanne**

Host: the Ubuntu desktop, `~/Documents/Projects/2026/UNSW-Battlecode-2026` (the only checkout; never `~/Projects`),
venv `.venv`, `--jobs $(( $(nproc) - 2 ))`. Branch `r/rc`, worktree `../wt-rc`, bots `bots/cezanne-<nn>-<slug>/`,
tools `tools/rc/` (copy `tools/ra/` and `tools/lune/score.py`; do not fork the scoring logic).

## Read first, in this order

1. `docs/hub/HYPOTHESES.md` — the ledger. You pick mechanisms from it, and you end every report with the rows you
   touched and proposed weights. Rows ≥ 0.3 are the menu; rows ≤ 0.2 only when their trigger has fired.
2. `docs/findings/2026-09-30-ra-lane.md` (Renoir: 33 single-knob moves, 0 accepted; caution costs economy one for
   one in this lineage; exploration value is a pool-fit lever; the seed moves the world by +0.07; V06's `W==32 &&
   H==16` terms are map identity), `docs/findings/2026-09-30-r1-search-ladder.md` (Lune: no CPU wall; the node cap
   is the one knob; late cap ×8 is the recommended level; wide search hurts the opening and helps later; the next
   lever is *what* the search values and *when* it searches wide), and `git show origin/r/sciel:claude/sciel-status.md`
   (Sciel: EW food-density memory cleared the economy bar at +0.067 and was killed by ally head-on +34 %; the fix
   is to discount the density term by ally saturation).
3. `docs/hub/prompts/2026-09-29-R2-open-lane.md` (the original lane brief; the loop is the same), and
   `docs/analysis/BENCHMARKS.md`.

## Base and gate

Base `cezanne-00-base` = `bots/lune-r1-07-latecap8x-only` verbatim (golden parity first), then `cezanne-01-nodevil`
with `devil_center_bonus`, `devil_lane_bonus`, `ally_body_buffer` inactive (map identity; D-033) as the parent of
everything after. Gate as in D-032: paired fixtures, seeds 1–3, pool + generalisation panel, both seats; accept on
the bootstrap 90 % lower bound of Δ(economy) > 0 on the pool with the generalisation lower bound > −0.02,
units/length lower bounds not < −0.02, no tier-2 rate up > 10 %, win lower bound > −0.02; per-checkpoint deltas
reported so a late-phase change is judged on the checkpoints it can move. One mechanism per version; the parent
reproducible from the same source; CPU probe on anything that adds computation.

## Where the ledger says to dig (start here, in this order)

- **L12 (0.7 after Sciel): the stateful-valuation direction.** Sciel-03a is the first mechanism in the programme to
  clear the economy bar; its failure was convergence crowding. Build the ally-saturation discount Sciel proposed
  (03b) on this base, then the enemy-density counterpart (S-1's EW enemy field as a risk term on the same grid), then
  the decay constant as a parameter. This is the highest-value line on the ledger.
- **L02/L03 (0.7): when to search wide.** Lune found the damage is opening-only and the gain late; the round-40
  boundary is a stand-in. Replace it with an observable: a cap scaled by local pearl sparsity (pearls seen within
  the last search horizon) or by units-in-view. The test is that the opening is unchanged and the late gain stays,
  on both panels, with no round threshold.
- **L11 (0.4): bed guarding keyed on structure, not a flat wait.** Renoir's flat waits lost on dense maps and won
  on sparse; the arm to try is a guard whose propensity is a function of measured bed density within reach and
  contact distance, with the H8 information-state ladder as the ablation.
- **L10 (0.4): the two D-030 fight rules** (refuse contact when the nearest observed bed is > 6 cells;
  converge-or-refuse), with expected sign on own deaths per fight.
- **L27 (0.5): one learned decision function in C++.** If HB-1 has published a wrapper or a split gate by the time
  you get here, port it as a switch; otherwise a GBT split gate fitted on the corpus (the `export_hgb.py` path).

Do not repeat a rejection another lane has logged unless you can say what is different (Renoir's table is in its
report; Sciel's in its status file). Renoir's "caution costs economy" result means any hygiene mechanism must
change *which* pockets and beds are entered, not how many — state that in the expected sign.

## Reporting

`claude/rc-status.md` after every version (running table: version, mechanism, ledger row, pool Δ with interval,
generalisation Δ, per-checkpoint, CPU max, verdict, why). `docs/findings/2026-10-0x-rc-lane.md` at every fifth
version, ending with the ledger rows touched and proposed weights. `CANDIDATE.toml` on every accepted version
(`language = "c++"`, lineage `cezanne`, `lineage_parent` = previous accepted). Commit and push `r/rc` after every
version. Do not register anything yourself. Do not read or use lane `rb`'s work (it is deliberately blind; you may
read its status file only when the director says the two lanes are being compared).
