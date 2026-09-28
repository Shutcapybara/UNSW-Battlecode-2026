# HANDOFF — read this first

The living spec for every model and person working on the UNSW Battlecode bots.
It is written to be pasted into a fresh context. Keep it short and current. When
something here is wrong, fix it in the next cycle, and note the change in §11.

**Read in this order:**

1. This file.
2. `FRONTIER.md`: which bots matter now.
3. Your line's own docs (§3).
4. `docs/ouroboros-macro-spec.md` §3, if you are building a core bot.

---

## 1. The contest

- **Docs:** https://game.battlecode.au/docs/. Read `structure`, `movement`, `splitting`, `sonar`, `death`, `timeouts`, `game-format`, `elo`. The sonar page changed recently (protocol 3); the current text is in the project description, and §1.1 summarises it.
- **Game:** sea dragons in a snake-like game. Each dragon is a separate process running our program. Each team can have up to 64 dragons.
- **Game length:** at most 500 rounds. Within a round, dragons act in ascending id order.
- **Winning:**
  - Eliminate the other team.
  - Otherwise, after round 500 (or if both teams die in the same round), the tiebreaks are:
    1. longest living dragon;
    2. total length;
    3. draw. Mutual elimination in the same round is a draw.
- **Rated play:**
  - A ranked battle is **5 games on random maps**.
  - Elo rating uses K=96 and is based on *performance against prediction*: winning 3–2 against a much weaker team loses rating.
  - Most games are autoscrims (every 2 h, against teams within 8 places).
  - **Consequence: we optimise per-game win rate across all map types.** Robustness beats peak performance on one map class.
- **Compute:**
  - 100M CPU points per dragon per turn. Going over kills that dragon.
  - There is no first-turn exemption.
  - A stdout write costs 2.5M + 4k/byte.
  - Parsing one round in Python costs about 10M.
  - Python works if engineered for it (ouroboros p99 about 48M). C++ has large headroom (hunter about 17M).
- **Map bundle:** the tournament runner uses checked-in `.map` files recursively under `maps/`, including `maps/new/`. The class list below is an 11-map historical snapshot; see `comparison.toml` for the current default directory selection.
  - **Compact**, ≤625 tiles: arena 11×11, Colosseum 16×16, default_small 16×16, devil 32×16, trophy 25×25.
  - **Open**, ≥875 tiles: queen_of_spades 25×35, default 32×32, stronghold 48×24, trauma 48×24, schooltime 60×40, big_empty 64×64.
  - The server's map pool is not known exactly. Test on the transposed and flipped variants too (`tools/ouroboros/mapgen.py`).
- **Engine facts learnt the hard way:**
  - The local engine is **deterministic**: the seed is fixed, so a (map, side, bot pair) is one exact game, and repeats are not samples.
  - Side matters because of id order.
  - A head-to-head collision kills both dragons. Moving into a body kills only the mover.
  - Sprinting k steps costs k−1 segments. A split takes the rear segments; 2-segment children are the meta.

### 1.1 Sonar (protocol 3)

- Up to 4 uint64 rays per turn, one each N/E/S/W. They are cast after the move, if the dragon is alive.
- A ray wraps around the map, passes through portals, and stops at the first kelp or dragon part it hits.
- A ray aimed into your own body exits from the tail. **This is how a parent hands a message to a child it has just split off.**
- Messages arrive at the start of the recipient's next turn. No sender or team is attached, so enemies can hear you: use a checksum or tag.
- Echoes give the sender counts of what its rays hit: kelp, ally, ally_head, enemy, enemy_head.

---

## 2. Lineage and ownership

| Line | Author | Prefix | Role in the project |
|---|---|---|---|
| **Ouroboros** | Claude | `ouroboros-` | Core bot (strongest-bot track) |
| **Leviathan** | GPT | `leviathan-` | Core bot (strongest-bot track) |
| **Kraken** | Kimi | `kraken-` | Exploration track |
| **Hydra** | GLM | `hydra-` | Exploration track |
| **Hunter** / fry | team member, with LLMs | `hunter-`, `fry-` | Human-led line. The deployed version is not recorded in this checkout; see `FRONTIER.md`. |

**Rules:**

- **Never edit another line's bots, tools or docs.** Read them, benchmark them, copy them into your own line (say so in the README).
- Shared files (`README.md`, `tools/benchmarking/tournament.py`, `maps/`) change only when the user asks.
- `FRONTIER.md` and §11 of this file are edited only by the cycle's unifier (§8).

**Naming:**

- Mainline: `<line>-vNN-<slug>`, for example `ouroboros-v12-core`. NN only goes up. The slug names the hypothesis.
- Exploration forks: `<line>-xNN-<slug>`, for example `hydra-x01-compact-rush`. Kraken's existing `kraken-sNN` sweeps count as the same thing.
- Parameter-only variants are **not** folders. Use `params.py` overrides (`bot@key=value` in `ouro.py`) and record them in the ledger.
- Borrowing another line's component: copy it, then write in the README: `Base: <bot>; borrowed: <component> from <bot>`.
- Never delete old bots; they are the baselines. They leave the current candidate pool in `FRONTIER.md` but remain available as comparison opponents.

**Every bot README contains:**

- line, base version, the *one* hypothesis, and the changes;
- results: which sets, W–L, side split, compact/open split, flips against the base;
- sandbox CPU (p50/p99/max);
- a verdict: promoted, archived, or null result.

---

## 3. Where things are

| What | Where |
|---|---|
| Bots | `bots/<name>/` (`main.py` or `main.cpp`, `bot.toml`, `README.md`, optional `params.py`) |
| Maps | `maps/**/*.map` (the shared bundle, including `maps/new/`). Variants: `python3 tools/ouroboros/mapgen.py` |
| CLI | `unswbc` (`unswbc run MAP BOT_A BOT_B`, `--sandbox` for judge CPU); `unswbc init python NAME` |
| Shared tournament | `tools/benchmarking/tournament.py` (round-robin / focus-bot; `--timeout 1200` for Python pools) |
| Claude harness | `tools/ouroboros/`: `ouro.py run/sweep/report/compare/standings/autopsy`, `phase.py` (win/loss phase stats), `deaths.py`, `replaystats.py`, `replayview.py`, `mapview.py`, `mapgen.py`. See its README. |
| GPT harness | `tools/leviathan/`: lineage review, replay decoder, probes, equivalence checks, regression tests |
| Kimi harness | `tools/kraken/kbench.py`, `docs/kraken-design-framework.md` |
| GLM tools | `tools/hydra_replay.py`, `tools/hydra_crossline.py`, `tools/autopsy.py`, `tools/family_report.py` |
| Hunter analysis | `tools/hunter/summarize.py`, `docs/hunter-python-results.md`, `docs/strategy-backlog.md`, `docs/bot-workflow.md` |
| Historical Fry comparison | `tools/experiments/fry_child_count/compare.py`, `docs/experiments/fry-child-count.md` |
| Cross-line reviews | `docs/cross-line-review.md` (GLM, §7 on hunter), `docs/family-comparison.md` (Kimi, including the hunter section), `docs/leviathan/LINEAGE_REVIEW.md` (GPT) |
| Line design docs | Ouroboros: `docs/ouroboros-design.md`, `docs/ouroboros-macro-spec.md`. Hydra: `docs/macro-spec.md` (supersedes `design-framework.md`). Kraken: `docs/kraken-macro-spec.md`, `docs/kraken-design-framework.md`. Leviathan: `docs/leviathan/DESIGN.md`, `RESULTS.md`. |
| Raw results and replays | `build/` (git-ignored, local only). Quote the numbers you rely on in a README or cycle file, or they are lost. |
| Current status | `FRONTIER.md`. Cycle history: `docs/cycles/cycle-NN.md` |

---

## 4. Architecture: the core starter spec

Everyone has converged on the same skeleton. Start from it, and deviate only
with a stated reason and a measurement.

### 4.1 Per-turn loop (one dragon)

```
sense    parse view → update terrain, pearls, bodies (incremental, cached)
hear     decode sonar packets (checksum/tag) → update team belief
model    world model: confirmed / remembered / predicted pearls, bed timers,
         enemy sightings (decaying), ally registry, zone summaries
role     role state machine check (cheap); crown election
target   role's selector picks a strategic target (cached a few turns)
generate candidate actions from enabled OPTIONS (moves, sprints, strike,
         trap, portal trip, split, yield, feed, …)
filter   exact simulation of each candidate; drop certain deaths and
         self-traps (continuation depth)
score    Σ θ·features in length units → argmax
speak    sonar scheduler fills 4 slots (child hand-off > self > best relay)
```

### 4.2 The mental model: a chess engine

- **Evaluation, not strategy branches.** Every decision is a candidate scored by one evaluation function in a common unit (length). "Strategies" are *weightings*, not code paths.
- **Team value V** (what the dragon evaluation approximates):

  ```
  V = λ_len·Σlen + λ_unit(t)·units + λ_crown(t)·(ourLongest − theirLongest)
      + λ_ctrl·Σ density·control − risk
  ```

  The λ values change with phase. λ_unit is high early (production compounds) and falls to 0 by the endgame. λ_crown is ~0 early and dominant after about round 400.
- **Options → roles → doctrine.** This is the parameterisation.
  - An *option* is a macro-action generator with preconditions.
  - A *role* is: enabled options + target selector weights + evaluation weight slice + constraints.
  - The *doctrine* is team-level parameters per (map class × phase): role mix, production target, split threshold, trade thresholds, crown/feed timing, scout quota.
  - Tuning θ = {doctrine, roles, shared tactics} is the end game of this project.
- **The admission rule for new ideas.** A new idea enters as a new option, a new feature tied to a named V component, or a new parameter. Anything else is not added. This rule exists to stop term proliferation, which every line has suffered from.
- **The convergence test.** The unified bot must be able to express *both* hunter-v20's behaviour (production-first ladder: split at length 4, trade freely) and ouroboros-v10's (survival, crown, feeding) as parameter points. The target is to tune compact maps towards the first and open maps towards the second.

### 4.3 Components and current best implementation

Converge per component: one reference implementation per component, and
competing versions only while there is a live hypothesis. The unifier updates
this table each cycle.

| Component | Current reference | Contenders / ideas to fold in | Status |
|---|---|---|---|
| Terrain and portals | ouroboros (exact edge learning, portal pairing) | leviathan-v07 local cache invalidation (CPU); 16-bit portal ids needed (GPT O2) | converged, needs fixes |
| Candidate simulation and safety | ouroboros exact path simulation (0 wall deaths) | hunter-v18/v19 continuation-depth lookahead; hunter id-order gating (only not-yet-moved heads can be constrained) | merge both |
| Threat model | ouroboros p_strike(k) × value exchanged | kraken binary danger (weaker); side/initiative term missing everywhere except hunter | open |
| Pearl model | hunter-v15+ bed countdown pre-positioning (`countdown < eta`) | ouroboros confirmed-vs-remembered fix (GPT O1); kraken bed prediction; symmetry mirroring (nobody yet) | **highest-value open item** |
| Pearl ownership | route-distance claims (fry-v14 / hunter-v06 / ouroboros) | explicit CLAIM packets beyond vision | converged |
| Production | hunter: `SPLIT 2` at length ≥ 4 while below limit | ouroboros evaluation-priced split with spawn windows (too cautious on compact maps) | open: make the threshold a doctrine parameter |
| Roles | ouroboros weight slices + parent→child hand-off | hunter-v20 single scout claimed over sonar with TTL | converged in form |
| Crown and endgame | ouroboros-v10: election, beacon with TTL, demotion, emergency hand-off, feeding from round 400 | kraken early length banking; timed claim lapse | converged; hunter lacks it (34 of 45 v20 losses are length tiebreaks) |
| Comms | ouroboros packets (checksum, kind, TTL relay) + hunter-v15 replicated team summary | hunter-v20 hotspot/coverage tags (value unproven: v20 < v14 against the field) | merge; every packet needs a consumer |
| Aggression tactics | hunter-v16 boost-surround/trap (exact enemy length, full visibility) | parity-priced strikes; crown-kill orders; chase horizon ≤ 6 (hydra, kraken) | open |
| Compute | ouroboros (`gc.disable`, stamps, cached waypoints, degradation) | leviathan local cache; C++ port if Python caps depth | fine |
| Harness | `ouro.py` (variants, compare, phase), leviathan equivalence and regression tests, kbench | one shared ledger format (§9.3) | converge next cycle |

---

## 5. Strategy summary

### 5.1 Clusters

| Cluster | Bots | Core idea | Compact maps | Open maps | How it wins / loses |
|---|---|---|---|---|---|
| **Swarm/churn ladder** | fry-v14, hunter-v14/v20, hydra-v06–v10 | Fixed priorities; split at 4; trade heads freely; strong tactics (v16+ traps, v18+ lookahead) | **Dominant**: hunter-v20 37–2–1 against the field | Weak: 13–35. Longest dragon ends at about 4 | Wins by elimination and churn. Loses the round-500 longest-dragon tiebreak while *winning total length* (no crown) |
| **Survival evaluator + crown** | ouroboros-v10 | One evaluation; exact simulation; avoid deaths; crown + feeding | Vulnerable: 7–53 against hunter-v16/v20 on compact variants. The opening pearl race is lost by round 30 | **Dominant**: 59–1 against hunters; 238–23 against the other AI lines | Wins by not dying and converting to one long dragon. Loses early eliminations |
| **Length banker** | kraken-v04 | Bank length early; bed prediction; size-coded roles | Middling | Good tiebreaks | Beats hunter-v20 12–9 on length; dies to bodies (56% of its deaths) |
| **Lean evaluator** | leviathan-v07 | Small bounded search; net-material accounting | Weak (under-produces) | Occasional big_empty wins | Clean but low production; loses the attrition wars |

### 5.2 The axes that decide games

1. **Opening economy (compact maps).** Pearls and splits in rounds 0–30 decide compact maps. hunter-v15 ate 3× v10's pearls by walking to beds before they spawned and splitting at every chance.
2. **Survival (everywhere).** Deaths compound. Exact simulation plus traffic awareness halves deaths compared with the ladders.
3. **Conversion (open maps, and any game reaching round 500).** Without a crown, a bot loses the tiebreak even while ahead on total length.
4. **Aggression is priced by production.** Equal trades favour the side that out-produces. Trading when behind in units loses. Far chases starve (keep them within about 6 steps).
5. **Initiative.** Id order means lower ids move first. Constraining a head that has already moved is wasted. Ouroboros loses more as side B.

**The champion must do all of these:** hunter-grade opening economy on compact maps, ouroboros-grade survival, and a crown everywhere.

### 5.3 Strengths and weaknesses by line

| Line | Strengths | Weaknesses |
|---|---|---|
| **Ouroboros** (v10) | Best open-map play and conversion; lowest deaths; unified evaluation; params.py variants; strongest harness for replay forensics | Compact-map openings; large 1,750-line single file (term proliferation, few ablations); Python CPU headroom about 50% |
| **Hunter** (v14/v20) | Best compact-map economy; the only encirclement tactics and multi-ply survival search; C++ headroom; excellent per-version measurement hygiene | No crown (round-500 losses); 36% of deaths self or wall; fixed ladder resists tuning; v20's extra comms/scouts cost points against the field |
| **Kraken** (v04) | Length conversion; bed prediction; relay gossip; CFG-everything | Body crashes (56% of deaths), wall deaths; 3-segment children; stale sonar origin (GPT K4) |
| **Leviathan** (v07) | Cleanest code; equivalence and regression testing; net-material accounting; confirmed-pearl sprint funding | Under-produces; teammate info unused; no crown; weakest in the field |
| **Hydra** (v06–v10) | Pack hunting from gossip; cheap C++; good self-criticism in reviews | Inherited ladder self-harm; tuned combat when the losses were economic; 6-bit id aliasing; dominated by hunter-v14 |

---

## 6. Parameterisation spec (what makes the game "just tuning")

- All tunables live in **one table** at the top of the bot.
  - Python: `P` / per-role `RP`, overridable by `params.py` (`PARAMS = {...}`).
  - C++: `params.h` with `constexpr` values, generated for variants.
  - Keys are `component.name` or `role.name` (for example `prod.split_min_len`, `hunt.max_chase`).
- **Map class** is an input: `compact` (≤625 tiles) or `open`. Doctrine parameters are tables keyed by (map class, phase).
- **Phase** defaults: opening 0–40, midgame 40–crown_start, consolidation crown_start–feed_start, endgame feed_start–500. State triggers (unit parity, map knowledge) can replace the round thresholds if measured.
- A new feature ships with a **neutral default** (weight 0, or the old behaviour). The variant that turns it on is the experiment.
- Document each parameter's range and meaning next to it. A parameter without a documented consumer is deleted.
- The minimum doctrine vector every core bot should expose:
  - `split_min_len`, `units_target(t)`, `λ_unit(t)`, `role_mix(phase)`, `scout_quota`
  - `trade_parity`, `max_chase`, `crown_start`, `crown_demote`, `feed_start`, `feed_max_len`, `feed_range`
  - `prepos_pearls` (bed pre-positioning on/off), `p_strike1..3`

---

## 7. Best practices (learnt across all lines)

**Measurement:**

- Measure before building. One loss autopsy that states one mechanism is worth more than ten sweeps.
- Report by map class and by side, always. Totals hide the compact/open split, which is the main structure of the game.
- Judge against the gauntlet, not your previous version. Within-line wins that lose ground against the field are the most common failure: hydra v07–v10, hunter v20 vs v14, ouroboros v11.
- Deterministic engine: a 20-game screen is exact for those 20 games and says little else. Add map variants for fresh samples, and keep a hold-out variant set you never tune on.

**Engineering:**

- Refactors must be **action-stream equivalent** (the leviathan practice). A behaviour change is a separate version.
- Price CPU at promotion: sandbox big_empty, p99 < 60M, max < 80M.
- Python pools locally need `--timeout 1200`. The default 180 s times out on 64×64 maps and corrupts comparisons.
- 2-segment children. Exact simulation for every move. Only confirmed pearls fund sprints. Lifetime ids need at least 16 bits in packets.

**Doctrine:**

- Every sonar packet kind needs a named consumer and an ablation result.
- A crown is mandatory by round 500. Pick one, protect it, feed it.

---

## 8. Split → iterate → converge

### 8.1 Tracks

- **Core track: Claude (Ouroboros) and GPT (Leviathan).**
  - Build the strongest possible bot on the §4 architecture.
  - Both should expose the §6 parameter table and the §4.3 component boundaries, so components can be swapped between the lines and compared one at a time.
  - Claude's current plan: `docs/ouroboros-macro-spec.md` §13.
    - P0: baseline and ablations.
    - P1: module refactor with equivalence (`v12-core`).
    - P2: correctness fixes.
    - P3: compact-map opening economy.
    - P4: map knowledge.
    - P5: automated tuning.
    - P6/P7: aggression and endgame.
- **Exploration track: Kimi (Kraken) and GLM (Hydra).**
  - Build real, competitive bots aimed where data is thin. Each exploration names:
    - the hypothesis;
    - the component it would feed back into;
    - the measurement that would prove it.
  - Good targets now:
    - **Compact-map specialist.** Can anything beat hunter-v20 on compact maps and variants? Try opening books by map class, bed pre-positioning, split thresholds of 3–5, early trade doctrine.
    - **Open-map crown specialist.** How early should the crown start, how big should the escort be, and is crown-kill aggression worth it on 64×64?
    - **Aggression extremes.** Parity-priced strike doctrine; trap tactics inside an evaluator; hunting the enemy crown.
    - **Information.** A zone summary protocol, symmetry inference (mirrored terrain and bed timers), claim packets. Measure consumer value, not packet count.
    - **Late replenishment.** Does splitting after round 380 help against swarms? (Ouroboros makes 0 births then.)
  - Bad targets: re-tuning parameters where sweeps are already flat; porting a ladder you have not measured against the gauntlet.
- **Hunter (user).** Continues independently. Its v14 and v20 are gauntlet references. Highest-value addition identified by three reviewers: a crown.

### 8.2 Cycle

1. **Unifier sets up** (start of cycle):
   - run the gauntlet round-robin (and any new candidates);
   - update `FRONTIER.md`, component table §4.3 and §11;
   - archive dominated bots;
   - post the cycle's focus questions.
2. **Lines work in parallel.** Each line ends the cycle with at most **2 candidates**, each with a README carrying its numbers.
3. **Unifier gauntlet** (end of cycle):
   - every candidate against the gauntlet, 11 maps plus variants, both sides;
   - sandbox CPU for Python bots on the big maps.
4. **Unifier prunes and converges:**
   - A bot is **dominated** if some active bot of the same cluster is at least as good on every set (compact, open, each gauntlet opponent) and better on at least one, with no unique strength worth keeping.
   - Dominated bots move to Archived.
   - The gauntlet stays at **6 bots or fewer**. There must be at least one representative per live cluster, including one bot that beats the current champion somewhere.
   - Component winners go into §4.3. Losing implementations of a converged component stop being maintained.
5. The unifier writes `docs/cycles/cycle-NN.md` (standings, flips, decisions) and a changelog line in §11.

Suggested unifier: alternate between Claude and GPT, or the user decides. The unifier must not promote its own line without the gauntlet numbers.

---

## 9. The iteration loop (per line)

### 9.1 Loop

1. **Observe.** Report a gauntlet run. Split by map class and side. Autopsy losses with replays until you can state *one* mechanism. Things to look at:
   - pearls, splits and units in rounds 0–30 (`phase.py`);
   - death causes (`deaths.py`);
   - longest dragon and total length at round 500;
   - who initiated head-to-heads;
   - newborn deaths within 10 rounds.
2. **Hypothesise.** One sentence, for example "we lose compact maps because we split 3× slower in rounds 0–30".
3. **Adapt.** Try a parameter variant first; add a feature only if no knob exists. Give it a neutral default.
4. **Screen.** Run the maps where the mechanism shows, against 2–3 opponents, both sides.
5. **Benchmark.** Run the full gauntlet plus variants. Use `compare` against the base and read the flips.
6. **Promote or archive.** Promote if the target set gains at least +4 net, no set drops more than 3 net, and CPU is within the gate. Write the README either way.

### 9.2 Standard benchmark sets

- **G:** gauntlet × 11 maps × 2 sides.
- **G+V:** G plus transposed and flipped variants.
- **Compact** and **open** subsets of G+V.
- **J:** sandbox, big_empty and trauma.
- **Hold-out:** new variants never used for tuning.

### 9.3 Ledger

Record one JSON line per game:

```
{bot, base, opponent, map, map_class, side, result, win_type, round,
 our_longest, their_longest, cpu_p99, cpu_max, cycle}
```

The raw ledger stays in `build/`. Put summary tables in the README and in the cycle file.

---

## 10. Model and compute guidance

These are recommendations only; the user decides.

- **Top tier** (Opus 5.5, GPT-6 Astra): diagnosing losses from replays, large refactors with equivalence checks, the unifier role.
- **Workhorse tier** (GPT-6 Sol, Sonnet-class): implementing well-specified components against this spec and a gate. Most exploration work fits here once bots are modular.
- **Cheap tier or plain scripts** (GPT-6 Luna, Haiku-class): running benchmarks, sweeps and ledgers. Better still, run these as scripts overnight and read only the summaries. A model watching match chunks wastes most of its tokens.
- Modular bots (about 300-line files) cut per-task context sharply. That is a reason to do the refactor early.

---

## 11. Changelog

- **Cycle 0, 2026-09-25 (Claude, unifier):**
  - HANDOFF and ACTIVE created.
  - Gauntlet: ouroboros-v10, hunter-v14, hunter-v20, fry-v14, kraken-v04.
  - Evidence in ACTIVE. The map set is now 11 maps (Colloseum, help, qos_ages and small removed; stronghold and trauma added), so older cross-line rankings do not transfer.
