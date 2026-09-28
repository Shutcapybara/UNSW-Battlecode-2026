# C1-C — early-game efficiency accounting on the C++ chassis  (model: **GLM 5.3**)

Shared rules: `docs/hub/prompts/2026-09-29-C1-index.md`. Depends on C1-A's chassis. Bots `cx-c01-eff`, `cx-c02-…`.
Until the chassis lands, build the accounting (§1) on `bots/yuna-v03-core` replays — it is the deliverable that
matters most and needs no chassis.

## 0. The job, and what it is not

The P1 pace probe (lead, 29 Sep) showed that pushing production up by schedule does not work: forcing the split
timing fails to reach the field's curve, and when it reaches it we still lose. So the material gap is **efficiency**,
not effort — pearls per dragon-turn, moves per pearl, dragons lost before they pay for themselves. This task is
**not** a split-timing sweep. It is the accounting that says where the material goes, then the fixes to the leaks
that the accounting exposes, each measured.

## 1. The ledger (day 1; replays first, chassis later)

Per game, per side, rounds 0–100 and 0–250, from replays (`tools/game_stats.py`, `tools/replay_stats/`; extend, do
not fork):

- **Income**: pearls eaten; pearls eaten per dragon-turn alive; length gained per pearl (should be 1 — anything else
  is a death cost); first-pearl round per dragon (birth to first eat).
- **Effort**: moves per pearl eaten; turns a dragon spends with no reachable ripe bed within its horizon (idle);
  turns spent waiting on a bed vs travelling; portal transits per pearl.
- **Leaks**: deaths by cause per 1k dragon-turns (wall, own body, ally body, head-on, portal step, timeout); length
  lost in deaths; newborn deaths within 10 rounds; pearls that ripened within 3 cells of one of our dragons and were
  eaten by the enemy or nobody (contested/missed beds).
- **Structure**: splits by r100, mean length at split, unit count curve.

Run it on: our live games (`LIVE/state`, our corpus games) and, from the corpus, ranked games of the top 10, ranks
11–30 and the band (same extractor). The output is a table "us vs band vs top" per statistic per map class, and one
sentence per row saying whether the gap is income, effort or leak. That sentence ordering is the priority list for
§2 — and for C1-B and C1-D, who read this file.

## 2. Fixes (on the chassis; each a `params.hpp` switch; each measured alone in exact pairs)

Only leaks the ledger ranks in its top three. Likely candidates, in the order the S1/A1 record suggests: newborn
targeting (the child's first bed on birth), bed waiting (stay on a bed with countdown ≤ k rather than wander),
contested-bed avoidance (do not walk to a bed an enemy head reaches first — C1-B supplies arrival rounds), idle
elimination (a dragon with no target within horizon moves toward the densest unclaimed bed cluster). Each fix is
accepted only if it moves the statistic it targets by the predicted amount **and** pearls eaten by r100 in pairs;
a fix that improves its own statistic and not the income is a leak moved, not closed.

## 3. Report

Findings `docs/findings/2026-09-30-cx-c01-eff.md` with the ledger table first; status `claude/cx-c-status.md`.
Falsifiers: the ledger finding no statistic where team 7 sits outside the band's interquartile range (then the gap
is not early-game efficiency and the director redirects); a fix moving its statistic without moving pearls by r100.
`CANDIDATE.toml` for the accepted fix set; the director registers it for the dev screen against 545.
