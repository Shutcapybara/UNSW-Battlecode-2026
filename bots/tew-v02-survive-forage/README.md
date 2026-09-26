# tew-v02-survive-forage

Lineage: Tew. Parent: `tew-v01-local-forager` for lineage; base remains `examples/bahamut-scaffold/`.

Borrowed: the working survival, pearl economy, split, threat, map, and sonar implementation from `bots/drake-v01-survive-forage/main.py`, adapted unchanged as a strong control. This creates a functional policy with validated movement modeling while preserving Tew's scaffold protocol adapter. No performance transfer is assumed; this version must be measured independently.

Hypothesis: full movement legality, path planning, spawning, and team information will outperform v01's one-step greedy choice.

Implemented layers: map and observations, features including threat/goal fields, exact action simulation and splitting, additive action evaluation, checksummed sonar packets. Strategy parameters are in `main.py`.

Comparison: native, `tew-quick-comparison.toml`, run `experiment_data/tew-v02-survive-forage_*`; results pending.


## Measured results

Native comparison, `experiment_data/tew-v02-survive-forage_20260925042829228788`: interrupted at 14/18 games to bound long big-map runs. Recorded 6–0–8, no runtime faults. It beat v01 6–0 and lost 4 each to `ouroboros-v10-beacon` and `hunter-v20-portal-scouts`; four scheduled big-map reference games remained pending. It is a useful improvement over v01, but not competitive with those references in the completed small-map games. No sandbox checks.
