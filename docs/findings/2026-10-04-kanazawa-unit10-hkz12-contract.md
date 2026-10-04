# Kanazawa unit 10 — H-KZ12 contract frozen (Himeji D-044 semantics) and per-dose exposure

4 October 2026, 07:40–07:50 UTC. Answers Seoul ff8fac943 (contract mismatch). Tool: `tools/kanazawa/q_dose.py` (read-only, 27 s).

## Frozen contract (Kanazawa withdraws its own variant; Seoul implements this one)
- **Feature** `Cb(u→v)`: cells reachable from v, **inclusive of v**, capped at 16, through non-kelp edges, excluding u and every cell occupied after the move by any dragon body **except each dragon's tail cell**. Unknown terrain in the bot = passable (the veto fires only on known closure).
- **Orbit escape**: no veto if reach ∪ {u} contains a simple terrain cycle ≥ L+1 (L = queen length after the move).
- **Veto** at dose k if `Cb < k` (**strict**), k ∈ {0, 4, 8, 16}, with k = 0 as the disabled parent. My `C ≤ k` and {0,5,8,16} are withdrawn.
- **Label**: queen death in rounds t+1…t+6 (Himeji's six-round landmark), reported **by cause** (wall/self/body/h2h/invalid), not wall-only.
- Fallback when every legal move is vetoed: take the move with the largest Cb. A veto must never force an invalid move.

## Exposure (in-sample stride 96 of the first 286 post-m2 team-7 games; replay snapshots, approximate legality per H27-05)
Our queen deaths: h2h 43, **wall 30**, self 17, body 5 (95 of 96 queens).

| k | vetoed moves (us) | death within 6 rounds: wall/self/body/h2h/none | vetoed moves with an alternative ≥ k | our wall deaths preceded by a veto | …of which the first veto had an alternative |
|---|---|---|---|---|---|
| 4 | 79 | 52/13/4/3/7 | 22 (28 %) | 23/30 | 12 |
| 8 | 154 | 63/17/4/6/64 | 32 (21 %) | **25/30** | **15** |
| 16 | 177 | 67/17/4/6/83 | 38 (21 %) | 25/30 | 15 |

Opponents (k = 8): 159 vetoes, 32 with an alternative; 12/15 wall deaths preceded, 7 with an alternative.

## Verdict against the frozen rule (written 07:41Z, before the first run)
- (a) ≥ 50 % of our wall deaths preceded by a veto at k=8: **pass** (25/30).
- (b) ≥ 50 % of vetoed moves have an alternative at k=8: **fail** (21 %); no dose passes. Most vetoes fire inside the pocket, where the move is already forced. H-KZ12 goes from 0.8 to **0.6**, as frozen.
- Post hoc (not part of the frozen rule): at the episode level, 15/30 of our queen wall deaths have a body-aware alternative at the first veto in the window. **Ceiling for a one-step veto: about 50 % of queen wall deaths, about 16 % of all queen deaths.** It is a ceiling because the alternative may also die.
- Body awareness halves the open-alternative share that unit 8 found with terrain only (about two-thirds then).
- False-positive load at k=8: 64/154 vetoes have no death within six rounds. That is a food and tempo cost; k=4 has 7/79.

## Implications
- Seoul screen: expected sign is fewer queen wall deaths. Realistic size is ≤ 50 % of wall deaths at k=8; **falsifier: < 25 % fewer at k=8, or food/turn down > 10 %**. k=4 is the cleanest dose (7/79 false positives).
- **H-KZ24 (new):** h2h is our largest queen death cause (43/95), larger than wall. Nobody has a lever on it. Size and test in unit 11.
- H-KZ22 reopened at 0.15: Himeji H28-05 is right that age > 3 alone does not show the donor was not born trapped.
