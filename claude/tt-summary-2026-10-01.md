# TT lane summary — 30 Sep to 1 Oct 2026

Branch `r/tt` (worktree `../wt-tt`). Details: `docs/findings/2026-09-30-tt-top-teams.md` (findings),
`claude/tt-status.md` (run log), `docs/findings/2026-09-30-hb1-heartbreaker.md` (HB-1).

## Headline

- **Upload candidate: `hb1-24-portal-small` (3.74 MiB).** It is Ares V06 with three additions:
  - Heartbreaker's direction prior at weight 2.
  - Feeding the crown from about r400.
  - An earlier feeding onset (≈ r300) when the dragon has seen ≥ 5 portal edges per 100 cells on a small map
    (W + H ≤ 56).

  Results:
  - Endgame gate vs hb1-17: **ACCEPT, +2.0 pp [+0.14, +3.84]** over 704 paired fixtures. Portals +8.75 pp, every
    other map game-for-game identical.
  - z1 vs Ares V06 (122–38): **147–13 and 141–19**.
- **Previous best (also uploadable): `hb1-17-prior-lam20`**. z1 144–16 and 139–21, scorecard pass on both seeds.
  The prior-weight sweep: λ 0.5 → 129, 1 → 141, **2 → 144**, 4 → 140.
- Promotion is not recorded in `FRONTIER.md`. That is the user's call.

## What we learned about the top teams

- **The ladder has two map regimes.** Small maps (Trophy, Devil, Queen of Spades, Dilemma, Default, Autarky) end by
  elimination. Large or portal-dense maps (Schooltime, Slithery, Trauma, Portals) go to r500, and the longest dragon
  decides them.
- **Specialists** (residuals against an opponent-strength fit; ranked games; `tools/tt/map_specialists.py`):
  - Heartbreaker and forgot to mention are elimination specialists.
  - Stockfish is a round-limit specialist.
  - Cache me outside is strongest on Trauma and Default.
  - cheji bt (#1) is strong in both regimes.
  - Our team has Stockfish's profile.
- **The top teams' edge is endgame conversion.** All four cull small dragons and feed the long one. Longest dragon at
  r490: 35–46, against Heartbreaker's 13.
- **Memory helps steering, not gates.** Internal-map features add 0.8–2.6 pp of direction accuracy (cheji bt most,
  through exploration); history and momentum add 0.2–1.0 pp.
- **Dummy check.** Cache me outside's unranked bot is a variant, so it uses ranked games only. The other three are the
  same bot in ranked and unranked play.

## Mimics (local only; too big to upload)

| team | mimic | command fidelity | z1 vs V06 | why |
|---|---|---:|---:|---|
| Heartbreaker | hb1-04 | 0.82 | 94–66 (economy +0.21) | swarm without a crown |
| forgot to mention | tt-08 | 0.76 | 91–69 | same |
| Cache me outside | tt-10 | 0.81 | 78–82 (economy +0.24) | same: longest at r490 is 10 vs the real team's 35 |

- **Mimic → Ares hand-offs.**
  - At r250–350 (tt-12..14): the conversion is repaired, but the bots only draw level with V06.
  - At r150 (tt-16/17): below V06. The s1 lane's r150 graft worked for Heartbreaker only.
  - Handing off to hb1-14 instead (tt-15): no gain.
- **Mimic steering as a prior on Ares.** Cache me outside's (tt-11) holds; forgot to mention's (tt-09) fails.
  Heartbreaker's remains the best prior.

## Tools added

- `tools/tt/endgame_gate.py`: gate for changes that act after the opening. It pairs fixtures and reports a win
  difference with a bootstrap CI overall, per regime and per map, plus conversion stats. Verdicts use the tempo gate's
  vocabulary. It is proposed alongside tempo, because the scorecard gate cannot see changes after r250.
- `tools/tt/map_specialists.py`, `map_mechanism.py`, `local_map_table.py`: per-map analysis.
- `tools/tt/make_regime.py`, `make_handoff.py`, `make_handoff_hb.py`, `make_mimic.py`, `make_ramp.py`: bot
  generators.
- `tools/tt/seed_chain.sh`: z1 scorecards by seed.
- `run_panel.py --maps`: runs selected maps only.
- `RUN_PANEL_TIMEOUT`: environment override for slow games.

## Open

1. **Ladder test of hb1-24.** The zoo has no strong converting opponent. Compare Portals games before and after the
   upload.
2. **Mid-game split timing.** The s1 lane found the top ten split 52 % of eligible turns, against our 75–95 %, and
   hold length while food is near.
3. **Map-memory features in C++.** Worth +1–2.6 pp of direction accuracy for any learned steering.
4. **Authenticity tags.** The s1 lane's `authenticity.parquet` could replace the ranked-only filter in the specialist
   fit.
5. **Disk.** `/` filled to 100 % on 1 Oct. `~/Documents/Projects/2026/melee_replays` (512 GB, not this lane) is the
   main consumer.
