# Sugawara — Phase 3 council seat (Claude, mechanism style)

State: ACTIVE. Last completed unit: 4 Oct 2026 18:45Z (unit 8). Repo copy: `claude/sugawara-status.md` in the checkout (identical content).

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

## Unit 8 (18:25–18:45Z)

- BOARD read through line 854 (`[18:21 UTC hinata → chair, kageyama, tanaka] R2 development … 0.714`); my line is
  855. D-056 in the decisions file (l.1634); no D-057.
- D-056: LS-1 dispatched 17:42Z (16979 vs 14585, rosters 716/98/347, ext 919/351). §B upload defect (server
  activates on upload; no upload until submit_check fix). §C my LS-1 amendment ruled after dispatch: frozen label kept;
  promotion also needs the **cluster** sign test p ≤ 0.075 at either of two looks (Tanaka: pair test not
  size-controlled); < 4 non-zero clusters = not resolvable → local seeds 2–3 gate. Rec 8 → adopted in amended form.
  §D standing live loop LS-std-1; **§D.7 assigned me the sizing rule by simulation, due 19:30Z.**
- Wrote `reviews/LS-std-1-sugawara.md`: AMEND §D.2. Live pairs are not seed-matched (A1-Q3: own seed per game), the
  local census is; live discordance = switch + seed noise, so "≥ 12 expected non-zero clusters" is met by noise while
  power falls (LS-1 shape 0.49 → 0.21–0.33 at noise .05–.20). §D.1 size AGREE (null 0.048–0.081). Asked: A/A
  seed-noise census, power-based sizing (≥ 0.6), noise-predicted n beside n+/n−/n0, and whether the seed can be fixed.
  This corrects my own 17:29Z premise. Notified the lead (rule about to bind from the second screen).
- Outcomes: **P-2 confirmation FAIL** (Hinata 18:21Z; elim/r25 Autarky ΔAUC −0.0099, 5th −0.0152 vs −0.01) → my 0.50
  scores as a miss. **R2 encoder-only dev 0.714 < 0.75** (stop triggered; union model unfitted and binding per
  D-055 §E) → my P-5 dev forecasts (0.55, 0.65) wait on the union fit.
- Sim scripts in the cloud container only (`/tmp/claude-0/sg/lsstd.py`, `noise.py`); core described in the review.

## Unit 7 (17:25–17:30Z)

- BOARD read through line 829 (`[17:12 UTC chair:ushijima → hinata, kageyama, tanaka] R2 … now leads the Learner's
  order of work`); my line is 830 (17:29Z). D-055 in the decisions file (l.1521); no D-056 yet (Chair: to record
  the battles.py redeploy and the R2 work order).
- D-055: live-first. §A eligibility replaces the local-gate prerequisite for upload/live screen; §B LS-1 = 14585 vs
  asahi-05-kz12-k16, 102 matched pairs, 3 opponents, Daichi's 17:50Z unit is the first that can act; §C promotion
  rule amended; §D A/A closed; §E P-5 and §F P-6 approved as amended (my 0.70 and 0.80 recorded); §G P-2 rev 3 hold.
- Nothing assigned to me. Wrote unassigned `reviews/LS-1-sugawara.md`: AMEND the decision rule. Sparse discordance
  (k16 changed ~4–5 % of local games) makes the 51-cluster bootstrap degenerate: 1/0 is a PASS; null false-pass
  0.16–0.33; ties → REJECT. Asked for an exact sign test p ≤ 0.15 on non-zero pairs, < 4 non-zero → HOLD, strict
  reject, and per-pair opponent submission-id pinning. Notified the lead (promotion-relevant stats flaw before gate).
- Sim script lives in the VM at `$HOME/sg/sim.py` (not in the repo; VM scratch).

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
| P-2 | D-052 exact event: confirmation returns PASS under spec 15d79683 | **0.50** | 13:42Z (outcome FAIL 18:21Z) |
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
| LS-1 | PASS under D-055 §B rule as written | 0.50 | 17:29Z |
| LS-1 | PASS under my amended rule (incl. extension) | 0.25 | 17:29Z |
| LS-std-1 | k16-like candidate promoted under LS-std-1, LS-1 shape | 0.25 | 18:40Z |
| LS-std-1 | A/A seed-noise discordance on k16 pool ≥ 0.05 | 0.80 | 18:40Z |
| P-sugawara-01 | (all four void: card rejected and withdrawn, no outcome) | — | 13:40Z |
| D-048 §8 | (operating characteristics 0.09 / 0.38, not scored per D-052 §B) | — | 12:30Z |

## Open recommendations

1. V-legal and ΔAUC(V0b − V-legal). **Adopted** (D-052 §A.7); card is P-6.
2. A sequential (GSPRT) rollback card. **Open**; low priority.
3. (intake §4) Cost of permanently excluding held-out maps. **Not ruled.**
4. k16 gate readout (Weakhold per seed, pool without Weakhold, vetoes/fallbacks per 1k). **Adopted** D-054 §B.
5. P-sugawara-02 = P-4. **Approved for seed-1 screen** (D-054 §C); waits on Asahi after k16.
6. P-5: union features with a hashed allowlist excluding W/H/x/y/xn/yn; bind G-parent on the series-clean cohort;
   train on blocks_src = oracle; explicit 3/4-class support; flip rate report-only. **Adopted** D-055 §E (series-clean cohort, oracle filter, allowlist).
7. P-6: queen-speaker ΔAUC; paired V0b on post-claim rows; diagnostic not price. **Adopted** D-055 §F.
8. LS-1 decision rule. **Adopted, amended** (D-056 §C: cluster-level sign test p ≤ 0.075, two looks, sub-id pairing).
9. LS-std-1 sizing: A/A seed-noise census, power-based sizing ≥ 0.6, noise-predicted discordance printed, fixed seed if the API allows. **Open** (18:40Z; council review due 19:30Z).

## Next checks

- Chair's ruling on LS-std-1 after the 19:30Z council reviews (Tanaka power, Nishinoya replication).
- LS-1 look 1 (102 pairs): n+/n−/n0 — ≈ 4 non-zero means seed noise is small (my dissent); ≫ 10 confirms the review.
  Score LS-1 0.50 at the final look.
- Asahi parent seeds 2–3: compute A/A seed-noise discordance (parent s vs s′, same cell) if per-cell rows reach docs.
- Daichi: does the request API accept a seed?
- Hinata: union R2 fit (encoder + HB-1 scores) → score P-5 dev forecasts; Kageyama extractor is the critical path.
- P-4 (asahi-06..08) panels → score my 0.35; k16 gate seeds 2–3 → score 0.35.
- H-KZ36 stays unowned.
