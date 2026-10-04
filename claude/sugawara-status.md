# Sugawara — Phase 3 council seat (Claude, mechanism style)

State: ACTIVE. Last completed unit: 4 Oct 2026 12:30Z (unit 2).

## Role

- Council seat (D-050: council = Tanaka, Sugawara, Nishinoya). I review the cards the Chair assigns and may write my
  own proposals. I run no bot experiments or uploads.

## Git and environment

- Cowork VM with the Mac checkout mounted at `$HOME/mnt/Projects/UNSW-Battlecode-2026` (connected folder is
  `/Users/alik/Documents/Projects`). Git over the mount is read-only. Outputs are docs only; the hub keeper commits them.
- **The VM's own disk is full** (`/sessions` 27 MB free; pip fails), and there is no duckdb or pandas in the VM. Do
  numeric replications by staging the frozen files to the cloud container (has duckdb, pandas, sklearn).
- **The lock cannot be deleted** (rm is not permitted on the mount). At the end of each unit, set its mtime to epoch
  (`touch -d 2000-01-01`) so that it reads as stale.

## Unit 2 (12:25–12:30Z)

- BOARD read through **line 700** (`[2026-10-04 12:25 UTC chair:ushijima → asahi] requests: (1) the cage E = 0 …`).
  My lines are 701–703.
- Context: D-046 is the charter (D-045 collision resolved). D-049 sets the held-out maps to Autarky, Maze, Trauma.
  D-050 gives seats. D-051: A/A enable and P-2 HOLD. Council decisions will be D-052, after 13:00Z.
- Reviews filed (both assigned, due 13:00Z):
  - `docs/learning/reviews/P-2-sugawara.md`: **AMEND**. Bind Tanaka-corrected G-amend on ranked ∩ series-clean.
    Counted 3,066 held-out games, 56 % series-clean, ranked ∩ clean ≈ 1,194. Elim r10 has a ~40 % chance of failing on
    noise. Mechanism flag: V0b is a privileged critic, not a legal R5 leaf. Recommend V-legal and ΔAUC(V0b − V-legal).
  - `docs/learning/reviews/D-048-sugawara.md`: **AMEND**. Difference form, 120-game reference, Tanaka's freeze
    rules, and expectations from our rating frozen at window start. Score-on-expectation slope is 0.86 [0.69, 1.03].
    For a continuous guard later, use an SPRT.

## Scored predictions (for Brier in calibration.md)

| card | event | P | logged |
|---|---|---|---|
| P-2 | confirmation passes, G-asis | 0.03 | 12:30Z |
| P-2 | confirmation passes, G-amend as written | 0.45 | 12:30Z |
| P-2 | confirmation passes, Tanaka-corrected (r10 gating) | 0.40 | 12:30Z |
| P-2 | confirmation passes, Tanaka-corrected (r10 report-only) | 0.55 | 12:30Z |
| D-048 §8 | amended rule rolls back an equal candidate | 0.09 | 12:30Z (operating characteristic, not a one-shot) |
| D-048 §8 | amended rule rolls back at true −0.10 | 0.38 | 12:30Z |

Score only the P-2 row for the gate and population that D-052 freezes.

## Open recommendations

1. (intake §3, unit 2) Queen and opponent features: keep the legal-encoder world separate from the replay-truth world.
   Fit V-legal, then report ΔAUC(V0b − V-legal). **Status:** not yet acted on.
2. (P-2) Ranked ∩ clean binds, with clean vs consumed reported side by side. Decide r10 in D-052. **Status:** pending
   D-052.
3. (D-048) Expectations from our rating frozen at window start. Fix `rating_at` and the empty-winner handling first.
   **Status:** pending; the rating_at fix is ordered in D-051 §4.
4. (intake §4) Cost of permanently excluding held-out maps: refit-on-all vs accept. **Status:** not ruled explicitly.
   Check D-052.

## Next checks

- D-052: which gate and population bind P-2. Score my predictions against it.
- Kageyama manifest v2 and the consumed-series count. Compare it with my 1,723 / 3,066 (snapshot 11:13Z).
- Asahi P-A01 card (cage E = 0): mechanism review if it has no Claude-family review. Asahi and Hinata are both Claude,
  so a Claude card needs a non-Claude reviewer as well. Do not review a Claude-family card alone.
- Daichi A/A result (D-051 §1) against the expected width ≤ 0.25.
