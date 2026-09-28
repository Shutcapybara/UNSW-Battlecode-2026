# Research list — data that does not exist yet

**v2 — 28 September 2026, `claude/analysis/session-01KHqE`.** Ordered by the decision each item unlocks divided by
its cost, after the ten analyses (`docs/findings/2026-09-28-analysis-claude-Q*.md`). Costs are estimates from the
measured speeds in this pass (replay-drive ≈ 500 turns/s in the VM; a live-pool game ≈ 30–90 s native on the Mac).
v1 (gpt-6/analysis/codex-session, 12:13 UTC) is appended verbatim.

| # | Item | What it needs | Cost | Decision it unlocks | Why this position |
|---:|---|---|---|---|---|
| 1 | **Two-orientation request pattern** (Q3): each arm's block as one 20-game request `M0..M9, M1..M9, M0`, or two 10-game batches with a parity check on the returned ids | a change to the legacy request builder + one test; no new data | 1 hour of code; the first block pays for itself (no fills) | 20 exact pairs per opponent per block instead of ≤ 10 with up to 6 fills; makes a 60-pair screen affordable (Q2 power) | Zero-cost, deterministic, removes the largest source of wasted field quota |
| 2 | **Opening stage points** r25 / r50 in the decoder's stage curves (and `first_length` semantics documented) | `LIVE/system/vendor` decoder + one re-decode pass over 446 replays (≈ 20 min) | hours | Locates where the r100 deficit (Q1) is created: split timing vs bed race vs first collisions; the mechanism the S1 bots must fix | Everything in Q1 points before r100 and the record cannot see there |
| 3 | **Live-pool panel on unswbc 1.2.2**, seeded, both sides, 3 seeds, references = swarm-heavy first (ouroboros-m01 mimic, gavroche-v32, 9508's source, clones of 62/545) plus a 10-dragon `dilemma_10.map` | `tools/chaewon/panel.py` / `tools/yeji/yrun.py`; 480 games per arm | ~4 h per arm on 4 cores | The selection instrument; the first calibration rows with a proper local side (Q4: today 0–4 common cells) | Nothing local currently exercises the live failure mode |
| 4 | **Judge-divergence tap game** (Q8 spec) | director authorisation; one upload, one dev game vs 752 on Trophy | 1 dev game; ~1 h including the build | Validity of replay-drive, replay-derived inboxes and IL features for every post-27-Sep game (121/121 live games diverge at ~92 %) | Cheapest item touching the most tools |
| 5 | **Refetch the four 9663 ranked series** (463004, 467153, 468473, 474275) and the post-09:33 series' submission ids | one API pass on the Mac by the executor | minutes | Books the Elo cost of testing (Q9: currently null); settles whether the submission binds at request or start | Cheap; needed before the blackout width is argued |
| 6 | **Band corpus**: ≤ 60 newest public replays of each of 790, 133, 977, 75, 19, 406 (played ranked vs us today) + 534, 875, 473, 241 | `tools/download_team_games.py` (authorisation: downloads) → `descriptive.py` | ~1 h download, ~2 h profiling | Q5: whether the band is cluster 1 (swarm) or cluster 3 (mid swarm); the six clone representatives; re-balancing the screen panel away from ranks 6/40 | Our rating is decided there and there is no data |
| 7 | **Clones of 62/9343 and 545/9571** (mimic recipe) | their replays already in hand (103 + 55 live games plus public) | ~1 day per two clones | A local opponent within 1 SD of the live eliminators (Q4 c); the S1 2×2 gets an opponent that punishes slow openings | Largest gap in the local panel |
| 8 | **Teammate-upload recovery** (9943 Heimdall v10, 9808, and the rest of the 75) | API submission zips (self-audit recipe) | hours | Every live control ever faced becomes a local opponent; fills the paired-cell gap for control-following candidates | Needed for item 3's reference set |
| 9 | **Probe fixtures extended** to Slithery Fight A and Trauma (Q6) | config change in `LIVE/config.json` / hub `runtime.probe_fixtures` | +2 probes per candidate (~6 min) | Catches the 97.5 M Slithery peak the current pair misses; keeps the 80/60 M gate honest | Cheap, prevents a live cap hit |
| 10 | **Sonar ablation** on seeded fixtures: one packet kind off per arm, exact pairs (Q7) | S1 host with per-kind switches; item 3's fixtures | ~2 h per kind | Whether any packet kind has a consumer worth its bytes (cost is zero, so only value matters) | Only valid way to price rays |
| 11 | **S1 2×2 results** (Chaewon, Yeji lines) | their seeded panels finishing | in progress | Production × dissolve sizes; feeds Q1's "opening first" ordering | Already running |
| 12 | **Stage-matched replay-drive counterfactuals** on the 141 pre-change public games | `replay_drive.py` per version | hours per version | "What would X have done from this live position" — valid only pre-change until item 4 lands | Wait for item 4 |
| 13 | **Autoscrim draw semantics** over 3 days (or ask hi@battlecode.au) | `seen_series` timestamps vs activations | days | Blackout width; today's data says key on start time (+4 … +36 min) | Low urgency once item 5 is done |
| 14 | **Rating-table patch** (Q10): shrunk score + evidence tier + live column in `benchmark_ratings.py::summary` | `benchmark_dashboard_data.py` access | 1 hour | Stops Sparse rows from being quoted as evidence; does not make the table predictive (that is item 3) | Hygiene |

Not recommended: a 20-game layout experiment (v1 item 5 / handoff §4) — the rule is already established on 446
games with 0 violations and the 20-game request pattern (item 1) is the fix; a local-ledger "shrinkage validation"
(v1 item 9) — done in Q10, negative.

---

## Appendix — v1 (gpt-6/analysis/codex-session, 12:13 UTC), retained verbatim

# Research list

Recommended order, based on the next decisions each item unlocks. Costs are planning estimates from the handoff, not measured execution times.

| Order | Work | Needed data / method | Cost | Decision unlocked |
|---:|---|---|---|---|
| 1 | Finish S1 2×2 seeded panels | Chaewon/Yeji 1.2.2 seeded panels; report seed-level intervals and both sides | In progress | Production × dissolve mechanism sizes and live-pool reference calibration |
| 2 | Live-pool panel | unswbc 1.2.2 seeded, both sides, three seeds, lineage-diverse references; 480 games per arm | ~4 hours per arm on 4 cores | Selection instrument and local transfer evidence |
| 3 | Recover teammate uploads | Retrieve the 75 team submission zips using the existing recovery workflow; checksum and preserve submission strata | Hours | Turn prior live opponents into reproducible local panel members |
| 4 | Ladder-band opponent clones | Obtain ≤60 newest replays per team; version-stratified fingerprints, then build six legal-input imitation clones | ~1 day per two clones | Select six representative ladder opponents for the local panel |
| 5 | Layout assignment experiment | 20 field games on one map with alternating request patterns; retain seed, order and layout | 20 games of quota | Choose alternating-arm fill policy or deliberate layout balancing |
| 6 | Judge-divergence tap | Director-authorized diagnostic upload logging raw stdin; one dev game | One upload + one dev game | Decide whether post-change replay-drive and local metering remain evidence |
| 7 | Autoscrim draw semantics | Relate ranked exposure to activation timestamps over three days, or obtain authoritative semantics | Days | Set the blackout window around even UTC hours |
| 8 | Stage-matched replay-drive | Replay pre-change public games under fixed bot versions and compare profiles | Hours per version | Estimate version-specific counterfactual behavior from live positions |
| 9 | Local-ledger and rating audit | Install/use available PyArrow runtime; reconstruct fixture/opponent/map/toolkit strata and implement shrinkage validation | 0.5–1 day | Decide whether local campaign scores can order the queue |
| 10 | Live/local trajectory transfer | Join local run `stats/*.json` stage series to live fixed-source/map/opponent profiles; compare toolkit 1.0.0 native with seeded 1.2.x | 1–2 days after recovery | Choose reference opponents and permit local scores in priority only if paired sign agreement is ≥70% on ≥10 pairs |

No uploads or API interactions were performed in this analysis. Items 5 and 6 require quota or director authorization, respectively, as specified in the handoff.
