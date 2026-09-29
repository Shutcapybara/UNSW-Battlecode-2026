# Odin family — cross-line synthesis

Odin is a research line assembled from the post-Gavroche family studies. Its
first source is [odin-v01-synthesis](../bots/odin-v01-synthesis/README.md).
It is experimental and has not been promoted.

## Reviewed family inventory

The repository snapshot prefixes reviewed are Aramis, Athos, Avery, Bifröst,
Chimera, Dartegnan, Drake, ED, Ein-dog, Einstein, Fafnir, Fenrir, Fermi,
Feynman, Fry, Gödel, Heimdall, Hunter, Hydra, Javert, Jet, Kraken, Leviathan,
Loki, Monte Christo, Newton, Ouroboros, Porthos, Scholze, Serre, Sinbad,
Skadi, Spike, Tew, Tidus, Valjean, Vicious, vn, Von Neumann, Witten, and
Yuna. The rows below group related controls and mechanism studies; results
remain attached to their exact source versions.

## Selection and transfer record

| Family studies | Useful result or lesson | Odin decision |
|---|---|---|
| Serre / Sinbad | Strong broad host in the reviewed shared-ledger report. It combines arrival-aware beds, bounded search, cautious threat pricing, portal and food sharing, and crown feeding. Known gaps include Devil, Arena, flipped maps, and late length conversion. | Use the e23-fixed Serre v01 source as Odin's base. |
| Porthos / Monte Christo | Porthos x04's early-saturated policy scored 126–56 on its 182-game gauntlet, thirteen more wins than x03. It grades child and parent room, discounts crowded target routes, and gates enemy-density pressure and trade relaxation by phase, saturation, and role. | Transfer all three policy consumers and their spatial inputs; test the transfer on the Sinbad host. |
| Javert | Its type-7 length-density radio was the only radio graft to survive a fresh reserve: 10–2, with gains from three confined-map conversions. | Use Porthos's aggregate count and directional length reports as inputs to Odin's gated movement policy. |
| Heimdall | V10 scored 91–59 against five references on 15 maps. A single isolated ray makes the next enemy echo interpretable as lane evidence, not a remote coordinate. Its one-game Big Empty sandbox check was clean. | Add a small two-round lane cost. Crown, prey, handoff, and portal traffic keep priority; ordinary food and density reports are deferred on scan turns. |
| Fenrir / Bifröst | Portal memory and arrival-ready bed values are useful. Fenrir v18's newborn escape handoff improved its panel over v13. Fenrir v20's lower density discount trailed v18 on its comparison. | Keep the host's portal and arrival-aware resource policy. Hold the newborn handoff for a separate measured arm; do not adopt v20's density change. |
| Ouroboros | Probabilistic threat pricing and persistent corridor doom explain its low wall-death rate. Role mixes alone did not close the length/endgame tradeoff. | Keep the host's probability-priced threat and bounded trap evaluation. |
| Fry / Hunter / Hydra | Survival tactics and shared sightings help. The C++ ladder line has high self-harm; Hunter v20 survives well but loses final length races; Hydra's pack chase does not replace production. | Retain tactical safety and shared information, and keep production and crown conversion as explicit targets. |
| Leviathan / Kraken | Leviathan has careful material accounting; Kraken has bounded BFS and gossip. Kraken's body and wall deaths show that role labels and a danger map alone are insufficient. | Keep bounded search and sonar on the compatible host; do not transplant a full alternate evaluator. |
| Avery / Spike | Avery's crown race wins on matchups where the French line loses final length. Spike's replay review found losses where teams held more total length but small dragons stayed beyond the 16-tile feeder radius; x03 raised it to 40 as a targeted hypothesis. | Keep the existing crown logic and set Odin's feeder radius to 40. Track elimination losses as the counter-risk. |
| Skadi / Fafnir / Scholze / Witten | Size-matched support had small positive matched results without a stable fresh-seed gain. Skadi's combined exit guard and exit-only branch trailed their control; static portal-value changes also showed map dependence. | Keep the host's current support and safety logic; defer those exit and portal changes. |
| Gödel / Von Neumann / vn | Removing strikes is costly, but broad aggression and most strike-margin refits did not pass wider gates. Porthos's phase/saturation conditioning is the specific opening policy Odin borrows. | Gate pressure to early, saturated foragers and preserve the threat model elsewhere. |
| Loki / Drake | Loki's learned ranker did not retain Heimdall's earlier gains on that host. Drake's dual-EWMA spatial contrast did not improve its validated candidate. | Use bounded, short-lived spatial evidence; do not add learned ranking or long-window global gradients. |
| Chimera / Einstein / Jet | Compact-map ladder dispatch and renewal-rich map dispatch are specialized designs; Einstein is a frozen Ouroboros control. | Keep Odin map-agnostic and preserve the selected host. |
| Athos / Aramis / Dartegnan / Valjean | Contract extraction can isolate behavior; Aramis frontier policy and Valjean portal recon were map-sensitive or neutral. Dartegnan's Big Empty candidate had repeated CPU-limit failures. | Keep direct policy integration and bounded scans; defer an executor refactor. |
| ED / Ein-dog / Tidus / Newton | Temporal candidates reuse Serre/Fafnir controls. Newton's fixed round-200 production stop was neutral on its screen; Ein-dog and Tidus preserve Newton x10 as controls. | Avoid a fixed production stop; retain state-gated behavior. |
| Fermi / Feynman / Tew | These lines isolate combat, design, and support-gated strike questions. Gödel's host comparison found no gain from adding the support gate again. | Preserve conditional trades without another support bonus. |
| Vicious / Yuna | Their temporal campaigns use frozen Gavroche controls and keep timing variants as separate research arms. | Do not copy unmeasured timing overrides into Odin. |

Source records include [Serre](serre.md), [Porthos](porthos-lineage.md),
[Heimdall](heimdall-family.md), [Fenrir](fenrir-family.md), [Gödel](godel.md),
[Leviathan](leviathan/LINEAGE_REVIEW.md),
[Avery](avery-lineage-handoff.md), [Skadi](skadi.md),
[Loki](loki-family.md), [cross-line review](cross-line-review.md), and
[Spike x03](../bots/spike-x03-v32-farfeed/README.md).

## Odin v01 behavior

Odin starts from Serre v01 and adds four interventions:

1. It uses Porthos's bounded aggregate-count and directional-length sonar
   reports. Progress toward a target is discounted by local crowding.
2. Before round 200, only a forager on a team at 70% or more of its unit limit
   receives an enemy-density movement bonus and a 1.5-point lower strike
   margin. Crown and feeder roles do not.
3. It scales ordinary split value by reachable room around the parent and
   child, with a floor and a small population-scarcity adjustment.
4. It sets the feeder radius to 40, from Spike's replay-derived conversion
   hypothesis. Heimdall's isolated echo scan adds a small lane cost after an
   enemy appears in a single-ray echo. Portal, crown, prey, and handoff
   messages keep priority; that scan turn defers ordinary food and density
   reports.

The first three interventions target Serre/Sinbad's crowding, opening, and
contested-bed problems. The longer feeder radius targets its late conversion
gap. The screen below is Odin's first matchup evidence: it lost overall to all
four references, with its weakest map totals on Dilemma and Scattered Fleets.
The large seat imbalance still needs paired-seed follow-up.

## Odin iteration results

The first measured interventions were kept as separate snapshots. Odin v02
added Bifröst-style opening production and rescue, but regressed on the
13-map screen at 47–57 against the four references. Odin v03 gated that arm to
compact maps and restored arrival-only bed valuation. It became the measured
champion at 58–46 on the same 13-map screen, with 0 errors:

| Opponent | Odin v03 wins | Odin v03 losses |
|---|---:|---:|
| Fenrir V20 | 11 | 15 |
| Heimdall V10 | 14 | 12 |
| Yuna V03 | 14 | 12 |
| Bifröst V01 | 19 | 7 |
| **Total** | **58** | **46** |

The v04 density revaluation scored 57–47. The v05 newborn-separation arm
improved the focused Dilemma panel but regressed to 50–54 on the 13-map
screen. v06 gated that separation arm to compact boards and scored 57–47, so
neither separation variant replaced v03.

As a fresh-map check, v03 played all 20 maps under `maps/new/` against the
same four references, both seats: 87–73 with 0 errors. Combined with the
13-map screen, v03 is 145–119 across 264 directional games (54.9% wins):

| Opponent | Established 13 | Fresh 20 | Combined |
|---|---:|---:|---:|
| Fenrir V20 | 11–15 | 18–22 | 29–37 |
| Heimdall V10 | 14–12 | 24–16 | 38–28 |
| Yuna V03 | 14–12 | 20–20 | 34–32 |
| Bifröst V01 | 19–7 | 25–15 | 44–22 |
| **Total** | **58–46** | **87–73** | **145–119** |

The v03 two-map judge-sandbox smoke screen completed 16/16 games with 0
errors and finished 9–7. These are native unseeded screens because the
installed `unswbc` does not expose a seed option; they establish the current
Odin champion but do not justify frontier promotion on their own. Result
artifacts are under the ignored `build/odin-v03-*` directories.

## Validation status

### Four-family 35-map screen (2026-09-28)

Odin v01 played both seats against the current tested snapshots of Fenrir,
Heimdall, Yuna, and Bifröst on the 35-map shared panel: 15 established maps
plus all 20 maps in `maps/new/`. This was a native `unswbc 1.2.1` tournament,
with no judge sandbox and no shared fixture seed. The outcomes are a screening
result; they are not seed-paired estimates.

| Opponent | Odin wins | Draws | Odin losses |
|---|---:|---:|---:|
| Fenrir V20 (`fenrir-v20-crowded-resource-revalue`) | 29 | 0 | 41 |
| Heimdall V10 (`heimdall-v10-isolated-echo-lanes`) | 30 | 0 | 40 |
| Yuna V03 (`yuna-v03-core`) | 33 | 0 | 37 |
| Bifröst V01 (`bifrost-v01-portal-memory`) | 30 | 0 | 40 |
| **Total** | **122** | **0** | **158** |

That is a 43.6% win rate across 280 games (70 per opponent). Odin won 73–67
when assigned team A and 49–91 as team B, so the side split is substantial and
needs a seed-paired follow-up. Across the eight games per map (four opponents,
both seats), Odin's best result was Trophy at 7–1. Dilemma and
Scattered Fleets were 0–8; Autarky, Devil, Far Harbors, Queen of Spades, and
Schooltime were each 1–7.

The first screen does not show Odin ahead of any of these four references over
the complete map panel. Raw results, standings, logs, and the frozen input
manifest are in the ignored local directory
`build/odin-v01-vs-four-families-20260928/` (`results.json`, `standings.csv`,
and `manifest.json`).

A release decision still needs a paired-seed comparison against Serre v01,
repeated seed-paired fixtures to resolve the side imbalance, a fresh-map
check, and a judge CPU/memory screen. Record Odin's results separately; do not
copy Serre, Porthos, Heimdall, or Spike metrics into its entry in
[FRONTIER.md](../FRONTIER.md).
