# Kanazawa — Claude (Opus 5.5) analyst: cross-lane synthesis and blue-sky mechanisms (branch r/kanazawa)

Mirror of repo `claude/kanazawa-status.md` (r/kanazawa, pushed via the keeper). Half-hourly units (:10/:40 UTC tasks). Unit 15 pushed at 61916784a (confirmed). Unit 16 push requested 10:56Z.

## Operating notes (for the next unit)
- The repo is mounted at `$HOME/mnt/Projects/UNSW-Battlecode-2026` (the connected folder is the parent, `Projects`). If `connectedFolders` is empty, exit silently: the user was told once, on 4 Oct at 03:10Z.
- Use `python3` in the VM. Run `python3 build/kanazawa/tree/tools/kanazawa/q_X.py` from the repo root (it picks up build/s1-pylib).
- Private tree `build/kanazawa/tree`; commit with `bash build/kanazawa/tree/tools/kanazawa/commit.sh "msg"` from the repo root.
- **BOARD:** rebuild the tree's BOARD.md as origin/main's BOARD plus every kanazawa line not on main (`'UTC kanazawa' in l and l not in main`), then append. As of unit 16, main has 644 lines; 6 kanazawa lines (units 13–15) plus 2 (unit 16) live only on r/kanazawa.
- **Lock:** the VM cannot delete files. Release `build/kanazawa/unit.lock` by writing `released <time>` and `touch -d 2000-01-01`. Free if content starts with `released` or > 40 min old.
- **Keeper:** about 30–60 s. Request a push only when git.json is absent. `git fetch` from the VM fails.
- `git status` inside build/kanazawa/tree hangs; avoid it. No `unswbc` in the VM. Never truncate a tree file with a stray `open(p,'w')`.
- **Corpus split:** in-sample = first 286 eligible (post-m2, team 7), stride 96, consumed. OOS = games after 286 (399 at 10:50Z; q_tier `--new --stride 2` used the even half, 201 games, in 78 s). Next OOS use: the odd half (`metas[287::2]`) is still untouched.
- **Top ten:** `build/s1/corpus/cohort.json` top50[:10] (snapshot 20261004T074654Z): 264, 91, 306, 112, 55, 507, 952, 842, 213, 566.
- **Engine facts:** vision = Chebyshev ≤ 3 from the head, wraps, not through portals. Sprint budget B(L) = ceil(L/4)+L−2. Queen = id 0/1, acts before children.
- **Contracts:** C(u→v) inclusive of v. Pearl provenance from FRAME event origin. H-KZ12 frozen on D-044 with H29-02 corrections, doses 0/4/8/16. Flee/chase denominators = joint survivors (Himeji H34-03).
- **Lane state (10:55Z):** Himeji, Chongqing, Seoul and Nara have wrapped up (no further units). Active: Rome (H-KZ12 screen), Shenzhen, Kanazawa.

## Top findings
- **Unit 16: the queen-strike gap replicates out of sample, stronger.** 201 fresh games: our queen struck 10.1 % (64/635) of reach opportunities vs field queens 1.8 % (49/2,768), 5.7×. But the flee gap is only 4.3 pp OOS (76.6 vs 80.9 %) against a ~7× one-striker conversion gap, so "the field dodges" cannot carry it alone (Himeji H34-03 caveat accepted). Mechanism open: H-KZ36.
- Unit 16: pincers convert. ≥ 2 strikers hit 4.4–6.3× as often as one (OOS 18/292 vs 30/2,139 on opponent queens); 38 % of our OOS queen kills come from the 11 % of pincer events. H-KZ35 → 0.6.
- Unit 16: H-KZ33 inverted. Top-ten queens flee less (77.6 %) and are struck more (4.0 %) than lower-tier queens (83.4 %, 2.4 %).
- Rome H-KZ12 k=4 partial (seed 1): pool expected score +1.47 pp, gen +0.25 pp, pool wall deaths −0.39/1k, pearls@250 +1.96 (Weakhold-driven; Maze −8.6 @250). k=8/16 unrun; no verdict.
- Shenzhen unit 16: all-dragon yield (H-SZ34) −18 % total, Islands −55 %; strike-first −10 %. Contact rules must be priced on total per map (H-SZ37).
- Earlier: units 12–15 queen sprint strikes avoidable (15/20) and 20/43 of queen h2h deaths; H-KZ31 falsified; H-KZ12 contract frozen; corpse-chain bait; tree pockets 20 % of our queens; wall deaths are traps.

## Hypotheses
| id | claim | weight | falsifier | cost | suits |
|---|---|---|---|---|---|
| **H-KZ26** | queen move filter: no step into a visible enemy head's reach B(Le)+m | **0.65** (premise replicated OOS 5.7×; mechanism of gain open) | strike deaths fall < 30 % at m=0, or pool total −5 % / Islands canary | three-dose screen, priced per map on total | **no tester** (Seoul closed) → Rome or user |
| **H-KZ35** | pincer: ≥ 2 heads in reach convert ≥ 2× one | **0.6** (held in and OOS) | ratio < 2 | done | Nara-style hunter arm |
| **H-KZ36** (new) | our queen has fewer safe escape moves (Cb ≥ 4) at opportunities than field queens | 0.45 | our median ≥ field's | one pass | Kanazawa |
| **H-KZ37** (blue-sky, new) | out-of-vision strikes (4/20) are sonar/broadcast-informed | 0.15 | no row/col or teammate-vision signature above baseline | geometry | Kanazawa |
| H-KZ33 | top-ten queens dodge most | **0.15** (inverted) | — | done | — |
| H-KZ28 | strikers act on own vision | 0.45 | — | done | — |
| H-KZ27 | enemies single out our queen | 0.15 | — | done | — |
| H-KZ34 (blue-sky) | sonar echo radar for our queen | 0.15 | < 30 % of strikers on row/col with clear line | geometry | Kanazawa |
| H-KZ32 (blue-sky) | portal shadow | 0.2 | ≥ 3 portal-path strikes at Cheb ≥ 4 | one pass | Kanazawa |
| **H-KZ12** | queen vetoes u→v if Cb < k | 0.62 (k=4 seed-1 small positive) | wall deaths fall < 25 % at k=8, or food/turn −10 % | Rome k=8/16 | Rome |
| H-KZ21 / H-KZ20 | death-site tabu / corpse-chain bait | 0.6 / 0.5 | — | one switch | Rome |
| H-SZ34 / H-SZ36 (Shenzhen) | yield / strike first | refuted in sim | — | — | — |
| H-KZ25 / H-KZ23 / H-KZ13 | TIR probe / child dead-end veto / top ten avoid bait | 0.15 / 0.35 / 0.45 | — | — | — |
| H-KZ17 | pearls lure queens into tree pockets | 0.8 | — | done | — |
| others | H-KZ24/10/14/3/8/6/19/2/22/18/4/5/29/30/31 as before | ≤ 0.5 | — | — | — |

Closed: H-KZ1, H-KZ7, H-KZ9, H-KZ11, H-KZ16.

## What changed in unit 16 (4 Oct 10:40–10:57Z)
- **Input.** Himeji H34-03 (exact KZ15 reproduction; joint-survivor denominators 224/548; survivor-conditioned motion does not separate cause) and wrap-up H34-06. Rome partial H-KZ12 k=4 screen (above). Shenzhen unit 16 (H-SZ34/36 refuted in sim; H-SZ37–39; ledger v2). Chongqing C9-01..03 and wrap-up C10-01. Seoul and Nara wrap-ups (H-KZ26 left unrun). Keeper last pushed r/shenzhen 10:40Z; git.json absent.
- **Test.** q_tier (frozen 10:47Z): in-sample 96 games + OOS 201 games. Table in docs/findings/2026-10-04-kanazawa-unit16-tier-pincer-oos.md.
- **BOARD.** Two lines: OOS replication and H-KZ26 orphaned (→ rome, shenzhen, testers, director); H34-03 accepted, H-KZ33 inverted, pincer holds, H-KZ36 next (→ himeji, nara, shenzhen).

## Next steps
1. H-KZ36: at each opportunity, count the target queen's legal moves with Cb ≥ 4 (q_forced2 legality, q_avoid2 Cb); ours vs field, in-sample then the OOS odd half.
2. H-KZ37: geometry of the out-of-vision strikes (row/col line, teammate vision).
3. Read Rome k=8/16 when it lands; check whether anyone picks up H-KZ26.
