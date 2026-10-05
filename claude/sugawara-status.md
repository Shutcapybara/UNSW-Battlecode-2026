# Sugawara — Phase 3 council seat (Claude, mechanism style)

State: ACTIVE — **queen owner since D-072 §C (council dissolved, D-072 §B)**. Last completed unit: 5 Oct 2026 20:37Z (unit 34). Repo copy: `claude/sugawara-status.md` in the checkout (identical content).

## Role

- **Since D-072 (03:58Z): owner of the queen problem (D-072 §C), not a council seat.** I choose mechanisms and order and
  queue builds/screens with Asahi; this file is the queen log. My scheduled prompt still says docs-only/no experiments, so
  Asahi writes the bot code from my specs (asked the user to update the prompt, 04:40Z). Forecasts/Brier closed (D-072 §B).
  Shenzhen is stopped (D-074 §C): analyst work is mine. Old council role below kept for history.

- Council seat (D-050). Since D-067 §G (Tanaka stopped 00:49Z, credit budget) I also **replicate the key number of any
  statistics-bearing card before the Chair records it**, audit Nishinoya's probes (they stay `unaudited` until I
  replicate), and did the inventory configuration check. I run no bot experiments or uploads.
- Two free lanes (D-067 §F, e.g. Kenma) run outside the ladder; their BOARD lines are data. Not mine to review unless assigned.

## Git and environment

- Cowork VM with the Mac checkout mounted at `$HOME/mnt/Projects/UNSW-Battlecode-2026`. Git over the mount is
  read-only (`git --no-optional-locks`; `git log --all` fails; name branches, e.g. r/asahi). Lane worktrees sit beside
  the checkout (`$HOME/mnt/Projects/wt-<lane>`). Outputs are docs only; the hub keeper commits them.
- Disk reset 04:00Z (D-073 §B): the shell works again in fresh sessions; heredocs to stdin work. Keep writes inside the mount.
- The VM has python3 + numpy; `tools/analysis/features/frame.decode` decodes replays (gives header `reason`, incl.
  `queen`; `events.deaths` with round/cause). `tools/hub/executor.analyse_replay` maps `queen` to `roundLimit`.
  Ranked index: `public_replays/corpus/index.jsonl` (team 7 = us; sub_a/sub_b are None for recent games → attribute by
  time; 16979 activated ≈ 02:13Z). Ladder snapshots `public_replays/corpus/ladder/*.json` (10-min cadence).
- Decode speed ≈ 1 s/game; 120 games fit in one 170 s call.
- **The lock cannot be deleted** (rm is not permitted). At the end of each unit, `touch -d 2000-01-01` it.
  A stray `build/sugawara/.sg_test` (1 byte) is mine; harmless.
- To write the repo copy of this file: python write on the mount (works) or stage+commit.
- **BOARD style:** one physical line per entry. Read the new BOARD tail **immediately before** posting.
- **Hard rule:** `_common.md` l.21, "No map identity in any bot: structure only". D-080 §D: binds learned features and ladder-rung artifacts, not free-lane bots (atlas trial needs gen panel, hidden-layout block, n_maps = 0 twin).

## Unit 34 (20:25–20:37Z): D-052 §B anchor question (Daichi 19:52Z)

- **Read:** BOARD through line 1491 (`[20:03 bokuto → asahi, chair, sugawara] JOB bokuto-58-reachable …`); my line 1492. No new D-record
  after D-088. Hinata 19:36Z accepted my three D-088 §C amendments (reached-view growth caveat). Bokuto JOBs 57 (queen blind-portal rule,
  e92220b72) and 58 (= 57 + reachable migration target, 7d999134f; his trial-5 fallback if 46 fails). Daichi 19:52Z: all-trials table at
  1725 (matches mine); question: D-052 §B on a trial bot, which anchor (−0.136 rolling at 20 games). Chair has not answered rec 29.
- **Done:** the −0.136 is a level on a rolling own anchor, not D-052 §B (a difference vs the replaced submission, own rating fixed at
  activation = 1829). As written: 17940 35/7 diff −0.052 [−0.191, +0.089] vs 17791's 65/13 → does not fire; at 1725 −0.062. Level moves
  ~0.12 with anchor, difference does not. Reading: D-052 §B binds the end-rule incumbent, not a trial bot pre-look. 17940 at 1725 now
  +0.108 (35/7). Review `docs/learning/reviews/D-052B-anchor-17940-sugawara.md`; code `build/sugawara/d052/`.
- Not notified: no rollback changes (neither form fires at 35 games); Chair decides applicability.
- Next: trial-4 look ≈ 22:15Z (review before Chair; pooled-line reading, anchor 1725, bar +0.204/+0.126); Chair on rec 29 and on the
  D-052 §B question; 46 probe + gen; 57/58 cards (queen wall deaths on qk2; 58 Schooltime routing); per-game growth check on the 40 (Hinata caveat).

## Unit 33 (19:26–19:31Z): D-088 §C curve-block check; §E trial-5 condition

- **Read:** BOARD through line 1484 (`[19:25 chair:ushijima … D-088 …]`); my lines 1485–1486. D-088: §A 17791 incumbent of record;
  §B note A accepted (anchor 1725 everywhere; Daichi table of all trialled subs); §C Hinata block recorded unchecked → me;
  §D trial 4 = 17940, look ≈ 22:15Z, > +0.204 pass, ≤ +0.126 against, between = unresolved (note B adopted); §E trial 5 =
  bokuto-46-regions if probe + gen (5th > −5 vs b13), fallback bokuto-25; §C restated as paired 5th pct > −5 (post hoc, Chair
  asked me to object if I read it differently). Bokuto 18:32Z: knobs do not spend budget; bokuto-52 lookahead. Asahi 18:47Z/19:20Z:
  41 qualifies, fails order test; 46 qk2 +11.76, h2h −5.88; 47 fails pool floor.
- **Done §C:** replicated exactly; amend labels — live-lead conversion 14/20 = 70 % (carried 20/26 includes 6 early elimination
  wins); queen alive r300 reached 0.72 vs target; vs top ten most of the economy gap is growth r100→r300 (−24.6), not r100 (−13.4).
  Review `docs/learning/reviews/D-088-curveblock-sugawara.md`.
- **Done §E:** 41 is a valid twin (all 46 changes atlas-gated). Pool 46−41 −0.74; 5th pct across 40 bootstrap seeds −5.88…−4.78,
  median −5.15, ≤ −5 in 88 % → restated rule undecidable. **Rec 29 (open):** record 46 as a waiver on qk2 twin +20.6 [+5.9, +36.8].
  Review `docs/learning/reviews/D-088-trial5-46-sugawara.md`; code `build/sugawara/t5/p5seeds.py`.
- Forecast log: 46 gen 5th pct > −5 0.70; trial-5 > +0.204 0.20, > +0.126 0.40. Notified the user (gate-condition statistics).
- Next: trial-4 look ≈ 22:15Z (review before Chair; pooled-line reading, anchor 1725); Daichi's all-trials table at 1725;
  46 probe + gen; Chair's response to rec 29; bokuto-52 points (budget use); 17530 15/21 split into live/early.

## Unit 32 (18:25–18:36Z): trial-3 look replication

- **Read:** BOARD through line 1469 (`[18:25 daichi → chair, … Trial-3 look (D-084 §C end rule, applied): 17791 … incumbent …]`);
  my line 1470. D-087 (18:19Z): §A compute limit 100 M, cut = death, probe ceiling 60 M; §B no seat term; §C bokuto-35 fails,
  **atlas bot must be ≥ its atlas-off twin on pool**; §D trial 4 = asahi-27 (17940, live 18:25:06Z), trial 5 = qualified one of
  bokuto-41-atlas0 / 46-regions / 47-precious (qk2 then h2h vs b18), fallback bokuto-25. Bokuto 17:33/18:16Z: ally-collision excess
  = atlas portal pairs; 46 adds region migration. Asahi 17:49Z: twin asahi-28 = b18 on pool; 17:57Z burn test.
- **Done:** trial-3 look — agree, replicated exactly (17791 +0.174 [+0.079, +0.282] n 60/12; 17388 +0.060 over 130/26; Δ +0.115,
  P(Δ ≤ 0.03) 0.13). Note A: D-084 §B +0.005 = anchor ≈ 1765–1770, not snapshot timing. Note B: trial-4 bar (+0.204) is
  selection-inflated. Review `docs/learning/reviews/D-087-trial3-look-sugawara.md`; code `build/sugawara/look3/`.
- Forecast log: 17940 > +0.204 at its look 0.25; 17791 post-window < +0.174 0.70. Rec 28 withdrawn (unit 31) confirmed by twin.
- Not notified: decision unchanged; trial 4 already live.
- Next: Hinata's frozen curve block for 17791 (queen columns, reached + carried, seat column); trial-4 look ≈ 22:15Z (review
  before Chair; Note B); 41/46/47 cards (twin rule D-087 §C, gen + hidden block); bokuto-25 probe; any bot using > 13 M/turn.

## Unit 31 (17:25–17:38Z): Hinata points replication; bokuto-35 card read

- **Read:** BOARD through line 1447 (`[17:13 asahi → bokuto, chair, sugawara, daichi] bokuto-35-knownbeds … does NOT qualify`);
  my lines 1448–1449. No new D-record after D-086. Hinata 16:53Z: points settled from our own replays (100 M cut, 25–29 Sep);
  seat column (no seat effect; 17791 look ≈ 18:20–18:45Z, not 17:50–18:10Z).
- **Done:** Hinata points — agree, every number replicates from o_s0–3 except tle total 2,836 vs 2,749 (timing). Review
  `docs/learning/reviews/D-086-points-hinata-sugawara.md`. bokuto-35 — agree not qualified; slithery (atlas right) loses more than
  devil_b (phantoms); n = 16 cells, p = 0.33; cost is the opener, not priors → **rec 28 withdrawn**. Review
  `docs/learning/reviews/bokuto-35-card-sugawara.md`.
- Forecast outcomes: 35−34 void; hidden block > 2/80 below 13-cull → 0 (P 0.25). 35−twin ≥ +2 pp lowered 0.45 → 0.30.
- Not notified: no gate flawed; trial order unchanged (trial 4 = asahi-27, D-086).
- Next: trial-3 (17791) look ≈ 18:20–18:45Z — review before the Chair (reached + carried; queen columns; Schooltime apart;
  Hinata seat column as column only); asahi-28 twin card; burn test (does a tle turn kill?); Chair's trial-5 naming now that 35 failed.

## Unit 30 (16:25–16:46Z): D-086 §E.1 points scan; bokuto-35 atlas known-bed count

- **Read:** BOARD through line 1438 (`[16:27 asahi → bokuto, chair] Component readings (D-086 §B) …`); my lines 1439–1440 (16:44Z).
  D-086 (16:24Z): §A exit-split recorded as amended; §B/C **trial 4 = asahi-27-b13-reserve** (not bokuto-27); trial 5 = Bokuto's
  latest complete bundle (35/34/33) with D-080 §D atlas block; rule: ladder gets the qualified candidate most different from
  trialled bots; §C look ≈ 17:50–18:10Z; Hinata seat column; §E points limit 30 M vs page 100 M — corpus check to Hinata or me;
  §F lead's RL question noted. Asahi 16:27Z: 25 level, 26 kills not wins; next bokuto-35 with gen + hidden + twin asahi-28.
- **Done (§E.1):** corpus cannot settle — 0/121 recent top-ten ranked games carry CPU; random 60 ranked: 1.3 % of actions, one
  game only (ours, seat A, max 10.07 M); tle 0. Burn test (Asahi) is the remaining path. Repo docs BAHAMUT_HANDOFF l.68 and
  BASELINES-2026-09-30 l.43 already say 100 M. Review `docs/learning/reviews/D-086-points-sugawara.md`.
- **Done (unassigned):** bokuto-35 known-bed term vs hidden layouts: devil_b 18/30 template fast beds real, slithery 118/131,
  dilemma_10 8/8, QoS 0/0, schooltime_open4 no match. Asked devil_b/slithery shown apart; 35 vs 34 and vs twin. Review
  `docs/learning/reviews/bokuto-33-35-atlas-sugawara.md`; code `build/sugawara/knownbeds/`.
- Forecasts (log): burn test 50 M survives 0.80; 35 − 34 pool ≥ +2 pp 0.35; 35 − twin ≥ +2 pp 0.45; hidden block < 13-cull by > 2/80 0.25.
- Rec 28 (new, open): per-layout atlas drop at first contradicting observation if devil_b loses.
- Not notified: no gate flawed; nothing human-in-the-loop for the council.
- Next: trial-3 look ~17:50–18:10Z (review before Chair; reached + carried; seat column; queen columns); asahi-28 twin + 35 cards;
  Asahi burn test result; Chair's trial-5 naming.

## Unit 29 (15:25–15:38Z): D-085 §B exit-split check

- **Read:** BOARD through line 1422 (`[15:23 chair:ushijima … D-085 …]`); my line is 1423 (15:37Z). D-085: §A Hinata/me band
  reading recorded (reached + carried side by side at looks); §B Bokuto's exit-split finding pending my check; §C trial 4 =
  bokuto-27 if probe + pool pass by trial 3 look (~17:20Z), else asahi-27; 25/26 queue by paired result vs 18. Asahi 15:06Z:
  27 ~15:40Z, 25 ~16:05Z, 26 ~16:30Z; enemy-queen columns added.
- **Done:** amend. Wall r100–300 us 132.1 vs opp 51.3 ✔. Len 3–5 wall deaths: L3 no-split 46 %, after production split 27 %,
  at cap 20 %, below cap 7 %. Order-fix upper bound 7.3 cells/game [5.5, 9.1]; cap class 25.8; Portals L3-whole 219/g.
  Diff one hunk, legal; reserve guard blocks escape split at units ≥ limit − 1 (Note C). Review
  `docs/learning/reviews/D-085-exitsplit-sugawara.md`; code `build/sugawara/exitsplit/` (rows sha fe124cca6d56).
- Forecasts (log): 27 meets §C 0.85; paired r300 total ≥ +5 vs 18 0.30; beats incumbent > 0.03 0.25.
- Recs 25–27 (new, open): reserve exemption for escape split; attack L3 corridor walkers (Portals); net-of-re-eat wall accounting.
- Not notified: not a gate flaw; trial order unchanged.
- Next: trial-3 look ~17:20Z (review before Chair; reached + carried views; queen columns); Asahi's 27 probe/pool/paired cards.

## Unit 28 (14:26–14:42Z): Hinata ≥ 1725 reading check (D-083 §A, D-084 §D)

- **Read:** BOARD through line 1416 (`[14:24 chair:ushijima … D-084. Trial 3 is recorded …]`); my line is 1417 (14:40Z).
  D-084: trial 3 = bokuto-18 = 17791 live 14:19:00Z, look ~17:20Z; 17388 back to +0.005 over 129; end rule mechanical (Daichi);
  trial 4 = asahi-27 (fp 16ceecff); §D Hinata's reading waits for me. Asahi 14:17Z: b18 h2h vs kenma-03 61–41, qk2 30–38.
- **Done:** amend. Hinata's numbers replicate (−0.03 queen; 94.4/76.6 +17.8). Survivorship: 7/11 elim losses end before r300;
  carried view ≥ 1725 total diff +0.8 [−24.9, +24.8] vs < 1725 +41.5; conversion 71 % vs 74 % (band-invariant). Gap = no lead
  built + early combat, not conversion. Review `docs/learning/reviews/P-hinata-07-band-sugawara.md`; code `build/sugawara/qband/`.
- Forecasts (log): b18 vs ≥ 1725 carried lead conversion ≥ 65 % 0.65; total r300 carried diff ≥ +10 0.35.
- Not notified: not a gate; the end rule is unaffected.
- Next: trial-3 look ~17:20Z (review before Chair; ask for both views); Chair's record of the amended reading.

## Unit 27 (13:27–13:38Z): bokuto-18 pre-trial mechanism read

- **Read:** BOARD through line 1405 (`[13:25 asahi → chair, daichi, bokuto] D-083 §B / bokuto-18 running …`); my line is 1406.
  D-083 (13:24Z): §A D-082 queen statements withdrawn; three targets per candidate (total length ≈ 78/154 r100/r300; queen
  alive r300 ≈ 0.58; ≥ 70 % r300 leads converted); **standing rule: Sugawara reviews Hinata's diagnosis-changing
  descriptions and the reverse**. §B–D trial 3 = bokuto-18 if Asahi posts probe OK + pool floor vs c05 (else asahi-27);
  look at ≥ 60 ranked games **reviewed by me before the Chair reads it**; end rule > 0.03 over 17388 (all games since 05:02Z).
  17388 active since 12:34:13Z (Daichi). Asahi 12:39Z/12:42Z: asahi-27 h2h 69–33 vs 17388; economy table (pool blind to the race).
- **Done:** bokuto-18 diff vs 17 — agree, no blocking flaw (atlas off real; inputs legal; queen test fine; notes on bundle
  and hide/split 380→290). Replicated Asahi's reserve effect: asahi-27 − b13 r300 total length +11.5 [+8.4, +15.0] (191 paired).
  Review `docs/learning/reviews/bokuto-18-sugawara.md`; code `build/sugawara/econ/pair.py`. Erratum 585 → 593 in P-hinata-07 review.
- Forecasts (log): b18 passes conditions 0.85; beats incumbent > 0.03 at look 0.40; queen alive r300 ≥ 0.40 0.55; total r300 ≥ 111 0.35.
- Not notified: no gate flawed; the trial condition is the Chair's and stands.

## Unit 26 (12:26–12:40Z): P-hinata-07 queen-column bug

- **Read:** BOARD through line 1374 (`[12:28 chair:ushijima → daichi, lead] D-082 §D …`); my line is 1375 (12:35Z). D-082
  (l.3589: §A curve table adopted, "queen survival does not separate winners from losers", corrects D-080 §A; §B reserve
  refuted; §C two targets: total length near top-ten winner curve + ≥ 70 % r300 leads converted; my LOO read for "which layer
  costs total length at r300"; §D Daichi has not activated 17388, lead asked at 13:20Z). Asahi results (asahi-27, qk2, h2h) due ~12:40Z, not yet posted.
- **Finding:** `tools/hinata/curves.py` hard-codes queen id 0 = A, 1 = B; id 0 is B's in 593/1,171 games (585 was a sum slip, erratum 13:35Z) (owner from map
  DRAGON lines). Owner-corrected end state matches the engine queen field 2,342/2,342 (card 1,894). Corrected: top ten
  r300 winner 0.58 vs loser 0.37 (+0.21 [+0.17, +0.25]); end queen length 8.8 vs 1.7; ours r300 14585 0.06/0.45, 17388
  0.12/0.47, 17530 0.50/0.57. Economy and lead-conversion columns unaffected. Review `docs/learning/reviews/P-hinata-07-sugawara.md`;
  code `build/sugawara/curvecheck/{own.py,fix2.py,out.txt}`. Forecasts: corrected re-run top-ten r300 diff ≥ +0.15 0.9; 17388 us−opp ≤ −0.25 0.85.
- Not notified: not a gate and no promotion/rollback depends on it; the Chair reads the BOARD. Rec 24 (new): add queen alive
  at r300 as a third reported column; fix curves.py at source.

## Unit 25 (11:27–11:38Z): D-081 §B reserve check

- **Read:** D-081 (l.3513: §A kenma-03 / 17388 incumbent by the end rule; §B hypothesis 'free slot' ordered to me + asahi-27;
  §C bokuto-17 atlas −4.41 on−off, my atlas forecast 0.55 → 0, Brier 0.3025; §D queue). BOARD through line 1365
  (`[11:24 chair:ushijima … D-081 §B–D …]`); my line is 1366 (11:36Z).
- **Result (240/240 replays; `build/sugawara/reserve/`):** not supported. b13-cull already keeps the slot (bokuto.hpp l.349/381);
  both trial bots 0.0 % of r100–400 snapshots at 64 units (14585 24.6 %). Queen length ≥ 4 at death 4/58, 3/43; with cap 0/0 (14585 3/116).
  17388's queen survives worse (end 2/60 vs 17/60); its ≥ 1725 edge is the 'longest' class (both queens dead) 10–5 vs 2–6.
  Review `docs/learning/reviews/D-081-reserve-sugawara.md`. Forecast: P(|asahi-27 pool − b13| > 2 pp) 0.20.
- Not notified (no promotion/rollback changes; the Chair's conditional trial is the decision and reads the BOARD).

## Unit 24 (10:26–10:36Z): D-080 feeding census

- **Read:** D-080 (l.3436: §A queen race after r100; §B Sugawara reads LOO on qk/qk2, supports bokuto-18 with feeding analysis;
  §C clone-prior paused; §D atlas admissible in free-lane bots with gen panel + hidden-layout block + my `n_maps = 0` twin;
  §E kenma-28 = parent). BOARD through line 1350 (`[10:19 chair:ushijima … D-080 §C–E …]`); my line is 1351 (10:34Z).
- **Feeding census** (`build/sugawara/feed/{feed.py,summ.py,rows.jsonl}`; TOP 10 vs ≥1650, 210 team-games; 17530 window 55):
  queen h2h deaths 0.42/g both; **wall 0.25/g us vs 0.03 top** — the survival gap is walls. Top median queen stays 3 to r400;
  upper quartile grows from r300–350; 10th feed median r329; suicide used by 4/10 top teams, 24 % of corpse eats near a suicide;
  17530 0 suicides. Escort 2 within 5 tiles both. Review `docs/learning/reviews/D-080-queen-feeding-sugawara.md`.
- Recommendation to Bokuto: (1) no queen wall deaths, (2) feed from r280–300. Asked Asahi for a queen-death-by-cause column.
- LOO on 13-cull: no build yet. Forecast (unscored): wall fix lifts queen alive r300 46 % → ≥ 58 %: 0.6.
- Not notified (no gate flawed; atlas ruling made).

## Unit 23 (09:25–09:37Z): bokuto-17 atlas flag

- **Read:** D-079 (l.3366: Kenma retired, REG-008 kenma-28 = 13-cull + pocket/reserve, no gain; BOARD overwrite #2;
  P-9 closed at S0, G = 0.018; D §: nothing confirmed on ladder, trial-2 interim 10–15 −0.193; look ~11:15Z; Daichi
  prepares paired live screen; Hinata optional pool-vs-ladder description). BOARD through line 1338
  (`[09:18 chair:ushijima … D-079 …]`); my line is 1339.
- P-9 first-stage forecast 0.45 → outcome 0 (Brier 0.2025, recorded D-079 §C, not council-scored).
- **Flag (unassigned):** `bokuto-17-atlas` carries a 17-live-map atlas (13-cull/c05: 10) feeding whole-map routing and the
  branch gate — map identity under the hard rule / D-033 / D-069 §C. Asked for an `n_maps = 0` twin and a Chair ruling
  before any job. Forecasts: on−off pool ≥ +2 pp 0.55; survives var block 0.35. Review
  `docs/learning/reviews/bokuto-17-atlas-sugawara.md`. Not notified (no gate pending on it).

## Unit 22 (08:25–08:33Z): P-9 S0 mechanism review

- **Read:** D-078 (l.3283: trial 1 +0.074, no Schooltime; trial 2 = 17530 live from 08:15:41Z; tie rule 0.10; clone 213 arms fail;
  P-9 S0 approved; my atlas note as §E); BOARD through line 1327 (`[08:23 daichi → chair, sugawara, asahi] D-078 (A)/(B) answers`);
  my line is 1328. BOARD overwrite at 08:17Z restored by the Chair (append with >> only, as I do).
- **P-9 / P-hinata-05 review (amend):** the cull hash reduces to rnd ≡ 3·me (mod 8), a fixed per-dragon 8-round cycle, not a per-turn
  coin; S0(a) per-turn ITT measures delay. Instrument = D = (3·me − r0) mod 8 at spell entry. Review
  `docs/learning/reviews/P-hinata-05-sugawara.md`. My P: first stage gap ≥ 0.25 0.45; S0 effect 0.20; S1|S0 0.25. Not notified (S0 diagnostic, not a gate).
- Daichi: Schooltime still in ranked draw (6.4 %); trial-1 zero is a 1.5 % event, not removal.

## Unit 21 (07:27–07:31Z): trial 2 out-of-sample read

- **Read:** D-077 (l.3199: trial 2 = bokuto-13-cull; control dropped; 13-cull is the local reference and LOO base; clone stop rule);
  BOARD through line 1304 (`[07:25 chair:ushijima → hinata, … D-077 §E–F. Clone …]`); my line is 1305.
- Chair 06:44Z agreed my LOO order/thresholds; caution: read layers against the base only. LOO is item (3) in the Mac queue (D-077 §D).
- **Replication:** 13-cull pool 241/272, +5.51 [+1.84, +8.82] vs c05. **Var block (Asahi, already on disk,
  `runs/<bot>/<fp>/var/index.jsonl`):** 13-cull 72/80 vs c05 63/80 (+11.25 [+1.25, +21.25]); +8 of +9 is schooltime_open4;
  other four 57/64 vs 56/64. k16 var −1.25 (pool +2.57; failed live).
- **Atlas note:** `world.hpp::atlas_try` (same in c05) seeds bed beliefs from template; 4/5 hidden layouts share template terrain
  (EDGE identical; TILE differs) → wrong unseen-bed prior on ≈11.4 % of ranked games; 13-cull's branch gate reads atlas_bed too.
  No harm measured on var block. Possible later card: atlas = terrain only. Review `docs/learning/reviews/D-077-trial2-var-sugawara.md`.
- Not notified (nothing gating is flawed; trial 2 order unchanged).

## Unit 20 (06:27–06:42Z): queen log #3

- **Read:** D-076 (l.3104); BOARD through line 1231 (`[06:21 chair:ushijima … D-076 …]`); my line is 1232 (06:40Z).
- **D-076 §C decided:** leave-one-out on the trial-2 base (bokuto-13-cull if its pool is ≥ 226 by 07:45Z, else bokuto-04).
  Order: −04+05, −06, −12+09, −02. Each paired against the base on pool + qk. Q1r in parallel: Q1 + reserve only while rnd < 60.
  Q2b-k16 and q2a are off. Plan §8. Review `docs/learning/reviews/D-076-loo-sugawara.md`.
- **Replication (seed-1 pool, paired vs c05 226):** Q1 226, kenma-03 220 (losses UNSW 5 / Australia 4 = reserve),
  Q2b 219, **bokuto-02-vac 195 (−31)**, bokuto-04 226. Layers interact. Gotcha: the c05 index 7df05a3f holds seeds 1–3, so filter seed==1.
- bokuto-13 layer map (tags 02, 03, 04, 05, 06, 08, 09, 11, 12, 13; six of them about the queen). Beacon is legal (sonar/sight/self).
- Owner events from unit 19 both failed (D-076 §C: Brier 0.3025 / 0.16, not scored). Not notified (nothing gating is flawed).

## Unit 19 (05:26–05:32Z) — queen log #2

- **Read:** D-075 (l.2980); BOARD through line 1217 (`[05:23 hinata → … Arm A11 …]`); my lines 1218–1219 (05:30Z).
- **D-075 §D answered:** Bokuto's queen block ahead of q2a, isolated (policy.hpp `// bokuto-04` lines only), on
  **carthage-05** (k16 rolled back 04:53Z; incumbent 14585). q2a parked. Q-plan §7 appended.
- **Paired re-read of Asahi's pool index files** (`wt-asahi/build/asahi/runs/<bot>/<fp>/pool/index.jsonl`): bokuto-04's
  42 queen wins = 38 on c05 wins + 4 rescues; 62/272 discordant (23 %); kenma-03 13/13 on c05 wins, 6 %. Pool queen
  columns ≠ prize. Review `docs/learning/reviews/D-075-queen-order-sugawara.md`.
- Owner forecasts: q2b pool 5th pct > −5 pp 0.55; q2b queen wins ≥ 25 0.60; q2b ≥ +5 pp vs c05 on bokuto-04 keeper panel 0.40.
- Not notified: the contradiction does not change the D-075 §C end rule (ladder windows decide).

## Unit 18 (04:25–04:40Z) — queen log #1

- **Read:** D-071–D-074; BOARD through 1202 (`[04:33 chair:ushijima … D-074 §B kenma-03 ladder trial]`); my lines 1203–1204.
- **Diagnosis (16979, 47 ranked, scans `build/sugawara/q16979.json`, `qtop.json`):** queen-decided 0–19 (19 of 29 losses);
  queen dies at length 2–4 in 43/43 (enemy h2h 22, wall 11, self 9 incl. 5 cage r0). Opp. queens in those losses: ≤ 3 in 7,
  6–30 in 12. Team 213: queen-decided 11–1, surviving queen = longest in 10/12 (crown queen). Queen = ids 0/1 on all 16 maps.
- **D-071 §C.1 done:** kenma-03 = pocket switch (a–c) + global reserve (d, the pool cost). Bokuto-04 read (guard + branch
  gate + queen caution/crown block).
- **Plan `docs/learning/proposals/Q-sugawara-01-queen-plan.md`:** Q1 cage (Kenma a–c, no reserve) → Q2a grow (no queen split
  leaving < 12, action-level gate via `w.limit = w.units` re-decide) → Q2b Bokuto caution/crown → Q3 queen-only guard.
  Readings: pool with queen columns (cost) + 68-game queen-keeper panels vs bokuto-04 and kenma-03 (prize).
- **Asked Asahi** (line 1204) to build q1 then q2a, alternating with Hinata's jobs.

## Queen scoreboard (fill as results land)

| build | parity | pool Δwin | pool q_dec W–L | queen alive @limit | keeper panels | ladder |
|---|---|---|---|---|---|---|
| 16979 (ref) | — | — | parent 0–5 / 272 | 4/47 ladder | — | q_dec 0–19 / 47 |
| kenma-03 (D-074 §B trial) | — | 220–52 vs 226–46 | ? | ? | — | trial 60 games (Daichi) |
| sugawara-q1-cage (asahi-21) | 270/272 (2 Schooltime) | 0.00 (226) | 3–5 | Schooltime 3/14 | qk 34–34 (+2.94) | — |
| sugawara-q2b-crown (asahi-25) | 134 disc | −2.39 [−5.89,+0.92] (219) | 16–5 | 17/149 | qk 27–41 (−7.35); vs b04 12/34 | closed |
| bokuto-02-vac (guard only) | 169 disc | 195 (−31) | ? | ? | — | — |
| bokuto-13-cull (trial 2, D-077) | probe pass | +5.51 (241) | 92–2 | 94/163 | var 72/80 vs 63 (+8 open4) | trial 2 after 17388 |
| sugawara-q1r (Q1 + reserve rnd<60) | spec 06:40Z | | | target ≥10/14 | | |
| LOO on trial-2 base (−04+05, −06, −12+09, −02) | spec 06:40Z | | | | | |
| sugawara-q2a-grow | parked (§7) | | | | | |
| bokuto-04-queen (D-075 §C trial 2) | — | 226–46 = c05; 38/42 q-wins on c05 wins | 42–4 | 44/189 | — | after 17388 |

## Unit 17 (03:25–03:37Z)

- **Read:** BOARD through line 1173 (`[03:21 UTC chair:ushijima → kageyama, asahi, sugawara, daichi, shenzhen] Fallback
  hypothesis: closed …`); my line is 1174 (03:34Z). D-070 (l.2739: §A 16979 first ten, queen rule; §B adopts my LS-1
  range + rec 21; §C T0 recorded; §D Kenma).
- **Nothing assigned by name.** Confirmed D-070 §A from replays (all flagged games reason `queen`), and computed an
  interim D-052 §B residual (approx. inputs): 29 games, diff −0.178 [−0.233, −0.122] → **P(fires at 40) revised 0.75**.
  Queen-loss tables: 16979 10/16 losses by queen (non-Schooltime 7/22 games vs parent 16/105); Schooltime cage 91/91
  r0 self-deaths, 15/120 of parent window. → `docs/learning/reviews/16979-interim-and-queen-losses-sugawara.md`.
- Notified the user (rollback likely at the 40-game look; forecast change from 0.08 to 0.75).
- Kageyama fallback count (0/76) closes my rec 19 event "p1_fallback > 1 %" locally (Asahi sandbox binding).
- Hinata T0: P(cost ≥ .005) 0.25 → no. Shenzhen 03:08Z correction (lookup 0.923 with terrain): data, not reviewed.

## Earlier units (summary)

- U16 (02:28Z): LS-1 final replication (adopted D-070 §B), rec 21 (adopted D-070 §B).
- U15 (01:35Z): A8b precedent (adopted D-068 §D), inventory rev 8 PASS, P-8 card filed (S0 approved D-068 §D), P1-slot softness reading (adopted as leading hypothesis D-068 §B).
- U14 (00:30Z): P-7 E2 PASS by bound (D-066 §B); p1-slot mechanism checks + rec 18 (adopted D-066 §E).
- U13 (23:29Z): drift row note (rec 17, D-065 §B). U12 (22:32Z): k16 promotion review (recs 15–16, D-064).
- U11–U5: P-7 amendment 1; D-058 §B precedents; P-6 amendA; R2 battery; LS-std-1 sizing; LS-1 rule; P-5/P-6 r2.

## Scored predictions (for Brier in calibration.md)

| card | event | P | logged |
|---|---|---|---|
| P-2 | confirmation PASS under spec 15d79683 | 0.50 | FAIL; Brier 0.25 (D-057 §B) |
| D-053 §D | k16 D-046 §4 gate PASS seeds 2–3 | 0.35 | 14:45Z |
| P-sugawara-02 | support / refute / later gate (orig.) | 0.40 / 0.25 / 0.20 | 14:55Z |
| P-sugawara-02 | support, amended | 0.35 | REFUTED; Brier 0.1225 (D-060 §B) |
| P-hinata-03 | dev ≥ 0.75 / G-macro / G-parent / panel gate / flip < 1 % | 0.55 / 0.10 / 0.85 / 0.20 / 0.15 | 15:30Z |
| P-hinata-04 | falsifier not triggered / V-legal AUC ≥ Φ | 0.85 / 0.20 | 15:30Z |
| P-5 r2 | dev ≥ .75 / G-parent clean / G-parent as written / ≥ .83 / panel gate | 0.65 / 0.70 / 0.60 / 0.20 / 0.25 | 16:28Z |
| P-6 r2 | falsifier not triggered | 0.80 | 16:28Z |
| LS-1 | PASS rule as written / my amended rule | 0.50 / 0.25 | NOT SCORED (D-069 §A: expired incomplete) |
| LS-std-1 | k16-like promoted / A/A noise ≥ 0.05 | 0.25 / 0.80 | 18:40Z (check calibration.md) |
| P-6 amendA | stump LOMO ≥ 12/14 | 0.25 | miss; Brier 0.0625 |
| P-6 amendA | V-legal* non-inferior | 0.40 | likely void |
| D-057 §C | sel. arm meets condition dev120 / full / A2 > A1 by .01 | 0.45 / 0.55 / 0.35 | 19:30Z |
| P-7 | E2 (orig.) | 0.60 | 20:31Z |
| P-7 amend 1 | E2 revised | 0.75 | PASS; Brier 0.0625 (D-066 §B) |
| P-7 amend 1 | distillation gate given trees / h2h ≥ .55 given step 0 < +.02 | 0.55 / 0.30 | 21:29Z |
| P-7 | h2h ≥ .55 / panel ≥ +.02 / live promotion | 0.45 / 0.25 / 0.15 | 20:31Z |
| D-063 §B | no rollback in 120 games given promoted | 0.87 | running since 02:13Z — now likely to miss |
| D-063 §B | harm clause fires / promotion (Chair / −.05 / −.02) | 0.07 / 0.85 / 0.72 / 0.58 | promotion happened (Chair rule, D-064) |
| p1-slot | selected arm in-bot parity < 1e-6 on ≥ 3 maps, first attempt | 0.85 | parity met both paths (D-068 §B) — score |
| rec 19 | λ* placeholder pool Δwin ≥ −2 pp, seed 1 | 0.35 | queued (Asahi arm 4) |
| rec 19 | p1_fallback > 1 % of turns on some map | 0.15 | 0/76 local (Kageyama 03:10Z); Asahi sandbox binding |
| rec 19 | λ = 0 pool Δwin ≤ −7 pp | 0.55 | queued (Asahi arm 3) |
| P-8 | S0 any head × bucket ≥ .005 / S0 direction / S1 given S0 / S2 / live in season | 0.60 / 0.25 / 0.20 / 0.20 / 0.07 | 01:31Z |
| D-069 | D-052 §B fires in 16979's first 40 ranked | 0.08 | 02:28Z (pre-games) — score at 40 |
| D-069 (rev.) | same, revised at 29 games (not for Brier; conditional on interim data) | 0.75 | 03:34Z |

## Open recommendations

1–17: see earlier history. Adopted: 1, 4, 6–10, 12, 15–17. Partly: 8, 11. Open: 2 (GSPRT rollback), 3 (cost of held-out exclusion), 13/14.
18–20 adopted (D-066 §E, D-068 §B–D). 21 (freeze pairing rule) **adopted** D-070 §B.
22. Queen reason in `executor.analyse_replay`. **Adopted** D-073 §A (Daichi to deploy).
23. **Superseded by ownership (D-072 §C).** The Schooltime cage (91/91 r0 queen self-deaths; ≈ 12.5 % of ranked draws in the parent window) is the largest single
    residual source and survives a rollback; un-park a structural fix (H-SZ1 style) or fast-track Kenma's pocket-queen
    evaluation. **Open** (03:34Z; implicit in BOARD line, not phrased as a card).

## Next checks (queen)

- **Trial-3 look (≥ 60 ranked games, Daichi) must be reviewed by me before the Chair reads it (D-083 §B):** D-081 table + Hinata curve block on curves.py ≥ 368313e94f33; check total length r300 and queen length r300 together (note B), Schooltime apart, incumbent window since 05:02Z.
- Asahi's bokuto-18 pool/probe (~13:50Z) and qk2/h2h vs kenma-03; any Hinata diagnosis-changing description (D-083 §A review duty).

- Chair/Hinata reaction to the P-hinata-07 fix (D-082 §A amendment?). Asahi 12:40Z results: asahi-27 qk2/h2h, kenma-03 qk2 queen columns, queen deaths by cause; read total length r100/r300 per D-082 §C.
- LOO on bokuto-13-cull: read for total length at r300 (D-082 §C) and queen alive r300.

- Chair's reaction to the reserve check (asahi-27 candidacy). If asahi-27 is built: qk2 vs b13 ≈ 0 expected.
- 'Longest' class: own longest/total at the limit when our queen died, 17388 vs 17530 vs top ten (rows.jsonl has final longest/total for our side only — add the opponent's if asked).
- bokuto-18 card: queen wall deaths/game, feeds by r330, and end-reason × result.

- bokuto-18 pool/probe: queen wall deaths per game, feeds by r330, queen length at the limit; Asahi's new columns + qk2.
- bokuto-17 cards incl. gen panel and the `n_maps = 0` twin (D-080 §D conditions). Trial-2 look (Daichi) with Hinata's matched column.
- Kageyama curve table (D-080 §B): check its queen columns against rows.jsonl (r300 alive 46 % for 17530).
- LOO on 13-cull: read on qk/qk2 vs base only, when built.

- Trial-2 look ~11:15Z (Daichi): rating-band split; does 17530's residual sit vs > 1725? Chair ruling on atlas / bokuto-17 jobs; Asahi's kenma-28 pool+var. Hinata's V card (unfunded) — review only if assigned.
- Hinata's response to the P-9 amendment (D histogram, first stage). Trial 2 (17530) look at ≥ 60 games (~13Z?) with Schooltime split; tie rule D-078 §C.
- LOO builds on 13-cull and Q1r: no results posted yet — check Asahi runs dir.

- Trial 1 (17388) look + trial 2 start (Daichi); ask for Schooltime(+open4) vs rest split. Asahi's var card; LOO builds on 13-cull (queue item 3); Q1r.
- Does the var block predict live better than the pool (k16 case)? Track per candidate.

- 07:45Z: bokuto-13-cull pool/probe → which base. Asahi's ack of the LOO + Q1r order; first LOO pool (−04+05). Trial 1 look ~08:00Z (Daichi).

- Asahi's ack of the amended order; c05/k16 keeper panels (D-075 §D); q1/q2b parity + pool. Trial 17388 (Daichi, ~08:00Z, anchor 1725).
- If Bokuto pools bokuto-07, re-run the paired table on it (does the churn shrink?).

- Asahi: q1 parity + pool; q2a pool + keeper panels. Kenma trial table (Daichi): Schooltime vs rest, queen alive.
- D-052 §B look on 16979 (Daichi) — my 0.08 forecast is still scored (D-072 §B keeps D-064 running event only; check).
- If q2a queens survive but stay short → feed range / crown (Q2b); if they die to heads → Q3 guard.
- Rec 22 adopted (queen reason in analyse_replay) now ordered to Daichi (D-073 §A).

## Older next checks

- D-052 §B look at 40 ranked games of 16979 (Daichi); score my 0.08 forecast; compare Daichi's frozen-input residual
  with my approximate −0.178 (own anchor, snapshot timing, draw handling).
- Daichi's queen-state scan + 14585 vs 303/420.
- Asahi D-068 §C results (arms 0, 2, 3, 4) vs forecasts; Shenzhen H-SZ74 (arm 4 recovers ≥ half of arm 2's loss).
- Single-team priors (213, 91) and Shenzhen H-SZ71/72.
- P-8 S0 result (Hinata/Data) and Nishinoya's review.
- Kenma h2h vs asahi-05-kz12-k16 (data). calibration.md: score p1-slot parity 0.85 event; LS-1 events void.
