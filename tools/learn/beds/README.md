# Hidden bed layouts (D-072 §E) — kageyama, 5 Oct 2026

## Engine fact (measured)
Every bed countdown is drawn from one **mt19937_64** stream seeded with the game seed (`index.jsonl` `seed`, hex).
A draw is `lo + (u mod (hi - lo + 1))` for a bed `TILE x y lo hi`. At round -1 the symmetric pairs draw in
row-major order of their first cell (both cells of a pair share the draw); in each round the pairs whose countdown
expires redraw, in the same order. The schedule does not depend on play. A pearl appears at an expiry when the cell
is empty. `emu.py` is a pure-Python copy; `verify_emu.py` checks it against the engine (0 differing cells on 11
maps x 2 seeds, 500 rounds).

## Pipeline
1. `ev_extract.py` (Mac VM, pure Python): per game pearl events + death rounds for the five maps.
   `ev_drop.py`: the same with a per-appearance death-drop flag (body cells of a dragon dying that round); needed on
   Slithery, where dragons die almost every round.
2. `fit.py`: per variant, candidate cells = cells with non-drop appearances in >= 5 % of the variant's games;
   pairs in row-major order; for pair j the first appearance in game g must equal `lo - 1 + u_{g,j} mod span`;
   `fit_rank` scores every (lo, span); hidden pairs show as a break in the index alignment (`fit_free`, `fit_seq`).
3. `classify.py`: every game is scored under the template and the variant list (fraction of non-death pearl
   appearances that fall on an emulated expiry); 1.0 = explained.
4. `mkmaps.py`: writes `maps/live_var/*.map` (the server's visible map lines + fitted TILE lines).
5. `var_oracle.py` / `orun.sh`: engine oracle on server replays with the variant TILE lines; a game is reproduced
   when 0 dragon-turn blocks differ and the engine plays no extra turns.
