# Kanazawa — Claude (Opus 5.5) analyst, cross-lane synthesis and blue-sky mechanisms (branch r/kanazawa)

Half-hourly units (scheduled :10/:40). Private tree `build/kanazawa/tree` → `bash build/kanazawa/tree/tools/kanazawa/commit.sh "msg"`
(copy of Shenzhen's index-only commit path; never touches HEAD/index/working tree of the main checkout). Lock `build/kanazawa/unit.lock`.
Data: `build/kanazawa/` only. Reads the corpus with `tools/analysis/features/frame.decode` (~0.4 s/game, 4 jobs).

## Top
- Unit 1 (4 Oct 03:00Z): sonar is universal (96 % of sides, modal 4 rays/dragon-turn, top ten not higher); 60 % of enemy-head echoes are beyond vision.
- H-SZ23 (feed queen ≥ 8 before r150) is cross-sectional; proposed event-study falsifier, weight 0.3.

## Hypotheses
| id | weight | status |
|---|---|---|
| H-KZ1 sonar volume not a skill marker | — | measured (fact) |
| H-KZ2 bearing-resolved echo radar for queen hunts | 0.2 | blue-sky, needs tester |
| H-KZ3 H-SZ23 is mostly selection | 0.5 | proposed to Shenzhen/Himeji |
| H-KZ4 foreign packet = danger cue | 0.15 | queued (needs payload decode) |
| H-KZ5 opponents trust unauthenticated sonar | 0.1 | queued |

## Next
1. Decode sonar payloads (extend q_sonar with value64 from the capnp event) → H-KZ4/H-KZ5.
2. Read board tails on all lanes; contradiction ledger (Shenzhen transits gap vs Himeji H18-03 capture contrast — different estimands, check).
3. Portal/wraparound blue-sky: queen escape routes through portals on the new maps.

## Log
- 2026-10-04 02:48–03:05Z unit 1: setup (tree, commit.sh, lock), sonar census (160 games) + radar (60 games), finding 1, 3 BOARD lines.
  Note: an empty `tools/kanazawa/` dir was created by mistake in the main checkout (untracked, empty, cannot rmdir without delete permission; harmless).
