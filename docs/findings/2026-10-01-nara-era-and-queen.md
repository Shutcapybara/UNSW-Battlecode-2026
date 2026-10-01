---
id: nara-era-and-queen
author: glm/nara (P2-A analyst)
kind: measurement
title: The 1 Oct rules switch — era boundary, the sprint formula, the queen rule verified, and the first queen anatomy
task: P2-A first unit (era tagging, post-change references, queen)
evidence: tools/nara/{era_probe,era_queen_probe,queen_probe,opening_probe}.py; build/nara/*.jsonl (main checkout, untracked);
sampled straight from public_replays/corpus (421-443 games per era sample, decoded with the F1 frame decoder)
---

# 1. When the live server switched

**The switch happened in the 1 Oct 05:54–09:23 UTC maintenance window.** The index contains no games at all with
start times in 06:00–09:00 UTC; the last game before the gap started 05:53:35 (old rules), the first after it
started **09:23:44 (game 800028, new rules)**.

Detection signal (tools/nara/era_probe.py): for every surviving multi-step move, `paid` (segments paid, derived
exactly as the F1 feature `sprint_cost`) must equal `steps − 1` under the old sprint rule. Zero violations in any
sampled game before 05:54 (2-hour buckets, 29 Sep 00:00 – 1 Oct 05:54, ~6-11 games each); violations in nearly every
game from 09:23 on. Moves where the actor died in the same round were excluded — death truncates the body and
fakes `paid = 0` (this was the whole of the pre-change "noise" in a first pass).

**Era rule for the store (proposal to the replay lead): `era = 'post' iff started_at ≥ 2026-10-01T09:00Z`.** No game
exists in the gap, so 09:00 is a clean round boundary that separates the eras exactly.

## The sprint formula is exact

44,825 surviving multi-step moves across 240 post-switch games: `paid = steps − min(steps, ⌈L/4⌉)` with L the
length at round start — **0 violations**. The min-2-segments floor was not separately exercised (no contradicting
move observed; untested where it binds).

# 2. The round-limit tiebreak: it is the ORIGINAL queen, dead = 0

`unswbc 1.2.3` documents the tiebreak as queen → longest → total. The corpus pins down what "queen" is:

**The queen is the team's lowest-id initial robot (the first-spawned dragon, id 0 for A / id 1 for B in every map
checked). If it is dead at the round limit, the team's queen length is 0. The title does NOT pass to any other
dragon — neither to a sibling initial dragon nor to the lowest-id living robot.**

Evidence, all post-switch round-limit games decoded with full per-robot tracking:

| test | games | outcome |
|---|---|---|
| server winner vs old rule (longest→total) vs living-queen rule | 183 rl games | server agreed with old rule 180/183; the 3 exceptions all have a living original queen on the winning side and match original-queen-dead→0 |
| sibling inheritance (orig queen dead, another initial alive) | 7 games, 5 discriminate | all 5: server followed longest (queen = 0), not the sibling's length |
| full rule check, server winner vs queen(dead=0)→longest→total | 201 rl games | **0 violations** |

Concrete flips: g818516 (Trauma) — B longest 60 vs A 36, **A won**: A's original queen alive (36), B's dead.
g801032 (Autarky) — A won with longest 29 vs 18 while its queen was dead and B's living-lowest child was 18: the
dead queen contributed 0, then longest decided. The living-lowest-id reading is rejected; it lost all 3 games that
discriminate.

**A living original queen of any length beats a dead queen, ahead of longest.** g816752 (Portals): queen of length 8
beat an opponent longest of 39.

# 3. Queen anatomy (post-change, 842 side-games, 09:23–13:30 UTC)

Per-round tracking of the original queen robot (tools/nara/queen_probe.py; sample capped at 12 games/team, cohorts
from the latest ladder snapshot):

| cohort | n | queen survives to r490 | q_len@490 ≥ 8 | median max q_len | median q_eats | median head-move rounds |
|---|---|---|---|---|---|---|
| top10 | 60 | **13.3 %** | 8.3 % | 4 | 3 | 57 |
| r11–30 | 154 | 1.9 % | 0 % | 4 | 3 | 37 |
| r31–50 | 124 | 4.0 % | 2.4 % | 4 | 3 | 40 |
| other | 504 | 6.9 % | 2.2 % | 4 | 3 | 58 |

- **Nobody protects the queen today.** Queens are ordinary small early dragons: they forage (median 3 pearls ever),
  wander (37–73 head-move rounds), never grow (median max length 4) and die young — 42–60 % of sides' queens are
  dead by r50, ~90 % by r300.
- Round-limit games only: survival 11.1 % (top10) / 0–4.5 % (mid ranks).
- **One team has already adapted: Cutlery (306, rank 1)** — 5 of its 12 sampled games have the queen alive at r490,
  all five grown to length ≥ 8: deliberate protection + feeding, within ~4 hours of the switch.
  Also seen: doifenshmirtz good incorporated (3/12, all ≥ 8), uoa (2/12), pig (2/12).
- Team 7 has **no post-switch games** (executor in shadow), so "us, post" is empty until the testers' local panels.

## What the queen is worth, today

Round-limit share of side-games by map (post sample): Slithery 100 %, Portals 98 %, Trauma 91 %, Schooltime 73 %,
Autarky 36 %, QoS 32 %, Default 29 %, PD 14 %, Trophy 13 %, Devil 10 %.

Among 201 post-switch round-limit games: **20 (10.0 %) were decided by the alive-vs-dead queen alone; 11 of the 20
(5.5 % of rl games) went against the longest-dragon order.** A side that keeps its queen alive while the opponent's
dies currently wins every round-limit game regardless of dragons — the field's queens die in 87–98 % of side-games,
so a protector wins essentially all its would-be longest-tiebreaks on round-limit maps.

# 4. Opening, pre vs post: the field has not shifted yet (except retention)

Same-code comparison (tools/nara/opening_probe.py): pre = 30 Sep 00:00–05:54 (428 games), post = 1 Oct 09:23+
(443 games), all top-50 sides pooled, per-map field medians:

| metric (field median, 10 maps) | median shift pre→post |
|---|---|
| pearls@50 | −1.0 % |
| pearls@100 | +2.5 % |
| splits@50 | −4.0 % |
| **total length@100** | **+12.2 %** |

Mechanically expected: opening dragons are length 2–4, whose ⌈L/4⌉ = 1 free step equals the old rule's free step —
the opening is nearly untouched by the sprint change; mid-game retention improves because long dragons now move
free (total@100 up on 8 of 10 maps). Outliers to watch: Schooltime pearls@100 +79 % (31→56, n 14→74 — plausibly a
real behaviour shift on the biggest-economy round-limit map, plausibly composition), Devil pearls@50 −24 %.

**Post-era BENCHMARKS references are NOT stable enough to rebuild yet**: my per-map post samples are 58–116 field
side-games against the pre-era ~1,500/map. The replay lead's store rebuild plus 1–2 more days of collection
(≥300/map) should precede the formal re-derivation. Until then: keep the pre-era opening targets (they measure a
field that has not moved), and treat every r250+ reference as stale.

# 5. Operational bug: the decoder's winner is pre-change

`tools/analysis/features/frame.py` `decode()` computes the replay winner as longest → total, and
`tools/analysis/features/extract.py:411` derives `won` from it; `tools/s1/build.py` stores it as `decoded_winner`.
From the switch on, this disagrees with the server in every queen-decided round-limit game — 11 of 201 rl games in
my sample (~5.5 % of rl, ~2–4 % of all games), and the same applies to **local panels run under 1.2.3** (the
engine applies the queen rule; the decoder does not). Every W-L-D the testers read off replays is affected until
this is patched. Suggested patch (frame.py, replacing the final-block tiebreak):

```python
# queen: the team's lowest-id initial robot, dead -> length 0 (verified on 201 rl games, 0 violations)
first = rounds[0]
qa = min((i for i in first if first[i][0] == 'A'), default=None)
qb = min((i for i in first if first[i][0] == 'B'), default=None)
la_q = len(rounds[-1][qa][1]) if qa is not None and qa in rounds[-1] else 0
lb_q = len(rounds[-1][qb][1]) if qb is not None and qb in rounds[-1] else 0
...
winner = 'A' if la_q > lb_q else 'B' if lb_q > la_q else <longest, then total, as now>
```

(a queen column pair `q_len_A/B` in the decode result would let the store carry `q_len@490` and `q_alive490`
natively — requested of the replay lead).

# 6. Ledger rows proposed (director applies)

| id | hypothesis | weight | falsifier / size |
|---|---|---|---|
| N1 | **Queen protection**: keep the original queen (own lowest id) alive to r490 (park/ward it once the round-limit regime is likely), optionally feed it. Value today ≈ every round-limit game vs a dead-queen opponent; ~7–10 pp on round-limit maps, ~3 pp pooled at current field death rates. | 0.7 | 160-game panel split by regime: elimination-map wins must not drop (the parked dragon forages less); economy guards as D-032. Expected sign: rl-map win up, elimination flat. |
| N2 | **Queen hunting**: identify the enemy original queen (spawn-geometry dragon; symmetry inference (L38) mirrors enemy spawns) and kill it once ahead, zeroing their first tiebreak. | 0.4 | Identification accuracy from partial views is the crux; cost of diverting 1–2 dragons. Falsified if the hunting version loses more from diversion than it gains in flipped rl games on the panel. |
| N3 | **Opening-era continuity**: pre-era opening targets (Q3's four components) remain valid post-change; the sprint change pays from mid-game (retention +12 % at r100), not in the opening. | 0.6 | Post-era store rebuild: if field pearls@50 medians move >10 % on ≥4 maps, re-derive. |

# 7. Reproduction

Run from the main checkout (owns `public_replays/`):

```
python tools/nara/era_probe.py --since "2026-09-29 00:00" --every-h 2 --per 14   # era rollup
python tools/nara/era_queen_probe.py <games.jsonl|gid[:winner]>                 # formula + queen verdicts
python tools/nara/queen_probe.py --since "2026-10-01T09:23" --out build/nara/queen_post.jsonl
python tools/nara/opening_probe.py --since "2026-09-30T00:00" --until "2026-10-01T05:54" --out build/nara/open_pre.jsonl
```

Data files: `build/nara/{era_probe2,queen_post,open_pre,open_post}.jsonl` (main checkout).
