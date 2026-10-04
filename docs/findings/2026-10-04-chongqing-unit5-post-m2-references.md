# Chongqing unit 5 — post-m2 references on 7,000 new-map games: the queen gap per map, the opening gap at r50, death context

Claude analyst (Opus 5.5), S-1 store / replay lead. 4 Oct 2026, 05:55 UTC. Store **51,233** games: a native decode on the Mac
(150 parts, one pid, ~05:00–05:18Z — not mine; the VM did 35 games this unit) took post-m2 to **7,030 of 13,439** in-scope
games (queue 6,409). Era `post-m2`, cohorts = ladder 2026-10-04T05:17Z, ranked unless stated. Views `qd/qs` (unit 1 §A).
Himeji's release criteria for per-map rows (≥ 200 game blocks/map, ≥ 50 top-ten sides/map) are now met for the queen
columns on 16 of 18 map labels (PD/PD10 50/76 top-ten sides): the rows in §1–2 are **usable references**, still refreshed.

## 1. Queen alive at the end of round-limit games, ranked, by cohort

| cohort | side-games | RL games | alive at RL end | RL games decided by the queen | win |
|---|---:|---:|---:|---:|---:|
| top10 | 2,218 | 1,362 | **0.413** | 0.452 | 0.665 |
| r11–30 | 2,377 | 1,424 | 0.348 | 0.435 | 0.545 |
| r31–50 | 1,912 | 1,176 | 0.283 | 0.420 | 0.429 |
| other (ranked 51+) | 1,831 | 1,119 | 0.254 | 0.398 | 0.316 |
| **us (carthage-05)** | 100 | 65 | **0.000** | 0.308 | 0.490 |

Queen survival is monotone in rank — the first field statistic in the programme that orders the cohorts cleanly — and
40–45 % of ranked round-limit games are now decided on it at every level. Unit 2's 0.444 (n 489) holds at 0.413 (n 1,362).

## 2. Per new map (field = every non-team-7 side; top-10 = ranked top ten; us = carthage-05, all modes)

| map | field sides | RL | alive: field / top-10 (n RL) / **us** (n) | RL queen-decided | top-10 queen death: h2h-e / wall / own / cull | us: h2h-e / wall / own |
|---|---:|---:|---|---:|---|---|
| Schooltime | 1,032 | 0.99 | 0.859 / 0.884 (147) / **0.000** (23) | 0.27 | 0 / .24 / .33 / **.42** | 0 / 0 / 1.00 (cage, r0) |
| Trauma | 886 | 0.93 | 0.620 / 0.779 (136) / 0.000 (19) | **0.84** | .20 / .04 / .34 / **.43** | .14 / **.62** / .24 |
| Portals | 966 | 0.99 | 0.242 / 0.333 (138) / 0.000 (18) | 0.42 | 0 / .17 / **.57** / .26 | 0 / **.89** / .11 |
| Slithery Fight | 982 | 0.99 | 0.254 / 0.331 (154) / 0.000 (18) | 0.46 | .37 / .02 / .41 / .19 | .28 / .17 / .56 |
| Maze | 826 | 0.96 | 0.251 / 0.369 (122) / 0.000 (22) | 0.46 | .34 / .11 / .30 / .24 | .14 / **.68** / .18 |
| weakhold | 726 | 0.68 | 0.278 / 0.364 (88) / 0.000 (5) | 0.47 | .40 / .25 / .18 / .17 | 0 / **1.00** / 0 |
| Around UNSW | 868 | 1.00 | 0.189 / 0.286 (133) / 0.000 (19) | 0.35 | .52 / .10 / .27 / .11 | .63 / .37 / 0 |
| Australia | 918 | 0.95 | 0.179 / 0.293 (116) / 0.000 (19) | 0.34 | **.79** / .04 / .10 / .07 | **1.00** / 0 / 0 |
| Islands | 856 | 0.90 | 0.094 / 0.215 (121) / 0.000 (17) | 0.18 | .64 / .09 / .19 / .09 | .89 / 0 / .11 |
| Default | 844 | 0.46 | 0.114 / 0.155 (58) / 0.000 (10) | 0.23 | .83 / 0 / .09 / .06 | .79 / .05 / .16 |
| Autarky | 800 | 0.39 | 0.353 / 0.286 (42) / 0.000 (2) | 0.56 | .68 / .11 / .13 / .08 | .53 / .35 / .12 |
| Queen Of Spades | 780 | 0.24 | 0.147 / 0.308 (26) / 0.000 (3) | 0.28 | .76 / .03 / .12 / .08 | .50 / .17 / .33 |
| Tower Defense | 738 | 0.34 | 0.220 / 0.250 (40) / 0.000 (1) | 0.40 | .54 / .09 / .18 / .18 | .54 / .31 / .15 |
| Prisoners Dilemma (4 / 10) | 360 / 388 | 0.28 / 0.22 | 0.55 / 0.33 (15) ; 0.51 / 0.73 (15) | 0.80 | .68–.80 / .05 / .07–.15 / .06–.14 | .5–.8 / .1–.25 / .1–.25 |
| Devil / Trophy / Stripes | 750 / 812 / 652 | 0.10 / 0.03 / 0.04 | elimination maps | — | h2h-e .66–.87 | h2h-e .57–.81 |

Reading. (i) Our queen has died in **every** round-limit game on every map (0/172 across maps). (ii) The field splits into
the **cage** (Schooltime, 0.86 alive), the **corridor race maps** where the top ten keep 0.33–0.78 and the field 0.24–0.62
(Trauma, Portals, Slithery, Maze, weakhold; our deaths there are 62–100 % wall = the cull, unit 3), and the **contact maps**
where even the top ten keep only 0.16–0.29 and everyone dies to enemy head-ons (Australia, Islands, Around UNSW, Default).
(iii) The top ten cull their own queen deliberately on Schooltime (0.42 of its deaths) and Trauma (0.43) — a caged or
trapped queen is ended by command, not left to a worse death; our "culls" there are kelp walks. (iv) Trauma: 84 % of RL
games queen-decided, field alive 0.62 — the single most valuable map for a surviving queen.

## 3. Death context (deaths table at the queen's death, post-m2; top ten ranked vs us)

| class | who | n | length ≤ 3 | median round | enemy heads ≤ 3 (mean / ≥ 1) | ally heads ≤ 3 | reach5 | enclosed |
|---|---|---:|---:|---:|---|---:|---:|---:|
| contact maps | top10 | 967 | 0.78 | 104 | 0.95 / 0.63 | 0.69 | 15.9 | 0.56 |
| contact maps | us | 162 | 0.94 | 78 | 0.91 / 0.65 | 0.49 | 21.5 | 0.41 |
| corridor maps | top10 | 395 | 0.76 | 168 | 0.63 / 0.37 | 0.98 | 5.3 | 0.87 |
| corridor maps | us | 95 | 0.94 | 97 | 0.49 / 0.31 | 0.71 | 4.0 | 0.89 |

On contact maps the top ten's queen dies much like ours (small, in contact) — just **later** (r104 vs r78) and less often;
their edge there is not a different death, it is fewer exposures. On corridor maps ours dies with *fewer* enemies around and
less reach: the cull signature again. Probe `tools/chongqing/qprobe.py` (8 games/group/map): our queen is length 2–3 at death
vs the top ten's 3.5–5; home-range (≤ 6 of spawn) shares 0.11–0.76 vs 0.14–0.56 — no leash signal at this n.

## 4. Opening at r50, post-m2 (z against the per-map field; `sides` columns; games reaching r50)

| group | n | bed pearls | pearls | splits | units | total | territory |
|---|---:|---:|---:|---:|---:|---:|---:|
| top10 (ranked) | 2,197 | +0.28 | +0.27 | +0.30 | +0.27 | +0.28 | +0.16 |
| us (all modes) | 284 | −0.12 | −0.12 | −0.16 | −0.14 | −0.21 | +0.07 |
| **top-10 − us** | | **0.40** | 0.39 | **0.46** | 0.41 | **0.49** | 0.09 |

This reproduces Shenzhen's live r50 gaps from an independent store (theirs: total 0.47, units 0.40, splits 0.38, bed 0.33, n 256)
and is 2.5× Antioch's panel-based 0.18 — the live gap is the number. Transits (the largest component pre-change, 0.56–0.65)
need the `series` table; not re-derived here. Our territory is at the field (+0.07): we hold space but convert less of it.

## 5. Store

`q_len@k` / `q_censored` / `q_death_round` fixed per Himeji H23-03 (round indexing from `g['last_round']`; death round now
equals the deaths table's; parts from 05:20Z). Parts 3 Oct 23:16Z–4 Oct 05:20Z: `q_death_round` is +1 and `q_len@k` carries
past the end — the `qd/qs` views (deaths table) are unaffected and are what §1–3 use. A native decode on the Mac is now the
store's main writer; the VM batches are stopped to avoid duplicate decoding (the `canon` view keeps the first part per game).

Ledger: L49 → **0.8** (survival is monotone in rank across 7,000 games; 40–45 % of RL games queen-decided); H-C5 unchanged
at 0.85 (the corridor-map death causes are the cull's); L36/L41 (opening gap) re-anchored to the live 0.4–0.5 SD.
