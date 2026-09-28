# pace-v01

Parent `chaewon-y04-probe` (yuna-v05-core + atlas + newborn-neck fix + portal probe; copied with
attribution, host untouched). The **P1 pace probe**: the only new policy is a controller that keeps
the team's material on the field's production curve; everything else is the host's.

## What the controller does

Targets are public-corpus **winner medians** per map class (compact = W*H <= 625; 280 games,
2026-09-29): compact u25 7 / u50 12 / u100 23, t25 17 / t50 30 / t100 58 / t250 86; open u25 6 /
u50 11 / u100 20, t25 15 / t50 27 / t100 50 / t250 116. The curve is linearly interpolated and
self-anchored at the observed round-0 material (a team is never "behind" at the start by
construction). Units are exact from the header; team total is a clamped EWMA of sampled visible
lengths (self + visible allies + a fresh crown beacon) times UNIT_COUNT, floored at 2*units.

Per turn, gaps ug/tg (fraction behind) select a mode:

- **push** (ug > 0.12, r < 380): `split_val` +7*deficit (max), opening production window +<=30 rounds.
- **hold** (ug < -0.12 and tg > 0.05): `split_val` -3 (max) — grow existing dragons instead of splitting.
- **grow** (tg > 0.05): pearl/bed/memory values x (1 + gain*deficit), confirmed-pearl 2-step sprints
  for dragons of length <= 8. The gain is **class-conditioned**: 1.2 on open maps, 0.3 on compact —
  a full boost on compact collapses the churn economy (trophy seed-1 isolation: units r100 33 -> 11,
  win -> loss; 2026-09-29).
- on pace: the host's default knobs.

Survival constraints are never relaxed by the controller: exact 1-3 step simulation, split
child-exit and child-area gates, child = 2, split_min = 4. The **pace-nolimit** arm
(`pace_nolimit = 1` via override.py in a generated copy, never committed) zeroes the
trap/threat/blind-portal penalties and skips the split exit gates to measure what they cost.

Activation: `LOG ACT:pace+` rides the same stdout write as the action (protocol.py `pending`) when
a push/grow knob shift is active (heartbeat <= 1/8 rounds) and on splits/pearl-sprints under it;
`LOG ACT:pace-` while an eligible split is suppressed under hold.

## Measurement report

- **Strategy**: targets = corpus winner medians per class (above). Attainment vs those targets:
  u100 median 12 compact / 16 open (targets 23/20), t250 39 / 67.5 (targets 86/116); on-pace at
  r100 in 21% / 45% of games — the field's curve was **not** attained against this pool.
- **Execution**: the controller is the only new option set; its ablation is the host arm (the
  controller leaves every survival gate intact). Activation: ACT:pace+ 31/118/58 lines in r0-100 on
  Schooltime/Portals/Trauma probes; ACT:pace- present.
- **Implementation**: probes below — zero faults everywhere, max < 80M; p99 < 60M on 7/8 cells
  (Slithery 60.1-60.9M vs a 58.6M host baseline on that fixture).
- **State**: host's state unchanged; the controller adds only the EWMA team-total estimate
  (consumer: the mode logic).
- **Messaging**: host's packets unchanged (crown beacons feed the total estimator); no new rays.
- **Momentum**: host's, unchanged (newborn10/100 births 33.3 vs host 34.4; wall+self/1k 12.5 vs
  12.4 — delta-neutral).

## Panel (unswbc 1.2.2, seeds 1-3, paired by map/side/seed/opponent; build/pace-panel)

| arm | ws | compact | open | paired vs host | better/worse |
|---|---|---|---|---|---|
| host (chaewon-y04) | 0.556 | 0.562 | 0.551 | — | — |
| **pace** | 0.539 | 0.615 | 0.488 | **-0.017 (p 0.56)** | 49/56/255 tie |
| nolimit (constraints off) | 0.356 | 0.438 | 0.301 | **-0.200 (p <1e-4)** | 38/110/212 tie |

Per-class paired: pace compact **+0.052** (23/16, p 0.34), open -0.062 (26/40, p 0.11, concentrated
in Queen of Spades -0.36). Win-predicting statistics over all 1080 games (L2 logistic, LOMO AUC
0.877): dt250 +1.26 and dl400 +0.87 carry it; own h2h deaths -0.78 is the strongest negative.
Falsifier: "pace attained with delta <= 0" did not fire — pace was never attained (21-45% on-pace);
valuation-level production control does not buy the field's curve against band opponents. Full
detail: docs/findings/2026-09-29-pace-v01.md.

## Metered probes (vs sinbad-v07-divecap; zero faults on every fixture/toolkit)

| toolkit | fixture | turns | p50 | p99 | max | pace+ r0-100 |
|---|---|---|---|---|---|---|
| 1.2.2 | Schooltime A | 23605 | 17.8M | 59.0M | 69.3M | 31 |
| 1.2.2 | Slithery Fight A | 24007 | 17.5M | 60.3M | 79.6M | 0 |
| 1.2.2 | Portals B | 7740 | 19.4M | 58.0M | 68.8M | 118 |
| 1.2.2 | Trauma B | 7111 | 16.8M | 54.0M | 63.7M | 58 |
| 1.0.0 | Schooltime A | 22800 | 17.7M | 58.1M | 71.4M | - |
| 1.0.0 | Slithery Fight A | 21684 | 17.8M | 60.9M | 79.6M | - |
| 1.0.0 | Portals B | 7857 | 19.5M | 57.8M | 69.1M | - |
| 1.0.0 | Trauma B | 11313 | 16.6M | 55.2M | 62.3M | - |

Gate: max < 80M passes on all eight; p99 < 60M passes on 7/8 — Slithery Fight sits at 60.1-60.9M
against a **host baseline of 58.6M p99 / 74.7M max on the same fixture** (measured 2026-09-29), i.e.
this host has only ~1.4M of p99 headroom there; the controller's residual cost is game composition
(sprinting restriction and log batching already applied; a further shave did not move it). The
director's live gate (max < 95M) clears everywhere with margin. The activation contract
(>= 10 pace+ in r0-100, >= 1 pace- in r0-500) holds on Schooltime/Portals/Trauma; Slithery Fight
plays the opening on pace (0 pace+ r0-100, markers appear later there).
