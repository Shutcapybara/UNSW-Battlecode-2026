# Bot Workflow

## Small Tournament

Start with a bounded dry run so the selected fixture count is clear. This
example compares two current snapshots across the complete recursive map bundle:

```sh
python3 tools/benchmarking/tournament.py \
  --focus-bot hunter-v23-supported-arrival-feed \
  --bots hunter-v23-supported-arrival-feed gavroche-v66-supported-safe \
  --dry-run

python3 tools/benchmarking/tournament.py \
  --focus-bot hunter-v23-supported-arrival-feed \
  --bots hunter-v23-supported-arrival-feed gavroche-v66-supported-safe \
  --no-replays \
  --output build/hunter-v23-focused
```

Use a fresh output directory for each distinct schedule. Add `--maps` when you
want a smaller map set; use `--resume` with the same selections to continue a
saved run.

## Full Tournament

Use an explicit bot pool for normal iteration. This example compares the two
latest documented Hunter and Gavroche snapshots against the same small roster:

```sh
PATH="$PWD/.venv/bin:$PATH" python3 tools/benchmarking/tournament.py \
  --focus-bot hunter-v23-supported-arrival-feed \
  --bots hunter-v14-cpp-hybrid-route-spacing hunter-v20-portal-scouts hunter-v23-supported-arrival-feed \
  --jobs 4 \
  --no-replays \
  --output build/hunter-v23-gauntlet
```

Without `--bots`, the runner selects every bot manifest. A focused run against
that entire historical pool can still exceed 10,000 matches. Use `--dry-run`
to print the count; it only lists individual matches when `--show-schedule` is
also supplied. Schedules over 10,000 require `--allow-large` before execution
or full schedule printing.

Results are saved in `standings.csv` and `results.json` under the selected
output directory. Reuse the same bot and map selections with `--resume`.

## Versioned snapshots and current line tips

Bot directories are frozen, standalone experiment snapshots. Copy a version
before changing its behavior; preserve measured source under its existing
name. A path rename requested by the owner is recorded in that bot's family
notes. Older versions remain useful as controls.

The latest named snapshots below are inventory pointers, not claims about the
deployed bot or promotion status:

| Line | Snapshot | Notes |
| --- | --- | --- |
| Hunter | `hunter-v23-supported-arrival-feed` | Latest Hunter snapshot; see the Hunter results in this document. |
| Gavroche | `gavroche-v66-supported-safe` | Latest numbered Gavroche snapshot. |
| Skadi | `skadi-v13-clear-exit-only` | Latest Skadi snapshot; see [Skadi notes](skadi.md). |
| Zach's Bifröst | `bifrost-v29-tuned-net-growth-farms` | Latest numbered snapshot; the family notes identify V01 as the strongest tested candidate. Separate from Rory's renamed Fenrir line; see [Bifröst notes](bifrost-family.md). |
| Rory's Fenrir | `fenrir-v20-crowded-resource-revalue` | Renamed from Rory's `bifrost-*` snapshots; see [Fenrir notes](fenrir-family.md). |

[`FRONTIER.md`](../FRONTIER.md) is the canonical status page: it tracks active
candidates, frontier status, source-specific estimated ELOs, the comparison
roster, and deployment status.
`docs/strategy-backlog.md` tracks open strategy work; family notes contain
line-specific results.

## Iteration loop (kraken)

`docs/kraken-design-framework.md` defines the method; `tools/kraken/kbench.py` is
the tooling:

```sh
python3 tools/kraken/kbench.py variant kraken-v04-eval kraken-v05-<hypo> --set key=value ...
python3 tools/kraken/kbench.py run screen --bots kraken-v05-<hypo>      # fast kill/keep
python3 tools/kraken/kbench.py run bench  --bots kraken-v05-<hypo>      # sandbox confirm
python3 tools/kraken/kbench.py analyze build/kbench-bench-kraken-v05-<hypo>
python3 tools/kraken/kbench.py compare build/kbench-bench-A build/kbench-bench-B
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

The maintained downloader enforces this identity check directly:

```sh
python3 tools/download_team_games.py "Just Keep Swimming" \
  --submission 8751 --out public_replays
```

`--submission` accepts the exact submission name or numeric submission ID. It
fetches each battle's metadata first, downloads only games where the target
team's submission ID matches exactly, and writes `download_manifest.json` plus
one provenance JSON file beside each replay.

The installed `unswbc` CLI can manage authentication and local replays but has
no command for listing server battles by submission ID or downloading a whole
version's replay set. Use the API for exact submission/game metadata and the
public pagination for history beyond the API's 200-battle window.
