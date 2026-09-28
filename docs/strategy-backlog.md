# Strategy Backlog

Priorities are ordered within each tier. Combat changes must remain conservative
when enemy size or team counts are uncertain.

The 18 live replay notes for 28 September are recorded in the
[Tyr V01 loss review](findings/2026-09-29-tyr-v01-live-loss-review.md). They
prioritize distributed early portal and center access, survival of long dragons
under dash or wall threats, and lower-cost feeding in dead ends. The submission
attribution is best-supported by the upload time and active status; the battle
payload did not expose historical submission IDs.

## P0: Combat Advantage

1. [ ] Add lead-aware equal-size kamikaze attacks. Permit an attack against a
	 visibly equal-sized enemy only when the friendly team has a confirmed unit
	 lead, the target size is reliable, and the trade improves survival or team
	 control. Preserve route, body-collision, and retreat safety checks.
2. [ ] Add significant-lead kamikaze attacks against smaller enemies. Define
	 and tune a significant unit lead using both an absolute and relative margin;
	 never trade a dragon based only on an uncertain or stale enemy count.
3. [ ] Add combat regression tests for equal-size targets with and without a
	 unit lead, and for smaller targets under ordinary versus significant leads.
	 Validate both single-step and multi-step attacks.
4. [ ] Improve enemy team-size estimates and confidence tracking so kamikaze
	 decisions distinguish visible facts, sonar reports, and stale observations.

## P1: Team Coordination And Growth

5. [x] Add directional 64-bit sonar messages for teammate position, length,
	 and round.
6. [ ] Extend sonar state with role, pearl sightings, and portal discoveries
	 without suppressing safety signals such as `MOVE_ASIDE`.
7. [ ] Add persistent estimates of the team's longest dragon and friendly
	 dragon positions and lengths, including decay and conflict resolution.
8. [ ] Tune the growth transition using round, team size, largest-dragon length,
	 pearl availability, enemy threats, and map type instead of fixed thresholds.
9. [ ] Add threat-aware endgame behavior: when no nearby enemy threat exists,
	 route pearls toward the largest friendly dragon or protect its growth
	 corridor.

## P2: Exploration And Target Selection

10. [ ] Improve portal incentives so smaller dragons explore safely while the
		largest dragon grows when appropriate.
11. [ ] Compare portal-trip reward against ordinary pearl routes before
		committing to a portal journey.
12. [ ] Compare Manhattan teammate distance with known-map route distance before
		relying on closest-dragon pearl ownership.
13. [ ] Use remembered pearl observations for scoring while treating stale or
		unseen pearls as uncertain rather than guaranteed.
14. [ ] Improve segregated-map behavior with exploration and region-ownership
		heuristics, especially on `schooltime`.

## P3: Validation And Release

15. [ ] Run the two-run small tournament workflow after each strategy change:
		focus the newest and second-newest versions against the same three-version
		pool on every map.
16. [ ] Run medium and full tournaments before submission, comparing focused
		wins, draws, losses, points, and errors.

## Versioning

- `fry-v01-danger-levels` through `fry-v10-pearl-seeker-center`: earlier
	strategy snapshots and variants.
- `fry-v11-size-aware-hunters`: baseline size-aware hunter.
- `fry-v12-stateful-size-aware-hunters`: persistent map, pearl, and enemy memory.
- `fry-v13-stateful-size-aware-2`: pearl claims over sonar messages.
- `fry-v14-stateful-size-aware-3`: closest-visible-teammate pearl ownership without explicit claims.
- `hunter-v01-team-growth`: team-length estimates and endgame growth, copied from fry-v14.
- `hunter-v02-team-growth`: adaptive growth timing; the largest known teammate has pearl priority, with a two-segment safety buffer against known enemy size.
- `hunter-v03-team-growth`: smaller dragons may safely explore completed portal trips when at least four teammates are alive.
- `hunter-v21-emergency-portals`: V20 plus a trapped-dragon escape through an adjacent portal when every ordinary exit is blocked; experimental, 10W/12L vs V20 with no errors, swept 0–2 on Stronghold.
- `hunter-v22-frontier-exploration`: V21 with frontier-first no-food movement, stronger revisit avoidance, and a small shortage-based group of portal scouts; went 9W/13L vs V21 across all 11 maps and both sides, with no errors.
- `hunter-v23-supported-arrival-feed`: V22 with radius-four support-gated trade-ups, arrival-time bed targeting, a bounded 4x4 resource-density exploration bias, and guarded late crown feeding; native focus gauntlet 71W/137L overall, 15W/11L vs V22, zero runner errors, not promoted.
- `kraken-v01-roles`: fixed-role scouts, hunters, and gatherers relaying map memory over sonar.
- `kraken-v02-bigmap`: big-map production and endgame growth, brawl-mode small maps, ally-head collision guards, and metered BFS with portal-local cache invalidation.
- `kraken-v03-judge-safe`: snapshot of kraken-v02 after sandbox CPU hardening; used as the stable bot-pool evaluation candidate.
- `kraken-v04-eval`: v03 with a kbench-parameterised CFG (KBENCH-PARAMS override block); identical behavior, the baseline for eval-weight sweeps.
- `loki-v01` (teacher ranker): trained Bifröst v01 baseline from public ranked submission #7771; native six-map panel 47–13, 40–8 on 48 matched external fixtures versus Bifröst v01's 43–5, and original sandbox screen 0–12 with 93 Loki CPU-limit events.
- `loki-v02-teacher-ranker`: v01 model/policy with sparse inference, cached geometry, tail-index simulation, and safe candidate pruning; 7–5 sandbox vs Bifröst v01 with zero Loki faults. Native Fenrir v18 panel 11–19 on 30 games; partial sandbox logs had 94 Fenrir CPU-limit events and no Loki events, with Loki peaking at 94.1M/100M points. See `docs/loki-family.md`.
- `gavroche-v01-mass-preserving-opening`: Monte Christo x12 with an early rescue split for long, partially observed spawns; 5–3 vs x12 and Hunter v20 on Autarky and Prisoner's Dilemma.
- `gavroche-v02-opening-production`: v01 plus stronger early production; separate target-map screens scored 13–3, while a single full-pool screen scored 12–4. It lost one Autarky side to x12 and cascades through four length-2 splits on round 0.
- `gavroche-v03-head-preserving-opening`: v02 with a head-preserving rescue split and more aggressive production; 1–3 on the Prisoner's Dilemma screen, rejected.
- `gavroche-v04-mobile-mass-rescue`: v02 with one-shot rescue for initial spawns; 3–5 on the target-map screen, including both Autarky losses to x12, rejected.
- `gavroche-v05-map-aware-rescue`: v02 with map-aware rescue splitting; 5–3 on the target-map screen, but lost an Autarky side to x12, rejected in favor of v02.
- `gavroche-v06-first-move-rescue`: v02 with one-shot rescue for initial dragons; 4–4 vs x12 and Hunter v20, no errors.
- `gavroche-v07-paced-rescue`: allows each large tail-born piece to rescue on a later round after a movement opportunity; 5–3 vs x12 and Hunter v20, no errors.
- `gavroche-v08-map-aware-opening`: v02 cascade on larger maps and paced rescue on compact maps; 11–5 across x12, Hunter v20, Hydra v07, and Sinbad v04.
- `gavroche-v09-two-stage-rescue`: v07 with one follow-up rescue; 10–6 across the same four references.
- `gavroche-v10-balanced-rescue`: v02 with a balanced initial split; split starts 14 as 7+7 on Autarky and 11 as 6+5 on Prisoner's Dilemma. Separate screens scored 12–4; the promoted v12 snapshot scored 10–6 in the single full-pool schedule. Hunter and Hydra each went 2–0 against it on Prisoner's Dilemma.
- `gavroche-v11-tail-mass-rescue`: v10 with a four-segment original head and larger tail piece; 4–4 vs x12 and Hunter v20, no errors.
- `gavroche-v12-balanced-opening`: v10 snapshot; scored 10–6 in the full 16-game schedule, and x12 won both Autarky games.
- `gavroche-v13-tail-paced-rescue`: v09-style `SPLIT (length - 2)` with a movement opportunity before follow-up rescue; scored 12–4 in the full 16-game schedule, swept x12 4–0, no errors. Historical baseline; native tournament results, not sandbox-verified.
- `gavroche-v14-four-segment-head`: v13 with `SPLIT (length - 4)`; scored 9–7 and x12 won both Autarky games, rejected.
- `gavroche-v15-divecap`: v13 with Sinbad v07's `v_dive = 3`; 100–82 in the 182-game cross-family panel and 78–52 against five selected model-family references. Strong x06 tf-05 result (19–7).
- `gavroche-v16-informed-divecap`: v15 plus full-strength room-normalised x06-style early density gradient; 111–71 in the 182-game panel and 77–53 across those five references. Native, not judge CPU-validated.
- `gavroche-v17-half-gradient`: v16 with `info_aggro_push` halved from 2.0 to 1.0; 125–83 in the 208-game panel and 84–46 across the five model-family references (Sinbad, x06 tf-05, reconstructed sparse grad1, x04 support, Monte Christo x12). Current broad-opponent candidate; native, not judge CPU-validated. Replay-map panel: Big Empty 12–4, Prisoner's Dilemma 14–2, Trophy 9–7.
- `gavroche-v18-fused-room-flood`: reuse one flood traversal for candidate trap scoring and the early density room factor. Big Empty mirror had no visible timeouts, but peaked at 99.5M CPU; insufficient margin.
- `gavroche-v19-spatial-density`: radius-window bucket lookup for retained sonar reports. Exact against the full scan on 488,520 grid queries, including wrapped/partial buckets; CPU remained 99.1M max and 82.7–83.3M p99 on Big Empty, so this alone did not solve the budget risk.
- `gavroche-v20-bounded-feeding`: v19 plus a separate adaptation of Avery v06 feeding (length≤10, start round 410 on 64×64, die beside a visible larger crown); not benchmarked as the CPU base was still too close to cap.
- `gavroche-v21-short-sprint-cap`: v19 with all three-step sprint candidates disabled while preserving one/two-step options. Big Empty mirror completed 500 rounds at 90.7M/93.1M max and 71.2M/72.1M p99 with zero timeouts, invalid actions or runtime logs. early 46/234 screen stopped at 22–24 with zero errors after losses on all four completed Big Empty, Autarky and Queen games vs v13/v15.
- `gavroche-v22-bounded-feeding`: v21 plus delayed no-action donation from short donors to a fresh visible longer crown. not screened; inherits v21’s over-broad sprint cutoff.

- `gavroche-v23-selective-sprint-cap`: cap three-step candidates to lengths 4–7; Big Empty max 94.7M, six-map panel 46–38, but v17 beat it 34–14 across the four top family refs.
- `gavroche-v24-selective-feed`: guarded late crown feeding on v23; Big Empty max 97.3M; stopped after 4–8 in the first 12 vs v23.
- `gavroche-v25-crown-margin-one`: crown margin 1 on v23; stopped at 54/96, 21–32–1.
- `gavroche-v26-sprint-cap10` / `v27-sprint-cap9`: Big Empty max 99.3M and 99.0M/99.5M respectively; insufficient headroom.
- `gavroche-v28-gradient-window-sprint-cap`: no-op due a disabled `info_aggro_push` guard; panel interrupted at 28/96.
- `gavroche-v29-saturation-window-sprint-cap`: 40–56 on the replay-sensitive six-map panel; rejected.
- `gavroche-v30-saturated-sprint-cap`: branched directly from v17; Big Empty max 99.8M, panel 54–42.
- `gavroche-v31-saturated-divecap`: V30 plus `v_dive=3`; panel 55–41, not better than v17/V23 on the top-family aggregate.
- `gavroche-v32-supported-divecap`: V31 plus x04’s support-weighted trades; 43/96 partial panel at the user-requested pause. Resume from the frozen experiment using `docs/gavroche-resume-2026-09-26.md`.

## kraken iteration loop (2026-09-24 session)

- Method + tooling: `docs/kraken-design-framework.md` and `tools/kraken/kbench.py`
  (variant / run screen|bench|pool / analyze / compare). One hypothesis per
  variant; screen kills bad ideas fast, sandbox bench confirms, full pool
  regresses.
- v03 pool data (520 sandbox matches): 73% of losses are mid-game
  eliminations (median round 234), and ~80% of deaths in losses are body
  crashes + lost head-to-heads. Priority hypotheses: mid-phase unit target
  too low vs swarm-of-equals bots (fry-v07/v09 9W-17L), hunter trade margin
  too generous, no endgame crown role (51 round-limit losses).
- Loop validated end-to-end: v04 mirrors v03 (4-4 on screen); first sweeps
  screened: team_target_mid=40 rejected (9W-15L, losses shift to the round
  limit), hunter_trade=1 neutral (10W-14L).
- Bench baseline (`build/kbench-bench-v04`, sandbox): v04 goes 34W-36L,
  worst CPU max 67.8M (0 over budget). Confirmed: fry-v03 12-0,
  hydra-v03-grower 8-2 (kraken beats GLM's python hydra), kraken-v03 6-6,
  hunter-v03 4-8, fry-v07/v09 2-10 each (the structural weakness). Two
  big_empty hydra matches are harness wall-clock timeouts at 1200s, not
  judge failures.

## kraken family learnings (2026-09-24 session)

- The judge sandbox is the source of truth: the same bot/native-opponent mix can diverge from local runs, so every final claim needs a `--sandbox` tournament.
- Portal-rich maps exposed the worst CPU spikes because completing a portal pairing invalidated the whole destination cache. Invalidate only the cells touching that portal edge.
- Reusable BFS stamps and a 450-cell normal-map cap keep kraken-v02 below the 100M turn budget while preserving the full 26-0 sweep over fry-v03.

## hydra family learnings (2026-09-24 session)

- Judge budget: every stdout write costs 2.5M CPU points and the sandbox
  runs python unbuffered, so a turn's output must leave in ONE write
  (including the per-turn `PROTOCOL 3` handshake line).
- A fresh split child's first metered turn must be a cheap boot turn:
  interpreter boot + imports eat most of the 100M budget; full logic on
  turn one exceeded it and the kill-restart cascade took out parents too.
- Collision is checked before movement: stepping onto our own tail is
  always fatal. The body trail must record the midway cell of sprints and
  must not append on split (no-move) turns.
- The boot turn must check the edge on OUR side of the neighbour tile
  (`get_opposite`), not the far side.
- Portal gossip cannot hash portal ids: portal-mesh maps carry ~1500 ids
  and 16-bit hashes collide into poisoned pairings.
- fry-v03 does NOT sprint broadly (95% single steps); its economy edge on
  big maps is the plan_trip beam-search harvest plus constant splitting
  (children form even under threat). hydra still loses the length race
  there ~2:1; porting the trip planner is the main hydra-v03 item.

## hunter-v03 matchup session (2026-09-24, later)

- Matchup evaluation is deterministic within one runner context but the
  engine seeds pearl draws per invocation: trust repeated full both-sides
  tournaments, never single games.
- hunter-v03 only attacks visible-BIGGER dragons, so a swarm of 3-4 segment
  dragons is invisible to its offense (hydra-v03's swarm-of-equals + round
  340 split freeze: 9-17 -> 11-15).
- The decisive edge was forking hunter-v03 to protocol 3 (hydra-v06-echo):
  4-direction status sonar, enemy sightings gossiped on two sonar slots with
  pack hunting, echo-radar stalker fleeing for the grower: 13-2-11.
- Map-wide radio yielding (owns_pearl over sonar positions) starved the
  richest map (big_empty 2W -> 2L) - keep yielding vision-local.
- Duplicating the sighting on a third sonar slot starved the status
  broadcast and cost 4 maps: crown election needs the status flowing.
- Next target: fry-v14-stateful-size-aware-3 tops the field (174 vs
  hydra-v06's 159 in the 5-bot round-robin).

## fry-v14 matchup session (2026-09-24, evening)

- The v06 field losses to fry-v14 (11-2-13) are a **numbers war**, not a
  combat problem: verbose Colloseum replays show head-to-head kills are
  perfectly symmetric (12 vs 12), but fry split 28 times while hydra split
  9. Both bots share identical `SPLIT 2`-at-length-4 code, so the gap is
  food conversion, and Colloseum (countdown-100/250 tiles, 66-round games)
  is a corpse-fed economy: the winner of the early race hoovers the dead
  and compounds; the loser starves. Mirrors confirm winner-take-all
  dynamics (winning side reaches 33-40 units).
- Gate experiment (hydra-v07-farm-first: gossip chase only when
  `units >= 6 && length >= 4`) did NOT close the split gap in single games
  — the chase is not the main feeding cost. Do not stack more gates on it
  before measuring.
- fry-v14's structural edges over the hydra line (found by diff):
  (a) whole-swarm `growth_action()` at round 400 vs hydra's
  largest-only conditional growth — the round-limit length race (help
  lost on length both sides, ~1700 deaths/game meat grinder), and
  (b) `owns_pearl` gating in the growth BFS so 64 farmers deconflict.
  hydra-v08-claims copies both.
- fry-v14 is still protocol 2 (constant filler sonar); its sonar channel
  is idle, so hydra's radio advantage stands.
- tools/autopsy.py needed bot-name->path resolution (`unswbc run` takes
  paths, not names); fixed. Single verbose games swing wildly with the
  per-invocation pearl seed (v07 mirror: 199 splits one game) — the
  tournament is the only counter.
- Replay diagnostics: `tools/leviathan/replay.py FILE.replay` (GPT's)
  decodes packed capnp replays to pearls/splits/deaths/trades per team.
  hydra additions: `tools/hydra_replay.py` (per-round series + head
  positions).
- Head-to-head autopsies vs fry-v14 (replay stats): deaths and initiated
  trades are always SYMMETRIC; the whole matchup is decided by pearl
  conversion (fry 88 vs hydra 18 on a Colloseum loss). fry out-splits
  hydra ~3:1 and compounds; hydra's dragons each eat ~2 pearls (barely
  breeding length) — per-capita feeding is similar, births are not.
- Self-mirrors are lopsided (25v72, 199v35 splits): individual games are
  winner-take-all coinflips. The only stable facts: (a) fry-v14 beats
  EVERY bot in the field on Colloseum/Colosseum, both sides, including
  fry-v03 — treat those 4 screen games as the field's tax; (b) fry-v03
  beats fry-v14 on schooltime both sides, so schooltime is winnable;
  (c) most other maps resolve as side-A coinflips.
- Variant screens vs fry-v14 (26 games each, single runs): v06 11-2-13,
  v07-farm-first 10-2-14 (gossip chase gated on units>=6 && len>=4),
  v08-claims 9-2-15 (+ whole-swarm r400 farm switch + owns_pearl in
  growth BFS; fixed one help side), v09-lanchester 8-2-16 (+ retreat-
  while-outnumbered: won default both sides but lost big_empty both),
  v10-farmclean 10-2-14 (= v08 minus stalker-flee; recovered big_empty
  side B). All inside the noise band; repeats decide promotion.
- DETERMINISM (corrects an earlier note): `unswbc run` replays a given
  (map, botA, botB) identically every time — repeated tournaments return
  byte-identical records. One 26-game screen is an exact measurement of
  that matchup, not a sample. "Pearl draws seeded per invocation" was
  wrong for local non-sandbox runs.
- Field round-robin verdict (5 bots, 260 games): hydra-v10 150 pts vs
  hydra-v06's 159 in the same field. Per-opponent: the v07 gossip gate
  gave back 3 wins to hunter-v03 (10-14 vs 13-11) — the ungated pack
  chase is load-bearing against hunter-family bots even though it looks
  passive against fry-v14. Net: v06 stays flagship; fry-v14 (177 in this
  field) remains ahead of the whole hydra line.
