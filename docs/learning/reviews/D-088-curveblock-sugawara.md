# D-088 §C — check of Hinata's trial-3 curve block (17791) — Sugawara, 5 Oct 2026 19:30Z

**Verdict: amend (labels only).** Every number replicates; two of the three "at target" readings depend on the view, and the
recorded conversion figure is the carried one, which counts games already won by elimination as converted leads.

## Replication

`python3 tools/hinata/look.py block build/hinata/look3 17791` on Hinata's frozen rows (60/12, 17791 from 14:19:00Z; sel.json
complete; 0 missing elo; queen guard 120/120 against the engine field). Output equals the 18:38Z BOARD line to the decimal:
≥ 1725 n 55/11, carried r300 97.5 vs 90.9, +6.6 [−14.2, +29.3]; r100 65.1 vs 57.3; queen alive r100/r300 carried 0.93/0.62;
leads converted (carried) 20/26; elimination losses 14, 9 before r300. Code read: `val()` carries the end state only when the
game ended before r; queen = lowest initial id (curves_qid, the fixed rule); band = opponent elo at the snapshot ≤ start.

## Amendments to the reading recorded in D-088 §C

1. **Conversion.** ≥ 1725: 55 games, 40 reached r300, 15 ended earlier (9 elimination losses, 6 wins). The carried view counts
   the 6 early wins as leads (opponent total 0) and as converted: 20/26 = 14/20 + 6/6. **Leads alive at r300 converted: 14/20
   = 70 %** (reached view), exactly at the D-082/D-083 target with n = 20 (Wilson 90 % ≈ [49 %, 81 %]). "At target" stands,
   but not "77 %"; 17530's 15/21 needs the same split before the two are compared.
2. **Queen alive r300.** Reached 0.72 (40 games), carried 0.62 (55). The D-083 target 0.58 is the top-ten winner figure
   from the owner-corrected curves (reached view). Both views clear it; quote the reached 0.72 against the target, the carried
   0.62 against 17530's 0.42.
3. **"Shift is early, not growth r100→r300 (32.4 vs 29.6)".** This subtracts a carried r300 (zeros for eliminated sides)
   from an r100 that both views share; it mixes growth with elimination. Against the top ten (reached, same view) the gap is
   r100 −13.4 (65.1 vs 78.5) and growth r100→r300 −24.6 (50.6 vs 75.2): **most of the economy gap is growth after r100**, not
   the opener. Versus 17530 the shift is early, as Hinata says. Both statements should carry their comparator.

## Mechanism / RL notes

- Inputs legal (replay end states; no bot-side features). Curve block is description, not a gate; no leakage path.
- Hinata's RL translation (queen alive r300 as a value feature) is sound and cheap; add "lead alive at r300" (reached) as the
  conversion target so the carried artefact does not enter a label.

## P / dissent

No forecast attached (description). Dissent: the field is 11/12 series ≥ 1725; no band contrast is possible on this window.
