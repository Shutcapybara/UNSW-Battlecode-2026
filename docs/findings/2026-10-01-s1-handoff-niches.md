---
id: S1-handoff-niches
author: s1 (Claude, Ouroboros lane)
kind: handoff
title: What the strong niches do that we don't, and what to act on
status: preliminary. The atlas panel run (fixed opponents) finishes 1 Oct and is what should confirm the mechanics.
data: s1 corpus store (40,593 top-50 live games, 28–30 Sep); niche extracts build/atlas/out/niche/*.parquet
---

## TL;DR

- **The gap is production volume after round 25.** At r25 we look like the top teams. By r50 they have made
  17–18 splits to our 9–12.5, and eaten 35–37 pearls to our 17–22.5. By r150 they field 27–31 dragons to our 9.
- **The other differences sit around that one.** They keep a tight blob, avoid enemy heads and take portals early.
  Their deaths are chosen; ours are accidents.
- **Actionable now:** a hygiene patch.
  - fix age-0 invalid actions in newborns;
  - add a move-safety filter against self and ally collisions;
  - end enclosed length-2 dragons deliberately;
  - check portal exits.
- **The biggest lever is not yet a fix.** We don't know why we stop splitting. One diagnostic decides whether it is a
  splitting problem or a foraging problem (see "Next step" at the end).
- **The data carries a contamination risk.** SSS (91) and Cutlery (306) run different bots in unranked games. Parts
  of the atlas used all modes. See `2026-10-01-s1-F-fingerprinting.md`.

## The three strong niches

These are k-means niches from the preliminary atlas, over live team@day units with at least 40 side-games on at
least 6 maps. The top-10 live versions concentrate in three of them. Our bots are almost absent from all three.

| niche | members (examples) | signature |
|---|---|---|
| **N12** | cheji, Stockfish, forgot to mention, calc, ddabap, SKKU, Sabotage-d, PPP, zitian, SSS 09-28 | spread, contact-averse, deliberate `suicide` recycling, early portals; sonar similar to ours |
| **N7** | 中国必须人能飞, 3.14159265, bread first search, Cache me outside 09-28/30, tungtung67, w daniel ma, EternalWisdom | the most compact blob, near-silent sonar, high wall deaths, own-corpse recycling |
| **N1** | Cutlery, Sponge, Cache me outside 09-29 | recycling by invalid action, fastest early births and transits, moderate sonar with no refraction |

## What all three do that we don't

Figures are medians of per-map medians. "Top" gives the range across N12, N7 and N1. "Us" gives all team-7 games /
games since 29 Sep 06:00.

| | top | us |
|---|---|---|
| splits by r50 / r150 | 17–18 / 56–64 | 9–12.5 / 27.5–32 |
| pearls by r50 / r150 | 35–37 / 131–161 | 17–22.5 / 70–73 |
| units at r50 / r150 | 10 / 27–31 | 8–9 / 9 |
| total length at r150 | 67–74 | 20–22 |
| nearest-ally distance at r150 | 2.9–3.8 | 4.3–4.5 |
| clustered share at r150 | 0.50–0.77 | 0.36–0.39 |
| nearest enemy head at r50 | 7.3–7.6 | 6.2–7.0 |
| enemy-contact share at r150 | 0.14–0.27 | 0.49–0.50 |
| territory at r150 | 0.58–0.74 | 0.35–0.37 |
| transits by r50 | 4–6 | 0.75–2.75 |
| death within 3 rounds of a transit | 0.09–0.10 | 0.13–0.17 |
| ally collisions per 1k dragon-turns | 1.0–1.2 | 1.7–1.8 |
| self-collision deaths per side-game, r0–150 | 2.4–8.9 | ~14 |
| newborns dead within 10 rounds | 0.29–0.42 | 0.35–0.48 |

**Splitting.** The split mechanics are the same everywhere:

- everyone splits 4 → 2+2;
- 75–90 % of children are length 2 or less;
- children re-split.

The difference is cadence. Their unit count compounds through r25–50, and ours plateaus at 8–9. Newborn loss is only
modestly worse for us, which is not enough to explain a 3× unit gap. This matches the tempo finding: our 23–26-round
gap is almost all income, not loss.

**Chosen deaths.**

- N12 records 23 suicides per side-game and N1 26 invalid-action deaths, against 2.4–5 self-collisions.
- These deaths are length-2 dragons, ~99 % enclosed, aged 8–11 rounds, with a median death round of ~90.
- N7's 41.5 wall deaths are **not** verified as deliberate.
- All 835 of our live invalid-action deaths are newborns at age 0, which is a bug.

**Not differentiating.**

- **Sonar:** N12 matches us (~4 rays per 1k dragon-turns, 25 % refracted) and N7 is almost silent.
- **Corpse share of pearls:** 0.26–0.33 for everyone, us included.

## How actionable it is

**A. Actionable now: known cause, known fix, measurable.** These are hygiene. They make later tests cleaner but
probably close only a few rounds of tempo.

1. **Newborn invalid actions.** A child's first action is chosen without the child's own legal-move check. The fix
   should take the rate to zero.
2. **Move-safety filter.**
   - Never move into our own body or an ally's projected next head position when an alternative exists.
   - Gate: tempo gate plus its ally head-on guard.
3. **Enclosure exit.**
   - A length-2 dragon with no safe continuation should use `suicide`, preferably next to an ally, rather than colliding.
   - Expect little tempo change; the loss term is ~0.5 rounds for us.
4. **Portal exit safety.**
   - Keep early portals, which are +EV (S1-Q5).
   - Add a landing check for enemy heads near the exit.
   - Target: death within 3 rounds of a transit from 0.13–0.17 down to ~0.10.

**B. Direction known, size unknown: one tempo-gate run each, about 85–170 paired games per arm.** Expect some to
come back NO GAIN.

5. **Split cadence after r25.** This is the biggest lever, but its cause is undiagnosed. There are three candidate
   causes, and each needs a different fix:
   - the policy declines to split when it could;
   - dragons are too short to split because they are not eating (a foraging problem);
   - children die before they compound. This contributes, but is too small to be the main cause.
6. **Cohesion term.** Reward a nearest-ally distance of about 3–4, with one weight to sweep.
7. **Enemy-head avoidance within about 7 tiles.**
   - The causal direction is shaky, because weak bots get invaded, which inflates our contact rate.
   - Only the r50 distance gap is clean evidence. Watch for passivity in the r150 material guard.

**C. Not actionable.**

- sonar changes;
- territory or contact share as direct objectives (they are outcomes, and optimising them invites gaming);
- copying a niche wholesale;
- the r150 gaps, which are downstream of r25–50.

## Caveats

- All of this is correlational. "Us" pools every team-7 submission, and live opponent mixes differ by cohort.
- The niche assignments come from the preliminary atlas on local replays with varied opponents. The fixed-panel run
  (`tools/s1/atlas_overnight.py`, ~11.5 h, finishing 1 Oct) re-derives them.
- **Decoy contamination.** SSS 09-28 sits in N12 and Cutlery in N1. Both teams deploy different bots in unranked games:
  - SSS's unranked games are split between a sonar-silent bot that wins 12–16 % and a bot like its ranked one;
  - Cutlery's invalid-action rate is 3.5 per 1k dragon-turns unranked against 16.5 ranked.

  Niche membership for these two, and the top-10 medians in older references, should be recomputed on ranked or
  fingerprint-authenticated games only. `tempo_reference.json` already excludes both teams.

## Next step

Run a **split-stall diagnostic** on our replays for rounds 25–50. For each dragon-turn, record:

- length;
- whether a safe split was available and whether it was taken;
- pearl intake per dragon over the previous 10 rounds;
- child survival.

Then:

- if eligible-but-declined turns dominate, it is a policy problem;
- if dragons rarely reach length 4, it is a foraging problem.

It needs only our replays and the existing per-dragon extraction (`tools/s1/extras.py`).

## Files

- figures and tables: `build/atlas/out/niche/{series,splits,deaths,sides}.parquet`, `build/atlas/out/*.csv`
- related findings: S1-Q3 (opening components), S1-Q4/Q5 (portals), S1-T (tempo), `docs/analysis/BENCHMARKS.md`
