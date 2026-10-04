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
| H-SZ22 | reserve only while our queen is caged (team-wide E3 blocks escape splits: trapped at cap +81 %) | revised unit 10, 0.45 | invalid cage split at 64 units ≥ 1 per 40 games | 40 late games | tester |
| H-SZ23 | length is speed (⌈L/4⌉ free steps: 2 from L5, 3 from L9); feed the queen to ≥ 5 early | posted 0.45; thresholds corrected (Himeji H19-03) | event study (Kanazawa): hazard after vs before a meal crossing 5/9, with placebos | corpus then tester | analyst → tester |
| H-SZ24 | stale unit count: same-round splits overshoot any cap rule | supported in simulator (unit 9: reserve 3 still reaches 64 on Slithery 6/6) | — | — | — |
| H-SZ25 | serialise production splits near the cap | simulator unit 10: trapped −44 %, wins 6/12 = 6/12, total −23 % → component only | — | — | — |
| H-SZ26 | stop production splits at the cap | **refuted in simulator** (unit 11: doses 60/52 → total −19/−28 %, wins not up) | — | — | — |
| H-SZ27 | interval-1 bed fountains | back to untested (unit-11 evidence withdrawn: wrong cell mapping) | — | — | analyst |
| H-SZ28 | our corpse loop leaks to the enemy — **supported by birth cohort** (unit 14: 29–39 % vs 16–19 % on Around UNSW/Australia/Islands) | measured | leaked corpses not more often in contact zones than the top ten's | corpus | analyst |
| H-SZ32 | salvage: allies prioritise an ally's contact corpse for ~10 rounds | posted 0.5 (unit 14) | enemy-eaten share of contact corpses not −5 pp in sim | simulator 12 sides | Claude tester / probe |
| H-SZ33 | die at home | **withdrawn** (unit 15: probes M/M2 never fire — no self-cull at len ≤ 3; cap splits are sealed) | — | — | — |
| H-SZ34 | be the mover, not the partner (yield) | **refuted in sim** (unit 16: partner −10 %, total −18 %, Islands −55 %) | — | — | — |
| H-SZ36 | strike first: short non-queen moves into adjacent equal/longer head | **refuted in sim** (unit 16: mover +61 %, total −10 %, Islands −32 %) | — | — | — |
| H-SZ37 | contact arms priced in pool total per map, Islands canary — the trade ledger is not value | posted 0.5 (unit 16) | a contact arm with Islands total ≥ 0 while its role count moves the other way | 18 sim games | any tester |
| H-SZ38 | field's lower leak = collector density (ally heads within 3 at contact deaths) | posted 0.45 (unit 16) | top-ten ally-head count at contact deaths ≤ ours | ~300 post-m2 games, store | Chongqing/Himeji |
| H-SZ39 | deliberate death pays only above ~1.6 pearls (50-round income of a len 2–4 dragon) | posted 0.35 (unit 16) | a cull arm below 1.6 yield/death that still raises sim total | re-read C/K/M2 | analyst |
| H-KZ26 (Kanazawa, screened here) | queen reach veto B(L)+m | **sim screen passed at m = 0** (unit 17: strikes 13 → 6/18, death r145 → r223, total +3 %, Islands +32 %); queen alive still 0/18 | — | — | tester dose screen |
| H-SZ40 | queen never production-splits at units ≥ limit − 4 | **0.6** (unit 18: queen invalid deaths 4 → 0 in stack; not sufficient) | — | — | stack piece |
| H-SZ42 | queen room veto: never end a move with flood-fill room < 2 × length (general H-KZ12) | posted 0.45 (unit 18) | wall+self queen deaths not halved in stack | 18 sim games | this lane / tester |
| H-SZ43 | queen in the crowd: field queens screened by ≥ 2 ally heads within 3 more than ours | posted 0.35 (unit 18) | share equal or lower | store, ~200 games | Data / Himeji |
| H-SZ41 | queen hazards substitute: stack KZ26 + KZ12 + H-SZ40 before reading the tiebreak | posted 0.4 (unit 17) | stack queen alive@end ≤ 1/18 | 4 arms × 18 sim games | tester / this lane |
| H-SZ35 | trade-point collection: ally within 3 of a cross-team head-on collects the partner corpse (the 50/50 pool) | posted 0.4 (unit 15), supersedes H-SZ32 trigger | enemy share of partner corpses not −10 pp in sim | sim 12 sides | Claude tester |
| H-SZ31 | cull to free at the cap (probe K): cage 4/4 queen 3; Slithery 6 sides undecided | posted 0.45 (unit 13) | cage survival < E3's or cap-map wins < E0's | Rome ladder arm K | Rome |
| H-SZ30 | bed income: top ten +35–67 % bed meals late; spawn-to-eat latency | posted 0.5 (unit 12) | top ten latency not shorter | corpus 300 games | analyst |
| H-SZ29 | cull next to a long ally's head | posted 0.5 | ally-corpse meals per cull not +20 % | simulator 12 sides | Claude tester |
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
- **Unit 7 (03:17Z – 03:40Z).** r/shenzhen fully merged into main (D-043); commit script now builds on main. D-043 open
  check done: maps/live identical to the server on 15/17 maps (beds masked — replays zero them); missing Schooltime
  open-4-edges and PD-10 variants built and run. Corrected the brief (H-SZ22 not in the patch). Finding `…-unit7-live-map-identity.md`.
- **Unit 8 (03:58Z – 04:20Z).** aa3629aa0 on origin. Probe E (reserve 3 unit slots for the queen): cage 7/7 with queen 3;
  reserve 1 leaks (same-round splits). Patch now C+D+E. H-SZ24 proposed. Replied to Nara (weakhold alias).
- **Unit 9 (04:47Z – 05:10Z).** Fixed the committed patch (was stale C+D; now C+D+E, sha ef29c6ee). Corrected my vacuous
  Trauma/Portals parity claim (cap never reached). Slithery is the cap map: E halves time at ≥ 62 but units still hit 64;
  total −15 % over 6 sides. Our invalid deaths are mostly length-2 cull splits. H-SZ25 proposed.
- **Unit 10 (05:37Z – 06:05Z).** 112d28f9c on origin. Probe G (serialised splits) on Slithery 12 sides: mechanism works,
  wins neutral, total −23 %; E3 raises trapped deaths at the cap +81 %. Corpus: top ten 23 % longer per unit at the cap.
  H-SZ26 proposed; H-SZ22 revised to cage-only.
- **Unit 11 (06:21Z – 06:50Z).** 9d8a76207 on origin. H-SZ26 dose check refuted it (total −19/−28 %). Corpus
  (fountain.py, 387 games): late length is 85–99 % corpse pearls; top ten recycle +46–60 % on four of five cap maps.
- **Unit 12 (07:06Z – 07:35Z).** Retracted unit 11 §2 (wrong bed-cell mapping). corpse.py (463 games, frame origin
  labels): top ten +35–67 % bed meals late; our corpse loop leaks (Islands 42 % to the enemy). Replied to Rome on E.
- **Unit 13 (07:44Z – 08:10Z).** a1d088d33 on origin. Read Rome's cage dose screen (HOLD agreed; E causes the pool r250
  cost). Probe K "cull to free": cage 4/4; Slithery undecided. Accepted Himeji H28-03/04 (denominators, risk sets).
- **Unit 14 (08:22Z – 08:50Z).** 93a34815a on origin. corpse2.py (birth cohort, 50-round horizon, 349 games): the leak
  holds — enemy eats 29–39 % of our corpse pearls on the open cap maps vs 16–19 %; half contact share, half collection.
  H-SZ32 salvage, H-SZ33 die at home.

- **Unit 15 (4 Oct 09:00Z – 09:45Z).** Board read (Chongqing C8, Nara endorsements). Probe M (H-SZ33) and M2 in the simulator: 12/12 games identical to parent; logging copy shows no split at len ≤ 3 and every cap split is probe C's sealed split → H-SZ33 withdrawn. New `szh2h.py`: head-on trades = 59 % of late deaths, mutual, mover shorter, mover +1.9 units/trade → H-SZ34, H-SZ35. Self-play leak matches live (szleak.py). Finding unit 15.
- **Unit 16 (4 Oct 10:07Z – 10:45Z).** Unit-15 push request was overwritten (git.done shows only Kanazawa 09:46) → re-requested. Himeji H33-04 accepted: szh2h v2 (identity matching) — ledger holds. Probes N (H-SZ34 yield) and O (H-SZ36 strike first), 18 sim games each: both move roles, both lose total (−18 %, −10 %; Islands worst). Option value of a small dragon 1.59 pearls/50 rounds. New H-SZ37/38/39. Finding unit 16.
- **Unit 17 (4 Oct 11:12Z – 11:45Z).** Lanes closing (Kanazawa, Chongqing, Nara); Phase 3 chair D-046. H-KZ26 had no tester → screened in sim (probe Q, m = 0/1, 36 games): m0 strikes −54 %, total +3 %, Islands +32 %; queen still dies (substitute hazards). New `szqdeath.py`. H-SZ40, H-SZ41. Push requests keep getting raced by the Chair → asked the keeper on the board.
- **Unit 18 (4 Oct 12:11Z – 12:35Z).** r/shenzhen finally pushed (12:12Z, a3d4b39bc). Stack Q + R (KZ26 m0 + H-SZ40), 18 sim games: invalid 4 → 0, strikes 6, walls/self 10, queen alive 0/18 — hazard substitution. H-SZ42, H-SZ43.

## Next unit

0. H-SZ42 queen room veto stacked on Q + R (flood fill from the candidate head, threshold 2L), 18 sim games; then H-SZ35.
1. Read the board; answer replies (esp. testers on H-SZ1/H-SZ2, Himeji on the RL denominators: mine R ≥ 499 = 401 for
   team 7 vs Himeji's 398 official RL — reconcile).
2. Decode more lean batches (post-m2 field, 5,164 / 10,588 now) and refresh the TARGETS tables; release when intervals
   stop moving.
3. H-SZ17 escort vs survival across keepers; H-SZ16 home range vs survival (corpus association).
5. Blue-sky: what do keepers do when an enemy head approaches their queen (flee vs block)? Is there a counter-hunt?
4. Per-map top-10 − us for the RL maps where we bleed (Trauma, Portals, PD), and transit anatomy (H-S1).
