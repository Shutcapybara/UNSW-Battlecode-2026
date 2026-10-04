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

## Entries

### REG-000 — `carthage-05-free-sprint` (incumbent)

- rung: pre-ladder parent (hand search with the hb1-14 GBT direction prior). parent: `carthage-04-sprint123`.
- switch: free on-route 2- and 3-step sprints on top of correct 1.2.3 sprint pricing.
- gate: D-042 item 4, win-led rule, bundle 05 against 00: pool win +0.045 [+0.019, +0.074], gen +0.017
  [+0.003, +0.031], seeds 1–3, both seats, old map pool (pre-swap).
- zero on the live maps (Rome, D-043, wheel 1.2.3): pool 656–160–0 of 816 (0.804); gen 1,038–353–1 of 1,392 (0.746).
- fingerprint: `ebeba55f` (from the upload name). live: submission **14585**,
  `LV-carthage-05-free-sprint-ebeba55f-ai`, active since 2 Oct 04:22Z.
- status: `incumbent`.
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

### REG-002 — `asahi-05-kz12-k16` (nominee, D-053 §D)

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
- status: `nominee`. Promotion at LS-1's stop if D-064 §B's five conditions hold (pairs, no fault, harm clause, loss
  limit −0.05, same binary).

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
