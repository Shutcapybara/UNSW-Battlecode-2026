# Bot Workflow

## Small Tournament

```sh
PATH="$PWD/.venv/bin:$PATH" python3 bots/tournament.py \
  --focus-bot <most-recent-bot> \
  --bots <third-most-recent-bot> <second-most-recent-bot> <most-recent-bot> \
  --jobs 8 \
  --no-replays \
  --output build/<most-recent-bot>-small
```

For rapid development, run two tournaments using the three most recent
versions as the shared pool. First focus the most recent version, then focus
the second most recent version. This tests both candidates against each other
and the third-most-recent version on every map and with both side assignments.
Use a fresh output directory for each run. For example, with hunter-v02,
hunter-v03, and hunter-v04:

```sh
PATH="$PWD/.venv/bin:$PATH" python3 bots/tournament.py \
  --focus-bot hunter-v04-team-state-sonar \
  --bots hunter-v02-team-growth hunter-v03-team-growth hunter-v04-team-state-sonar \
  --jobs 8 \
  --no-replays \
  --output build/hunter-v04-small

PATH="$PWD/.venv/bin:$PATH" python3 bots/tournament.py \
  --focus-bot hunter-v03-team-growth \
  --bots hunter-v02-team-growth hunter-v03-team-growth hunter-v04-team-state-sonar \
  --jobs 8 \
  --no-replays \
  --output build/hunter-v03-small
```

The third-most-recent version is included mainly as a tiebreaker and baseline;
the primary comparison is between the two focused versions.

## Full Tournament

```sh
PATH="$PWD/.venv/bin:$PATH" python3 bots/tournament.py \
  --focus-bot <bot> \
  --jobs 8 \
  --no-replays \
  --output build/<bot>-full
```

Use this for extensive testing across every bundled map and bot.

Results are saved in `standings.csv` and `results.json` under the selected output directory.

## Versioning

Use flat, zero-padded names so versions sort naturally:

```text
fry-v01-<strategy>
fry-v02-<strategy>
...
fry-v14-<strategy>
hunter-v01-<strategy>
```

The `fry` lineage contains the existing strategy snapshots. The `hunter`
lineage is for new experimental architecture built from the fry snapshots.
Never rename or modify an older version when creating a new experiment; copy
it into the next version first. Every new version must also be added to this
lineage table and to `docs/strategy-backlog.md`.

Current strategy lineage:

| Version | Strategy |
| --- | --- |
| `fry-v01-danger-levels` | danger-level reproduction |
| `fry-v02-dragon-hunters` | aggressive dragon hunting |
| `fry-v03-portal-hunters` | portal pearl trips |
| `fry-v04` through `fry-v10` | strategy variants and pearl seekers |
| `fry-v11-size-aware-hunters` | size-aware attacks |
| `fry-v12-stateful-size-aware-hunters` | persistent map, pearl, and enemy memory |
| `fry-v13-stateful-size-aware-2` | sonar pearl claims |
| `fry-v14-stateful-size-aware-3` | closest-teammate pearl ownership |
| `hunter-v01-team-growth` | team-length estimates and endgame growth |
| `hunter-v02-team-growth` | adaptive growth timing for the largest teammate |
| `hunter-v03-team-growth` | safe unmatched-portal exploration by smaller dragons |
| `hunter-v21-emergency-portals` | V20 plus a last-resort portal crossing when ordinary exits are blocked; experimental, 10W/12L vs V20 |
| `hunter-v22-frontier-exploration` | V21 with frontier-first exploration and multiple shortage-based portal scouts; 9W/13L vs V21 on all maps, no errors |
| `hunter-v23-supported-arrival-feed` | V22 with radius-four supported hunts, arrival-time bed targets, Estuary regional bias, and guarded late crown feeding; native focus gauntlet 71W/137L overall, 15W/11L vs V22, not promoted |
| `kraken-v01-roles` | role-based scouts, hunters, and gatherers with sonar gossip |
| `kraken-v02-bigmap` | big-map production, brawl mode, and judge-safe metered search |
| `kraken-v03-judge-safe` | snapshot of kraken-v02 after sandbox CPU hardening |
| `kraken-v04-eval` | v03 with kbench-parameterised CFG; eval-function baseline (identical behavior) |
| `gavroche-v01-mass-preserving-opening` | Monte Christo x12 with an early rescue split for long, partially observed spawns |
| `gavroche-v02-opening-production` | v01 plus early two-segment production; 13–3 in separate screens and 12–4 in one full-pool schedule |
| `gavroche-v03-head-preserving-opening` | v02 with head-preserving rescue and more aggressive production; rejected |
| `gavroche-v04-mobile-mass-rescue` | v02 with a one-shot initial-spawn rescue; rejected after Autarky regression |
| `gavroche-v05-map-aware-rescue` | v02 with map-aware rescue splitting; rejected after losing an Autarky side to x12 |
| `gavroche-v06-first-move-rescue` | v02 with one-shot rescue for initial dragons; 4–4 vs x12 and Hunter v20 |
| `gavroche-v07-paced-rescue` | v02 with at most one rescue split per dragon per round; 5–3 vs x12 and Hunter v20 |
| `gavroche-v08-map-aware-opening` | v02 cascade on larger maps and paced rescue on compact maps; 11–5 across four references |
| `gavroche-v09-two-stage-rescue` | v07 with one follow-up rescue; 10–6 across four references |
| `gavroche-v10-balanced-rescue` | v02 with a balanced initial split; separate screens 12–4, later full-pool snapshot scored 10–6 |
| `gavroche-v11-tail-mass-rescue` | v10 with a four-segment head and larger tail piece; 4–4 vs x12 and Hunter v20 |
| `gavroche-v12-balanced-opening` | v10 snapshot; 10–6 in the full-pool screen, x12 won both Autarky games |
| `gavroche-v13-tail-paced-rescue` | v09-style `L-2` rescue with one movement opportunity between splits; historical baseline, 12–4 in the full pool, swept x12 4–0 |
| `gavroche-v14-four-segment-head` | v13 with a larger original head; 9–7 in the full pool, x12 won both Autarky games |
| `gavroche-v15-divecap` | v13 with Sinbad v07's lower unpaired-portal value; 100–82 on the native cross-family panel |
| `gavroche-v16-informed-divecap` | v15 plus full-strength early room-normalised density gradient; 111–71 on the native cross-family panel |
| `gavroche-v17-half-gradient` | v16 with half-strength early density gradient; 84–46 against five selected model-family references, current broad-opponent candidate; native, not judge CPU-validated |
| `gavroche-v18-fused-room-flood` | v17 with one flood-fill reused for trap and room-gradient scoring; Big Empty sandbox mirror passed but still reached 99.5M CPU points |
| `gavroche-v19-spatial-density` | v18 with exact toroidal buckets for density reports; 488,520 full-grid equivalence checks passed, but Big Empty still peaked at 99.1M |
| `gavroche-v20-bounded-feeding` | v19 with a short-donor, delayed explicit crown-feeding experiment; superseded by v22 for CPU-safe testing |
| `gavroche-v21-short-sprint-cap` | v19 with all three-step candidate paths disabled; Big Empty sandbox max 93.1M, p99 72.1M, zero timeouts/invalid actions; rejected after an early 46-game screen lost all four Big Empty, Autarky and Queen games vs v13/v15 |
| `gavroche-v22-bounded-feeding` | v21 plus delayed crown donations from visible, longer crowns to donors of length ≤10; prototype, not screened |
| `gavroche-v23-selective-sprint-cap` | v19 with three-step candidates retained for lengths 4–7; Big Empty max 94.7M, six-map panel 46–38; loses to v17 4–8 and trails it 34–14 across the top four families |
| `gavroche-v24-selective-feed` | guarded late feeding on v23; Big Empty max 97.3M, early screen 4–8 vs v23; rejected |
| `gavroche-v25-crown-margin-one` | v23 with crown margin 1; stopped at 54/96, 21–32–1; rejected |
| `gavroche-v26-sprint-cap10` | v19 retaining triples only through length 9; Big Empty max 99.3M, insufficient CPU margin |
| `gavroche-v27-sprint-cap9` | v19 retaining triples only through length 8; Big Empty max 99.0M/99.5M, insufficient margin |
| `gavroche-v28-gradient-window-sprint-cap` | intended early density-window cap, but guard never activated because `info_aggro_push=0`; panel stopped at 28/96 |
| `gavroche-v29-saturation-window-sprint-cap` | v19 with cap during early saturation; Big Empty max 99.4M, panel 40–56; rejected |
| `gavroche-v30-saturated-sprint-cap` | v17 with cap throughout ≥70% saturation; Big Empty max 99.8M, panel 54–42; rejected |
| `gavroche-v31-saturated-divecap` | v30 plus `v_dive=3`; panel 55–41, equal to v23 29–19 against top four families; not promoted |
| `gavroche-v32-supported-divecap` | v31 plus x04-style supported trade bonus; panel paused at 43/96, partial 23–20; resume note: `docs/gavroche-resume-2026-09-26.md` |
| `hydra-v01-core` | python from-scratch swarm with sonar gossip map |
| `hydra-v02-hunters` | python pack hunting (beats fry-v03 17-9) |
| `hydra-v03-grower` | python swarm-of-equals + late split freeze |
| `hydra-v06-echo` | hunter-v03 forked to protocol 3: status radio, enemy gossip, echo radar |
| `hydra-v07-farm-first` | v06 + gossip chase gated on units>=6 && length>=4 (not promoted) |
| `hydra-v08-claims` | v07 + whole-swarm r400 farm switch + owns_pearl growth BFS (not promoted) |
| `hydra-v09-lanchester` | v08 + retreat-while-outnumbered evasion (not promoted) |
| `hydra-v10-farmclean` | v08 minus stalker-flee in farm mode (not promoted; field 150 vs v06 159) |
| `loki-v01-teacher-ranker` | Bifröst v01 fork with an exported gradient-boosted candidate ranker trained on ranked submission #7771 replays; action-imitation holdouts recorded, game-benchmarked status pending |

## Iteration loop (kraken)

`docs/kraken-design-framework.md` defines the method; `bots/kbench.py` is
the tooling:

```sh
python3 bots/kbench.py variant kraken-v04-eval kraken-v05-<hypo> --set key=value ...
python3 bots/kbench.py run screen --bots kraken-v05-<hypo>      # fast kill/keep
python3 bots/kbench.py run bench  --bots kraken-v05-<hypo>      # sandbox confirm
python3 bots/kbench.py analyze build/kbench-bench-kraken-v05-<hypo>
python3 bots/kbench.py compare build/kbench-bench-A build/kbench-bench-B
```

Long runs go through `nohup`; screen is non-sandbox (fast), bench and pool
are sandboxed (judge-true). One hypothesis per variant; see the framework
doc for the full rules.

## Retrieve server battles and replays for a submission version

Use the submission ID as the identity of a version. The active version can
change, so do not infer which version played a battle from the team's current
active submission or from the battle's date alone.

1. Confirm that the local `unswbc` credentials belong to the intended team with
   `./.venv/bin/unswbc auth status`. Use the credential already stored by
   `unswbc` (under `~/.unswbc/keys.json` for this setup); never print, log,
   commit, or paste the key.
2. Call `GET https://game.battlecode.au/api/v1/submissions` with
   `Authorization: Bearer <team-key>`. Find the exact submission name and
   record its numeric ID and upload time. The API returns all versions and
   their W/D/L totals. The official endpoint reference is
   [Battlecode API docs](https://game.battlecode.au/docs/api).
3. Enumerate the team's battles. `GET /battles?limit=200` returns newest first
   and is capped at 200. In current testing, `offset` and `page` query
   parameters did not advance this API result. For older battles, use the
   public site's paginated battle list:
   `https://game.battlecode.au/battles?teams=<team-id>&page=<page-number>`.
   The page size was 10 in the 2026-09-27 check. For Just Keep Swimming, the
   team ID is `7`, so page 2 is
   `https://game.battlecode.au/battles?teams=7&page=2`. Read the site's page
   count each time; it can grow. The public list has no submission-version
   filter, so collect its battle IDs across every page and deduplicate them.
4. For each candidate, call `GET /battles/<battle-id>` and inspect the games
   and both teams' submission IDs. Keep a game only when Just Keep Swimming's
   submission ID exactly equals the target ID. This is the reliable version
   match. Skip queued or unfinished games; the replay is available only after
   a game finishes. Compare the matched games' outcomes with the submission's
   W/D/L totals as a completeness check, allowing for totals to update while
   battles are still running.
5. For each finished game with a replay, download
   `GET /battles/<game-id>/replay` and save it as
   `replay/<submission-name>/<game-id>.replay`. The replay endpoint redirects
   to a temporary signed URL. The team key must not be forwarded to that URL;
   the official API docs note that `curl -L` strips the header when following
   the cross-host redirect, while Python's `urllib` does not. For another HTTP
   client, explicitly suppress the `Authorization` header after redirects.
   Keep requests below the API limit of 120 per minute and honor `Retry-After`
   on HTTP 429. Root `.gitignore` ignores `*.replay` files.

The installed `unswbc` CLI can manage authentication and local replays but has
no command for listing server battles by submission ID or downloading a whole
version's replay set. Use the API for exact submission/game metadata and the
public pagination for history beyond the API's 200-battle window.
