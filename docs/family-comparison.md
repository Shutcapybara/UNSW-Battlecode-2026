# Four-family comparison: Kraken, Hydra, Leviathan, Ouroboros

2026-09-24. Method: 260-match round robin (`build/crossline-rr1`), all 13
maps, both sides, champions of each line plus fry-v14 as the field's
reference shark. Non-sandbox with replays (the five `help`-map Python
timeouts are harness wall-clock artifacts, not judge failures). Replay
examination via `tools/ouroboros/replaystats.py` (Claude's parser,
read-only) aggregated by `tools/family_report.py`
(`build/crossline-rr1/family-report.json`). Judge-CPU claims come from each
family's own sandbox runs, cited where used.

## Results

Standings (104 matches per bot, 3/1/0 scoring):

| bot | W | D | L | pts |
| --- | ---: | ---: | ---: | ---: |
| **ouroboros-v05-spread** (Claude, Python) | 89 | 0 | 15 | 267 |
| fry-v14-stateful-size-aware-3 (C++ ref) | 49 | 2 | 51 | 149 |
| kraken-v04-eval (Kimi, Python) | 47 | 0 | 54 | 141 |
| hydra-v06-echo (GLM, C++) | 36 | 2 | 64 | 110 |
| leviathan-v07-local-cache (GPT, Python) | 32 | 0 | 69 | 96 |

Head-to-head (row's wins vs column, 26 matches per pair):

| | fry-v14 | hydra-v06 | kraken-v04 | levi-v07 | ouro-v05 |
| --- | --- | --- | --- | --- | --- |
| fry-v14 | – | 13-11 | 12-13 | 18-7 | 6-20 |
| hydra-v06 | 11-13 | – | 12-13 | 10-15 | 3-23 |
| kraken-v04 | 13-12 | 13-12 | – | 17-8 | 4-22 |
| leviathan-v07 | 7-18 | 15-10 | 8-17 | – | 2-24 |
| ouroboros-v05 | 20-6 | 23-3 | 22-4 | 24-2 | – |

Replay-derived style profile (per game, 255 replays):

| bot | deaths | body | self | wall | splits | child sizes | pearls | peak units | final longest |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| ouroboros-v05 | 114.8 | 54.4 | 12.2 | **0.0** | 129 | all 2 | 1528 | 25 | **8** |
| fry-v14 | 186.2 | 49.2 | 56.0 | 18.1 | 214 | all 2 | 1859 | 27 | 4 |
| kraken-v04 | 179.1 | **100.5** | 10.0 | **29.4** | 184 | 2:110, 3:66 | 1398 | 25 | 6 |
| hydra-v06 | 168.2 | 50.5 | 49.3 | 10.6 | 188 | all 2 | 1760 | 14 | 3 |
| leviathan-v07 | 152.6 | 42.0 | 39.3 | 14.0 | 168 | all 2 | 1486 | 16 | 5 |

## Per-family assessment

### Ouroboros (Claude) — the one that is winning

**Approach.** The most chess-like design of the four (1695-line Python):
a single evaluation function in length units over enumerated candidates
(moves, sprints, strikes, splits), with a *probabilistic* threat model
(`p_strike1/2/3` — an enemy 1 step away takes a trade with p=0.75, not 1.0),
tunnel/doom memory with 200-round persistence, exit counting (0/1 free
neighbour penalties), crowding/traffic terms, reverse-BFS goal distances,
and phase-scheduled role mixes (early 45/25/30 gather/hunt/scout → late
70/30/0) with a crown elected from round 200 that stops splitting.
`params.py` override mechanism; `gc.disable()` for judge points.

**What the replays say.** Zero wall deaths across 104 games — the doom/
tunnel model works. Lowest deaths per game (114.8 vs kraken's 179.1) while
still splitting 129 times. The deep dive (0092, default) is the signature
win: peaks at 33 units, feeds the mid-game trade war at roughly even
exchange (h2h 6/16/10 up/even/down), then converts — longest dragon 21 at
round 500 while kraken was ground down to 2 units / 14 total length. It
wins the attrition war *and* the length race.

**Criticism.** 89 wins came non-sandbox; the design is the heaviest Python
of the four (probabilistic threat + doom search + reverse BFS per turn) and
their own promotion gate (sandbox p99 < 60M) had to be engineered down to —
if the meter ever bites, it bites here. The role-mix fractions are
hand-tuned constants with no opponent adaptation; fry-v14 still takes 6
games off it, all on maps where pure swarm density beats finesse
(Colloseum tax applies to everyone). And the crown-from-round-200 rule is
fragile to misidentification: `crown_memory=40` rounds of staleness means a
dead crown can haunt target allocation for 40 rounds.

**Useful claims to trust.** The threat model's core insight — *model enemy
aggression probabilistically, not adversarially* — is validated by the
wall-death and body-death gap. Kraken's hard 2-step reservation
double-counts risk and still dies more.

### Kraken (Kimi) — mine

**Approach.** Role-at-birth encoded in split size (2=scout, 3=hunter,
larger=gatherer), capped BFS compass for targets, weighted-sum move eval,
sonar gossip with relay TTL, brawl mode on small poor maps, big-map
production targets. Judge-hardened: worst sandbox max 96.0M over 520
matches, zero over-budget turns.

**What the replays say.** The damning number is **100.5 body-crash deaths
per game — 56% of all deaths** — against ouroboros's 54.4 with similar
unit volume. Plus 29.4 wall deaths (ouroboros: 0). Kraken's danger map
marks tiles but its pathing doesn't model *where bodies will be*, and it
has no tunnel/doom concept at all. Median final units of 3 (vs peak 25)
shows teams getting ground to stubs even in games kraken wins. The
role-size encoding costs material: hunters are born at length 3 into a
pool where everyone else fights at 2-4, and the 66 three-segment children
per game are 50% more expensive than everyone else's 2-segment children
for no measured combat benefit (head-to-head is symmetric).

**Criticism.** The strategy layer is sound (beats fry-v14, hydra-v06,
leviathan; 325W-192L full pool) but the tactics leak: danger is binary
(lethal/soft) where ouroboros prices it probabilistically; escape/space
checks are per-move flood fills where ouroboros tracks corridor doom
persistently. The gossip protocol is the best of the four Python bots
(relay TTL, bed predictions, portal pairing) but the information barely
changes outcomes — sightings feed a compass bias, not a coordinated hunt.
Hydra-v06's pack hunting shows what the same channel can do.

### Hydra (GLM) — two different bots sharing a name

**Approach.** The Python line (v01-v03) pioneered the ideas everyone
copied: roles, gossip map, swarm-of-equals (cap size 4, split constantly),
and the crown insight (freeze at 340, elect a non-splitting grower). The
C++ line (v06-echo onward) forked hunter-v03 onto protocol 3: 4-direction
status sonar, enemy sightings gossiped on two slots for pack hunting,
echo-radar stalker detection. v07-v10 are matchup experiments against
fry-v14 (farm-first, claims, lanchester, farmclean — none promoted).

**What the replays say.** Lowest peak units (14) and lowest median final
longest (3) of the field: hydra-v06 neither wins the numbers war nor
banks a crown. It beats leviathan on grit (pack hunting works: 10-15 is
still a loss, but leviathan beats fry-v14 nowhere) but loses to everything
else. Its h2h profile (57.5/game) with only 14 peak units means its small
pack is constantly trading — by design (gossip-chased pack kills), but the
economy doesn't replace the losses.

**Criticism.** The C++ fork bought CPU headroom it didn't need (Python
hydra was already judge-safe) and paid for it in iteration speed: v07-v10
are all small patches to hunter.cpp, none promoted, while ouroboros lapped
the field with Python. The pack-hunting gossip is excellent; the grower
underneath is still hunter-v03's, and the endgame freeze means hydra
deliberately stops competing for the numbers war it was already losing.
Split identity crisis: the Python line's swarm-of-equals insight (which
beats size-gated attackers) was abandoned exactly when it was winning the
argument.

**Useful claims to trust.** "Gossip is only trusted for 15 rounds, and
only chased within 6 path steps: far chases starve" — matches kraken's
own finding that far hunts starve. The v10 lesson (a locally-sensible
flee term becoming a map-wide reflex when applied swarm-wide) is a general
warning about global reflexes from local terms.

### Leviathan (GPT) — the methodologist

**Approach.** The smallest codebase (330-line main.py + a 17-key weights
dict): bounded enumeration of moves/sprints/trades/splits scored by
sum(weight × feature), with the field's best *accounting* — material is
net length change (three pearls in three steps = one net segment, not
three), trades are priced with a unit-loss cost scaled by 1/units, stale
pearls can be targets but cannot fund sprints. Dynamic roles from local
state rather than birth assignment. Sonar self-reports are decoded and
stored but deliberately unused ("infrastructure only").

**What the replays say.** Lowest split count (168/game) and lowest peak
units of the Python bots (16): it consistently under-produces, then loses
attrition wars (69 losses, worst of the field). But the deaths are clean
(42 body, 39 self, 14 wall — best ratios among the losers), the sandbox
margin is real (v07 worst 83.6M vs kraken's 96.0M), and it beats
hydra-v06 15-10. Their RESULTS.md is the most honest empirical record of
the four: equivalence testing (v07's action stream identical to v06 in 32
native cases), regression tests, explicit "these are deterministic
map/side cases, not a ladder rating" caveats.

**Criticism.** Discipline outran ambition: seven versions of careful
measurement produced a bot that loses to everything except hydra. The
17-weight evaluator is too coarse to express what ouroboros's 60+
parameters express (no phase schedule, no crown, no corridor model, no
coordination), and "teammate reports decoded but unused" leaves the
multiplayer dimension on the table. The measured 4-4 vs kraken-v03 came
on 4 maps; on 13 maps it's 8-17. Method is their product; the bot isn't
yet.

## Cross-cutting lessons

1. **Everyone converged on the same architecture** (world model →
   candidate generation → weighted eval → argmax, roles as weight slices,
   parameters swept by tooling). The winner is decided by *feature depth*
   (ouroboros's probabilistic threat + doom memory + exit counting) and by
   respecting the two-game structure (swarm war → crown race).
2. **2-segment children are the meta.** Everyone but kraken splits
   exclusively at 2; kraken's 3-segment hunters pay 50% more per unit for
   a role label that gossip could carry for free.
3. **Python is fast enough if you engineer the meter** (kraken 96M worst,
   ouroboros promotes at p99<60M, leviathan 83.6M worst). C++ bought hydra
   headroom it didn't spend and cost it iteration speed.
4. **Wall/self deaths are solved problems** (ouroboros 0.0 wall/game via
   persistent doom memory); kraken's 29.4 wall deaths/game is pure
   addressable loss.
5. **The benchmark that matters** is fry-v14 plus the other families'
   champions on all 13 maps both sides — single-map deterministic results
   are exact for the matchup and meaningless for the field (leviathan's
   4-4 vs kraken on 4 maps became 8-17 on 13).

## What kraken-v05 should steal

- From ouroboros: probabilistic strike model (replace binary danger),
  persistent corridor-doom memory, exit-count terms, crown from mid-game.
- From hydra: gossip-chased pack hunting with a 6-step chase horizon.
- From leviathan: material accounting (net length, not gross pearls) and
  the discipline of an action-stream equivalence check before promotion.
- Drop: size-encoded roles (use 2-segment children, role via gossip
  hand-off — ouroboros proves the parent's back-ray lands on the newborn).
"""
