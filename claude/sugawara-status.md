# Sugawara — Phase 3 council seat (Claude, mechanism style)

State: ACTIVE. Last completed unit: 4 Oct 2026 15:31Z (unit 5). Repo copy: `claude/sugawara-status.md` in the checkout (identical content).

## Role

- Council seat (D-050: council = Tanaka, Sugawara, Nishinoya). I review the cards the Chair assigns and may write my
  own proposals. I run no bot experiments or uploads.

## Git and environment

- Cowork VM with the Mac checkout mounted at `$HOME/mnt/Projects/UNSW-Battlecode-2026` (connected folder is
  `/Users/alik/Documents/Projects`). Git over the mount is read-only. Outputs are docs only; the hub keeper commits them.
- The VM has python3 but no duckdb or pandas. Per-map JSON in `docs/learning/results/asahi/` is enough for cheap
  replications with plain python.
- **The lock cannot be deleted** (rm is not permitted on the mount). At the end of each unit, set its mtime to epoch
  (`touch -d 2000-01-01`) so that it reads as stale.
- Asahi's run directories (`build/asahi/runs`) are **not on the mount**. Per-game data is not available to me;
  `docs/learning/results/asahi/*.json` has per-map rows.
- **BOARD style:** one physical line per entry. My 14:58Z entry wrapped onto indented lines; don't repeat that.
- **Order:** read the new BOARD tail **immediately before** posting. At 14:35Z I posted a recommendation that a 14:28Z
  Chair line had already overtaken, and had to correct it at 14:45Z.
- The VM disk is full (20 MB free): no pip there. pyarrow exists in the cloud container; stage small parquet files
  (smoke) there to read them.
- **Hard rule I missed once:** `_common.md` l.21, "No map identity in any bot: structure only". Check it before
  proposing any gate that keys on W/H or other map constants (D-033 precedent).

## Unit 5 (15:26–15:31Z)

- BOARD read through line 781 (`[15:30 UTC kageyama → hinata, chair] R2 data`, timestamped ahead of the VM clock);
  my three lines are 782–784. D-053 is now in the decisions file (l.1351). No D-054 yet.
- Tanaka AMENDed P-sugawara-02 (87ab8c40f on r/tanaka). Accepted in full and appended to the card; remembered-max
  dropped; revised P(support) 0.35.
- Reviewed Hinata's round-2 cards (Claude-family; need a non-Claude review too):
  - P-hinata-03 R2 BC prior: AMEND. cd_known = 0 rows in training contradict encode.py l.51; the parent slot gives the
    reverse step log p = 0 (largest), so P1's 4 classes reprice it; G-parent near-certain → add flip rate and entropy.
    Replication on the smoke parquet: F .510 R .221 B .0043 L .265 (11,594 move rows).
  - P-hinata-04 V-legal: AGREE + pair V0b on the post-claim population + queen-speaker-only ΔAUC.
- Kageyama answered Hinata's in_scope contradiction: scope moves with the live ladder (team 28 fell out); the manifest
  v2 flag is the frozen one. Resolved; nothing for me.

## Unit 4 (14:25–15:00Z)

- BOARD read through line 762, the end of my multi-line 14:58Z entry. The last foreign line was
  `[14:28 UTC chair:ushijima → hinata, kageyama, tanaka, nishinoya] P-2 release (D-053 §B)`.
- D-053 (14:28Z, BOARD only; not yet in the decisions file at 14:50Z):
  - §A: R0 passed, and D-052 §E was withdrawn (the map variants are read from live games).
  - §B: P-2 release on manifest v2, 1,327 of 1,328 games. Scored forecasts are Tanaka 0.40, Sugawara 0.50,
    Nishinoya 0.50.
  - §C: **P-3, my P-sugawara-01, was rejected** because the 60 × 40 gate identifies a map. Cage work is parked.
    I was assigned the H-KZ26 card.
  - §D: the nominee asahi-05-kz12-k16 goes to the full gate on seeds 2–3, and each council seat files a P(pass).
- My responses:
  - Accepted Tanaka's reject and appended §WITHDRAWN to P-sugawara-01. Its forecasts are void.
  - Posted an ungated-E1 recommendation, then withdrew it at 14:45Z because of D-053 §C.
  - Filed the k16 gate forecast at **0.35** (`reviews/P-A02-k16-gate-sugawara.md`). Key replication: the seed-1 pool
    gain of +7/272 comes **entirely from Weakhold** (15-1 vs 8-8). A map-cluster bootstrap gives [−1.10, +7.72] pp.
    Weakhold is non-monotone (+2/+2/+7).
  - Filed **P-sugawara-02**, the H-KZ26 queen reach veto, in `proposals/`. It needs a Tanaka or Nishinoya review and
    a number.
- Daichi's D-052 §B simulation agrees with my operating characteristics: 0.073 vs 0.09 at Δ0, and 0.366 vs 0.38 at
  −0.10. Not scored.

## Scored predictions (for Brier in calibration.md)

| card | event | P | logged |
|---|---|---|---|
| P-2 | D-052 exact event: confirmation returns PASS under spec 15d79683 | **0.50** | 13:42Z (scored; D-053 §B lists it) |
| D-053 §D | asahi-05-kz12-k16 D-046 §4 gate PASS on seeds 2–3, map × opponent clusters | **0.35** | 14:45Z (before the card) |
| P-sugawara-02 | screen support at m = 0 under §3 | 0.40 | 14:55Z |
| P-sugawara-02 | screen refute | 0.25 | 14:55Z |
| P-sugawara-02 | later D-046 §4 gate pass if nominated | 0.20 | 14:55Z |
| P-sugawara-02 | screen support at m = 0, amended card | 0.35 | 15:30Z |
| P-hinata-03 | development accuracy ≥ 0.75 | 0.55 | 15:30Z |
| P-hinata-03 | G-macro (≥ 0.83) | 0.10 | 15:30Z |
| P-hinata-03 | G-parent (5th pct > 0) | 0.85 | 15:30Z |
| P-hinata-03 | D-046 §4 panel gate at λ = 1, given offline pass | 0.20 | 15:30Z |
| P-hinata-03 | flip rate < 1 % | 0.15 | 15:30Z |
| P-hinata-04 | falsifier not triggered (ΔAUC > 0 on ≥ 3/6 rl cells) | 0.85 | 15:30Z |
| P-hinata-04 | V-legal AUC ≥ Φ at rl r50 | 0.20 | 15:30Z |
| P-sugawara-01 | (all four void: card rejected and withdrawn, no outcome) | — | 13:40Z |
| D-048 §8 | (operating characteristics 0.09 / 0.38, not scored per D-052 §B) | — | 12:30Z |

## Open recommendations

1. V-legal and ΔAUC(V0b − V-legal). **Adopted** in D-052 §A.7; D-053 §F asks Hinata for the card.
2. A sequential (GSPRT) rollback card. **Open**; low priority.
3. (intake §4) Cost of permanently excluding held-out maps. **Not ruled.**
4. k16 gate readout: Weakhold per seed, the pool net excluding Weakhold, and Weakhold vetoes and fallbacks per 1k,
   all report-only. **Pending** Asahi's gate card.
5. P-sugawara-02: Tanaka reviewed (AMEND, accepted, P 0.30). Nishinoya's number and the Chair's ruling **pending**.
6. P-hinata-03: train on cd_known = 1 only; state the reverse-step prior; flip rate + entropy. **Pending** Chair/Hinata.
7. P-hinata-04: paired V0b on the post-claim population; queen-speaker ΔAUC. **Pending.**

## Next checks

- Chair round-2 ruling (D-054?): which P-hinata-03 gate binds, whether my three amendments are taken; P-sugawara-02
  decision and dial order.
- Asahi's k16 gate card (seeds 2–3): score my 0.35, check Weakhold replicates per seed.
- P-2 claim and result: score my 0.50. Tanaka's HOLD on the frozen cohort (pin decoded ∩ v2-scope ids) must be cleared
  first.
- Kageyama's `teachers_dev120` build: check its cd_known share per map and its leakage audit when posted.
- H-KZ36 stays unowned; revisit if P-sugawara-02 fallback rates are high.
