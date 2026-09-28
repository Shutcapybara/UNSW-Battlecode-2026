---
id: A1-Q3-layout-assignment
author: gpt-6/analysis/codex-session
kind: hypothesis
title: Layout balance remains unresolved in the current local mirror
task: A1 statistics analysis
supersedes: none
evidence: current hub schema and selected live result fields; historical assignment analysis incomplete
---

The live record stores map hash, seed, request time, series, side and source, and the hub code now emits descriptive layout counts by map/source/side plus repeated map/seed conflicts. This snapshot does not establish a layout assignment rule: no fitted model or controlled request-order experiment has been run. The handoff's reported block pattern (opposite layouts for 10/10 maps in one block, matching 9/10 and 8/9 in two others) is not treated as a re-derived result here.

**Decision:** Do not change fill order based on this evidence. Balance arms by recorded layout when possible, but retain layout as a stratum in contrasts.

**Falsifier:** Repeated map/seed observations demonstrate deterministic seed-to-layout mapping and a replicated request-pattern intervention changes which arm receives which layout; that would justify a deliberate request policy.
