---
id: 2026-09-28-analysis-layout-id-parity
author: glm/analysis/a1
kind: observation
title: "Starting layout is deterministic on nine of ten live maps: layout = parity of the game id. Prisoners Dilemma has four layouts and no local rule"
task: "A1 §3.3 — starting-layout assignment"
supersedes: []
evidence: "All 486 games in LIVE state.json (verified + unverified; map_hash present on 446). Unit = game. Series→games linkage via state.blocks[].requests. Checks: layout vs {seed, side, arm, opponent, own submission, pool, request position, hour, series, game-id parity}; strict-alternation test; series-purity test (0/446 mixed cells). Script: tools/analysis/a3_layout_assignment.py."
---

# The rule

For the nine two-layout maps (all live maps except Prisoners Dilemma / map_id 17):

**map_hash = the layout selected by the game's own id parity (id mod 2) — 0 exceptions in 446 games.**

Verified three ways: (a) per-map contingency of hash against id parity is pure for all nine maps; (b) the same layout repeats for an entire series (0/446 series have two layouts on one map), and consecutive series requested back-to-back (3 s apart, ids contiguous +10) always share layouts per map; (c) every observed "all maps flipped at once" event (e.g. block ca5af1bf, 9/10 maps mismatched between arms) sits at an id gap between the two arms' series that is ODD — foreign games were created between the two requests (5 foreign ids 474275–474279 in the ca5af1bf case).

What it is NOT a function of: seed (all 486 seeds distinct — untestable directly, but seed parity shows no association), side, arm, opponent, our submission, pool, request position, hour. Requested-time gaps per se explain nothing: two 6-second gaps behaved oppositely (7bb77b13 ctrl→cand shared 9/10; ca5af1bf ctrl→cand flipped 10/10) — the id gap is what differs.

**Prisoners Dilemma (map 17) breaks the rule**: 4 distinct hashes, id-mod-2 and id-mod-4 both fail, single-map fill requests cycled through all four hashes in 12 minutes (05:15–05:27). Treat Dilemma layout as random among 4 from our side.

# Operational consequences

- Same-layout candidate/control arms: request the two 10-game batches back-to-back with nothing in between (current executor behaviour) — the only failure mode is foreign games interleaving, observed at ~3 of ~45 series boundaries in this record (~7%).
- Opposite-layout arms on all nine maps at once: interleave an odd number of games (one dev game) between the two requests.
- Fills: instead of re-rolling batches until a map matches (up to 6 batches/block today), count ids — one filler game deterministically flips every two-layout map. For Dilemma, expect E≈2 extra requests under 4-way randomness, or drop Dilemma from layout-matched fills.
- The hub now recomputes this per cycle (`tools/hub/analysis.py::layout_parity`) and flags any map whose parity match rate drops below 1.0 — that is the alarm for a server-side rule change.

**Decision fed**: fill strategy for screen blocks (both-layouts coverage at ~1 extra game per block instead of ~6 batches), and the layout-assignment field experiment (§4) is only needed for Dilemma.

**Falsifier**: any future game on the nine maps whose map_hash contradicts its id parity (the hub detector will catch it), or a demonstration that two games with the same id parity on the same map received different layouts.
