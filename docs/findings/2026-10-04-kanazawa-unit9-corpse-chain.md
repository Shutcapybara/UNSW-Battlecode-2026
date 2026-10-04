# Kanazawa unit 9 — corpse-chain bait (H-KZ20), event provenance

4 Oct 2026, 07:12–07:35 UTC. Read-only corpus query `tools/kanazawa/q_chain.py`; no bots, no shared-store writes.

## Question and frozen criterion
Unit 7 found that tree-pocket entries are pearl-baited. H-KZ20 asks whether those pearls are corpse pearls from an earlier death in the same pocket.
Provenance uses the FRAME event stream (spawn origin `bed` = environmental, otherwise the donor's team), not template cells. This follows Himeji H27-01.
Frozen before the run (07:20Z): falsified if the pooled in-pocket corpse share ≤ the board-wide corpse share at the same rounds. Supported (weight 0.5) if diff ≥ +0.10 and the chain share ≥ 0.25.
**Caveat:** the chain test (donor body intersects the pocket) is near-tautological, because corpse pearls drop on body cells. I report it but do not count it. Donor identity, cause, age and lag carry the information.

## Sample
Same in-sample as unit 8: the post-m2 team-7 index, first 286 eligible, stride 96. The selection is pinned to the first 286 because the index grew to 291+ during the unit. First tree-pocket entry per queen per side. Pocket = terrain pocket C ≤ 5 with no cycle (q_cycle).

## Result
| | entries | with pocket pearl | in-pocket corpse / all | board corpse share |
|---|---:|---:|---:|---:|
| us | 19 | 17 | **24/46 (0.52)** | 188/844 (0.22) |
| opponents | 14 | 12 | 9/26 (0.35) | 152/635 (0.24) |
| pooled | 33 | 29 | 33/72 (0.46) | 340/1479 (0.23) |

- **Us:** 13/19 entries have a corpse pair in the pocket. Donors: 10 entries own child/wall, 3 foe (2 invalid, 1 self); by pearl count own wall 20, foe 4. Every donor had length 3 and its head in the pocket. Donor age at death 5–79 (median 9). Lag from donor death to queen entry 2–66 (median 20). Excluding weakhold: 16/34 = 0.47.
- **Opponents:** in-pocket corpse share is near base (Δ+0.11 at the pearl level, 7/14 entries). Their donors are mixed (own wall, own invalid, foe wall).
- **H-KZ22 (born trapped):** falsified. 0/13 of our donors died at age ≤ 3, so children walk into pockets later; they are not split into them.
- **Fresh games** (10 games after the frozen 286, mostly the 06:26Z batch): our entries 3/3 with own-child wall corpses (weakhold r40, Autarky r44, Maze r389). The opponent entry is the same on weakhold.
- **Weakhold r40 branch** (unit 8): a sibling of length 3 dies in the (8,7) pocket at r20, age 9. Its two pearls sit there until our queen enters at r40. The r40 'veto' branch is therefore also a corpse-chain branch.

## Reading
By the frozen criterion H-KZ20 is supported, and specifically for us: our tree pockets kill our small children first, and their corpses then bait our queen. Opponents show little of this. The evidence is associational: pockets that attract children also attract queens, and the pearl may not be causal. Unit 7's rate ratio (20–25 % vs 1–2 % with/without pearl) suggests it is.

## Mechanism proposals (for testers; one switch each)
1. **Death-site tabu (queen):** never step into a terrain tree pocket (C ≤ 5, acyclic) that holds a pearl not seen spawning from the environment, or where an ally was seen to die. Expected sign: our queen tree-pocket deaths fall ≥ 30 %; food/turn falls < 3 % (pocket pearls are ~2 per event).
2. **Child dead-end veto:** length ≤ 4 dragons veto acyclic pockets with C ≤ L+1. Expected sign: fewer length-3 wall deaths and fewer corpse baits; this composes with Himeji H-H7 (child food capture), so watch environmental food.
Both are subsets of H-KZ12. Tabu is cheaper than the full cycle veto and targets the observed path.

## Pointers
Raw output: build/kanazawa/tmp/u9_chain*.txt (local). Query: tools/kanazawa/q_chain.py (`--new` runs the post-286 games).
