# Riptide measured baselines

Riptide x02 improves the independent family to **42–67–1** on G, versus x01 **33–77–0**. Mainline v09 remains substantially stronger at **85–25–0**, but x02 wins four fixtures that v09 loses. Retain both Riptide sources for research; x02 is the stronger starting point within this family.

## Structural comparison: full gauntlet G

| Set | Base W–L–D | Candidate W–L–D | Score Δ | Net W–L Δ |
|---|---:|---:|---:|---:|
| ALL | 33–77–0 | 42–67–1 | +9.5 | +19 |
| compact | 4–46–0 | 3–46–1 | -0.5 | -1 |
| side B | 16–39–0 | 21–33–1 | +5.5 | +11 |
| compact B | 1–24–0 | 0–24–1 | -0.5 | -1 |
| fry-v14-stateful-size-aware-3 | 9–13–0 | 10–12–0 | +1.0 | +2 |
| hunter-v14-cpp-hybrid-route-spacing | 7–15–0 | 10–12–0 | +3.0 | +6 |
| hunter-v20-portal-scouts | 8–14–0 | 9–13–0 | +1.0 | +2 |
| kraken-v04-eval | 9–13–0 | 11–10–1 | +2.5 | +5 |
| side A | 17–38–0 | 21–34–0 | +4.0 | +8 |
| compact A | 3–22–0 | 3–22–0 | +0.0 | +0 |
| ouroboros-v10-beacon | 0–22–0 | 2–20–0 | +2.0 | +4 |
| open | 29–31–0 | 39–21–0 | +10.0 | +20 |
| open B | 15–15–0 | 21–9–0 | +6.0 | +12 |
| open A | 14–16–0 | 18–12–0 | +4.0 | +8 |

Improved: 15; regressed: 5; unchanged: 90. Deterministic fixtures.

G is five ACTIVE opponents × eleven original maps × both sides. The x02 V set below is a targeted validation set, **not full G+V**.

## Complementarity against mainline

Mainline v09 scores 85–25–0 on the same 110 frozen fixtures. Source/map hashes match.

| Branch | G W–L–D | Wins where v09 did not win | v09 wins not retained |
|---|---:|---:|---:|
| x01 | 33–77–0 | 0 | 52 |
| x02 | 42–67–1 | 4 | 47 |

These are deterministic complementary fixtures, not evidence of a reliable opponent detector or automatic portfolio selector.

**x01 complementary wins:**

None.

**x02 complementary wins:**

- `default`, side B, vs `hunter-v14-cpp-hybrid-route-spacing` (v09 L).
- `default`, side A, vs `hunter-v14-cpp-hybrid-route-spacing` (v09 L).
- `queen_of_spades`, side B, vs `kraken-v04-eval` (v09 L).
- `trauma`, side A, vs `ouroboros-v10-beacon` (v09 L).

## Frozen configuration screens

| Profile | Games | W–L–D |
|---|---:|---:|
| x01-screen | 24 | 2–22–0 |
| x01-myopic | 24 | 2–22–0 |
| x01-bank-screen | 24 | 2–22–0 |
| x01-silent | 24 | 4–20–0 |
| x01-monolith | 20 | 2–18–0 |
| x02-screen | 24 | 5–19–0 |
| x02-factory | 24 | 4–20–0 |

The common 24-game screen is arena/default_small/default/big_empty × Hunter
v14, Hunter v20 and Leviathan v09 × both sides. The monolith screen is a
separate 20-game open-map set against v09/Hunter v20; do not compare its raw
win count to the 24-game screens. The x02 screen preserves its original 0.35
fork-risk constant; the same value was later exposed as a parameter.

The core screen result is x01 2–22, x02 5–19 (three improved outcomes, none
regressed). Turning x01's horizon down to one or applying the early-bank
profile leaves all 24 outcomes unchanged. This does **not** establish action
or mechanism equivalence. The four-game x02 neutral control *does* reproduce
x01 movement, split and sonar streams exactly with viability disabled.

Disabling the self-report broadcasts improves x01 from 2–22 to 4–20 on this
screen: big_empty/B against Hunter v14 and default/A against v09 change to
wins, with no lost wins. The current ownership consumer therefore has no
demonstrated benefit on the screen. Keep the radio-on source as the frozen
control; use `radio=False` as a recorded search starting point. This ablation
does not establish that all communication is harmful.

The factory profile finishes 4–20 versus x02's 5–19: one improved fixture,
two regressions. Removing the food gate and relaxing reproduction risk does
not establish a repair of the opening deficit. On compact screen maps its
opening pearl average rises to 24.42 and splits to 7.33, while opponents still
collect 36.50 pearls and split 13.00 times. The extra production is too small
to overturn any of the twelve compact losses.

Opening [0,30), per game on the screen's compact maps: x01 eats 23.08 pearls
and makes 6.17 splits against the opponents' 37.83 pearls and 13.50 splits.
x02 remains almost unchanged (22.83 pearls, 6.17 splits). Its improvements
therefore do not fix the opening production deficit. Most x01 wall/self deaths
occur after the planner reports no legal action; a few deaths also involve
incomplete knowledge beyond vision. Neither planner is an omniscient safety
proof.

### Paired profile comparisons


**x01-screen → x01-myopic**

| Set | Base W–L–D | Candidate W–L–D | Score Δ | Net W–L Δ |
|---|---:|---:|---:|---:|
| ALL | 2–22–0 | 2–22–0 | +0.0 | +0 |
| compact | 0–12–0 | 0–12–0 | +0.0 | +0 |
| side B | 1–11–0 | 1–11–0 | +0.0 | +0 |
| compact B | 0–6–0 | 0–6–0 | +0.0 | +0 |
| hunter-v14-cpp-hybrid-route-spacing | 0–8–0 | 0–8–0 | +0.0 | +0 |
| hunter-v20-portal-scouts | 2–6–0 | 2–6–0 | +0.0 | +0 |
| leviathan-v09-arrival | 0–8–0 | 0–8–0 | +0.0 | +0 |
| side A | 1–11–0 | 1–11–0 | +0.0 | +0 |
| compact A | 0–6–0 | 0–6–0 | +0.0 | +0 |
| open | 2–10–0 | 2–10–0 | +0.0 | +0 |
| open B | 1–5–0 | 1–5–0 | +0.0 | +0 |
| open A | 1–5–0 | 1–5–0 | +0.0 | +0 |

Improved: 0; regressed: 0; unchanged: 24. Deterministic fixtures.

**x01-screen → x01-bank-screen**

| Set | Base W–L–D | Candidate W–L–D | Score Δ | Net W–L Δ |
|---|---:|---:|---:|---:|
| ALL | 2–22–0 | 2–22–0 | +0.0 | +0 |
| compact | 0–12–0 | 0–12–0 | +0.0 | +0 |
| side B | 1–11–0 | 1–11–0 | +0.0 | +0 |
| compact B | 0–6–0 | 0–6–0 | +0.0 | +0 |
| hunter-v14-cpp-hybrid-route-spacing | 0–8–0 | 0–8–0 | +0.0 | +0 |
| hunter-v20-portal-scouts | 2–6–0 | 2–6–0 | +0.0 | +0 |
| leviathan-v09-arrival | 0–8–0 | 0–8–0 | +0.0 | +0 |
| side A | 1–11–0 | 1–11–0 | +0.0 | +0 |
| compact A | 0–6–0 | 0–6–0 | +0.0 | +0 |
| open | 2–10–0 | 2–10–0 | +0.0 | +0 |
| open B | 1–5–0 | 1–5–0 | +0.0 | +0 |
| open A | 1–5–0 | 1–5–0 | +0.0 | +0 |

Improved: 0; regressed: 0; unchanged: 24. Deterministic fixtures.

**x01-screen → x01-silent**

| Set | Base W–L–D | Candidate W–L–D | Score Δ | Net W–L Δ |
|---|---:|---:|---:|---:|
| ALL | 2–22–0 | 4–20–0 | +2.0 | +4 |
| compact | 0–12–0 | 0–12–0 | +0.0 | +0 |
| side B | 1–11–0 | 2–10–0 | +1.0 | +2 |
| compact B | 0–6–0 | 0–6–0 | +0.0 | +0 |
| hunter-v14-cpp-hybrid-route-spacing | 0–8–0 | 1–7–0 | +1.0 | +2 |
| hunter-v20-portal-scouts | 2–6–0 | 2–6–0 | +0.0 | +0 |
| leviathan-v09-arrival | 0–8–0 | 1–7–0 | +1.0 | +2 |
| side A | 1–11–0 | 2–10–0 | +1.0 | +2 |
| compact A | 0–6–0 | 0–6–0 | +0.0 | +0 |
| open | 2–10–0 | 4–8–0 | +2.0 | +4 |
| open B | 1–5–0 | 2–4–0 | +1.0 | +2 |
| open A | 1–5–0 | 2–4–0 | +1.0 | +2 |

Improved: 2; regressed: 0; unchanged: 22. Deterministic fixtures.

**x02-screen → x02-factory**

| Set | Base W–L–D | Candidate W–L–D | Score Δ | Net W–L Δ |
|---|---:|---:|---:|---:|
| ALL | 5–19–0 | 4–20–0 | -1.0 | -2 |
| compact | 0–12–0 | 0–12–0 | +0.0 | +0 |
| side B | 3–9–0 | 2–10–0 | -1.0 | -2 |
| compact B | 0–6–0 | 0–6–0 | +0.0 | +0 |
| hunter-v14-cpp-hybrid-route-spacing | 2–6–0 | 1–7–0 | -1.0 | -2 |
| hunter-v20-portal-scouts | 2–6–0 | 3–5–0 | +1.0 | +2 |
| leviathan-v09-arrival | 1–7–0 | 0–8–0 | -1.0 | -2 |
| side A | 2–10–0 | 2–10–0 | +0.0 | +0 |
| compact A | 0–6–0 | 0–6–0 | +0.0 | +0 |
| open | 5–7–0 | 4–8–0 | -1.0 | -2 |
| open B | 3–3–0 | 2–4–0 | -1.0 | -2 |
| open A | 2–4–0 | 2–4–0 | +0.0 | +0 |

Improved: 1; regressed: 2; unchanged: 21. Deterministic fixtures.


## x02 orientation validation

Twenty-two transposed/flipped maps × v09/Hunter v20 × both sides (88 games).
The default x02 policy was frozen before viewing this set. These orientations
were held out for this Riptide selection, not globally unused by the project.

| Set | W–L–D |
|---|---:|
| ALL | 17–71–0 |
| compact | 1–39–0 |
| side B | 9–35–0 |
| compact B | 0–20–0 |
| hunter-v20-portal-scouts | 17–27–0 |
| leviathan-v09-arrival | 0–44–0 |
| side A | 8–36–0 |
| compact A | 1–19–0 |
| open | 16–32–0 |
| open B | 9–15–0 |
| open A | 7–17–0 |

## Monolith orientation validation

Twelve open-map variants × v09/Hunter v20 × both sides (48 games). Frozen `population_max=1` prevents reproduction; it retains the two to four initial dragons on these maps.

| Set | W–L–D |
|---|---:|
| ALL | 2–46–0 |
| open | 2–46–0 |
| side B | 1–23–0 |
| open B | 1–23–0 |
| hunter-v20-portal-scouts | 1–23–0 |
| leviathan-v09-arrival | 1–23–0 |
| side A | 1–23–0 |
| open A | 1–23–0 |

The original wins are both trauma/A (against v09 and Hunter v20). Only two validation wins remain: trauma_FX/B against v09, and trauma_T/A against Hunter v20. All four are longest-dragon tiebreaks. This is a narrow survival/banking signal, not a robust general specialist.

## Judge CPU and verification

x01: arena and big_empty, both sides versus Hunter v20.

| Metric | Per-game range, million points |
|---|---:|
| cpu_p50 | 5.7–11.3 |
| cpu_p99 | 9.8–15.2 |
| cpu_max | 10.0–17.6 |

x02: big_empty and trauma, both sides versus Hunter v20.

| Metric | Per-game range, million points |
|---|---:|
| cpu_p50 | 8.0–11.6 |
| cpu_p99 | 10.8–15.6 |
| cpu_max | 11.0–18.0 |

CPU values are runner-rounded per-game percentile ranges, not pooled percentiles. See the bot READMEs for verdicts. All 532 games have checked replays and no recorded runner/analysis errors or timeouts; Riptide has zero invalid-action deaths. Per-run evidence is in `build/leviathan/riptide-final/health.json`.

31 Python-discovered tests pass, including compiling/running both C++ rule suites. Native results do not substitute for sandbox metering. Source/map snapshots, all replays, standard ledgers and ablation manifests remain in `build/leviathan/riptide-*`.


## Decision and next search

Retain Riptide as an independent **research baseline**, not a replacement for
v09 or an ACTIVE promotion. Preserve x01 as the original negative control and
x02 as the capacity-filter branch. A few complementary wins justify further
search only if their economic/survival mechanism can be reproduced on new
maps; overall deficits must remain visible.

The capacity component's full-G gain is entirely on open maps: +10 wins there,
with a compact win becoming a draw in aggregate. The paired total is 15
improved fixtures and 5 regressions, not a uniform safety improvement. Its
17–71 orientation result includes 0–44 against v09, so the isolated direct
win over v09 in the selection screen does not generalize to these variants.

The next structural questions are: how to value forecast food under enemy
competition; how to fund reproduction while head pressure is high; and how to
turn distributed reserves into one winning length without inheriting the
mainline's feeding system. The horizon ablation does not support blindly
increasing search depth. The CPU headroom allows new models, but is not evidence
that more search alone will improve play.
