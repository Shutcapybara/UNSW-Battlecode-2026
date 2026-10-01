# Benchmark candidates, 1 Oct: 20 local bots to test your iterations against

Selection by s1 (Claude), from the overnight fixed panel: 20,243 games, 247 bots, seed 1, 10 ladder maps,
6 opponents × 2 seats. The list is chosen for **strength and diversity**: the strongest band, one or two per family,
plus style slots that cover niches the strong band does not. It is a gauntlet, not a ranking.

**Read the numbers as bands.**

- Panel strength has an SE of about ±35 for 120 games and about ±50 for 60 games.
- Rankings split by map agree only moderately (rank correlation 0.46 between halves of the maps).
- Within the top band most neighbours are ties.

## The list

Column key:

- **panel** = Bradley–Terry rating on the panel.
- **tempo** = rounds behind the top-ten opening curves; lower is faster. It correlates −0.84 with panel strength.
- **worst map** = win share on the bot's worst map.
- **niche** = authenticated atlas niche (5 = the ~2000-Elo second tier; 9 = calc/Stockfish; 10 = PPP / early portals;
  7 = exit-safety family).

| # | bot | lane / author | lang | panel | games | tempo | win | worst map | niche | why it is here |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | hb1-12-direction-prior | claude/hb1 | C++ | 1774 | 120 | −3.8 | 0.84 | 0.67 | 5 | strongest on the panel; Ares V06 plus Heartbreaker direction prior. **61.6 MB, not uploadable** |
| 2 | fenrir-v19-bed-and-opening-balance | fenrir | py | 1735 | 60 | 9.7 | 0.82 | 0.50 | 5 | best Python bot; also strong in the 133k older-results fit (1677) |
| 3 | yuna-x33-nb-tight20 | yuna | py | 1716 | 60 | 6.6 | 0.80 | 0.67 | 10 | best early-portal (PPP-like) bot |
| 4 | sciel-03c-ewradio | glm/sciel | C++ | 1700 | 119 | 1.0 | 0.78 | 0.67 | 5 | fast opening, even across maps |
| 5 | sciel-04a-row | glm/sciel | C++ | 1698 | 119 | 0.3 | 0.78 | 0.58 | 5 | second sciel line (row routing) |
| 6 | hb1-10-escape-split | claude/hb1 | C++ | 1693 | 120 | −0.4 | 0.78 | 0.50 | 5 | Ares V06 plus escape split; **uploadable (0.2 MB)** |
| 7 | esquie-03-starve-wait2 | glm-5.3/esquie | C++ | 1693 | 120 | 7.0 | 0.78 | 0.58 | 5 | strong mid-game, slower opening |
| 8 | ra-08-monoco-bed-attraction | codex/ra | C++ | 1684 | 120 | 3.7 | 0.77 | 0.67 | 5 | even across maps; reachable-bed value |
| 9 | ares-v37-near-portal-scout | codex/ares | C++ | 1675 | 120 | 0.7 | 0.76 | 0.50 | 5 | best Ares-line portal scout |
| 10 | ra-03-monoco-sprint-discipline | codex/ra | C++ | 1666 | 120 | 3.0 | 0.75 | 0.67 | 5 | even across maps; sprint control |
| 11 | r3-03-escape-early | glm/r3 | C++ | 1666 | 120 | 0.0 | 0.75 | 0.58 | 5 | fast opening; early escape |
| 12 | yuna-v05-core | yuna | py | 1658 | 120 | 4.5 | 0.74 | 0.67 | 10 | yuna finalist; even across maps |
| 13 | lune-r1-03-search8x | claude-opus/lune | C++ | 1658 | 120 | 2.1 | 0.74 | 0.50 | 5 | deep-search line |
| 14 | yuna-x43-local-crown-donor | yuna | py | 1649 | 120 | 2.3 | 0.73 | 0.50 | 10 | strong in both fits (older results 1688); crown donation |
| 15 | hb1-04-deployable | claude/hb1 | C++ | 1561 | 120 | **−10.7** | 0.64 | 0.25 | **9** | **style slot:** the only local bot playing like the top ten (calc/Stockfish); fastest opening; loses the round-500 longest-dragon tiebreak (no crown). 61.6 MB |
| 16 | r3-02-exit-known | glm/r3 | C++ | 1633 | 120 | 4.7 | 0.72 | 0.33 | 7 | style slot: leader of the exit-safety family |
| 17 | bifrost-v26-tuned-route-ownership | bifrost | py | 1615 | 60 | 11.2 | 0.70 | 0.50 | 5 | style slot: route ownership; top-3 in the older-results fit (1682) |
| 18 | eunchae-s02-pearl-band | gpt/eunchae | py | 1585 | 120 | 14.5 | 0.67 | 0.33 | 10 | style slot: strongest novel bot (pearl-band foraging) |
| 19 | tyr-v12-devil-scout-tiebreak | tyr | py | 1642 | 1,936 | 7.8 | 0.67 | 0.50 | 5 | **reference anchor:** long history, keeps comparisons continuous |
| 20 | fenrir-v20-crowded-resource-revalue | fenrir | py | 1606 | 4,895 | 8.3 | 0.62 | 0.28 | 5 | **reference anchor:** panel opponent with the most games |

**Added later on 1 Oct (graft result):**

- `ouroboros-g01-hbmimic-ares-r150` scores 0.84 on the panel, tying hb1-12. It runs hb1-04's opening, then Ares V06
  from round 150.
- It is not uploadable (61.6 MB), so use it as a local benchmark for the top-ten-style opening combined with a crown
  endgame.
- Details: `docs/findings/2026-10-01-s1-next-steps.md` §5.

**Left out on purpose:**

- near-duplicates of listed bots: hb1-13 (the phased version of hb1-12), sciel-04b, esquie-03b, and the other yuna x
  variants;
- the other lanes' bests, which are far below this band: kraken-s02-trade1 at 1245, leviathan-x04 at 872, and the
  Ouroboros bests (b01 at 1615, but its worst map is 0.33). Add them back for cross-lane tracking if you want them.

## How to evaluate an iteration against the list

1. **All 10 ladder maps, both seats, at least 3 seeds.**
   - Seed 1 alone is what the panel used, and it is not enough to order the top band.
   - Name files `s<seed>__<map>__<A>__<B>.replay` so the gates can pair fixtures.
2. **Opening:** `python3 tools/s1/tempo_gate.py <your run> <parent run>`. Verdicts:
   - ACCEPT;
   - NO GAIN;
   - REJECT;
   - MAP GUARD (faster overall but slower on named maps);
   - INCONCLUSIVE.
3. **Whole game:** W-L-D per map against each candidate, and the round-500 reason. A rise in losses "on length" while
   total length is ahead means a missing crown, as with hb1-04.
4. **Report per map.** A pooled win rate can hide a map collapse; worst-map win share is the column to watch.

## Caveats

- **Where the strength comes from.** The panel opponents are all second-tier styles, so "strong" here means strong
  against those styles. hb1-04 is in the list to test against the top-ten style.
- **No field calibration.** There is no per-bot link to live rating yet. That needs a log of which bot was live when.
- **Bots on 60 games** (fenrir-v19, yuna-x33, bifrost-v26) carry wider intervals than the 120-game bots.
- **Data:**
  - `build/atlas/out/auth/candidates_pool.csv` covers all 247 bots;
  - the method is in `docs/findings/2026-10-01-s1-atlas.md` and `docs/findings/2026-10-01-s1-next-steps.md`.
