# Pieces and puzzles — a reference for stripping ideas down and building them up

**Owner:** T-1 · **Companion to** [TAXONOMY.md](TAXONOMY.md) (ids link to `docs/taxonomy/<id>.md`) · **State as of**
30 Sep 2026, `main` 9315914c9 + lane branches · **Last reviewed:** 2026-09-30

The taxonomy lists everything the programme has built and measured. This page reduces it to two collections and one
axis: the **pieces** (the primitive things a bot can know, believe, commit to, evaluate, search and do), the
**puzzles** (the questions the game forces a dragon to answer, stated independently of any mechanism), and the
**information horizon** — how far back and how far forward in time a piece reaches. The horizon axis is here because
it is the programme's least-explored dimension: the production bot is built as a per-turn optimiser, and the memory it
has is thin and short.

Use it three ways: (1) to strip — take a puzzle, find the pieces that currently answer it, and ask what the bot does
with each removed; (2) to build — climb one rung of the horizon ladder for one puzzle at a time, with the test named
for that rung; (3) to place a new idea — every proposal should name the puzzle it answers, the rung it adds and the
pieces it needs.

---

## 1. The horizon ladder

| Rung | What the dragon uses | Example in the programme |
|---|---|---|
| **R0 — now** | The current 7×7 view, current bodies, this turn's radio | Ares ally/enemy-nearer target discounts; threat map from visible heads |
| **R1 — last observation** | A lookup of the last thing seen at a cell or about an object, with a TTL | Ares pearl memory (≤40 rounds), bed countdowns, portal pairs, body-seen-near-portal (≤12 rounds) |
| **R2 — accumulated belief** | A quantity that integrates many observations and decays: rates, densities, hazard maps | Sciel EW food density (half-life ~34 rounds); Tyr density EWMA (half-life 4); visit counts |
| **R3 — commitment** | The dragon's own intent carried across turns: a target, a plan, a mode, with explicit exit conditions | Target hysteresis (1 target, re-scored every turn); newborn escape plan (≤18 turns); crown/feeder role |
| **R4 — shared intent** | Beliefs or intentions exchanged between dragons and used as evidence | Crown consensus; V33 split-time portal route; proposed target claims (sciel-05); L33 coupled beliefs |
| **R5 — structure / learned** | Map-level structure inferred over the game, or behaviour learned offline | Dead-end peel and arrival maps (cx router); map signature (analysis only); m01/Loki (Python) |

Forward horizon is the mirror image: R0 plans only for this move; R1 knows a bed will ripen; R3 plans to *be there when
it ripens*; R5 predicts where food and danger will be from structure.

## 2. Where Ares actually sits

**The decision is an argmax recomputed from scratch every turn** (`bots/ares-v06-expanded-search-support/policy.hpp:1129-1438`):
target BFS → one target → candidate 1–3-step paths → score → move or split. What carries over between turns, and how
strongly it can move a decision:

| Carried state | Rung | Time constant | Weight in the decision | Pointer |
|---|---|---|---|---|
| Direction momentum | R3 | EWMA decay 0.6 → half-life ≈ 1.4 turns | ≤ 0.6 score points (goal term 1.2, trap term up to 30+) | `policy.hpp:1390, 1433-1434`; `params.hpp:97` |
| Previous target | R3 | 1 turn; kept only if its value ×1.25 ≥ the new best | re-scored every turn; no plan, no exit condition | `policy.hpp:1230-1233` |
| Visit counts | R2 | −1 per cell every 16 rounds over the last 64 trail cells | −0.15 per visit | `policy.hpp:1133-1141, 1389` |
| Local ally/enemy density | R2 | half-life 4 rounds (literal) | multiplies target values | `policy.hpp:548` |
| Radio density reports | R2 | half-life 4, ttl 16, ≤32 sources | multiplies target values beyond view | `policy.hpp:576`; `params.hpp:125-126` |
| Pearl memory | R1 | 40 rounds, then worth 0 | 6 vs 10 for a visible pearl | `policy.hpp:733-736`; `params.hpp:92` |
| Bed countdowns | R1 (forward) | exact spawn round | worth 8 **only if ripe by arrival**; `bed_wait = 0`, so a bed ripening after arrival is worth 0 | `policy.hpp:737-751` |
| Seen / never seen | R1 | binary | never-seen cell worth 5; a cell seen empty 1 or 300 rounds ago both worth 0 | `policy.hpp:751-752` |
| Bodies seen near a landing | R1 | 12 rounds | blind-landing risk 1.0 vs 0.15 | `policy.hpp:777-787` |
| Enemy memory (DragonMem) | R1 | per id | read only for enemy **length**; position, facing, first-seen are stored and unread | `world.hpp:47-66`; [F-06](taxonomy/F-06.md) |
| Newborn escape plan | R3 | ≤ 18 turns, newborns only | route bonus 3.5·0.91^age | `policy.hpp:191-299` |
| Crown / feeder / prey | R3–R4 | crown ttl 20, prey ttl 15; from round 250 | role switch | `policy.hpp:359-419, 489-536` |
| Echo counts | — | stored, never read | 0 | [F-19](taxonomy/F-19.md) |

Reading of the table, stated plainly:

1. **The food model is a last-observation lookup, not a belief.** A cell's worth is a step function of the last thing
   seen there. Nothing accumulates where food tends to appear, where it was eaten, or how fast a region renews; nothing
   predicts a bed that ripens after arrival. (The one R2 food belief built on Ares, Sciel's EW food density, lives on an
   unmerged branch.)
2. **Commitment is one turn deep.** The bot re-derives its target every turn and keeps the old one only on a 25 % tie
   margin. There is no plan object, no mode, no exit condition — outside the 18-turn newborn escape plan and the late
   crown roles.
3. **The memory that exists has short time constants** — 1.4, 4, 12, 16, 40 rounds — in a 500-round game.
4. **Others are modelled from the current view only.** Ally and enemy discounts use this turn's heads; the threat map
   uses heads within 7 cells now; enemy history is kept only to estimate length.
5. **The spatial horizon is also short:** after round 40 the target search stops at 48 nodes and binds in ~80 % of
   decisions (R-1). Widening it late (lune-r1-07) was the one search change that held (+0.026 econ, hold).

So the concern holds, with one qualification: the bot is not memoryless, but its memory is lookups and short EWMAs
feeding a per-turn scorer. Switches bolted onto that scorer compete with a dozen hand-tuned instantaneous terms, which is
why most of them measured as small or null.

## 3. What the evidence says about information beyond the turn

| Mechanism | Rung | What it changed | Host | Result | Why it stopped |
|---|---|---|---|---|---|
| Atlas (full map from first view) | R5 prior | target values, routes | Ares V08 | econ **+0.188** (p@50 1.217 vs 0.970); ally head-on +205 % | out-of-sample rule ([S-20](taxonomy/S-20.md)) |
| EW food density | R2 | target values (unseen, beds) | Ares (Sciel) | econ **+0.067…+0.105**; gen **+6…+16 %**; ally head-on +24…+38 % | crowding guard ([S-25](taxonomy/S-25.md), [S-22](taxonomy/S-22.md)) |
| Late search cap ×8 | spatial | which target is found | Ares (Lune) | econ +0.026, dragons +0.053 | hold; round-keyed ([S-32](taxonomy/S-32.md)) |
| Supply-gated bed wait | R1 forward | target values when starved | Ares (Esquie) | +0.0018, Trauma +6 pp | local hold ([S-28](taxonomy/S-28.md)) |
| Flat bed wait | R1 forward | target values always | Ares (Renoir) | −0.06; QoS/Trauma +0.14–0.16, Devil −0.72 | reject; keying untested ([S-27](taxonomy/S-27.md)) |
| Pearl-memory TTL 20 / 60 | R1 | target values | Ares | −0.013 / +0.002 | reject / hold ([S-29](taxonomy/S-29.md)) |
| Exploration value, info gain | R1/R2 | target values | Ares (Renoir) | unseen 3: +0.110 pool, gen −0.016; info gain −0.223 | pool fit ([S-26](taxonomy/S-26.md)) |
| Portal pair memory / exit-known | R1 | move gate | Ares (R-3), chassis | transits −22…−68 %, per-transit hazard unchanged, econ −0.05…−0.12 | throttle ([S-15](taxonomy/S-15.md)) |
| HOLD packet | R4 | move risk | Ares V07 | ally head-on −13 %, score −5 pp | reject ([S-17](taxonomy/S-17.md)) |
| Target hysteresis 1.75 | R3 | stickiness only | Ares (Monoco) | econ −0.044 | reject ([S-57](taxonomy/S-57.md)) |
| Momentum w 0.6 | R3 | move term | Python (yuna) | +6/80; variants plateau; **never varied on Ares** | [S-57](taxonomy/S-57.md) |
| S1 density gossip → early economy | R4 | early targets | Python (v10 host) | negative everywhere | [S-24](taxonomy/S-24.md) |
| Router: arrival maps + assignment | R4/R5 | targets, spacing | cx chassis | length r100 176/3/61, atlas carried ~2/3; units n.s. | wrong host; never on Ares ([S-58](taxonomy/S-58.md)) |
| Blind-exit memory | R1 | landing risk | Python; inherited in Ares, never varied | valjean Dilemma+Autarky 3–21 → 14–10 | [S-16](taxonomy/S-16.md) |
| Learned policies | R5 | whole policy | Python only | m01 51–53; Loki 0–30 on CPU | CPU / teacher ceiling ([S-53](taxonomy/S-53.md)–[S-56](taxonomy/S-56.md)) |

Patterns the table supports:

- **The two largest economy effects in the programme are both information beyond the view** — map knowledge (atlas) and
  an accumulated food belief (EW density). The second is legal and generalised off-pool (+16 % on unseen maps).
- **Information paid only when it changed *which target* a dragon chose.** Every positive row acts in target valuation
  or search (A-02/A-03); every move-level term or entry gate (A-04/A-10) measured negative or as a volume throttle.
  Target level is necessary, not sufficient: flat bed waiting, info gain and a stiffer hysteresis were target-level and
  negative — each added a rung without a better estimate behind it.
- **Every information gain became a coordination problem.** Better beliefs send several dragons to the same good place;
  the ally head-on guard then rejects the change. The information puzzle and the coordination puzzle are the same puzzle
  at two scales: knowing where food will be, and knowing who else is going there. Build them together.
- **Commitment has only been tested bluntly** — a stiffer tie margin with no better reason to stick (negative). A plan
  with explicit exit conditions (L31) has never been built.
- **The existing memory has never been ablated.** Nobody knows how much of V06's strength its R1–R3 state provides.
- **The CPU reason is gone.** Much of the thinness is inherited from Python hosts that ran at the 100 M wall; Ares uses
  8.6 M.

A caution against over-reading: in the team-recon imitation studies, adding history features raised predictability of
the top teams' moves by only 0.3–1.0 pp (306, 62, 470) and ours by 5.4 pp (GLM direction models,
`experiment_data/team_recon_*_glm`). Taken at face value, strong teams' moves are no more history-dependent than ours.
The instrument is weak — a known-source bot (gavroche-v54) imitated only to 73.6 % with the same features, so the ceiling
is the feature set — but it argues that the edge may lie in *what is computed* (map-level knowledge, arrival races)
rather than in long memory as such.

## 4. The puzzles

Stated without reference to any mechanism. "Needs" is the horizon the puzzle requires; "Ares" is the rung the
production line answers it at today.

| # | Puzzle | Needs | Ares | Problems it produces | Tried above Ares's rung (result) |
|---|---|---|---|---|---|
| Q1 | **Where is food now, and where will it be?** | R2 belief + forward bed timing | R1 lookup; beds only if ripe by arrival | [P-10](taxonomy/P-10.md), [P-09](taxonomy/P-09.md) | EW density + (blocked by Q2); atlas + (banned); bed wait flat − / gated LH |
| Q2 | **Can I get it before anyone else, allies included?** | R3 intents of others, arrival times | R0 (current heads, distance tie-break) | [P-04](taxonomy/P-04.md), [P-07](taxonomy/P-07.md) | valuation guards − (Sciel); claims and assignment never on Ares |
| Q3 | **Will I still have room after this move, and in ten?** | R0 forward simulation + R5 structure (dead ends) | R0+ (time-aware flood with vacancy, 5-step reach) | [P-01](taxonomy/P-01.md), [P-05](taxonomy/P-05.md), [P-06](taxonomy/P-06.md) | dead-end peel (chassis only); hard/soft reach − ; critical split LH/− |
| Q4 | **When should I split, and where does the child start?** | R2 local supply + R3 child plan | R0 split score; newborn escape plan R3 | [P-02](taxonomy/P-02.md), [P-11](taxonomy/P-11.md) | siting (inert); pace targets −; escape-early H; V33 route handoff LH |
| Q5 | **What is on the other side of this portal?** | R1–R2 exit history, R4 ally transit intents | R1 (pairs, bodies seen ≤12 rounds) | [P-03](taxonomy/P-03.md) | pre-entry memory (throttle); HOLD −; post-transit steering − |
| Q6 | **What will the enemy near me do?** | R2 per-enemy behaviour | R0 (heads within 7, reach ≤3) + length memory | [P-12](taxonomy/P-12.md) | Python aggression refits −; nothing on Ares |
| Q7 | **Who among us should go where?** | R4 shared intent / division of labour | R0 discounts + R1 radio facts | [P-04](taxonomy/P-04.md), [P-12](taxonomy/P-12.md) convergence | S1 gossip −; roles (Python) mixed; router (chassis) |
| Q8 | **How is material turned into the win condition?** | R3–R4 crown consensus + clock | R3 roles from r250, feed clock keyed on W+H | [P-13](taxonomy/P-13.md) | earlier conversion −; crown params never varied on Ares |
| Q9 | **What kind of map is this?** | R5 structure inferred in play | none (three 32×16 identity terms) | [P-14](taxonomy/P-14.md), [P-15](taxonomy/P-15.md) | atlas (banned); signatures analysis-only; size-threshold doctrines (Python) |
| Q10 | **What phase of the game am I in?** | R2 state (sparsity, contact, saturation) | round thresholds (40, 150, 200, 250, 380) | [P-08](taxonomy/P-08.md) | late cap by round H; state-keyed budget never built |
| Q11 | **Am I being consistent with what I decided last turn?** | R3 plan with exit conditions | 1-turn hysteresis, 1.4-turn momentum | [P-18](taxonomy/P-18.md); commitment failures at portals and dead ends | stiffer hysteresis −; modes never built |
| Q12 | **Did the change help?** | — | D-032 interval gate | [P-19](taxonomy/P-19.md)–[P-22](taxonomy/P-22.md) | see §6 |

## 5. The pieces

Grouped by layer. Rung is the piece's own horizon; "Ares" is whether it is live in V06 and the lanes' base.

**Knowing (stored facts)** — terrain and kelp edges [F-01](taxonomy/F-01.md) R1, Ares ✔ · portal pairs
[F-02](taxonomy/F-02.md) R1 ✔ · seen / never-seen [F-03](taxonomy/F-03.md) R1 binary ✔ · pearl memory
[F-04](taxonomy/F-04.md) R1 40 rounds ✔ · bed countdowns [F-05](taxonomy/F-05.md) R1 forward ✔ (future branch off) ·
respawn-gap memory (inside F-05) R2, chassis only · other dragons and vacancy [F-06](taxonomy/F-06.md) R0 + length
memory ✔ · own body [F-07](taxonomy/F-07.md) ✔ · portal transit memory [F-18](taxonomy/F-18.md) R1, off · echoes
[F-19](taxonomy/F-19.md) unread · atlas [F-21](taxonomy/F-21.md) R5 prior, dead code.

**Believing (derived estimates)** — room flood [F-09](taxonomy/F-09.md) R0 forward ✔ · 5-step reach
[F-10](taxonomy/F-10.md) R0, teammates' V13+ · threat map [F-11](taxonomy/F-11.md) R0 ✔ · ally/enemy density
[F-12](taxonomy/F-12.md) R2 half-life 4 ✔ · EW food density [F-13](taxonomy/F-13.md) R2 half-life 34, branch only ·
visits [F-08](taxonomy/F-08.md) R2 ✔ · dead-end peel [F-24](taxonomy/F-24.md) R5, chassis only · arrival maps
[F-25](taxonomy/F-25.md) R0 forward, chassis only · map signature [F-48](taxonomy/F-48.md) R5, analysis only ·
phase from state (F1 HMM, [F-45](taxonomy/F-45.md)) R2, analysis only.

**Committing (intent across turns)** — target + hysteresis [F-15](taxonomy/F-15.md) R3 one turn ✔ · momentum
[F-14](taxonomy/F-14.md) R3 1.4 turns ✔ · newborn escape plan [F-17](taxonomy/F-17.md) R3 ≤18 turns ✔ · crown/feeder
role [F-16](taxonomy/F-16.md) R3 from r250 ✔ · modes and mode beliefs [A-24](taxonomy/A-24.md) never built · roles at
creation [A-26](taxonomy/A-26.md) Python only.

**Evaluating** — target valuation [A-03](taxonomy/A-03.md) (where information has paid) · move scorer
[A-04](taxonomy/A-04.md) (a sum of ~15 instantaneous terms) · threat and support [A-11](taxonomy/A-11.md) ·
crowding terms [A-16](taxonomy/A-16.md).

**Searching** — target BFS with node caps [A-02](taxonomy/A-02.md) · 1–3-step candidates and sprints
[A-05](taxonomy/A-05.md) · look-ahead / reply search [A-22](taxonomy/A-22.md) (never on Ares).

**Acting** — move, sprint, routine split [A-06](taxonomy/A-06.md), escape split [A-07](taxonomy/A-07.md), cramped
split [A-08](taxonomy/A-08.md), dive [A-10](taxonomy/A-10.md), feed-by-dying [A-14](taxonomy/A-14.md), sonar.

**Sharing** — radio facts (pearls now, beds due ≤30, pairs, density, crown, prey, split handoff)
[F-20](taxonomy/F-20.md), [A-12](taxonomy/A-12.md), [A-13](taxonomy/A-13.md) · intents: HOLD (type 8, rejected), route
handoff (type 9, V33), target claims (proposed).

**Scheduling** — round thresholds [A-15](taxonomy/A-15.md), [F-23](taxonomy/F-23.md) · map-size doctrines
[A-18](taxonomy/A-18.md).

## 6. Strip and build

**Strip first: measure what the existing memory is worth.** Build `ares-bare`: every carried channel in §2 set to R0
where a parameter allows it (`memory_ttl` 0, `momentum_weight` 0, `target_hysteresis` 1.0, `visit_weight` 0,
`density_ally_weight`/`density_enemy_weight` 0, `blind_fresh` 0; gossip receipt and the previous-target path need a
one-line switch each). Run V06 vs bare under D-032, then
leave-one-in (bare + one channel). This has never been done; it tells which channels are load-bearing, which are
decorative, and whether "memory" as currently built is worth anything — the baseline every build step below needs.
Check each variant diverges from its parent in the golden replay before scoring it (dead parameters and header-only
builds have produced null "results" before, [P-19](taxonomy/P-19.md)).

**Test beliefs before policies.** An R2 belief is a predictor and can be scored offline, in seconds, on replays: does
the food belief put mass where pearls actually appear next (log-likelihood per round)? Does the hazard belief predict
the next death? Does an arrival map predict who reaches a bed first? Only a belief that predicts better than the R1
lookup is worth wiring into the scorer. The F1 frames ([F-45](taxonomy/F-45.md)) already carry the positions needed.

**Then build one rung per puzzle, target level first, coordination alongside.**

| Puzzle | Next rung | Minimal build | Must be paired with | Diagnostic beside the gate |
|---|---|---|---|---|
| Q1 food | R2 belief + R1 forward | EW food density (Sciel 03a) and bed value for ripening-after-arrival keyed on the belief, not a flat wait | Q2 deconfliction | belief log-likelihood; pearls/100 dt; per-map deltas |
| Q2 contest | R3–R4 intents | target claim packet (cell, id, round) read as an arrival commitment; or the router's greedy assignment over visible allies | — | ally head-on per 1k; pocket co-occupancy; claims honoured |
| Q3 room | R5 structure | dead-end peel and tree value as a switch (from cx-b02) | Q4 (splits are the escape) | trapped len/1k by reach band; mill count on Slithery |
| Q11 commitment | R3 plan | a target with explicit exit conditions (reached, value fell below x, danger rose, a better target by margin m) replacing the 25 % tie | Q1 (a plan needs a better reason to stick) | target switches per 100 turns; oscillation count |
| Q4 production | R2 local supply | child start chosen by the Q1 belief, carried in the split handoff | Q2 | newborn deaths ≤10 rounds per 100 births |
| Q5 portals | R2 per-pair hazard + R4 ally transits | per-pair survival rate (not a gate) priced into routes; transit intent shared | Q2 | deaths per 100 transits at unchanged transit volume |
| Q10 phase | R2 state | search budget keyed on local sparsity instead of round 40 | — | per-checkpoint deltas |

Order suggested by the evidence: bare-Ares ablation → Q1 belief scored offline → Q1+Q2 built together on Ares (the pair
that has shown the largest effect and the binding guard) → Q11 plans → the rest. Each step is one D-032 run on the
desktop once the switch exists.

## 7. Placing a new idea

Before building, write one line: *puzzle Qn · rung Rk → Rk+1 · pieces used (ids) · acts on target / move / split /
radio · paired coordination piece · offline predictor test · gate and diagnostic.* An idea that cannot name its puzzle,
or that adds a move-level term at the same rung, has the profile of the switches that measured null.

## Change log
- 2026-09-30 — created (T-1), in response to the lead's concern that the bots use only current-turn information.
