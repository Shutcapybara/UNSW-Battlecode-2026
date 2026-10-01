---
id: antioch-queen-features-learned-track
author: antioch (P2-A Claude analyst)
kind: proposal
question: Which queen features should every evaluation and learned model see, and what does the standard learned-policy approach for this class of game look like under a 4 MiB upload?
evidence: the post-change queen tables (docs/findings/2026-10-01-antioch-era-and-queen.md); carthage-01/02/06/07 panels; the verso/hb1 prior budget (claude/verso-status.md); prior art from public competitions of the same shape (below)
---

## 1. What this game is, in known terms

- **Formally** it is a decentralised partially observable Markov game (Dec-POMDP, two teams):
  - many homogeneous agents per team, each seeing a 7×7 egocentric window, on a torus with portals;
  - a narrow broadcast channel (sonar), simultaneous growth/split/death, a fixed horizon and a terminal tiebreak.
- **The nearest public prior art:**
  - **Kaggle Hungry Geese (2021).** Multi-snake on a torus, simultaneous moves, starvation. The top solutions were:
    - behaviour cloning on the leaders' episodes;
    - then RL fine-tuning by self-play (HandyRL, IMPALA/PPO style) with a small ResNet on an egocentric, torus-wrapped board;
    - often a shallow search (MCTS or 1–2 ply) on top, with the net as prior and value — the AlphaZero recipe at small scale.
  - **Kaggle Lux AI (2021, 2022).** Many units, grid resources, a time limit per turn. Winners used:
    - imitation learning from the top agents' replays with a UNet-style CNN and per-unit action heads (season 1);
    - PPO self-play from scratch on a fast vectorised simulator (season 2), with heavy reward shaping early and
      win/loss later.
  - **Halite I–IV (Two Sigma).** Multi-unit resource collection. Rule bots won some seasons. The strongest ML entries
    were imitation-learned (gradient-boosted trees or CNNs on per-unit features). They lost mostly on coordination
    and tail cases.
  - **Battlesnake.** Search (alpha-beta / MCTS) with hand-written evaluation dominates. Learned value functions help
    when the CPU allows.
  - **MIT Battlecode.** Bytecode limits make it overwhelmingly rule-based with tuned weights. That is our CPU-budget
    regime, but our 4 MiB and 30 M points/turn are far looser than Battlecode's bytecode cap.
- **The standard pipeline, in order:**
  1. imitation (behaviour cloning) from strong replays;
  2. self-play RL with one policy shared by every agent (parameter sharing; centralised training, decentralised
     execution: MAPPO-style);
  3. a league or opponent pool against forgetting and cycling (AlphaStar-lite: past selves + the field's mimics);
  4. compress the result to the deploy budget (quantise, prune, distil to a smaller net or trees);
  5. optionally keep a shallow search with the net as prior/value.
- **Where we are on it:**
  - Steps 1 and 5 already exist in pieces: Heartbreaker direction GBT as a prior inside Ares's search
    (`hb1-14-prior-r540`, `verso-05`). That is the only mechanism that moved the gate in phase 1 (win +0.15).
  - Steps 2–4 do not exist.
  - The blocker is not model size. It is **simulator throughput**. Revised 2 Oct: the official engine runs in-process
    at about 10 k decisions/s per core (H-RL1), roughly 10⁸ agent-decisions/h on the desktop when the CPU is free.
    A real-bot panel game is 20–40 k decisions, so that is enough for BC-initialised PPO runs of 10⁸–10⁹ decisions in
    hours to a day.

## 2. Budget arithmetic (4 MiB zipped, 30 M points/turn, first-turn boot)

- **The current GBT prior:** 1.5 M nodes, about 3.4 MiB as source text, boot about 7.8 M points (verso). Trees are an
  expensive way to buy capacity in *bytes*.
- **A small conv net.** Input: 7×7 × 12 channels (terrain/kelp edges, own/ally/enemy bodies, heads, pearls, beds,
  portals, last-seen age) + 32 scalars (§3 queen block, length, round, mode). Layers: 2 × conv3×3 (32 ch) → dense 64 →
  heads (4 directions + sprint length + split size + value).
  - About **115 k parameters**: int8 ≈ 115 KB, about 300 KB as hex text. That is under a tenth of today's prior.
  - About 120 k MACs per dragon-turn. At 20–40 dragons that is 2.5–5 M MACs per turn.
  - It must be probed with `arena.py --sandbox` (the judge prices points, not MACs). A GRU(64) carrying accumulated state
    (L34) adds about 25 k parameters.
- **GBT alternative:** a few hundred trees of depth 6 on §3's scalar features is about 50–200 KB. That is cheap and
  proven in-house (`tools/hb1/cpp/gbt_parity.cpp`, golden parity tooling exists). It cannot see the spatial view except
  through hand features.
- **So both fit with room to spare.** Even a net plus today's GBT prior would fit if the prior were cut to 1,000 trees.

## 3. Queen feature set (H-Q8) — one block every evaluation and every learned model should get

Computable in-bot from the 7×7 view, the id scheme (queen = id 0 for A / 1 for B; ids interleave by team parity), sonar
(H-Q6) and the round:

| group | feature | why (pointer) |
|---|---|---|
| identity | `is_queen` (own id = queen id) | everything below is conditioned on it |
| state | own queen alive (known / inferred), age of that knowledge in rounds | H-Q7 modes; 71 % of side-rounds are queenless |
| | enemy queen alive (seen / inferred), age | H-Q7; 98 % of enemy queens are dead at RL today |
| | `mode` ∈ {turtle, hunt, longest-race, queen-race} | H-Q7 |
| | rounds remaining; RL-likely map (regime selector, hb1-21) | the queen only matters at r500 |
| | pocket map (queen spawns in a dead end) | Slithery / Autarky / PD: the queen level is moot |
| geometry | own queen's last-known position and distance from me | escorts / feeders (H-Q5, H-Q2) |
| | enemy queen's last-known position, distance, staleness | H-Q4, H-Q6: 25 % visibility, median gap 5 rounds |
| exposure (queen) | enemy heads within 3; reach-weighted enemy heads (each counts if `dist ≤ 1 + ⌈L_enemy/4⌉`, the 1.2.3 free sprint) | hazard 5 / 34 / 76 per 1k rounds at 0 / 1 / 2+ heads within 3 |
| | ally heads within 2 (crowding) and within 3 (escort) | carthage-06: ally kills 97 vs enemy 45 once enemy head-ons are removed |
| | free cells reachable in 5 (trap, L24 band ≤ 8); kelp edges at the head | saved head-ons return as wall/body deaths (carthage-06) |
| | rounds since the queen's own last split | himeji: post-split exposure RR ≈ 7–8 |
| race | own queen length; last-seen enemy queen length; margin | the both-alive tiebreak (H-Q2) |
| | queen's rank among own dragons; distance to the nearest bed / corpse pearl | feeding (TT: cull beside the long one) |

**H-Q8 claim.** Adding this block lifts any learned or tuned model more than any single hand rule built on the same
quantities. Hand rules are what carthage-01/02/06/07 tested; each fixed one hazard and moved deaths elsewhere.
- **Falsifier:** a GBT direction/split model with the block vs without it, on the same training data, shows no gain in
  held-out decision accuracy on queen turns and no change in queen alive@490 in a panel.
- **Size:** offline fit plus one panel (pool + gen, seeds 1–3).

## 4. The learned-policy track (H-RL1 – H-RL4)

| id | step | claim | falsifier | size / prerequisite |
|---|---|---|---|---|
| H-RL1 | environment | **Revised 2 Oct: no reimplementation needed.** The official 1.2.3 engine runs in-process: `unswbc.engine.EngineModule.run(map, bot_reply)` calls Python once per dragon turn with the exact observation text the bot receives. Measured with a trivial policy (`tools/antioch/rl/engine_bench.py`): about **10 k decisions/s per core** including start-up, about 80 µs per decision. With ~12 free cores that is ~10⁸ agent-decisions/h raw, and ~2–5×10⁷/h once batched GPU inference is in the loop. The claim: a vectorised wrapper (one engine per process or thread, a shared GPU inference server batching across games) sustains ≥ 2×10⁷ decisions/h. | < 5×10⁶ decisions/h with batched inference | about a day of engineering; exact rules for free, so no parity work |
| H-RL2 | behaviour cloning | A shared per-dragon conv policy (§2 shape, §3 block) cloned from the top ten's post-change replays plus the H-Q1 mimic matches hb1's direction accuracy (≥ 0.83) on held-out turns, and adds split/sprint heads. | held-out direction accuracy < hb1 GBT's 0.829, or the panel win of the net-as-prior < `hb1-14` | the corpus (now 78 k games; the top ten's post-change sample grows daily); 4090 |
| H-RL3 | self-play fine-tune | PPO with parameter sharing from H-RL2. Reward is the terminal win under the 1.2.3 tiebreak, with shaped queen/material terms annealed to 0. The opponent league is past selves + hb1-14 + field mimics. The result beats its BC parent on the gate panels. | no win gain over the BC parent after 10⁶ self-play games | needs H-RL1 |
| H-RL4 | deploy | int8 net (≤ 300 KB text) as policy prior + value inside Ares's search (the AlphaZero-lite form that already worked with the GBT prior), or standalone if the search adds nothing. | over 30 M points/turn or 4 MiB; or the panel win ≤ the GBT-prior bot | `arena.py --sandbox` probe |

**Recommended order.**
- **Start now, cheapest:** H-Q8 as GBT features. Then H-RL2 as BC + net-as-prior. It needs no new simulator and reuses
  the hb1 prior's plumbing.
- **H-RL1 is now short:** the engine is the environment. The long pole moves to:
  - credit assignment (20–40 agents, a terminal reward at r500: shaped rewards and per-agent value heads, as Lux S2);
  - a C++ port of the observation encoder and net for upload, with a golden parity test (done before for the GBT);
  - CPU contention with the testers' panels: a director scheduling call (the Mac's 18 cores can host rollouts too).
- **Ledger:** L16 / L27 / L34 cover parts of this. Proposed: a new row for the learned-policy track at 0.6 (H-RL1 now cheap).
