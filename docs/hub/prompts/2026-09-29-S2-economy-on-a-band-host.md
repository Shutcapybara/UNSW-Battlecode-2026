# Build prompt S2 — economy first, on a host inside the band

Issued by the JKS director (Claude, Cowork session 01Nu), 29 September 2026, for **Just Keep Swimming, team 7**.
Repository `/Users/alik/Documents/Projects/UNSW-Battlecode-2026` (`REPO`). Self-contained; S1
(`docs/hub/prompts/2026-09-28-S1-swarm-dissolve.md`) supplies the shared rules of the game (§5), the framework (§3),
the measurement protocol (§7) and the deliverable format (§8) — they apply unchanged except where this prompt says
otherwise. Read `docs/findings/2026-09-28-director-S1-evaluation.md` first: three lineages built S1 independently
and it failed the same way three times; this prompt exists because of what they found.

## 0. Your job in one paragraph

Build one bot, `<lineage>-s02-<tag>`, on a host that is already inside the live band, that raises **units at r100 and
total length at r250** on the ten public maps against band-class opponents without raising deaths — and nothing
else. Keep the crown/beacon layer of your host. Do not move any production or conversion clock. Deliver the S1 §8
package (manifest, README, findings, seeded paired panel, ablations) plus the two items in §4. Ship within one
session; iterate as s03, s04.

## 1. What changed since S1 (facts you build on)

- **The host.** ouroboros-v10-beacon scores 0.15–0.30 against our own local band; every S1 delta was against an
  incumbent far below the live control. Start from `bots/fenrir-v18-arrival-ready-beds` (byte-identical to the live
  control 9508; teammate code — copy with attribution in `lineage_parent`, never edit in place), `bots/yuna-v05-core`,
  or `bots/chaewon-y04-probe` (yuna-v05 + atlas + newborn-neck fix + portal probe, +0.062 on 96 fixtures).
- **Production is pearl-limited, not rule-limited** (chaewon: sinbad eats 630 pearls on Trophy where v10 eats 60;
  sakura: three maps starve at 5–6 units r100). Loosening the split rule alone adds churn (≈ 240 self-collisions per
  Portals game), not units. The levers are bed pre-positioning (arrive as the countdown hits zero), confirmed-pearl
  sprint funding, contested-pearl appetite, and not dying on the first step: portal-step deaths are the yuna family's
  largest killer (47 of 89 deaths on Default), 101 wall deaths per Schooltime game for y04, and every one of 1,005
  audited friendly head-ons was at a portal exit.
- **Known fixes to inherit:** the newborn neck bug (a split child keeps the parent's facings — link the neck by
  adjacency), the atlas (ship the ten public maps' terrain; match on the first view; +0.15/+0.25 on two hosts;
  `tools/chaewon/build_atlas.py`), the solo-ray portal probe (cast one ray through the adjacent portal; the echo
  tells next turn whether a dragon stands on the line; +0.062), the HOLD packet through the portal (blind head-ons
  19 → 6 on the probe fixture), Prisoners Dilemma's sealed corridors (a 10-dragon server version exists; treat PD as
  a trap map until the local set has it).
- **The framework strip cost real points** (sakura's extras-only arm: −16 net on the four portal-heavy maps).
  Portal exploration as a `reposition` bias for gatherers on portal-pair-rich maps is *in*; a scout role, density
  gossip and hotspot packets stay out.
- **Rays are free** in points (A1-Q6/Q7); price packets by whether a consumer changes an action, never by bytes.
- **Sonar-based certificates deliver only when the body is straight at the cut** (chaewon, 35–49 % of splits) — or
  always (kazuha, sakura). The A2 analysis is settling this; do not depend on the certificate for anything.

## 2. Hypotheses (each with its falsifier; report which fired)

- **H-econ:** bed pre-positioning + confirmed-pearl sprints + contested-pearl appetite raise total length at r250 by
  ≥ +15 and units at r100 by ≥ +4 in exact pairs against the panel, with self+wall deaths ≤ 5 per 1k dragon-turns.
  Falsifier: total r250 delta < +8 or deaths above the bar.
- **H-portal-safety:** the solo-ray probe + HOLD packet + atlas cut portal-step deaths per game by ≥ 50 % on Default,
  Schooltime and Portals in exact pairs. Falsifier: portal-step deaths fall < 25 %.
- **H-explore:** a `reposition` portal-dive bias for gatherers on maps with ≥ 6 portal pairs recovers ≥ +3 net pairs
  over the base on Portals/Slithery/Trauma (sakura's regression maps). Falsifier: ≤ 0 net on those maps.

Ablate each on the same seeded fixtures (base, +econ, +portal-safety, +explore, all).

## 3. Measurement (S1 §7, with these changes)

- Opponents for the panel: `bots/fenrir-v18-arrival-ready-beds`, `bots/sinbad-v07-divecap`,
  `bots/gavroche-v32-supported-divecap`, `bots/ouroboros-m01-vibing-mimic`, `bots/yuna-v05-core`,
  `bots/chaewon-y04-probe`, plus every `bots/clone-*` that exists (see §4). Not `fry-*`, not ouroboros-v10.
- unswbc 1.2.2 seeded (deterministic across machines; record the seed); ten maps × both sides × seeds 1–3.
- Metered probes on **four** fixtures (Schooltime A, Portals B, Slithery Fight A, Trauma B) on both toolkits; the hub
  gate is zero faults, max < 80 M, p99 < 60 M on 1.0.0.
- Activation contract markers of your own choosing (`ACT:bed` on a pre-positioning move, `ACT:sprint` on a funded
  sprint, `ACT:probe` on a portal ray, `ACT:dive` on an exploration step), declared in `CANDIDATE.toml`.
- Report the S1 six-line format plus: units r25/r50/r100, total r250, portal-step deaths per game, pearls eaten per
  game, first-pearl round — medians per map class, per arm.

## 4. Two extra deliverables this generation

1. **A clone of one live eliminator** as a local opponent: `bots/clone-62-v01` (Heartbreaker, 103 live games in
   `LIVE/state` + the public corpus) or `bots/clone-545-v01` (dev test 1, 55 + 25 games). Recipe: the imitation
   approach of `bots/ouroboros-m01-vibing-mimic` (legal-input features from `features_view.py`, a boosted-tree policy)
   trained on that team's games, validated by its induced profile against our bots (target: within 1 standardised
   unit of the live profile on units r100 / total r250 / longest r400, A1-Q4 c). This is the single most valuable
   artefact any lineage can produce: nothing local currently exercises the failure mode that decides live games.
2. **A 10-dragon Prisoners Dilemma map** (`maps/dilemma_10.map`: four extra length-2 dragons at (19,6)/(12,9)/
   (15,14)/(16,1) per A1-Q3) so local PD results stop being irrelevant to the server's.

## 5. Deliverables and anti-goals

S1 §8 verbatim (`bots/<lineage>-s02-<tag>/` with `bot.toml`, `main.py`, `params.py`, `CANDIDATE.toml`, `README.md`;
`docs/findings/<date>-<lineage>-s02-<tag>.md`; nothing uploaded). `priority = 300` in the manifest; the director
sets the queue order from evidence. Anti-goals: no clock changes, no dissolve/escort work, no scouts or gossip, no
learned ranker in the turn loop, no wall clock, no unseeded randomness, no local-rating claims, no upload. One
paragraph for the director at the end: what you built, the paired number with its N and seed, the CPU profile on the
four fixtures, which falsifiers fired, and what s03 changes.
