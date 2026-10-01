# TT — the top teams: cheji bt (team 70) and Stockfish (team 206)

Request (user, 30 Sep 2026): an HB-1-style analysis of the two top teams. Branch `r/tt` (from `r/hb1`). Method and
tools are HB-1's (`docs/findings/2026-09-30-hb1-heartbreaker.md`, `tools/hb1/`, now parameterised by
`HB_TEAM` / `HB_BUILD` / `HB_TAG`), plus `tools/tt/`. Running log with every table: `claude/tt-status.md`. Raw rows:
`game_stats/runs/tt*`.

## Headline

1. **The top teams' edge over Heartbreaker is the endgame conversion, not the swarm.** All three run the same swarm
   economy to ~r200. cheji bt and Stockfish then dissolve the swarm into one long dragon (longest 40 and 46 at r490,
   37–46 % of their material in it) and win 75 % / 72 % of round-limit games; Heartbreaker never converts (longest
   13, 10 %, 26 %).
2. **They convert by deliberately killing their own small dragons** (~1 % of turns; Heartbreaker: never). cheji bt: an
   invalid command, a timed mass cull — from ~r330 each small dragon dies with ~10 % per turn. Stockfish: a backward
   step into its own neck, from r250 at ~2 % per turn, weighted toward small dragons next to an ally head.
3. **They are harder to copy from the local view.** Command-level GBT accuracy: Heartbreaker 0.826, Stockfish 0.763,
   cheji bt 0.741. cheji bt's split gate is not a rule (0.829 vs Heartbreaker's 0.975); Stockfish's production is
   rule-like with round thresholds at ~250 and ~350 (hand-written phase logic).
4. **Our bots have the tactic and run it late.** Ares's feeder (within 4 cells of the elected crown, step backward
   into the neck) activates from ~r400–430, 100–150 rounds after the top teams; Ares ends at longest 25, hb1-12 at
   28.5 with 57 % of its round-limit losses despite a material lead.
5. **Moving Ares's feeding earlier fixes the conversion and does not pay on any local measure.** tt-01 (from ~r300)
   cuts round-limit losses with a material lead from 57 % to 20 % and loses 3 games net on the z1 panel (fewer
   elimination wins); tt-02 (from ~r250) over-converts (−5.0 pp). No local opponent converts early, so the value of
   the top teams' timing against teams that do is not measurable locally.

## Data

Mac corpus, synced 30 Sep: cheji bt 4,126 completed games (25 Sep 18:20 – 30 Sep 11:57 UTC, 116 opponents),
Stockfish 1,932 (26 Sep 22:12 – 30 Sep 12:11, 71 opponents), 105 shared. All extracted to v5 rows, 0 errors. No
submission ids. Ladder 30 Sep 12:11 UTC: cheji bt #1 (2096), Stockfish #4 (2079; #2–#4 within 2 Elo). Win rates in
the corpus 0.806 and 0.692; head-to-head cheji bt 69–36. cheji bt's weakest map (Slithery Fight 0.62) is Stockfish's
best (0.79). Held-out = 20 % of each team's games (by game, seed 62); map-identifying columns excluded.

## Q1 — structure (GBT held-out; tree depth 4 in brackets)

| decision | Heartbreaker | cheji bt | Stockfish |
|---|---:|---:|---:|
| split gate | 0.975 (0.952) | 0.829 (0.779) | 0.934 (0.872) |
| direction | 0.829 (0.685) | 0.751 (0.638) | 0.771 (0.664) |
| child size | 0.957 (0.918) | 0.911 (0.858) | 0.980 (0.871) |
| sonar mask | 0.981 (0.937) | 0.983 (0.950) | 0.971 (0.925) |
| late gate (r ≥ 350, len ≥ 8) | 0.9994 | 0.983 | 0.979 |
| whole command | 0.826 | 0.741 | 0.763 |

- Direction is driven by candidate features for all three (drop-family −11 to −14 pp); the two top teams leave about a
  quarter of moves undetermined by the local view (Heartbreaker a sixth). Calibration: near-certain moves 28 % /
  17 % / 21 %, near-ties 13 % / 22 % / 18 % (Heartbreaker / cheji bt / Stockfish), all calibrated (ECE ≤ 0.022).
- cheji bt splits on 27.5 % of eligible turns (Heartbreaker 9.7 %), with no simple rule; child sizes are more varied
  (many 8+ children). Stockfish's gate tree: no exit → split; in the open, split after eating at length ≤ 4, with
  branches at rounds ~250 and ~350. Stockfish also emits single-direction sonar rays, which neither other team does.
- Memory beyond the current view (action history + decayed spatial trail; 400-game subset per team): direction
  +0.97 pp for cheji bt (0.7448 → 0.7545, mostly its own-position trail), +0.39 pp for Stockfish, +0.19 pp for
  Heartbreaker; the split gate gains nothing. Memory does not close the gap: a quarter of their moves stay
  undetermined by the current view plus simple memory of it.

## Q2 — behaviour around blocked states (all games)

| state | Heartbreaker | cheji bt | Stockfish |
|---|---|---|---|
| trapped, split legal | split 99.9 % | split 98 % | split 98 % |
| trapped, split not legal | step into a wall or an ally head (all die; ally head-on kills the ally) | **self-kill in place 97 %** | wall 56 %, backward into own neck 27 %, ally cell 15 % |
| free exit, split not legal | never self-kills | self-kill 0.5 % (cull) | backward self-kill ~0.5 % (cull) |
| invalid splits | 0 / 186,440 | 0 / 694,397 | 0 / 547,677 |

The Heartbreaker-measured wrapper slightly lowers command accuracy for both top teams: wrapper rules are
team-specific. (Tool fix: HB-1's enumeration and `wrapper.label()` assumed non-move = split; self-kill is now its own
class. Heartbreaker's results are unaffected.)

## Q3 — stability

Both policies are static over their well-sampled spans (within / forward / backward transfer within ~1 pp for every
decision; change-points only where the corpus density changes). cheji bt: a possible split-size change on 30 Sep
06:00–12:00 UTC (one window, 308 games, flagged only). Stockfish's rating rose ~100 Elo (1980 → 2079) while its five
per-turn decisions stayed the same.

## The conversion

Medians over running games, dragons / longest / total length:

| round | Heartbreaker | cheji bt | Stockfish | Ares V06 (z1 panel) | hb1-12 (z1 panel) | tt-01 (z1 panel) |
|---:|---|---|---|---|---|---|
| 200 | 25 / 9 / 78 | 40 / 4 / 95 | 40 / 5 / 100 | 29 / 4 / 69 | 36 / 4 / 87 | 36 / 4 / 84 |
| 300 | 28 / 10 / 98 | 51 / 5 / 123 | 35 / 15 / 100 | 30 / 5.5 / 75 | 45 / 6 / 112 | 44 / 5 / 107 |
| 400 | 27 / 11 / 109 | 8 / 25 / 86 | 21 / 32 / 105 | 26 / 9 / 88 | 45 / 9 / 133 | 15 / 22 / 88 |
| 490 | 27 / 13 / 124 | 4 / 40 / 77 | 11.5 / 46 / 100 | 5 / 25 / 63 | 8 / 28.5 / 91 | 4 / 33 / 69.5 |

(Teams vs the live ladder, our bots vs the zoo panel: timing comparable, levels not.)

The cull decision (turns at length ≤ 3; GBT AUC 0.991 cheji bt, 0.975 Stockfish): rate by round — cheji bt < 1.1 % to
r300, 2.5 % r300–350, 9.4–10.5 % from r350; Stockfish 0.4–0.5 % to r250, 1.8–2.5 % after. By distance to the nearest
ally head — cheji bt 3.7 % adjacent, ~1 % beyond; Stockfish 2.9 % adjacent, 1.2 % at 2, 0.6 % at 4, ≤ 0.2 % beyond 5.

## Ports onto hb1-12 (Ares V06 + Heartbreaker's direction prior)

| version | one change | z1 W–L (hb1-12: 139–21) | gate | round-limit win rate | limit losses with a material lead | longest r490 |
|---|---|---|---|---:|---:|---:|
| tt-01-feed300 | `feed_base` 40 → 140 (feeding from ~r300) | 136–24 | fail (−1.88 pp; own body +37 %) | 0.80 (0.78) | 20 % (57 %) | 33 (28.5) |
| tt-02-feed250 | `feed_base` 190 (from ~r250) | 131–29 | fail (−5.00 pp; own body +49 %) | 0.74 | 24 % | 34.5 |

Head-to-heads, ten live maps, 40 fixed fixtures: hb1-12 vs the Heartbreaker mimic 33/40; tt-01 vs the mimic 29/40
(paired: 4 W→L, 0 L→W); tt-01 vs hb1-12 19/40.

- Earlier feeding does what it is meant to (cheji bt's schedule reproduced; material no longer wasted at the round
  limit) and costs elimination wins against opponents that can be eliminated or that never convert.
- r250 is too early for Ares: Stockfish's feed is slow and proximity-weighted; Ares's is all-or-nothing near the
  crown, so the start round without the rate over-converts.
- Two notes on the gate for this kind of change: the economy mean uses pearls to r250, so a conversion change cannot
  move it; and the own-body hygiene rate counts feeder suicides, so it penalises deliberate feeding by construction.

## Follow-up (1 Oct): the upload limit, the cull target, and three more ports

- **Upload limit.** The upload zip is capped at 4 MiB; hb1-12 zips to 17.1 MiB. `hb1-14-prior-r540` (same prior,
  540 rounds, 3.74 MiB) scores 141–19 on the z1 panel vs Ares V06 (hb1-12: 139–21) and is the uploadable base.
- **Which ally a small dragon dies next to** (`tools/tt/cull_target.py`): cheji bt after r330 — 6 % beside an ally
  of visible length 1–2, 24 % at 3–4, 45 % at 5–6, 57 % at 7–9, 74 % at 10–14, 82 % at 15+, 4 % with no ally in view.
  Stockfish after r250 — 3.6 % rising to 11.7 %. **This corrects the "timed mass cull" reading above**: cheji bt feeds
  the long dragon; its ~10 %/turn is an average.
- **Ports on hb1-14** (z1 seed 1, parent 141–19, longest 27 at r490):

| version | mechanism | W–L | longest r490 | round-limit W/L | verdict |
|---|---|---|---:|---|---|
| tt-03-proxfeed | flat 3 % beside any longer ally from r250 | 137–23 | 28 | 59–18 | fail; no concentration |
| tt-04-feedlong | cheji bt's rate table from r330 | 136–24 | 27 | 60–17 | fail; dragons die, the long one does not eat them |
| **tt-05-feed300-up** | Ares's own feeders from ~r300 (tt-01's change, uploadable) | **141–19** | **32** | **67–13** | level with the parent; gate fails only on own-body deaths (the mechanism) |

- A donor's cull rule does not transfer without the donor's harvesting behaviour (tt-04), as its split gate did not
  (hb1-11). Ares's own co-designed crown + feeder logic, started on the top teams' schedule, does concentrate.
- hb1-14's 160 panel games: 62 of 79 elimination wins end before r300; a late elimination is predicted by the
  opponent's unit count (≤ 5 at r300: 14 of 17), not by our own. No zoo opponent converts like the top teams (their
  longest in round-limit games 5–24.5; ours 24.5–33.5; cheji bt 40, Stockfish 46).

## Follow-up (1 Oct): the next two teams — Cache me outside (#1) and forgot to mention (#2)

Ladder 30 Sep 17:15 UTC. **Dummy-bot check first** (some teams hide their bot when ranked scrims are not forced):
a GBT trained on 70 % of a team's ranked games scores its held-out ranked vs its unranked games
(`tools/tt/dummy_policy.py`). forgot to mention: equal (gate 0.963 / 0.969, direction 0.729 / 0.725, all windows) —
same bot, all 2,792 games used. Cache me outside: gate equal, direction 0.763 / 0.741, ranked ahead in 7 of 8 windows —
not a dummy but a variant in unranked play, so **distilled from its 598 ranked games only**. cheji bt and Stockfish
pass the behavioural check (ranked and unranked fingerprints match), so their earlier analyses stand.

| GBT held-out | Heartbreaker | cheji bt | Stockfish | forgot to mention | Cache me outside (ranked) |
|---|---:|---:|---:|---:|---:|
| split gate | 0.975 | 0.829 | 0.934 | 0.975 | 0.970 |
| direction (tree depth 4) | 0.829 (0.685) | 0.751 (0.638) | 0.771 (0.664) | 0.735 (0.631) | 0.758 (0.584) |
| child size | 0.957 | 0.911 | 0.980 | 0.988 | 0.997 |
| sonar mask | 0.981 | 0.983 | 0.971 | 0.964 | 0.928 |
| whole command | 0.826 | 0.741 | 0.763 | 0.741 | 0.765 |
| split rate (eligible turns) | 10 % | 28 % | 20 % | 31 % | 42 % |

- forgot to mention: rule-driven aggressive production (split whenever it has just eaten, units ≤ 61, until ~r350);
  the hardest steering (0.735, 25 % near-ties); the most self-kills (~2.3 % of turns, by invalid command; it chooses
  death over a legal split 30 % of the time when trapped).
- Cache me outside: chain-splitting (split again within 4 turns of a split); the largest tree→GBT steering gap of any
  team (+17 pp — the strongest candidate for a learned direction policy); state-dependent sonar unlike any other team
  (most common pattern only 28 % of turns) — likely real communication; Elo 1842 → 2096 over the span.
- **Conversion, all four top teams:** longest at r490 40 / 46 / 36 / 35 (Heartbreaker 13); all four cull small
  dragons and **feed the long one** — cull rate beside an ally of length 15+ vs 1–2: cheji bt 82 vs 6 %, Stockfish 11.7
  vs 3.6 %, forgot to mention 37 vs 6.3 %, Cache me outside 21 vs 7.5 %.

## Follow-up (1 Oct): mimics and priors for forgot to mention and Cache me outside

Built on hb1-04's chassis (`tools/tt/make_mimic.py`) with a learned cull model run first, die-in-place when trapped,
and each team's scaled direction GBT (compact parity exact on 20,000 held-out rows). Cache me outside uses ranked
games only.

| bot | what | fidelity (40 held-out games): command / direction / self-kill recall | z1 vs Ares V06 (122–38) | gate |
|---|---|---|---:|---|
| tt-08-ftm-mimic | forgot to mention mimic (local) | 0.761 / 0.755 / 0.90 | 91–69 | fail (economy +0.08) |
| tt-09-prior-ftm | hb1-14 + ftm direction (uploadable 3.74 MiB) | — | 117–43 | fail |
| tt-10-cmo-mimic | Cache me outside mimic (local) | 0.806 / 0.804 / 0.80 | 78–82 | fail (economy **+0.24**) |
| tt-11-prior-cmo | hb1-14 + cmo direction (uploadable 3.73 MiB) | — | 127–33 | hold |
| hb1-14-prior-r540 | reference: Heartbreaker direction | — | 141–19 | hold |

- **The mimics have the economy but not the conversion.** Median longest dragon at r490 is 10–12.5 for the mimics
  against 35–36 for the real teams; 71–79 % of the mimics' round-limit losses come with a material lead. The cull
  model reproduces *when* a dragon dies (recall 0.80–0.90), but whom it feeds is a team-level choice that the local
  view does not show. Ares' crown rule supplies it, which is why the Ares-based priors win 63–72 % of round-limit
  games.
- **Heartbreaker's steering remains the best prior for Ares.** Cache me outside's is level with V06 (+3 pp); forgot
  to mention's is slightly worse.
- **Next if pursued:** a mimic with the swarm plus Ares' crown election for conversion. This would combine tt-10's
  economy (+0.24) with a written conversion rule. The C++ map-memory features would add about 1 pp of direction.

## Follow-up (1 Oct): per-map specialists, and a map-regime selector

**Who is a specialist where** (`tools/tt/map_specialists.py`; Bradley-Terry over 25,124 ranked ladder games, team
strength + per-map side advantage; residual = actual − expected win rate on the map, pp; * = beyond 2 SE). The all-games
fit (64,594 games) agrees on every large effect.

| team | strong on | weak on |
|---|---|---|
| Heartbreaker | Trophy +29*, Queen of Spades +27*, Autarky +11*, Dilemma +8* | Portals −37*, Slithery −36*, Schooltime −24*, Trauma −11* |
| cheji bt | Queen of Spades +25*, Schooltime +15* | Autarky −24*, Slithery −11* |
| Stockfish | Portals +23*, Schooltime +20* | Dilemma −24*, Devil −22*, Autarky −16* |
| forgot to mention | Autarky +24*, Queen of Spades +14* | Schooltime −17*, Portals −14* |
| Cache me outside | Trauma +26*, Default +23* | Schooltime −23*, Slithery −18* |
| us (7) | Schooltime +32*, Portals +18 | Dilemma −25, Trauma −20*, Autarky −12 |

**Why** (`tools/tt/map_mechanism.py`, each team's replays by map). The maps split by how games end:
- *Elimination maps* (Trophy, Devil, Queen of Spades, Dilemma, Default, Autarky; all ≤ 1,024 tiles): the top teams
  win 45–96 % of games by elimination. Heartbreaker and forgot to mention, early swarmers (2–6× the opponent's units
  at r100), win here.
- *Round-limit maps* (Portals and Slithery 0–2 % eliminations, Trauma 3–21 %, Schooltime mixed; Schooltime 2,400,
  Slithery 1,701 and Trauma 1,152 tiles; Portals has 20 portal pairs on 512 tiles): the longest dragon at r500
  decides. Stockfish ends with a longest dragon of 49–64 against 30–42 and wins. Heartbreaker's longest is 11–19
  against 24–28, and it loses 82–84 % of games on Slithery and Portals.
- The specialists lose the other regime in the matching way. Stockfish is *eliminated* in 41–48 % of games on Devil
  and Dilemma, with 11 units at r100 against Heartbreaker's 13–20. cheji bt is the only team strong in both regimes,
  through both an early swarm and an elected crown (Schooltime: total 256, longest 58).

**Locally** (`tools/tt/local_map_table.py`, z1 panel, 16 games per map per seed): our mimics reproduce their team's
regime profile — hb1-04 (Heartbreaker) wins 77 % on elimination maps vs 31 % on round-limit maps; tt-08 (forgot to
mention) 79 vs 23 %; tt-10 (Cache me outside) 67 vs 22 %. Ares V06 is flat (77 / 76 %). Heartbreaker's direction
prior lifts Ares mostly on elimination maps (hb1-14: 93 / 81 %). On round-limit maps every loss is at the round limit,
often with a material lead: V06 12 of 31, hb1-17 5 of 9, tt-05 (feeding from ~r300) only 1 of 9.

**Prior-weight sweep** (hb1-14 with λ for Heartbreaker's direction prior; z1 seed 1, vs V06 122–38):
λ 0.5 → 129–31 (fail), 1.0 → 141–19 (hold), **2.0 → 144–16 (pass**; economy +0.11, win share +13.8 pp; uploadable
3.74 MiB: `hb1-17-prior-lam20`), 4.0 → 140–20 (pass).

**Selector** (`tools/tt/make_regime.py`; no map names): hb1-17 with tt-05's earlier feeding onset only when the
dragon's own information says round-limit regime — W·H ≥ 1,100 (known at init), or ≥ 4 portal edges per 100 seen
cells (Portals 7.8; elimination maps ≤ 2.3). `hb1-19-regime-feed140` (tt-05's onset) and `hb1-20-regime-feed200`
(earlier still); both uploadable.

| bot | rule | z1 s1 | z1 s2 | total |
|---|---|---:|---:|---:|
| hb1-17 | — | 144–16 | 139–21 | 283–37 |
| hb1-19 | onset 140 if W·H ≥ 1100 or ≥ 4 portal edges/100 seen cells | 142–18 | 141–19 | 283–37 |
| hb1-20 | same, onset 200 | 135–25 | 132–28 | 267–53 |
| **hb1-21** | onset 140 if ≥ 5 portal edges/100 seen cells (no size rule) | **147–13** | **140–20** | **287–33** |

Size was the wrong switch. Ares' onset already moves earlier with W + H, so on large maps the earlier onset only cost
games (Schooltime 27 → 24 of 32). The small portal-dense map was the gap: Ares fed late there, yet games still run to
r500. hb1-21 against hb1-17 with the endgame gate (`tools/tt/endgame_gate.py`; 448 paired fixtures, z1 seeds 1–2
plus Portals seeds 1–10):
- **Portals +8.75 pp, 95 % CI [+0.6, +16.9]** (141 vs 127 of 160). Conversion failures (round-limit losses with a
  material lead) fall from 23 to 1, and the longest dragon at the end rises from 30 to 36.
- Elimination maps are identical. Devil, Dilemma, Queen of Spades and Trophy are bit-identical; on Default and Autarky
  the rule fires now and then, changing game lengths but no results.
- Overall +2.9 pp [0.0, +6.0] → INCONCLUSIVE by the gate's rule (lower bound must be above 0). More Schooltime and
  Default seeds are queued, the two maps where the rule sometimes fires.

**Why an endgame gate.** The scorecard gate is the older BENCHMARKS step-4 rule, and it misjudges late-game changes:
- Its economy term is measured up to r250, so a change acting from r300 can at best "hold".
- Its hygiene term counts chosen deaths (culls) as failures, which BENCHMARKS' 30 Sep revision says not to do.
- Its win share is unpaired and from one seed.

Tempo covers r10–150 by design. The endgame gate pairs fixtures (seed, map, opponent, seat) so the opening is shared.
It reports the win difference with a bootstrap CI overall, per regime (elimination / round-limit maps) and per map,
plus per-arm round-limit record, elimination losses, conversion failures and longest at the end. Its verdicts use the
tempo vocabulary (ACCEPT / REJECT / NO GAIN / INCONCLUSIVE). It is proposed alongside tempo, not as a replacement:
- tempo for opening changes;
- this gate for changes that act after ~r150;
- the scorecard tables for diagnosis.

**Cross-reference: the s1 lane's findings** (`docs/findings/2026-10-01-s1-next-steps.md`, Mac checkout):
- The s1 lane grafted Ares onto the Heartbreaker mimic (hb1-04) and found **r150 the best hand-over**: 0.64 → 0.84,
  tying hb1-12. r250 gave 0.79 and r350 0.78.
- The lane traced the mimic's losses to the missing crown: longest dragon 12 vs 24 on Portals, Slithery, Default and
  Schooltime. That is the same conversion gap found here.
- My Cache me outside hand-offs used r250–350 only. r150 hand-offs for both new mimics (tt-16 Cache me outside, tt-17
  forgot to mention) are queued.
- Its split-stall result is the mid-game counterpart of the regime story. The top ten split 52 % of eligible turns
  (ours 75–95 %), and hold length while food is near.

## Follow-up (1 Oct, evening): hb1-24, the selector that passes

Iterations on the portal rule (all hb1-17 plus tt-05's feeding onset when the rule fires; paired endgame gate):

| bot | rule | Portals vs hb1-17 | Default | verdict |
|---|---|---|---|---|
| hb1-21 | ≥ 5 portal edges per 100 *seen* cells | +8.75 pp [+0.6, +16.9] | rule fires in 46 of 160 games (local portal clusters), −1.25 pp n.s. | INCONCLUSIVE overall (+1.7 [−0.4, +3.8]) |
| hb1-22 | ≥ 6 per 100 seen, ≥ 150 seen | −1.9 pp (gain lost) | still fires | — |
| hb1-23 | ≥ 4 per 100 *map* cells | +1.25 pp (gain lost) | never fires | NO GAIN vs hb1-21 |
| **hb1-24** | hb1-21's rule, only when W + H ≤ 56 | **+8.75 pp [+0.6, +16.9]** | never fires | **ACCEPT** |

- Why hb1-23 failed: each dragon is its own process with its own map, and a child starts with nothing. A dragon born
  at r250 never sees enough of the map for an area-normalised count to cross the threshold. A density over the cells
  it has seen works for young dragons.
- Why the W + H gate is principled rather than a map list: Ares' onset is `500 − feed_base − 0.6·(W + H)`, so it is
  already early on large maps (the size-based rule in hb1-19 hurt Schooltime). The earlier onset is only missing where
  the map is small *and* elimination is blocked by portals.
- **hb1-24 vs hb1-17** (z1 seeds 1–2, plus Portals, Default and Schooltime seeds 1–10; 704 paired fixtures):
  - overall **+2.0 pp [+0.14, +3.84]**;
  - round-limit maps +3.65 pp [+0.5, +7.0]; elimination maps identical (0 of 320 games changed);
  - Portals conversion failures 23 → 1, and the longest dragon at the end rises from 30 to 36.

  z1 scorecards are 147–13 and 141–19 (pass, pass); hb1-17 got 144–16 and 139–21. The bot is deterministic: hb1-24
  reproduces hb1-21 game for game on Portals and hb1-17 everywhere else. Uploadable (3.74 MiB).
- **Upload candidate: `hb1-24-portal-small`.** The open question is the ladder. The local zoo has no strong converting
  opponent, and the effect is per-map, so a live check would compare Portals games before and after.

## What to take, and what is open

- **Conditional conversion, not a fixed earlier round.** Keep the swarm while elimination is on; convert on the top
  teams' schedule when it is not. The measured ingredients: a rate schedule (cheji bt ~10 %/turn from ~r330,
  Stockfish ~2 %/turn from r250) rather than an instant feed; feeding toward any adjacent longer ally (Stockfish) as
  well as toward an elected crown.
- **Die in place when trapped** (cheji bt) instead of stepping into an ally.
- **Not worth a mimic.** A local-view copy of either team would match ~0.74–0.76 of commands; Heartbreaker at 0.83
  gave a mimic at half strength. Their strength is in decisions that depend on more than the local view, and in the
  conversion, which is a rule we can write.
- **Open, not measurable locally:** whether matching their conversion timing wins against teams that convert. It needs
  games against such teams. Two uploadable bots exist for that comparison: `hb1-14-prior-r540` (late conversion) and
  `tt-05-feed300-up` (from ~r300), level with each other on the zoo panel.

## Ledger rows touched and proposed weights

| row | current | proposed | evidence |
|---|---:|---:|---|
| L03 (H10) phase bifurcation → phase-conditional logic keyed on state | 0.5 | **0.6** | Both top teams run an explicit phase switch (swarm → conversion), Stockfish with round thresholds; a fixed earlier round on our bot fails, pointing to state-keyed conversion rather than a clock. |
| L27 learned decision functions | 0.7 (HB-1 proposal) | 0.7 (unchanged) | The cull decision is learnable (AUC 0.975–0.991) but is better written as a rule; the top teams' steering is less learnable than Heartbreaker's. |
| new: endgame conversion timing/rate is where the top two differ from the rank-40 swarm | — | 0.8 | Trajectories over 4,126 + 1,932 + 817 games; round-limit win rate 0.75 / 0.72 vs 0.26. |
| new: converting earlier pays against opponents that also convert | — | 0.5 | Not measurable locally (tt-01 even vs hb1-12, worse vs non-converting opponents); needs ladder games. |
