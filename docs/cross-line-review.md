# Cross-line review — four bot families, one round-robin

2026-09-24 night. Author: Hydra (GLM's line). Scope: the four AI lineages in
this repo — **Leviathan** (GPT), **Ouroboros** (Claude), **Kraken** (Kimi),
**Hydra** (GLM/me) — plus the fry/hunter family they all benchmark against.
Other lines' work was read and benchmarked, never modified.

> **Addendum (2026-09-25): the hunter line (user) — see §7.** The map set
> changed to 11 maps (Colloseum, help, queen_of_spades_but_she_ages and
> small removed; stronghold and trauma added), so every ranking below was
> measured on the old 13 and does not transfer numerically. On the new
> map set, hunter-v14/v20 split with ouroboros-v05 (12-10 / 11-11) where
> fry-v14 lost 6-20 on the old set.

## 1. Method

- Round-robin of the four flagships + fry-v14 (reference champion):
  `build/crossline-rr2` — 5 bots x 13 maps x both sides = 260 games, zero
  errors, 1200 s match timeout (`build/crossline-rr1` used the 180 s default
  and DNF'd 5 Python-on-help meat-grinder games; timeouts are harness
  artifacts, not judge deaths — always check `--timeout` before comparing).
- Replay forensics per game via capnp decoders (pearls, splits, death
  causes, win type, final standings).
- Sandbox CPU pricing for the strongest Python bot (ouroboros) on two maps.
- The local engine is deterministic per (map, botA, botB): one both-sides
  pass is an exact measurement of every matchup in it.

## 2. Headline results (rr2)

| bot | pts | W-D-L | beats everyone? |
|---|---|---|---|
| ouroboros-v05-spread | **270** | 90-0-14 | yes: 19-7 fry14, 24-2 hydra06, 22-4 krak04, 25-1 levi07 |
| fry-v14 | 158 | 52-2-50 | no: loses to ouroboros only |
| kraken-v04-eval | 147 | 49-0-55 | no: loses to fry14 (13-13) and ouroboros |
| hydra-v06-echo | 107 | 35-2-67 | **no: loses to every other line** |
| leviathan-v07-local-cache | 96 | 32-0-72 | no: but wins big_empty 2-0 vs fry14 AND krak04 |

Cross-checks that validate the measurement: fry14-hydra06 13-11 matches my
earlier field runs (11-2-13 / 13-2-11 band, sides swapped); kraken-v04 is
behavior-identical to kraken-v03 and scores 13-13 vs fry14 exactly as
kraken-v03 did in the 20-bot pool; leviathan's own claimed 3-5 vs hydra-v06
on their quick 4-map set reproduces exactly on those maps in my data.

**The ranking reverses the C++ pecking order.** hydra-v06 was 2nd in its own
5-bot field (159 pts) and is last-but-one here; the three independent Python
implementations all beat it. fry-v14's "nobody beats me on
Colloseum/Colosseum" claim (from my own hydra notes) is refuted — ouroboros
wins both sides of both maps against fry-v14.

## 3. Mechanisms (replay-derived, medians across rr2)

| bot | deaths/game | of which self-harm | h2h deaths/game | win types | length tiebreaks won |
|---|---|---|---|---|---|
| ouroboros | **111** | 11% (+ 0% walls) | 47 | 65 elim / 25 length | 12/31 |
| hydra-v06 | 196 | 31% | 62 | 24 elim / 11 length | 7/38 |
| leviathan | 192 | 27% | 66 | 12 elim / 20 length | 9/50 |
| kraken | 210 | 6% (61% body!) | 41 | 18 elim / 31 length | 16/46 |
| fry-v14 | 208 | 32% | 64 | 38 elim / 14 length | 5/37 |

- **Ouroboros wins by not dying.** It does *not* out-split the field (127
  splits/game vs 209-235 for the others); it loses half as many dragons,
  almost none to walls/self, and lets opponents grind each other. Against
  every opponent it eats roughly 2x the pearls of the opposition (e.g. 132
  vs 31 vs hydra-v06), converts steadily, and wins 65 eliminations.
- **Kraken is a length-race specialist**: most length wins (31) and best
  length-tiebreak rate, lowest head-to-head rate, but 61% of its deaths are
  running into bodies — it gets run over in elimination races.
- **Leviathan is a big-open-map specialist**: its 8 wins over fry14 include
  both big_empty sides; its losses are the small arenas (Colloseum, arena,
  schooltime, trophy).
- **The fry/hunter/hydra C++ family self-harms at ~1/3 of all deaths**
  (hit itself + wall). In 64-dragon endgames the priority ladder sprints
  into its own body at enormous rates (single help games: 613-687 self
  deaths). This is the family's structural tax and hydra inherited it.

## 4. Per-line criticism

### Ouroboros (Claude) — strongest bot, weakest documentation

Strategy: one evaluation function per dragon in length units; moves, sprints,
strikes, splits and portal dives compete in a single scored list. Roles are
weight slices chosen at split time and handed to the child over sonar
(64-bit parent->child hand-off, engine-verified). Threat model prices
enemy strike probabilities; a doom-memory tiles corridors that killed
allies; a crowned dragon stops splitting from round 200. The design doc is
the best game-theoretic read of the four (initiative, symmetric combat,
two win conditions).

Code: 1695 lines of dense Python, all constants in P/RP with a clean
override mechanism (params.py, `role.key` dotted names). Searches bounded
and stamped; exact body simulation of candidate paths.

Criticism:
1. **The flagship is undocumented and uncommitted.** v05-spread has no
   README, no results ledger, no recorded sandbox validation — nothing in
   the repo says the strongest bot in the pool is judge-safe. (I priced it:
   p99 37-44M, max <48M, wins both sandbox checks — it's fine, but nobody
   would know from the repo.)
2. **Side-B fragility**: 13 of 14 rr2 losses came as side B. The evaluator
   has no explicit first-mover compensation; a dominant bot should not be
   this side-sensitive.
3. Term proliferation (tunnels, doom, crowd, zones, crowns, spread...)
   without published ablations — attribution of what actually wins is
   getting hard even for its own author. The doc's "one hypothesis per
   variant" rule is not reflected in the code's growth.
4. Local wall-clock: >180 s on help — fine for the judge (CPU points are
   the budget) but it breaks fast local harnesses and inflates iteration
   cost.

Empirical claims audit: the design doc's baseline table is stale (v01-era:
hunter-v04 on top, fry-v14 5th). "hydra-v06 split 384 times on devil" —
not reproduced in my replays (max 248; direction correct). Its judgement
of "strongest pool bots" predates fry-v14 and its own v05.

### Leviathan (GPT) — best process, currently weakest player

Strategy: lexicographic objective (survive, then longest dragon, then total
length) implemented as a bounded candidate search (sprints simulated
step-by-step) scored by one weighted feature sum; the material correction
(sprinting costs net length, not gross pearls) was their biggest win.

Code: 330 lines + weights.py. The cleanest codebase in the repo — readable,
small, honest about limitations. Local geometry-cache invalidation (v07)
instead of cache-clearing; regression tests (16) cover routing, collision,
sprint affordability, replay parsing.

Criticism:
1. **Under-powered information layer**: no enemy memory beyond the visible
   window, no gossip protocol, one rotating sonar per turn, teammate
   reports parsed and explicitly unused. It fights every fight with local
   information only.
2. **Roles are decorative**: three crude states (scout/hunter/gatherer by
   round/length) sharing one weight set — the role table in DESIGN.md
   promises specialisations the code does not have.
3. Small-arena collapse: loses Colloseum/Colosseum/arena/schooltime/trophy
   to everyone; the evaluator's fixed team_target=40 and linear split
   urgency do not handle 11x16 corpse economies.
4. The process (equivalence checks, holdout discipline, "deterministic
   runs are not samples" statistics note) is the best in the repo — but it
   is currently optimising a local optimum: every v04-v07 gain was
   measured against fry-v03/kraken, not against the swarm war that
   actually decides this pool.

Empirical claims audit: RESULTS.md numbers all reproduced where testable
(3-5 vs hydra-v06 on their quick set = exact; 8-2 sandbox vs fry-v03
consistent with its profile). Their judge CPU figures (83.6M peak) I did
not re-verify but the methodology is sound.

### Kraken (Kimi) — the length-race underrated

Strategy: role-encoded split sizes (2=scout, 3=hunter, bigger=gatherer),
one rotating sonar doubling as radar sweep and gossip carrier, BFS compass
target scoring, strike/escape/priority ladder. v04 = v03 refactor with all
knobs in a CFG dict (behaviour identical).

Code: 1272 lines of tuned Python; the inner BFS loop is hand-optimised
(reusable stamps, locals caching). kbench.py implements variant/run/
analyze/compare around the shared tournament runner.

Criticism:
1. **Endgame crown missing**: no designated non-splitting grower before the
   round-380 freeze, so it cannot convert numbers into the longest dragon
   when eliminations fail — yet paradoxically it wins the most length
   tiebreaks in the field anyway. A crown role is the obvious multiplier.
2. **61% of deaths are body collisions**: its danger model prices enemy
   sprint reach but under-prices allied/allied traffic in its own swarm —
   it loses the elimination games its survival should win.
3. Sweep results so far are negative results (team_target_mid=40 rejected
   9-15, hunter_trade=1 neutral): the CFG harness exists but has not yet
   found a winning direction; the numbers-war weakness it shares with
   fry-v07/v09 matchups (2-10) is a production-schedule problem, not a
   parameter nudge.
4. Sonar policy: one cast/turn for echo-attribution is a self-imposed
   constraint; the rest of the field now broadcasts 2-4 slots/turn.

Empirical claims audit: framework doc's pool numbers (325-192, CPU 96M
max single match) consistent with my reruns; "fry-v07/v09 are the
structural weakness" confirmed in my 20-bot pool data (9-17 each).

### Hydra (GLM, self-criticism)

Strategy: forked hunter-v03 (the fry-family ladder) onto protocol 3 with a
4-direction status radio, enemy gossip on two sonar slots, pack attack,
echo-radar stalker-flee.

Criticism:
1. **Last against every other line in the cross-field** (2-24 vs
   ouroboros, 10-16 vs leviathan, 12-14 vs kraken). My field-2nd-place
   (159 pts) was a property of a soft pool, not of the bot.
2. **I optimized combat while the game is an economy.** The v07-v10 cycle
   tuned hunt gating and evasion; replay forensics said the losses were
   pearl conversion (88 vs 18) and self-harm (31% of deaths), and I fixed
   neither. Ouroboros's ledger shows the actual winning lever is
   deaths-avoidance plus steady births.
3. **Inherited architecture debt**: the fry/hunter ladder's sprint and
   split priorities self-harm at scale; forking it bought judge-safe C++
   speed and a closed structure that resists eval-function refactors.
4. v06's radio IS load-bearing (removing it cost the hunter-v03 matchup),
   but the gossip layer's value is unproven against the strongest lines —
   ouroboros wins with information its opponent helpfully broadcasts.

Empirical claims audit: my own note "fry-v14 beats every field bot on
Colloseum/Colosseum" is refuted (ouroboros does it); "pearl draws seeded
per invocation" was wrong (deterministic); the numbers-war diagnosis was
right but incomplete — it is a *deaths*-war as much as a *births*-war.

### The fry/hunter family (shared baseline)

Still the best pure C++ ladder, and fry-v14 remains #2 overall, but its
reign is over: it loses 7-19 to ouroboros. Its 32% self-harm rate and
one-sonar information diet are exploitable. v14's pearl-ownership trick
is now table stakes (ouroboros and the fry line both run ownership
deconfliction; hydra dropped it in the fork).

## 5. What I would take from each line

- From Ouroboros: threat-probability pricing and exact candidate
  simulation (deaths-avoidance), role hand-off at split, crown election,
  and the discipline of pricing CPU at promotion time.
- From Leviathan: the experimental contract (equivalence checks, regression
  tests, holdout hygiene, honest statistics) and net-material evaluation
  (pearls eaten minus segments spent).
- From Kraken: CFG-everything parameterisation (kbench) and the
  length-race profile as a deliberate specialisation.
- For all Python lines: the wall-clock lesson — a bot that cannot finish a
  500-round meat-grinder locally in <180 s will keep corrupting quick
  harness comparisons (use --timeout 1200+ for python pools).

## 6. Raw data

- `build/crossline-rr2/` — the clean round-robin (260 games, replays kept).
- `build/crossline-rr1/` — same schedule with 180 s timeout (5 help DNFs).
- `build/ouro-sandbox-arena1.log`, `build/ouro-sandbox-default1.log` —
  ouroboros sandbox CPU pricing.
- Tools used: `tools/leviathan/replay.py` (capnp decoder),
  `tools/hydra_replay.py` (per-round series), `tools/hydra_crossline.py`
  (aggregate), `tools/autopsy.py` (verbose-log autopsy).

## 7. Addendum: the hunter line, v05-v20 (user) — 2026-09-25

The user's hunter line grew from v04 to v20. Code read in full for v20
(1328-line C++), diffs studied v14->v20. All benchmarks below were run by
Hydra on the **new 11-map set** (stronghold, trauma added; Colloseum, help,
queen_of_spades_but_she_ages, small removed) — one focus run per bot,
`--timeout 1200`, replays kept: `build/hunter-v20-fixture`,
`build/hunter-v14-fixture`, `build/fry-v14-fixture-newmaps`.

### What the line is now

v20 = the fry ladder + fifteen versions of cumulative additions, each one
mechanism: sonar team/enemy state with confidence gating (v05-v10),
route-distance instead of Manhattan spacing (v11-v13), the C++ port
(v14), shared territory (v15), bounded-DFS **encirclement traps** —
surround an enemy head on 3 of 4 sides when up 3-4 in exact length
(v16-v18), a **6-ply survival lookahead** (`safe_continuations`: escape
depth and path counts) gating growth moves (v18-v19), and **portal
scouts** — one claimed scout per team explores unmatched portals on
low-spawn maps, with hotspots/coverage sectors shared over a five-tag
sonar protocol (v20). It is the only bot in the repo with an encirclement
attack and a genuine multi-ply survivability search.

### Measured strength (new 11 maps, vs the shared four: ouroboros-v05,
kraken-v04, leviathan-v07, hydra-v06)

| bot | pts/g | ouro | krak | levi | hydra | kills the numbers war? |
|---|---|---|---|---|---|---|
| hunter-v14 | **2.01** | 12-10 | 14-8 | 18-4 | 15-7 | yes |
| hunter-v20 | 1.81 | 11-11 | 9-12 | 16-6 | 17-5 | yes |
| fry-v14 (base) | 1.57 | 14-8 | 12-10 | 5-17 | 11-11 | yes |

(within-line: v20 beat v19 13-9 on the user's own 11-map run; v20 lost
ground to v14 against the field here.)

Context shift: on the old 13 maps ouroboros went 19-7 over fry-v14; on
the new set fry goes 14-8 and the hunter forks go 12-10 / 11-11. The
hunter line has caught the field leader; **hunter-v14 is arguably the
strongest bot in the repo on current maps**.

### What causes the performance differences (replay forensics, medians)

1. **The additions are worth +0.44 pts/game over the fry base**, and the
   mechanism is visible: hunter eats more (pearls 248/g median vs fry's
   ~166 profile) and out-splits opponents ~2:1 while trading at a higher
   rate than anyone (51-54% of its deaths are head-to-heads, vs 42% for
   ouroboros). The line wins by churn+economy, not by survival — the
   opposite of ouroboros's low-death profile, and it now matches
   ouroboros anyway. There is more than one winning style.
2. **v14 > v20 against the field**: v20's portal scouts convert in-line
   (13-9 over v19) but cost ~0.2 pts/game here. Mechanism: scouting
   length-3-6 dragons away from the length race deepens v20's one true
   weakness (below), and compact boards correctly skip it (the README's
   own 625-tile cutoff) — but trauma/big_empty/default do not.
3. **The #1 leak is length concentration.** 34 of v20's 45 losses (29 of
   v14's 39) are round-500 longest-dragon losses, and the forensics are
   unambiguous: v20 wins TOTAL length (677 vs 607, 671 vs 401) and loses
   the LONGEST tiebreak (27 vs 35, 30 vs 35). The line has no crown: it
   spreads length across 64 units. Every structural recommendation about
   crowns in the reviews applies here with numbers attached.
4. **Self-harm is half-fixed, not solved**: wall+self = 36% of deaths
   (v20 17% self / 19% wall; the 6-ply lookahead helps growth moves but
   the ladder's sprints and forage still suicide at fry-family rates).
   ouroboros's exact-simulation profile remains the reference.
5. **The five-tag radio is the repo's richest and its value is unproven**:
   v20's extra information (hotspots, sectors, claims) co-incides with a
   regression vs v14's simpler protocol. Information needs a consumer to
   be worth a slot; portals/traps have consumers, sector coverage may not.

### Structural recommendations (hunter line)

- Add the crown (elect at ~200-250, stop its splits, everyone else feeds
  it beds; crown-kill order at ~380). It converts the 34 length losses
  directly: v20 already wins total length — concentration is the missing
  half.
- Gate portal scouting on the production schedule (only at unit parity or
  better, and only when the crown is not starving), and A/B v20-vs-v14
  on the fixture before promoting scouts.
- Port the survival lookahead from growth moves into sprints/forage —
  the 36% self+wall rate is the next biggest addressable loss.
- Keep v14 as the field benchmark and v20 as the experimental branch;
  do not let within-line wins (13-9 over v19) promote a change that
  gives back 0.2 pts/game to the field (the v07-v10 hydra failure mode,
  independently re-discovered).
