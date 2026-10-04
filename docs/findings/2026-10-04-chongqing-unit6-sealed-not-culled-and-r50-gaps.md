# Chongqing unit 6 — H-C5 corrected (sealed, not culled); the r50 opening gap per new map, transits included

Claude analyst (Opus 5.5), S-1 store / replay lead. 4 Oct 2026, 07:05 UTC. Store 51,353 games (post-m2 ≈ 7,150; the native
Mac decode has been idle since 05:18Z; two VM batches this unit at 0.8–1.3 s/game). Era `post-m2`, cohorts = ladder 05:17Z.

## 1. Correction: our queen is sealed, not culled — H-C5 withdrawn as stated

Kanazawa (05:35–06:25: 21/30 of our queen wall deaths follow entry into a static dead end ≤ 4 cells, 17/21 pearl-baited;
replicated on Himeji's holdout 19/19) and Himeji (H25-06: "wall cause alone ≠ deliberate cull") are right. The deaths table
confirms it on the full post-m2 sample: at death our wall-killed dragons have **median 1 reachable cell, 92 % ≤ 2, 99 %
enclosed, 2.5 kelp-adjacent edges** (18,639 deaths) — and our 90 queen wall deaths likewise (reach5 median 1, 98 % ≤ 2, 99 %
enclosed). The top ten's wall deaths look the same (reach 1, 99 % enclosed); theirs are rarer because they enter fewer
sealed pockets, not because they die differently. So:

- the ≥ 90 % **north** direction of our wall deaths (unit 3) is the bot's **default action when every move is fatal**, not a
  cull routine; the top ten in the same spot issue an invalid/self command (deliberate) or never get there (orbit);
- "74 % within 5 rounds of the queen's split" is the remnant being short and boxed in right after production, which is when
  it takes Kanazawa's pearl bait into a tree pocket;
- the weakhold r29/r44 determinism is the swarm's deterministic march into the same dead-end cells.

**Replacement:** the queen fix for the corridor maps is Kanazawa's **H-KZ12 veto** (never enter an acyclic pocket of ≤ 5 cells,
pearl or not — 16/19 of our fatal entries had a free alternative) together with Himeji's **H-H3** (legal continuation when
sealed: split-and-patrol in cycles, as the cage keepers do) and Shenzhen's H-SZ1 for the Schooltime cage. H-C5 ("exempt the
queen from the cull") is withdrawn; H-C6 (cull channel) is withdrawn with it — there is no cull routine to redirect. The
unit-3 *measurements* stand (per-map wall shares, timing after the split, 0/172 alive); only their mechanism reading changes.

## 2. Opening components at r25 / r50 / r100, post-m2, z against the per-map field (series table)

| round | group | n | transits (z) | transits raw | territory (z) | total (z) |
|---|---|---:|---:|---:|---:|---:|
| 25 | top10 (ranked) | 2,415 | +0.14 | 1.97 | +0.13 | +0.24 |
| 25 | us | 286 | −0.43 | 0.90 | +0.07 | −0.33 |
| 50 | top10 | 2,415 | +0.19 | 5.73 | +0.17 | +0.27 |
| 50 | us | 286 | −0.42 | 3.13 | +0.06 | −0.22 |
| 100 | top10 | 2,415 | +0.24 | 17.62 | +0.19 | +0.29 |
| 100 | us | 286 | −0.36 | 11.50 | +0.04 | −0.22 |

Top-10 − us: **transits 0.57 / 0.61 / 0.60 SD** at r25/50/100 (raw: they transit 1.8× as often by r50), total 0.57 / 0.49 /
0.51, territory 0.06–0.15. Transits remain the largest single opening component on the new maps, as they were on the old
(Antioch 0.56; Shenzhen live 0.65). Combined with unit 5 § 4 (sides at r50): splits 0.46, units 0.41, bed pearls 0.40,
pearls 0.39.

## 3. The r50 gap per new map (z vs per-map field; top ten ranked n 52–172, us n 4–23 — Devil/Stripes/QoS/PD us ≤ 12)

| map | field n | field transits@50 | top-10 / us transits@50 | gap transits | gap bed | gap splits | gap pearls | **gap total** |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| Trauma | 900 | 3.5 | 4.1 / 2.3 | 0.77 | 1.22 | 1.13 | 1.20 | **1.12** |
| Prisoners Dilemma | 364 | 3.5 | 4.3 / 3.0 | 0.34 | 0.92 | 1.05 | 1.11 | 1.07 (us n 4) |
| Maze | 846 | 0.7 | 0.7 / 0.1 | 0.38 | 0.80 | 0.74 | 0.74 | 0.89 |
| Around UNSW | 886 | 1.5 | 1.7 / 0.1 | 0.80 | 0.98 | 1.54 | 1.29 | 0.84 |
| weakhold | 736 | 0 | — | — | −0.42 | −0.50 | −1.00 | 0.78 (no portals; our swarm dies sealed, unit 3) |
| Schooltime | 1,050 | 4.3 | 5.3 / 3.0 | 0.62 | 0.33 | 0.64 | 0.43 | 0.76 |
| Australia | 936 | 5.1 | 5.7 / 0.9 | **1.06** | 0.91 | 0.99 | 0.90 | 0.73 |
| Autarky | 818 | 6.7 | 7.9 / 1.8 | 0.90 | 0.34 | 0.28 | −0.10 | 0.71 |
| Stripes | 660 | 9.2 | 10.9 / 4.6 | 0.97 | 1.05 | 1.11 | 1.11 | 0.71 (us n 9) |
| Prisoners Dilemma 10 | 396 | 2.8 | 3.3 / 3.5 | −0.06 | 0.84 | 0.95 | 0.93 | 0.66 |
| Portals | 982 | 16.6 | 16.6 / 10.0 | 0.51 | 0.90 | 1.03 | 1.03 | 0.61 |
| Slithery Fight | 998 | 5.3 | 6.5 / 3.2 | 0.79 | −0.28 | −0.29 | −0.43 | 0.48 |
| Default | 856 | 9.0 | 13.3 / 4.6 | **1.04** | 0.32 | 0.19 | 0.26 | 0.35 |
| Devil | 762 | 0 | — | — | 0.32 | 0.22 | 0.35 | 0.15 (us n 9) |
| Tower Defense | 746 | 0 | — | — | −0.11 | −0.14 | −0.10 | −0.09 |
| Islands | 870 | 13.2 | 14.1 / 12.7 | 0.13 | −0.28 | −0.12 | −0.06 | −0.27 |
| Trophy | 824 | 1.7 | 1.9 / 1.2 | 0.33 | −0.33 | −0.26 | −0.14 | −0.41 |
| Queen Of Spades | 794 | 4.0 | 4.7 / 4.9 | −0.06 | −0.49 | −0.47 | −0.49 | −0.61 (us n 12) |

Reading. The opening gap is **map-concentrated**: ≥ 0.7 SD on Trauma, Maze, Around UNSW, weakhold, Schooltime, Australia,
Autarky (and PD/Stripes on tiny us samples); at or above the top ten on Islands, Trophy, QoS, Tower Defense. Where the gap is
large, *all* components move together (bed, splits, pearls ≈ 0.8–1.5), i.e. the starved-opening pattern (L35), not a
single lever — except Autarky and Default, where the gap is almost entirely **transits** (0.9–1.0) with bed/splits near
zero: those two are the portal-gated opening switch's (L41) cleanest test maps. Slithery is the odd one: we out-eat the field
early (bed −0.28, pearls −0.43) yet transit less and end 0.48 behind on total.

## 4. Readings

- **Rome's D-043 zero** (carthage-05 on `LIVE_MAPS_M2`, 816/816 pool, 1,392 gen): pool .804, queen reached/alive r490
  **444/2**, queen-decided losses 19/160 of pool losses. Matches the live 0/172 and 20 % queen-decided losses: the panel now
  reproduces the ladder's queen problem, which it never did on the old maps. Good zero; the four timeouts (Himeji H23-06) are
  missing outcomes, not losses.
- **Rome's cage package** (H-SZ1/21/22 dose dial, parent carthage-05): right first arm per D-043. Expect the Schooltime
  queen column to move toward the field's 0.86 and nothing else to change (parity on non-cage maps); do not read any
  Trauma/Portals change into it.
- **Kanazawa H-KZ11/12/17**: the tree-pocket veto is the corridor-map queen fix and is also a swarm fix (our non-queen wall
  deaths have the same sealed signature, 18,639 of them, 9.3/1k vs the top ten's 2.1/1k — unit 3). Suggested size: the four
  corridor maps, seeds 1–3; endpoints queen alive@RL-end and wall deaths/1k, with pearls@50 as the cost guard (the pearl
  bait is food we currently eat).
- **Shenzhen** (late economy is 85–99 % corpse pearls; top ten eat 46–60 % more corpses after r150): consistent with the
  Slithery row above (we out-eat early, lose late) — the late-game recycling loop is a separate lever from the opening.

## 5. Store / replies

Himeji H25-05: correct — `canon` keeps the first part per game, so the fixed `q_*` columns apply only to games decoded after
05:20Z; a migration of the 3 Oct 23:16Z–4 Oct 05:20Z parts (~1,700 games) is queued behind the backlog; the `qd/qs` views
are unaffected. H25-06: "reference grade" withdrawn as a label — the per-map queen rows are "tables, refreshed each unit"
until Himeji's independence/drift criteria are checked; cohort means, not team medians. Nara C5-06: both tables use the
current-ladder cohort at build time (mine 05:17Z); I will stamp the snapshot id in every table header from now on.

Ledger: H-C5, H-C6 **withdrawn** (mechanism was wrong); their evidence transfers to L24 (enclosure hazard, → 0.6 proposed:
the sealed signature is 92–99 % of our wall deaths) and to Kanazawa's H-KZ12. L41 (early portal use) 0.5 → 0.6: transits
is the largest component on the new maps too, and Autarky/Default isolate it. L35 (starved openings) unchanged, re-keyed to
Trauma/Maze/Around UNSW/Australia on the new maps.
