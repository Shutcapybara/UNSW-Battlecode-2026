# Rome07 — Schooltime cage safety, E3 screen

Parent: `carthage-05-free-sprint` (post-M2 zero, `unswbc 1.2.3`). One package switch, copied from the parent:
when every simulated move is fatal, a dragon at length ≥4 splits and retains length 2; a shorter non-queen issues the
invalid command rather than colliding with an ally. Original queens do not pay sprint segments. Non-queen decisions
use a cap reduced by three units to reserve capacity for the caged queen.

Dose dial preregistered on 2026-10-04: dose 0 is unchanged parent; dose 1 uses the same C+D+E package with one
reserved slot; dose 3 is this C+D+E3 package. Expected sign: improve Schooltime queen survival and queen-decided
outcomes; E3 should reduce cap deaths at least as much as E1, with possible economy/material or win cost on other maps.
This is a seed-1 screen on the M2 pool and current gen panel; it is not a deployment-gate result.

This is a screening arm. It is not tagged as a shippable candidate. D-044 requires a learned-policy translation in the
finding before any later deployment decision.
