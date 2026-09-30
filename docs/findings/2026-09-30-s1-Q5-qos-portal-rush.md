---
id: S1-Q5-qos-portal-rush
author: s1
kind: observation
question: On Queen of Spades, is the early blind portal rush principled risk-taking or overfit gambling?
evidence: s1 corpus store, QoS side-games 7,674 (7,158 with a transit); transits table; sides table
---

**Map.** 25×35. Each side starts with two length-3 dragons. The two portal pairs link each side's corner near its spawn
to the opponent's half:

- A's pair runs (3,3)/(4,3) ↔ (8,33)/(9,33).
- The other pair runs (15,1)/(16,1) ↔ (20,31)/(21,31).

**What the field does.**

- 2,537 of 7,158 first transits happen at exactly round 8, the shortest path from spawn.
- The median first transit is at round 13.
- The top four teams rush with zero spread: the first transit is at round 8 in 73–92 % of their games, IQR 0.

**It is not a gamble on this map.** Deaths within 10 rounds of a side's first transit, by when that transit happens:

| first transit | died within 10 rounds |
|---|---|
| ≤ r15 (rush) | **5.5 %** (98 % of these are blind) |
| r16–40 | 24 % |
| r41–150 | 48 % |

- Waiting is what is dangerous: the exit side fills up with the opponent.
- Rushers eat 20 pearls by r50 against 10 for non-rushers, within the same teams.

**The advantage holds up under controls.**

- **Within the same team** (40 teams that sometimes rush and sometimes do not; 3,971 sides), holding the Elo gap and
  counting only sides alive at r16: rushing is +0.75 ± 0.08 logit, ×2.1 win odds.
- **When exactly one side rushes** (1,945 games), the rusher wins 0.668. At a gap within ±100 Elo it wins 0.635.

**Heuristic or overfit?** It looks like a general heuristic ("take portals early") that happens to be very good on QoS.

- The same teams rush portals early on the other maps too: 66–84 % of their side-games have a transit by r15 (cheji 50 %).
- How safe a blind first transit is depends on the map. Died-10 by map:

| map | blind first transit died within 10 rounds |
|---|---|
| Trauma | 0.5 % |
| Schooltime | 4 % |
| PD | 4–6 % |
| Default | 8 % |
| Autarky | 9 % |
| QoS | 18 % (all first transits; rushes 5.5 %) |
| Slithery | 25 % |
| Portals | 30 % |
| Trophy | 32 % |

- The heuristic is +EV on most ladder maps. Whether it transfers to unseen maps depends on their exits.
- A version that also prices the exit (known or blind, crowded or not) would be the principled form.

**Us.** Our median first transit is at r30. We rush in 11 % of games. Our QoS win share is 0.28 (Elo-expected ~0.42).

## Addendum: the out-of-sample bet

This treats each ladder map as one draw of an unseen map (`build/s1/out/rush_by_map.csv`).

- **Rush** = the first transit comes within 7 rounds of the earliest first transit seen on that map.
- **Within-team** = compared with the same team's other games on that map, holding the Elo gap, among teams that
  sometimes rush and sometimes do not.

| map | dragons/side | rush died-10 | later first transit died-10 | within-team win effect (logit) | pearls@50 gain | total@100 gain |
|---|---|---|---|---|---|---|
| Trauma | 2 | 0.1 % | 0.9 % | +0.37 ± 0.08 | +12.6 | +9.1 |
| Schooltime | 3 | 1.7 % | 11.7 % | +0.32 ± 0.08 | +7.8 | +25.8 |
| Default | 4 | 2.1 % | 12.7 % | +0.06 ± 0.07 | +1.1 | +0.9 |
| PD | 3 | 3.2 % | 8.7 % | +0.19 ± 0.22 | +5.8 | +3.7 |
| QoS | 2 | 5.5 % | 34.5 % | +0.69 ± 0.08 | +7.9 | +5.5 |
| PD 10 | 5 | 5.6 % | 9.1 % | +1.14 ± 0.26 | +9.8 | +2.3 |
| Autarky | 6 | 5.9 % | 12.1 % | +0.30 ± 0.09 | +2.8 | +3.9 |
| Trophy | 2 | 10.9 % | 49.5 % | +1.15 ± 0.08 | +9.9 | +19.8 |
| Portals | 3 | 28.2 % | 28.8 % | +0.40 ± 0.08 | +17.2 | +11.6 |
| Slithery | 7 | 31.6 % | 19.9 % | +0.11 ± 0.08 | +14.4 | +3.5 |

(Devil has no portals.)

1. **The early rush is +EV on every ladder map** (0 of 10 negative). That includes the two maps with hostile exits,
   where 28–32 % of rushers die.
2. **Waiting makes the exit more dangerous on 8 of 10 maps** (QoS 5.5 % → 34.5 %, Trophy 11 % → 50 %). The
   mechanism is structural: early on, the opponent has not reached the far side of the portal yet. That is a property
   of spawn separation, not of a memorised map, so it is the part most likely to transfer to unseen maps.
3. **Top teams do not tune the rush to exit hazard.** The per-team correlation across maps between rush share and the
   map's rush death rate runs −0.6 to +0.4 (cheji −0.03). They look like blanket policies with quirks, not memorised
   safe exits.
4. **The QoS bet in numbers.** It stakes one of two dragons (half the material) at a 5.5 % loss rate; the worst ladder
   map is ~30 %. Across the ten maps, the pearl gain covered the worst case.
5. **What an unseen map could still do.** It could have exits into dead ends or enemy spawns. The ladder sample has two
   such maps out of ten, and there the rush was still neutral to positive.
