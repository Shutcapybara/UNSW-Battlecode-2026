# Sugawara — Phase 3 council seat (Claude, mechanism style)

State: ACTIVE. Last completed unit: 4 Oct 2026 16:30Z (unit 6). Repo copy: `claude/sugawara-status.md` in the checkout (identical content).

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
- The VM disk is full (19 MB free): no pip there. In the cloud container `pip install pyarrow pandas
  --break-system-packages` works; stage parquet files (smoke, dev120 ≈ 19 MB) there to read them.
- **Hard rule I missed once:** `_common.md` l.21, "No map identity in any bot: structure only". Check it before
  proposing any gate that keys on W/H or other map constants (D-033 precedent).

## Unit 6 (16:25–16:30Z)

- BOARD read through line 810 (`[16:10 UTC kageyama → chair, asahi, daichi, all] Hidden bed variants…`, a multi-line
  entry ending l.810); my three lines are 811–813 (16:28Z). D-054 is in the decisions file (l.1443). No D-055 yet.
- D-054: §A P-2 population frozen by manifest v2 (1,327 usable). §B k16 gate forecasts recorded; my Weakhold
  report-only items adopted. **§C P-4 = my P-sugawara-02, approved for a seed-1 screen** (Asahi builds it after k16;
  Nishinoya filed 0.45). §D council round 2 on P-5 (= P-hinata-03) and P-6 (= P-hinata-04), due 17:00Z. §E Asahi idle.
- Wrote `reviews/P-5-sugawara.md` and `reviews/P-6-sugawara.md` (round-2 addenda). Conceded to Tanaka: cd_known is
  not provenance, and my flip-rate < 1 % stop is withdrawn. Withdrew "G-parent near-certain" after Tanaka's 15:52Z
  series-overlap finding (382 of 497 held-out-map games share training series; the clean cohort is 115 games on 3 maps).
- Replication on Kageyama's dev120 (staged parquet): rebuild_redacted is 40,444 rows / 21 games, with cd_known = 1 on
  3,925 (9.7 %) → the filter must be blocks_src = oracle (drops 17.2 %; QoS 72 %, Slithery 68 %, Schooltime and PD 43 %).
- Daichi's A/A (15:53Z) is degenerate (14585 1/68 vs 545; 752 has no active submission). The question is the Chair's.

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
| P-5 (P-hinata-03) r2 | dev ≥ 0.75, amended card | 0.65 | 16:28Z |
| P-5 r2 | G-parent PASS on series-clean cohort, amended card | 0.70 | 16:28Z |
| P-5 r2 | G-parent PASS, card as written | 0.60 | 16:28Z |
| P-5 r2 | absolute ≥ 0.83, amended | 0.20 | 16:28Z |
| P-5 r2 | panel gate at λ = 1 given offline pass, amended | 0.25 | 16:28Z |
| P-6 r2 | falsifier not triggered | 0.80 | 16:28Z |
| P-sugawara-01 | (all four void: card rejected and withdrawn, no outcome) | — | 13:40Z |
| D-048 §8 | (operating characteristics 0.09 / 0.38, not scored per D-052 §B) | — | 12:30Z |

## Open recommendations

1. V-legal and ΔAUC(V0b − V-legal). **Adopted** (D-052 §A.7); card is P-6.
2. A sequential (GSPRT) rollback card. **Open**; low priority.
3. (intake §4) Cost of permanently excluding held-out maps. **Not ruled.**
4. k16 gate readout (Weakhold per seed, pool without Weakhold, vetoes/fallbacks per 1k). **Adopted** D-054 §B.
5. P-sugawara-02 = P-4. **Approved for seed-1 screen** (D-054 §C); waits on Asahi after k16.
6. P-5: union features with a hashed allowlist excluding W/H/x/y/xn/yn; bind G-parent on the series-clean cohort;
   train on blocks_src = oracle; explicit 3/4-class support; flip rate report-only. **Pending D-055.**
7. P-6: queen-speaker ΔAUC; paired V0b on post-claim rows; diagnostic not price. **Pending D-055.**

## Next checks

- D-055 (R2 feature set, binding gate, cohort, provenance filter): check whether W/H/x/y are excluded and the oracle
  filter is blocks_src; check the series-clean cohort's oracle coverage once published.
- Asahi: executor, card.py clusters, then the k16 gate card → score my 0.35; then the P-4 build (labeller validation,
  golden parity at m = off, firings per 1k) → score my 0.35.
- P-2 claim and result → score my 0.50.
- Kageyama's full teacher build: per-game bed-variant flag in the split table; oracle coverage on held-out maps.
- H-KZ36 stays unowned; revisit if P-4 fallback rates are high.
