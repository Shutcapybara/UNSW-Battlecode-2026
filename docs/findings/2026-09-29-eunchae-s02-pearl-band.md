---
id: eunchae-s02-pearl-band
author: gpt/eunchae/2026-09-29
kind: observation
title: "S2 pearl-band candidate prepared; paired evidence and clone admission remain incomplete"
task: Build an economy-first S2 candidate on an in-band host and provide the required local opponent and Prisoners Dilemma map.
supersedes: nothing
evidence:
  - bots/eunchae-s02-pearl-band/CANDIDATE.toml
  - bots/eunchae-s02-pearl-band/README.md
  - maps/dilemma_10.map
  - experiment_data/team_recon_62_20260927T140359Z/evidence/feature_schema.json
---

## Candidate

The repository already contained `bots/eunchae-s02-pearl-band` before this run; its committed source is from `chaewon-y04-probe`, preserving its yuna-v05 host, atlas, adjacency newborn fix, crown/beacon layer, and solo-ray portal probe. Bed value is 10 (from 8), bed wait is 16 (from 12), split value is 9 (from 8), and portal dive value is 8.5 (from 7). No production or conversion clock changed. `ACT:bed`, `ACT:sprint`, `ACT:probe`, and `ACT:dive` markers were added.

The prompt's claimed economic mechanisms are only partially implemented: stronger bed valuation and portal exploration are parameter changes; confirmed-pearl sprint funding was not isolated as a separate policy. No ablation or paired panel was completed, so H-econ and H-explore are unresolved. The inherited probe's S1 evidence reports 35.9 vs 31.6 portal-step deaths per game on its earlier panel; this does not establish the S2 H-portal threshold.

## Measurement status

The checkout contains unswbc 1.2.2 at `~/.venvs/bc122/bin/unswbc`. Running it needed `PYTHONPYCACHEPREFIX=/tmp/eunchae-pycache` because the default user cache is outside the writable workspace. One sandbox run on Schooltime A vs sinbad-v07 began but its sandbox progress estimated more than 36 minutes; no completed CPU profile or paired outcome is claimed. A non-sandbox Trauma smoke completed through round 500; team B (sinbad-v07) won on length. It is a launch check only, not a paired measurement or metered CPU probe. The full 6-opponent × 10-map × 2-side × 3-seed panel, the five-arm ablations, replay-derived economy metrics, and the four-fixture metered profile remain unmeasured. Consequently no falsifier can honestly be called fired from S2 data.

## Clone deliverable

The repository has public Heartbreaker corpus and model audit artifacts under `experiment_data/team_recon_62_20260927T140359Z`, including a 52-feature legal-view schema and an exported family tree. That is enough to study the policy, but the live bot needs a compatible online feature extractor and a validated induced profile. No `bots/clone-62-v01` or `bots/clone-545-v01` is claimed: the existing Vibing++ mimic has a different training target and feature schema, so relabeling it would not be a clone. Building and validating one requires the full feature parity and tournament work that could not be completed in this pass.

## Map deliverable

The repository already contained `maps/dilemma_10.map`, derived from `maps/dilemma.map`, with four extra length-2 dragons at the coordinates specified in S2. The six-dragon source map was preserved.
