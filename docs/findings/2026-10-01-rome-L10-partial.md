# Rome L10: partial far-contact guard result

**Status: incomplete; no D-032 verdict.** The user requested wrap-up while the gen panel was still running. The run was interrupted after 1,253 of 1,392 gen fixtures; those partial gen replays were not scored. Do not treat this as an accept or as a complete reject.

## Test

- Parent: `rome-01-nodevil`, the 1.2.3-measured base with D-033's 32x16 terms disabled.
- Candidate: `rome-02-far-contact`, one switch that skips a direct head-on path if the contact cell is more than six Manhattan cells from any currently known bed.
- Expected sign recorded before the run: reduce far-contact head-on losses, with neutral-to-positive economy.
- Seeds 1–3, both seats. The z1 pool completed all 480 fixtures. The paired gen panel had 1,253/1,392 completed fixtures when interrupted.
- CPU sandbox probe: four maps, no errors, maximum 10.82M points per turn (under the 30M cap).
- Runtime: `unswbc 1.2.3`. This MacBook Pro has 18 cores; runs used 16 jobs. The host rejected the request for `nice -n 10` priority.

## Completed z1 pool scorecard

| Measure | Parent | Candidate | Change |
|---|---:|---:|---:|
| W-L-D | 401-78-1 | 405-74-1 | +4 expected-score points |
| Expected-score share | 83.65% | 84.48% | +0.83 percentage points |
| Mean normalized pearl checkpoints (r50/r100/r150/r250) | 1.1398 | 1.1398 | +0.0000 |
| Normalized pearls r50/r100/r150/r250 | 1.091/1.136/1.157/1.175 | 1.091/1.136/1.157/1.175 | +0.000 at displayed precision |
| Units / total length / births @ r100 | 1.316/1.200/1.119 | 1.316/1.200/1.119 | +0.000 each |

Tier-2 deaths per 1,000 dragon-turns: wall 5.663→5.615 (-0.9%); own body 3.765→3.820 (+1.5%); ally body 1.551→1.547 (-0.2%); ally head-on 0.628→0.624 (-0.7%); invalid 0→0. The worst relative tier-2 increase was own-body deaths, +1.5%, below the 10% guard.

The scorecard's z1 point-estimate gate reports **hold**: economy, units, and length are unchanged at its displayed precision; win share rose 0.83 points; no tier-2 rate rose by more than 10%. The D-032 paired 90% lower bounds were not computed here, and per-map deltas are not included in the scorecard output. The pool result alone therefore does not satisfy the full protocol gate.

## Gen, not scored

At interruption, 1,253/1,392 gen fixtures had completed. There is no complete paired gen score, no valid gen economy delta, and no complete per-map report. The required gen guard and the three-number result against `TARGETS.md` cannot be determined. Post-change field references/targets are also unpublished, so baseline reports use absolute and parent-relative values only.

Scorecard output for the completed pool is in `game_stats/runs/rome-02-far-contact-z1-s1-2-3.md` and `.json`. Partial gen replays remain under the ignored `build/zoo/gen-rome-02-far-contact-61fb6691/replays/`; no replay or blob is committed.
