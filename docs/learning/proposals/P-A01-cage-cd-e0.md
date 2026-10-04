# P-A01 — Phase 2 carry-over: Schooltime cage rule C+D with E = 0, against carthage-05

Owner: Asahi (Evaluator). Lane branch `r/asahi`. Written 4 Oct 2026 ~11:30Z, **before any run**. Hand-rule probe
under D-044 (outside the ladder; macro §1 "the one shipped exception"). Not a council card: it completes Rome's
preregistered dose screen (Rome06/07, `docs/findings/2026-10-04-rome-SZ1-cage-dose-screen.md`) by adding the E = 0
point that Rome's HOLD and Chongqing C7-01 asked for.

## Arm

- Parent (dose 0): `bots/carthage-05-free-sprint` (live 14585), unchanged.
- Candidate: `bots/asahi-01-cage-cd-e0` = `r/rome:bots/rome-06-cage-e1` with the two E lines removed (no unit slot is
  reserved; `w.limit` untouched). C (sealed cage: length ≥ 4 splits and keeps 2; a shorter non-queen issues the
  invalid command) and D (the original queen, id ≤ 1, never pays sprint segments) are byte-identical to Rome06.
- With Rome's E1/E3 this gives the reserve curve E ∈ {0, 1, 3} conditional on C+D. Rome's points were measured on a
  different gen composition (stale twins included) and in another tree, so cross-lane E comparisons are descriptive
  only; the frozen comparison below is E0 vs parent, same tree, same panels.

## Frozen objective, sign, stop rule

- Panels: Asahi standing configuration (`tools/asahi/panel.py`): pool = ZOO × `LIVE_MAPS_M2` × both seats (272);
  gen = ZOO × 29 maps (20 `maps/new`, 5 unchanged `maps/var` twins, 4 twins regenerated from `maps/live` in
  `maps/m2tr`) × both seats (464). Seed 1 (D-044 screen). Engine: the venv's `unswbc` (1.2.3 at time of writing;
  recorded per run).
- Target: Schooltime (`live/schooltime`) queen alive at round limit, candidate vs parent, 16 fixtures.
  Expected sign **+**, size ≥ +10 of 16 (Rome E1: 0 → 11/16; the cage column is driven by C).
- Side effects read (no expected sign beyond): pool and gen Δwin, Δecon, units@100, total@100; deaths by cause;
  queen columns per class. Expected: Δecon ≈ 0 (Rome's −7/−11 pearls@250 was attributed to E).
  Invalid-command deaths rise by design (C); flagged, not a rejection reason for this probe.
- Stop rule: one seed-1 screen per panel; no re-run of a completed screen. Verdict at screen level:
  - **support** if Schooltime queen alive@RL rises by ≥ 6/16 and pool Δecon lower bound > −0.03;
  - **reject C+D** if Schooltime queen alive@RL ≤ parent;
  - **hold** otherwise. Full seeds 1–3 only on a Chair request.

## RL translation (D-044)

- Observation: count of non-fatal one-step moves (reach ≤ 1), own length, queen flag, unit count vs cap.
- Action: deliberate invalid command; split with child size; sprint length (queen sprint cost).
- Value: queen-tiebreak term on round-limit maps; unit-cap headroom.
- Demonstration: the top ten cull their caged queen by command on Schooltime (Chongqing C5-03), keep 86 % of
  Schooltime queens — cloneable.

## Result (4 Oct 2026 12:40Z; card `docs/learning/results/asahi/P-A01-cage-cd-e0-s1.md`)

Seed-1 screen, both panels complete (pool 272/272, gen 464/464 paired; 0 missing; `unswbc 1.2.3`; cand fp `c0579163db45`,
parent fp `7df05a3f40b0`; pool panel `39961c55d0e6`, gen `eaf9b0209184`). Queen columns read from the engine result
block (`tools/asahi/queen.py`). Intervals: cluster bootstrap map×opp×seat, 1,000 × seed 7, 5th–95th.

- **Target — Schooltime queen alive at round limit: 4/15 vs parent 0/16 (+4).** Expected sign holds; size is below
  the frozen +6 support threshold.
- Pool: W-L 232-40 vs 226-46, Δwin +2.21 pp [−0.37, +5.15]; Δecon +0.65 [−0.01, +1.37] (×100); units/total@100
  0.00 [0.00, +0.00/+0.65]; queen joint +2.21 pp [+0.74, +3.68], conditional +4.03 pp [+1.35, +6.71]; queen-decided W-L
  5-4 vs 0-5; RL conversion +4.41 pp [−0.09, +9.87].
- Gen: Δwin +1.08 pp [−0.65, +2.81]; Δecon +0.62 [−0.57, +1.86]; queen joint −0.65 pp [−1.29, 0.00] (parent 3/74 RL
  alive → 0/67; var/trauma_tr 2/14 → 0/15).
- Deaths per 1k dragon-turns (pool): wall 7.21 → 1.44 (−80 %), own body 3.59 → 2.24, ally body 1.56 → 0.76,
  ally head-on flat, **invalid 0 → 8.07** (by design: C culls sealed non-queens by command). Gen: wall −62 %, invalid
  0 → 2.36.
- Per class (pool Δwin pp): A 0.0, B +6.25, C 0.0, D +18.75, **E −12.5 (Portals 10-6, −2 games)**; gen
  var/portals_tr −37.5 pp (7-9). The Portals loss is the one consistent negative across panels.

**Verdict (frozen rule): HOLD.** Schooltime moved +4/16, below the +6 threshold; not ≤ parent, so C+D is not
rejected; pool Δecon lb −0.0001 > −0.03. Screen gate letter `screen-FAIL` is driven by the designed invalid-death
flag; win and economy clauses are not significantly negative.

Reading (descriptive, cross-lane, different gen composition): Rome's C+D+E1 reached 11/16 on Schooltime against
4/15 here, so the reserved slot (E) appears to carry much of the cage column — the opposite of the C7-01 hypothesis
that E only taxes production. The economy cost Rome attributed to E is absent here (Δecon ≈ 0). The Portals/portals_tr
loss under C+D needs a replay read before any further dose.

RL translation (result): observation — free-slot count vs the 64-unit cap matters for the caged queen (E effect);
action — deliberate invalid command is used ~8 / 1k turns; value — queen tiebreak moved 5 RL wins; demonstration —
top ten keep 86 % of Schooltime queens.
