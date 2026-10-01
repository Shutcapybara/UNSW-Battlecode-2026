# Carthage (P2-T tester) — base under unswbc 1.2.3, the queen, carthage-01 (1 Oct 2026)

Host desktop, `unswbc 1.2.3`, panels from `tools/carthage/lane.py` (a copy of `tools/verso/lane.py`; D-032 gate
unchanged): pool = 8 zoo × 10 live maps × both seats, gen = 4 opponents × 31 maps × both seats, seeds 1–3 (480 + 744
games per arm). Win share from `frame.py` with the 1.2.3 ranking (queen → longest → total; patch on `r/carthage`,
equivalent to Antioch's engine-verdict patch on every game checked). Numbers are absolute and parent-relative: no
post-change references exist yet.

## Base `carthage-00-base` (hb1-14-prior-r540, D-033 `W==32 && H==16` terms off)

Golden parity: with the switch on, identical to hb1-14 on Devil (657 turns) and Trauma (9,454); off, divergent on Devil
only.

| Panel | n | win | econ~ | p50 / p100 / p150 / p250 | units@100 | total@100 | wall / self / ally body / ally h2h per 1k |
|---|---|---|---|---|---|---|---|
| pool | 480 | 0.826 | 1.139 | 1.09 / 1.14 / 1.16 / 1.17 | 1.32 | 1.20 | 6.89 / 4.62 / 1.83 / 1.86 |
| gen | 744 | 0.689 | 1.111 | 1.16 / 1.11 / 1.11 / 1.07 | 1.40 | 1.42 | 2.92 / 2.04 / 0.95 / 0.96 |

CPU probe max 10.83 M points/turn.

## The queen on the base (`tools/carthage/queen.py`)

| | pool | gen |
|---|---|---|
| games reaching r490 | 219 / 480 | 157 / 744 |
| our queen alive at r490 | 0.9 % | 0.6 % |
| — excluding the pocket maps (Slithery, Autarky, Dilemma and twins) | 1.2 % (of 168) | 0.8 % (of 127) |
| queen is the longest own dragon at r490 | 0.9 % | 0.6 % |
| opponent's queen alive at r490 | 3.2 % | 0.0 % |
| verdicts decided by the queen (won / lost) | 1 / 7 | 1 / 0 |
| median queen death round (excl. pocket maps) | 94 | 73 |
| queen death causes (excl. pocket maps) | h2h 146, wall 74, self 40, body 28 | h2h 464, wall 47, self 28, body 22 |

The queen splits a median 4 times and peaks at length 4: in this lineage it is an ordinary small forager. The pocket
maps kill it on r3–5 through the opening rescue split (Antioch H-Q3: unsavable, both teams).

## carthage-01-queen-guard (switch `queen_guard`; parent 00)

Mechanism: the queen prices its own death with +24 material (threat cost, blind-cell risk, trap-penalty scale, dive
cost, head-on strike gain). Expected: queen alive@490 up, win up, economy flat.

| | pool | gen |
|---|---|---|
| Δecon~ [5 %, 95 %] | +0.008 [−0.008, +0.027] | −0.027 [−0.046, −0.012] |
| Δwin [5 %, 95 %] | −0.020 [−0.046, +0.002] | −0.009 [−0.031, +0.013] |
| Δunits@100 / Δtotal@100 lb | −0.015 / −0.021 | −0.081 / −0.086 |
| tier-2 | all within ±3 % | all within ±3 % |
| queen alive@490 (excl. pocket) | 1.2 % → 3.6 % | 0.8 % → 8.6 % |
| median queen death (excl. pocket) | r94 → r135 | r73 → r116 |
| queen h2h deaths | 146 → 102 | 464 → 349 |
| queen-decided W/L | 3 / 7 | 10 / 0 |

Per-map pool Δecon: autarky +0.097, trophy +0.012, trauma +0.003, default −0.028, queen_of_spades −0.029, devil −0.032,
schooltime −0.055, portals −0.056 (pocket maps 0). **Verdict: REJECT** (pool econ lb ≤ 0, total@100 lb −0.021, pool win
lb −0.046, gen econ lb −0.046). Against H-Q1's falsifier: queen alive@490 0.036 on pool ≪ 0.5.

Reading: pricing delays the queen's death by ~40 rounds but does not prevent it. Head-on is the main killer and kills
both dragons whatever their lengths, so a value premium (which mostly changes contests by length) cannot stop a hunter
trading its head for ours; the queen has to stay out of enemy heads' reach. The −2 pp pool win with no economy loss is
unexplained at this point (20 better / 29 worse pairs, p = 0.25).

## carthage-02-queen-nosplit (switch `queen_nosplit`; parent 00)

Mechanism: the queen never takes a production split (`tyr_split_option`, opening production split); rescue and
escape splits kept. Expected: queen length and survival up, economy down (fewer births).

| | pool | gen |
|---|---|---|
| Δecon~ [5 %, 95 %] | −0.036 [−0.056, −0.008] | −0.317 [−0.352, −0.284] |
| Δwin [5 %, 95 %] | −0.016 [−0.047, +0.013] | −0.221 [−0.249, −0.193] |
| Δunits@100 / Δtotal@100 lb | −0.146 / −0.072 | −0.565 / −0.511 |
| queen alive@490 (excl. pocket) | 1.2 % → 13.3 % | 0.8 % → 8.7 % |
| queen length at r490 when alive | 21.1 | 21.5 |
| queen-decided W/L | **23 / 6** (base 1 / 7) | 11 / 2 |

Per-map pool Δecon: trauma +0.187, autarky −0.013, default −0.015, trophy −0.076, queen_of_spades −0.115, portals
−0.166, devil −0.168, schooltime −0.422. **Verdict: REJECT** on every economy and material guard; gen collapses.

Reading: the queen is a large share of the opening material, so taking it out of production costs births at once
(units@100 −0.47 on gen), and gen's hunters punish the thinner swarm. The tiebreak effect is real — a kept queen turned
the queen verdicts from 1–7 to 23–6 on the pool — but buying it with production is the wrong price. The queen must keep
producing (Antioch's "shed length by splitting its tail") and be kept safe some other way. 03 (01 + 02) was stopped
after 40 games and not scored.

## carthage-06-queen-avoid (switch `queen_avoid`; parent 00)

Mechanism: for the queen only, −40 for a move ending on a cell an enemy head can reach next turn, −3 per cell inside
torus distance 6 of each visible enemy head, and no head-on strikes; production splits unchanged. Expected: queen
head-on deaths down sharply, queen alive up, small economy cost.

| | pool | gen |
|---|---|---|
| Δecon~ [5 %, 95 %] | −0.017 [−0.033, +0.003] | −0.040 [−0.054, −0.016] |
| Δwin [5 %, 95 %] | −0.002 [−0.032, +0.028] | +0.013 [−0.012, +0.037] |
| Δunits@100 / Δtotal@100 lb | −0.115 / −0.107 | −0.087 / −0.110 |
| queen alive@490 (excl. pocket) | 1.2 % → 2.9 % | 0.8 % → **23.6 %** |
| queen deaths h2h / wall / body / self (excl. pocket) | 146/74/28/40 → 88/92/54/37 | 464/47/22/28 → 235/51/53/47 |
| median queen death (excl. pocket) | r94 → r136 | r73 → r152 |
| queen-decided W/L | 5 / 7 | **33 / 0** |

Per-map pool Δecon: trauma +0.018, trophy +0.012, queen_of_spades −0.021, schooltime −0.044, devil −0.048, default
−0.049, portals −0.079. **Verdict: REJECT** (pool econ lb −0.033, units/total@100 lb −0.115/−0.107, pool win lb −0.032,
gen econ lb −0.054).

Reading: distance halves the queen's head-on deaths on both panels and makes the gen queen survive a quarter of
r490 games (every queen verdict won, 33–0), at a ~2–4 % economy cost. On the pool the head-ons it saves come back as
trapped deaths (body +26, wall +18): fleeing heads pushes a length-2–4 queen into pockets and other bodies. The queen's
hazard is the ordinary small-forager hazard spread over ~100 rounds; avoiding one cause moves it to the next. The
pool's per-map numbers say the cost is concentrated on Portals and the open maps where the queen forages most.

Queen deaths on 06's pool, off the pocket maps (271): wall 92, ally h2h 52, ally body 45, self 37, enemy h2h 36,
enemy body 9 — **our own dragons kill the queen 97 times, the enemy 45**. At death the queen is length 2 in 158 and
3 in 86; 88 deaths come within 3 rounds of the queen's own production split; 138 have an ally body within 2 and no
enemy head within 3. This is what carthage-07 (the swarm yields to the queen) addresses.

## carthage-07-queen-yield (switch `queen_yield`; parent 00)

Mechanism: non-queen dragons pay 20 for ending adjacent to a visible ally queen's head (6 at distance 2); the queen pays
the same next to any visible ally head. Expected: fewer ally-caused queen deaths, economy flat.

| | pool | gen |
|---|---|---|
| Δecon~ [5 %, 95 %] | **+0.029 [+0.011, +0.052]** | −0.041 [−0.064, −0.021] |
| p50 / p100 / p150 / p250 | +0.047 / +0.043 / +0.024 / +0.000 | −0.046 / −0.044 / −0.053 / −0.020 |
| Δunits@100 / Δtotal@100 | +0.073 [+0.018] / +0.064 [+0.022] | −0.051 / −0.068 |
| Δwin [5 %, 95 %] | +0.003 [−0.025, +0.030] | −0.040 [−0.061, −0.013] |
| queen alive@490 (excl. pocket) | 1.2 % → 0.0 % | 0.8 % → 0.0 % |

**Verdict: REJECT** (pool win lb −0.025; gen econ lb −0.064). The mechanism did not touch its target: queen deaths by
cause and killer on the pool, base → 07: enemy h2h 111 → 124, wall 74 → 67, ally body 27 → 34, ally h2h 35 → 31, self
40 → 26. Its pool economy gain is a side effect in the opening (p50 +0.047): the starting dragons spread away from the
queen's spawn. It reverses on gen, so it is map-shaped, not a spacing law.

**Correction** to the 06 reading above: on the *base*, the queen's killers off the pocket maps are enemy 112, ally 62
(h2h 35, body 27), wall 74, self 40. Own dragons outnumber the enemy only after 06 removes most enemy head-ons.

Next: the sprint arms (04, 05) are on the panel; for H-Q1 the next design is a phase change rather than a premium —
the queen produces in the opening as now, then retires to a safe, low-traffic region and stays small (tail shed by
splitting) until a late regrowth window. and 03 (01+02) are on the panel; then an avoidance mechanism (keep the queen
beyond enemy heads' reach, sprint-aware) and Antioch's tail-shedding variant.
