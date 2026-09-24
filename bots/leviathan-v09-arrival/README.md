# leviathan-v09-arrival

Line: Leviathan (GPT). Base: leviathan-v08-core; borrowed: full evaluator and
crown pipeline from ouroboros-v10-beacon; arrival predicate inspired by
hunter-v15. The pearl component is new standalone Python, not a ladder port.

Hypothesis: valuing beds due before arrival improves compact opening production.
The new feature approximates V's material/control term, through the existing
route-distance and ownership target selector. It does not bypass safety filters.

Changes: `pearl_model.arrival_value` values a bed when due ≤ now + ETA − 1,
decays overdue predictions, and runs only on compact maps in the tested profile.
A separately ablated correction requires current observation for simulated
pearl growth. Neither predictions nor remembered pearls fund simulated growth
in the selected profile. Core config defaults are neutral; params.py explicitly
enables `pearl.prepos=1` and `pearl.confirmed_only=1`. The source files match
the frozen benchmark snapshots exactly.

## Verdict

Gate: compact net W–L gain ≥4, no compact/open/opponent set below −3, sandbox p99 <60M and max <80M. Observed net deltas: `{'compact': 26.0, 'open': 2, 'fry-v14-stateful-size-aware-3': 6, 'hunter-v14-cpp-hybrid-route-spacing': 10, 'hunter-v20-portal-scouts': 14, 'kraken-v04-eval': 0.0, 'ouroboros-v10-beacon': -2}`. CPU gate: pass.

**Verdict: Promoted as the Leviathan working candidate for the next convergence; ACTIVE promotion remains with the unifier.**

Sets: G = five gauntlet opponents × 11 maps × both sides (110); V = the same
opponents on 22 transpose/flip variants (220). G+V = 330. Variants were held
out until the candidate profile was frozen; no tuning used their outcomes.
These are deterministic fixtures, not independent random samples. Source/map
hashes and native/sandbox modes are checked by tools/leviathan/converge.py.
Raw evidence lives in build/leviathan/cycle1-*; tables here are durable.

## G+V paired results

| Set | Base W–L–D | Candidate W–L–D | Score Δ | Net W–L Δ |
|---|---:|---:|---:|---:|
| ALL | 229–99–2 | 244–86–0 | +14.0 | +28 |
| compact | 79–69–2 | 93–57–0 | +13.0 | +26 |
| side B | 116–47–2 | 122–43–0 | +5.0 | +10 |
| compact B | 39–34–2 | 45–30–0 | +5.0 | +10 |
| fry-v14-stateful-size-aware-3 | 53–13–0 | 56–10–0 | +3.0 | +6 |
| hunter-v14-cpp-hybrid-route-spacing | 46–20–0 | 51–15–0 | +5.0 | +10 |
| hunter-v20-portal-scouts | 35–31–0 | 42–24–0 | +7.0 | +14 |
| kraken-v04-eval | 62–2–2 | 63–3–0 | +0.0 | +0 |
| side A | 113–52–0 | 122–43–0 | +9.0 | +18 |
| compact A | 40–35–0 | 48–27–0 | +8.0 | +16 |
| ouroboros-v10-beacon | 33–33–0 | 32–34–0 | -1.0 | -2 |
| open | 150–30–0 | 151–29–0 | +1.0 | +2 |
| open B | 77–13–0 | 77–13–0 | +0.0 | +0 |
| open A | 73–17–0 | 74–16–0 | +1.0 | +2 |

Improved: 32; regressed: 17; unchanged: 281. Deterministic fixtures.

## Original 11 maps (G)

| Set | Base W–L–D | Candidate W–L–D | Score Δ | Net W–L Δ |
|---|---:|---:|---:|---:|
| ALL | 78–31–1 | 85–25–0 | +6.5 | +13 |
| compact | 26–23–1 | 35–15–0 | +8.5 | +17 |
| side B | 39–15–1 | 41–14–0 | +1.5 | +3 |
| compact B | 11–13–1 | 14–11–0 | +2.5 | +5 |
| fry-v14-stateful-size-aware-3 | 18–4–0 | 20–2–0 | +2.0 | +4 |
| hunter-v14-cpp-hybrid-route-spacing | 16–6–0 | 16–6–0 | +0.0 | +0 |
| hunter-v20-portal-scouts | 12–10–0 | 17–5–0 | +5.0 | +10 |
| kraken-v04-eval | 21–0–1 | 21–1–0 | -0.5 | -1 |
| side A | 39–16–0 | 44–11–0 | +5.0 | +10 |
| compact A | 15–10–0 | 21–4–0 | +6.0 | +12 |
| ouroboros-v10-beacon | 11–11–0 | 11–11–0 | +0.0 | +0 |
| open | 52–8–0 | 50–10–0 | -2.0 | -4 |
| open B | 28–2–0 | 27–3–0 | -1.0 | -2 |
| open A | 24–6–0 | 23–7–0 | -1.0 | -2 |

Improved: 12; regressed: 5; unchanged: 93. Deterministic fixtures.

## Frozen transpose/flip validation (V)

| Set | Base W–L–D | Candidate W–L–D | Score Δ | Net W–L Δ |
|---|---:|---:|---:|---:|
| ALL | 151–68–1 | 159–61–0 | +7.5 | +15 |
| compact | 53–46–1 | 58–42–0 | +4.5 | +9 |
| side B | 77–32–1 | 81–29–0 | +3.5 | +7 |
| compact B | 28–21–1 | 31–19–0 | +2.5 | +5 |
| fry-v14-stateful-size-aware-3 | 35–9–0 | 36–8–0 | +1.0 | +2 |
| hunter-v14-cpp-hybrid-route-spacing | 30–14–0 | 35–9–0 | +5.0 | +10 |
| hunter-v20-portal-scouts | 23–21–0 | 25–19–0 | +2.0 | +4 |
| kraken-v04-eval | 41–2–1 | 42–2–0 | +0.5 | +1 |
| side A | 74–36–0 | 78–32–0 | +4.0 | +8 |
| compact A | 25–25–0 | 27–23–0 | +2.0 | +4 |
| ouroboros-v10-beacon | 22–22–0 | 21–23–0 | -1.0 | -2 |
| open | 98–22–0 | 101–19–0 | +3.0 | +6 |
| open B | 49–11–0 | 50–10–0 | +1.0 | +2 |
| open A | 49–11–0 | 51–9–0 | +2.0 | +4 |

Improved: 20; regressed: 12; unchanged: 188. Deterministic fixtures.

## Ablation and loss autopsy

Thirty compact fixtures versus Hunter v14, Hunter v20 and Kraken v04:

| Arrival | Confirmed simulation | W–L–D |
|---|---|---:|
| off | off | 15–14–1 |
| on | off | 22–8–0 |
| off | on | 15–14–1 |
| on | on | 22–8–0 |

Arrival alone gives eight improved outcomes and one regression. Confirmed-only
changes three action streams but no outcomes in this screen. Opening [0,30)
pearls rise 16.23→23.07, splits 6.27→8.63, units 6.27→8.40. Deaths rise
1.80→2.03, so the supported mechanism is collection and production.

The two open-map G regressions belong to confirmed simulation (arrival is off
on open maps): default/A vs Hunter v14, longest 22→7; queen_of_spades/B vs
Kraken v04, longest 29→13. Both lose the round-500 comparison; first action
divergences are rounds 90 and 64. Do not conflate targeting gains with a
uniform strength gain from the correctness change.

## Verification and CPU

29 regression tests pass. With both options off, all six neutral comparison
games preserve movement, splits and sonar exactly (Hunter v20 on arena,
default_small and default, both sides). Four sandbox games on big_empty and
trauma versus Hunter v20 finish 4–0, with zero timeouts or unexpected invalid
actions. All 76 no-action deaths are after round 400 with only PROTOCOL output,
consistent with the inherited feed action. They are not reported as zero
invalid deaths. CPU values are runner-rounded per-game percentile ranges:

| Metric | Per-game range (million points) |
|---|---:|
| cpu_p50 | 18.6–29.8 |
| cpu_p99 | 28.8–48.9 |
| cpu_max | 41.5–67.1 |

## Parameters and convergence limits

`pearl.prepos`: boolean, neutral 0; consumed by choose_target.
`pearl.compact_only`: boolean, default 1; area ≤625 gate.
`pearl.prediction_ttl`: 0–30 rounds, default 4; overdue reward decay.
`pearl.confirmed_only`: boolean, neutral 0; consumed by simulate.
Other P/RP knobs retain their reference names and consumers.

This is a measured pearl-component candidate, not a claim of full HANDOFF
architecture completion. Inherited 12-bit lifetime IDs, 8-bit portal IDs and
portal gossip correction still need repair. The complete map×phase doctrine,
scout quota, parity pricing and hunter-style priority parameter point remain
open. See docs/leviathan/CONVERGENCE.md for interfaces and explicit scope.

No other line or shared file was changed and no online submission was made.
