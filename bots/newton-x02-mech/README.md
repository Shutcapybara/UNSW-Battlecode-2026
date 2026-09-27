# newton-x02-mech — instrumented master, every Newton mechanism default-off

- **Lineage:** Newton (2026-09-27). Mission: repair fafnir/serre's residual
  compact-contact leak (0-8 vs ouroboros-v13 and tew-v12 on devil+arena) on the
  same chassis. Parent: `bots/fafnir-v01-phalanx` (= `bots/newton-x01-frozen`).
- **Parity:** with every mechanism off this source reproduces newton-x01
  exactly (devil A/B vs v13, outcome/rounds/counters; verified after each code
  addition). The only always-on addition is the split-decision funnel counter
  `policy.SPLITSTAT`, dumped under the `/tmp/sinbad-trace-on` TRACE flag.
- **Dormant mechanisms added** (all default-off, each measured as a cycle-1 arm;
  see `docs/newton.md` for the full ledger):
  - `crown_split` — crown may produce under compact_prod (null result)
  - `guard_age`/`guard_p` — young-dragon threat floor (null result)
  - `fast_edisc_nc`/`fast_edisc_nc_min` — map-size scoping for the fast-bed contest
  - `atk_space*` — space-denial trades (negative alone and combined)
  - `unit_stop_round` — compact production stop for endgame conversion
- **Result:** not promoted; retained as the iteration master for cycle 2.
  Best composite (this master + the n10 override) is `bots/newton-x10-candidate`.
