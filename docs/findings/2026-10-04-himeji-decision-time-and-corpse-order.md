# Himeji unit31 — decision-time visibility and event-ordered corpse fates

4 October 2026, 08:52–09:06 UTC. Read-only analysis; one query worker, no simulator or bot runs.
Sources: Himeji `9f39befad`, main `e70867963`, Kanazawa `54d23e7dd`, Shenzhen `d42e90558`, Seoul `905c8a1ca`, Nara `88bea787e`, Rome `1ac66fa62`. Full source/data cursors and query receipts are in `tools/himeji/unit31_audit/manifest.json`. Main remained separate and untouched. D-043/D-044 apply; historical verdicts remain frozen.

## 1. Striker visibility changes when measured at its decision

Kanazawa unit12's `q_seen.py` measures both heads at `R[death_round]`. That precedes the queen's move. A later-acting attacker gets a different observation.

Using the **already verified unit30 raw TurnStart states**, all **20/20** selected enemy strikes on our queen start within wrapped Chebyshev distance 3 of the queen's current head. The round-start count was **15/20**. Opponent-queen cases similarly change **3/4 → 4/4**. The five own cases that change are 869494, 881387, 858816, 857671 and 869498; four are the food-extended strikes. The installed 1.2.3 helper defines vision as a wrapped 7×7 head window (`Tile.is_in_vision`). This is geometric observation availability, not proof of which information the bot used.

This is the same consumed selection: 20 own14585 cases / 12 series, **2 ranked and 18 unranked**, plus four opponent cases / four series; 23 unique replay payloads and full map hashes rechecked. It is a deterministic correction, not a new field rate or an independent replication. No sampling interval is appropriate for the exact correction on these selected records.

**Reading to Kanazawa:** the five round-start-unseen attacks do not require tracking beyond the attacker's own vision at action time. H-KZ28's “first saw within two rounds” also needs actor-turn histories before applying its frozen bar; a run of consecutive round snapshots is not first-ever sight. H-KZ29 remains possible, but approach paths alone and these five cases cannot establish it. Test approaches against food-directed drift and matched non-queen targets, with actual observation times and whole-series holdout. Unknown enemy submission IDs remain unknown; neither targeting nor intent is established.

This does **not** give our queen the attacker's later observation: it can still lack the head in its own current vision. Prediction, memory and ally information need their own availability timestamps; an ally seeing a head does not demonstrate a message reached the queen before its move.

## 2. H-KZ26 is a promising screen, not 11–15 demonstrated rescues

Accept the food-free budget correction and the peer's disclosed selection. Preserve its 15/20 approximate alternatives and weight .6 alongside Himeji's qualification:

- Candidate occupancy exempts every tail and does not project the queen's candidate-specific body/growth; the peer explicitly calls this approximate. A geometrically reachable endpoint is not a verified legal escape or a counterfactual survivor.
- Excluding the four **observed** food-assisted strikes leaves 11/20, but does not prove the alternative endpoints are safe from other food-supported routes. “Conservative” here concerns removing cases, not a certified conservative threat model.
- `bfs(..., cap=11)` and missing-distance=99 can miss long threats. Four pure source fixtures reproduce two controls and two failures: L12 has B=13; cells at distance12/13 are threats but the capped search marks them unthreatened. Incidence in the selected replay cases is **not measured**; this is not a claim that the published 15 changes. Bound search by actual enemy budget plus dose, and represent unresolved distance explicitly.
- “0/20 inside reach in the prior round” has missing values: for example game869495 has `d1=None, B1=None`. Report evaluable denominator and births/absence separately; do not convert absent attackers into verified distant attackers.

H-H8 (proposed L24/L49, .4) stays open; H-H6 .5 and H-H7 .4 remain. For an assigned H-KZ26 screen, retain a fixed reach feature and doses off/0/1 on clean carthage-05/live-M2, with H-KZ12 off or fixed, and no second changing mechanism. Before claiming coverage, use at least **60 independent eligible encounters**, including nonattacks, to estimate exposure and variance; match full hash, mode, seat, opponent, phase, lengths, visible food and action order, and reserve later whole series. Sixty is a pilot, not powered proof of wins or a 30% hazard reduction. Select a dose before the held-out D-042 win-led gate; previous 10pp paired planning needs 149/306/463 pairs at discordance .2/.4/.6 before clustering. Falsifier: adequately precise absence of added threat calibration/targeted risk reduction, or adverse overall wins/economy without the predicted benefit. Wide or unexposed nulls remain inconclusive. Rome is already running H-KZ12; no additional arm requested.

## 3. Shenzhen's cohort repair is useful; preserve event identity within rounds

Accept the switch from gross late meals to fully followed birth cohorts. `corpse2.py` now follows births150..R−50, but chooses the first `(round, team)` eat on the cell at or after the birth round. A different pearl may have been eaten on that cell earlier in the **same round**. Team-alphabetical sorting is also not event order.

On the **five newly arrived ranked14585 games / one series** (both sides, ten sides), 1,670 eligible corpse pearls produce two changed fates:

| Game | Birth | Round-only fate | Event-linked fate |
|---|---|---|---|
| 1025051, QoS | r158, (5,4), donor38/A | ally | enemy, r160, age2 |
| 1025055, Portals | r419, (12,7), donor838/A | ally | not eaten within50 |

Raw event traces confirm an eat **before** the new spawn in both birth rounds: event13997 before14115, and144613 before144616. Matching donor + birth round + cell to FRAME's event provenance, with uniqueness assertions, changes total ally/enemy/not-by50 from **1594/29/47 to1592/30/48**. Every birth is accounted for; “not by50” is a fate residual, not a claim that the pearl physically remains. Source/code/counts and counterexamples: `corpse-order.json`.

These two errors do **not** overturn the peer349-game gap of29–39% vs16–19%, nor replace its table. Request event-identity recut on that population. Further qualifications before reference grade: separate ranked/unranked and full map hashes; freeze ladder membership; cluster by series (current `q_corpse2.py` resamples side rows, not games when two top-ten sides share a game); use death-event enemy heads for contact labels instead of `R[r]`. The proposed “half location, half collection” is a descriptive reweighting, not a causal decomposition. Preserve H-SZ28 and its reported intervals with these qualifications.

For H-SZ32 salvage, 12 sides can establish implementation exposure, not a well-powered 5pp response. If assigned, use a fixed post-death horizon and premium doses0/x/2x, paired carthage-05-derived parent, current hashes, corpse-fate plus environmental-food/death/material/win costs, and a variance pilot before sizing the gate. Do not bundle H-SZ33's death-location intervention into that dial. A doomed unit's attempted relocation may not be legal and can change the death itself; measure that risk set explicitly.

## 4. Fresh live series and the switching negative control

New games1025051–1025055: **1–4 vs939**, ranked, own14585, seatA, one series at07:27Z. Five payload/full-map/official-winner checks and ten terminal-queen-field checks pass. Two games reach490, queen alive **0/2**; three early games are censored, not zero-length490 observations. One queen verdict among four losses (**1/4**) and among five games (**1/5**); one longest loss and two elimination losses. PD opponent queen is15 at490 and17 atterminal, so merely keeping a length3 queen would not win that observed comparison. This does not identify its feeding mechanism.

Both round-limit losses are behind on total at490 and terminal: loss-with-material-lead / RL losses **0/2**, losses / material-leading RL games **0/0 undefined**. One selected series is insufficient for a population interval or new stable target. Full hashes, per-side checkpoint values and reason strings accompany the report; frozen H20 reference/intervals are unchanged.

The earlier06:26Z series vs939 was5–0 with the same own submission, seat and ranked mode. **There are zero exact map-hash matches** across the two series. Even their common label weakhold has different hashes (`9c3aa9986574…` versus `665aaa6c8538…`). Opponent bot identifiers are blank in both. Thus the score swing provides no matched switching/spoofing test. H-H2 remains unresolved; alternatives include map composition, variants, ordinary outcome variance and an unobserved opponent change. `series-match.json` is the reproducible negative control. Do not infer intent or stable performance decline.

## 5. Tester and collection readings

Rome `1ac66fa62`: clean carthage05, 1.2.3, live-M2 seed1, corrected doses0/4/8/16; 1777-turn dose0 parity and CPU receipts support implementation checks, not efficacy. Old terrain-only k5 +1.1pp pool pilot remains historical/nonconforming. Chat cursor24 reports60/272 on the current sequence; no completed corrected dose table or gate. Earlier464 failed gen launches remain missing/invalid records, never losses. Close cursor25: all272 k4 games succeeded, but KZ12 logs are absent. Official outcome scoring may proceed; exposure/fallback/feature-conformance claims remain unverified until logged diagnostics or a validated reconstruction is available. Missing logs are not zero exposures; a rerun with different outcomes must remain a separate diagnostic sample.

Seoul's resolved-contract/no-duplicate-run decision is accepted. Nara's zero reading needs two qualifications: live top-team Schooltime96% does not remove headroom from our local parent0/16; and pearl association plus approximate alternatives is not a causal trap mechanism estimate. 1.2.3 local and1.2.9 probes are different populations; a asserted difference in sprint/verdict semantics needs source or fixed-action evidence. No simulator environment change or unrequested rerun here.

Freeze08:56:45Z:122794 corpus records, +297 including five own arrivals, latest own07:27:19Z. Sole collector35400 healthy (latest observed11 downloads/0 errors); ownwatch **still absent**, source6bb33fd7 unchanged. Arrivals through opponent collection do not resolve H26 integration/backfill. RO immutable/query-only DB checkpoint08:49:52Z has14585 active/14265 idle and1173 series; WAL excluded. Ladder084952Z: top306/264/213/91/112/566/55/842/952/507, own76,939rank85. Store31games/62sides plus1110 pending and historical754 unchanged; shared51396 is peer-reported, not recertified. No API, collector configuration, executor or main-source writes.

## RL translation (D-044)

- **Observation:** actor-turn-stamped heads, lengths, known terrain/body/food and information age; candidate-specific next head/body, enemy sprint budget, observed-message availability, corpse donor/birth event/age and death context. Unknown distances and missing observations are explicit, never safe-by-default.
- **Action:** compare ordinary queen moves against a fixed threat representation; retreat may cost food or enter a trap. Salvage priorities and death-location moves are separate action families/dials, with parent0. No policy implemented here.
- **Value/reward:** official queen→longest→total outcome, all-cause/cause-specific deaths, food opportunity cost, birth-cohort enemy-denial fates and economy. Use correct decision-time labels and whole-series holdout; do not label all observed attacks inevitable or all geometric alternatives successful rescues.
- **Demonstration:** selected replays demonstrate food-assisted strikes and same-round corpse turnover. They do not demonstrate remote queen tracking, deliberate spoofing, successful escape alternatives, or beneficial salvage. Those require additional matched observation analysis and assigned held-out tests.

## Reproduction

From Himeji's tree, using main's Python for decoding, never its simulator:

```
python tools/himeji/strike_vision_timing.py --repo MAIN --audit tools/himeji/unit30_audit/strike-audit.json --peer tools/himeji/unit31_audit/peer-seen.txt --out /tmp/vision.json
python tools/himeji/reach_cap_check.py --peer tools/himeji/unit31_audit/peer-q_avoid.py --out /tmp/reach.json
python tools/himeji/corpse_event_order.py --repo MAIN --metadata tools/himeji/unit31_audit/new-own-metadata.json --out /tmp/corpse-order.json
```

`recent_live_check.py` ran against frozen unit31 index with all pre-delta own IDs excluded; full selected metadata is committed for reconstruction. Output `recent-live-sides.jsonl`, `recent-live-summary.json`. No replay payloads or databases are committed.
