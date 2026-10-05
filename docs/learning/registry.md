# Model and experiment registry (Chair keeps the file; owners add entries)

Promotion and rollback work only on artifacts registered here (macro §6.3). One entry per artifact. An artifact is
one switch on a registered parent.

## Entry fields

| Field | Meaning |
|---|---|
| id | `REG-<nnn>`, assigned in order |
| name | bot directory `bots/<lane>-<nn>-<slug>/`, or model file for offline-only artifacts |
| rung | R0–R8, or `outside` for temporary hand rules |
| parent | registered id of the parent |
| switch | the one change, and its off value |
| data hash | manifest hash from `docs/learning/splits/` and the dataset build |
| code commit | commit that builds it |
| features / heads | feature blocks and output heads |
| hyperparameters | as trained |
| offline metrics | on the frozen held-out split, per map_era, with n and interval |
| export size | zip bytes (limit 4 MiB) |
| turn-0 CPU | points at turn 0 and the maximum per turn (limit 30 M) |
| fingerprint | bot runtime-source fingerprint (`fp8` in the upload name) |
| gate | card id, runtime wheel and engine hash, verdict letter |
| live | submission id, upload name, live-screen card, promotion or rollback D-record |
| status | `offline`, `candidate`, `nominee`, `uploaded`, `incumbent`, `retired`, `rejected` |

## Ratings on the ladder (D-076 §A)

Each submission has its own rating; the team's rating is the active submission's. Re-activating an older
submission brings its rating back; a new one starts from the rating of the submission it replaces and moves fast
at first. A trial therefore costs the incumbent's rating nothing.

## Entries

### REG-000 — `carthage-05-free-sprint` (incumbent until 5 Oct 11:2xZ; the rollback target, D-081)

- rung: pre-ladder parent (hand search with the hb1-14 GBT direction prior). parent: `carthage-04-sprint123`.
- switch: free on-route 2- and 3-step sprints on top of correct 1.2.3 sprint pricing.
- gate: D-042 item 4, win-led rule, bundle 05 against 00: pool win +0.045 [+0.019, +0.074], gen +0.017
  [+0.003, +0.031], seeds 1–3, both seats, old map pool (pre-swap).
- zero on the live maps (Rome, D-043, wheel 1.2.3): pool 656–160–0 of 816 (0.804); gen 1,038–353–1 of 1,392 (0.746).
- fingerprint: `ebeba55f` (from the upload name). live: submission **14585**,
  `LV-carthage-05-free-sprint-ebeba55f-ai`, active 2 Oct 04:22Z to 5 Oct 02:13Z and restored 5 Oct 04:53:55Z
  (D-075 §A). Not serving ranked games during the ladder trials of D-074 §B and D-075 §C (17388 since 05:02Z).
- status: `uploaded` (rollback target; replaced as incumbent by REG-005 under D-081 §A).
- Open items for Live ops and the Evaluator:
  - the hub's candidate row for this bot shows `submission: null` and status `runtime_ok` although 14585 is live;
    reconcile it before any rollback depends on that row;
  - the hub probe row (max 11,027,838 points, toolkit label `unswbc 1.0.0`) is identical to hb1-14's row; treat it
    as unverified and re-probe with turn 0 included. Rome's sandbox probes of carthage-05 derivatives give maxima of
    9.60 M to 10.37 M points per turn.

### REG-001 — `hb1-14-prior-r540` (fallback)

- rung: pre-ladder. The Heartbreaker GBT direction prior inside the Ares search (D-041).
- export size: 3.74 MiB. fingerprint: `ed7e4515`. live: submission **14265**, `LV-hb1-14-prior-r540-ed7e4515-ai`,
  active 1 Oct 17:00Z to 2 Oct 04:22Z.
- status: `uploaded` (rollback target one activation away).

### REG-002 — `asahi-05-kz12-k16` (live 5 Oct 02:13Z to 04:53Z; **rolled back**, D-075 §A)

- rung: outside the ladder (`temporary` hand rule, D-044). parent: REG-000.
- switch: queen-only veto on a one-step move into a pocket with body-conditioned reach Cb < 16 that has no cycle of
  at least the projected queen length + 1 (H29 contract); k = 0 reproduces the parent on 272 of 272 pool games.
- screen (seed 1, Asahi P-A02): pool Δwin +2.6 points [+0.7, +4.4]; gen −0.2 [−1.1, +0.7]; wall deaths on classes C
  and E −4.86 per 1,000 [−8.16, −2.08]; pearls@50 −0.75; queen endpoint no response.
- gate (seeds 2–3, Asahi 21:25Z): **HOLD**. Pool +1.10 points [−0.37, +2.76] (436–108 against 430–114 of 544); gen
  +0.22 [0.00, +0.54]. Weakhold (named before the run) +28.1 points [+15.6, +40.6]; pool without Weakhold −0.59
  [−1.56, +0.39]. Council round on promotion called (D-063 §B). Deploy probe on the fixed tree: zip 3.741 MiB;
  maximum 11.01 M points per turn; first turn 10.73 M; no errors; runtime fingerprint `43bd2d4f` (hub archive
  fingerprint 0cf975af).
- live: uploaded 17:32Z as submission **16979** (`LV-asahi-05-kz12-k16-0cf975af-ai`, fingerprint 0cf975af, zip
  3.74 MiB; CPU maximum 10.6 M points per turn over 106,507 turns, round 0 at most 7.13 M, no faults). It was active
  by a hub defect from about 17:33Z to 17:40Z (D-056 §B). LS-1 dispatched 17:42Z (job 5ed81ad3e1f3): 102 matched
  pairs against 14585 on teams 716, 98 and 347. Promotion conditions: D-056 §C.
- LS-1 final (job expired at its deadline, 160 of 204 games): 75 pairs, paired mean +0.080 [−0.029, +0.187], no fault;
  by opponent 716 +0.233, 98 0.000, 347 −0.050. Its own frozen letter: HOLD.
- status: **`uploaded`, rolled back.** Activated 5 Oct 02:13:22Z by Daichi under D-064 §B (D-069). **Rolled back
  to REG-000 (14585) at 04:53:55Z under D-052 §B (D-075 §A):** 45 ranked games, 9 series; score minus expectation
  against 14585's last 120 games −0.263, 95th percentile −0.126; alone 16–28, −0.211 [−0.327, −0.082]; queen-rule
  W–L 1–14; no fault. Cause not established (noise, field change, or the veto exposing the queen). Still a local
  parent (pool 233–39 against 226–46) pending the queen-keeper panel of D-075 §D.

### REG-003 — `hinata-v0b` (value model, R1 candidate; **failed** its confirmation, D-057 §B)

- rung: R1. class: logistic on Φ's features plus queen terms, per era, regime and checkpoint (`lr_q`).
- code: `tools/hinata/archive/v0_2920bb57.py`; scorer `p2_confirm.py` sha 0d0d1b7a…; spec sha 15d79683….
- data: P-2 development rows (`tools/hinata/PROVENANCE-P2.md`); held-out pin 2ebf99ce… (22,305 rows, 3,305 games).
- held-out result: elimination r25 ΔAUC −0.0099 [−0.0152, −0.0049] (fail); round-limit r50 +0.043, r150 +0.074,
  r400 +0.150. Uses replay truth of both teams: a training-time critic, not deployable.
- size: under 50 KB of coefficients. status: `failed`.

### REG-004 — `hinata-p1-enc-dev` (R2 development fit, encoder only, teacher-weighted)

- rung: R2, development only. class: boosted trees on encoder v1 (1,193 columns, allow-list sha b109e5c0…).
- code: `tools/hinata/r2_bc.py` rev 3 edc66ef7… (rev 4 a31faa5d… for the learning curve); run manifest 6f222de6….
- data: dev120 oracle rows, 189,630 moves, 97 games, 49 series, ten teachers; five series folds.
- offline: forward/right/left accuracy 0.714 [0.706, 0.724]; queen 0.678; per teacher 0.676 to 0.768; learning
  curve 0.676 / 0.684 / 0.703 / 0.714 at 0.10 / 0.25 / 0.50 / 1.0 of the training series.
- status: `diagnostic`. The battery's A3 is the unweighted refit (D-060 §E).

### REG-005 — `kenma-03-pocket-queen` (free lane Kenma, retired; **the incumbent since D-081**)

- rung: outside the ladder (free lane, D-067 §F). parent: `carthage-05-free-sprint` lineage, Kenma's tree
  `../wt-kenma/bots/kenma-03-pocket-queen`.
- change: a proven sealed pocket of at most 8 cells makes the queen split to 2 or take the least-eating step inside
  it; trapped donors split 1; every non-queen plans with one unit slot reserved (Sugawara's read, 04:38Z).
- local: 58–44 against carthage-05, 57–45 against k = 16, 54–48 against `bokuto-04-queen` (Kenma, 102 games each).
  Same-host seed-1 pool (Asahi): 220–52; against carthage-05 −2.21 points [−4.41, −0.37]; against k = 16 −4.78
  [−7.72, −1.84]; queen-decided 13–4; queen alive at the round limit 15 of 147.
- deploy: zip 3,923,010 B; maximum 10,910,667 points a turn with the first turn; no fault (Kenma).
- live: submission **17388**, `LV-kenma-03-pocket-queen-c5d2ff46-ai`, runtime e60733a9…; first ranked series 5 Oct
  05:02Z; trial to the first series boundary at or after 60 ranked games. Statistic and end rule: D-075 §B–C.
- **trial result (Daichi, 08:03Z; D-078 §A):** 60 games, 12 series, 31–29; score minus expectation at 1725 +0.074
  [−0.048, +0.197]; performance rating 1781 [1686, 1876]; against 14585's reference +0.117 [−0.018, +0.269];
  queen-rule losses 7; no fault; no Schooltime game in the window. Variant block 69 of 80 (carthage-05: 63).
- **end rule (D-081 §A):** +0.117 over the reference against a bar of 0.03; `bokuto-13-cull` at +0.001; the windows differ by 0.115. By opponent rating: at or above 1725 +0.162 [0.000, +0.324] (35 games), below −0.048; queen-rule losses 7 of 29. Caveats: the interval includes zero; no Schooltime game in the window; nobody maintains the bot.
- status: **`incumbent`** (submission 17388; **active since 5 Oct 12:34:13Z**, first ranked series 12:36Z; rollback target 14585; D-052 §B applies). Since reactivation 20 games, 10–10. On the corrected curve table its queen is alive at round 300 in 12 % of games (opponents 47 %): our worst queen.

### REG-006 — `bokuto-04-queen` (free lane Bokuto; **second ladder trial approved**, D-075 §C)

- rung: outside the ladder (free lane). Tree `../wt-bokuto/bots/bokuto-04-queen` (uncommitted), runtime ff68a709….
- local: 58–44 against carthage-05 (Bokuto, 102 games). Same-host seed-1 pool (Asahi): 226–46; against carthage-05
  0.00 points [−5.15, +4.78]; against k = 16 −2.57 [−7.35, +2.21]; queen-decided **42–4**; queen alive at the round
  limit 44 of 189, on 11 of 17 maps; economy −6.3 [−9.5, −2.7].
- deploy: probe **passed** (Asahi, 5 Oct 05:53Z): zip 3,928,551 B; maximum 12.86 M points a turn, first turn 12.47 M;
  no error in 10 games. Daichi holds a byte-exact copy (tree sha256 3e31f947…). live: none yet.
- paired read (Sugawara, D-076 §C): 38 of its 42 queen-decided wins are fixtures carthage-05 also won; 31 gains and
  31 losses against carthage-05; three stacked layers, so nothing is attributable to the queen block alone.
- status: `candidate`; trial 2 unless `bokuto-13-cull` qualifies (D-076 §B).

### REG-007 — `bokuto-13-cull` (free lane Bokuto; trial 2 ended; the local reference)

- rung: outside the ladder (free lane). Tree `../wt-bokuto/bots/bokuto-13-cull` (uncommitted); byte copy in
  `wt-asahi/bots/bokuto-13-cull`, to be committed on `r/asahi` (D-077 §C). Runtime fingerprint d192d721….
- change on the carthage-05 chassis (Bokuto's layers 02 to 13): a survival guard and cage split; a dead-end branch
  model; queen caution, hiding and feeding; allies yield to the queen; the queen fights while the team is small;
  corridors worth at least 3 pearls are explicit targets; a spare length-2 dragon culls itself at the unit cap.
- local: 70–31–1 against carthage-05 by Bokuto's own run (102 games). **Same-host seed-1 pool (Asahi, 07:20Z):
  241–31; against carthage-05 +5.51 points [+2.19, +9.19]; against `bokuto-04-queen` +5.51 [+1.47, +9.56]; against
  k = 16 +2.94 [−0.74, +6.99]. Queen-decided 92–2; queen alive at the round limit 94 of 163 (58 %).** Economy
  −0.60 [−3.62, +1.97]. Costs: Stripes 4–12, Autarky and Portals −12.5; ally head-on deaths +14.5 %.
- deploy: probe passed: zip 3.75 MiB; at most 12.38 M points a turn, first turn included; no error in 10 games.
- variant block (80 fixtures Bokuto never saw): 72 of 80 against carthage-05's 63 (`schooltime_open4` 15 against 7;
  the other four layouts 57 of 64 against 56); weighted by live share +5.75 points [+2.97, +8.62].
- live: submission **17530**, `LV-bokuto-13-cull-877fa2c9-ai`, uploaded 5 Oct 08:14:33Z (hub fingerprint 877fa2c9;
  runtime d192d721…); byte copy committed on `r/asahi` (17d7574d5). Trial 2: its first 60 ranked games. End rule:
  D-075 §C as amended by D-077 §B and D-078 §C.
- **trial result (Daichi, 10:56Z; D-081):** 60 games, 12 series, 30–30; −0.041 [−0.132, +0.062] at rating 1725; +0.001 [−0.110, +0.126] over the reference; at or above 1725 −0.073 [−0.148, −0.003] (25 games), below −0.019; queen-rule losses 14 of 30; queen alive at the end 17 of 60; no fault. Not chosen.
- second window (to 12:23Z): 60 more games, 30–30; **all 120: −0.054 [−0.128, +0.023]**. Corrected curve table: queen alive at round 300 in 50 % (opponents 57 %), total length 55 and 103 at rounds 100 and 300: our best queen, our smallest economy.
- status: `uploaded` (trial ended; plays at 14585's level on the ladder).

### REG-008 — `kenma-28-harvest-reserve` (Kenma's last bot; the lane is retired, D-079 §A)

- rung: outside the ladder. Tree `../wt-kenma/bots/kenma-28-harvest-reserve`; fingerprint 73f60fe2…. Parent
  `bokuto-13-cull` (d192d721…) plus Kenma's pocket and reserved-slot components (from `kenma-21`, 62671c2e…).
- local (Kenma's harness, 102 games, no error): 72–30 against carthage-05; its parent scored 73–29 on the same
  harness.
- same-host (Asahi, 10:07Z): seed-1 pool 241–31, the same count as its parent; against `bokuto-13-cull` 0.00 points
  [−1.10, +1.10]; variants 72 of 80; queen alive at the limit 95 of 166; probe passed (3.75 MiB, 12.56 M points).
  Kenma's layer adds nothing on top of Bokuto's bot (D-080 §E). Byte copy on `r/asahi`.
- status: `measured`; no trial (equal to its parent); member of the `qk2` panel.

### REG-009 — `bokuto-17-atlas` (free lane Bokuto; an atlas bot, D-080 §D)

- rung: outside the ladder. Tree `../wt-bokuto/bots/bokuto-17-atlas` (`r/bokuto` 5ce986d95). `bokuto-13-cull` plus a
  terrain atlas of all 17 live maps matched on observed edges, a move-level pocket ban and whole-map routes.
- local (Bokuto's harness): 66–33 against `asahi-05-kz12-k16` (Weakhold 0–6 → 5–1).
- conditions for a trial (D-080 §D): `gen` panel and hidden-layout block not below `bokuto-13-cull`'s; the twin with
  `n_maps = 0`; pool and probe. Asahi's runs are in progress.
- same-host (Asahi, 10:40Z and 11:18Z): pool 228–44; against `bokuto-13-cull` −4.78 points [−8.46, −1.08]; variants 75 of 80; `gen` (29 unknown maps) −1.19 [−3.88, +1.51]; probe passed. Twin with the atlas off (`asahi-26-b17-atlas0`): pool 240–32; atlas on minus off −4.41 [−8.46, −0.35], exactly 0 on `gen`. `qk2` 28–40.
- status: `measured`; not a trial candidate (the atlas costs 4.4 points where it is exact; D-081 §C).

### REG-010 — `asahi-27-b13-reserve` (qualified; fallback for trial 3, D-083 §D)

- `bokuto-13-cull` plus Kenma's two global reserve lines (non-queens decide with one unit slot fewer). Fingerprint
  16ceecff. Built for the Chair's reserve hypothesis of D-081 §B; Sugawara's replay check refuted the mechanism
  (survival), and Asahi's economy columns show another: on the pool total length at round 300 is 138.5 against the
  parent's 127.5.
- same-host (Asahi, 12:39Z): pool 237–35; against `bokuto-13-cull` −1.47 points [−2.94, 0.00]; against carthage-05
  +4.04 [+0.37, +8.09]; head to head against the incumbent 69–33 (parent 64–38; paired +4.90 [+0.98, +9.80]); `qk2`
  33–35; queen alive at the end 96 of 162 on the pool; probe passed (3.75 MiB, 12.37 M points).
- status: `candidate` (qualified under D-076 §A; trial 3 only if `bokuto-18-queenfeed` fails its conditions).

### REG-011 — `bokuto-18-queenfeed` (free lane Bokuto; **trial 3 on condition**, D-083 §D)

- Tree `../wt-bokuto/bots/bokuto-18-queenfeed` (`r/bokuto`). The atlas-off twin of `bokuto-17-atlas` plus: the queen
  fed from round 290; queen terrain safety from round 0 (no blind portal dive, no single-exit cell, no escape
  split); the dodge from round 0; Kenma's reserve lines.
- local (Bokuto's harness): at parity with `bokuto-13-cull` on 34 games; queen 20–52 long at the limit where she lives.
- condition for trial 3: Asahi's deploy probe passes and the same-host pool is not below carthage-05 (paired 5th
  percentile above −5 points). Then Daichi runs the trial without a further record.
- status: `candidate` (Asahi's job running since 13:00Z).

