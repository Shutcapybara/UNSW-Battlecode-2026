---
id: kanazawa-unit1-sonar-census
author: Kanazawa (Claude Opus 5.5 analyst)
kind: measurement + hypotheses
title: Unit 1 — sonar is universal; echoes see enemy heads beyond vision; H-SZ23 needs an event-study falsifier
evidence: build/kanazawa/sonar/sides.csv (160 post-m2 ranked games, every k-th of 12,477 eligible); q_radar run over 60 more
queries: tools/kanazawa/q_sonar.py, tools/kanazawa/q_radar.py (frame.decode SonarPing events; corpus read-only)
---

# 1. H-KZ1 — who uses sonar (post-m2 ranked, started ≥ 2026-10-02T03:49Z)

320 side-games. 96.2 % cast at least one sonar. Rays per 100 dragon-rounds: top ten 248 (n 29), ranks 11–50 281 (n 119),
others 257 (n 172). Most teams sit at ~400 (four rays, every dragon, every turn), us included (401.6). Top-ten teams with
low rates: 952 (46), 87 (80), 213 (129), 264 (132) — n 1–8 sides per team, so no claim about a style effect.
Ray endings: kelp 62.3 %, ally body 21.4 %, ally head 12.4 %, enemy body 2.4 %, enemy head 1.5 %, nothing 0 %
(wraparound: a ray that finds nothing comes back to the sender's own body, counted as ally). 23.9 % of rays are refracted
(sent into the sender's own neck, leaving through the tail).
Reading: sonar volume is not a differentiator; the content and use are invisible in replays (payloads not decoded here).

# 2. H-KZ2 — echoes as a long-range head sensor (60 games, 2.81 M rays)

Rays ending on an enemy head: 26,832; 60 % of them end more than 3 cells (Chebyshev) from the sender's head, i.e.
outside the 7×7 vision. Enemy-hit ray length median 4, p90 14. Rays ending on the enemy queen's head: 744 (12 per game),
75 % beyond vision. Echo counts are summed over the four rays, so the sender learns "an enemy head lies on one of my
four lines" but not which — unless it casts fewer rays (bearing by schedule) or reads which of its own packets came back.
carthage-05 reads `get_sonar_echoes()` (policy.hpp:23) but only as counts.

# 3. Reading of H-SZ23 (Shenzhen unit 6)

The hazard drop with queen length (2.04 → 1.12 /1k rounds) is cross-sectional. Queens become long where they are safe
(home range, keeper teams, ally-cull feeding), so length marks safety as well as causing speed; team stratification does
not remove position. Falsifier proposed: event study within queen — enemy-kill hazard in the k rounds after the meal that
takes it to ≥ 8 vs the k rounds before, keepers only. Also in tension with H-SZ8 (SSS, 𓎼 feed only in the last 90
rounds) and H-SZ3 (a length-5 runner alive 67 %). Proposed weight 0.3.

# 4. Hypotheses

| id | claim | falsifier | size if true | cost | suits |
|---|---|---|---|---|---|
| H-KZ1 | sonar volume is not a skill marker | — (measured; closed as a fact) | — | done | — |
| H-KZ2 (blue-sky) | a bearing-resolved echo schedule (one ray per turn in rotation from 2 heads, or reserve one direction for scanning) finds the enemy queen earlier than vision | simulator on live maps: bearing to the enemy queen before first sight in < 20 % of games | feeds H-SZ5/14 hunts; small alone | bot copy, 12 sim games | Claude tester |
| H-KZ3 | H-SZ23's length→hazard effect is mostly selection | event-study hazard after crossing 8 < 0.7× before | resets the feed-timing target | corpus pass | Shenzhen or GPT auditor |
| H-KZ4 (blue-sky) | a received packet that fails our checksum means an enemy ray ended on us: a free danger cue | P(death within 10 rounds \| foreign packet) not > 1.5× base | small–moderate | corpus (needs payloads in decode) | Kanazawa |
| H-KZ5 (blue-sky) | some opponents trust any sonar payload; our rays that hit them (2.4 % + 1.5 %) inject data | payload entropy per team shows no unauthenticated format | unknown; spoofing lane | corpus payload decode | Kanazawa |
