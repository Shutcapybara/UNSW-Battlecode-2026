# jet-v05-frame-mirror (Jet lineage, Claude)

**Host:** `gavroche-v32-supported-divecap`, unchanged except `protocol.py` (about 20 lines) plus `frame.py` and
`frame_config.py`.

**Idea:** the policy plays each game in a chosen *frame*. The frame is the identity, an x-mirror, a y-mirror or a
180° rotation of the board. Observations are transformed on the way in: tile coordinates and row order, body
coordinates and direction letters, edge rows, and facing. MOVE and SONAR directions are transformed back on the way
out.

**Why it works:** on symmetric live maps, the side at seat A's spawns wins most games (32/48). The cause is the
bots' coordinate-order tie-breaks, not the map or the move order (Jet cycle 22). Seat B is told to play in seat A's
frame (the map's own symmetry), so it plays the mirror image of its seat-A game.

**Frame table:**
- Seat B uses `r` (180°) on 32x32, 32x16, 25x35, 54x18, 48x24 and 63x27, and `fx` on 25x25 and 60x40.
- Seat A is unchanged, and unknown board sizes are unchanged.
- The frame depends only on (W, H, team), so all dragons of a team agree and sonar payloads stay consistent.

**Exactness:** the wrapper is exact.
- A rotated-frame v32 against a rotated-frame v32 on position-swapped maps reproduces v32 vs v32 on the originals.
  The length and unit curves are identical for all 500 rounds on autarky, queen_of_spades and trauma, and the
  x-mirror does the same on trophy.
- In the id frame the bot is exactly v32.

**Result (Jet c23 stage 2):**

| | Score (of 120) |
|---|---|
| jet-v05 (P table) | 99 |
| v32 | 86 |

- The panel was 6 opponents not used for selection (newton-x10, tew-v12, fafnir-v01, scholze-v03, von_neumann-x07,
  ouroboros-v10) × 10 live maps × 2 seats, unswbc 1.0.0.
- Paired: up 16, down 3.
- No map is worse. queen_of_spades 12 vs 7, schooltime 12 vs 9, autarky 11 vs 9.
- In-sample (stage 1, the 6 c20 opponents): seat B 33 vs 24 of 48 on 8 maps.

**Known limits:**
- 32x16 is shared by portals and dilemma (180°) and devil (x-mirror). The table uses `r` for all three, so devil
  seat B keeps v32's result (stage 1: fx 6/6, r 4/6, id 3/6).
- The gain depends on the host's biases. Re-derive the table (tools/jet/frame_table.py) before wrapping another host.

**Activation:** `LOG ACT:frame:<mode>` once per dragon when the frame is not the identity. **Runtime:** a few list
transforms per turn (negligible against v32's budget). Evidence:
`experiment_data/cohort_research_20260927T011500Z_jet/cycle_23_frame_choice/`.
