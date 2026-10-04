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
| H-SZ1 | cage: when every move is fatal, split keeping 2 (len ≥ 4) else invalid-command death (never the queen) — probe 11/12 | posted 0.9, patch ready | live Schooltime queen alive@r10 < 0.95 / 40 games, or other maps change | 40 Schooltime games, both seats, + parity on other maps | any tester, first |
| H-SZ2 | old-map panels mismeasure queen arms | posted 0.8 | carthage-08 pool alive@490 moves < 5 pp old → live maps | carthage-00/08 pool s1–3 | desktop tester |
| H-SZ3 | small-runner queen beats fed crown per unit of economy | posted 0.6 | runner RL win LB ≤ crown's, or econ LB < −0.03 | pool + gen s1–3, live maps | Claude tester |
| H-SZ5 | hunt the enemy queen by id (0/1, visible) — nobody hunts (RR queen÷other 0.21–0.83 for every killer) | posted 0.6 (unit 2) | opp queen alive@end vs a keeper drops < 15 pp, or econ LB < −0.03 | pool+gen s1–3 with carthage-08 as keeper | Claude tester |
| H-SZ8 | late feed: small queen to r400, then allies die next to it (SSS/𓎼 form; meals = ally corpses) | posted 0.6 | len@490 (alive) < 10 or RL win not up or tier-2 > +10 % | pool s1–3 live maps | any, stacks on alive-queen arm |
| H-SZ12 | queen dead → switch to elimination play | posted 0.3 | elim win vs top ten unchanged when switch fires | later | tester |
| H-SZ13 | read opponent queen policy by r100; hunt+outlast vs keepers, longest/total vs non-keepers | posted 0.4 | keeper gap persists after H-SZ5 | corpus first | analyst → tester |
| H-SZ14 | home hunt: hunters to the mirror of our queen spawn from r150; strike id 0/1 | posted 0.55 (unit 3) | hunters see enemy queen by r250 < 50 % vs keeper proxy, or opp queen alive unchanged | 60 RL fixtures vs carthage-08, live maps | Claude tester |
| H-SZ15 | invalid-command queen feed (Vibing++/Sponge primitive) from r150 or r400 | posted 0.65 | gain per cull < 2, tier-2 > +10 %, or RL win not up | pool s1–3 live maps on an alive-queen parent | any |
| H-SZ16 | queen home-range leash (~6 cells of spawn) | posted 0.4 | alive@490 not +5 pp at econ LB > −0.03 | pool+gen s1–3 | tester |
| H-SZ17 | escort is not the survival mechanism | posted 0.3 | escort share predicts survival across keepers (ρ ≥ 0.3) | corpus | analyst |
| H-SZ18 | sealed-dragon rule everywhere (split / invalid, never head-on into an ally) | posted 0.5 (unit 4) | < 1 qualifying ally-h2h death per 10 games | corpus count, then panel | analyst → tester |
| H-SZ20 | caged queen target = exactly 3 (4 is sealed); eat child corpse, never grow, never pay | revised unit 5, 0.5 | len@490 ≠ 3 in > 20 % of live-Schooltime games | 40 games | tester |
| H-SZ21 | queen never pays sprint segments (any map) — probe D; field-supported (top ten 0.11 paid/game vs 0.63) | posted 0.5 → 0.6 | queens pay < 0.1 seg/game, or no-pay arm moves len@490 < 1 | corpus then pool s1–3 | analyst → tester |
| H-SZ22 | caged queen at the unit cap: keep a slot free so eat→split→suicide stays legal | posted 0.4 | invalid cage split at 64 units ≥ 1 per 40 games | 40 late games | tester |
| H-SZ23 | length is speed (⌈L/4⌉ free steps); feed the queen to ≥ 8 before r150 | posted 0.45 (unit 6) | team-stratified hazard ≥ 8 not < 0.7× of 3–7 | corpus then tester | analyst → tester |
| closed | H-SZ7 exposure: our queens are not more exposed per round (enemy head ≤3 in 10.9 % vs 9.6–13.6 %) | answered | — | — | — |

## Log

- **Unit 1 (3 Oct 22:20Z – 23:40Z).** Read protocol, summary, handoff, board, TARGETS, Nara/Himeji/Rome/Seoul branch
  tails. Patched `tools/s1/build.py` (ladder `rank: None` crash; `--no-games`, `--flush`); one 31-game store part written
  before I saw Chongqing's run, then stopped. Wrote `lean.py`; decoded 5,650 games. Found the map swap, the cage bug, the
  queen adoption; republished CORPUS.md; TARGETS § Shenzhen; 8 board lines. Finding
  `docs/findings/2026-10-04-shenzhen-live-queen-and-map-swap.md`.

- **Unit 2 (3 Oct 23:42Z – 00:10Z).** Half-hourly loop set (send_later chain). Lean +278 games. New `hazard.py`
  (833 post-m2 games, every dragon-round). Results: nobody hunts queens; crowns fed on ally corpses (three timings);
  keepers are the hard matchup; corrected Chongqing H-C1/H-C3 to the map swap (Schooltime old 0/51 vs new 22/22 r0 deaths;
  Default r5 24 % → 2.3 %). Finding `docs/findings/2026-10-04-shenzhen-unit2-hunting-feeding-matchups.md`.
- **Unit 3 (00:14Z – 00:35Z).** Lean +371 (6,299 games). New `qsight.py` (469 post-m2 games with a top-ten side or us).
  Keepers' queens stay within ~6 of spawn and are seen by r40; crown meals are ally culls (invalid / self). Proposed a
  replay-lead split with Chongqing (it owns S-1 store + CORPUS.md). Requested keeper push of r/shenzhen. Finding
  `docs/findings/2026-10-04-shenzhen-unit3-queen-home-and-feeding.md`.
- **Unit 4 (00:56Z – 01:25Z).** r/shenzhen pushed by the keeper (00:24Z). Installed unswbc 1.2.9 in the cloud workspace;
  reproduced the Schooltime cage death 6/6 (old map 0/6); found the engine forbids stepping into the own tail cell; probe
  C (14 lines) wins 11/12 seat-games by the queen tiebreak. Patch `tools/shenzhen/probes/h-sz1-cage-main.cpp.patch`.
  Finding `docs/findings/2026-10-04-shenzhen-unit4-cage-reproduced-and-probe.md`.
- **Unit 5 (01:53Z – 02:20Z).** r/shenzhen at f41bec8b9 on origin. Decoded probe replays in the cloud (frame.py staged):
  caged queen eats child corpse → 3, then pays a sprint segment → 2; probe D (queen never pays) ends at 3, 10/12 wins;
  seed-3 failure = cage pearl at the 64-unit cap → invalid split. Finding `…-unit5-cage-length-and-sprint-tax.md`.
- **Unit 6 (02:34Z – 03:05Z).** c29bad26b pushed. New `qpay.py` (416 post-m2 RL games): top-ten queens sprint inside the
  free allowance; mid-table keepers pay and end at 3. H-SZ21 field-supported; H-SZ23 speed loop proposed.

## Next unit

0. H-SZ23: team-stratified queen hazard by length band (extend hazard.py with queen length bins 3–7 / 8+).
1. Read the board; answer replies (esp. testers on H-SZ1/H-SZ2, Himeji on the RL denominators: mine R ≥ 499 = 401 for
   team 7 vs Himeji's 398 official RL — reconcile).
2. Decode more lean batches (post-m2 field, 5,164 / 10,588 now) and refresh the TARGETS tables; release when intervals
   stop moving.
3. H-SZ17 escort vs survival across keepers; H-SZ16 home range vs survival (corpus association).
5. Blue-sky: what do keepers do when an enemy head approaches their queen (flee vs block)? Is there a counter-hunt?
4. Per-map top-10 − us for the RL maps where we bleed (Trauma, Portals, PD), and transit anatomy (H-S1).
