# tools/sophie — K-1 (what kills us per map; hazard signatures)

Pipeline (run from the repo root; each step resumable and sized for 170 s calls on a small VM):

    python tools/sophie/k1_extract.py --set us     --out build/sophie/x2/us          # team-7 corpus games
    python tools/sophie/k1_extract.py --set field  --out build/sophie/x2/field       # the A2 field sample
    python tools/sophie/k1_extract.py --set local:<dir with replays/> --out build/sophie/x2/local-<name>
    K1_X=build/sophie/x2 K1_AGG=build/sophie/agg2 python tools/sophie/k1_aggregate.py   # sides / deaths / cells parquet
    K1_AGG=build/sophie/agg2 python tools/sophie/k1_cards.py --out game_stats/runs/sophie-trouble-all.json [--us-filter ranked]
    python tools/sophie/k1_residual.py game_stats/runs/sophie-trouble-residual.json        # win-prob residual per map
    python tools/sophie/k1_cells.py                  # per-cell rows (needs build/sophie/maps/<hash>.map, dumped from replays)
    python tools/sophie/k1_hazard_fit.py glm|trees   # Poisson GLM (leave-one-terrain-out) and Poisson trees
    python tools/sophie/k1_signatures.py <sig.json> <ratios.json> <profiles.csv>
    python tools/sophie/k1_extras.py <extras.json>   # gen transfer, where-vs-how decomposition, hot cells
    python tools/sophie/k1_render.py <paragraphs.json>   # markdown card sections
    python tools/sophie/k1_timeline.py <game_id> [step]  # decoded read of one corpus game from team 7's side

Reusable pieces:

    python tools/sophie/hazard.py features <map file>   # per-cell structural features, map scalars
    python tools/sophie/hazard.py profile <map file>    # share of cells per signature + per-class hazard index

The extractor is built on the F1 decoder and reproduces F1's death classes, contexts, pearls, births and
dragon-turns exactly (checked on 200 field games). Kelp lives on edges, so a cell's `deg` is its number of open sides.
