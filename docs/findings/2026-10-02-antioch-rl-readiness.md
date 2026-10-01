---
id: antioch-rl-readiness
author: antioch (P2-A Claude analyst)
kind: decision support
question: When is it sensible to start RL / learned-policy training, and in what order?
evidence: this programme's state on 2 Oct (findings cited inline); lead's hosts (only Claude lanes on the desktop / 4090)
---

## Recommendation

1. **Groundwork: start now.** It is cheap, needs no CPU that the testers use, and unblocks everything later:
   - **G1** the batched environment over the in-process engine (H-RL1), with a GPU inference server; benchmark it;
   - **G2** the H-Q8 feature encoder in Python + C++ with a golden parity test;
   - **G3** the GBT accuracy-per-KB curve for the direction decision (offline, CPU).
2. **Training: not yet.** Start it when all four entry conditions below hold, expected in about 2–4 days.
   - First run: **expert iteration with GBTs (H-RL5)**. PPO (H-RL3) only if H-RL5 plateaus.
3. **Mining stays first in the meantime.** It is still paying, and every hand result sharpens the reward and the
   features the training will use.

## Readiness, item by item

| item | state | evidence |
|---|---|---|
| rules known and verified | ✅ | era switch, queen semantics, sprint price verified by three analysts independently |
| outcome label correct | ⚠ | the engine verdict is right; `frame.py` still infers the old tiebreak on main (patch pending; carthage's branch has a fix) |
| shaped reward defined and validated | ✅ (mostly) | Φ: LOMO AUC r50 0.86 / 0.63 (elimination / RL maps), calibrated, era-transferable. The queen term is not yet estimable (queens rarely live) |
| environment | ⚠ | official engine in-process, ~10 k decisions/s/core raw; batched-inference wrapper not built (G1) |
| observation / features | ⚠ | H-Q8 block specified; himeji: split-age has held-out timing evidence; encoder and C++ parity not built (G2) |
| opponents and baseline | ✅ | base re-measured under 1.2.3 on two hosts (carthage 0.826 / 0.689, kyoto 0.836 / 0.693); arms 01–07 as opponents |
| evaluation | ⚠ | gate is economy-led; the win-led rule for endgame mechanisms awaits the director (board 19:40 UTC) |
| deploy path | ✅ / ⚠ | GBT export and parity exist (hb1); bytes per accuracy unmeasured (G3) |
| imitation data | ⚠ | opening: pre-change data is valid (post/pre field medians 1.00 at r25/r50). Endgame and queen: the field plays the queen badly (top-ten RL queen survival 0.7 %), so cloning the field cannot teach queen play. That is exactly where search or RL must add value |
| compute | ⚠ | desktop CPU is shared with carthage (the only Claude tester); RL rollouts compete for it |
| opportunity cost | ❌ (for now) | hand mechanisms still pay: 04+05 win pool +0.045 [+0.019], gen +0.017 [+0.003]; 06 +0.107 on gen RL fixtures; H-S1 (portal memory, 57 % vs 19 % die3) untested |

## Entry conditions for training (all four)

1. **The gate can judge a learned arm.** The director rules on the win-led criterion for endgame or whole-policy
   changes, and the frame patch is on main. Otherwise a learned bot that wins by conversion is rejected by the
   economy bound, as carthage-06 was.
2. **G1 benchmarked:** ≥ 2×10⁷ decisions/h with batched inference, on at most 8 cores, so carthage keeps the rest.
3. **G2 parity:** the Python and C++ encoders agree bit for bit on 1,000 replayed turns, including the queen block.
4. **Mining yield falls:** two consecutive hand arms in each active family (queen, portal, sprint) fail to move
   paired win on either panel. Until then, the next hand arm is cheaper evidence than a training run. Today the queen
   and portal families are still paying.

## Why expert iteration (H-RL5) first, not PPO

- **It keeps what works.** Ares's search plus a learned prior is the only mechanism that moved the gate in phase 1
  (+0.15 win). H-RL5 iterates that loop rather than replacing it.
- **It learns from targets the field cannot supply.** It learns from the *search's* choices, so it can learn queen play
  that the field cannot demonstrate.
- **It suits the trees we already have.** It is supervised, so GBTs work, and GBT beat MLP on all five HB-1 decisions.
- **Every iteration is a gate-testable bot.** Failure shows up after one iteration, not after a long PPO run.
- **PPO needs more of the pipeline before it can start:** the differentiable net, credit assignment over 20–40 agents,
  and the C++ net port. Start it only if H-RL5 plateaus, warm-started from the H-RL5 prior by distillation.

## What mining should prioritise meanwhile (feeds the training directly)

- **H-S1 portal memory.** A one-rule test that also tells training whether portal knowledge is a feature to carry.
- **04+05 stack plus a regime-gated 06.** This sets the base the training starts from.
- **H-V1.** Does ΔΦ rank the existing arms' win changes? It validates the shaping before any RL run depends on it.
- **The top-ten post-change sample.** Five teams have 0 post-change games; the collector request is open. Without them,
  post-change imitation of the strongest play is impossible.
