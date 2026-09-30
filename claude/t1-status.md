# T-1 status — taxonomy (lineage `t1`, branch `r/t1`)

**30 Sep 2026, initial build.** Lineage name `t1` chosen by the session (the prompt left it "as given by the lead"; none
was given). Read-only over every other tree; nothing outside `docs/TAXONOMY.md`, `docs/taxonomy/` and this file was
written.

## What was delivered
- `docs/TAXONOMY.md` (≈395 lines): §1 state and features (28 bot-side, 12 analysis-side), §2 algorithm designs (27),
  §3 problems (25, three-number form where the sources give it), §4 attempted solutions (62 families with verdict and
  why each stopped), §5 matrices (P×S in full; S×lineage and F×consumer summarised), §6 a ranked opportunity space (15
  items with size, cost and lane).
- `docs/taxonomy/`: one detail file per id (F-01…F-28, F-40…F-51, A-01…A-27, P-01…P-25, S-01…S-62), the registers
  `map-mechanism.md` (553 rows), `contradictions.md` (C-01…C-84), `dead-and-unmeasured.md`, `matrices.md`, and the
  `_*.tsv` summaries the matrices are regenerated from.
- Sync point: `main` at `9315914c9` + lane branches as fetched 30 Sep 06:30 UTC (`origin/r/{esquie,monoco,ra,sciel,r3,r4}`,
  `origin/cx/*`, `origin/{pace,glm,sakura,yeji,chaewon,kazuha,gpt}/*`, `origin/analysis/a1`) + the claude.ai project
  status files. The next update diffs from here.
- Method: nine parallel readers extracted the corpus into structured notes (ledger/decisions/prompts; 28 Sep findings;
  29–30 Sep findings and lanes; analysis and experiments; family docs; C++ code; two Python code slices; model lines),
  detail files were written from the notes against a fixed id catalogue, and a verification pass checked 85 claims
  against the sources (10 corrected).

## Proposed ledger changes (for the director; not applied here)
1. **L12** — record Sciel 03b/03c/04a/04b: all built, all REJECT on h2h_ally (+24…+38 %), family closed by its lane;
   replace "fix (03b) queued in lane rc" (also in D-034 and BASELINES). The economy evidence (+0.067…+0.105 pool,
   +6…+16 % gen) stands; the named fix is spent.
2. **New row (L35 proposed): arrival-level deconfliction / target claims** on Ares — Sciel's sciel-05 packet or the cx
   router's greedy assignment. Evidence: the ally head-on guard rejected every Ares economy gain ≥ +0.05 (Sciel 03a–04b,
   Renoir 07a, V08). Never built (TAXONOMY §6 #1).
3. **L24** — absorb esquie-04 (V19 at panel scale, z1 seeds 1+2): REJECT, econ −0.035, own-body +24 %, pooled trapped
   37.0→39.7, Slithery trapped −19 %. Esquie proposes 0.5→0.35; the ledger rule allows one step per rejection on the
   right host. Also add the teammates' wave 2 as (T) rows (V20–V27 null/negative; V28 minimum-sacrifice split 12–8; V32
   dead-end child search 11–9; V33 split portal-route handoff 33–27 round robin) — the ledger's own procedure requires
   this before R work in the area, and M-1 was issued in it.
4. **L01** — the evidence column cites "+12.9 % dragons r100"; R-1 found it does not reproduce on the pool (+0.011 s1,
   −0.025 s2) and appears only off-pool (+0.130). Amend the evidence text (contradictions C-01).
5. **L25** — no longer unbenchmarked: robert-v01 (same profile on V06) 12–8 vs V06 in a 20-game screen; Lune L1 (×2)
   105–55, exp −0.106 on the fixed panel.
6. **L06** — two exit-side instances exist that fit the revival shape: Ares's inherited `blind_*` body-sighting memory
   (never varied on Ares) and V33's type-9 route handoff. Neither has been measured per transit.
7. **Id clash** — Esquie's proposed "L31 (starved openings)" collides with L31 (state machines). Suggest a new id
   (e.g. L36) for starved openings / supply-gated waiting, with esquie-03b's LOCAL HOLD as its evidence.
8. **L17 vs L30** — L17 (production cannot be forced, 0.1) and D-035's "r3-03 is a production lever, +5 pp" are in
   tension; the decisive test is r3-03 at seed 3 against a units-matched control (C-06).
9. **Record keeping** — D-027 and D-028 are cited (C1-addendum, TEAM-SUMMARY) but absent from the decisions file; the
   project copy `claude/hypothesis-ledger.md` is stale (L01, L06, L12, L20, L21 weights differ from the repo).
10. **Mandated, not delivered** — D-032's re-scores (Renoir 17a/17d/18a/18c, Lune late cap) and the ledger-queued Monoco
   re-scores (ra-03, ra-05); R-4b (interval GATE line, corpse-share diagnostic); R-6 prompt never issued.

## Gaps in the sources (so the next update knows what is not covered)
- Absent from the snapshot: `docs/findings/sakura-s01-data/` result files, `docs/findings/yeji-s1-runs/`, `docs/athos.md`,
  the aramis/dartegnan/javert experiment reports, `tools/*.py` sources for rl_earlygame/loki/ouroboros/leviathan,
  `ouroboros-m01` `model.json`. Their mechanisms are recorded from READMEs only and marked so.
- Lanes with nothing on origin yet: R-2b (Basquiat), R-2c (Cézanne), SF-1, RL-1, HB-1, K-1 (Sophie's branch unpushed;
  read from the project status file).
- Branch `r/t1` is committed in the local repository; the session's machine has no GitHub credentials, so it has not
  been pushed to origin.

## Update procedure
See `docs/TAXONOMY.md` §"Keeping this current". Each later update appends a dated section here: sources diffed, ids
added or amended, verdicts changed, and §6 re-ranking.
