# serre-v01-foundation

- **Lineage:** Serre (super-lineage; owner brief 2026-09-26: combine the proven
  mechanisms of the strongest existing bots onto one chassis and iterate).
- **Parent:** `build/sinbad/exp/e23` — sinbad-v07-divecap plus the newborn
  body-chain bugfix (a newly split dragon misread its own and other newborns'
  bodies; in one game a 14-long crown died on its first move). Sinbad's
  designated v08 start point. Byte parity manifest: `tools/serre/frozen.json`
  (10 files, zero mismatches).
- **Borrowed:** the entire sinbad mechanics set (arrival-aware bed values,
  threat model, crown/feeding, food sharing by sonar, hunting to length 8,
  strike search, portal-pair sharing, escape split, `v_dive = 3`).
- **Why this foundation:** strongest measured bot in the 64k-game shared
  ledger — rating panel 84.0% established (114 fixtures, 55 opponents), and
  dominant direct head-to-head: 18–6 vs ouroboros-v13, 20–2 vs leviathan-v09,
  17–5 vs tew-v12, 13–11 vs monte_christo-x12, 4–0 vs valjean-v01,
  2–0/2–0/2–2 vs the von_neumann cells (fixture-collapsed native games).
  The e23 bugfix is result-neutral (72–36 vs v07's 70–38 on 108 games) and
  fixes a real kill mechanism.

## Measured (this source)

Baseline records established by the Serre harness runs below; every later
graft arm pairs per-fixture against them (deterministic engine).

| Set | Config | Record |
|---|---|---|
| Dev screen (32) | `configs/serre/screen.toml` | see `docs/serre.md` experiment log |
| Gauntlet (182) | `configs/serre/gauntlet.toml` | see `docs/serre.md` |
| Fresh reserve (16) | `configs/serre/reserve.toml` | see `docs/serre.md` |
| Judge sandbox (4) | `configs/serre/sandbox.toml` | see `docs/serre.md` |

## Inherited known weaknesses (from the sinbad handoff/v07 README)

- devil: enemy swarms take the central fast-bed columns by round 40–50.
- arena: opening economy out-produced ~2× by round 20–30.
- Flipped maps (FX/FY): ~50% vs ouroboros-v13 vs ~75% on originals.
- Round-500 length stalls (valjean measured the same family): material
  plateaus from ~round 120 while top opponents keep growing.

## Roadmap

The graft backlog (ranked, with source-lineage evidence) lives in
`docs/serre.md`. Selection/promotion gates: `tools/serre/selection_rule.json`
(frozen before any outcome was read).
