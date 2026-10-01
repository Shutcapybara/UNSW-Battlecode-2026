# Monoco `ra` lane — checkpoint after version 10

Base: Ares V06, atlas off. Every candidate is a standalone `bots/ra-NN-*` copy with its own `CANDIDATE.toml`; its switch-off copy is golden-replayed against four V06 transcripts before testing. The fixed z1 pool uses eight opponents, ten live maps, both seats, and fixed field median references. CPU uses four dense sandbox fixtures. The interim per-turn ceiling is 30M until R-1 publishes its wall.

| Version | Mechanism | Pool economy delta | r100 dragons / length | Pool win delta | Candidate CPU max | Verdict |
|---|---|---:|---:|---:|---:|---|
| ra-01 | Trap penalty 30 → 60 | −0.0838 | −0.0504 / −0.0507 | −4.37 pp | 8.72M | reject; wall hygiene −14.36% did not offset economy/material loss |
| ra-02 | Child-room minimum 4 → 8 | −0.0139 (seeds 1+2) | −0.0143 / −0.0144 | flat | 8.72M | reject; below +0.05 gate and material guards fell |
| ra-03 | Sprint action cost 1.0 → 1.5 | +0.0209 (seeds 1+2) | +0.0233 / +0.0233 | +0.31 pp | 8.66M | reject; sprint cost improved, but economy missed +0.05 |
| ra-04 | `pearl_ttl` 40 → 60 | 0.0000 | 0 / 0 | 0.00 pp | 8.45M | reject; changed parameter has no active call site |
| ra-05 | Active memory TTL 40 → 60 | +0.0024 (seeds 1+2) | +0.0001 / −0.0022 | 0.00 pp | 8.86M | hold; slight hygiene gains, switch off for retest on a future accepted economy base |
| ra-06 | Target hysteresis 1.25 → 1.75 | −0.0435 | −0.0586 / −0.0509 | −2.50 pp | 8.56M | reject; hygiene fell 2–3% but economy/material/wins regressed |
| ra-07 | Ally-density weight 0.10 → 0.50 | −0.0169 (seeds 1+2) | −0.0156 / −0.0059 | −0.94 pp | 8.81M | reject; targeted ally head-to-head death reduction was 2.11%, below its 10% prediction |
| ra-08 | Reachable-bed value 8.0 → 10.0 | −0.0327 | −0.0533 / −0.0461 | −3.75 pp | 8.52M | reject; economy/material/wins fell beyond resolution |
| ra-09 | Newborn escape area threshold 11 → 15 | +0.0110 (seeds 1+2) | −0.0323 / −0.0234 | −2.50 pp | 8.56M | hold; self/wall deaths improved 5.14%/1.13%, but newborn deaths improved only 2.04%; switch off |
| ra-10 | Immediate pearl value 10.0 → 12.0 | −0.0093 (seeds 1+2) | −0.0099 / −0.0060 | −2.03 pp | 8.54M | hold; small hygiene gains with flat/slightly lower economy; switch off |

## What the lane has learned

No version passed the economy gate, so the accepted stack adds nothing to V06: the combined change against base is zero on both panels. No candidate qualified for generalisation or registration. Every switch-off golden check matched all four fixtures with zero divergent decisions, and every candidate CPU maximum stayed below 30M.

Three mechanisms produced small hygiene-only signals: longer active memory (ra-05), a broader newborn escape trigger (ra-09), and higher immediate pearl priority (ra-10). Those switches are off pending an accepted economy base to stack them on. Trap weighting, a larger child-room gate, sprint-cost inflation, stronger target hysteresis, ally-density spreading, and higher bed value either regressed the economy/material curve or failed to move their intended statistic enough. The next useful exploration should prioritize a direct economy improvement; the retained-material gap remains the central open deficit.

Full per-version status is in `claude/ra-status.md`. Completed fixture indices, replay payloads, and feature tables are retained locally under ignored `build/zoo/raNN*`; the reproducible outcome summaries are published as run contributions under `game_stats/runs/`.
