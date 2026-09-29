# R-2 `ra` status — Monoco lineage

Base: `ares-v06-expanded-search-support`, atlas off (V06's atlas helper has no call site). The requested `claude/r1-status.md`, other-lane status, and ten-day plan are absent from this repository snapshot; the brief's default V06 base is used. Worktree: `../wt-ra`, branch `r/ra`.

| Version | Mechanism | Pool delta | Generalisation panel delta | CPU max | Verdict | Why |
|---|---|---:|---:|---:|---|---|
| ra-01 | Double existing enclosed-room/trap penalty | −0.0838 normalized economy mean; r100 dragons −0.0504, length −0.0507 | not run | 8.72M candidate points | rejected on pool | Panel win rate fell 4.37 points. Wall deaths improved 14.36%, but economy/material fell beyond resolution; no seed 2 or generalisation panel. |

Candidate expectation was entered in `bots/ra-01-monoco-trap-avoidance/CANDIDATE.toml` before candidate runs. The four sandbox CPU outputs and generated golden transcripts are under ignored `build/`.
| ra-02 | Raise the child-room minimum from 4 to 8 reachable cells before splitting | seed 1/2 combined: economy −0.0139; r100 dragons/length −0.0143/−0.0144; win flat | not run | 8.72M candidate points | rejected on pool | 320 seed-1 plus 320 seed-2 side-games. Hygiene rates were flat; economy missed +0.05 and both r100 material guards fell. |
| ra-03 | Raise the existing multi-step sprint action cost from 1.0 to 1.5 (switch `Params::monoco_sprint_discipline`) | seed 1/2 combined: economy +0.0209; r100 dragons/length +0.0233/+0.0233; win +0.31 pp | not run | 8.66M candidate points | rejected on pool | Sprint cost/pearl fell 0.0145 and hygiene stayed under 10%, but the economy gain missed +0.05; no generalisation run. |
| ra-04 | Increase `pearl_ttl` from 40 to 60 rounds | pool delta exactly 0 across all metrics and wins | not run | 8.45M candidate points | rejected as no-op | The changed constant has no call sites; the policy uses `memory_ttl`. No seed 2 or generalisation run. |
| ra-05 | Increase active policy memory TTL from 40 to 60 rounds | seed 1/2 combined: economy +0.0024; r100 dragons/length +0.0001/−0.0022; win flat | not run | 8.86M candidate points | hold | All hygiene classes improved slightly (wall −0.74%, ally-body −0.32%, ally head-to-head −2.36%) but economy is flat; switch is off for retest stacked on the next accepted economy change. |
| ra-06 | Increase target hysteresis from 1.25 to 1.75 to reduce target churn | seed 1: economy −0.0435; r100 dragons/length −0.0586/−0.0509; win −2.50 pp | not run | 8.56M candidate points | rejected on pool | Hygiene classes each improved 2–3%, but all r100 material and the economy curve fell; outside resolution and fails guards, so no seed 2 or generalisation run. Switch remains on in the measured candidate. |

ra-06 switch-off parity fingerprint: `params.hpp` SHA-256 `94119ae09453ad4e408620b72790d992ad1308e09a78ae6615b8e436a7ef0614`; golden replays: 52,728 turns, 1,842 dragons, 0 divergences. Seed-1 pool features are in ignored `build/zoo/ra06/`; parent features are in `build/zoo/ra01/`.

| ra-07 | Increase ally-density target discount weight from 0.10 to 0.50 to spread target choices | seed 1/2 combined: economy −0.0169; r100 dragons/length −0.0156/−0.0059; win −0.94 pp | not run | 8.81M candidate points | rejected on pool | The targeted ally head-to-head death rate improved only 2.11%, below its predicted 10%; all other hygiene rates improved 1.97–2.30%, but economy/material regressed. No generalisation run. |

ra-07 switch-off parity fingerprint: `params.hpp` SHA-256 `67559f2e54551313afca2c7f530fa76b7b4fd326fbc0e58b5c3517254b6eb999`; golden replays: 52,728 turns, 1,842 dragons, 0 divergences. Seed-1/2 pool features are in ignored `build/zoo/ra07/` and `build/zoo/ra07-s2/`.

| ra-08 | Raise reachable-bed target value from 8.0 to 10.0 | seed 1: economy −0.0327; r100 dragons/length −0.0533/−0.0461; win −3.75 pp | not run | 8.52M candidate points | rejected on pool | Ally-body deaths rose 1.83% (inside hygiene ceiling), but economy/material/wins fell beyond resolution; no seed 2 or generalisation run. |

ra-08 switch-off parity fingerprint: `params.hpp` SHA-256 `a2c618a9143ef40fc0b2fba98df11d0731047999f3a7b43d3d576417722072d5`; golden replays: 52,728 turns, 1,842 dragons, 0 divergences. Seed-1 pool features are in ignored `build/zoo/ra08/`.

| ra-09 | Raise newborn escape topology-area trigger from 11 to 15 | seed 1/2 combined: economy +0.0110; r100 dragons/length −0.0323/−0.0234; win −2.50 pp | not run | 8.56M candidate points | hold | Self deaths improved 5.14% and wall 1.13%, but the targeted newborn-death rate improved only 2.04%; economy is flat and material fell, so switch is off pending retest on a future accepted economy base. |

ra-09 switch-off parity fingerprint: `params.hpp` SHA-256 `2ef04c8b0dec5991493140a3a0a8480c945363aaa9f95cf8823febcbebf7f11d`; golden replays: 52,728 turns, 1,842 dragons, 0 divergences. Seed-1/2 pool features are in ignored `build/zoo/ra09/` and `build/zoo/ra09-s2/`.

| ra-10 | Raise immediate pearl target value from 10.0 to 12.0 | seed 1/2 combined: economy −0.0093; r100 dragons/length −0.0099/−0.0060; win −2.03 pp | not run | 8.54M candidate points | hold | Self, ally-body, and ally head-to-head rates improved 0.62–1.51% while wall was flat; economy is flat/slightly down, so switch is off pending retest stacked on a future accepted economy change. |

ra-10 switch-off parity fingerprint: `params.hpp` SHA-256 `396d286e9c2d62c0f7c4dcfba096f325dd5595c1d6380a6ac8be42f2c803266f`; golden replays: 52,728 turns, 1,842 dragons, 0 divergences. Seed-1/2 pool features are in ignored `build/zoo/ra10/` and `build/zoo/ra10-s2/`.

| ra-11 | Reduce the general threat-risk budget from 1.0 to 0.70 (switch `Params::monoco_threat_budget`) | seed 1/2 combined: economy +0.0024; r100 dragons −0.0107, length −0.0017; win −1.56 pp | not run | 8.59M candidate points | rejected on pool | Economy gain was far below +0.05 and panel wins declined; all hygiene classes stayed below the +10% ceiling. No generalisation run. Switch remains on in the measured candidate. |

ra-11 switch-off parity fingerprint: `params.hpp` SHA-256 `a929e7562bd4d8a11ce9a2604ddf5fead30d898128092a491c9988705ea18f80`; golden replays: 52,728 turns, 1,842 dragons, 0 divergences. Seed-1/2 pool features are in ignored `build/zoo/ra11/` and `build/zoo/ra11-s2/`.

## ra-12 in progress

| ra-12 | Move the existing growth-value schedule 40 rounds earlier, from round 380 to 340 | seed 1 incomplete: 94/160 index rows; 37 engine failures with `Errno 35` resource-unavailable errors | not run | 8.52M candidate points | pending | Pool execution was interrupted after repeated engine resource errors; no score or gate verdict is available. Candidate switch remains on pending a clean complete pool. |

ra-12 switch-off parity fingerprint: `params.hpp` SHA-256 `c46a19fec51b011c217f2ec322ed8d37a8d388ef586bd112a2ddf5b87fe84416`; golden replays: 52,728 turns, 1,842 dragons, 0 divergences. Candidate pool output is under ignored `build/zoo/ra12/`.
