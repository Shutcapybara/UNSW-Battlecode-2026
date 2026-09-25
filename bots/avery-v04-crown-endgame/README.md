# avery-v04-crown-endgame — FAILED EXPERIMENT (kept as baseline evidence)

**Lineage:** avery · **Parent:** avery-v03-swarm-spacing.

## Hypothesis

19 of v03's 20 round-500 losses were lost on the longest-dragon tiebreak,
13 by ≤ 6 segments. Banking one crown + endgame feeding should flip most.

## Changes vs v03

- Crown role from round 200 (`crown_min_len=4`): volunteer when no longer
  crown known; CROWN beacons relayed 3 hops; demote when a known crown is
  3+ longer. Crown skips voluntary splits, head-risk ×1.5.
- Feeding from round 400: small (len ≤ 20) non-crown dragons converge on
  the known crown and die into an adjacent ally BODY segment.
- Crown-kill from round 380: strikes vs enemies ≥ longest known ally get
  +60 (trade penalty removed).
- Self packet gains a crown flag (bit 50); new K_CROWN packet kind.

## Measured result — hypothesis REJECTED as implemented

Run `experiment_data/avery-v04-crown-endgame_20260925060524786389` (242 games,
11 opponents): gauntlet-5 **74–35–1 — exactly flat vs v03**, but a large
regression vs the tew line (6–7 wins per tew bot vs v03's 9) and vs
ouroboros (10–12 vs v03's 16–6). Total 113–128–1.

Failure analysis (trace of a default-map loss to kraken-v04):

1. **Mass volunteering.** Every dragon with len ≥ 4 and no known crown
  volunteers from round 200 → most of the swarm stops splitting → economy
  stalls against aggressive opponents.
2. **Crowns die before 500.** A crown banked to len 40 by round 386 and
  another to 28 by 477, but none survived to the ruling; end-game living
  lengths were only 3–10. Length banked is not length kept.
3. Feeding converted some traffic into team kills for little gain.

## Lesson carried to v05

Make the crown strictly singular and late (`crown_start=300`,
`crown_min_len=8`, demote margin 2), drop feeding entirely, keep
crown-kill. See `bots/avery-v05-strict-crown`.
