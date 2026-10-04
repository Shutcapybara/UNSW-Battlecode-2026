# Antioch learned-policy entry checks and Ares rollout rate

Date: 4 October 2026. Runtime: `unswbc==1.2.5`.

This closes the three director follow-ups on whether the 1.2.5 scorecard can
judge a learned candidate, whether hand-mining has reached its stopping rule,
and how quickly the complete Ares policy can collect self-play turns. It is a
readiness audit and throughput measurement; it does not change gate policy or
authorize a learned-policy promotion.

## Results

| Check | Result | Evidence and limit |
|---|---|---|
| 1.2.5 learned-arm gate | Not ready to certify a learned candidate | `frame.py` is version 7 and decodes official engine winners from current replays. The standard `scorecard.py` still emits its economy-led ruling. The win-led Himeji rule in D-042 is scoped to 1.2.3 adaptations, and the handoff says 1.2.5 screens are not a new ruling. No ratified 1.2.5 learned-arm thresholds were found. The director needs to declare those thresholds before a learned-arm verdict can be called. |
| Hand-mining yield | Training-entry stop condition not met | Entry requires two consecutive hand arms in each active queen, portal and sprint family to fail to move paired wins on either panel. The latest Carthage 05−00 1.2.5 bundle has positive win intervals on both panels (+2.62 pp pool, +1.25 pp gen); 05−04 is inconclusive on pool and positive on gen. H-S1 was untested at the time of this audit; its later follow-up rejected one portal arm, which still does not satisfy the two-consecutive condition. Recent queen arms have not yielded a durable two-panel mover, but that alone does not satisfy the all-family condition. |
| Full-policy rollout throughput | Measured; 1.2.5 run passed | Ten serial Carthage05 self-play games (same bot in both seats), five maps and seeds 101–102, verified exactly 540 HB1 rounds / 1,620 trees. They produced 182,440 actor turns in 121.05 seconds: 1,507 turns/s or 5.43 million turns/hour. The observed fixture mix corresponds to 297 complete games/hour, heavily affected by the long `big_empty` and `stronghold` games. |

## Gate audit

`tools/analysis/features/frame.py` at `FRAME_VERSION = 7` provides the needed
official winner decoding. That means the replay data can support win-based
statistics; it does not select acceptance thresholds. The current standard
scorecard still applies the existing economy-led `gate_line`. The Himeji
win-led rule recorded by D-042 is explicitly scoped to the 1.2.3 rule
adaptations, while the Carthage 1.2.5 results are documented as fresh screens,
not a version-wide re-verdict.

Accordingly, do not label the current scorecard a ratified 1.2.5 learned-arm
gate and do not change its thresholds by inference. A director ruling must
define the win-led criterion and material/economy guards for a learned search
or endgame change. Then the scorecard implementation can encode that ruling.

## Hand-mining yield audit

The stated RL-entry rule requires two successive hand arms **in each** active
family (queen, portal, sprint) to miss paired-win movement on both pool and gen
panels. The available evidence does not clear that condition:

- **Sprint:** `carthage-05-free-sprint` vs `carthage-00-base` is positive on
  both panels under 1.2.5. The 05−04 increment is inconclusive on pool and
  positive on gen, not two consecutive two-panel non-movers.
- **Portal (at audit time):** H-S1 had not yet been tested. Its later 4 Oct
  follow-up is one rejected arm and still leaves the two-consecutive condition
  unmet.
- **Queen:** recent Carthage arms have not produced a durable win mover, but
  this cannot substitute for the all-family test.

Therefore the programme's opportunity-cost condition does not currently
justify declaring hand-mining exhausted. The next useful hand check remains
the queued H-S1 portal-memory test, alongside the current sprint and queen
queues as they produce results. Keep PPO parked; GBT expert iteration is the
first learned track only after the gate and entry conditions are resolved.

## Rollout method and result

Reproduce with:

```sh
nice -n 10 .venv/bin/python tools/antioch/rl/ares_rollout_bench.py \
  --out build/antioch/rl/ares-rollout-v1
```

The script verifies the installed runtime, the compact 540-round prior and
that Carthage05 calls that prior. It warms the engine outside the measured
interval, then runs complete official CLI games serially on both seats. The
121.05 seconds include the engine, both C++ Ares searches, orchestration and
compact replay writes. Replay parsing is performed after timing.

The measured 5.43M turns/hour is roughly one-fifth of the 28.63M callbacks/hour
G1 inference probe, but those rates are not directly comparable: G1 used an
untrained MLP without Carthage's search workload. This
benchmark also excludes feature extraction, target serialization and GBT
refitting; it is neither end-to-end training throughput nor a strength result.
The 297 games/hour figure reflects only this ten-game map/seed mix and is
especially sensitive to the long maps.

Machine-readable report and replay fixtures:
`build/antioch/rl/ares-rollout-v1/report.json`. The benchmark source and report
record the Carthage05 fingerprint and source hashes for reproduction.

## Decision

Do not start learned-policy training on the claim that the programme's entry
checks have passed: the 1.2.5 learned-arm gate is not ratified and hand-mining
yield has not met its all-family stop rule. Keep the 540-round prior. The
measured full-policy rate gives an initial estimate for later rollout
planning, but a training budget should include feature extraction and fitting
measurements.

Related records: `docs/findings/2026-10-02-antioch-rl-readiness.md`,
`docs/findings/2026-10-03-antioch-director-host-rl-groundwork.md`,
`docs/findings/2026-10-03-carthage-05-vs-00-five-seed-1.2.5.md`,
`docs/findings/2026-10-03-carthage-05-vs-04-five-seed-pool.md` and
`docs/findings/2026-10-03-carthage-05-vs-04-five-seed-gen.md`.

## Subsequent ruling

On 4 October, D-045 resolved the gate question prospectively for learned
policy/search candidates evaluated under 1.2.5. The opt-in `learned125` lane
gate is implemented in `tools/carthage/lane.py`; its thresholds and run
protocol are recorded in
`docs/findings/2026-10-04-antioch-learned-arm-gate.md`. This clears the
evaluation-gate item only. The hand-mining stop condition remains unmet, so the
entry audit's decision to keep training queued still stands.

## H-S1 follow-up — 4 October 2026

The initial hand-mining audit above preceded the queued portal test. The
predeclared H-S1 test has now completed on Carthage 12 versus Carthage 05,
seeds 1–3, both seats, and complete pool/gen panels under `unswbc 1.2.5`.
Per-transit died3 fell 2.7% on pool and 1.3% on gen, below the 25% target;
normalized `econ~` lower bounds were −0.065 and −0.038, below the −0.02 floor.
Reject this portal arm. It is one negative portal result, so it does not
satisfy the separate requirement for two consecutive non-moving arms in every
active family. Keep training queued. Full methods, map deltas, and artifacts:
`docs/findings/2026-10-04-carthage-12-hs1-portal-memory.md`.
