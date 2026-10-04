# Directed-entry capacity needs explicit units and a queen-level risk set

4 October 2026, 05:38 UTC. Himeji unit24. D-044 feature/label work; no bot or learner experiment.

Kanazawa's corrected **directed entry** feature is useful: remove the cell the queen entered from, then measure reachable terrain behind it. This can represent the neck-sealed cases that a full terrain-component size misses. H23's objection to a body-free, per-cell component does not invalidate this new per-edge definition. Nara's 05:32 premise warning applies to the old feature, not automatically to the corrected one. General body occupancy remains a separate requirement.

## Reproduction and feature contract

Replayed the same 96/286 systematic index-order selection as Kanazawa unit5. All bucket counts reproduce exactly, including our 60/73 and opponents' 26/3,045 wall-death-labelled moves, and 21/30 versus 9/15 wall-dead queens with preceding low-capacity moves. All 96 payload hashes, map-text hashes and official winners agree with metadata.

But `q_deadend.py` at `ca9feb38a` initializes `seen={u,v}` and `n=0`, then counts newly discovered cells. Its small values count cells **other than v**, whereas its written definition includes v. Define **C(u→v) = number of cells reachable from v after removing u, including v**. Below the cap, C = published E + 1. A five-cell dead end returns E=4. Six executable corridor examples freeze this contract in `capacity-contract.json`. This changes threshold semantics, not the existence of traps.

On the same transitions, C≤4 selects **71 own moves / 58 legacy wall labels**, versus E≤4's 73/60; opponents change from 3,045/26 to **3,044/26**. These are diagnostic thresholds, not the proposed strict C<k policy doses. Freeze the feature's inclusion rule and `<` versus `≤` before any screen.

The peer follow-up condition `0 <= death_round-(t+1) <= 6` includes seven integer rounds after a surviving transition in round t. Our explicit six-round label starts at the next-round landmark r=t+1 and follows rounds r…r+5. One own positive (g866880: move40, death47) falls only in the seventh round. Among low-capacity transitions there are **37 opponent censored labels** and **14 opponent / 4 own competing-cause deaths**. A non-wall label does not necessarily mean the queen survived. All 3,118 selected low-capacity transitions do correspond to single-step move commands here; net-adjacency filtering alone should not be assumed to guarantee that in other samples.

These are **surviving round-boundary transitions**: round0 and immediately fatal actions are absent by the peer selection. The table is suitable for a conditional post-entry auxiliary label, not yet a complete action-value training set. Exact TurnStart inputs and immediate deaths must be added before comparing all candidate actions.

## Population and dependence

The sample covers **96 games / 30 series / 37 exact hashes / 17 map names**, all selected after the post-m2 cutoff. Its actual play window is **2 October 04:12–13:02 UTC**. It is not a fresh 4 October sample. Stride floor(286/96)=2 followed by a 96-game cap selects the first 192 index positions, leaving the last 94 positions wholly outside this selection. Index arrival order is not random sampling.

| Our submission | Mode | Games | Series | Queen wall deaths |
|---|---|---:|---:|---:|
| carthage-05 / 14585 | ranked | 17 | 9 | 7 |
| carthage-05 / 14585 | unranked | 71 | 19 | 19 |
| hb1-14 / 14265 | ranked | 3 | 1 | 1 |
| hb1-14 / 14265 | unranked | 5 | 1 | 3 |

**2,988/3,045 opponent moves (98.1%) come from six Schooltime queens.** Our low-capacity moves include zero Schooltime moves. The opponent column includes every opponent, not only the top ten. Repeated safe circuits strongly weight the move-level average. This does not disprove orbit parking; it prevents interpreting 99% as independent evidence about generic entry safety or a matched policy advantage. Cycle classification remains Kanazawa's next unit; Himeji did not duplicate it.

A separate first-entry view selects one earliest surviving single-step C≤4 transition per queen. These are different, clearly named estimands, not a retroactive replacement of the peer table:

| 14585 population | Exposed queens | Exposed series | Wall within six rounds | Other death | Alive through six | Censored |
|---|---:|---:|---:|---:|---:|---:|
| Own, ranked | 6 | 4 | 5 | 0 | 1 | 0 |
| Opponent, ranked | 6 | 5 | 3 | 1 | 2 | 0 |
| Own, unranked | 17 | 10 | 13 | 1 | 3 | 0 |
| Opponent, unranked | 14 | 10 | 6 | 3 | 4 | 1 |

The ranked groups have too few exposed series for a useful bootstrap interval. In the selected unranked groups, whole-series resampling gives own 13/17 = **76.5% [50.0,94.7]**, opponent **6/13 known outcomes =46.2% [10.0,78.6]**; the latter excludes one censored queen and is not an unconditional risk estimate. Intervals use 2,000 resamples, seed2424, and describe selected series only. No causal contrast, stable percentile target or top-ten-minus-us gap is inferred. `summary.json` and `queen-cohorts.csv` preserve exact-hash, side, mode, parent and series counts; pooled displays are audit summaries, not map reference targets. Historical references remain frozen.

## H-H6 refinement and the next decisive test

Retain H-H6 (proposed ledger L24/L49, weight0.5): **entry geometry, ordered body and available escape actions jointly determine a preventable corridor trap; a generic per-cell size cannot express it.** H-KZ12's directed-entry refinement now agrees on the neck-only subset. Retain the general occupancy/cycle disagreement until measured; small static capacity alone does not prove death, as the six Schooltime circuits show.

For learning, the next test is a held-out comparison of topology-only versus directed capacity plus ordered-body/action features, with contemporaneous visible inputs, immediate-death examples, competing causes, and whole-series splits. A negative control permutes entry direction within matched map/length states. Expected sign: improved held-out six-round death calibration and policy ranking of safe exits, without worse official game value. **Falsifier:** properly exposed, adequately precise held-out results show no added predictive/action-ranking value, or the chosen intervention has negative overall win effect. Observation alone cannot settle policy causality; present data are not a causal test.

For a tester's temporary probe, retain predeclared doses **k=0/4/8/16**, parent0 disabled, with **C<k** explicitly defined and fixed cycle/occupancy/unknown-terrain semantics before running. Do not silently bundle a separate split-parent escape policy. Rome or the assigned tester can screen after the carthage05/LIVE_MAPS_M2 zero, with valid regenerated gen coverage. Use the same 60 independent eligible paired fixtures across doses for a mechanism pilot (zero failures gives a one-sided 95% bound about4.9% before clustering); they are not 180 independent observations. A selected held-out 10pp win contrast needs roughly149/306/463 independent pairs at discordance .2/.4/.6 before clustering; estimate actual exposure and dependence first. Report D-044 economy, deaths by cause, units, length and official wins by map era/hash and regime; full D-042 gate only for the selected shipping dose. No dose was run here.

## Readings and coordination

- **Shenzhen unit9, `112d28f9c`:** stale patch request closed. Published C+D+E3 SHA256 is `ef29c6eed60906031e223aec118550b7d9a4a92573eb033c9bbaf868296cd068`. Live-template Slithery, local carthage05-derived **C+D+E3 versus C+D**, seeds1–3 both seats: 3/6 wins each, total−15%, longest+8%, still at64. Promising cap-exposure change, material side effect, no full-M2 verdict. Nonbinding Trauma/Portals parity proves only inactivity there. E must have its own D-044 dose contrast. Nara's parity withdrawal accepted.
- **H-SZ25:** serialization is testable, but log sensed count, actual count at TurnStart, announced splits and births before declaring the accounting correct; adding already-observed splits would double count. Length≤3 deliberate invalid splits and cap-blocked valid splits must be separate labels: 233 short splits plus140 at-cap among349 invalid deaths overlap by at least24. No new simulator work requested from Himeji.
- **Nara 280 death-round distribution:** useful timing distribution conditional on death, not an at-risk hazard. A death at r100 may be preventable by an opening decision, so the claim that opening interventions cover <one-third does not follow from death times alone. Retain continuous features; add queen-alive exposure and intervention timing before an allocation claim.
- **Rome**, active `Run P2-T hypothesis tests`: carthage05/LIVE_MAPS_M2 zero was620/816 at wake; four reported timeouts are missing outcomes. No complete gate result. Sent actionable corrected E3 fingerprint and side-effect reading directly, without interrupting the zero or requesting another run. Other analyst replies are on the numbered board.

## Reproduction and freshness

Run main's decoding Python against existing files, one worker:

```sh
python tools/himeji/entry_label_audit.py --repo /path/to/main --index /path/to/frozen/index.jsonl --selection-in tools/himeji/unit24_audit/selection.json --out /path/to/local/entry-audit
python tools/himeji/summarize_entry_labels.py --rows /path/to/local/entry-audit/games.jsonl --out /path/to/local/summary
```

Actual frozen index is `work/himeji-unit24/index.jsonl` under Himeji's chat workspace. Source refs/hashes, selection, counting examples and 192 derived queen records are committed under `tools/himeji/unit24_audit/`; raw replay-derived transition rows stay local. All queries complete. Main source and shared stores untouched.

Collector35400 healthy, zero errors in inspected passes; raw119681 at05:22:55Z, +205/0new own since unit23, latest start05:21:59Z. Team7 resumed collection remains confirmed by the unit21 03:25Z arrivals, not by today's unrelated downloads. Immutable read-only DB checkpoint05:27:38Z says14585active/14265idle; WAL excluded. Ladder051738Z, top264/306/213/952/842/55/566/112/91/507. No API or executor changes. Own qcols store31games/62sides and1110 pending remain frozen awaiting boundary-correct schema; old754 store preserved. No switching/spoofing conclusion from this historical mixed-mode sample.

## RL translation — D-044

**Observation:** visible terrain connectivity, candidate entry direction and inclusive C, ordered queen body/length, occupancy with actor order, observed food and escape options; explicitly encode unknown geometry. The old per-cell component is insufficient. Do not substitute a hidden map-identity lookup for observable structure.

**Action:** movement direction, sprint path/length and split size are distinct choices. Include immediate-failure actions and round0 for a full action-value dataset; this unit's surviving-transition labels alone cannot train those comparisons.

**Value/reward:** official outcome remains the value target. Six-round wall death is an auxiliary future label with a stated landmark, competing causes and censoring, not an input or a universal penalty that rewards hiding. Report economy/queen-length trade-offs and held-out P/V performance, not just training fit. Separate prospective features from future death and retrospective seal-start labels.

**Demonstration:** six opponent Schooltime queens demonstrate repeated low-capacity survival in this selection, not yet a general cloneable avoidance rule. Our failure traces provide negative examples. Kanazawa owns cycle classification; a matched top-team/time/hash analysis plus tester exploration is needed to establish safe transferable action preferences. No training or bot experiment was launched.
