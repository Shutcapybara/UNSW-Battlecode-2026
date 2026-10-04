# Kanazawa lane wrap-up: 16 units, 4 Oct 02:30–10:57Z (Claude Opus 5.5, analyst)

The lane is closed by user request. Its scheduled tasks (:10 and :40) are disabled. The niche was cross-lane synthesis, contradictions between lanes, and blue-sky mechanisms. All work is analysis on the S-1 corpus: there are no bot versions, because the VM has no `unswbc`. Tools are in `tools/kanazawa/q_*.py`, and there is one finding per unit in `docs/findings/2026-10-04-kanazawa-unit*.md`.

## What the lane established, by strength
1. **Our queen dies to enemy sprint strikes that the field's queens avoid** (units 11–16). This is the strongest result.
   - 20 of our 43 queen h2h deaths are enemy sprint strikes from distance ≥ 2. Every one was a trade (the striker died too).
   - In 15/20, a legal step existed at the last turn that was outside every visible enemy's reach B(L) = ceil(L/4)+L−2 and kept Cb ≥ 4. The result holds with uncapped BFS.
   - Per opportunity (enemy head with our queen in Chebyshev ≤ 3 and BFS reach ≤ B(Le)+1), our queen is struck 9.5 % of the time in sample and **10.1 % out of sample (64/635)**, against 3.1 % and **1.8 %** for field queens. The out-of-sample ratio is 5.7×.
   - Enemies do not chase our queen more than our children (31 % vs 32 %), so targeting (H-KZ27) is out.
   - The flee gap (69–77 % vs 78–81 %) is too small to explain the whole ratio. The mechanism is still open. The leading candidate is H-KZ36: our queen has fewer safe escape moves.
   - Cost of a reach veto: it fires in about 25 per 1,000 queen-rounds, roughly 10 firings per strike prevented.
2. **Pincers convert** (H-KZ35, 0.6, held in and out of sample). An opponent queen with ≥ 2 of our heads in reach is struck 4.4–6.3× as often as with one. 38 % of our out-of-sample queen kills came from the 11 % of opportunities that were pincers. A queen hunter needs a forcing pattern, not just a "go for the queen" weight.
3. **Our queens die in traps, not in fights** (units 1–9). Wall deaths are traps (dead ends and tree pockets). Tree pockets take 20 % of our queens. Pearls lure queens into pockets (H-KZ17, 0.8), and corpse chains act as bait. This led to the H-KZ12 contract: the queen vetoes a step u→v if Cb < k, frozen on D-044 with doses 0/4/8/16, and Rome runs it. The k=4 seed-1 result is small and positive (pool +1.47 pp; Maze pearls −8.6 at r250). k=8 and k=16 have not run.
4. **Falsified or inverted:**
   - H-KZ31: an invisibility rule (keep enemy heads at Chebyshev ≥ 4) is possible in only 4/20 cases.
   - H-KZ33: top-ten queens dodge more than other teams' queens. Inverted: they flee less and are struck more.
   - H-KZ27: enemies single out our queen.
   - H-KZ30: a bodyguard child strikes the striker first.
   - H-KZ29: strikers track our queen beyond vision.

## Cross-lane positions
- Shenzhen H-SZ34 ("be the mover") and H-KZ26 act on different dragons: in 19/20 queen strikes the striker was longer than or equal to our queen. Shenzhen's own sim later priced all-dragon yield at −18 % total (Islands −55 %). Any contact rule must be judged on per-map totals (H-SZ37), and that applies to H-KZ26 too.
- Himeji's corrections are adopted throughout: H30-01 (the B(L) formula), H31-01 (decision state is the attacker's own TurnStart) and H32-03 (being in vision is necessary, not sufficient).

## Recommended next actions for whoever picks this up
1. **Tester (Seoul or Rome):** H-KZ26 three-dose screen (m = 0/1/2, fallback Cb ≥ 4, uncapped reach), priced on pool total and per map with Islands as the canary. This is the largest identified queen lever.
2. **Analyst:** H-KZ36. At each opportunity, count the queen's legal moves with Cb ≥ 4, ours vs the field's. Tools: q_forced2 for legality, q_avoid2 for Cb, q_suff for opportunities.
3. **Hunter arm (Nara-style):** a pincer rule. Commit a second head before striking an opponent queen.
4. **Rome:** finish H-KZ12 k = 8/16.
5. **Blue-sky, untested:**
   - H-KZ32: portal shadow (strikers ignore queens they reach only through portals).
   - H-KZ34: sonar echo radar on the queen's row and column.
   - H-KZ37: sonar-informed strikes from out of vision.
   - H-KZ25: backward (TIR) sonar as a terrain probe.

## Method notes
- In-sample is the first 286 eligible post-m2 team-7 games at stride 96. Games after 286 are out of sample (`--new`).
- Objectives were frozen in the docstring before each run. Where a follow-up was added after a primary, it is labelled exploratory.
- Lane mechanics: commits go through `tools/kanazawa/commit.sh`, which never touches the shared index or HEAD, and pushes go through the keeper only.
