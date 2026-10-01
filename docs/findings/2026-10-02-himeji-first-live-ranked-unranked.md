# Himeji unit 7 — first live games of submission 14265

Published 2026-10-01 17:39 UTC. **The first collected live games are 5–0 ranked and 1–9 unranked, against different opponents.
Our queen died in all 15.** This is two single-series diagnostics, not evidence of a ranked/unranked mode effect or
a stable deployment-strength estimate. One unranked loss documents a late material-lead reversal.

## Identity, populations and limits

All 15 replay headers identify our bot as **14265**, agreeing with corpus metadata and main D-041's activated
`LV-hb1-14-prior-r540-ed7e4515-ai`. Our side is A in all 15. Opponent header identifiers are empty, so their submitted
versions are unknown. Current ladder ranks describe teams, not proof of the versions used in these replays.

| Population | Games / series / opponents | Opponent | Official W–L–D | Queen alive@490 / reached | Queen alive at RL end / RL |
|---|---:|---|---:|---:|---:|
| Ranked | 5 / 1 / 1 | h (841), rank85 | 5–0–0 | 0/1 | 0/1 |
| Unranked live test | 10 / 1 / 1 | Team SKKU (249), rank6 | 1–9–0 | 0/4 | 0/3 |

The ranked extract covers Slithery, Devil, PD, Autarky and Trophy. The unranked series covers all ten pool maps.
These are all completed collected post-rule team-7 replays at the frozen index; collection does not establish that
they are all games the team played. Era is post-1.2.3; all occur after the established transition gap.

**Uncertainty/stability:** one series per population, one opponent and one seat cannot estimate across-series
uncertainty or generalize to the field. No bootstrap CI is published: resampling the lone series would falsely give
zero width. The current ranked top-ten-minus-us field gap is still **NA**, now because matched contemporary field
references and adequate live coverage are missing, not because live-us has no games. Local panels remain separate.
The no-Devil panel baseline is also a different variant from the activated hb1-14 submission.

All official winners agree with the corpus index, all 30 end queen fields agree with reconstructed states,
and old/new inferred winners happen to agree for these 15. This small sample does not invalidate earlier audits
showing that official-result extraction is necessary.

## Opening, component by component

Cells below are **us / this game's opponent** at r50. These are raw paired diagnostics, **not field percentiles**.
Bed pearls, splits and commanded-path transits are cumulative through checkpoint 50, matching Himeji/S-1 event
conventions. Territory and total use checkpoint states. All 15 games actually play r50. The CSV also includes bed
capture, units, r25/100/150/250, explicit played-checkpoint flags and signed opponent-minus-us differences.

| Population | Map | Bed pearls | Splits | Transits | Territory share | Total length |
|---|---|---:|---:|---:|---:|---:|
| Ranked | Slithery Fight | 152/55 | 108/25 | 2/0 | 0.50/0.50 | 113/74 |
| Ranked | Devil | 40/10 | 23/2 | 0/0 | 0.80/0.20 | 48/8 |
| Ranked | Prisoners Dilemma | 22/7 | 18/5 | 2/2 | 0.79/0.21 | 31/12 |
| Ranked | Autarky | 36/15 | 30/4 | 5/0 | 0.67/0.33 | 49/34 |
| Ranked | Trophy | 28/22 | 16/3 | 0/0 | 0.96/0.04 | 32/11 |
| Unranked | Schooltime | 9/10 | 5/7 | 0/2 | 0.28/0.72 | 12/18 |
| Unranked | Portals | 28/17 | 11/6 | 7/6 | 0.50/0.50 | 23/19 |
| Unranked | Slithery Fight | 148/134 | 103/97 | 6/0 | 0.44/0.56 | 94/93 |
| Unranked | Queen Of Spades | 18/23 | 9/11 | 5/3 | 0.46/0.54 | 23/21 |
| Unranked | Default | 8/24 | 8/15 | 1/14 | 0.21/0.79 | 21/38 |
| Unranked | Trophy | 24/31 | 11/14 | 1/2 | 0.49/0.51 | 25/36 |
| Unranked | Prisoners Dilemma | 11/14 | 11/18 | 0/1 | 0.16/0.84 | 2/17 |
| Unranked | Autarky | 22/24 | 21/24 | 0/12 | 0.47/0.53 | 31/36 |
| Unranked | Devil | 14/34 | 10/23 | 0/0 | 0.34/0.66 | 7/31 |
| Unranked | Trauma | 24/4 | 13/4 | 5/2 | 0.50/0.50 | 27/12 |

Against h, we lead total material on **all five maps at both r25 and r50**. Against Team SKKU's unranked entry,
**6 of the 9 losses are already behind on total at r25, and 6/9 at r50** (not necessarily the same six). Default's
r50 bed pearls are 8–24 and transits 1–14; Devil is 14–34 bed pearls and 10–23 splits. This is evidence of opening
deficits in those individual games. It cannot attribute a causal cost to any one component.

There are also losses despite r50 material leads: **Portals 23–19, QoS 23–21, Trauma 27–12**. A queen-only account
would miss the observed opening and later conversion failures. Both queens are dead at the end of all three RL
unranked games, so none of those verdicts was queen-decided; the opposing queen survives only the Default elimination.

`cluster-diagnostics.json` reports r25/50/100/150/250 by Esquie's explicitly published groupings: corridor/kelp
(Devil, Trauma), portal-heavy (Portals), default/trophy, QoS, and Schooltime singleton. Autarky, PD and Slithery
stay per-map singletons because the available excerpt does not specify their exact k=8 assignments. Cluster means
are equally weighted over the observed map-games; they are not opponent-matched field gaps. Every row has counts,
era via the frozen post source, uncertainty/stability labels and a null field percentile. Do not invent missing
cluster membership or treat outcome-based queen-hazard groupings as Esquie's structural signatures.

## Queen and material-lead denominators

Median queen death is **r5 ranked** and **r59.5 unranked**; all 15 queens die. Pocket-map mix differs, so comparing
those medians as a treatment effect would be misleading. Dead-as-zero queen length at actual r490 has median 0 in
both populations. Schooltime reaches r490 but ends by elimination at r498, which explains unranked 0/4 reached
versus 0/3 RL-end denominators. No early end is carried into the r490 denominator.

| Cohort, material checkpoint | RL losses with lead / RL losses | RL losses with lead / all RL leads |
|---|---:|---:|
| Ranked, r490 | 0/0 (NA) | 0/0 (NA) |
| Unranked, r490 | 1/2 | 1/1 |
| Ranked, final state | 0/0 (NA) | 0/0 (NA) |
| Unranked, final state | 0/2 | 0/0 (NA) |

These tiny denominators are a descriptive audit, not targets or estimated rates for the field. Lead means own
total length strictly exceeds opponent total at the named checkpoint. The numerator changes when the checkpoint
changes; neither fraction can be called simply “round-limit losses with a lead” without its definition.

## Trauma g826786: an observed late reversal

At the **start of r490**, our longest robot is id444, length21 versus the opponent's longest13; total is72–68.
Both queens are dead. At **r494**, id444 hits a wall and loses21 segments. At r495 our total is49 versus67, and the
replacement longest is17 versus16. The opponent's id403 eats five ally-corpse pearls in rounds490–497, growing
from13 to18. Our replacement id355 also grows to18. The final header says queen0–0, longest18–18, total51–57:
official loss on total. There are no own splits or multi-step moves in the recorded last ten rounds.

This directly identifies the wall death in the lead reversal. It does not prove an avoidable winning alternative,
intentional ally feeding, or a fix's causal gain. Next live reading should separately track (a) early material
deficits and (b) deaths of the currently decisive robot while ahead. Existing L39/H-Q7 endgame questions remain
relevant even when both queens are dead. H-H1 stays proposed weight0.5; no new intervention claim or bot experiment.

## Coordination and next unit

No new main/peer commits since unit6: main1d838553a, Antioch85637735c, Carthagef91c65873,
Nara21a182700, Kyoto7c835936c. Their board entries, TARGETS and status cursors are unchanged. Rome's local status
now says L10 pool480/480, gen0/1392, without a new paired score/verdict. Completion alone does not validate L10;
the official baseline corrections still apply before the comparison. No new tester outcome is inferred.

Freshness: index **80071 unique games**, latest start **2026-10-01T17:29:40.177Z**, SHA
`ce48c0ded51db812e57b5350ff054e5e0c1ed039aba60012242c0fff69c51efd`; ladder **20261001T173018Z.json**, SHA`43ee125383d431f552201f6dc932e8db15d4460f5751873fe603c9c97198a7d1`. The frozen ladder records are included.
Mac S-1 games file remains3,822,463bytes/mtime_ns1790764194040268141, last verified pre-era; published desktop post
store sync remains pending. No helper that might rebuild shared normalizers was called.

Next: new live **ranked** series/opponents/seats and additional observed maps; retain unranked as a separate testing
population. Refresh current ranked field references per map/structural grouping before assigning live percentiles.
Accumulate series rather than resampling these fifteen games into false precision. Preserve this first-live freeze
and all historical panel/reference verdicts. No collector, simulator, upload or activation actions were taken.

## Reproduction

```
python tools/himeji/live_first.py --repo /path/to/main --decoder /path/to/wt-himeji --out /scratch/live
python tools/himeji/summarize_live.py /scratch/live
python tools/himeji/endgame_finish.py /path/to/corpus/replays/826786.replay /path/to/wt-himeji /scratch/trauma.json
```

For the exact frozen audit, copy `games.jsonl`, `manifest.json` and `ladder.json` from
`tools/himeji/unit7_audit/` into the scratch directory before running. The source decoder/extractor and existing
`post_refs.one` are from Himeji parent99b9dbd11; the outcome is replaced by the authoritative header before feature
extraction. Checkpoint and geometry conventions are preserved. One query worker was used, now complete. No shared
cache/store/corpus writes. Data files are compact JSON/CSV, without replays or models.
