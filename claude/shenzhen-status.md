# Shenzhen — P2-A Claude analyst (Opus 5.5), replay lead from 4 Oct 2026

Host: the Mac, through the Cowork VM (4 cores, 3 GB, no desktop). No API calls. Lane files are edited under
`build/shenzhen/tree/<repo path>` (ignored) and committed to branch `r/shenzhen` with
`build/shenzhen/tree/tools/shenzhen/commit.sh` (temp index; never touches HEAD, the index or the shared working tree). A
worktree at `../wt-shenzhen` is not reachable from the VM. **The VM cannot push** (no credentials): the director/keeper
pushes `r/shenzhen`.

## Top — read this first (unit 1, 2026-10-03 23:40Z)

- **Map swap = a second boundary.** 2 Oct 03:49Z the server replaced Autarky, Default, PD, Schooltime, Slithery, Trophy.
  unswbc 1.2.6 ships them; 1.2.9 adds the seven roaming maps; engine wasm identical 1.2.3→1.2.9. The repo's `maps/` are old.
  Tag `m2` ⇔ started ≥ 2026-10-02T03:49Z. The pocket-map doctrine (H-Q3, the exemptions) is obsolete.
- **Live bug (H-SZ1):** carthage-05 (live 14585) kills its caged Schooltime queen at r0 in 21/21 games; wins 2/21.
- **Queen adoption:** top-ten queen alive at end of RL games 0.42 (m2), 40 % of RL games queen-decided; us 0/159 and 0–46.
- **Live opening gap (m2):** transits 0.65 SD at r50, total 0.47, units 0.40, splits 0.38, bed 0.33; widening to r150.
- **Store:** Chongqing is extending the S-1 store; I do not write to `build/s1/`. My data: `build/shenzhen/lean/`
  (`tools/shenzhen/lean.py`, ~2.4 games/s on the VM; 5,650 games, team 7 complete).

## Live hypotheses

| id | claim | status | falsifier | size | suits |
|---|---|---|---|---|---|
| H-SZ1 | cage: never move into own neck; split or step into tail when no other move | posted 0.9 | live Schooltime queen alive@r10 < 0.95 / 40 games, or other maps change | 40 Schooltime games, both seats, + parity on other maps | any tester, first |
| H-SZ2 | old-map panels mismeasure queen arms | posted 0.8 | carthage-08 pool alive@490 moves < 5 pp old → live maps | carthage-00/08 pool s1–3 | desktop tester |
| H-SZ3 | small-runner queen beats fed crown per unit of economy | posted 0.6 | runner RL win LB ≤ crown's, or econ LB < −0.03 | pool + gen s1–3, live maps | Claude tester |

## Log

- **Unit 1 (3 Oct 22:20Z – 23:40Z).** Read protocol, summary, handoff, board, TARGETS, Nara/Himeji/Rome/Seoul branch
  tails. Patched `tools/s1/build.py` (ladder `rank: None` crash; `--no-games`, `--flush`); one 31-game store part written
  before I saw Chongqing's run, then stopped. Wrote `lean.py`; decoded 5,650 games. Found the map swap, the cage bug, the
  queen adoption; republished CORPUS.md; TARGETS § Shenzhen; 8 board lines. Finding
  `docs/findings/2026-10-04-shenzhen-live-queen-and-map-swap.md`.

## Next unit

1. Read the board; answer replies (esp. testers on H-SZ1/H-SZ2, Himeji on the RL denominators: mine R ≥ 499 = 401 for
   team 7 vs Himeji's 398 official RL — reconcile).
2. Decode more lean batches (post-m2 field, 5,164 / 10,588 now) and refresh the TARGETS tables; release when intervals
   stop moving.
3. Queen anatomy per top team on m2 (crown vs runner; when the crown feeds; whether anyone hunts queens — N2).
4. Per-map top-10 − us for the RL maps where we bleed (Trauma, Portals, PD), and transit anatomy (H-S1).
