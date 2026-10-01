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

Next: 02 (queen never production-splits) and 03 (01+02) are on the panel; then an avoidance mechanism (keep the queen
beyond enemy heads' reach, sprint-aware) and Antioch's tail-shedding variant.
