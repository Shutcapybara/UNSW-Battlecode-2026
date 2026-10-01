# antioch — P2-A Claude analyst, replay lead (from 1 Oct 2026)

Worktree `../wt-antioch` (desktop), branch `r/antioch`, tools `tools/antioch/`, findings `docs/findings/<date>-antioch-*.md`.
Data: the corpus and the S-1 store are rsynced from the Mac into this worktree (`public_replays/corpus/`, `build/s1/`);
from now on the desktop copy of the store is the one I build. Never call the API; the hub collector stays on the Mac.

## Handoff — session wrap-up (2026-10-01 21:00 UTC)

**Delivered (all on `r/antioch`; findings in `docs/findings/2026-10-0{1,2}-antioch-*.md`):**
1. **Era:** the switch is 05:57:53Z → 09:26:58Z, and `games.era` is in the store. The live map pool changed too.
2. **Queen:**
   - semantics: the original lowest-id dragon, no succession, keeps the head on a split;
   - field survival in round-limit games 2.2 % (top ten 0.7 %);
   - three pocket maps kill it by design;
   - where one queen survives a round-limit game, its side won 36/36.
3. **Decoder bug:** `frame.py` uses the old tiebreak. The patch is validated 300/300 against server winners:
   `tools/antioch/patches/frame-engine-verdict.patch`. The director should apply it on main.
4. **Store:** 2,862 post-change in-scope games decoded. `S1_ERA` in `q.py` and `build.py corpus --era` added. **Synced
   to the Mac** (`build/s1/corpus`, additive; the lead authorised re-syncs after each build).
5. **Targets** (`docs/hub/TARGETS.md` § antioch):
   - endgame and queen columns;
   - post-change opening references: the field did not move; stable to ±4–5 %; top-ten − us now led by transits 0.56 SD;
   - win potential Φ: LOMO AUC r50 0.86 (elimination maps) / 0.63 (round-limit maps), calibrated; tempo-form 0.64.
     Coefficients in `tools/antioch/phi_post_v1.json`.
6. **Readings:**
   - carthage-06: gen round-limit fixtures +0.107 [+0.042, +0.175];
   - carthage-02: elimination losses 168 → 320;
   - carthage-04/05: reproduce exactly; the gain is longest races on round-limit fixtures;
   - gate answer: win-led with guards, under which 04+05 accepts.
7. **Hypotheses posted:** H-Q1/2/4/5/6/7/8 (queen), H-S1/2/3 (portal memory, scouts, queen-directed latent states;
   portal danger 57 % vs 19 %; rays cross portals), H-V1 (Φ), H-RL1–5 (learned track; the engine runs in-process at
   ~10 k decisions/s/core; GBT expert iteration first).
8. **RL readiness:** groundwork now (G1 env, G2 encoder parity, G3 GBT per-KB). Training after four entry conditions;
   see `2026-10-02-antioch-rl-readiness.md`.

**Open, for the next session (in order):**
1. Read the board since 20:50 UTC; answer the director's rulings on the gate rule and the frame patch.
2. Re-sync the corpus from the Mac, then `build.py games && build.py corpus --era post`, then re-sync the store to the
   Mac.
3. H-V1: does ΔΦ@100 rank carthage's arms' win Δ better than tempo / economy? This needs local stores per arm.
4. Refit Φ and the queen tables once the missing top-ten teams appear (collector request open).
5. Readings of carthage-08/09 and kyoto-02/03 as they land.

**Environment:**
- Every desktop venv is on unswbc 1.2.3, the latest (the parent `.venv` was upgraded from 1.2.2 on the lead's say-so).
- `duckdb` lives in `build/s1-pylib` (PYTHONPATH, or `q.py` adds it).
- Push by SSH URL: `git push git@github.com:Shutcapybara/UNSW-Battlecode-2026.git r/antioch`.

## Top — read this first (updated 2026-10-01 22:20 ACST)

- **Era switch:** the live server adopted 1.2.3 between **05:57:53Z** (last old-rule game) and **09:26:58Z** (first
  new-rule game) on 1 Oct; there are no games in between. Era rule: `post` ⇔ `started_at ≥ 2026-10-01T06:00Z`. Evidence:
  sprint pricing on 1,804 games (0 mixed; every priced sprint before is k−1, every one after is max(0, k−⌈L/4⌉)), and the
  queen field is non-zero only after. Tagged in the store: `games.era`; `S1_ERA=pre|post` scopes the views and norms.
- **The queen** is the team's *original* lowest-id dragon. The engine's 4th `TeamStanding` int32 equals its length and
  reads 0 once it has died; there is no succession. On a split the parent keeps the id **and the head end**
  (12,039/12,039 splits), so the queen survives splitting but keeps only the head piece.
- **Gate win share is computed with the old tiebreak.** `frame.decode` infers the winner as longest → total
  (`frame.py:224-233`); the scorecard's win share (`scorecard.py:141` via `extract.py:411`) inherits it. The fix (read the
  engine's own verdict and the queen field) is in `tools/antioch/patches/frame-engine-verdict.patch`, for the director to
  apply. FRAME_VERSION goes 5 → 6. Validated: the patched decoder matches the server's recorded winner on 300/300
  sampled corpus games (135 pre, 165 post, incl. 2 queen-decided).

- **Queen value:** where exactly one queen survives a round-limit game it won 36/36, 26 of those from behind on total.
  RL queen survival: field 2.2 %, top ten 0.7 %. Pocket maps (Slithery, Autarky, PD) kill every queen on r4–5.
- **Corpus gaps:** five of the top ten have no post-change games; no ladder snapshot since 06:21Z (requests on the board).
- **RL readiness:** groundwork now, training after four entry conditions (finding `2026-10-02-antioch-rl-readiness.md`).
- **Next unit:** carthage-04/05 engine-verdict reading (extraction running); H-V1 (does ΔΦ rank arms' win Δ); store sync to
  the Mac (needs the lead's permission); refit Φ and the queen tables when the collector adds the missing top-ten teams.

## Hosts

Only the Claude instances (carthage, antioch) are on the desktop with the 4090. GPT/GLM instances (himeji, nara, kyoto,
rome) are on the Mac and get no GPU-heavy items (lead, 2 Oct).

## Live hypotheses

| id | claim | status | falsifier | size | suits |
|---|---|---|---|---|---|
| H-Q1 | queen preservation from r0 raises RL win ≥ 10 pp at ≤ 0.02 economy | posted 1 Oct, proposed ledger 0.7 | queen alive r490 on pool < 0.5, or RL win Δ LB ≤ 0 | pool + gen, seeds 1–3 | Claude tester |
| H-Q2 | feed the queen late (TT's cull-into-the-long-one, keyed on the queen) | posted, after H-Q1 | both-alive RL win ≤ 0.5 vs queen-keepers | ~200 games mirror | after H-Q1 |
| H-Q3 | pocket escape by splitting | **falsified** 1 Oct (engine probe) | — | — | — |
| H-Q5 | queen-local enemy density penalty + ally escort (lead's idea) | posted 23:10; hazard 5 / 34 / 76 per 1k at 0 / 1 / 2+ enemy heads within 3 | survival not above H-Q1 arm, or econ LB < −0.02 | stacked on H-Q1 | any tester |
| H-Q6 | timestamped queen sightings over sonar (lead's idea) | posted 23:10; enemy queen seen 25 % of rounds, median gap 5 | no gain over H-Q1/H-Q5 noise | as H-Q1 | after H-Q5 |
| H-Q7 | queen-state swarm modes (turtle / hunt / longest race / queen race), with a sonar heartbeat so the swarm knows (lead's idea) | posted 23:25; 71 % of side-rounds are played queenless, median 294 rounds left | mode-switch arm not > constant policy vs an H-Q1 opponent (RL win LB > 0) | pool + gen, seeds 1–3 vs an H-Q1 mimic | after H-Q1 + H-Q6 |
| H-Q8 | queen feature block for every eval / learned model (lead's request) | posted 16:10 UTC | GBT ± block: no held-out gain on queen turns, no queen alive change | offline + 1 panel | any; verso/hb1 lineage owners |
| H-RL1–4 | learned-policy track: engine-in-process env → BC → PPO self-play league → int8 net as prior/value (lead's request) | posted 16:10 UTC; env measured ~10 k decisions/s/core, proposed 0.6 | per row in the finding §4 | — | **Claude lanes only (GPU on the desktop)**; director to staff |
| H-RL5 | expert iteration with GBTs (search → GBT imitates search → next prior) | posted 17:20 UTC; GBT > MLP on all five HB-1 decisions | iteration 2 not > iteration 1 | CPU-heavy self-play | Claude/desktop lane or scheduled Mac CPU |
| H-V1 | win potential Φ as the gate's early guard and the RL shaping signal (lead's request) | posted 18:10 UTC; LOMO AUC r50 0.86 elim / 0.63 RL, tempo-form 0.64 | ΔΦ@100 does not rank arms' win Δ better than tempo/econ | offline on existing panels | analyst (me) next; any tester |
| H-S1 | portal memory: skip pairs whose last own transit died (57 % vs 19 % die3) | posted 19:10 UTC | died3 not −25 %, or econ LB < −0.02 | pool + gen s1–3 | any tester |
| H-S2 | scout-and-return; queen never transits unscouted pairs (lead's idea) | posted 19:10 UTC; rays cross portals | not < H-S1 alone on died3, or no queen gain | after H-S1, H-Q1 | Claude tester |
| H-S3 | latent-state swarm directed by the queen (lead's idea; L31/L32/L33 concrete) | posted 19:10 UTC | stacked arm not > best single queen arm | 2–3 arms, after H-Q1 | Claude tester; H-RL5 later |
| H-Q4 | hunt the enemy queen once the field keeps queens | watch, 0.3 | field RL queen survival < 10 % for a week | corpus watch | — |

## Store maintenance (replay lead)

- `tools/s1/build.py`: `ERA_SWITCH`, `games.era`, `corpus --era pre|post`.
- `tools/s1/q.py`: `S1_ERA` scopes `c_sides` (and everything built on it) and the norms. Norms are cached as
  `norm_series_<era>.parquet`. Unset keeps the old pooled behaviour; it was tested unset and returns the same games.
- Sync from the Mac: `rsync -a alik@192.168.0.86:/Users/alik/Documents/Projects/UNSW-Battlecode-2026/public_replays/corpus/{index.jsonl,ladder,teams.json} public_replays/corpus/`,
  then `replays/`. Build with `nice -n 15 … build.py games && build.py corpus --era post --jobs 6`. The desktop is
  shared with the testers: stay at ≤ 6 jobs, niced.

## Log

- 2026-10-01 22:20 — launched. Era established, store tagged, queen semantics, decoder bug found.
- 2026-10-01 22:45 — unit 1 posted: finding, TARGETS endgame columns, 7 board lines, CORPUS.md, frame patch. H-Q3
  closed. Opening references pending the build.
- 2026-10-01 23:10 — H-Q5 (density) and H-Q6 (sonar sightings) posted from the lead's suggestions, with hazard and visibility numbers.
- 2026-10-01 23:25 — H-Q7 (queen-state swarm modes) posted from the lead's suggestion.
- 2026-10-02 (UTC 16:10 1 Oct) — H-Q8 and H-RL1–4 posted (lead's request); board time convention switched to UTC. Unit 2 in progress: post store decode, 06 paired reading, opening refs.
- 2026-10-02 (18:10 UTC 1 Oct) — post store decode done (2,862 post games). Φ win potential fitted and posted. The store sync to the Mac was **blocked by the permission classifier** (writing the Mac's shared build/s1); left for the lead.
- 2026-10-01 19:40 UTC — readings: carthage-06 (gen RL-fixture +0.107 [+0.042, +0.175], elimination −0.012), carthage-02 (elimination losses 168 → 320). Gate answer posted: win-led for endgame mechanisms with econ/tier-2/ΔΦ guards; 04+05 would accept.
- 2026-10-01 20:10 UTC — opening refs published (field unchanged; transits now the largest gap); RL-readiness decision note.
- 2026-10-01 20:40 UTC — carthage-04/05 reading: reproduces exactly; gain is round-limit longest races (05 pool +0.103, gen +0.068 on RL fixtures), no queen effect. Candidate under the win-led rule.
- 2026-10-01 21:00 UTC — session wrap-up: handoff section added; desktop venvs all on 1.2.3.
