# P-7 (scoping) — Self-play fine-tuning of the cloned network on the Mac

Author: council:sugawara, 4 Oct 2026 ~21:00Z. Assigned by D-059 §B.4 (due 22:00Z). Scoping card: **no training
starts on this card**; the Chair rules with the R2 battery table in hand. File name per TEMPLATE; the Chair assigns
P-7 in INDEX.md.

## 1. Claim, rung and mechanism

- Rung: R8 in reduced form (PPO from a cloned prior, small league), entered from R2 rather than R6. Departs from the
  ladder text (R8 "only if R6 plateaus") — that departure is D-059's to make, not this card's.
- Parent: the R2 winner, if it is a network (A10 or a per-teacher A10). If the battery selects trees, this card is
  void until a network clone exists: PPO needs a differentiable policy (ExIt with trees is R6, a different card).
- **One switch:** the policy's training signal changes from teacher labels (forward/right/left) to game outcome
  under self-play, with a KL penalty to the frozen clone. Same observation, same action head, same deploy path.
- Mechanism: imitation caps us at teacher level minus imitation error (D-059 §B.4); the field's top is ~2190–2330 Elo
  vs our 1723. Outcome-trained updates can fix the clone's compounding errors on states teachers never visit (the
  DAgger argument) and can learn queen/endgame play the field plays badly (top-ten RL queen survival 0.7 %, antioch
  2 Oct).

## 1b. Precedent (D-058; sources checked in `reviews/D-058-B-precedents-sugawara.md`)

| Precedent | Method | Close in | Departs in |
|---|---|---|---|
| Hungry Geese 1st (HandyRL, 2021) | self-play RL, dedicated compute | snakes on a torus, ~1 s/move | 4 single agents, full obs; their compute ≫ ours |
| Lux S1 1st (Pressman 2021) | self-play actor-critic, per-cell action map, reward shaping | many units, grid economy | central control, full obs; a later reproduction needed **1 V100 + 600 CPU cores, ~5 M episodes** to beat it 90 % (arXiv 2301.01609) |
| IEEE microRTS 2023 (RAISocketAI, arXiv 2402.08112) | DRL; iterative fine-tuning; BC → DRL fine-tune reported as an efficient bootstrap | small-compute contest, scripted agents had won 5 years | full obs, central control |
| AlphaStar (Vinyals et al., Nature 2019) | supervised clone → league RL with KL to the supervised policy, frozen past opponents | exactly this recipe | compute ~10⁴× ours |
| MAPPO (Yu et al. 2021) | PPO, shared parameters across agents, centralised critic | decentralised agents with a team reward | small agent counts (≤ 27), no 20–40-agent snakes |

Closest overall: microRTS (clone→fine-tune on modest hardware) and AlphaStar (KL-anchored league). No precedent at
our compute with 20–40 decentralised agents under 7×7 partial observation; that part rests on evidence.

## Mechanism checks (council seat)

- **Observation legality.** The actor sees only the IO block at turn start plus its own per-process memory — the
  same encoder as the deployed clone (window planes + 66 scalars, D-059 §B.2). Required: the self-play wrapper feeds
  the actor through the **deploy encoder**, not a training-only re-encoder (antioch's H-Q8 wrapper is a subset
  encoder; its move mask is not a complete legal-action model — fix before training).
- **Critic.** A centralised critic may use privileged state (whole map, both teams, Φ's replay-wide inputs): it is
  never deployed, so there is no train/deploy skew (CTDE, as MAPPO). This also settles where Tanaka's 20:19Z point
  bites: privileged Φ is illegal **at deploy** (P-6), legal **as a training critic or potential-based shaping**
  (Ng et al. 1999; shaping by γΦ(s')−Φ(s) leaves the optimal policy unchanged).
- **Leakage.** League maps = training maps only; held-out maps (splits/heldout-maps.json) are refused by the env
  loader as in r2_battery load(). Confirmation and live use the existing frozen splits; no self-play game is ever a
  test row.
- **Simpler known methods, in order:** (i) filtered self-imitation — play the clone, keep won games' turns, re-clone
  (cheapest; no critic); (ii) ExIt with the search chassis as improver (R6, antioch H-RL5); (iii) this card. I would
  rank (i) before PPO as a one-night probe of whether outcome signal adds anything at our sample sizes. Kept as a
  dissent, not bundled.
- **Opponent pool.** Self-play against itself only exploits its own weaknesses. League = current policy + frozen
  clone + per-teacher A2/A10 clones (proxies for the field's top teams) + chassis bots. Teacher identity, not map
  identity.

## 2. Expected sign and size

- Head-to-head vs the frozen clone on training maps: +0.05 to +0.10 win share after the first 6 iterations.
- Seed-1 panels vs the clone: +0.00 to +0.03 win; transfers to the field less than head-to-head (league overfit).
- Side effects to watch: invalid-command and self-harm deaths (PPO exploration with an incomplete mask), length
  hoarding vs kills (reward = win; shaping only through Φ), map_era separation.

## 3. Falsifier and stop rule (written before any run)

- One iteration = 2×10⁷ actor decisions collected + one PPO update (≤ 4 epochs).
- After 6 iterations (≈ 1.2×10⁸ decisions; budget ≤ 15 Mac-hours at ≤ 8 cores): **stop and refute** if the fine-tuned
  policy wins < 0.55 of ≥ 200 paired head-to-head games vs the frozen clone (training maps, fixed local seeds, both
  seats), or its seed-1 panel win vs the clone is < +0.02. Also stop at once if KL(policy‖clone) per decision exceeds
  0.5 nats or invalid-command deaths per 1k dragon-turns double.
- No extension after results; a second budget needs a new D-record.

## 4. Test plan

- Entry conditions (all): (E1) the network clone is selected by D-057 §C/D-058 §C and exports in C++ at int8 with
  bit-parity on 1,000 replayed turns and ≤ 30 M points/turn incl. turn 0; (E2) **in-loop throughput measured on the
  Mac** with that network on ≤ 8 cores ≥ 1×10⁷ decisions/h; (E3) legal-action mask complete (split/cull/sprint can
  stay masked off: forward/right/left only, as the clone).
- Offline per iteration: head-to-head vs clone, KL, death mix. Panels: seed-1 screen both panels after iteration 6
  only. Live: one LS-std-1 screen if the panel passes.

## 5. Cost (measured where possible)

- **Engine with batched inference (measured, not on the Mac):** 28.63 M callback decisions/h, 7,953/s, 3.05 average
  cores under an 8-CPU cap, 698 games, untrained 36→128→128→4 MLP on a 3060 Ti (antioch, 3 Oct,
  `docs/findings/2026-10-03-antioch-batched-engine-readiness.md`). Raw engine ≈ 80 µs/decision/core.
- **A10 inference cost (measured here, 4 Oct 20:45Z):** numpy fp32 forward of the exact A10 shape (7×7×23 → conv3×3
  32 → conv3×3 32 → [1568+66] → 64 → 4, 0.88 M MAC) on one Xeon 2.1 GHz core: 0.059 ms at batch 1 (17 k/s), 25–29 k
  decisions/s at batch 8–256. So CPU inference adds ~35–40 µs/decision — below engine cost; **no GPU needed for
  rollouts**. Backward ≈ 2× forward → ~8 k samples/s/core for updates in numpy; torch/MPS faster.
- **Estimate (not measured): 1–3×10⁷ decisions/h on 8 Mac cores** with A10 in the loop. Decisions per real game are
  not in the docs (antioch's untrained-policy games averaged 713); at 5–15 k/game that is ~1–6 k games/h.
- **Hours to a first league iteration:** engineering 1–2 days (PPO learner with shared parameters, deploy-encoder in
  the wrapper, complete mask, C++ export path already needed by R2) + ~1–2 h compute per iteration. First iteration
  ≈ day 2; falsifier readout ≈ 15 Mac-hours later (two nights).
- **Scale gap:** 1.2×10⁸ decisions ≈ 10–25 k games vs ~5 M episodes for the Lux S1 reproduction: two to three
  orders of magnitude less. The KL anchor to the clone is what makes this budget plausible at all.
- **Displaces:** the Learner slot under HEAVY.lock (Evaluator panels > Learner > Data) for ~8 cores overnight;
  R2 battery refits and A2 per-teacher fits if run concurrently; Hinata's time on R1/V-legal. Panels keep priority.

## 6. RL translation (D-044)

- Observation: the deploy encoder's window planes + scalars at turn start; per-process memory only.
- Action: forward/right/left (other actions as the chassis does them, unchanged).
- Value/reward: terminal win/loss (+ round-limit tiebreak per engine), potential-based shaping with Φ; centralised
  privileged critic, training-only.
- Demonstration: none during PPO; the clone enters as the initial policy and as the KL anchor.

## 7. Numeric predictions

- P(E2: A10 in-loop ≥ 1×10⁷ decisions/h on ≤ 8 Mac cores) = **0.60**.
- P(head-to-head ≥ 0.55 vs clone after 6 iterations) = **0.45**.
- P(seed-1 panel Δwin ≥ +0.02 vs clone after 6 iterations) = **0.25**.
- P(a later LS-std-1 live promotion from this line within the season) = **0.15**.
- Expected effect if it works: +0.02 to +0.05 panel win per two-night budget, falling per iteration.

## Dissent (author's own)

- Run the filtered self-imitation probe (§ simpler methods, i) first: same wrapper, no critic, one night; if outcome-
  filtered re-cloning moves head-to-head < +0.02, PPO at 2–3 orders less compute than precedent is unlikely to do
  better.
