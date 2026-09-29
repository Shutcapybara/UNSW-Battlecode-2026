# R-3 status — the C1-F leak switches re-targeted at Ares (GLM 5.3, ../wt-r3, branch r/r3)

Task: `docs/hub/prompts/2026-09-29-R3-ares-leaks-glm.md`. Finding: `docs/findings/2026-09-30-r3-ares-leaks.md`.
Nothing registered; no CANDIDATE marked ready.

## Log

- **Step 1 (leaks on Ares — confirmed, proceed).** Ares V06 is atlas-off by construction (`atlas_try`
  is never called — dead scaffold), so the R-4 z1 seed-1 panel (160 games, fingerprint-matched) was
  valid step-1 data. New instrument `tools/analysis/r3_ledger.py`: the exact C1-C leak classes +
  the exact C1-D portal walk (2.38 M verified walks). Pooled: trapped 36.1 len/1k (top10 18.5, band
  32.8), portal 6.3, crowd23 11.4 (top10 2.7); portal 29.4 deaths/100 steps at 62.5 steps/game
  (team 306: 12.5 at 47), wall+self near 15.9/game, same-pair doubles 14.9/game. yuna-v05 (local
  Tyr reference) is worse than Ares on every row. The lineage claim holds.
- **Step 2 (four switches, one per version, carrier golden-identical 0/15178 turns).**
  - r3-01 F-1 pair memory: **FAIL** — economy −0.051, win −5.6pp; portal row 6.3→4.9 via −22%
    transits, per-100-steps WORSE (31.8). Throttle.
  - r3-02 F-2 exit-known: **FAIL** — economy −0.120; every tier-2 rate down (h2h-ally −54%) but
    −68% transits, per-100 32.6. The sakura shape.
  - r3-03 escape-early: v1 wired inert (160 games bit-identical to V06 — reported as the find);
    v2 (escape competes at −10 while enclosed, 38/8487 Portals transcript divergences): **HOLD** —
    win +5.0pp at seed 1 AND seed 2, economy +0.035/+0.013, length +0.05, neutral gen, CPU probe
    4.7/7.3/8.7M 0 errors; but own-body +11% at both seeds (guardrail) and the targeted trapped row
    did not move — it is a split-when-cramped production lever. Not registered.
  - r3-04 kelp cost: **FAIL (hold-shape)** — the biggest row movements (wall −27%, trapped −30%,
    newborn −15%) at economy −0.072.
- **Step 3 (stack).** r3-05 = r3-03 + r3-04: **FAIL** (economy −0.107, costs compound not
  compose; hygiene wins survive: wall −33%). Stack stopped per protocol; r3-05 gen not run.
- **Tooling fixed on the way (r/r3, mergeable):** runtime fingerprint now `bot.toml` + code only
  (CANDIDATE.toml text no longer moves panel dirs — panel directories renamed to the corrected
  fingerprints, no games invalidated); scorecard seed-filter (a pooled parent dir no longer
  contaminates seed-specific comparisons) + NaN-change and gen-gate cosmetics.

## What the director should read

The negative result is the deliverable: **pre-entry portal pricing (F-1/F-2) cannot fix Ares's
portal leak — the per-transit death rate never improved, only volume fell; and the kelp/room
surcharge buys real hygiene at an economy cost the gate forbids.** The leaks live in post-transit
navigation (steer the first steps after a transit) and newborn siting — both untested, both
directly measurable with the instruments in this branch. r3-03 is a genuine +5pp production lever
held back by newborn churn — worth a siting follow-up, not registration as-is.

## Where things are

Branch `r/r3` (r/r4 merged in): step-1 instruments + ledger JSONs; five bots r3-01…05 with
measured CANDIDATE.tomls; the finding with all tables; this file. Panels under build/zoo/
(fingerprint-keyed): V06 z1 s1+s2 + gen s1, r3-01/02 z1+gen s1, r3-03 z1 s1+s2 + gen s1,
r3-04 z1 s1, r3-05 z1 s1. Run env: ~/.venvs/bc122.
