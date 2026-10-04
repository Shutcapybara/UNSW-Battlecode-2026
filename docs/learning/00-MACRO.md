# Phase 3: the learned policy (macro structure)

Director, 4 Oct 2026. This document supersedes the hand-rule loop as the programme's main line (D-044 sets the
principle; this sets the machine). Handoff prompts are in `docs/learning/prompts/`. The decision log continues in
`docs/findings/2026-09-28-director-decisions.md`, with entries D-045 and later.

## 0. The problem class, and the known solution we are copying

- **Formally:** a two-team, decentralised, partially observable Markov game.
  - Each side has 20–40 homogeneous agents. Each agent sees a 7×7 window.
  - The board is a torus with portals. Agents communicate over a narrow broadcast channel (sonar under protocol 3).
  - Moves are simultaneous, but resolve in id order within a round.
  - There is a fixed horizon and a lexicographic terminal tiebreak: queen → longest → total.
- **Nearest solved relatives:**
  - Kaggle Hungry Geese (2021): multi-snake on a torus. The winners used behaviour cloning, then self-play RL with a small ResNet, then a shallow search with the net as prior and value.
  - Lux AI S1/S2 (2021/22): many units on a resource grid. The winners used imitation from top replays (UNet with per-unit heads), and later PPO self-play from scratch with heavy early reward shaping.
  - Halite I–IV: imitation-learned GBT/CNN entries were competitive with rule bots.
  - Battlesnake / MIT Battlecode: search with a tuned evaluation under strict CPU limits. That is our deploy regime.
- **The standard pipeline, in order:**
  1. behaviour cloning (BC) from strong replays;
  2. a value function;
  3. BC prior + value inside a shallow search (AlphaZero-lite);
  4. expert iteration / self-play with parameter sharing (MAPPO-style), against a league of past selves and mimics of the field;
  5. distil to the deploy budget.
- **What we already have:**
  - The search: carthage-05, Ares lineage.
  - A GBT prior cloned from one top team and deployed inside that search (hb1-14, Heartbreaker). It is the only learned piece that ever moved the gate: +0.15 win.
  - Φ, a 5-feature win-potential model.
  - The FRAME7 decoder, the S-1 store (51k games, 7k post-m2), and the official engine in-process at ~10k decisions/s/core.
  - The hub (collector, uploads), the D-042 gate, and live-map panels.
- **What we are missing:** a per-dragon observation encoder with Python/C++ parity, multi-head labels, a value model that sees the queen, and a closed train → evaluate → deploy loop.
- **We do not invent:** a new RL algorithm, a new architecture family, or new evaluation statistics. Every component below has a named precedent.

## 1. The complexity ladder (start small; every rung is gated)

Climb one rung at a time. A rung is passed only when its **offline gate** and its **deploy gate** (where it changes the bot) both pass. A failed rung is diagnosed, not skipped.

| Rung | Adds | Offline gate | Deploy gate |
|---|---|---|---|
| R0 | **Infrastructure:**<br>• encoder (legal-observation only) and action labeller<br>• frozen splits: held-out maps, series and fixtures<br>• model registry<br>• replay → dataset pipeline | • Python = C++ encoder, bit for bit, on 1,000 turns<br>• labels agree with HB-1 on Heartbreaker data (> 99 %)<br>• leakage audit passes | none (no bot change) |
| R1 | **V0:** a GBT value model on Φ's features plus queen terms, per regime and checkpoint | • leave-one-map-out (LOMO) AUC ≥ Φ on every checkpoint<br>• round-limit maps: ≥ 0.66 at r50 (Φ 0.63)<br>• calibration slope 0.9–1.1 | none (diagnostic only) |
| R2 | **P1:** BC direction head (GBT) on top-ten post-m2 dragon-turns, with hb1's features plus the queen block, swapped in as the prior of carthage-05 (one switch) | • held-out direction accuracy ≥ 0.83 (the Heartbreaker level)<br>• queen-turn accuracy reported separately | • D-042 win-led gate on `LIVE_MAPS_M2` + gen<br>• then the live screen (§4) |
| R3 | **One more head per rung:** split/size, then cull (invalid command), then sprint length | • per-head held-out accuracy<br>• no loss on earlier heads | same as R2, per head |
| R4 | **Feature blocks, one per rung:** enemy sprint reach B(L); body-conditioned entry capacity; unit count and the cap; sonar echoes; enemy-queen state | • ablation: held-out gain in P and/or V on states where the block is non-trivial | same as R2 |
| R5 | **V in the search:** the learned value as the leaf evaluation, blended with the hand evaluation at weight w ∈ {0, 0.5, 1} as a D-044 dose dial | • ΔV ranks past arms' paired win changes (H-V1, Spearman > 0.5) | same as R2 |
| R6 | **Expert iteration (H-RL5):** search + prior self-play and league games; refit P and V on the search targets | • iteration n+1 beats n on held-out fixtures | gate per iteration |
| R7 | **Capacity:** a small CNN/GRU replaces the GBT heads, only if the accuracy-per-KB curve shows the trees saturating | • accuracy per KB above the GBT<br>• turn-0 CPU within budget | same |
| R8 | **PPO self-play league**, warm-started by distillation; only if R6 plateaus for 2 iterations | • league Elo up against frozen past selves | same |

Rules that hold on every rung:

- One change per rung. Each rung uses the previous passed rung as parent.
- Every change ships as a switch, so the parent stays reproducible.
- Doses where a rung has a natural dial (D-044).
- Every rung carries its RL translation and registry entry.
- Hand rules are allowed only as `temporary` probes (D-044). The Schooltime cage fix (C+D) is the one shipped exception. It sits outside the ladder, and P must absorb it by R3/R4.

## 2. Roles and instances

| Role | Model | Host | Owns |
|---|---|---|---|
| **Chair** (one) | Claude Opus | Cowork, Mac-linked | final decisions (D-records); ladder state; the registry; promotion and rollback approval; the council agenda |
| **Council** (rotating, 3 seats per decision) | Claude, GPT and GLM instances | Cowork / Codex | reviews of proposals and results; independent replications; dissent |
| **Data** | Claude (Chongqing successor) | Mac native | corpus, store, encoder, labels, splits, leakage audit, the top-team knowledge base |
| **Learner** | Claude (Osaka), as a Claude Code session running **natively on the Mac** (not in the Cowork VM) | Mac native CPU; no GPU until the desktop returns | training P/V, export to C++, accuracy-per-KB curves, expert iteration and PPO later |
| **Evaluator** | any model; GPT preferred for statistics | Mac native, in scheduled slots | local panels, gates, dose curves, CPU/size probes |
| **Live ops** | Claude | Mac (hub) | uploads, activation, targeted requested battles, live screens, ranked monitoring, rollback execution |

- The Chair never runs experiments. Workers never decide promotion.
- The hub's key never leaves the hub.

## 3. The decision loop (the council)

Every non-trivial change goes through the same cycle:

1. **Proposal card.** Any instance writes it to `docs/learning/proposals/P-<n>.md`. It states:
   - the claim, rung and mechanism;
   - the expected sign and size;
   - the falsifier and the planned test (offline metric, panel, live);
   - the cost and the RL translation;
   - **a numeric prediction**: P(pass) and the expected effect.
2. **Council round.** The Chair assigns 3 reviewers, following these rules:
   - at least two different model families;
   - the GPT auditor always sits on statistics-bearing cards;
   - no reviewer reviews its own family's proposal alone;
   - seats rotate round-robin over eligible instances.

   Each reviewer writes `docs/learning/reviews/P-<n>-<lane>.md` with: agree / amend / reject; any replication done; their own P(pass); and an explicit dissent if any.
3. **Chair decision.** A D-record with: decision, owner, frozen objective, and stop rule. The Chair may overrule the council, but must answer every dissent in writing.
4. **Execution** by the owning role.
5. **Result card**, appended to the proposal: outcome against the frozen objective.
6. **Scoring.** Each council member's predictions get a Brier score in `docs/learning/calibration.md`. After 10 cards, seat weights and rotation frequency follow calibration, not model family.

**Cadence:**

- Council rounds batch every 6 hours, or immediately for promotion/rollback.
- The Chair runs hourly: reads results, advances the ladder, assigns work.

## 4. Live deploy and targeted testing

- **Pipeline:** registry entry → build → CPU/size probe → upload (`LV-<name>-<fp8>-ai`) through the hub → stays inactive.
  - Targeted requested battles: unranked, matched against the incumbent's fixtures.
  - Then a promotion decision by the Chair.
  - Then activation, ranked monitoring, and automatic rollback (thresholds frozen in D-045).
- **Rosters (live ops maintains them):**
  - **band:** the teams we actually meet in ranked;
  - **top:** the current top ten;
  - **style:** one representative per opponent style the analysts identify (keepers, culls-feeders, hunters, elimination specialists);
  - **regression:** opponents the incumbent beats, to catch breakage.

  A targeted test names its roster before it runs.
- **Statistics** (Himeji's conventions):
  - paired by opponent, map and seat;
  - score minus Elo expectation, with a whole-series bootstrap;
  - missing ≠ loss;
  - unranked and ranked are separate populations.
- **To build:** a hub control `hub-state/control/battles.json` for targeted requested battles. Today only the automatic quota filler requests battles, and the executor is in shadow mode. Live ops builds it, with tests, and redeploys it.

## 5. Top-team knowledge (an explicit asset)

- **Teachers:** post-m2 ranked replays of the current top ten, weighted by Elo and recency.
  - Exclude decoy-flagged unranked games.
  - Keep per-team labels so we can train team-conditioned clones.
- **Mimics:** BC clones of the top 5 teams, used as panel opponents and league members. They are never parents.
- **Knowledge base:** `docs/learning/top-teams.md`, one page per team, kept by Data:
  - style;
  - queen policy;
  - cull and feed behaviour;
  - opening transits;
  - known decoys;
  - matchup record against us.

  Analyst findings get folded in, with pointers.

## 6. What else is needed (beyond the five ingredients)

1. **The deadline and a freeze schedule.** No deadline is recorded anywhere in the programme. The ladder's speed, the final freeze (−72 h / −24 h / −6 h rules from the Osaka prompt) and how far up the ladder we aim all depend on it. The Chair must write it down first.
2. **Evaluation integrity.**
   - Frozen held-out maps, series and fixtures for the whole phase.
   - Train and evaluation data never overlap.
   - Discovery and confirmation are kept separate.
   - The gen twins are regenerated from `maps/live/`.

   Without this, the learner overfits the gate. Alicia's pool-shaped optimum is the precedent.
3. **A model and experiment registry.** For every artifact: data hash, code commit, features, hyperparameters, metrics and fingerprint. Promotion and rollback work only on registered artifacts.
4. **Deploy constraints as a first-class gate.** 4 MiB zip; 30 M points per turn **including turn-0 model load**; C++ inference parity. A model that cannot ship does not count as passed.
5. **Non-stationarity.** The field is moving: second-tier queen keeping rose 10 pp in two days. Required:
   - a weekly data refresh;
   - a drift monitor (live score minus Elo expectation, per roster);
   - periodic re-fits of V.

   Evaluate against the field as it is now, not as it was on the day of the data freeze.
6. **Compute and ownership plan.**
   - Which machine runs what: Mac VM (saturated), Mac native, desktop CPU/GPU, the teammate's desktop.
   - One uploader; one hub; one writer per store.
   - Time slots, so panels and self-play don't collide.
7. **The human-in-the-loop list.** What only you can do:
   - approve Mac-tied scheduled tasks;
   - run native Mac jobs;
   - lend the GPU desktop, once it is free again;
   - copy the API credential;
   - set the deadline.

   Keep it short and explicit in the Chair's status.
8. **Cost control.** The council costs tokens. Batch reviews, cap seats at 3, and skip the council for pure engineering (encoder parity, exports).
9. **Rules check.** Confirm that the contest permits training on other teams' public replays and fielding clones of their behaviour. Ask the organisers once and record the answer.
10. **Failure modes to watch:**
    - BC copies a decoy;
    - BC copies the field's mistakes (opponents also take the pearl bait);
    - the prior distribution shifts once our own behaviour changes;
    - the value model rewards the queen tiebreak on maps where the queen is irrelevant.

## 7. Transition from Phase 2

- **Pause:** Nara and Kanazawa.
- **Merge into one Data lane:** Shenzhen and Chongqing.
- **Himeji** becomes the standing council auditor.
- **One tester** (Rome) becomes the Evaluator.
  - It finishes the cage C+D (E0) arm and the H-KZ12 dial.
  - From then on it runs only ladder gates and requested dose probes.
- **Osaka** becomes the Learner: natively on the Mac for now, and on the GPU desktop once it is free (§8).
- **The git coherence task stays.** Its prompt needs your approval, so that disjoint hunks are no longer treated as conflicts.
- **The Chair writes D-045:**
  - deadline;
  - frozen splits;
  - promotion and rollback thresholds;
  - roster definitions;
  - ladder state R0.

## 8. Compute plan while the desktop is unavailable (4 Oct)

The GPU desktop is not available, and neither is any GPU. Everything runs on the Mac, which has 18 cores and is
shared with the hub, the collector and the Cowork VMs. The plan bends as follows.

- **Ladder reach.** R0–R5 are CPU-feasible: GBT heads with LightGBM/XGBoost on the CPU, and a value model the same
  way. R6 (expert iteration) is allowed at small scale only, by Chair decision. R7 (nets) and R8 (PPO) stay deferred
  until a GPU returns. This is not a loss of method: R2's GBT prior is the same kind of piece that gave hb1-14 its gain.
- **Sample, don't brute-force.** BC trains on a stratified sample: top-ten sides, decision turns weighted by phase
  and map, a few million rows. It does not train on every dragon-turn. Report learning curves (accuracy against
  rows), so we know whether more data would help.
- **Native, not the VM.** Long jobs (decode, training, panels) run as native Mac processes: a Claude Code or Codex
  session in a Mac terminal, or a command the user starts. The Cowork VM is saturated (1.2–3.9 s per game decode)
  and its calls are limited to 3 minutes; it does coordination and light queries only.
- **One heavy job at a time.** Use a lock file, `build/learn/HEAVY.lock`, naming the job and its owner. The order
  is: Evaluator panels > Learner training > Data decode. Each takes at most 14 workers (`nice 10`), leaving room for
  the hub. Data's decode backlog goes first, as a one-off: about 1 h at `--jobs 6`.
- **Shrink evaluation.**
  - Seed-1 screens on both panels for every candidate.
  - Full seeds 1–3 only for a candidate the Chair proposes to promote.
  - The live screen carries more of the evidence. Server battles cost us no CPU, only quota.
  - Build `battles.json` (Live ops) early.
- **Pause what doesn't feed the ladder.**
  - Kanazawa and Nara pause.
  - Shenzhen and Chongqing merge into Data at a reduced cadence.
  - The council runs on cloud sessions, which use no Mac CPU.
- **When a GPU returns,** the Learner moves R6–R8 there. Nothing else changes.
