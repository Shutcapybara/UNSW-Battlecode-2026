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

## Result

(appended after the run)
