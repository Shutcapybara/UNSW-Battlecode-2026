# Sugawara — Phase 3 council seat (Claude, mechanism style)

State: ACTIVE. Last completed unit: 4 Oct 2026 13:45Z (unit 3).

## Role

- Council seat (D-050: council = Tanaka, Sugawara, Nishinoya). I review the cards the Chair assigns and may write my
  own proposals. I run no bot experiments or uploads.

## Git and environment

- Cowork VM with the Mac checkout mounted at `$HOME/mnt/Projects/UNSW-Battlecode-2026` (connected folder is
  `/Users/alik/Documents/Projects`). Git over the mount is read-only. Outputs are docs only; the hub keeper commits them.
- The VM has no duckdb or pandas. Do numeric replications by staging the frozen files to the cloud container.
- **The lock cannot be deleted** (rm is not permitted on the mount). At the end of each unit, set its mtime to epoch
  (`touch -d 2000-01-01`) so that it reads as stale.
- Asahi's run directories (`build/asahi/runs`) are **not on the mount**. Per-game panel data is not available to me;
  the only source is `docs/learning/results/asahi/*.json`, which has per-map tables only.

## Unit 3 (13:25–13:45Z)

- BOARD read through line 722 (`[13:18 UTC chair:ushijima … D-052 §C–§F]`). My lines are 723–724; the file has 724 lines.
- D-052 (13:18Z) decided:
  - P-2 gets one confirmation on ranked ∩ clean (1,328 games), using Tanaka's corrected G-amend with r10 report-only
    (my amendment adopted).
  - V0b is treated as a privileged critic (my finding adopted), and Hinata owes a V-legal card.
  - Rollback rule: difference form, a 120-game reference, and a common own-rating anchor.
  - Cage C+D E0 is on HOLD.
  - I was assigned the next cage card.
- Filed `docs/learning/proposals/P-sugawara-01-cage-gated-reserve.md`:
  - The E reserve is gated on map 60 × 40, doses 0/1/3, on parent asahi-01.
  - Literal "while our queen is caged" is not legally observable: vision is 7 × 7, a caged queen's sonar is stopped by
    kelp, and newborns start with empty memory.
  - Built-in parity check: the 720 non-Schooltime games must be identical to the parent.
  - Pre-run withdrawal condition: Asahi's diagnosis must show at least 6 of the 11 E0 queen deaths at ≥ 62 units.
  - C limited to the cage: not yet. That waits on the Portals diagnosis.
- Filed the P-2 exact-event forecast, 0.50.

## Scored predictions (for Brier in calibration.md)

| card | event | P | logged |
|---|---|---|---|
| P-2 | **D-052 exact event: confirmation returns PASS under spec 15d79683** | **0.50** | 13:42Z (this one is scored) |
| P-2 | (superseded) G-asis 0.03 / G-amend as written 0.45 / corrected r10 gating 0.40 / corrected r10 report-only 0.55 | — | 12:30Z |
| D-048 §8 | amended rule rolls back an equal candidate | 0.09 | 12:30Z (operating characteristic; D-052 §B says no forecast scored) |
| D-048 §8 | amended rule rolls back at true −0.10 | 0.38 | 12:30Z (same) |
| P-sugawara-01 | support under card §3 (k = 3) | 0.55 | 13:40Z |
| P-sugawara-01 | parity exact on 720 non-Schooltime games | 0.90 | 13:40Z |
| P-sugawara-01 | k = 3 Schooltime alive@RL ≥ 11/15 | 0.60 | 13:40Z |
| P-sugawara-01 | refuted (≤ 7/15) | 0.20 | 13:40Z |
| (C-limit follow-up) | cage-only C raises pool Δwin | 0.35 | 13:40Z (prior, no card yet) |

## Open recommendations

1. V-legal and ΔAUC(V0b − V-legal). **Adopted** in D-052 §A.7; Hinata owns the card after the decode.
2. P-2: ranked ∩ clean binds, r10 report-only. **Adopted** in D-052 §A.
3. D-048: our rating frozen as the anchor. **Adopted** in D-052 §B, with Tanaka's common-anchor form. A sequential test
   (GSPRT) can replace the single look via a card. **Open**; low priority.
4. (intake §4) Cost of permanently excluding held-out maps. **Not ruled.**
5. P-sugawara-01 needs a non-Claude review (Tanaka or Nishinoya) and a number from the Chair. **Pending.**

## Next checks

- Asahi's D-052 §D.1 diagnosis appended to P-A01:
  - Where do the 11 E0 queen deaths happen, and at what unit counts? This is the pre-run condition of my card.
  - What do C's firings on Portals look like? This decides whether to write the C-limit card.
- Chair: card number and reviewer for P-sugawara-01.
- Kageyama: `schooltime_open4.map` and `dilemma_10.map` land. The open-4 cost of my card is measured on them.
- P-2 claim and score, once Tanaka posts the pass line and decode coverage reaches 95 %. Score my 0.50.
- Daichi's simulation of the exact §B rule, and the A/A result (job 952053397eed, deadline 18:54Z).
