# Rome 1.2.3 baseline and queen audit

**Run:** 2026-10-01, `unswbc 1.2.3`, seed 1–3, both seats. Base: `rome-01-nodevil`, copied from `hb1-14-prior-r540` with D-033's three `W == 32 && H == 16` terms disabled. No parent was supplied to this baseline run, so these are absolute measurements and the new Rome zero; they are not an accept/reject gate result.

## Scorecard

| Panel | Fixtures | W–L–D | Expected-score share | Normalized pearl economy | Checkpoints / guards |
|---|---:|---:|---:|---:|---|
| Pool (z1) | 480 | 401–78–1 | 83.65% | 1.1398 | pearls r50/r100/r150/r250: 1.091/1.136/1.157/1.175; units r100 1.316; total length r100 1.200; births r100 1.119 |
| Gen | 1,392 | 1,041–351–0 | 74.78% | no post-rule field reference | raw per-map medians: pearls r50/r100/r150/r250 35/114/176/235; units r100 27; total length r100 65; births r100 46 |

Tier-2 deaths per 1,000 dragon-turns, pool: wall 5.663, own body 3.765, ally body 1.551, ally head-on 0.628, invalid 0. Gen: wall 0.047, own body 0.423, ally body 0.459, ally head-on 0, invalid 0. The scorecard found no normalized gen reference for the 29 generalisation maps. Analysts have not published post-rule target references yet; pre-1-Oct references remain pre-rules.

The full absolute scorecard is [rome-01-nodevil-z1+gen-s1-2-3.md](../../game_stats/runs/rome-01-nodevil-z1+gen-s1-2-3.md). It has no parent-relative or per-map deltas because this is the baseline arm. The next paired candidate run uses the same 480 + 1,392 fixtures and reports per-map deltas against these saved parent replays.

## Queen and replay-rule audit

The queen is the lowest-ID dragon on the team in the first replay round. Queen statistics use round index 490; dead queens contribute length zero to mean and median. “Longest by round” is the share of observed team-rounds for which the queen ties or exceeds the team's longest dragon.

| Panel | Queen alive at r490 | Mean length (dead=0) | Median | Queen longest at r490 | Longest among survivors | Longest by round r0–490 |
|---|---:|---:|---:|---:|---:|---:|
| Pool (480) | 2 (0.42%) | 0.063 | 0 | 2 (0.42%) | 2/2 (100%) | 18,728 / 167,682 (11.17%) |
| Gen (1,392) | 6 (0.43%) | 0.096 | 0 | 6 (0.43%) | 6/6 (100%) | 17.14% |

All 72,334 measurable successful sprint charges matched `max(0, steps - ceil(start_length / 4))`. Fatal sprint actions were excluded because the resulting length cannot reveal the amount paid. Every longest-dragon tiebreak had tied queen lengths (pool 198/198; gen 224/224), and every queen-tiebreak winner agreed with the queen lengths (pool 18/18; gen 20/20).

The rule preflight also inspected two round-limit Trauma replays: one reported a queen tiebreak with queen lengths 11–0 at r490, and another reported a longest-dragon tiebreak with queens tied 0–0. This confirms the queen-first, then longest ordering in Rome's 1.2.3 replays.

## Resource and provenance notes

The run used 16 workers on an 18-core MacBook Pro, leaving two cores unused. macOS denied `nice -n 10` with `setpriority: Operation not permitted`, so process priority could not be lowered. The golden copy check was performed under the previously available 1.2.2 runtime: 0 divergent turns over 21,479 Schooltime turns; it is code-copy parity, not performance evidence for 1.2.3.
