# R-2 `sciel` status — Sciel lineage (GLM 5.3)

Base: `ares-v06-expanded-search-support`, atlas off (no `claude/r1-status.md` exists in any worktree
as of lane start, so the brief's default V06 base applies; Ares V06's atlas helper has no call site
either way). Worktree `../wt-sciel`, branch `r/sciel`. Run env `~/.venvs/bc122` (unswbc 1.2.2).

`sciel-00-base` = byte-identical Ares V06 policy + documenting `Params::atlas_enabled=false`.
Golden parity vs the ra lane's Ares V06 transcripts: **52,728 turns / 1,842 dragons across
schooltime-A, portals-B, slithery_fight-A, trauma-B (seed 1), 0 divergent**.
Fingerprint `779808b9c98f99b4d8f432398f78f290dade2f2061e8d54736a2b6d2ecfff205`.
Lane tooling copied from `tools/ra/` (ra's lane.py/variant.py/gen_reference.json, paths moved to
`tools/sciel/`, `build/sciel/runs`) — thanks ra; scoring logic unchanged.

Mechanism picks read (before choosing): ra has rejected, all vs its base — bed anticipation
(01a-c), child-room gate 4→8 (02a), pearl-TTL 40→20 (08a), threat ×0.25 (17c), revisit 0.05 (18a),
enemy-density devaluation off (19a), hunters from r40 (20b), strike margin 0 (21a); r3 rejected
pair-memory, exit-known, kelp-cost, escape-early held (+5pp win, own-body +11% guardrail).
**Untried per the R-3 director-read and the C1-C ledger: newborn siting and post-transit
navigation** — this lane starts with the first and holds the second.

| Version | Mechanism | Pool delta | Generalisation panel delta | CPU max | Verdict | Why |
|---|---|---|---|---:|---|---|
| sciel-01a-siting | Newborn siting: split score gains siting term for child spawn cell (food arrival-earliness within 4 via parent knowledge − reference 5.0, ×0.8; ally-crowd at spawn, cap 2.0) | econ~ −0.003 (mean −0.004); win 0.725 vs 0.762 (pairs 2/150/8, p=0.11); nb10 34.6→34.6 (statistic unmoved) | ≡ base (pearls 1/244/3; win 0.540 vs 0.520; var+devil_tr +0.100 the only mover) | 8.60M | **REJECT** | Mechanism barely fires (golden: 1 divergence in 13,649 schooltime turns): a len-4 parent just ate, so its tail is near food by construction; where it did fire (portals −0.018, devil −0.015) econ fell — the delay costs more than the sit buys. Kill number: pool econ~ −0.003 vs +0.05 gate. Switch stays (sit_enabled, default off in future parents). Untested variant for later: hand the child its first target in the birth packet (needs a new payload field), rather than shaping timing. |

Base reference numbers (seed 1, 160 side-games): econ~ 1.111, win 0.762, u100|n~ 1.20, t100|n~ 1.04,
wall 8.74, self 5.74, nb10 34.6. Gen (248): econ 1.098 abs, win 0.520.
