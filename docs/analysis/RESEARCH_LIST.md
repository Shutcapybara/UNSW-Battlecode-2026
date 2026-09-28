# Research list — data that does not exist yet (handoff A1 §4, costed and ordered)

Author `glm/analysis/a1`, 2026-09-28. Costs assume the Mac (4 cores) and the current quotas; "unlocks" names the decision that waits on it. Order = mine, by (decision value) / (cost × risk).

## Priority order

**R1. Deploy the current `tools/hub` to `app/current`** — cost: minutes, no games.
Unlocks: the calibration table (rows already computed offline), layout-parity alarm, runtime/sonar tables, Elo trajectory in every packet. The deployed revision (09:21 UTC) predates all of it. Nothing else on this list reports automatically until this happens. *Note the concurrent session editing tools/hub in the main checkout — deploy from a reconciled state.*

**R2. Judge-divergence tap build** (findings 2026-09-28-analysis-judge-tap-spec) — cost: 1 upload, 1 dev game, ~1 h.
Unlocks: validity of replay-drive/metering for post-27-Sep games; permanent early warning for judge changes. Cheapest decisive experiment on the list.

**R3. Layout-assignment field check for Dilemma** — cost: ~10 dev games in one hour.
Unlocks: whether map 17's four layouts follow any controllable rule (id mod 4 failed; seed untestable — 486 distinct seeds). Until then, layout-matched fills skip Dilemma (nine maps are already deterministic by id parity — no experiment needed there, contrary to the handoff's 20-game estimate).

**R4. Live-pool panel on unswbc 1.2.2, seeded, both sides, 3 seeds** (S1 §7.1; `tools/chaewon/panel.py` / `tools/yeji/yrun.py`) — cost: ~4 h/arm on 4 cores.
Unlocks: the selection instrument; (a) trajectory-matching local side for all six mapped bots (only tidus has comparison runs today), (b) the toolkit-strata comparison (zero ledger overlap), (c) calibration rows with a proper local side. This is the single most valuable DATA item; R1–R3 are cheaper and unblock reporting first.

**R5. Band-team replay download + fingerprints** — cost: one download batch (≤600 files, executor/key), then ~2 h compute (`tools/team_recon_claude/descriptive.py`).
Unlocks: the ±8-band behavioural clustering, choice of 6 clones (recipe: team_recon_306 REPORT §5a), and the local panel's opponent set. Analyst is key-blocked; executor action.

**R6. Teammate-upload recovery from API zips** — cost: hours (75 submissions).
Unlocks: every live control (9508, 9573, 9604 …) as a byte-exact local opponent — the reference panel becomes the actual live band. Highest accuracy-per-hour after R5 for calibration.

**R7. Elo exposure fetch** — cost: one API fetch of 4 series details (+ team elo history if exposed).
Unlocks: exact K and the true cost of the 20 ranked test games (locally: eloChange null everywhere). Feeds the blackout-window redesign (activation-duration model, see the Elo finding).

**R8. Autoscrim draw semantics** — cost: 3 days of ranked_exposure↔activation correlation, or one email to hi@battlecode.au.
Unlocks: blackout width around even UTC hours (secondary once the activation-duration model from the Elo finding is adopted).

**R9. S1 2×2 results (Chaewon/Yeji seeded panels)** — in progress, no action.
Unlocks: production × dissolve mechanism sizes; feeds loss-anatomy targets.

**R10. Stage-matched replay-drive counterfactuals** — cost: hours per version, AFTER R2 (validity gate).
Unlocks: "what would version X have done from this live position" for pre-change games.

## Explicitly deprioritised

- **20-game layout experiment (handoff §4 row 4) as specified**: obsolete — nine maps answered analytically (id parity, 0/446 exceptions); only the Dilemma sub-experiment survives (R3).
- **Toolkit strata from existing data**: impossible (zero overlapping cells); subsumed by R4.
