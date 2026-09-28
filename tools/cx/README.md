# tools/cx — C1 chassis instruments (unswbc 1.2.2 venv: `~/.venvs/bc122/bin/python`)

Golden-decision harness (two commands):

    python3 tools/cx/golden.py record maps/trauma.map bots/yuna-v03-core bots/fenrir-v18-arrival-ready-beds --side B --seed 1 --gzip
    python3 tools/cx/golden.py replay build/cx/golden/trauma-B-1/yuna-v03-core.jsonl.gz bots/<your-bot> [--all] [--free-sonar|--ignore-sonar]

`record` plays the game through unswbc's own engine and pools (bot unchanged) and stores every dragon's init,
input blocks and replies; `replay` feeds each dragon's inputs to a fresh process of any bot and diffs the
canonical replies (LOG/INDICATOR/DOT/LINE dropped), exit 1 on the first divergence.
Reference transcripts (yuna-v03-core vs fenrir-v18, seed 1): build/cx/golden/{schooltime-A,portals-B,slithery_fight-A,trauma-B}-1/.

Also: `arena.py` (one game: units/length r25–r250, pearls, deaths by cause, sandbox points incl. boot turn),
`bench.py` (map × side × seed fixtures in parallel, `--summary X --vs Y` = paired better/same/worse + sign test),
`meter.py` (sandbox parse/sense/policy/BFS breakdown), `view.py` (ASCII 7×7 view of a recorded turn),
`build_atlas.py` (atlas.hpp from maps/*.map). NB unswbc 1.2.2's sandbox wasm cache hashes only .c/.cpp files;
arena.py purges a bot's cached wasm before every sandbox game so header edits are not silently ignored.
