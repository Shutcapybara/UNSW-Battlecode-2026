# THE GOAT v04 — bounded sprint

Lineage: **THE GOAT**. Parent: `the-goat-v02-sprint-discipline`.

This immutable arm keeps v02's retained sprint weight (`w_sprint = 1.5`) and
adds only bounded search budgets: lower cold-start target expansion, dense
target expansion, short-sprint enumeration, newborn escape nodes, and flood
caps. The change responds to the pinned sandbox result for v02, which exceeded
the CPU maximum on the Schooltime probe.

It is a runtime-recovery candidate, not a promotion claim. It must pass the
four sandbox probes and repeat the live/generalisation strategy screens before
it can replace v02.
