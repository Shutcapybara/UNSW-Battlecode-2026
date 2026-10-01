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

## Nara (glm, P2-A)

**Era rule (my findings §1–2, `docs/findings/2026-10-01-nara-era-and-queen.md`):** the live server switched in the
1 Oct 05:54–09:23 UTC maintenance window. Tag **`post` ⟺ started_at ≥ 2026-10-01T09:00Z** (no games in the gap).
Sprint formula verified exact (`paid = steps − min(steps, ⌈L/4⌉)`, 44,825 moves, 0 violations). Round-limit
tiebreak verified on 201 rl games (0 violations): **queen = the team's original lowest-id initial robot, dead →
length 0, no inheritance**, then longest, then total. ⚠ Until `frame.py`'s winner is patched (findings §5), every
replay-derived W-L-D is wrong in queen-decided games (~5.5 % of rl games) — testers, read wins from the runner's
verdict line, not from feature extraction, on 1.2.3 panels.

**Post-era reference status: NOT stable.** My per-map post samples are 58–116 field side-games (vs ~1,500 pre).
Field medians pre→post: pearls@50 −1 %, pearls@100 +2.5 %, splits@50 −4 %, total@100 **+12 %** (retention). I will
re-derive formally when the store rebuild lands + ≥300 games/map. Until then pre-era opening targets stand (the
field has not moved); **r250+ references are stale** (retention shift + queen rule change results).

| cluster / map | phase | metric | top-10 value | us | gap / target | era | query |
|---|---|---|---|---|---|---|---|
| all | r0–25 | total length vs same opposition (field SD) | +0.11 | −0.49 (pre) | 0.60 SD | pre (carried) | S-1 Q3; post pending store |
| all | r50 | bed pearls ÷ field median | 1.07 | 0.83 (pre) | target ≥ 1.0 | pre (carried) | S-1 Q3; `tools/nara/opening_probe.py` |
| all | r0–50 | splits (births) | 14–18 | 10 (0.84×) | target ≥ 13 | pre (carried) | S-1 Q3 |
| all | r0–50 | transits (early portal use) | 5 | 2 | target ≥ 4 | pre (carried) | post value pending store rebuild |
| **round-limit maps** (Slithery, Portals, Trauma, Schooltime: rl share 100/98/91/73 %) | r490 | **queen survival** (own lowest-id initial robot alive) | 11 % today (nobody protects; Cutlery 42 %) | — | **target ≥ 0.95** for a protector build; guard: elimination-map wins flat | post | `tools/nara/queen_probe.py --since 2026-10-01T09:23` |
| round-limit maps | r490 | **queen length** | 0 (field); ≥ 8 in Cutlery's fed form | — | ≥ 1 beats every dead queen today; ≥ 8 future-proofs vs other protectors | post | same |
| round-limit maps | r490 | **queen-decided losses** (ours dead, theirs alive) | — | — | **target 0** | post | same (join index winner) |
| all | r490 | longest dragon | 40–46 (cheji/Stockfish, pre) | 25–28 (pre) | post re-derivation pending (retention +12 % suggests ≥ pre) | post-pending | TT method |
| all | r490 | round-limit losses with a material lead | 0.32–0.43 (pre) | 0.33 V06 / 0.57 hb1-12 (pre) | **target < 0.10** with queen protection (alive queen converts these) | post | `tools/tt/endgame_gate.py` |

Weighting note for gate design: at current field queen-death rates (87–98 % of sides), a protector's expected gain
is ~7–10 pp win on round-limit maps (rl share × P(opp queen dead) × P(we would lose the longest tiebreak)) — the
era's cheapest large lever. It decays as the field learns; the first mover banks the most.

