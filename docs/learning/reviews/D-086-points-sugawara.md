# D-086 §E.1 — points a turn from the corpus: cannot be settled from server replays — Sugawara (unit 30, 5 Oct 2026 16:30–16:45Z)

Asked of Hinata or me (D-086 §E.1): the highest points a turn top-ten dragons used and survived in ranked games.

## Result: the field is not there

- The decoder reads per-action CPU from `action.child(1)` (`tools/analysis/features/frame.py` l.158–160; `tle` from bit 0 of field 4).
- **121 most recent ranked games with a top-ten team** (ladder snapshot 20261005T162705Z, non-dev ranks 1–10; finished 15:16–16:30Z): **0 carry a CPU value** on any action. `build/sugawara/knownbeds/pts.py`, `pts.txt`.
- **Random 60 ranked games, 25 Sep – 5 Oct** (seed 7, pool 88,374): 1,232,166 action records, **15,444 with CPU (1.3 %), all from one game** (1089395, 5 Oct 00:06Z, team 7 = us, seat A only): max 10,070,341, median 6,522,897 — consistent with our probes (12.8 M peak). `tle` bit set on 0 records. `cpu_any.py`, `cpu_who.py`, `cpu_any.txt`.
- So the server writes CPU into a replay rarely and, where seen, only for one side. A full-corpus scan for "any surviving turn > 30 M" would take ≈ 44 h of decoding at ≈ 1 s/game and would mostly read empty fields. **The corpus route does not settle it; Asahi's local burn test (§E.2) is the remaining evidence.** A cheaper filter (a byte signature of the CPU child) could make a scan feasible; I did not build one.

## Documentary evidence already in the repo (for the Chair)

- `docs/BAHAMUT_HANDOFF.md` l.68 (commit 373adefbb, 30 Sep): "Judge limits are 100 million CPU points per dragon per turn and 48 MB memory; initialization also counts", linking the timeouts page.
- `docs/BASELINES-2026-09-30.md` l.43: "9 M points/turn at 8× search, 22 M fully unbounded, against a 100 M cap."
- So two of our own documents from 30 Sep already agree with the contest page; the 30 M figure in the brief/prompts/probes is the outlier. Not a measurement, but it lowers the prior that 30 M is the server's number.

## Forecast (log only)

- Asahi's burn test: a dragon spending ~50 M in one turn survives locally on unswbc 1.2.3: 0.80.
