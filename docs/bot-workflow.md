# Bot Workflow

## Quick Tournament

```sh
PATH="$PWD/.venv/bin:$PATH" python3 bots/tournament.py \
  --focus-bot <bot> \
  --jobs 8 \
  --no-replays \
  --maps arena schooltime small \
  --output build/<bot>-quick
```

Use this for rapid development and direct strategy comparisons.

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
