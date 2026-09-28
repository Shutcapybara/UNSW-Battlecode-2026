# tools/yeji — the Yeji adapt / test / benchmark loop

Claude's harness for the Yeji bots (`bots/yeji-*`). Needs unswbc **1.2.2** (for `--seed`; install in a scratch venv:
`python3 -m venv ~/.venvs/bc122 && ~/.venvs/bc122/bin/pip install unswbc==1.2.2 pycapnp`) — never replace the 1.0.0
binary the live gate uses. Set `UNSWBC=/path/to/unswbc` to use another toolkit; the version is recorded on every row.

```sh
# a paired panel: candidates (or variants NAME@key=value,...) vs a pool, both sides, seeded
python3 tools/yeji/yrun.py run --cands yeji-s03-compactfield "yeji-s03-compactfield@w_field=0.0" \
    --pool yuna-v02-core sinbad-v07-divecap ... --maps live10 --seeds 1,2,3 --jobs 2 --out runs/NAME [--sandbox] [--keep losses]

# paired report (by map, side, seed, opponent): score, delta, pairs better/worse, sign test, per map/opponent
python3 tools/yeji/yrun.py report runs/A runs/B --control CONTROL_LABEL [--detail]

# contract statistics medians (ours|theirs), compact/open split, ACT counts, conversion funnel
python3 tools/yeji/yrun.py stats runs/A runs/B

# one replay: contract statistics (units/longest at r100/250/400/499, deaths, births, newborn deaths, ACT tags, funnel)
python3 tools/yeji/ystats.py REPLAY

# metered probe: CPU max/p99/p50 from `unswbc run --sandbox -v` output + activation contract from CANDIDATE.toml
python3 tools/yeji/meter.py LOG REPLAY TEAM bots/NAME

# crown lifecycle (who logged ACT:crown, when, max length, how it ended)
python3 tools/yeji/crowns.py REPLAY TEAM

# public-map prior for a bot (terrain, portals, fast beds, bed field), CPU-cheap constant form
python3 tools/yeji/build_prior.py --compact bots/NAME/mapprior.py
```

Variants copy the bot into `RUN/build/variants/` at the start of a run and rewrite `params.py` (keys must already
exist), so editing the source bot during a run does not leak into it. Runs resume (same `--out`) and retry errored
games. The live-pool panel is 10 maps × 2 sides × seeds × pool; 160 games per arm at one seed take ≈ 70–90 minutes on
two cores (Slithery Fight and Schooltime dominate).

The loop: observe (report / stats / ystats / deaths.py / crowns.py) → state one mechanism → add it as an option,
feature or parameter with a neutral default → screen on the maps where it should act → full panel paired against the
parent → metered probes (Schooltime as A, Portals as B vs sinbad-v07-divecap) → freeze a new version directory.

## Held-out panel (the selection instrument from s06 on)

Tournament maps are out of sample, so selection uses maps no Yeji version was tuned on: `tools/yeji/HOLDOUT_MAPS`
(ten synthetic maps from `maps/new/`). `--maps $(cat tools/yeji/HOLDOUT_MAPS)`. Live-map panels are in-sample
evidence only. Variants of gavroche/yuna-style bots (params.py `P` + override.py) are written as an appended
`OVERRIDE.update({...})`.
